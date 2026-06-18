# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e_main.c

## Purpose
Implements the Linux PCI/netdev driver for Atheros/Attansic ATL1E-class Ethernet controllers. It owns PCI probe/remove, netdev setup, open/close, reset recovery, DMA ring allocation, device configuration, interrupt handling, NAPI RX polling, TX mapping/offloads, PHY link management, suspend/resume/WOL, and PCI error recovery. Hardware-specific register definitions and lower-level helpers come from `atl1e.h` and `atl1e_hw.h`.

## Important APIs, Types, and Functions
Driver registration is via `atl1e_pci_tbl`, `atl1e_driver`, and `module_pci_driver`. Netdev operations are collected in `atl1e_netdev_ops`: `atl1e_open`, `atl1e_close`, `atl1e_xmit_frame`, `atl1e_get_stats`, `atl1e_set_multi`, `atl1e_set_mac_addr`, feature/MTU/ioctl handlers, TX timeout, and optional netpoll.

Lifecycle functions include `atl1e_probe`, `atl1e_init_netdev`, `atl1e_sw_init`, `atl1e_up`, `atl1e_down`, `atl1e_remove`, `atl1e_suspend`, `atl1e_resume`, `atl1e_shutdown`, and PCI AER callbacks `atl1e_io_error_detected`, `atl1e_io_slot_reset`, `atl1e_io_resume`. Ring/resource functions include `atl1e_init_ring_resources`, `atl1e_setup_ring_resources`, `atl1e_free_ring_resources`, `atl1e_init_ring_ptrs`, `atl1e_clean_tx_ring`, `atl1e_clean_rx_ring`, and `atl1e_configure_des_ring`.

Data-path functions include `atl1e_intr`, `atl1e_clean`, `atl1e_clean_rx_irq`, `atl1e_clean_tx_irq`, `atl1e_xmit_frame`, `atl1e_cal_tdp_req`, `atl1e_tso_csum`, `atl1e_tx_map`, and `atl1e_tx_queue`. Link/PHY and feature functions include `atl1e_check_link`, `atl1e_link_chg_event`, `atl1e_link_chg_task`, `atl1e_phy_config`, `atl1e_mii_ioctl`, `atl1e_vlan_mode`, `atl1e_rx_mode`, and `atl1e_set_multi`.

## Control Flow and State
Probe enables the PCI function, forces a 32-bit coherent DMA mask because the hardware has a single shared high-DMA-address register, requests BARs, allocates `net_device` plus `struct atl1e_adapter`, maps BAR0, installs MII/NAPI/timer hooks, applies module options, configures PCI command bits, initializes adapter defaults, initializes the PHY, resets hardware, reads the MAC address, creates reset/link work items, and registers the netdev.

Open initializes ring sizing, allocates one coherent ring block plus TX buffer metadata, requests a shared IRQ, and calls `atl1e_up`. `atl1e_up` initializes hardware, resets ring pointers, restores multicast/VLAN state, writes descriptor/page/register configuration, enables NAPI and interrupts, then triggers a manual interrupt to establish link state. Close and down paths set `__AT_DOWN`, stop the queue, reset MAC, disable NAPI/IRQ/timers, clear carrier, and clean TX/RX resources.

Interrupt control uses `adapter->irq_sem` to avoid nested enable/disable. The ISR reads `REG_ISR`, acknowledges status with `ISR_DIS_INT`, handles fatal PCIe/DMA conditions by scheduling `reset_task`, updates hardware stats on SMB, schedules link work for PHY/manual events, cleans TX completions, and masks RX events before scheduling NAPI. NAPI consumes RX page data until budget, then re-enables RX interrupts.

TX control flow computes descriptor demand, stops the queue if the ring lacks space, programs VLAN/802.3/offload fields, maps head and frags into TPD descriptors with 0x3000-byte segment limits, marks EOP, stores the skb on the last descriptor, writes a memory barrier, and rings `REG_MB_TPD_PROD_IDX`. RX control flow reads the current hardware write offset for the active page, validates sequence numbers, filters hardware-error frames unless `NETIF_F_RXALL`, copies packet bytes into a fresh skb, strips FCS unless requested, applies checksum/VLAN metadata, submits through GRO, advances page offsets, and toggles RX page validity when a page wraps.

Persistent state is split across `struct atl1e_adapter` flags (`__AT_DOWN`, `__AT_RESETTING`, `__AT_TESTING`), link speed/duplex, NAPI and workqueue state, the MDIO spinlock, software ring indices, coherent DMA memory, TX buffer metadata, hardware MMIO registers, PHY registers, and accumulated `hw_stats`.

## Dependencies and Integration Points
Depends on Linux PCI, DMA mapping, netdevice, NAPI, IRQ, timer, workqueue, MII ioctl, VLAN accel, checksum/TSO/GSO, ethtool setup, and optional netpoll APIs. It integrates with lower-level ATL1E hardware functions declared in `atl1e_hw.h`, option parsing from `atl1e_param.c`, ethtool ops via `atl1e_set_ethtool_ops`, and the kernel PCI error-handling framework.

## Risks
The largest risks are DMA and ring correctness. The hardware single-high-DMA-register constraint is why the driver uses 32-bit DMA; relaxing it would corrupt descriptors/pages. TX mapping unwind paths must preserve `next_to_use` and unmap only the mappings actually created. RX sequence mismatch schedules a full reset, so malformed descriptor sequencing can cause link flaps under load. Copy-based RX is simpler than page recycling but can drop packets under memory pressure. Reset work races are controlled by `__AT_RESETTING`, `__AT_DOWN`, IRQ masking, NAPI disable, and work cancellation; changes to ordering can produce use-after-free, stuck IRQs, or netdev queue hangs. Suspend/WOL paths directly program MAC/PHY while IRQs/resources may be freed, so netif-running checks must remain consistent.

## Test Signals
Exercise probe/remove, open/close, MTU changes, tx timeout reset, PCI error recovery, suspend/resume with and without WOL, netpoll if enabled, ethtool feature toggles for VLAN/RXALL/RXFCS, MII ioctl register access, multicast/promiscuous/allmulti filtering, TSO/checksum/VLAN TX, RX checksum/VLAN delivery, heavy bidirectional traffic across ring wrap, forced DMA mapping failures, link up/down events, and interrupt moderation behavior. Regression clues include queue stuck after TX_BUSY, repeated `pcie phy linkdown` or `PCIE DMA RW error`, RX sequence errors, missed carrier updates, and stats counters not moving after traffic.
