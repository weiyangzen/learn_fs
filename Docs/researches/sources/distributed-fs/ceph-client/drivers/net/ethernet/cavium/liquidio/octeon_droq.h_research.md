# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_droq.h

## Purpose
Declares the Descriptor Ring Output Queue data model and public receive-queue APIs. In LiquidIO terminology output is from the Octeon device, so these structures implement host ingress.

## Important APIs, Types, and Functions
Important structs include `octeon_droq_desc` for DMA buffer/info pointers, `octeon_droq_info` for packet length and receive header, `octeon_skb_page_info` for page DMA ownership, `octeon_recv_buffer`, `oct_droq_stats`, `octeon_recv_pkt`, `octeon_recv_info`, `octeon_droq_ops`, and `octeon_droq`. Inline helpers allocate and free `octeon_recv_info`. Public prototypes cover DROQ init/delete/create, packet processing in tasklet and poll mode, interrupt enable, refill retry, dispatch registration, and dispatch argument lookup.

## Control Flow
The header has no direct runtime flow, but its callback structure controls whether the C implementation sends normal packets to a queue-specific fast-path function or falls back to opcode dispatch. `poll_mode` and `drop_on_max` influence receive processing behavior under NAPI and budget pressure.

## State and Persistence Behavior
`octeon_droq` persists all ring and buffer state for a receive queue: descriptor ring, read/write/refill indices, packet counters, thresholds, receive buffer list, hardware credit/sent register mappings, dispatch list, stats, DMA address, app context, and NAPI metadata. `octeon_recv_pkt` and `octeon_recv_info` are transient dispatch containers.

## Dependencies and Integration Points
Depends on `union octeon_rh` from `liquidio_common.h`, Linux NAPI and page/DMA concepts, and `octeon_device` ownership. It is consumed by core device setup, VF/PF netdev receive setup, interrupt handlers, and representor receive dispatch.

## Risks
Struct layout and queue state fields are tightly coupled to DMA descriptor programming and packet processing. `MAX_RECV_BUFS` assumes a 64 KiB maximum packet and typical buffer sizing; changing buffer sizes or max packet sizes requires revisiting this bound. Callback ownership rules must be clear because buffers passed through `fptr` or dispatch functions are no longer refill-owned.

## Test Signals
Build coverage, descriptor size checks, receive queue init/delete, NAPI poll and tasklet processing, dispatch function registration, stats updates, jumbo receive buffer counts, low-credit refill, and callback buffer ownership tests validate this header's contract.
