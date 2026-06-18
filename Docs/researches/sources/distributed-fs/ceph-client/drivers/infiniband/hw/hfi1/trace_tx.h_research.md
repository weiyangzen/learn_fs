# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_tx.h

## Purpose
`trace_tx.h` defines tracepoints for hfi1 transmit-side behavior: PIO buffer availability, QP sleep/wakeup, SDMA descriptor/engine progress, user SDMA request lifecycle, AHG updates, buffer-control-table programming, verbs send completion, send-loop activity, and accelerated IPoIB transmit queues. Like `trace_tid.h`, it is observability infrastructure rather than packet logic.

## Important APIs, Types, and Events
The file declares `parse_sdma_flags()` and `print_u32_array()` formatting helpers. Major trace families include `hfi1_piofree`, `hfi1_wantpiointr`, `hfi1_qpwakeup`, `hfi1_qpsleep`, `hfi1_sdma_descriptor`, `hfi1_sdma_engine_select`, `hfi1_sdma_user_free_queues`, `hfi1_sdma_user_process_request`, `hfi1_sdma_user_reqinfo`, `hfi1_sdma_user_header`, `hfi1_sdma_user_completion`, `hfi1_usdma_defer`, `hfi1_usdma_activate`, `hfi1_usdma_we`, `hfi1_sdma_user_header_ahg`, `hfi1_sdma_state`, `bct_set`, `bct_get`, `hfi1_qp_send_completion`, `hfi1_rc_do_send`, `hfi1_rc_do_tid_send`, and many `hfi1_txq_*`/`hfi1_tx_*` IPoIB queue events.

## Control Flow
Callers trace queue transitions and descriptor construction at specific TX lifecycle points. User SDMA call sites emit request metadata, data length, computed packet lengths, TID offsets, header templates, AHG descriptor arrays, waits, activations, and final completion states. SDMA engine code emits descriptor words, status, sequence numbers, and queue head/tail positions. PIO and verbs code trace QP waits, wakeups, and completions.

## State, Persistence, and Dependencies
The header stores no runtime data. It snapshots fields from `struct send_context`, `struct sdma_engine`, `struct hfi1_user_sdma_pkt_q`, `struct hfi1_pkt_header`, `struct buffer_control`, `struct rvt_qp`, `struct rvt_swqe`, `struct hfi1_ipoib_txq`, and `struct ipoib_txreq`. It depends on `hfi.h`, `mad.h`, `sdma.h`, `ipoib.h`, and `user_sdma.h`. The conditional `CONFIG_HFI1_DEBUG_SDMA_ORDER` path adds sequence-number detail for ordering investigations.

## Integration Points
`user_sdma.c` relies heavily on this file for `hfi1_sdma_user_*` and `hfi1_usdma_*` events. `verbs.c` and `verbs_txreq.c` use QP sleep/wakeup and completion traces. SDMA core code traces descriptor and progress state. IPoIB transmit code uses the queue and ring events to debug netdev stop/wake behavior and descriptor pressure.

## Risks and Test Signals
Risks include tracepoint format drift, copying too many AHG elements into the fixed trace array if callers pass an unexpected length, and diagnostic ambiguity when events are emitted before memory barriers or state publication. Test signals include compile coverage with and without `CONFIG_HFI1_DEBUG_SDMA_ORDER`, ftrace visibility for `hfi1_tx`, SDMA stress producing defer/activate/completion transitions, PIO pressure producing `hfi1_qpsleep`/`hfi1_qpwakeup`, and IPoIB traffic producing ring head/tail progress.
