<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp.h -->
# sources/distributed-fs/openafs/src/libafscp/afscp.h

## Purpose
Defines the public libafscp client API and shared data structures for cells, servers, volumes, FIDs, directory streams, stat/directory caches, open files, and callback tracking. It is the main consumer-facing header for lightweight OpenAFS file-protocol operations.

## Important APIs, Types, And Functions
Core structs include `afscp_server`, `afscp_cell`, `afscp_volume`, `afscp_venusfid`, `afscp_dirent`, `afscp_dirstream`, `afscp_dircache`, `afscp_statent`, `afscp_openfile`, and `afscp_callback`. The API covers initialization/auth (`afscp_Init`, `afscp_Finalize`, `afscp_Insecure`, `afscp_AnonymousAuth`, `afscp_LocalAuthAs`), cell/server lookup, callback management, FID allocation, stat/read/write, RPC wrappers, ACL fetch/store, directory parsing/path resolution, volume lookup, and directory mode selection.

## Control Flow
Consumers initialize the library and authentication, resolve cells/servers/volumes/FIDs, perform file or directory RPC wrappers, and maintain callbacks/stat caches through the callback helpers. The header documents ownership for FID helpers and uses `afscp_errno` as the library error channel.

## State And Persistence
The header declares no storage except `afscp_errno`, but its structures describe persistent in-process state: Rx security classes, ubik VL clients, server Rx connections, volume caches, stat and directory caches guarded by pthread mutex/condition variables, and callback expiration data. Runtime persistence is memory-only.

## Dependencies And Integration Points
It depends on OpenAFS protocol headers (`afsint`, constants, cell config, directory format, util) and pthreads on Windows. It is installed as `afs/afscp.h` by `libafscp/Makefile.in` and implemented by sibling `afscp_*.c` files.

## Risks And Test Signals
Risks include ABI exposure of internal structs, global `afscp_errno`, thread-safety assumptions around shared caches/callbacks, fixed-size names/address arrays, and API declarations drifting from implementation. Test signals are compile coverage for consumers, initialization/auth smoke tests, path resolution, stat/read/write, ACL, callback invalidation, and multithreaded cache wait behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp.h -->
