# sources/distributed-fs/ceph-client/drivers/ntb/test/ntb_perf.c

## Purpose
Implements an NTB raw performance measuring client. It negotiates inbound/outbound memory windows with peers, maps peer windows, then copies configurable amounts of data to the peer window using CPU MMIO writes or DMA to report throughput through debugfs.

## Important APIs, Types, And Functions
- `enum perf_cmd` defines the control protocol for exchanging sizes, translation addresses, clear events, done status, and link state.
- `struct perf_ctx` is per-device state, including peer descriptors, command transport callbacks, test threads, debugfs, and synchronization.
- `struct perf_peer` stores per-peer inbound/outbound MW mappings, translation addresses, service work, status bits, and init completion.
- `struct perf_thread` is a worker that copies data, tracks DMA synchronization, copied bytes, duration, and status.
- `perf_init_service()` selects message-register command transport when available, otherwise scratchpad/doorbell transport.
- `perf_service_work()` executes the command state machine: send size, setup inbound buffer, send xlat, setup outbound translation, or clear.
- `perf_submit_test()` launches worker threads against a selected peer and waits for completion.
- Debugfs files `info`, `run`, and `threads_count` expose configuration, status, execution, and results.

## Control Flow
Probe allocates context, derives global peer indices, maps each outbound peer MW, initializes work threads, selects command service, sets NTB callbacks, unmasks either message or doorbell events, enables link, and creates debugfs. Link events mark peers up/down and enqueue size or clear commands. Command receive decodes peer messages/scratchpads and schedules service work to allocate inbound buffers and program MW translations. Once both sides exchange size and translation, the peer completion is signaled.

Writing a peer index to `run` waits for peer init, marks the test busy, initializes per-thread state, queues copy workers, and waits until the atomic thread counter reaches zero. Workers allocate random source buffers, optionally request DMA channels and map peer MMIO resources, loop until `1 << total_order` bytes are copied in chunks up to `1 << chunk_order`, then synchronize DMA and record duration. Reading `run` formats per-thread throughput or error status.

## State And Persistence
State is volatile in peer status bits, completions, scratchpad/message command slots, MW translations, DMA mappings, worker state, and debugfs. Link-down clear commands free inbound/outbound translations and abort active tests. Module parameters `max_mw_size`, `chunk_order`, `total_order`, and `use_dma` influence runtime behavior.

## Dependencies And Integration Points
Depends on NTB peer MW APIs, inbound MW translation, doorbells, scratchpads or messages, DMAengine, workqueues, waitqueues, debugfs, and PCI DMA mapping. It is a consumer of hardware providers and a validation tool for MW throughput.

## Risks And Edge Cases
- Global-index calculation and scratchpad layout are subtle for multi-port NTB topologies.
- Command transport assumes single in-flight message slots and retry loops; busy or stale status can return `-EAGAIN`.
- DMA mapping of peer MMIO resources and source pages is sensitive to DMA alignment and NUMA channel selection.
- `perf_set_tcnt()` and result reads serialize with `busy_flag`; interruptions must terminate all workers and DMA waits.
- Link-down while a test is active frees MWs and terminates work, so cleanup ordering is important.
- Large `total_order`/thread counts can allocate substantial memory and run long tests.

## Test Signals
Functional tests include loading with CPU copy and DMA modes, checking debugfs `info` for peer mappings, writing peer index to `run`, reading throughput results, changing `threads_count`, and bouncing links during tests. Logs for command service selection, `Failed to set inbuf/outbuf translation`, DMA map failures, or `Freeing while test on-fly` identify integration issues.
