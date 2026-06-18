# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_test_stash.c

## Purpose
Stress test for QMan context/data stashing and multi-CPU portal routing. It creates a ring of per-CPU "hot potato" handlers, forwards one DMA-backed frame across CPUs through QMan FQs, mutates and validates frame data at each hop, and verifies that stashed handler context and frame data are usable in DQRR callbacks.

## Important APIs, types, and functions
`struct hp_handler` contains stashed RX FQ, TX FQ, mixers, DMA address, frame pointer, FQIDs, and CPU identity. `struct hp_cpu` tracks each CPU's handler list and iterator. `on_all_cpus` runs setup and teardown helpers on each online CPU using temporary kthreads. Main helpers include `allocate_frame_data`, `process_frame_data`, `create_per_cpu_handlers`, `init_phase2`, `init_phase3`, `init_handler`, `send_first_frame`, and `destroy_per_cpu_handlers`. DQRR callbacks are `normal_dqrr` and `special_dqrr`.

## Control flow and state behavior
`qman_test_stash` skips single-CPU systems. Otherwise it creates an aligned slab for handlers, allocates and DMA maps deterministic frame data, creates handlers on every CPU, links RX FQIDs to previous TX FQIDs, assigns LFSR mixers, initializes each RX FQ on its target CPU with `QM_FQCTRL_CTXASTASHING`, and creates TX no-modify FQs. The special handler sends the first frame. Each callback validates the frame by XORing the previous handler mixer, then applies its own mixer before enqueueing to the next handler. The special callback counts complete loops and wakes the main waitqueue at `HP_LOOPS`.

## Dependencies and integration points
Depends on `qman_dma_portal` for DMA mapping, affine portal targeting for local FQ initialization, QMan enqueue/dequeue callbacks, Linux kthreads, SMP calls, DMA APIs, waitqueues, and slab alignment. It exercises FQID allocation and release through QMan gen_pools.

## Risks and test signals
Failure cleanup is incomplete in several early-error paths; allocated DMA memory, handlers, or FQIDs may leak after a mid-test failure. The test assumes all online CPUs can run setup kthreads promptly and that portal affinity matches CPU identity. Signals are final loop completion, absence of corrupt frame warnings, no enqueue failures, and successful retirement/OOS/destruction of all RX FQs plus TX FQ destruction and FQID release.
