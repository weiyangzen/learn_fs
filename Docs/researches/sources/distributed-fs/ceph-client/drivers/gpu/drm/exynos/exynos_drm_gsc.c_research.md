# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_gsc.c

Purpose: this file implements the GSCaler IPP backend. GSC is another memory-to-memory image processor supporting format conversion, crop, scale, rotation/flip, tiled formats, and DMA in/out.

Important structures and APIs: `struct gsc_context` embeds an IPP object and stores DRM/DMA state, current task, register base, clock array, scaler state, id, IRQ, and rotation flag. `struct gsc_scaler` tracks prescaler and main-scaler ratios. `struct gsc_driverdata` provides per-compatible clock names and IPP limits. The IPP backend callbacks are `gsc_commit()` and `gsc_abort()`.

Control flow: probe selects driver data, builds linear and tiled format tables with SoC-specific limits, acquires clocks, maps registers, requests IRQ, enables runtime PM autosuspend, and registers the component. Bind registers DMA and IPP capabilities. Commit resumes runtime PM, records the task, resets hardware, programs source format/rotation/size/address, destination format/size/address, computes prescaler ratios, loads horizontal and vertical coefficient tables based on scaling ratio, and starts one-shot memory-to-memory processing. IRQ detects overflow and frame-done status, dequeues source and destination buffer indices, marks runtime PM idle, and completes the IPP task with success or error. Abort resets and completes active work with `-EIO`.

State and persistence: state is in `gsc_context`: current task, scaler ratios, rotation flag, clock handles, runtime PM usage, and buffer mask registers. There is no persistent storage.

Dependencies and integration points: depends on IPP core, Exynos DMA mapping, DRM fourcc/modifier definitions, `regs-gsc.h`, platform/property APIs, runtime PM, clocks, and component framework. Userspace reaches it through IPP IOCTLs.

Risks: the file contains large hard-coded coefficient tables; wrong ratio selection can degrade scaling or program invalid coefficients. Reset waits up to `GSC_RESET_TIMEOUT`; failure returns `-EBUSY`. Source/destination buffer mask handling assumes single-buffer index 0 for submitted tasks. Tiled output uses Samsung 16x16 modifiers and must match hardware expectations. Runtime PM put on reset failure happens without `mark_last_busy`, unlike normal completion.

Test signals: caps/limits for exynos5250/5420/5433 compatibles, RGB/YUV/tiled formats, up/down scaling, rotations, crop, overflow/frame-done IRQs, reset timeout injection, abort while active, autosuspend, and clock enable rollback.
