# sources/distributed-fs/openafs/src/fsprobe/fsprobe.c

## Purpose
Implements the AFS FileServer probe facility. It initializes Rx connections to one or more file servers and volume servers, periodically collects statistics and partition information, and calls a user-supplied handler after each probe sweep.

## Important APIs, Types, And Functions
Public functions are `fsprobe_Init`, `fsprobe_Cleanup`, `fsprobe_ForceProbeNow`, and `fsprobe_Wait`. Important private pieces are `fsprobe_CleanupInit`, `fsprobe_LWP`, `XListPartitions`, globals `fsprobe_numServers`, `fsprobe_ConnInfo`, `fsprobe_Results`, `fsprobe_ProbeFreqInSecs`, `fsprobe_initflag`, `fsprobe_Handler`, `fsprobe_force_lock`, and `fsprobe_force_cv`.

## Control Flow
`fsprobe_Init` validates arguments, initializes locks and callback stubs, allocates connection/stat/result arrays, initializes Rx, creates null client/server security objects, opens file-server and volume-server connections for each socket, lists partitions, creates an AFS callback service using `RXAFSCB_ExecuteRequest`, starts the Rx server, and launches the probe thread. `fsprobe_LWP` loops forever: increments probe count, clears result arrays, calls `RXAFS_GetStatistics64` with fallback to `RXAFS_GetStatistics`, queries volume partition information via 64-bit or old APIs, calls the registered handler, then waits for the configured interval or a force-probe signal. `fsprobe_Cleanup` destroys Rx connections and optionally frees arrays.

## State And Persistence
State is process-global: server count, connection array, latest results, probe number, thread, locks, and cached partition lists. No disk state is written. The probe thread is not explicitly stopped by cleanup.

## Dependencies And Integration Points
Integrates with Rx, rxnull security, generated fsint callback stubs, volser partition APIs, hostutil name lookup, OPR mutex/condition primitives, and `fsprobe_callback.c`.

## Risks And Test Signals
Major risks include infinite probe thread lifetime, cleanup racing with the thread, global `newvolserver` protocol detection shared across all servers, unchecked allocation of `stats64.ViceStatistics64_val`, and limited copying into fixed host/name buffers. Tests should cover initialization failures, partial connection failures returning `-2`, forced probes, 64-bit and old statistics fallbacks, partition listing fallback, cleanup after failed init, and handler invocation counts.
