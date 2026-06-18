# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSRDRSupport.cpp

## Purpose
`AFSRDRSupport.cpp` creates, registers, initializes, and tears down the redirector device. It also handles MUP path queries, service-provided redirector initialization, cache backing setup, root FCB creation/removal, and library initialization/closure.

## Important APIs, Control Flow, And State
`AFSInitRDRDevice` creates `AFSRDRDeviceObject`, initializes RDR tree/list locks and events, initializes the root FCB with `AFSInitRdrFcb`, clears `DO_DEVICE_INITIALIZING`, increments stack size, and registers as a UNC provider using `FsRtlRegisterUncProviderEx` when available or legacy `FsRtlRegisterUncProvider` plus `IoRegisterFileSystem`.

`AFSRDRDeviceControl` answers MUP `IOCTL_REDIR_QUERY_PATH` and `_EX` by accepting paths whose first component matches `AFSServerName`, returning `LengthAccepted`; other control codes fail with `STATUS_INVALID_DEVICE_REQUEST`.

`AFSInitializeRedirector` loads the library service, records cache block sizing, max RPC length, dump-file location, max direct I/O and dirty thresholds, dot-file/short-name/reparse/direct-service flags, and cache backing. Cache backing is either a service-provided memory mapping locked through an MDL or an opened cache file referenced by handle/object. It then stores path/link limits and calls `AFSInitializeLibrary` with the global file ID.

`AFSCloseRedirector` unloads the library and releases memory cache MDL, cache file handle/object/name, dump location, and root FCB. `AFSInitRdrFcb` allocates a paged `AFSFcb` plus nonpaged `AFSNonPagedFcb`, initializes FsRtl advanced header, main/paging resources, and atomically publishes it. `AFSRemoveRdrFcb` atomically removes and frees those resources.

## Dependencies And Integration Points
This file integrates the fs shim with MUP/UNC routing, the library lifecycle, cache manager callbacks, user-mode redirector initialization IOCTL structures, cache-file persistence, global tracing dump location, and shared FCB types from the wider OpenAFS redirector headers. It depends on `AFSLoadLibrary`, `AFSInitializeLibrary`, `AFSUnloadLibrary`, `AFSExAllocatePoolWithTag`, FsRtl, Zw file APIs, MDL page locking, and device extension layouts.

## Risks And Test Signals
Failure unwind has several subtle points: MDLs should be freed with the correct MDL routine, cache handle/object order must remain balanced, and `pDevExt = NULL` after FCB removal in the failure path can obscure later cleanup. The direct I/O minimum uses `5 * 1024 * 1204`, likely a typo for `1024 * 1024`. MUP query code trusts type-3 buffers and path lengths. Tests should cover UNC acceptance/rejection, registration on legacy and modern OS paths, memory-cache vs file-cache initialization, direct-service mode, dump location allocation, unload while initialized, duplicate root FCB publication, and injected failures at every cache setup stage.
