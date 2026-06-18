# File Research: sources/block-storage/stratisd/src/engine/sim_engine/pool.rs

This file implements `SimPool`, the simulator’s in-memory implementation of the `Pool` trait.

State:
- data block devices
- cache block devices
- filesystem table
- filesystem limit
- overprovisioning flag
- optional modern `EncryptionInfo`
- validated integrity spec
- optional last reencryption timestamp

Construction/reporting:
- `new()` deduplicates input paths, creates simulated data devices, sets default fs limit to 10 and overprovisioning enabled.
- JSON conversion reports available actions, fs limit, filesystems, data devices, and cache devices.
- `record()` returns a save-shaped `PoolSave`.

Filesystem behavior:
- `create_filesystems()`:
  - enforces fs limit;
  - validates sizes and names;
  - treats duplicate same-name/same-size specs idempotently;
  - rejects conflicting existing sizes.
- `destroy_filesystems()`:
  - refuses destruction when target snapshots or dependent snapshots have scheduled reverts;
  - removes existing requested filesystems;
  - rewires snapshot origins when an origin is removed.
- `rename_filesystem()` uses shared idempotent rename precheck.
- `snapshot_filesystem()`:
  - enforces fs limit;
  - validates snapshot name;
  - returns identity if existing target has matching size;
  - creates a new filesystem with origin set to source UUID.

Blockdev/cache behavior:
- `init_cache()`:
  - validates absolute paths;
  - rejects cache on encrypted pools when unsupported;
  - requires at least one cache path on first initialization;
  - is idempotent for matching existing cache devices.
- `add_blockdevs()`:
  - validates paths;
  - requires cache initialization before adding cache devices;
  - rejects adding a path already present in the opposite tier;
  - filters duplicates/already-present devices in the same tier.
- `set_blockdev_user_info()` validates user info as a Stratis name and returns rename-style action.
- `grow_physical()` always returns identity in simulator.

Encryption token behavior:
- `bind_clevis()` and `bind_keyring()` require encrypted pool state.
- Both enforce token-slot limits and distinguish:
  - explicit token slot;
  - automatic free slot;
  - legacy single-token behavior.
- They return identity for identical existing bindings and errors for slot/type conflicts.
- `unbind_keyring()` and `unbind_clevis()` prevent removing the last unlock method.
- Rebind methods reject empty slots and wrong mechanism types.
- Simulated Clevis rebind does not regenerate token data; it validates and returns success action.

Online encryption lifecycle:
- `start_encrypt_pool()`:
  - identity if already encrypted;
  - otherwise converts input encryption info and stores it;
  - returns dummy sector/key info.
- `do_encrypt_pool()` and `finish_encrypt_pool()` are no-ops.
- `start_reencrypt_pool()` errors if unencrypted; otherwise returns empty key info.
- `do_reencrypt_pool()` is a no-op.
- `finish_reencrypt_pool()` sets `last_reencrypt = Some(Utc::now())` and returns `ReencryptedDevice`.
- `decrypt_pool_idem_check()` returns identity if unencrypted or deleted action if encrypted.
- `do_decrypt_pool()` is a no-op.
- `finish_decrypt_pool()` clears encryption info and last reencryption timestamp.

Properties and metadata:
- Physical size is simulated as very large, allocated size as fixed, used as zero.
- `metadata_version()` returns v2.
- Current/last pool and filesystem metadata are serialized JSON from simulator state.
- `free_token_slots()` derives from encryption info.
- `volume_key_is_loaded()` and `load_volume_key()` always return false.
- `avail_actions()` is always full.
- `out_of_alloc_space()` is always false.
- `set_fs_limit()` only allows increasing the limit.
- `set_overprov_mode()` stores the requested value.

Merge scheduling:
- `set_fs_merge_scheduled()` validates origin presence and prevents ambiguous chained or competing scheduled reverts before updating the filesystem flag.

Tests:
- Cover filesystem rename, destroy, create, duplicates, and device addition behavior.

Role in architecture:
- This is the main behavioral simulator for pool operations. It mirrors real engine idempotence and validation semantics where practical, while stubbing actual storage, crypto, and device-mapper operations.
