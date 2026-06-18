# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_gmu.h

## Purpose

`a6xx_gmu.h` defines the public GMU data model and low-level MMIO helpers used by the A6xx/A7xx/A8xx Adreno driver. It describes GMU BOs, bandwidth-manager metadata, boot and idle-state constants, the `struct a6xx_gmu` state container, register access wrappers, OOB request IDs, and function prototypes shared with GPU, HFI, preemption, and crash-state code.

## Important APIs, Types, And Functions

- `struct a6xx_gmu_bo` stores a GMU-visible GEM object, CPU virtual mapping, size, and IOVA.
- `struct a6xx_bcm` describes a Bus Clock Manager used to construct RPMh DDR interconnect votes.
- `struct a6xx_gmu` is the central persistent object embedded in `struct a6xx_gpu`.
- `GMU_WARM_BOOT` and `GMU_COLD_BOOT` identify firmware boot mode.
- `GMU_IDLE_STATE_ACTIVE`, `GMU_IDLE_STATE_SPTP`, and `GMU_IDLE_STATE_IFPC` define how much low-power control firmware owns.
- `gmu_read()`, `gmu_write()`, `gmu_write_bulk()`, `gmu_rmw()`, `gmu_read64()`, `gmu_poll_timeout()`, and RSCC variants abstract register offsets based on the GPU register base.
- `enum a6xx_gmu_oob_state` names direct CPU-to-GMU requests: boot/slumber, GPU critical-section, DCVS, and perfcounter.
- Exported prototypes cover HFI init/start/stop/frequency, GX/SPTP status, SPTPRAC control, GMU resume/stop/init/remove, OOB operations, sysprof setup, and GMU wait-idle.

## Control Flow

The header is not executable control flow, but it encodes the contracts the C files follow. GMU users obtain a pointer from `to_a6xx_gpu(adreno_gpu)->gmu`, serialize state-changing firmware communication with `gmu->lock`, access registers through helpers that subtract `mmio_offset`, and select OOB request/ack/clear bits in `a6xx_gmu.c` from `enum a6xx_gmu_oob_state`. The HFI code owns queue contents but stores queue descriptors inside `gmu->queues`. Crash-state code reads `gmu->initialized`, `gmu->log`, `gmu->hfi`, `gmu->debug`, and register helpers to snapshot state safely.

## State And Persistence Behavior

`struct a6xx_gmu` persists across runtime PM cycles and stores device/locking state, MMIO/RSCC mapping, IRQs and power domains, firmware and diagnostic BOs, clocks, frequency and bandwidth tables, RPMh votes, HFI queues, QMP/AOSS state, and status bits. The `status` bit definitions are persistent software bookkeeping, not hardware registers. They coordinate PDC sleep, firmware startup, sysprof OOB, and one-time secure initialization.

## Dependencies And Integration Points

The header includes Linux completion, polling, interrupt, notifier, and QMP types, plus msm DRM, Adreno GPU, and A6xx HFI headers. It exposes GMU helpers to `a6xx_gmu.c`, `a6xx_gpu.c`, `a6xx_gpu_state.c`, and A8xx-related code. Register constants come from XML-generated headers included by implementation files, so helper callers pass dword register offsets rather than byte offsets.

## Risks And Edge Cases

- `GMU_BYTE_OFFSET()` assumes the caller passes GPU-base dword offsets and that `mmio_offset` was derived correctly from platform resources. Incorrect resource layout causes silent wrong MMIO access.
- `gmu_write_bulk()` receives `size` in bytes but writes to an IO pointer computed from dword register offset; callers must pass firmware block sizes correctly and maintain alignment.
- `gmu_poll_timeout*` macros directly evaluate conditions on MMIO reads; callers must choose atomic versus sleepable variants based on IRQ/runtime context.
- `struct a6xx_gmu` combines wrapper, legacy, full GMU, A7xx, and A8xx state. Code must check `initialized`, `legacy`, `adreno_has_gmu_wrapper()`, and `adreno_has_rgmu()` before assuming HFI/firmware buffers exist.
- OOB enum values are ABI-like inside the driver. Reordering without updating the bit table in `a6xx_gmu.c` would break firmware handshakes.

## Test Signals

Header-level issues surface as build failures, sparse/type warnings, bad MMIO offsets, OOB timeout logs, crash-state NULL dereferences, or runtime PM imbalance. Useful checks include building with `CONFIG_DRM_MSM_GPU_STATE`, booting wrapper and full-GMU targets, reading GMU state after suspend/resume, and exercising sysprof/perfcounter paths that require the `GMU_STATUS_OOB_PERF_SET` bit.
