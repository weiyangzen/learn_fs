# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_main.c

## Purpose
`txgbe_main.c` is the main PCI/netdev driver for Wangxun 10/25/40GbE PF devices. It initializes shared `wx` state plus TXGBE-private state, configures netdev features and UDP tunnel offloads, handles probe/remove/shutdown, open/close/up/down/reset, service work, SR-IOV, PTP, Flow Director, phylink/PHY setup, and traffic-class changes.

## Important APIs, Types, and Functions
Important routines include `txgbe_probe()`, `txgbe_remove()`, `txgbe_open()`, `txgbe_close()`, `txgbe_up()`, `txgbe_down()`, `txgbe_reset()`, `txgbe_disable_device()`, `txgbe_setup_tc()`, `txgbe_do_reset()`, `txgbe_reinit_locked()`, `txgbe_service_task()`, `txgbe_module_detection_subtask()`, `txgbe_link_config_subtask()`, `txgbe_udp_tunnel_sync()`, `txgbe_sw_init()`, and `txgbe_init_type_code()`. `txgbe_netdev_ops` delegates common packet/filter/timestamp operations to shared `wx` helpers.

## Control Flow
Probe enables PCI memory, configures DMA/BAR/MMIO, caps total VFs to 63, installs ethtool/netdev/UDP tunnel ops, initializes `wx`, waits for flash and management firmware, resets hardware, sets feature flags, validates EEPROM checksum, installs default MAC filter, initializes service and interrupt scheme, builds EEPROM id, tests firmware host interface, allocates `struct txgbe`, initializes Flow Director state, initializes PHY/phylink, registers netdev, stores drvdata, stops TX queues, and checks PCIe bandwidth. Open allocates resources, configures hardware, sets up misc and queue IRQs, sets real queue counts, starts PTP, and completes up. Down/close disable traffic, stop link, notify VFs, reset, clean rings, free IRQs/resources, clear FDIR filters, and release hardware.

## State and Persistence Behavior
`struct wx` stores shared netdev, queues, flags, SR-IOV, PTP, RSS, Flow Director callbacks, service work, and link state. `struct txgbe` stores PHY/link/IRQ-domain/FDIR private state. Hardware state includes MAC, queues, interrupts, Flow Director, UDP tunnel ports, PF reset-done, GPIO/PHY, and firmware link settings. No disk persistence exists; EEPROM and module state are read from hardware/firmware.

## Dependencies and Integration Points
The file integrates PCI core, netdev, UDP tunnel NIC offload, ethtool, `libwx` hardware/library/PTP/mailbox/SR-IOV helpers, TXGBE hardware/PHY/AML/IRQ/FDIR subsystems, and kernel phylink. `.sriov_configure` points to `wx_pci_sriov_configure()`.

## Risks and Edge Cases
Probe error unwinding spans manual resources, devm resources, interrupt scheme, service work, PHY, and private TXGBE state. `txgbe_close_suspend()` frees resources without freeing IRQs, relying on suspend/shutdown context. FDIR filters are freed on close, so user rules do not survive close/open. AML and SP paths diverge for phylink, GPIO, RSC, TX head writeback, and firmware. VF notification during disable uses `wx_set_all_vfs()` after clearing `clear_to_send`.

## Test Signals
Probe/remove all supported SP/AML IDs, EEPROM checksum fail, firmware mismatch, PHY init fail, register_netdev fail, MSI-X/MSI/legacy interrupts, open/close with traffic, UDP tunnel port programming, TC changes, reset while up/down, SR-IOV max VFs, Flow Director mode/rules, PTP, AML module insertion/link setup, and shutdown behavior.
