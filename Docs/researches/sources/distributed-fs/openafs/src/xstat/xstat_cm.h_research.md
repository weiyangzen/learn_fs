# sources/distributed-fs/openafs/src/xstat/xstat_cm.h

## Purpose

`xstat_cm.h` is the public interface for the Cache Manager extended statistics collector implemented in `xstat_cm.c`. It defines initialization flags, connection/result structures, exported globals, and the functions a monitoring program uses to start, force, wait for, and clean up cache-manager probes.

## Important APIs and Types

- Flags: `XSTAT_CM_INITFLAG_DEBUGGING` enables diagnostic output; `XSTAT_CM_INITFLAG_ONE_SHOT` makes the probe thread stop after one collection round.
- `struct xstat_cm_ConnectionInfo` stores the target socket, Rx connection, and resolved host name.
- `struct xstat_cm_ProbeResults` stores the current probe number, probe time, connection pointer, collection id, callback data buffer, and RPC result status.
- Exported globals expose connection count/array and latest probe results.
- `xstat_cm_Init`, `xstat_cm_ForceProbeNow`, `xstat_cm_Cleanup`, and `xstat_cm_Wait` are the public lifecycle functions.

## Control Flow and State

The header describes the required lifecycle: call `xstat_cm_Init` first with sockets, interval, handler, flags, and collection ids; read latest results from exported globals inside the handler; optionally force probes; wait for one-shot or continuous operation; call cleanup when done. Runtime state is defined in `xstat_cm.c`, not in this header.

## Dependencies and Integration Points

The header includes platform socket headers, Rx definitions, generated `afscbint.h`, and `afs_stats.h`. It defines `FSINT_COMMON_XG` before including stats so applications can include xstat and fsint interfaces together. Installed copies are produced by `src/xstat/Makefile.in`.

## Risks and Test Signals

Because the interface exposes global mutable state instead of opaque handles, only one active collector instance is supported per process. ABI/API changes to the structs affect external monitoring tools. Build tests should include this header from standalone consumers on Unix and NT environments; runtime tests should validate the documented lifecycle against `xstat_cm.c`.
