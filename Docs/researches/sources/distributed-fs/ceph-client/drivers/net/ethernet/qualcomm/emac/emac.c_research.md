<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac.c

## Purpose
`emac.c` is the main Qualcomm EMAC Gigabit Ethernet platform driver. It owns probe/remove/shutdown, netdev operations, IRQ/NAPI integration, clock/resource setup, PHY/SGMII setup, link recovery work, hardware statistics aggregation, and feature/MTU reconfiguration.

## Important APIs, Types, and Functions
- Public helpers: `emac_reg_update32()`, `emac_reinit_locked()`, and `emac_update_hw_stats()`.
- Netdev operations: open/stop/start_xmit/change_mtu/set_features/set_rx_mode/get_stats64/tx_timeout.
- IRQ/NAPI: `emac_isr()` masks/unmasks interrupts, handles error/TX/RX/overflow bits, and schedules NAPI; `emac_napi_rtx()` processes RX and reenables RX interrupts.
- Probe helpers: `emac_init_adapter()`, `emac_clks_get()`, `emac_clks_phase1_init()`, `emac_clks_phase2_init()`, `emac_clks_teardown()`, and `emac_probe_resources()`.
- Platform lifecycle: `emac_probe()`, `emac_remove()`, and `emac_shutdown()`.

## Control Flow
Probe sets a 46-bit DMA mask, allocates an Ethernet netdev, initializes locks/stats/IRQ masks, maps core and CSR resources, enables phase-1 clocks, configures external MDIO PHY and internal SGMII, enables phase-2 clocks, sets offload features and MTU limits, initializes rings and NAPI, registers the netdev, then logs hardware IDs. Open requests the core IRQ, allocates DMA rings, opens SGMII, and brings the MAC up. Close reverses SGMII, MAC, ring, and IRQ state under `reset_lock`. Feature/MTU changes while running call `emac_reinit_locked()`, which downs MAC, resets SGMII, and brings MAC back up. Remove unregisters netdev/NAPI, cancels work, tears down clocks and MDIO, unmaps SGMII, and frees the netdev.

## State and Persistence
`struct emac_adapter` is netdev private data and persists for the platform device lifetime. Statistics are accumulated in `adpt->stats` under a spinlock because hardware counters are read-and-accumulated. Runtime reset state is serialized by `reset_lock`; recovery is deferred to `work_thread`.

## Dependencies and Integration Points
The driver integrates with platform resources, OF/ACPI matching (`qcom,fsm9900-emac`, `QCOM8070`), clock framework, DMA API, PHY/MDIO helper in `emac-phy.c`, SGMII helper in `emac-sgmii.c`, MAC ring/data path in `emac-mac.c`, ethtool setup, NAPI, and standard Ethernet netdev APIs.

## Risks and Edge Cases
- Several error paths assume `phydev`/`mii_bus` were initialized before cleanup labels; ordering changes must preserve that.
- `emac_remove()` frees the core IRQ even though `emac_close()` also frees it for opened interfaces; unregister sequencing must prevent double-free.
- `emac_set_features()` temporarily writes `netdev->features` before reinit so MAC mode sees the new state.
- Hardware stat reads accumulate registers; concurrent readers require the documented stats lock.
- ACPI platforms skip clock management entirely, so clock bugs differ between ACPI and DT systems.
- TX timeout and SGMII decode errors converge on the same reset work path.

## Test Signals
Probe/remove under DT and ACPI, open/close cycles, MTU and VLAN feature changes while up, TX timeout recovery, interrupt-driven RX/TX under load, hardware stats monotonicity, and suspend/shutdown behavior are important regression signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac.c -->
