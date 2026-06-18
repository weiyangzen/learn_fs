# sources/control-plane/rook/pkg/daemon/ceph/osd/daemon.go

This file is the main OSD runtime/provisioning implementation for starting OSD daemons, discovering and filtering devices, invoking ceph-volume, and querying OSD info.

`StartOSD()` creates the OSD config directory, updates LVM config, activates PVC-backed volume groups when needed, runs `ceph-volume lvm activate --no-systemd`, starts `ceph-osd`, and releases LVM devices after shutdown. Signal handling kills the `ceph-osd` process by `fuser` on SIGTERM to help volume detach. `Provision()` handles encrypted PVC KEK setup, device-mapper version logging, orchestration-status updates, PVC/raw discovery versus host discovery, optional foreign-cluster wiping, available-device selection, ceph-volume configuration, CRUSH/topology assignment, LVM release, and final status updates.

`getAvailableDevices()` is the central device filter: skips mounted devices, filesystems, existing BlueStore signatures, unavailable ceph-volume inventory, unsupported encrypted partitions/LVs, loop/LVM misuse under filters, and non-matching desired devices. It recognizes PVC data/metadata/wal pseudo-types and persistent device links. `GetOSDInfoById()` searches both LVM and raw ceph-volume lists.

State spans host devices, LVM VGs/LVs, ceph-volume metadata, ConfigMap orchestration status, environment-driven encryption, and Ceph OSD metadata. Risks include many shell-dependent branches, careful PVC/LVM release timing, global `getOsdUUID` override in tests, and partial failure handling around `ceph-osd` exit. `daemon_test.go` heavily covers UUID detection, available-device selection, and volume-group name parsing.
