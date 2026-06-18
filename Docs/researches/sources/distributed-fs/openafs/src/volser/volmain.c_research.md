# sources/distributed-fs/openafs/src/volser/volmain.c

## Purpose

`volmain.c` is the executable entry point for the OpenAFS volume server (`volserver`). It initializes platform services, audit and logging, the OpenAFS volume package, Rx networking, security classes, and the Volser RPC service. It also starts the background transaction maintenance loop that periodically garbage-collects stale volume transactions and releases accumulated partition locks when the server is idle.

The file is operational glue rather than RPC business logic. Most volume operations live in `volprocs.c`, while transaction list mechanics live in `voltrans.c`; `volmain.c` owns daemon lifetime and the global policy knobs those modules consume.

## Important APIs, Types, and Globals

- `main(int argc, char **argv)` performs process initialization, option parsing, volume package setup, Rx service creation, and starts the Rx server loop.
- `ParseArgs` defines and applies command-line options for logging, Rx binding/MTU/jumbograms, worker thread count, audit sinks, sync policy, config path, restricted query policy, and server-to-server encryption policy.
- `BKGLoop` is the detached background daemon. Every `GCWAKEUP` seconds it calls `GCTrans()` and `TryUnlock()`, and reopens the log every ten loop iterations.
- `TryUnlock` releases partition locks via `VPFullUnlock()` when there are no running RPC calls and no active Volser transactions.
- `MyBeforeProc` and `MyAfterProc` update `runningCalls` under `VTRANS_LOCK`; they are installed as Rx service callbacks to make idle detection reliable.
- `shutdown_signal` in pthread builds logs live transactions at shutdown, including transaction id, volume id, and partition, then exits.
- `volser_syscall` provides the platform-specific hook for Rx/syscall integration, with Solaris ioctl, generic ENOSYS fallback, and regular `AFS_SYSCALL` paths.
- `vol_rxstat_userok` authorizes Rx statistics management through `afsconf_SuperUser`.
- `vol_IsLocalRealmMatch` delegates local-realm checks to the cell configuration directory and logs failures.

Important globals exported to other volserver code include `tdir`, `DoLogging`, `restrictedQueryLevel`, `DoPreserveVolumeStats`, `doCrypt`, Rx/network knobs, and worker/concurrency knob `lwps`.

## Control Flow

Startup begins with audit initialization and AFS server path initialization. `configDir` defaults to the server etc directory, then `ParseArgs` may override configuration, logging, Rx, thread, audit, query, and encryption options. After error table setup, platform-specific init, and logging setup, `main` initializes the volume package, local locks, directory package, and Rx networking. The background GC loop starts before the Rx services are registered.

The server opens the AFS config directory, installs the audit user realm check, builds server security objects, and creates the `VOLSER` Rx service with `AFSVolExecuteRequest` as the generated RPC dispatcher. It also creates the `rpcstats` service, installs the Rx stats authorization callback, logs the command line, and donates the main thread to the Rx worker pool with `rx_StartServer(1)`.

## State and Persistence Behavior

This file does not directly mutate volume contents, but it controls persistent side effects by initializing the volume package and exposing daemon-wide policy. Audit and logging destinations are opened here. `TryUnlock` closes process-held partition lock descriptors. Signal shutdown logs active transactions and exits without rollback, warning that affected volumes may require salvage. `runningCalls` is in-memory state protected by `VTRANS_LOCK`.

## Dependencies and Integration Points

It depends on the OpenAFS volume package, Rx, auth/cell configuration, audit, platform wrappers, `volprocs.c` (`VPFullUnlock` and RPC dispatcher behavior), `voltrans.c` (`TransList`, `GCTrans`), and common logging/error helpers declared in `volser_internal.h`.

## Risks and Edge Cases

Risks include abrupt signal shutdown during volume mutation, incorrect active-call accounting causing premature or delayed partition unlock, process-wide effects from command-line policy, address binding errors with netinfo/netrestrict, weakened principal validation under `-allow-dotted-principals`, and platform-specific divergence between pthread and LWP builds.

## Test Signals

Useful tests include daemon startup with default and explicit config paths, logging modes and invalid logging option combinations, restricted query policy, server-to-server crypto modes, Rx bind with netinfo/netrestrict, signal shutdown during a long transaction, periodic GC, and partition unlock only after calls and transactions are idle.
