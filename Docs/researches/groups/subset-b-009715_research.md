# Research: subset-b-009715

Grouped research for NFS-Ganesha include files under `sources/user-network-fs/nfs-ganesha/src/include`. Each source section preserves the source path in the title and is wrapped with reconciliation markers for source-tree-aligned per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/common_utils.h -->
# sources/user-network-fs/nfs-ganesha/src/include/common_utils.h

## Purpose
`common_utils.h` is a central utility contract for NFS-Ganesha C code. It collects portability shims, compile-time checks, thread/lock wrappers with logging, time helpers, DNS/statistics wrappers, byte-buffer comparison, and strict small integer parsing. Because it is included widely by SAL, FSAL, logging, idmapper, RPC, and test code, changes here have cross-tree effects.

## Important APIs, Types, And Functions
The header exposes global pthread attributes (`default_mutex_attr`, `default_rwlock_attr`) and the global `PTHREAD_stack_size` used by the `PTHREAD_create` wrapper. `BUILD_BUG_ON`, `ARRAY_SIZE`, `CONCAT`, `UNUSED`, `SCANDIR_CONST`, and `HAVE_MNTENT_H` are compile-time/platform helpers. The pthread wrappers (`PTHREAD_MUTEX_*`, `PTHREAD_RWLOCK_*`, `PTHREAD_COND_*`, `PTHREAD_SPIN_*`, and attribute wrappers) wrap POSIX primitives, log to `COMPONENT_RW_LOCK`, and abort on unexpected errors. Inline helpers include `PTHREAD_mutex_trylock`, `PTHREAD_cond_timedwait`, `timespec_diff`, `timespec_update`, `timespec_to_nsecs`, `nsecs_to_timespec`, `timespec_add_nsecs`, `timespec_sub_nsecs`, `gsh_time_cmp`, `gsh_buffdesc_comparator`, `now`, `now_mono`, `gsh_gethostname`, `gsh_getaddrinfo`, `gsh_getnameinfo`, and `parse_uint16_from_str`.

## Control Flow
The lock/condition wrappers are macros, so control flow is injected at call sites: call POSIX primitive, log on success at full debug, log critical and `abort()` on non-recoverable return values. `PTHREAD_mutex_trylock` and `PTHREAD_cond_timedwait` are softer wrappers that treat `EBUSY` and `ETIMEDOUT` as expected outcomes. `PTHREAD_create` initializes a scratch attr if needed, applies the configured stack size, and delegates to `pthread_create`.

## State And Persistence
The header does not persist data to disk. It depends on external global state for logging levels, default pthread attributes, DNS statistics, and thread stack size. Time helpers read system clocks. `timespec_update` writes `tv_sec` and `tv_nsec` via atomic stores to allow low-cost publication of timestamp snapshots.

## Dependencies And Integration Points
It depends on libc/POSIX headers, `abstract_atomic.h`, `gsh_types.h`, `log.h`, and later `idmapper.h` for DNS statistics. It is foundational for code that uses the project-specific pthread wrappers, including the thread fridge, export manager, delayed executor, FSAL, connection manager, and logging code.

## Risks
Macro wrappers evaluate pointer arguments once but still change debugging and abort semantics globally. The wrappers assume most pthread errors are fatal, which is appropriate for core locks but risky for code that might otherwise recover. `config_error_no_error`-style aliasing is not here, but this file does perform atomic stores through casted `timespec` fields and assumes field sizes match `uint64_t`. `parse_uint16_from_str` relies on `errno`, so callers must include the correct headers through existing transitive includes. `timespec_sub_nsecs` computes `tv_nsec = ts.tv_nsec - t->tv_nsec` in the borrow case, which is unusual and should be tested before reuse in new code.

## Test Signals
Useful tests include compile-only checks for platform shims, lock-wrapper smoke tests under high log levels, timed-wait tests for `ETIMEDOUT`, thread creation tests honoring `PTHREAD_stack_size`, strict parser cases for empty strings, trailing characters, overflow, and `UINT16_MAX`, and time arithmetic tests across second/nanosecond boundaries. Existing usage in `support/fridgethr.c`, `support/delayed_exec.c`, `support/exports.c`, `log/display.c`, and FSAL tests gives integration coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/common_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/conf_url.h -->
# sources/user-network-fs/nfs-ganesha/src/include/conf_url.h

## Purpose
`conf_url.h` defines the pluggable configuration URL interface used by config parsing to fetch configuration content from non-local backends, currently shaped around `rados://` URLs.

## Important APIs, Types, And Functions
`struct gsh_url_provider` is the provider registration object with a list node, provider name, lifecycle hooks (`url_init`, `url_shutdown`), and `url_fetch`. Public functions are `config_url_init`, `config_url_shutdown`, `register_url_provider`, `config_url_fetch`, and `config_url_release`. The header also declares RADOS watch helpers `gsh_rados_url_setup_watch` and `gsh_rados_url_shutdown_watch`.

## Control Flow
The implementation initializes a provider list, an rwlock, a simple URL regex, and conditionally loads `libganesha_rados_urls.so`. Providers register themselves with `register_url_provider`; `config_url_fetch` regex-matches the scheme and dispatches to the matching provider's `url_fetch`; `config_url_release` closes the returned `FILE *` and frees the backing buffer.

## State And Persistence
State lives in `conf_url.c`: a global provider list, rwlock, compiled regex, and optional dlopen handle. Fetches may materialize remote content into a buffer and `FILE *` stream. Persistent backing storage is provider-specific; this generic layer only owns transient fetch buffers and dynamic library state.

## Dependencies And Integration Points
It depends on `gsh_list.h`, `stdio.h`, `regex`, `dlfcn`, logging, and optional RADOS URL module symbols. It integrates with the parser's ability to read config from URLs and with RADOS URL watch setup during service registration.

## Risks
`register_url_provider` sets `code = EEXIST` on duplicate names but still calls `url_init` and adds the new provider, so duplicate registration behavior is hazardous. The regex only recognizes `rados://`, so adding schemes requires implementation changes. `config_url_release` uses `free(fbuf)` while most of the tree uses `gsh_free`; provider allocation must match this contract. URL fetch output ownership must be followed exactly to avoid leaks or double frees.

## Test Signals
Tests should cover initialization/shutdown idempotence, duplicate provider registration, malformed URLs, quoted and unquoted `rados://` strings, missing RADOS backend library, failed provider fetch, successful fetch/release, and concurrent fetch/registration behavior under the provider rwlock.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/conf_url.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/conf_url_rados.h -->
# sources/user-network-fs/nfs-ganesha/src/include/conf_url_rados.h

## Purpose
`conf_url_rados.h` is the build-gated public interface for the RADOS-backed configuration URL provider. It only exposes declarations when `RADOS_URLS` is enabled in generated `config.h`.

## Important APIs, Types, And Functions
When enabled, it includes `librados.h` and declares `gsh_rados_url_setup_watch`, `gsh_rados_url_shutdown_watch`, and `register_service_to_ceph`. These functions bridge generic config URL handling to Ceph/RADOS service discovery and watch behavior.

## Control Flow
The generic `conf_url.c` code dynamically loads the RADOS URL module and resolves setup/shutdown watch callbacks. Provider initialization is expected to happen from the RADOS module package init, which registers a `gsh_url_provider` with the generic URL layer.

## State And Persistence
The header itself has no state. Runtime state is in the RADOS provider and may include librados cluster/ioctx handles, watches, object contents, and service registration data in Ceph. That state persists externally in the Ceph cluster as defined by the provider.

## Dependencies And Integration Points
It depends on generated feature macro `RADOS_URLS`, `gsh_list.h`, `stdbool.h`, and `<rados/librados.h>`. It integrates with `conf_url.h`, the RADOS URL shared library, and any cluster service registration path that calls `register_service_to_ceph`.

## Risks
All declarations disappear when `RADOS_URLS` is unset, so callers must be feature-gated or use the generic no-op wrappers in `conf_url.h`. Linking directly against these functions in a non-RADOS build will fail. The provider involves external Ceph credentials, network state, and watch lifetimes, so shutdown ordering is important.

## Test Signals
Build matrix coverage should include both `RADOS_URLS=ON` and `OFF`. Runtime tests need missing librados/backend handling, successful provider registration, watch setup/shutdown, Ceph service registration, URL fetch of existing and missing objects, and shutdown after failed partial initialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/conf_url_rados.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/config-h.in.cmake -->
# sources/user-network-fs/nfs-ganesha/src/include/config-h.in.cmake

## Purpose
`config-h.in.cmake` is the CMake template for generated `config.h`. It centralizes version strings, install/runtime paths, OS markers, and build feature macros that conditionally compile large parts of NFS-Ganesha.

## Important APIs, Types, And Functions
The key macro helper is `GSH_CHECK_VERSION`. Version macros include `GANESHA_VERSION_MAJOR`, `GANESHA_VERSION_MINOR`, `GANESHA_EXTRA_VERSION`, `GANESHA_VERSION`, `GANESHA_BUILD_RELEASE`, `VERSION_COMMENT`, `_GIT_HEAD_COMMIT`, `_GIT_DESCRIBE`, and `BUILD_HOST`. Feature macros include protocol support (`_USE_NFS3`, `_USE_NFS_RDMA`, `_USE_NLM`, `_USE_RQUOTA`, `_USE_9P`), dependencies (`USE_DBUS`, `HAVE_KRB5`, `USE_CAPS`, `USE_LTTNG`, `USE_MONITORING`), FSAL/ACL/Ceph/Gluster features, debug/sanitizer toggles, and `RADOS_URLS`. Path macros include `GANESHA_CONFIG_PATH`, `GANESHA_PIDFILE_PATH`, `NFS_V4_RECOV_ROOT`, `NFS_V4_RECOV_DIR`, `NFS_V4_OLD_DIR`, and `DEFAULT_NFS_CCACHE_DIR`.

## Control Flow
CMake expands `@...@` substitutions and `#cmakedefine` entries into concrete `#define` or commented-out macros. Downstream C files use these macros for preprocessor conditionals, not runtime branching.

## State And Persistence
The generated header persists build-time configuration into every compiled object. It embeds filesystem paths, module location, git/build identity, and feature decisions. Runtime persistence is indirect through code enabled by these macros.

## Dependencies And Integration Points
Almost every project header includes `config.h` directly or indirectly. It gates OS-specific headers in `extended_types.h`, optional RADOS URL declarations, FSAL features in `fsal.h` consumers, protocol compilation, debug code, and sanitizer/dlopen flags.

## Risks
Mismatched generated config and installed modules can break dynamic loading or feature assumptions. Path macros are compiled in, so packaging mistakes affect default config, pidfile, recovery, and module locations. Feature macro combinations need broad build coverage; for example `SANITIZE_ADDRESS` changes dlopen flags and `RADOS_URLS` changes URL provider behavior.

## Test Signals
Test signals are mostly build/configuration matrix checks: minimal build, Linux/FreeBSD/Darwin where supported, DBus on/off, RADOS URLs on/off, sanitizer builds, Ceph/Gluster FSAL options, NFS protocol subsets, and packaging tests that verify generated paths and version strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/config-h.in.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/config_parsing.h -->
# sources/user-network-fs/nfs-ganesha/src/include/config_parsing.h

## Purpose
`config_parsing.h` defines the public data model and helper macros for parsing Ganesha configuration files into typed C structures. It is the contract used by core config blocks, exports, FSAL modules, logging, recovery, and DBus update paths.

## Important APIs, Types, And Functions
Core opaque type `config_file_t` points at `struct config_root`. `enum term_type` describes lexer/parser terms; `enum config_type` describes target field types. `struct config_error_type` records categorized scan, parse, init, FSAL, uniqueness, validation, missing, deprecated, dispose, and internal errors plus a diagnostic memstream. `struct config_item_list` maps tokens to bit values. `struct config_item` describes one config parameter, with unions for booleans, strings/paths, IPs, integer ranges, FSIDs, lists/enums/tokens, boolbits, nested blocks, procedural handlers, and deprecated items. `struct config_block` wraps a top-level or nested block descriptor.

## Control Flow
Callers define static `config_item` arrays using `CONF_ITEM_*`, `CONF_MAND_*`, `CONF_RELAX_BLOCK`, `CONF_ITEM_BLOCK`, `CONF_ITEM_PROC_MULT`, and `CONFIG_EOL`. `config_ParseFile` builds a parse tree. `load_config_from_parse` walks matching blocks from the root, calls block `init`, validates and converts individual terms, then calls block `commit`. `load_config_from_node` does the same from a specific parse node. Error helpers classify whether accumulated errors are fatal, critical, harmless, or export-specific critical.

## State And Persistence
The parser owns an in-memory parse tree freed by `config_Free`. The parse root carries a generation number used by exports to track config updates. `config_error_type` can own a diagnostic buffer/memstream when initialized dynamically. Configuration persistence remains in the input file or URL; this API only transforms it into live process state.

## Dependencies And Integration Points
The header depends on standard C headers and is implemented by `config_parsing.c` plus lexer/parser files. It integrates with `support/exports.c` for export blocks, `FSAL/fsal_manager.c` for FSAL loading/configuration, logging config, recovery config, MDCACHE config, and FSAL-specific export blocks.

## Risks
The error-combining helpers treat the leading bitfield portion of `struct config_error_type` as a `uint16_t`, which is layout-sensitive and must be updated if the bitfield count grows. Offset macros depend on exact target structure/member names. `CONFIG_MARK_SET` writes bit masks through `set_off`, so incorrect offsets corrupt adjacent config state. Commit/init callbacks have nuanced ownership rules; returning allocated block memory or freeing it on errors must match parser expectations.

## Test Signals
Tests should parse valid and invalid config files, verify mandatory/unique/relaxed/deprecated handling, exercise all integer ranges and octal mode parsing, validate block init/commit/free paths, confirm diagnostic buffers, and verify export update generation behavior. Existing `config_parsing/test_parse.c` and `verif_syntax.c` are direct parser signals; export and FSAL startup tests provide integration coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/config_parsing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/connection_manager.h -->
# sources/user-network-fs/nfs-ganesha/src/include/connection_manager.h

## Purpose
`connection_manager.h` declares the clustered connection manager that ensures an NFS client is active on only one Ganesha server at a time. It mitigates NFSv4 exactly-once-semantics hazards when load balancing can move a client before older requests finish on another server.

## Important APIs, Types, And Functions
The API centers on `connection_manager__client_t`, embedded in `gsh_client`, and `connection_manager__connection_t`, embedded in XPRT custom data. Important enums are drain results, registration results, client states (`DRAINED`, `ACTIVATING`, `ACTIVE`, `DRAINING`), and connection-start results. Callback types register/deregister connections and drain other servers. Public functions set/clear callbacks, initialize the module and per-client state, initialize/start/finish connections, test drain success, and drain local client connections.

## Control Flow
New XPRTs call `connection_manager__connection_init`, then `connection_manager__connection_started` after the client address is known. If connection management is disabled or the address is loopback, the connection is allowed unmanaged. For managed clients, `DRAINED` transitions to `ACTIVATING`, invokes the cluster callback to register and drain other servers, then becomes `ACTIVE` or reverts to `DRAINED`. Active clients register additional connections directly. A local drain request transitions `ACTIVE` to `DRAINING`, sets TCP linger to RST quickly, calls `SVC_DESTROY` on each connection, waits for connection finish notifications, and then marks the client `DRAINED` or `ACTIVE` depending on remaining connections.

## State And Persistence
State is in memory: per-client mutex, condition variable, list of managed connections, connection count, per-connection XPRT/client pointers, destruction flag, and destroy start time. Metrics are updated for states, connection-start latency/result, and drain latency/result. No state is persisted across restart; cluster registration persistence is delegated to callbacks.

## Dependencies And Integration Points
The header depends on `common_utils.h`, RPC `SVCXPRT`, `gsh_client`, `network_id`, and Ganesha socket utilities. Implementation integrates with `client_mgr.c`, `xprt_handler.h`, `connection_manager_metrics`, `nfs_param.core_param.enable_connection_manager`, callback providers for cluster coordination, and LTTng tracepoints.

## Risks
Correctness depends on callback implementations being registered before managed traffic arrives and on callbacks deregistering exactly once after successful registration. The header documents lease extension after drain, but implementation currently carries a TODO, so reclaim windows are a known correctness risk. New incoming connections abort local draining by moving `DRAINING` back to `ACTIVE`, which is intentional priority behavior but must be understood by cluster callbacks. Stuck destroyed connections are detected only after timeout multiples.

## Test Signals
Tests should cover disabled manager, loopback bypass, callback default refusal, successful first activation, concurrent activation waiters, additional active connections, drain with no local client, drain of active connections, drain aborted by new connection, timeout/stuck detection, deregister-on-finish, callback clear/set assertions, and metrics label updates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/connection_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/delayed_exec.h -->
# sources/user-network-fs/nfs-ganesha/src/include/delayed_exec.h

## Purpose
`delayed_exec.h` declares a small delayed task executor for scheduling callback work after a nanosecond delay. It is intentionally simpler than the thread fridge and is used for upcall retry/recall/revoke style operations.

## Important APIs, Types, And Functions
The public API is `delayed_start`, `delayed_shutdown`, and `delayed_submit(void (*)(void *), void *, nsecs_elapsed_t)`. Delays are expressed in the project `nsecs_elapsed_t` type from `gsh_types.h`.

## Control Flow
`delayed_start` initializes a mutex, condition variable, AVL tree of execution times, and one detached executor thread. `delayed_submit` computes a realtime due date, inserts a task into an AVL bucket keyed by that time, and wakes the executor if the new task is earliest. The executor waits indefinitely when empty, timed-waits until the next due time, pops due tasks, unlocks, runs callbacks, and repeats. `delayed_shutdown` blocks new submissions, waits for active submitters, signals the thread, waits up to 120 seconds, and cancels remaining threads if needed.

## State And Persistence
State is process-local: an AVL timer tree, task lists, executor thread list, mutex, condition variable, `deny_submission`, active submitter count, and running/stopping state. There is no disk persistence. Pending tasks are lost on process shutdown.

## Dependencies And Integration Points
The implementation depends on pthreads, RCU thread registration, project AVL/list/memory/log utilities, `common_utils.h`, and atomic helpers. Callers include `FSAL_UP/fsal_up_top.c` for layout recall, delegation recall, revoke checks, and async returns.

## Risks
Only one executor thread is started, so long-running callbacks delay all later tasks. Callbacks execute outside the executor mutex but still share one worker. `delayed_submit` allocates before taking the lock and returns `EAGAIN` after shutdown begins. Shutdown uses asynchronous cancellation if the detached thread does not exit cleanly, so callback code must tolerate abrupt process teardown. Time is based on `CLOCK_REALTIME` via `now`, so wall-clock jumps can affect scheduling.

## Test Signals
Tests should verify zero-delay execution, ordered delayed execution, multiple tasks with identical due times, earliest-task wakeup, submission during shutdown, long callback behavior, shutdown with no tasks, shutdown while tasks are pending, and caller integration for upcall retries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/delayed_exec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/display.h -->
# sources/user-network-fs/nfs-ganesha/src/include/display.h

## Purpose
`display.h` defines a safe append-only string formatting buffer used throughout Ganesha logging and diagnostics. It provides primitives for printf-style appending, string concatenation, truncation, and rendering opaque data as printable strings or hex.

## Important APIs, Types, And Functions
`struct display_buffer` stores total size, start pointer, and current append pointer. Core APIs are `display_buffer_remain`, `display_start`, `display_finish`, `display_force_overflow`, `display_reset_buffer`, `display_buffer_len`, `display_vprintf`, `display_printf`, `display_opaque_bytes_flags`, `display_opaque_bytes`, `display_opaque_value_max_impl`, `display_opaque_value_max`, `display_opaque_value`, `display_len_cat`, `display_cat`, and `display_cat_trunc`. Opaque rendering flags control hex case, `0x` prefix, invalid argument handling, and truncation policy.

## Control Flow
Display primitives call `display_start`, copy or format bounded bytes, then call `display_finish`. Once a buffer fills, implementation marks overflow and writes an ellipsis while trying not to split a UTF-8 character. Non-primitive display routines may compose other display functions and rely on the last primitive to finish the buffer.

## State And Persistence
The only state is caller-owned buffer memory and the current pointer. There is no global state and no persistence. Overflow is represented by moving `b_current` to the logical end and leaving a valid NUL-terminated truncated string.

## Dependencies And Integration Points
It depends on libc formatting/string headers and is implemented by `log/display.c`. Callers include NFS state owner/session display, NLM utilities, file handle display macros, FSAL attribute logging, export option logging, recovery code, and handle mapping code.

## Risks
Callers must initialize `struct display_buffer` with valid size/start/current values and must not write directly without respecting `display_start`/`display_finish`. Small buffers below four bytes are forced empty/overflowed. Return values matter: callers that ignore `<=0` will not overflow memory, but diagnostic output may be incomplete. Opaque value display scans `len` bytes for printability even when `max` is smaller, so very large inputs can cost more than expected.

## Test Signals
`log/test_display.c` exercises repeated appends, overflow, reset, printf, and opaque rendering with printable and non-printable inputs. Additional tests should cover invalid buffers, tiny buffers, UTF-8 truncation, invalid length/null/empty flags, `OPAQUE_BYTES_NO_TRUNC`, uppercase/lowercase hex, and nested display functions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/display.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/err_inject.h -->
# sources/user-network-fs/nfs-ganesha/src/include/err_inject.h

## Purpose
`err_inject.h` is a compile-time gated interface for worker-delay error injection. It is only active when `_ERROR_INJECTION` is defined.

## Important APIs, Types, And Functions
When enabled, the header declares global delay controls `worker_delay_time` and `next_worker_delay_time`, plus `init_error_injector`. With `_ERROR_INJECTION` disabled, it contributes no declarations.

## Control Flow
The intended flow is build-time opt-in, initialize the injector, then have worker code consult or update the delay globals to introduce controlled timing faults. The header itself contains no logic.

## State And Persistence
The active state is global process memory. There is no persistence; injected behavior lasts only for the process and build configuration.

## Dependencies And Integration Points
It has no includes. Integration depends on code compiled under `_ERROR_INJECTION` that defines and uses these globals. It is a testing/debug hook rather than production API.

## Risks
Because declarations vanish outside error-injection builds, all usage must be preprocessor-gated. Global mutable delay state is inherently racy unless implementation adds synchronization. Leaving `_ERROR_INJECTION` enabled in production would intentionally alter worker timing.

## Test Signals
Build tests should include injection enabled and disabled. Runtime tests should verify injector initialization, one-shot versus persistent delay behavior, and absence of unresolved symbols in normal builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/err_inject.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/export_mgr.h -->
# sources/user-network-fs/nfs-ganesha/src/include/export_mgr.h

## Purpose
`export_mgr.h` declares the export manager: the in-memory registry, locking protocol, lookup APIs, mount/unmount work, reference handling, and config hooks for NFS exports.

## Important APIs, Types, And Functions
`struct gsh_export` represents an export with list/tree nodes, state/lock/share lists, root and junction object handles, parent/mounted export links, FSAL export pointer, full and pseudo paths, QoS fields, read/write size limits, filesystem ID, permissions, refcount, lock, options, export ID, status, pNFS marker, mount/update flags, and config generation. Admin helpers are `EXPORT_ADMIN_LOCK`, `EXPORT_ADMIN_UNLOCK`, `EXPORT_ADMIN_TRYLOCK`, `is_export_admin_counter_valid`, and `is_export_update_in_progress`. Public APIs allocate/insert/get/find/mount/unmount/remove/iterate exports, manage references, revert and queue mount/unexport work, prune/remove exports, initialize stats time, handle async delegation transitions, and parse export ID lists.

## Control Flow
Configuration creates or updates exports through config blocks in `support/exports.c`. `alloc_export` creates a referenced export; commit paths validate FSAL/export parameters, initialize roots, mount into pseudo-fs, insert into the export AVL/list registry, and drop config references. Runtime lookups fetch by ID, path, pseudo path, or tag. Updates take `export_admin_mutex`, increment `export_admin_counter` before and after mutation, and use work queues for mount/unexport cleanup.

## State And Persistence
Export state is live process memory backed by FSAL object handles and refcounted path strings. `config_gen` records which parse-tree generation last touched an export. Export definitions persist in the configuration source, not in this header. `nfs_stats_time` captures stats timing.

## Dependencies And Integration Points
It depends on list/AVL/atomic utilities and `fsal.h`. It integrates tightly with `support/exports.c`, pseudo-fs construction, `op_ctx`, FSAL export creation, NFS state lists, pNFS helpers, QoS, conditional logging export ID filters, and DBus export update paths.

## Risks
The lock hierarchy matters: export admin updates use a mutex/seqlock pattern, while individual exports have rwlocks and RCU-refcounted paths. Incorrect reference handling can free exports while objects still point at them. The admin counter is non-atomic by design, so it is advisory and can have false negatives. Update paths must preserve static config fields versus atomically changeable fields and must avoid ABBA deadlocks with `export_opt_lock`.

## Test Signals
Tests should cover export allocation/refcounting, duplicate export IDs, lookup by ID/path/pseudo/tag, mount/unmount work queues, dynamic add/update/remove, seqlock retry detection, stale export shortcuts, path ref acquisition/release, FSAL max read/write adjustment, pNFS export handling, and config reload pruning/remounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/export_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/extended_types.h -->
# sources/user-network-fs/nfs-ganesha/src/include/extended_types.h

## Purpose
`extended_types.h` supplies platform-dependent type compatibility definitions used by older Ganesha code and filesystem interfaces.

## Important APIs, Types, And Functions
It includes generated `config.h`, then includes OS-specific extended type headers for Linux or FreeBSD. It defines `longlong_t`, `u_longlong_t`, `uint_t`, and maps missing `ENOATTR` to `ENODATA`.

## Control Flow
All behavior is preprocessor selection. `LINUX` and `FREEBSD` macros from generated config choose the OS-specific include path. If `ENOATTR` is unavailable, the fallback macro is defined.

## State And Persistence
No runtime state or persistence exists. The header affects compile-time type names and errno compatibility.

## Dependencies And Integration Points
It depends on `config.h`, `<sys/types.h>`, and OS-specific headers under `os/linux` or `os/freebsd`. It integrates with FSAL and xattr-facing code that expects Solaris/BSD-style type names or `ENOATTR`.

## Risks
Mapping `ENOATTR` to `ENODATA` overlays errno semantics on Linux, which is intentional but can surprise code that distinguishes them elsewhere. Unsupported OS macros may skip platform headers. Type aliases may conflict if platform headers define them differently.

## Test Signals
Build tests on Linux and FreeBSD are the main signal. Compile checks should verify the aliases and `ENOATTR` availability, and xattr tests should validate expected no-attribute error mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/extended_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/fridgethr.h -->
# sources/user-network-fs/nfs-ganesha/src/include/fridgethr.h

## Purpose
`fridgethr.h` declares Ganesha's thread fridge, a POSIX-thread pool abstraction used for request decoding, async state work, idmapper reaping, FSAL upcalls, FD LRU cleanup, and other background loops.

## Important APIs, Types, And Functions
Core types are opaque `struct fridgethr`, `struct fridgethr_entry`, nested `struct fridgethr_context`, `struct fridgethr_params`, and `struct fridgethr_work`. `fridgethr_flavor_t` selects worker versus looper behavior. `fridgethr_defer_t` selects fail-fast versus queueing when full. Commands are run, pause, and stop. Public APIs initialize/destroy fridges, submit work, wake loopers, pause/stop/start asynchronously, run synchronous commands, ask a looper whether it should break, populate looper threads, adjust per-context wait, cancel threads, and initialize/shutdown the global `general_fridge`.

## Control Flow
`fridgethr_submit` dispatches to an idle thread, spawns if below `thr_max`, queues if allowed, or returns `EWOULDBLOCK`. Worker threads repeatedly run `ctx.func`, call optional cleanup, then freeze waiting for more work, timeout, pause, or stop. Looper fridges run a submitted function repeatedly with `thread_delay` sleeps and optional wake callbacks. Pause/start/stop set command state and notify completion through callback/condition variables; `fridgethr_sync_command` wraps those transitions with a timeout.

## State And Persistence
Fridge state is entirely in memory: thread lists, idle queues, queued work, command state, transition callback state, pthread attrs/locks, per-thread context, flags, and wait timeout. The global `op_ctx` TLS is declared in `fsal.h` but actually defined in `fridgethr.c`, so fridge threads are central to request-local context handling.

## Dependencies And Integration Points
It depends on project list and wait queue utilities, pthread wrappers from `common_utils.h` in implementation, RCU thread registration, logging, and `nfs_core.h`. Integration points include `state_async.c`, `idmapper.c`, `log_functions.c`, `FSAL_UP/fsal_up_async.c`, `FSAL/commonlib.c`, and FSAL-specific async fridges.

## Risks
Thread cancellation is asynchronous during hard teardown, so code running in fridge threads must be robust to process shutdown paths. Queueing fridges can accumulate unbounded work unless callers bound submissions. Transition state rejects overlapping pause/start/stop with `EBUSY`. Looper and worker parameters have strict compatibility rules, especially `wake_threads` only for loopers and no queue deferment for loopers.

## Test Signals
Tests should cover invalid parameters, submit with null/stopped/paused fridges, dispatch to idle threads, spawn up to `thr_max`, queued work drain, worker timeout exit above `thr_min`, pause/start/stop callbacks and sync timeouts, looper wake behavior, task cleanup, thread init/finalize hooks, and global fridge init/shutdown.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/fridgethr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/fsal.h -->
# sources/user-network-fs/nfs-ganesha/src/include/fsal.h

## Purpose
`fsal.h` is the main File System Abstraction Layer public header for Ganesha core code. It declares operation context handling, FSAL module loading/registration/configuration, common FSAL operation wrappers, attribute helpers, async I/O helpers, and FD LRU configuration.

## Important APIs, Types, And Functions
The header declares thread-local `op_ctx`, global `pnfs_fsal`, delegation config tokens, root export options, cluster node identifiers, and context functions such as `init_op_context`, `release_op_context`, `suspend_op_context`, `resume_op_context`, and export/client/pNFS setters. FSAL manager APIs include `load_fsal_static`, `register_fsal`, `unregister_fsal`, `lookup_fsal`, `load_fsal`, `fsal_load_init`, `fsal_init`, `subfsal_commit`, `start_fsals`, `destroy_fsals`, and cleanup routines. Operation helpers wrap access, lookup, create, readdir, remove, rename, open/reopen/close, statfs, commit, verify, read/write, xattr listing, and attribute display/logging.

## Control Flow
During startup/config, `start_fsals` and export parsing load FSAL modules by name. `load_fsal` dlopens module shared objects, resolves `fsal_init` if constructors do not register, and expects `register_fsal` to publish the module with default ops. `fsal_load_init` then calls module `init_config` or `update_config`. Protocol operations set `op_ctx`, then call FSAL wrapper functions that validate common conditions and dispatch through `fsal_obj_handle->obj_ops` or `fsal_module->m_ops`.

## State And Persistence
FSAL module state is process memory: module list under `fsal_lock`, per-module refcounts, operation vectors, server/handle/export lists, dlopen handles, paths, configured flags, and pNFS table entries. `op_ctx` is thread-local and must be set for operations expecting request/export/client credentials. FD LRU state tracks global FD counters and policy parameters. Persistent state belongs to backing filesystems or recovery/config subsystems, not this header.

## Dependencies And Integration Points
It depends on `fsal_api.h`, NFS protocol headers, ACL and fs_locations headers, config parsing, display buffers, and FSAL access-check helpers. It integrates with `FSAL/fsal_manager.c`, `FSAL/commonlib.c`, exports, SAL state code, protocol handlers, pNFS utilities, MDCACHE, recovery, and FSAL plugin modules.

## Risks
`lookup_fsal` sets `op_ctx->fsal_module`, so callers need a valid operation context. Attribute copying has nuanced ownership for ACLs, fs_locations, and security labels; misuse can leak or double-release references. `fsal_close` silently normalizes `ERR_FSAL_NOT_OPENED` for regular files and ignores non-regular files. Dynamic loading is sensitive to generated module paths, lowercase basename conversion, API version checks, and registration state. FD LRU settings influence resource exhaustion behavior.

## Test Signals
Test signals include FSAL dynamic/static load and version mismatch tests, config init/update paths, refcounted lookup/unregister, operation wrapper tests with mock `obj_ops`, attr prepare/copy/release ownership tests, close/commit edge cases, async read/write completion, xattr listing cookie behavior, FD LRU high/low water behavior, and integration tests under FSAL_MEM/VFS/proxy modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/fsal.h -->
