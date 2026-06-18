# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dmc_wl.c

### Purpose
`intel_dmc_wl.c` implements DMC wakelock support. On platforms where display registers may be powered down in DC states, it explicitly asks DMC to exit the DC state before selected MMIO accesses and releases that request after a short hold time.

### Important APIs, Types, And Functions
The implementation uses `struct intel_dmc_wl` from the header, local `struct intel_dmc_wl_range`, and the module parameter value in `display->params.enable_dmc_wl`. Public functions are `intel_dmc_wl_init()`, `intel_dmc_wl_enable()`, `intel_dmc_wl_disable()`, `intel_dmc_wl_flush_release_work()`, `intel_dmc_wl_get()`, `intel_dmc_wl_put()`, `intel_dmc_wl_get_noreg()`, and `intel_dmc_wl_put_noreg()`. Important internal helpers are `intel_dmc_wl_sanitize_param()`, `__intel_dmc_wl_supported()`, `intel_dmc_wl_check_range()`, `intel_dmc_wl_reg_in_range()`, `__intel_dmc_wl_take()`, `__intel_dmc_wl_release()`, and delayed work callback `intel_dmc_wl_work()`.

### Control Flow
Initialization sanitizes the enable parameter: unsupported hardware is forced disabled, negative/default values enable wakelock only on display version 30+, out-of-range values are clamped to enabled, and always-locked mode seeds the refcount to one. Enabling dynamic DC states records the active DC state, writes `DMC_WAKELOCK_CFG_ENABLE`, marks the software state enabled, and takes the hardware lock immediately if references already exist. Disabling flushes pending release work, clears the config enable bit, clears the request bit, marks the lock not taken, and tolerates existing software users.

`intel_dmc_wl_get()` first filters by register range unless the mode is "any register" or the caller used the no-register variant. If the wakelock is not currently enabled, it only increments the refcount so a later enable can take it. If enabled, it cancels pending release work, increments or initializes the refcount, and when transitioning from zero calls `__intel_dmc_wl_take()` to set `DMC_WAKELOCK_CTL_REQ` and wait atomically for `DMC_WAKELOCK_CTL_ACK`. `intel_dmc_wl_put()` applies the same range filter, warns on underflow, decrements the refcount, and when it reaches zero queues delayed release work. The release worker clears the request bit and waits for ACK to clear, unless a new reference arrived first.

### State, Persistence, And Dependencies
Software state lives in `display->wl`: spinlock, `enabled`, `taken`, `refcount`, cached `dc_state`, and delayed release work. The spinlock protects all mutable state and allows use from atomic MMIO paths. Hardware state is `DMC_WAKELOCK_CFG` and `DMC_WAKELOCK1_CTL`. The 50 ms hold time avoids immediate churn after the last user drops the wakelock, and the 5000 us timeout bounds atomic waits. Dependencies include `intel_de` firmware MMIO accessors, DC state/register definitions, DRM warnings, Linux delayed work, spinlocks, and refcount APIs.

### Integration Points
This file integrates with the display MMIO access path through get/put calls around register programming, with dynamic DC state enable/disable, and with DMC register definitions from `intel_dmc_regs.h`. The range tables encode platform knowledge for powered-off registers and registers touched by DMC in DC3CO/DC5/DC6 modes.

### Risks
The code documents a possible race when wakelock is enabled while an existing user is between get and the protected MMIO; resolving it depends on hardware guidance. Range tables are manual and platform-specific, so missing a register can leave accesses unprotected in DC states, while broad matching hurts power/performance. Timeout warnings mean the display may not have exited or re-entered DC state as expected. Disable semantics with outstanding users are not fully specified by hardware. Always-locked mode intentionally holds the refcount and changes power behavior.

### Test Signals
Useful signals include parameter sanitization on unsupported and display version 30+ platforms, get/put nesting and underflow warnings, atomic-context register accesses through protected and unprotected ranges, enable with preexisting references, disable with outstanding references, delayed release cancellation/requeue behavior, timeout-free ACK transitions, and power tests showing DC state exit only for intended MMIO ranges.
