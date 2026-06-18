# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_hw_queues.c

## Purpose
`efct_hw_queues.c` builds and tears down SLI queue topology for EFCT. It creates EQ, CQ, MQ, WQ, and RQ-pair objects, maps WQs to CPU interrupt affinities, tracks RQ buffer ownership, processes RQ completions, and reposts consumed receive buffer pairs.

## Important APIs, Types, and Functions
Top-level exports are `efct_hw_init_queues`, `efct_hw_map_wq_cpu`, queue constructors (`efct_hw_new_eq`, `efct_hw_new_cq`, `efct_hw_new_cq_set`, `efct_hw_new_mq`, `efct_hw_new_wq`, `efct_hw_new_rq_set`), destructors (`efct_hw_del_eq`, `efct_hw_del_cq`, `efct_hw_del_mq`, `efct_hw_del_wq`, `efct_hw_del_rq`, `efct_hw_queue_teardown`), and RQ helpers (`efct_hw_rqpair_process_rq`, `efct_hw_rqpair_sequence_free`, `efct_efc_hw_sequence_free`). Internal helpers `efct_hw_rqpair_find`, `efct_hw_rqpair_get`, and `efct_hw_rqpair_put` manage RQ tracker state.

## Control Flow
`efct_hw_init_queues` resets queue counters, initializes the EQ list, creates one EQ per configured vector, creates a single MQ on the first EQ, creates one WQ per EQ, allocates a CQ set for RQs, and allocates an RQ-pair set. Each RQ object owns a header queue and a data queue, plus an `rq_tracker` indexed by ring position. All RQs are marked MRQ with the first RQ header ID as the base MRQ ID.

RQ completion flow starts in HW CQ processing and enters `efct_hw_rqpair_process_rq`. It parses RQ ID/index/status, handles buffer length/DMA errors by retrieving and reposting the consumed buffer, finds the RQ wrapper through the RQ hash and lookup table, removes the `struct efc_hw_sequence` from `rq_tracker`, fills lengths/fcfi/EQ private pointer, and calls `efct_unsolicited_cb`. Freeing a sequence posts payload then header DMA addresses back to the paired RQ and restores the tracker entry.

## State and Persistence Behavior
Queue topology is volatile driver state under `struct efct_hw`. Queue wrapper objects are heap allocated and linked into EQ/CQ lists. RQ state persists while hardware is active through `rq_tracker`, which is protected by the header RQ lock and must mirror what was posted to firmware. `wq_cpu_array` maps Linux CPUs to WQs based on PCI IRQ affinity.

## Dependencies and Integration Points
The file depends on SLI queue allocation APIs (`sli_queue_alloc`, `sli_cq_alloc_set`, `sli_fc_rq_set_alloc`, `sli_rq_write`), PCI IRQ affinity, EFC unsolicited callback dispatch, and the shared queue hash helpers in `efct_hw.c`. It is called by `efct_hw_init` and `efct_hw_teardown`.

## Risks
Queue allocation failure paths free wrapper objects but rely on later teardown/free calls for SLI queue resources in some cases. `efct_hw_new_mq` stores `entry_size = EFCT_HW_MQ_DEPTH` instead of an explicit MQ entry byte size, which is worth checking against SLI expectations. `efct_hw_map_wq_cpu` leaves CPUs unmapped if affinity masks are unavailable; HW allocation falls back to WQ 0. RQ tracker corruption causes dropped frames or double-posted buffers. Error cases in RQ processing need careful buffer reposting to avoid RQ starvation.

## Test Signals
Tests should validate queue counts for one and multiple EQs, CQ-set/RQ-set allocation, CPU-to-WQ mapping with missing affinity, RQ completion/repost parity, RQ error status handling, queue teardown after partial allocation, and unsolicited frame dispatch after RQ processing.
