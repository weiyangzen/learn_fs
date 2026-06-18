# sources/distributed-fs/ceph-client/crypto/async_tx/async_raid6_recov.c

Purpose: implements async_tx RAID6 recovery for two missing data blocks or one data block plus P parity, using DMA PQ/XOR/memcpy helpers when available and software RAID6 recovery otherwise.

Important APIs/types/functions: `async_sum_product()` computes `A*x ^ B*y`; `async_mult()` multiplies a page by a GF coefficient. `__2data_recov_4()`, `__2data_recov_5()`, and `__2data_recov_n()` handle two-data recovery special cases. `async_raid6_2data_recov()` is the exported two-data recovery entry. `async_raid6_datap_recov()` is the exported data-plus-P recovery entry.

Control flow: public functions first choose sync fallback if no DMA PQ channel or no scribble buffer is available. The fallback waits dependencies, builds a pointer table with zero pages, and calls `raid6_2data_recov()` or `raid6_datap_recov()`. Async paths construct operation chains using syndrome generation, XOR, multiplication, and sum-product helpers, preserving original callback/flags for the final operation. The code temporarily rewrites `blocks` and `offs` to compute deltas, then restores them.

State and persistence: operations modify failed data/parity pages in place. Descriptor chains and scribble buffers are transient. The caller-owned `blocks` and `offs` arrays are temporarily mutated and restored.

Dependencies and integration points: depends on RAID6 Galois-field tables, async_memcpy, async_xor, async_pq, DMA engine PQ, and async_tx core.

Risks: recovery math and temporary pointer rewrites are fragile. Missing scribble buffers force sync path or reuse caller arrays. Special-case paths for 4- and 5-disk arrays exist because DMA engines may not handle zero/single-source PQ uniformly. Invalid fail indexes hit `BUG_ON()`.

Test signals: two-data recovery across 4, 5, and larger disk counts; data+P recovery; DMA and sync paths; all faila/failb orderings; NULL source pages; callback/dependency ordering; and recovered data validation against software RAID6.
