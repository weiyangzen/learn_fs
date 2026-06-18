## sources/control-plane/ceph-csi/internal/cephfs/nodeserver.go

Purpose: Implements CephFS CSI node RPCs for staging, publishing, unpublishing, unstaging, volume stats, mount option construction, encryption unlock, fencing metadata, and health checking.

Important types/functions: `NodeServer`, `getCredentialsForVolume`, `getVolumeOptions`, `validateSnapshotBackedVolCapability`, `maybeUnlockFileEncryption`, `generateLockCookie`, `maybeInitializeFileEncryption`, `NodeStageVolume`, `setUserIdMapping`, `setClientAddress`, `startSharedHealthChecker`, `mount`, `getBackingSnapshotRoot`, `NodePublishVolume`, `NodeUnpublishVolume`, `NodeUnstageVolume`, `NodeGetCapabilities`, `NodeGetVolumeStats`, and `setMountOptions`.

Control flow: Stage validates, locks by volume ID, resolves dynamic/static/monitor-list volume options, sets net namespace, validates snapshot-backed read-only capability, creates a mounter, initializes fscrypt if needed, recovers FUSE mounts, sets user/client metadata for fencing, mounts if not already mounted, bind-mounts snapshot root for snapshot-backed volumes, unlocks file encryption, stores FUSE mountinfo, and starts a health checker. Publish validates service-account restrictions, restores FUSE if needed, checks staging mount, handles read-only/encrypted subdirectory paths, and bind mounts to the target. Unpublish/unstage stop health checks and unmount/remove paths. Stats use health checks before filesystem stats.

State and persistence: Mutates node mount table, writes/removes FUSE `NodeStageMountinfo`, stores CephFS subvolume or snapshot metadata for user ID and client address, uses RADOS object locks during fscrypt unlock, and starts health checker state in memory.

Dependencies and integrations: Uses CSI protobufs, csi-common validators/stats, core metadata, store volume parsing, mounter package, fscrypt, KMS settings embedded in volume options, Kubernetes service-account validation context, health checker manager, and Ceph cluster connections.

Risks and tests: FUSE mounter does not support encryption; snapshot-backed volumes are read-only only. Metadata operations may be unsupported by older clusters. Client address parsing and blocklisting depend on fencing being enabled and later controller unpublish. `NodeUnstageVolume` returns error if mountinfo removal fails, which can affect non-FUSE paths depending on helper behavior. Tests cover mount option precedence only; integration should cover stage/publish idempotency, encryption lock contention, FUSE recovery, service-account denial, corrupted mounts, and stats health conditions.
