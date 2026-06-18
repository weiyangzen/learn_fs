# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-trace.h

## Purpose

`cdns2-trace.h` defines the trace event schema for the Cadence CDNS2 USBHS gadget driver. It converts low-level controller activity into structured ftrace events for pullup transitions, endpoint halt/configuration, EP0 setup/status flow, USB and DMA interrupts, request lifecycle, TRB queuing/completion, ring snapshots, and request progress.

## Important APIs, Event Classes, And Events

The trace system is named `cdns2-dev` with variable name `cdns2_dev`. The header includes tracepoint APIs, USB Chapter 9 definitions, `cdns2-gadget.h`, and `cdns2-debug.h`, relying on decode helpers for USB IRQs, endpoint IRQs, EP0 IRQs, control requests, TRBs, and raw rings.

Event classes reduce duplication. `cdns2_log_enable_disable` backs `cdns2_pullup`. `cdns2_log_simple` backs string events such as no-room-on-ring, EP0 status/setup, and device state. `cdns2_log_doorbell` records endpoint name and transfer-ring address. `cdns2_log_request` backs enqueue, enqueue error, allocation, free, dequeue, and giveback while capturing request pointers, buffer, lengths, status, DMA, flags, SG metadata, and TRB bounds.

Dedicated events include endpoint halt, WA1 diagnostics, DMA endpoint interrupt status, EPX/EP0 IRQ decoding, TRB queue/complete, ring dump, endpoint enable/disable/busy-halt retry, request-handled progress, and endpoint hardware configuration.

## Control Flow And State

Trace calls are passive hooks placed in implementation code. When disabled, tracepoints are low overhead; when enabled, they snapshot selected driver and MMIO state into trace buffers. Some events read hardware registers and some copy a full transfer ring, so event placement matters.

Trace state is not driver-owned persistence. Trace buffers are managed by the kernel tracing subsystem. The header copies transient request, endpoint, and TRB data into trace entries so later analysis is not dependent on object lifetime, except for diagnostic pointer values.

## Dependencies And Integration Points

The header integrates with CDNS2 private structs and debug decoders. It depends on `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE cdns2-trace`, which require build rules to make the header visible from the trace generation context. Runtime consumers use tracefs/perf/ftrace.

## Risks

The biggest risks are tracepoint cost and dereference safety. `cdns2_ring` copies a sizable TRB segment; enabling it heavily can perturb timing or flood buffers. Events that dereference request, endpoint, descriptor, or ring pointers assume valid objects at the call site. MMIO values read in `TP_fast_assign` can race with hardware.

## Test Signals

Build tests should catch trace generation mistakes. Runtime validation should enable individual events and confirm expected output during pullup, EP0 setup, request enqueue/dequeue/giveback, endpoint halt, DMA interrupt, and TRB completion paths.
