<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context_types.h

## Purpose
`intel_context_types.h` defines the core `struct intel_context` data model and backend `struct intel_context_ops` used by i915 submission engines.

## Important APIs, Types, and Functions
`struct intel_context_ops` defines backend hooks for allocation, pinning, unpinning, request cancellation, enter/exit, stats update, reset, destroy, virtual engine creation, parallel context creation, and sibling lookup. `struct intel_context` contains references, engine/inflight pointers, VM, GEM context pointer, breadcrumb signal lists, context state VMA, ring, timeline, wakeref, flags, LRC state/descriptor/tag, stats, active/pin tracking, ops pointer, SSEU, pinned context list link, workaround batch page, GuC state, GuC ID, destroyed link, parallel submission metadata, and selftest fault-injection flags.

## Control Flow
This header has no runtime control flow, but its fields drive the lifecycle implemented in `intel_context.c`, breadcrumb signaling in `intel_breadcrumbs.c`, GuC submission, LRC setup, and parallel submission. Bit definitions under `flags` encode context state transitions such as allocated, valid, closed, banned, nopreempt, GuC initialized, perma-pinned, parking, exiting, low-latency, and own-state.

## State and Persistence
The structure is the persistent in-memory representation of a GPU context. It owns/holds references to GPU-visible state objects, scheduling state, active and pin counters, runtime accounting, and submission metadata for both execlists and GuC paths.

## Dependencies and Integration Points
The header depends on active tracking, software fences, engine types, SSEU, wakerefs, and GuC firmware ABI definitions. It is the shared contract between engine setup, context lifecycle code, scheduler backends, breadcrumbs, PM, hang recovery, and selftests.

## Risks and Edge Cases
Several fields are accessed under RCU or special locks, so readers must honor the documented protection. `inflight` encodes a pointer plus low-bit count, making alignment assumptions important. Parent/child parallel pointers are immutable after creation but not fully refcounted in both directions. GuC state has its own lock and must not be mixed with timeline or pin locks incorrectly.

## Test Signals
Signals include lockdep/RCU debug, context lifecycle selftests, GuC scheduling tests, parallel submission tests, breadcrumb wait tests, runtime stats validation, and fault-injection paths for dropped GuC messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context_types.h -->
