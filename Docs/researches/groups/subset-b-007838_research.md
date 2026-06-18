# Research Report: subset-b-007838

This grouped report covers the OrangeFS Windows client-service and client-test files assigned to `subset-b-007838`. Each file section preserves the original source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/dokany-interface.c -->
# sources/distributed-fs/orangefs/src/client/windows/client-service/dokany-interface.c

## Purpose
This is the Windows user-mode filesystem adapter that binds Dokany callbacks to OrangeFS client operations. It translates Dokany/Windows requests into `fs.c` wrapper calls, maps OrangeFS errors into NTSTATUS/Win32-style failures, converts between Unicode mount paths and OrangeFS paths, derives request credentials, and maintains per-open context plus IO caches.

## Important APIs, Types, And Functions
The central exported entry is `dokan_loop(PORANGEFS_OPTIONS options)`, which allocates `DOKAN_OPTIONS`, initializes `context_cache`, assigns `DOKAN_OPERATIONS`, and repeatedly invokes `DokanMain`. Dokany callbacks include `PVFS_Dokan_create_file`, `cleanup`, `close_file`, `read_file`, `write_file`, `flush_file_buffers`, `get_file_information`, `find_files_with_pattern`, `delete_file`, `delete_directory`, `move_file`, `set_allocation_size`, `set_file_time`, `get_disk_free_space`, and `get_volume_information`. `context_entry` stores a Dokany context id, open flags, and copied `PVFS_credential`. Helpers include `error_map`, `convert_wstring`, `convert_mbstring`, `get_fs_path`, `get_requestor_credential`, `get_credential`, `add_context`, `remove_context`, `check_perm`, `check_create_perm`, and `PVFS_sys_attr_to_file_info`.

## Control Flow
The mount loop is started by `service-main.c` and blocks in `DokanMain`. For open/create, Dokany flags are mapped with `DokanMapKernelToUserCreateFileFlags`, a request credential is loaded, a local path is converted to an OrangeFS path, existence and permissions are checked, and the callback dispatches to create, mkdir, truncate, or open validation. Successful opens assign a generated context and cache the credential. Read/write first try `io_cache_get` by context; on a miss they resolve the path to a `PVFS_object_ref`, perform `fs_read2`/`fs_write2`, then insert the ref into the IO cache. Directory enumeration pages through `fs_find_files`, converts each entry to `WIN32_FIND_DATAW`, and feeds Dokany’s fill callback.

## State And Persistence
The file owns process-local `context_cache` protected by `context_cache_mutex`; entries persist only for a Dokany open context and are removed on close. The IO cache is external but keyed by the same context. Persistent remote state is changed through OrangeFS operations: create/remove/rename/truncate/setattr/write/flush. The adapter synthesizes Windows metadata from OrangeFS attributes and reports the filesystem name as `NTFS` for compatibility while using OrangeFS volume name and fs id for visible volume fields.

## Dependencies And Integration Points
It depends on Dokany, Windows token/process/security APIs, OrangeFS `pvfs2.h`, `fs.h`, certificate helpers, credential helpers, `user-cache`, `io-cache`, `quickhash`, and gossip logging. Credential modes are controlled by global `goptions`; list, cert, and server modes are active, while LDAP support is commented out. This file is the primary integration surface between Windows filesystem consumers and the OrangeFS system-interface wrappers.

## Risks And Test Signals
Concurrency risk is high because Dokany can dispatch multiple threads against context and IO caches; mutex coverage protects qhash operations but returned cache entry pointers are used after unlock in some helpers. Memory cleanup is uneven: `PVFS_Dokan_cleanup` allocates `fs_path` for delete-on-close but does not free it before return, and several `MALLOC_CHECK` paths in enumeration can leak earlier allocations. `PVFS_Dokan_move_file` ignores `ReplaceIfExisting`. `PVFS_Dokan_set_end_of_file` is a no-op while allocation-size truncates, which may diverge from Windows expectations. Security descriptor support is mostly unimplemented. Client-test signals include create/open/read/write/flush/delete/rename/move/find/info/space tests, but locking, security descriptors, replace semantics, and many failure mappings are not directly tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/dokany-interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/fs.c -->
# sources/distributed-fs/orangefs/src/client/windows/client-service/fs.c

## Purpose
`fs.c` is the OrangeFS abstraction layer used by the Dokany adapter. It hides direct `PVFS_sys_*` calls behind path-oriented helpers for initialization, lookup, create, remove, rename, truncation, attributes, IO, directory listing, statfs, and shutdown.

## Important APIs, Types, And Functions
The global `tab` stores the parsed pvfstab. Public functions include `fs_initialize`, `fs_get_mntent`, `fs_resolve_path`, `fs_lookup`, `fs_create`, `fs_remove`, `fs_rename`, `fs_truncate`, `fs_getattr`, `fs_setattr`, `fs_mkdir`, `fs_io`, `fs_io2`, `fs_flush`, `fs_find_files`, `fs_get_diskfreespace`, `fs_get_id`, `fs_get_name`, and `fs_finalize`. Internal helpers include `split_path`, `sys_lookup_follow_links`, and `sys_get_symlink_attr`.

## Control Flow
Initialization parses a tab file, starts the PVFS system interface, and adds the first mount entry. Path resolution strips an optional drive prefix and translates backslashes to forward slashes. Namespace-changing calls split the requested path into parent and entry name, follow symlinks on the parent, then call the appropriate `PVFS_sys_create`, `PVFS_sys_mkdir`, `PVFS_sys_remove`, or `PVFS_sys_rename`. Attribute, truncate, flush, and deprecated path IO calls first resolve the target to an object ref. `fs_io2` bypasses lookup and operates on a supplied object ref for the Dokany IO cache. Directory listing uses `PVFS_sys_readdirplus`, copies names and attributes, and tries to repair stat failures with `PVFS_sys_getattr`.

## State And Persistence
All durable state changes occur in OrangeFS. Local state is limited to the parsed mount table and temporary heap buffers. The implementation currently assumes one filesystem: `fs_get_mntent`, `fs_get_id`, and `fs_get_name` ignore their numeric inputs and use the first mount entry.

## Dependencies And Integration Points
This file depends on OrangeFS `pvfs2.h`, `str-utils.h`, and `client-service.h`. It is called by `dokany-interface.c` and indirectly exercised by the Windows client tests through the mounted drive.

## Risks And Test Signals
Symlink following is manual and capped at `FS_MAX_LINKS`, which is useful but creates complex memory ownership around copied attributes. Several allocation-failure branches leak sibling buffers or use uninitialized pointers in cleanup labels, especially in `fs_rename`. `fs_getattr` copies attributes from `sys_lookup_follow_links` then immediately calls `PVFS_util_release_sys_attr(attr)`, which is subtle because callers still rely on scalar fields. Directory attr arrays are also released after copying, so consumers must not expect allocated attr fields to remain valid. Tests cover common create, move, delete, directory listing, IO, flush, stat time, and statfs paths, but not symlink resolution or multi-filesystem behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/fs.h -->
# sources/distributed-fs/orangefs/src/client/windows/client-service/fs.h

## Purpose
`fs.h` declares the service-side OrangeFS filesystem abstraction used by the Dokany layer. It presents path-based and object-ref-based operations over the OrangeFS system interface.

## Important APIs, Types, And Functions
It exposes initialization/finalization (`fs_initialize`, `fs_finalize`), mount lookup (`fs_get_mntent`, `fs_get_id`, `fs_get_name`), path conversion (`fs_resolve_path`), namespace operations (`fs_lookup`, `fs_create`, `fs_remove`, `fs_rename`, `fs_mkdir`), metadata operations (`fs_truncate`, `fs_getattr`, `fs_setattr`, `fs_get_diskfreespace`), IO (`fs_io`, `fs_io2`, plus read/write macros), flush, and directory paging (`fs_find_files`).

## Control Flow
The header is purely declarative. Callers initialize the library against a tab file, resolve Windows paths to OrangeFS paths, perform operations with a `PVFS_credential`, and finalize at service shutdown. The `fs_read`/`fs_write` macros route through lookup-based `fs_io`; `fs_read2`/`fs_write2` route through object-ref-based `fs_io2`.

## State And Persistence
The header does not define state, but its API implies persistent OrangeFS mutations through create/remove/rename/truncate/setattr/write/flush and process-global mount table state initialized by `fs_initialize`.

## Dependencies And Integration Points
It includes `pvfs2.h` and is consumed by `dokany-interface.c` and service initialization code. It also defines the seam where tests through Dokany indirectly reach OrangeFS system calls.

## Risks And Test Signals
The API uses mutable `char *` paths and caller-owned output buffers, so buffer size discipline is a caller responsibility. `PVFS_sys_attr` ownership is not obvious from declarations; implementation releases allocated fields internally in some cases. The object-ref IO API is essential for performance but requires cache invalidation to be correct. Tests exercise the API indirectly through mounted-drive behavior, not as unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/io-cache.c -->
# sources/distributed-fs/orangefs/src/client/windows/client-service/io-cache.c

## Purpose
`io-cache.c` implements a small qhash-backed cache from Dokany file contexts to OrangeFS object refs so read/write callbacks can avoid repeated path lookup.

## Important APIs, Types, And Functions
The file defines external globals `io_cache` and `io_cache_mutex`, and implements `io_cache_compare`, `io_cache_add`, `io_cache_remove`, and `io_cache_get`. Entries are `struct io_cache_entry` from `io-cache.h`, containing context, `PVFS_object_ref`, IO type, and update flag.

## Control Flow
`io_cache_add` searches for an existing context. If present, it updates `io_type` when needed and returns. On miss, it allocates and initializes an entry and inserts it into `io_cache`. `io_cache_get` searches by context, copies the object ref/type/update flag into caller outputs, and returns `IO_CACHE_HIT` or `IO_CACHE_MISS`. `io_cache_remove` removes and frees the entry.

## State And Persistence
State is entirely in-memory and scoped to the service process. Entries should correspond to active Dokany contexts. Persistent filesystem data is not stored here; the cache only accelerates lookup.

## Dependencies And Integration Points
It depends on `gen-locks`, `gossip`, `client-service.h`, `io-cache.h`, OrangeFS types, and quickhash. `dokany-interface.c` uses this cache in `PVFS_Dokan_read_file` and `PVFS_Dokan_write_file`.

## Risks And Test Signals
The search and insert/remove operations are mutex-protected, but `io_cache_add` mutates an existing entry after releasing the mutex, and `io_cache_get` copies after releasing the mutex. That can race with remove or another update under heavy concurrent IO. There is no automatic removal shown in `PVFS_Dokan_close_file`, so lifetime depends on callers remembering to remove entries; otherwise stale object refs may accumulate. IO tests and multi-threaded file creation provide some signal but do not directly verify cache correctness or races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/io-cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/io-cache.h -->
# sources/distributed-fs/orangefs/src/client/windows/client-service/io-cache.h

## Purpose
`io-cache.h` declares the in-memory Dokany-context-to-OrangeFS-object cache used by the Windows client service read/write path.

## Important APIs, Types, And Functions
It defines result constants `IO_CACHE_HIT` and `IO_CACHE_MISS`, update constants `IO_CACHE_NO_UPDATE` and `IO_CACHE_UPDATE`, and `struct io_cache_entry` with quickhash linkage, `ULONG64 context`, `PVFS_object_ref object_ref`, `enum PVFS_io_type io_type`, and `update_flag`. It declares compare/add/remove/get functions.

## Control Flow
Callers add a context after resolving a path and performing successful IO, retrieve it on later IO, and remove it when the context is no longer valid. The header does not define initialization; the service initializes the qhash and mutex in `service-main.c`.

## State And Persistence
The declared structure is process-local cache state only. It persists for service lifetime or until explicit removal, not across restarts.

## Dependencies And Integration Points
It includes Windows, OrangeFS, and `quickhash.h`. It is consumed by `io-cache.c`, initialized by `service-main.c`, and used by `dokany-interface.c`.

## Risks And Test Signals
The cache key is a Dokany context id, so context uniqueness and cleanup are critical. There is no generation counter or mount id in the key. Tests that stress read/write performance can reveal functional misses but not subtle stale-entry races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/io-cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/ldap-support.c -->
# sources/distributed-fs/orangefs/src/client/windows/client-service/ldap-support.c

## Purpose
`ldap-support.c` implements optional LDAP-backed mapping from Windows user names to OrangeFS credentials. It connects to an LDAP server, searches configured attributes, validates numeric UID/GID values, and builds a `PVFS_credential`.

## Important APIs, Types, And Functions
Public functions are `PVFS_ldap_init`, `PVFS_ldap_cleanup`, and `get_ldap_credential`. `check_number` validates LDAP attribute values before conversion. The global `timeout` gives LDAP searches a 15-second bound. The implementation reads LDAP configuration from global `goptions`.

## Control Flow
Initialization calls Netscape-style LDAP SSL setup and disables certificate verification. Credential lookup handles `SYSTEM` specially by returning the system credential, initializes an LDAP connection with optional SSL, sets protocol version 3, binds with configured DN/password or anonymously, constructs a filter from configured object class, naming attribute, and user name, requests UID/GID attributes, and scans the first result entry. If both numeric values are present, it calls `init_credential`.

## State And Persistence
The file stores no durable state. LDAP library initialization is process-global, and each credential lookup uses transient connection/search/result objects. Credentials may later be cached by `user-cache.c`.

## Dependencies And Integration Points
It depends on Windows, LDAP/LDAP SSL headers, `cred.h`, `ldap-support.h`, `client-service.h`, and reporting via `report_error`. The Dokany credential path currently has LDAP mode commented out, and service initialization also comments out LDAP init/cleanup, so this implementation appears dormant unless re-enabled.

## Risks And Test Signals
LDAP filters interpolate `user_name` without escaping, creating LDAP injection risk if external names can contain filter metacharacters. `LDAPSSL_VERIFY_NONE` disables server certificate verification. `attrs[0]` and `attrs[1]` are heap-allocated with fixed 32-byte buffers and `strncpy` may leave them unterminated. `results` is not initialized before use. There are no listed client tests for LDAP mode; coverage would require configured LDAP integration tests and credential cache interaction checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/ldap-support.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/ldap-support.h -->
# sources/distributed-fs/orangefs/src/client/windows/client-service/ldap-support.h

## Purpose
`ldap-support.h` declares the optional LDAP credential integration for the Windows client service.

## Important APIs, Types, And Functions
It declares `PVFS_ldap_init`, `PVFS_ldap_cleanup`, and `get_ldap_credential(char *user_name, PVFS_credential *credential)`.

## Control Flow
The expected lifecycle is process startup initialization, credential lookup per cache miss/requestor, and process shutdown cleanup. The header itself does not enforce that lifecycle.

## State And Persistence
No state is declared here. Implementations use process-global LDAP library state and external global options.

## Dependencies And Integration Points
It includes `pvfs2.h` and `client-service.h`, so consumers have OrangeFS credential types and option definitions. In current service code, includes/calls are commented out, indicating an integration point rather than active behavior.

## Risks And Test Signals
Because LDAP mode is disabled in the current call path, declarations can drift from implementation unnoticed. No direct tests in the assigned client-test set validate this API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/ldap-support.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/messages.h -->
# sources/distributed-fs/orangefs/src/client/windows/client-service/messages.h

## Purpose
`messages.h` is a generated Microsoft Message Compiler/ETW header for the OrangeFS Windows client provider. It gives service code macros for registering an ETW provider and writing info/error events.

## Important APIs, Types, And Functions
The provider is `OrangeFS-Client-Provider` with GUID `cd75d1d2-a19b-4c81-a8a9-629fcd2fd998`. It defines channel `WINEVENT_CHANNEL_GLOBAL_APPLICATION`, descriptors `INFO_EVENT` and `ERROR_EVENT`, provider context `PROVIDER_GUID_Context`, registration macros `EventRegisterOrangeFS_Client_Provider` and `EventUnregisterOrangeFS_Client_Provider`, enabled checks, and write macros `EventWriteINFO_EVENT` and `EventWriteERROR_EVENT`.

## Control Flow
Service startup calls the register macro through `init_event_log`; shutdown calls unregister. Error reporting calls `EventWriteERROR_EVENT(message)`. Generated helpers manage enable callbacks, event bit masks, provider registration handles, and `EVENT_DATA_DESCRIPTOR` packing for a single ANSI string payload.

## State And Persistence
Runtime ETW state is held in global generated context variables and registration handles. Events are persisted/consumed by Windows ETW/Event Log infrastructure, not by this file.

## Dependencies And Integration Points
The header depends on Windows ETW headers such as `wmistr.h`, `evntrace.h`, and `evntprov.h`. `service-main.c` includes it for event registration and error logging.

## Risks And Test Signals
The file is generated; manual edits risk divergence from the manifest. The write template uses `strlen` on the message pointer and emits `"NULL"` when absent. If the provider is not registered, writes become effectively no-ops. Tests in `client-test` do not validate ETW emission; service startup/error tests or Event Viewer inspection would be needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/service-main.c -->
# sources/distributed-fs/orangefs/src/client/windows/client-service/service-main.c

## Purpose
`service-main.c` is the executable entry point and Windows service control layer for the OrangeFS client. It can install/remove the service, run as a Windows service, or run as a console process, then starts filesystem initialization and the Dokany mount loop.

## Important APIs, Types, And Functions
Major functions include `main`, `service_main`, `service_ctrl`, `service_install`, `service_remove`, `main_init`, `main_loop`, `main_thread_start`, `main_thread_stop`, `cache_thread_start`, `cache_thread_stop`, `check_mount_point`, service/event log helpers, and error formatting/reporting helpers. Globals include service status handles, `is_running`, `run_service`, worker thread handles, `debug_log`, global caches, and global `PORANGEFS_OPTIONS goptions`.

## Control Flow
Command-line parsing handles install/remove, service mode, mount override, and debug mode. Both service and console paths initialize ETW, Winsock, OpenSSL, user and IO caches, parse config, add users, configure gossip debug variables, validate the mount point, start the user-cache maintenance thread, and call `main_loop`. `main_loop` finds `PVFS2TAB_FILE` or a tab file beside the executable, retries `fs_initialize` every 15 seconds while running, then calls `dokan_loop`. Service stop/shutdown marks pending stop and requests Dokany unmount via `DokanRemoveMountPoint`.

## State And Persistence
Persistent system state is affected by `service_install` and `service_remove` through the Windows Service Control Manager. Runtime state includes global options, cache qhashes, mutexes, service status, ETW registration, debug file `service.log`, and the mounted Dokany filesystem. Filesystem state is delegated to OrangeFS via `fs.c`.

## Dependencies And Integration Points
It depends on Dokany, Windows SCM/threading/Winsock APIs, OpenSSL, gossip, generated ETW `messages.h`, configuration, certificate, user-cache, IO-cache, and `fs.h`. It starts the `dokan_loop` defined in `dokany-interface.c`.

## Risks And Test Signals
Cleanup ordering is fragile: `service_main_exit` can free/destroy caches and call `free(options)` even if allocation/configuration failed before options is initialized in some paths. `cache_thread_stop` uses `TerminateThread`, which can interrupt while holding `user_cache_mutex` or owning OpenSSL/heap objects. `main_thread_start` waits indefinitely on the mount thread, so service startup blocks inside service_main after reporting running. The service install path does not quote executable paths with spaces. Client-test coverage validates mounted behavior after startup but not service install/remove, SCM status transitions, ETW registration, retry behavior, or shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/service-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/user-cache.c -->
# sources/distributed-fs/orangefs/src/client/windows/client-service/user-cache.c

## Purpose
`user-cache.c` caches OrangeFS credentials by Windows user name so requestor credential lookup does not repeatedly parse certificates, LDAP entries, or configured user lists.

## Important APIs, Types, And Functions
It implements `user_compare`, `add_cache_user`, `get_cache_user`, and `user_cache_thread`. The disabled `remove_user` shows intended explicit removal. Global `user_cache` and `user_cache_mutex` are initialized in `service-main.c`. Entries are `struct user_entry` from `user-cache.h`.

## Control Flow
`add_cache_user` removes an existing entry for the user, allocates a new one, copies the username and `PVFS_credential`, clamps certificate expiration to not exceed the credential timeout, and inserts the entry in the qhash. `get_cache_user` searches by case-insensitive username and copies the credential on hit. `user_cache_thread` sleeps for one minute, scans qhash buckets, and removes entries whose ASN.1 UTC expiration is older than `time(NULL)`.

## State And Persistence
The cache is process-local and lost on restart. Entries hold copied credential data and optional OpenSSL ASN.1 expiration objects. Persistent identity data remains in config/certs/LDAP, not here.

## Dependencies And Integration Points
It depends on Windows sleep, OpenSSL ASN.1, OrangeFS credential helpers, `gen-locks`, `security-util`, `client-service.h`, `user-cache.h`, and `cred.h`. It is used by `dokany-interface.c` during request credential lookup and maintained by the thread started in `service-main.c`.

## Risks And Test Signals
`strncpy(entry->user_name, user_name, 256)` can leave the name unterminated. If `ASN1_UTCTIME_new` fails after freeing the old expiration, `add_cache_user` returns without freeing the allocated entry or cleaning the copied credential. The cache thread scans one qhash head per bucket and may miss chained entries depending on quickhash internals. It runs forever and is stopped with `TerminateThread`, which risks lock/heap corruption. Client tests indirectly exercise cache hits/misses through filesystem operations but do not validate expiration or concurrent credential lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/user-cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/user-cache.h -->
# sources/distributed-fs/orangefs/src/client/windows/client-service/user-cache.h

## Purpose
`user-cache.h` declares the user credential cache shared by service startup, credential resolution, and the maintenance thread.

## Important APIs, Types, And Functions
It defines `USER_CACHE_HIT` and `USER_CACHE_MISS`, `struct user_entry` with qhash linkage, `user_name[256]`, `PVFS_credential`, and optional `ASN1_UTCTIME *expires`, plus functions `user_compare`, `add_cache_user`, `get_cache_user`, and `user_cache_thread`.

## Control Flow
The service initializes the qhash and mutex, credential lookup calls `get_cache_user` and `add_cache_user`, and a background thread periodically expires entries.

## State And Persistence
The declared entry structure stores copied credentials and optional certificate expiration in memory only. It has no persistent backing.

## Dependencies And Integration Points
It includes OpenSSL ASN.1, OrangeFS, and quickhash. It is implemented by `user-cache.c`, initialized by `service-main.c`, and consumed by `dokany-interface.c`.

## Risks And Test Signals
The API exposes mutable `char *user_name` inputs and depends on callers to manage credential cleanup for returned copies. The thread entry point never terminates cooperatively. Tests do not directly target this header’s behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-service/user-cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/Makefile -->
# sources/distributed-fs/orangefs/src/client/windows/client-test/Makefile

## Purpose
This Makefile builds the `client-test` executable, primarily for comparing behavior against a Linux kernel module or mounted filesystem target.

## Important APIs, Types, And Functions
Targets compile `client-test.o`, `create.o`, `file-ops.o`, `info.o`, `open.o`, `test-io.o`, `test-support.o`, and `timer.o`, then link `client-test` with `-g` and `-lpthread`. `clean` removes the executable and object files.

## Control Flow
Each object has an explicit compile rule using `cc -o $@ -c $< $(CFLAGS)`. The final link rule uses the object list and `$(LDFLAGS)`.

## State And Persistence
Build outputs are local object files and the `client-test` binary. No runtime state is created by the Makefile itself.

## Dependencies And Integration Points
It assumes a Unix-like build environment, `cc`, pthreads, and the local test support/timer sources. It does not list every header dependency, and it omits modules such as `find.o` even though `test-list.h` can include find tests under `WIN32`.

## Risks And Test Signals
The Makefile is not a Windows build recipe despite living under `windows/client-test`; it compiles the portable/Linux side of the tests. Header dependency coverage is incomplete, so incremental rebuilds can miss changes. Successful `make` is a build signal for the non-Windows test harness, not for Dokany service integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/client-test.c -->
# sources/distributed-fs/orangefs/src/client/windows/client-test/client-test.c

## Purpose
`client-test.c` is the command-line test runner for mounted OrangeFS client behavior. It validates a root directory, parses reporting and test-selection options, then runs registered filesystem operation tests.

## Important APIs, Types, And Functions
It defines an internal singly linked `list_node` for requested test names. Functions include `add_list_node`, `free_list`, `find_operation`, `setoption`, `init`, `run_tests`, `finalize`, and `main`. It consumes `global_options`, `test_operation`, and `op_table` from `test-support.h` and `test-list.h`.

## Control Flow
`main` requires a root directory, normalizes it with a trailing slash, allocates options and an empty test list, then calls `init`. `init` verifies the root is a directory and parses `-tabfile`, `-console`, `-file`, and explicit test names. `run_tests` runs all tests if the list is empty or resolves names through `find_operation` and runs them in requested order. Fatal test failures stop the run with `CODE_FATAL`; technical errors are reported with strerror.

## State And Persistence
State is in `global_options`, the transient test list, optional report file, and filesystem artifacts created by individual tests under `root_dir`.

## Dependencies And Integration Points
The runner uses Windows or POSIX stat APIs depending on platform and calls all test modules through `op_table`. Tests interact with OrangeFS only through the mounted path and C runtime filesystem calls.

## Risks And Test Signals
`free_list` frees the head node, so callers must not use it afterward. Some failure paths leak `options` or `test_list`. The runner stops at the first fatal/technical error, which is useful for smoke testing but can hide later failures. Its strongest signal is end-to-end compatibility of the mounted filesystem with ordinary CRT operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/client-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/create.c -->
# sources/distributed-fs/orangefs/src/client/windows/client-test/create.c

## Purpose
`create.c` contains client tests for directory creation, file creation, long path/name behavior, and repeated file creation.

## Important APIs, Types, And Functions
Public tests are `create_dir`, `create_subdir`, `create_dir_toolong`, `create_files`, `create_file_long`, `create_file_toolong`, and `create_files_many`. Helpers include `create_dir_cleanup`, `randchar`, `create_subdir_cleanup`, `create_subdir_int`, `create_files_cleanup`, `create_file_int`, and `create_file_long_int`.

## Control Flow
Tests generate random names under `options->root_dir`, perform `_mkdir`, `fopen`, or repeated create operations, report expected success/failure via `report_result`, and clean up artifacts. Long file tests require `-tabfile`, parse the first tabfile line to account for filesystem root length, then synthesize names near or beyond `MAX_FILE_NAME`.

## State And Persistence
Temporary directories and files are created under the test root and normally removed before return. `create_files_many` creates and immediately removes 1000 zero-byte files through `create_file_int`.

## Dependencies And Integration Points
It depends on CRT directory/file APIs, errno, `test-support.h`, and helper generators/reporters. These tests indirectly cover Dokany create disposition, mkdir, path length handling, and cleanup behavior.

## Risks And Test Signals
Cleanup is best effort. `create_subdir_cleanup` returns early without freeing `root_dir_int` if path equals root. Long-name tests depend on tabfile parsing assumptions and Windows path limits. Expected error code `2` is platform-specific (`ENOENT`/file not found), so results may vary across runtime layers. These tests are important signals for namespace creation and path conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/create.h -->
# sources/distributed-fs/orangefs/src/client/windows/client-test/create.h

## Purpose
`create.h` declares the creation-related test functions registered by `test-list.h`.

## Important APIs, Types, And Functions
It exposes `create_dir`, `create_subdir`, `create_dir_toolong`, `create_files`, `create_file_long`, `create_file_toolong`, and `create_files_many`, all with signature `int (global_options *options, int fatal)`.

## Control Flow
The header is declarative. `client-test.c` invokes these functions through `op_table`; each function reports results and returns `0`, an errno-style technical error, or `CODE_FATAL`.

## State And Persistence
State is owned by implementations in `create.c` and by the shared `global_options`.

## Dependencies And Integration Points
It includes `test-support.h` for `global_options` and result constants. It is consumed by `test-list.h`.

## Risks And Test Signals
The broad signature makes fatal policy caller-controlled. No direct compile-time relationship records which tests require `-tabfile`; that is enforced only at runtime in `create.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/create.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/file-ops.c -->
# sources/distributed-fs/orangefs/src/client/windows/client-test/file-ops.c

## Purpose
`file-ops.c` tests deletion, directory removal, rename, and move behavior through ordinary CRT filesystem APIs against the mounted client root.

## Important APIs, Types, And Functions
Tests include `delete_file`, `delete_file_notexist`, `delete_dir_empty`, `delete_dir_notempty`, `rename_file`, `rename_file_exist`, `move_file`, `move_file_baddir`, and `move_file_exist`. `lookup_file_int` wraps `_stat` to check whether a path exists.

## Control Flow
Each test creates random files/directories as needed, performs `_unlink`, `_rmdir`, or `rename`, reports expected results, and removes remaining artifacts. Move tests build destination paths under newly created or intentionally missing directories.

## State And Persistence
Temporary files and directories are created under `options->root_dir`. Cleanup generally removes final artifacts, though some paths omit unlink of moved files before removing directories, depending on target behavior.

## Dependencies And Integration Points
The module depends on CRT stat/rename/remove APIs, errno constants, `test-support.h`, and `file-ops.h`. It exercises Dokany delete-on-close, directory empty checks, and `fs_rename`.

## Risks And Test Signals
`delete_dir_notempty` reports expected `ENOTEMPTY` but fatal logic checks `code != 0`, so a correct `ENOTEMPTY` result can be treated as fatal if fatal were enabled. `rename_file_exist` comments that OrangeFS overwrites, reports success expected, but fatal logic checks `code != EACCES`, which conflicts with the report expectation. These inconsistencies reduce reliability of fatal-mode signal. Still, the tests are useful for namespace mutation and error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/file-ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/file-ops.h -->
# sources/distributed-fs/orangefs/src/client/windows/client-test/file-ops.h

## Purpose
`file-ops.h` declares namespace mutation tests for delete, rename, and move operations.

## Important APIs, Types, And Functions
It declares delete tests (`delete_file`, `delete_file_notexist`, `delete_dir_empty`, `delete_dir_notempty`), rename tests (`rename_file`, `rename_file_exist`), and move tests (`move_file`, `move_file_baddir`, `move_file_exist`).

## Control Flow
The header is consumed by `test-list.h`, which registers these tests for the runner. All functions follow the shared `global_options`/`fatal` signature.

## State And Persistence
State is in implementation-created temporary filesystem objects under the configured root.

## Dependencies And Integration Points
It includes `test-support.h` for shared test types. It is implemented by `file-ops.c`.

## Risks And Test Signals
The header gives no metadata about expected success/failure or fatal defaults; those live separately in `test-list.h` and implementation logic, where some inconsistencies exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/file-ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/find.c -->
# sources/distributed-fs/orangefs/src/client/windows/client-test/find.c

## Purpose
`find.c` provides Windows-only tests for directory lookup and wildcard enumeration against the mounted client.

## Important APIs, Types, And Functions
Under `WIN32`, it implements `find_files` and `find_files_pattern`. It uses `_findfirst`, `_findnext`, `_findclose`, `struct _finddata_t`, `quick_create`, and reporting helpers.

## Control Flow
`find_files` creates ten random files and confirms each exact path can be found. `find_files_pattern` creates ten files with an `xyz` prefix, finds them using an `xyz*` pattern, then using `xyz?????`, and marks each generated name as found. Both tests clean up generated files.

## State And Persistence
Only temporary files under `options->root_dir` are created and removed. Search state is held in CRT find handles.

## Dependencies And Integration Points
It depends on Windows CRT find APIs and `test-support.h`. It directly exercises `PVFS_Dokan_find_files_with_pattern`, name conversion, wildcard matching, and directory paging through the mounted path.

## Risks And Test Signals
The non-Windows branch is not implemented. The pattern test does not reset `mark[]` between `*` and `?` checks, so the second check can pass based on first-pass marks. Error handling assumes `errno == ENOENT` after enumeration completion. The test is still valuable for confirming basic find callbacks and wildcard compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/find.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/find.h -->
# sources/distributed-fs/orangefs/src/client/windows/client-test/find.h

## Purpose
`find.h` declares Windows-only find/enumeration tests.

## Important APIs, Types, And Functions
When `WIN32` is defined, it includes `test-support.h` and declares `find_files` and `find_files_pattern`.

## Control Flow
`test-list.h` registers these functions only for Windows builds. Non-Windows builds see no test declarations.

## State And Persistence
The header defines no state. Runtime file creation and cleanup are in `find.c`.

## Dependencies And Integration Points
The Windows-only guard matches the implementation’s use of CRT `_findfirst` APIs. These tests integrate with the Dokany directory enumeration path.

## Risks And Test Signals
Because declarations vanish on non-Windows builds, build coverage differs by platform. The Makefile for the Linux-style build does not include `find.o`, consistent with the guard.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/find.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/info.c -->
# sources/distributed-fs/orangefs/src/client/windows/client-test/info.c

## Purpose
`info.c` tests file metadata timestamps and reported volume free/total space for the mounted filesystem.

## Important APIs, Types, And Functions
It implements `file_time` and platform-specific `volume_space`. Windows uses `_stat` and `_getdiskfree`; non-Windows uses `statfs`.

## Control Flow
`file_time` records current time, creates a random file, stats it, computes absolute differences for atime/ctime/mtime, and expects each to be within 15 seconds. `volume_space` retrieves disk space, reports the API result, and emits free/total GB performance-style values.

## State And Persistence
`file_time` creates and removes one temporary file. `volume_space` only reads filesystem metadata.

## Dependencies And Integration Points
It depends on CRT stat APIs, Windows `_diskfree_t` or POSIX `statfs`, errno, and `test-support.h`. It exercises Dokany `GetFileInformation` and `GetDiskFreeSpace`.

## Risks And Test Signals
`file_time` computes `code` from timestamp differences but reports a literal actual value of `0`, hiding failures in the report line while still returning fatal if enabled. The non-Windows GB calculation lacks parentheses around the full divisor, producing incorrect scaling. The tests provide useful smoke signal for metadata translation and statfs but need fixes for precise assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/info.h -->
# sources/distributed-fs/orangefs/src/client/windows/client-test/info.h

## Purpose
`info.h` declares metadata and volume-space tests for the client test runner.

## Important APIs, Types, And Functions
It declares `file_time(global_options *options, int fatal)` and `volume_space(global_options *options, int fatal)`.

## Control Flow
The functions are registered from `test-list.h` and run by `client-test.c` using the common test signature.

## State And Persistence
No state is declared in the header. Implementations create at most temporary test files.

## Dependencies And Integration Points
It includes `test-support.h`. The tests connect to Dokany metadata and statfs callbacks through standard library calls.

## Risks And Test Signals
As with other test headers, expected platform behavior and fatal policy are not represented here; they are split across implementation and `test-list.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/open.c -->
# sources/distributed-fs/orangefs/src/client/windows/client-test/open.c

## Purpose
`open.c` tests basic file open modes against the mounted client using standard `fopen`.

## Important APIs, Types, And Functions
It implements `open_file_cleanup`, `open_file_int`, and the public `open_file` test.

## Control Flow
`open_file` generates a random path, opens it with modes `"w"`, `"r"`, `"a"`, and `"w+"`, reporting success after each. It cleans up the file at the end or on fatal failure. `open_file_int` wraps `fopen` and returns `errno` on failure.

## State And Persistence
One temporary file is created under `options->root_dir` and removed by `_unlink`.

## Dependencies And Integration Points
It depends on stdio, errno, `open.h`, and shared test support through that header. It exercises Dokany create/open dispositions, read/write access handling, and close cleanup.

## Risks And Test Signals
The test assumes the `"w"` mode creates the file before `"r"` and `"a"` are attempted. It does not verify file contents or append semantics. It is a useful minimal smoke test for open/create access mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/open.h -->
# sources/distributed-fs/orangefs/src/client/windows/client-test/open.h

## Purpose
`open.h` declares the basic open-mode test.

## Important APIs, Types, And Functions
It declares `open_file(global_options *options, int fatal)`.

## Control Flow
The function is registered in `test-list.h` and called through the generic test runner.

## State And Persistence
The header has no state. `open.c` manages temporary file creation and cleanup.

## Dependencies And Integration Points
It includes `test-support.h`. The declaration participates in the mounted-filesystem smoke-test suite.

## Risks And Test Signals
The copyright year differs from surrounding files, suggesting old code. The single declaration gives no detail about tested modes; callers must consult `open.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/open.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/test-io.c -->
# sources/distributed-fs/orangefs/src/client/windows/client-test/test-io.c

## Purpose
`test-io.c` contains throughput and correctness tests for sequential file IO, flush behavior, and multi-threaded file creation/write workload.

## Important APIs, Types, And Functions
Public tests are `io_file`, `flush_file`, and `io_file_mt`. Helpers include `io_file_cleanup`, `io_file_int`, `io_file_mt_cleanup`, platform-specific `io_file_mt_thread`, and `thread_args`. Constants include `BUF_MAX_SIZE`, `NUM_SIZES`, `THREAD_COUNT`, and `FILE_COUNT`.

## Control Flow
`io_file` iterates sizes from 4 KiB through 1 GiB, writes patterned data in chunks up to 1 MiB, reads it back, reports write/read timings, and compares one buffer chunk. `flush_file` writes 4 KiB, calls `fflush`, opens a second reader, and compares data. `io_file_mt` launches ten threads, each creating a directory and writing 100 small files, then reports summed per-file time and wall-clock total.

## State And Persistence
Tests create temporary files and per-thread directories under `options->root_dir` and attempt cleanup at the end. No state is persisted intentionally.

## Dependencies And Integration Points
It depends on Windows threads/process APIs or POSIX pthreads, local `timer` and `thread` helpers, stdio, errno, and test support. It exercises Dokany read/write, flush, close, create, and concurrent dispatch paths, including the service IO cache.

## Risks And Test Signals
`io_file` compares only the last chunk-sized buffer after a large read, not every byte of the whole file. Some loops can spin if `fwrite`/`fread` returns zero without errno. The non-Windows `total` accumulator is not initialized before joins. Multi-thread tests stress concurrency but mostly file creation/write, not simultaneous writes to the same file. These tests are strong performance smoke signals but partial correctness checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/test-io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/test-io.h -->
# sources/distributed-fs/orangefs/src/client/windows/client-test/test-io.h

## Purpose
`test-io.h` declares IO-related tests for the client test runner.

## Important APIs, Types, And Functions
It declares `io_file`, `flush_file`, and `io_file_mt`, all using the shared `global_options`/`fatal` signature.

## Control Flow
`test-list.h` registers these functions, and `client-test.c` invokes them either in the default suite or by explicit test name.

## State And Persistence
The header has no state. Implementations create temporary files and directories under the configured root.

## Dependencies And Integration Points
It includes `test-support.h`. Tests exercise mounted OrangeFS IO through the C runtime and, under the service, the Dokany read/write/flush callbacks.

## Risks And Test Signals
The header does not expose test sizes, thread counts, or performance semantics, so changing those in `test-io.c` can significantly alter runtime without any declaration change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/test-io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/test-list.h -->
# sources/distributed-fs/orangefs/src/client/windows/client-test/test-list.h

## Purpose
`test-list.h` defines the registry of named client tests that `client-test.c` can run by default or by explicit command-line name.

## Important APIs, Types, And Functions
It defines `test_operation`, with `name`, function pointer, and `fatal` flag, and declares/initializes `op_table[]`. Registered tests cover create, open, IO, flush, delete, rename, move, metadata, Windows-only volume/find tests, and multi-threaded IO.

## Control Flow
The runner scans `op_table` until the `{NULL, NULL, 0}` sentinel. Default mode runs every row in order; explicit mode looks up names against this table. The `fatal` field determines whether individual tests should convert expected assertion failures into `CODE_FATAL`.

## State And Persistence
Because `op_table` is defined in a header, every translation unit including it gets a definition unless guarded by usage patterns. In this source set it is intended for inclusion by `client-test.c`.

## Dependencies And Integration Points
It includes every test module header and `test-support.h`. `WIN32` gates `volume-space`, `find-files`, and `find-files-pattern`.

## Risks And Test Signals
Defining a non-`static` global table in a header can cause multiple-definition problems if included by more than one linked object. Fatal policy is inconsistent with some implementation expectations. This file is the authoritative list of test signals available to validate the Dokany-mounted client.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/test-list.h -->
