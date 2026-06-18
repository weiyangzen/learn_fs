# sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSRedirCommonDefines.h

## Purpose
Centralizes constants and debug helpers shared by OpenAFS Windows redirector components: pool tags, object type IDs, debug flags, volume/authgroup/device flags, library names, and trace/assert wrappers.

## Important APIs, Types, And Functions
Defines memory tags (`AFS_GENERIC_MEMORY_*`, FCB/VCB/CCB, extent, name, provider tags), object types (`AFS_FILE_FCB`, directory, ioctl, mountpoint, symlink, DFS, redirector), debug flags, pool states, volume flags, authgroup reparse policy flags, device flags, `AFS_LIBRARY_CONTROL_DEVICE_NAME`, and `AFS_REDIR_LIBRARY_SERVICE_ENTRY`. Inline/macro helpers include `AFS_ASSERT`, `AFSBreakPoint`, `AFSPrint`, `AFSDbgTrace`, and `try_return`.

## Control Flow
No domain algorithm. Allocation/initialization code stamps tags and types; debug code calls trace/breakpoint helpers depending on checked/free build and debugger state.

## State And Persistence
No owned state, though external trace/dump function pointers are assumed by macros. Constants influence kernel pool diagnostics, runtime flags, and service device identity.

## Dependencies And Integration Points
Depends on Windows kernel build macros and debugger primitives. Integrates redirector allocation, library control device setup, trace logging, and reparse policy.

## Risks
Pool tag reuse weakens diagnostics. `AFS_ASSERT` assumes dump callback validity. Debug behavior differs by build. Device names are ABI-sensitive.

## Test Signals
Poolmon/Verifier tag checks, checked-build breakpoint behavior, library control device open, and debug trace routing validate the definitions.
