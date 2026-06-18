# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSInit.cpp

## Purpose
`AFSInit.cpp` contains `DriverEntry`, the kernel driver's primary initialization routine. It establishes global driver state, reads registry configuration, initializes tracing/dump support, creates the secure control device and symbolic link, installs dispatch and Fast I/O tables, creates control queues/resources, registers shutdown and process-notify callbacks, initializes the redirector device, and seeds the system process entry used by auth-group tracking.

## Important APIs, Control Flow, And State
`DriverEntry` first initializes global strings and OS-version-dependent callbacks, including `ZwSetInformationToken` discovery and an XP-only service table fallback on 32-bit builds. It reads registry settings through `AFSReadRegistry`, enforces optional clean-shutdown policy, allocates `AFSRegistryPath`, and records dirty shutdown state with `AFSUpdateRegistryParameter` when requested. It creates `AFSDeviceObject` via `IoCreateDeviceSecure`, initializes notification state, calls `AFSInitializeControlDevice`, and exposes `\\??\\AFSRedirector`.

The dispatch table routes IRP majors to local shims such as `AFSCreate`, `AFSRead`, `AFSWrite`, `AFSDevControl`, `AFSShutdown`, `AFSLockControl`, security handlers, and `AFSSystemControl`, with all unhandled operations defaulting to `AFSDefaultDispatch`. It also fills `AFSFastIoDispatch` and cache-manager callbacks used by the library-backed cache/Fcb layer. Runtime state initialized here includes worker queue events/resources, `AFSSysProcess`, process tree root via `AFSInitializeProcessCB`, `AFSCacheManagerCallbacks`, and `AFSDbgLogLock`.

## Dependencies And Integration Points
This file ties together registry helpers, logging, dump-file support, generic control-device setup, process/auth support, RDR device registration, Fast I/O handlers, cache manager callbacks, and all filesystem IRP dispatch modules declared in `AFSCommon.h`. It depends heavily on Windows kernel APIs: `IoCreateDeviceSecure`, `IoCreateSymbolicLink`, `IoRegisterShutdownNotification`, `PsSetCreateProcessNotifyRoutine*`, `MmGetSystemRoutineAddress`, `RtlGetVersion`, and FSD/Fast I/O structures.

## Risks And Test Signals
Initialization has many partially initialized resources; failure unwinding must keep `AFSRegistryPath`, symbolic links, control device resources, shutdown registration, and debug locks balanced. Process-notify registration deliberately ignores final registration status by resetting `ntStatus` to success, so callback absence is a possible diagnostic gap. Clean-shutdown registry flags can prevent driver load. Test signals include driver load/unload under missing registry values, clean/unclean shutdown policy, XP/Vista+ callback paths, control device access ACLs, symbolic-link communication, Fast I/O table population, and failure injection for each allocation or device creation step.
