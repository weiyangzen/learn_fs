# sources/distributed-fs/ceph-client/drivers/misc/ocxl/trace.h

Purpose: declares OCXL trace events for MMU notifier activity, context lifecycle, PASID termination, XSL fault handling/acknowledgement, and AFU IRQ allocation/free/receive.

Important APIs and types: `TRACE_EVENT()` and `DECLARE_EVENT_CLASS()` definitions include `ocxl_mmu_notifier_range`, `ocxl_init_mmu_notifier`, `ocxl_release_mmu_notifier`, `ocxl_context_add`, `ocxl_context_remove`, `ocxl_terminate_pasid`, `ocxl_fault`, `ocxl_fault_ack`, `ocxl_afu_irq_alloc`, `ocxl_afu_irq_free`, and `ocxl_afu_irq_receive`.

Control flow: call sites pass PASID, PIDR/TIDR, SPA pointer, PE, DSISR/DAR/TFC, virtual/hardware IRQ data, and address ranges. The trace definitions format these fields for kernel tracing.

State and persistence: trace events are transient diagnostic data emitted into tracing buffers when enabled.

Dependencies and integration points: includes `<linux/tracepoint.h>` and uses the standard `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` pattern. It is consumed by `trace.c`, `link.c`, and IRQ/context code.

Risks and test signals: field-size mismatches can produce misleading diagnostics, especially pointer, PIDR, and 64-bit register formatting. Tests should enable each event, trigger the corresponding operation, and verify the expected payload names and values are present.
