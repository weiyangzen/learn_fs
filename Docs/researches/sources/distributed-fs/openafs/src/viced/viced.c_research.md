# sources/distributed-fs/openafs/src/viced/viced.c

## Purpose

`viced.c` is the OpenAFS fileserver main program. It parses fileserver options, initializes logging, audit, directory buffers, RX services, host/callback/protection/VL libraries, the volume package, and background maintenance threads. Under demand-attach fileserver builds, it also coordinates startup restore and shutdown save of fileserver state.

## Important APIs, Types, And Functions

- Global configuration/state includes RX/logging flags, CPS lists, `confDir`, cache sizes, vnode/cache/callback counts, server addresses, `FS_HostUUID`, and DAFS `struct fs_state fs_state`.
- Signal/admin functions: `CheckSignal_Signal`, `ShutDown_Signal`, `viced_SuperUser`, `fs_IsLocalRealmMatch`, and `viced_syscall`.
- Maintenance threads: `FiveMinuteCheckLWP`, `HostCheckLWP`, `FsyncCheckLWP`, and `ShutdownWatchdogLWP`.
- Shutdown: `ShutDownAndCore` tranquilizes RX/volumes, flushes, prints counters, shuts down volume state, and optionally saves DAFS state.
- Option handling: `ParseRights`, `max_fileserver_thread`, `ParseArgs`, and `CheckParms`.
- External initialization: `InitPR`, `vl_Initialize`, `ReadSysIdFile`, `WriteSysIdFile`, `Do_VLRegisterRPC`, `SetupVL`, and `InitVL`.
- `main` performs process initialization and then sleeps indefinitely after server startup.

## Control Flow

`main` initializes directory paths and ihandle defaults, parses command options, opens the config directory and logs, registers soft signals, initializes audit and directory buffers, initializes `fs_state`, raises fd limits, configures volume callback hooks, initializes ACL and RX, binds the fileserver RX service on port 7000, creates RX stats service, initializes host and callback packages, registers with VLDB, initializes PR, initializes the volume package, attaches volumes, restores DAFS state before starting RX worker threads in DAFS builds, starts background maintenance pthreads, records host identity/start time, then loops forever.

Shutdown starts by making RX and volumes tranquil. DAFS shutdown marks `fs_state.mode = FS_MODE_SHUTDOWN`, shuts down the volume package, waits until the five-minute, host-check, and fsync-check threads report tranquil, then calls `fs_stateSave()` unless this is an abnormal panic shutdown or state saving was disabled.

## State And Persistence Behavior

Persistent identity is stored in the SysID file with magic/version, UUID, and registered server addresses. `ReadSysIdFile` validates it and populates `FS_HostUUID` and addresses unless NetInfo/NetRestrict supplied addresses; `WriteSysIdFile` rewrites it after successful VL address registration. DAFS state persistence is delegated to `serialize_state.c`, but this file determines when restore/save is safe relative to RX request serving and helper-thread quiescence.

## Dependencies And Integration Points

`viced.c` integrates nearly every server subsystem in this subset: RX/RXKAD/RX stats, Ubik/VL client calls, PR client calls, volume package APIs, host/callback packages, audit, command parsing, logging, directory buffers, ihandle cache, and platform soft signals. It exposes `viced_SuperUser` for RX stats authorization and sets `V_BreakVolumeCallbacks` to delayed callback-break integration unless `-novbc` is used.

## Risks And Edge Cases

- Startup ordering is critical: DAFS must restore state before RX request processing begins.
- Shutdown waits for helper threads via condition variables; bugs in tranquil flags can hang shutdown/state save.
- `ReadSysIdFile` uses `if (!(fd = afs_open(...)))`, which treats fd `0` as failure.
- VL registration conflict `VL_MULTIPADDR` is not fatal in `main`, but it indicates address ownership problems requiring repair.
- Many command-line options tune resource limits; invalid combinations can silently clamp values, so behavior depends on logs.

## Test Signals

High-value tests include option parsing boundaries, RX bind address selection with NetInfo/NetRestrict, SysID read/write round trip, VL registration retry/conflict paths, DAFS restore-before-RX ordering, shutdown state-save only after helper-thread quiescence, and abnormal shutdown skipping state save.
