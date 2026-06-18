# sources/distributed-fs/ceph-client/drivers/md/bcache/debug.c

Purpose: provides optional bcache debug verification and debugfs dumping. Under `CONFIG_BCACHE_DEBUG`, it verifies in-memory B-tree contents against a disk reread and compares cached read data against backing storage. Under `CONFIG_DEBUG_FS`, it exposes a per-cache-set debugfs file that streams textual extent keys.

Important APIs/functions: `bch_btree_verify()` rereads a B-tree node, runs normal node read validation/sort on the debug copy, and panics with detailed dumps if the in-memory sorted keys differ from disk. `bch_data_verify()` reads the backing device for a completed bio and checks cache-returned data byte-for-byte. `bch_debug_init_cache_set()` creates a `bcache-<uuid>` debugfs file. `bch_debug_init()` creates the root `bcache` debugfs directory and `bch_debug_exit()` removes it.

Control flow: B-tree verification takes the node I/O mutex and cache-set verify mutex, reads the on-disk node into a scratch B-tree, calls `bch_btree_node_read_done()`, and compares sorted bsets. On mismatch it dumps in-memory, reread, and raw on-disk bsets before `panic()`. Data verification allocates a temporary bio with pages, reads the same backing-sector range, iterates both bios segment-by-segment, and reports cache-set errors on mismatches. The debugfs read path uses a `dump_iterator`, `bch_keybuf_next_rescan()`, and `bch_extent_to_text()` to refill a page buffer one key at a time.

State and persistence: debug code does not mutate persistent metadata, but it reads cache buckets and backing devices directly. `bch_btree_verify()` uses `c->verify_ondisk` and `c->verify_data` scratch storage allocated by B-tree cache setup. The debugfs iterator owns an independent keybuf whose `last_scanned` starts at key zero.

Dependencies/integration: depends on B-tree read validation, keybuf scanning, extent text formatting, `debugfs`, `seq_file` support, Linux bio helpers, and cache-set error handling. Request read completion can call `bch_data_verify()` when device verification is enabled.

Risks: debug verification is intentionally fatal on mismatch and can add high I/O and memory pressure. The debugfs implementation has a comment noting missing cache-set refcounting, so teardown while a dump file is open is a lifetime risk. Test signals include enabling `CONFIG_BCACHE_DEBUG` and `CONFIG_DEBUG_FS`, reading debugfs during active I/O, forced data mismatch detection, and ensuring non-debug builds compile to header stubs.
