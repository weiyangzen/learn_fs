<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/initlayer/setup_unix.go -->
# sources/cloud-native/moby/daemon/initlayer/setup_unix.go

Purpose: populates the init layer used as a top readonly layer for containers on Linux/FreeBSD.

Important APIs and control flow: `Setup(initLayerFs, uid, gid)` iterates required container mountpoint paths, unlinks any existing path components inside the init layer, creates missing parent directories, creates required directories/files with ownership, and creates `/etc/mtab` as a symlink to `/proc/mounts`.

State and persistence: mutates the init layer filesystem tree by creating directories, files, symlinks, and ownership. It removes stale path entries before recreation.

Dependencies and integration: used during layer initialization for containers and depends on `moby/sys/user` chown helpers plus `unix.Unlink`.

Risks: it unlinks path prefixes under the init layer, so correct path joining is critical. File creation uses mode `0755` for placeholder files. `f.Chown` and `f.Close` errors are not fully checked in sequence.

Test signals: no direct tests here; container creation and rootfs setup integration tests cover behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/initlayer/setup_unix.go -->
