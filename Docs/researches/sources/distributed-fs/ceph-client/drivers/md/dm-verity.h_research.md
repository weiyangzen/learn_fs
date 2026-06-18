# sources/distributed-fs/ceph-client/drivers/md/dm-verity.h

## Purpose
`dm-verity.h` is the shared internal interface for the dm-verity target, FEC helper, signature helper, and LoadPin integration. It defines the target's configuration/runtime state and per-bio verification state.

## Important APIs, Types, and Functions
Important definitions include `DM_VERITY_MAX_LEVELS`, `enum verity_mode`, `enum verity_block_type`, `struct dm_verity`, `struct pending_block`, and `struct dm_verity_io`. Exported helpers include `verity_hash()`, `verity_hash_for_block()`, `dm_is_verity_target()`, `dm_verity_get_mode()`, and `dm_verity_get_root_digest()`.

## Control Flow
The main target allocates and initializes `struct dm_verity` in its constructor and stores it in `ti->private`. Each mapped bio receives a `struct dm_verity_io` from device-mapper per-bio storage. Verification code fills `pending_block` entries with expected and actual digests, possibly batches two SHA-256 blocks, and uses the flexible hash context field at the end of `dm_verity_io`.

## State and Persistence Behavior
`struct dm_verity` contains immutable table-derived state such as data/hash devices, block sizes, hash levels, root digest, salt, algorithm, and hash tree layout, plus runtime state such as `hash_failed`, corruption counters, `validated_blocks`, workqueue, dm-io client, and recheck mempool. It does not write persistence; it describes how persistent hash metadata is interpreted.

## Dependencies and Integration Points
The header depends on dm-io, dm-bufio, device-mapper, interrupt support, crypto shash, and SHA-2. FEC, signature verification, the main target, and LoadPin trust checks all include it.

## Risks and Test Signals
Risks include per-IO data size miscalculation due to the variable-length hash context, digest-size assumptions exceeding `HASH_MAX_DIGESTSIZE`, and mode semantics consumed by external callers. Tests should validate constructor-calculated `per_io_data_size`, SHA-256 optimized vs generic crypto paths, root digest copy ownership, and target identity checks.
