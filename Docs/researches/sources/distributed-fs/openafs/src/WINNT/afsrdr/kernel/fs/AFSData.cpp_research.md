# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSData.cpp

Purpose: defines global storage for the Windows OpenAFS redirector kernel module. The `NO_EXTERN` include pattern makes this translation unit own the globals declared elsewhere.

Important APIs/types/functions: globals include `AFSDriverObject`, `AFSDeviceObject`, `AFSRDRDeviceObject`, `AFSFastIoDispatch`, `AFSRegistryPath`, debug/trace flags, server/share names, cache-manager callbacks, max direct/dirty IO settings, debug-log buffers/events, dump trace state, `AFSAuthGroupFlags`, `AFSActiveAuthGroup`, `AFSNoPAGAuthGroup`, `AFSSetInformationToken`, and `AFSDebugTraceFnc`.

Control flow: no executable control flow beyond static initialization. Other modules read/write these globals during driver initialization, dispatch, tracing, memory handling, auth, and shutdown.

State/persistence: all state is process/kernel global and initialized to null/zero or default function pointers. Registry-reading code in `AFSGeneric.cpp` later populates debug and size settings. No direct persistence here.

Dependencies/integration: included by all `AFSCommon.h` consumers through extern declarations. It anchors shared device object pointers, fast I/O dispatch table, cache manager callbacks, and AuthGroup globals used across this subset.

Risks: globals create broad implicit coupling and initialization-order hazards. Incorrect default values can disable tracing, break device dispatch, or make special AuthGroup comparisons invalid. The exported C linkage block means name/linkage assumptions matter.

Test signals: driver initialization should verify all global pointers/strings/callbacks are populated before dispatch use; shutdown should leave no dangling dump/debug buffers; AuthGroup code needs initialized NoPAG/active GUIDs before requests are processed.
