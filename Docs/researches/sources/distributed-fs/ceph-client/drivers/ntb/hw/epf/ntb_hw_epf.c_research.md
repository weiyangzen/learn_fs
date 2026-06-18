# sources/distributed-fs/ceph-client/drivers/ntb/hw/epf/ntb_hw_epf.c

## Purpose

This file implements a host-side PCI driver that exposes a configurable endpoint-function NTB device through the generic NTB core. It maps endpoint-defined control, doorbell, peer scratchpad, and memory-window BARs; sends control commands to endpoint firmware/function logic; configures interrupts; and implements NTB ops for link control, memory windows, scratchpads, and doorbells.

## Important APIs, types, and functions

`struct ntb_epf_dev` embeds `struct ntb_dev` and stores a device pointer, command mutex, BAR mapping table, memory-window/scratchpad/doorbell counts, mapped control/doorbell/peer-spad regions, scratchpad offsets, a last doorbell value, and the valid doorbell mask.

Command protocol constants define control-register offsets (`NTB_EPF_COMMAND`, `NTB_EPF_ARGUMENT`, `NTB_EPF_CMD_STATUS`, address/size registers, count registers, doorbell data/offset registers) and commands (`CMD_CONFIGURE_DOORBELL`, `CMD_TEARDOWN_DOORBELL`, `CMD_CONFIGURE_MW`, `CMD_TEARDOWN_MW`, `CMD_LINK_UP`, `CMD_LINK_DOWN`). `ntb_epf_send_command()` serializes command submission and polls status up to one second.

The NTB ops table `ntb_epf_ops` includes memory-window count/alignment/set/clear, peer memory-window count/address, link enable/disable/is-up, scratchpad and peer scratchpad read/write, doorbell valid mask, peer doorbell set, doorbell read/clear, and no-op mask operations. PCI lifecycle functions are `ntb_epf_pci_probe()` and `ntb_epf_pci_remove()`.

## Control flow and state behavior

Probe rejects PCI bridges, allocates the device state with devm, obtains the per-device BAR map from PCI ID driver data, initializes the embedded NTB device, initializes the command mutex, enables the PCI device, requests regions, enables bus mastering, sets a 64-bit or fallback 32-bit DMA mask, maps the control BAR, maps or derives peer scratchpad space, maps the doorbell BAR, allocates MSI-X or MSI vectors, requests IRQs, sends a configure-doorbell command to the endpoint, reads memory-window and scratchpad counts from the control region, validates memory-window count, and registers the NTB device.

The endpoint command path writes an argument, writes a command, polls `NTB_EPF_CMD_STATUS` for OK or ERROR, times out after one second, clears status, and releases the mutex. Link enable and disable are command wrappers. Memory-window setup writes lower/upper address and size registers and sends `CMD_CONFIGURE_MW`; clear sends `CMD_TEARDOWN_MW`.

IRQ vector 0 is treated as link event, while other vectors are doorbells. The ISR computes the vector index from `irq - pci_irq_vector(pdev, 0)`, stores `db_val = irq_no + 1`, and dispatches `ntb_link_event()` or `ntb_db_event()`. Doorbell peer signaling reads endpoint-provided doorbell entry size/data/offset from control registers and writes the data into the mapped doorbell region.

Three BAR maps are provided for TI J721E, NXP/Freescale i.MX8, and Renesas R-Car PCI IDs. These maps determine where config, peer scratchpad, doorbell, and memory windows live.

## Dependencies and integration points

The driver depends on PCI, MSI/MSI-X allocation, MMIO accessors, DMA mask setup, the NTB core, and endpoint-side firmware/function behavior that implements the command/status register protocol. It registers PCI IDs for TI J721E, Freescale `0x0809`, and Renesas `0x0030` RAM-class endpoint devices.

## Risks and edge cases

`ntb_epf_mw_to_bar()` uses `idx > ndev->mw_count`, so `idx == mw_count` can access beyond valid memory-window entries. Some BAR maps contain `NO_BAR`; callers must not request absent memory windows, and validation should ensure endpoint-reported `mw_count` matches the map. `ntb_epf_mw_set_trans()` ignores the return value from `ntb_epf_send_command()` and always returns 0 after issuing the command. `ntb_epf_mw_clear_trans()` initializes `ret = 0` and also ignores the command return, so teardown failures are hidden. `ntb_epf_peer_db_set()` computes `interrupt_num = ffs(db_bits) + 1`; `db_bits == 0` or multi-bit values are not explicitly rejected, and `ffs()` is one-based, so off-by-one behavior should be checked. `ntb_epf_deinit_pci()` unconditionally iounmaps `peer_spad_reg`, even when it aliases inside `ctrl_reg`, which may be unsafe depending on `pci_iounmap()` expectations for derived addresses.

## Test signals

Validation should include probe/remove on each BAR map, MSI-X and MSI fallback, endpoint command OK/ERROR/timeout behavior, link vector and doorbell vector interrupts, memory-window setup/teardown including endpoint errors, peer doorbell writes, scratchpad and peer scratchpad access, invalid peer/index handling, absent BAR handling, and NTB client bind/unbind. Endpoint integration tests should assert command status clearing and correct BAR layout for each platform.
