# subset-b-007087 GlusterFS debug error-gen, io-stats, sink, and trace build research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/error-gen/src/error-gen.c -->
# sources/distributed-fs/glusterfs/xlators/debug/error-gen/src/error-gen.c

## Purpose
Implements the GlusterFS `debug/error-gen` translator. It sits in a one-child xlator graph and injects synthetic failures into selected filesystem operations so higher layers, clients, and tests can exercise error handling. It supports a controlled percentage failure mode, a legacy `random-failure` mode, optional fixed errno injection, per-FOP enable lists, short-write simulation for `writev`, statedump reporting, and runtime option reconfiguration.

## Important APIs, types, and functions
`error_no_list[]` maps `GF_FOP_*` operation numbers to realistic errno candidates. `generate_rand_no()` chooses an index in the errno list for a FOP. `conv_errno_to_int()` converts option strings such as `ENOENT`, `EIO`, and the pseudo error `GF_ERROR_SHORT_WRITE` to integer codes, defaulting unknown names to `EAGAIN`. `error_gen()` is the decision engine: it checks `eg_t` state, decides whether the current operation should fail, and returns either a configured errno or a random FOP-specific errno.

The many `error_gen_*` FOP handlers all follow the same pattern: read `egp->enable[GF_FOP_*]`, call `error_gen()` when enabled, unwind the stack with `op_ret = -1` and the chosen `op_errno` on failure, or tail-wind to the child xlator on success. Notable wrappers include `error_gen_writev()`, which recognizes `GF_ERROR_SHORT_WRITE` by duplicating a one-element iovec and halving its length before winding, and lookup/create/directory wrappers that must supply the right strict-unwind argument shape.

Lifecycle and integration functions are `init()`, `reconfigure()`, `fini()`, `mem_acct_init()`, and `error_gen_priv_dump()`. The exported `fops`, `dumpops`, `cbks`, `options`, and `xlator_api` tables register this translator as identifier `error-gen`, category `GF_TECH_PREVIEW`.

## Control flow
Initialization validates that there is exactly one subvolume, allocates `eg_t`, initializes its lock, parses `error-no`, `failure`, `enable`/`error-fops`, and `random-failure`, assigns `this->private`, and seeds `rand()` with `gf_time()`.

For each intercepted FOP, the fast path is: start in the `error_gen_*` wrapper, check whether that FOP is enabled, call `error_gen()` if so, and either return an immediate synthetic error through `STACK_UNWIND_STRICT()` or pass the request to `FIRST_CHILD(this)` with `STACK_WIND_TAIL()`. Normal controlled-probability mode compares `rand() % FAILURE_GRANULARITY` against `egp->failure_iter_no`, which is a numerator derived from the configured percentage. Legacy `random-failure` mode locks `eg_t`, increments `op_count`, injects when the count reaches `failure_iter_no`, then resets the count and chooses the next interval as `3 + rand() % GF_UNIVERSAL_ANSWER`.

Reconfiguration repeats option parsing against the existing private object. It updates the fixed errno, random-failure flag, enabled FOP bitmap, and failure numerator without replacing the xlator instance.

## State and persistence behavior
State is process-local only. `eg_t` stores enabled FOP bits, operation count, failure numerator or legacy interval, optional fixed errno, random-failure flag, and a lock. There is no durable persistence; option changes come from the volfile/management plane and live in memory. Statedump exposes `op_count`, `failure_iter_no`, `error_no_int`, and `random_failure` under `xlator.debug.error-gen.<name>.priv`.

The only protected mutable state in `error_gen()` is the legacy random-failure counter path. In normal probability mode, reads of `failure_iter_no`, `error_no_int`, and `enable[]` are lockless, so reconfiguration can race with active FOPs in the usual xlator-option style.

## Dependencies and integration points
Depends on GlusterFS xlator APIs, strict unwind/wind macros, FOP enums and names, memory accounting, statedump, locks, `gf_fop_int()`, `gf_time()`, and the `error-gen.h`/`error-gen-mem-types.h` declarations. It integrates as a pass-through debug xlator above exactly one child translator and relies on the child FOP vector for all non-injected work.

## Risks and test signals
Risk areas include the use of process-global `rand()`/`srand()` in multi-threaded graphs, lockless normal-mode option reads during reconfigure, realistic errno tables that may miss newer FOPs, unknown `error-no` values silently becoming `EAGAIN`, and strict-unwind argument mismatches when FOP signatures evolve. `error_gen_writev()` frees the shortened iovec immediately after `STACK_WIND_TAIL()`, so tests should verify that the downstream stack does not retain that temporary vector beyond the call path.

Useful tests include configuring each supported errno, enabling a subset of FOPs, forcing 0 percent and 100 percent failure, exercising legacy `random-failure`, validating short-write behavior on multi-vector writes, reconfiguring while load is active, confirming all disabled FOPs pass through, and checking statedump output after injected operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/error-gen/src/error-gen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/error-gen/src/error-gen.h -->
# sources/distributed-fs/glusterfs/xlators/debug/error-gen/src/error-gen.h

## Purpose
Declares the private state and errno-table shape used by the `debug/error-gen` translator. It also defines the translator's pseudo-error range for behavior that cannot be represented by a normal `-1, op_errno` result.

## Important APIs, types, and functions
`GF_FAILURE_DEFAULT` is a legacy default percentage constant. `enum GF_PSEUDO_ERRORS` currently defines `GF_ERROR_SHORT_WRITE = 1000`, used to make `writev` pass a smaller iovec rather than unwind with an errno. `eg_t` is the private xlator state: `enable[GF_FOP_MAXVALUE]`, `op_count`, `failure_iter_no`, `error_no_int`, `random_failure`, and `gf_lock_t lock`. `sys_error_t` stores an errno count and fixed-size errno array used by `error_no_list[]` in the C file.

## Control flow
The header does not implement behavior, but its fields directly drive `error_gen()`. `failure_iter_no` is deliberately overloaded: in legacy `random-failure` mode it is an operation interval, while in normal mode it is the numerator for the configured failure percentage against the C file's `FAILURE_GRANULARITY`.

## State and persistence behavior
All declared state is private in-memory translator state. It is allocated in `init()`, mutated by `reconfigure()` and FOP execution, exposed through statedump, and freed in `fini()`. No on-disk format or network serialization is defined here.

## Dependencies and integration points
Includes `error-gen-mem-types.h` for allocation tags and depends on GlusterFS core definitions brought in by the C file, especially `GF_FOP_MAXVALUE`, `gf_boolean_t`, and `gf_lock_t`. The pseudo-error constant is consumed by the `writev` failure path.

## Risks and test signals
The overloaded `failure_iter_no` name is easy to misuse when adding features. `sys_error_t.error_no[20]` assumes no FOP errno list grows beyond 20 entries. Future pseudo-errors need to stay outside platform errno ranges and must be handled explicitly by wrappers. Tests should cover the short-write pseudo-error and any change to FOP count or errno list sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/error-gen/src/error-gen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/io-stats/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/debug/io-stats/Makefile.am

## Purpose
Top-level Automake fragment for the GlusterFS `debug/io-stats` translator directory.

## Important APIs, types, and functions
`SUBDIRS = src` delegates all build work to the implementation subdirectory. `CLEANFILES =` is intentionally empty.

## Control flow
Automake descends into `src` when building, installing, cleaning, or distributing this translator.

## State and persistence behavior
No runtime state or persistence exists in this build file.

## Dependencies and integration points
This file connects the `xlators/debug/io-stats` directory into the recursive build. The actual module, headers, compiler flags, and library linkage are defined in `src/Makefile.am`.

## Risks and test signals
Build risk is low. A missing or misspelled `SUBDIRS` would exclude the translator from builds. Test signal is an autotools build confirming `io-stats.la` is reached through this directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/io-stats/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/io-stats/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/debug/io-stats/src/Makefile.am

## Purpose
Builds and installs the `io-stats` xlator shared module.

## Important APIs, types, and functions
`xlator_LTLIBRARIES = io-stats.la` declares the module, with `xlatordir` targeting `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/debug`. `io_stats_la_SOURCES = io-stats.c` and `noinst_HEADERS = io-stats-mem-types.h` define the source set. `io_stats_la_LIBADD` links against `libglusterfs.la`. `AM_CPPFLAGS` adds libglusterfs, generated RPC/XDR, rpc-lib include paths, and defines `DATADIR` from `$(localstatedir)`. `AM_CFLAGS` adds warning and GlusterFS C flags.

## Control flow
The autotools build compiles `io-stats.c` with the listed include paths, links a module with default xlator LDFLAGS, and installs it under the debug xlator directory for runtime graph loading.

## State and persistence behavior
No runtime state is stored here. The `DATADIR` macro affects runtime dump paths in `io-stats.c`, so packaging/localstatedir choices influence where periodic stats files are created.

## Dependencies and integration points
Integrates with the GlusterFS module build system, libtool, libglusterfs, and generated RPC/XDR headers. The noinst memory header is private to this module.

## Risks and test signals
Risks include missing include paths for generated RPC headers and incorrect `DATADIR` causing dump files to land in the wrong local-state tree. Test by building the target and verifying `io-stats.la` links and installs to the expected xlator path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/io-stats/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/io-stats/src/io-stats-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/debug/io-stats/src/io-stats-mem-types.h

## Purpose
Defines memory-accounting type IDs for allocations made by the `debug/io-stats` translator.

## Important APIs, types, and functions
The `gf_io_stats_mem_types_` enum starts at `gf_common_mt_end + 1` and defines tags for `ios_conf`, `ios_fd`, `ios_stat`, `ios_stat_list`, `ios_sample_buf`, `ios_sample`, and the sentinel `gf_io_stats_mt_end`. It also declares `extern const char *__progname`, which `io-stats.c` uses when forming dump filenames.

## Control flow
`mem_acct_init()` in `io-stats.c` passes `gf_io_stats_mt_end` to `xlator_mem_acct_init()`. Allocation sites then use the specific tags with `GF_CALLOC()` or related allocation helpers.

## State and persistence behavior
The enum does not hold runtime state. It affects in-memory accounting and diagnostics only.

## Dependencies and integration points
Includes `glusterfs/mem-types.h` for the shared memory-type base. Integrated with GlusterFS memory accounting and the module build.

## Risks and test signals
Adding allocation categories requires keeping the enum before the sentinel and ensuring `mem_acct_init()` still covers all tags. Tests should include memory-accounting initialization and leak diagnostics for the io-stats translator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/io-stats/src/io-stats-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/io-stats/src/io-stats.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/io-stats/src/io-stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/sink/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/debug/sink/Makefile.am

## Purpose
Top-level Automake fragment for the `debug/sink` translator directory.

## Important APIs, types, and functions
`SUBDIRS = src` delegates build work to the implementation directory.

## Control flow
Recursive Automake enters `src` to build and install the sink translator.

## State and persistence behavior
No runtime state or persistence is defined here.

## Dependencies and integration points
Connects `xlators/debug/sink` to the broader GlusterFS build. Module-specific details are in `src/Makefile.am`.

## Risks and test signals
Build risk is limited to ensuring `src` participates in recursive builds. Test by running the automake build and confirming `sink.la` is produced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/sink/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/sink/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/debug/sink/src/Makefile.am

## Purpose
Builds and installs the `sink` debug xlator module.

## Important APIs, types, and functions
`xlator_LTLIBRARIES = sink.la` declares the module and `xlatordir` installs it under the versioned debug xlator directory. `sink_la_SOURCES = sink.c`, `sink_la_LIBADD` links `libglusterfs.la`, `sink_la_LDFLAGS` uses default xlator module flags, and `AM_CPPFLAGS` adds libglusterfs and generated RPC/XDR include paths.

## Control flow
The build compiles `sink.c`, links a loadable module, and installs it for graph loading.

## State and persistence behavior
No runtime state is stored by this build file.

## Dependencies and integration points
Integrates with GlusterFS libtool module conventions and libglusterfs. There are no private headers.

## Risks and test signals
The sink translator is small, so build coverage is the main signal: successful compilation and module installation with the expected debug xlator path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/sink/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/sink/src/sink.c -->
# sources/distributed-fs/glusterfs/xlators/debug/sink/src/sink.c

## Purpose
Implements a minimal `debug/sink` translator. It can terminate a graph for debugging by reporting itself up/down to parents and satisfying only root lookup with a directory-like inode response.

## Important APIs, types, and functions
`init()` and `fini()` are no-op lifecycle hooks. `notify()` maps `GF_EVENT_PARENT_UP` to `GF_EVENT_CHILD_UP` and `GF_EVENT_PARENT_DOWN` to `GF_EVENT_CHILD_DOWN` through `default_notify()`. `sink_lookup()` returns success for lookup by unwinding with `op_ret = 0`, `op_errno = 0`, the supplied inode, a zeroed `struct iatt` with `ia_type = IA_IFDIR`, the original xdata, and a zeroed postparent. The exported `fops` table only registers `.lookup`; `cbks` is empty; `xlator_api` identifies the module as `sink`, category `GF_TECH_PREVIEW`.

## Control flow
Mount or `glfs_init()` root lookup reaches `sink_lookup()`, which manufactures enough directory metadata for the root to appear valid and immediately unwinds. Parent graph events are reflected as child graph events so the xlator can be considered available. All other events are ignored, and all unimplemented FOPs fall back to absent/default behavior from the xlator framework.

## State and persistence behavior
There is no private state, allocation, background thread, or durable persistence. Returned lookup metadata is transient and minimal.

## Dependencies and integration points
Includes `glusterfs/defaults.h` for default notification and xlator definitions. Integrates as a debug graph endpoint or placeholder where a child xlator would normally exist.

## Risks and test signals
Because only lookup is implemented and the returned `iatt` is sparse, this xlator is suitable only for narrow debug use. Tests should verify parent-up/down notification mapping, root lookup success, and expected failures or unsupported behavior for non-lookup operations. If advanced debugging use is added, lookup should distinguish paths and populate more metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/sink/src/sink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/trace/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/debug/trace/Makefile.am

## Purpose
Top-level Automake fragment for the `debug/trace` translator directory.

## Important APIs, types, and functions
`SUBDIRS = src` delegates build work to the trace implementation directory. `CLEANFILES =` is empty.

## Control flow
Recursive Automake descends into `src` to build the trace xlator.

## State and persistence behavior
No runtime state or persistence is defined in this file.

## Dependencies and integration points
Connects `xlators/debug/trace` into the recursive GlusterFS build. The implementation and private headers are defined by `src/Makefile.am`.

## Risks and test signals
Build risk is limited to directory inclusion. Test by confirming recursive builds enter `src` and produce `trace.la`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/trace/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/trace/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/debug/trace/src/Makefile.am

## Purpose
Builds and installs the `trace` debug xlator module.

## Important APIs, types, and functions
`xlator_LTLIBRARIES = trace.la` declares the module, with installation under the versioned debug xlator directory. `trace_la_SOURCES = trace.c`, `noinst_HEADERS = trace.h trace-mem-types.h`, `trace_la_LIBADD` links `libglusterfs.la`, and `trace_la_LDFLAGS` uses default xlator module flags. `AM_CPPFLAGS` includes libglusterfs and generated RPC/XDR headers.

## Control flow
The automake target compiles `trace.c` with private trace headers and links a loadable debug xlator.

## State and persistence behavior
No runtime state exists in this build file. It ensures `trace-mem-types.h` is available to the implementation but not installed as a public header.

## Dependencies and integration points
Integrates with the GlusterFS xlator build system, libglusterfs, and generated RPC/XDR include paths.

## Risks and test signals
Build risks include missing private headers and generated include paths. Test with a module build and installed-file check for the versioned debug xlator path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/trace/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/trace/src/trace-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/debug/trace/src/trace-mem-types.h

## Purpose
Defines memory-accounting identifiers for the `debug/trace` translator.

## Important APIs, types, and functions
The `gf_trace_mem_types_` enum starts at `gf_common_mt_end + 1`, defines `gf_trace_mt_trace_conf_t` for the trace configuration object, and ends with `gf_trace_mt_end`.

## Control flow
The trace implementation uses this enum when initializing memory accounting and allocating private trace configuration state.

## State and persistence behavior
No runtime state is held in the header. The enum affects memory-accounting diagnostics only.

## Dependencies and integration points
Includes `glusterfs/mem-types.h` and is listed as a private header in `trace/src/Makefile.am`. It is expected to be consumed by `trace.c` and possibly `trace.h`.

## Risks and test signals
If trace gains more allocation categories, this enum must stay synchronized with `mem_acct_init()` and allocation call sites. Test signals include successful trace memory-accounting initialization and leak reports tagged with the trace type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/trace/src/trace-mem-types.h -->
