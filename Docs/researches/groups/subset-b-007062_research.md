# subset-b-007062 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/compat-errno.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/compat-errno.c

## Purpose
This file provides GlusterFS's errno compatibility translation layer. It maps native platform `errno` values to GlusterFS stable `GF_ERROR_CODE_*` values and back so errors can be serialized, compared, and transported across different operating systems without assuming that numeric errno assignments are identical.

## Important APIs, types, and functions
The public APIs are `gf_errno_to_error(int32_t op_errno)` and `gf_error_to_errno(int32_t error)`. They lazily initialize two static 1024-entry arrays, `gf_errno_to_error_array` and `gf_error_to_errno_array`, guarded only by the integer flag `gf_compat_errno_init_done`. `init_errno_arrays()` first installs identity mappings for `0..GF_ERROR_CODE_UNKNOWN-1`, then calls platform-specific `init_compat_errno_arrays()` implementations selected by `GF_SOLARIS_HOST_OS`, `GF_DARWIN_HOST_OS`, `GF_BSD_HOST_OS`, or `GF_LINUX_HOST_OS`.

## Control flow
Callers pass an errno or portable error code into one of the two conversion functions. Zero is returned immediately. On first nonzero use, arrays are initialized with identity mappings and then adjusted for platforms where errno ordering differs. Inputs inside the portable error-code range are looked up in the appropriate array; out-of-range values are returned unchanged.

## State and persistence behavior
All state is process-local static memory. The translation arrays persist for the lifetime of the process and are never reset. No disk persistence occurs. Initialization is lazy and non-atomic, so concurrent first calls can race while writing the same deterministic table values.

## Dependencies and integration points
The file depends on `glusterfs/compat-errno.h` for `GF_ERROR_CODE_*` constants and platform errno availability. It is used by dictionary serialization, RPC, translator callbacks, and other libglusterfs components that need portable error values in cross-platform messages.

## Risks and edge cases
The lazy initialization flag is not protected by a mutex or atomic primitive. The mappings are deterministic, but data race tooling can report this and weak memory models could observe partially initialized arrays. Array bounds depend on `GF_ERROR_CODE_UNKNOWN` staying below 1024 and native errno constants used as indexes also remaining below 1024. Platform blocks are long hand-maintained tables, so incorrect or missing mappings can silently degrade to identity behavior.

## Test signals
Useful tests should verify round-trip conversions for Linux identity behavior and for representative Solaris, Darwin, and BSD remaps under those build flags. Boundary tests should cover zero, negative values, `GF_ERROR_CODE_UNKNOWN`, and values above the mapping range. Thread sanitizer coverage of concurrent first use would exercise the known lazy-init race.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/compat-errno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/compat.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/compat.c

## Purpose
This file contains operating-system compatibility shims used by libglusterfs. Most code is Solaris-specific extended attribute support for platforms where xattrs are represented through attribute directories and where symlinks or device files need a mapped regular file. It also provides fallback implementations for missing libc helpers and a portable lazy unmount wrapper.

## Important APIs, types, and functions
Solaris exports include `solaris_fsetxattr`, `solaris_fgetxattr`, `solaris_setxattr`, `solaris_getxattr`, `solaris_listxattr`, `solaris_flistxattr`, `solaris_removexattr`, `solaris_unlink`, `solaris_rename`, `make_export_path`, and `solaris_xattr_resolve_path`. Generic or conditional helpers include `strsep`, `vasprintf`, `asprintf`, `mkdtemp`, `gf_extattr_list_reshape`, `strnlen`, and `gf_umount_lazy`.

## Control flow
Solaris path xattr operations first call `solaris_xattr_resolve_path()`. Regular files and directories use native attribute operations. Special files are redirected to a mapped file under `GF_SOLARIS_XATTR_DIR` below the export root discovered by walking GFID xattrs with `make_export_path()`. Set/get/list/remove operations then use `attropen`, `openat`, `read`, `write`, `unlinkat`, and directory iteration. `gf_umount_lazy()` builds a `runner_t`, invokes Linux `umount -l` or the platform `umountd`, and optionally removes the mount directory on Linux.

## State and persistence behavior
Compatibility calls persist data only through filesystem xattrs and the Solaris mapped-xattr files. The mapped files are keyed by inode number beneath the export's hidden xattr directory. `solaris_unlink()` removes the mapped file when the source has a single link; `solaris_rename()` removes a mapped destination before rename. No process-global cache is maintained.

## Dependencies and integration points
The file integrates with GlusterFS allocation/logging (`GF_CALLOC`, `GF_FREE`, `gf_msg`), path/stat conversion (`iatt_from_stat`), GFID helpers, syscall wrappers, and command execution via `runner_t`. Higher layers call these through compatibility macros from `glusterfs/compat.h` and `glusterfs/syscall.h`.

## Risks and edge cases
`make_export_path()` and related Solaris functions use repeated `strcat()` into `PATH_MAX` buffers and assume path lengths fit. Error handling around `dup`, `fdopendir`, and `close` can leak or double-close if platform semantics differ. `mkdtemp()` appears to treat `mkstemp()` as returning a string, which is only safe if a platform macro changes that interface; otherwise it is suspicious. The Solaris mapped-xattr scheme relies on inode stability and cleanup paths being consistently used.

## Test signals
Tests should cover Solaris xattrs on regular files, symlinks, device files, ENOENT-to-ENODATA translation, zero-size get/list calls, too-small list buffers returning `ERANGE`, unlink and rename cleanup of mapped xattr files, BSD extattr list reshaping, missing `strnlen`, and `gf_umount_lazy()` command construction on Linux and non-Linux builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/ctx.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/ctx.c

## Purpose
This file creates and initializes the process-wide GlusterFS context object and lazily attaches a timer-wheel context to it. The context is the shared runtime root for graphs, volume files, memory pools, logging defaults, command arguments, host identity, and statistics.

## Important APIs, types, and functions
`glusterfs_ctx_new()` allocates and initializes `glusterfs_ctx_t`; `global_ctx` stores the first created context. `glusterfs_ctx_tw_get()` lazily creates and references `struct gf_ctx_tw`, whose `timer_wheel` comes from `gf_tw_init_timers()`. `glusterfs_ctx_tw_put()` releases that reference, and `glusterfs_ctx_tw_destroy()` cleans pending timers with `gf_tw_cleanup_timers()`.

## Control flow
Context creation uses plain `CALLOC` before memory accounting is finalized, initializes graph/mempool/volfile lists, daemon pipe descriptors, default log level, valgrind-tool mode, dict statistics atomics, hostname storage, and context locks. Timer-wheel access locks `ctx->lock`, either references the existing `ctx->tw` or allocates and initializes a new one, then returns the raw timer-wheel pointer.

## State and persistence behavior
The file owns in-memory process state only. `global_ctx` is set once to the first created context. The hostname is copied from the running host. Timer-wheel state persists until all `GF_REF` holders release it and the destroy callback runs.

## Dependencies and integration points
It depends on `glusterfs/globals.h` for context structures and global memory-accounting state, `timer-wheel.h` for timer lifecycle, pthread locks, atomics, and list macros. Many libglusterfs subsystems rely on `THIS->ctx` or `global_ctx` for memory pools, logging, stats, and graph state.

## Risks and edge cases
`global_ctx` assignment is not synchronized, so concurrent context creation can race. `glusterfs_ctx_tw_get()` does not check allocation or `gf_tw_init_timers()` failure before dereferencing and returning `ctx_tw->timer_wheel`. `glusterfs_ctx_tw_put()` assumes `ctx->tw` is non-NULL. Context destruction is not present here, so ownership of allocated hostname and locks must be handled elsewhere.

## Test signals
Tests should assert initialized defaults, hostname allocation failure behavior through fault injection, global context first-set behavior, timer-wheel lazy creation and reference release, and failure paths for timer allocation. Concurrency tests around first timer access and context creation would expose races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/ctx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/daemon.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/daemon.c

## Purpose
This file implements GlusterFS daemonization helpers. It is a small wrapper around fork/session detachment, optional `chdir("/")`, and optional standard stream redirection to `/dev/null`.

## Important APIs, types, and functions
`os_daemon_return(int nochdir, int noclose)` forks and returns the fork result to the parent while completing daemon setup in the child. `os_daemon(int nochdir, int noclose)` calls that helper and exits the parent with `_exit(0)` when fork succeeded.

## Control flow
`os_daemon_return()` calls `fork()`. The parent receives the child PID and returns it. The child calls `setsid()`, optionally changes directory to root, and optionally reopens stdin, stdout, and stderr to `DEVNULLPATH`. `os_daemon()` converts the positive parent return into process exit, leaving only the child to continue with return 0 or -1.

## State and persistence behavior
The file changes process state: parent/child split, session leadership, current working directory, and standard file descriptors. It writes no persistent data and allocates no heap state.

## Dependencies and integration points
It includes `glusterfs/daemon.h` for `DEVNULLPATH` and public declarations. Startup code uses these helpers to detach long-running daemons while preserving the option to keep cwd or standard streams for foreground/debug modes.

## Risks and edge cases
The implementation performs a single fork, not the classic double-fork pattern, so the child remains a session leader and could acquire a controlling terminal later. If `chdir("/")` fails, execution continues unless later stream reopening fails; the return code can be overwritten by subsequent success. `freopen()` failure returns -1 but may leave some streams already redirected.

## Test signals
Tests should cover parent return of child PID, child return 0, `nochdir` preserving cwd, `noclose` preserving streams, failure injection for `fork`, `setsid`, `chdir`, and each `freopen`, plus integration startup tests that verify foreground mode does not daemonize.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/daemon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/default-args.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/default-args.c

## Purpose
This file captures GlusterFS translator FOP arguments and callback results into `default_args_t` and `default_args_cbk_t` structures. It is used when operations need to be resumed, replayed, wound through default paths, or stored across asynchronous boundaries.

## Important APIs, types, and functions
The exported surface is a large family of `args_*_store()` and `args_*_cbk_store()` functions for lookup, stat, create, open, read/write, xattr, locks, readdir, setattr, fallocate, discard, zerofill, ipc, seek, active lock migration, leases, icreate, namelink, and copy-file-range. Cleanup helpers are `args_wipe()`, `args_cbk_wipe()`, and `args_cbk_init()`.

## Control flow
Each store function copies scalar arguments, duplicates `loc_t` through `loc_copy()`, references `fd_t`, `inode_t`, `dict_t`, and `iobref` objects, duplicates strings with `gf_strdup()`, and duplicates iovec or checksum buffers when needed. Callback store functions capture `op_ret`, `op_errno`, returned `iatt` structures, xdata, directory entries, and lock lists. Wipe functions release references and heap buffers after the captured call state is consumed.

## State and persistence behavior
The file creates only in-memory retained call state. Persistence is via referenced GlusterFS objects and duplicated buffers inside the provided args structure. Correct lifetime depends on callers invoking the matching wipe function after use. Directory entry and lock-list copies are stored in embedded linked lists.

## Dependencies and integration points
It depends on `glusterfs/defaults.h` and many core object ownership helpers: `loc_copy`, `loc_wipe`, `dict_ref`, `fd_ref`, `inode_ref`, `iobref_ref`, `iov_dup`, `gf_dirent_for_name2`, `entry_copy`, `gf_flock_copy`, and list macros. Default translators and stack-resume logic consume these snapshots.

## Risks and edge cases
Most functions return 0 even if a nested allocation fails, except selected lock-list helpers. Some functions dereference required inputs without validation, such as `fd_ref(fd)` or `iobref_ref(iobref)` in paths where callers are expected to pass non-NULL values. Partial failures while copying directory entries or lock migration entries can leave partially populated lists for cleanup. Ownership distinctions between borrowed scalars and referenced objects are critical.

## Test signals
Tests should verify every store/wipe pair under normal and NULL-optional arguments, reference-count increments/decrements, deep copies of iovec, directory entries, checksums, and lock migration lists, and fault-injection behavior for allocation failure mid-copy. Replay/resume tests should confirm captured args remain valid after original caller-owned inputs are released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/default-args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/defaults-tmpl.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/defaults-tmpl.c

## Purpose
This template backs generated default translator operations. It fills `xlator_fops` with default pass-through FOP implementations and supplies non-generated default handlers for lifecycle and notification behavior.

## Important APIs, types, and functions
`_default_fops` initializes each FOP slot to `default_*` functions, and `default_fops` points to that table. Hand-written functions include `default_forget`, `default_releasedir`, `default_release`, `default_notify`, `default_mem_acct_init`, and `default_fini`.

## Control flow
Generated FOPs forward calls to the first child translator and unwind callbacks. `default_notify()` routes events according to direction: parent up/down and cleanup flow to children; child up/down/connecting/auth/upcall/ping flow to parents or root; graph top child-down can mark `graph->used = 0` and broadcast `child_down_cond` when all client xlators are down. `default_fini()` frees `this->private`.

## State and persistence behavior
The default FOP table is static process state. `default_notify()` mutates in-memory graph state for child-down completion and may propagate events through translator graph relationships. No disk persistence occurs.

## Dependencies and integration points
It depends on `glusterfs/defaults.h`, translator graph structures, `xlator_notify`, `XLATOR_NOTIFY`, graph mutex/condition variables, and memory-accounting setup through `xlator_mem_acct_init()`. It is foundational for translators that omit explicit FOP, callback, notify, or lifecycle handlers.

## Risks and edge cases
Notification routing is graph-sensitive and can accidentally bypass parents that have not `init_succeeded`. Root forwarding special cases are important for FUSE/client graphs. `default_fini()` blindly frees `this->private` without translator-specific cleanup, so translators with richer private state need custom fini handlers.

## Test signals
Tests should validate generated default FOP forwarding, callback unwind behavior, notify propagation for each event family, root xlator forwarding, child-down graph condition broadcast, and that translators with default fini only use simple `GF_FREE`-managed private data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/defaults-tmpl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/dict.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/dict.c

## Purpose
This file implements GlusterFS's core dictionary container, typed `data_t` values, conversion helpers, serialization, comparison, and debugging dumps. Dictionaries are used widely for xattrs, xdata, options, RPC payloads, and translator metadata.

## Important APIs, types, and functions
Core lifecycle APIs include `dict_new`, `dict_ref`, `dict_unref`, `dict_reset`, `data_ref`, `data_unref`, and `data_copy`. Lookup/update APIs include `dict_setn`, `dict_addn`, `dict_get`, `dict_get_with_ref`, `dict_deln`, `dict_foreach`, `dict_foreach_match`, `dict_copy`, `dict_copy_with_ref`, `dict_rename_key`, and `are_dicts_equal`. Typed APIs include integer, unsigned, double, string, pointer, binary, GFUUID, `iatt`, `mdata`, flag, and boolean getters/setters. Serialization APIs include `dict_allocate_and_serialize`, `dict_unserialize`, `dict_unserialize_specific_keys`, `dict_serialized_length_lk`, and value-join/dump helpers.

## Control flow
New dictionaries and data values come from context memory pools. `dict_set_lk()` either replaces an existing pair or prepends a new `data_pair_t` with an embedded key. Values are refcounted; `dict_unref()` destroys pairs and unrefs values when the dict refcount reaches zero. Typed setters generally format numeric values into string-backed `data_t` objects, while binary setters wrap caller-provided buffers with static/dynamic ownership flags. Getters usually acquire a referenced `data_t`, validate its type, convert or expose the payload, then unref the data wrapper.

## State and persistence behavior
Dictionary state is process memory protected by `dict->lock` for basic mutation and lookup. Serialized dictionaries use a count plus key/value length headers in big-endian order, followed by null-terminated keys and raw value bytes. Unserialization currently marks values as `GF_DATA_TYPE_STR_OLD`, preserving older protocol behavior. Runtime statistics are accumulated into `THIS->ctx->stats` during dict destruction.

## Dependencies and integration points
The file depends on GlusterFS memory pools, atomics, logging, endian conversion, compatibility errno, statedump, `iatt`, `mdata_iatt`, UUID helpers, fnmatch, list utilities, and many common macros. It is a cross-cutting dependency for translators, RPC, xattr operations, configuration, locking, and state dumps.

## Risks and edge cases
Some iteration helpers walk `members_list` without taking `dict->lock`, so callers must avoid concurrent mutation unless the API explicitly locks. Several typed pointer getters return raw payload pointers after unreffing the `data_t`; safety depends on the parent dict keeping the data alive. Serialization bounds checks are extensive, but `keylen` and `vallen` are signed after conversion from unsigned wire values, so very large lengths require careful fuzzing. `_dict_modify_flag()` has an error path that unlocks based on `this` and `key`, which must match actual lock acquisition. Ownership flags (`is_static`) are central: a wrong setter choice can leak, double-free, or retain caller memory unsafely.

## Test signals
Test coverage should include refcount lifecycle, replacement accounting in `totkvlen`, type validation, numeric range conversion, string/binary ownership behavior, concurrent lookup/update stress, dictionary equality with match and value-ignore callbacks, serialization round trips, malformed serialized buffers, specific-key extraction, flag set/clear/check, statedump/log dumps with large values, and memory fault injection for partial mutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/dict.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/event-epoll.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/event-epoll.c

## Purpose
This file implements the epoll backend for GlusterFS's event subsystem. It manages file descriptor registration, one-shot epoll delivery, poller worker threads, dynamic thread reconfiguration, poller-death notifications, and rearming after handlers complete.

## Important APIs, types, and functions
The backend exports `event_ops_epoll` with `event_pool_new_epoll`, `event_register_epoll`, `event_select_on_epoll`, unregister variants, `event_dispatch_epoll`, `event_reconfigure_threads_epoll`, `event_pool_destroy_epoll`, and `event_handled_epoll`. Internal state is organized into `event_slot_epoll`, `event_slot_epoll_table`, `event_thread_data`, slot generation counters, atomic slot refs, and the `poller_death` list.

## Control flow
Registration allocates a slot from table arrays, initializes handler/data/event flags, stores index and generation in `epoll_event.data`, and calls `epoll_ctl(ADD)`. Dispatch starts poller threads and joins the first one. Workers loop in `epoll_wait()`, validate slot generation, suppress duplicate in-handler delivery, invoke the registered handler, and rely on the handler path to call `gf_event_handled()`. `event_handled_epoll()` decrements `in_handler` and rearms the fd with `epoll_ctl(MOD)` if the slot generation still matches.

## State and persistence behavior
All state is in-memory in `struct event_pool`. Slot tables persist until event-pool destruction. Slot generation values detect stale events after unregister/reuse. `do_close` defers fd close until final slot unref. Poller-death notification temporarily splices registered slots to a local list while a shrinking worker notifies handlers with `event_thread_died = 1`.

## Dependencies and integration points
The file depends on Linux `sys/epoll.h`, GlusterFS event types from `glusterfs/gf-event.h`, threading through `gf_thread_create`, syscall wrappers, atomics, locks, lists, and structured logging. The public wrappers in `event.c` choose this backend when epoll is available.

## Risks and edge cases
The backend has complex concurrency: slot refs, slot locks, event-pool mutex, generation checks, unregister racing handler execution, and thread reconfiguration all interact. Failure to call `gf_event_handled()` after a handler can leave a one-shot fd disabled. `event_select_on_epoll()` skips `epoll_ctl(MOD)` while a handler is active, relying on later rearm. Destroy mode blocks new registrations but comments acknowledge races with concurrent registration. Poller-death list slicing must avoid use-after-free and missed notifications.

## Test signals
Tests should cover register/select/unregister/close, stale generation delivery, handler rearm, missing handled behavior, concurrent unregister during handler, error/hup single handling, dynamic thread increase/decrease, destroy-mode shutdown, poller-death notifications, slot-table expansion and exhaustion, and fd close deferral until final unref.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/event-epoll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/event-history.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/event-history.c

## Purpose
This file wraps circular-buffer history storage for translator or subsystem events. It provides a small `eh_t` object with a buffer, lock, save, dump, and destroy operations.

## Important APIs, types, and functions
The exported APIs are `eh_new`, `eh_dump`, `eh_save_history`, and `eh_destroy`. `eh_t` owns a `buffer_t *` created by `cb_buffer_new()`, and callers supply an optional `destroy_buffer_data` callback for buffered entries.

## Control flow
`eh_new()` allocates an `eh_t`, creates the circular buffer with configured size and use-once behavior, initializes a mutex, and returns the history object. `eh_save_history()` appends data through `cb_add_entry_buffer()`. `eh_dump()` calls `cb_buffer_dump()` with a caller-supplied dumper. `eh_destroy()` destroys the buffer, destroys the mutex, and frees the history.

## State and persistence behavior
History is in-memory only. The circular buffer determines retention and overwrite/use-once behavior. The lock is initialized but this file does not acquire it around save or dump, so synchronization is either inside the circular-buffer implementation or expected from callers.

## Dependencies and integration points
It depends on `glusterfs/event-history.h`, circular-buffer helpers, GlusterFS allocation and logging, pthread mutexes, and translator/subsystem code that records diagnostic histories.

## Risks and edge cases
`eh_save_history()` does not check for NULL `history` before dereferencing. `eh_dump()` tolerates NULL history, but save does not. The local mutex is unused here, which can be misleading if callers assume `eh_t` itself serializes access. Destroy during concurrent save/dump would be unsafe without external coordination.

## Test signals
Tests should cover allocation failure, buffer creation failure cleanup, save/dump order, use-once behavior, destroy callback invocation, NULL destroy handling, NULL history behavior for dump and save, and concurrent access if circular-buffer internals claim thread safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/event-history.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/event-poll.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/event-poll.c

## Purpose
This file implements the portable `poll(2)` backend for GlusterFS's event subsystem. It is the fallback when epoll is unavailable and intentionally supports only one event thread.

## Important APIs, types, and functions
The backend exports `event_ops_poll` with `event_pool_new_poll`, register/select/unregister/close functions, `event_dispatch_poll`, no-op `event_reconfigure_threads_poll`, and `event_pool_destroy_poll`. Internal helpers include `__event_getindex`, `__flush_fd`, `event_dispatch_poll_resize`, and `event_dispatch_poll_handler`.

## Control flow
Pool creation allocates an event pool and registration array, creates a nonblocking breaker pipe, registers the read end, and forces `eventthreadcount` to 1. Registration appends an `event_slot_poll` entry and expands the array by 256 when full. Selection mutates event masks. Dispatch rebuilds the cached `pollfd` array when `changed` is set, polls with a 1 ms timeout, then invokes handlers for entries with `revents`.

## State and persistence behavior
The event pool holds a mutable registration array, cached `pollfd` array, breaker pipe fds, `used`, `count`, `changed`, and `activethreadcount`. State is in-memory only. Unregister removes entries by swapping the last used registration into the removed slot, so indexes can change.

## Dependencies and integration points
It depends on POSIX poll, pthreads, fcntl, GlusterFS memory/logging/syscall wrappers, and the common event API in `glusterfs/gf-event.h`. `event.c` falls back to this backend when epoll creation is unavailable or the platform lacks epoll.

## Risks and edge cases
Because unregister swaps entries, cached indexes can become stale and `__event_getindex()` must search by fd. The 1 ms timeout is simple but can wake frequently. Reallocation failure during registration can leave `event_pool->reg` NULL because `GF_REALLOC` result is assigned directly. Destroy frees the pool without destroying mutex/condition fields initialized elsewhere, unlike the epoll backend. The poll backend has no `event_handled` hook and no one-shot suppression, so handlers must tolerate level-triggered repeated readiness.

## Test signals
Tests should cover fallback creation, breaker pipe flushing, registration growth and realloc failure, stale index lookup, unregister swapping, select mask changes, dispatch resize after changes, handler invocation flags, destroy-mode loop exit, close-on-unregister, and behavior when multiple threads are requested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/event-poll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/event.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/event.c

## Purpose
This file is the backend-neutral public facade for GlusterFS event handling. It chooses epoll or poll, forwards registration and dispatch operations through `event_ops`, and coordinates event-poller shutdown.

## Important APIs, types, and functions
Public APIs include `gf_event_pool_new`, `gf_event_register`, `gf_event_unregister`, `gf_event_unregister_close`, `gf_event_select_on`, `gf_event_dispatch`, `gf_event_reconfigure_threads`, `gf_event_dispatch_destroy`, `gf_event_pool_destroy`, and `gf_event_handled`. The shutdown helper uses `struct event_destroy_data` and `poller_destroy_handler`.

## Control flow
`gf_event_pool_new()` tries `event_ops_epoll.new()` when epoll is compiled in and falls back to `event_ops_poll.new()` on failure. Other wrapper APIs validate the pool and call the selected backend. `gf_event_dispatch_destroy()` creates a nonblocking pipe, registers the read end, marks the pool as destroy mode, reconfigures event threads to zero, writes wakeups to the pipe while waiting on `event_pool->cond`, unregisters the pipe, and closes both fds.

## State and persistence behavior
The facade mutates backend event-pool state: selected `ops`, destroy flag, active thread count, and registered destroy pipe. No persistent storage occurs. `gf_event_pool_destroy()` only destroys the pool if destroy mode is set and active thread count is zero.

## Dependencies and integration points
It depends on `glusterfs/gf-event.h`, `timespec_now_realtime`, syscall wrappers, pthread condition waits, and the backend symbols from `event-epoll.c` and `event-poll.c`. RPC transports and other async subsystems call this facade instead of backend-specific APIs.

## Risks and edge cases
Shutdown is timing-sensitive: the destroy pipe must wake all pollers, handlers must drain it and call `gf_event_handled()`, and the retry count is bounded by the prior thread count plus ten. If pipe registration fails, cleanup closes fds but may leave destroy not set. `gf_event_pool_destroy()` silently refuses destruction if called before dispatch destroy completes. The parameter names in `poller_destroy_handler()` swap `poll_out` and `poll_in`, though only handled cleanup matters there.

## Test signals
Tests should cover epoll selection, poll fallback, wrapper validation failures, dispatch destroy with active pollers, timeout/retry behavior, destroy pipe cleanup, refusal to destroy before shutdown, `gf_event_handled()` delegation on epoll and no-op behavior on poll, and failure injection for pipe/register/write paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/events.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/events.c

## Purpose
This file sends GlusterFS event notifications as UDP datagrams to the configured event receiver. It formats event type, timestamp, and a caller-provided message into a compact string.

## Important APIs, types, and functions
The exported API is `_gf_event(eventtypes_t event, const char *fmt, ...)`. It uses `EVENT_PORT` 55555, default localhost behavior, `EVENT_LAST` validation, and event error/status constants such as `EVENT_SEND_OK`, `EVENT_ERROR_RESOLVE`, `EVENT_ERROR_SOCKET`, `EVENT_ERROR_MSG_FORMAT`, and `EVENT_ERROR_SEND`.

## Control flow
The function validates the event id, inspects `THIS->ctx->cmd_args` for `volfile_server` and `volfile_server_transport`, resolves either the volfile server or localhost with `getaddrinfo()`, creates the first usable datagram socket, formats the caller message with `gf_vasprintf()`, prefixes it with `gf_time()` and event id using `gf_asprintf()`, sends it with `sendto()`, then closes and frees resources.

## State and persistence behavior
There is no retained process state. Each event creates a socket, sends one datagram, and closes it. Delivery is best-effort UDP with no retry, acknowledgement, or persistence.

## Dependencies and integration points
The file depends on networking headers, `glusterfs/events.h`, `glusterfs/globals.h`, syscall wrappers, GlusterFS allocation helpers, and the active translator context through `THIS`. It integrates with CLI/daemon event consumers listening on the fixed event port.

## Risks and edge cases
The code assumes `THIS` and `THIS->ctx` are valid; early startup or non-translator contexts could crash. `getaddrinfo()` uses `AI_ADDRCONFIG`, which can surprise IPv4/IPv6-only environments. The host selection ignores unix volfile transport and otherwise targets the volfile server for clients. UDP send failures are reported only as status codes. Large formatted messages can exceed practical datagram size and be dropped or fragmented.

## Test signals
Tests should cover invalid event ids, localhost and volfile-server host selection, unix transport fallback, DNS failure, socket failure across addrinfo entries, format allocation failure, send failure, successful datagram contents with timestamp/event/message, and behavior with NULL or unavailable context where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/fd-lk.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/fd-lk.c

## Purpose
This file maintains a per-file-descriptor lock context that tracks and merges byte-range locks. It records active ranges, coalesces compatible locks, splits or removes ranges on unlock/conflicting updates, and exposes an empty-context check.

## Important APIs, types, and functions
Public APIs include `fd_lk_ctx_create`, `fd_lk_ctx_ref`, `fd_lk_ctx_unref`, `fd_lk_insert_and_merge`, `fd_lk_ctx_empty`, and `fd_lk_overlap`. Internal helpers manage lock nodes: `_fd_lk_delete_lock`, `_fd_lk_destroy_lock`, `_fd_lk_destroy_lock_list`, `fd_lk_ctx_node_new`, `_fd_lk_add_locks`, `_fd_lk_sub_locks`, `_fd_lk_insert_and_merge`, and `_fd_lk_delete_unlck_locks`.

## Control flow
`fd_lk_insert_and_merge()` references `fd->lk_ctx`, creates a node from the requested `gf_flock`, locks the context, recursively merges it into the list, prints debug state, unlocks, and unreferences the context. Overlapping ranges of the same type are combined. Overlapping ranges of different types create a union range, subtract the new lock from the union, delete old nodes, recursively insert resulting fragments, and remove `F_UNLCK` entries.

## State and persistence behavior
State is an in-memory `fd_lk_ctx_t` with an atomic refcount, mutex, and `lk_list` of `fd_lk_ctx_node_t`. Ranges store normalized `fl_start` and inclusive `fl_end`; `l_len == 0` maps to `LLONG_MAX`. There is no disk persistence. Destruction occurs when the context refcount reaches zero.

## Dependencies and integration points
It depends on `glusterfs/fd.h`, `glusterfs/fd-lk.h`, lock owner/type formatting helpers, `gf_flock_copy`, atomics, list macros, and GlusterFS allocation/logging. It is attached to `fd_t` and used by lock handling paths that need local knowledge of fd-associated locks.

## Risks and edge cases
Recursive merge/split logic is subtle and allocation failures can leave the list partly updated or silently drop the requested lock. `_fd_lk_delete_unlck_locks()` initializes `ret = -1` and never sets success, though callers ignore it. `_fd_lk_sub_locks()` copies whole nodes with list pointers and then callers reinitialize list heads; any missed path could corrupt lists. Range math can overflow when computing `flock->l_start + flock->l_len - 1`. Debug printing assumes initialized owner/type fields.

## Test signals
Tests should cover non-overlap insertion, same-type coalescing, unlock exact match, unlock middle split into two retained ranges, left/right edge overlaps, opposing lock type replacement, `l_len == 0` infinite ranges, negative or overflowing range inputs, allocation failure during split, refcount destruction, and `fd_lk_ctx_empty()` under concurrent access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/fd-lk.c -->
