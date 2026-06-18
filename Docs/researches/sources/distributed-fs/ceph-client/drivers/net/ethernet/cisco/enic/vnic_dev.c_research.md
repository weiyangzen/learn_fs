# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_dev.c

## Purpose
`vnic_dev.c` is the core Cisco vNIC device abstraction. It discovers BAR resources, allocates descriptor rings, implements firmware device-command transports, caches firmware/stats/notify buffers, manages link/config commands, and exposes helper APIs used by ENIC and related Cisco vNIC drivers.

## Important APIs, types, and functions
- Resource discovery: `vnic_dev_discover_res()`, `vnic_dev_get_res_count()`, `vnic_dev_get_res()`.
- Ring memory: `vnic_dev_alloc_desc_ring()`, `vnic_dev_free_desc_ring()`, `vnic_dev_clear_desc_ring()`.
- Command transports: `_vnic_dev_cmd()` for legacy MMIO devcmd, `_vnic_dev_cmd2()` for WQ/result-ring devcmd2, `vnic_devcmd_init()` for devcmd2-first fallback to devcmd1.
- Command routing: `vnic_dev_cmd()`, `vnic_dev_cmd_proxy_by_index_start()`, `vnic_dev_cmd_proxy_end()`, and proxy/no-proxy helpers.
- Firmware/config/state commands: `vnic_dev_fw_info()`, `vnic_dev_spec()`, `vnic_dev_stats_dump()`, open/close/init/deinit/enable/disable/reset/status helpers, MAC/filter/VLAN-related helpers, `vnic_dev_classifier()`, overlay offload controls, and RSS capability query.
- Notify buffer support: `vnic_dev_notify_set()`, `vnic_dev_notify_unset()`, `vnic_dev_notify_ready()`, `vnic_dev_link_status()`, `vnic_dev_port_speed()`, `vnic_dev_msg_lvl()`, `vnic_dev_mtu()`.
- Lifecycle: `vnic_dev_register()`, `vnic_dev_unregister()`, `vnic_dev_get_pdev()`.

## Control flow and state
Registration stores `priv`/`pdev` and walks the BAR resource table, accepting normal and management-vNIC headers. Queue resources use a fixed stride, while singleton resources point at one MMIO region. Descriptor ring allocation aligns descriptor count, descriptor size, and base address before allocating coherent memory and setting `desc_avail` to `count - 1`.

Firmware command flow writes arguments before the command register for write commands and reads results after `STAT_BUSY` clears for read commands. It detects surprise removal by status/fetch index `0xFFFFFFFF`. Devcmd2 allocates a WQ for commands and a result ring, posts command descriptors with a write barrier, tracks posted index, result index, and color, and falls back to devcmd1 on setup failure. Proxy mode wraps commands for SR-IOV/subordinate vNIC targets.

Persistent driver state includes cached coherent firmware info, stats, and notify buffers; interrupt coalescing conversion factors; resource table; proxy mode/index; command args; and optional devcmd2 controller. Hardware state is persistent until reset/deinit through devcmds and MMIO queue setup.

## Dependencies and integration points
The file integrates PCI DMA APIs, BAR MMIO, ENIC WQ allocation for devcmd2, vNIC resource and devcmd ABIs, netdev logging, and firmware-provided capability negotiation. Higher-level ENIC code relies on these routines for every device configuration, queue resource, and firmware operation.

## Risks and test signals
High-risk areas include resource-table bounds checking, command timeout/error handling, devcmd2 ring full/color handling, coherent buffer lifetime, proxy error sign conventions, and fallback compatibility with old firmware. Test signals include probe on old/new firmware, devcmd2 fallback logs, MAC/filter/RSS/offload command success, surprise-removal paths returning `-ENODEV`, stats/notify checksums, reset/open/enable status commands, and no DMA leaks on unregister.
