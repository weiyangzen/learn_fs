# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/Include/AFSDefines.h

## Purpose
`AFSDefines.h` centralizes fs-layer constants, flags, registry value names, device names, network-provider constants, extent geometry, GUIDs, and the `PAFSSetInformationToken` function pointer type.

## Important APIs, Control Flow, And State
Registry defines cover debug flags, trace level/subsystem/buffer size, max dirty/direct I/O, NetBIOS and mount-root names, shutdown status, and clean-shutdown requirement. Device defines name the control device and symbolic link. Flag macros wrap bit tests and interlocked set/clear operations. Timing/cache constants define one-second units, server flush/purge delays, read-ahead granularity, directory enumeration buffer size, and write-to-EOF detection.

The header defines directory CCB/entry flags, network-provider `WN_*`, `RESOURCE*`, `RESOURCETYPE*`, `RESOURCEUSAGE*`, and `RESOURCEDISPLAYTYPE*` constants, instance identifiers, extent skip-list geometry, maximum extent release count, control-device security GUID, debug ring maximum/wrap flag, connection/process/auth-group flags, special share count, OpenAFS DFS reparse tag/GUID, directory enumeration sentinel indexes, library state flags, custom DACL SID GUID and length, and `PAFSSetInformationToken`.

## Dependencies And Integration Points
The constants are consumed across initialization, logging, process/auth, provider enumeration, extent/cache management, directory enumeration, library lifecycle, and security DACL code. GUID definitions rely on `initguid.h` inclusion from `AFSCommon.h`.

## Risks And Test Signals
Interlocked flag macros assume lvalue widths compatible with `InterlockedOr/And`. `QuadAlign` casts through `ULONG`, which is unsafe for 64-bit pointer-sized values if used on pointers. Constants duplicated from Windows networking headers can drift. Tests should include 32/64-bit builds, static analysis for pointer truncation, trace buffer clamping, library flag transitions, provider enumeration values, and reparse tag/GUID correctness.
