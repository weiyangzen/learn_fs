# Group Research: group_1174_nbdkit_sources_virtualization_nbdkit_filters_scan_scan_c_sources_vi_fe4fd35cf647

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/scan/scan.c -->
# File Research: sources/virtualization/nbdkit/filters/scan/scan.c

This file implements the public nbdkit `scan` filter callbacks. The filter opportunistically warms the backing cache by running a per-connection background thread that sends `NBD_CMD_CACHE` requests, with configurable scan direction behavior through `scan-ahead`, `scan-clock`, `scan-forever`, and `scan-size`.

Key control flow: configuration validates `scan-size` as a power of two in `[512..32M]`; `.get_ready` records the final server thread model; `.open` tracks whether the connection is for the default export; `.prepare` only starts scanning when the default export is used, the final thread model is `NBDKIT_THREAD_MODEL_PARALLEL`, and the underlying layer advertises `NBDKIT_CACHE_NATIVE`; `.pread` can enqueue a `CMD_NOTIFY_PREAD` command with the next offset before forwarding the read.

Important state is per connection in `struct scan_handle`: default-export flag, thread-running flag, pthread id, and `bgthread_ctrl`. The background command queue is protected by a mutex and uses the vector helpers declared in `scan.h`.

Risks and invariants: scanning is deliberately disabled for non-default exports, non-parallel backends, and non-native cache support. Queue append failures in `.pread` return failure before the real read. Thread shutdown depends on sending `CMD_QUIT`, joining the thread, destroying the mutex, and resetting the vector exactly once.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/scan/scan.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/scan/scan.h -->
# File Research: sources/virtualization/nbdkit/filters/scan/scan.h

This header defines the shared interface between the scan filter front-end and its background worker. It exports the global scan parameters `scan_clock`, `scan_forever`, and `scan_size`, which are configured in `scan.c` and consumed by the worker implementation outside this file.

The central data structures are `struct command`, with `CMD_QUIT` and `CMD_NOTIFY_PREAD` variants plus an offset, and `struct bgthread_ctrl`, which holds the command vector, mutex, and `nbdkit_next *` used to issue cache operations. `DEFINE_VECTOR_TYPE(command_queue, struct command)` provides the generated vector API used by `scan.c`.

The public worker entry point is `scan_thread(void *)`. Correctness depends on all producers and the worker respecting `bgthread_ctrl.lock` for command queue access and on `scan_size` staying validated by `scan_config_complete`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/scan/scan.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/spinning/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/spinning/Makefile.am

This Automake file builds the `nbdkit-spinning-filter.la` module from `spinning.c` and the public filter header. It installs the filter as a libtool module with `-module -avoid-version -shared`, applies the shared Windows no-undefined/import-library handling, and optionally applies `filters/filters.syms` as a linker version script.

Include paths cover generated headers, public nbdkit headers, common utilities, and common include files. The filter links against `common/utils/libutils.la`, `common/replacements/libcompat.la`, the Windows import library when applicable, and `-lm` for math functions used in the seek-time curve.

The file also distributes `nbdkit-spinning-filter.pod` and conditionally builds the man page and HTML documentation via `podwrapper.pl` when POD support is available.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/spinning/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/spinning/spinning.c -->
# File Research: sources/virtualization/nbdkit/filters/spinning/spinning.c

This file implements the `spinning` filter, which makes an export behave like a rotational disk by inserting seek latency before reads, writes, and zero requests. It advertises `.is_rotational = 1` and disables `.can_multi_conn` because each NBD connection currently has an independent view of head positions.

Configuration supports `heads`, `separate-heads`, `min-seek-time`, `half-seek-time`, and `max-seek-time`. Completion derives a quadratic seek-time curve through the configured minimum, half-stroke, and full-stroke times and validates that it reproduces the three configured points.

Per-connection state records export size and a vector of head ranges. `.prepare` splits the export across up to 64 heads, initializes per-head mutexes, and reduces head count for tiny exports. `do_seek` finds the responsible head by offset, locks either that head or head 0 depending on `separate-heads`, updates simulated positions, and sleeps when movement exceeds `TRACK_SIZE`.

Risks and invariants: the vector search assumes non-empty, ordered head ranges; zero-sized exports produce zero heads and would make request paths unsafe if invoked. Holding the head lock during sleep intentionally serializes seek behavior. The computed delay can be negative if users configure unusual timing, and negative delays are skipped.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/spinning/spinning.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/stats/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/stats/Makefile.am

This Automake file conditionally builds the C++ `stats` filter only when `HAVE_CXX` is true. The module source is `stats.cpp` plus the public filter header, compiled as C++11 with `$(WARNINGS_MODULE_CXXFLAGS)`.

The filter includes public/generated nbdkit headers, common include files, and common utilities, then links against `common/utils/libutils.la`, `common/replacements/libcompat.la`, and the Windows import library when needed. Standard module flags and the optional `filters/filters.syms` linker script match the other filter modules.

Documentation distribution and man/HTML generation are controlled by `HAVE_POD`, producing `nbdkit-stats-filter.1` from `nbdkit-stats-filter.pod`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/stats/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/stats/stats.cpp -->
# File Research: sources/virtualization/nbdkit/filters/stats/stats.cpp

This C++ filter records operation counts, byte totals, elapsed operation time, total runtime throughput, and optional request-size/alignment histograms for reads, writes, trims, zeroes, extents, cache, and flush. It requires `statsfile`, optionally appends with `statsappend`, and controls histogram verbosity with `statsthreshold`.

Global `nbdstat` structures hold per-operation counters and unordered-map histograms. A global pthread mutex protects all stats and output. `.get_ready` opens the report file with `O_CLOEXEC` and records start time; `.unload` prints totals and closes/free resources. Each operation callback timestamps before forwarding to `next`, then records only successful operations.

Histogram logic buckets request size by `floor(log2(size))` and alignment by trailing zero bits in the offset, with offset 0 treated as any alignment. Output includes cumulative alignment fixups and prints buckets until the configured percentile threshold is covered.

Risks and invariants: `print_threshold == 0` disables histogram allocation. `record_stat` degrades to basic counters after `std::bad_alloc`. Flush uses size 0 and therefore is not included in histograms. The code aborts if histogram per-bucket counts diverge from the operation total, treating that as internal corruption.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/stats/stats.cpp -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/swab/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/swab/Makefile.am

This Automake file builds the `nbdkit-swab-filter.la` module from `swab.c` and the public filter header. It uses the shared nbdkit module flags, optional linker version script, and links against common utilities, compatibility replacements, and the Windows import library where applicable.

Include paths cover public/generated nbdkit headers plus common include and utility directories. `nbdkit-swab-filter.pod` is included in `EXTRA_DIST`, and POD-enabled builds generate the `nbdkit-swab-filter.1` manual page and corresponding HTML.

The build file has no platform guard beyond the common Windows import/no-undefined handling, so the filter is intended to be broadly portable.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/swab/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/swab/swab.c -->
# File Research: sources/virtualization/nbdkit/filters/swab/swab.c

This filter presents the same export with fixed-width byte swapping applied to data. `swab-bits` accepts 8, 16, 32, or 64 bits; 8 effectively disables transformation. Export size is rounded down to the swap width, and block-size constraints are adjusted so clients are told to use at least that alignment.

All data-bearing or range-bearing operations require count and offset alignment to `bits/8`, returning `EINVAL` otherwise. Reads forward to the underlying plugin and then swap in place. Writes allocate a temporary block, byte-swap into it, and write transformed bytes to the underlying layer. Trim, zero, extents, and cache validate alignment and either forward directly or use `nbdkit_extents_aligned`.

Risks and invariants: the filter relies on strict alignment to avoid partial element transformations. Write allocation is per request and can fail with the caller-visible errno. The code casts buffers to 16/32/64-bit pointer types after alignment validation, so callers must not bypass the advertised constraints.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/swab/swab.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/tar/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/tar/Makefile.am

This Automake file builds `nbdkit-tar-filter.la` from `tar.c` only on non-Windows platforms, because the implementation depends on `open_memstream` and shell/subprocess behavior. It distributes `nbdkit-tar-filter.pod`.

The module includes public/generated nbdkit headers, common include files, replacements, and utilities. It links against common utilities, compatibility replacements, and the Windows import library variable, although the module itself is guarded by `!IS_WINDOWS`. The optional filter linker version script is applied when available.

When POD support is present, it generates `nbdkit-tar-filter.1` and HTML documentation using `podwrapper.pl`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/tar/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/tar/tar.c -->
# File Research: sources/virtualization/nbdkit/filters/tar/tar.c

This filter exposes a single regular file embedded inside an underlying tar archive. It requires `tar-entry`, optionally limits scanning with `tar-limit`, and lets users override the `tar` executable path.

The first connection entering `.prepare` calculates the member offset and size under a global mutex. It constructs a shell command running `tar --no-auto-compress -t --block-number -v -f - <entry>`, streams bytes read from the underlying plugin into that subprocess until the tar output file receives data or the scan limit is reached, parses tar's block and size output, and converts the tar block number to the member payload offset.

Per-connection handles copy the resolved offset and size. The filter reports member size, prefixes the export description, and forwards read/write/trim/zero/cache operations with the member offset added. Extents are requested against the underlying archive range, then copied back with offsets translated down.

Risks and invariants: initialization assumes the tar archive is not sparse while scanning. Temporary-file and subprocess failures abort preparation. The code checks offset and size against `INT64_MAX` but does not fully verify that the member lies inside the archive. Global initialization means later connections reuse the first resolved member metadata.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/tar/tar.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/time-limit/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/time-limit/Makefile.am

This Automake file builds the `nbdkit-time-limit-filter.la` module from `time-limit.c` and the public filter header. It uses standard filter module flags, optional `filters/filters.syms`, and links common utilities, compatibility replacements, and the platform import library.

Include paths cover public/generated headers, common include files, and common utilities. The POD file `nbdkit-time-limit-filter.pod` is distributed and, when POD support is available, converted into `nbdkit-time-limit-filter.1` and HTML documentation.

The build file has no special feature or platform guard, so the filter is built wherever the common nbdkit filter infrastructure is available.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/time-limit/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/time-limit/time-limit.c -->
# File Research: sources/virtualization/nbdkit/filters/time-limit/time-limit.c

This filter disconnects a client after a configured per-connection elapsed time. It accepts `time-limit`, `time_limit`, or `timelimit`, parsed by `nbdkit_parse_delay`; the default is 60 seconds. Configuration completion converts seconds/nanoseconds to microseconds, with `(0,0)` disabling the filter.

Each handle stores a `struct timeval` captured in `.open`. Before every read, write, trim, zero, extents, or cache request, `check_time_limit` compares current elapsed time with the configured limit. If exceeded, it sets `ESHUTDOWN` when available or `EIO`, calls `nbdkit_disconnect(1)`, and returns failure.

Risks and invariants: the timer starts before the underlying `.open`; a `next` failure currently returns `NULL` without freeing the allocated handle. The disconnect is asynchronous, so the client may not observe the specific errno. Operations not overridden by this filter are not time-gated.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/time-limit/time-limit.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/tls-fallback/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/tls-fallback/Makefile.am

This Automake file builds `nbdkit-tls-fallback-filter.la` from `tls-fallback.c` and the public filter header. It uses public/generated/common include paths, standard module flags, and the optional filter linker script.

The filter has minimal dependencies compared with most other modules: it links only the Windows import library variable and does not link common utility or replacement libraries. `nbdkit-tls-fallback-filter.pod` is distributed, and POD-enabled builds generate the man page and HTML documentation.

The build file does not conditionally disable the filter by platform or TLS library; runtime behavior is implemented through nbdkit's `is_tls` callback arguments.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/tls-fallback/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/tls-fallback/tls-fallback.c -->
# File Research: sources/virtualization/nbdkit/filters/tls-fallback/tls-fallback.c

This filter serves a harmless plaintext dummy export to non-TLS clients while forwarding TLS-authenticated connections to the real backend. The default message is a static 512-byte buffer, configurable with `tlsreadme`; the handle value `&message` is used as the insecure sentinel.

`.get_ready` rejects `NBDKIT_THREAD_MODEL_SERIALIZE_CONNECTIONS`, because insecure and secure connections must coexist. For non-TLS handshakes, list/default export callbacks expose only the empty export and `.open` intentionally does not call `next`, avoiding backend work and information leaks. For TLS, callbacks forward normally.

For insecure handles, the filter overrides size, block size, writability, flush, rotational, extents, multi-conn, cache, description, and pread behavior. It advertises no write-like capabilities and reads directly from the message buffer.

Risks and invariants: the security model depends on overriding every callback reachable before or during plaintext handshake so the backend is never consulted for insecure clients. `strncpy` intentionally may leave the configured message without a terminating NUL; size is fixed at the full message buffer.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/tls-fallback/tls-fallback.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/truncate/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/truncate/Makefile.am

This Automake file builds `nbdkit-truncate-filter.la` from `truncate.c` and the public filter header. It uses standard nbdkit filter module flags, common include paths, common utility/replacement libraries, the platform import library, and the optional `filters/filters.syms` linker script.

The POD file `nbdkit-truncate-filter.pod` is distributed. When POD support is enabled, `podwrapper.pl` generates the section 1 man page and HTML output.

The build is unconditional across supported platforms, relying only on common nbdkit helpers such as rounding, zero detection, and power-of-two validation.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/truncate/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/truncate/truncate.c -->
# File Research: sources/virtualization/nbdkit/filters/truncate/truncate.c

This filter presents a per-connection virtual size derived from the underlying export by applying optional `truncate`, `round-up`, and `round-down` operations. Rounding values are parsed as sizes, must be positive, fit in `unsigned`, and be powers of two.

Each connection caches the underlying `real_size` and computed virtual `size` during `.prepare`. Reads inside the real size forward to the backend and reads beyond it are zero-filled. Writes inside the real size are clamped and forwarded; any remaining write beyond the real size must be all zeroes or fails with `ENOSPC`. Trim, zero, and cache similarly clamp to the real backend range and treat tail-only requests as successful no-ops.

The filter always advertises extents and fast zero support after probing the underlying layer. Extents for tail-only ranges are reported as zero/hole; mixed ranges copy underlying extents through a bounded temporary extents list.

Risks and invariants: `truncate_extents` uses the global `truncate_size` when reporting tail length, which matters if the visible size came from only rounding. Dynamic backend resizing is intentionally ignored after prepare. Tail writes of non-zero data are rejected rather than materialized.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/truncate/truncate.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/xor/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/xor/Makefile.am

This Automake file builds `nbdkit-xor-filter.la` from `xor.c` and the public filter header. It uses public/generated/common include paths and standard module linker flags, including the optional `filters/filters.syms` version script.

Unlike many filters, this module does not link common utility or replacement libraries; it only includes the platform import library variable. `nbdkit-xor-filter.pod` is distributed and conditionally converted to man/HTML documentation when POD support is enabled.

The build is unconditional and depends on helper headers from common include paths for alignment, min/max, random generation, and rounding.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/xor/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/xor/xor.c -->
# File Research: sources/virtualization/nbdkit/filters/xor/xor.c

This filter applies a reversible XOR transform to data. It supports `xor=VALUE` with `xorlen=1..8`, or `xor=rand[:SEED]`, which uses deterministic pseudo-random 8-byte blocks derived from offset plus seed. Configuration requires exactly one `xor` mode and a valid length, except random mode sets length to 8 and forbids separate `xorlen`.

For value mode, `.get_ready` converts the numeric parameter to big-endian bytes. The data path has optimized aligned loops for 1, 2, 4, and 8 byte patterns and recursive unaligned handling. Random mode locates the generated 64-bit value for each aligned 8-byte window and handles unaligned leading/trailing bytes.

Reads transform the buffer after backend read. Writes copy the caller buffer, transform it, then write the transformed block. Zero and trim are implemented identically by writing transformed zero-filled chunks of up to 64 KiB, preserving FUA only when the backend supports native FUA.

Risks and invariants: trim loses discard/sparse semantics because transformed zero data must be written. Value-mode aligned fast paths cast the `xor` byte array to integer pointers, so byte order and host alignment assumptions matter. Random mode depends on stable `random.c` behavior for reproducibility.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/xor/xor.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/xz/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/xz/Makefile.am

This Automake file builds the `nbdkit-xz-filter.la` module only when `HAVE_LIBLZMA` is true. The module sources are `blkcache.c`, `blkcache.h`, `xz.c`, `xzfile.c`, `xzfile.h`, and the public filter header.

The build includes public/generated nbdkit headers, common include files, and common utilities. It compiles with `$(LIBLZMA_CFLAGS)` and links `$(LIBLZMA_LIBS)`, common utilities, compatibility replacements, and the platform import library. The optional filter linker script is applied when configured.

`nbdkit-xz-filter.pod` is distributed. POD-enabled builds generate `nbdkit-xz-filter.1` and HTML documentation.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/xz/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/xz/blkcache.c -->
# File Research: sources/virtualization/nbdkit/filters/xz/blkcache.c

This file implements a small fixed-depth LRU cache for decompressed xz blocks. `new_blkcache` allocates the cache object and an array of block slots, initializing hit/miss stats. `free_blkcache` frees every cached block data pointer, the slot array, and the cache.

`get_block` linearly scans slots for a block containing the requested uncompressed offset. On a hit, it swaps the hit slot with slot 0 to mark it most recently used, updates hit stats, and returns the data plus start/size. On a miss it increments miss stats.

`put_block` evicts the least-recently-used slot at `maxdepth - 1`, shifts all slots down, and inserts the supplied data pointer at slot 0. Ownership of `data` transfers to the cache.

Risks and invariants: `put_block` assumes `maxdepth >= 1`, guaranteed by `xz.c` config validation. Cache access is not internally synchronized; the xz filter forces serialized requests. The LRU update swaps with slot 0 rather than doing a full move, which is simple but approximate.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/xz/blkcache.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/xz/blkcache.h -->
# File Research: sources/virtualization/nbdkit/filters/xz/blkcache.h

This header declares the opaque `blkcache` type, cache statistics structure, and public cache operations used by the xz filter. `blkcache_stats` tracks hit and miss counters as `size_t`.

The API consists of `new_blkcache`, `free_blkcache`, `get_block`, `put_block`, and `blkcache_get_stats`, with nbdkit nonnull attributes on pointer parameters. `get_block` returns a borrowed cached data pointer and fills the containing block's start and size. `put_block` accepts ownership of a decompressed block buffer.

The closing include guard comment says `NBDKIT_XZFILE_H` even though the guard is `NBDKIT_BLKCACHE_H`; this is cosmetic but can confuse readers.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/xz/blkcache.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/xz/xz.c -->
# File Research: sources/virtualization/nbdkit/filters/xz/xz.c

This file implements the public `xz` filter callbacks. The filter presents an xz-compressed backend as a read-only uncompressed export, with per-connection decompressed-block caching. Configuration supports `xz-max-block` to cap allowed uncompressed block size and `xz-max-depth` to set cache depth.

`.open` always opens the underlying plugin read-only, allocates a handle, and creates a block cache. `.prepare` opens and validates the xz metadata through `xzfile_open`, then rejects files whose largest uncompressed block exceeds `xz-max-block`. `.get_size` returns the uncompressed size from the parsed xz index. The filter denies writes and extents, advertises multi-connection consistency, and uses cache emulation.

`.pread` first checks the local block cache. On miss it decompresses the xz block containing the requested offset via `xzfile_read_block`, inserts it into the cache, copies the requested slice, and recurses if the client request crosses block boundaries.

Risks and invariants: request serialization is forced with `NBDKIT_THREAD_MODEL_SERIALIZE_REQUESTS`, protecting the unsynchronized cache and liblzma state. Large xz blocks allocate full uncompressed block buffers. Recursive reads depend on xz index block coverage and progress across block boundaries.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/xz/xz.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/xz/xzfile.c -->
# File Research: sources/virtualization/nbdkit/filters/xz/xzfile.c

This file abstracts liblzma index parsing and block decompression for the xz filter. `xzfile_open` allocates an `xzfile`, verifies the header magic, parses all stream indexes from the end of the file, computes stream/block counts and maximum uncompressed block size, and logs uncompressed size metadata.

`parse_indexes` mirrors xz tooling behavior: it validates file size alignment, walks backward through stream footers, skips stream padding, decodes stream footer/header flags, decodes each index with `lzma_index_decoder`, validates header/footer flag equality, stores stream flags and padding, and concatenates indexes for multi-stream files. `iter_indexes` counts non-empty blocks and tracks the largest uncompressed block.

`xzfile_read_block` locates the xz block containing an uncompressed offset, reads and decodes the block header, validates compressed size against the index, allocates the full uncompressed block buffer, streams compressed bytes through a liblzma block decoder, frees filter option allocations, and returns the decompressed block plus uncompressed start/size.

Risks and invariants: memory use scales with the xz block's uncompressed size. Error paths must clean up `lzma_stream`, indexes, filter options, and data buffers. The function reads compressed data up to the backend size and reports corrupt headers, mismatched indexes, and invalid offsets as hard failures.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/xz/xzfile.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/xz/xzfile.h -->
# File Research: sources/virtualization/nbdkit/filters/xz/xzfile.h

This header declares the opaque `xzfile` helper used by `xz.c`. It exposes lifecycle functions, metadata accessors, and block decompression.

`xzfile_open(nbdkit_next *)` verifies and parses the underlying xz stream indexes. `xzfile_close` releases liblzma index resources. `xzfile_max_uncompressed_block_size` returns the largest block size for configuration enforcement, while `xzfile_get_size` returns total uncompressed size.

`xzfile_read_block` decompresses the block containing a requested uncompressed offset and returns a heap buffer owned by the caller, along with block start and size. Its interface deliberately works at xz block granularity so `xz.c` can cache decompressed blocks.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/xz/xzfile.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/Makefile.am

This top-level plugin Automake file includes common rules, distributes `plugins.syms`, and delegates plugin builds to `SUBDIRS = $(plugins)`. The actual plugin list is provided by the configured `$(plugins)` variable elsewhere in the build system.

Its role is structural: it ties all enabled plugin subdirectories into the recursive build while keeping common plugin symbol export metadata in `EXTRA_DIST`.

There is no direct compilation logic here; platform and dependency gating happens in each plugin subdirectory's `Makefile.am`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/S3/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/S3/Makefile.am

This Automake file packages the Python `S3` plugin. `S3.py` is the source, and `nbdkit.py` is distributed as a test stub. When `HAVE_PYTHON` is true, it generates an executable script named `nbdkit-S3-plugin` by replacing `@sbindir@` in `S3.py`, then installs it as a plugin script with mode `0555`.

The file distributes `nbdkit-S3-plugin.pod` and conditionally builds the section 1 man page plus HTML documentation using `podwrapper.pl`.

No C module is compiled here; runtime dependencies are Python, boto3/botocore, and nbdkit's Python plugin loader.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/S3/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/S3/S3.py -->
# File Research: sources/virtualization/nbdkit/plugins/S3/S3.py

This Python nbdkit plugin serves S3-compatible storage as a block device. In single-object mode, it reads byte ranges from one object and is read-only. In sharded mode, configured with both `size` and `object-size`, it maps blocks to keys named `<key>/<blockno:016x>` and supports writes, zero, trim, flush, FUA, multi-conn, and fast zero.

`Config` parses credentials, endpoint, bucket, key, device size, and object size; credential-like values are read through `nbdkit.read_password`. Plugin callbacks advertise parallel threading, write capability only in sharded mode, no cache, and block-size preferences favoring object size.

Each `Server` owns a boto3 S3 client. Reads fetch missing sharded objects as zeroes. Writes handle unaligned starts/ends by reading affected partial objects under an object-specific `MultiLock`, then write full object-sized bodies. Zero uses partial writes at edges and deletes whole covered objects. Trim deletes only fully covered objects, using paginated `list_objects_v2` and batched `delete_objects`.

The file includes local and optional remote unit tests plus a stub-compatible design. Risks: single-object writes intentionally fail; partial-write correctness depends on per-key locking only within this process; delete operations raise on S3 errors; timeouts are mapped to `ETIMEDOUT` but other boto errors propagate.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/S3/S3.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/S3/nbdkit.py -->
# File Research: sources/virtualization/nbdkit/plugins/S3/nbdkit.py

This is a small Python stub of the real `nbdkit` module for unit testing `S3.py` outside the nbdkit process. It defines a logger, `FLAG_MAY_TRIM`, `parse_size`, `debug`, and `set_error`.

The stub intentionally implements only the minimum needed by the local tests in `S3.py`. It does not provide constants such as `THREAD_MODEL_PARALLEL`, `CACHE_NONE`, or `FUA_NATIVE` used by normal plugin registration paths, so it is not a full emulation of the runtime module.

Its purpose is test isolation: code paths that only need parsing, debug logging, or trim flags can run under standard Python.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/S3/nbdkit.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/blkio/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/blkio/Makefile.am

This Automake file builds `nbdkit-blkio-plugin.la` only when `HAVE_LIBBLKIO` is true. The module source is `blkio.c` plus the public plugin header.

The build uses public/generated headers, common include files, and common utilities. It compiles with `$(LIBBLKIO_CFLAGS)` and links common utilities, the platform import library, and `$(LIBBLKIO_LIBS)`. Standard plugin module flags and the optional `plugins/plugins.syms` version script are applied.

The POD file `nbdkit-blkio-plugin.pod` is distributed. POD generation inserts the shared magic-parameter text before building the man page and HTML output.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/blkio/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/blkio/blkio.c -->
# File Research: sources/virtualization/nbdkit/plugins/blkio/blkio.c

This plugin adapts libblkio block devices to nbdkit. It requires `driver=<DRIVER>`, accepts arbitrary libblkio properties, supports `get=PROPERTY` debug reporting, and forbids direct `read-only` configuration in favor of nbdkit's `-r`. Path properties are converted to absolute paths.

`.open` creates a libblkio instance, sets readonly and pre-connect properties, connects, sets post-connect properties, starts the device, prints requested properties, and optionally allocates/maps a per-handle 64 MiB bounce buffer when `needs-mem-regions` is true. `.get_size` reads `capacity`, and `.block_size` derives constraints from `request-alignment` and `optimal-io-alignment`.

I/O callbacks use queue 0 synchronously: read/write/flush/write-zeroes/discard submit one request and wait for one completion with `blkioq_do_io`. FUA and MAY_TRIM map to libblkio flags. Capabilities for flush, trim, and zero are tied to writability; FUA is native.

Risks and invariants: the plugin serializes requests rather than using libblkio's event model. Bounce-buffer users reject requests larger than 64 MiB. Completion `ret` must be zero; any other value is treated as unexpected failure. Property timing depends on the hard-coded pre-connect property list.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/blkio/blkio.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/cc/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/cc/Makefile.am

This Automake file builds the `cc` plugin on non-Windows platforms, because the implementation requires `mkstemps`, dynamic loading, and shell commands. It compiles `cc.c` with configured `CC_PLUGIN_CC` and `CC_PLUGIN_CFLAGS` embedded as preprocessor strings.

The module includes public/generated headers, common include files, common utilities, and the local build directory. It links common utilities, the platform import library, and dynamic loader libraries `$(DL_LIBS)`. Optional plugin symbol versioning uses `plugins/plugins.syms`.

Documentation generation builds a section 3 man page from `nbdkit-cc-plugin.pod`, replacing OCaml include/library placeholders in the POD output.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/cc/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/cc/cc.c -->
# File Research: sources/virtualization/nbdkit/plugins/cc/cc.c

This plugin compiles a user-supplied C nbdkit plugin at configuration time, dynamically loads it, and forwards nbdkit callbacks to the loaded subplugin. The first parameter must be `script=<file>` or `script=-`; inline scripts are read from stdin into a temporary `.c` file when stdio is safe.

Configuration also accepts `CC`, `CFLAGS`, and `EXTRA_CFLAGS`; all other key/value pairs are saved and replayed into the subplugin's `.config`. `cc_config_complete` compiles the source to a temporary `.so`, loads it with `dlopen`, locates `plugin_init`, checks API version and required callbacks (`open`, `get_size`, `pread`), copies the plugin struct with size compatibility, then invokes the subplugin's load/config/config_complete.

The wrapper provides a broad callback surface: lifecycle, export negotiation, capabilities, block size, I/O, extents, cache, and cleanup. Missing optional callbacks either default to conservative answers or return appropriate errors/fallback signals. Thread model is delegated to the subplugin.

Risks and invariants: compiler command construction intentionally leaves compiler/flags unquoted but shell-quotes source/output paths. Running arbitrary compiler and plugin code is inherent. Temporary compiled output is unlinked after `dlopen`. Errno preservation is enabled so forwarded subplugin errors survive.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/cc/cc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/cdi/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/cdi/Makefile.am

This Automake file builds `nbdkit-cdi-plugin.la` only on non-Windows platforms because the implementation runs a shell script. It compiles `cdi.c` with public/generated headers, common include files, common utilities, and local include path support.

The module links common utilities, the platform import library, and `$(JANSSON_LIBS)`, with `$(JANSSON_CFLAGS)` in compile flags. Although this file links Jansson, the listed `cdi.c` uses shell tools such as `jq` rather than direct JSON parsing. Optional plugin symbol versioning uses `plugins/plugins.syms`.

POD-enabled builds generate `nbdkit-cdi-plugin.1` and HTML documentation, inserting the shared magic-parameter text.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/cdi/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/cdi/cdi.c -->
# File Research: sources/virtualization/nbdkit/plugins/cdi/cdi.c

This plugin exports one layer from a container image as a read-only block device. It accepts `name` as a required image name/URI and `layer` as an index, including negative indexes interpreted by the shell/JQ expression.

At `.get_ready`, `make_layer` creates a temporary file, constructs a shell script with quoted variables, runs `podman pull`, saves the image as a Docker directory, uses `jq` and `cut` to find the selected layer digest in `manifest.json`, moves that layer file over the temporary file, removes the extracted directory, reopens the resulting file read-only with `O_CLOEXEC`, and unlinks it.

Runtime callbacks need no per-connection handle. Size is determined by `device_size(fd)`, data is served with a robust `pread` loop, multi-conn is true, and cache is emulated through reads.

Risks and invariants: runtime depends on external `podman`, `jq`, shell, temporary storage, and enough disk space for the saved image. The exported file descriptor is global and closed at unload. The plugin is read-only and parallel-safe because all clients read the same immutable fd.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/cdi/cdi.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/curl/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/curl/Makefile.am

This Automake file builds `nbdkit-curl-plugin.la` when libcurl is available and the platform is not Windows, because the implementation uses a self-pipe. Sources are `config.c`, `curldefs.h`, `curl.c`, `scripts.c`, `times.c`, `worker.c`, and the public plugin header.

The module includes public/generated headers, common include files, replacements, and utilities. It compiles with `$(CURL_CFLAGS)` and links common utilities, compatibility replacements, the platform import library, and `$(CURL_LIBS)`. Optional plugin symbol versioning uses `plugins/plugins.syms`.

Documentation generation builds `nbdkit-curl-plugin.1` and HTML from POD, inserting the shared magic-parameter text.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/curl/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/curl/config.c -->
# File Research: sources/virtualization/nbdkit/plugins/curl/config.c

This file owns most configuration parsing and libcurl easy-handle setup for the curl plugin. It stores global options for URL, CA paths, cookies, cookie/header scripts, redirects, headers, HTTP version, IP resolution, credentials, protocol allowlists, proxy settings, TLS versions/ciphers, TCP options, timeout, Unix sockets, user, and user-agent.

`curl_config` parses each supported parameter, including password reads, boolean parsing, protocol parsing for old and new curl APIs, validation of unsupported proxy CA options, and rejection of cookiefile/cookiejar `-` to avoid stdin/stdout interaction. `curl_config_complete` requires `url` and rejects conflicting static/script header or cookie configuration and renew settings without scripts.

`allocate_handle` creates a `struct curl_handle`, initializes a libcurl easy handle, installs private data, verbose debug callback, error buffer, URL, signal/redirect/fail behavior, and every configured curl option. It prepares the handle for later read/write setup. `free_handle` cleans up the easy handle and any copied headers. `curl_dump_plugin` reports compile-time and dynamic curl versions/protocols. `debug_cb` routes verbose curl text and headers into `nbdkit_debug`, optionally including connection/transfer ids.

Risks and invariants: configuration is global across all handles. The `resolve` branch appends to `headers` rather than `resolves`, which looks like a likely bug because `CURLOPT_RESOLVE` later receives `resolves`. Security-sensitive options such as `sslverify=false` and protocol allowlists directly affect what remote resources can be accessed.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/curl/config.c -->