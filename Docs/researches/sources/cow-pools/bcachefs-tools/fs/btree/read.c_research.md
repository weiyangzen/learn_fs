# File Research: sources/cow-pools/bcachefs-tools/fs/btree/read.c

Read completeness: full file read, 1320 lines.

Purpose: btree node read, validation, retry, normalization, root read, and scrub logic. This file turns on-disk btree-node buffers into in-memory btree nodes with one sorted bset, handles checksum/encryption/version compatibility, retries readable replicas, logs hard and soft errors, and schedules repairs when needed.

Major components:
- IO lock and wait helpers: `bch2_btree_node_io_lock()`, `bch2_btree_node_io_unlock()`, `bch2_btree_node_wait_on_read()`, and `bch2_btree_node_wait_on_write()` coordinate node IO flags and submit queued write bios before sleeping.
- Error reporting: `btree_err_msg()` and `__btree_err()` attach device, node offset, bset offset, fsck error id, retry state, and read/write context to validation errors.
- Topology repair helper: `bch2_btree_node_drop_keys_outside_node()` removes keys outside a repaired node range and rebuilds aux search trees.
- Validation: `bch2_validate_bset()` validates bset version, checksum mode flags, offsets, header identity, min/max keys, and key format; `bch2_validate_bset_keys()` validates individual packed keys, ordering, compatibility conversion, and can drop damaged keys when fsck permits.
- Main read completion: `bch2_btree_node_read_done()` walks all bsets in a node, verifies checksum/decrypts, validates metadata, skips blacklisted non-first bsets, sorts and de-overlaps keys through `bch2_key_sort_fix_overlapping()`, rebuilds the node into one bset, validates values, clears in-memory btree pointer fields, and marks nodes for rewrite when needed.
- Asynchronous read path: `btree_node_read_endio()` queues `btree_node_read_work()`, which retries alternate replicas, records IO failures, schedules rewrite after soft errors, and queues merge work for very empty nodes.
- Public read entry: `bch2_btree_node_read()` chooses a read device, allocates a `btree_read_bio`, maps the btree node buffer, and submits sync or async IO.
- Root loading: `bch2_btree_root_read()` allocates a cache node, reads it synchronously, transitions cache state, and installs the root for reads.
- Scrub: `bch2_btree_node_scrub()` reads one pointer replica into a bounce buffer and `btree_node_scrub_work()` rewrites the btree pointer key if checksum/magic validation fails.

Control-flow and invariants:
- Read validation uses the same bset/key validation functions as write validation, with compatibility transforms applied before/after on-disk version checks.
- `bch2_btree_node_read_done()` always collapses read bsets into one sorted in-memory bset and sets aux trees and whiteout flags for normal in-memory operation.
- If `btree_ptr_v2.sectors_written` is zero, the node is accepted but marked `need_rewrite_ptr_written_zero`.
- Blacklisted journal sequence handling distinguishes first bset from later bsets and pointer-written from legacy full-node reads.
- Read retry tracks per-device failures in `struct bch_io_failures` and only reports hard lost data when no readable replica remains.

Dependencies and integration:
- Uses `btree/sort.h` for sorting and bounce allocation, `btree/update.h` for rewrite scheduling, `btree/write.h` for IO wait behavior, checksum/encryption helpers, journal sequence blacklist, recovery state, and device IO accounting.
- Exports functions declared in `read.h`; used by node scan, cache/root loading, scrub/fsck, and normal traversal paths.

Risks and validation notes:
- The file is deliberately fsck-aware: many corruptions can be fixed by truncating/dropping keys or updating superblock versions, but write-time corruption triggers emergency read-only.
- Compatibility transforms mutate bset/node/key fields during validation; callers must pass the correct read/write direction.
- Scrub only handles `KEY_TYPE_btree_ptr_v2` and does not fully rebuild the in-memory node; it checks magic/checksums and requests rewrite through transaction code.
