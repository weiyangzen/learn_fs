# sources/cloud-native/moby/daemon/graphdriver/register/register_zfs.go

Purpose: blank-import registration hook for the ZFS graphdriver.

Important APIs and control flow: imports the ZFS graphdriver for side effects on Linux or FreeBSD unless `exclude_graphdriver_zfs` is set. The imported package registers `"zfs"`.

State, dependencies, and risks: no direct state. Build tags control whether ZFS is included in driver selection. Runtime initialization still requires the `zfs` command, `/dev/zfs`, and a valid dataset. The signal is successful platform build and graphdriver registration.
