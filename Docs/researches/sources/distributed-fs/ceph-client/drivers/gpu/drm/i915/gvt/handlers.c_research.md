# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/handlers.c

## Purpose
`handlers.c` is the central MMIO policy table and special-register emulator for Intel GVT-g vGPUs. It converts the i915 MMIO table into GVT-tracked register metadata, overlays device/platform-specific handlers, and implements guest-visible side effects that cannot be represented by plain virtual-register storage: display, interrupts, forcewake, fences, ring control, PV info, DP AUX/DPCD, power/PLL registers, execlist enablement, reset, and selected command-accessible registers.

## Important APIs, Types, And Functions
Exported entry points include `intel_gvt_get_device_type`, `intel_gvt_render_mmio_to_engine`, `intel_gvt_find_mmio_info`, `intel_gvt_setup_mmio_info`, `intel_gvt_clean_mmio_info`, `intel_gvt_for_each_tracked_mmio`, `intel_vgpu_default_mmio_read`, `intel_vgpu_default_mmio_write`, `intel_vgpu_mask_mmio_write`, `intel_vgpu_mmio_reg_rw`, `intel_gvt_restore_fence`, and `intel_gvt_restore_mmio`. The `MMIO_*` macros are the declarative layer for assigning `struct intel_gvt_mmio_info` handlers and attributes.

## Control Flow
`intel_gvt_setup_mmio_info` allocates MMIO attributes, enumerates the i915 MMIO table, installs the PV info block handler, and layers generic plus platform-specific handlers. Runtime access enters `intel_vgpu_mmio_reg_rw`, checks special blocks, then per-register metadata, enforces read-only and mode-mask behavior, and calls the registered read/write callback or the default vreg path. Key callbacks model hardware side effects for fences, forcewake ACKs, reset, execlist ELSP submission, DP AUX/DPCD, flip events, PV notifications, power wells, PLL locks, and GuC/unsupported paths.

## State And Persistence
Per-vGPU state is stored in `vgpu->mmio.vreg`, PV flags, display/DPCD data, flip-done bitmaps, fence state, HWS page addresses, SBI cache, and submission state. Global state includes the MMIO info hash table, block array, attribute array, and tracked MMIO counts. `F_PM_SAVE` marks registers restored by `intel_gvt_restore_mmio`; fences are restored separately. `enter_failsafe_mode` persists containment state in `vgpu->failsafe`.

## Dependencies And Integration Points
The file integrates i915 display/GT register definitions, GVT GTT and workload submission, interrupt emulation, I2C/DP helpers, PV info, scheduler policy, hardware access wrappers, and uncore register access. `mmio.c` calls this for emulated BAR0 MMIO, and `kvmgt.c` reaches it through VFIO BAR0 accesses.

## Risks
Register semantics are exacting: stale bit definitions or missed side effects can break guest drivers. DP AUX length/offset handling, FORCE_NONPRIV validation, mode-mask writes, read-only masks, and platform-specific PLL/power behavior are high-risk areas. False failsafe entry can disable supported guests, while missed failsafe checks can allow unsupported guest behavior to corrupt emulation state.

## Test Signals
Look for clean GVT initialization without duplicate/non-tracked MMIO warnings; guest PV info probing; execlist workload submission; DP AUX link training; vblank and flip-done delivery; fence/MMIO restore after suspend/resume; and negative coverage for invalid FORCE_NONPRIV, out-of-range fences, malformed AUX lengths, unsupported GuC DMA, and read-only/mode-mask writes.
