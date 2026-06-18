# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-trace.h

Purpose: declares Linux ftrace tracepoints for the older Cadence CDNS3 USBSS gadget controller path. The complete 496-line file was read. It records endpoint halt/workaround activity, doorbell writes, USB and endpoint IRQ decoding, control requests, request lifecycle, aligned-buffer handling, TRB preparation/completion, ring dumps, endpoint enable/disable state, and request-handled decisions.

Important APIs/types/functions: `CDNS3_MSG_MAX`; tracepoints and event classes including `cdns3_halt`, `cdns3_wa1`, `cdns3_wa2`, `cdns3_log_doorbell`, `cdns3_log_usb_irq`, `cdns3_log_epx_irq`, `cdns3_log_ep0_irq`, `cdns3_log_ctrl`, `cdns3_log_request`, `cdns3_ep0_queue`, `cdns3_log_aligned_request`, `cdns3_log_trb`, `cdns3_log_ring`, `cdns3_log_ep`, and `cdns3_log_request_handled`; the `TRACE_INCLUDE_*` plus `<trace/define_trace.h>` block.

Control flow: no standalone runtime flow. When enabled, generated tracepoint call paths run `TP_fast_assign` blocks to snapshot request, endpoint, register, and decoded state, then format via `TP_printk`.

State and persistence: owns no persistent driver state; emitted trace records are transient ftrace data. Some events read live MMIO/register or request fields, so each record is a volatile snapshot.

Dependencies/integration: depends on Linux tracepoint/USB headers and local `core.h`, `cdns3-gadget.h`, `cdns3-debug.h`. Integrated through CDNS3 instrumentation sites and the kernel tracing subsystem.

Risks: tracepoints must only dereference live request/endpoint objects; IRQ events read registers while tracing; large ring dynamic buffers can be expensive or truncated; the file is CDNS3, not the newer CDNSP path.

Test signals: build with tracing, enable `cdns3:*`, enumerate a gadget, queue control/bulk traffic, force stalls/workarounds, and verify decoded IRQ, request, TRB, and ring output without crashes or suspicious truncation.
