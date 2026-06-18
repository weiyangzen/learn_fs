<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_config.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_config.c

## Purpose

`icssg_config.c` is the firmware and shared-memory configuration layer for the TI ICSSG Ethernet driver. It programs MII/MIIG registers, hardware queue descriptors, MSMC buffer pools, VLAN/FDB tables, R30 firmware commands, port speed/duplex state, PVIDs, and management-queue messages used by switch, HSR/PRP offload, and EMAC modes.

## Important APIs, Types, and Functions

Key exported functions are `icssg_config_ipg()`, `icssg_config()`, `icssg_set_port_state()`, `icssg_config_half_duplex()`, `icssg_config_set_speed()`, `icssg_send_fdb_msg()`, `icssg_fdb_add_del()`, `icssg_fdb_lookup()`, `icssg_vtbl_modify()`, `icssg_get_pvid()`, `icssg_set_pvid()`, and `emac_fdb_flow_id_updated()`. Internal helpers initialize MII TX config, MIIG queue descriptors, EMAC versus firmware-offload buffer pools, and R30 command slots.

## Control Flow

`icssg_config()` clears the slice DRAM config region, initializes MIIG queues and shared-memory packet descriptors, selects link defaults, sets interface mode, configures MII/IPG/RGMII, sets PRUSS GPI/XFR/constant-table state, writes RX flow IDs, initializes the proper MSMC buffer layout, and resets R30 command words. Firmware offload paths call `icssg_init_fw_offload_mode()` and use forwarding/local-injection pools; EMAC mode calls `icssg_init_emac_mode()` and disables forwarding pools. FDB operations allocate a firmware management buffer from ICSSG hardware queues, write a `mgmt_cmd`, push it to firmware, poll for a response queue entry, copy `mgmt_cmd_rsp`, and recycle the buffer.

## State and Persistence Behavior

The file writes persistent runtime state into PRUSS DRAM, shared RAM, MSMC RAM, MIIG/MII regmaps, VLAN table entries, PVID words, buffer-pool descriptors, and firmware command queues. It updates `prueth->vlan_tbl`, `prueth->icssg_hwcmdseq`, and shared-memory FDB/VLAN material guarded by `vtbl_lock` or `cmd_lock` where required.

## Dependencies and Integration Points

It depends on register and memory offsets from `icssg_config.h`, `icssg_switch_map.h`, and `icssg_mii_rt.h`; queue primitives from `icssg_queues.c`; classifier helpers; PRUSS remoteproc/pruss config APIs; kernel `regmap`, `iopoll`, CRC/hash helpers, and Ethernet address helpers. `icssg_prueth.c`, `icssg_switchdev.c`, VLAN callbacks, multicast sync, link adjustment, and HSR/switch mode changes call into this file.

## Risks and Edge Cases

MSMC buffer base addresses must be 64 KiB aligned or setup fails. The hardware management command path can block up to 20 seconds waiting for firmware. FDB hashing and VLAN support are limited to firmware assumptions such as 256 effective VLAN IDs in callers and fixed bucket sizing. `icssg_fdb_lookup()` returns `0` both for no membership and some error-like absence cases after a successful command, so callers must handle zero as no entry. R30 commands rely on firmware clearing all command words to `EMAC_NONE`.

## Test Signals

Useful checks include EMAC and switch/HSR open-close cycles, bridge VLAN add/delete, multicast membership add/delete, PVID changes, FDB add/delete/lookup, link speed changes at 10/100/1000, half-duplex-capable DT variants, firmware command timeout injection, and regmap/trace validation of queue, buffer-pool, VLAN, and port-state writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_config.c -->
