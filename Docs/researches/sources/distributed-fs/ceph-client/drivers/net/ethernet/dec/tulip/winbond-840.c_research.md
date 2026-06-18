<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/winbond-840.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/winbond-840.c

Purpose: Standalone PCI Ethernet driver for Winbond W89c840 and compatible Compex/TX9882 boards. The chip is Tulip-like but has station/filter registers and a documented broken TX FIFO, so the driver maintains separate state and workarounds.

Important APIs and functions: `w840_probe1()` enables PCI, maps I/O, reads EEPROM MAC, initializes `struct netdev_private`, probes one MII PHY, and registers the netdev. `netdev_open()` requests IRQ, allocates coherent RX/TX rings, initializes registers, starts queue, and starts media timer. `start_tx()` maps skb data, uses one or two descriptor buffers for the 1 KB TX buffer limit, accounts `tx_q_bytes`, and stops the queue for ring/FIFO pressure. `intr_handler()` loops over interrupt status, handling RX, TX completion, errors, and interrupt mitigation. `netdev_rx()`, `netdev_tx_done()`, `tx_timeout()`, and `netdev_error()` own packet receive, TX completion, reset recovery, and abnormal events. Ettool and ioctl use `mii_if_info`.

Control flow: Probe is static setup. Open resets hardware and starts rings. TX descriptor ownership is set after `cur_tx` update under lock to avoid races with interrupts. Interrupts acknowledge status, process RX/TX, and throttle on work limits. Timer polls MII link every 10 seconds and applies CSR6 changes through `update_csr6()`.

State and persistence: `struct netdev_private` stores rings, DMA addresses, skb arrays, stats, timer, lock, PCI device, CSR6 shadow, MII info, PHY address, RX/TX cursors, FIFO byte accounting, and `tx_full`. No persistent storage beyond EEPROM reads.

Dependencies and integration: Includes `tulip.h` for shared descriptor/status constants but is otherwise standalone. Uses Linux PCI, DMA, netdevice, MII library helpers, CRC multicast hash, timers, and PM callbacks.

Risks: The broken TX FIFO workaround depends on `tx_q_bytes` and queue thresholds; mistakes can silently corrupt traffic. PM synchronization is complex and documented in-file. RX buffer unmap lengths depend on skb lengths. MII absent devices may not operate correctly. `tx_timeout()` performs full software reset with IRQ disabled.

Test signals: High-load ping/large packets for FIFO bug, TX queue stop/wake thresholds, MII link changes including Davicom PHY parallel detection, RX refill under allocation failure, multicast filter modes, suspend/resume with running and stopped device, and interrupt work-limit throttling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/winbond-840.c -->
