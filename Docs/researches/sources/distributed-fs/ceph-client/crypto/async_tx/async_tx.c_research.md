# sources/distributed-fs/ceph-client/crypto/async_tx/async_tx.c

Purpose: provides core async_tx descriptor submission, dependency chaining, channel switching, callback triggering, quiescing, and DMA-engine channel selection support.

Important APIs/types/functions: under `CONFIG_DMA_ENGINE`, `async_tx_init()` and `async_tx_exit()` manage global DMA engine references, and `__async_tx_find_channel()` prefers a dependent descriptor's channel when capable. `async_tx_channel_switch()` inserts an interrupt descriptor or waits when a dependency chain must move channels. `async_tx_submit()` submits or chains descriptors while respecting dependency locks. `async_trigger_callback()` schedules a callback after dependencies. `async_tx_quiesce()` waits for completion and acks descriptors.

Control flow: a new descriptor with a dependency is examined under the dependency descriptor lock. It is appended directly, submitted directly, or routed through channel switch. Channel switch uses DMA interrupt capability when available, otherwise waits synchronously. Submission acks descriptors according to `ASYNC_TX_ACK` and always acks consumed dependencies. Synchronous fallback users call `async_tx_quiesce()` before CPU work and `async_tx_sync_epilog()` after.

State and persistence: descriptor parent/next/ack state persists until DMA completion and ack. No filesystem state. Module init holds DMA engine availability while loaded.

Dependencies and integration points: depends on DMA engine descriptor conventions, async_tx flags/macros from `<linux/async_tx.h>`, RCU list headers, and exported users in async_memcpy/xor/pq/raid recovery.

Risks: dependency chaining is lock-order sensitive; submitting while holding descriptor locks can deadlock drivers, hence the disposition logic. Acking the wrong descriptor can hide live operations. Fallback waits panic on DMA error. Channel switching relies on interrupt descriptor support or safe polling.

Test signals: same-channel chaining, cross-channel switching, no-interrupt fallback, dependency ack misuse detection, callback after dependency, `ASYNC_TX_ACK` behavior, DMA errors, and configs without DMA engine.
