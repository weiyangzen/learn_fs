<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/verify.c -->
# sources/distributed-fs/ceph-client/fs/verity/verify.c

Purpose: Verifies file data against fs-verity Merkle trees during reads and provides readahead and async workqueue helpers for filesystem integrations.

Important APIs, types, and functions: Defines `struct fsverity_pending_block`, `struct fsverity_verification_context`, `fsverity_readahead()`, `is_hash_block_verified()`, `verify_data_block()`, `fsverity_verify_blocks()`, optional `fsverity_verify_bio()`, `fsverity_enqueue_verify_work()`, and `fsverity_init_workqueue()`.

Control flow: Readahead maps a data page range to needed hash-page ranges at each Merkle level and calls filesystem `readahead_merkle_tree`. Verification batches one or two data blocks, maps their folio data, hashes them, then `verify_data_block()` ascends from leaf hashes to the root until it finds an already verified hash block or reaches the root. It then descends, hashing each unverified hash block, comparing expected versus real hashes, marking hash blocks verified, and finally comparing the data block hash. EOF-spanning sub-page blocks past file size must be all zeroes. Bio verification iterates folios from completed read bios and sets `BLK_STS_IOERR` on failure.

State and persistence: Uses per-inode `fsverity_info` root hash, tree topology, optional salted hash state, and hash-block verification state. Verification marks hash pages `PG_checked` or sets bitmap bits for sub-page block sizes; no persistent metadata is changed.

Dependencies and integration points: Called by filesystem read_folio/readahead/bio completion paths. Depends on filesystem `read_merkle_tree_page` and optional readahead operation, page/folio mapping, block layer when enabled, SHA optimized two-block hashing, tracepoints, and high-priority per-CPU workqueue.

Risks and test signals: Risks include trusting evicted hash pages, bitmap and `PG_checked` memory-ordering bugs, kmap nesting limits, corrupted-tree diagnostics, EOF zero verification, block alignment assumptions, and async verification latency. Test valid and corrupted data blocks, corrupted hash blocks at every level, cache eviction and reread, sub-page Merkle blocks, EOF partial pages, bio and non-bio filesystems, concurrent reads of the same hash blocks, and workqueue initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/verify.c -->
