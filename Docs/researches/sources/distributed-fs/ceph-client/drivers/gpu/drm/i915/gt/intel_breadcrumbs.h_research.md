<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_breadcrumbs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_breadcrumbs.h

## Purpose
`intel_breadcrumbs.h` declares the breadcrumb signaling API and small lifecycle helpers for engine request-completion notifications.

## Important APIs, Types, and Functions
It declares creation/free/reset/park functions, request enable/cancel functions, context cleanup, and debug printing. Inline helpers are `intel_breadcrumbs_unpark()`, `intel_breadcrumbs_park()`, `intel_engine_signal_breadcrumbs()`, `intel_breadcrumbs_get()`, and `intel_breadcrumbs_put()`.

## Control Flow
Callers create breadcrumbs for an IRQ-capable engine, unpark/park them with engine PM, queue irq work from interrupt context through `intel_engine_signal_breadcrumbs()`, and enable/cancel request-specific breadcrumbs around waits. Reference management uses `kref`.

## State and Persistence
The header does not own state, but its inlines mutate `b->active`, queue `engine->breadcrumbs->irq_work`, and adjust `b->ref`. The persistent fields are defined in `intel_breadcrumbs_types.h`.

## Dependencies and Integration Points
It depends on Linux atomics and irq_work plus the breadcrumb type definition. It is included by engine PM, request wait, interrupt, and debug code.

## Risks and Edge Cases
`intel_breadcrumbs_park()` calls the heavy park path only when the active count reaches zero, so active reference imbalance can leave IRQs armed or prematurely disarm them. `intel_engine_signal_breadcrumbs()` assumes `engine->breadcrumbs` is initialized and safe for IRQ work queueing.

## Test Signals
Build coverage validates prototypes. Runtime signals include balanced park/unpark counts, IRQ work firing from interrupts, reference-counted free after engine cleanup, and request wait wakeups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_breadcrumbs.h -->
