# sources/cloud-native/moby/daemon/graphdriver/fuse-overlayfs/fuseoverlayfs_unsupported.go

Purpose: unsupported-platform package stub for fuse-overlayfs.

Important APIs and control flow: under build tag `!linux`, it only declares package `fuseoverlayfs`, so the Linux implementation and driver registration are absent.

State, dependencies, and risks: no runtime state or dependencies. The integration effect is that `fuse-overlayfs` is unavailable to `graphdriver.New` outside Linux. Build success on unsupported platforms is the test signal.
