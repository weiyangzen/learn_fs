# sources/distributed-fs/ceph-client/include/linux/async_tx.h

## Purpose
Declares the async_tx DMA offload framework for memory copy, XOR, RAID6 syndrome generation/validation, recovery, and callback chaining.

## Important APIs, Types, And Functions
`struct dma_chan_ref` tracks DMA channels in the async pool. `enum async_tx_flags` controls zero/drop destination behavior, immediate ACK, dependency fences, and PQ XOR destination behavior. `struct async_submit_ctl` carries flags, dependency descriptor, callback, callback parameter, and scribble space. Channel functions include `async_tx_issue_pending_all()`, `async_tx_issue_pending()`, and `async_tx_find_channel()`, with DMA-engine/config stubs when unavailable. Helpers include `async_tx_sync_epilog()`, `addr_conv_t`, `init_async_submit()`, `async_tx_submit()`, and operations `async_xor()`, `async_xor_offs()`, `async_xor_val_offs()`, `async_memcpy()`, `async_trigger_callback()`, `async_gen_syndrome()`, `async_syndrome_val()`, `async_raid6_2data_recov()`, `async_raid6_datap_recov()`, and `async_tx_quiesce()`.

## Control Flow, State, And Persistence
Operations choose a DMA channel when available and fall back to synchronous execution otherwise. Dependency descriptors chain operations; `ASYNC_TX_FENCE` marks data dependencies, and callbacks run at completion or immediately in synchronous fallback. Channel refs are RCU/list/atomic-count managed by the core.

## Dependencies And Integration Points
Depends on dmaengine, spinlocks, interrupts, pages, and optional architecture channel selection. Integrated by RAID, MD, lib/raid6, storage, and memory offload users.

## Risks And Test Signals
The async/sync semantic split is risky: flags such as `ASYNC_TX_XOR_ZERO_DST` and `ASYNC_TX_XOR_DROP_DST` differ between paths. Tests should cover DMA and no-DMA configs, dependency chains, callback order, issue-pending behavior, RAID6 recovery correctness, channel switching, and quiesce waiting.
