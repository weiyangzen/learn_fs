# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-mcd-phy.c

## Purpose
This file implements MCD D-PHY setup for IPU6 ISYS platforms with one or two MCD PHY blocks. It applies large per-lane/port register tables for 1-, 2-, and 4-lane configurations, powers PHY blocks with reference counting, and programs all active sensor PHY configurations discovered by the async notifier.

## Important APIs, types, and functions
`common_init_regs[]` holds common PHY initialization writes. `x1_*`, `x2_*`, and `x4_*` register tables encode per-port lane configurations. `ipu6_isys_mcd_phy_powerup_ack()`, `ipu6_isys_mcd_phy_powerdown_ack()`, `ipu6_isys_mcd_phy_reset()`, and `ipu6_isys_mcd_phy_ready()` manage hub power/reset/ready state. `ipu6_isys_mcd_phy_common_init()` applies common init for PHYs represented by bound sensors. `ipu6_isys_driver_port_to_phy_port()` normalizes driver CSI port numbering to PHY port numbering and validates lane counts. `ipu6_isys_mcd_phy_config()` writes per-sensor PHY tables. Public `ipu6_isys_mcd_phy_set_power()` performs refcounted power transitions.

## Control flow and integration points
CSI-2 stream enable calls `ipu6_isys_mcd_phy_set_power()`. If the target PHY already has users, the refcount is incremented and no reconfiguration is done. Otherwise the code powers up, deasserts reset, applies common init for all bound sensors, applies per-port/lane config from notifier metadata, asserts reset release/ready sequencing, then sets refcount to one. On disable, the refcount is decremented and the PHY is powered down only when the last user stops.

## State, persistence, and dependencies
Persistent state is the static `phy_power_ref_count[]` per PHY and hardware register state. The config walker depends on `isys->notifier.done_list` entries carrying `sensor_async_sd` CSI-2 port/lane data. It also depends on IPU6 platform CSI register definitions, `isp->base`, `isys->pdata->base`, poll timeouts, and V4L2 async notifier state.

## Risks and test signals
Risks are global static refcounts across devices, notifier-list assumptions during power transitions, invalid port-to-phy remapping, table errors in hard-coded register values, unsupported 4-lane on invalid ports, and missing rollback after config/ready failures. Test signals include multi-camera concurrent streaming sharing one PHY, balanced refcount powerdown, valid 1/2/4-lane ports, PHY power/ready ack success, repeated stream toggles, and no CSI receiver errors after common/per-port config.
