## sources/control-plane/ceph-csi/internal/cephfs/controllerserver.go

Purpose: Implements CephFS CSI controller RPCs for volume create/delete, expand, snapshot create/delete, controller publish/unpublish, and backing-snapshot/fencing metadata coordination.

Important types and functions: `ControllerServer` embeds `DefaultControllerServer` and owns `VolumeLocks`, `SnapshotLocks`, `OperationLocks`, `VolumeGroupLocks`, and `ClusterName`. Key functions include `CreateVolume`, `DeleteVolume`, `ControllerExpandVolume`, `CreateSnapshot`, `DeleteSnapshot`, `ControllerPublishVolume`, `ControllerUnpublishVolume`, `createBackingVolume*`, `checkContentSource`, `cleanUpBackingVolume`, `doSnapshot`, `getSubvolumeMetadataHandler`, `removeUserIdMapping`, and `fenceNode`.

Control flow: `CreateVolume` validates, builds admin credentials and `VolumeOptions`, checks content source, validates clone/restore/backing-snapshot rules, checks OMAP reservation state, reserves a name, creates a subvolume or clone/snapshot-backed reference, retrieves root path, sets Kubernetes metadata, and returns CSI volume context. Delete reverses backend subvolume or reftracked backing snapshot state, then undoes the journal reservation. Snapshot create reserves a snapshot, creates a CephFS subvolume snapshot, records metadata, and copies encryption config for restore.

State and persistence: Persistent state spans CephFS subvolumes/snapshots, RADOS OMAP journals via `store`, KMS/fscrypt DEKs, snapshot-backed reftracker objects, subvolume/snapshot metadata keys, and Kubernetes secrets. Locks provide in-process idempotency and collision control but do not replace backend journal consistency.

Dependencies and integrations: Uses CSI protobufs, gRPC status codes, go-ceph FSAdmin/OSD admin via core/store, Kubernetes metadata/secret helpers, reftracker errors, KMS, and Ceph OSD blocklist for fencing. Controller publish returns service-account restrictions from CephFS metadata; unpublish removes node user mapping and optionally blocklists a stale client address.

Risks and tests: Complex error rollback can leave stale OMAPs or subvolumes if backend cleanup fails. Clone pending/in-progress is mapped to `Aborted`; EAGAIN is mapped to `ResourceExhausted`. Snapshot-backed volumes have read-only and expansion restrictions. Test coverage in this subset is indirect; high-value tests are idempotent create/delete, clone retry, snapshot-backed reftracker races, fencing metadata, and metadata unsupported clusters.
