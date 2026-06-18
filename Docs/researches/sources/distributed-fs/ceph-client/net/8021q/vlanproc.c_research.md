<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlanproc.c -->
# sources/distributed-fs/ceph-client/net/8021q/vlanproc.c

This file implements the optional `/proc/net/vlan` interface. It creates per-net namespace proc entries for VLAN configuration and one proc file per VLAN device.

`vlan_proc_init()` creates `/proc/net/vlan` and `/proc/net/vlan/config`; `vlan_proc_cleanup()` removes them. `vlan_proc_add_dev()` creates a per-device proc file named after the VLAN device and stores the proc entry in `vlan->dent`; `vlan_proc_rem_dev()` removes it. The `config` file uses seq operations to iterate netdevices under RCU and print VLAN device name, VID, and real device. Per-device output from `vlandev_seq_show()` prints VID, reorder flag, private flags, stats, real-device name, ingress priority map, and egress priority map.

State is per-net proc directory/config pointers and per-device proc dent pointers. The display path reads VLAN device private data, stats, and RCU-protected egress maps. Dependencies include procfs, seq_file, net namespace generic storage, netdevice iteration, and VLAN stats helpers.

Risks include proc-name collisions with `config`, stale private data if proc removal races with device teardown, and egress-map traversal without proper RCU. Tests should cover namespace init/cleanup, VLAN register/unregister and rename proc updates, reading config and per-device files, priority-map display, and builds without `CONFIG_PROC_FS` using stubs from `vlanproc.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlanproc.c -->
