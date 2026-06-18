# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_rotator.c

## Purpose
This file implements the Exynos rotator IPP backend. The hardware reads a source DMA buffer, applies crop, rotation, and reflection, writes a destination DMA buffer, and signals completion through an interrupt. The driver registers the hardware as a DRM Exynos IPP processor with crop and rotate capabilities.

## Important APIs, Types, and Functions
The key driver objects are `struct rot_context`, which stores the IPP object, DRM device, DMA registration cookie, MMIO base, clock, format table, and currently active IPP task, and `struct rot_variant`, which selects supported formats and limits by compatible string.

Important functions are `rotator_probe()`, `rotator_bind()`, `rotator_unbind()`, `rotator_commit()`, `rotator_irq_handler()`, `rotator_runtime_suspend()`, and `rotator_runtime_resume()`. Register helpers include `rotator_reg_set_irq()`, `rotator_reg_get_irq_status()`, `rotator_src_set_fmt()`, `rotator_src_set_buf()`, `rotator_dst_set_transf()`, `rotator_dst_set_buf()`, and `rotator_start()`. Format/limit tables describe XRGB8888 and NV12 limits for S5PV210, Exynos4210, Exynos4212/4412, and Exynos5250.

## Control Flow
Probe allocates context, selects variant data from device tree, maps registers, requests IRQ, gets the `rotator` clock, enables runtime PM autosuspend, and registers as a component. Bind attaches to the DRM device, registers the device for DMA mapping, and calls `exynos_drm_ipp_register()` with crop and rotate capabilities. An IPP task enters through `rotator_commit()`: runtime PM resumes the device, the current task pointer is stored, source format/crop/DMA registers are programmed, transform bits are written, destination registers are programmed, IRQ is enabled, and the start bit is set. The IRQ handler reads status, clears the pending bit, drops runtime PM with autosuspend, and calls `exynos_drm_ipp_task_done()` with success only for complete status.

## State and Persistence Behavior
The only live task state is `rot->task`, which is cleared in the interrupt handler. Runtime PM keeps the hardware clock on only while a task is running and for the autosuspend delay afterward. Register state is rewritten for every commit, so no per-job state persists in hardware beyond an active operation. Format limits are static data tied to the device compatible string.

## Dependencies and Integration Points
The driver depends on the Exynos DRM IPP framework, component framework, runtime PM, DMA registration helpers, MMIO register definitions in `regs-rotator.h`, and device-tree compatibles for the supported SoCs. It integrates with user-visible Exynos IPP operations through `DRM_EXYNOS_IPP_CAP_CROP` and `DRM_EXYNOS_IPP_CAP_ROTATE`.

## Risks
`rotator_commit()` assumes the IPP framework serializes tasks because there is only one `rot->task` pointer and no local queueing. If a reset or illegal-status interrupt is lost, runtime PM and task completion can hang. Only NV12 and XRGB8888 are mapped in `rotator_src_set_fmt()`, so adding formats requires both register mapping and limit updates. The file contains a duplicate unreachable `return 0;` in `rotator_bind()`, which is harmless but signals low cleanup coverage. DMA addresses are written as 32-bit register values, so platform DMA mask and buffer placement must match hardware addressing.

## Test Signals
Test with IPP crop-only, rotate 90/180/270, reflect X/Y, combined rotate plus reflect, XRGB8888 and NV12 formats, SoC-specific minimum/maximum/alignment limits, illegal parameter rejection, IRQ completion, autosuspend/resume cycles, component unbind, and fault injection for missing IRQ or clock acquisition errors.
