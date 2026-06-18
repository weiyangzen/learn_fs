# Research: subset-b-007063

Grouped research for GlusterFS `libglusterfs/src` files. Each section is source-tree aligned and intended to split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/fd.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/fd.c

## Purpose
`fd.c` implements GlusterFS' in-memory file-descriptor object lifecycle and the process/client fd table used to map integer fd slots to `fd_t *` instances. It is not a POSIX fd wrapper around kernel descriptors; it tracks Gluster translator state for open files/directories, binds fds to inodes, keeps refcounts, stores per-translator fd context, and provides statedump/dict dump helpers for diagnostics.

## Important APIs, Types, and Functions
- `gf_fd_fdtable_alloc()`, `gf_fd_fdtable_destroy()`: allocate and tear down `fdtable_t`, including its `pthread_rwlock_t`, free-slot list, and references held by table entries.
- `gf_fd_unused_get()`, `gf_fd_put()`, `gf_fdptr_put()`, `gf_fd_fdptr_get()`: allocate, release, find, and ref table entries. `GF_ANON_FD_NO` is ignored on put.
- `fd_create_uint64()`, `fd_create()`, `fd_anonymous_with_flags()`, `fd_anonymous()`: allocate `fd_t` objects from the inode table's fd mempool, initialize `_ctx`, lock context, inode reference semantics, flags, and list membership.
- `fd_ref()`, `__fd_ref()`, `fd_unref()`: atomic refcount operations around `fd_t`. `fd_unref()` removes the fd from the inode list and destroys it when the count reaches zero.
- `fd_bind()`, `__fd_bind()`, `fd_lookup()`, `fd_lookup_uint64()`, `fd_lookup_anonymous()`: manage inode `fd_list` membership and PID/anonymous lookup.
- `fd_close()`, `fd_destroy()`: invoke translator callback hooks (`fdclose`, `fdclosedir`, `release`, `releasedir`) and release inode/lock/context state.
- `fd_ctx_set()`, `fd_ctx_get()`, `fd_ctx_del()` and unlocked variants: attach one `uint64_t` value per xlator to an fd.
- `fd_dump()`, `fdtable_dump()`, `fd_ctx_dump()`, `fdtable_dump_to_dict()`: statedump and dictionary export.

## Control Flow
`gf_fd_fdtable_alloc()` creates a table, then under a write lock calls `gf_fd_fdtable_expand()` with `nr=0`. Expansion rounds to a power-of-two multiple sized by `fdentry_t`, allocates a new entry array, copies old entries if present, chains new entries through `next_free`, sets `first_free`, and frees the old array. `gf_fd_unused_get()` takes a write lock, pops `first_free`, marks the entry `GF_FDENTRY_ALLOCATED`, and stores the caller's `fd_t *`; if no free slot exists it expands and retries, with a defensive two-attempt cap.

`fd_create*()` allocates an `fd_t` using `fd_allocate()`, which initializes `_ctx` sized to the current graph's `xl_count + 1`, creates an fd-lock context, initializes the inode list and lock, and sets the atomic refcount to 1. The actual inode reference is taken by `fd_create_uint64()` after allocation because `fd_allocate()` may be called while holding `inode->lock`; taking `inode_ref()` there would invert lock ordering. Anonymous fds are allocated and bound while holding `inode->lock`, with `GF_ANON_FD_FLAGS` plus possible `O_DIRECT`.

`fd_unref()` decrements the atomic refcount while holding `inode->lock`; if it reaches zero and is still on the inode list, it unlinks the fd and decrements `active_fd_count`. Destruction is done after unlocking and calls translator release callbacks based on file type, restores `THIS`, destroys the fd lock, frees context, decrements `fd_count` if the fd had been bound, unrefs the inode and fd lock context, and returns the fd object to its mempool.

## State and Persistence
All state is process memory only. Persistent side effects are indirect through translator callbacks. `fdtable_t` state includes `fdentries`, `max_fds`, `first_free`, and a rwlock. `fd_t` state includes inode binding, PID, flags, anonymous flag, per-xl context array, fd-lock context, and atomic refcount. Table dump functions serialize current runtime state to statedump or dictionaries but do not persist it.

## Dependencies and Integration Points
The file depends on `glusterfs/fd.h`, inode/table definitions, mempool allocation (`mem_get0`, `mem_put`, `GF_CALLOC`, `GF_REALLOC`), atomics, list helpers, fd-lock context, statedump, logging, and translator graph callbacks. It is a core integration point between higher-level FOP open/create/opendir paths, inode lifecycle, client fd tables, and translators that store fd-private state.

## Risks and Edge Cases
- `gf_fd_fdtable_expand()` updates `first_free` to the start of the new range, so callers must hold the table write lock.
- `gf_fd_put()` checks `fd < fdtable->max_fds` before taking the lock, so concurrent table resize assumptions depend on ownership discipline.
- `gf_fd_put()` deliberately masks double-put/unallocated-put bugs by no-oping if the entry is not allocated.
- `fd_ctx_set()` can reallocate `_ctx`; callers using unlocked variants must already hold `fd->lock`.
- `fd_destroy()` changes thread-local `THIS` while invoking xlator callbacks and must restore it even across directory/file branches.
- Lock-order comments in `fd_allocate()` are important: moving `inode_ref()` inside allocation can deadlock.

## Test Signals
Useful tests cover fdtable growth and free-list reuse, invalid puts and anonymous fd behavior, refcount-to-destroy callback ordering, per-xl fd context set/get/delete including growth beyond initial graph count, statedump/dict output for open fds, and concurrent `gf_fd_fdptr_get()` plus `gf_fd_put()` behavior under the table locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/fd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/gen-defaults.py -->
# sources/distributed-fs/glusterfs/libglusterfs/src/gen-defaults.py

## Purpose
`gen-defaults.py` is a build-time code generator that expands `#pragma generate` markers in a template C file into default GlusterFS FOP forwarding and callback functions. It delegates operation metadata and string substitution to `generator.py`.

## Important APIs, Types, and Functions
- Imports `ops`, `fop_subs`, `cbk_subs`, and `generate` from `generator.py`.
- `FAILURE_CBK_TEMPLATE`, `CBK_RESUME_TEMPLATE`, `CBK_TEMPLATE`, `RESUME_TEMPLATE`, `FOP_TEMPLATE`: template strings for default failure unwind, callback resume, normal callback, resume wind, and direct tail-wind functions.
- `gen_defaults()`: iterates all operation names from `ops` and prints generated code for each template class.

## Control Flow
The script reads the path provided as `sys.argv[1]` line by line. If a line contains `#pragma generate`, it emits begin/end generated-code comments and all generated default functions. Otherwise it prints the original line without its trailing newline. The generation order is all failure callbacks, all callback resumes, all callbacks, all resumes, then all FOPs.

## State and Persistence
The script has no persistent state. Its output is stdout, normally redirected by the build to create or refresh a generated C source. Operation order follows Python dictionary insertion order in `generator.py`.

## Dependencies and Integration Points
It integrates with the libglusterfs build system, `defaults-tmpl.c` style inputs, `STACK_UNWIND_STRICT`, `STACK_WIND`, `STACK_WIND_TAIL`, and the operation metadata in `generator.py`. Generated defaults provide pass-through xlator behavior used across translator stacks.

## Risks and Edge Cases
- Missing or reordered metadata in `generator.py` changes generated ABI-facing functions.
- The marker search is substring-based, not syntax-aware.
- The script expects exactly one input argument and does not validate it.
- Generated text formatting is template-driven and not automatically reindented.

## Test Signals
Regenerate defaults from the canonical template and diff against committed/generated output. Add spot checks for representative FOPs with pointer and scalar callback args, especially `readv`/`writev` naming special cases inherited from `generator.py`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/gen-defaults.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/generator.py -->
# sources/distributed-fs/glusterfs/libglusterfs/src/generator.py

## Purpose
`generator.py` is the central Python metadata table for GlusterFS file operations, translator callbacks, and dump callbacks used by local code generators. It encodes operation argument lists, callback argument lists, journal classifications, syncop-specific extras, and inode-link hints.

## Important APIs, Types, and Functions
- `ops`: dictionary keyed by FOP name. Entries contain tagged tuples such as `fop-arg`, `cbk-arg`, `extra`, `journal`, and `link`.
- `xlator_cbks`: metadata for callbacks such as `forget`, `release`, `releasedir`, client lifecycle hooks, and `ictxmerge`.
- `xlator_dumpops`: metadata for dump callbacks such as `priv`, `inode`, `fd`, `inodectx`, and dictionary variants.
- `get_error_arg(type_str)`: maps pointer types to `NULL` and scalar types to `-1` for failure callback generation.
- `get_subs(names, types, cbktypes=None)`: builds substitution dictionaries for short arg lists, typed long arg declarations, error args, and optional callback error args.
- `generate(tmpl, name, subs)`: replaces `@NAME@`, `@UPNAME@`, and per-operation substitutions in a template.
- `fop_subs`, `cbk_subs`: generated substitution dictionaries populated at import time.

## Control Flow
Importing the module constructs `ops`, `xlator_cbks`, and `xlator_dumpops`, then iterates `ops.items()` to compute substitution maps. For each op, fop arguments and callback arguments are filtered by tag. `generate()` applies template replacement, with explicit uppercase exceptions for `writev` to `WRITE` and `readv` to `READ`.

## State and Persistence
There is no runtime persistence. The file's metadata is authoritative build-time state: generated defaults, stubs, syncops, journals, and reconciliation code can depend on the tuple contracts. Some entries include historical compatibility hacks, such as `nosync` fields, `extra` callback-derived values used by syncops, and special journal classifications.

## Dependencies and Integration Points
The file is consumed by `gen-defaults.py` and other generator scripts in libglusterfs. The metadata mirrors function typedefs in GlusterFS headers (`fop_*`, `fop_*_cbk`, `default_args_t`, `default_args_cbk_t`) and translator stack macros. Journal tags classify operations as `fd-op`, `inode-op`, or `entry-op`, which integrates with reconciliation and changelog logic.

## Risks and Edge Cases
- Metadata drift can break generated prototypes or callback unwinds across the codebase.
- Tuple shapes are loosely typed; a malformed tuple can fail late during generation.
- The `extra`, `nosync`, `journal`, and `link` conventions are domain-specific and easy to misuse.
- `copy_file_range` contains type strings with trailing spaces, so consumers must tolerate exact metadata.

## Test Signals
Generator tests should import the module, validate tuple schemas, regenerate known templates, and compile generated C. High-value coverage includes operations with extras (`writev`, `fsync`), create/link/mkdir link hints, journal classes, and the `readv`/`writev` uppercase exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/generator.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/gf-dirent.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/gf-dirent.c

## Purpose
`gf-dirent.c` provides helpers for GlusterFS directory entry objects and distributed directory offset transformations. It also links or fills inode/stat metadata for directory entries returned by `readdir`/`readdirp` style operations.

## Important APIs, Types, and Functions
- `gf_itransform()`, `gf_deitransform()`, `gf_dirent_orig_offset()`: encode/decode backend leaf identity into/from a presented directory offset.
- `gf_dirent_for_name2()`, `gf_dirent_for_name()`: allocate and initialize `gf_dirent_t` objects with name, stat, inode, dict, and list state.
- `gf_dirent_entry_free()`, `gf_dirent_free()`: release dict/inode references and free entries on a list.
- `entry_copy()`: deep-ish copy preserving inode/dict references.
- `gf_link_inode_from_dirent()`, `gf_link_inodes_from_dirent()`: link dirent inodes under a parent inode.
- `gf_fill_iatt_for_dirent()`: builds a `loc_t` and performs `syncop_lookup()` to populate `entry->d_stat` and `entry->inode`.

## Control Flow
Offset transform functions use the leaf count from `this->graph`. For single-leaf graphs they pass offsets through. For multi-leaf graphs, small offsets are encoded as `offset * leaf_count + client_id`; large offsets set a top bit and pack a shifted backend offset plus client id. Decode paths reverse this to locate the backend leaf or original backend offset.

Dirent allocation computes the variable-size struct length, initializes the list head, copies metadata, zeroes stats when absent, clears dict/inode, and copies the NUL-terminated name. Free paths unref optional dict/inode and unlink the list node. `gf_fill_iatt_for_dirent()` searches or creates an inode, copies GFID from the dirent stat, builds parent/name/path in a `loc_t`, calls `syncop_lookup()`, then updates the dirent on success and wipes the loc.

## State and Persistence
State is in-memory `gf_dirent_t` list nodes plus inode/dict references. Offset transforms encode state into `d_off` values visible across directory iteration. No data is persisted here, but inode linking mutates the inode table.

## Dependencies and Integration Points
Depends on xlator graph leaf counts, `inode_link`, `inode_lookup`, `inode_grep`, `inode_new`, `inode_path`, `loc_wipe`, uuid helpers, `dict_ref/unref`, and `syncop_lookup`. It is used by translators that aggregate directory entries across subvolumes and by readdirp flows that need inode/stat attachment.

## Risks and Edge Cases
- Offset encoding depends on fixed bit constants and leaf count; changing leaf-count behavior can break readdir continuation.
- `gf_dirent_free()` returns early for empty lists and assumes callers pass a list sentinel with initialized `list`.
- `gf_link_inodes_from_dirent()` notes a possible nlookup accounting policy violation.
- `gf_fill_iatt_for_dirent()` creates an inode when one is missing and must clean `loc_t` correctly on all paths.

## Test Signals
Test transform/de-transform round trips for one leaf, multiple leaves, huge offsets, zero, and `(uint64_t)-1`. Test dirent allocation/copy/free with dict/inode references and readdirp fill behavior with mocked successful and failed `syncop_lookup()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/gf-dirent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/gf-io-common.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/gf-io-common.c

## Purpose
`gf-io-common.c` implements shared synchronization and thread-pool infrastructure for the newer GlusterFS I/O framework. It provides monotonic timed barriers, thread creation/configuration, naming, signal masking, optional CPU affinity, priority setup, and pool teardown.

## Important APIs, Types, and Functions
- `gf_io_sync_start()`, `gf_io_sync_done()`, `gf_io_sync_wait()`: create and operate a multi-party sync/barrier object with timeout and retry handling.
- `gf_io_thread_pool_start()`, `gf_io_thread_pool_wait()`: create, initialize, join, and destroy thread pools.
- `gf_io_thread_name()`, `gf_io_thread_mask()`, `gf_io_thread_affinity()`: configure per-thread name, signal mask, and Linux CPU pinning.
- `gf_io_thread_attr_priority()`, `gf_io_thread_attr()`: build pthread attributes for stack size and optional scheduler priority.
- Internal `gf_io_thread_init()` and `gf_io_thread_main()`: run the three-phase startup handshake before invoking engine-specific setup/main callbacks.

## Control Flow
`gf_io_sync_start()` records a monotonic absolute timeout, initializes mutex and condition variable, and sets count/pending/phase. `gf_io_sync_done()` decrements pending and either signals completion or waits for all participants, then destroys the sync object for the waiter. `gf_io_sync_wait()` acts as a reusable phase barrier: the last participant resets pending to count, increments phase, and broadcasts; others wait for phase change.

Thread-pool start initializes the pool, creates a sync object with `num_threads + 1` participants, starts pthreads, then steps through creation, configuration, and engine-specific setup phases. Each worker stores a thread-local `gf_io_thread_t`, configures name/mask/affinity, calls the pool config setup function, and then runs the config main function. On startup failure, created threads are timed-joined and the pool is destroyed.

## State and Persistence
State is in-memory only: sync counters, phase, result, timeout, thread list, pthread ids, pool mutex, and thread-local `gf_io_thread`. Thread names and scheduler attributes are process-visible runtime state.

## Dependencies and Integration Points
Uses pthreads, `CLOCK_MONOTONIC` condition variables, `CLOCK_REALTIME` timed joins on Linux, `urcu/uatomic.h`, Gluster logging/check helpers, list utilities, and the `gf_io_thread_pool_config_t` callback contract from `gf-io-common.h`. It is called by `gf-io.c` to start worker threads for an active engine.

## Risks and Edge Cases
- Timeout retry exhaustion calls `GF_ABORT()` when retries are zero.
- Variable-length `pthread_t ids[cfg->num_threads]` requires a sane nonzero thread count.
- Priority setup may fail without privileges; callers need to surface errors cleanly.
- Affinity indexing fails if fewer CPUs are set than requested threads.
- Startup has several phases; wrong pending counts can deadlock.

## Test Signals
Tests should cover sync success, timeout/retry accounting, error propagation through barriers, startup failure cleanup, pool wait teardown, thread naming limits, disabled/null CPU affinity, and signal mask behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/gf-io-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/gf-io-legacy.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/gf-io-legacy.c

## Purpose
`gf-io-legacy.c` provides the legacy implementation of the `gf_io_engine_t` interface. It bridges the newer I/O framework to existing GlusterFS event and timer infrastructure when `io_uring` is unavailable or not selected.

## Important APIs, Types, and Functions
- `gf_io_engine_legacy`: exported engine descriptor with name `legacy` and mode `GF_IO_MODE_LEGACY`.
- `gf_io_legacy_setup()`, `gf_io_legacy_cleanup()`: initialize/reset legacy sequence state and no-op cleanup.
- `gf_io_legacy_wait()`: delegates to `gf_event_dispatch(global_ctx->event_pool)`.
- `gf_io_legacy_cancel()`: cancels timer-backed operations or reports missing/already completed timers.
- `gf_io_legacy_callback()`: immediately completes a callback operation.

## Control Flow
Setup resets a static sequence counter. Wait dispatches the global event loop. Legacy callbacks increment `gf_io_legacy_seq` atomically and call `gf_io_cbk(NULL, seq, id, res)`. Cancel interprets `op->cancel.id` as a `gf_timer_t *`; absent timers complete cancel with `-ENOENT`, failed timer cancellation completes cancel with `-EALREADY`, and successful cancellation completes the original operation with `-ECANCELED` and the cancel request with `0`.

## State and Persistence
The only local state is static `gf_io_legacy_seq`, used to provide callback sequence values. Event and timer state lives in `global_ctx`.

## Dependencies and Integration Points
Depends on `gf-io-legacy.h`, global context, `gf-event.h`, and `timer.h`. It integrates new `gf_io` callback/cancel abstractions with the older event loop.

## Risks and Edge Cases
- Cancellation assumes timer IDs are stored as pointer-sized integers.
- `worker_*` hooks are NULL because this engine has no worker threads; callers must handle legacy mode correctly.
- Global event dispatch remains the blocking wait path until event code migrates to the I/O framework.

## Test Signals
Exercise callback immediate completion, timer cancel success and failure, null timer IDs, sequence monotonicity under concurrent callbacks, and full `gf_io_run("legacy", ...)` behavior with setup/cleanup handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/gf-io-legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/gf-io-uring.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/gf-io-uring.c

## Purpose
`gf-io-uring.c` implements the Linux `io_uring` backend for GlusterFS' I/O framework. It uses direct `io_uring_setup`, `io_uring_enter`, and `io_uring_register` syscalls, maps submission/completion rings, dispatches callbacks through CQEs, and supports asynchronous cancellation and callback NOP requests.

## Important APIs, Types, and Functions
- `gf_io_engine_io_uring`: exported `gf_io_engine_t` named `io_uring`.
- `gf_io_uring_setup()`, `gf_io_uring_cleanup()`: create, validate, map, probe, and destroy the ring.
- `gf_io_uring_sq_init()`, `gf_io_uring_cq_init()`, corresponding fini functions: manage ring memory mappings.
- `gf_io_uring_enter()`, `gf_io_uring_dispatch()`, `gf_io_uring_dispatch_no_process()`: submit SQEs and optionally wait/process completions.
- `gf_io_uring_cq_process()`, `gf_io_uring_cq_process_some()`: consume CQEs with atomic head updates and invoke `gf_io_cbk()`.
- `gf_io_uring_sq_commit()`, `gf_io_uring_sq_flush()`: use SQE padding to mark committed batches and advance the SQ tail.
- `gf_io_uring_cancel()`, `gf_io_uring_callback()`: build cancellation and NOP SQEs.

## Control Flow
Setup calls `io_uring_setup()` with `IORING_SETUP_CLAMP`, logs parameters, verifies required features `IORING_FEAT_NODROP` and `IORING_FEAT_SUBMIT_STABLE`, ensures at least `GF_IO_URING_QUEUE_MIN` SQ entries, maps SQ/CQ structures, runs `IORING_REGISTER_PROBE`, preinitializes the SQ array, clears SQEs, and returns `GF_IO_URING_WORKER_THREADS`.

Submit-side logic obtains an SQE for a sequence slot, waiting/flushing if the ring is full. `gf_io_uring_common()` writes `user_data`, clears padding, and commits the batch when the id is not chained. Flush consumes committed batch lengths from SQE padding, updates SQ tail with memory barriers, calls `io_uring_enter()`, and processes CQEs when the kernel accepted fewer requests than submitted. Worker loops process one CQE if available, then dispatch with wait enabled if no completion was immediately available.

## State and Persistence
All state is runtime-only: static `gf_io_uring` stores mapped SQ/CQ pointers, masks, entry counts, params, and ring fd. SQE padding is repurposed as intra-process pending batch metadata, so compatibility with kernel struct layout is crucial.

## Dependencies and Integration Points
Depends on Linux syscall numbers, `<linux/io_uring.h>` through `compat-io_uring.h`, URCU atomics/memory barriers, poll, Gluster event dispatch for non-I/O-framework events, and the common `gf_io` request/callback pool. It is selected by `gf-io.c` when compiled with `HAVE_IO_URING` and when setup succeeds.

## Risks and Edge Cases
- Unsupported kernels or missing features cause setup failure and fallback to legacy at the caller.
- Unexpected `io_uring_enter()` errors other than `EAGAIN`, `EBUSY`, or `ENOMEM` abort the process because request stream recovery is considered unsafe.
- The implementation relies on `__pad2` in `struct io_uring_sqe` for private batch counts.
- CQ head is advanced by compare/exchange across workers; memory-ordering mistakes can drop or duplicate completions.
- `IORING_SETUP_SQPOLL` is noted as currently impractical without fd registration.

## Test Signals
Test setup fallback on unsupported kernels, feature validation, SQ/CQ mmap failure cleanup, SQ commit/flush batching, chained request behavior, CQ processing under multiple workers, cancel for timer vs normal ids, and stress tests for partial submission and full-ring backpressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/gf-io-uring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/gf-io.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/gf-io.c

## Purpose
`gf-io.c` is the top-level runtime for the GlusterFS I/O framework. It chooses an engine (`io_uring` when built and usable, otherwise legacy), owns global operation maps/pools, batches requests, runs setup/wait/cleanup handlers, starts worker threads, and dispatches callbacks.

## Important APIs, Types, and Functions
- Global `gf_io_t gf_io` and thread-local `gf_io_worker_t gf_io_worker`.
- `gf_io_run(name, handlers, data)`: main entry point that selects an engine and runs the framework.
- `gf_io_batch_submit()`: reserves ids, fills `gf_io_op_t` slots, submits batched/chained requests, and returns ids to callers.
- `gf_io_data_wait()`: waits for a request data slot to become unchained/available, servicing worker or flush paths meanwhile.
- `gf_io_async_handler`: executes async functions and then callbacks.
- `gf_io_worker_setup()`, `gf_io_worker_main()`, `gf_io_workers_stop()`: worker lifecycle glue around engine hooks.
- `gf_io_sync()`, `gf_io_sync_wake()`: run an async function and wait synchronously for completion.

## Control Flow
`gf_io_run()` clears global state, allocates `op_map` and `op_pool` using mmap-backed locked memory, then tries engines in order. For a matching/available engine, it calls engine setup, initializes `gf_io`, runs `gf_io_main()`, invokes engine cleanup, and returns on success; otherwise it tries the next engine and eventually returns `-ENXIO`.

`gf_io_main()` optionally starts a worker pool, runs handler setup via `gf_io_sync()`, waits in `engine.wait()`, runs handler cleanup, then stops workers and joins the pool. Worker main loops call `engine.worker()` while enabled; on shutdown they call cleanup and participate in stopping other workers. In debug builds, callback and async function latency is measured and logged when above threshold.

## State and Persistence
State is in-process global memory: engine descriptor, operation id map, operation pool, worker count, shutdown flag, and per-thread worker structs. `gf_io_alloc()` uses `mmap`, `mlock`, and `MADV_DONTFORK` where available to keep critical request state resident and out of forked children.

## Dependencies and Integration Points
Integrates `gf-io-legacy`, optional `gf-io-uring`, `gf-io-common` thread pools/sync, global logging, request id helpers/macros, and external handler callbacks. It is intended to host future async I/O and timer/callback functionality while still dispatching legacy events.

## Risks and Edge Cases
- Engine order and requested `name` determine fallback behavior.
- Worker stop posts callbacks through the same engine; broken callback dispatch can block shutdown.
- `gf_io_batch_submit()` copies request operations into pooled slots and uses chain flags; submitters must preserve lifetime until copied.
- Debug latency checks assume callbacks are quick; slow callbacks can indicate deadlocks or blocking work in the callback path.
- Locked mmap may fail under memory limits, preventing framework startup.

## Test Signals
Test engine selection by name and fallback, operation pool allocation failure cleanup, batched request id assignment including chains, `gf_io_data_wait()` with worker and non-worker callers, setup/wait/cleanup handler ordering, worker shutdown propagation, and debug latency instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/gf-io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/gidcache.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/gidcache.c

## Purpose
`gidcache.c` implements a small set-associative timeout cache for auxiliary group lists. It avoids repeated group-list lookups for the same id/uid/gid tuple while preserving correctness when credentials change.

## Important APIs, Types, and Functions
- `gid_cache_init(cache, timeout)`: initializes lock, max age, bucket count, and clears entries.
- `gid_cache_reconf(cache, timeout)`: changes the cache timeout under lock.
- `gid_cache_lookup(cache, id, uid, gid)`: finds a live entry and returns it while keeping the cache locked.
- `gid_cache_release(cache, agl)`: unlocks after a successful lookup.
- `gid_cache_add(cache, gl)`: inserts or updates an entry, reusing expired/matching entries and maintaining LRU order within a bucket.

## Control Flow
Lookup hashes `id` to a bucket, scans up to `AUX_GID_CACHE_ASSOC` entries in LRU order, skips empty entries, requires matching id plus matching uid/gid, and returns only if `gf_time()` is before `gl_deadline`. It intentionally leaves the lock held so the caller can copy the returned `gid_list_t` without an extra allocation or race, then calls `gid_cache_release()`.

Add ignores null lists and disabled timeout (`gc_max_age == 0`). It scans for an entry with the same id or the first free slot, frees any reused list, evicts the oldest slot when the bucket is full, slides later populated entries down, and stores the new entry at the newest populated position with a refreshed deadline.

## State and Persistence
The cache is entirely in memory. Entries own `gl_list` pointers transferred from the caller into the cache. Reconfiguration changes only future lookup/add behavior; entries may remain but become unusable when timeout is zero.

## Dependencies and Integration Points
Depends on `gidcache.h`, `mem-pool.h`, `common-utils.h`, Gluster locks, `GF_FREE`, and `gf_time()`. It integrates with authentication/request contexts that need supplemental groups for a process or client identity.

## Risks and Edge Cases
- Successful lookup returns with the cache lock held; caller must release promptly or block all cache operations.
- Lookup breaks on credential mismatch or expiration and does not reclaim; add performs reuse/eviction.
- `gid_cache_add()` takes ownership of `gl->gl_list`; callers must not free it after successful add.
- Timeout reconfiguration to zero disables new inserts but does not immediately free old entries.

## Test Signals
Test bucket hashing, LRU slide/eviction, update of expired same-id entries, uid/gid mismatch invalidation, timeout zero behavior, lookup lock/release discipline, and memory ownership of `gl_list`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/gidcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/globals.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/globals.c

## Purpose
`globals.c` initializes and exposes process/thread global libglusterfs state: FOP/upcall name arrays, the fallback global xlator used for `THIS`, memory accounting toggles, thread-local syncop/synctask/uuid/lkowner/lease buffers, and cleanup hooks for thread-local allocations.

## Important APIs, Types, and Functions
- `gf_fop_list[]`, `gf_upcall_list[]`: string lookup tables for FOP and upcall enum values.
- `gf_global_mem_acct_enable_get/set()`: global memory accounting flag accessors.
- `glusterfs_this_init()`, `__glusterfs_this_location()`: initialize and return thread-local `THIS` storage, defaulting to `global_xlator`.
- `global_xl_init()`, `global_xl_reconfigure()`, `global_xl_fini()`, `global_xl_options[]`: global xlator option handling for latency and metrics path.
- `syncopctx_getctx()`, `synctask_get/set()`: thread-local sync operation state.
- `glusterfs_uuid_buf_get()`, `glusterfs_lkowner_buf_get()`, `glusterfs_leaseid_buf_get()`, `glusterfs_leaseid_exist()`: thread-local reusable formatting buffers.
- `gf_thread_needs_cleanup()`, `glusterfs_globals_init()`: register TLS destructor and one-time global initialization.

## Control Flow
`glusterfs_globals_init(ctx)` initializes logging globals then calls `pthread_once()` for `gf_globals_init_once()`. That function initializes the fallback xlator and creates a pthread key whose destructor frees `thread_syncopctx.groups` and calls `mem_pool_thread_destructor()`. `gf_thread_needs_cleanup()` stores a non-null value in the key so pthreads will invoke the destructor at thread exit.

The global xlator installs empty fops/cbks plus init/reconfigure/fini hooks. Init and reconfigure read `measure-latency` and `metrics-dump-path` options into the process context. `__glusterfs_this_location()` returns the address of the thread-local xlator pointer, initializing it to `global_xlator` if absent.

## State and Persistence
State is process global and thread-local memory only. The global xlator and option list remain for process lifetime. TLS buffers persist per thread until thread exit. The memory accounting flag is a plain static int, not persisted.

## Dependencies and Integration Points
Depends on pthread once/key/TLS, syncop types, translator option macros, logging, list helpers, mempool TLS cleanup, and libglusterfs message IDs. Almost every translator path indirectly depends on `THIS` and the FOP string tables.

## Risks and Edge Cases
- `gf_global_mem_acct_enable_set()` is unsynchronized; callers must avoid racing semantics.
- Failure to create the pthread cleanup key is fatal and exits the process.
- TLS destructors require `gf_thread_needs_cleanup()` to have been called after a thread allocates relevant resources.
- `global_xl_reconfigure()` logs option dictionaries, which can expose configuration values in logs.

## Test Signals
Test `pthread_once()` idempotence, default `THIS` behavior on fresh threads, option init/reconfigure effects on context, TLS buffer reuse per thread, cleanup destructor freeing syncop groups, and FOP/upcall string table bounds through `gf_fop_string()` consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/globals.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/async.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/async.h

## Purpose
`async.h` declares the GlusterFS asynchronous worker framework built on URCU wait-free queues/stacks and process signals. It exposes initialization, shutdown, thread-count adjustment, and an inline `gf_async()` enqueue-or-run helper.

## Important APIs, Types, and Functions
- `gf_async_t`: queued work item containing a callback and `cds_wfcq_node`.
- `gf_async_worker_t`: worker control record with async self-job, available stack node, pthread id, numeric id, and running flag.
- `gf_async_queue_t`: cache-line-aligned URCU wait-free queue head/tail.
- `gf_async_control_t`: global controller with queue, available worker stack, worker table, pthread barrier, signal masks/handlers, pid, max thread count, packed running/stopping counts, and enabled flag.
- `gf_async_init()`, `gf_async_fini()`, `gf_async_adjust_threads()`: lifecycle declarations.
- `gf_async(async, cbk)`: inline submit helper.

## Control Flow
When `gf_async_ctrl.enabled` is false, `gf_async()` invokes the callback synchronously. When enabled, it sets `async->cbk`, initializes the queue node, enqueues it into the global wait-free queue, and if the queue was previously empty sends `GF_ASYNC_SIGQUEUE` to the process to wake the leader worker.

## State and Persistence
State is runtime-only and process-wide in `gf_async_ctrl`. Worker counts are packed into a 32-bit field with high 16 bits for running and low 16 bits for stopping. Signal handlers/masks are saved in the controller for restoration.

## Dependencies and Integration Points
Depends on URCU `wfcqueue`/`wfstack`, pthreads, signals, common-utils logging/abort helpers, and Gluster context initialization. It integrates with code that wants asynchronous callback execution without each caller owning a thread pool.

## Risks and Edge Cases
- It uses `SIGALRM` and `SIGVTALRM`; conflicts with other process users of those signals can break scheduling.
- Enqueued `gf_async_t` storage must outlive asynchronous execution.
- `kill()` failure in the wake path is fatal via `gf_async_fatal()`.
- Counts are limited to 16-bit subfields, though public max is 128 threads.

## Test Signals
Test disabled synchronous execution, enabled enqueue wake behavior, signal-handler installation/restoration in implementation, worker count adjustment boundaries, queue-empty wake decisions, and object lifetime discipline for stack-allocated async items.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/async.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/atomic.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/atomic.h

## Purpose
`atomic.h` defines GlusterFS portable atomic integer wrappers. It supports compiler `__atomic` builtins, older `__sync` builtins, and a lock-based fallback for unsupported type sizes, especially 64-bit atomics on 32-bit platforms.

## Important APIs, Types, and Functions
- `gf_atomic_int8_t`, `gf_atomic_int16_t`, `gf_atomic_int32_t`, `gf_atomic_int64_t`, pointer-sized signed variants, unsigned variants, and `gf_atomic_t` aliasing int64.
- `GF_ATOMIC_INIT`, `GET`, `ADD`, `SUB`, `AND`, `OR`, `XOR`, `NAND`, `FETCH_*`, `SWAP`, `CMP_SWAP`, `INC`, `DEC`.
- `GF_ATOMIC_CHOOSE()`: selects builtin vs lock implementation based on `sizeof(_atomic) > sizeof(uint64_t)`.
- Lock fallback macros: initialize and operate under `gf_lock_t`.
- Builtin implementations: `__atomic_*` with acquire/release or `__sync_*`.

## Control Flow
Compile-time feature and word-size macros decide whether each type embeds a zero-size dummy lock field or a real `gf_lock_t`. At each operation, `GF_ATOMIC_CHOOSE()` compares structure size and dispatches to the lock or builtin macro. Builtin `__atomic` operations use acquire/release memory order; `__sync` operations rely on full barriers.

## State and Persistence
Atomic state is embedded in caller-owned structures. Lock fallback atomics also embed a mutex-like `gf_lock_t` that must be initialized by `GF_ATOMIC_INIT`.

## Dependencies and Integration Points
Depends on `locking.h`, integer types, bool, and configure-time macros (`HAVE_ATOMIC_BUILTINS`, `HAVE_SYNC_BUILTINS`, `SIZEOF_LONG`). It is used broadly for fd refs, client refs/counts, I/O counters, and other shared state.

## Risks and Edge Cases
- All atomic variables must be initialized before use, especially lock fallback variants.
- The lock/builtin selection assumes mutex-bearing structures are larger than `uint64_t`.
- Direct access to `.value` bypasses synchronization.
- `NAND` semantics differ historically across builtin families; callers should avoid relying on nuanced old-value behavior without tests.

## Test Signals
Build on 32-bit and 64-bit configurations, with and without atomic builtins where possible. Test every operation against expected returned values, compare-swap success/failure, concurrent increments, and struct sizes that drive lock fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/call-stub.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/call-stub.h

## Purpose
`call-stub.h` declares the deferred-call representation used to capture GlusterFS FOP calls and callbacks for later resume or unwind. It centralizes prototypes for creating stubs across the full FOP surface.

## Important APIs, Types, and Functions
- `call_stub_t`: contains list linkage, `call_frame_t *`, unions of FOP function pointers and callback pointers, FOP id, poison/wind state, and captured `default_args_t`/`default_args_cbk_t`.
- `fop_*_stub()` declarations: capture forward FOP invocations such as lookup, open, readv, writev, locks, xattrs, create, put, and copy_file_range.
- `fop_*_cbk_stub()` declarations: capture callbacks with op_ret/op_errno and returned data.
- `call_resume()`, `call_resume_keep_stub()`: resume captured work.
- `call_stub_destroy()`: release captured references.
- `call_unwind_error()`, `call_unwind_error_keep_stub()`: unwind captured calls with errors.

## Control Flow
The header itself declares contracts; implementation code allocates `call_stub_t`, stores the selected function pointer in the correct union member, captures arguments into `default_args_t` or callback args, then later resumes or unwinds based on `fop`/`wind`. Callers can keep or destroy the stub depending on the resume/unwind variant.

## State and Persistence
Stub state is in-memory, listable, and frame-associated. It captures references to GlusterFS objects and must follow ownership rules enforced by implementation. There is no persistence.

## Dependencies and Integration Points
Depends on `defaults.h`, `default-args.h`, `list.h`, FOP typedefs, `call_frame_t`, `loc_t`, `fd_t`, `dict_t`, `inode_t`, lock types, and iovec/iobref structures. Translators use it for delayed operations, serialization, throttling, barriers, and error unwinds.

## Risks and Edge Cases
- Prototype drift from generator metadata or FOP typedefs can break compilation or ABI assumptions.
- Captured pointer lifetimes are subtle; implementation must ref/unref all objects consistently.
- Some declarations intentionally map closely related callback types, which makes copy/paste type mistakes likely.
- `poison` and `wind` fields indicate lifecycle state and misuse can lead to double resume or double free.

## Test Signals
Compile-time coverage is critical across all FOP stubs. Runtime tests should capture/resume/destroy representative entry, inode, fd, xattr, lock, read/write, and callback stubs, including error unwind and keep-stub variants with refcount leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/call-stub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/checksum.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/checksum.h

## Purpose
`checksum.h` declares rsync-style checksum helpers used by GlusterFS code that compares or synchronizes byte ranges.

## Important APIs, Types, and Functions
- `gf_rsync_weak_checksum(unsigned char *buf, size_t len)`: returns a 32-bit weak rolling checksum.
- `gf_rsync_strong_checksum(unsigned char *buf, size_t len, unsigned char *sum)`: writes a strong checksum.
- `gf_rsync_md5_checksum(unsigned char *data, size_t len, unsigned char *md5)`: writes an MD5 digest.

## Control Flow
This header only declares functions. Implementations in checksum source files compute weak and strong hashes over caller-provided buffers and write digest bytes to caller-provided output storage.

## State and Persistence
No state is declared. All state is local to the implementation and caller-provided buffers.

## Dependencies and Integration Points
Integrates with FOPs such as `rchecksum`, replication/heal checks, and any translator needing rsync-compatible block comparison.

## Risks and Edge Cases
- Callers must supply output buffers of the expected digest size.
- MD5 and rsync weak checksums are not security primitives; they are integrity/synchronization helpers.
- Header lacks explicit size constants for strong and MD5 outputs, so caller/implementation agreement matters.

## Test Signals
Compare weak, strong, and MD5 outputs against known vectors, including empty input, single byte, large buffers, and repeated patterns. Test callers for correct output buffer sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/circ-buff.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/circ-buff.h

## Purpose
`circ-buff.h` declares a mutex-protected circular buffer abstraction that stores timestamped opaque pointers, usually for bounded history/debug/event tracking.

## Important APIs, Types, and Functions
- `circular_buffer_t`: one entry with `struct timeval tv` and `void *data`.
- `buffer_t`: ring metadata (`w_index`, `used_len`, `size_buffer`), entry pointer array, data destructor, mutex, and `use_once` policy.
- `cb_buffer_new()`, `cb_buffer_destroy()`: allocate and free a buffer.
- `cb_add_entry_buffer()`: append an item, overwriting or stopping based on policy.
- `cb_buffer_show()`, `cb_buffer_dump()`: display/dump stored entries via a callback.

## Control Flow
The header defines the object model. Implementations allocate an array of entry pointers, write entries at `w_index`, track used length up to capacity, and use `destroy_buffer_data` when replacing or destroying item data.

## State and Persistence
All state is in memory and protected by `buffer->lock`. Stored payload ownership is defined by the destroy callback. No persistence exists beyond optional dump output.

## Dependencies and Integration Points
Depends on `common-utils.h` for Gluster types and pthread support. It is used by subsystems needing a fixed-size rolling event history.

## Risks and Edge Cases
- `BUFFER_SIZE`/`TOTAL_SIZE` are small defaults but `cb_buffer_new()` accepts a size, so implementation must avoid assumptions.
- Payload lifetime depends on the destroy callback being correct.
- Dump/show callbacks must not mutate buffer state without respecting locks.

## Test Signals
Test allocation/destruction, wraparound, use-once behavior, timestamp population, destructor invocation on overwrite/destroy, and concurrent add/dump locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/circ-buff.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/client_t.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/client_t.h

## Purpose
`client_t.h` declares the core GlusterFS client identity object, authentication data shared with RPC, client table entries, client context storage, and diagnostics/disconnect APIs.

## Important APIs, Types, and Functions
- `client_auth_data_t`: RPC-compatible auth flavour, length, and fixed 400-byte data payload.
- `struct client_ctx`: key/value scratch context entries.
- `client_t`: atomic bind/count refs, bound/current xlators, table index, opversion, auth info, subdir mount state, fd counter, scratch context lock/table, and flexible `client_uid`.
- `clienttable_t` and `cliententry_t`: free-list table for `client_t *` entries.
- `gf_client_get()`, `gf_client_ref()`, `gf_client_unref()`, `gf_client_put()`: lifecycle and table ownership.
- `client_ctx_set/get/del/dump()`: per-client scratch context helpers.
- fdtable/inode dump helpers and `gf_client_disconnect()`.

## Control Flow
The header defines table constants and APIs; implementation uses a free-list table similar to fd tables, atomic reference counters for client lifetime, and scratch context slots guarded by `scratch_ctx_lock`. Client get locates or creates a client using xlator/auth/uid/subdir identity.

## State and Persistence
Client state is in memory. It tracks identity, auth, subdir root inode/GFID, open fd count for detach behavior, and per-client scratch contexts. Diagnostics export state to dicts or statedump output.

## Dependencies and Integration Points
Depends on Gluster locks, atomics, xlator/inode/dict types, and RPC authentication conventions. It is central to server-side connection management, translator client callbacks, detach/disconnect flows, and per-client fd/inode accounting.

## Risks and Edge Cases
- Flexible array `client_uid[]` requires allocation sized for the UID string.
- Auth data exists in both fixed and dynamic forms; comparisons must avoid length/termination mistakes.
- Scratch context table starts fixed-size; implementation must handle collisions or expansion carefully.
- Disconnect must coordinate refs, bind state, fd counts, and translator callbacks.

## Test Signals
Test client lookup/create identity matching, ref/unref teardown, table expansion/free-list behavior, auth comparison with binary data, subdir mount fields, scratch context set/get/delete, disconnect callback behavior, and fd/inode dump outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/client_t.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/cluster-syncop.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/cluster-syncop.h

## Purpose
`cluster-syncop.h` declares synchronous helper operations for issuing FOPs across a list of cluster subvolumes and collecting per-subvolume replies. It supports lookup, metadata ops, xattrs, locks, entry ops, fd ops, and success-mask helpers.

## Important APIs, Types, and Functions
- `PARALLEL_FOP_ONLIST(...)`: macro that runs a helper function on selected subvolumes, waits on a `syncbarrier_t`, and restores frame state.
- `cluster_local_t`: frame-local wrapper containing reply array and barrier.
- `cluster_*` functions: synchronous multi-subvolume variants for lookup, setattr, get/setxattr, locks, rmdir/unlink/mkdir/readlink/symlink/link/mknod, xattrop, fstat/ftruncate/open/fsetattr/put, and tiebreaker locks.
- `cluster_replies_wipe()`, `cluster_fop_success_fill()`: reply cleanup and success-mask utilities.
- `cluster_xattrop_cbk()`: common callback for xattrop aggregation.

## Control Flow
`PARALLEL_FOP_ONLIST` initializes a stack `cluster_local_t`, wipes reply slots, initializes each reply dirent list, sets up a sync barrier, replaces `frame->local`, counts selected subvolumes from the `on` bitmap, calls the helper for each selected subvolume, waits for callbacks, destroys the barrier, restores the old frame local, and resets the stack root.

## State and Persistence
State is temporary per operation: reply arrays, output/success bitmaps, lock-acquired bitmaps, frame-local barrier state, and callback-filled `default_args_cbk_t` entries. There is no persistence here.

## Dependencies and Integration Points
Depends on `defaults.h`, `default-args.h`, `syncop.h`, `call_frame_t`, `xlator_t`, `loc_t`, `fd_t`, `dict_t`, inode and lock types. Cluster translators use this API to send the same operation to many children and make decisions from collected replies.

## Risks and Edge Cases
- The macro uses a stack local as `frame->local`; callbacks must complete before the macro returns.
- `waitfor` is the selected subvolume count; zero-count behavior depends on syncbarrier implementation.
- Reply entries require initialized list heads before callbacks append dirents.
- Frame local/root state restoration is critical for nested or repeated cluster operations.

## Test Signals
Test selected-subvolume bitmaps, zero and partial selections, callback aggregation, reply wipe/list initialization, lock/unlock rollback masks, success-mask filling, and operations where one subvolume fails or times out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/cluster-syncop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/common-utils.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/common-utils.h

## Purpose
`common-utils.h` is a broad foundational header for libglusterfs. It defines constants, validation/logging/assertion macros, bit helpers, iovec utilities, time formatting/diff helpers, path/network/string parsing prototypes, thread helpers, hashing, fd closing helpers, and many cross-subsystem utility declarations.

## Important APIs, Types, and Functions
- Constants: size units, process modes, port ranges, time units, hidden paths, thread name limits, lease buffer sizes, shard GFIDs, special client PIDs, IPC targets.
- Macros: `alloca0`, `min`, `max`, `gf_roof`, `gf_floor`, `VALIDATE_OR_GOTO`, `GF_VALIDATE_OR_GOTO`, xattr guards, `GF_ASSERT`, `GF_STATIC_ASSERT`, `GF_ABORT`, `GF_UUID_ASSERT`.
- Inline helpers: bit-array set/clear/value, iovec duplicate/free/length/subset/skip/copy/load/unload, zero-filled checks, time formatting, thread-name wrapper, `gf_time`, `gf_tvdiff`, `gf_tsdiff`.
- Types: `dht_changelog_rename_info_t`, DNS cache structs, `list_node`, `iov_iter_t`, `token_iter_t`, socket union.
- Prototypes: string-to-number/bytesize/bool/time parsers, IP/hostname validation, UUID/lkowner/lease formatting, path utilities, reserved port parsing, local address checks, xxhash/GFID generation, thread creation/name helpers, service-running checks, recursive rmdir/unlink, robust read/write, SHA256, xattr namespace validation, FOP string/int mapping, pipe/nanosleep helpers.

## Control Flow
Inline iovec helpers implement small iterator-style control flow over scatter/gather buffers. `iov_iter_init()` positions at an offset; `iov_iter_next()` advances through current and subsequent iovecs; `iov_range_copy()` copies between two iterator ranges; `iov_subset()` materializes a subrange into caller-provided or newly allocated iovecs. Time formatters lazily initialize static format arrays, choose local or UTC time from logging settings, and append timezone and microseconds where present.

## State and Persistence
Most items are macros/prototypes with no state. Inline time formatting uses static local pointers initialized once without explicit locking but only to constant arrays. Functions declared here may mutate filesystem paths, process resource limits, DNS caches, or files depending on implementation, but this header itself persists nothing.

## Dependencies and Integration Points
This header is included across libglusterfs and translators. It depends on pthreads, sockets, iovec, uuid, URCU compiler macros, mempool, compat uuid, iatt, logging messages, and many forward-declared Gluster types. It is a high-risk integration surface because API or macro changes affect many translation units.

## Risks and Edge Cases
- Macros can evaluate arguments more than once (`min`, `max`, path removal), so callers must avoid side-effect expressions.
- Validation macros rely on a visible `this` symbol in some contexts.
- `mem_0filled()` returns nonzero when data is not all zero, which is easy to misread from its name.
- Several inline helpers perform pointer arithmetic on `void *`, relying on compiler extensions.
- Header-wide changes can cause large rebuild and behavior changes.

## Test Signals
Tests should cover iovec iterator boundary conditions, zero-filled detection, time formatting in local/UTC modes, validation macro errno behavior through representative users, string/bytesize parsers in implementation, IP validation, GFID generation, robust read/write partial I/O, fd closing exceptions, and FOP string/int mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/common-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/compat-errno.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/compat-errno.h

## Purpose
`compat-errno.h` defines GlusterFS' stable cross-platform error-code namespace and declares conversion functions between platform `errno` values and Gluster error codes. It also supplies missing errno aliases for portability.

## Important APIs, Types, and Functions
- `GF_ERROR_CODE_*`: numeric error constants for common POSIX/Linux errors, NFSv3 errors, Darwin, Solaris, and BSD-specific cases.
- `GF_ERROR_CODE_UNKNOWN` and `GF_ERRNO_UNKNOWN`: fallback unknown value 1024.
- Portability aliases: `ENOATTR`/`ENODATA`, `EBADFD`, `ETIME` when absent.
- `gf_errno_to_error(int32_t op_errno)`, `gf_error_to_errno(int32_t error)`: conversion declarations implemented per OS.

## Control Flow
The header is macro-only except conversion declarations. Compile-time conditionals define aliases when the platform lacks a symbol. Runtime conversion functions map native errno to/from the stable Gluster numeric namespace.

## State and Persistence
No state. The constants are part of wire/protocol/logging compatibility and must remain stable.

## Dependencies and Integration Points
Depends on `<errno.h>`. Used anywhere Gluster serializes, logs, or translates errors across nodes or platforms, including RPC, FOP callbacks, and translator error handling.

## Risks and Edge Cases
- Duplicate `GF_ERROR_CODE_ALREADY` and `GF_ERROR_CODE_INPROGRESS` definitions appear with identical values.
- Some fallback aliases depend on other platform-specific symbols being available.
- Changing numeric constants can break cross-version or cross-platform interoperability.
- Conversion implementations must handle unknown/unsupported codes without leaking host-specific surprises.

## Test Signals
Test bidirectional conversion for common errors, unknown values, platform aliases, NFS-specific codes, and robust mutex codes. Cross-platform CI is especially valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/compat-errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/compat-io_uring.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/compat-io_uring.h

## Purpose
`compat-io_uring.h` provides compile-time compatibility definitions for `io_uring` setup flags, feature bits, and operation codes that may be missing from older kernel headers.

## Important APIs, Types, and Functions
- Includes `<linux/io_uring.h>`.
- Defines missing `IORING_SETUP_*` flags through `IORING_SETUP_R_DISABLED`.
- Defines missing `IORING_FEAT_*` feature bits through `IORING_FEAT_NATIVE_WORKERS`.
- Defines missing `IORING_OP_*` opcodes from `NOP` through `UNLINKAT`.

## Control Flow
The header uses `#ifndef` guards around each macro. If the system kernel headers already define a value, that definition is used; otherwise Gluster supplies the expected numeric value.

## State and Persistence
No runtime state. It affects compile-time availability of constants used by `gf-io-uring.c`.

## Dependencies and Integration Points
Directly integrated with `gf-io-uring.c` setup, feature logging, opcode probing, and SQE construction. It shields Gluster from older development headers while still requiring runtime kernel support.

## Risks and Edge Cases
- The comment notes io_uring operations are usually enum constants, so `#ifndef` may not detect every header/version condition cleanly.
- Supplying constants at compile time does not mean the running kernel supports the feature or opcode; runtime probing remains mandatory.
- Numeric values must match Linux UAPI exactly.

## Test Signals
Build against old and new kernel headers, compile `gf-io-uring.c`, and run setup/probe tests on kernels with and without the declared features. Verify all fallback numeric constants against Linux UAPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/compat-io_uring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/compat-uuid.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/compat-uuid.h

## Purpose
`compat-uuid.h` wraps libuuid APIs behind `gf_uuid_*` inline functions so the rest of GlusterFS uses a consistent portability layer.

## Important APIs, Types, and Functions
- `gf_uuid_clear()`, `gf_uuid_compare()`, `gf_uuid_copy()`, `gf_uuid_generate()`, `gf_uuid_is_null()`, `gf_uuid_parse()`, `gf_uuid_unparse()`: one-to-one inline wrappers over libuuid.

## Control Flow
Each inline function immediately delegates to the corresponding libuuid function. The TODO comment leaves room for platform-specific implementations such as libc UUID support on NetBSD.

## State and Persistence
No internal state. UUID values are caller-provided buffers.

## Dependencies and Integration Points
Depends on `<uuid/uuid.h>`. Used across inode GFIDs, leases, path/GFID mapping, dictionary values, and common utility functions.

## Risks and Edge Cases
- Callers must provide correctly sized `uuid_t` and output buffers.
- `gf_uuid_unparse()` uses libuuid's default string case/format; code requiring lower/upper variants must be explicit elsewhere.
- Porting to platforms without libuuid requires filling in the compatibility TODO.

## Test Signals
Test parse/unparse round trips, null detection after clear, compare/copy semantics, generated UUID non-null behavior, and platform builds where libuuid differs or is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/compat-uuid.h -->
