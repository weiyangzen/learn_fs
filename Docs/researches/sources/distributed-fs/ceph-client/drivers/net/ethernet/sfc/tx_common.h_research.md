# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tx_common.h

Purpose: declares shared SFC TX queue lifecycle, completion, mapping, and TSO fallback helpers.

Important APIs: exposes queue probe/init/fini/remove, buffer dequeue, completion functions, enqueue unwind, DMA chunk/data mapping, TSO header-length calculation, maximum descriptor estimation, and software TSO fallback. `efx_tx_buffer_in_use()` treats nonzero length or option descriptors as active.

State and integration: no independent state; it is included by `tx.c`, TSO paths, and NIC-specific TX code. External `efx_separate_tx_channels` is declared for channel topology decisions elsewhere.

Risks and tests: callers must obey ownership rules documented in `efx_enqueue_unwind()` and must pass appropriate completion counters. Build-test with all SFC NIC generations and runtime-test TX queue teardown with outstanding buffers.
