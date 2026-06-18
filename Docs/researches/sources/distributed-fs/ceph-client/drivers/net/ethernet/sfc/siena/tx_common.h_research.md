<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx_common.h

## Purpose
Declares shared Siena TX queue lifecycle, completion, DMA mapping, descriptor-limit, and TSO fallback helpers used by the TX hot path and NIC setup code.

## Important APIs, Types, And Functions
- Lifecycle declarations: `efx_siena_probe_tx_queue()`, `efx_siena_init_tx_queue()`, `efx_siena_fini_tx_queue()`, `efx_siena_remove_tx_queue()`.
- Completion declarations: `efx_siena_xmit_done_check_empty()` and `efx_siena_xmit_done()`.
- Mapping helpers: `efx_siena_enqueue_unwind()`, `efx_siena_tx_map_chunk()`, `efx_siena_tx_map_data()`.
- Utility: `efx_tx_buffer_in_use()`, `efx_siena_tx_max_skb_descs()`, `efx_siena_tx_tso_fallback()`, and module parameter declaration `efx_siena_separate_tx_channels`.

## Control Flow
This header provides the contracts between enqueue code and completion/setup code. Enqueue maps descriptors and calls unwind on failure; event handling calls completion helpers; probe/remove call lifecycle helpers.

## State And Persistence Behavior
No state is owned here. `efx_tx_buffer_in_use()` defines the shared meaning of an active TX buffer as nonzero length or an option descriptor flag.

## Dependencies And Integration Points
Relies on `struct efx_tx_queue`, `struct efx_tx_buffer`, `struct sk_buff`, and DMA address types from surrounding driver headers. Included by `tx.c` and `tx_common.c`.

## Risks And Test Signals
The inline buffer-use predicate must remain consistent with producer and completion code. Build coverage should catch signature drift between hot path and common implementation. Runtime signals are correct unwind/completion behavior and no spurious-reset logs under normal TX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx_common.h -->
