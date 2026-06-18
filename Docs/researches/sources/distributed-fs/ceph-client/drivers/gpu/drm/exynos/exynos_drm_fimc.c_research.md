# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fimc.c

Purpose: this file implements the FIMC IPP backend. FIMC performs memory-to-memory image processing: source DMA read, crop, colorspace/format handling, scaling, rotation/flip, and destination DMA write.

Important structures and APIs: `struct fimc_context` embeds `struct exynos_drm_ipp`, stores the DRM device, DMA-private mapping, current task, MMIO base, lock, clocks, scaler state, alias id, and IRQ. `struct fimc_scaler` stores prescaler and main scaler settings. The IPP callback table `ipp_funcs` points to `fimc_commit()` and `fimc_abort()`. `exynos_drm_check_fimc_device()` filters FIMC instances by DT alias and the `fimc_devs` module parameter.

Control flow: probe filters devices, builds a dynamic `exynos_drm_ipp_formats` table for linear and Samsung tiled formats with id-dependent limits, maps registers, requests IRQ, sets up clocks, enables runtime PM autosuspend, and adds a component. Bind registers DMA and registers the IPP instance with crop, rotate, scale, and convert capabilities. A committed IPP task resumes the device, stores `ctx->task`, programs source format/order/tile mode/size/window/address, programs destination format/rotation/size/address, computes scaler ratios, and starts capture/scaler/DMA. The IRQ clears interrupt state, detects overflow and frame end, resolves the completed buffer id, drops runtime PM, calls `exynos_drm_ipp_task_done()`, dequeues the destination buffer, and stops hardware. Abort resets hardware and completes the active task with `-EIO`.

State and persistence: mutable state includes `ctx->task`, scaler configuration, IRQ mask state, buffer sequence register state, runtime PM usage, and clock handles. No persistence beyond runtime kernel state exists.

Dependencies and integration points: depends on the Exynos IPP core, Exynos DMA registration, DRM fourcc/modifier definitions, FIMC register definitions in `regs-fimc.h`, clocks from the FIMC device and parent, component framework, and runtime PM. Userspace reaches it through IPP IOCTLs in the top-level driver.

Risks: programming order is hardware-sensitive; source/destination format, rotation, size, address, scaler, then start must remain consistent. Buffer sequencing and IRQ masking are protected by `ctx->lock`, but `ctx->task` itself is manipulated from commit, IRQ, and abort paths. Overflow returns `IRQ_NONE`, so task completion after overflow depends on later state. Clocks include parent writeback clocks, making probe fragile to DT clock names. Tiled format support has different limits and modifiers that must match userspace expectations.

Test signals: IPP get caps/limits for every FIMC alias, crop/scale/rotate/convert jobs, tiled NV12/NV21 jobs, abort while active, runtime autosuspend after completion, overflow/error injection, FIMC mask module parameter behavior, and repeated bind/unbind with IOMMU registration.
