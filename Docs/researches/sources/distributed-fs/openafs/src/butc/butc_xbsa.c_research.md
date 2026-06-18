# sources/distributed-fs/openafs/src/butc/butc_xbsa.c

## Purpose
`butc_xbsa.c` is the Tape Coordinator's abstraction layer for XBSA servers. It hides whether BSA functions come from a platform XBSA shared library or the in-tree `NEW_XBSA` adapter, validates coordinator inputs, manages `butx_transactionInfo`, and maps BSA return codes to BUTX errors.

## Important APIs, Types, And Functions
The file declares function pointers for all BSA operations used by the coordinator, with signatures differing between `NEW_XBSA` and external-XBSA builds. `xbsa_error()` maps known BSA/ADSM return codes to operator log messages. Public wrapper functions are `xbsa_MountLibrary()`, `xbsa_Initialize()`, `xbsa_BeginTrans()`, `xbsa_EndTrans()`, `xbsa_Finalize()`, `xbsa_QueryObject()`, `xbsa_ReadObjectBegin()`, `xbsa_ReadObjectEnd()`, `xbsa_WriteObjectBegin()`, `xbsa_DeleteObject()`, `xbsa_WriteObjectEnd()`, `xbsa_WriteObjectData()`, and `xbsa_ReadObjectData()`.

## Control Flow
`xbsa_MountLibrary()` selects an ADSM server type, loads external symbols on old builds or binds directly to in-tree BSA functions under `NEW_XBSA`, queries the API version, rejects an incompatible technical-standard level, and sets server capability flags for multiple-server support. `xbsa_Initialize()` fills environment strings, validates owner/token/server strings, calls `XBSAInit()`, calls `XBSAGetEnvironment()`, and records `maxObjects`. Transaction wrappers begin/end/finalize BSA sessions. Query prepares a backup-file `QueryDescriptor` and stores the resulting object in `info->curObject`. Read and write wrappers convert coordinator buffers to `DataBlock`, enforce `XBSAMAXBUFFER`, and set count/end-of-data outputs. `xbsa_WriteObjectBegin()` also rotates transactions when `numObjects == maxObjects`, fills `ObjectDescriptor` fields, and starts the BSA object. Delete maps to `XBSAMarkObjectInactive()` for backup objects.

## State And Persistence
`butx_transactionInfo` is the central state object: API version, BSA handle, server type/flags, max object count, current object count, server name, security token, owner, and current object descriptor. Persistent effects occur in the external XBSA/TSM server through create, send, mark-inactive, and transaction commit calls.

## Dependencies And Integration Points
It depends on `butc_xbsa.h`, `afs/butx.h`, `afs/tcdata.h`, `bubasics`, coordinator logging (`ELog()`), and platform dynamic linking for non-`NEW_XBSA` AIX/Solaris builds. It is called from dump/restore paths to store and retrieve backup data through XBSA instead of tape media.

## Risks And Test Signals
Risks include dynamic-library path/symbol drift, ABI differences between external XBSA and `NEW_XBSA`, server environment hacks (`envP[0] = NULL` for TSM V5), and transaction rollover at `maxObjects`. Several error messages are misleading copy/pastes, so tests should assert return codes rather than logs alone. Test signals include mount failure, invalid server type, version rejection, successful initialization with server name, begin/end/finalize sequencing, query no-match handling, read/write buffer bounds, transaction rollover, delete no-volume mapping, and both `NEW_XBSA` and external-XBSA builds.
