<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_bdev_snapshot.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_bdev_snapshot.rs

Purpose: coordinates crash-consistent snapshot requests across nexus replicas. It validates requested replica topology, pauses frontend I/O, schedules per-replica snapshot commands, gathers status per replica, and resumes I/O.

Important APIs/types/functions: `NexusReplicaSnapshotDescriptor`, `NexusReplicaSnapshotStatus`, `NexusSnapshotStatus`, `ReplicaSnapshotExecutor`, `SnapshotExecutorReplicaCtx`, `ReplicaSnapshotExecutor::new`, `take_snapshot`, `Nexus::check_nexus_state`, `do_nexus_snapshot`, and `create_snapshot`.

Control flow: public `create_snapshot` requires a snapshot name, verifies nexus operations are allowed, requires non-empty children and `NexusState::Open`, pauses the I/O subsystem, builds a `ReplicaSnapshotExecutor`, runs per-replica snapshots in parallel through `join_all`, resumes I/O, and returns per-replica errno statuses plus skipped replica UUIDs. Each snapshot task is spawned on the primary reactor, relooks up the nexus and child by replica UUID, gets a nonblocking I/O handle, and calls `handle.create_snapshot`.

State and persistence: this file does not persist snapshot state itself; it sends snapshot parameters to child block device handles. It records a parsed snapshot timestamp in the returned status. The frontend pause freezes new I/O while snapshots are issued so participating healthy replicas see a consistent point.

Dependencies/integration: depends on child UUID extraction, `NexusChild` health, `SnapshotParams`, `ISnapshotDescriptor`, reactor scheduling, `CoreError::to_errno`, `nexus_lookup`, and the nexus pause/resume implementation. It assumes child devices implement `create_snapshot` on their I/O handles.

Risks: topology validation requires the replica descriptor count to equal nexus child count, even if some are skipped. `create_time` parsing uses `unwrap_or_default`, so invalid timestamps silently become default. Resume errors are logged but the snapshot result is still returned, potentially leaving initiators unable to access the nexus. Per-replica failures are encoded as status integers rather than failing the whole snapshot after dispatch.

Test signals: missing snapshot name, non-open or empty nexus, descriptor count mismatch, duplicate replica UUID, unknown replica UUID, skipped replica handling, unhealthy participating replica rejection, child handle failure mapped to errno, partial replica failures in result vector, pause failure aborting operation, and resume failure logging.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_bdev_snapshot.rs -->
