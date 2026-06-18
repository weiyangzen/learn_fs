<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/tx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/tx.h

## Purpose
Declares internal EF4 transmit helpers related to descriptor length limiting and TSO enqueue support.

## Important APIs, types, and functions
- `ef4_tx_limit_len(struct ef4_tx_queue *, dma_addr_t, unsigned int)` lets NIC-specific code cap a DMA segment length, typically for page or hardware boundary constraints.
- `ef4_enqueue_skb_tso(struct ef4_tx_queue *, struct sk_buff *, bool *)` declares a TSO enqueue path, although the researched `tx.c` comments indicate current Falcon code no longer uses software TSO there.

## Control flow
No runtime control flow is implemented in this header. It provides cross-file declarations for TX implementation units and NIC-specific helpers.

## State and persistence behavior
No state is stored here.

## Dependencies and integration points
Includes `<linux/types.h>` and depends on EF4 TX queue and SKB types from including translation units. The declarations integrate TX data-path code with NIC descriptor constraints and any TSO implementation compiled elsewhere.

## Risks and test signals
Risks are declaration drift if the TSO implementation is removed or signatures change. Test signals are build coverage of all TX translation units and descriptor-boundary tests for `ef4_tx_limit_len` callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/tx.h -->
