# sources/distributed-fs/openafs/src/WINNT/afsd/afsd.h

## Purpose
`afsd.h` is the central private include for the Windows AFSD cache manager executable. It collects subsystem headers, declares the GUI entry-point functions, exposes major AFSD globals, defines service names and hook symbols, and sets compile-time feature flags used by AFSD implementation files.

## Important APIs, types, and functions
The header declares `InitClass`, `InitInstance`, `MainWndProc`, `About`, `afs_exit`, and `afsi_log`. It defines service/event names `AFS_DAEMON_SERVICE_NAME` and `AFS_DAEMON_EVENT_NAME`, worker thread count `WORKER_THREADS`, hook DLL/function-name constants for `afsdhook.dll`, and `SERVICE_CONTROL_CUSTOM_DUMP`.

It exports many cache-manager globals: root volume/cell/fid/scache, mount-root strings, cache path, gateway/session flags, freelance root state, DNS/read-only/short-name/direct-IO settings, RX MTU, redirector/SMB state, virtual cache, and data verification settings.

## Control flow
The header does not execute code. It shapes compile-time behavior by defining flags such as `USE_BPLUS`, `DFS_SUPPORT`, `LOG_PACKET`, `LOCK_TESTING`, and by undefining `NOTSERVICE`. Its broad include list makes AFSD implementation files see cache manager, SMB, redirector, volume, directory, buffer, daemon, ioctl, performance, rawops, initialization, and event-log interfaces.

## State and persistence behavior
The extern globals declared here represent long-lived AFSD process state. Some mirror persistent configuration loaded elsewhere, such as cache path, mount root, DNS settings, redirector policy, and SMB/RDR enablement. The header itself stores nothing but centralizes access to mutable global runtime state.

## Dependencies and integration points
`afsd.h` is a high-coupling integration header. It includes Windows NetBIOS headers, OSI, VLDB/AFS protocol headers, protection server headers, and most AFSD cache-manager modules. It is included by event logging and flush-volume code to access service names and interface state.

## Risks and edge cases
Because this header includes many subsystems and declares many globals, changes can cause widespread rebuilds and hidden coupling. Compile-time flags in a common header can silently change behavior across unrelated modules. Global mutable state makes initialization order important and complicates tests. Hook function typedefs expose extension points that can affect startup, daemon, SMB, stopping, and stopped phases.

## Test signals
Build tests should compile representative AFSD modules after any header change. Integration tests should validate service/event names, hook loading expectations, worker thread count assumptions, and consistent visibility of SMB/RDR/cache-manager globals across modules. Static analysis should watch for unwanted dependency growth from adding includes here.
