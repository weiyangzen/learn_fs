# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_eth_com.h

## Purpose
`ena_eth_com.h` defines the ENA Ethernet I/O communication contract used by the netdev and XDP paths. It wraps hardware descriptor preparation and completion APIs from the ENA common layer with Linux-driver-facing TX/RX context structures and fast inline helpers for doorbells, completion queue phase handling, interrupt unmasking, LLQ burst accounting, NUMA hints, and queue free-space checks.

## Important APIs, Types, And Functions
`struct ena_com_tx_ctx` carries transmit metadata: ENA metadata descriptor state, DMA buffer list, optional LLQ push header, protocol indices, checksum/TSO flags, request ID, buffer count, and header length. `struct ena_com_rx_ctx` carries received descriptor output, checksum status, hash, fragment status, descriptor count, packet offset, and buffer capacity. External APIs are `ena_com_prepare_tx()`, `ena_com_rx_pkt()`, `ena_com_add_single_rx_desc()`, and `ena_com_cq_empty()`. Inline helpers include `ena_com_free_q_entries()`, `ena_com_sq_have_enough_space()`, `ena_com_is_doorbell_needed()`, `ena_com_write_sq_doorbell()`, `ena_com_tx_comp_req_id_get()`, `ena_com_comp_ack()`, and `ena_com_cq_inc_head()`.

## Control Flow, State, And Integration
The TX path fills `ena_com_tx_ctx`, optionally checks LLQ burst capacity with `ena_com_is_doorbell_needed()`, calls `ena_com_prepare_tx()`, and rings the SQ doorbell. Completion handling reads the current CQ descriptor at `head & (q_depth - 1)`, validates the phase bit, uses `dma_rmb()` before consuming `req_id`, checks the ID against queue depth, and advances head/phase. State is transient ring state held in `ena_com_io_sq` and `ena_com_io_cq`, especially `tail`, `next_to_comp`, `head`, `phase`, cached TX metadata, LLQ entry budget, doorbell address, and interrupt registers.

## Dependencies
This header depends on `ena_com.h`, ENA descriptor definitions in `ena_eth_io_defs.h`, Linux MMIO ordering (`writel`, `dma_rmb`, `READ_ONCE`), and netdev logging. It is consumed heavily by `ena_netdev.c` and `ena_xdp.c`.

## Risks And Test Signals
The critical risks are descriptor ring wrap/phase errors, stale completion reads without the DMA barrier, LLQ free-space underestimation, invalid request IDs, and incorrect metadata caching decisions. Test signals include TX/RX traffic under ring wrap, LLQ and host-placement modes, TSO/checksum offload traffic, invalid completion fault injection, and queue stop/wake behavior under saturation.
