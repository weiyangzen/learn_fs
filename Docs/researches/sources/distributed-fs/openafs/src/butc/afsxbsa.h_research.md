# sources/distributed-fs/openafs/src/butc/afsxbsa.h

## Purpose
`afsxbsa.h` supplies the in-tree XBSA/BSA compatibility header used when `NEW_XBSA` is enabled. It defines the BSA scalar types, constants, return codes, object/query/transaction structures, BSA function prototypes, and adapter-global state used by `afsxbsa.c`.

## Important APIs, Types, And Functions
The header maps BSA integer types to C scalar/paired-word forms and defines API/version constants (`BSA_API_VERSION`, `BSA_API_RELEASE`, `BSA_API_LEVEL`), ADSM-specific bounds, BSA maximum string sizes, and BSA return codes. It defines key data types including `ObjectName`, `ObjectOwner`, `ObjectDescriptor`, `QueryDescriptor`, `DataBlock`, `SecurityToken`, `CopyId`, `Vote`, `ObjectType`, `ObjectStatus`, `CopyType`, schedule/access policy structures, and the adapter `xGlobal`. It declares the BSA data movement functions implemented in `afsxbsa.c` and helper routines such as `xlateRC()`, `xparsePath()`, `StrUpper()`, `ourTrace()`, `ourLogEvent_Ex()`, `ourRCMsg()`, and `stdXOpenMsgMap()`.

## Control Flow
As a header, it has no runtime control flow. It controls compilation by including TSM DSM headers, declaring `extern "C"` linkage for C++, defining call-sequencing flags and operation states, and providing the `XOPENRETURN()` macro that traces and returns from adapter functions.

## State And Persistence
The header declares `xopenGbl` and trace buffers as externs. `xGlobal` holds DSM session info, initial BSA owner, session flags, current operation, current copy type, and query look-ahead storage. Persistent effects are not in the header, but these declarations govern how `afsxbsa.c` tracks external TSM session state while manipulating persistent TSM objects.

## Dependencies And Integration Points
It directly depends on IBM TSM DSM headers and is included by `butc_xbsa.h` under `NEW_XBSA`. The type definitions must match what `butc_xbsa.c` expects from a platform XBSA library so the coordinator can use either the external library or this adapter through the same function-pointer surface.

## Risks And Test Signals
The typedefs use legacy assumptions such as `unsigned long` widths and two-word 64-bit structures, so ABI behavior matters across 32-bit and 64-bit platforms. String typedefs are fixed-size arrays that rely on callers to leave room for terminators. `XOPENRETURN()` uses `sprintf()` into global trace storage and is not thread-local. Test signals include compile checks against supported TSM header versions, ABI/sizeof checks for descriptors and `DataBlock`, and functional tests that verify `butc_xbsa.c` can call the same interface in `NEW_XBSA` and non-`NEW_XBSA` builds.
