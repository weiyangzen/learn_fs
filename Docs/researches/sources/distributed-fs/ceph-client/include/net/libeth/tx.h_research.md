# sources/distributed-fs/ceph-client/include/net/libeth/tx.h

Purpose: Defines libeth transmit completion descriptors and common completion helpers for skb, fragments, slab buffers, XDP, and XSK transmit paths.

Important APIs/types/functions: `libeth_sqe_type` classifies send queue elements as empty/context, slab, frag, skb, XDP_TX, XDP_XMIT, XDP_XMIT_FRAG, XSK_TX, and XSK_TX_FRAG. `libeth_sqe` stores type, batch/report index, object union, DMA unmap address/length, fragment count, packet/byte stats, and driver-private scratch. `LIBETH_SQE_CHECK_PRIV` verifies private data fits. `libeth_cq_pp` bundles DMA device, XDP frame bulk, stats pointer, XDP count, and NAPI context. `libeth_tx_complete` handles common completion; `libeth_tx_complete_any` covers remaining/special types.

Control flow: Completion first unmaps DMA for skb/frag/slab types, then updates skb stats and consumes skb or frees slab memory. Other types fall through to specialized handling elsewhere. Every completed SQE is reset to `LIBETH_SQE_EMPTY`.

State and persistence: State is per-descriptor completion metadata and per-poll on-stack stats. No persistent global state.

Dependencies/integration: Depends on sk_buff, DMA mapping helpers, NAPI skb consumption, XDP frame bulk, libeth stats types, and driver queues.

Risks: Wrong `type` causes missed unmap/free or double-free; only common types update stats in the inline helper, so XDP/XSK paths must use `libeth_tx_complete_any`; driver-private data size must be asserted. Test signals include skb completion stats, frag-only unmap, slab free, empty/context no-op, NAPI/non-NAPI skb consume, XDP/XSK special completion, and SQE reset.
