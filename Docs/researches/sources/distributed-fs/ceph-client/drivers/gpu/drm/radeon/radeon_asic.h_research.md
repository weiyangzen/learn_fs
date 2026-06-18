# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_asic.h

## Purpose

`radeon_asic.h` is the declaration hub for generation-specific Radeon ASIC code. It exposes the callback implementations that `radeon_asic.c` installs into `struct radeon_asic`, plus helper structures used to save display/memory-controller state around reset or modeset operations. It is the compile-time contract between common Radeon code and per-generation implementation files.

The header spans legacy R100/R200/R300/R400, integrated RS chipsets, R600/R700, Evergreen/Northern Islands, SI, CIK/Kaveri-era ASICs, and UVD/VCE media blocks.

## Important APIs, Types, And Declarations

The common section declares clock and backlight helpers for legacy and AtomBIOS paths: engine/memory clock getters and setters, clock-gating hooks, and panel backlight accessors.

Small save-state structures include `struct r100_mc_save`, `struct rv515_mc_save`, and `struct evergreen_mc_save`, each capturing register or CRTC state needed while stopping and resuming memory-controller/display access.

Generation sections declare lifecycle functions (`*_init`, `*_fini`, `*_suspend`, `*_resume`), reset functions, command processor and ring operations, IRQ handlers, GART and VM helpers, display bandwidth/vblank/wait/page-flip callbacks, HPD callbacks, copy paths, surface register management, PLL/MC/PCIe register accessors, safe-register setup, microcode initialization, and debugfs hooks. R600 and newer declarations add DMA rings, interrupt-handler rings, audio/HDMI helpers, clock counters, temperatures, UVD clocks, and DPM entry points.

Later sections declare Cayman/SI/CIK VM operations, IB parsers, multi-ring pointer accessors, SDMA helpers, compute-ring accessors, DPM/fan-control APIs, powergate hooks, and media block declarations for UVD v1.0/v2.2/v3.1/v4.2 and VCE v1.0/v2.0.

## Control Flow

The header has no executable control flow, but its organization mirrors the driver's runtime flow. Common initialization selects a family in `radeon_asic_init()`, then later generic code calls through `rdev->asic` into the declared functions for hardware bring-up, ring startup, memory management, display updates, interrupts, power management, and teardown.

Reset and suspend/resume flows use the declared save-state structures and lifecycle functions. Command submission flows call the declared CS parsers, IB parsers, ring tests, IB execution helpers, fence emitters, semaphore emitters, and lockup detectors. VM and GART flows use the declared page-entry, TLB flush, page-table write/copy/set, and VM flush functions.

## State And Persistence Behavior

The header itself stores no state. It defines the shape of state transitions performed by implementation files: memory-controller save/restore structures, ring read/write pointer accessors, fence and semaphore emission, GART/VM page table updates, IRQ enable/process state, DPM power-state transitions, fan modes, clock settings, and media firmware lifecycle.

The declarations show which state is per-device (`struct radeon_device *rdev` appears almost everywhere), per-ring (`struct radeon_ring *ring`), per-fence, per-IB, per-encoder, or per-power-state. Many APIs return status codes that determine whether init, resume, DPM, ring tests, or parsing may continue.

## Dependencies And Integration Points

This header assumes prior visibility of core Radeon types such as `struct radeon_device`, `struct radeon_ring`, `struct radeon_ib`, `struct radeon_fence`, `struct radeon_semaphore`, `struct radeon_cs_parser`, `struct radeon_bo`, `struct radeon_encoder`, `struct radeon_mc`, `struct radeon_ps`, `enum radeon_hpd_id`, and `enum radeon_dpm_forced_level`. It also references DRM types including `struct drm_display_mode`, `struct drm_encoder`, `struct dma_resv`, and `struct seq_file`.

It integrates per-generation `.c` files with `radeon_asic.c` and generic Radeon subsystems. Build correctness depends on Kconfig and object selection matching every declaration used by the selected ASIC tables. Runtime correctness depends on these prototypes matching actual implementations exactly, because the function pointers are used across many subsystems.

## Risks And Edge Cases

The largest risk is contract drift: a prototype mismatch, missing implementation under some Kconfig combination, or callback table using a function with subtly different semantics can break builds or hardware initialization. Because many functions perform MMIO, DMA, page-table writes, IRQ processing, or power transitions, the cost of incorrect wiring is high.

The header also exposes historical overlap between generations. Some callbacks are reused across families, while others are family-specific despite similar names. That reuse is efficient but risky when a new chip differs in packet format, register layout, VM flush sequence, or power-management requirement.

## Test Signals

Test signals are primarily build and runtime integration coverage: compile all relevant Radeon Kconfig combinations, boot each supported family class, exercise init/fini/suspend/resume/reset, run graphics and DMA ring tests, submit command streams through parsers, stress GART/VM mappings, verify vblank/page-flip/display bandwidth behavior, test HPD and backlight, run UVD/VCE firmware and ring tests where present, and validate DPM/fan/temperature controls. Link errors, unresolved symbols, invalid callback warnings, ring lockups, VM faults, IRQ storms, or missing media/display capabilities indicate header-to-implementation drift.
