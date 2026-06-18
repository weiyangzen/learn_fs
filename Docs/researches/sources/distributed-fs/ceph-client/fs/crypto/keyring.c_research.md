# sources/distributed-fs/ceph-client/fs/crypto/keyring.c

## Purpose
`keyring.c` implements the filesystem-level fscrypt master-key keyring and the ioctls for adding, removing, and querying encryption keys. It also registers fscrypt-specific Linux key types and supports test-dummy keys.

## Important APIs, Types, and Functions
- `struct fscrypt_keyring` stores the per-superblock hash table of `fscrypt_master_key` objects.
- Lifetime helpers: `fscrypt_put_master_key()`, `fscrypt_put_master_key_activeref()`, `fscrypt_initiate_key_removal()`, and `fscrypt_destroy_keyring()`.
- Lookup and insertion: `allocate_filesystem_keyring()`, `fscrypt_find_master_key()`, `add_new_master_key()`, `add_existing_master_key()`, `do_add_master_key()`, and `add_master_key()`.
- User claim tracking: `allocate_master_key_users_keyring()`, `find_master_key_user()`, `add_master_key_user()`, and `remove_master_key_user()`.
- Ioctls: `fscrypt_ioctl_add_key()`, `fscrypt_ioctl_remove_key()`, `fscrypt_ioctl_remove_key_all_users()`, and `fscrypt_ioctl_get_key_status()`.
- Provisioning key support: `key_type_fscrypt_provisioning` and `get_keyring_key()` let userspace provide key material via a constrained keyring key.
- Test helpers: `fscrypt_get_test_dummy_key_identifier()` and `fscrypt_add_test_dummy_key()`.

## Control Flow
Adding a key validates the user argument, checks privileges for descriptor-based v1 keys, loads raw key material either directly or from an fscrypt-provisioning key, initializes HKDF and key identifiers for v2 keys, and inserts or revives the master key under `fscrypt_add_key_mutex`. Removing a key first removes the current user claim or all user claims, then transitions the master key from present to incompletely removed by wiping secret material and dropping the present active reference. If unlocked inodes remain, the code syncs the filesystem, prunes dentries for decrypted inodes, and reports busy-file status if eviction cannot complete.

## State and Persistence
Keyring state is per mounted superblock in `sb->s_master_keys`. Master-key objects track secret material, user claims, decrypted inodes, prepared per-mode keys, active refs, structural refs, and `mk_present`. The Linux keyring entries in `mk_users` represent which users have added a v2 key. No keys are persisted to disk by this code; userspace must re-add them after remount.

## Dependencies and Integration
The implementation depends on Linux keyrings, capabilities, RCU hash traversal, refcounting, key quotas, blk-crypto software-secret derivation for hardware-wrapped keys, HKDF, dcache/inode eviction, and fscrypt key setup. It is consumed by `keysetup.c`, `policy.c`, filesystem ioctl handlers, and unmount teardown.

## Risks and Edge Cases
- Active and structural refs intentionally mean different things; incorrect ref handling could leave removed keys in the hash table or free them while lookups race.
- `mk_present` is read locklessly in some paths and must be updated with `WRITE_ONCE()`.
- Removal can be incomplete if decrypted inodes remain busy; userspace must inspect status flags.
- Descriptor-based keys are privileged because descriptors are not cryptographic identifiers.
- Hardware-wrapped keys use a distinct key-identifier HKDF context to avoid collisions with raw software secrets.
- `mk_users->keys.nr_leaves_on_tree` is inspected under `mk_sem`; user-claim races must stay serialized.

## Test Signals
Use fscrypt ioctl tests for add/remove/status under one user and multiple users, descriptor privilege checks, provisioning-key type/flag mismatch, hardware-wrapped add paths, re-adding incompletely removed keys, busy inode status flags, unmount teardown, and KCSAN/lockdep coverage for RCU/refcount/keyring interactions.
