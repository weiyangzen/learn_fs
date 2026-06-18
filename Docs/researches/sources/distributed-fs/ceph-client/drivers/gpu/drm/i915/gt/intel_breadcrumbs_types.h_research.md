<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_breadcrumbs_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_breadcrumbs_types.h

## Purpose
`intel_breadcrumbs_types.h` defines `struct intel_breadcrumbs`, the shared state container for i915 request breadcrumb signaling and IRQ management.

## Important APIs, Types, and Functions
The central type is `struct intel_breadcrumbs`. Important fields are `ref`, `active`, `signalers_lock`, `signalers`, `signaled_requests`, `signaler_active`, `irq_lock`, `irq_work`, `irq_enabled`, `irq_armed`, `engine_mask`, `irq_engine`, and IRQ enable/disable function pointers.

## Control Flow
The comments document the design: instead of waking every waiter on every interrupt, the implementation wakes/uses a first client to perform coherent seqno checks, then cascades wakeups for completed clients and transfers bottom-half responsibility through the signaler queue.

## State and Persistence
All fields are runtime state. Lists persist request/context wait state until completion/cancel, `irq_armed` persists a GT PM wakeref while interrupts are expected, and `irq_enabled` tracks hardware interrupt enable nesting.

## Dependencies and Integration Points
The type depends on irq_work, kref, list/llist, spinlocks, engine type definitions, engine masks, and wakeref tokens. It is consumed by `intel_breadcrumbs.c`, engine PM, engine interrupt signaling, and debug paths.

## Risks and Edge Cases
The lock partition is important: `signalers_lock` protects signaler list modifications, `irq_lock` protects hardirq-sensitive interrupt state, and `signaler_active` gates context teardown waiting for RCU walkers. Misusing these fields can race interrupt disarm with waiter insertion or free a context while it is being walked.

## Test Signals
Test signals include lockdep, RCU debug, request wait stress, park/free assertions, interrupt enable/disable balance, and contexts with ordered signal lists under heavy completion races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_breadcrumbs_types.h -->
