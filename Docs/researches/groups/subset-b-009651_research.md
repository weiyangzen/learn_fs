# Research Report: subset-b-009651

Grouped research for selected libfuse high-level API, daemonization, logging, and loop implementation files. Each section preserves the original source path and is bounded by deterministic split markers.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse.c -->
# sources/user-network-fs/libfuse/lib/fuse.c

## Purpose

`fuse.c` implements libfuse's high-level path-based API on top of the low-level `fuse_session` request API. It translates kernel-facing inode/nodeid requests into user filesystem paths, invokes callbacks from `struct fuse_operations`, manages the high-level `struct fuse` lifecycle, and owns high-level conveniences such as hidden-file deletion, readdir buffering, node remembering, module stacking, interrupt delivery, and option parsing.

The file is the main bridge between applications using `fuse_new()`, `fuse_loop()`, `fuse_mount()`, and path-oriented callbacks such as `getattr`, `read`, `write`, `readdir`, `rename`, and `unlink`, and the lower-level dispatcher that works with `fuse_req_t`, `fuse_lowlevel_ops`, and kernel protocol opcodes.

## Important APIs, Types, And Functions

Core private types include `struct fuse_fs`, which wraps `struct fuse_operations`, user data, and debug state; `struct fuse`, which owns the `fuse_session`, node tables, LRU list, config, lock, module stack, and cleanup thread; `struct node`, which maps libfuse node ids to parent/name/path state and open/cache/lock metadata; `struct node_table`, which is a split-growing hash table used for both id and name indexes; `struct fuse_dh`, which tracks high-level directory handles and buffered directory entries; and `struct fuse_context_i`, which extends public `struct fuse_context` with the current request.

The public and ABI-versioned entry points include `fuse_fs_new`, `_fuse_new_31`, `_fuse_new_30`, `fuse_new_31`, `fuse_new_30`, `fuse_destroy`, `fuse_mount`, `fuse_unmount`, `fuse_get_session`, `fuse_loop`, `fuse_loop_mt_312`, `fuse_loop_mt_32`, `fuse_loop_mt_31`, `fuse_exit`, `fuse_get_context`, `fuse_getgroups`, `fuse_interrupted`, `fuse_invalidate_path`, `fuse_clean_cache`, `fuse_notify_poll`, `fuse_version`, and `fuse_pkgversion`.

The callback wrapper layer is exposed inside libfuse as `fuse_fs_*` helpers such as `fuse_fs_getattr`, `fuse_fs_open`, `fuse_fs_read_buf`, `fuse_fs_write_buf`, `fuse_fs_readdir`, `fuse_fs_lock`, `fuse_fs_statx`, and `fuse_fs_syncfs`. These wrappers set `fuse_get_context()->private_data`, apply debug logging, provide fallback behavior where appropriate, and normalize absent callbacks to `-ENOSYS` or success depending on operation semantics.

`fuse_path_ops` is the low-level operation table. Its handlers, named `fuse_lib_*`, receive nodeids and request objects, reconstruct or lock paths, call the `fuse_fs_*` wrapper, update high-level caches, and send low-level replies.

## Control Flow

Construction starts in `_fuse_new_31`: allocate `struct fuse`, initialize default timeouts and interrupt signal, parse `fuse_lib_opts`, register built-in modules, create the thread-local context key, build a base `fuse_fs`, optionally push `modules=` layers, create a versioned `fuse_session` with `fuse_path_ops`, initialize name/id hash tables, initialize locks and LRU/slab lists, create the root node, and return the high-level handle. The 3.0 compatibility constructors add `--help` handling before delegating.

Request processing flows from a loop (`fuse_loop`, `fuse_loop_mt_*`, or lower-level session loop) into `fuse_session_process_buf_internal`, which dispatches through `fuse_path_ops`. Each handler calls `req_fuse_prepare` to create a thread-local context populated with uid, gid, pid, and umask from `fuse_req_ctx(req)`. The handler then obtains a path with `get_path`, `get_path_name`, `get_path_wrlock`, or `get_path2`; prepares interrupt handling if enabled; calls the corresponding high-level operation wrapper; updates node or directory-handle state; and replies with `fuse_reply_*` or `reply_err`.

Path reconstruction walks from a node to the root through parent pointers under `f->lock`, prepending names into a dynamically resized path buffer. Mutating operations can take tree locks on destination nodes or ancestor paths. If a conflicting tree lock exists, `lock_queue_element` instances are queued on `f->lockq` and signaled by `wake_up_queued` when paths are unlocked.

Lookup and cache flow is split between `lookup_path`, `do_lookup`, and `find_node`. A successful filesystem `getattr` creates or finds a `node`, assigns a generation and nodeid, inserts it into name/id hash tables, increments lookup counts, sets entry and attribute timeouts, and optionally records stat data for `auto_cache`. `FORGET` and `FORGET_MULTI` decrease `nlookup`; remembered nodes can be moved to an LRU list instead of being immediately freed.

File open/create paths call the filesystem callback, set policy flags such as `direct_io`, `keep_cache`, `parallel_direct_writes`, and `noflush`, increment `open_count`, and reply with open/create data. Release decrements `open_count` and removes `.fuse_hidden*` files when the last handle closes. Reads and writes use buffer-vector helpers so either `read`/`write` or `read_buf`/`write_buf` implementations can satisfy the same low-level request.

Directory flow uses `struct fuse_dh`. `opendir` allocates a high-level directory handle and stores it in the low-level file handle. `readdir` either writes directly into a response buffer when the filesystem supplies nonzero offsets, or stores a linked list of `fuse_direntry` records for later offset-based replay. `readdirplus` can call `do_lookup` for entries marked with `FUSE_FILL_DIR_PLUS`.

Shutdown in `fuse_destroy` restores an installed interrupt signal handler, creates a context for destroy callbacks, unlinks hidden nodes, frees every node from id table buckets, asserts slab lists are empty, unloads modules, frees hash tables/session/configuration, destroys locks, and deletes the thread-local context key.

## State And Persistence Behavior

The file maintains in-memory runtime state only. There is no disk persistence, but it has durable effects on the mounted filesystem and on backing files through user callbacks. Important mutable state includes the node id counter and generation, name and id hash tables, root and child nodes, lookup/reference counts, open counts, hidden-file flags, per-node lock lists, stat cache timestamps and sizes, LRU remembered-node ordering, module reference counts, and a global thread-local context key reference count.

Node tables use incremental split hashing. `hash_id`/`hash_name` grow and split tables when use reaches half of size; `unhash_id`/`unhash_name` can remerge and shrink when use falls below a quarter. With `FUSE_NODE_SLAB`, node memory comes from page-sized `mmap` slabs; otherwise it comes from `calloc`.

With `remember > 0`, forgotten nodes remain in `lru_table` until `fuse_clean_cache` ages them out. Single-threaded `fuse_loop` uses `fuse_session_loop_remember` with `poll` timeouts to clean remembered nodes, while multithreaded `fuse_loop_mt_312` starts `fuse_prune_nodes` as a cleanup thread.

Hidden-file state implements POSIX unlink semantics for open files. If `hard_remove` is disabled and an open file is unlinked or overwritten, libfuse renames it to `.fuse_hidden%08x%08x`, marks the node hidden, decrements visible link counts in getattr/statx replies, and unlinks the hidden path on final release or destroy.

## Dependencies And Integration Points

This file depends on public libfuse headers (`fuse.h`, `fuse_lowlevel.h`, `fuse_opt.h`) and internal headers (`fuse_i.h`, `fuse_kernel.h`, `fuse_misc.h`, `util.h`). It integrates directly with low-level session creation through `fuse_session_new_versioned`, request replies such as `fuse_reply_entry`, buffer utilities such as `fuse_buf_copy`, mount helpers via `fuse_session_mount`/`unmount`, and notification APIs through `fuse_lowlevel_notify_*`.

It also integrates with optional loadable modules. Built-ins `subdir` and, when configured, `iconv` are registered by factory symbol. Dynamic modules are loaded as `libfusemod_<name>.so` and searched for `fuse_module_<name>_factory`; factories can wrap the existing `fuse_fs` stack.

System dependencies include pthread mutexes, condition variables and thread-local keys; POSIX signals for interrupt handling; `dlopen`/`dlsym` for modules; `mmap` for node slabs; `poll` for the remembered-node single-thread loop; and standard filesystem types and constants.

## Risks And Edge Cases

The highest-risk area is path and node concurrency. Tree locks, queued waiters, hidden-file renames, `FORGET` handling, and multi-path operations such as rename must preserve parent/name consistency while callbacks may block or be interrupted. `try_get_path2` explicitly notes that locking two paths needs deadlock checking, so rename/link style operations deserve focused concurrency tests.

The node/name table implementation aborts on internal inconsistencies and relies on correct reference accounting. Incorrect `nlookup`, `refctr`, `open_count`, or LRU transitions can produce stale nodes, leaked nodes, premature deletion, or aborts. The slab allocator assumes page alignment when deriving a slab from a node pointer.

Callback return validation is limited. The code logs when reads or writes exceed requested size, but it still depends on filesystem implementations to follow high-level API contracts. Many wrappers treat absent callbacks as `-ENOSYS`, while release/opendir/open defaults are success; changing those semantics can break compatibility.

`fuse_destroy` iterates all modules with `while (fuse_modules) fuse_put_module(fuse_modules)`, which touches global module state, so module reference-count correctness matters across multiple `struct fuse` instances. `fuse_lib_help` loads modules to print help and does not visibly release every dynamically loaded module in that path.

Interrupt handling uses a signal sent to the worker thread once per second until the operation marks itself finished. This depends on signal handler setup, request interruption registration, and the callback being signal-aware or syscall-interruptible.

## Test Signals

Unit tests should exercise node lookup/forget/reference transitions, name and id hash growth/shrink behavior, path reconstruction with concurrent renames, hidden-file unlink/release flow, `remember` LRU expiry, and `lookup_path_in_cache` plus `fuse_invalidate_path` behavior. Callback wrapper tests should verify `-ENOSYS` defaults, private-data assignment, debug-safe formatting, buffer-vector fallback between `read`/`read_buf` and `write`/`write_buf`, and validation when callbacks return oversized reads or writes.

Integration tests should mount small high-level filesystems and drive lookup, create, open, read/write, readdir/readdirplus, rename including `RENAME_EXCHANGE`, xattrs, locks, ioctl, poll, fallocate, copy_file_range, lseek, statx, syncfs, and interrupt requests. Stress tests should combine multithreaded loops with rename/unlink/open/forget storms, remembered-node cleanup, module stacking, and forced interrupted open/create/opendir replies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_daemonize.c -->
# sources/user-network-fs/libfuse/lib/fuse_daemonize.c

## Purpose

`fuse_daemonize.c` implements both the legacy `fuse_daemonize(int foreground)` helper and the newer early-daemonization protocol used when a filesystem wants the parent process to remain alive until mount and FUSE initialization are known to have succeeded. The new path is coordinated through `fuse_daemonize_early_start`, `fuse_daemonize_early_success`, `fuse_daemonize_early_fail`, and internal state setters called from mount and FUSE_INIT handling.

The file exists to make daemon startup observable and failure-aware: the original process forks, the parent waits on a pipe, and the child signals success only after the mount has completed and the session has received or processed initialization.

## Important APIs, Types, And Functions

The private `struct fuse_daemonize` stores the requested flags, pipe file descriptors, watcher thread handle, and atomic state bits: `active`, `daemonized`, `mounted`, and `got_init`. The singleton `daemonize` object is file-global and initialized with invalid file descriptors.

New API functions are `fuse_daemonize_early_start(unsigned int flags)`, `fuse_daemonize_early_success(void)`, `fuse_daemonize_early_fail(int err)`, `fuse_daemonize_early_is_used(void)`, `fuse_daemonize_early_is_active(void)`, `fuse_daemonize_early_set_mounted(void)`, and `fuse_daemonize_set_got_init(void)`. The last two are internal coordination hooks declared in `fuse_daemonize_i.h`.

Important private helpers are `do_daemonize`, `daemonize_child`, `parent_watcher_thread`, `start_parent_watcher`, `stop_parent_watcher`, `fuse_daemonize_early_signal`, and `close_if_valid`.

## Control Flow

`fuse_daemonize_early_start` resets the singleton file descriptors, records flags, optionally `chdir("/")`, and if `FUSE_DAEMONIZE_NO_BACKGROUND` is not set marks daemonization active and calls `do_daemonize`. A second call while active returns success without forking again.

`do_daemonize` creates a signal pipe and a death pipe, then forks. The child closes the parent-side pipe ends, records the signal write end and death read end, and calls `daemonize_child`. The parent closes the child-side pipe ends, blocks reading an integer status from the signal pipe, closes both remaining fds, and exits with the received status or failure if the read is short.

`daemonize_child` creates a stop pipe, calls `setsid`, redirects stdin to `/dev/null`, and starts `parent_watcher_thread`. The watcher polls the parent death pipe and stop pipe. If the parent dies before normal completion, the child exits with failure; if the stop pipe is written, it returns normally. Once the watcher is running, the child marks itself daemonized and continues setup.

`fuse_daemonize_early_success` is intentionally tolerant if the new API was not used. When active, it delegates to `fuse_daemonize_early_signal(FUSE_DAEMONIZE_SUCCESS)`. That signal helper suppresses success notification until both `mounted` and `got_init` are true, then deactivates the state, stops the watcher, writes the status to the parent, redirects stdout and stderr to `/dev/null` after successful daemonization, and closes all tracked fds. `fuse_daemonize_early_fail` always attempts to signal an error status through the same path.

The legacy `fuse_daemonize` rejects use after the newer API is active or daemonized. For background mode, it creates a waiter pipe, forks, lets the parent wait for one byte from the child, calls `setsid`, `chdir("/")`, redirects stdin/stdout/stderr to `/dev/null`, signals the parent, and returns in the child. For foreground mode it only changes directory to `/`.

## State And Persistence Behavior

All daemonization state is process-local in the singleton `daemonize`. There is no file persistence. The code mutates process-level state: forks, creates a new session, changes working directory, redirects standard file descriptors, creates pipes, and starts or joins a pthread. Parent and child have independent copies of the singleton after fork, with the child retaining the operational file descriptors.

The `mounted` and `got_init` flags decouple mount completion from FUSE_INIT completion. This is important because libfuse can run synchronous or asynchronous initialization paths; success should be reported only when both conditions needed by the selected mode have occurred.

## Dependencies And Integration Points

This file includes public `fuse_daemonize.h` and internal `fuse_daemonize_i.h`. Its internal setters are expected to be called from mount/session code: `fuse_daemonize_early_set_mounted` from `fuse_session_mount()` and `fuse_daemonize_set_got_init` when FUSE_INIT is handled. Higher-level helper code calls `fuse_daemonize_early_start` before mounting and calls success/failure at appropriate post-mount or init points.

System dependencies include `fork`, `pipe`, `setsid`, `chdir`, `open`, `dup2`, `close`, `read`, `write`, `poll`, `_exit`, pthread creation/joining, atomics, and `errno`/`err` reporting.

## Risks And Edge Cases

The parent exits using the integer status written by the child. `fuse_daemonize_early_fail(int err)` writes the caller's value directly; if callers pass negative errno values, process exit status truncation may be surprising. `FUSE_DAEMONIZE_FAILURE` is defined but not directly used by the fail path.

`parent_watcher_thread` loops on `poll` errors without checking for cancellation or persistent invalid fds. If stop signaling fails, `stop_parent_watcher` still joins and could block if the watcher cannot observe the stop pipe. The new path uses atomics for state bits but not a broader mutex around fd lifecycle; repeated or cross-thread success/failure calls could race around `active` and fd closure.

`fuse_daemonize_early_signal` calls `errx(EINVAL, ...)` if the signal helper is reached while inactive. That exits the process rather than returning an error, so misuse is fatal. Legacy `fuse_daemonize` calls `perror` with a string that already contains a newline and may not have a meaningful `errno` for the "new API already used" case.

## Test Signals

Tests should cover early daemonization in foreground/no-background and background modes, including parent exit status on success and failure, deferral of success until both mounted and got_init are set, parent-death detection before success, stop-watcher cleanup, fd closure, and stdout/stderr redirection after success. Regression tests should verify that legacy `fuse_daemonize` refuses to run after the new API is active and preserves the long-standing foreground/background behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_daemonize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_daemonize_i.h -->
# sources/user-network-fs/libfuse/lib/fuse_daemonize_i.h

## Purpose

`fuse_daemonize_i.h` is the private header for libfuse's early daemonization coordination hooks. It exposes only the internal state transitions needed by mount and initialization code while keeping the public daemonization API in `include/fuse_daemonize.h`.

## Important APIs, Types, And Functions

The header declares `fuse_daemonize_early_set_mounted(void)`, `fuse_daemonize_early_is_used(void)`, and `fuse_daemonize_set_got_init(void)`. It includes `<stdint.h>` and `<stdbool.h>` and uses a standard include guard `FUSE_DAEMONIZE_I_H_`.

`fuse_daemonize_early_set_mounted` is documented as called from `fuse_session_mount()`. `fuse_daemonize_set_got_init` records that FUSE_INIT handling happened. `fuse_daemonize_early_is_used` lets other internals detect whether the new early daemonization path is active or has daemonized.

## Control Flow

The header has no executable control flow. Its declarations support the control flow in `fuse_daemonize.c`: early start sets `active`, mount code calls the mounted setter, init handling calls the got-init setter, and success signaling checks both flags before notifying the parent.

## State And Persistence Behavior

No state is defined in this header. The declarations mutate or query the file-global daemonization singleton in `fuse_daemonize.c`. There is no persistence beyond process memory and inherited post-fork state.

## Dependencies And Integration Points

This private header is included by `fuse_daemonize.c` and should be included by internal session or mount code that needs to mark mount/init progress. It should not be treated as a public application header; public callers use `include/fuse_daemonize.h`.

## Risks And Edge Cases

Because this header intentionally exposes only partial daemonization state management, incorrect call placement in mount or init code can make the parent wait forever or exit too early. The functions have no parameters describing which session is being initialized, so the implementation is singleton-oriented rather than per-session.

## Test Signals

Tests should verify that mount code calls `fuse_daemonize_early_set_mounted` exactly after a successful mount and that FUSE_INIT handling calls `fuse_daemonize_set_got_init`. Integration tests for `fuse_daemonize.c` should indirectly validate this header by confirming that early success is not signaled until both internal hooks have run.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_daemonize_i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_i.h -->
# sources/user-network-fs/libfuse/lib/fuse_i.h

## Purpose

`fuse_i.h` is a central private libfuse header that defines internal request, session, channel, module, and loop-configuration structures shared across the library implementation. It bridges public headers such as `fuse.h` and `fuse_lowlevel.h` with implementation files such as `fuse.c`, `fuse_lowlevel.c`, `fuse_loop.c`, `fuse_loop_mt.c`, mount backends, buffer utilities, and daemonization code.

## Important APIs, Types, And Functions

Key internal structures are `struct fuse_req`, `struct fuse_notify_req`, `struct fuse_session_uring`, `struct fuse_session`, `struct fuse_chan`, `struct fuse_module`, and, for API versions at or above 3.12, the private `struct fuse_loop_config`.

`struct fuse_req` stores the owning session, unique request id, atomic reference count, request lock, credentials/context, channel, interruption state, io_uring/copy-file-range flags, interrupt callback union, list links, and security-context iterator state. `struct fuse_session` stores mountpoint, fd/custom I/O, mount options, low-level ops, userdata, owner, connection info, request and interrupt lists, locks, initialization and destroy state, thread-loop synchronization, buffer sizing, synchronous FUSE_INIT state, io_uring pool settings, timeout thread pointer, and desired connection feature masks.

`struct fuse_chan` is a reference-counted wrapper around a FUSE device fd used by clone-fd multithreaded loops. `struct fuse_module` tracks high-level stack modules, their factories, dynamic-library ownership, and reference counts. `struct fuse_loop_config` is the ABI-safe internal v2 loop configuration with a `version_id`, `clone_fd`, `max_idle_threads`, and `max_threads`.

Function declarations cover channel reference management, mount backend calls, reply sending and request freeing, CUSE initialization, thread creation, buffer freeing, internal receive/process functions, high-level constructor and multithread loop ABI entry points, loop config verification, and daemonization-state detection.

## Control Flow

This header has no executable control flow, but it defines the shared data model used by the core control paths. Session loops receive requests into `struct fuse_buf`, associate them with `struct fuse_req`, and process them through `fuse_session_process_buf_internal`. Multithreaded loops create and release `struct fuse_chan` instances when clone-fd mode is enabled. High-level creation in `fuse.c` calls `fuse_session_new_versioned` and relies on `struct fuse_session` fields for synchronization and errors.

The private loop config uses `version_id` to distinguish the newer internal layout from the older public `struct fuse_loop_config_v1`, whose first field overlapped with `clone_fd`. `fuse_loop_cfg_verify` enforces this before `fuse_session_loop_mt_312` consumes the structure.

## State And Persistence Behavior

All structures describe in-memory runtime state. There is no disk persistence. State with broad behavioral impact includes request reference counts, session exit/error flags, `got_init`, feature masks, buffer size, multithread exit semaphore/lock, sync-init wakeup fields, io_uring pool pointer, timeout thread pointer, module reference counts, and channel fd reference counts.

The `mountpoint` and `bufsize` fields are atomic because they can be read or updated across session-management paths. `mt_exited`, `uring.pool`, and `timeout_thread` coordinate asynchronous loop and teardown behavior across threads.

## Dependencies And Integration Points

The header includes `fuse.h`, `fuse_lowlevel.h`, and `util.h`, plus pthreads, semaphores, atomics, fixed-width integers, and booleans. It is included by the session loops, high-level API implementation, low-level implementation, mount code, CUSE code, buffer code, io_uring support, and daemonization integration.

It also defines constants `FUSE_DEFAULT_MAX_PAGES_LIMIT`, `FUSE_DEFAULT_MAX_PAGES_PER_REQ`, and `FUSE_BUFFER_HEADER_SIZE`, which influence buffer sizing and kernel request capacity assumptions.

## Risks And Edge Cases

As a private ABI coordination header, layout changes can break implementation files that access fields directly. `struct fuse_session` is especially sensitive because it combines mount state, request queues, synchronization primitives, feature negotiation, io_uring state, and sync-init state. The private `struct fuse_loop_config` is guarded by `version_id`; callers passing an older public layout to the new API should receive `-EINVAL` instead of being misinterpreted.

`MIN` is defined as a GNU statement-expression macro using `typeof`, so this private header assumes GNU C extensions. Channel `ctr` updates depend on callers holding `struct fuse_chan.lock` as implemented in `fuse_loop_mt.c`; misuse outside those helpers could race with fd close and free.

## Test Signals

Compile-time tests should cover supported `FUSE_USE_VERSION` boundaries, especially the visibility and compatibility of `struct fuse_loop_config` versus `struct fuse_loop_config_v1`. Runtime tests should exercise request reference counting, channel get/put close behavior, session receive/process behavior with and without custom I/O, sync-init fields, io_uring shutdown interactions, and multithread loop config validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_log.c -->
# sources/user-network-fs/libfuse/lib/fuse_log.c

## Purpose

`fuse_log.c` implements libfuse's small logging abstraction. It provides a default stderr logger, an optional syslog backend switch, and a public hook for applications or tests to replace the log sink.

## Important APIs, Types, And Functions

The file defines file-global `to_syslog` and `log_func` state. `default_log_func(enum fuse_log_level level, const char *fmt, va_list ap)` writes to `vsyslog` when syslog mode is enabled and otherwise writes to `stderr` with `vfprintf`.

Public functions are `fuse_set_log_func(fuse_log_func_t func)`, `fuse_log(enum fuse_log_level level, const char *fmt, ...)`, `fuse_log_enable_syslog(const char *ident, int option, int facility)`, and `fuse_log_close_syslog(void)`.

## Control Flow

`fuse_set_log_func` installs the provided callback, falling back to `default_log_func` when passed `NULL`. `fuse_log` creates a `va_list`, delegates to the current callback, and ends the list. `fuse_log_enable_syslog` sets `to_syslog` and calls `openlog`; `fuse_log_close_syslog` calls `closelog`.

## State And Persistence Behavior

State is process-global and in-memory. The current log function and syslog toggle affect every libfuse component using `fuse_log`. There is no file persistence in this implementation, though syslog mode emits to the host's syslog facility.

## Dependencies And Integration Points

The file includes `fuse_log.h` and depends on `<stdio.h>`, `<stdbool.h>`, `<syslog.h>`, and `<stdarg.h>`. It is used by most libfuse implementation files for diagnostics, including allocation failures, option warnings, clone-fd failures, module load failures, and debug traces in `fuse.c`.

## Risks And Edge Cases

There is no locking around `log_func` or `to_syslog`, so changing the log function or enabling syslog concurrently with logging is a data race in multithreaded filesystems. `fuse_log_close_syslog` does not reset `to_syslog`, so subsequent default logs still call `vsyslog` after `closelog`; many libc implementations tolerate this by reopening implicitly, but behavior is backend-dependent.

The defined `MAX_SYSLOG_LINE_LEN` is unused, so this implementation does not enforce a syslog line length cap. Custom log callbacks receive the live `va_list` and must consume it immediately.

## Test Signals

Tests should install a custom callback and assert that `fuse_log` forwards level, format, and arguments. A reset test should pass `NULL` to restore the default logger. Syslog tests can mock or intercept `openlog`, `vsyslog`, and `closelog`, and concurrency tests should document or expose the absence of synchronization around global logger state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_loop.c -->
# sources/user-network-fs/libfuse/lib/fuse_loop.c

## Purpose

`fuse_loop.c` implements the single-threaded low-level session loop, `fuse_session_loop`. It repeatedly receives one request buffer from a `struct fuse_session`, processes it synchronously, and exits when the session is marked exited, receive returns EOF/error, or a session error is recorded.

## Important APIs, Types, And Functions

The only function defined is `int fuse_session_loop(struct fuse_session *se)`. It uses `struct fuse_buf`, `fuse_session_exited`, `fuse_session_receive_buf_internal`, `fuse_session_process_buf`, `fuse_buf_free`, and, when configured, `fuse_uring_stop`.

## Control Flow

The function initializes a reusable `struct fuse_buf` with `mem = NULL`, then loops while `!fuse_session_exited(se)`. Each iteration calls `fuse_session_receive_buf_internal(se, &fbuf, NULL)`. `-EINTR` is ignored and retried. Nonpositive results break the loop. Positive results are processed by `fuse_session_process_buf(se, &fbuf)`.

After the loop, the receive buffer is freed. A positive last receive length is normalized to success (`0`). If `se->error` is nonzero, that value overrides the result. If the session has an io_uring pool, `fuse_uring_stop(se)` is called before returning.

## State And Persistence Behavior

The loop maintains only the reusable request buffer and return code locally. It mutates session state indirectly through receive and process calls; those paths can allocate requests, update request lists, dispatch operations, set `se->error`, or mark the session exited. There is no persistence beyond process memory and the mounted FUSE device interaction.

## Dependencies And Integration Points

The file includes `fuse_config.h`, `fuse_lowlevel.h`, `fuse_i.h`, and `fuse_uring_i.h`. It is the low-level loop used directly by low-level filesystems and indirectly by high-level `fuse_loop` when remembered-node cleanup is not needed.

It expects the session to have been created and mounted already, and it reads from the session's main fd through `fuse_session_receive_buf_internal`. For high-level filesystems, request processing eventually dispatches into `fuse_path_ops` from `fuse.c`.

## Risks And Edge Cases

The loop is strictly single-threaded, so a blocking callback prevents all other requests from being processed. It treats `-EINTR` during receive as harmless, but any other negative receive result exits. Since it calls `fuse_session_process_buf` rather than the internal channel-aware variant, there is no cloned channel passed to processing.

The function stops io_uring only after the main loop exits. If processing code sets `se->error`, that session error overrides a normal receive exit, which is useful but can obscure the original receive result.

## Test Signals

Tests should use a fake or instrumented session receive path to cover EINTR retry, positive receive and process dispatch, zero/negative termination, positive-length normalization to zero, `se->error` override, and io_uring stop on exit. Integration tests should compare behavior with `fuse_session_loop_mt_312` under the same mounted low-level filesystem.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_loop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_loop_mt.c -->
# sources/user-network-fs/libfuse/lib/fuse_loop_mt.c

## Purpose

`fuse_loop_mt.c` implements libfuse's multithreaded low-level session loop and the private loop-configuration API introduced for FUSE 3.12. It dynamically creates worker threads to receive and process kernel requests, optionally clones `/dev/fuse` file descriptors per worker, and preserves ABI compatibility with older `fuse_session_loop_mt` signatures.

## Important APIs, Types, And Functions

Private runtime types are `struct fuse_worker`, which stores list links, pthread id, per-thread `fuse_buf`, optional cloned `fuse_chan`, and parent `fuse_mt`; and `struct fuse_mt`, which stores worker counts, available-worker count, session pointer, sentinel list node, error, clone-fd flag, idle-thread cap, and max-thread cap.

Channel APIs implemented here are `fuse_chan_get` and `fuse_chan_put`, backed by private `fuse_chan_new`. Thread creation is centralized in `fuse_start_thread`, which also applies `FUSE_THREAD_STACK` and blocks termination-related signals in worker threads during `pthread_create`.

Loop entry points are `fuse_session_loop_mt_312`, `fuse_session_loop_mt_32`, and `fuse_session_loop_mt_31`, exported with symbol versions for FUSE 3.12, 3.2, and 3.0 compatibility. Loop-config APIs are `fuse_loop_cfg_create`, `fuse_loop_cfg_destroy`, `fuse_loop_cfg_verify`, `fuse_loop_cfg_convert`, `fuse_loop_cfg_set_idle_threads`, `fuse_loop_cfg_set_max_threads`, and `fuse_loop_cfg_set_clone_fd`.

## Control Flow

`fuse_session_loop_mt_312` verifies or creates a config, initializes `struct fuse_mt`, starts the first worker while holding `se->mt_lock`, then waits on `se->mt_finish` until `fuse_session_exited(se)` is true. When the session exits, it cancels all workers, joins them through `fuse_join_worker`, records `mt.error`, stops io_uring if present, applies `se->error` override, destroys an auto-created config, and returns.

Each worker runs `fuse_do_work`. It enables cancellation around `fuse_session_receive_buf_internal`, retries `-EINTR`, exits on nonpositive results, and on negative receive errors marks the session exited and records `mt->error`. For a valid request, it locks `se->mt_lock`, detects `FUSE_FORGET` and `FUSE_BATCH_FORGET` requests as a special no-scale-up case, decrements available worker count for non-forget work, and starts another worker when no workers are available, `numworker < max_threads`, and the session has received init. It then processes the buffer with `fuse_session_process_buf_internal` and restores availability.

Idle worker reaping occurs after processing when `max_idle != -1`, available workers exceed the configured idle cap, and more than one worker exists. The worker removes itself from the list, decrements counts, detaches itself, frees its buffer, drops its channel, and exits.

Clone-fd flow starts in `fuse_loop_start_thread`. If `clone_fd` is enabled, it calls `fuse_clone_chan`, which uses either custom `se->io->clone_fd` or `fuse_clone_chan_fd_default`. The default path opens `/dev/fuse`, sets close-on-exec if needed, and issues `FUSE_DEV_IOC_CLONE` with the session master fd. If cloning fails once, the loop logs and disables further clone-fd attempts.

Compatibility entry points allocate a new private config and convert older inputs. `fuse_loop_cfg_convert` maps v1 `max_idle_threads` to both `max_threads` and `max_idle_threads` to preserve older pool-cap behavior, then transfers `clone_fd`.

## State And Persistence Behavior

State is runtime-only. Worker list membership, `numworker`, `numavail`, `mt.error`, session exit state, and the per-worker buffers/channels are mutated under `se->mt_lock` except for receive/process work outside the lock. `se->mt_finish` is a semaphore used to wake the controller when workers leave the receive loop.

Channels own cloned fds and close them when their reference count reaches zero. Worker buffers are retained per worker so cancellation cleanup can free memory correctly. The environment variable `FUSE_THREAD_STACK` influences pthread stack size but is not persisted.

## Dependencies And Integration Points

The file includes low-level, kernel, misc, io_uring, util, and internal headers. It depends on pthreads, signals, semaphores, ioctl, `/dev/fuse`, `FUSE_DEV_IOC_CLONE`, `fcntl`, and close-on-exec behavior. It integrates with `struct fuse_session` fields declared in `fuse_i.h`, especially `mt_lock`, `mt_finish`, `got_init`, `error`, `io`, `fd`, and `uring.pool`.

High-level `fuse_loop_mt_312` in `fuse.c` calls this session loop after starting the high-level cleanup thread. Low-level users can call the session loop directly.

## Risks And Edge Cases

The worker-scaling algorithm intentionally ignores FORGET bursts when deciding to spawn more threads. This prevents thread explosions but can delay scaling if mixed workloads are misclassified or if buffers are fd-backed and opcode inspection is unavailable.

`max_threads` can be set to zero by the public setter even though the worker-spawn condition requires `numworker < max_threads`; because the first worker is started before demand scaling, zero effectively prevents additional workers after the initial one. Invalid extremely large idle-thread values are rejected in `fuse_loop_cfg_set_idle_threads`, but `fuse_loop_cfg_set_max_threads` does not cap against `FUSE_LOOP_MT_MAX_THREADS`.

Thread cancellation is used for shutdown. Correct cleanup relies on cancellation being enabled only during receive and disabled around processing and list manipulation. If a worker exits through the idle-reap branch it detaches itself and frees its own structure, so list/count locking must remain correct.

`fuse_chan_get` asserts `ch->ctr > 0` before locking, which is not a synchronization guarantee by itself. Callers need a valid channel reference before calling it. Clone-fd fallback logs an error and continues without clone-fd, which may hide a performance or isolation regression unless tests assert the fallback path.

## Test Signals

Tests should cover config creation defaults, version-id verification, v1 conversion semantics, setter warnings and edge values, custom and default clone-fd success/failure, environment-controlled thread stack parsing, signal mask restoration after thread creation, worker growth up to `max_threads`, no growth on FORGET-only bursts, idle worker reaping, receive errors setting session exit and return errors, cancellation and join cleanup, channel reference-count close behavior, and io_uring stop on exit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_loop_mt.c -->
