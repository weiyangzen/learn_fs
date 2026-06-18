# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/qos_sq.c

## Purpose
`qos_sq.c` manages the backing NPA/NIX resources for dynamically allocated QoS send queues. It allocates SQB aura/pool memory, initializes QoS SQs, disables contexts, drains pending descriptors, frees SQBs, and exposes qid allocation helpers for the HTB tree manager.

## Important APIs, Types, and Functions
Exports are `otx2_qos_get_qid()`, `otx2_qos_free_qid()`, `otx2_qos_enable_sq()`, and `otx2_qos_disable_sq()`. Key internals include `otx2_qos_sq_aura_pool_init()`, `otx2_qos_sq_free_sqbs()`, `otx2_qos_sqb_flush()`, `otx2_qos_ctx_disable()`, `otx2_qos_nix_npa_ndc_sync()`, and `otx2_qos_aura_pool_free()`.

## Control Flow
Enable derives the real SQ index from `hw->non_qos_queues + qidx`, locks the mailbox, initializes the NPA aura/pool and SQB buffers, then calls common SQ initialization. Disable validates that the queue is a live QoS queue, waits for SQB head/tail to settle, flushes SMQ, performs NIX/NPA NDC sync, cleans TX CQEs, disables SQ/aura/pool contexts by mailbox AQ writes, frees SQB pages and queue memory, and frees aura/pool qmem.

## State and Persistence
State spans the QoS SQ bitmap, `qid_to_sqmap`, SQB pointers/counts in `otx2_snd_queue`, NPA aura/pool contexts, SQ context, queue memory (`sqe`, `tso_hdrs`, `timestamps`), and CQ completion state. Resources persist only while a QoS class owns the qid and the interface is up.

## Dependencies and Integration Points
The file uses `otx2_txrx.h` queue structures, `otx2_struct.h` descriptor formats, NPA/NIX AQ mailbox helpers, common SQ initialization, SMQ flush helpers, DMA mapping/IOMMU translation, and `otx2_cleanup_tx_cqes()` from the data path. It is called by `qos.c`.

## Risks and Edge Cases
Mailbox lock coverage is split between callers and helpers; nested or missing locks can deadlock or race. Error unwind during SQB allocation must remove buffers from aura and unmap pages correctly. Disable returns early when interface is down because common teardown already freed SQs. The code verifies indices to avoid disabling non-QoS queues. CN10K LMTST uses a different AQ message type.

## Test Signals
Test repeated HTB class add/delete under traffic, QoS queue exhaustion, interface down while QoS queues exist, DMA allocation failure injection, CN10K and non-CN10K AQ paths, SQB leak checks, TX CQ cleanup correctness, and qid bitmap compaction after deletes.
