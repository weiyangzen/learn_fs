# sources/distributed-fs/ceph-client/drivers/net/ethernet/moxa/moxart_ether.c

## Purpose
`moxart_ether.c` is a platform Ethernet driver for the MOXA ART internal MAC, documented as RTL8201CP based hardware. It provides netdev open/stop/transmit/multicast/MAC-address operations, fixed RX/TX descriptor rings, interrupt handling, and Device Tree probing.

## Important APIs, Types, And Functions
The driver uses `struct moxart_mac_priv_t` from `moxart_ether.h` for private state. Key functions are `moxart_mac_probe`, `moxart_remove`, `moxart_mac_open`, `moxart_mac_stop`, `moxart_rx_poll`, `moxart_mac_start_xmit`, `moxart_tx_finished`, `moxart_mac_interrupt`, `moxart_mac_set_rx_mode`, and `moxart_set_mac_address`. The netdev ops are collected in `moxart_netdev_ops`, and the platform driver matches `moxa,moxart-mac`.

## Control Flow
Probe allocates an Ethernet device, maps the first MMIO resource, parses IRQ 0, obtains or randomizes the MAC address, allocates coherent descriptor rings and separate RX/TX buffer areas, requests the interrupt, adds NAPI, and registers the netdev. Open enables NAPI, resets the MAC, writes the MAC address, initializes TX and RX descriptor rings, enables interrupts/DMA/MAC units, and starts the TX queue. RX interrupt masks RX completion and schedules NAPI. `moxart_rx_poll` walks RX descriptors until the budget or DMA-owned descriptor, validates error bits, syncs the DMA buffer for CPU, copies the packet into a newly allocated SKB, sends it to GRO, updates stats, then returns descriptor ownership to DMA. TX maps the outgoing SKB data, fills the current descriptor, pads short frames, syncs for device, sets first/last/end bits, gives ownership to DMA, kicks poll demand, advances the ring head, and updates the watchdog timestamp. TX completion unmaps all descriptors from tail to head, updates stats, consumes SKBs, and wakes the queue if enough space returns.

## State And Persistence
State is held in descriptor memory, DMA mappings, per-ring indices, SKB pointers, software copies of register values, NAPI state, and netdev stats. Nothing persists across unload except platform firmware configuration. RX buffers are permanently allocated for the device lifetime and remapped on open, while TX maps each SKB on demand and unmaps on completion.

## Dependencies And Integration Points
The driver integrates with platform devices, Device Tree address and IRQ parsing, DMA mapping, NAPI/GRO, Kbuild module registration, and the generic Ethernet netdev stack. Register definitions, descriptor bit fields, ring sizes, and private state come from `moxart_ether.h`.

## Risks
The TX ring cleanup drains all descriptors from tail to head on any TX completion interrupt without checking per-descriptor DMA ownership, which assumes interrupts only arrive after all queued descriptors have completed. RX copies packets rather than building SKBs around DMA buffers, which is simple but costs memory bandwidth. Multicast hash registers are only ORed when addresses are added and are not cleared before recomputing a new list, so stale multicast bits can remain. TX padding writes beyond `skb->len` without explicitly expanding tailroom, relying on the original SKB headroom/tailroom. Error paths after partial RX DMA mapping in ring setup log mapping failures but continue. Probe uses `irq_of_parse_and_map` and later `devm_request_irq`, with manual `devm_free_irq` in remove.

## Test Signals
Test probe/remove, random and firmware MAC address paths, open/stop cycles, ping and bulk TX/RX traffic, NAPI budget behavior, multicast filter changes, queue stop/wake under TX pressure, RX error descriptors, DMA mapping failure injection, and module unload. Hardware tests should inspect interrupt mask/status and descriptor ownership transitions under load.
