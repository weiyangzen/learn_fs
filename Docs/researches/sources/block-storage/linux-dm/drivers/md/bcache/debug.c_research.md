# File Research: sources/block-storage/linux-dm/drivers/md/bcache/debug.c

## Purpose
Provides bcache debug and verification helpers, including btree readback verification, data verification against backing devices, and debugfs dumping of cache-set keys.

## Main Interfaces
- Global debugfs root: `bcache_debug`.
- Under `CONFIG_BCACHE_DEBUG`: `bch_btree_verify()` and `bch_data_verify()`.
- Under `CONFIG_DEBUG_FS`: `bch_debug_init_cache_set()` and debugfs file operations for dumping btree extents.
- Lifecycle: `bch_debug_init()`, `bch_debug_exit()`.

## Control Flow
`bch_btree_verify()` reads the just-written btree node from disk into verification buffers, parses/sorts it with normal read completion logic, compares it with the in-memory sorted version, and panics with detailed dumps on mismatch. `bch_data_verify()` rereads backing-device data and compares bio segments. Debugfs dump reads keys through a `keybuf`, formats each extent, and streams lines to userspace.

## State And Synchronization
Btree verification takes the node `io_mutex` and cache-set `verify_lock`. Debugfs dumping owns a per-open `dump_iterator` and keybuf; cache-set refcounting is explicitly noted as incomplete by a comment.

## Integration Points
Uses btree parsing/sorting from `btree.c`/`bset.c`, extent formatting from `extents.c`, bbio helpers, debugfs, seq/file APIs, and the global bcache debug directory also used by closure debugging.

## Notable Behaviors
- Verification is intentionally fatal on mismatch, dumping in-memory, readback, and on-disk bsets.
- `bch_debug_init()` ignores debugfs creation failures by design.
- Debugfs cache-set files are named `bcache-<uuid>`.

## Risks And Review Focus
- Verification IO runs in debug paths but still touches live metadata locks and buffers.
- Debugfs dump lacks robust cache-set lifetime management per the inline comment.
- Data verification allocates a mirror bio and must keep segment iteration aligned.
