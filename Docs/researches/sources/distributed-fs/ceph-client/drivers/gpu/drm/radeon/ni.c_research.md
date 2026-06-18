# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni.c

## Purpose

`ni.c` is the Northern Islands/Cayman/Terascale-NI ASIC support file for the legacy Radeon DRM driver. It wires the hardware-specific bring-up and teardown path for Cayman-family discrete GPUs and Aruba/TN integrated GPUs: firmware loading, memory controller programming, GART/VM setup, graphics command processor rings, reset/lockup handling, UVD/VCE media rings, suspend/resume, VM fault decoding, and a small VCE clock helper.

Although it lives under a Ceph client source snapshot, the file is Linux DRM GPU code and depends on the broader `drivers/gpu/drm/radeon` subsystem.

## Important APIs, Functions, and Data

- `tn_smc_rreg()` / `tn_smc_wreg()` access TN SMC indirect registers under `rdev->smc_idx_lock`.
- `ni_init_microcode()` requests PFP, ME, RLC, MC, and optionally SMC firmware by ASIC family and validates exact firmware sizes before use.
- `ni_mc_load_microcode()` loads MC IO-register presets and MC firmware into MC sequencer RAM for GDDR5 discrete parts when the MC is not running.
- `cayman_gpu_init()` programs chip configuration, tiling, backend map, shader/resource defaults, cache controls, and selected TN clock-gating defaults.
- `cayman_pcie_gart_enable()`, `cayman_pcie_gart_disable()`, and `cayman_pcie_gart_tlb_flush()` configure VM context 0 for the PCIE GART and contexts 1-7 for GPU VM use.
- `cayman_fence_ring_emit()`, `cayman_ring_ib_execute()`, `cayman_cp_resume()`, and pointer helpers implement the graphics CP ring programming model.
- `cayman_gpu_check_soft_reset()`, `cayman_gpu_soft_reset()`, `cayman_asic_reset()`, and `cayman_gfx_is_lockup()` provide status-driven reset and lockup classification.
- `cayman_startup()`, `cayman_resume()`, `cayman_suspend()`, `cayman_init()`, and `cayman_fini()` are the high-level lifecycle functions used by the Radeon ASIC dispatch table.
- `cayman_vm_init()`, `cayman_vm_decode_fault()`, and `cayman_vm_flush()` provide NI VM integration.
- `tn_set_vce_clocks()` adjusts TN VCE engine clock dividers through AtomBIOS clock-divider calculation and CG ECLK registers.

The file also contains large static register data sets: TN RLC save/restore lists, Cayman/Aruba golden registers, and per-family MC IO initialization tables.

## Control Flow

Initialization begins in `cayman_init()`. It reads and validates ATOM BIOS, posts the GPU when needed, initializes ATOMBIOS, golden registers, scratch/surface state, clocks, fences, memory controller, BO manager, firmware, and power management. It then initializes GFX, DMA, UVD/VCE, interrupt, and GART ring objects before entering `cayman_startup()`.

`cayman_startup()` is the active hardware bring-up sequence. It enables PCIe gen2/ASPM, initializes scratch VRAM, programs MC, optionally loads MC firmware when DPM is not already handling it, enables the PCIE GART, programs GPU registers, initializes TN RLC buffers for IGPs, starts writeback and fence rings, starts UVD/VCE, initializes interrupts, initializes GFX/DMA ring buffers, loads CP firmware, resumes CP and DMA engines, resumes media engines, initializes the IB pool and VM manager, and finally initializes audio. Most steps fail fast with a propagated error.

The graphics CP path halts CP before loading PFP/ME firmware, programs ring base/read/write-pointer registers for three CP rings, starts only the primary GFX ring, writes clear-state packets, tests the ring, and marks CP1/CP2 not ready. IB execution emits mode-control and indirect-buffer packets and performs a cache sync for the VMID.

Reset handling first derives a reset mask from GRBM, SRBM, DMA, VM L2, display, and MC status. Soft reset halts CP, disables DMA ring buffers if needed, stops the memory controller, asserts GRBM/SRBM reset bits by engine class, resumes MC, and prints status before and after. If soft reset does not clear the mask, `cayman_asic_reset()` falls back to PCI config reset.

Suspend reverses runtime resources: PM suspend, audio/VM manager shutdown, CP/DMA stop, UVD shutdown, IRQ suspend, writeback disable, and GART disable. Final teardown extends this with ring/resource frees, firmware-adjacent subsystems, GEM, fences, BO, ATOMBIOS, and BIOS memory.

## State and Persistence Behavior

The file mutates persistent driver state in `struct radeon_device`: firmware pointers, `rdev->config.cayman`, ring readiness and pointers, `rdev->gart.ready`, VM manager context table addresses, `rdev->accel_working`, media capability flags, and BIOS/PM initialization state. Hardware state is mostly MMIO register programming through `RREG32`/`WREG32`; GART table state is persisted in VRAM and context page-table base addresses are saved on GART disable for contexts 1-7.

Firmware objects are requested from the kernel firmware loader and retained in `rdev` until later driver cleanup. Ring buffers, writeback, GART tables, dummy page, and IB/VM manager state are allocated by shared Radeon helpers and must remain coherent across suspend/resume.

## Dependencies and Integration Points

`ni.c` depends on common Radeon subsystems: ATOMBIOS parsing/programming, memory controller helpers from Evergreen/R600, BO/TTM memory management, ring/fence/IB infrastructure, IRQ/IH, UVD/VCE/audio helpers, DPM/PM, VM manager, and firmware size constants from `radeon_ucode.h`. It includes `ni.h`, `ni_reg.h`, `nid.h`, `evergreen.h`, `radeon_asic.h`, and firmware/state blobs such as `clearstate_cayman.h`.

The file integrates with `ni_dma.c` through calls to `cayman_dma_resume()`, `cayman_dma_stop()`, and `cayman_dma_fini()`, and with `ni_dpm.c` because DPM may load MC firmware and controls clocks/power around the same hardware.

## Risks and Edge Cases

- Firmware size validation is strict; missing or wrong firmware disables acceleration or returns `-EINVAL`.
- MC firmware is mandatory for discrete NI after initialization, but TN/IGP skips MC firmware. Mistakes in this distinction can break bring-up.
- Register programming order is critical. GART, MC, CP firmware, ring base writes, and writeback setup have hardware sequencing constraints.
- `cayman_pcie_gart_disable()` saves VM context base addresses before disabling; losing this state can break VM restoration.
- Reset code deliberately clears MC from the reset mask because MC is usually busy rather than hung; real MC failures may require fallback reset.
- CP1/CP2 rings are configured but marked not ready in this driver path, so callers must respect ring readiness.
- UVD/VCE failures disable or zero ring sizes to avoid later resume attempts against missing BOs.
- `tn_set_vce_clocks()` currently uses only `ecclk` for dividers and waits on `CG_ECLK_STATUS`; timeout behavior is important on broken firmware/hardware.

## Test Signals

Useful validation includes firmware load logs, `dmesg` absence of bogus firmware length errors, successful `radeon_ring_test()` for GFX and DMA rings, GART enable log with expected GTT size/table address, working suspend/resume, clean UVD/VCE ring initialization when hardware supports them, VM fault decode logs that identify expected blocks, and reset paths that clear `cayman_gpu_check_soft_reset()` masks. IGT/KMS modeset tests, OpenGL command submission, GPU VM workloads, DMA copy tests, and forced GPU reset tests exercise the main paths.
