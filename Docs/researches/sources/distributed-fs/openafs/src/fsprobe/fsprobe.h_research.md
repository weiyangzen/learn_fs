# sources/distributed-fs/openafs/src/fsprobe/fsprobe.h

## Purpose
Declares the public interface and result structures for the AFS FileServer probe facility.

## Important APIs, Types, And Functions
Defines `struct ProbeViceStatistics`, `struct fsprobe_ConnectionInfo`, and `struct fsprobe_ProbeResults`. Declares global `fsprobe_numServers`, `fsprobe_ConnInfo`, `fsprobe_Results`, and functions `fsprobe_Init`, `fsprobe_ForceProbeNow`, `fsprobe_Cleanup`, and `fsprobe_Wait`.

## Control Flow
The header documents the expected lifecycle: call `fsprobe_Init` with server sockets, probe interval, handler, and debug flag; inspect exported results from the handler after each sweep; optionally call `fsprobe_ForceProbeNow`; wait with `fsprobe_Wait`; and clean up with `fsprobe_Cleanup`.

## State And Persistence
The public globals expose live connection metadata and the latest probe result arrays. These are process-memory structures, not persisted data.

## Dependencies And Integration Points
The header includes socket, Rx, `afsint`, volser, and volume-interface definitions. It is installed as `afs/fsprobe.h` and used by monitoring code and `fsprobe_test`.

## Risks And Test Signals
The API exposes mutable globals, making synchronization and ownership unclear. `ProbeViceStatistics` embeds fixed `VOLMAXPARTS` disk slots and legacy 32-bit counters even though the implementation may down-convert 64-bit stats. Tests should compile external consumers, verify structure layout expectations, and exercise handler access to globals during probe updates.
