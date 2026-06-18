# sources/distributed-fs/ceph-client/include/net/tso.h

## Purpose

`tso.h` provides helper state and APIs for software-assisted TCP segmentation offload in drivers, including header/data construction and DMA mapping of GSO payload regions.

## Important APIs, types, and functions

`struct tso_t` tracks the current frag index, segment size, data pointer, IPv4 ID, transport header length, IPv6 flag, and TCP sequence. Header/data helpers are `tso_count_descs()`, `tso_start()`, `tso_build_hdr()`, and `tso_build_data()`. `struct tso_dma_map` describes xmit-time DMA mapping state for linear and fragmented payloads, with IOVA and fallback per-region fields. `struct tso_dma_map_completion_state`, `tso_dma_map_init()`, `tso_dma_map_next()`, `tso_dma_map_count()`, `tso_dma_map_cleanup()`, `tso_dma_map_completion_save()`, and `tso_dma_map_complete()` support deferred unmap at completion.

## Control flow

Drivers call `tso_start()` for a GSO skb, loop over segments building headers and data chunks, and size TX descriptors with `tso_count_descs()`. For DMA, drivers initialize a map, request DMA chunks for each segment, save IOVA completion state in the TX ring, and later call `tso_dma_map_complete()` at completion. If the IOVA path was not used, the helper returns false and the driver must use its normal per-region unmap path.

## State and persistence behavior

`struct tso_t` is transient per xmit. `struct tso_dma_map` is xmit-time state, while `tso_dma_map_completion_state` persists in the driver ring until TX completion. DMA mappings persist until `tso_dma_map_cleanup()` or completion teardown.

## Dependencies and integration points

It depends on SKB/GSO, DMA mapping, IP headers, IOVA DMA helpers, and driver TX rings. It integrates with NIC drivers that do TSO in software or need generic GSO DMA mapping.

## Risks and test signals

Risks include undercounting descriptors, header buffer overflow beyond `TSO_HEADER_SIZE`, sequence/IP ID errors across segments, DMA mapping leaks on partial failure, and mixing IOVA and fallback cleanup paths. Tests should cover IPv4/IPv6 TSO, fragmented and linear skbs, last-segment handling, DMA map failure unwind, IOVA completion, and per-region fallback unmapping.
