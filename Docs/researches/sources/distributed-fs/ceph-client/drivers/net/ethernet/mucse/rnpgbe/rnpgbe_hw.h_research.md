# sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_hw.h

Purpose: hardware constants for rnpgbe board families and core queue/MMIO settings.

Important declarations: N500 and N210 firmware-to-PF control/shared-memory bases, common PF-to-FW mailbox control and mask offsets, `RNPGBE_DMA_AXI_EN`, and `RNPGBE_MAX_QUEUES` set to 8.

Control flow: no executable flow. Constants are consumed by `rnpgbe_chip.c` and `rnpgbe_main.c`.

State and persistence: none directly; constants define runtime MMIO address calculations.

Dependencies and integration: included by board and PCI netdev code.

Risks: incorrect offsets break mailbox synchronization and reset paths. Queue count must match `alloc_etherdev_mq` usage and any future real TX/RX queue implementation.

Test signals: BAR2 MMIO sanity on both N500 and N210 hardware, mailbox command success, and queue count consistency in netdev registration.
