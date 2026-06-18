# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_droq.c

## Purpose
Implements Descriptor Ring Output Queues, which are Octeon-to-host receive queues. It allocates DMA descriptor rings and receive buffers, tracks hardware packet counts, converts completed descriptors into SKBs or dispatch packets, refills descriptors, handles low-credit/OOM recovery, and registers per-queue receive operations.

## Important APIs, Types, and Functions
Public functions include `octeon_get_dispatch_arg`, `octeon_droq_check_hw_for_pkts`, `octeon_delete_droq`, `octeon_init_droq`, `octeon_retry_droq_refill`, `octeon_droq_process_packets`, `octeon_droq_process_poll_pkts`, `octeon_enable_irq`, `octeon_register_droq_ops`, `octeon_unregister_droq_ops`, and `octeon_create_droq`. Internal helpers include `octeon_droq_setup_ring_buffers`, `octeon_droq_destroy_ring_buffers`, `octeon_create_recv_info`, `octeon_droq_refill`, `octeon_droq_dispatch_pkt`, `octeon_droq_drop_packets`, and `octeon_droq_fast_process_packets`.

## Control Flow
Initialization allocates a coherent descriptor ring, allocates one receive buffer per descriptor, maps buffers for device DMA, computes the maximum safe empty descriptor threshold for 64 KiB packets, initializes dispatch list state, and asks chip code to program OQ registers. Runtime processing reads the hardware packet count, caps work by budget, swaps descriptor metadata, distinguishes normal NIC data from slow-path opcodes, either passes packets to `droq->ops.fptr` or queues dispatch callbacks, advances read/refill indices, refills descriptors when thresholds are reached, writes credits after a memory barrier, then runs queued dispatch functions. Poll-mode processing loops until budget is consumed or no packets remain.

## State and Persistence Behavior
Persistent queue state is in `struct octeon_droq`: descriptor DMA address, ring indices, pending packet count, refill count, thresholds, receive buffer list, credit/sent registers, dispatch list, stats, NAPI object, app context, and CPU callback data. Buffers transition from device-owned DMA mappings to host-owned SKBs/pages and back during refill.

## Dependencies and Integration Points
Depends on DMA helpers, page/SKB receive-buffer helpers from `octeon_network.h`, dispatch registration from `octeon_device.c`, IQ interrupt accounting, chip-specific register setup, NAPI/tasklet callers, and LiquidIO firmware receive headers from `liquidio_common.h`.

## Risks
Ring index, refill, and DMA ownership bugs can corrupt receive traffic or leak pages. Multi-buffer packet assembly and slow-path dispatch depend on accurate firmware length and header fields. Low-memory behavior tries to pull up undispatched buffers and schedule OOM recovery; regressions can starve the device of credits. `octeon_create_droq` increments `num_oqs` after `octeon_init_droq`, while `octeon_init_droq` is also used by initial setup that increments elsewhere, so call-site ownership matters.

## Test Signals
RX traffic with linear and jumbo packets, slow-path dispatch packets, no-dispatch drops, low-memory refill failure, OOM retry, NAPI and tasklet processing, budget limits with `drop_on_max`, queue delete after packets, interrupt resend/enable, descriptor credit accounting, page recycling, DMA unmap checks, and stats counters are primary signals.
