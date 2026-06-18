# sources/distributed-fs/openafs/src/libadmin/cfg/cfginternal.c

## Purpose
This file implements private helpers for the OpenAFS configuration admin library. It validates `cfg_host_t` handles, lazily opens BOS handles, resolves and compares host names/addresses, edits local configuration-side filesystem state, sleeps portably, and, on Windows, starts/stops/queries the AFS client and BOS control services.

## Important APIs, Types, and Functions
- `cfgutil_HostHandleValidate` checks the opaque host handle magic values, validity flag, host/cell names, and cell handle before public cfg entry points use it.
- `cfgutil_HostHandleBosInit` lazily initializes `cfg_host->bosHandle` with `bos_ServerOpen` under `cfg_host->mutex`.
- `cfgutil_HostNameGetFull`, `cfgutil_HostNameIsAlias`, `cfgutil_HostNameIsLocal`, `cfgutil_HostAddressFetchAll`, `cfgutil_HostAddressIsValid`, and `cfgutil_HostNameGetAddressString` provide hostname/address normalization and comparison. Several are Windows-only and return `ADMCFGNOTSUPPORTED` on Unix.
- `cfgutil_HostNameGetCellServDbAlias` opens a null cell, opens BOS on a filesystem database host, iterates the server CellServDB, and returns the entry that aliases a requested host.
- `cfgutil_CleanDirectory` removes non-directory entries from one directory without recursing.
- `cfgutil_HostSetNoAuthFlag` creates or unlinks `AFSDIR_SERVER_NOAUTH_FILEPATH` for local server no-auth mode.
- `cfgutil_WindowsServiceStart`, `cfgutil_WindowsServiceStop`, and `cfgutil_WindowsServiceQuery` wrap the Windows SCM and translate generic service failures through `ServiceCodeXlate`.

## Control Flow and State
Most helpers use the library convention `rc == 1` for success, `rc == 0` for failure, and return a detailed `afs_status_t` through `st` when provided. BOS handle initialization is guarded by a pthread mutex and stores the resulting handle back in the host handle for reuse. Host address helpers allocate address arrays and free them after comparison or conversion. Windows service helpers open SCM/service handles, issue start/stop/query operations, poll until timeout, and close handles before returning.

## Persistence and Side Effects
The file can mutate local server authentication state by creating/truncating or unlinking the server `NoAuth` marker file. `cfgutil_CleanDirectory` unlinks files in a target directory. Windows helpers change local service state. Network and RPC side effects include DNS lookups, BOS connections, and CellServDB iteration.

## Dependencies and Integration Points
The helpers depend on `afs_AdminErrors.h` status codes, BOS admin APIs, client admin null-cell opening, `afs/dirpath.h` canonical paths, pthreads, roken, DNS/socket APIs, and Windows service APIs behind `AFS_NT40_ENV`. `cfgservers.c` and other cfg modules rely on these routines for common validation, BOS setup, host identity checks, and service control.

## Risks
Large parts of host resolution and Windows service logic are platform-specific; Unix callers receive `ADMCFGNOTSUPPORTED` for some address/full-name operations. Several buffers are assumed to be correctly sized by callers (`MAXHOSTCHARS`, `MAXPATHLEN`). The non-recursive cleaner silently ignores disappearing files and directories, which is intentional but can mask unexpected filesystem content. `cfgutil_HostSetNoAuthFlag` bypasses BOS credentials by editing the local flag file directly, so privilege and locality checks are critical. Error handling often preserves only one status, and later cleanup failures can overwrite earlier root causes.

## Test Signals
Useful tests include invalid-host-handle cases for every validation branch, concurrent lazy BOS initialization, host alias comparison with multi-address hosts, `NoAuth` file creation/removal with permission failures, `CleanDirectory` behavior with files/directories/missing directories, and Windows service start/stop timeout/error translation. On Unix, tests should assert the documented `ADMCFGNOTSUPPORTED` paths.
