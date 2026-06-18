## sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/bmac.c

Purpose: PowerMac `macio` network driver for Apple BMAC and BMAC+ Ethernet controllers behind DBDMA engines. It owns the Linux `net_device` lifecycle, maps the controller and TX/RX DMA channels, reads Open Firmware MAC properties and SROM station address data, and registers a normal Ethernet device.

Important APIs and types: `struct bmac_data` stores DMA MMIO pointers, ring command arrays, SKB rings, a software TX queue, multicast hash state, power-management flags, and a spinlock. The public integration surfaces are `bmac_netdev_ops`, `bmac_ethtool_ops`, the `macio_driver` `bmac_driver`, and module init/exit. Internal helpers include little-endian DBDMA accessors, `bmread()`/`bmwrite()`, MIF bit-banged PHY reads/writes, SROM bit clocking, ring constructors, interrupt handlers, and reset/start/timeout helpers.

Control flow: probe validates three resources and three interrupts, maps MMIO, disables the chip, prepares DBDMA command storage inside the private area, requests misc/TX/RX IRQs, powers the chip down until open, then registers the netdev. Open marks the device opened, resets/enables chip, initializes TX/RX rings, starts RX DMA, enables MACs/interrupts, and sends a dummy minimum frame because the hardware reportedly cannot receive until it transmits once. TX goes through a software `sk_buff_head`: `bmac_output()` enqueues, `bmac_start()` drains while DMA ring slots are available, and `bmac_txdma_intr()` completes SKBs and wakes the queue. RX DMA interrupt consumes completed descriptors, validates minimum length, strips FCS, passes packets through `eth_type_trans()`/`netif_rx()`, then rebuilds descriptors.

State and persistence: runtime state is entirely in `struct bmac_data`, hardware registers, DBDMA command rings, and SKBs. There is no disk persistence. Suspend/resume detach the device, stop timers/IRQs/DMA, free ring SKBs, power the chip off through `PMAC_FTR_BMAC_ENABLE`, then rebuild on resume if opened.

Dependencies and integration points: depends on PowerPC `macio`, Open Firmware properties, `pmac_call_feature`, DBDMA, Linux netdev/ethtool APIs, CRC helpers for multicast hashing, and Apple BMAC register constants from `bmac.h`.

Risks: old bus APIs (`virt_to_bus()`/`bus_to_virt()`) and raw DBDMA command manipulation are architecture-specific and fragile. RX fallback uses a global emergency buffer when allocation fails. Timeout recovery resets both DMA and MAC with in-flight state assumptions. SROM checksum verification currently returns success after reading, so station-address validation is minimal. Queueing plus DMA ring state requires lock correctness around interrupts, timeout, and close.

Test signals: build on PowerMac/mac-io configs, boot probe with BMAC and BMAC+ device-tree matches, `ip link set up/down`, sustained RX/TX, multicast/promiscuous mode changes, suspend/resume, IRQ error counters, and injected TX timeout or SKB allocation failure paths.
