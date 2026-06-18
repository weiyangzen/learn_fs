<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/trace/src/trace.c -->
# sources/distributed-fs/glusterfs/xlators/debug/trace/src/trace.c

## Purpose
Debug translator that records GlusterFS FOP calls and callbacks before passing them to its single child. It can log to the process log, to an event-history ring, or both, and is intended for diagnosing call parameters, return values, GFIDs, paths, fd/inode lifetime, locks, xattrs, and stat buffers.

## APIs, Types, and Functions
Exports the translator `xlator_api` with `fops`, `cbks`, `dumpops`, init/fini/reconfigure, and memory accounting. The FOP wrappers cover lookup, stat/readlink, namespace mutations, fd operations, directory operations, locks, xattr ops, xattrop, rchecksum, setattr/fsetattr, and seek. Each wrapper logs request details, stores a GFID pointer in `frame->local` when callbacks need it, then `STACK_WIND`s to the first child. Callback functions format `op_ret`, `op_errno`, returned `iatt`, `statvfs`, lock data, fd pointers, and directory entries, then unwind with `TRACE_STACK_UNWIND`. Helpers include `trace_stat_to_str()`, `dump_history_trace()`, `enable_all_calls()`, `enable_call()`, `process_call_list()`, and `trace_dump_history()`.

## Control Flow, State, and Persistence
`init()` validates exactly one child, allocates `trace_conf_t`, initializes the global `trace_fop_names` table from `gf_fop_list`, applies `include-ops` or `exclude-ops`, creates `this->history` with `eh_new()`, sets `log-file`, `log-history`, `history-size`, and optional `force-log-level`, then stores private config. `reconfigure()` refreshes include/exclude state and toggles log destinations, but does not resize the existing history buffer. Runtime state is in `this->private`, `this->history`, per-frame `local` GFID pointers, and fd/inode ctx markers used so release/releasedir/forget can be logged. The translator does not persist data beyond logs and event-history dumps.

## Dependencies and Integration
Depends on GlusterFS xlator stack macros, event-history, logging, statedump, circ-buffer, time formatting, inode/fd ctx APIs, and FOP enum/name tables. It integrates as a pass-through debug xlator in a volume graph and exposes a dump operation for history.

## Risks and Test Signals
Risks include large fixed log buffers truncating complex data, global `trace_fop_names` shared by all instances, `frame->local` storing raw GFID array pointers from loc/fd/inode objects instead of an owned copy, possible null loc/inode assumptions in debug paths, and `init()` error exits that can leak the allocated config/history on some branches. Test signals are volume startup with valid/invalid child counts, include/exclude filtering, reconfigure toggles, statedump history output, representative FOP request/callback log pairs, and release/releasedir/forget logs after successful open/opendir/lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/trace/src/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/trace/src/trace.h -->
# sources/distributed-fs/glusterfs/xlators/debug/trace/src/trace.h

## Purpose
Private header for the trace translator. It defines trace configuration, per-FOP enable metadata, default history sizing, and logging/unwind helpers used by `trace.c`.

## APIs, Types, and Functions
Defines `TRACE_DEFAULT_HISTORY_SIZE`, `trace_fop_name_t`, global `trace_fop_names[GF_FOP_MAXVALUE]`, and `trace_conf_t` with `log_file`, `log_history`, `history_size`, and `trace_log_level`. `TRACE_STACK_UNWIND()` clears `frame->local` before strict unwind. `LOG_ELEMENT()` sends a formatted record to event history via `gf_log_eh()` and/or the normal log via `gf_log()`.

## Control Flow, State, and Persistence
The header has no standalone control flow, but its macros control callback cleanup and dual-destination logging. State is process memory: the global FOP enable table and each xlator instance's `trace_conf_t`. History persistence is indirect through `this->history` in `trace.c`.

## Dependencies and Integration
Assumes GlusterFS types and symbols such as `gf_boolean_t`, `GF_FOP_MAXVALUE`, `STACK_UNWIND_STRICT`, `THIS`, and logging APIs are already visible through including source files.

## Risks and Test Signals
Because it defines, not declares, `trace_fop_names`, including this header from multiple objects would create duplicate definitions. `LOG_ELEMENT()` relies on `THIS->name`, so thread-local xlator context must be correct. Build coverage of trace and runtime logging with both destinations enabled are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/trace/src/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/Makefile.am

## Purpose
Top-level Automake manifest for feature translators under GlusterFS `xlators/features`.

## APIs, Types, and Functions
Defines conditional directory variables for `cloudsync` and `metadisp`, then lists feature subdirectories in `SUBDIRS`: locks, quota, read-only, quiesce, marker, index, barrier, arbiter, upcall, compress, changelog, gfid-access, snapview, trash, shard, bit-rot, leases, selinux, sdfs, namespace, thin-arbiter, utime, simple-quota, and optional directories. `CLEANFILES` is empty.

## Control Flow, State, and Persistence
Automake traverses `SUBDIRS` in order during build, install, clean, and dist operations. There is no runtime state.

## Dependencies and Integration
Integrated by the GlusterFS build system and configure-time flags `BUILD_CLOUDSYNC` and `BUILD_METADISP`. Child `Makefile.am` files define each translator module.

## Risks and Test Signals
Risks are build omissions, conditional directory mismatch with configure output, or ordering problems if one translator depends on another generated artifact. Test signals are `make`, `make install`, and distribution builds with optional flags both enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/arbiter/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/arbiter/Makefile.am

## Purpose
Directory-level Automake entry for the arbiter feature translator.

## APIs, Types, and Functions
Only declares `SUBDIRS = src` and an empty `CLEANFILES`.

## Control Flow, State, and Persistence
Build traversal descends into `src`, where the actual arbiter module is defined. No runtime behavior or persistent state exists here.

## Dependencies and Integration
Included from `xlators/features/Makefile.am`. The real integration is delegated to `arbiter/src/Makefile.am`.

## Risks and Test Signals
The only meaningful risk is the `src` subdirectory being absent or not generated in distribution archives. Build traversal through `make` is the test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/arbiter/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/arbiter/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/arbiter/src/Makefile.am

## Purpose
Build recipe for the arbiter translator shared object.

## APIs, Types, and Functions
When `WITH_SERVER` is enabled, builds `arbiter.la` as an xlator module under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/features`. Sources are `arbiter.c`; private headers are `arbiter.h` and `arbiter-mem-types.h`; it links `libglusterfs.la`.

## Control Flow, State, and Persistence
Automake compiles the translator with GlusterFS include paths, XDR include paths, `GF_CPPFLAGS`, `GF_CFLAGS`, and `-Wall`. Runtime behavior lives in `arbiter.c`.

## Dependencies and Integration
Depends on the server build toggle, libglusterfs, and generated RPC/XDR headers. The installed module is loaded by volume graphs using the `features/arbiter` xlator.

## Risks and Test Signals
Risks include server-disabled builds omitting the translator and include path drift for XDR/libglusterfs headers. Test signals are module build, installation path correctness, and loading the module in a server-enabled volume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/arbiter/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/arbiter/src/arbiter-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/arbiter/src/arbiter-mem-types.h

## Purpose
Memory-accounting type definitions for the arbiter translator.

## APIs, Types, and Functions
Defines `gf_arbiter_mem_types_t`, starting at `gf_common_mt_end + 1`, with `gf_arbiter_mt_inode_ctx_t` for `arbiter_inode_ctx_t` allocations and `gf_arbiter_mt_end` as the accounting upper bound.

## Control Flow, State, and Persistence
No runtime flow. The enum is consumed by `xlator_mem_acct_init()` and `GF_CALLOC()` in `arbiter.c` to classify per-inode context allocations.

## Dependencies and Integration
Includes `glusterfs/mem-types.h` and is listed as a non-installed header in the arbiter build.

## Risks and Test Signals
Risks are enum collisions if the common memory type contract changes or if new allocations are added without new accounting IDs. Test signals are successful `mem_acct_init()` and memory-accounting reports that classify arbiter inode contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/arbiter/src/arbiter-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/arbiter/src/arbiter.c -->
# sources/distributed-fs/glusterfs/xlators/features/arbiter/src/arbiter.c

## Purpose
Feature translator used for arbiter bricks in replicated volumes. It lets AFR receive successful metadata-shaped responses for selected inode write operations without writing user data to the arbiter brick, while still allowing lookup/self-heal style operations to reach the child.

## APIs, Types, and Functions
Important helpers are `__arbiter_inode_ctx_get()`, `arbiter_inode_ctx_get()`, `arbiter_lookup_cbk()`, `arbiter_fill_writev_xdata()`, and `arbiter_forget()`. FOPs include `lookup`, write-like short-circuit handlers for `truncate`, `ftruncate`, `writev`, `fallocate`, `discard`, and `zerofill`, plus defensive `readv` and `seek` returning `ENOSYS`. The translator exports standard `init`, `fini`, `reconfigure`, `mem_acct_init`, `fops`, `cbks`, `options`, and `xlator_api`.

## Control Flow, State, and Persistence
`lookup` winds to the child and its callback allocates or retrieves `arbiter_inode_ctx_t` under the inode lock, then caches the returned `iatt`. Short-circuited write-like FOPs retrieve that cached `iatt`, return success, and unwind with pre/post buffers both pointing to the cached attributes; `writev` returns `iov_length()` and may echo requested `GLUSTERFS_OPEN_FD_COUNT` and `GLUSTERFS_WRITE_IS_APPEND` xdata. `forget` deletes and frees inode ctx. There is no on-disk persistence in this translator; persistence remains with lower translators for FOPs that are allowed through defaults.

## Dependencies and Integration
Depends on GlusterFS dict, stack, logging, inode ctx, iovec, and memory-accounting APIs. It must have exactly one child and is intended to sit where AFR can target an arbiter child.

## Risks and Test Signals
Risks include stale cached `iatt` if lookup is old, successful write-like replies that do not reflect storage changes, no owned xdata on most short-circuit replies, assumptions that inode/fd and ctx are present, and correctness dependence on AFR not sending normal application reads to the arbiter. Test signals are arbiter-volume lookup/write/truncate/fallocate/discard/zerofill behavior, `ENOSYS` for accidental reads/seeks, inode ctx cleanup on forget, xdata echo behavior for writev, and validation that self-heal/stat/xattr operations still pass through by default.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/arbiter/src/arbiter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/arbiter/src/arbiter.h -->
# sources/distributed-fs/glusterfs/xlators/features/arbiter/src/arbiter.h

## Purpose
Private arbiter translator header defining the per-inode context shape.

## APIs, Types, and Functions
Includes `glusterfs/iatt.h` and defines `arbiter_inode_ctx_t`, which currently stores only one `struct iatt iattbuf`.

## Control Flow, State, and Persistence
No control flow. The struct is allocated in inode ctx on lookup, read by short-circuit write-like FOPs, and freed during forget. It is volatile memory state only.

## Dependencies and Integration
Used by `arbiter.c` and paired with `arbiter-mem-types.h` for allocation accounting.

## Risks and Test Signals
Risk is that a single cached stat buffer may be insufficient if future FOPs need richer metadata or xdata. Build coverage and behavior of cached pre/post attributes in arbiter write replies are the test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/arbiter/src/arbiter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/barrier/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/barrier/Makefile.am

## Purpose
Directory-level Automake entry for the barrier feature translator.

## APIs, Types, and Functions
Declares `SUBDIRS = src` and empty `CLEANFILES`.

## Control Flow, State, and Persistence
Build traversal descends into `src`; no runtime state exists in this file.

## Dependencies and Integration
Included from the top-level features Makefile. The module build itself is in `barrier/src/Makefile.am`.

## Risks and Test Signals
Risk is limited to build traversal or distribution omissions. A full build that enters `barrier/src` is the test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/barrier/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/barrier/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/barrier/src/Makefile.am

## Purpose
Build recipe for the barrier translator module.

## APIs, Types, and Functions
Builds `barrier.la` unconditionally as an xlator module under the features xlator directory. Source is `barrier.c`; private headers are `barrier.h` and `barrier-mem-types.h`; it links `libglusterfs.la`.

## Control Flow, State, and Persistence
Automake compiles with GlusterFS and RPC/XDR include paths plus `GF_CPPFLAGS`, `GF_CFLAGS`, and `-Wall`. Runtime behavior is all in `barrier.c`.

## Dependencies and Integration
Depends on libglusterfs, GlusterFS timer/call-stub/statedump APIs, and generated XDR include paths.

## Risks and Test Signals
Risks are include/library path drift and unconditional module build in configurations where the feature is not expected. Test signals are module compilation, install path, and successful volume loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/barrier/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/barrier/src/barrier-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/barrier/src/barrier-mem-types.h

## Purpose
Memory-accounting type definitions for the barrier translator.

## APIs, Types, and Functions
Defines `gf_barrier_mt_priv_t` for `barrier_priv_t` allocations and `gf_barrier_mt_end` as the memory-accounting bound, starting after common types.

## Control Flow, State, and Persistence
No control flow. Consumed by `mem_acct_init()` and private allocation in `barrier.c`.

## Dependencies and Integration
Includes `glusterfs/mem-types.h` and is a private build header.

## Risks and Test Signals
Risks are missing accounting IDs if more allocation classes are introduced. Test signals are successful memory-accounting initialization and statedump/mem-accounting visibility for barrier private state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/barrier/src/barrier-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/barrier/src/barrier.c -->
# sources/distributed-fs/glusterfs/xlators/features/barrier/src/barrier.c

## Purpose
Feature translator that delays acknowledgements for a narrow class of mutating or durability-sensitive FOPs while a runtime barrier is enabled. The child operation still runs immediately; only the callback unwind to the caller is queued.

## APIs, Types, and Functions
Exports FOPs for `rmdir`, `unlink`, `rename`, `removexattr`, `fremovexattr`, `truncate`, `ftruncate`, `fsync`, and synchronous `writev`. Callback wrappers use `BARRIER_FOP_CBK` to either queue a callback stub or unwind immediately. Helpers include `barrier_local_set_gfid()`, `barrier_local_free_gfid()`, `__barrier_enable()`, `__barrier_disable()`, `__barrier_enqueue()`, `__barrier_dequeue()`, `barrier_dequeue_all()`, `barrier_timeout()`, `notify()`, `reconfigure()`, `barrier_dump_priv()`, and queue dump helpers.

## Control Flow, State, and Persistence
`init()` allocates `barrier_priv_t`, initializes the queue/lock, reads `barrier` and `barrier-timeout`, and optionally starts a timer. Each barrier-class FOP winds to the child and stores an allocated GFID in `frame->local`. When the child callback fires, the macro locks private state; if enabled, it creates a callback stub and appends it to `priv->queue`; otherwise it frees local GFID and unwinds. Disabling via translator op/reconfigure or timeout cancels the timer, splices the queue to a local list, marks disabled, and resumes queued stubs. State is volatile memory: queue, timer, timeout, enabled flag, and queue size.

## Dependencies and Integration
Uses GlusterFS timer, call-stub, list, lock, default notify, xlator option, and statedump APIs. Runtime control comes through `GF_EVENT_TRANSLATOR_OP` with a `barrier` dict key and through settable volume options.

## Risks and Test Signals
Risks include callback-stub allocation failure disabling the barrier, queued callback growth until timeout/disable, synchronous writes without `O_SYNC`/`O_DSYNC` bypassing the barrier, cancellation races around timer changes, and `barrier_dump_priv()` returning `-1` even after a successful dump. Test signals are enabling/disabling through volume set and translator op, queued acknowledgement ordering, timeout release, statedump queue contents with GFIDs/paths, sync-write filtering, and cleanup on fini.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/barrier/src/barrier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/barrier/src/barrier.h -->
# sources/distributed-fs/glusterfs/xlators/features/barrier/src/barrier.h

## Purpose
Private interface and shared macro support for the barrier translator.

## APIs, Types, and Functions
Defines `barrier_priv_t` with timer, lock, queued callback stubs, timeout, queue size, enabled flag, and padding. Declares queue/timer enable/disable helpers. The `BARRIER_FOP_CBK` macro implements callback-time gating: create a callback stub while enabled, enqueue it, or unwind and release frame-local GFID when not queued.

## Control Flow, State, and Persistence
The macro centralizes the callback control flow for all barriered FOPs and is responsible for switching from normal unwind to queued deferred unwind. State is volatile and owned by `barrier_priv_t`.

## Dependencies and Integration
Depends on `barrier-mem-types.h`, call stubs, GlusterFS stack unwind macros, locks, lists, and logging. Included only by `barrier.c`.

## Risks and Test Signals
Macro complexity can obscure ownership of `_stub`, `frame->local`, and lock/unlock paths. Stubs must match each FOP callback signature exactly. Test signals are build coverage of every macro expansion and runtime tests for allocation-failure, enabled, disabled, and timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/barrier/src/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/Makefile.am

## Purpose
Directory-level Automake entry for the bit-rot feature.

## APIs, Types, and Functions
Declares `SUBDIRS = src`.

## Control Flow, State, and Persistence
Build traversal descends into `src`. There is no runtime state or cleanup rule here.

## Dependencies and Integration
Included by the top-level features Makefile. Actual bit-rot build definitions are below `src`.

## Risks and Test Signals
Risk is limited to traversal/distribution omissions. A build that enters `bit-rot/src` is the test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/Makefile.am

## Purpose
Build traversal manifest for bit-rot subcomponents.

## APIs, Types, and Functions
Declares `SUBDIRS = stub bitd`, building the bit-rot stub and daemon-side translator pieces.

## Control Flow, State, and Persistence
Automake descends into `stub` and `bitd` in that order. No runtime state exists here.

## Dependencies and Integration
The ordering implies shared stub headers or libraries are available before `bitd` compiles.

## Risks and Test Signals
Risks are missing child directories and ordering drift if `bitd` depends on generated stub artifacts. Full bit-rot builds are the test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/Makefile.am

## Purpose
Build recipe for the daemon-side bit-rot translator module.

## APIs, Types, and Functions
When `WITH_SERVER` is enabled, builds `bit-rot.la` from `bit-rot.c`, `bit-rot-scrub.c`, `bit-rot-ssm.c`, and `bit-rot-scrub-status.c`. Private headers include `bit-rot.h`, scrub headers, message IDs, and state-machine header. It links libglusterfs and `libgfchangelog.la`, and compiles with `-DBR_RATE_LIMIT_SIGNER`.

## Control Flow, State, and Persistence
Automake sets include paths for libglusterfs, RPC/XDR, rpc-lib, timer-wheel contrib code, and the bit-rot stub. Runtime behavior is in the C sources.

## Dependencies and Integration
Depends on server builds, changelog library, timer-wheel, bit-rot stub headers, and GlusterFS core headers. Installs as an xlator under `features`.

## Risks and Test Signals
Risks include server-disabled omission, link dependency drift with changelog/timer-wheel, and CFLAGS changing signer throttling behavior. Test signals are server build/link, module load, changelog integration, and scrub/signing runtime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-bitd-messages.h -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-bitd-messages.h

## Purpose
Message ID and canonical string catalog for the bit-rot daemon translator.

## APIs, Types, and Functions
Uses `GLFS_MSGID(BITROT_BITD, ...)` to allocate stable message identifiers for fd creation, reads, checksums, signing, changelog registration, crawling, scrub scheduling, corruption marking, bad-object listing, memory, timer, and state-machine events. Also defines string macros for common message text.

## Control Flow, State, and Persistence
No runtime flow. Stability is persistent at the logging ABI level: comments require appending new IDs and never removing old ones to avoid ID reuse.

## Dependencies and Integration
Includes `glusterfs/glfs-message-id.h` and is included by bit-rot daemon sources for `gf_msg()` calls.

## Risks and Test Signals
Risks include accidental ID removal/reordering, typos in strings becoming operator-visible, and missing strings for newer IDs. Test signals are successful compilation of all `gf_msg()` uses and log/message catalog consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-bitd-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub-status.c -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub-status.c

## Purpose
Thread-safe counters and timestamp updates for bit-rot scrub statistics.

## APIs, Types, and Functions
Implements `br_inc_unsigned_file_count()`, `br_inc_scrubbed_file()`, `br_update_scrub_start_time()`, and `br_update_scrub_finish_time()`. These update fields in `br_scrub_stats_t` under its pthread mutex.

## Control Flow, State, and Persistence
Each function returns immediately on null input. Counter increments lock, update one counter, and unlock. Start time stores `scrub_start_time`. Finish time validates the supplied formatted time fits in `last_scrub_time`, then records `scrub_end_time`, calculates `scrub_duration`, and copies the string. State is volatile in `br_private_t.scrub_stat` and later exposed by bit-rot status code.

## Dependencies and Integration
Depends on pthreads, `GF_TIMESTR_SIZE` from GlusterFS common utilities, and `bit-rot-scrub-status.h`. Called by scrub execution in `bit-rot-scrub.c` and status export in `bit-rot.c`.

## Risks and Test Signals
Risks include unsynchronized readers elsewhere seeing partial stats, finish updates silently skipped if the time string is too long, and duration underflow if finish precedes start due to bad sequencing. Test signals are concurrent scrub counter updates, status dictionary values, and start/finish duration correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub-status.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub-status.h -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub-status.h

## Purpose
Defines the scrub statistics structure and update API for bit-rot scrub status.

## APIs, Types, and Functions
`struct br_scrub_stats` tracks `scrubbed_files`, `unsigned_files`, last scrub duration, formatted last scrub completion time, start/end timestamps, `scrub_running`, and a pthread mutex. Declares the increment and start/finish update functions implemented in the C file.

## Control Flow, State, and Persistence
The header has no control flow. It defines volatile process state stored inside `br_private_t` and consumed by scrub execution and status reporting.

## Dependencies and Integration
Includes standard integer/time/pthread headers and relies on GlusterFS time string sizing being available to includers.

## Risks and Test Signals
Risks are lock initialization/destruction ownership outside this header and readers that do not take the lock. Test signals are clean initialization, concurrent scrub updates, and exported status fields matching expected counters and timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub-status.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub.c -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub.c

## Purpose
Implements daemon-side bit-rot filesystem scrubbing: scheduled or on-demand traversal of child bricks, checksum verification against object signatures, marking corrupt objects, bad-object collection, scrub worker scaling, scrub option handling, and scrub monitor initialization.

## APIs, Types, and Functions
Major object-verification helpers are `bitd_fetch_signature()`, `bitd_scrub_pre_compute_check()`, `bitd_scrub_post_compute_check()`, `bitd_compare_ckum()`, and `br_scrubber_scrub_begin()`. Scanner/worker flow is handled by `br_fsscanner()`, `br_fsscanner_handle_entry()`, `wait_for_scrubbing()`, `br_scrubber_proc()`, queue helpers, and cleanup handlers. Scheduling APIs include `br_fsscan_schedule()`, `br_fsscan_activate()`, `br_fsscan_reschedule()`, `br_fsscan_deactivate()`, and `br_fsscan_ondemand()`. Option APIs include `br_scrubber_handle_options()` and throttle/frequency helpers. Status and integration APIs include `br_child_set_scrub_state()`, `br_collect_bad_objects_from_children()`, `br_get_bad_objects_list()`, `br_monitor_thread()`, `br_scrubber_monitor_init()`, and `br_scrubber_init()`.

## Control Flow, State, and Persistence
The timer-wheel callback `br_kickstart_scanner()` resets stats, moves the monitor to active, and broadcasts a kick to per-child scanner threads. Each scanner walks its child with `syncop_ftw()`, batches entries into `br_scanfs.queued`, swaps queued entries to ready, and wakes scrubber workers. Workers round-robin across children, run lookup/open, skip non-regular and DHT linkfiles, fetch signature/version before checksum, compute SHA256, refetch signature after checksum to avoid races, compare hashes, and set `BITROT_OBJECT_BAD_KEY` plus `EVENT_BITROT_BAD_FILE` on mismatch. Monitor state, child active flags, queues, timer, worker count, and scrub stats are in `br_private_t`, `br_child_t`, `br_scanfs`, `br_scrubber`, and `br_monitor`; persistent effects are xattrs on corrupted objects and quarantine/bad-object directory contents read through child translators.

## Dependencies and Integration
Depends on GlusterFS syncop lookup/open/readdir/fgetxattr/fsetxattr/ftw, inode/fd/loc helpers, timer-wheel, changelog-era bit-rot signature xattrs, SHA256 checksum helpers, pthreads, token-bucket initialization, event reporting, message IDs, and state-machine functions in `bit-rot-ssm.c`. It is initialized and driven by the main bit-rot translator in `bit-rot.c`.

## Risks and Test Signals
Risks include races with concurrent signing or writes despite pre/post checks, cancellation while worker owns queued entries, scanner/worker deadlocks around condition variables, memory pressure in copied entries and signatures, bad-object marking failure after mismatch detection, shard-stat exceptions hiding counts, and zero-timeout bugs for stalled/invalid frequency. Test signals are scrub scheduling/rescheduling/ondemand, pause/resume, connected/disconnected child handling, checksum mismatch marking and event emission, unsigned/stale signature counts, bad-object list aggregation, worker scale up/down by throttle, and long-running cancellation/cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub.h -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub.h

## Purpose
Public internal interface for bit-rot scrub scheduling, initialization, option handling, scanner entry point, and bad-object collection.

## APIs, Types, and Functions
Declares `br_fsscanner()`, schedule/reschedule/activate/deactivate/ondemand functions, `br_scrubber_handle_options()`, `br_scrubber_monitor_init()`, `br_scrubber_init()`, `br_collect_bad_objects_from_children()`, and `br_child_set_scrub_state()`.

## Control Flow, State, and Persistence
No direct control flow. The declarations expose the scrub subsystem to `bit-rot.c` and the state machine, allowing lifecycle code to start scanner threads, configure scrub behavior, and ask children for bad-object inventories.

## Dependencies and Integration
Includes `bit-rot.h`, so callers share `br_private_t`, `br_child_t`, xlator, dict, and scrub state definitions.

## Risks and Test Signals
Risks are contract drift between this header and `bit-rot-scrub.c`, especially for functions used by `bit-rot-ssm.c`. Build coverage and runtime calls from init/reconfigure/CLI status paths are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-ssm.c -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-ssm.c

## Purpose
Scrub state machine implementation for bit-rot. It maps current scrub monitor state and requested event to scheduling, pausing, resuming, or on-demand actions.

## APIs, Types, and Functions
Implements action functions `br_scrub_ssm_noop()`, `br_scrub_ssm_state_pause()`, `br_scrub_ssm_state_ipause()`, `br_scrub_ssm_state_active()`, and `br_scrub_ssm_state_stall()`, plus `br_scrub_state_machine()`. The static `br_scrub_ssm[BR_SCRUB_MAXSTATES][BR_SCRUB_MAXEVENTS]` table maps inactive/pending/active/paused/ipaused/stalled states against schedule/pause/ondemand events.

## Control Flow, State, and Persistence
`br_scrub_state_machine()` reads `priv->scrub_monitor.state`, derives the event from the on-demand flag or `_br_child_get_scrub_event()`, then invokes the table entry. Actions call scheduler functions in `bit-rot-scrub.c` or update `scrub_monitor->state` directly. State is volatile monitor state; no disk persistence occurs here.

## Dependencies and Integration
Depends on `bit-rot-ssm.h`, `bit-rot-scrub.h`, message IDs, and `br_private_t` definitions from `bit-rot.h`. Called by monitor startup, reconfigure, and on-demand control paths in the main bit-rot translator.

## Risks and Test Signals
Risks include invalid state/event indexes if enums drift, no null validation on `this->private`, subtle differences between paused and initially paused states, and on-demand no-op behavior in several states. Test signals are transition tests for schedule, pause, resume, stalled active scrub, and on-demand requests from pending versus non-pending states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-ssm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-ssm.h -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-ssm.h

## Purpose
Defines scrub states, scrub events, and the state-machine entry point for bit-rot scrubbing.

## APIs, Types, and Functions
Defines `br_scrub_state_t` values `INACTIVE`, `PENDING`, `ACTIVE`, `PAUSED`, `IPAUSED`, `STALLED`, and `BR_SCRUB_MAXSTATES`; defines `br_scrub_event_t` values `SCHEDULE`, `PAUSE`, `ONDEMAND`, and `BR_SCRUB_MAXEVENTS`; forward-declares `struct br_monitor`; declares `br_scrub_state_machine(xlator_t *, gf_boolean_t)`.

## Control Flow, State, and Persistence
No direct control flow. The enum numeric order is part of the table contract in `bit-rot-ssm.c`, and current state is stored in `struct br_monitor` from `bit-rot.h`.

## Dependencies and Integration
Includes `glusterfs/defaults.h` for xlator and boolean-related defaults. Used by `bit-rot.h`, `bit-rot-scrub.c`, and `bit-rot-ssm.c`.

## Risks and Test Signals
Risks are enum reordering without updating the state table and adding states/events without table coverage. Build coverage plus transition tests for every enum value are the test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-ssm.h -->
