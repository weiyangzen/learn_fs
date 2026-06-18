# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_v3d.c

Purpose: Binds and manages the gen4 V3D hardware block for VC4: MMIO/debugfs exposure, runtime power management, IRQ install, hardware init, and shared binner memory allocation used by binning command lists.

Important APIs/types/functions: `v3d_regs[]` defines debugfs register dumps. `vc4_v3d_debugfs_ident()` reports V3D revision/slices/TMUs/QPUs/semaphores. `vc4_v3d_pm_get()`/`put()` wrap runtime PM with `vc4->power_refcount`. `vc4_v3d_get_bin_slot()` allocates a 512 KiB binner slot or waits for render completion. `bin_bo_alloc()`, `vc4_v3d_bin_bo_get()`, `bin_bo_release()`, and `vc4_v3d_bin_bo_put()` manage a 16 MiB bin BO. Runtime PM callbacks enable/disable clocks and IRQs. `vc4_v3d_bind()`/`unbind()` integrate with the component framework.

Control flow: Bind allocates `vc4_v3d`, maps registers, obtains clock/IRQ, enables runtime PM, checks `V3D_IDENT0`, clears old binner overflow registers, installs IRQs, sets autosuspend, and stores `vc4->v3d`. Binner allocation loops until it gets a 16 MiB BO that does not cross a 256 MiB high-nibble boundary, then initializes slot allocator state and enables OOM interrupts. Slot allocation is guarded by `job_lock`, waits on last render seqno when full, and returns a bit index.

State and persistence: Device state includes `vc4->v3d`, `vc4->irq`, `power_refcount`, `bin_bo`, `bin_bo_kref`, `bin_alloc_size`, `bin_alloc_used`, and `bin_alloc_overflow`. The binner BO persists while referenced by jobs and is released by kref. Runtime PM state persists in the platform device.

Dependencies and integration points: Uses platform/component framework, runtime PM, clocks, VC4 IRQ helpers, BO allocator, render job wait/seqno helpers, debugfs, and V3D registers from `vc4_regs.h`. Validation allocates bin slots through `vc4_v3d_get_bin_slot()`, and submit paths require PM refs.

Risks: Binner memory addressing workaround is critical; a BO crossing the 256 MiB boundary can cause bad DMA addressing. Power refcount imbalance can leave V3D powered or suspend while in use. Slot exhaustion waits on render completion and must handle signals. Bind failure paths must drop runtime PM refs. All paths reject gen>4.

Test signals: Probe tests should verify IDENT0 mismatch failure, IRQ install/uninstall, runtime suspend/resume clock behavior, debugfs output, binner BO allocation under fragmented DMA memory, slot allocation/reuse after job completion, and no stale BPOA/BPOS across unbind/rebind.
