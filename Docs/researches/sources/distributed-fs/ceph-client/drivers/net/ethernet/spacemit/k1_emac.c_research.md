# sources/distributed-fs/ceph-client/drivers/net/ethernet/spacemit/k1_emac.c

## Purpose
`k1_emac.c` is a standalone SpacemiT K1 Ethernet MAC driver. It implements a platform `net_device` driver with coherent DMA descriptor rings, MDIO bus registration, PHY connection, NAPI RX/TX cleanup, multicast filtering, runtime PM aware open/stop, hardware statistics extension, ethtool reporting, and system sleep callbacks.

## Important APIs, Types, And Functions
- `struct emac_priv` is the central private state: MMIO base, buffer size, TX/RX rings, netdev/platform device, NAPI, clocks, APMU syscon regmap and offset, IRQ, PHY interface, hardware stats and offsets, TX coalescing state, timers, delay-line settings, and `stats_lock`.
- `struct emac_desc_ring` describes a coherent descriptor ring, DMA address, descriptor count, head/tail indices, and RX/TX buffer sidecar arrays.
- `struct emac_tx_desc_buffer` and `struct emac_rx_desc_buffer` track skb ownership and DMA mappings.
- `emac_init_hw()` programs MAC filtering, thresholds, frame sizes, RX IRQ mitigation, DMA reset, 64-bit DMA mode, strict bursts, and burst length.
- `emac_alloc_*_resources()` and `emac_free_*_resources()` allocate/free coherent descriptor rings and sidecar arrays.
- `emac_tx_mem_map()` maps the skb head plus fragments into descriptors, using two buffers per descriptor and deferring ownership of the first descriptor until all descriptors are initialized.
- `emac_rx_clean_desc()` receives completed descriptors, validates frame status, strips FCS, feeds `napi_gro_receive()`, and refills RX buffers.
- `emac_interrupt_handler()` acknowledges DMA interrupts, disables RX/TX transfer-done interrupts, and schedules NAPI.
- `emac_mii_read()` and `emac_mii_write()` implement MDIO via MAC MDIO registers with poll timeouts.
- `emac_stats_update()` periodically reads 32-bit hardware statistic counters, detects wraparound, and adds saved offsets from previous down/up cycles.
- `emac_open()`/`emac_stop()` allocate/free resources and call `emac_up()`/`emac_down()`.
- `emac_probe()` configures OF resources, clocks, reset, fixed-link registration, MDIO bus, netdev ops, ethtool ops, and NAPI.

## Control Flow
Probe allocates an Ethernet netdev, enables scatter-gather features, parses MMIO, syscon, IRQ, MAC address, internal delay properties, clocks and reset, registers any fixed-link, initializes software defaults and timers, registers the MDIO bus, registers the netdev, and adds NAPI. `emac_config_dt()` converts `tx-internal-delay-ps` and `rx-internal-delay-ps` into delay-line units and validates them against the 8-bit delay code range.

Open allocates TX and RX coherent rings, then `emac_up()` runtime-resumes the device, parses/connects the PHY, programs APMU interface mode and delay line, initializes MAC/DMA hardware, writes the MAC address, configures TX/RX DMA base addresses, preallocates RX skb buffers, starts the PHY, requests the shared IRQ, enables DMA interrupts, enables NAPI, starts the queue, and schedules the stats timer.

TX checks available descriptors against the skb fragment count, stops the queue if space is low, maps the skb into descriptors, sets first/last/interruption flags, writes all descriptors before setting ownership on the first, kicks `DMA_TRANSMIT_POLL_DEMAND`, and stops the queue proactively when the remaining ring space approaches `MAX_SKB_FRAGS + 2`. TX cleanup runs inside the shared NAPI poll and unmaps both descriptor buffers before freeing the skb.

RX uses `emac_alloc_rx_desc_buffers()` to keep descriptors populated with DMA-mapped skbs. `emac_rx_clean_desc()` walks from the RX tail until it hits a DMA-owned descriptor or budget is exhausted, validates descriptor status bits, subtracts FCS, submits frames to GRO, clears sidecar ownership, advances tail, and refills empty descriptors.

Hardware statistics are read on demand through netdev/ethtool getters and periodically by `stats_timer`. `emac_down()` updates counters before reset and copies current totals into offset unions so later hardware counter resets do not make stats jump backwards.

## State And Persistence
Runtime state lives in `emac_priv`, coherent descriptor rings, skb sidecar arrays, timers, work item, and hardware registers. Hardware stats are accumulated in 64-bit software unions with offset copies to survive interface down/up resets. TX drops use per-CPU netdev dstats. Delay-line and interface-mode state is loaded from DT and programmed into the APMU syscon. No disk state is persisted.

## Dependencies And Integration Points
The driver integrates with OF (`spacemit,k1-emac`, `phy-handle`, fixed-link, `spacemit,apmu`, delay properties), syscon/regmap, phylib/of_mdio, runtime PM, clock/reset frameworks, DMA mapping, NAPI, ethtool netlink stats families, and netdev core. It uses definitions from `k1_emac.h` for register and descriptor layout.

## Risks
- TX mapping failure in `emac_tx_mem_map()` frees descriptors only from `old_head` to current `head`; failures while filling buffer 2 of a descriptor need careful leak testing.
- Hardware descriptor base registers are written as 32-bit values while DMA mode is set to 64-bit; this assumes reachable low address allocation or hardware-specific interpretation.
- Stats reads can time out if a PHY stops the reference clock; the driver returns without rescheduling in some cases, so link-down/up transitions are important.
- `emac_down()` disconnects PHY before disabling IRQ/NAPI; ordering should be validated under concurrent interrupts.
- MTU changes are refused while running, so userspace must down the interface before changing frame size.
- Internal delay conversion is rounded; marginal board timing depends on DT values and the fixed 15.6 ps step assumption.

## Test Signals
Exercise probe with valid/random MAC, fixed-link and external PHY, RMII/RGMII modes, delay property bounds, open/stop cycles, SG TX with many fragments, ring-full queue stop/wake, RX error descriptors, multicast/allmulti/promisc hashing, `ethtool -S`, RMON/MAC/pause stats, register dumps, TX timeout recovery, suspend/resume, runtime PM, and link speed changes. Watch for DMA mapping errors, MDIO poll timeouts, stats timeout messages, IRQ storms, and queue stalls.
