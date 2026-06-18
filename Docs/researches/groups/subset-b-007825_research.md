# subset-b-007825 Research

Grouped research for the listed OpenAFS xstat files and OrangeFS admin utilities. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/xstat/xstat_cm_test.c -->
# sources/distributed-fs/openafs/src/xstat/xstat_cm_test.c

## Purpose
`xstat_cm_test.c` is a command-line exerciser for the OpenAFS Cache Manager extended-statistics client. It resolves one or more Cache Manager hosts, asks `xstat_cm` to collect selected AFSCB xstat collections, and prints human-readable summaries of call counters, cache-manager performance state, server up/down distributions, RPC timings, transfer buckets, authentication, and access statistics.

## Important APIs, Types, And Functions
The main entry points are `main`, `RunTheTest`, `CM_Handler`, `print_cmCallStats`, `PrintPerfInfo`, `PrintFullPerfInfo`, `PrintOverallPerfInfo`, `PrintRPCPerfInfo`, `PrintOpTiming`, `PrintXferTiming`, `PrintErrInfo`, and `CountListItems`. The file uses `xstat_cm_Init`, `xstat_cm_Wait`, `xstat_cm_Cleanup`, `xstat_cm_Results`, AFS command parser types (`cmd_syndesc`, `cmd_item`), `hostutil_GetHostByName`, `opr_softsig_Init`, and Rx finalization.

## Control Flow
`main` registers `-cmname`, `-collID`, `-onceonly`, `-frequency`, `-period`, and `-debug` options through the OpenAFS `cmd` framework. `RunTheTest` initializes soft signal handling, derives one-shot/debug flags, counts command-list items, resolves CM hostnames to port 7001 socket addresses, parses collection IDs into an `afs_int32` array, and starts `xstat_cm_Init` with `CM_Handler`. `xstat_cm_Wait` then blocks for one collection in one-shot mode or for the requested period in continuous mode. `CM_Handler` checks `probeOK`, optionally dumps raw words, and switches on the collection number: call-info prints macro-expanded `AFS_CM_CALL_STATS`, perf-info is intentionally suppressed, and full-perf decodes and prints overall, RPC, authentication, and access groups.

## State And Persistence
The file keeps only process-local state: `debugging_on`, `one_shot`, static operation-name arrays, parsed socket and collection arrays, and the global `xstat_cm_Results` maintained by the xstat module. It writes no persistent state. It does allocate `CMSktArray` and `collIDP`; cleanup focuses on `xstat_cm_Cleanup` and `rx_Finalize`, so command-side allocations are process-lifetime allocations.

## Dependencies And Integration Points
It integrates with the `xstat_cm` library, the AFSCB/cache-manager xstat wire structures, Rx, host utilities, OpenAFS command parsing, and the generated `AFS_component_version_number.c`. The printed structure sizes must match the Cache Manager that serves the statistics, so this test is both a sample client and a compatibility probe for xstat collection layouts.

## Risks And Test Signals
Risks include strict struct-size assumptions for perf/full-perf collections, no bounds guard on operation-name arrays beyond constants, process exits from inside `RunTheTest`, and memory not freed before normal process termination. Useful test signals are successful host resolution, one-shot collection completion, expected output for `AFSCB_XSTATSCOLL_CALL_INFO` and `AFSCB_XSTATSCOLL_FULL_PERF_INFO`, size-mismatch messages against incompatible CMs, and error reporting when a CM probe fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/xstat/xstat_cm_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/xstat/xstat_fs.c -->
# sources/distributed-fs/openafs/src/xstat/xstat_fs.c

## Purpose
`xstat_fs.c` implements the client side of OpenAFS File Server extended statistics. It initializes Rx client connections to one or more file servers, starts a callback listener so file servers can treat the collector like a minimal Cache Manager, runs a probe thread that periodically calls `RXAFS_GetXStats`, exports the latest result through global state, and provides helpers for waiting, forced probes, cleanup, and cross-platform full-performance-stat decoding.

## Important APIs, Types, And Functions
Exported state includes `xstat_fs_numServers`, `xstat_fs_ConnInfo`, `xstat_fs_Results`, and the backing `xstat_fsData` collection buffer. Exported functions are `xstat_fs_Init`, `xstat_fs_Cleanup`, `xstat_fs_ForceProbeNow`, `xstat_fs_DecodeFullPerfStats`, and `xstat_fs_Wait`. Private functions are `xstat_fs_CleanupInit` and the probe-thread body `xstat_fs_LWP`. The implementation uses `struct xstat_fs_ConnectionInfo`, `struct xstat_fs_ProbeResults`, Rx security/service APIs, `RXAFS_GetXStats`, the AFSCB callback dispatcher, pthreads, and OpenAFS `opr_mutex_t`/`opr_cv_t`.

## Control Flow
`xstat_fs_Init` validates arguments, records flags and collection IDs, initializes the force-probe condition variable, verifies callback stubs through `xstat_fs_CleanupInit`, allocates connection records, initializes Rx, creates null Rx client/server security objects, resolves host names, creates Rx connections to AFS service 1 on the supplied file-server sockets, starts an AFSCB callback service, starts the Rx server, and creates `xstat_fs_LWP`. The probe thread increments the probe number, iterates each server and each requested collection ID, zeroes the shared collection buffer, calls `RXAFS_GetXStats`, and invokes the caller-provided handler after each server/collection result. It exits after one pass in one-shot mode or sleeps until the next frequency timeout, with `xstat_fs_ForceProbeNow` waking the condition variable early.

## State And Persistence
The module is intentionally global and single-instance. It persists in memory the connection array, copied collection ID array, latest result metadata, shared data buffer, debug/one-shot flags, callback service, Rx connections, thread handle, and synchronization primitives. It writes no disk state. `xstat_fs_Cleanup` destroys Rx connections and optionally frees the connection array, but the copied collection ID array is not freed in the visible cleanup path.

## Dependencies And Integration Points
The module depends on OpenAFS Rx, the AFS file-server RPC interface, callback RPC stubs from `xstat_fs_callback.c`, `afs/fs_stats.h`, pthreads, and host utilities. Consumers link to this module through `xstat_fs.h` and provide a no-argument handler that reads `xstat_fs_Results`.

## Risks And Test Signals
Risks include unsynchronized access to global result buffers between the probe thread and handler consumers, partial cleanup after failed initialization, allocation of collection IDs before `xstat_fs_CleanupInit`, fixed `AFS_MAX_XSTAT_LONGS` buffering, and compatibility complexity in `xstat_fs_DecodeFullPerfStats` for 32-bit versus 64-bit `timeval` and remote word order. Tests should cover invalid init arguments, unreachable servers returning `-2`, one-shot thread join, forced probe wakeups, handler error logging, cleanup after partial setup, and decoding of small and large full-performance-stat payloads from opposite-endian hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/xstat/xstat_fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/xstat/xstat_fs.h -->
# sources/distributed-fs/openafs/src/xstat/xstat_fs.h

## Purpose
`xstat_fs.h` is the public interface for the OpenAFS File Server xstat client. It defines initialization flags, connection/result data structures, exported module state, and the functions needed to initialize polling, force an immediate collection, wait for collection activity, decode full-performance statistics, and clean up.

## Important APIs, Types, And Functions
The key flags are `XSTAT_FS_INITFLAG_DEBUGGING` and `XSTAT_FS_INITFLAG_ONE_SHOT`. `struct xstat_fs_ConnectionInfo` stores the server socket, Rx connection, and computed host name. `struct xstat_fs_ProbeResults` stores probe number/time, current connection, collection ID, `AFS_CollData`, and probe status. Public functions are `xstat_fs_Init`, `xstat_fs_ForceProbeNow`, `xstat_fs_Cleanup`, `xstat_fs_Wait`, and `xstat_fs_DecodeFullPerfStats`.

## Control Flow
Consumers call `xstat_fs_Init` once with file-server socket addresses, polling frequency, handler, flags, and collection IDs. The handler reads `xstat_fs_Results` after each probe. Long-running callers use `xstat_fs_Wait` or `xstat_fs_ForceProbeNow`, then eventually call `xstat_fs_Cleanup`.

## State And Persistence
The header declares process-global state owned by `xstat_fs.c`: server count, connection array, and latest probe results. There is no durable persistence, but the exported variables make the module stateful and non-reentrant.

## Dependencies And Integration Points
It includes platform networking headers, Rx, `afs/afsint.h`, and `afs/fs_stats.h`, and sets `FSINT_COMMON_XG` to allow coexistence with the Cache Manager xstat header. It is consumed by tests and any xstat file-server monitoring tool.

## Risks And Test Signals
Because consumers access mutable globals directly, ABI and struct-layout stability matter. Compile coverage with both Unix and Windows networking environments, plus runtime collection tests that verify handlers see valid `connP`, `collectionNumber`, and `data` fields, are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/xstat/xstat_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/xstat/xstat_fs_callback.c -->
# sources/distributed-fs/openafs/src/xstat/xstat_fs_callback.c

## Purpose
`xstat_fs_callback.c` supplies the AFSCB server-side callback routines required when the file-server xstat collector opens an Rx callback listener. The collector is not a real Cache Manager, so most callbacks are no-op compatibility stubs; identity-oriented calls return a generated UUID and interface address list.

## Important APIs, Types, And Functions
The file defines `afs_cb_inited`, `afs_cb_interface`, private `init_afs_cb`, and many `SRXAFSCB_*` RPC handlers including `CallBack`, `InitCallBackState`, `Probe`, `GetCE64`, `GetCE`, `GetLock`, `XStatsVersion`, `GetXStats`, `InitCallBackState2`, `WhoAreYou`, `InitCallBackState3`, `ProbeUuid`, `GetServerPrefs`, `GetCellServDB`, `GetCellByNum`, `GetLocalCell`, `GetCacheConfig`, and `TellMeAboutYourself`.

## Control Flow
The callback listener created in `xstat_fs_Init` dispatches AFSCB RPCs to these functions. Most simply return success or `RXGEN_OPCODE` for unsupported optional calls. `init_afs_cb` generates a UUID with platform-specific APIs and populates local addresses through `rx_getAllAddr`. `SRXAFSCB_WhoAreYou` and `SRXAFSCB_TellMeAboutYourself` lazily initialize and copy `afs_cb_interface`; `SRXAFSCB_ProbeUuid` compares the incoming UUID with the cached one; `SRXAFSCB_GetLocalCell` allocates and returns the string `"This is xstat_fs"`.

## State And Persistence
State is process-local: one generated callback UUID, address list, and initialization flag. No callback contents are cached, and no filesystem or registry state is changed. `GetLocalCell` allocates a string for the RPC output and relies on RPC/XDR cleanup by the caller/runtime.

## Dependencies And Integration Points
The stubs satisfy symbols expected by `RXAFSCB_ExecuteRequest` from `afs/afscbint.h`, and are explicitly sanity-called by `xstat_fs_CleanupInit`. They depend on Rx address discovery, UUID helpers, host utility logging when verbose mode is compiled on, and Windows UUID APIs on NT builds.

## Risks And Test Signals
Risks are mostly protocol-compatibility risks: unsupported callbacks return `RXGEN_OPCODE`, while a file server may expect identity callbacks to behave consistently. `afs_cb_inited` is not locked, so concurrent initial identity RPCs can race. Test signals include successful xstat polling against a file server, callback probes not causing disconnects, stable `WhoAreYou`/`ProbeUuid` behavior, and compile coverage across Windows and Unix UUID paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/xstat/xstat_fs_callback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/xstat/xstat_fs_test.c -->
# sources/distributed-fs/openafs/src/xstat/xstat_fs_test.c

## Purpose
`xstat_fs_test.c` is a command-line test client for the `xstat_fs` File Server statistics module. It resolves file-server hosts, requests specified xstat collection IDs, and prints raw call information, overall performance counters, full detailed RPC/transfer timings, and callback counters.

## Important APIs, Types, And Functions
Important functions include `main`, `RunTheTest`, `FS_Handler`, `PrintCallInfo`, `PrintPerfInfo`, `PrintFullPerfInfo`, `PrintOverallPerfInfo`, `PrintDetailedPerfInfo`, `PrintOpTiming`, `PrintXferTiming`, `PrintCbCounters`, and `CountListItems`. The file uses `xstat_fs_Init`, `xstat_fs_Wait`, `xstat_fs_Cleanup`, `xstat_fs_DecodeFullPerfStats`, `xstat_fs_Results`, OpenAFS command parsing, host utilities, Rx finalization, and xstat collection constants such as `AFS_XSTATSCOLL_CALL_INFO`, `AFS_XSTATSCOLL_PERF_INFO`, `AFS_XSTATSCOLL_FULL_PERF_INFO`, and `AFS_XSTATSCOLL_CBSTATS`.

## Control Flow
`main` registers command parameters for file-server names, collection IDs, one-shot mode, frequency, period, and debug mode. `RunTheTest` initializes signal handling, parses flags and defaults, builds a fixed local array of up to twenty file-server socket addresses on port 7000, parses collection IDs, and starts `xstat_fs_Init` with `FS_Handler`. The handler checks `probeOK`, dumps raw entries in debug mode, and dispatches by collection ID. `PrintFullPerfInfo` calls `xstat_fs_DecodeFullPerfStats` before printing platform-neutral detailed timings; `PrintPerfInfo` directly casts the buffer to `struct afs_PerfStats` after a size check.

## State And Persistence
The test maintains only process-local flags, static display-name tables, parsed sockets, collection IDs, and the shared `xstat_fs_Results` populated by the xstat module. It does not persist data. The fixed `FSSktArray[20]` and process-lifetime allocation of `collIDP` are notable state choices.

## Dependencies And Integration Points
It integrates with the file-server xstat library, AFS file-server statistics structures, Rx, OpenAFS command parsing, host name utilities, and the generated component-version include. Its output is a human-facing validation surface for the xstat wire format and `xstat_fs_DecodeFullPerfStats`.

## Risks And Test Signals
Risks include the fixed twenty-server socket array, struct-size assumptions for direct perf casts, little validation of collection IDs, process exits inside command handling, and potential mismatch between `CbCounterStrings` and returned callback-stat count. Useful tests include one-shot and continuous runs, multiple collection IDs per server, debug raw dumps, full-perf decoding from different server architectures, callback counter collection, and failure paths for host resolution and failed probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/xstat/xstat_fs_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/module.mk.in -->
# sources/distributed-fs/orangefs/src/apps/admin/module.mk.in

## Purpose
`module.mk.in` contributes the OrangeFS admin application sources to the build system. It defines the admin client program source list and the server-side admin utility source list relative to `src/apps/admin`.

## Important APIs, Types, And Functions
The file is Make input, not C code. Its important variables are `DIR`, `ADMINSRC`, and `ADMINSRC_SERVER`. `ADMINSRC` lists utilities such as debug/performance/event controls, `pvfs2-ls`, `pvfs2-stat`, `pvfs2-mkdir`, `pvfs2-chmod`, `pvfs2-chown`, `pvfs2-fs-dump`, `pvfs2-fsck`, `pvfs2-cp`, xattr/touch/link/remove tools, check/drop-cache tools, and credential tools gated by security options. `ADMINSRC_SERVER` lists server-space tools such as `pvfs2-mkspace` and `pvfs2-showcoll`.

## Control Flow
During Makefile generation/build inclusion, the variable appends add source files to the broader build's admin target lists. Conditional blocks include credential-related tools depending on `ENABLE_SECURITY_KEY` or `ENABLE_SECURITY_CERT`.

## State And Persistence
The file has no runtime state. Its persistent effect is build graph composition: changing it changes which admin programs are compiled and distributed.

## Dependencies And Integration Points
It integrates with OrangeFS's autoconf/Make infrastructure and assumes the surrounding build logic consumes `ADMINSRC` and `ADMINSRC_SERVER`. It is the build integration point for many files in this subset.

## Risks And Test Signals
Risks are omissions, stale file names, and conditional security-tool build drift. Build-system tests should verify that listed tools compile under normal, key-security, and cert-security configurations and that server-only utilities are not linked into client admin targets incorrectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-check-config.c -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-check-config.c

## Purpose
`pvfs2-check-config.c` is intended to compare OrangeFS server configuration copies across configured filesystems, but in this source its core retrieval implementation is disabled behind `#if 0` and `compare_configs` is a stub that always returns mismatch after printing the master config pointer/string. As written, it is more of an unfinished diagnostic shell than a working checker.

## Important APIs, Types, And Functions
Important functions are `main`, `print_usage`, `compare_configs`, and `get_config`. The disabled `get_config` block references internal client state-machine APIs (`PINT_client_state_machine_post`, `PVFS_SERVER_GET_CONFIG`, persisted config buffers), `PVFS_credentials`, and state-machine fields. Active code uses `PVFS_sys_initialize`, `PVFS_util_parse_pvfstab`, `PVFS_sys_fs_add`, `PVFS_mgmt_count_servers`, and `PVFS_mgmt_get_server_array`.

## Control Flow
`main` rejects arguments, initializes the PVFS system, parses pvfstab, and loops over mount entries. For each filesystem it adds the mount entry, counts IO servers, allocates a server-address array, retrieves server addresses, and calls `get_config` for each server. The first server's filesystem config becomes the master pointer; every server's config is compared to it. Because active `get_config` returns zero without filling output buffers, the comparison path can pass null pointers to `compare_configs`.

## State And Persistence
Runtime state includes parsed mount table entries, server-address arrays, and intended config buffers. No persistent state is changed. Memory management is incomplete: server arrays and config buffers are not released in the active loop.

## Dependencies And Integration Points
The active code depends on PVFS sysint/mgmt APIs, pvfstab parsing, and mount entries. The disabled code depends on internal state-machine details that the comment says broke intended sysint usage and needed rewriting. This file is built as an admin utility via `module.mk.in`.

## Risks And Test Signals
Major risks are the disabled functionality, null config pointers, `compare_configs` always returning nonzero, leaked allocations, and break paths that skip cleanup/finalization. A useful test signal today is that the command initializes and iterates pvfstab without crashing; a functional test would require restoring `get_config`, comparing actual server config text whitespace-insensitively, and checking mismatched server config reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-check-config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-check-server.c -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-check-server.c

## Purpose
`pvfs2-check-server.c` checks whether a named OrangeFS server can provide filesystem configuration. It builds a temporary mount entry from protocol, host, port, and filesystem name, initializes the PVFS library, and calls `PVFS_sys_fs_add` to retrieve/add the filesystem configuration.

## Important APIs, Types, And Functions
The file defines `struct options`, `main`, `parse_args`, and `usage`. It uses `PVFS_util_gen_mntent`, `PVFS_sys_initialize`, `PVFS_sys_fs_add`, `PVFS_sys_finalize`, `PVFS_util_gen_mntent_release`, `PVFS_perror`, and command-line `getopt`.

## Control Flow
`parse_args` requires `-h`, `-f`, `-n`, and `-p`, allocating strings for hostname, filesystem name, network protocol, and reading the port. `main` formats `proto://host:port` into a fixed buffer, creates a mount entry, initializes PVFS, and calls `PVFS_sys_fs_add`; failure at that point means the configuration server did not respond or returned unusable config. Cleanup finalizes PVFS and releases the generated mount entry on success.

## State And Persistence
All state is transient: parsed options, generated mount entry, and PVFS system initialization. The command does not write server or local configuration.

## Dependencies And Integration Points
It depends on PVFS system initialization and configuration-fetching behavior. It is a small admin/diagnostic tool built from the admin source list and useful for deployment checks before writing pvfstab entries.

## Risks And Test Signals
Risks include fixed `config_server[256]` truncation through bounded `sprintf` components, leaked option strings on most error paths, and not finalizing PVFS on some failures after initialization. Test signals include successful checks against a known test server, clean errors for bad protocol/port/filesystem, and validation that generated mntent release/finalization happens under leak checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-check-server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-chmod.c -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-chmod.c

## Purpose
`pvfs2-chmod.c` implements an OrangeFS chmod-like admin utility. It parses an octal mode and one or more PVFS pathnames, resolves each path, looks up the target object without following the final symlink, and updates the target's `PVFS_ATTR_SYS_PERM` attribute.

## Important APIs, Types, And Functions
Important functions are `main`, `parse_args`, `pvfs2_chmod`, `usage`, and `check_perm`. The implementation uses `PVFS_util_init_defaults`, `PVFS_util_resolve`, `PVFS_util_gen_credential_defaults`, `PINT_remove_base_dir`, `PINT_lookup_parent`, `PVFS_sys_lookup`, `PVFS_sys_ref_lookup`, `PVFS_sys_getattr`, `PVFS_sys_setattr`, `PVFS_sys_finalize`, and `PVFS_util_translate`-compatible permission bit constants through `PVFS_permissions`.

## Control Flow
`parse_args` accepts `-v`, requires a three- or four-digit octal mode, validates each digit through `check_perm`, packs special/user/group/other bits into `PVFS_permissions`, and copies target strings. `main` initializes default PVFS state and iterates targets until one fails. `pvfs2_chmod` resolves a user path to filesystem ID and PVFS-relative path, generates credentials, finds the parent and basename (special-casing `/`), looks up the target without following the final link, fetches settable attributes, copies old attributes, changes `perms`, sets the mask to `PVFS_ATTR_SYS_PERM`, and calls `PVFS_sys_setattr`.

## State And Persistence
The persistent effect is modification of object permission metadata on OrangeFS. Runtime state consists of parsed options, path buffers, credentials, lookup/getattr responses, and old/new attribute structs. Target strings are allocated and not freed before process exit.

## Dependencies And Integration Points
It depends on the PVFS sysint, `str-utils`, and `pint-sysint-utils` parent/path helpers. It is integrated as an admin command and follows the same path-resolution pattern as `pvfs2-chown`.

## Risks And Test Signals
Risks include lack of symbolic chmod syntax, no recursive support, fixed `PVFS_NAME_MAX` buffers, root-path basename handling where `str_buf` remains empty, memory leaks, and stopping at the first failed target. Tests should cover mode parsing for UGO and SUGO forms, invalid digits, regular files/directories/symlinks, root handling, multiple targets, permission-denied failures, and verification with `pvfs2-stat`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-chmod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-chown.c -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-chown.c

## Purpose
`pvfs2-chown.c` implements an OrangeFS ownership-changing utility. It accepts a local user name, group name, and one or more target paths, resolves each target in OrangeFS, and updates `PVFS_ATTR_SYS_UID` and `PVFS_ATTR_SYS_GID`.

## Important APIs, Types, And Functions
Important functions are `main`, `parse_args`, `pvfs2_chown`, `usage`, `check_owner`, and `check_group`. The code uses POSIX account lookup (`getpwnam`, `getgrnam`) and PVFS APIs/helpers: `PVFS_util_init_defaults`, `PVFS_util_resolve`, `PVFS_util_gen_credential_defaults`, `PVFS_sys_lookup`, `PINT_remove_base_dir`, `PINT_lookup_parent`, `PVFS_sys_ref_lookup`, `PVFS_sys_getattr`, and `PVFS_sys_setattr`.

## Control Flow
`parse_args` handles `-v`, requires at least user, group, and one filename, resolves user/group names to numeric IDs, and copies target filenames. `main` initializes PVFS defaults and calls `pvfs2_chown` for each target until an error. `pvfs2_chown` resolves the path, generates credentials, locates the parent and target entry, gets current settable attributes, copies them, updates owner/group and mask, and writes the attributes back.

## State And Persistence
The persistent behavior is metadata mutation on OrangeFS objects. Runtime state mirrors `pvfs2-chmod`: path buffers, credentials, lookup responses, and copied attributes. The parsed target and option allocations are not explicitly freed before exit.

## Dependencies And Integration Points
The utility bridges local POSIX account/group databases to OrangeFS UID/GID fields. It depends on PVFS sysint/path helper libraries and is built with the rest of admin tools.

## Risks And Test Signals
Risks include accepting only names, not numeric IDs; no support for preserving one side with `user:` or `:group`; fixed path buffers; root-path handling; and stopping after the first target failure. Tests should cover valid and invalid local users/groups, multiple target paths, symlink final-component behavior, permission failures, and post-change stat output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-chown.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-config.in -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-config.in

## Purpose
`pvfs2-config.in` is the template for the installed `pvfs2-config` shell helper. It reports OrangeFS build/install metadata such as prefix, exec-prefix, version, compiler include flags, client link flags, and server link flags.

## Important APIs, Types, And Functions
This is a shell script template using configure substitutions such as `@prefix@`, `@exec_prefix@`, `@PVFS2_VERSION@`, `@includedir@`, `@libdir@`, `@LIBS@`, `@THREAD_LIB@`, `@OPENSSL_LIB@`, transport build flags, and transport library directories. Supported options are `--prefix`, `--exec-prefix`, `--version`, `--cflags`, `--libs`, `--static-libs`, `--serverlibs`, and `--static-serverlibs`.

## Control Flow
The script rejects empty invocation, then loops over arguments. `--prefix=DIR` and `--exec-prefix=DIR` override output variables for that process. Query options echo substituted values. Link-flag options build `libflags` incrementally, adding optional GM, IB, OpenIB, RDMA, MX, Portals, and realtime libraries when configured.

## State And Persistence
It has no persistent state; overrides affect only the current process output. Its installed contents persist configure-time build decisions.

## Dependencies And Integration Points
It is consumed by downstream builds that compile/link against OrangeFS client or server libraries. It integrates with autoconf substitution and the project's transport selection options.

## Risks And Test Signals
Risks include stale or misspelled library flags, shell word-splitting of paths with spaces, `--static-libs` being identical to `--libs`, and downstream link failures if optional transport substitutions are wrong. Tests should run the installed script for every option in representative build configurations and compile a small client/server program using the emitted flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-config.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-cp.c -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-cp.c

## Purpose
`pvfs2-cp.c` copies a single file between Unix and OrangeFS endpoints in any direction, replacing older import/export tools. It detects endpoint type, opens or creates the destination, streams data through a fixed-size buffer, optionally reports throughput, and preserves permissions/attributes when possible.

## Important APIs, Types, And Functions
Key types are `struct options`, `enum object_type`, `enum open_type`, `pvfs2_file_object`, `unix_file_object`, and `file_object`. Key functions are `main`, `parse_args`, `resolve_filename`, `generic_open`, `generic_read`, `generic_write`, `generic_cleanup`, `make_attribs`, `convert_pvfs2_perms_to_mode`, `Wtime`, and `print_timings`. PVFS dependencies include hints (`PVFS_hint_import_env`, `PVFS_hint_free`), sysint initialization, credentials, `PVFS_sys_lookup`, `PVFS_sys_ref_lookup`, `PVFS_sys_getattr`, `PVFS_sys_create`, `PVFS_sys_read`, `PVFS_sys_write`, `PVFS_sys_setattr`, request descriptors, distributions, and path helpers.

## Control Flow
`parse_args` reads optional timing, stripe size, datafile count, and buffer size, then requires source and destination. `main` imports hints, initializes PVFS, resolves both endpoints by trying `PVFS_util_resolve`, opens the source, opens/creates the destination, allocates the buffer, and loops `generic_read`/`generic_write` at monotonically increasing offsets until EOF or error. `generic_open` handles Unix directories by appending the source basename, refuses directory sources, refuses overwriting existing PVFS destinations, creates PVFS destinations with temporary mode 0777, and optionally sets a `simple_stripe` distribution strip size. `generic_cleanup` closes Unix descriptors and preserves permissions for PVFS-to-Unix, Unix-to-PVFS, Unix-to-Unix, and PVFS-to-PVFS copies.

## State And Persistence
Persistent effects are destination file creation/truncation and attribute changes. Runtime state includes endpoint descriptors/refs, copied attributes, credentials, PVFS hints, request descriptors, and the transfer buffer. For PVFS destinations, the file may exist with permissive attrs until cleanup restores source-derived attributes.

## Dependencies And Integration Points
The utility is an admin build target and a user-facing sysint client. It integrates local POSIX file APIs with OrangeFS metadata/data APIs, distribution selection, environment hints, and internal path utilities.

## Risks And Test Signals
Risks include no retry loop for short POSIX writes, return type `size_t` carrying negative PVFS errors, missing `PVFS_Request_free` on PVFS read/write error paths, possible basename/path concatenation overflow, refusal to overwrite PVFS targets but truncation of Unix targets, and created PVFS files left behind on failed transfers. Test signals should cover all four copy directions, directory destinations, existing PVFS target refusal, large files with partial read/write conditions, attribute preservation, strip size/datafile options, and cleanup after injected write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-cp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-drop-caches.c -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-drop-caches.c

## Purpose
`pvfs2-drop-caches.c` asks all servers in an OrangeFS filesystem to flush/drop OS I/O caches. It resolves a mount point to a filesystem ID and sends `PVFS_SERV_PARAM_DROP_CACHES` through the management API.

## Important APIs, Types, And Functions
The file defines `struct options`, `main`, `parse_args`, and `usage`. It uses `PVFS_util_init_defaults`, `PVFS_util_resolve`, `PVFS_util_gen_credential_defaults`, `PVFS_mgmt_setparam_all`, and `PVFS_sys_finalize`.

## Control Flow
`parse_args` accepts `-v` and required `-m <mount>`, copies the mount string, appends a slash for compatibility with path-prefix removal behavior, and rejects extra positional args. `main` initializes PVFS, resolves the mount, generates credentials, and calls `PVFS_mgmt_setparam_all` with parameter value zero and no detailed-error array.

## State And Persistence
There is no local persistent state. The remote persistent/operational effect is server cache dropping, which can affect performance and benchmarking state across all servers in the filesystem.

## Dependencies And Integration Points
It depends on OrangeFS sysint/mgmt APIs and server support for `PVFS_SERV_PARAM_DROP_CACHES`. It fits the admin command pattern for mount-point-targeted management actions.

## Risks And Test Signals
Risks include requiring a mount point rather than fsid, appending `/` without length recheck, no detailed per-server errors, option memory leaks, and cluster-wide performance disruption. Tests should verify success on a test filesystem, error reporting for unknown mounts and insufficient privileges, and server-side evidence that caches were requested to drop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-drop-caches.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-event-mon-example.c -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-event-mon-example.c

## Purpose
`pvfs2-event-mon-example.c` is an example admin utility that queries recent event-monitor records from all IO servers in an OrangeFS filesystem and prints them as rows containing server index, API, operation, value, ID, flags, and timestamp.

## Important APIs, Types, And Functions
The file defines `EVENT_DEPTH`, `struct options`, `main`, `parse_args`, and `usage`. It uses `PVFS_util_init_defaults`, `PVFS_util_resolve`, `PVFS_util_gen_credential_defaults`, `PVFS_mgmt_count_servers`, `PVFS_mgmt_get_server_array`, `PVFS_mgmt_event_mon_list`, and `PVFS_sys_finalize`.

## Control Flow
`parse_args` accepts `-v` and required `-m <mount>`, appending a slash to the mount point. `main` initializes PVFS, resolves the filesystem, generates credentials, counts IO servers, allocates a `server_count x EVENT_DEPTH` matrix of `PVFS_mgmt_event`, obtains IO-server addresses, fetches event lists, and prints every event whose flags do not include `PVFS_EVENT_FLAG_INVALID`.

## State And Persistence
The tool is read-only. Runtime state is the allocated event matrix and server-address array; these are not explicitly freed before process exit. No server state is modified.

## Dependencies And Integration Points
It depends on OrangeFS management event-monitor support and provides a simple text output suitable for examples or ad hoc monitoring. It is built with the admin tools but is not a daemon.

## Risks And Test Signals
Risks include fixed depth truncating older events, no per-server detailed errors, memory leaks, appending `/` without bounds checking, and a likely typo in error reporting where `PVFS_perror("PVFS_mgmt_event_mon_list", EVENT_DEPTH)` passes the depth instead of the return code. Tests should cover normal event retrieval, invalid mount handling, zero-server cases, invalid-event filtering, and output parsing under populated event histories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-event-mon-example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-fs-dump.c -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-fs-dump.c

## Purpose
`pvfs2-fs-dump.c` is a filesystem inspection utility. It puts OrangeFS servers into admin mode, enumerates all in-use handles, traverses the directory tree from `/`, verifies that directory data handles and metafile datafiles exist in the handle list, prints either text or Graphviz dot output, reports remaining handles, and restores normal server mode.

## Important APIs, Types, And Functions
Important functions are `main`, `build_handlelist`, `traverse_directory_tree`, `descend`, `verify_dirdatahandles`, `verify_datafiles`, `analyze_remaining_handles`, handle-list helpers, print helpers, `parse_args`, and `get_type_str`. It uses `PVFS_mgmt_count_servers`, `PVFS_mgmt_get_server_array`, `PVFS_mgmt_setparam_list`, `PVFS_mgmt_statfs_list`, `PVFS_mgmt_iterate_handles_list`, `PINT_cached_config_map_to_server`, `PVFS_sys_lookup`, `PVFS_sys_getattr`, `PVFS_sys_readdir`, `PVFS_mgmt_get_dirdata_array`, and `PVFS_mgmt_get_dfile_array`.

## Control Flow
`main` parses `-m`, `-d`, `-k`, `-f`, and `-v`, initializes PVFS, resolves the mount, gets credentials and server addresses, switches IO/meta servers to admin mode, builds the global handle list from server stats and batched handle iteration, emits a header, traverses the tree, analyzes leftover handles, emits a trailer, finalizes the handle list, restores normal mode, and finalizes PVFS. Directory traversal looks up root, validates it as a directory, prints/removes it from the handle list, verifies root dirdata, recursively reads directory entries, prints each object, verifies file datafiles or nested dirdata, and removes seen handles from the list. Leftover analysis classifies remaining handles as internal, preallocated data/metafiles, unknown, or all-accounted-for.

## State And Persistence
The intended persistent filesystem state is read-only, but server operational mode is changed to admin and then back to normal. Runtime state is a module-global handle list split by server, parsed output options, credentials, and server address arrays. `handlelist_finalize` is empty in this implementation, so the handle-list memory is not freed.

## Dependencies And Integration Points
It is tightly integrated with OrangeFS management APIs, cached configuration handle-to-server mapping, sysint directory traversal, and server admin mode semantics. Dot output integrates with Graphviz for visual inspection.

## Risks And Test Signals
Risks include leaving servers in admin mode on unexpected assertion/exit paths, heavy use of `assert(0)` for runtime filesystem inconsistencies, O(n) handle lookup/removal, memory leaks, possible incorrect `calloc(server_count, sizeof(PVFS_handle))` for pointer arrays, and incomplete cleanup on errors. Tests should run against a small known filesystem, verify text and dot output, inject missing datafile/dirdata scenarios if possible, check normal-mode restoration after failures, and compare handle counts to server stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-fs-dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-fsck.c -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-fsck.c

## Purpose
`pvfs2-fsck.c` is an OrangeFS filesystem checker and optional repair tool. It creates or locates `/lost+found`, enumerates all server handles, traverses reachable directories, removes invalid dirents, verifies required datafile/dirdata backing handles, finds orphaned subtrees/files, salvages recoverable objects into lost+found, and removes leftover unreferenced data/dirdata objects when destructive mode is enabled.

## Important APIs, Types, And Functions
Key functions are `main`, `build_handlelist`, `traverse_directory_tree`, `match_dirdata`, `descend`, `verify_datafiles`, `find_sub_trees`, `fill_lost_and_found`, `cull_leftovers`, `create_lost_and_found`, `create_dirent`, `remove_directory_entry`, `remove_object`, handle-list helpers, `parse_args`, `get_type_str`, and `get_user_action_to_continue`. Key state includes `struct options`, global `fsck_opts`, global `laf_ref`, and `global_removals`.

## Control Flow
`main` parses mount/destructive/safety options, initializes PVFS, resolves the filesystem, gets credentials and server addresses, creates `/lost+found` before admin mode, switches all IO/meta servers to admin mode, builds a handle list including removal of reserved handles, and runs four passes. The first pass traverses `/`, removes broken dirents, checks datafiles and dirdata, and deletes unrecoverable objects. The second pass scans remaining handles for orphaned subtrees and collects other leftovers into an alternate list. The tool then leaves admin mode. The third pass tries to salvage orphaned metafiles/directories into lost+found after verifying their backing handles. The fourth pass removes leftover unreferenced data/dirdata/internal objects. Destructive operations are logged as `not` performed unless `-a`, `-p`, or `-y` enabled destructive mode.

## State And Persistence
In non-destructive mode, the tool mostly reports intended actions while still creating/looking up lost+found only if destructive mode allows actual mkdir. In destructive mode it persists significant metadata changes: new lost+found entries, removed directory entries, removed objects, and possibly lost+found creation. It also temporarily changes server mode to admin during scanning. Runtime state is held in per-server handle-list arrays and global options/removal count.

## Dependencies And Integration Points
The checker depends on OrangeFS sysint, management APIs, cached config handle ownership mapping, server admin mode, reserved-handle iteration, and management-only create/remove dirent/object operations. `pvfs2-fsck.h` declares the internal function and handle-list interfaces used in this implementation.

## Risks And Test Signals
Risks are high because destructive mode mutates filesystem metadata. There are many `assert` calls on runtime conditions, limited rollback, O(n) handle searches, path/mode changes that may leave servers in admin mode after abnormal termination, and subtle list ownership issues when matching handles across main and alternate lists. Safety prompting counts removals globally but only prompts in destructive mode. Tests should start with non-destructive dry runs on clean and intentionally damaged test filesystems, verify no changes under `-n`, exercise safety prompts with `-s`, confirm salvage naming (`lostfile.<handle>`, `lostdir.<handle>`), verify server mode restoration, and run post-fsck tree/data integrity checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-fsck.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-fsck.h -->
# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-fsck.h

## Purpose
`pvfs2-fsck.h` declares the internal interfaces and handle-list structure for `pvfs2-fsck.c`. It is not a broad public API; it organizes the checker's parsing, traversal, repair, removal, and per-server handle-list operations.

## Important APIs, Types, And Functions
The header declares utility helpers (`parse_args`, `usage`, `get_type_str`), processing passes (`build_handlelist`, `traverse_directory_tree`, `match_dirdata`, `descend`, `verify_datafiles`, `find_sub_trees`, `fill_lost_and_found`, `cull_leftovers`), modification functions (`create_lost_and_found`, `create_dirent`, `remove_object`, `remove_directory_entry`), and `struct handlelist` with arrays for per-server handle pointers, capacities, and used counts. Static handle-list helpers cover initialize, add one/many handles, finish, find, remove, return, finalize, and optional debug print.

## Control Flow
`pvfs2-fsck.c` includes this header after defining `struct options`, so the static parser prototype refers to the implementation-local options type. The processing prototypes mirror the four-pass checker flow: build all handles, walk reachable tree, identify subtrees, fill lost+found, and cull leftovers.

## State And Persistence
The header defines no state directly, but `struct handlelist` is the central in-memory persistence mechanism for fsck's view of all handles and their consumption as objects are matched, salvaged, or removed.

## Dependencies And Integration Points
It depends on PVFS core types such as `PVFS_fs_id`, `PVFS_BMI_addr_t`, `PVFS_credential`, `PVFS_object_ref`, `PVFS_handle`, and `PVFS_ds_type`, supplied by prior includes in `pvfs2-fsck.c`. It is tightly coupled to that C file because many declarations are `static` and refer to local types.

## Risks And Test Signals
Risks include weak standalone includability, static prototypes in a header, tight coupling to definition order, and declaration drift from `pvfs2-fsck.c`. Compile coverage of `pvfs2-fsck.c` is the main signal; behavioral signals come from fsck tests that stress handle-list add/find/remove/return/finalize paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-fsck.h -->
