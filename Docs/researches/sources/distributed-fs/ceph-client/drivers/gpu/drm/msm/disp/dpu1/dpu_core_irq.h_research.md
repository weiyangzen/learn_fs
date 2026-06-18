# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_core_irq.h

Purpose: this header declares the DPU core interrupt API used by the MSM KMS integration and DPU submodules. It exposes lifecycle hooks, IRQ dispatch, status readback, callback registration, and debugfs setup.

Important APIs: `dpu_core_irq_preinstall()` prepares interrupt state before DRM IRQ install; `dpu_core_irq_uninstall()` tears it down. `dpu_core_irq()` is the top-level handler called through the MSM KMS IRQ path. `dpu_core_irq_read()` reads the status for a catalog/`DPU_IRQ_IDX()` interrupt index. `dpu_core_irq_register_callback()` and `dpu_core_irq_unregister_callback()` bind one callback and opaque argument to a specific DPU interrupt index. `dpu_debugfs_core_irq_init()` exposes debugfs state under a parent dentry.

Dependencies: the header includes `dpu_kms.h` and `dpu_hw_interrupts.h`, so callers operate on `struct dpu_kms`, `struct msm_kms`, and hardware interrupt abstractions. Catalog files provide interrupt indices for CTL start, pingpong done, interface underrun/vblank/tear, and writeback done; encoder and CRTC code register/wait on those indices.

State and persistence: the header itself has no state. The implementation likely stores callback arrays and enabled masks in the `dpu_kms`/hardware interrupt layer. Callback lifetime is important because physical encoder and CRTC objects may be enabled/disabled dynamically.

Risks: unregister/register mismatches can leave stale callback pointers reachable from IRQ context. IRQ indices must be validated against catalog bounds. `dpu_core_irq_read()` is used as a timeout fallback in encoder waits, so incorrect read semantics can hide missed interrupts or double-handle events.

Test signals: DRM IRQ install/uninstall during probe/remove, vblank enable/disable, encoder wait timeout paths, pingpong done and CTL start delivery, underrun reporting, writeback completion, debugfs IRQ status, and stress with rapid modeset/suspend/resume.
