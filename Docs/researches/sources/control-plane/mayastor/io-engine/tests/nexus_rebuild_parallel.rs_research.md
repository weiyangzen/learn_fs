# sources/control-plane/mayastor/io-engine/tests/nexus_rebuild_parallel.rs

Purpose: stress-tests concurrent rebuild capacity by creating 20 volumes across three nodes, then adding the missing replica to every nexus and monitoring until all rebuilds complete.

Important APIs/types/functions: `Volume`, `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, `GrpcConnect`, `ChildState`, `Status`, tonic `Code`, and `monitor_volumes`.

Control flow: the test creates three large aio backing files, starts three io-engine containers with `/tmp` bind mounts, creates one pool per node, then creates 20 volumes. Each volume gets three replicas, but the initial nexus uses only replicas 1 and 2. The test then adds replica 0 to each nexus, starting rebuilds, and `monitor_volumes` polls child states until all are online or timeout/fault occurs.

State and persistence behavior: no persistent store. The meaningful state is per-volume child state and rebuild progress. `Faulted` immediately fails the monitor, while `Degraded`/`Unknown` keeps polling.

Dependencies and integration points: compose, aio bdev files, remote NVMf replica shares, gRPC builders, and timed polling.

Risks: 30 seconds may be tight on slow hosts; the test validates state convergence but not rebuilt data contents.

Test signals: no child faults, all degraded children progress to `Online`, and timeout returns a cancelled status if rebuilds stall.
