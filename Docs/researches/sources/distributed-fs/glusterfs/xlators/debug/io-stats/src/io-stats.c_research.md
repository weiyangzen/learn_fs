# sources/distributed-fs/glusterfs/xlators/debug/io-stats/src/io-stats.c

## Purpose
Implements GlusterFS `debug/io-stats`, a maintained profiling translator that records filesystem operation counts, read/write byte totals, block-size histograms, latency measurements, per-file top lists, throughput records, upcall counters, fd lifetime statistics, and optional latency samples. It can return stats through translator-info dictionaries, write manual dumps via a special xattr on client graphs, and periodically dump JSON/text stats plus sample files from a background thread.

## Important APIs, types, and functions
Core state types are `struct ios_conf`, `struct ios_global_stats`, `struct ios_fd`, `struct ios_stat`, `struct ios_stat_head`, `struct ios_stat_list`, `ios_sample_t`, and `ios_sample_buf_t`. `ios_conf` owns cumulative and incremental counters, options, top-N lists, sampling state, DNS cache, dump thread state, and the `unique_id` used in metric and file names.

Counter helpers include `ios_bump_read()`, `ios_bump_write()`, `ios_bump_upcall()`, `ios_bump_stats()`, `BUMP_FOP`, `START_FOP_LATENCY`, `UPDATE_PROFILE_STATS`, `END_FOP_LATENCY`, and `BUMP_THROUGHPUT`. Context helpers include `ios_fd_ctx_set()`, `ios_inode_ctx_set()`, `ios_inode_ctx_get()`, `ios_stat_ref()`, `ios_stat_unref()`, and `ios_stats_cleanup()`.

Dumping and reporting are handled by `io_stats_dump_global_to_logfp()`, `io_stats_dump_global_to_json_logfp()`, `io_stats_dump_global_to_dict()`, `io_stats_dump()`, `io_stats_dump_stats_to_dict()`, `io_stats_dump_fd()`, `conditional_dump()`, `_ios_dump_thread()`, `io_stats_dump_latency_samples_logfp()`, and `_io_stats_write_latency_sample()`. `notify()` handles `GF_EVENT_TRANSLATOR_INFO` requests and upcall accounting.

Lifecycle and configuration functions are `init()`, `reconfigure()`, `fini()`, `ios_conf_destroy()`, `ios_init_stats()`, `ios_init_top_stats()`, `ios_destroy_top_stats()`, `io_stats_clear()`, `mem_acct_init()`, `ios_set_log_format_code()`, `xlator_set_loglevel()`, `gf_check_log_format()`, and `gf_check_logger()`. The exported `fops`, `cbks`, `dumpops`, `options`, and `xlator_api` tables register it as `io-stats`, category `GF_MAINTAINED`.

## Control flow
Initialization requires at least one child, allocates `ios_conf`, sets `unique_id`, optionally copies `volume-id` into the graph, initializes locks and cumulative/incremental stats, builds top-list sentinels, reads all volume options, allocates the latency sample ring buffer, creates the reverse-DNS cache, applies logging/thread options, stores `this->private`, and starts `_ios_dump_thread()` when `ios-dump-interval > 0`.

Each FOP wrapper records a start timestamp when latency measurement is enabled, stores any needed pointer or path in `frame->local`, then winds to the first child. The callback updates profile stats and unwinds. `readv` bumps read bytes after successful completion using the returned iovec length; `writev` bumps write bytes before the child call using requested iovec length; open/create allocate fd context, increment open-fd counts, and initialize inode stats; release logs fd stats when enabled and decrements open-fd count; forget removes inode stats. Directory and file top lists are updated from inode contexts, and read/write callbacks update throughput top lists.

Manual dump flow is triggered in `io_stats_setxattr()` by dictionary keys matching `*io*stat*dump`. `conditional_dump()` allows this only in `GF_CLIENT_PROCESS`, sanitizes `../`, builds a file under `DEFAULT_VAR_RUN_DIRECTORY`, chooses JSON or text based on the xattr key, and calls `io_stats_dump()`. Management-plane flow goes through `notify(GF_EVENT_TRANSLATOR_INFO)`, which can clear stats, return top lists, return cumulative/incremental dict stats, or peek without resetting incremental counters.

Periodic dump flow is `_ios_dump_thread()`: create stats and sample directories, derive filenames from `__progname`, `unique_id`, and instance name, sleep for the configured interval, write stats in the configured dump format, then swap and dump latency samples. Reconfigure can start or stop this thread as the interval crosses zero and updates logging, dump, sampling, and async-thread options live.

## State and persistence behavior
Most state is in-memory and process-local. Cumulative counters persist for the life of the translator until explicitly cleared or unloaded. Incremental counters are reset by non-peek dump operations. Per-fd stats live in fd context and are freed on release. Per-inode stats live in inode context with manual refcounting and are unreferenced on forget and top-list cleanup. Top-N lists retain references to `ios_stat` objects. Latency samples use a preallocated circular buffer; dump swaps in a fresh buffer and writes the old one.

Durable side effects are diagnostic files, not filesystem data: manual dumps under `DEFAULT_VAR_RUN_DIRECTORY`, periodic stats under `_IOS_DUMP_DIR`, and periodic samples under `_IOS_SAMP_DIR`. Paths are affected by the build-time `DATADIR` macro and runtime `unique-id`/instance names. DNS cache entries are in-memory dict entries with TTL.

## Dependencies and integration points
Depends heavily on GlusterFS core: xlator FOP/callback APIs, default wind/unwind macros, inode/fd contexts, atomics, locks, dicts, statedump, logging controls, syncop xattr, async thread controls, upcall event structures, memory accounting, path constants, and generated FOP/upcall name tables. It integrates with the `gluster volume profile`/translator-info path, client-side xattr-triggered diagnostics, brick/client logging options, io-threads queue-size reporting through `IO_THREADS_QUEUE_SIZE_KEY`, and global threading controls.

## Risks and test signals
Concurrency risks include lockless updates to latency totals/averages while hit counts are atomic, sample-buffer pointer swaps using `conf->lock` while collectors use `ios_sampling_lock`, dump-thread cancellation around file I/O, and top-list refcount/list ordering correctness. Data-quality risks include counting requested write bytes before child completion, block-size bucket bounds for unusual lengths, divide-by-zero or integer-division behavior in interval reports, and open-fd underflow if release paths are unbalanced. Security and operational risks include dump path handling, reverse DNS latency during sample formatting, client-only xattr dump enforcement, and global logging option side effects.

Useful tests include open/read/write/release accounting, failed open/create paths, incremental dump reset versus peek, `GF_IOS_INFO_CLEAR`, top-list ordering and truncation at 100 entries, latency min/max/average updates, sample interval and ring wrap behavior, periodic dump thread start/stop through reconfigure, manual setxattr dumps on client versus brick process modes, upcall counter classification, io-threads queue-size dict integration, and memory/refcount cleanup on inode forget and translator unload.
