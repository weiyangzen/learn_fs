# sources/control-plane/mayastor/io-engine/tests/nexus_io.rs

Purpose: broad nexus I/O coverage for NVMf multipath/ANA, NVMe reservation acquire/preempt behavior, write-zeroes correctness, subsystem pause/share races, and frozen nexus behavior after child faults or ENOSPC.

Important APIs/types/functions: `nexus_create`, `nexus_create_v2`, `nexus_lookup`, `nexus_lookup_mut`, `nexus_destroy`, `NexusNvmeParams`, `NexusPauseState`, `NvmeAnaState`, `NvmeReservation`, `NexusNvmePreemption`, `NexusStatus`, `ChildState`, `FaultReason`, `Lvs`, `PoolArgs`, v0 gRPC requests, NVMe helper functions, `MayastorTest`, `NmveConnectGuard`, and `reactor_poll!`.

Control flow: tests create local and remote nexuses over shared replicas, inspect ANA with `nvme list-subsys`, inspect reservation reports, preempt reservations with another nexus, validate shutdown and child handle cleanup, table-drive reservation types/keys, verify write-zeroes across local and remote children, race pause/resume/unshare/share, and check frozen-state operation rejection.

State and persistence behavior: PTPL directories persist reservation state across restart. In-process nexus state transitions include shared, unshared, paused, unpaused, frozen, shutdown, and destroyed. ENOSPC is distinguished from frozen subsystem state.

Dependencies and integration points: kernel `nvme` CLI, libnvme reservation report parsing, NVMf target, LVS, compose, in-process reactors, and crossbeam channels.

Risks: host NVMe tooling and kernel behavior are required; multipath test is ignored; race tests intentionally depend on ordering-sensitive behavior.

Test signals: reservation report fields, ANA state text, read/write byte patterns, zeroed reads, `Shutdown` status, child device/handle cleanup, pause/freeze state assertions, and operation rejection while frozen.
