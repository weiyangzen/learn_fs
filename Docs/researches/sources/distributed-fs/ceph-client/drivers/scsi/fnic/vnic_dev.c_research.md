# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_dev.c

## Purpose

`vnic_dev.c` is the shared Cisco vNIC device-control layer used by FNIC. It discovers hardware resources from BAR0, allocates coherent descriptor rings, wraps firmware device commands, exposes link/stats/notification helpers, and registers/unregisters the private `struct vnic_dev`.

## Important APIs, types, and functions

- `struct vnic_dev` stores PCI/device-private pointers, discovered resources, command backend, DMA notification/stat/fw buffers, interrupt mode, and devcmd2 state.
- `vnic_dev_discover_res()` parses the BAR0 resource table and records WQ/RQ/CQ/interrupt/devcmd resources.
- `vnic_dev_get_res_count()` and `vnic_dev_get_res()` return resource counts and MMIO addresses.
- `vnic_dev_alloc_desc_ring()`/`vnic_dev_free_desc_ring()` allocate 512-byte-aligned coherent descriptor rings.
- `vnic_dev_cmd1()` implements the legacy MMIO devcmd register path.
- `vnic_dev_cmd2()` implements the queued devcmd2 path using a WQ plus a result ring and color bit.
- `vnic_dev_cmd_init()` selects devcmd2 when present and falls back to devcmd1.
- Helper commands include firmware info, dev-specific values, stats dump/clear, open/close/init/enable/disable, reset status, MAC address, packet filter, address add/delete, notification buffer setup, link status, port speed, MTU, message level, and link-down count.

## Control flow

Registration allocates a `struct vnic_dev`, binds PCI/private pointers, and discovers BAR resources. Command initialization checks for `RES_TYPE_DEVCMD2`; if present it allocates a devcmd2 WQ and results ring, initializes firmware with `CMD_INITIALIZE_DEVCMD2`, and then routes future commands through queued descriptors. Otherwise it uses the legacy status/cmd/args MMIO block.

Legacy commands check `STAT_BUSY`, write input args, post the command, poll status in 100 microsecond intervals, translate firmware errors, and read output args. Devcmd2 commands check queue fullness through posted/fetch indexes, fill a command descriptor, post it, and poll the next result entry until its color matches.

## State and persistence behavior

The object caches DMA buffers for notification, stats, and firmware info. `vdev->args[]` is scratch space for command execution. Resource mappings persist for the life of the device. Notification state is shared with firmware through a checksum-protected coherent structure copied by `vnic_dev_notify_ready()`.

## Dependencies and integration points

The file depends on PCI DMA APIs, `vnic_resource.h`, `vnic_devcmd.h`, `vnic_wq.h`, and `vnic_stats.h`. It is the lower layer for FNIC queue setup, firmware control, link monitoring, and statistics retrieval.

## Risks and edge cases

- `vnic_dev_cmd1()` maps firmware error indexes through a small local array; unexpected firmware error values would index out of bounds.
- Devcmd2 treats `0xffffffff` posted/fetch indexes as surprise-removal evidence and returns `-ENODEV`.
- `vnic_dev_spec()` copies a value into the caller even if the command returned an error.
- Notification checksum polling loops until a consistent copy appears; corrupted shared memory could spin longer than expected.
- `vnic_dev_set_default_vlan()` returns the command return code cast to `u16`, not the output argument, which is suspicious against the command comment.

## Test signals

Tests should exercise BAR resource parsing, ring alignment, devcmd1 fallback, devcmd2 initialization and teardown, command timeout/error paths, stats dump, notification checksum reads, link-state helpers, and surprise-removal handling.
