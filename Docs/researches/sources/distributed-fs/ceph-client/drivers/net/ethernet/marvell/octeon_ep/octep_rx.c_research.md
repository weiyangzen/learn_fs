# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_rx.c

## Purpose
This file implements PF receive queue allocation, hardware descriptor provisioning, page-buffer refill, packet completion processing, skb construction, checksum status propagation, and receive queue cleanup for OCTEON Output Queues.

## Important APIs, Types, And Functions
- Setup/cleanup: `octep_setup_oqs()`, `octep_setup_oq()`, `octep_free_oqs()`, `octep_free_oq()`, and `octep_oq_free_ring_buffers()`.
- Buffer management: `octep_oq_fill_ring_buffers()` allocates and DMA maps one page per descriptor; `octep_oq_refill()` replenishes consumed descriptors once `refill_threshold` is reached.
- Hardware accounting: `octep_oq_dbell_init()` credits all descriptors; `octep_oq_check_hw_for_pkts()` reads packet counters and updates pending packets.
- Packet processing: `__octep_oq_process_rx()` parses response headers, builds skbs from pages, handles multi-descriptor packets as skb frags, sets checksum state, and submits to GRO; `octep_oq_process_rx()` loops to a NAPI budget and refills descriptors.

## Control Flow
Queue setup allocates `struct octep_oq`, coherent hardware descriptor memory, a software `octep_rx_buffer` array, page buffers for every descriptor, initializes indices, and asks chip-specific `setup_oq_regs()` to write queue registers. During NAPI, `octep_oq_process_rx()` checks whether pending packets are known; if not, it reads hardware counters. It processes up to budget packets, decrementing pending count, and when enough descriptors have been consumed, refills with new pages and writes descriptor credits to hardware.

For each packet, the first page contains an 8-byte hardware response length header and optionally an 8-byte extended offload header. The driver unmaps the page, builds an skb around it, reserves the response header(s), appends either a single buffer or additional page fragments for large packets, sets protocol and checksum status, and calls `napi_gro_receive()`.

## State And Persistence
Runtime OQ state includes descriptor DMA address, `buff_info` pages, `host_read_idx`, `host_refill_idx`, `refill_count`, `last_pkt_count`, `pkts_pending`, `max_single_buffer_size`, `pkts_credit_reg`, `pkts_sent_reg`, and per-queue stats. This state is volatile and tied to open/stop lifetime. Hardware-visible state consists of OQ descriptors, page DMA addresses, packet counter acknowledgements, and descriptor credits.

## Dependencies And Integration Points
The file depends on `octep_config.h` for queue sizes and thresholds, `octep_main.h` for device context and hardware ops, Linux DMA/page allocation APIs, netdevice/NAPI/GRO APIs, and `octep_rx.h` hardware formats. It is called from `octep_open()`, `octep_stop()`, and `octep_napi_poll()`.

## Risks And Edge Cases
- `octep_oq_drop_rx()` receives the original `buff_info` pointer while advancing through fragments; any future change must ensure each consumed fragment page is unmapped and released exactly once.
- Large packets span consecutive descriptors; ring wrap and `data_len` accounting must remain correct.
- Counter wrap handling writes back large packet counters when above `0xF0000000U`; hardware semantics must match this strategy.
- Page allocation or DMA mapping failures reduce refill and packet processing; sustained failures can starve OQ credits.
- Extended response header size is subtracted only when firmware advertises Rx offloads; PF/VF firmware capability mismatches can corrupt packet alignment.

## Test Signals
Run traffic tests for small frames, jumbo frames, fragmented/gathered receive, checksum offload on/off, GRO, NAPI budget exhaustion, descriptor refill threshold behavior, receive under memory pressure, queue stop/start cycles, hardware packet counter wrap simulation if possible, and DMA debug for map/unmap balance.
