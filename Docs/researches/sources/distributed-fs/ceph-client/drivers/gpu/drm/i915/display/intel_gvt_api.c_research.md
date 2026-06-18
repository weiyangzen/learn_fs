# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_gvt_api.c

Purpose: exports a small namespace-scoped display-device API for GVT code to query i915 display MMIO offsets and valid pipe presence without reaching directly into display macros.

Important APIs/types/functions: exported GPL namespace functions are `intel_display_device_pipe_offset()`, `intel_display_device_trans_offset()`, `intel_display_device_cursor_offset()`, `intel_display_device_mmio_base()`, and `intel_display_device_pipe_valid()`.

Control flow: each offset function returns the corresponding `INTEL_DISPLAY_DEVICE_*` or `DISPLAY_MMIO_BASE` macro result. Pipe-valid first bounds-checks `pipe` against `PIPE_A` and `I915_MAX_PIPES`, then checks `DISPLAY_RUNTIME_INFO(display)->pipe_mask`.

State and persistence: no state is mutated. Results reflect persistent runtime display info and platform MMIO layout.

Dependencies and integration: depends on `intel_display_core.h`, display register/layout macros, runtime info, and Linux symbol export namespace `I915_GVT`.

Risks: the API trusts the passed `intel_display *`; invalid callers can still crash. Offset semantics must remain stable for GVT consumers when display register layout macros evolve.

Test signals: module/link tests for `I915_GVT` namespace consumers, pipe-mask validation on platforms with fewer than max pipes, and offset comparisons against direct macro expectations.
