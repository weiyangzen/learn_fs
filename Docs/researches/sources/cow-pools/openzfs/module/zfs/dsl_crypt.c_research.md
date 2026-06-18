# File Research: sources/cow-pools/openzfs/module/zfs/dsl_crypt.c

## Purpose

`dsl_crypt.c` manages OpenZFS dataset encryption at the DSL layer. It owns encryption parameter parsing, wrapping-key lifecycle, in-memory spa keystore structures, DSL crypto key loading/unloading, dataset-to-key mappings for zio, key creation/cloning/destroy, key changes and promotion updates, encrypted dataset creation, raw send/receive key serialization, and cryptographic dispatch wrappers used by lower layers.

The file’s top comment defines the three keystore AVL trees:

- Wrapping key tree: user-supplied keys loaded by `zfs load-key`, keyed by encryption-root dsl_dir object.
- DSL crypto key tree: decrypted master keys, keyed by DSL crypto key ZAP object.
- Key mapping tree: dataset object to DSL crypto key mapping, used by zio/ARC lookups.

## Tunable

`zfs_disable_ivset_guid_check` allows raw receives without matching IV set GUIDs for the errata path associated with older encrypted send streams. The file exports it as `zfs_disable_ivset_guid_check`.

## Crypto Params And Wrapping Keys

`dsl_crypto_params_create_nvlist()` parses encryption properties and crypto arguments into `dsl_crypto_params_t`. It validates command, encryption algorithm, key format, keylocation, wrapping-key length, normalizes `ZIO_CRYPT_ON`, creates an in-memory `dsl_wrapping_key_t` when raw key data is provided, removes encryption-only properties from the normal DSL property nvlist, and returns the params object.

`dsl_crypto_params_free()` frees keylocation and optionally unloads/frees the wrapping key.

`dsl_wrapping_key_create()`, `dsl_wrapping_key_hold()`, `dsl_wrapping_key_rele()`, and `dsl_wrapping_key_free()` manage wrapping-key memory and refcounts. Freeing zeroes key material before releasing memory.

## Spa Keystore Initialization

`spa_keystore_init()` initializes locks and AVL trees for DSL keys, key mappings, and wrapping keys. `spa_keystore_fini()` asserts DSL keys and mappings are empty, destroys all remaining wrapping keys, tears down AVLs, and destroys locks.

Comparison functions key AVLs by DSL crypto key object, dataset object, and wrapping-key root dsl_dir object.

## Key Lookup And Loading

`dsl_dir_get_encryption_root_ddobj()` and `dsl_dir_get_encryption_version()` read fields from a dsl_dir’s crypto ZAP. `dsl_dir_incompatible_encryption_version()` reports unsupported key versions.

`spa_keystore_wkey_hold_dd()` finds the wrapping key for a dataset by reading the encryption root ddobj and looking it up in the wrapping-key AVL.

`dsl_crypto_key_open()` reads a DSL crypto key ZAP from disk, validates crypto suite support, reads wrapped master/HMAC key data plus IV/MAC/version, unwraps with the supplied wrapping key, initializes a `dsl_crypto_key_t`, holds the wrapping key, and returns a held decrypted key. Authentication failures map to `EACCES`.

`spa_keystore_dsl_key_hold_dd()` first tries to hold an already-loaded DSL key, otherwise holds the wrapping key, opens the key from disk, and inserts it into the DSL-key AVL. If another thread inserted the same key during I/O, it discards the new key and returns the existing one.

`spa_keystore_dsl_key_rele()` drops a DSL key hold and removes/frees the key when the refcount reaches zero.

`spa_keystore_load_wkey()` validates a load-key request, holds the target dsl_dir, verifies the dataset is an encryption root, proves the wrapping key can open the DSL key, fills keyformat/salt/iters from disk, optionally no-ops for verification-only calls, inserts the wrapping key into the keystore, and creates zvol minors under the dataset.

`spa_keystore_unload_wkey()` waits for txg I/O to release references, opens the pool/dir, removes an unloaded wrapping key if its refcount is zero, and removes zvol minors under the dataset.

## Key Mappings

`spa_keystore_create_mapping()` creates or reuses a dataset-object to DSL-key mapping. It holds the DSL key for the dataset’s dsl_dir, inserts a new mapping under `sk_km_lock`, or bumps the existing mapping refcount and frees the temporary one.

`spa_keystore_remove_mapping()` finds a mapping by dataset object and releases it.

`key_mapping_rele()` is carefully structured to avoid taking the mapping AVL writer lock on the common path. When the refcount appears to reach zero, it takes a temporary reference, acquires `sk_km_lock` as writer, confirms finality, removes the AVL node, releases the DSL key, destroys the refcount, and frees the mapping.

`spa_keystore_lookup_key()` is the hot-path lookup used by zio/ARC. It takes `sk_km_lock` as reader, finds the mapping, and optionally adds a hold to the mapped DSL key. It can also be called as an existence check with `tag == NULL` and `dck_out == NULL`.

## Dataset Key Status And Properties

`dsl_dataset_get_keystatus()` reports none/available/unavailable depending on whether a crypto object exists and whether the wrapping key is loaded. `dsl_dir_get_crypt()` reads the encryption suite or returns `ZIO_CRYPT_OFF`.

`dsl_dataset_crypt_stats()` adds keystatus, encryption algorithm, key GUID, keyformat, PBKDF2 salt/iters, IV set GUID, and encryption root name to a dataset property nvlist.

`dsl_crypto_can_set_keylocation()` validates whether `keylocation` can be set: unencrypted datasets may only use `none`; encrypted datasets require a valid keylocation and must be encryption roots.

## Syncing DSL Crypto Keys

`dsl_crypto_key_sync_impl()` writes the full on-disk DSL crypto key ZAP payload: suite, root ddobj, GUID, IV, MAC, wrapped master key, wrapped HMAC key, keyformat, salt, and iters.

`dsl_crypto_key_sync()` wraps the in-memory master/HMAC keys with the current wrapping key and stores them with `dsl_crypto_key_sync_impl()`.

`dsl_crypto_key_create_sync()` creates a new DSL crypto key ZAP, initializes random key material, syncs it, stores refcount and version, zeroes/destroys temporary key material, and returns the ZAP object.

`dsl_crypto_key_clone_sync()` increments a DSL crypto key ZAP refcount for encrypted clones. `dsl_crypto_key_destroy_sync()` decrements the refcount or destroys the ZAP when it reaches one.

## Changing Keys And Promotion

`spa_keystore_change_key_check()` validates `zfs change-key` command variants: new key, inherit, force new key, and force inherit. It rejects unencrypted datasets and clones, enforces root/inheritance rules, validates keylocation/keyformat/PBKDF2 parameters, and checks that needed wrapping keys are loaded unless forced.

`spa_keystore_change_key_sync_impl()` recursively updates descendants inheriting from an old encryption root. With a new wrapping key it holds and rewraps each DSL key, otherwise it only updates the root ddobj field. It recurses through child dsl_dirs and clone directories, using `skip` for clone paths that share an already-updated key.

`spa_keystore_change_key_sync()` applies user properties, updates keylocation, selects old/new encryption root ddobjs, holds the wrapping-key AVL writer lock, recurses through affected descendants, replaces the old wrapping key in the keystore, inserts the new key when applicable, and releases inherited references.

`spa_keystore_change_key()` runs the change as a reserved-space sync task.

`dsl_dir_rename_crypt_check()` prevents moving a non-root encrypted dataset under a different encryption root. `dsl_dataset_promote_crypt_check()` verifies promote can occur without unexpected rewraps. `dsl_dataset_promote_crypt_sync()` updates keylocation and encryption-root references when promotion makes the target the encryption root.

## Dataset Creation And Clones

`dmu_objset_create_crypt_check()` validates encryption parameters for new objsets. It resolves inherited encryption, rejects encryption params for unencrypted datasets, requires the encryption and bookmark v2 features, verifies parent key availability for inheritance, and validates explicit keylocation/keyformat/PBKDF2 data.

`dsl_dataset_create_crypt_sync()` handles encrypted dataset creation. Clones share the origin key by cloning the DSL crypto key refcount. Non-clones either inherit the parent wrapping key or use a new wrapping key, create a DSL crypto key ZAP, store it in the dsl_dir ZAP, activate the encryption feature, and load the new wrapping key when supplied.

## Raw Send/Receive

`dsl_crypto_recv_raw_objset_check()` validates raw-receive objset metadata: objset type, meta-dnode compression/checksum/nlevels/block size/indirect shift/nblkptr/maxblkid, portable MAC, existing objset immutable fields, and optional from-IV-set GUID match.

`dsl_crypto_recv_raw_objset_sync()` creates the objset if needed, installs the portable MAC, clears local MAC and user-accounting-complete flag, marks the objset for raw write, sets meta-dnode compression/checksum/maxblkid, and syncs the dataset immediately for existing datasets.

`dsl_crypto_recv_raw_key_check()` validates raw-received DSL crypto key fields, rejects unsupported/old key versions, ensures incremental receives keep the same key GUID, and validates wrapping key metadata.

`dsl_crypto_recv_raw_key_sync()` creates the crypto ZAP for a new encrypted receive, activates encryption, stores default keylocation `prompt`, and writes received key material exactly as provided.

`dsl_crypto_recv_raw()` runs raw receive setup as a sync task.

`dsl_crypto_populate_key_nvlist()` builds the nvlist used for raw send. It reads the DSL crypto key ZAP, IV set GUID, wrapping-key properties from the encryption root, objset portable MAC, and meta-dnode structural fields. It rejects legacy unsupported key versions and records errata where needed.

## Crypto Dispatch Helpers

`dmu_objset_crypto_key_equal()` compares two objsets’ loaded key GUIDs.

`spa_crypt_get_salt()` retrieves a key-derived salt for a dataset.

`spa_do_crypt_objset_mac_abd()` generates or verifies objset-level portable/local MACs, with special handling for zero local MACs in user-accounting edge cases.

`spa_do_crypt_mac_abd()` generates or verifies normal block MACs.

`spa_do_crypt_abd()` is the main encryption/decryption multiplexer. It looks up the dataset key by bookmark objset, borrows ABD buffers, generates salt/IV for encryption as needed, uses deterministic salt/IV for dedup blocks, calls `zio_do_crypt_data()`, supports decrypt fault injection except for dnode blocks, zeroes salt/IV/MAC on encryption failure, returns ABD buffers correctly, and releases the key.

## Concurrency And Security Notes

The keystore uses separate rwlocks for DSL keys, key mappings, and wrapping keys. The mapping lock is on the I/O hot path, so allocation/freeing and final removal are structured to minimize writer-lock time. Key material is zeroed before free where directly handled. Authentication failures are deliberately exposed as access errors. Raw receive validation is strict about key versions and IV set GUIDs unless the errata tunable disables that check.

## Dependencies

This file depends on DSL pool/dir/dataset, ZAP, zio crypt primitives, objset creation/sync, properties, zvol minor management, feature flags, raw send/receive metadata, ABD buffer access, and dataset promotion/rename workflows.
