# sources/control-plane/csi-driver-nfs/pkg/nfs/nodeserver.go

Purpose: implements the CSI Node service for publishing/unpublishing NFS volumes, reporting node identity/capabilities, returning filesystem stats, and rejecting unsupported stage/unstage/expand operations.

Important APIs and types: `NodeServer`, `NodePublishVolume`, `NodeUnpublishVolume`, `NodeGetInfo`, `NodeGetCapabilities`, `NodeGetVolumeStats`, `NodeStageVolume`, `NodeUnstageVolume`, `NodeExpandVolume`, `makeDir`, `isStaleFileHandle`, and the test-injectable `lstatFunc`.

Control flow: `NodePublishVolume` validates volume capability, volume ID, and target path, locks by volumeID-targetPath, collects mount flags and readonly mode, parses `server`, `share`, `subdir`, metadata placeholders, mount options, and mount permissions, validates the final NFS source path, creates the target when missing, returns idempotently when already mounted, unmounts and remounts stale NFS handles, mounts with a timeout, and chmods when permissions are nonzero. `NodeUnpublishVolume` validates and locks, then uses forced cleanup when the mounter implements `MounterForceUnmounter`, otherwise normal cleanup. `NodeGetVolumeStats` caches statfs responses by volume ID after validating path existence.

State and persistence behavior: writes mount target directories and changes permissions on mounted paths. Uses in-memory locks and timed volume stats cache. It relies on the host mount table through Kubernetes mount utilities for actual persistence of mounts.

Dependencies and integration points: depends on CSI protobufs, gRPC status codes, klog, `k8s.io/mount-utils`, Kubernetes volume metrics, OS/syscall errors, and helper functions in `utils.go` and `nfs.go`. Controller internal mount/unmount routes through this node service.

Risks: `WaitUntilTimeout` times out the caller but cannot cancel the underlying mount goroutine. Path validation rejects only slash-separated `..`, not Windows backslash traversal. Mount options from the volume context are appended as a single string. Stats cache is keyed only by volume ID, not path, so reused IDs across paths can return stale stats until expiry.

Test signals: `nodeserver_test.go` covers validation errors, lock conflicts, missing target creation, readonly and zero-permission flows, stale handle remount, unpublish validation, node info/capabilities, statfs success/error, and stale-handle detection.
