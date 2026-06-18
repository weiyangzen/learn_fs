## sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/ftgmac100.c

## Purpose
Implements the Faraday FTGMAC100 gigabit Ethernet platform driver, including Aspeed AST2400/AST2500/AST2600 variants. It manages DMA descriptor rings, RX/TX packet processing, PHY or NCSI link management, reset/recovery, checksum/VLAN offloads, multicast filtering, pause control, ring sizing, clocks/resets, and OF probing.

## Important APIs, Types, and Functions
The main private type is `struct ftgmac100`. Key functions include `ftgmac100_probe`, `ftgmac100_remove`, `ftgmac100_open`, `ftgmac100_stop`, `ftgmac100_hard_start_xmit`, `ftgmac100_interrupt`, `ftgmac100_poll`, `ftgmac100_rx_packet`, `ftgmac100_tx_complete`, `ftgmac100_reset`, `ftgmac100_reset_task`, `ftgmac100_adjust_link`, `ftgmac100_setup_mdio`, `ftgmac100_probe_dt`, `ftgmac100_probe_ncsi`, `ftgmac100_init_all`, `ftgmac100_alloc_rings`, `ftgmac100_alloc_rx_buffers`, `ftgmac100_set_ringparam`, and pause/multicast/MAC address helpers.

## Control Flow and State
Probe identifies the MAC variant, maps registers, initializes pause defaults, obtains MAC address, selects descriptor end-of-ring bit layout, sets up embedded MDIO where applicable, connects PHY/fixed PHY/NCSI, obtains resets/clocks for Aspeed, applies AST2600 test-mode workaround, initializes default ring sizes and feature flags, and registers the netdev. Open allocates descriptor rings and scratch RX buffer, sets initial link speed for NCSI or no-link for PHY, resets hardware, adds NAPI, requests IRQ, initializes rings/RX buffers/MAC registers, enables interrupts, and starts PHY or NCSI. TX maps the SKB head and frags to descriptors, sets checksum/VLAN control bits, publishes OWN on the first descriptor last, advances the ring pointer, stops the queue below threshold, and pokes TX polling. NAPI reclaims TX descriptors, receives RX descriptors, restarts MAC after overflow-class errors, and carefully clears/rechecks latched interrupts before completing.

Persistent state includes descriptor memory and SKB arrays, ring pointers, requested new ring sizes, scratch RX DMA buffer for allocation failures, multicast hash caches, pause settings, current speed/duplex, NCSI device pointer, reset work, clocks/resets, and variant flags.

## Dependencies and Integration Points
Depends on platform/OF APIs, DMA coherent and streaming mapping, PHYLIB, fixed PHY, optional NCSI, Aspeed clocks/reset/MDIO, NAPI, ethtool, VLAN helpers, checksum helpers, CRC32 multicast hashing, and register/descriptor definitions from `ftgmac100.h`.

## Risks and Test Signals
Risks include descriptor ownership/barrier mistakes, freeing the same SKB across multi-fragment TX descriptors, RX scratch-buffer behavior under allocation pressure, ring resize reset races, lock ordering among RTNL/PHY/MDIO during reset, NCSI fixed-PHY lifecycle, variant-specific end-of-ring bit differences, AST2400/AST2600 checksum errata, and restart behavior after RX overflow/AHB errors. Test with RGMII PHY and NCSI modes, AST2400/2500/2600 compatibles, up/down and remove during reset work, iperf with SG/checksum/VLAN on/off, multicast/promisc/allmulti, RX allocation failure, `ethtool -G/-a/-A`, link speed/duplex changes, TX timeout, AHB/error interrupt injection, and NCSI VLAN filtering.
