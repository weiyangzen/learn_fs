<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/cp-library/orangefs-client.h -->
# sources/distributed-fs/orangefs/src/client/cp-library/orangefs-client.h

## Purpose
Public ABI header for the OrangeFS client DLL/library. It defines fixed-width types, permission/debug constants, object/credential/mount/attribute structures, and exported function prototypes.

## Important APIs, Types, And Functions
Key types include `OrangeFS_fsid`, `OrangeFS_handle`, `OrangeFS_credential`, `OrangeFS_object_ref`, `OrangeFS_mntent`, `OrangeFS_attr`, `OrangeFS_sysresp_lookup`, and enums for I/O type, object type, flow protocol, and encoding. It defines gossip debug masks, debug output type masks, permission bits, pointer-alignment macros for 32-bit/64-bit ABI matching, and all `DLL_CODE` client functions.

## Control Flow
No executable control flow. Consumers include this header, initialize credentials and a filesystem, perform file operations, and finalize. `CREATING_DLL` controls whether declarations are exported or imported on Windows.

## State And Persistence
The header declares data shapes that carry persistent filesystem metadata such as owner, group, permissions, timestamps, link target, distribution parameters, directory entry count, and flags. It stores no runtime state.

## Dependencies And Integration Points
Depends on C99 fixed-width types and Windows `__declspec` semantics. The structures must remain layout-compatible with PVFS internal equivalents and external callers compiled against the DLL.

## Risks And Test Signals
Risks include ABI fragility from pointer fields and manual padding, Windows-only `DLL_CODE` definitions when compiled on non-Windows platforms, constants drifting from PVFS enums/masks, and callers misunderstanding ownership of pointer fields in `OrangeFS_attr`. Test signals are 32-bit and 64-bit ABI size checks, C/C++ compile coverage, DLL import/export tests, and round-trip operations through every prototype.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/cp-library/orangefs-client.h -->
