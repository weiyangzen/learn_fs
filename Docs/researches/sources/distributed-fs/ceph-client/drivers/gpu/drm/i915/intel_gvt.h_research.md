# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_gvt.h

Purpose: declares the GVT integration interface and provides no-op stubs when GVT is disabled.

Important APIs/types: under `CONFIG_DRM_I915_GVT`, defines `struct intel_gvt_mmio_table_iter`, `struct intel_vgpu_ops`, and declarations for init/remove/resume, host init, MMIO table iteration, and ops registration. Without GVT, inline stubs make init/remove/resume harmless and MMIO iteration return success.

Control flow: i915 core code can call GVT hooks unconditionally; compile-time configuration decides whether real backend integration or stubs are used.

State and persistence: no state in the header. Real state is in `intel_gvt.c` globals and `drm_i915_private` vGPU fields.

Dependencies and integration: includes only `linux/types.h` and forward-declares `drm_i915_private`, keeping the boundary narrow between i915 core and optional virtualization.

Risks: stubbed `intel_gvt_iterate_mmio_table()` returns success despite doing nothing, which is correct only when callers are also conditional on GVT context. Interface changes must keep disabled builds compiling.

Test signals: build coverage with GVT enabled and disabled, module namespace export tests, and virtualization init paths.
