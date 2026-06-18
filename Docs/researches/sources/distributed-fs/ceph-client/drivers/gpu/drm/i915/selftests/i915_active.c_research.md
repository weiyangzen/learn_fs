# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_active.c

Purpose: Provides live selftests and debug helpers for `i915_active`, validating request tracking, retirement callbacks, barriers, and wait/flush behavior.

Important APIs/functions: `i915_active_live_selftests()`, `i915_active_print()`, and `i915_active_unlock_wait()`. Test cases include `live_active_wait()`, `live_active_retire()`, and `live_active_barrier()`.

Control flow: Tests allocate a `live_active` wrapper with active/retire callbacks, create kernel requests on all UABI engines, hold submission behind a software fence, add requests to `i915_active`, then release and check counts/retirement. Wait test explicitly waits active idle; retire test uses `igt_flush_test()`; barrier test preallocates/acquires engine barriers and waits retirement. Unlock wait flushes signaled active fences and waits for callback/work completion.

State/persistence: `live_active` stores `i915_active`, kref, and retired flag. Active callbacks take/drop refs so the object survives until retirement. `i915_active_print()` walks the active tree and preallocated barriers for diagnostics.

Dependencies/integration: Uses GT engines, request creation, software fences, `igt_flush_test`, active fence internals, DMA fence callback lists, and DRM printers.

Risks: Tests depend on all UABI engines making progress; wedged GT skips tests. Direct manipulation of active fence slots in `active_flush()` assumes signaled fences and internal structure invariants. Barrier detection uses memory barriers to avoid racing with active-barrier updates.

Test signals: Selftest failures print missing retirement, incorrect active counts, active tree/barrier details, and flush errors.
