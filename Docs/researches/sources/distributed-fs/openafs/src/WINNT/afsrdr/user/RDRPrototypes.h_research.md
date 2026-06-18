# sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRPrototypes.h

## Purpose
Centralizes C-linkage prototypes for the Windows redirector user-mode implementation. It lets C and C++ redirector modules call common request, file, directory, extent, pioctl, pipe, byte-range-lock, volume, user, and FID conversion helpers without circular includes.

## Important APIs, Types, And Functions
The header forward-declares `cm_user_t`, `cm_req_t`, `cm_fid_t`, and `cm_scache_t`, includes shared `AFSUserPrototypes.h`, and declares `RDR_InitReq`, `RDR_SetInitParams`, worker/request dispatch, directory/file lifecycle helpers, async file extent functions, pioctl open/write/read/close, byte-range lock helpers, volume info helpers, FID hold/release, pipe helpers, raw read/write helpers, `RDR_UserFromCommRequest`, `RDR_UserFromAuthGroup`, `RDR_ReleaseUser`, `RDR_fid2FID`, `RDR_FID2fid`, and ioctl init/shutdown.

## Control Flow
The prototypes describe the end-to-end dispatch graph used by `RDRInit.cpp`: worker threads receive an `AFSCommRequest`, map it to a user, fan out to one of these helper families, and return `AFSCommResult` or asynchronous result callbacks. The same declarations support helper modules that need to call back into driver notification functions.

## State And Persistence
The header has no runtime state. Its signatures expose the state surfaces passed across modules: auth users, AFS file IDs, cache-manager FIDs/scaches, request contexts, result-buffer lengths, mapped I/O buffers, and flags such as WoW64, fast query, mount following, cache bypass, and FID holding.

## Dependencies And Integration Points
This is a broad integration header for `afsrdr/user` modules and includes `ntsecapi.h` for security/auth interfaces. It must remain consistent with shared driver callback structures from the common redirector headers and with implementations spread across many `.cpp`/`.c` files.

## Risks And Test Signals
The main risk is prototype drift, especially across C/C++ compilation units and shared structures whose layout also matters to the kernel driver. Full Windows redirector build coverage and request-dispatch smoke tests are the primary signals.
