# sources/cloud-native/moby/daemon/graphdriver/zfs/zfs_unsupported.go

Purpose: fallback ZFS helper definitions for platforms outside Linux and FreeBSD.

Important APIs and control flow: under build tag `!linux && !freebsd`, `checkRootdirFs` returns nil and `getMountpoint` returns the ID unchanged. Because the main ZFS implementation is itself built only for Linux or FreeBSD, these helpers primarily satisfy package completeness when needed by build constraints.

State, dependencies, and risks: no state. The file does not register or implement ZFS by itself. Build coverage is the primary signal.
