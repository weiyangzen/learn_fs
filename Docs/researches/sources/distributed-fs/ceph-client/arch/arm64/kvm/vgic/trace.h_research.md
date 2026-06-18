<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/trace.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/trace.h

## Purpose
This VGIC trace header defines a tracepoint for pending interrupt state updates in the virtual interrupt controller.

## Important APIs, Types, And Functions
- `TRACE_EVENT(vgic_update_irq_pending)` records vCPU ID, IRQ number, and pending level.

## Control Flow
VGIC code calls the generated `trace_vgic_update_irq_pending()` helper when an interrupt pending state changes. The trace event captures fields and formats a concise line for tracefs/perf consumers.

## State And Persistence Behavior
No VGIC state is mutated or persisted here. Event samples are transient trace buffer data when tracing is enabled.

## Dependencies And Integration Points
It depends on Linux tracepoint infrastructure and is part of `TRACE_SYSTEM kvm`. `TRACE_INCLUDE_PATH` points back to the VGIC source directory so trace generation can find this header.

## Risks And Edge Cases
Tracepoint field names and event names are consumed by tooling. Because this is on interrupt paths, enabled tracing overhead should stay small.

## Test Signals
Enable `events/kvm/vgic_update_irq_pending` and inject SGIs, PPIs, SPIs, or LPIs. Kernel build validates trace macro paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/trace.h -->
