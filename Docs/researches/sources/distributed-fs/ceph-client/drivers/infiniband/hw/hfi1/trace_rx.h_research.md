# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_rx.h

## Purpose

`trace_rx.h` defines receive-path tracepoints for packet headers, receive interrupts, and MMU invalidation notifications. These events expose low-level receive metadata that helps correlate packet processing with context and memory events.

## Important Events

- `hfi1_rcvhdr` records device, RHF error flags, context, receive packet type, header length, total length, updated eager indicator, and eager tail index.
- `hfi1_receive_interrupt` records device, context number, slow-path status, and DMA receive-tail setting.
- `hfi1_mmu_invalidate` records context/subcontext, invalidation type string, and start/end address range.

The file also defines `show_tidtype()` for expected, eager, and invalid TID type names.

## Control Flow and State

These tracepoints are passive receive-path instrumentation. They snapshot packet/context fields when invoked. They do not own persistent state.

## Dependencies and Integration Points

The file depends on RHF decoding helpers, receive context structures, packet metadata, MMU invalidation call sites, and `show_packettype()` from `trace.h`. It is relevant for TID RDMA because KDETH/TID errors and FECN eager-delivery fallback are diagnosed by combining receive header traces with TID-specific and header-decoding traces.

## Risks and Test Signals

Risks include logging packet metadata after packet buffers have been advanced or using stale RHF fields. Test signals include receive interrupt traces per active context, rcvhdr traces with correct expected/eager/error/bypass type, and MMU invalidation traces aligned with memory deregistration or invalidation tests.
