# Group Research: subset-b-009684

This grouped report covers the requested mergerfs vendored libfuse sources and the vendored moodycamel blocking queue header. Each file section is bounded by reconciliation markers for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse.cpp

## Purpose
`fuse.cpp` is mergerfs' high-level FUSE adapter. It keeps the in-memory node namespace, translates kernel low-level requests into `fuse_operations` path/file-handle callbacks, maintains lookup/open/reference state, formats directory data through `fuse_dirents_t`, and wires the high-level operation table into the low-level dispatch layer.

## Important APIs, Types, and Functions
The central static `struct fuse f` holds the single active session, operation table, name/id hash tables, node id generator, global mutex, and path lock queue. `node_table`, `nodeid_gen_t`, `lock_queue_element`, and `fuse_dh` support node lookup, path locking, and directory-handle caching. Public entry points include `fuse_new`, `fuse_destroy`, `fuse_get_session`, `fuse_exit`, `fuse_exited`, `fuse_notify_poll`, `fuse_invalidate_all_nodes`, `fuse_gc`, `fuse_gc1`, `fuse_populate_maintenance_thread`, `fuse_passthrough_open`, and `fuse_passthrough_close`.

## Control Flow
`fuse_new` copies the caller's `fuse_operations`, creates a low-level session with `fuse_path_ops`, initializes hash tables, and installs root node id `FUSE_ROOT_ID`. Low-level requests enter one of the `fuse_lib_*` handlers, resolve node ids to relative paths with `get_path*`, call the corresponding high-level operation, update node/cache state when needed, and reply through `fuse_reply_*`. Mutating operations such as unlink, rmdir, and rename use write path locks and update name-table membership. Create/tmpfile allocate provisional nodes to provide a node id to passthrough-aware backends, then either remember/open the node after success or forget it on failure.

## State and Persistence
All node state is process-local. The id/name hash tables track node ids, parents, names, lookup counts, open counts, remembered status, and `stat_crc32b`. Nothing is persisted across process restart. `remember_nodes` can pin lookups. `open_auto_cache` compares stat fingerprints and sets `keep_cache` when a file is unchanged across opens. Maintenance jobs periodically GC pooled nodes/message buffers and optionally append metrics under `/tmp/mergerfs.<pid>.info`.

## Dependencies and Integration Points
This file integrates with `fuse_lowlevel.cpp` through `fuse_path_ops`, with `node.cpp`/`node.hpp` for pooled `node_t`, with `fuse_dirents.cpp` for readdir buffers, with `fuse_msgbuf.cpp` for read buffers, with `fuse_req.cpp` for request allocation, with `fuse_cfg` for runtime policy, and with kernel passthrough ioctls on `/dev/fuse`.

## Risks
The file is concurrency sensitive: path locks, node refcounts, `open_count`, and queued condition variables must stay balanced. Incorrect node unlink/rename ordering can produce stale paths or use-after-free. `find_node` provisional nodes need cleanup on every failed create/tmpfile path. `free_path_and_update_stat` must not update a node after kernel forget. Directory handles rely on a lock barrier before destruction.

## Test Signals
Exercise lookup/forget churn, open-unlink-release, rename over existing nodes, interrupted create/open replies, readdir/readdirplus with repeated offsets, auto-cache invalidation after stat changes, passthrough open/close failure paths, and maintenance GC under active operations. Race tests should stress parallel read/process threads with unlink, rename, forget, and releasedir.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_cfg.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_cfg.cpp

## Purpose
`fuse_cfg.cpp` defines the global `fuse_cfg` instance and implements small accessors for configuration values that need validation or synchronized log-file state.

## Important APIs, Types, and Functions
`fuse_cfg_t::valid_uid`, `valid_gid`, and `valid_umask` compare configured values against invalid sentinels from `fuse_cfg.hpp`. `log_file()` and `log_file(std::shared_ptr<FILE>)` read/write the active log file under `_log_mutex`. `log_filepath()` and `log_filepath(const std::string&)` similarly manage a shared string path.

## Control Flow
Configuration is read directly by the rest of libfuse and mergerfs. This implementation only guards log metadata: readers take a shared lock and writers take a unique lock. The filepath setter allocates a new shared string before acquiring the mutex, then atomically swaps the pointer while locked.

## State and Persistence
The only state in this file is the process-global `fuse_cfg` object and its shared pointers. Values are not persisted here; they are populated by mergerfs startup/config parsing elsewhere. The log file pointer and path are reference-counted so readers can hold stable objects after the lock is released.

## Dependencies and Integration Points
The file includes `fuse_cfg.hpp` and uses `<mutex>` plus the shared mutex declared in the header. Consumers include `fuse.cpp`, `fuse_loop.cpp`, `fuse_lowlevel.cpp`, debug logging, and helper code that applies uid/gid/umask, FUSE init caps, thread counts, and log paths.

## Risks
The global object is mutable and used broadly, so initialization order matters. The FILE pointer itself is not made thread-safe by the shared pointer; callers still need to coordinate writes at the logging layer. Changes to invalid sentinel values must stay consistent with the validation methods.

## Test Signals
Check default invalid uid/gid/umask behavior, setting explicit uid/gid/umask, concurrent log path/file readers while replacing the path/file, and startup paths where no log file is configured.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_cfg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_dirents.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_dirents.cpp

## Purpose
`fuse_dirents.cpp` builds packed FUSE directory-entry buffers and an offset index used by the high-level readdir cache in `fuse.cpp`.

## Important APIs, Types, and Functions
The exported API is `fuse_dirents_init`, `fuse_dirents_add` for POSIX `dirent`, `fuse_dirents_add` for mergerfs `fs::dirent64`, `fuse_dirents_reset`, and `fuse_dirents_free`. Internal helpers calculate aligned `fuse_dirent_t` sizes, grow the kvec-backed byte buffer, and allocate space for the next entry.

## Control Flow
Initialization allocates a 32 KiB data buffer and an offset vector with an initial zero entry. Each add operation computes aligned entry size, resizes the data vector when needed, appends an offset entry, fills inode/name/type fields, and copies the name bytes without appending a string terminator. `fuse_lib_readdir` later uses the offset vector as the FUSE directory offset space.

## State and Persistence
The `fuse_dirents_t` object owns two dynamic kvec buffers: raw packed dirent bytes and `uint32_t` offsets. State is per open directory handle and is destroyed on releasedir. It is not persistent and must be protected by the directory handle lock in the caller.

## Dependencies and Integration Points
This file depends on FUSE dirent structs, `kvec.h`, `fs_dirent64.hpp`, and C dirent/stat headers. `fuse.cpp` owns the lifecycle in `fuse_lib_opendir`, repopulates it through filesystem `readdir`/`readdir_plus`, and slices it for replies.

## Risks
Offsets are stored as `uint32_t`, so extremely large directory buffers risk truncation. Name length correctness is delegated to callers. Allocation failure must be propagated or the directory stream will return ENOMEM. Alignment must match kernel expectations for `fuse_dirent_t`.

## Test Signals
Test empty directories, many entries beyond 32 KiB, long names, `dirent` and `dirent64` inputs, reset/reuse after repeated offset-zero reads, and ENOMEM simulation around buffer growth.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_dirents.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_i.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_i.hpp

## Purpose
`fuse_i.hpp` is the private internal header for the vendored FUSE implementation. It defines the simplified session shape and internal notification/request wiring shared by the loop, session, and low-level dispatch files.

## Important APIs, Types, and Functions
`struct fuse_session` contains callback pointers for receiving and processing buffers, a destroy callback, the low-level data pointer, atomic exit state, the active `/dev/fuse` fd, buffer size, and cloned read fds. `struct fuse_notify_req` models an intrusive pending-notify list with a unique id and reply callback. Internal declarations include `fuse_session_setup_read_fds`, `fuse_session_read_fd`, and `fuse_lowlevel_new_common`.

## Control Flow
The library collapses libfuse's former session/channel hierarchy for mergerfs' single-mount model. `fuse_session.cpp` fills and owns this structure, `fuse_loop.cpp` reads from either the main or cloned fds, and `fuse_lowlevel.cpp` installs receive/process callbacks and notification state.

## State and Persistence
Session state is in-memory and process-local. `exited` is atomic so signal handlers and worker threads can coordinate shutdown. `clone_fds` are owned by the session and closed when the session fd changes or the session is destroyed.

## Dependencies and Integration Points
The header includes public FUSE headers plus `fuse_msgbuf_t.h`, C++ `<atomic>`, and `<vector>`. It is a private bridge between high-level setup, low-level kernel protocol handling, signal handling, and the threaded loop.

## Risks
Because callback pointers are cast from `void *` in `fuse_session_new`, signatures must remain exactly compatible. Any future multi-mount support would require undoing the simplified single-session globals. Atomic exit protects the flag but not the rest of the session fields, so fd changes must remain lifecycle-bound.

## Test Signals
Build tests should catch signature drift. Runtime tests should cover single-thread shared-fd reads, multi-read-thread cloned-fd setup/fallback, signal-triggered exit, and session destroy after failed mount/setup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_i.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_loop.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_loop.cpp

## Purpose
`fuse_loop.cpp` implements the multi-threaded FUSE read/process loop used by mergerfs. It separates request reads from optional request processing workers, supports cloned `/dev/fuse` fds, applies CPU pinning policies, and starts/stops maintenance jobs around the loop.

## Important APIs, Types, and Functions
`fuse_session_loop_mt` is the main loop. `fuse_loop_mt` wraps it for `struct fuse` using `fuse_cfg`. `AsyncWorker` reads requests and enqueues processing lambdas to a process thread pool. `SyncWorker` reads and processes inline. `_calculate_thread_counts` interprets raw configuration values, and `_retriable_receive_error` masks transient receive errors.

## Control Flow
The loop computes read/process counts, optionally creates a processing `ThreadPool`, asks the session to clone fds for read threads, starts read workers, captures pthread ids, pins them, logs the effective configuration, then waits on a semaphore until a worker exits and marks the session exited. On shutdown it cancels read threads and destroys thread pools. `fuse_loop_mt` surrounds this with `MaintenanceThread::setup`, `fuse_populate_maintenance_thread`, and `MaintenanceThread::stop`.

## State and Persistence
Loop state is transient: thread pools, semaphores, msgbuf allocations, and session exit status. Message buffers are allocated per received request and freed after processing. The maintenance thread is process-local and periodic.

## Dependencies and Integration Points
It depends on `thread_pool.hpp`, `pin_threads`, `maintenance_thread`, `fuse_i`, `fuse_lowlevel`, `fuse_msgbuf`, `fuse_cfg`, `fmt`, syslog, pthread cancellation, and POSIX semaphores. It calls session receive/process callbacks installed by `fuse_lowlevel.cpp`.

## Risks
Thread-count calculation must avoid zero or negative queue depths. Async mode requires every enqueued closure to free its msgbuf exactly once. Cancellation is enabled only during blocking reads; changing that can introduce leaks or inconsistent callback execution. A read worker exiting for one fatal fd error exits the whole session.

## Test Signals
Exercise configured thread counts `0`, negative divisors, positive values, process-thread disabled mode, process-thread enabled mode, cloned fd success and fallback, EINTR/EAGAIN/ENOENT receive retry, ENODEV shutdown, and pinning strings from `pin_threads.cpp`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_loop.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_lowlevel.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_lowlevel.cpp

## Purpose
`fuse_lowlevel.cpp` is the kernel protocol layer. It reads raw FUSE messages, allocates request objects, dispatches opcodes to low-level handlers, performs the FUSE INIT negotiation, marshals all replies, and sends kernel notify messages.

## Important APIs, Types, and Functions
`struct fuse_ll` stores low-level ops, owner uid, negotiated `fuse_conn_info_t`, mutex, init/destroy flags, and pending notify list. Reply APIs include `fuse_reply_err`, `fuse_reply_none`, `fuse_reply_entry`, `fuse_reply_create`, `fuse_reply_attr`, `fuse_reply_statx`, `fuse_reply_open`, `fuse_reply_write`, `fuse_reply_buf`, `fuse_reply_data`, `fuse_reply_statfs`, `fuse_reply_xattr`, `fuse_reply_ioctl`, and `fuse_reply_poll`. Notify APIs include poll, invalidate inode/entry, delete, and retrieve. `fuse_lowlevel_new_common` creates the session.

## Control Flow
Before INIT, the session process callback is `fuse_ll_buf_process_read_init`, which rejects non-INIT messages. `do_init` parses kernel capabilities, calls the high-level init callback, intersects requested capabilities with supported ones, configures max pages/write size/background limits, updates message-buffer size, and replies with the ABI-specific init struct size. After INIT, `fuse_ll_buf_process_read` builds a `fuse_req_t`, copies header context, validates the opcode against `fuse_ll_funcs`, and invokes the mapped operation. Reply helpers write a `fuse_out_header` plus payload through `writev` and free the request.

## State and Persistence
Negotiated connection state persists for the process lifetime. Pending notification requests are kept in an intrusive list until the kernel replies. There is no durable storage. Request objects are pooled by `fuse_req.cpp`; message buffers are managed by the loop.

## Dependencies and Integration Points
This file depends on kernel ABI structs from `fuse_kernel.h`, request/session internals from `fuse_i.hpp`, pooled message/request allocation, debug/syslog helpers, `fuse_cfg`, and POSIX `read`/`writev`.

## Risks
The FUSE ABI is size- and version-sensitive; wrong compatibility sizes or capability flags can break mounts. Every reply path must free the request exactly once. `fuse_send_msg` assumes full `writev` success and does not retry partial writes. Notify unique ids and list operations require correct locking.

## Test Signals
Test INIT with old/new minor versions, capability negotiation, max_pages resizing, unsupported opcode ENOSYS, short read EIO, debug logging, every reply helper's payload size, ioctl retry on 32-bit compat paths, notify poll/inval/delete/retrieve, and destroy called exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_lowlevel.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_msgbuf.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_msgbuf.cpp

## Purpose
`fuse_msgbuf.cpp` manages page-aligned buffers used to read requests from `/dev/fuse` and reply with page-aligned data.

## Important APIs, Types, and Functions
Exports include `msgbuf_alloc`, `msgbuf_alloc_page_aligned`, `msgbuf_free`, `msgbuf_get_bufsize`, `msgbuf_get_pagesize`, `msgbuf_set_bufsize`, `msgbuf_alloc_count`, `msgbuf_gc`, and `msgbuf_clear`. `PageAlignedAllocator` uses `posix_memalign`; `ShouldPoolMsgbuf` keeps only buffers matching current size.

## Control Flow
A constructor queries system page size, asserts the write-header alignment fits within a page, and initializes the default buffer size. Allocations come from an `ObjPool` sized to `g_bufsize`. `msgbuf_alloc` returns a buffer whose `mem` pointer is offset so `fuse_in_header` and `fuse_write_in` can be prepended/aligned for write requests. `msgbuf_alloc_page_aligned` returns a page-aligned data region. Changing max pages updates `g_bufsize` and clears the pool.

## State and Persistence
Global page size, buffer size, and object pool state persist for the process. Buffers are not durable and are recycled until GC/clear or size changes.

## Dependencies and Integration Points
The file depends on `fuse_kernel.h`, `fuse_msgbuf.hpp`, `objpool.hpp`, `fatal.hpp`, and POSIX memory/page APIs. It is used by `fuse_loop.cpp` for request reads and by `fuse.cpp` for read replies.

## Risks
`g_bufsize` is global and pool clearing during active use would be unsafe if called outside init/maintenance expectations. Alignment assumptions are critical for kernel read/write layout. Allocation failure must propagate to avoid null dereferences.

## Test Signals
Verify page size discovery, default and negotiated max-page sizes, write-aligned and page-aligned pointer offsets, pool reuse count, pool clearing after size changes, and ENOMEM handling in read paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_msgbuf.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_opt.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_opt.cpp

## Purpose
`fuse_opt.cpp` implements libfuse-style command-line and `-o` option parsing for the vendored library.

## Important APIs, Types, and Functions
Public functions are `fuse_opt_free_args`, `fuse_opt_add_arg`, `fuse_opt_insert_arg`, `fuse_opt_add_opt`, `fuse_opt_add_opt_escaped`, `fuse_opt_match`, and `fuse_opt_parse`. `fuse_opt_context` tracks input args, parsed output args, accumulated comma options, option templates, and callback state.

## Control Flow
Parsing copies argv[0], scans each argument, handles `-ofoo,bar` and `-o foo,bar` as option groups, honors `--`, matches templates from `struct fuse_opt`, writes values into offsets or calls the user callback, and reinserts accumulated options as `-o <opts>`. Option groups understand comma and backslash escaping. Template parameters support `%s` strings and integer `sscanf` formats.

## State and Persistence
No persistent state exists. The parser reallocates `fuse_args` ownership: on success, the caller receives a newly allocated argv array and the previous one is freed through the temporary context cleanup. Accumulated options are heap strings.

## Dependencies and Integration Points
This parser is used by `helper.cpp`, `mount_generic.h`, and `mount_bsd.h` to separate mount/helper/kernel options. It depends only on `fuse_opt.h` and libc allocation/string APIs.

## Risks
Ownership is subtle: callers must use `fuse_opt_free_args` on allocated outputs. `%s` option targets are overwritten without freeing previous values in `process_opt_param`, so templates should not match the same field repeatedly unless callers handle it. Escaping behavior must match mount helper expectations.

## Test Signals
Test non-option mountpoints, `--`, `-o` with escaped commas/backslashes, templates with `=` and separated space parameters, keep/discard/proc callback return values, multiple matches, allocation failures, and invalid integer parameters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_opt.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_req.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_req.cpp

## Purpose
`fuse_req.cpp` provides pooled allocation for low-level request objects.

## Important APIs, Types, and Functions
The file exports `fuse_req_alloc()` and `fuse_req_free(fuse_req_t*)`, backed by a static `ObjPool<fuse_req_t> g_pool`.

## Control Flow
`fuse_lowlevel.cpp` calls `fuse_req_alloc` after reading a kernel request and fills the returned structure with context, connection, session, fd, and ioctl state. Reply helpers call `fuse_req_free` after writing the response, while no-reply operations such as forget call `fuse_reply_none`, which also frees the request.

## State and Persistence
The object pool is process-local and persists for the lifetime of the library. Requests are transient and must not escape after a reply. There is no persistent storage.

## Dependencies and Integration Points
It includes `fuse_req.hpp` and `objpool.hpp`. Its correctness is tightly coupled to reply ownership in `fuse_lowlevel.cpp` and every `fuse_lib_*` handler that must produce exactly one reply or no-reply free.

## Risks
Leaks occur if a handler returns without replying. Double frees occur if a handler replies twice or calls `fuse_req_free` after a reply helper. Thread safety depends on `ObjPool` behavior under the read/process thread model.

## Test Signals
Use request storm tests, unsupported opcode paths, forget/no-reply paths, ENOMEM allocation failure, and sanitizers to catch leaks or double frees around interrupted open/create replies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_req.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_session.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_session.cpp

## Purpose
`fuse_session.cpp` implements the simplified single-mount session lifecycle and fd management.

## Important APIs, Types, and Functions
It defines `fuse_session_new`, `fuse_session_destroy`, `fuse_session_reset`, `fuse_session_exited`, `fuse_session_exit`, `fuse_session_data`, `fuse_session_clearfd`, `fuse_session_setfd`, `fuse_session_setup_read_fds`, `fuse_session_read_fd`, `fuse_session_setbufsize`, `fuse_session_fd`, and `fuse_session_bufsize`. Internal helpers clone `/dev/fuse` fds via `FUSE_DEV_IOC_CLONE` and close clone fds.

## Control Flow
`fuse_session_new` allocates a C++ `fuse_session`, stores callbacks and low-level data, and initializes fd to `-1`. Destroy invokes the low-level destroy callback, closes clone fds and the main fd, then deletes the session. Multi-read setup attempts to open `/dev/fuse` and clone the main fd for each read worker beyond the first; on any clone failure it closes all clones, logs a warning, and falls back to the shared fd.

## State and Persistence
The session owns the main fd, cloned fds, buffer size, callback pointers, low-level data pointer, and atomic exit flag. State is in-memory and tied to mount lifetime.

## Dependencies and Integration Points
It depends on `fuse_i.hpp`, kernel ioctl constants, syslog, and POSIX fd APIs. `helper.cpp`/`fuse.cpp` set fd and bufsize; `fuse_loop.cpp` queries read fds; signal handling toggles exit state.

## Risks
Fd ownership is delicate: `fuse_session_clearfd` transfers the main fd to unmount code and closes clones. Cloned-fd support depends on kernel support for `FUSE_DEV_IOC_CLONE`. Callback casts from `void *` require exact function signatures.

## Test Signals
Test session create/destroy, setfd replacing clones, clearfd transfer, clone success/failure fallback, multiple read thread fd selection, signal/session exit, and destroy after partial setup failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_session.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_signals.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_signals.cpp

## Purpose
`fuse_signals.cpp` installs and removes process signal handlers that request FUSE session shutdown.

## Important APIs, Types, and Functions
Public functions are `fuse_set_signal_handlers(struct fuse_session*)` and `fuse_remove_signal_handlers(struct fuse_session*)`. A static atomic `g_fuse_instance` points to the current session. `exit_handler` calls `fuse_session_exit`. `set_one_signal_handler` conditionally sets or restores handlers.

## Control Flow
Setup installs `exit_handler` for SIGINT, SIGTERM, and SIGQUIT, ignores SIGPIPE, then stores the session pointer. Removal restores default handlers for signals that still point to the installed handlers and clears the atomic if it matches the session.

## State and Persistence
Only the process-global atomic session pointer persists. Handlers affect process-wide signal disposition, not just the FUSE instance.

## Dependencies and Integration Points
This file depends on `fuse_lowlevel.h`, atomics, and POSIX `sigaction`. `helper.cpp` installs handlers after mount/daemonize and removes them during teardown. `fuse_loop.cpp` observes session exit.

## Risks
Signal disposition is process-global, so embedding this library in a process with its own handlers can conflict. The conditional restore logic only resets handlers if they match expected values; external handler changes may remain. The handler only toggles an atomic/session flag, which is appropriate for async-signal safety.

## Test Signals
Test SIGINT/SIGTERM/SIGQUIT shutdown, SIGPIPE ignored behavior, handler removal after normal teardown, removal with wrong session pointer warning, and coexistence when a signal had a non-default handler before setup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_signals.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/helper.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/helper.cpp

## Purpose
`helper.cpp` provides libfuse-compatible high-level setup, mount, daemonize, command-line parsing, main loop entry, and teardown functions for mergerfs.

## Important APIs, Types, and Functions
Key exported functions are `fuse_parse_cmdline`, `fuse_daemonize`, `fuse_mount`, `fuse_unmount`, `fuse_setup`, `fuse_teardown`, and `fuse_main`. Internal helpers parse `-f`, mountpoint, fsname/subtype options, add default subtype, recover from disconnected mountpoints, call `fuse_kern_mount`, and centralize setup/teardown.

## Control Flow
`fuse_parse_cmdline` uses `fuse_opt_parse` to extract foreground and mountpoint while preserving relevant options. `fuse_mount_common` ensures fds 0-2 are open, calls platform `fuse_kern_mount`, and computes buffer size. `fuse_setup_common` parses options, mounts, creates `fuse_new`, daemonizes unless foreground, installs signal handlers, and returns the active `struct fuse`. `fuse_main` runs `fuse_loop_mt`, then tears down.

## State and Persistence
The helper owns the allocated mountpoint string, mount fd during setup, and process daemonization state. It does not persist configuration; it mutates process session/cwd/stdio during daemonization.

## Dependencies and Integration Points
It integrates `fuse_opt`, `fuse_lowlevel`, platform mount helpers, signal handlers, `fuse.cpp`, and the threaded loop. It is the main compatibility surface used by mergerfs startup.

## Risks
Daemonization changes cwd and stdio and uses a pipe to let the parent exit after initialization. Error paths must unmount and free mountpoint exactly once. Mountpoint realpath recovery may unmount disconnected FUSE mounts. Adding default subtype changes mount options based on argv[0].

## Test Signals
Test foreground/background startup, invalid/multiple mountpoints, disconnected mountpoint recovery, mount failure cleanup, fuse_new failure cleanup, signal setup failure, teardown after clearfd, and `fuse_main` return code mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/helper.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/maintenance_thread.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/maintenance_thread.cpp

## Purpose
`maintenance_thread.cpp` implements a small periodic job runner used by libfuse for GC and optional metrics.

## Important APIs, Types, and Functions
`MaintenanceThread::setup` starts the thread, `push_job` appends a `std::function<void(u64)>`, and `stop` cancels and joins it. `_thread_loop` names the thread `fuse.maint`, increments a minute counter, and runs all registered functions under a mutex.

## Control Flow
Setup creates one pthread. The loop disables cancellation while holding the job mutex and invoking functions, enables cancellation before sleeping, increments the count each minute, and repeats forever. Stop cancels the sleeping thread and joins it.

## State and Persistence
Global state includes the pthread id, vector of job functions, and mutex. Jobs persist until process exit; this file does not clear `g_funcs` on stop.

## Dependencies and Integration Points
It depends on `fatal.hpp`, `mutex.hpp`, pthreads, and sleep. `fuse_loop.cpp` starts/stops it and `fuse.cpp` registers GC/metrics callbacks through `fuse_populate_maintenance_thread`.

## Risks
Callbacks execute under the maintenance mutex, so slow callbacks block registration and each other. Since jobs are not cleared, repeated setup/stop cycles in one process can duplicate callbacks. Cancellation safety depends on only enabling cancellation outside the critical section.

## Test Signals
Test setup/stop lifecycle, callback execution count, duplicate setup behavior, cancellation during sleep, callback exceptions/abort policy, and long-running callbacks delaying stop.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/maintenance_thread.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/mount.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/mount.cpp

## Purpose
`mount.cpp` is a tiny translation unit that includes `mount.hpp`, causing the platform-specific mount helper implementation to be compiled.

## Important APIs, Types, and Functions
The actual APIs are selected by `mount.hpp`: `fuse_kern_mount`, `fuse_kern_unmount`, and supporting helpers from either BSD or generic headers.

## Control Flow
There is no runtime control flow in this file beyond inclusion. Build-time platform macros choose which header implementation is compiled into this object.

## State and Persistence
No state is declared here. State belongs to the included helper implementation and the OS mount table/fds it manipulates.

## Dependencies and Integration Points
`helper.cpp` declares and calls `fuse_kern_mount`/`fuse_kern_unmount`; this file provides their definitions through the include model. It depends on `mount.hpp` and the platform macros it evaluates.

## Risks
Header-implemented functions can cause ODR/link surprises if included in more than one translation unit. Any platform macro mistake compiles the wrong mount path.

## Test Signals
Build on Linux and BSD targets, verify exactly one definition of mount helpers, and run mount/unmount smoke tests through `fuse_mount_common`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/mount.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/mount.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/mount.hpp

## Purpose
`mount.hpp` selects the platform-specific kernel mount implementation for the vendored FUSE layer.

## Important APIs, Types, and Functions
On FreeBSD, NetBSD, OpenBSD, or DragonFly it includes `mount_bsd.h`. Otherwise it includes `mount_generic.h` and `mount_util.h`.

## Control Flow
All behavior is compile-time selection based on OS macros. There is no executable logic in this header.

## State and Persistence
No direct state exists. The included implementations manipulate process environment, fds, mount helpers, and mount table state.

## Dependencies and Integration Points
It is included by `mount.cpp`. `helper.cpp` relies on the selected implementation to provide `fuse_kern_mount` and `fuse_kern_unmount`.

## Risks
Because implementations live in headers, including this header from multiple source files could duplicate non-inline definitions. Portability depends on correct OS macro coverage.

## Test Signals
Compile on each supported OS family and verify the expected helper path is selected. Linux should include generic plus mtab utilities; BSD should include BSD-only mount code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/mount.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/mount_bsd.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/mount_bsd.h

## Purpose
`mount_bsd.h` implements kernel mount and unmount support for BSD-style FUSE environments using `mount_fusefs`.

## Important APIs, Types, and Functions
It defines BSD mount option parsing via `fuse_mount_opts`, `mount_opts`, `fuse_mount_opt_proc`, `fuse_kern_mount`, and `fuse_kern_unmount`. Helpers include `mount_help`, `mount_version`, `do_unmount`, `init_backgrounded`, and `fuse_mount_core`.

## Control Flow
`fuse_kern_mount` sets environment markers for `mount_fusefs`, parses args into kernel options, handles help/version, then calls `fuse_mount_core`. Core accepts an inherited `FUSE_DEV_FD`, opens a fuse device from `FUSE_DEV_NAME` or `/dev/fuse`, optionally forks and execs `mount_fusefs` with fd and mountpoint, and returns the device fd. Unmount resolves the fuse character device from `fstat`, validates it looks like a fuse device, forks `/sbin/umount -f`, then closes the fd.

## State and Persistence
It manipulates process environment, open fds, child processes, and the OS mount table. No library heap state persists except parsed option strings during the call.

## Dependencies and Integration Points
The file depends on BSD headers, `fuse_opt`, and `mount_fusefs`. It is selected by `mount.hpp` for BSD platforms and called by `helper.cpp`.

## Risks
The argv array for `mount_fusefs` is fixed size. Environment variables can redirect fd/device behavior. Fork/wait error handling is minimal. Unmount depends on BSD device naming and may no-op if validation fails.

## Test Signals
BSD tests should cover inherited `FUSE_DEV_FD`, device open, `FUSE_NO_MOUNT`, help/version options, kernel option forwarding, init-backgrounded behavior, mount helper failure, and unmount of valid/invalid fuse fds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/mount_bsd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/mount_generic.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/mount_generic.h

## Purpose
`mount_generic.h` implements Linux/Unix-generic FUSE mount and unmount logic, including direct kernel `mount(2)` and fallback to `fusermount`/`fusermount3`.

## Important APIs, Types, and Functions
Exports are `fuse_kern_mount` and `fuse_kern_unmount`. Internal pieces include `mount_opts`, `fuse_mount_opts`, `exec_fusermount`, `set_mount_flag`, `fuse_mount_opt_proc`, `receive_fd`, `fuse_mount_sys`, `fuse_mount_fusermount`, and `get_mnt_flag_opts`.

## Control Flow
Arguments are parsed into kernel flags, kernel options, fusermount-only options, subtype options, and mtab options. `fuse_mount_sys` validates/repairs a mountpoint, opens `/dev/fuse`, appends fd/rootmode/user/group options, builds the FUSE type/source, and attempts `mount(2)`. EPERM or `auto_unmount` triggers fallback to `fuse_mount_fusermount`, which forks a helper, passes a communication fd in `_FUSE_COMMFD`, and receives the mounted fuse fd via `SCM_RIGHTS`. Unmount closes the fd, checks for already-unmounted poll errors, uses direct lazy unmount as root, or execs fusermount for unprivileged users.

## State and Persistence
The implementation mutates the OS mount table, `/etc/mtab` through `mount_util.h` when appropriate, child process state, and open fds. Parsed strings are freed before return.

## Dependencies and Integration Points
It depends on `fuse_opt`, `mount_util.h`, POSIX sockets/fork/mount APIs, and `fusermount` binaries. `helper.cpp` calls it through `fuse_mount_common` and teardown.

## Risks
Mount security and fd passing are sensitive. The fixed argv array limits option count. Direct mount fallback decisions rely on errno. `auto_unmount` only works through helper mode. `receive_fd` validates only basic control-message shape.

## Test Signals
Test direct root mount, unprivileged fusermount fallback, `auto_unmount`, subtype and fsname combinations, `fuseblk` missing support, broken mountpoint ENOTCONN recovery, mtab updates, fd close behavior, and helper exec failure paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/mount_generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/mount_util.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/mount_util.h

## Purpose
`mount_util.h` provides shared mount-table and path utilities for the generic mount path and `fusermount`.

## Important APIs, Types, and Functions
Public helpers are `fuse_mnt_add_mount`, `fuse_mnt_umount`, `fuse_mnt_remove_mount`, `fuse_mnt_resolve_path`, and `fuse_mnt_check_fuseblk`. Internals include `mtab_needs_update`, `add_mount`, `exec_umount`, and `remove_mount`.

## Control Flow
`mtab_needs_update` skips updates when `/etc/mtab` is missing, symlinked, inside the mount, or read-only. Add/remove/update helpers fork `/bin/mount` or `/bin/umount` with fake/no-canonicalize flags while SIGCHLD is blocked. `fuse_mnt_umount` either calls `umount2` directly or delegates to `/bin/umount`. `fuse_mnt_resolve_path` canonicalizes the parent path while preserving a final component that may not yet exist. `fuse_mnt_check_fuseblk` scans `/proc/filesystems`.

## State and Persistence
The durable state touched here is the OS mount table or mtab representation. It also changes effective uid temporarily for mtab write checks.

## Dependencies and Integration Points
`mount_generic.h` uses these helpers after direct root mounts and unmounts. `fusermount.cpp` uses them for resolving mountpoints, mtab updates, and fuseblk support checks.

## Risks
Forked mount/umount commands must be present at `/bin/mount` and `/bin/umount`. The `mtab_needs_update` prefix check is path-sensitive. Temporary `setreuid` use must restore uid. Path resolution edge cases around trailing slashes, `.`, and `..` can affect mount safety.

## Test Signals
Test symlinked `/etc/mtab`, read-only mtab, missing mtab, root and non-root update paths, relative/trailing slash mountpoints, missing final component, fuseblk present/absent, and failure of fork/exec/wait.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/mount_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/node.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/node.cpp

## Purpose
`node.cpp` provides pooled allocation and cleanup for `node_t` objects used by the high-level FUSE namespace cache.

## Important APIs, Types, and Functions
Exports are `node_alloc`, `node_free`, `node_gc`, and `node_clear`, backed by a static `ObjPool<node_t> g_NODE_POOL`.

## Control Flow
`fuse.cpp` requests nodes for root, lookup, create/tmpfile provisional ids, and path entries. Freed nodes return to the pool. Maintenance GC calls `node_gc` for basic cleanup and `node_clear` for thorough cleanup.

## State and Persistence
The object pool is global and process-local. It caches memory for reuse but no node identity persists once freed or across process restarts.

## Dependencies and Integration Points
The file depends on `node.hpp` and `objpool.hpp`. It is one of the key memory-management dependencies of `fuse.cpp`.

## Risks
Pool reuse means `node_t` fields must be fully initialized by callers before use. Clearing the pool while live nodes exist would be unsafe unless `ObjPool` protects against it or only free objects are cleared.

## Test Signals
Use lookup/forget churn, GC under load, sanitizer runs for use-after-free, and assertions around `node_t` initialization after reuse.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/node.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/node.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/node.hpp

## Purpose
`node.hpp` defines the compact node record used by the high-level FUSE namespace cache.

## Important APIs, Types, and Functions
`struct node_t` contains hash links for name/id tables, name string, parent pointer, node id, kernel lookup count, internal refcount, open count, remembered flag, stat-cache fingerprint, and tree lock counter. It declares `node_alloc`, `node_free`, `node_gc`, and `node_clear`. Static assertions pin the expected structure size on 64-bit and 32-bit builds.

## Control Flow
`fuse.cpp` embeds `node_t` in two hash tables: by node id and by `(parent,name)`. Lookup operations increment `nlookup`; forget operations decrement it. Open/release update `open_count`. Rename/unlink change name and parent links. Path resolution uses `treelock` to protect against concurrent tree mutation.

## State and Persistence
Every field is in-memory only. Node id values are exposed to the kernel for the active mount, but are regenerated after restart.

## Dependencies and Integration Points
This header is shared by `node.cpp` and `fuse.cpp`. Its layout affects memory usage and metrics reporting in `fuse.cpp`.

## Risks
Bitfield packing and static size assertions can fail across compilers/ABIs. Refcount, lookup count, open count, and treelock invariants are manually maintained. `name` ownership is external to the struct and must be freed exactly once.

## Test Signals
Compile on 32-bit/64-bit targets, stress lookup/forget/open/release/rename/unlink interactions, and verify metrics size expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/node.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/pin_threads.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/pin_threads.cpp

## Purpose
`pin_threads.cpp` implements named CPU-affinity policies for FUSE read and process threads.

## Important APIs, Types, and Functions
The namespace exposes policy functions `R1L`, `R1P`, `RP1L`, `RP1P`, `R1LP1L`, `R1PP1P`, `RPSL`, `RPSP`, `R1PPSP`, and dispatcher `PinThreads::pin`. Policies use logical CPU vectors or physical core-to-CPU maps from `CPU`.

## Control Flow
Each policy fetches available CPUs/cores, returns if none, and calls `CPU::setaffinity` for read and process pthread ids according to the policy name: one logical CPU, one physical core, read/process together, read/process separated, or spread across CPUs/cores. `pin` ignores empty/`false` type strings and logs a warning for unknown values.

## State and Persistence
No state is stored here. It mutates OS thread affinity masks for the lifetime of the threads.

## Dependencies and Integration Points
It depends on `cpu.hpp` and `syslog.hpp`. `fuse_loop.cpp` calls `PinThreads::pin` after thread-pool creation and before processing continues.

## Risks
Affinity policy names are stringly typed. CPU topology discovery may be unavailable or constrained by cpusets. Some policies reuse the first CPU/core when there are fewer cores than requested, which can concentrate load.

## Test Signals
Test every policy string on single-core, SMT multi-core, and cpuset-limited environments; verify invalid strings warn and `false` is no-op; verify read/process thread ids are pinned as intended.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/pin_threads.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/pin_threads.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/pin_threads.hpp

## Purpose
`pin_threads.hpp` declares the CPU-affinity policy API for FUSE read and process worker threads.

## Important APIs, Types, and Functions
It declares the individual policy functions and the dispatcher `pin(const CPU::ThreadIdVec&, const CPU::ThreadIdVec&, const std::string&)` in namespace `PinThreads`.

## Control Flow
The header has no runtime flow. Callers pass read-thread ids, process-thread ids, and a policy string to the implementation.

## State and Persistence
No state is declared. Affinity changes are applied by the implementation to live pthreads.

## Dependencies and Integration Points
It includes `cpu.hpp` for thread id vector types and `<string>`. `fuse_loop.cpp` is the primary caller.

## Risks
Public policy declarations must stay synchronized with the dispatcher implementation. Adding a policy in the header without dispatcher support will compile but be unreachable through config.

## Test Signals
Build tests should catch signature drift. Config tests should verify every documented policy string maps to a declared implementation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/pin_threads.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/xalloc.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/xalloc.hpp

## Purpose
`xalloc.hpp` provides fatal allocation helpers that include source file and line information in error messages.

## Important APIs, Types, and Functions
Macros `xstrdup(S)` and `xmalloc(S)` expand to `xstrdup_impl` and `xmalloc_impl` with `__FILE__` and `__LINE__`. `xstrdup_impl` rejects null input and failed `strdup`; `xmalloc_impl` exits on failed `malloc`.

## Control Flow
Callers invoke the macros where allocation is considered unrecoverable. On invalid/null input or allocation failure, the helper prints a mergerfs-prefixed diagnostic to stderr and exits `EXIT_FAILURE`. On success, it returns the allocated pointer.

## State and Persistence
No state is held. Returned memory ownership belongs to the caller.

## Dependencies and Integration Points
The header depends on stdio/stdlib and is used by `fuse.cpp` for root node name allocation. It can be included anywhere a fail-fast allocation policy is acceptable.

## Risks
These helpers terminate the process instead of returning errors, so they should not be used in paths where libfuse is expected to recover from ENOMEM. `xmalloc(0)` behavior follows libc `malloc(0)` and may abort on null.

## Test Signals
Test null `xstrdup`, forced allocation failure, diagnostic file/line accuracy, and caller ownership/free behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/xalloc.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/util/fusermount.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/util/fusermount.cpp

## Purpose
`fusermount.cpp` is the setuid-style helper for mounting and unmounting FUSE filesystems safely for unprivileged users.

## Important APIs, Types, and Functions
The file is a standalone `main`. Major helpers include privilege switching (`drop_privs`, `restore_privs`), mtab locking/update, unmount authorization (`may_unmount`), symlink-safe mountpoint verification (`check_is_mount*`, `chdir_to_parent`, `umount_nofollow_support`), config parsing (`read_conf`), option filtering (`do_mount`, `find_mount_flag`, `get_mnt_opts`), mountpoint permission checking (`check_perm`), fuse device open, `mount_fuse`, and `send_fd`.

## Control Flow
`main` parses `-o`, `-u`, `-z`, `-q`, help/version, resolves the mountpoint under dropped privileges, and either unmounts or mounts. Mounting opens `/dev/fuse`, reads `/etc/fuse.conf`, enforces `mount_max`, verifies mountpoint permissions, builds safe mount options, calls `mount(2)`, optionally updates mtab, sends the fuse fd to the caller over `_FUSE_COMMFD`, and handles `auto_unmount` by daemonizing and unmounting when the control socket closes. Unmounting validates ownership/mtab for root-effective helper mode and avoids symlink-following attacks.

## State and Persistence
It mutates mount table state, may update mtab, reads `/etc/fuse.conf`, and passes fds over Unix sockets. Globals include `user_allow_other`, `mount_max`, and `auto_unmount`.

## Dependencies and Integration Points
It uses `mount_util.h`, libc/POSIX mount/socket/namespace APIs, `/dev/fuse`, `/etc/fuse.conf`, and `_FUSE_COMMFD`. `mount_generic.h` execs this helper for fallback/unprivileged mounts.

## Risks
This is security-critical. `allow_other`, `dev`, `suid`, `blkdev`, mountpoint ownership, symlink races, and mtab authorization all need strict behavior. The helper assumes Linux-specific namespace and fsuid APIs. Fixed buffers and manual option parsing require bounds vigilance.

## Test Signals
Test non-root mount with/without `user_allow_other`, `mount_max`, directory and regular-file mountpoints, symlink race prevention, lazy and normal unmount, mtab symlink mode, fd passing, `auto_unmount`, missing `/dev/fuse`, and old `/proc/fs/fuse/dev` fallback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/util/fusermount.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/util/mount.mergerfs.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/util/mount.mergerfs.cpp

## Purpose
`mount.mergerfs.cpp` is a mount helper wrapper that translates `/sbin/mount.*` style invocations into an execution of the mergerfs filesystem binary.

## Important APIs, Types, and Functions
The standalone `main` parses positional source/mountpoint plus `-t` and `-o` options. Helpers `shell_quote` and `add_option` build a safe shell command string.

## Control Flow
The program derives filesystem type from argv[0] names like `mount.fuse.<type>` or `mount.fuseblk.<type>`, parses source and mountpoint, ignores mount manager options such as `nofail`, `user`, `auto`, and `_netdev`, handles `setuid=USER`, preserves real mount options, ensures `dev` and `suid` are added unless disabled by options, splits `type#source` when type is empty, then execs `/bin/sh -c '<type> <source> <mountpoint> -o <options>'`. With `setuid=`, it wraps the command in `su - USER -c`.

## State and Persistence
No internal state persists. It affects the process by execing a shell command and may set `HOME=/root` if no home exists and not switching users.

## Dependencies and Integration Points
It is intended for system mount integration for mergerfs. It depends on `/bin/sh`, optional `su`, and the mergerfs executable matching the derived type.

## Risks
Shell execution is inherently sensitive, but `shell_quote` handles single quotes. Option parsing uses `strtok` on comma-separated options and does not honor escaped commas. `setuid=` causes a shell command through `su`, which depends on system policy and PATH/command availability.

## Test Signals
Test `mount.mergerfs src dst`, `mount.fuse.mergerfs`, `type#source`, `-t fuse.mergerfs`, ignored options, `nodev`/`nosuid`, `setuid=`, source or mountpoint containing quotes/spaces, missing args, and empty type/source errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/util/mount.mergerfs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/moodycamel/blockingconcurrentqueue.h -->
# sources/user-network-fs/mergerfs/vendored/moodycamel/blockingconcurrentqueue.h

## Purpose
`blockingconcurrentqueue.h` wraps `moodycamel::ConcurrentQueue` with a semaphore so consumers can block until items are available.

## Important APIs, Types, and Functions
The template `moodycamel::BlockingConcurrentQueue<T, Traits>` exposes producer/consumer token types, queue constants from the underlying concurrent queue, constructors with capacity/producer sizing, move/swap support, `enqueue`, `try_enqueue`, bulk enqueue variants, `try_dequeue`, bulk try-dequeue variants, blocking `wait_dequeue`, timed wait variants, `size_approx`, `is_lock_free`, and non-member `swap`.

## Control Flow
Successful enqueue operations delegate to `inner` and then signal the `LightweightSemaphore` once or by bulk count. Dequeue operations first acquire one or more semaphore permits, then spin on `inner.try_dequeue` or `inner.try_dequeue_bulk` until the promised item count is retrieved. Blocking waits call `sema->wait` or `waitMany`; timed waits return false/zero if the semaphore times out. The semaphore is allocated using the queue traits allocator and held by a unique_ptr with custom deleter.

## State and Persistence
State is in-memory: the underlying lock-free queue plus semaphore permit count. Queue movement is supported only when no other thread is using it. Tokens remain tied to the moved queue state.

## Dependencies and Integration Points
It includes `concurrentqueue.h` and `lightweightsemaphore.h`, plus standard type traits, memory, chrono, and time headers. It is a vendored general-purpose concurrency primitive used by components that need MPMC queues with blocking consumers.

## Risks
Correctness depends on signaling the semaphore only after successful enqueue and consuming permits before dequeue. After a semaphore permit is acquired, dequeue spins until an item appears, relying on the underlying queue's eventual visibility. `size_approx` is only an estimate. Destruction or move while threads are active is unsafe.

## Test Signals
Test single/multiple producers and consumers, explicit tokens, bulk enqueue/dequeue counts, timed wait expiry, move/swap only while quiescent, allocation failure construction, semaphore count consistency under failed try_enqueue, and high-contention stress with sanitizers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/moodycamel/blockingconcurrentqueue.h -->
