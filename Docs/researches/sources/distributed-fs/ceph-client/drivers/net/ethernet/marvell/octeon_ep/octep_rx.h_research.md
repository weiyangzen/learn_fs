# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_rx.h

## Purpose
This header defines PF receive-side hardware descriptor formats, response headers, offload flags, receive buffer bookkeeping, per-queue/interface statistics, and `struct octep_oq`, the software state for an OCTEON Output Queue.

## Important APIs, Types, And Functions
- Hardware descriptor: `struct octep_oq_desc_hw` contains a DMA buffer pointer and an optional host info pointer; static assert enforces 16 bytes.
- Response headers: `struct octep_oq_resp_hw` stores big-endian packet length; `struct octep_oq_resp_hw_ext` stores Rx offload verification flags.
- Offload helpers: `OCTEP_RX_OFFLOAD_*`, `OCTEP_RX_IP_CSUM()`, `OCTEP_RX_CSUM_IP_VERIFIED`, `OCTEP_RX_CSUM_L4_VERIFIED`, and `OCTEP_RX_CSUM_VERIFIED()`.
- Stats: `struct octep_oq_stats` tracks per-queue packets, bytes, and allocation failures; `struct octep_iface_rx_stats` mirrors hardware interface counters.
- Queue state: `struct octep_oq` stores queue identity, device/netdev pointers, NAPI pointer, buffers, MMIO registers, counters, indices, descriptor memory, and DMA address.

## Control Flow
`octep_rx.c` allocates and fills `octep_oq` instances. Hardware DMA writes packets into pages referenced by `octep_oq_desc_hw`; the driver interprets response headers at the beginning of those pages, updates `octep_oq` indices and counters, and recycles descriptors by writing credits to `pkts_credit_reg`.

## State And Persistence
The header defines runtime-only state structures. `host_read_idx`, `host_refill_idx`, `refill_count`, `pkts_pending`, and `last_pkt_count` are the core receive cursor fields. `iface_rx_stats` fields are snapshots of hardware counters copied elsewhere. No file or firmware-persistent state is defined.

## Dependencies And Integration Points
The types are consumed by PF queue code, PF main NAPI code, ethtool stats, and firmware stats structures. The queue struct embeds Linux `napi_struct` pointers indirectly and depends on DMA address, device, netdev, page, and MMIO pointer types from kernel headers.

## Risks And Edge Cases
- Hardware descriptor and response header sizes are ABI-sensitive; static asserts help catch accidental layout changes.
- Offload verification macros treat either IP or L4 verified flags as enough for `CHECKSUM_UNNECESSARY`; protocol expectations should match firmware semantics.
- `buffer_size` and `max_single_buffer_size` must account for response header sizes exactly to avoid skb length/alignment bugs.
- Queue count and descriptor count assumptions rely on power-of-two ring masks in the main/queue code.

## Test Signals
Build-time static asserts, DMA descriptor programming, checksum-offload receive tests, jumbo receive tests, ethtool/stat consistency, NAPI processing under traffic, and memory-leak checks on open/stop exercise this header's contracts.
