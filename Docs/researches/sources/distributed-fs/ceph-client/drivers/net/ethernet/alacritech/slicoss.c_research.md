# sources/distributed-fs/ceph-client/drivers/net/ethernet/alacritech/slicoss.c

## Purpose
`slicoss.c` is the non-accelerated Linux PCI netdev driver for Alacritech SLIC Mojave/Oasis Gigabit Ethernet adapters. It handles firmware loading, EEPROM MAC discovery, PCI probe/remove, netdev open/stop, TX/RX DMA queues, NAPI interrupt processing, link status UPRs, multicast filtering, and ethtool/netdev stats.

## Important APIs and functions
- PCI/netdev lifecycle: `slic_probe()`, `slic_remove()`, `slic_init()`, `slic_open()`, and `slic_close()`.
- Firmware paths: `slic_load_firmware()` downloads main card microcode sections and validates firmware structure; `slic_load_rcvseq_firmware()` downloads receive sequencer firmware.
- EEPROM path: `slic_read_eeprom()` uses a temporary shared-memory/UPR setup, validates magic/checksum via `slic_eeprom_valid()`, and sets the netdev MAC.
- DMA queue setup: `slic_init_rx_queue()`, `slic_init_tx_queue()`, `slic_init_stat_queue()` allocate RX buffers, TX descriptor pool entries, and status descriptor arrays; corresponding free functions undo mappings and buffers.
- Datapath: `slic_xmit()` maps an SKB head and posts a TX command buffer; `slic_xmit_complete()` consumes status completions; `slic_handle_receive()` validates RX descriptors, handles errors, and passes packets through GRO.
- Interrupt/NAPI: `slic_irq()` masks interrupts and schedules NAPI; `slic_poll()` dispatches shared-memory ISR bits and reenables interrupts; `slic_handle_irq()` fans out RX, TX, UPR, link, and error paths.
- Link and filtering: `slic_set_link_autoneg()`, `slic_handle_link_irq()`, `slic_configure_link*()`, `slic_set_rx_mode()`, and `slic_set_mac_address()`.

## Control flow
Probe enables PCI, configures DMA mask/regions, allocates a netdev, maps registers, initializes hardware enough to load firmware and read EEPROM, then registers the netdev. Opening resets/reloads firmware, initializes RX/TX/status/shared-memory state, enables NAPI, programs ISP/interrupt aggregation/MAC/filter/link autoneg, requests IRQ, enables interrupts, and queues an initial link-status UPR. Interrupts write-mask the card, inspect shared-memory ISR, and schedule NAPI. NAPI handles RX frames until budget, TX completions through status descriptors, link events through UPRs, and error counters, then reenables interrupts. Close stops queue/carrier, disables NAPI/interrupts, powers down PHY/MAC, clears UPRs, frees all DMA resources, and resets the card.

## State and persistence behavior
Runtime state includes TX/RX/status queues, coherent shared memory for ISR/link, firmware-loaded card microcode, UPR list state, stats, NAPI, link speed/duplex, and multicast/promiscuous settings. EEPROM stores persistent MAC/FRU/card configuration but is read only. Firmware must be available at each initialization path because open reloads the card.

## Dependencies and integration points
The driver depends on PCI, firmware loader, DMA API, NAPI/netdev, ethtool, MII definitions, CRC32 multicast hashing, and SLIC hardware register/descriptor definitions from `slic.h`. It exposes standard netdev ops and ethtool stats.

## Risks and edge cases
The driver maps only `skb_headlen()` for TX, so fragmented SKBs rely on upper layers/features not advertising scatter-gather. Firmware parsing has multiple sanity checks but malformed firmware can still exercise complex section loops. RX buffers combine a hardware descriptor immediately before packet data and require 256-byte DMA alignment. UPR retries on errors can reorder expectations if link/config requests stack up. Interrupt handling relies on shared-memory ISR visibility and memory barriers. Open/close reload and free all volatile resources, so error unwinds must stay exact.

## Test signals
Test PCI probe/remove for Mojave and Oasis IDs, firmware missing/invalid paths, EEPROM checksum failure and MAC selection, open/close cycles, link up/down/autoneg for copper/fiber, multicast/promiscuous filter programming, RX error counters, TX completion wakeups, NAPI budget handling, IRQ sharing/spurious IRQ, ethtool stats, and DMA API debug on allocation/unmap paths.
