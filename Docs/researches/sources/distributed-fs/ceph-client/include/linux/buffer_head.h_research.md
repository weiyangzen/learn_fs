## sources/distributed-fs/ceph-client/include/linux/buffer_head.h

**Purpose:** This header defines the legacy `buffer_head` abstraction used by filesystems and block helpers to track block mappings, state flags, and buffer-backed folio I/O.

**Important APIs/types/functions:** `enum bh_state_bits` defines state such as `BH_Uptodate`, `BH_Dirty`, `BH_Lock`, `BH_Mapped`, `BH_Delay`, `BH_Unwritten`, and `BH_Meta`. `struct buffer_head` stores state bits, circular folio/page linkage, block number, size, data pointer, block device, completion callback/private data, metadata association, refcount, and uptodate lock. Macro families generate `set_buffer_*`, `clear_buffer_*`, and `buffer_*` helpers. APIs cover allocation, lookup/read (`__find_get_block`, `bdev_getblk`, `__bread_gfp`, `sb_bread`), dirty/writeback, locking/waiting, submit, block write/read helpers, migration, metadata-buffer lists, and optional buffer-head LRU management.

**Control flow, state, persistence:** Buffer state is bit-based and refcounted. Reads lock buffers and submit block I/O when not uptodate; write helpers mark dirty and submit; `brelse()`/`bforget()` drop references or discard dirty state. Data persistence occurs only through block I/O initiated by implementation functions.

**Dependencies/integration:** Depends on block, fs, pagemap, waitqueue, atomic, migration, and folio APIs. It integrates with legacy filesystems, superblocks, block devices, and address-space operations.

**Risks and test signals:** Risks include stale uptodate barriers, leaked refs, buffer/folio aliasing bugs, dirty-state loss, migration races, and incorrect use in highmem or no-`CONFIG_BUFFER_HEAD` builds. Test signals include filesystem write/read/truncate tests, fsync metadata tests, writeback error injection, buffer migration tests, lockdep, KASAN, and `CONFIG_BUFFER_HEAD=n` compile coverage.
