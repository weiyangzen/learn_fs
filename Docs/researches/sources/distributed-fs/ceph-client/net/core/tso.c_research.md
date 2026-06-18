# sources/distributed-fs/ceph-client/net/core/tso.c

## Purpose
This file provides software helpers for TCP/UDP segmentation offload header construction, payload iteration, and DMA mapping of GSO payload regions. Drivers can use it to build per-segment headers and walk payload DMA chunks without duplicating skb fragment logic.

## APIs, Types, and Functions
TSO header/data APIs are `tso_start()`, `tso_build_hdr()`, and `tso_build_data()`, operating on `struct tso_t`. DMA APIs are `tso_dma_map_init()`, `tso_dma_map_cleanup()`, `tso_dma_map_count()`, and `tso_dma_map_next()`, operating on `struct tso_dma_map`. The internal `tso_dma_iova_try()` attempts contiguous DMA IOVA mapping before fallback per-region mapping.

## Control Flow, State, and Persistence
`tso_start()` initializes transport header length, IPv4 ID, TCP sequence, IPv6 flag, initial payload pointer, and first frag index. `tso_build_hdr()` copies the original headers, adjusts IPv4 total length/ID or IPv6 payload length, updates TCP sequence and clears PSH/FIN/RST for non-final TCP segments, or updates UDP length. `tso_build_data()` advances sequence, remaining size, data pointer, and transitions from linear data to fragments.

DMA initialization maps payload after `hdr_len`. It first attempts DMA IOVA allocation and links the linear payload and each skb frag into one contiguous mapping with one sync. If that fails, it resets map state and maps the linear region and each frag independently with `dma_map_phys()`. Cleanup destroys IOVA or unmaps each region. `tso_dma_map_count()` predicts descriptor count for the next payload range, and `tso_dma_map_next()` yields DMA address/chunk pairs while advancing iterator state.

Persistent state is confined to caller-owned `struct tso_t` and `struct tso_dma_map`; DMA mappings persist until explicit cleanup.

## Dependencies and Integration
Depends on skb GSO metadata, TCP/UDP/IP/IPv6 headers, VLAN protocol detection, skb fragment APIs, DMA mapping and DMA IOVA APIs, unaligned access helpers, and net driver conventions. Integration is primarily with NIC drivers that need software segmentation or descriptor preparation for GSO skbs.

## Risks and Test Signals
Risks include incorrect header length assumptions, IPv4 ID/sequence drift, mishandling UDP GSO versus TCP, off-by-one fragment iteration, DMA leak on partial map failure, incorrect descriptor counts at region boundaries, and using `virt_to_phys()` only for valid linear skb memory. Test signals include driver selftests with linear-only and fragmented GSO skbs, IPv4/IPv6 TCP and UDP GSO checksums/lengths, DMA API debug, IOVA fallback fault injection, KASAN on frag iteration, and packet captures comparing segmented output.
