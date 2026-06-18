# sources/control-plane/csi-driver-nfs/pkg/nfs/nodeserver_test.go

Purpose: validates CSI node publish/unpublish, node info/capabilities, volume stats, and stale NFS handle detection.

Important APIs and helpers: `TestNodePublishVolume`, `TestNodeUnpublishVolume`, `TestNodeGetInfo`, `TestNodeGetCapabilities`, `getTestNodeServer`, `TestNodeGetVolumeStats`, and `TestIsStaleFileHandle`.

Control flow: publish cases check missing capability, missing volume ID, missing target, lock conflicts, target creation, readonly mounts, already-mounted targets, PV/PVC metadata contexts, zero mount permissions, invalid octal permissions, and injected `ESTALE` remount. Unpublish cases check required fields, not-mounted cleanup, and lock conflicts. Stats cases cover missing IDs/paths, nonexistent paths, and normal statfs on a temporary directory.

State and persistence behavior: creates and removes test directories under the repository/test utility workdir and `/tmp`. Temporarily overrides `lstatFunc` to simulate stale handles and restores it in cleanup.

Dependencies and integration points: depends on `NewFakeMounter`, `NewEmptyDriver`, CSI protobufs, gRPC status codes, test utility path helpers, and `syscall.ESTALE`.

Risks: fake mounter means no real kernel mount table or NFS server is exercised. Some table fields are unused or only partially asserted. Volume stats success depends on host filesystem metric availability.

Test signals: useful unit-level signal for validation, locking, idempotency, stale remount behavior, and stat response construction.
