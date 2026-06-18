# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_ctxts.h

## Purpose

`trace_ctxts.h` defines tracepoints for HFI1 user/context data and receive-side mapping histogram output. These events make context allocation and runtime packet distribution visible.

## Important Events

- `hfi1_uctxtdata` records device name, context/subcontext, PIO credits and hardware free counter, PIO base address, receive header queue count and DMA address, eager buffer count/DMA address, and subcontext count.
- `hfi1_ctxt_info` records user-visible context configuration such as eager TID count, eager receive size, receive header queue count and entry size, and SDMA ring size.
- `ctxt_rsm_hist` calls `hfi1_trace_print_rsm_hist()` to emit a compact histogram of receive-side mapping context use.

## Control Flow and State

The header declares only trace events. Event state is captured when callers invoke the tracepoints. The histogram state lives in `trace.c`; this header only declares the formatting helper and event.

## Dependencies and Integration Points

The events depend on `struct hfi1_devdata`, `struct hfi1_ctxtdata`, `struct hfi1_ctxt_info`, context credit fields, eager buffer metadata, and common `DD_DEV_ENTRY` trace macros. They integrate with context initialization and receive path diagnostics.

## Risks and Test Signals

The most likely risk is dereferencing partially initialized context fields if events are placed too early or too late in lifecycle code. Useful tests confirm that context open/init paths emit sane counts and DMA addresses, and that `ctxt_rsm_hist` remains bounded and readable under multi-context traffic.
