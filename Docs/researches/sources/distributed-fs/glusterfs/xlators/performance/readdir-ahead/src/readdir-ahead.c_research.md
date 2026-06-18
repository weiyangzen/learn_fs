# sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/src/readdir-ahead.c

## Purpose
Implements `performance/readdir-ahead`, which converts small sequential `readdirp` requests into larger child `readdirp` prefetches. It buffers directory entries per fd, serves sequential callers from the buffer, disables itself on non-sequential access, maintains a global cache limit, and refreshes or invalidates entry `iatt` data when file metadata changes during prefetch.

## Important APIs, Types, And Functions
Main fops are `rda_opendir`, `rda_readdirp`, mutation fops for data and metadata writes, and cbks `rda_releasedir`/`rda_forget`. `get_rda_fd_ctx()` creates `rda_fd_ctx` with state flags such as `RDA_FD_NEW`, `RUNNING`, `EOD`, `ERROR`, `BYPASS`, and `PLUGGED`. `rda_fill_fd()` and `rda_fill_fd_cbk()` drive internal prefetch. `__rda_fill_readdirp()` and `__rda_serve_readdirp()` move entries from cache to the caller. `rda_inode_ctx_update_iatts()` maintains per-inode stat snapshots and generation counters. `RDA_COMMON_MODIFICATION_FOP` wraps mutation calls to update inode stat state after success.

## Control Flow
`opendir` stores md-cache xdata keys and starts a filler. `rda_readdirp()` checks fd context state under lock; if the offset is unexpected or another user stub is pending, it marks bypass and sends the request to the child. Otherwise it serves from cache when enough data, EOD, or error state exists; if not, it stores a single pending stub and ensures the filler is running. The filler issues large child `readdirp` calls at `next_offset`, appends returned entries to `ctx->entries`, updates cache accounting, handles EOD/error, wakes a pending stub when possible, and continues until bypass, EOD, error, or cache limit stops it.

## State And Persistence
Per-fd state includes current served offset, next prefetch offset, cached byte size, state flags, pending stub, fill frame, xdata keys, writes-during-prefetch dictionary, atomic prefetch counter, and cached dirent list. Translator-private state stores request size, watermarks, cache limit, global cache size, and `parallel-readdir`. Per-inode context stores the latest trusted `iatt` and a generation counter. All state is in memory and freed on `releasedir` or inode forget.

## Dependencies And Integration Points
Uses Gluster call stubs, fd/inode contexts, gf_dirent lists, dict APIs, atomic counters, child `readdirp`, mutation fops, md-cache xdata propagation, and option parsing. It is sensitive to write-behind because write-behind may return cached write responses with invalid or delayed `iatt`, so this translator invalidates stat snapshots when needed.

## Risks
Only one pending user stub is supported; concurrent or out-of-order reads force bypass. Cache-limit handling stops prefetch globally, which can affect unrelated directories. `parse` and generation logic for writes during prefetch is subtle: missing an invalidation can expose stale `d_stat`, while over-invalidation loses metadata-cache value. `rda_releasedir()` logs but does not unwind a pending stub, so release with in-flight user request is a serious lifecycle anomaly. `parallel-readdir` is parsed but not directly used in this file, implying cross-translator behavior or dead configuration.

## Test Signals
Test sequential `ls`-style reads, offset resets to zero after EOD, non-sequential offsets, concurrent callers, cache high/low watermark transitions, global cache-limit stop, child `ENOENT`/error propagation, md-cache xdata reuse, writes/truncates/xattr/setattr during active prefetch, and releasedir while fill is active. Check cache-size accounting returns to zero after release.
