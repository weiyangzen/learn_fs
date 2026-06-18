# sources/distributed-fs/coda/coda-src/venus/comm.h

## Purpose
This header declares the Venus communications subsystem: connection entries, server entries, probe workers, global tunables, exported communication functions, synchronization macros, and RPC statistics macros.

## Important APIs, Types, and Functions
`connent` represents one authenticated RPC2 connection for a server and uid, with `connid`, `CheckResult`, refcounting, and death marking. `srvent` represents a file server, callback connection, binding state, probe flags, bandwidth estimate, and connection factory. `probeslave` is a `vproc` worker for up probes, down probes, or forced binds. Constants define defaults for RPC retries/timeouts and SFTP windows. Functions cover initialization, server lookup, connection release, probing, multi-bind/probe, down-server reporting, bandwidth checks, and fail disconnect/reconnect.

## Control Flow
Macros `START_COMMSYNC` and `END_COMMSYNC` make lower-priority vprocs yield to higher-priority communication traffic. Timing/stat macros wrap uni- and multi-RPC calls, log packet statistics when enabled, and update operation counters.

## State and Persistence Behavior
The header exposes process-global communication tunables and `CommQueue`. No state is persisted, but these declarations govern all Venus RPC access to persistent Coda data.

## Dependencies and Integration Points
It depends on RPC2, SFTP, Vice interfaces, callback types, collection utilities, `fso`, `venusrecov`, `vproc`, and volume classes. It is included by most Venus components that perform file server RPCs.

## Risks and Test Signals
Risks are macro side effects, priority starvation, hidden friend coupling, and inconsistent timing builds. Tests should compile with and without `TIMING`, exercise priority synchronization, and verify public error mappings through representative Vice operations.
