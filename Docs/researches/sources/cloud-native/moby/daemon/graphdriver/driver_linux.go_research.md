# sources/cloud-native/moby/daemon/graphdriver/driver_linux.go

Purpose: Linux graphdriver priority declaration.

Important APIs and control flow: defines `priority = "overlay2,fuse-overlayfs,btrfs,zfs,vfs"`. `graphdriver.New` uses this ordered list to prefer existing prior state and to auto-select the first supported driver on a new root.

State, dependencies, and risks: there is no direct runtime state. The order encodes Linux storage policy: native overlay2 first, rootless-friendly fuse-overlayfs second, then Btrfs, ZFS, and VFS fallback. Driver init functions still perform feature detection and may return not-supported errors. Tests are indirect through graphdriver initialization and per-driver suites.
