
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_main.c

## Purpose

This file is the main HIBMCGE PCI/netdev driver. It registers the PCI driver, handles probe/shutdown/module lifecycle, initializes hardware/IRQ/MDIO/debugfs/service work, implements netdev operations, manages unicast MAC filters, and coordinates periodic diagnostics/stat updates and reset scheduling.

## Important APIs, Types, and Functions

- `hbg_probe()` allocates the netdev, maps PCI BAR0, initializes hardware subsystems, configures netdev features/ops, sets MTU/MAC/ethtool ops, and registers the netdev.
- `hbg_net_open()` initializes TX/RX rings, enables interrupts and MAC, starts the queue, and starts PHY.
- `hbg_net_stop()` stops PHY/queue/MAC/IRQs, tears down rings, asks hardware to clear TX/RX state, and rebuilds registers.
- `hbg_net_set_mac_address()`, `hbg_net_set_rx_mode()`, and MAC-table helpers manage the hardware unicast filter.
- `hbg_service_task()` handles scheduled error resets, NP link repair, BMC diagnostic pushes, and 30-second stats accumulation.
- `hbg_module_init()` registers debugfs, installs PCI error handlers, and registers the PCI driver.

## Control Flow

Probe allocates `struct hbg_priv` inside the netdev, enables PCI with managed APIs, sets a 32-bit DMA mask, maps BAR0, sends hardware init, initializes IRQs, MDIO/PHY, MAC filter table, delayed work, debugfs, and default pause settings. Netdev open allocates rings before enabling hardware traffic. Netdev stop disables traffic before freeing rings, then resets/rebuilds hardware so RX FIFO references to freed buffers are cleared.

MAC filtering keeps the host MAC at index 0, stores additional unicast addresses in a software table backed by hardware station-address slots, and disables the UC filter when the table overflows or promiscuous mode is requested. MTU changes are rejected while the interface is running.

The service task reschedules itself every second. It handles reset and NP-link-failure bits, pushes diagnostics only when requested, and periodically accumulates 32-bit hardware stats.

## State and Persistence

Persistent state includes netdev features, PCI BAR mapping, `priv->state` bits, MAC table, saved pause settings, stats, delayed work, and hardware register configuration. Device-managed actions clean up delayed work, debugfs subtrees, PHY connection, MDIO bus, IRQs, and netdev registration.

## Dependencies and Integration Points

The file integrates all HIBMCGE modules: hardware, MDIO/PHY, IRQ, TX/RX, ethtool, debugfs, error recovery, diagnostics, and PCI AER. It depends on PCI, netdev, PHYLIB, VLAN constants, unicast filter helpers, RTNL-mediated close/open in reset paths, and module init/exit infrastructure.

## Risks and Edge Cases

`hbg_hw_txrx_clear()` relies on ring teardown happening first; calling it with live buffers would let hardware reference freed memory. MAC filter overflow intentionally disables filtering, increasing received traffic. MTU changes are down-only. The service task starts immediately during probe, so it can run before netdev registration but after core initialization; helpers must tolerate that ordering. `hbg_net_get_stats()` adds `rx_frame_long_err_cnt` twice to `rx_length_errors`, which may overstate that aggregate.

## Test Signals

Signals include PCI probe for Huawei device `0x3730`, BAR0 mapping, netdev registration, open/stop cycles without DMA leaks, MAC address changes and UC filter overflow behavior, promiscuous toggling, down-only MTU changes, periodic stats updates, reset and NP-link service actions, clean shutdown with interface up, and debugfs lifecycle.
