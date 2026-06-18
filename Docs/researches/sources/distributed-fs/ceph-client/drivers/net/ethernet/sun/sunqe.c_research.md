# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunqe.c

## Purpose
`sunqe.c` implements the Sun QuadEthernet 10baseT SBUS driver. One QEC controller owns shared global registers and interrupt delivery for up to four QE/MACE channels; each channel is exposed as a Linux Ethernet netdev with PIO/register initialization, coherent descriptor and packet buffers, interrupt-driven RX, lazy TX reclaim, multicast filter programming, ethtool link reporting, and platform-driver lifecycle.

## Important APIs, Types, And Functions
- Module and driver entry: `qec_init()`, `qec_exit()`, `qec_sbus_driver`, OF match table for `"qe"`, and global `root_qec_dev`.
- QEC lifecycle: `qec_global_reset()`, `qec_init_once()`, `qec_get_burst()`, and `get_qec()` allocate/map the shared controller, validate MACE mode, reset QEC, configure local memory partitioning and burst mode, request the shared IRQ, and publish the parent in platform data.
- Channel lifecycle: `qe_stop()`, `qe_init_rings()`, `qe_init()`, `qe_open()`, `qe_close()`, `qec_ether_init()`, and `qec_sbus_remove()`.
- Data path: `qec_interrupt()`, `qe_rx()`, `qe_tx_reclaim()`, `qe_start_xmit()`, and `qe_tx_timeout()`.
- Error handling: `qe_is_bolixed()` decodes QEC/MACE status bits, updates netdev stats, and resets the channel for lockup-prone conditions.
- Multicast and ethtool: `qe_set_multicast()`, `qe_get_drvinfo()`, `qe_get_link()`, `qe_ethtool_ops`, and `qec_ops`.

## Control Flow
Each `"qe"` platform child probes through `qec_ether_init()`. It allocates an Ethernet netdev, gets the `channel#`, obtains or creates the parent QEC via `get_qec()`, maps per-channel QEC and MACE registers, allocates coherent descriptor and packet-buffer memory, stops the channel, installs netdev and ethtool ops, and registers the netdev. The first child for a QEC maps global registers, confirms MACE mode, resets the controller, computes burst capabilities from OF properties, partitions local memory into channel RX/TX FIFO areas, and requests the shared IRQ.

`ndo_open` sets the base MACE config and calls `qe_init()`, which resets MACE and QEC channel, writes descriptor ring addresses, masks/unmasks RX/TX/error interrupts, positions local-memory FIFO pointers by channel, programs MACE PHY/TX/RX/FIFO/address registers, clears multicast filter state, initializes rings, waits briefly for link, clears missed counters, and calls `qe_set_multicast()` to enable TX/RX. The shared IRQ reads QEC global status nibble by nibble, services each active child, processes errors first, drains RX descriptors, and only reclaims TX/wakes the queue when TX interrupts were enabled because the queue had filled.

TX copies SKB data into coherent per-channel TX buffers, writes one descriptor, wakes the channel, updates stats, and frees the SKB immediately. RX copies from coherent RX buffers into newly allocated SKBs, reposts descriptors at the delayed mirror position, and updates stats.

## State And Persistence
`struct sunqec` persists per physical QEC while loaded: global MMIO, four child pointers, burst capabilities, OF platform device, and root list linkage. `struct sunqe` persists per channel: register bases, coherent descriptor block, coherent packet buffers, ring cursors, lock, parent pointer, MACE config, channel number, platform device, and netdev. There is no disk state. MAC address comes from SPARC `idprom`, so channels initially share that base address unless platform firmware or external mechanisms adjust it.

## Dependencies And Integration Points
The driver depends on SPARC SBUS helpers, Open Firmware properties/resources, DMA coherent allocation, Linux netdev/ethtool/SKB APIs, CRC multicast hashing, and idprom. It consumes the register and state definitions in `sunqe.h`. It integrates with one shared QEC IRQ and with child `"qe"` OF nodes under a parent QEC resource.

## Risks And Edge Cases
- The shared interrupt assumes `qecp->qes[channel]` exists for any status nibble; partial probe or unexpected hardware status could expose null child pointers.
- The TX path copies into fixed `PKT_BUF_SZ` buffers and does not visibly guard against oversized SKBs beyond normal Ethernet MTU assumptions.
- RX and TX are interrupt-driven without NAPI; high packet rates can increase IRQ load.
- `qe_set_multicast()` stops and wakes the queue without taking `qep->lock`, relying on netdev serialization and hardware behavior.
- Error paths reset the channel from IRQ context for several MACE lockup conditions.
- Parent QEC lifetime is global and freed at module exit, while child remove frees channel resources; ordering must remain platform-driver controlled.

## Test Signals
Test with SPARC/SBUS builds, OF probe with four channels, shared IRQ dispatch, open/close, link-state reporting from `MREGS_PHYCONFIG`, TX queue full and wake behavior, TX timeout reset, RX under allocation failure, multicast/allmulti/promiscuous transitions, and module unload after multiple QEC instances.
