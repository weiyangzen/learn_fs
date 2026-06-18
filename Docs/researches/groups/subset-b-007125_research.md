# subset-b-007125 GlusterFS NLM callback and performance translator research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nlmcbk_svc.c -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nlmcbk_svc.c

## Purpose
Implements the rpcgen-generated NLM callback service used by Gluster NFS lock management to receive NSM/NLM callback notifications. The file registers `NLMCBK_PROGRAM` version `NLMCBK_V1` on UDP and TCP, dispatches the `NLMCBK_SM_NOTIFY` procedure, and starts the shared NFS RPC poller.

## Important APIs, types, and functions
`nlmcbk_sm_notify_0_svc()` adapts the RPC service entry point to `nlm4svc_sm_notify()`. `nlmcbk_program_0()` is the RPC procedure switch, decodes `xdr_nlm_sm_status`, sends void replies, and frees arguments. `nsm_thread()` is the worker entry that unsets any existing portmapper registration, creates UDP/TCP transports, registers the callback program, sets `THIS`, and calls `nfs_start_rpc_poller()`.

## Control flow
The NFS translator starts `nsm_thread()` with the NFS xlator pointer. The thread registers transports, then the SunRPC service layer invokes `nlmcbk_program_0()` for incoming calls. `NULLPROC` receives an immediate void reply; `NLMCBK_SM_NOTIFY` is decoded and forwarded into the NLM implementation, then replied to with an XDR void result.

## State and persistence behavior
No durable state is stored here. Runtime state is the RPC transport registration in portmap/rpcbind and the process-global xlator context `THIS` for the callback thread. Failure paths log and return without cleaning earlier registrations or transports.

## Dependencies and integration points
Depends on `nlm4.h` for NLM program/procedure constants, XDR functions, and `nfs_start_rpc_poller()`. It integrates with `nlm4svc_sm_notify()` in the NLM server path, the process portmapper, libtirpc/SunRPC `svc_*` APIs, Gluster logging, and NFS message IDs.

## Risks and test signals
Risks include generated-code drift from `nlm4.x`, leaked UDP transport if TCP registration fails, portmapper conflicts, missing `errno` propagation on registration failures, and callback service startup silently ending before the poller starts. Useful tests include simulated `NULLPROC` and `NLMCBK_SM_NOTIFY` RPCs over UDP/TCP, rpcbind registration/unregistration conflicts, malformed XDR decode, argument-free failure logging, and NFS lock recovery after an NSM status notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nlmcbk_svc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/performance/Makefile.am

## Purpose
Defines the automake traversal order for the GlusterFS performance translator family. It causes build/install recursion into write-behind, read-ahead, readdir-ahead, io-threads, io-cache, quick-read, md-cache, open-behind, and nl-cache.

## Important APIs, types, and functions
There are no C APIs. `SUBDIRS` is the significant build interface because it controls which translator modules are included in the performance xlator subtree. `CLEANFILES` is present but empty.

## Control flow
During `make`, automake recurses into the listed directories. io-threads, io-cache, and md-cache build rules in this subset are reachable only because they appear in this parent list.

## State and persistence behavior
No runtime state is involved. The persistent behavior is build/install inclusion in generated makefiles.

## Dependencies and integration points
Integrates with the top-level autotools build and package layout for `xlator/performance` modules. Adding or removing a performance translator requires this list to remain consistent with the child directory and volfile expectations.

## Risks and test signals
Risks are build omissions, install omissions, and stale subdirectory names. Test signals are successful `make` recursion, packaged `.so` files for each listed translator, and `make distcheck` catching missing or renamed subdirectories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-cache/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/performance/io-cache/Makefile.am

## Purpose
Routes automake recursion for the io-cache translator into its `src` directory.

## Important APIs, types, and functions
`SUBDIRS = src` is the only functional build contract. `CLEANFILES` is empty.

## Control flow
The performance parent makefile enters this directory, then automake enters `src`, where `io-cache.la` is built.

## State and persistence behavior
No runtime state exists; this file only persists the module's build topology.

## Dependencies and integration points
Depends on `src/Makefile.am` to define the actual shared xlator. It integrates with the parent performance translator build.

## Risks and test signals
The main risk is a broken recursive build if `src` is renamed or omitted. Build tests should confirm `io-cache.la` is produced from a clean tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-cache/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/Makefile.am

## Purpose
Builds the `io-cache` performance translator as a loadable GlusterFS xlator module.

## Important APIs, types, and functions
`xlator_LTLIBRARIES = io-cache.la` declares the plugin. `io_cache_la_SOURCES` compiles `io-cache.c`, `page.c`, and `ioc-inode.c`. `noinst_HEADERS` tracks `io-cache.h`, `ioc-mem-types.h`, and `io-cache-messages.h`. `io_cache_la_LIBADD` links against `libglusterfs.la`.

## Control flow
Autotools compiles the three C files, links a module with `GF_XLATOR_DEFAULT_LDFLAGS`, and installs it under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/performance`.

## State and persistence behavior
No runtime state is stored. The file fixes the module name, install location, include path surface, and linkage.

## Dependencies and integration points
Depends on libglusterfs headers, generated RPC/XDR include directories, and the contrib rbtree path because io-cache uses `rbthash`. The installed module is discovered by Gluster's translator loader and volfile parser.

## Risks and test signals
Risks include omitting one of the three cooperative implementation files, missing rbtree include paths, or creating a module that links but lacks required xlator symbols. Test signals include successful module build, symbol presence for `xlator_api`, and runtime load of `performance/io-cache`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/io-cache-messages.h -->
# sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/io-cache-messages.h

## Purpose
Defines stable log message IDs and reusable message strings for the io-cache translator.

## Important APIs, types, and functions
`GLFS_MSGID(IO_CACHE, ...)` allocates message identifiers such as `IO_CACHE_MSG_NO_MEMORY`, `IO_CACHE_MSG_PAGE_FAULT`, `IO_CACHE_MSG_SERVE_READ_REQUEST`, and `IO_CACHE_MSG_DEFAULTING_TO_OLD`. The `_STR` macros provide human-readable text for common logging paths.

## Control flow
No control flow is implemented. C files include this header and pass the IDs to `gf_smsg()` or `gf_msg()` on allocation, validation, configuration, and cache fault errors.

## State and persistence behavior
Message IDs are part of Gluster's externally visible log compatibility surface. The comments require append-only changes to prevent ID reuse.

## Dependencies and integration points
Depends on `glfs-message-id.h` and the global `IO_CACHE` component registration. It integrates with structured logging, downstream log parsers, and support tooling that keys off message IDs.

## Risks and test signals
Risks are deleting/reordering IDs, misspelled strings, and logging an ID for the wrong component. Test signals are compile-time inclusion, message catalog consistency checks, and log assertions on representative io-cache error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/io-cache-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/io-cache.c -->
# sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/io-cache.c

## Purpose
Implements the main io-cache translator: lifecycle, volume options, FOP interception, cache validation, cache invalidation, page fault dispatch, priority parsing, pruning triggers, and statedump support. It caches read data in per-inode pages and forwards all operations to its single child as needed.

## Important APIs, types, and functions
`ioc_readv()` is the read entry point and either bypasses caching or initializes an `ioc_local_t` and calls `ioc_dispatch_requests()`. `ioc_dispatch_requests()` maps a read range to page offsets, handles ready pages, in-flight pages, cache misses, and timeout validation. `ioc_cache_validate()` and `ioc_cache_validate_cbk()` issue child `fstat` requests when cached pages are older than `cache-timeout`. `ioc_update_pages()` refreshes cached page data after successful writes. Mutating operations such as `ioc_setattr()`, `ioc_truncate()`, `ioc_ftruncate()`, `ioc_discard()`, and `ioc_zerofill()` flush affected inode caches. `init()`, `reconfigure()`, `fini()`, and `mem_acct_init()` define the xlator lifecycle. `ioc_get_priority_list()` and `ioc_get_priority()` implement pattern-based eviction priority.

## Control flow
Lookup, create, mknod, open, and readdirp callbacks create or update `ioc_inode_t` state and apply fd-level bypass for size limits, `O_DIRECT`, or priority zero. A cached read ensures the inode has a page table, checks fd bypass, enqueues the caller on each requested page, then either wakes immediately from ready pages, schedules `ioc_page_fault()` for misses, or schedules `fstat` validation for old pages. Fault and validation callbacks later wake the queued frames; `ioc_frame_return()` unwinds only after the frame has received all page fragments.

## State and persistence behavior
Runtime state lives in `ioc_table_t` at `this->private`, inode contexts containing `ioc_inode_t`, fd contexts used as cache-bypass flags, page tables, LRU lists, wait queues, and per-frame `ioc_local_t` objects. There is no durable persistence. Reconfigure mutates cache size, timeout, file-size filters, pass-through, and priority lists; existing cached pages remain unless normal invalidation/pruning removes them.

## Dependencies and integration points
Depends on Gluster xlator FOP/callback APIs, inode/fd context APIs, `rbthash`, iovec/iobref helpers, memory pools, `dict_t`, statedump, logging/message IDs, option parsing macros, and child translator `readv`/`fstat`/metadata FOPs. It integrates with graph options such as `performance.io-cache`, NFS read behavior through `op_errno`, and inode invalidation callbacks from lower translators.

## Risks and test signals
Key risks are stale data if mtime/nsec validation misses a mutation, wait-count imbalance across page faults and validation, incorrect `cache_used` accounting when pages are stale or destroyed, priority-list reconfigure leaking old entries, missing fd refs in write paths, and lock ordering between table and inode locks during prune. High-value tests include cache hit/miss reads across page boundaries, concurrent readers waiting on the same page, validation timeout with unchanged and changed mtimes, write-through cache updates, truncate/discard/zerofill invalidation, `O_DIRECT` and size-limit bypass, priority zero bypass, cache-size pruning by priority, statedump under contention, and clean teardown after inode forget.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/io-cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/io-cache.h -->
# sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/io-cache.h

## Purpose
Declares the io-cache translator's shared data structures, defaults, locking helpers, and cross-file function prototypes.

## Important APIs, types, and functions
`ioc_table_t` stores translator-wide page size, cache size, cache usage, file-size filters, inode LRU buckets, priority list, cache timeout, and memory pools. `ioc_inode_t` binds cache state to a Gluster inode. `ioc_cache` owns the per-inode page table, page LRU, mtime/nsec validation state, and last validation time. `ioc_page_t` represents one cached page, its vectors, iobref, wait queue, ready/stale flags, and lock. `ioc_local_t`, `ioc_waitq_t`, and `ioc_fill_t` model in-flight read assembly. Locking macros wrap table, inode, and local mutexes with trace logging.

## Control flow
The header does not execute logic, but it defines the contracts used across `io-cache.c`, `page.c`, and `ioc-inode.c`: page creation/destruction, waiting/wakeup, page faulting, frame return, inode creation/destruction, cache validity, and pruning.

## State and persistence behavior
All declared state is in-memory translator state. The header fixes the shape of inode contexts, fd-bypass interactions, and page cache accounting, but it has no on-disk format.

## Dependencies and integration points
Includes Gluster dict, call-stub, rbthash, compat errno, iobref/iovec-adjacent types through included headers, fnmatch, and io-cache message IDs. It is the internal ABI among the io-cache implementation files.

## Risks and test signals
Risks include structure fields being accessed without the expected lock, misuse of `char` flags for ready/stale/dirty state, global assumptions around `IOC_PAGE_TABLE_BUCKET_COUNT`, and prototypes that imply lock ownership only through naming. Tests should stress multi-page reads, concurrent invalidation, lock-order safety, and cache accounting around all callers of `__ioc_page_destroy()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/io-cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/ioc-inode.c -->
# sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/ioc-inode.c

## Purpose
Provides inode-scoped helpers for io-cache: pointer-string conversion utilities, cache-validation wakeup handling, inode cache object creation, and destruction.

## Important APIs, types, and functions
`ioc_inode_create()` allocates an `ioc_inode_t`, initializes page LRU and mutex state, assigns priority weight, and links it into table inode lists. `ioc_inode_destroy()` removes an inode from table lists, flushes pages, destroys its page table, and frees the object. `ioc_inode_wakeup()` processes the inode-level validation wait queue, either waking ready pages when cache metadata is still valid or issuing new page faults when it is not. `ptr_to_str()` and `str_to_ptr()` convert pointer values for string storage/use.

## Control flow
When `io-cache.c` creates or discovers inode state, this file links it into eviction structures. During fstat validation, pages waiting on inode validation are queued at `ioc_inode->waitq`; the validation callback calls `ioc_inode_wakeup()`, which iterates those pages and either wakes their frame wait queues or restarts page reads.

## State and persistence behavior
State is in-memory only: table inode counters, `inodes` and `inode_lru` lists, page table ownership, and wait queues. Destroy is normally triggered from the inode `forget` callback.

## Dependencies and integration points
Depends on `io-cache.h`, io-cache memory types, Gluster inode contexts, list primitives, rbthash lifecycle, and page helpers from `page.c`.

## Risks and test signals
Risks include using priority weights outside allocated LRU bucket bounds, destroying an inode with active page waiters, races between validation wakeup and page fault callbacks, and pointer-string conversion truncation on unusual platforms. Test signals include inode create/update/forget cycles, validation wait queues with multiple pages, invalidation while faults are in flight, and teardown with empty and non-empty page tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/ioc-inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/ioc-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/ioc-mem-types.h

## Purpose
Defines io-cache-specific memory accounting type IDs.

## Important APIs, types, and functions
`enum gf_ioc_mem_types_` starts at `gf_common_mt_end + 1` and names allocation classes for iovecs, tables, strings, wait queues, priorities, list heads, call pools, inodes, fill records, and pages.

## Control flow
No runtime control flow exists. `mem_acct_init()` in `io-cache.c` registers up to `gf_ioc_mt_end`, and allocation sites pass these enum values to `GF_CALLOC`, `GF_MALLOC`, or related helpers.

## State and persistence behavior
The IDs feed runtime memory accounting. They are not persisted but affect diagnostics and leak attribution.

## Dependencies and integration points
Depends on `glusterfs/mem-types.h` and integrates with Gluster's xlator memory accounting subsystem.

## Risks and test signals
Risks are enum overlap with common types, missing new allocation categories, or changing IDs in ways that confuse diagnostics. Test signals include successful `xlator_mem_acct_init()`, memory statedump categories, and leak tests for page/fill/waitq paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/ioc-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/page.c -->
# sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/page.c

## Purpose
Implements the page-level mechanics for io-cache: page lookup/creation/destruction, LRU pruning, wait queues, child read fault callbacks, read-result assembly, and page error handling.

## Important APIs, types, and functions
`__ioc_page_get()` looks up a rounded offset in the inode `rbthash` and refreshes page LRU position. `__ioc_page_create()` allocates and inserts a page. `__ioc_page_destroy()` removes and frees pages unless waiters force the page stale. `ioc_prune()` and `__ioc_inode_prune()` evict least-recent pages across priority buckets. `__ioc_wait_on_page()` queues a frame for a page range. `ioc_fault_cbk()` stores child `readv` data into the page and wakes waiters. `__ioc_frame_fill()` converts page data into per-frame `ioc_fill_t` fragments. `ioc_frame_unwind()` merges fragments into the final read reply.

## Control flow
`ioc_dispatch_requests()` from `io-cache.c` creates page waiters and starts faults. The child `readv` callback updates mtime validation state, copies vectors/iobrefs into the page, marks the page ready, fills each waiting frame, and lets `ioc_waitq_return()` decrement frame wait counts. A frame unwinds only after all page waiters have returned, so multi-page reads can complete in any fault order while still assembling the output by offset.

## State and persistence behavior
State is the in-memory page table, page LRU, wait queues, cached iovec/iobref references, ready/stale flags, and cache-used byte accounting. No durable data is stored; cached data is discarded on flush, prune, error, forget, or process shutdown.

## Dependencies and integration points
Depends on io-cache structures, Gluster iovec/iobref helpers, rbthash, child `readv`, memory accounting types, message IDs, and table/inode locks. It is tightly integrated with `io-cache.c` for dispatch/validation and `ioc-inode.c` for inode lifecycle.

## Risks and test signals
Risks include underflow/overflow in range math, copying zero or short pages incorrectly, stale-page destruction while waiters exist, `cache_used` divergence from actual iobref size, wait-count imbalance, lost errors when one page of a multi-page read fails, and memory leaks around `iov_subset()` or iobref merge failures. Tests should cover EOF short reads, sparse/zero-filled reads, simultaneous faults for the same page, page pruning during in-flight reads, child read errors, multi-page result ordering, and cache accounting after every destroy path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/page.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-threads/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/performance/io-threads/Makefile.am

## Purpose
Routes automake recursion for the io-threads translator into its `src` directory.

## Important APIs, types, and functions
`SUBDIRS = src` is the effective build rule. `CLEANFILES` is empty.

## Control flow
The parent performance build enters this directory, then recurses into `src` to build `io-threads.la`.

## State and persistence behavior
No runtime state exists; the file persists only build topology.

## Dependencies and integration points
Depends on `src/Makefile.am` and the parent `xlators/performance` automake setup.

## Risks and test signals
Risks are broken recursion or an unbuilt translator if the child directory is renamed. Build tests should confirm the io-threads module is produced and installed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-threads/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-threads/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/performance/io-threads/src/Makefile.am

## Purpose
Builds the `io-threads` performance translator as a loadable GlusterFS module.

## Important APIs, types, and functions
`xlator_LTLIBRARIES = io-threads.la` declares the plugin. `io_threads_la_SOURCES = io-threads.c` compiles the implementation. `noinst_HEADERS` tracks `io-threads.h`, `iot-mem-types.h`, and `io-threads-messages.h`. `io_threads_la_LIBADD` links `libglusterfs.la`.

## Control flow
Autotools compiles `io-threads.c`, links it with default xlator flags, and installs it under the performance xlator directory.

## State and persistence behavior
No runtime state is stored. The file fixes the module identity and include/link dependencies.

## Dependencies and integration points
Depends on libglusterfs, generated RPC/XDR include directories, and the xlator loader's expected module location.

## Risks and test signals
Risks include missing the `xlator_api` implementation at link/load time or mismatched install names. Test signals include successful build, installed `.so`, and runtime loading of `performance/io-threads`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-threads/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-threads/src/io-threads-messages.h -->
# sources/distributed-fs/glusterfs/xlators/performance/io-threads/src/io-threads-messages.h

## Purpose
Defines structured log message IDs and reusable strings for the io-threads translator.

## Important APIs, types, and functions
`GLFS_MSGID(IO_THREADS, ...)` assigns IDs for init failure, child misconfiguration, memory/accounting failures, pthread setup failures, and worker initialization failures. `_STR` macros provide common messages.

## Control flow
No logic is implemented. `io-threads.c` includes this header for `gf_smsg()` calls during init, memory accounting, and thread setup.

## State and persistence behavior
The message IDs form part of Gluster's stable logging interface and should be appended rather than reordered or removed.

## Dependencies and integration points
Depends on `glfs-message-id.h` and the global `IO_THREADS` component ID. It integrates with log analysis and support tooling.

## Risks and test signals
Risks are ID reuse, component mismatch, and stale messages after code changes. Compile tests and log-path assertions for init failure and worker setup failure cover the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-threads/src/io-threads-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-threads/src/io-threads.c -->
# sources/distributed-fs/glusterfs/xlators/performance/io-threads/src/io-threads.c

## Purpose
Implements the io-threads translator, which decouples most filesystem operations from the caller by wrapping them in call stubs and executing them on a dynamically scaled worker pool with per-priority and per-client queues.

## Important APIs, types, and functions
`IOT_FOP()` creates a FOP stub and schedules it. `iot_schedule()` classifies operations into high, normal, low, or least priority. `__iot_enqueue()` and `__iot_dequeue()` maintain per-priority fair queues grouped by client. `iot_worker()` waits on the condition variable, resumes stubs, handles idle exit, and honors shutdown. `__iot_workers_scale()` starts more worker threads based on queued work and configured limits. `iot_getxattr()` has a special `IO_THREADS_QUEUE_SIZE_KEY` path reporting queue depths. `notify()`, `iot_exit_threads()`, `fini()`, and client callbacks handle graph shutdown and disconnected-client cleanup.

## Control flow
Each FOP wrapper creates a `call_stub_t` that resumes the corresponding default child operation on a worker. Scheduling chooses priority by FOP type or forces least priority for ordinary client PIDs when enabled. Enqueue signals one worker and may scale the pool. Workers dequeue respecting active-thread limits per priority and round-robin among clients for fairness, then call `call_resume()` unless the stub is poisoned. Shutdown marks `down`, wakes workers, and waits for `curr_count` to reach zero.

## State and persistence behavior
Runtime state is `iot_conf_t` in `this->private`: mutex/cond, worker counts, queue depths, per-priority active limits, client queue contexts, watchdog settings, atomic queued stub count, and pass-through/cleanup flags. Client-specific queue arrays are stored in client context and freed on client destroy. No durable state is persisted.

## Dependencies and integration points
Depends on Gluster call stubs, default resume/failure callbacks, FOP priority enums, client contexts, atomic counters, pthreads, statedump, option parsing, logging/message IDs, and default event notification. Integrates with io-stats through `IO_THREADS_QUEUE_SIZE_KEY`, with graph teardown via parent/child down notifications, and with clients through disconnect poisoning.

## Risks and test signals
Risks include starvation if priority limits are misconfigured, queue-size/accounting mismatch on poisoned or failed stubs, deadlock during parent-down drain, use-after-free if client contexts are destroyed while queued requests still reference them, watchdog overreaction via `SIGTRAP`, and runtime reconfigure changing limits without waking/scaling enough workers. Tests should cover priority classification, per-client round-robin fairness, worker scale-up/idle scale-down, pass-through startup, queue-size xattr responses, parent/child down cleanup, disconnected-client poisoning, watchdog disabled/enabled behavior, and all FOP wrappers producing the correct default child calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-threads/src/io-threads.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-threads/src/io-threads.h -->
# sources/distributed-fs/glusterfs/xlators/performance/io-threads/src/io-threads.h

## Purpose
Declares io-threads configuration constants and runtime state structures used by `io-threads.c`.

## Important APIs, types, and functions
`IOT_MIN_THREADS`, `IOT_DEFAULT_THREADS`, `IOT_MAX_THREADS`, `IOT_DEFAULT_IDLE`, and `IOT_THREAD_STACK_SIZE` define defaults and bounds. `iot_client_ctx_t` stores one request list and client-list node per priority. `iot_fop_data_t` stores per-priority active limits/counts, client queues, no-client queue, queue sizes, and watchdog markers. `iot_conf_t` stores global worker-pool, queue, watchdog, option, and synchronization state.

## Control flow
The header has no executable flow, but `io-threads.c` relies on these structures for queue scheduling, worker scaling, statedump, reconfigure, and shutdown.

## State and persistence behavior
All declared state is process memory. It determines how queued operations survive while the graph is active and how they are drained on shutdown, but it has no persistent format.

## Dependencies and integration points
Includes Gluster dict/list/compat errno, iot memory types, pthread/semaphore-related platform headers, and priority constants from Gluster core.

## Risks and test signals
Risks include counters not protected by the mutex, queue-list node misuse because `iot_client_ctx_t` embeds both request and client links, and option defaults drifting from volume option definitions. Tests should inspect statedump values under load and validate queue cleanup across client lifecycle events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-threads/src/io-threads.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-threads/src/iot-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/performance/io-threads/src/iot-mem-types.h

## Purpose
Defines io-threads-specific memory accounting type IDs.

## Important APIs, types, and functions
`enum gf_iot_mem_types_` defines allocation classes for `iot_conf_t` and client queue context arrays, ending at `gf_iot_mt_end`.

## Control flow
No control flow exists. `mem_acct_init()` registers the enum range, and allocation sites use the IDs for diagnostics.

## State and persistence behavior
The enum affects runtime memory accounting only. It is not persisted.

## Dependencies and integration points
Depends on `glusterfs/mem-types.h` and integrates with xlator memory accounting.

## Risks and test signals
Risks are enum overlap, missing new allocation classes, and confusing memory leak attribution. Test signals include successful memory accounting init and statedump/leak reports showing io-threads allocations under the right categories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/io-threads/src/iot-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/md-cache/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/performance/md-cache/Makefile.am

## Purpose
Routes automake recursion for the md-cache translator into its `src` directory.

## Important APIs, types, and functions
`SUBDIRS = src` is the only functional build declaration.

## Control flow
The parent performance build enters this directory, then enters `src` to build and install `md-cache.la`.

## State and persistence behavior
No runtime state exists; this is build metadata.

## Dependencies and integration points
Depends on the child `src/Makefile.am` and parent performance automake recursion.

## Risks and test signals
Risks are failing to build/install md-cache if recursion is broken. Build and install tests should confirm `md-cache.so` is produced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/md-cache/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/md-cache/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/performance/md-cache/src/Makefile.am

## Purpose
Builds the `md-cache` translator and installs a compatibility symlink named `stat-prefetch.so`.

## Important APIs, types, and functions
`xlator_LTLIBRARIES = md-cache.la` declares the plugin. `md_cache_la_SOURCES = md-cache.c` builds the implementation. `noinst_HEADERS` includes memory and message headers. `stat-prefetch-compat` removes any old `stat-prefetch.so` and symlinks it to `./md-cache.so`; `install-exec-local` invokes that rule and `uninstall-local` removes the symlink.

## Control flow
The module is compiled and linked against `libglusterfs.la`, installed to the performance xlator directory, and the compatibility symlink is created during install.

## State and persistence behavior
No runtime state is managed, but install state includes the `stat-prefetch.so` symlink for older volfiles or tooling.

## Dependencies and integration points
Depends on libglusterfs, generated RPC/XDR include paths, contrib rbtree includes, and install-time filesystem operations. Integrates with Gluster's translator loader under both `md-cache` and legacy `stat-prefetch` names.

## Risks and test signals
Risks include a broken relative symlink, stale compatibility module on uninstall, missing headers from distribution, and loader failures under legacy names. Tests should cover clean install/uninstall, symlink target validity, module load as `performance/md-cache`, and legacy `performance/stat-prefetch` load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/md-cache/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/md-cache/src/md-cache-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/performance/md-cache/src/md-cache-mem-types.h

## Purpose
Defines md-cache-specific memory accounting categories.

## Important APIs, types, and functions
`enum gf_mdc_mem_types_` assigns allocation IDs for `mdc_local_t`, metadata cache objects, translator config, IPC/upcall helpers, and the enum end marker.

## Control flow
No executable control flow exists. The md-cache implementation uses these IDs through Gluster allocation macros after memory accounting init.

## State and persistence behavior
The IDs affect runtime diagnostics only and are not durable.

## Dependencies and integration points
Depends on `glusterfs/mem-types.h` and integrates with the xlator memory accounting subsystem used by md-cache.

## Risks and test signals
Risks include overlapping IDs, missing categories for new md-cache allocations, and misleading leak reports. Test signals are successful md-cache `mem_acct_init()` and memory statedump output under these categories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/md-cache/src/md-cache-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/md-cache/src/md-cache-messages.h -->
# sources/distributed-fs/glusterfs/xlators/performance/md-cache/src/md-cache-messages.h

## Purpose
Defines structured log message IDs for the md-cache translator.

## Important APIs, types, and functions
`GLFS_MSGID(MD_CACHE, ...)` declares IDs for no memory, discard update, cache update, IPC upcall failure, and missing xattr-cache support.

## Control flow
No logic is implemented. The md-cache C implementation includes this header for structured logging.

## State and persistence behavior
Message IDs are stable external log identifiers and should be appended rather than removed or reordered.

## Dependencies and integration points
Depends on `glfs-message-id.h` and the global `MD_CACHE` message component. Integrates with logging, upcall diagnostics, and support tooling.

## Risks and test signals
Risks are ID reuse, missing IDs for new warning/error paths, and component mismatch. Test signals include compile coverage and runtime log assertions for cache update, discard update, upcall failure, and no-xattr-cache paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/md-cache/src/md-cache-messages.h -->
