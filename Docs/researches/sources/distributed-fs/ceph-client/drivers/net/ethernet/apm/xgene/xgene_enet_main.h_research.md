## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_main.h

Purpose: shared header for the original X-Gene Ethernet driver, defining queue limits, ring state, operation tables, private driver state, and common helper prototypes.

Important APIs, types, and functions: constants cover MTU, buffer sizes, queue/ring counts, starting buffer/ring numbers for ports/hardware generations, IRQ name size, and PHY polling intervals. `struct xgene_enet_desc_ring` stores ring identity, head/tail indexes, IRQ/NAPI, coherent descriptors, command addresses, completion SKB arrays, RX SKB/page pools, expanded buffers, and per-ring stats. `struct xgene_mac_ops`, `xgene_port_ops`, `xgene_ring_ops`, and `xgene_cle_ops` abstract MAC variants, port reset/clear/bypass/shutdown, ring setup/clear/commands/length/coalescing, and classifier init. `struct xgene_enet_pdata` is the main persistent context for netdev, resources, rings, queue counts, MMIO bases, ops, link work, MSS slots, delays, MDIO/GPIO state, and pause state.

Control flow, state, and dependencies: included by all original X-Gene implementation files. Runtime behavior is largely selected by assigning operation-table pointers in `xgene_enet_setup_ops`; the rest of the driver calls through those pointers.

Integration points: connects hardware headers, CLE, ring2 definitions, ethtool setup, and extended stats init. Helper `xgene_enet_dst_ring_num` combines resource manager and ring number for hardware queue routing.

Risks: this header defines cross-file ABI. Changing ring/private data layout affects every implementation file. Queue constants and starting ring numbers are hardware contracts. Optional fields such as `page_pool`, `cle_ops`, and `mdio_driver` must be checked by mode-specific code.

Test signals: compile all objects; runtime tests should verify correct operation-table selection, queue counts, ring ID derivation, stats, link polling, and MDIO/GPIO-dependent paths.
