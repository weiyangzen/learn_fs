# sources/distributed-fs/ceph-client/drivers/net/ipa/gsi_trans.c

Purpose: Implements the GSI transaction abstraction used for IPA data transfers and immediate commands. It reserves TREs, owns scatterlist/command-payload resources, formats TREs, rings channel doorbells, tracks transaction lifetimes, handles DMA mapping/unmapping, and coordinates completion/cancellation.

Important APIs/functions: Pool APIs are `gsi_trans_pool_init()`, `gsi_trans_pool_alloc()`, `gsi_trans_pool_exit()`, plus DMA variants. Transaction APIs include `gsi_channel_trans_alloc()`, `gsi_trans_free()`, `gsi_trans_cmd_add()`, `gsi_trans_page_add()`, `gsi_trans_skb_add()`, `gsi_trans_commit()`, `gsi_trans_commit_wait()`, `gsi_trans_complete()`, `gsi_trans_read_byte()`, and channel transaction init/exit. Private state helpers move transactions between allocated, committed, pending, completed, polled, and free cursors.

Control flow: Allocation atomically reserves TRE capacity before returning a zeroed `struct gsi_trans` and scatterlist space. Add functions populate command, page, or SKB scatterlist entries and perform DMA mapping for data paths. Commit writes one TRE per scatterlist element, sets chain/IEOT/BEI/type flags, maps the final TRE to the transaction, advances ring index, updates TX accounting, moves state to committed/pending, and rings the doorbell when requested or when the ring is full. Completion unmaps DMA, calls IPA completion callback, completes waiters, and frees resources. Reset cancellation marks pending transactions cancelled and schedules NAPI.

State and persistence: `struct gsi_trans_info` holds atomic TRE availability, cursor IDs, transaction array, TRE-to-transaction map, scatterlist pool, and command payload DMA pool. Pools are fixed-size and circular; allocations are implicitly freed when TRE reservations are released. No persistent storage exists.

Dependencies: Depends on Linux DMA/scatterlist/SKB APIs, `gsi_private` for doorbells/update, `ipa_gsi` callbacks for transaction release/complete and TX accounting, and `ipa_cmd` opcodes for immediate commands.

Risks: Cursor arithmetic is modulo ring count and assumes power-of-two validated ring sizes. Pool allocation intentionally over-allocates to avoid wrap straddles; changing max allocation can double memory use. Failure to free unused or failed transactions leaks TRE reservations. Command transactions use DMA-coherent payloads and `DMA_NONE`; mixing data and command assumptions would corrupt mapping/unmapping behavior.

Test signals: Allocation pressure should return NULL rather than overrun TREs. SKB/page mapping failures should be recoverable by freeing the transaction. Completion events should map to the final TRE. Cancel/reset tests should complete cancelled RX transactions. TX tests should verify BQL queued/completed byte and transaction counts.
