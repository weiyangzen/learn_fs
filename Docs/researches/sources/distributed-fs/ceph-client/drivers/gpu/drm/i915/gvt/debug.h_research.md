# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/debug.h

Purpose: centralizes GVT logging macros with consistent prefixes and subsystem tags.

Important APIs/types/functions: defines `gvt_err()`, `gvt_vgpu_err()`, and subsystem debug macros `gvt_dbg_core()`, `gvt_dbg_irq()`, `gvt_dbg_mm()`, `gvt_dbg_mmio()`, `gvt_dbg_dpy()`, `gvt_dbg_el()`, `gvt_dbg_sched()`, `gvt_dbg_render()`, and `gvt_dbg_cmd()`. `gvt_vgpu_err()` prints a vGPU id when a valid `vgpu` variable is in scope, otherwise falls back to a generic GVT prefix.

Control flow and state: no persistent state. The only branching is in `gvt_vgpu_err()`, which checks `IS_ERR_OR_NULL(vgpu)`.

Dependencies and integration points: depends on kernel `pr_err()` and `pr_debug()` plus call-site availability of a `vgpu` symbol for `gvt_vgpu_err()`. It is included broadly by GVT source files to make debug output grepable by subsystem.

Risks and test signals: macro use depends on local variable naming, so using `gvt_vgpu_err()` outside a scope with `vgpu` will fail to compile. Format-string correctness is checked by compiler diagnostics. Runtime signals are correctly prefixed errors and dynamic-debug controllable subsystem messages.
