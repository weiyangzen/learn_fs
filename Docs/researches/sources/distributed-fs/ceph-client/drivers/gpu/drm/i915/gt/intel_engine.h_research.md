<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine.h

## Purpose
`intel_engine.h` is the main public façade for i915 engine objects. It defines engine MMIO access macros, engine masks, status-page layout, execlist helpers, and prototypes/inlines for engine initialization, cleanup, IRQ, reset, idle, diagnostics, virtual engines, heartbeat/property clamping, and pinned contexts.

## Important APIs, Types, and Functions
Important macros include `ENGINE_READ*`, `ENGINE_WRITE*`, engine class masks, `I915_GEM_HWS_*` status-page offsets, `execlists_num_ports()`, `execlists_active()`, `intel_read_status_page()`, and `intel_write_status_page()`. Declared functions include engine init/free/release, common setup/cleanup, resume, ring submission setup, stop/cancel CS, pending MI forcewake wait, active head/batch head reads, instdone capture, IRQ enable/disable, idle checks, dump helpers, busy-time retrieval, hung-entity lookup, context-size calculation, pinned context creation/destruction, CCS enablement, property clamping, and virtual/parallel engine creation.

## Control Flow
The header provides fast-path inlines for reading/writing engine-relative registers through `intel_uncore`, checking GuC/virtual/heartbeat capabilities, getting virtual siblings, and setting/clearing hung context pointers. `execlists_active()` uses repeated READ_ONCE and memory barriers to read a stable active request pointer.

## State and Persistence
No state is owned by the header, but it defines persistent hardware status-page offsets used for preemption, seqno, migration, GGTT bind, PXP, GSC, and scratch values. The write helper flushes status-page cachelines before and after stores to make HW-visible writes robust.

## Dependencies and Integration Points
The header depends on PMU/request/selftest, engine/GT/timeline/workaround types, uncore register helpers, and GuC virtual-engine helpers. It is included across GT code and is the API boundary for engine lifecycle, command submission, debugging, PM, heartbeat, and reset flows.

## Risks and Edge Cases
Register macros assume register definitions accept an engine base parameter. Status-page offsets are ABI-like within the driver and must remain aligned with command emission code. Virtual engine heartbeat is only valid with GuC submission. Inline state helpers such as hung context pointer setters have no locking, so callers must provide the correct synchronization.

## Test Signals
Build coverage catches macro/prototype drift. Runtime signals include engine init on all platform engine masks, MMIO register dump correctness, HWSP seqno/preempt paths, virtual engine creation, heartbeat capability checks, and reset/hung-context capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine.h -->
