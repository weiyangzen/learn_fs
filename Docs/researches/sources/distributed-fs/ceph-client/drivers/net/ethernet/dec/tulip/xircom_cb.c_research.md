<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/xircom_cb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/xircom_cb.c

Purpose: Standalone CardBus Ethernet driver for tulip-like Xircom cards. It uses very small coherent descriptor/buffer pages and CardBus-specific register setup rather than the shared Tulip core.

Important APIs and functions: `xircom_probe()` enables PCI/CardBus resources, disables power management, allocates 8 KiB coherent RX and TX areas, maps I/O, initializes hardware, reads MAC tuples from boot ROM space, sets up descriptors, registers the netdev, and starts transceiver setup. `xircom_open()` requests IRQ and calls `xircom_up()`. `xircom_start_xmit()` frees completed descriptors, copies skb data into one of four fixed TX buffers, gives ownership to hardware, and triggers transmit. `xircom_interrupt()` handles shared IRQ filtering, link changes, clears status, and scans TX/RX descriptors. Descriptor helper functions process completed RX/TX. CSR helpers activate/deactivate RX/TX and enable interrupts.

Control flow: Probe performs more hardware setup than typical netdev drivers, including descriptor setup and transceiver initialization before open. Open enables interrupts and queues. Runtime TX and RX use four descriptors at offsets inside coherent pages. Interrupts scan all descriptors on every handled event and return RX descriptors to hardware immediately.

State and persistence: `struct xircom_private` stores RX/TX coherent buffers, DMA handles, four TX skb pointers, MMIO base, open flag, next TX descriptor index, spinlock, PCI device, and netdev. Hardware state lives in CSR0 through CSR16 and PCI power-management config. No persistent writes.

Dependencies and integration: Uses Linux PCI, CardBus vendor ID matching, netdevice, coherent DMA, spinlocks, and optional netpoll. It does not integrate with `tulip.h` despite Tulip-like CSRs.

Risks: TX/RX are copied through fixed 1536-byte buffers, so large or VLAN-sized frames are risky. The interrupt handler clears status with `0xffffffff` despite a FIXME. Promiscuous mode is always enabled in `xircom_up()`. Error packet discard is TODO in RX. `deactivate_transmitter()` appears to clear bit 1 rather than bit 13, matching a likely bug or hardware oddity. Probe-time transceiver setup can start hardware before netdev open.

Test signals: Card insertion/removal, IRQ sharing and hot unplug status `0xffffffff`, link change carrier updates, four-descriptor TX queue pressure, RX packet length clamping, open/close descriptor removal, netpoll, and first-packet behavior noted by TODO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/xircom_cb.c -->
