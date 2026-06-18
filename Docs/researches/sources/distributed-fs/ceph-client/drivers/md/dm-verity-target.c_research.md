# sources/distributed-fs/ceph-client/drivers/md/dm-verity-target.c

## Purpose
`dm-verity-target.c` implements the `verity` device-mapper target for transparent read-only block integrity verification. It maps reads to a data device, verifies returned blocks against a Merkle hash tree stored on a hash device, handles corruption and I/O error policies, optionally repairs data via FEC, optionally verifies the root hash signature at table load, and exposes status/IMA/LSM metadata.

## Important APIs, Types, and Functions
Key functions include `verity_hash()`, `verity_hash_at_level()`, `verity_verify_level()`, `verity_hash_for_block()`, `verity_recheck()`, `verity_handle_data_hash_mismatch()`, `verity_verify_io()`, `verity_end_io()`, `verity_map()`, `verity_status()`, `verity_parse_opt_args()`, `verity_setup_hash_alg()`, `verity_setup_salt_and_hashstate()`, `verity_ctr()`, `verity_dtr()`, `dm_verity_get_mode()`, `dm_verity_get_root_digest()`, and `dm_is_verity_target()`. The file also defines module parameters for hash prefetch sizing and bottom-half verification thresholds.

## Control Flow
Constructor parsing validates the fixed arguments, opens data/hash devices read-only, initializes hashing and salt state, parses optional behavior/FEC/signature arguments, verifies the root hash signature if requested, computes hash-tree levels and block positions, creates dm-io, dm-bufio, mempool, and verification workqueue resources, and initializes FEC. `verity_map()` rejects writes and misaligned/out-of-range I/O, installs per-bio state, prefetches hash blocks, submits the read, and lets `verity_end_io()` schedule verification. Verification walks each data block, obtains expected digests through the hash tree, hashes mapped bio data, handles zero-block optimization, and finishes the original bio with success or error.

## State and Persistence Behavior
The target is read-only and does not update the data or hash devices. Persistent trust comes from immutable table parameters: root digest, salt, hash algorithm, block geometry, hash start, and optional FEC/signature inputs. Runtime state includes cached verified hash buffers in dm-bufio auxiliary data, optional `validated_blocks` for `check_at_most_once`, corruption counters, `hash_failed`, and workqueue/mempool state.

## Dependencies and Integration Points
The file integrates with device-mapper target registration, dm-bufio for hash block caching, dm-io for recheck reads, Linux crypto or optimized SHA-256 library paths, workqueues including optional `system_bh_wq`, audit logging, reboot/panic policies, security hooks for LSM integrity metadata, FEC helpers, and signature helpers. It exports query functions used by LoadPin and other kernel code.

## Risks and Test Signals
Critical risks are accepting corrupted data, deadlocking or sleeping in bottom-half verification, incorrect hash-tree level math, signature option parsing errors, and unsafe `check_at_most_once` use after underlying data changes. Tests should cover valid reads, metadata corruption, data corruption with each mode, I/O errors with error modes, FEC recovery and failure, zero-block substitution, root hash signature required/missing/invalid, tasklet fallback on `-EAGAIN`, status table round trips, and LSM preresume metadata.
