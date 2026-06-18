# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/genet/bcmgenet.c

## Purpose

`bcmgenet.c` is the main Linux platform/netdev driver for Broadcom GENET Gigabit Ethernet controllers. It binds OF/ACPI platform devices, detects GENET revision-specific register layouts, configures UniMAC, RDMA/TDMA descriptor rings, interrupts, NAPI, ethtool operations, RX classification filters, statistics, power management, and suspend/resume. It integrates with `bcmgenet.h` for register definitions/private state, `bcmmii.c` for PHY/MDIO setup, and `bcmgenet_wol.c` for Wake-on-LAN transitions.

## Important APIs, Types, and Functions

The file exposes the platform driver through `module_platform_driver(bcmgenet_driver)` and installs `bcmgenet_netdev_ops` and `bcmgenet_ethtool_ops`. Important netdev entry points are `bcmgenet_open`, `bcmgenet_close`, `bcmgenet_xmit`, `bcmgenet_timeout`, `bcmgenet_set_rx_mode`, `bcmgenet_set_mac_addr`, `bcmgenet_get_stats64`, and `bcmgenet_change_carrier`. Important ethtool paths cover link settings, pause, EEE, WOL, coalescing, driver stats, and RX NFC rule insertion/deletion.

Hardware abstraction is built around revision-selected `struct bcmgenet_hw_params` instances plus runtime register-offset tables `bcmgenet_dma_regs` and `genet_dma_ring_regs`. `bcmgenet_set_hw_params` chooses GENET v1-v5 register maps, validates the hardware revision from `SYS_REV_CTRL`, records integrated PHY revision hints, and selects descriptor word width. Descriptor helpers `dmadesc_set_addr`, `dmadesc_set_length_status`, and `dmadesc_set` hide 32-bit versus 40-bit DMA address programming.

Key control functions include `init_umac`, `reset_umac`, `bcmgenet_umac_reset`, `bcmgenet_init_dma`, `bcmgenet_init_tx_queues`, `bcmgenet_init_rx_queues`, `bcmgenet_dma_teardown`, `bcmgenet_fini_dma`, `bcmgenet_isr0`, `bcmgenet_isr1`, `bcmgenet_irq_task`, `bcmgenet_resume`, and `bcmgenet_suspend`.

## Control Flow

Probe allocates a multi-queue Ethernet device, maps registers, records IRQs, sets defaults for pause/checksum/scatter-gather features, requests an optional WOL IRQ, enables the main clock long enough to detect hardware parameters, sets the DMA mask, initializes MDIO support, configures queue counts and stats synchronizers, disables carrier, turns the clock back off, and registers the netdev.

Open enables the clock, powers internal PHYs when necessary, clears UniMAC reset, initializes UniMAC, reapplies features and the MAC address, clears/reinitializes the hardware filter block, initializes RX/TX DMA rings, requests the two main IRQs, attaches the PHY through `bcmgenet_mii_probe`, applies pause settings, starts NAPI/MAC/link interrupts/PHY, and starts TX queues. Close follows the reverse order: stop queues and RX, optionally stop/disconnect PHY, disable DMA and NAPI, mask interrupts, cancel deferred IRQ work, reclaim all TX descriptors, free RX/TX control blocks, free IRQs, power down the internal PHY, and disable the clock.

TX maps one SKB head plus frags into descriptors. `bcmgenet_xmit` reserves descriptor space under the per-ring spinlock, prepends a 64-byte transmit status block for checksum metadata, maps all fragments, writes descriptors with SOP/EOP/append-CRC/checksum flags, advances software producer/write pointers, and updates the hardware producer index unless batching through `netdev_xmit_more`. TX completion is NAPI-driven by `bcmgenet_tx_poll`, which calls `__bcmgenet_tx_reclaim` to compare hardware consumer index with software `c_index`, unmap DMA, complete SKBs, update per-ring u64 stats, and wake stopped queues.

RX uses preallocated 2 KB SKBs mapped into RDMA descriptors. `bcmgenet_desc_rx` reads the hardware producer index, tracks hardware discard counters, refills each descriptor before handing the old SKB upward, parses the 64-byte receive status block, validates length/SOP/EOP/error bits, applies checksum-complete metadata, strips status/alignment bytes and optional FCS, updates per-ring stats, and submits packets via `napi_gro_receive`. `bcmgenet_rx_poll` also feeds `net_dim` when adaptive RX coalescing is enabled.

IRQ instance 1 handles per-ring RX/TX events by masking the ring interrupt and scheduling the corresponding NAPI instance. IRQ instance 0 handles MDIO completion/error wakeups and defers PHY/link events to `bcmgenet_irq_task`.

## State and Persistence Behavior

Persistent runtime state lives in `struct bcmgenet_priv`: mapped base address, revision/flags, queue descriptors/control blocks, RX NFC rules/list, PHY/MDIO pointers, IRQ state, pause/WOL options, clocks, and MIB/software counters. Ring state is held in `struct bcmgenet_tx_ring` and `struct bcmgenet_rx_ring`, including producer/consumer/read/clean pointers, descriptor ownership, NAPI objects, and u64 stats. No disk persistence is involved; state is rebuilt at probe/open/resume and torn down at close/remove/suspend. Wake settings persist only in driver memory (`wolopts`, `sopass`) while the device object exists.

## Dependencies and Integration Points

The file depends on Linux netdev, NAPI, ethtool, phylib, platform device, PM, DMA mapping, clocks, and `unimac.h` register definitions. It calls MDIO/PHY helpers in `bcmmii.c` (`bcmgenet_mii_init`, `bcmgenet_mii_probe`, `bcmgenet_mii_config`, `bcmgenet_phy_pause_set`, `bcmgenet_phy_power_set`) and WOL helpers in `bcmgenet_wol.c`. Device matching is through `brcm,genet-v1` through `brcm,genet-v5`, BCM2711/BCM7712 compatibles, and ACPI ID `BCM6E4E`. It has a soft dependency on `mdio-bcm-unimac`.

## Risks and Edge Cases

The highest-risk areas are descriptor ring accounting, DMA mapping rollback, version-specific register offsets, and PM/WOL resume branches. TX mapping failure rewinds descriptors and unmaps already-mapped fragments; regressions here can leak DMA mappings or corrupt ring pointers. RX refilling occurs before packet validation, so allocation failure drops the packet but still advances consumer state. `bcmgenet_dma_regs` and `genet_dma_ring_regs` are file-scope globals selected at probe time; mixed GENET revisions in one loaded kernel would be risky if multiple devices with different versions coexist. Suspend/resume has two paths: a fast WOL path that preserves RX state and reinitializes TX only, and a full reset path that restores filters, features, DMA, and PHY configuration. RX NFC/HFB programming has version-specific filter enable and queue mapping layouts and only supports masks made from 0x00/0x0f/0xf0/0xff bytes.

## Test Signals

Useful validation signals include successful probe/open/close cycles across GENET revisions, TX/RX traffic with SG and checksum offload enabled, DMA mapping failure injection, TX timeout recovery, ethtool stats/coalescing/pause/EEE/RXNFC operations, multicast/promiscuous filter behavior, PHY link up/down interrupts, suspend/resume with and without WOL, magic-packet wake, wake-filter rules, and 32-bit versus 40-bit DMA mask coverage. Runtime logs to watch include GENET version mismatch warnings, DMA disable timeouts, RX oversize/fragment/error messages, TX DMA map failures, and PHY attach failures.
