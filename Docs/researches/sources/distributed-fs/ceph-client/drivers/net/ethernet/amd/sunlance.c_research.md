# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/sunlance.c

## Purpose
`sunlance.c` is the Linux SPARC/SBus LANCE Ethernet driver. It supports LANCE devices behind plain SBus, `ledma`, or `lebuffer`, with either coherent DVMA memory or PIO buffer access. It registers as a platform driver for Open Firmware nodes named `le` and provides netdev and basic ethtool integration for classic Sun systems.

## Important APIs, Types, And Functions
Hardware formats are `struct lance_rx_desc`, `struct lance_tx_desc`, and `struct lance_init_block`. `struct lance_private` stores LANCE registers, DMA registers, coherent or PIO init-block storage, ring cursors, platform-device links, cable-selection state, burst-size settings, busmaster CSR value, function pointers for DVMA/PIO ring/RX/TX implementations, multicast timer, and DMA address. Major functions include `load_csrs`, `lance_init_ring_dvma`, `lance_init_ring_pio`, `init_restart_ledma`, `init_restart_lance`, `lance_rx_dvma`, `lance_tx_dvma`, `lance_rx_pio`, `lance_tx_pio`, `lance_open`, `lance_close`, `lance_reset`, `lance_start_xmit`, `lance_set_multicast`, `sparc_lance_probe_one`, `sunlance_sbus_probe`, and `sunlance_sbus_remove`.

## Control Flow
The platform probe determines whether the parent is `ledma`, `lebuffer`, or neither, then calls `sparc_lance_probe_one`. Probe allocates a netdev, maps LANCE registers, optionally maps LEDMA registers, either maps PIO `lebuffer` memory or allocates coherent init-block memory, selects the DVMA or PIO function set, derives busmaster and burst settings from device tree properties, resolves cable selection/auto-carrier detection, resets LEDMA, sets netdev ops/ethtool ops/IRQ, initializes a multicast retry timer, registers the netdev, and stores driver data.

Open stops LANCE, requests IRQ, programs LEDMA high address bits for DVMA, clears mode and multicast filters, initializes rings, loads CSR1/2/3, starts the netdev queue, initializes/restarts the chip, and optionally sends a fake packet to detect carrier loss during auto-select. Interrupts ack CSR0 sources, clear errors, call selected RX/TX handlers, count babble/miss errors, and on memory error stop, reset DMA FIFO, reinitialize rings, reload CSRs, restart, and wake the queue.

TX copies packet data into the selected TX buffer path, pads to `ETH_ZLEN`, sets ownership, advances the ring, stops the queue when full, kicks transmit demand, and frees the SKB. TX completion handlers update collision/error stats, toggle TPE/AUI on carrier loss when auto-select is enabled, restart on buffer/underflow errors, and wake the queue. RX handlers copy completed packets into SKBs and return descriptors to chip ownership. Multicast updates stop and restart the chip; if TX is active they defer through a timer.

## State And Persistence
Runtime state includes coherent/Pio init block, descriptor rings and packet buffers, ring indices, cable selection (`tpe`, `auto_select`), LEDMA burst settings, multicast timer, mapped resources, and netdev stats. There is no disk persistence. Device-tree properties and IDPROM MAC address seed initial runtime state.

## Dependencies And Integration Points
The file depends on SPARC/SBus platform devices, Open Firmware properties, SBUS read/write helpers, LEDMA register definitions, auxio link-test control, IDPROM, DMA coherent allocation, netdev/SKB APIs, ethtool driver info, timers, IRQs, and platform-driver registration.

## Risks
Two access paths, DVMA and PIO, must remain behaviorally equivalent. Hardware cache/DMA quirks are handled with register readbacks, FIFO invalidation, and LEDMA burst configuration; regressions are hard to detect without old hardware. Multicast changes defer when TX is busy because callbacks can come from interrupt context. Auto carrier selection intentionally toggles media on carrier loss and can be disruptive if the platform properties are wrong. Resource cleanup must match whether registers, LEDMA, PIO buffer, or coherent memory were allocated.

## Test Signals
Validation requires SPARC/SBus hardware or suitable emulation. Test probe on plain, LEDMA, and lebuffer configurations; RX/TX traffic; queue full/wake; carrier-loss auto-selection; multicast/promiscuous changes during active TX; TX underflow restart; memory-error restart; platform remove cleanup; and `ethtool -i`/link reporting.
