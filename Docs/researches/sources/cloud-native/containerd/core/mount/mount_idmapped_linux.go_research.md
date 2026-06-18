<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_idmapped_linux.go -->
# sources/cloud-native/containerd/core/mount/mount_idmapped_linux.go

Purpose: Linux idmapped mount primitives and id mapping parsers.

Important APIs/types/functions: `parseIDMapping`, `parseIDMappingList`, `IDMapMount`, `IDMapMountWithAttrs`, and `GetUsernsFD`.

Control flow: mapping strings must be `container-id:host-id:size`, optionally comma-separated. `IDMapMountWithAttrs` clones a mount tree with `open_tree`, applies `MOUNT_ATTR_IDMAP` plus requested set/clear attributes via `mount_setattr`, and attaches it to the target with `move_mount`. `GetUsernsFD` parses uid/gid maps and delegates to the utility helper.

State and persistence: produces a mounted tree at the target and returns an open user namespace FD from helper code. No repository-level persistence.

Dependencies and integration points: used by `mount_linux.go` for `uidmap=`/`gidmap=` mount options and overlay lowerdir remapping. Requires Linux kernel idmapped mount support and valid user namespace mappings.

Risks: accepts zero size because it only rejects negative values; mapping semantics are kernel-enforced later. Syscalls require kernel and filesystem support; partial failures close tree fds but may still depend on callers for target cleanup.

Test signals: `mount_idmapped_linux_test.go` covers valid/invalid mapping strings, writable/read-only idmapped mounts, and uid/gid remapping effects under root and kernel >= 5.12.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_idmapped_linux.go -->
