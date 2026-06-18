# sources/distributed-fs/ceph-client/drivers/ntb/hw/amd/ntb_hw_amd.c

## Purpose

This file implements the AMD PCIe Non-Transparent Bridge hardware driver. It binds to supported AMD/Hygon PCI devices, maps NTB MMIO registers, exposes NTB hardware operations to the generic NTB core, manages memory windows, scratchpads, doorbells, link events, MSI/MSI-X/INTx interrupts, heartbeat polling, side-info readiness state, debugfs diagnostics, and PCI lifecycle.

## Important APIs, types, and functions

The driver state is `struct amd_ntb_dev` from `ntb_hw_amd.h`. Hardware ops are provided through `amd_ntb_ops`, including memory-window count/alignment/translation, peer memory-window address, link status/enable/disable, doorbell masks/read/clear/peer-set, scratchpad read/write, and peer scratchpad read/write.

Memory-window functions include `ndev_mw_to_bar()`, `amd_ntb_mw_count()`, `amd_ntb_mw_get_align()`, `amd_ntb_mw_set_trans()`, `amd_ntb_peer_mw_count()`, and `amd_ntb_peer_mw_get_addr()`. Link functions include `amd_ntb_get_link_status()`, `amd_poll_link()`, `amd_link_is_up()`, `amd_ntb_link_is_up()`, `amd_ntb_link_enable()`, and `amd_ntb_link_disable()`.

Interrupt and event handling is split across `ndev_init_isr()`, `ndev_deinit_isr()`, `ndev_interrupt()`, `ndev_vec_isr()`, `ndev_irq_isr()`, `amd_handle_event()`, and `amd_handle_db_event()`. Side-info and heartbeat helpers are `amd_set_side_info_reg()`, `amd_clear_side_info_reg()`, `amd_init_side_info()`, `amd_deinit_side_info()`, and `amd_link_hb()`.

PCI lifecycle is handled by `amd_ntb_pci_probe()`, `amd_ntb_pci_remove()`, `amd_ntb_pci_shutdown()`, `amd_ntb_init_pci()`, `amd_ntb_deinit_pci()`, `amd_init_dev()`, and `amd_deinit_dev()`. Module init creates a top debugfs directory and registers the PCI driver.

## Control flow and state behavior

Probe allocates `amd_ntb_dev`, attaches PCI driver data, initializes the embedded `ntb_dev` with topology `NTB_TOPO_NONE` and AMD ops, enables the PCI device, requests regions, enables bus mastering, configures a 64-bit or fallback 32-bit DMA mask, maps BAR0 as `self_mmio`, derives `peer_mmio` by adding `AMD_PEER_OFFSET`, determines primary/secondary topology from the side-info register, initializes NTB capabilities, initializes interrupts, reserves the highest doorbell bit as a peer-unload notification bit, enables link-up/down event interrupts, sets local side ready, polls link, creates debugfs, and registers the NTB device with the core.

The driver supports only primary/secondary topology, not B2B. In those modes it splits the 16 scratchpads into local and peer halves by offset and starts delayed heartbeat polling. Link-up is considered true only when peer side-info readiness is observed, with extra primary-side interpretation of link-up/link-down events and peer status bits. Link-down handling can clear peer ready state and reschedule heartbeat polling until the peer returns.

Memory-window translation writes peer-side XLAT and limit registers, verifies that hardware accepted both values, and rolls back on failure. BAR1 uses 32-bit limit writes, while BAR23/BAR45 paths use 64-bit helpers. Peer memory-window address simply exposes local PCI BAR resources to clients.

Doorbell state is represented by a valid mask and a mask register guarded by `db_mask_lock`. Interrupt setup prefers MSI-X with 24 vectors and a minimum of 16, falls back to MSI, then INTx. Doorbell vectors below `AMD_DB_CNT` dispatch `ntb_db_event()`, and event vectors or single-vector mode dispatch link/power events. The highest reserved doorbell bit signals peer driver unload and triggers link-event notification plus heartbeat rescheduling.

Remove and shutdown clear local ready state, notify the peer via the reserved doorbell, unregister the NTB device, remove debugfs, cancel heartbeat work, tear down interrupts, unmap PCI resources, and free memory.

## Dependencies and integration points

This driver depends on the NTB core, PCI/MSI/MSI-X APIs, MMIO accessors, debugfs, delayed work, DMA mask setup, and AMD-specific register layout from `ntb_hw_amd.h`. It registers PCI IDs for multiple AMD and Hygon devices and exposes itself to NTB clients through `ntb_register_device()`.

## Risks and edge cases

Several index checks use `idx > count` rather than `idx >= count`, which should be reviewed against expected callers because `idx == count` can map past the last valid memory window or vector. `amd_ntb_link_disable()` logs "Enabling Link" despite disabling interrupts, which is confusing for diagnostics. Event handling switches on exact status values, so combined event bits may fall to the default path instead of handling each bit. Link status reads sometimes return success-like zero when PCI capability reads fail, potentially hiding errors. Register writes are verified for memory-window setup, but rollback paths write a mix of self/peer registers and should be tested carefully on hardware. Callbacks into NTB core may occur from IRQ context.

## Test signals

Useful tests include PCI probe/remove/shutdown on each supported device data variant, MSI-X full vector setup and fallback to MSI/INTx, memory-window translation for BAR1/BAR23/BAR45 including rollback on verification failure, scratchpad partitioning for primary and secondary topologies, doorbell mask set/clear and peer doorbell signaling, reserved unload doorbell behavior, link up/down events, peer D-state events, heartbeat recovery after peer reload, debugfs `info` reads, and NTB client bind/unbind through the core. Hardware tests should confirm side-info readiness behavior across surprise link removal and driver reload.
