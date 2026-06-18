# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_main.c

## Purpose
`ngbe_main.c` is the main PCI/netdev driver for Wangxun GbE PF devices. It matches PCI IDs, initializes `struct wx`, configures netdev features, handles probe/remove/suspend/resume/shutdown, opens and closes the interface, manages interrupts, service work, phylink, PTP, SR-IOV, and traffic-class reconfiguration.

## Important APIs, Types, and Functions
Important routines include `ngbe_probe()`, `ngbe_remove()`, `ngbe_open()`, `ngbe_close()`, `ngbe_up()`, `ngbe_down()`, `ngbe_setup_tc()`, `ngbe_suspend()`, `ngbe_resume()`, `ngbe_dev_shutdown()`, `ngbe_irq_enable()`, `ngbe_intr()`, `ngbe_msix_misc()`, `ngbe_misc_and_queue()`, `ngbe_request_irq()`, and `ngbe_request_msix_irqs()`. The `ngbe_netdev_ops` table delegates most packet/filter operations to shared `wx` helpers.

## Control Flow
Probe enables PCI memory, sets DMA mask, requests BARs, allocates netdev/`struct wx`, ioremaps BAR0, caps total VFs to seven, initializes shared software state, waits for flash, checks management firmware, resets hardware, validates EEPROM, configures WOL, reads EEPROM version, installs MAC filter, initializes service/interrupt scheme, initializes MDIO/phylink, registers netdev, and stores drvdata. Open controls hardware, allocates rings, configures the device, requests IRQs, connects PHY, sets queue counts, starts PTP, and calls `ngbe_up()`. Down/close stop phylink, notify VFs, disable queues/interrupts, update stats, reset filters/PTP, clean rings, free IRQs/resources, and release hardware.

## State and Persistence Behavior
Runtime state includes `wx` queues, flags, service timer/work, WOL bits, phylink/PHY pointers, interrupt scheme, PTP state, SR-IOV state, EEPROM id string, and netdev feature flags. Hardware state includes MAC/VLAN filters, GPIO, interrupts, queues, wake filters, and PF reset-done bit. WOL can affect device wake behavior across system sleep, but driver state is rebuilt on probe/resume.

## Dependencies and Integration Points
The file integrates with PCI core, netdev ops, phylink/MDIO, ethtool setup, shared `wx` library, PTP, mailbox/SR-IOV, WOL, and kernel PM. `.sriov_configure` points to `wx_pci_sriov_configure()`, and misc interrupts call `wx_msg_task()`.

## Risks and Edge Cases
Probe has many error labels; resource ownership across devm allocations, manual BAR requests, interrupt scheme, phylink, and allocated `rss_key`/`mac_table` needs failure-path coverage. `ngbe_disable_device()` notifies VFs and disables VF TX/RX only when `num_vfs` is nonzero. Shared-vector handling for seven VFs changes interrupt behavior. Suspend/resume must coordinate with WOL and netdev running state.

## Test Signals
Probe/remove all supported device IDs and subsystem variants, including GPIO-controlled SFP and NCSI/WOL variants. Test open/close with traffic, MSI-X/MSI/legacy interrupts, SR-IOV enable with seven VFs, mailbox interrupts, suspend/resume with WOL on/off, TC changes while up/down, PTP PPS events, and error injection in flash/management/reset/MDIO/register_netdev paths.
