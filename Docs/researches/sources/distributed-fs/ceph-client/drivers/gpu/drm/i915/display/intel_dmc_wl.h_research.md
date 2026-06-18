# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dmc_wl.h

### Purpose
`intel_dmc_wl.h` declares the DMC wakelock state container and public API used by display code to protect MMIO accesses while low-power DC states may have powered down register blocks.

### Important APIs, Types, And Functions
`struct intel_dmc_wl` contains a spinlock, `enabled` flag, `taken` flag, `refcount_t`, cached `dc_state`, and delayed work item. The declared functions cover init, enable, disable, release-work flush, register-scoped get/put, and no-register get/put variants.

### Control Flow
The header has no executable logic, but it establishes the lifecycle expected by callers: initialize during display setup, enable when dynamic DC states are enabled, wrap relevant MMIO operations with get/put, flush release work before teardown or state transitions, and disable when DC states are disabled.

### State, Persistence, And Dependencies
The wakelock state persists inside `struct intel_display` via this struct. The lock comment states that the spinlock protects `enabled`, `taken`, `dc_state`, and `refcount`; the cached DC state avoids taking the display power-domain mutex in atomic MMIO contexts. Dependencies include Linux types, workqueue, refcount, spinlock availability through included kernel headers, `i915_reg_t`, and `struct intel_display`.

### Integration Points
This header is consumed by DMC wakelock implementation and display register access sites that need to acquire/release the DMC wakelock. It links the low-level register identifier type `i915_reg_t` with the display-wide state in `struct intel_display`.

### Risks
Correctness depends on callers balancing get/put calls and using the register-scoped variant whenever range filtering matters. The cached `dc_state` must be updated exactly when DC state policy changes, otherwise range checks can be too narrow or too broad. Because this can be called in atomic context, future API changes must preserve non-sleeping behavior.

### Test Signals
Header-level signals are build coverage for all call sites and lockdep-friendly use from atomic paths. Runtime tests should verify balanced get/put behavior, register and no-register variants, flush during teardown, and correct behavior when DC state changes.
