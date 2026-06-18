## sources/cloud-native/buildkit/util/overlay/overlay.go

Purpose: tiny cross-platform overlay mount classifier.

Important API: `IsOverlayMountType(mount.Mount) bool` returns true when `mnt.Type == "overlay"`.

State/persistence: none. Dependencies: containerd mount type.

Integration points: Linux overlay differ uses this helper while parsing snapshot mounts. Risks: only recognizes literal `overlay`, not platform aliases or fuse-overlayfs. Test signals: indirect via overlay Linux tests.
