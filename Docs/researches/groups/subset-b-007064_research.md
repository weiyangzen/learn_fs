<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/compat.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/compat.h

## Purpose
Provides platform compatibility glue for GlusterFS builds across Linux, BSD, Darwin, and Solaris. It normalizes missing constants, filesystem flags, xattr APIs, timestamp accessors, path limits, endian helpers, and selected libc functions so the rest of libglusterfs can compile against a mostly uniform interface.

## APIs, Types, and Functions
Important definitions include `UNIX_PATH_MAX`, `GF_XATTR_NAME_MAX`, `FALLOC_FL_*`, `F_GETLK64/F_SETLK64/F_SETLKW64`, `_PATH_UMOUNT`, `NAME_MAX`, `EUCLEAN`, and `ST_ATIM_*`/`ST_MTIM_*`/`ST_CTIM_*` accessor macros. Old libc wrappers map `l* xattr` calls to non-link-aware calls when unavailable. BSD and Darwin sections define `off64_t`, `ino64_t`, `sighandler_t`, IPv6 address aliases, and endian conversion macros. Solaris declares compatibility functions such as `asprintf()`, `strsep()`, Solaris xattr wrappers, rename/unlink wrappers, and `solaris_xattr_resolve_path()`. The exported `gf_umount_lazy()` abstracts lazy unmount plus optional directory removal.

## Control Flow, State, and Persistence
This header is compile-time control flow: preprocessor branches select OS-specific shims. It keeps no runtime state, but its macro choices determine how all callers interpret timestamps, xattr names, fallocate flags, and device/path limits. GCC poisoning of `system`, `mkostemp`, and `popen` enforces safer internal run APIs unless `RELAX_POISONING` is set.

## Dependencies and Integration
Depends on OS headers such as `sys/un.h`, `sys/xattr.h`, `linux/falloc.h`, `sys/extattr.h`, `machine/endian.h`, `libgen.h`, and `argp`. It is included by core headers including `iatt.h` and `glusterfs-fops.h`, so incompatibilities propagate widely.

## Risks and Test Signals
Risks are stale OS assumptions, silent behavior changes when link-aware xattr calls are unavailable, Darwin hard failure without 64-bit inode support, Solaris xattr emulation divergence, and timestamp precision loss when only zero-nsec fallbacks exist. Test signals include multi-OS compile coverage, xattr round trips on symlinks, stat timestamp conversion tests, fallocate flag availability checks, and builds that verify poisoned APIs are not used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/daemon.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/daemon.h

## Purpose
Declares GlusterFS daemonization helpers and the canonical null-device path used when detaching a process from the terminal.

## APIs, Types, and Functions
`DEVNULLPATH` is `/dev/null`. `os_daemon_return(int nochdir, int noclose)` and `os_daemon(int nochdir, int noclose)` expose daemon setup variants. The parameters follow the standard daemon convention: optionally avoid changing directory and optionally avoid closing standard descriptors.

## Control Flow, State, and Persistence
The header carries no state. Implementations are expected to fork/session-detach, redirect descriptors to `DEVNULLPATH` when requested, and return status in the variant-specific manner.

## Dependencies and Integration
Integrated by process startup paths for `glusterfs`, `glusterfsd`, and management daemons. It interacts with PID files, `glusterfs_ctx_t.daemon_pipe`, logging startup, and service managers.

## Risks and Test Signals
Risks include descriptor leaks, double-fork error handling, changing cwd unexpectedly, and daemonizing under supervisors that expect foreground mode. Test signals are startup tests for `--no-daemon` and daemon modes, stderr/stdout closure checks, PID-file correctness, and failure injection around fork, setsid, chdir, and opening `/dev/null`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/daemon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/default-args.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/default-args.h

## Purpose
Declares helpers that copy translator FOP input arguments and callback results into `default_args_t` and `default_args_cbk_t`. These snapshots support call stubs, wind/resume paths, default pass-through translators, and retry/deferred execution paths.

## APIs, Types, and Functions
The file provides `args_*_store()` for nearly every filesystem operation: lookup/stat/truncate/access, namespace operations, open/create/readv/writev, xattrs, locks, directory reads, checksums, setattr/fallocate/discard/zerofill, ipc/seek/lease, active-lock migration, icreate/namelink, and copy-file-range. Matching `args_*_cbk_store()` helpers store callback outputs including `iatt` pre/post buffers, inodes, fds, dicts, dirents, checksums, leases, and lock lists. `args_wipe()`, `args_cbk_wipe()`, and `args_cbk_init()` manage cleanup and initialization.

## Control Flow, State, and Persistence
Callers build a stack-local or heap call-stub argument object, invoke the appropriate store helper before winding, and later resume or unwind using the saved fields. The state is transient but ownership-sensitive: locs, dicts, iobrefs, fds, and inodes need correct ref/unref behavior in implementations.

## Dependencies and Integration
Depends on `defaults.h` types, `dict_t`, `loc_t`, `fd_t`, `inode_t`, `iatt`, `gf_flock`, dirents, leases, and lock migration structures. It integrates directly with the `default_*` entry points and the translator stack/call-stub framework.

## Risks and Test Signals
Risks include missing deep references, stale pointers to caller-owned data, incorrect paired cleanup, and signature drift when a FOP is extended. Test signals include call-stub replay tests, leak/refcount checks on dict/fd/inode/iobref fields, fault-injection paths through every `args_*_store()`, and compile failures when FOP prototypes change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/default-args.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/defaults.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/defaults.h

## Purpose
Defines the default translator operation surface for libglusterfs. It gives translators standard pass-through FOPs, callbacks, resume handlers, failure callbacks, notify/release/forget hooks, and argument carrier structures.

## APIs, Types, and Functions
`default_args_cbk_t` stores callback state such as op status, inode/fd, stat/pre/post buffers, vectors, iobrefs, xattrs/xdata, checksums, dirents, seek offsets, leases, and lock lists. `default_args_t` stores request-side state such as locs, fds, offsets, modes, masks, flags, link names, lock domains, xattr operations, lease data, and copy-file-range fds/offsets. The header declares `default_fops`, `default_notify()`, `default_forget()`, `default_release()`, `default_releasedir()`, normal `default_*` FOP/MOP entry points, `default_*_resume()` variants, `default_*_cbk()` and `default_*_cbk_resume()` handlers, `default_*_failure_cbk()` helpers, `default_mem_acct_init()`, and `default_fini()`.

## Control Flow, State, and Persistence
Default operations typically wind a request to the first child or unwind a standardized failure. Resume variants re-enter operations after call-stub/synctask suspension. Callback variants relay child results back up the stack. The structures are transient per-call state, while `default_fops` is a shared function table.

## Dependencies and Integration
Depends on `dict.h`, `iatt.h`, `locking.h`, and `stack.h`, plus core translator, inode, fd, iobuf, dirent, lease, and lock types. It is the integration baseline for xlators that only override selected operations.

## Risks and Test Signals
Risks include prototype mismatches across normal/resume/callback paths, incorrect default behavior for newer FOPs, refcount mistakes in saved arguments, and failure callbacks that lose required xdata or pre/post attributes. Test signals are translator pass-through tests, stacked xlator smoke tests, FOP signature compile coverage, leak checks on stubbed calls, and negative-path tests for each failure callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/defaults.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/dict.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/dict.h

## Purpose
Defines GlusterFS dictionaries, the dynamic key/value container used for xdata, options, RPC metadata, xattrs, and cross-translator annotations.

## APIs, Types, and Functions
Core types are `data_t`, `data_pair_t`, and `dict_t`. `data_t` stores a byte pointer, atomic refcount, typed `gf_dict_data_type_t`, length, and static/dynamic ownership flag. `dict_t` tracks count, total serialized key/value length, refcount, lock, linked members, and extra allocation. APIs cover creation/ref/unref/reset, `dict_setn()`/`dict_addn()`/`dict_get()`/`dict_deln()`, serialization/unserialization, copying, foreach and match traversal, typed conversions for signed/unsigned integers, doubles, strings, dynamic/static pointers, binary data, UUIDs, `iatt`, and mdata. `GF_PROTOCOL_DICT_SERIALIZE` and `GF_PROTOCOL_DICT_UNSERIALIZE` wrap RPC conversion with logging and errno assignment.

## Control Flow, State, and Persistence
Dictionaries are mutable refcounted in-memory state. Members are a linked list protected by `gf_lock_t`; serialized form is used across RPC and persisted metadata paths. Static data wrappers do not own payload memory, while dynamic wrappers transfer/free ownership.

## Dependencies and Integration
Depends on `common-utils.h`, atomics, pthread locking, `glusterfs-fops.h` data type enums, `iatt`, UUIDs, logging, and message IDs. Nearly every translator uses `dict_t` for xdata and configuration.

## Risks and Test Signals
Risks include static/dynamic ownership confusion, serialization size limits (`DICT_KEY_VALUE_MAX_SIZE`), unchecked typed getter failures, refcount leaks, and lockless inline iteration misuse. Test signals include serialize/unserialize round trips, typed getter/setter tests, refcount/leak tests, fuzzing malformed dict buffers, xdata propagation tests, and concurrency checks around set/delete/foreach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/dict.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/event-history.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/event-history.h

## Purpose
Declares a small event-history ring buffer abstraction for recording recent diagnostic events and dumping them through caller-provided formatting callbacks.

## APIs, Types, and Functions
`struct event_hist` contains a `buffer_t *` circular buffer and a `pthread_mutex_t` lock, with `eh_t` as the typedef. APIs are `eh_new()`, `eh_save_history()`, `eh_dump()`, and `eh_destroy()`. Creation takes buffer size, one-shot-buffer policy, and a data destructor callback.

## Control Flow, State, and Persistence
The event history is process-local volatile state. Callers allocate a history buffer, save entries under lock, dump the circular buffer through a callback, and destroy it with optional item cleanup.

## Dependencies and Integration
Depends on `circ-buff.h`, `glusterfs.h` for `gf_boolean_t`, pthreads, and diagnostic consumers selected by command-line or config options such as event history support.

## Risks and Test Signals
Risks include storing pointers whose lifetime is shorter than the history, destructor mismatches, dump/save races if locking is bypassed, and buffer-size choices that hide important events. Test signals include wraparound tests, one-shot mode tests, destructor invocation checks, concurrent save/dump stress, and statedump/log dump validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/event-history.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/events.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/events.h

## Purpose
Provides the compile-time event reporting facade used by GlusterFS code to emit structured operational events when event support is enabled.

## APIs, Types, and Functions
When `USE_EVENTS` is defined, the header includes `eventtypes.h` and declares `_gf_event(eventtypes_t event, const char *fmt, ...)` with printf-format checking. Without event support, `_gf_event()` is a static inline no-op returning 0. The `gf_event(event, fmt...)` macro validates the format through `FMT_WARN()` and calls `_gf_event()`.

## Control Flow, State, and Persistence
The control flow is compile-time gated. Runtime event delivery is delegated to the enabled implementation; otherwise calls are compiled as no-ops. This header stores no state.

## Dependencies and Integration
Integrated into management and translator paths that announce cluster or process events. Depends on event type definitions and common format-check macros from the broader logging/common-utils stack.

## Risks and Test Signals
Risks include event call sites silently doing nothing in builds without `USE_EVENTS`, format-string mismatch, and assuming event delivery is synchronous or reliable. Test signals include builds with and without event support, compiler format warnings, event daemon integration tests, and checks that key operational transitions emit expected event IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/fd-lk.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/fd-lk.h

## Purpose
Defines per-fd POSIX lock tracking context used to remember and merge locks associated with a GlusterFS fd.

## APIs, Types, and Functions
`fd_lk_ctx_t` contains a lock list, atomic refcount, and `gf_lock_t`. `fd_lk_ctx_node_t` stores command, lock type, start/end offsets, list link, and original `gf_flock`. Helper macros stringify `F_UNLCK`, `F_RDLCK`, `F_WRLCK`, `F_SETLK`, `F_SETLKW`, and `F_GETLK`. APIs include `fd_lk_ctx_create()`, `fd_lk_ctx_ref()`, `fd_lk_ctx_unref()`, `fd_lk_insert_and_merge()`, and `fd_lk_ctx_empty()`.

## Control Flow, State, and Persistence
Lock state is process-local and tied to `fd_t->lk_ctx`. Insert/merge records new lock ranges, combines compatible ranges, and removes or adjusts unlocked ranges. Refcounting controls lifetime while the fd or lock migration code references the context.

## Dependencies and Integration
Depends on `locking.h`, `list.h`, `gf_flock`, and `fd.h`. It integrates with `GF_FOP_LK`, active lock migration, reconnect handling, and fd cleanup.

## Risks and Test Signals
Risks include off-by-one lock range merging, unlock-before-lock accounting, stale lock state after fd close, and thread races around `lk_list`. Test signals include overlapping lock merge tests, unlock split tests, migration/reconnect scenarios, refcount leak checks, and concurrency tests around fd lock updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/fd-lk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/fd.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/fd.h

## Purpose
Defines GlusterFS file descriptor objects and fd tables. These objects connect open-file state to inodes, translator-private fd context, anonymous fd handling, and process fd-number allocation.

## APIs, Types, and Functions
`fd_t` stores pid, flags, atomic refcount, inode list membership, inode pointer, context lock, per-xlator `_fd_ctx` array, lock context, translator count, and anonymous status. `fdtable_t` is a refcounted table with rwlock, max size, entries, and free-list head. APIs allocate/destroy fd tables, get/free fd numbers, get fd pointers, copy/get all fds, create/look up/bind/close/ref/unref fds, create anonymous fds, test anonymous/list-empty state, and set/get/delete translator context values.

## Control Flow, State, and Persistence
`fd_t` state is volatile but long-lived for open handles. It is linked into an inode's fd list, referenced by call frames and translators, and eventually closed/unrefed. `fdtable_t` tracks process-visible numeric fd slots with `first_free` and sentinel values `GF_FDTABLE_END` and `GF_FDENTRY_ALLOCATED`.

## Dependencies and Integration
Depends on `list.h`, `glusterfs.h`, `fd-lk.h`, logging, and `xlator.h`. It is central to open/create/read/write/flush/fsync/lock paths and to protocol client/server fd translation.

## Risks and Test Signals
Risks include fdtable expansion/free-list corruption, fd context races, anonymous fd misuse, refcount leaks, and stale inode links. Test signals include fd allocation/free reuse tests, concurrent lookup/ref/unref stress, statedump context inspection, anonymous fd paths, and lock context cleanup on close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/fd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-dirent.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-dirent.h

## Purpose
Defines GlusterFS directory-entry objects and helpers for readdir/readdirp results, inode linking from directory entries, and distributed offset transformation.

## APIs, Types, and Functions
`gf_dirent_t` stores list links, inode number, offset, name length, d_type, optional `iatt`, per-entry dict, inode pointer, and flexible `d_name`. `gf_dirent_len()` and `gf_dirent_size()` compute allocation size. `inode_dir_or_parentdir()` recognizes `.` and `..`. APIs include `gf_dirent_for_name()`, `gf_dirent_for_name2()`, `entry_copy()`, `gf_dirent_entry_free()`, `gf_dirent_free()`, `gf_link_inode_from_dirent()`, `gf_link_inodes_from_dirent()`, `gf_fill_iatt_for_dirent()`, and offset transforms `gf_itransform()`, `gf_deitransform()`, and `gf_dirent_orig_offset()`.

## Control Flow, State, and Persistence
Directory entries are transient result lists passed through callbacks. Readdirp-style entries may carry stat data and inode references, allowing the inode table to be populated from directory listings. Offset transform helpers encode/decode distributed translator offsets.

## Dependencies and Integration
Depends on `iatt.h`, `inode.h`, `dict_t`, `xlator_t`, and list primitives. It integrates with `GF_FOP_READDIR`, `GF_FOP_READDIRP`, DHT offset handling, md-cache, protocol serialization, and inode cache population.

## Risks and Test Signals
Risks include flexible-array allocation mistakes, leaked dict/inode refs, incorrect `.`/`..` handling, and offset collisions across subvolumes. Test signals include readdir/readdirp round trips, valgrind/leak tests for entry lists, inode-linking checks, and DHT offset encode/decode tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-dirent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-event.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-event.h

## Purpose
Defines the low-level event loop abstraction used to register file descriptors, dispatch readiness notifications, manage poller threads, and support epoll-backed event processing.

## APIs, Types, and Functions
`event_handler_t` callbacks receive fd, slot index, generation, user data, readiness flags, error flag, and thread-exit notification. `event_pool` stores ops, epoll/poll fd data, breaker pipe, registration arrays, epoll slot tables, poller-death list, event cache, configured and active thread counts, auto-thread count, synchronization primitives, destroy flag, and poller thread IDs. `event_slot_epoll` tracks fd, events, generation, slot index, refs, close/handler/error state, data, handler, poller-death link, and lock. Public wrappers include `gf_event_pool_new()`, register/unregister/close, select-on, dispatch, reconfigure threads, destroy, dispatch-destroy, and handled notification.

## Control Flow, State, and Persistence
Callers create a pool, register fds with handlers, dispatch from one or more poller threads, modify interest masks with `select_on`, and unregister or unregister-close when done. Generation fields protect against stale fd events after slot reuse. State persists for the process lifetime of the event pool.

## Dependencies and Integration
Depends on pthreads, atomics/locks, list primitives, and `common-utils.h`. Used by RPC transports, sockets, management listeners, and client/server event processing.

## Risks and Test Signals
Risks include stale event delivery, fd close races, thread reconfiguration races, poller death notification ordering, and fallback differences between poll and epoll. Test signals include register/unregister stress, generation mismatch tests, multi-thread dispatch, unregister-close race tests, and clean shutdown with active handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-io-common.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-io-common.h

## Purpose
Defines common utilities for the GlusterFS I/O framework: negative-errno result handling, synchronization barriers, and configurable thread-pool startup/wait helpers.

## APIs, Types, and Functions
Result macros convert syscall-style results into framework `res` values: `gf_errno_check()`, `gf_ret_check()`, `gf_res_errno()`, `gf_res_errno0()`, `gf_res_err()`, `gf_res_ptr()`, `gf_check()`, `gf_succeed()`, and `gf_res_combine()`. `gf_io_lock()` and `gf_io_unlock()` abort on impossible pthread-lock failures. `gf_io_sync_t` stores mutex/cond, timeout, retry/phase/pending counts, opaque data, and result. Thread-pool types include `gf_io_thread_pool_t`, `gf_io_thread_t`, setup/main callbacks, and `gf_io_thread_pool_config_t` with name, CPU affinity, signals, count, stack, scheduling priority, first id, timeout, and retries. APIs are `gf_io_sync_start()`, `gf_io_sync_done()`, `gf_io_sync_wait()`, `gf_io_thread_pool_start()`, and `gf_io_thread_pool_wait()`.

## Control Flow, State, and Persistence
Errors are normalized at call sites and logged with source location. Synchronization objects coordinate worker startup/shutdown phases with retries and timeout. Thread pools maintain a list of worker records under mutex until all threads terminate.

## Dependencies and Integration
Depends on pthreads, errno, urcu compiler hints, logging, libglusterfs message IDs, common-utils, and compat errno. Used by `gf-io.h`, legacy and io_uring engines, and other threaded components.

## Risks and Test Signals
Risks include passing positive errno values, treating negative results as standard errno incorrectly, deadlocks in sync barriers, scheduler priority portability, and CPU-affinity gaps. Test signals include result-conversion unit tests, timeout/retry synchronization tests, thread naming/priority failure injection, and worker startup/cleanup leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-io-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-io-legacy.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-io-legacy.h

## Purpose
Declares the legacy I/O engine descriptor for the pluggable `gf_io` framework.

## APIs, Types, and Functions
Includes `gf-io.h` and exports `extern const gf_io_engine_t gf_io_engine_legacy`.

## Control Flow, State, and Persistence
The header has no state. At runtime engine selection can copy or reference `gf_io_engine_legacy` into the global `gf_io.engine` when legacy mode is chosen or when newer engines are unavailable.

## Dependencies and Integration
Depends entirely on `gf_io_engine_t` from `gf-io.h`. It integrates with engine selection, fallback behavior, and callback/async submission in the core I/O framework.

## Risks and Test Signals
Risks include legacy engine divergence from the common engine contract and fallback paths hiding io_uring initialization failures. Test signals include engine selection tests, legacy callback/async completion tests, shutdown/wait behavior, and parity checks against threaded/io_uring modes for supported operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-io-legacy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-io-uring.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-io-uring.h

## Purpose
Declares the io_uring I/O engine descriptor and its queue/retry/thread sizing constants.

## APIs, Types, and Functions
Defines `GF_IO_URING_QUEUE_SIZE` as `GF_IO_ID_REQ_COUNT`, `GF_IO_URING_QUEUE_MIN` as 4096, `GF_IO_URING_MAX_RETRIES` as 100, and `GF_IO_URING_WORKER_THREADS` as 16. Exports `extern const gf_io_engine_t gf_io_engine_io_uring`.

## Control Flow, State, and Persistence
This header carries no runtime state, but constants constrain io_uring setup and retry loops. The exported engine participates in `gf_io_run()` engine selection and implements the common engine callbacks.

## Dependencies and Integration
Depends on `gf-io.h`. It integrates with kernel io_uring feature probing, I/O request ID sizing, worker pool initialization, and LIBGLUSTERFS message IDs for io_uring failures.

## Risks and Test Signals
Risks include queue sizes unsupported by older kernels, insufficient feature checks, retry loops masking unrecoverable kernel errors, and worker-count tuning mismatches. Test signals include io_uring feature-probe tests, fallback-to-legacy tests, queue-min boundary tests, cancellation tests, and shutdown under pending submissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-io-uring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-io.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-io.h

## Purpose
Defines the core asynchronous I/O framework: request ID layout, engine abstraction, global I/O state, worker access, batching/chaining, cancellation, callback dispatch, and async function submission.

## APIs, Types, and Functions
Request IDs combine a 16-bit request index, 8 flag bits, and a counter; macros define masks, `GF_IO_ID_FLAG_CHAIN`, and counter increment. `gf_io_mode_t` selects legacy, io_uring, or threaded mode. Debug builds wrap callbacks and async functions with names/file/line via `GF_IO_CBK()` and `GF_IO_ASYNC()`. Core types include `gf_io_worker_t`, `gf_io_op_t`, `gf_io_request_t`, `gf_io_batch_t`, `gf_io_handlers_t`, `gf_io_engine_t`, and global `gf_io_t`. APIs and inline helpers include `gf_io_run()`, `gf_io_mode()`, `gf_io_worker_get()`, `gf_io_reserve()`, `gf_io_data_wait/read/write()`, `gf_io_get()`, `gf_io_put()`, `gf_io_cbk()`, batch init/add/submit, request chaining, cancel prepare/submit, callback prepare/submit, and async prepare/submit.

## Control Flow, State, and Persistence
`gf_io_run()` initializes the selected engine and blocks until process termination. Submission reserves sequence numbers, waits for free operation slots, fills `gf_io.op_pool`, and calls an engine operation. Completion invokes callbacks and returns slots to `op_map`. Batches submit multiple requests, optionally chaining them sequentially.

## Dependencies and Integration
Depends on urcu atomics/barriers, `gf-io-common.h`, `syscall.h`, pthreads, and engine descriptors. It underpins newer async infrastructure and integrates with logging through slow-callback/debug metadata.

## Risks and Test Signals
Risks include request-ID wrap/reuse races, memory-ordering bugs in `op_map`, callback use-after-free, chain/batch misuse, cancellation races, and global shutdown handling. Test signals include high-concurrency slot reuse tests, debug abort coverage for malformed batches, cancellation tests, callback latency logs, and engine parity tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gidcache.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gidcache.h

## Purpose
Defines a fixed-size auxiliary group-ID cache keyed by identifiers for uid/gid resolution, reducing repeated group lookup cost in busy systems.

## APIs, Types, and Functions
The cache is 4-way associative with 256 buckets, for `AUX_GID_CACHE_SIZE` of 1024 entries. `gid_list_t` stores lookup id, uid, gid, group count, allocated gid list, and expiration deadline. `gid_cache_t` stores a lock, max age, bucket count, and the fixed entry array. APIs are `gid_cache_init()`, `gid_cache_reconf()`, `gid_cache_lookup()`, `gid_cache_release()`, and `gid_cache_add()`.

## Control Flow, State, and Persistence
The cache is in-memory and time-bounded. Lookups search a bucket set under lock, return a const `gid_list_t`, and require `gid_cache_release()` by callers. Reconfiguration changes maximum age. Adds replace or populate entries and set deadlines.

## Dependencies and Integration
Depends on `glusterfs.h`, `locking.h`, `gid_t`, and `time_t`. It integrates with credential resolution, FUSE/server request authentication, and `cmd_args_t` gid timeout configuration.

## Risks and Test Signals
Risks include stale group membership until deadline, fixed-size collision pressure, ownership of `gl_list`, caller failure to release, and races during reconfiguration. Test signals include hit/miss/expiry tests, collision replacement tests, reconf timeout tests, concurrent lookup/add stress, and credential-auth integration checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gidcache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/glfs-message-id.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/glfs-message-id.h

## Purpose
Allocates stable log message ID ranges and defines the macro system for typed GlusterFS log messages.

## APIs, Types, and Functions
`GLFS_MSGID_BASE` and `GLFS_MSGID_SEGMENT` define global message-space layout. `GLFS_MSGID_COMP()` allocates component ranges in `_msgid_comp`. Legacy `GLFS_MSGID()` and migrated `GLFS_MIG()` support older numeric IDs. New typed messages use `GLFS_COMPONENT()`, `GLFS_NEW()`, `GLFS_OLD()`, and `GLFS_GONE()`, which generate message structs, inline capture functions, process functions, static range assertions, and formatted `_gf_log()` calls. Field helpers include `GLFS_U32/I32/U64/I64`, `GLFS_ERR`, `GLFS_RES`, `GLFS_RAW`, `GLFS_STR`, `GLFS_FUNC`, `GLFS_UUID`, and `GLFS_PTR`. Component segments are reserved for glusterfsd, libglusterfs, rpc, cli, glusterd, AFR, DHT, POSIX, quota, EC, io translators, and many others.

## Control Flow, State, and Persistence
This is compile-time code generation. `__COUNTER__` assigns IDs relative to component bases, `_Static_assert` prevents overruns, and inline message constructors defer formatting data preparation until logging is invoked. IDs are persistent external contracts for logs and tooling.

## Dependencies and Integration
Depends on logging, standard integer formatting, `strerror()`, and UUID formatting. Used by component message catalogs such as `libglusterfs-messages.h`.

## Risks and Test Signals
Risks include reordering or deleting IDs, exhausting a segment, macro argument mistakes, compiler-extension portability, and inconsistent field semantics. Test signals include compile-time static assertions, generated log output tests, ID-stability reviews, and builds across supported compilers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/glfs-message-id.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/globals.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/globals.h

## Purpose
Declares process-global GlusterFS state, operation-version constants, the `THIS` translator pointer mechanism, global xlator data, thread-local buffers, timer-wheel references, and global memory-accounting controls.

## APIs, Types, and Functions
Defines default port/transport, global xlator names, glusterd op-version keys, write-protection xattr keys, and the `GD_OP_VERSION_*` enum through version macros. `THIS` dereferences `__glusterfs_this_location()`, and `DECLARE_OLD_THIS` saves it. Externs include `global_xlator`, `global_xl_options`, `gf_fop_list`, `gf_upcall_list`, and `global_ctx`. APIs include syncop/synctask context accessors, UUID/lkowner/leaseid buffer getters, `glusterfs_globals_init()`, `gf_thread_needs_cleanup()`, timer-wheel get/put, and global memory accounting get/set.

## Control Flow, State, and Persistence
The header exposes thread-local and process-global state used throughout translator execution. `THIS` changes around calls to represent the currently executing xlator. Operation versions are persistent compatibility gates across cluster nodes.

## Dependencies and Integration
Depends on `xlator.h`, `options.h`, and `glusterfs_ctx_t`. It is integrated into almost every xlator, management operation, logging path, and compatibility negotiation path.

## Risks and Test Signals
Risks include incorrect `THIS` restoration, thread-local buffer reuse, global initialization ordering, op-version changes breaking rolling upgrades, and memory-accounting toggles racing with allocators. Test signals include translator stack tests validating `THIS`, op-version negotiation tests, thread cleanup tests, timer-wheel refcount tests, and global init failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/globals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/glusterfs-acl.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/glusterfs-acl.h

## Purpose
Defines GlusterFS POSIX ACL wire/xattr structures and helper mappings. It contains legacy Linux-oriented ACL support plus a newer libacl-style portable interface when `sys/acl.h` is available.

## APIs, Types, and Functions
Legacy constants include ACL RPC program/version, POSIX ACL permission bits, tag values, undefined id, xattr version, and disk xattr names `system.posix_acl_access` and `system.posix_acl_default`. `posix_acl_xattr_header` and `posix_acl_xattr_entry` model xattr layout; inline helpers compute xattr size and entry count. Runtime structures include `posix_ace`, `posix_acl`, `posix_acl_ctx`, and `posix_acl_conf`. New virtual RPC xattrs are `GF_POSIX_ACL_ACCESS` and `GF_POSIX_ACL_DEFAULT`; `GF_POSIX_ACL_REQUEST()` recognizes either. With `HAVE_SYS_ACL_H`, `gf_posix_acl_get_key()` and `gf_posix_acl_get_type()` map between `acl_type_t` and virtual keys.

## Control Flow, State, and Persistence
ACL xattr structures represent persistent ACL metadata; virtual keys are transported over RPC and not stored on disk. `posix_acl_conf` holds process/translator ACL configuration and minimal ACL cache under a lock.

## Dependencies and Integration
Depends on `locking.h`, uid/gid/mode types, optional `sys/acl.h`, and `SLEN` from `glusterfs.h` via include order. Integrated with POSIX ACL xlator, server/client xattr paths, and permission checking.

## Risks and Test Signals
Risks include endian/layout mismatches, Linux-specific legacy assumptions, invalid ACL size/count parsing, virtual xattrs leaking to disk, and unsupported NetBSD behavior. Test signals include ACL xattr encode/decode tests, access/default mapping tests, permission enforcement cases, cross-platform build coverage, and malformed ACL rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/glusterfs-acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/glusterfs-fops.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/glusterfs-fops.h

## Purpose
Defines stable enums and small protocol structures for GlusterFS filesystem operations, translator events, lock commands/types, lease commands/types, xattrop operations, seek modes, upcall flags, and dictionary data types.

## APIs, Types, and Functions
`glusterfs_fop_t` enumerates all FOP IDs from `GF_FOP_NULL` through `GF_FOP_COPY_FILE_RANGE` and `GF_FOP_MAXVALUE`. `glusterfs_event_t` enumerates parent/child, poll, cleanup, transport, graph, auth, defrag, barrier, upcall, scrub, ping, and signal events. Other enums include `gf_op_type_t`, `glusterfs_lk_cmds_t`, `glusterfs_lk_types_t`, `gf_lease_types_t`, `gf_lease_cmds_t`, `glusterfs_lk_recovery_cmds_t`, `gf_lk_domain_t`, `entrylk_cmd`, `entrylk_type`, `gf_xattrop_flags_t`, `gf_seek_what_t`, `gf_upcall_flags_t`, and `gf_dict_data_type_t`. `gf_lease` stores lease command/type/id/flags, and `gf_lkowner_t` stores lock-owner bytes.

## Control Flow, State, and Persistence
These numeric values are protocol and logging contracts. They drive dispatch tables, FOP arrays, RPC encoding, default operation tables, and translator event switching. The structures are transient request payloads but their sizes and values affect wire compatibility.

## Dependencies and Integration
Depends on `compat.h`. Included by `glusterfs.h`, dict typing, defaults, xlator interfaces, and protocol code.

## Risks and Test Signals
Risks include renumbering enums, missing `GF_FOP_MAXVALUE` updates, array-size mismatches, lease-id length assumptions, and incompatible dict data type changes. Test signals include RPC compatibility tests, `gf_fop_list` length checks, translator dispatch compile coverage, lock/lease round trips, and rolling-upgrade tests for new FOPs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/glusterfs-fops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/glusterfs.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/glusterfs.h

## Purpose
Central libglusterfs umbrella header for global constants, xattr key contracts, command-line/runtime context structures, graph lifecycle APIs, lock structures, and process-wide configuration.

## APIs, Types, and Functions
The header defines numerous xattr and xdata keys for pathinfo, node UUIDs, GFIDs, bitrot, locks, quota, AFR/DHT/index/heal, cloudsync, FUSE options, logging defaults, network timeouts, lock modes, and internal FOP context. It defines `gf_boolean_t`, cloudsync object states, FOP priorities and `fop_pri_to_string()`, `xlator_cmdline_option_t`, `server_cmdline_t`, `cmd_args_t`, `glusterfs_graph_t`, `glusterfs_ctx_t`, `gf_volfile_t`, `gf_flock`, `lock_migration_info_t`, and attributes `GF_MUST_CHECK`/`GF_UNUSED`. Graph APIs include create/construct/init/prepare/activate/deactivate/reconfigure/attach/destroy/fini and leaf/parent helpers. Other APIs include `glusterfs_ctx_new()`, `gf_flock_copy()`, `gf_free_mig_locks()`, and `glusterfs_read_secure_access_file()`.

## Control Flow, State, and Persistence
`cmd_args_t` captures startup configuration; `glusterfs_ctx_t` is the main process context holding active graphs, pools, event/iobuf/log resources, locks, timers, management pointers, daemon pipes, SSL flags, stats, janitor/disk-check threads, and backtrace buffer. Graph functions manage volfile-derived translator graphs through activation, reconfiguration, and cleanup. Many xattr keys are persistent on-disk or over-the-wire contracts.

## Dependencies and Integration
Includes FOP enums, list, logging, lock owner, UUID, refcount, OpenSSL SHA, and POSIX headers. It is imported by most libglusterfs and xlator code.

## Risks and Test Signals
Risks include key string drift, global context initialization ordering, graph lifecycle races, SSL/security flag confusion, command-line option lifetime issues, and lock migration leaks. Test signals include graph reconfigure/attach tests, xattr compatibility tests, startup option parsing tests, context cleanup leak tests, and rolling-upgrade behavior around persistent keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/glusterfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/graph-utils.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/graph-utils.h

## Purpose
Declares small helpers for building and inspecting GlusterFS translator graphs.

## APIs, Types, and Functions
`glusterfs_graph_print_file(FILE *file, glusterfs_graph_t *graph)` serializes a graph to a file stream. `glusterfs_xlator_link(xlator_t *pxl, xlator_t *cxl)` links a parent and child translator. `glusterfs_graph_set_first(glusterfs_graph_t *graph, xlator_t *xl)` records the first/root translator for graph traversal.

## Control Flow, State, and Persistence
The functions mutate or inspect graph topology in memory. Printing can persist a representation to a file for diagnostics or generated volfile output, while link/set-first adjust active graph relationships before activation.

## Dependencies and Integration
Relies on `FILE`, `glusterfs_graph_t`, and `xlator_t` supplied by includers such as `glusterfs.h`/`xlator.h`. Used by volfile parsing, graph construction, debugging, and graph reconfiguration.

## Risks and Test Signals
Risks include cycles, missing first translator, incorrect parent/child linkage, and output that diverges from parser expectations. Test signals include graph print/parse round trips, topology validation, cycle rejection, and reconfiguration tests that compare expected parent/child relationships.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/graph-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/hashfn.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/hashfn.h

## Purpose
Declares non-cryptographic hash functions used by GlusterFS for data distribution, lookup tables, or message/string hashing.

## APIs, Types, and Functions
`SuperFastHash(const char *data, int32_t len)` computes a 32-bit hash for a byte string. `gf_dm_hashfn(const char *msg, int len)` computes another 32-bit hash used by GlusterFS distribution/mapping code.

## Control Flow, State, and Persistence
Both APIs are pure hash computations with no persistent state. Their output can affect persistent placement or lookup behavior if used for layout decisions.

## Dependencies and Integration
Depends on integer and size types. Integrated with hash tables and distributed layout code that needs stable, fast hashes.

## Risks and Test Signals
Risks include hash instability if algorithms change, collision behavior under adversarial names, signed-length misuse, and non-cryptographic use in security-sensitive paths. Test signals include known-vector tests, distribution/collision benchmarks, DHT placement compatibility tests, and checks for negative/zero length handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/hashfn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/iatt.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/iatt.h

## Purpose
Defines GlusterFS internal inode-attribute representation and conversions to/from POSIX `struct stat`.

## APIs, Types, and Functions
`ia_type_t` models file type. `ia_prot_t` stores suid/sgid/sticky and owner/group/other rwx bits. `struct iatt` stores valid flags, inode/device/rdev, size, nlink, uid/gid, block size/count, atime/mtime/ctime/btime with nanoseconds, file attributes/mask, GFID, type, and protection. `mdata_iatt` carries mutable time metadata. Validity masks and macros check field presence. Helpers convert device major/minor, mode to type/protection, type/protection to mode, `iatt_to_mdata()`, `iatt_from_stat()`, `iatt_to_stat()`, and `is_same_mode()`.

## Control Flow, State, and Persistence
`iatt` values are passed through FOP callbacks and xdata and may represent persistent filesystem metadata. `iatt_from_stat()` caps `ia_blocks` to size-derived maximum to avoid over-accounting preallocated blocks, then sets valid flags except GFID/INO. Conversion helpers centralize mode and timestamp representation.

## Dependencies and Integration
Depends on `compat.h` timestamp macros, UUID support, sys/stat, and device macros. Used by lookup/stat/create/readdirp callbacks, dict serialization, inode linking, quota, DHT, AFR, and protocol code.

## Risks and Test Signals
Risks include sparse-file block accounting inaccuracies, timestamp precision portability, invalid `ia_flags`, mode/type conversion mistakes, birth-time availability, and device-number conversion differences. Test signals include stat conversion round trips, sparse/preallocated file quota tests, mode-bit tests, nanosecond preservation tests, and GFID validity checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/iatt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/inode.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/inode.h

## Purpose
Defines the in-memory inode table, inode, dentry, and per-translator inode context APIs used by GlusterFS to cache namespace state and object identity.

## APIs, Types, and Functions
`inode_table_t` stores global table lock, dentry/inode hash sizes, root inode, owning xlator, hash buckets, active/lru/purge/invalidate lists and counts, fd mempool, context slot count, invalidator callback, cleanup state, and root id/level. `dentry_t` links inode, parent, and name into inode and hash lists. `inode_t` stores table, GFID, lock, nlookup/kids atomics, fd counts, refcount, type, fd/dentry/hash/list links, namespace inode, invalidation/lru flags, and flexible `_inode_ctx` array. APIs cover table creation/destruction, inode new/link/unlink/rename/find/path/resolve, lookup/forget/ref/unref, invalidation, dentry grep, context set/get/reset/delete for one or two values, LRU limit changes, fd/inode context merge, linked/dentry checks, lookup-needed checks, directory-name discovery, and namespace-inode assignment.

## Control Flow, State, and Persistence
The inode table is process-local cache state keyed by GFID and parent/name. Lookups and links populate it; forget/unref/LRU/purge/invalidate paths evict or notify. Per-xlator context slots attach translator-private state to shared inode objects.

## Dependencies and Integration
Depends on `iatt.h`, UUIDs, `fd.h`, lists, locks, and xlator callbacks. Integrated with FUSE nlookup semantics, DHT/AFR caches, readdirp inode linking, fd tracking, and graph cleanup.

## Risks and Test Signals
Risks include dentry cycles, stale GFID/name aliases, ref/nlookup leaks, invalidation races, context slot misuse, and LRU/purge list corruption. Test signals include path/link/rename tests, forget/invalidation tests, dentry cycle detection logs, concurrent lookup/ref tests, and statedump ref/context inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/inode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/iobuf.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/iobuf.h

## Purpose
Defines GlusterFS pooled I/O buffers and iobref containers used to manage memory backing vector I/O without excessive allocation churn.

## APIs, Types, and Functions
`iobuf_pool` owns arenas bucketed by page size, filled lists, purge lists, default page size, arena size, miss count, and arena count. `iobuf_arena` represents an mmap region with passive/active lists, counts, allocation stats, and flexible `iobufs`. `iobuf` stores arena link, lock, atomic refcount, usable pointer, page size, and allocated buffer. `iobref` is a refcounted list of iobuf pointers. APIs create/destroy pools, allocate/ref/unref iobufs, convert to iovec, allocate small/page-aligned buffers, create/ref/unref/add/merge/clear iobrefs, compute sizes, dump stats, and copy an iovec into pooled storage. Macros provide alignment and pointer/page-size access.

## Control Flow, State, and Persistence
I/O buffers are process-local pooled memory. Allocation chooses a size bucket or small buffer path, moves buffers between passive/active lists, and returns arenas to purge when idle. Iobrefs group buffers so request/response vectors keep backing memory alive across async callbacks.

## Dependencies and Integration
Depends on mmap flags, atomics, locks, list, and `struct iovec`. Used by readv/writev callbacks, protocol serialization, quick-read/content paths, and translator data movement.

## Risks and Test Signals
Risks include refcount leaks, arena-list corruption, alignment mistakes, copying beyond iovec lengths, unbounded large-buffer misses, and use-after-unref in async paths. Test signals include iobuf ref/unref stress, iobref merge tests, valgrind/ASAN on read/write paths, alignment tests, and stats dump verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/iobuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/latency.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/latency.h

## Purpose
Defines a compact latency accumulator for measuring operation durations in nanoseconds.

## APIs, Types, and Functions
`gf_latency_t` stores minimum, maximum, total, and count. APIs are `gf_latency_new(size_t n)` for arrays, `gf_latency_reset()`, and `gf_latency_update(gf_latency_t *lat, struct timespec *begin, struct timespec *end)`.

## Control Flow, State, and Persistence
Callers allocate one or more counters, reset them, and update with begin/end timestamps after operations. State is in-memory diagnostic data and usually tied to process or translator lifetime.

## Dependencies and Integration
Depends on `time.h` and integer types. Integrated with `glusterfs_ctx_t.measure_latency`, statedump/statistics paths, and operation profiling.

## Risks and Test Signals
Risks include non-monotonic timestamps if callers use unsuitable clocks, total overflow in long-running processes, unsynchronized concurrent updates, and min initialization mistakes. Test signals include reset/update unit tests, monotonic-clock integration checks, concurrent update review, and latency statedump validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/latency.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/libglusterfs-messages.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/libglusterfs-messages.h

## Purpose
Defines the LIBGLUSTERFS component log message catalog: stable legacy message IDs, newer typed messages, and legacy string constants used by libglusterfs logging sites.

## APIs, Types, and Functions
Starts `GLFS_COMPONENT(LIBGLUSTERFS)` and lists many `GLFS_MIG()` IDs for dictionary, memory, file, graph, event, thread, inode, fd, lock, network, option, timer, and async failures. New typed `GLFS_NEW()` messages cover I/O call failure, thread priority/CPU/name errors, slow callbacks, no engine, io_uring unsupported/invalid/missing features/too small/unrecoverable enter failure, sync timeout/abort/completion, bad errno/return, file-descriptor limit failure, unlink failure, and `inet_net_pton()` failure. The trailing `LG_MSG_*_STR` constants preserve old string text for many log sites.

## Control Flow, State, and Persistence
This header generates compile-time log identifiers and inline message constructors. Message IDs are persistent operational contracts for log parsing and support tooling; string constants remain compatibility text for older `gf_msg()` style logging.

## Dependencies and Integration
Depends on `glfs-message-id.h`. Used by compatibility, dict, event, graph, inode, iobuf, gf-io, and common-utils code when emitting `LG_MSG_*`.

## Risks and Test Signals
Risks include deleting/reordering IDs, mismatch between typed messages and call sites, duplicated stale string constants, and component segment exhaustion. Test signals include compile-time ID-range checks, logging call compilation, log-format tests for typed messages, and review that new messages append rather than reuse IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/libglusterfs-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/list.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/list.h

## Purpose
Provides GlusterFS's intrusive circular doubly linked list primitives, closely resembling Linux kernel `list_head`.

## APIs, Types, and Functions
`struct list_head` stores next/prev pointers. APIs/macros initialize, add head/tail, ordered add by comparator, delete, delete-and-init, move head/tail, test empty/last/singular, splice/append with optional source reinit, replace with optional old reinit, rotate left, convert node to containing entry, access first/last/next/previous entries, iterate forward/reverse, safe iterate while deleting, and return nullable next/prev entries relative to a head. `LIST_POISON1` and `LIST_POISON2` mark deleted links.

## Control Flow, State, and Persistence
Lists are embedded into owning structures; the head is a sentinel and empty list points to itself. Operations directly mutate links and do not perform locking. Persistence is whatever lifetime the embedding structure provides.

## Dependencies and Integration
No external dependencies beyond compiler `typeof` support. Used throughout libglusterfs for inode/fd/dentry lists, event slots, iobuf arenas, graphs, volfiles, lock lists, and thread pools.

## Risks and Test Signals
Risks include using uninitialized nodes, deleting twice, iterating without safe macros while deleting, missing locks around shared lists, and type errors hidden by intrusive casting. Test signals include list primitive unit tests, ASAN/UBSAN for poisoned pointers, stress tests on inode/event/iobuf lists, and code review for safe iteration in deletion paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/list.h -->
