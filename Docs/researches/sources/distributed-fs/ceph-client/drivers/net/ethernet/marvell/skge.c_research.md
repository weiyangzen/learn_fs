# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/skge.c

## Purpose
This file is the PCI driver for SysKonnect/Marvell Yukon and Genesis Gigabit Ethernet adapters. It provides PCI probe/remove, board reset, one or two netdev ports per adapter, DMA descriptor rings, NAPI RX/TX completion, PHY/MAC initialization for Genesis and Yukon families, ethtool operations, Wake-on-LAN, multicast filtering, interrupt handling, suspend/resume, shutdown, and optional debugfs diagnostics.

## Important APIs, types, and functions
The file relies on hardware types from `skge.h`, especially `struct skge_hw`, `struct skge_port`, `struct skge_ring`, descriptor structs, and register macros. Netdev operations are `skge_up()`, `skge_down()`, `skge_xmit_frame()`, `skge_ioctl()`, `skge_get_stats()`, `skge_tx_timeout()`, `skge_change_mtu()`, `skge_set_multicast()`, and `skge_set_mac_address()`.

Major helper groups are ethtool/WOL/VPD access, ring allocation and RX buffer setup, Genesis XMAC/Broadcom PHY initialization and link handling, Yukon GMAC/Marvell PHY initialization and link handling, queue/RAM buffer setup, TX/RX data paths, interrupt and error handling, PCI reset/probe/remove, PM, and debugfs.

## Control flow
Module init optionally forces 32-bit DMA for DMI-listed boards, initializes debugfs, and registers the PCI driver. Probe enables the PCI device, requests BARs, sets bus mastering and DMA masks, allocates `skge_hw`, maps registers, resets and identifies the board, initializes one or two netdevs, registers them, and for dual-port boards requests the shared IRQ at probe time.

Opening a port validates its MAC, allocates a coherent descriptor block for RX and TX rings, allocates ring element arrays, fills RX buffers, requests IRQ for single-port boards, initializes the MAC/PHY family under `phy_lock`, configures RAM buffer partitions and BMU queues, starts RX, enables LEDs and port interrupts, enables NAPI, and programs multicast filters. Closing disables TX, stops timers/NAPI/interrupts, frees IRQ for single-port boards, stops family-specific MAC/PHY, resets TX/RX queues and FIFOs, cleans TX/RX buffers, frees rings and coherent memory, and clears `skge->mem`.

Transmit pads short skbs, verifies descriptor availability, maps the linear head and fragments, programs checksum offload fields, marks descriptors owned by hardware with memory barriers, starts the TX queue, updates BQL, and stops the netdev queue when low on descriptors. TX completion in NAPI unmaps descriptors no longer owned by hardware, frees the skb on EOF, completes BQL, and wakes the queue when enough descriptors are available.

RX NAPI first handles TX completion, then walks RX descriptors until budget or hardware ownership, validates frame status and hardware length, copies small frames or swaps in a new skb for larger frames, applies RX checksum metadata, passes packets through GRO, reuses descriptors on error or allocation failure, restarts the receiver, and reenables interrupts after NAPI completion.

The top-level ISR masks by `hw->intr_mask`, schedules PHY tasklet work for external PHY interrupts, schedules per-port NAPI for RX/TX queue interrupts, clears packet arbiter timeouts, dispatches MAC interrupts, and handles hardware error interrupts. The PHY tasklet reads slow PHY registers under `phy_lock`, updates link state, then unmasks external interrupts.

## State and persistence behavior
Runtime board state lives in `struct skge_hw`; per-port state lives in `struct skge_port`. Descriptor memory is coherent DMA allocated on port open and freed on close. Hardware register state persists while the PCI device is powered and is rebuilt by `skge_reset()` and `skge_up()`. WOL settings are stored in `skge->wol` and programmed during suspend/shutdown; they are not persisted to disk. Optional debugfs entries exist only while enabled and devices are up.

## Dependencies and integration points
The driver integrates with PCI, DMA mapping, netdev, NAPI/GRO, ethtool, MII ioctls, DMI quirks, debugfs, tasklets, PM, and architecture IRQ headers. It depends heavily on register and descriptor definitions in `skge.h`. It supports multiple vendors through the PCI ID table and separates Genesis and Yukon behavior through `is_genesis()` and hardware ID checks.

## Risks and edge cases
The driver contains many hardware errata workarounds and chip-specific branches; regressions can be family-specific. RX/TX ring manipulation depends on memory barriers and ownership bits. `skge_set_coalesce()` uses `min(delay, ecmd->rx_coalesce_usecs)` in the TX branch, which looks suspicious when only TX coalescing is configured. Debugfs notifier behavior depends on netdev ops pointer matching. PCI error handling may mask hardware error interrupts if bits cannot be cleared. Probe has distinct IRQ ownership rules for single-port and dual-port boards. WOL programming changes PHY power behavior during suspend/shutdown. Several paths use `BUG_ON()` for DMA alignment/boundary assumptions.

## Test signals
Test with supported PCI IDs for one-port and two-port cards, 32-bit and 64-bit DMA mask paths, Genesis and Yukon resets, copper and fiber PHYs, forced/autoneg link settings, pause negotiation, WOL magic/link wake, VPD read/write, ring resize while running, MTU changes with jumbo frames, checksum offload TX/RX, fragmented skb transmit unwind, RX allocation failure and small-packet copy path, interrupt masking/NAPI reenabling, PHY tasklet link changes, suspend/resume with running ports, shutdown WOL, and debugfs creation/removal when configured.
