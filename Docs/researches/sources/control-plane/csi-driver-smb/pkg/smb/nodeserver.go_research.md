# sources/control-plane/csi-driver-smb/pkg/smb/nodeserver.go

## Purpose
CSI node service implementation for staging, publishing, unpublishing, unstaging, volume stats, node info, and mount-related helpers.

## Important APIs, Types, and Functions
Implements `NodePublishVolume`, `NodeUnpublishVolume`, `NodeStageVolume`, `NodeUnstageVolume`, `NodeGetCapabilities`, `NodeGetInfo`, `NodeGetVolumeStats`, `NodeExpandVolume`, `ensureMountPoint`, Kerberos helpers, mount flag helpers, and group permission helpers.

## Control Flow
Publish validates request, handles ephemeral volumes by staging directly at target, otherwise bind-mounts staging to target and propagates read-only flags. Stage validates volume/source, locks by volume-target, resolves credentials from secrets or Kubernetes secret for ephemeral volumes, prepares Linux CIFS or Windows SMB options, handles Kerberos caches, ensures mountpoint, appends subDir, validates traversal, and mounts with a timeout. Unstage cleans SMB mountpoint and deletes Kerberos cache. Stats read filesystem metrics and cache responses.

## State and Persistence
Creates mountpoints, bind mounts, SMB/CIFS mounts, Kerberos cache files and symlinks, and timed volume stats cache entries. Uses per-volume operation locks.

## Dependencies
Depends on CSI protobufs, mount-utils, Kubernetes volume metrics, os/filepath, runtime, base64, klog, Azure timed cache, utility timeout helpers, and platform-specific SMB mount helpers.

## Integration Points
Called by kubelet and by controller internal mount/unmount paths. Integrates with Kubernetes secrets for ephemeral volume credentials and `volumeMountGroup` for group access.

## Risks and Edge Cases
Mount timeout is fixed at 110 seconds. Password special characters change sensitive option shape. Kerberos symlink is shared per UID and requires careful cleanup. Cached stats can become stale for up to cache duration.

## Test Signals
Mapped tests are outside this item, but rg shows node tests covering stage/publish/unpublish/unstage, stats, Kerberos helpers, mountpoint behavior, and group mode helpers.
