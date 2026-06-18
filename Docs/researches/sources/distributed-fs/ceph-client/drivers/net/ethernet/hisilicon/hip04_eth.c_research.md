
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hip04_eth.c

## Purpose

This file implements the Hisilicon P04 Ethernet platform driver. It configures GMAC/PPE registers, manages fixed-size TX descriptors and RX buffers, supports PHY link adjustment for SGMII/MII, handles NAPI RX/TX cleanup, provides TX coalescing ethtool knobs, and registers a platform netdev for `hisilicon,hip04-mac`.

## Important APIs, Types, and Functions

- `struct hip04_priv` holds MMIO bases, PPE syscon regmap, PHY state, NAPI, TX/RX descriptor/buffer arrays, TX coalescing state, and timeout work.
- `hip04_mac_probe()` is the platform probe path.
- `hip04_mac_open()` and `hip04_mac_stop()` start/stop queues, PHY, NAPI, interrupts, and DMA mappings.
- `hip04_mac_start_xmit()` maps one SKB into a TX descriptor, starts hardware TX, updates BQL and stats, and schedules TX cleanup by NAPI or hrtimer.
- `hip04_rx_poll()` reclaims TX and consumes RX descriptors/buffers under NAPI.
- `hip04_config_fifo()`, `hip04_config_port()`, `hip04_mac_enable()`, and `hip04_mac_disable()` program PPE/GMAC hardware.
- `hip04_get_coalesce()` and `hip04_set_coalesce()` expose TX coalescing limits.

## Control Flow

Probe allocates a netdev, maps resources, parses `port-handle` to get port/channel/group, obtains a syscon regmap, reads PHY mode and optional PHY handle, requests the IRQ, initializes TX timeout work and NAPI, resets/configures PPE and GMAC, installs a random MAC address, allocates rings, and registers the netdev.

Open resets software indices and PPE, maps all RX buffers and pushes their DMA addresses to hardware, starts PHY, starts the queue, enables MAC/interrupts, and enables NAPI. TX maps the SKB, fills a hardware descriptor with big-endian fields, writes the descriptor address to PPE, updates BQL/stats, advances `tx_head`, and uses frame-count or timer thresholds to schedule NAPI cleanup. NAPI first reclaims TX descriptors, then consumes RX buffers until budget or hardware says no packet is ready, refilling each slot.

Stop disables NAPI/queue/MAC, forces TX reclaim, resets PPE, stops PHY, and unmaps RX buffers. TX timeout work restarts the interface by stop/open.

## State and Persistence

Runtime state includes descriptor rings, RX fragment pool, DMA mappings, TX head/tail, RX head, remaining RX count, BQL state, coalescing hrtimer settings, PHY link speed/duplex, PPE syscon state, and netdev stats. Hardware configuration persists until reset or driver removal.

## Dependencies and Integration Points

The driver depends on platform devices, OF properties, syscon/regmap, PHYLIB/OF PHY, NAPI, DMA API, hrtimer, netdev BQL, and optional `CONFIG_HI13X1_GMAC` register/layout variants. Kconfig selects `MFD_SYSCON`, `HNS_MDIO`, and `MARVELL_PHY`.

## Risks and Edge Cases

The driver uses many conditional register layouts for HI13X1. `hip04_alloc_ring()` can leak previously allocated RX frags if allocation fails before probe cleanup calls `hip04_free_ring()` with partially initialized data. `hip04_mac_stop()` has a duplicated `int i;` declaration in the source, which needs build validation. RX `build_skb()` consumes preallocated fragments and refill failures can stall RX. TX cleanup relies on hardware clearing descriptor `send_addr`. Timeout recovery runs stop/open from work context.

## Test Signals

Signals include OF probe with valid `port-handle`, syscon, PHY mode and PHY handle; open/close cycles; link changes for SGMII/MII; TX coalescing values accepted/rejected at limits; RX/TX traffic with BQL completions; interrupt error logging for RX/TX drops; TX timeout recovery; and HI13X1/non-HI13X1 build coverage.
