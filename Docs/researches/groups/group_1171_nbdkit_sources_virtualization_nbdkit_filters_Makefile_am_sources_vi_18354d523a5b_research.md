# Group Research: group_1171_nbdkit_sources_virtualization_nbdkit_filters_Makefile_am_sources_vi_18354d523a5b

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/Makefile.am

Purpose: top-level Automake entry for the nbdkit filter directory.

Key details:
- Includes `$(top_srcdir)/common-rules.mk`.
- Distributes `filters.syms`, the linker version script used by many filter subdirectories.
- Delegates recursive build traversal to `SUBDIRS = $(filters)`, so the actual filter set is controlled by the configured `filters` variable outside this file.

Integration notes:
- This file is pure build orchestration; adding/removing filters depends on the higher-level configure/build variables, not local hard-coded subdir names.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/blocksize-policy/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/blocksize-policy/Makefile.am

Purpose: builds the `nbdkit-blocksize-policy-filter.la` module and its optional man page.

Key details:
- Sources are `policy.c` plus `include/nbdkit-filter.h`.
- Includes nbdkit public headers, generated headers, `common/include`, and `common/utils`.
- Links `common/utils/libutils.la`, `common/replacements/libcompat.la`, and Windows import support.
- Adds `filters/filters.syms` as a linker version script when `USE_LINKER_SCRIPT` is enabled.
- Generates `nbdkit-blocksize-policy-filter.1` from POD when `HAVE_POD` is available.

Integration notes:
- The build depends on common utility helpers for parsing/rounding/power-of-two support used by `policy.c`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/blocksize-policy/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/blocksize-policy/policy.c -->
# File Research: sources/virtualization/nbdkit/filters/blocksize-policy/policy.c

Purpose: filter that advertises and enforces NBD block-size policy, optionally rejecting requests that violate minimum/maximum/alignment constraints.

Key details:
- Configures `blocksize-error-policy`, `blocksize-minimum`, `blocksize-preferred`, `blocksize-maximum`, and `blocksize-write-disconnect`.
- Error policy modes are `allow`, `error`, and `strict-error`; `error` permits unaligned final tails by rounding the checked count up at EOF.
- `policy_block_size` merges user-configured constraints with backend-advertised constraints, synthesizing defaults when needed.
- `check_policy` rejects misaligned offsets, undersized counts, oversized data requests, and counts not divisible by minimum block size with `EINVAL`.
- `policy_pwrite` can force client disconnect on writes larger than `blocksize-write-disconnect`.
- `policy_can_extents` forces extents support so `.extents` can align backend results even when the plugin lacks native extents.
- Registered callbacks include `.block_size`, `.pread`, `.pwrite`, `.zero`, `.trim`, `.cache`, and `.extents`.

Risk notes:
- In `policy_config_complete`, the maximum multiple check uses `config_maximum % config_maximum`, which is always zero for nonzero values; it likely intended `config_maximum % config_minimum`. This weakens validation.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/blocksize-policy/policy.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/blocksize/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/blocksize/Makefile.am

Purpose: builds the `nbdkit-blocksize-filter.la` module and optional man page.

Key details:
- Sources are `blocksize.c` and `include/nbdkit-filter.h`.
- Includes nbdkit headers, generated headers, `common/include`, and `common/utils`.
- Links utility, replacement compatibility, and Windows import libraries.
- Applies the shared filter symbol version script when configured.
- Generates `nbdkit-blocksize-filter.1` from POD under `HAVE_POD`.

Integration notes:
- This build mirrors the blocksize-policy filter but compiles the transforming blocksize implementation rather than just policy enforcement.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/blocksize/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/blocksize/blocksize.c -->
# File Research: sources/virtualization/nbdkit/filters/blocksize/blocksize.c

Purpose: adapts arbitrary client request sizes to an underlying plugin’s stricter block-size requirements.

Key details:
- Configures `minblock`, `maxdata`, and `maxlen`.
- Validates `minblock` as a power of two no larger than 64 KiB; `maxdata`/`maxlen` must align to `minblock` when both are set.
- Per-connection handle values are finalized in `.prepare` by combining user configuration with backend block-size constraints.
- Advertises permissive client constraints: minimum `1`, maximum `0xffffffff`, and preferred at least `4096`/`minblock`.
- Uses a global `pthread_rwlock_t` and one shared bounce buffer for unaligned head/tail handling.
- `.pread` splits unaligned requests into aligned backend reads plus buffer copies.
- `.pwrite` and `.zero` use read-modify-write for unaligned heads/tails; aligned bodies use shared read locks.
- FUA is emulated by clearing `NBDKIT_FLAG_FUA` and flushing when the backend reports `NBDKIT_FUA_EMULATE`.
- `.trim` ignores unaligned edges and trims only aligned body regions.
- `.extents` asks backend for block-aligned extents and copies them to the caller.
- `.cache` rounds requested ranges outward to aligned backend cache calls.

Risk notes:
- Serialization is centered on one bounce buffer; correctness depends on using exclusive locking on every bounce-buffer path.
- Size is rounded down to `minblock`, so clients see a truncated virtual size when backend size is not aligned.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/blocksize/blocksize.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/bzip2/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/bzip2/Makefile.am

Purpose: conditionally builds the bzip2 decompression filter.

Key details:
- Guarded by `HAVE_BZLIB`.
- Builds `nbdkit-bzip2-filter.la` from `bzip2.c`.
- Includes nbdkit headers, replacement headers, common includes, and utility headers.
- Links `BZLIB_LIBS`, `common/utils`, `common/replacements`, and Windows import support.
- Uses shared filter symbol script when enabled.
- Generates `nbdkit-bzip2-filter.1` from POD when `HAVE_POD`.

Risk notes:
- CFLAGS include `$(ZLIB_CFLAGS)` while linking `$(BZLIB_LIBS)`; this may be intentional carryover from gzip-like filters or a build variable mismatch worth checking.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/bzip2/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/bzip2/bzip2.c -->
# File Research: sources/virtualization/nbdkit/filters/bzip2/bzip2.c

Purpose: exposes a bzip2-compressed backend as a read-only uncompressed NBD export.

Key details:
- Opens the underlying plugin read-only regardless of requested mode.
- On first `.prepare`, protected by a mutex, fully decompresses the backend into an unlinked temporary file.
- Uses `BZ2_bzDecompressInit`, streaming 4 MiB input/output buffers, and records compressed and uncompressed sizes.
- `bzip2_get_size` returns the decompressed size and rejects use if the backend compressed size changes after decompression.
- `.pread` services reads from the temporary uncompressed file with full retry-on-short-read behavior.
- Forces `can_write = 0`, `can_multi_conn = 1`, `can_extents = 0`, and `can_cache = NBDKIT_CACHE_EMULATE`.
- Export description is prefixed with “expansion of bzip2-compressed image”.
- `.unload` closes the temporary file descriptor.

Risk notes:
- Entire image is decompressed before serving size/read data; startup latency and temporary storage requirements scale with decompressed size.
- The bzip2 format lacks embedded uncompressed size, explaining the eager full decompression.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/bzip2/bzip2.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/cache/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/cache/Makefile.am

Purpose: builds the Unix-only cache filter module.

Key details:
- Guarded by `!IS_WINDOWS` because reclaim/hole punching and related filesystem behavior are OS-specific.
- Builds `nbdkit-cache-filter.la` from `blk.c`, `blk.h`, `cache.c`, `cache.h`, `lru.c`, `lru.h`, `reclaim.c`, and `reclaim.h`.
- Includes nbdkit headers, generated headers, `common/bitmap`, `common/include`, and `common/utils`.
- Links bitmap and utility libraries plus Windows import support placeholder.
- Adds linker symbol script when configured.
- Generates `nbdkit-cache-filter.1` from POD when available.

Integration notes:
- This Makefile binds together the cache front-end, block store, LRU heuristic, and reclaim state machine.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/cache/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/cache/blk.c -->
# File Research: sources/virtualization/nbdkit/filters/cache/blk.c

Purpose: block-level backing store for the cache filter.

Key details:
- Creates an unlinked temporary file under `TMPDIR` or `LARGE_TMPDIR`.
- Chooses `blksize` as `max(cache-min-block-size, statvfs.f_bsize)` to support hole punching.
- Maintains a two-bit bitmap per block: not cached, clean, or dirty.
- Initializes and resizes bitmap/LRU state alongside the sparse temp file.
- `blk_read_multiple` groups adjacent cached or uncached runs; uncached reads go to the backend, cached reads go to the temp file.
- `cache-on-read` copies backend reads into the temp file as clean blocks.
- `blk_cache` explicitly caches a block or issues `posix_fadvise` for already cached blocks.
- `blk_writethrough` writes both temp cache and backend, marking clean.
- `blk_write` writes dirty blocks in writeback/unsafe mode, but delegates to writethrough for writethrough mode or writeback+FUA.
- `for_each_dirty_block` scans the bitmap and invokes a callback for dirty blocks.

Integration notes:
- Callers are required to hold the cache filter’s exclusive lock around these functions.
- Calls `reclaim` before operations that may allocate more cache space.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/cache/blk.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/cache/blk.h -->
# File Research: sources/virtualization/nbdkit/filters/cache/blk.h

Purpose: declares the cache filter’s block-store API.

Key details:
- Exposes lifecycle: `blk_init`, `blk_free`, and `blk_set_size`.
- Declares block read/cache/write paths: `blk_read`, `blk_read_multiple`, `blk_cache`, `blk_writethrough`, and `blk_write`.
- Defines `block_callback` and `for_each_dirty_block` for flush scanning.
- Documents that callers must hold an exclusive lock for all operations after initialization/free.

Integration notes:
- This header is the contract between `cache.c` and the temp-file/bitmap implementation in `blk.c`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/cache/blk.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/cache/cache.c -->
# File Research: sources/virtualization/nbdkit/filters/cache/cache.c

Purpose: main nbdkit cache filter that layers a local temporary block cache over a backend plugin.

Key details:
- Global configuration includes `cache=writeback|writethrough|unsafe`, `cache-min-block-size`, optional reclaim thresholds, and `cache-on-read`.
- `cache_on_read` supports static boolean mode or path-triggered mode.
- `.get_ready` initializes the block cache; `.prepare` forces early size discovery and cache sizing.
- `.block_size` advertises cache-friendly preferred size while preserving backend constraints.
- Overrides `.can_cache` to native because this filter handles caching.
- Overrides `.can_fast_zero` to advertise support but rejects fast zero attempts.
- `cache_pread` handles unaligned heads/tails with temporary buffers and delegates block reads to `blk.c`.
- `cache_pwrite` performs read-modify-write for unaligned writes, handles FUA emulation, and flushes when needed.
- `cache_zero` implements zero by writing zero-filled blocks into the cache rather than calling backend `.zero`.
- `cache_flush` scans dirty blocks, writes them through, then flushes the backend unless in unsafe mode.
- `cache_cache` rounds cache requests outward to whole cache blocks and explicitly caches them.
- Multi-connection semantics are forced true for writeback/unsafe and delegated in writethrough mode.

Risk notes:
- Writeback/unsafe semantics intentionally decouple backend persistence from client writes.
- All block operations depend on the global mutex; this is simple and safe but limits parallelism.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/cache/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/cache/cache.h -->
# File Research: sources/virtualization/nbdkit/filters/cache/cache.h

Purpose: shared configuration/state declarations for cache filter components.

Key details:
- Declares `enum cache_mode` with writeback, writethrough, and unsafe modes.
- Exposes global `blksize`, `min_block_size`, `max_size`, `hi_thresh`, and `lo_thresh`.
- Declares cache-on-read mode enum `COR_OFF`, `COR_ON`, `COR_PATH`, plus `cor_path`.
- Declares `cache_on_read()` for `blk.c`.

Integration notes:
- This header couples `cache.c`, `blk.c`, `lru.c`, and `reclaim.c` around shared runtime policy.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/cache/cache.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/cache/lru.c -->
# File Research: sources/virtualization/nbdkit/filters/cache/lru.c

Purpose: approximate LRU tracking for cache reclaim.

Key details:
- Uses two one-bit-per-block bitmaps to track recently accessed blocks.
- `lru_set_size` resizes both bitmaps and sets target window `N` to roughly a quarter of either max cache size or virtual image size, with minimum 100 blocks.
- `lru_set_recently_accessed` sets the block in `bm[0]`; when `c0 >= N/2`, it swaps `bm[0]` and `bm[1]`, clears the new `bm[0]`, and resets counters.
- `lru_has_been_recently_accessed` checks both bitmaps.
- Intended as a low-memory heuristic rather than an exact recency list.

Integration notes:
- Reclaim uses this to prefer punching holes in blocks outside the recent-access window.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/cache/lru.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/cache/lru.h -->
# File Research: sources/virtualization/nbdkit/filters/cache/lru.h

Purpose: declares the cache filter’s approximate LRU API.

Key details:
- Exposes `lru_init`, `lru_free`, and `lru_set_size`.
- Exposes `lru_set_recently_accessed` for read/write/cache paths.
- Exposes `lru_has_been_recently_accessed` for reclaim selection.

Integration notes:
- This is a small internal interface consumed by `blk.c` and `reclaim.c`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/cache/lru.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/cache/reclaim.c -->
# File Research: sources/virtualization/nbdkit/filters/cache/reclaim.c

Purpose: cache space reclaim mechanism using hole punching.

Key details:
- If `HAVE_CACHE_RECLAIM` is unavailable, `reclaim` is a no-op.
- When enabled, state machine transitions from not reclaiming to LRU reclaim once allocated cache space crosses the high threshold.
- Continues reclaiming until allocation drops below the low threshold.
- Reclaims up to two blocks per `reclaim` call.
- Starts with blocks not recently accessed according to `lru_has_been_recently_accessed`; if exhausted, switches to reclaiming any cached block.
- `reclaim_block` punches a hole with `fallocate(FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE)` and clears the cache bitmap entry.

Risk notes:
- Reclaim assumes dirty data has already been handled or that clearing the bitmap is correct for the current cache mode; call ordering and state meaning in `blk.c` are important.
- Lack of hole-punch support disables reclaim at compile time.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/cache/reclaim.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/cache/reclaim.h -->
# File Research: sources/virtualization/nbdkit/filters/cache/reclaim.h

Purpose: declares cache reclaim availability and entry point.

Key details:
- Defines `HAVE_CACHE_RECLAIM` when `FALLOC_FL_PUNCH_HOLE` is available.
- Declares `reclaim(int fd, struct bitmap *bm)`.
- Documents that reclaim must be called with the block/cache lock held.

Integration notes:
- Used by `cache.c`/`blk.c` to keep temp cache allocation below configured limits.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/cache/reclaim.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/checkwrite/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/checkwrite/Makefile.am

Purpose: builds the checkwrite filter and optional manual page.

Key details:
- Builds `nbdkit-checkwrite-filter.la` from `checkwrite.c`.
- Includes common nbdkit and utility headers.
- Links `common/utils`, `common/replacements`, and Windows import support.
- Uses `filters.syms` when linker scripts are enabled.
- Generates `nbdkit-checkwrite-filter.1` from POD when available.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/checkwrite/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/checkwrite/checkwrite.c -->
# File Research: sources/virtualization/nbdkit/filters/checkwrite/checkwrite.c

Purpose: verification filter that accepts write-like requests only when they match existing backend data.

Key details:
- Opens the backend read-only but advertises write, flush, FUA, trim, zero, fast-zero, and multi-conn support.
- `.pwrite` reads the target range from the backend and compares it to the supplied write buffer; mismatch returns `EIO`.
- Debug flag `checkwrite_debug_showdiffs` can emit hexdiffs on mismatches.
- `.flush` is a no-op.
- `.trim` and `.zero` are handled by `checkwrite_trim_zero`, which verifies the backend already reads as zero.
- Uses extents when available to skip known-zero regions and only read/check nonzero extents.
- Fast zero is rejected with `ENOTSUP` if checking would require actual reads.

Integration notes:
- Useful for validating copy/convert tools by proving write requests match a read-only expected image without mutating it.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/checkwrite/checkwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/count/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/count/Makefile.am

Purpose: builds the count filter and optional manual page.

Key details:
- Builds `nbdkit-count-filter.la` from `count.c`.
- Includes nbdkit public/generated headers.
- Links Windows import support; no extra common utility libraries are required.
- Uses the common filter symbol script when configured.
- Generates `nbdkit-count-filter.1` from POD when available.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/count/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/count/count.c -->
# File Research: sources/virtualization/nbdkit/filters/count/count.c

Purpose: lightweight accounting filter for read/write/zero/trim byte totals.

Key details:
- Maintains atomic counters for bytes read, written, zeroed, and trimmed.
- Wraps `.pread`, `.pwrite`, `.trim`, and `.zero`, incrementing counters only after successful downstream operations.
- `.unload` logs final totals with `nbdkit_debug`.
- Falls back to non-atomic `_Atomic` macro on platforms without `<stdatomic.h>`.

Risk notes:
- On platforms without atomics, counters are explicitly “atomic enough” only for statistics, not strict concurrency accuracy.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/count/count.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/cow/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/cow/Makefile.am

Purpose: builds the copy-on-write filter and optional manual page.

Key details:
- Builds `nbdkit-cow-filter.la` from `blk.c`, `blk.h`, `cow.c`, and `cow.h`.
- Includes `common/bitmap`, `common/include`, `common/replacements`, and `common/utils`.
- Links bitmap, utility, replacement compatibility, and Windows import support.
- Applies shared filter version script when configured.
- Generates `nbdkit-cow-filter.1` from POD when available.

Integration notes:
- Unlike the cache filter, this filter supports persistent-in-process overlay state per export rather than a cache persistence policy.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/cow/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/cow/blk.c -->
# File Research: sources/virtualization/nbdkit/filters/cow/blk.c

Purpose: block-level sparse overlay implementation for the COW filter.

Key details:
- Uses unlinked temporary files as sparse overlays.
- Splits overlays into multiple files when virtual size exceeds `MAX_FILE_SIZE` of 8 TiB.
- Maintains a two-bit bitmap per overlay block: not allocated, allocated, or trimmed.
- `blk_create` initializes the first temporary file, mutex, and bitmap.
- `blk_set_size` resizes bitmap and overlay file vector, creating/removing temp files as needed and truncating each file.
- `blk_status` exposes overlay presence/trim state to extent synthesis.
- `blk_read_multiple` groups runs with identical bitmap state and same temp-file shard; reads backend, overlay, or returns zeroes for trimmed blocks.
- Optional cow-on-read writes backend-read data into overlay and marks blocks allocated.
- `blk_cache` can ignore, pass through backend cache, read backend, or copy backend data into the overlay depending on cache mode.
- `blk_write` writes a whole block into the correct overlay shard and marks allocated.
- `blk_trim` marks a whole block as trimmed without punching holes.

Risk notes:
- Some bitmap updates in cow-on-read happen after a backend read and temp write; concurrent reads/writes rely on documented ordering rather than broad serialization.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/cow/blk.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/cow/blk.h -->
# File Research: sources/virtualization/nbdkit/filters/cow/blk.h

Purpose: internal API for COW overlay block operations.

Key details:
- Forward-declares `struct blk_overlay`.
- Declares global lifecycle `blk_load` and `blk_unload`.
- Declares per-overlay lifecycle `blk_create`, `blk_free`, and `blk_set_size`.
- Exposes `blk_status` for extent handling.
- Exposes block read/read-multiple, cache, write, and trim calls.
- Defines `enum cache_mode` for COW cache behavior: ignore, passthrough, read, or copy into overlay.

Integration notes:
- Used by `cow.c`; it hides temp-file sharding and bitmap details behind block-sized operations.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/cow/blk.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/cow/cow.c -->
# File Research: sources/virtualization/nbdkit/filters/cow/cow.c

Purpose: nbdkit copy-on-write filter that makes a read-only backend appear writable by storing changes in temporary overlays.

Key details:
- Configures `cow-block-size`, `cow-on-cache`, and `cow-on-read`.
- Keeps a global mapping from export name to `blk_overlay`, so connections to the same export share one overlay.
- Opens the backend read-only regardless of requested mode.
- `.get_size` initializes overlay size to backend size; `.prepare` forces this early.
- Advertises write, trim, flush, extents, FUA, cache, fast-zero, and multi-connection support.
- `.pread` reads from overlay, backend, or zero-filled trimmed blocks through `blk_read*`.
- `.pwrite` writes full blocks directly to overlay and serializes unaligned read-modify-write through `rmw_lock`.
- `.zero` writes zero-filled blocks into overlay; fast zero is rejected with `ENOTSUP`.
- `.trim` marks aligned blocks trimmed and handles unaligned edges as zero writes.
- `.flush` is deliberately ignored because overlay data is temporary.
- `.cache` maps backend cache support to block cache behavior, optionally copying cache requests into the overlay.
- `.extents` combines overlay bitmap state with backend extents, reporting trimmed overlay blocks as hole+zero.

Risk notes:
- FUA/flush are intentionally ignored, so durability is only in-process temporary overlay lifetime.
- Export-name overlay sharing is useful for multi-connection consistency but means overlay memory/temp usage persists until filter unload.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/cow/cow.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/cow/cow.h -->
# File Research: sources/virtualization/nbdkit/filters/cow/cow.h

Purpose: tiny shared declaration for COW block size.

Key details:
- Declares external `unsigned blksize`.
- Included by COW block and filter implementation files.

Integration notes:
- Keeps block size as shared mutable configuration between `cow.c` and `blk.c`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/cow/cow.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/ddrescue/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/ddrescue/Makefile.am

Purpose: builds the ddrescue mapfile filter and optional manual page.

Key details:
- Builds `nbdkit-ddrescue-filter.la` from `ddrescue.c`.
- Includes common headers, replacements, and utils.
- CFLAGS include `GNUTLS_CFLAGS`; LIBADD includes `GNUTLS_LIBS`, common utils, replacements, and Windows import support.
- Applies shared linker symbol script when enabled.
- Generates `nbdkit-ddrescue-filter.1` from POD.

Integration notes:
- The filter itself parses text mapfiles and does not directly use TLS in visible code; GNUTLS linkage may be inherited from broader build conventions.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/ddrescue/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/ddrescue/ddrescue.c -->
# File Research: sources/virtualization/nbdkit/filters/ddrescue/ddrescue.c

Purpose: restricts readable ranges according to GNU ddrescue mapfile status.

Key details:
- Parses `ddrescue-mapfile`.
- Skips comments and first status line, then parses tab-separated offset, length, and status.
- Stores only `+` ranges as readable ranges.
- Rejects negative offsets/lengths.
- Disables write and cache support.
- `.pread` succeeds only if the entire requested range is contained inside one recorded good range; otherwise returns `EIO`.

Risk notes:
- Reads spanning adjacent good ranges are rejected unless contained in a single stored range.
- No range merging or sorting is performed.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/ddrescue/ddrescue.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/delay/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/delay/Makefile.am

Purpose: builds the delay injection filter and optional manual page.

Key details:
- Builds `nbdkit-delay-filter.la` from `delay.c`.
- Includes nbdkit public/generated headers.
- Links Windows import support.
- Uses filter symbol script when enabled.
- Generates `nbdkit-delay-filter.1` from POD when available.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/delay/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/delay/delay.c -->
# File Research: sources/virtualization/nbdkit/filters/delay/delay.c

Purpose: injects configurable latency into nbdkit operations.

Key details:
- Supports separate delays for read, write, zero, trim/discard, extents, cache, open, and close/finalize.
- Historical `wdelay` sets write, zero, and trim delays together.
- `delay-trigger` makes delays conditional on a file existing.
- Uses `nbdkit_parse_delay` for duration parsing.
- `.open` delays before opening backend; `.finalize` delays well-behaved disconnects using `nanosleep`.
- `.pread`, `.pwrite`, `.zero`, `.trim`, `.extents`, and `.cache` delay then delegate.
- `delay-fast-zero=false` causes delayed fast-zero requests to fail quickly with `ENOTSUP` instead of sleeping.

Risk notes:
- Close delay cannot affect clients that simply drop the connection; comments explicitly call out this limitation.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/delay/delay.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/error/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/error/Makefile.am

Purpose: builds the error injection filter and optional manual page.

Key details:
- Builds `nbdkit-error-filter.la` from `error.c`.
- Includes common nbdkit and utility headers.
- Links common utils, replacement compatibility, and Windows import support.
- Applies shared filter symbol script when enabled.
- Generates `nbdkit-error-filter.1` from POD.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/error/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/error/error.c -->
# File Research: sources/virtualization/nbdkit/filters/error/error.c

Purpose: randomly injects configured errno failures into selected request types.

Key details:
- Per-operation settings cover `pread`, `pwrite`, `trim`, `zero`, `extents`, and `cache`.
- Error names supported include `EPERM`, `EIO`, `ENOMEM`, `EINVAL`, `ENOSPC`, and `ESHUTDOWN`.
- Supports global and per-operation error code, probability, and trigger-file configuration.
- Trigger files are resolved with `nbdkit_absolute_path`.
- Random state is initialized at load time and protected by a mutex.
- `random_error` skips when rate is zero, checks trigger file if configured, handles 100% rates directly, and uses 32-bit random comparison for partial rates.
- Each wrapped operation either injects `-1` with configured errno or delegates to `next`.

Integration notes:
- Useful for resilience testing of clients and upper filters under controlled operation-specific failures.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/error/error.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/evil/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/evil/Makefile.am

Purpose: builds the Unix-only evil data corruption filter and optional manual page.

Key details:
- Guarded by `!IS_WINDOWS`; comment says it relies on a Unix domain socket.
- Builds `nbdkit-evil-filter.la` from `evil.c`.
- Includes common headers and utility headers.
- Links common utils and Windows import support placeholder.
- Applies shared linker symbol script when enabled.
- Generates `nbdkit-evil-filter.1` from POD.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/evil/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/evil/evil.c -->
# File Research: sources/virtualization/nbdkit/filters/evil/evil.c

Purpose: corrupts read data to simulate bit flips or stuck bits/wires.

Key details:
- Modes are `cosmic-rays`, `stuck-bits`, and `stuck-wires`.
- Configures corruption probability, stuck probability, and random seed.
- Default probabilities depend on mode.
- Chooses an adaptive power-of-two block size so expected corrupt bits per block is about 100.
- `cosmic-rays` uses a global random state and tightens thread model to serialized requests.
- `stuck-bits` seeds random state by disk offset block so the same backing offsets corrupt consistently.
- `stuck-wires` seeds only by global seed so the same positions within every request corrupt consistently.
- Probabilities near zero skip corruption; probabilities above `1/8` corrupt all bits.
- `.pread` delegates to backend then corrupts the returned buffer.

Integration notes:
- This is test/fault-injection code, not a storage transform preserving data integrity.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/evil/evil.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/exitlast/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/exitlast/Makefile.am

Purpose: builds the exit-on-last-client filter and optional manual page.

Key details:
- Builds `nbdkit-exitlast-filter.la` from `exitlast.c`.
- Includes nbdkit public/generated headers.
- Links Windows import support.
- Uses shared filter symbol script when configured.
- Generates `nbdkit-exitlast-filter.1` from POD.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/exitlast/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/exitlast/exitlast.c -->
# File Research: sources/virtualization/nbdkit/filters/exitlast/exitlast.c

Purpose: shuts down nbdkit when the last active client connection closes.

Key details:
- Maintains an atomic unsigned connection count.
- `.open` delegates to backend and increments the count.
- `.close` decrements the count; when it reaches zero, logs and calls `nbdkit_shutdown`.
- No per-connection handle state is needed.

Risk notes:
- On platforms without `<stdatomic.h>`, the fallback treats plain 32-bit ints as sufficient for this simple counter.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/exitlast/exitlast.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/exitwhen/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/exitwhen/Makefile.am

Purpose: builds the event-driven shutdown filter and optional manual page.

Key details:
- Builds `nbdkit-exitwhen-filter.la` from `exitwhen.c`.
- Includes common headers, replacements, and utilities.
- Links common utils, replacements, and Windows import support.
- Applies shared filter symbol script when enabled.
- Generates `nbdkit-exitwhen-filter.1` from POD.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/exitwhen/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/exitwhen/exitwhen.c -->
# File Research: sources/virtualization/nbdkit/filters/exitwhen/exitwhen.c

Purpose: shuts down nbdkit when configured external events occur and no clients are active.

Key details:
- Events include file created, file deleted, process exits, pipe/fd closed, and script exit status 88 where supported.
- Maintains event list, protected connection count, and `exiting` flag under a mutex.
- `dump_plugin` reports supported event types.
- Event checks use `access`, Linux `/proc/PID/stat` fd behavior or `kill(pid,0)`, `poll` for fd closure, and `system` for scripts.
- Background polling thread checks events every `exit-when-poll` seconds only when there are no active connections.
- `get_ready` exits cleanly before daemon startup if an exit condition already holds.
- `preconnect` rejects new connections once exiting.
- `.open` increments active connections; `.close` decrements and shuts down when exiting and count reaches zero.

Risk notes:
- Script mode runs shell commands with `system`; configuration must be trusted.
- Process-exit detection differs between Linux and non-Linux paths.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/exitwhen/exitwhen.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/exportname/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/exportname/Makefile.am

Purpose: builds the export-name policy/description filter and optional manual page.

Key details:
- Builds `nbdkit-exportname-filter.la` from `exportname.c`.
- Includes common headers, replacements, and utils.
- Links common utils, replacements, and Windows import support.
- Uses shared filter symbol script when configured.
- Generates `nbdkit-exportname-filter.1` from POD.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/exportname/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/exportname/exportname.c -->
# File Research: sources/virtualization/nbdkit/filters/exportname/exportname.c

Purpose: controls advertised exports, default export mapping, strict export acceptance, and export descriptions.

Key details:
- Configures `default-export`, `exportname-list`, `exportname-strict`, repeated `exportname`, and `exportdesc`.
- List modes are keep, error, empty, default-only, and explicit.
- Maintains an `nbdkit_exports` list for explicit names.
- Description modes are keep, none, fixed string, or script.
- Script descriptions are generated by constructing a shell snippet with quoted export name, running it with `popen`, and reading up to NBD string length.
- `list_exports` either delegates to backend, errors, returns empty/default-only, or uses explicit list, then applies description policy.
- `default_export` can remap `""` to configured default; in strict mode it permits default only if `""` was explicitly advertised.
- `open` rejects unlisted exports in strict mode, stores the selected export name in the handle, and delegates open.
- `export_description` recomputes description based on handle export name.

Risk notes:
- Script descriptions execute configured shell code; configuration source must be trusted.
- Error message in strict-open path appears to miss a closing quote around export name.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/exportname/exportname.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/ext2/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/ext2/Makefile.am

Purpose: conditionally builds the ext2 filesystem filter and optional manual page.

Key details:
- Guarded by `HAVE_EXT2`.
- Builds `nbdkit-ext2-filter.la` from `ext2.c`, `io.c`, and `io.h`.
- Includes nbdkit headers, common includes, and utility headers.
- CFLAGS include `EXT2FS_CFLAGS` and `COM_ERR_CFLAGS`.
- Links common utils, Windows import support, `EXT2FS_LIBS`, and `COM_ERR_LIBS`.
- Applies shared filter linker script when configured.
- Generates `nbdkit-ext2-filter.1` from POD when available.

Integration notes:
- This work item includes only the build file; the actual ext2 filter implementation lives in adjacent `ext2.c`, `io.c`, and `io.h` outside this grouped file list.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/ext2/Makefile.am -->