# sources/cloud-native/moby/daemon/graphdriver/zfs/zfs_freebsd.go

Purpose: FreeBSD-specific ZFS graphdriver helpers.

Important APIs and control flow: `checkRootdirFs` uses `unix.Statfs` and checks `Fstypename` bytes for `"zfs"`; otherwise it logs and returns `graphdriver.ErrPrerequisites`. `getMountpoint` shortens layer IDs to at most 12 characters before an optional suffix separated by `-`, preserving a suffix when present.

State, dependencies, and risks: no persistent state. Dependencies include FreeBSD `Statfs_t`, logging, graphdriver errors, and string splitting. Risks include `id[:maxlen]` panicking if an ID shorter than 12 characters reaches this helper, though graphdriver layer IDs are normally long. The shortened mountpoint avoids FreeBSD mount/path constraints but can collide if truncated IDs share prefixes. Build and FreeBSD integration tests are the signal.
