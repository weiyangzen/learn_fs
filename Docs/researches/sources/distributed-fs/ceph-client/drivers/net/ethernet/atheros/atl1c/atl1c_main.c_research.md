# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/atl1c_main.c

## Purpose
`atl1c_main.c` is the main Linux PCI Ethernet driver for ATL1C/L2C/L1D devices. It owns PCI probe/remove, netdev registration, queue allocation, DMA descriptor setup, MAC reset/configuration, NAPI RX/TX handling, interrupt handling, transmit mapping/offloads, link-change work, suspend/resume/shutdown, and PCI error recovery.

## Important APIs, types, and functions
The file registers `atl1c_driver` through `module_pci_driver()` with a PCI ID table for Attansic/Atheros L1C/L2C/L2C_B/L2C_B2/L1D/L1D_2. `atl1c_probe()` enables the PCI device, sets a 32-bit DMA mask, maps BAR0, detects `nic_type`, allocates a multiqueue netdev, installs netdev and ethtool ops, sets NAPI instances, initializes software state, resets PCIe/MAC/PHY, reads/programs the MAC address, and registers the netdev.

The netdev API is `atl1c_netdev_ops`: open/close, start_xmit, set RX mode, change MTU, feature fix/set, MII ioctl, tx timeout, stats, and optional netpoll. Descriptor lifecycle is handled by `atl1c_setup_ring_resources()`, `atl1c_free_ring_resources()`, `atl1c_configure_des_ring()`, `atl1c_reset_dma_ring()`, and ring cleanup helpers. RX is handled by `atl1c_alloc_rx_buffer()` and `atl1c_clean_rx()`. TX is handled by `atl1c_xmit_frame()`, `atl1c_tso_csum()`, `atl1c_tx_map()`, `atl1c_tx_rollback()`, and `atl1c_clean_tx()`.

## Control flow and state behavior
Open allocates DMA rings, configures hardware, requests IRQ, checks link, enables NAPI, unmasks interrupts, and starts queues. Interrupts read `REG_ISR`, acknowledge status, schedule RX/TX NAPI, clear PHY interrupts, and queue reset/link-change work for error or link events. RX NAPI consumes valid RRD entries, unmaps RFD buffers, applies VLAN tags, passes SKBs to GRO, refills RFDs, and re-enables queue interrupts. TX maps SKB head/frags into TPDs, sets checksum/TSO/VLAN fields, rings the producer index, and completion NAPI unmaps/free SKBs and wakes stopped queues.

The adapter state persists while the netdev exists. Hardware state is reset and rebuilt across open/close, link down, reset work, suspend/resume, and PCI error recovery. `__AT_DOWN`, `__AT_RESETTING`, `work_event`, `irq_sem`, NAPI state, and ring indices coordinate concurrency.

## Dependencies and integration points
This file depends on Linux PCI, DMA, NAPI, netdev, MII ioctl, ethtool registration, PM, and PCI error recovery APIs. It depends on `atl1c_hw.c` for MAC/PHY/EEPROM/link helpers and on `atl1c.h`/`atl1c_hw.h` for descriptors and register constants. It integrates with userspace through the netdev, ethtool, MII ioctls, WoL, and module PCI binding.

## Risks
The 32-bit DMA mask is intentional because hardware has a shared high-address register; changing it would require auditing all ring/buffer programming. `atl1c_init_ring_ptrs()` appears to use `buffer_info[i]` inside the inner TX loop instead of `buffer_info[j]`, which can leave most TX buffer states uninitialized. `atl1c_change_mtu()` only changes MTU while running; when down, the new value path relies on core state without updating driver `max_frame_size` immediately. RX currently warns but does not support multi-RFD packets. Error paths around `atl1c_open()` call `atl1c_free_irq()` even after `atl1c_up()` may already have failed before IRQ allocation. Concurrency depends on careful ordering of NAPI disable, IRQ masking, and work cancellation.

## Test signals
Strong signals are probe/remove under module load/unload, RX/TX traffic with checksum, SG, TSO/TSO6, VLAN tag insertion/stripping, MTU changes including jumbo-capable devices, suspend/resume with and without WoL, cable link transitions, netpoll if configured, PCI AER recovery, DMA API debug with no leaks or wrong-direction unmaps, and NAPI interrupt re-enable under load.
