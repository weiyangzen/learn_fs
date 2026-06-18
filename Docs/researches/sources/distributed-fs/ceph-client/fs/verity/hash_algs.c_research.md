<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/hash_algs.c -->
# sources/distributed-fs/ceph-client/fs/verity/hash_algs.c

Purpose: Defines fs-verity supported hash algorithms and provides hashing helpers for Merkle blocks, descriptors, salted initial states, and startup sanity checks.

Important APIs, types, and functions: Exports `fsverity_hash_algs`, `fsverity_get_hash_alg()`, `fsverity_prepare_hash_state()`, `fsverity_hash_block()`, `fsverity_hash_buffer()`, and `fsverity_check_hash_algs()`.

Control flow: Algorithm lookup validates the fs-verity algorithm number and logs unknown ids. Salt preparation pads salt to the hash compression block size, initializes SHA-256 or SHA-512 state, feeds the padded salt, and returns a duplicated initial context. Block hashing either hashes directly when unsalted or clones the precomputed state, updates with a full Merkle block, and finalizes. Buffer hashing dispatches to one-shot SHA helpers. Init-time checks assert nonzero algorithm ids, maximum digest sizes, power-of-two digest and block sizes, and mapping to `HASH_ALGO_*`.

State and persistence: Static algorithm table is immutable. Salted hash states are allocated per Merkle tree parameter set and freed by callers. No persistent storage is written.

Dependencies and integration points: Used by enable, open, measure, signature, and verify paths. Depends on SHA library helpers, `hash_digest_size`, and fs-verity public algorithm numbering.

Risks and test signals: Risks include algorithm-number ABI drift, salted hashing incompatibility, missing digest-size validation, and BUG paths for unsupported algorithms. Test SHA-256 and SHA-512 enable/verify, salted and unsalted files, invalid algorithm ids, and startup sanity on modified algorithm tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/hash_algs.c -->
