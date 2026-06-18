# Research: subset-b-003727

Grouped research for Radeon driver ACPI, AGP, and ASIC dispatch files. Each section preserves the original source path for reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_acpi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_acpi.h

## Purpose

`radeon_acpi.h` is the Radeon driver's local contract for AMD GPU-related ACPI control methods. It does not implement ACPI calls itself; instead it names method function IDs, bitfields, request codes, display vectors, and conditional helper prototypes used by the ACPI and VGA switcheroo integration paths elsewhere in the driver.

The file documents four firmware interfaces: `ATIF` for graphics-driver/SBIOS interaction and display/power notifications, `ATPX` for PowerXpress mux and discrete-GPU power control, `ATRM` for reading a discrete GPU VBIOS image through ACPI, and `ATCS` for AMD chipset-specific PCIe state and performance requests.

## Important APIs, Types, And Constants

The header forward-declares `struct radeon_device` and `struct acpi_bus_event`, then defines ACPI method IDs and payload bit meanings. `ATIF_FUNCTION_VERIFY_INTERFACE`, `ATIF_FUNCTION_GET_SYSTEM_PARAMETERS`, `ATIF_FUNCTION_GET_SYSTEM_BIOS_REQUESTS`, `ATIF_FUNCTION_SELECT_ACTIVE_DISPLAYS`, lid/TV/panel helpers, graphics-device enumeration, and external-GPU information constants describe the ATIF call surface. Their companion masks include notification capabilities, supported-function bits, pending SBIOS request bits, panel expansion modes, target GPU IDs, power-source IDs, ATIF display vector bits, and external/removable GPU flags.

The `ATPX_*` constants describe hybrid graphics support: verification, PX parameter discovery, dGPU power control, display mux control, I2C/AUX/HPD mux control, switch-start/end notifications, connector mapping, and display detection ports. Key flags include dynamic PowerXpress support, dynamic dGPU power-off, dGPU display requirements, Microsoft hybrid graphics support, per-connector output/HPD/I2C ownership, and symbolic integrated/discrete GPU selectors.

The `ATCS_*` constants describe chipset functions for dock/external state, PCIe performance requests, device-ready notification, and PCIe bus width setting. The performance request constants encode advertise/wait flags, link-speed request type, remove/low-power/Gen1/Gen2/Gen3 requests, and return states such as refused, complete, and in progress.

Under `CONFIG_VGA_SWITCHEROO`, the file exposes `radeon_register_atpx_handler()`, `radeon_unregister_atpx_handler()`, `radeon_has_atpx_dgpu_power_cntl()`, `radeon_is_atpx_hybrid()`, `radeon_has_atpx()`, and `radeon_atpx_dgpu_req_power_for_displays()`. These are the only function prototypes in this header and form the public Radeon-side hook into Linux hybrid-GPU switching.

## Control Flow

There is no executable control flow in this header. Its comments define the expected ACPI transaction flow: the driver verifies an interface, discovers system parameters and notification mode, receives `Notify(VGA, 0x81)` or a custom VGA notification, calls `GET_SYSTEM_BIOS_REQUESTS`, then reacts to pending request bits by performing driver work such as display detection or display switching before calling a method such as `SELECT_ACTIVE_DISPLAYS`.

For PowerXpress, the implied control flow is capability discovery through ATPX, then optional dGPU power control and mux switching. For ATCS, the implied flow is external-state or PCIe capability discovery, followed by a PCIe performance or bus-width request and interpretation of the returned status.

## State And Persistence Behavior

This file stores no runtime state. The persistent state it describes lives in platform firmware or CMOS: TV standard, panel expansion mode, system BIOS request queues, mux ownership, dGPU power state, dock state, and PCIe/link settings. The driver-visible state is represented as bitmasks and small integer values parsed from ACPI buffers.

Because ACPI buffers are firmware ABI payloads, the sizes and fields in the comments are part of the driver's state contract even though the header does not declare packed C structs for them.

## Dependencies And Integration Points

The direct dependencies are kernel ACPI support, Radeon device structures, and optional `CONFIG_VGA_SWITCHEROO`. The constants are consumed by Radeon ACPI implementation code that evaluates ACPI methods and by switcheroo paths that need to know whether a platform has ATPX and whether the dGPU must be powered for displays.

The integration boundary is firmware-facing and display/power-management-facing: display hotplug/reconfiguration, panel brightness, lid state, dock/external GPU state, hybrid graphics muxes, VBIOS retrieval, and PCIe performance management all depend on these definitions matching platform firmware.

## Risks And Edge Cases

The main risk is ABI drift or misinterpretation of firmware bitfields. A wrong bit position can power off a display-driving dGPU, select the wrong mux owner, miss a BIOS display-switch request, or issue a PCIe performance request that firmware refuses. Several payloads have variable structure sizes, repeated structures, or optional trailing fields, so callers must validate returned buffer sizes before reading fields.

Hybrid graphics platforms are particularly fragile because old PowerXpress, dynamic PX, A+A systems, and Microsoft hybrid graphics use overlapping but not identical ATPX features. ATIF notification handling also depends on whether firmware uses standard VGA notify code `0x81` or a custom `0xd0`-range code.

## Test Signals

Useful signals include boot and resume tests on systems with and without ATPX/ATIF/ATCS, VGA switcheroo registration state, dGPU runtime power transitions, display mux switching, hotplug/display-switch notifications, lid and brightness events, VBIOS retrieval through ATRM on PowerXpress laptops, and ACPI method buffer validation under firmware with older interface versions. Regression logs to watch include ACPI evaluation failures, missing switcheroo handlers, unexpected dGPU power requirements, and failed PCIe performance requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_acpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_agp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_agp.c

## Purpose

`radeon_agp.c` implements Radeon AGP initialization, resume, suspend, and teardown. When `CONFIG_AGP` is enabled, it acquires the kernel AGP backend, applies known hostbridge/GPU/subsystem AGP mode quirks, enables a safe AGP transfer mode, and maps the AGP aperture into Radeon memory-controller GTT fields. When AGP support is absent, the public init path becomes a no-op.

The file exists to keep legacy Radeon AGP systems usable despite old bridge and laptop quirks, while allowing the rest of the driver to treat the resulting aperture as the GTT window.

## Important APIs, Types, And Functions

`struct radeon_agpmode_quirk` describes one compatibility override: hostbridge vendor/device, Radeon chip vendor/device, subsystem vendor/device, and forced default AGP mode. `radeon_agpmode_quirk_list` is a sentinel-terminated table of old Intel, VIA, ATI, ASRock, IBM, Dell, Sony, Acer, Asus, and other combinations that need AGP 1x, 2x, 4x, or 8x for stability.

`radeon_agp_head_init(struct drm_device *dev)` allocates and populates `struct radeon_agp_head` from the kernel AGP bridge info. It tries `agp_find_bridge()` first, falls back to `agp_backend_acquire()`, copies `agp_kern_info`, rejects `NOT_SUPPORTED`, initializes the memory list, and records aperture capabilities such as `cant_use_aperture`, `page_mask`, and base address.

The private helpers `radeon_agp_head_acquire()`, `radeon_agp_head_release()`, `radeon_agp_head_enable()`, and `radeon_agp_head_info()` wrap AGP backend ownership, mode enabling, and information transfer into Radeon-local structures. The public lifecycle consists of `radeon_agp_init()`, `radeon_agp_resume()`, `radeon_agp_suspend()`, and `radeon_agp_fini()`.

## Control Flow

`radeon_agp_init()` is the central path. It acquires the AGP backend, queries AGP info, rejects apertures smaller than 32 MiB, computes a default transfer mode from the intersection of host mode and Radeon AGP status, applies table-driven quirks, validates or substitutes the module parameter `radeon_agpmode`, clears the AGP mode bits, sets the chosen 1x/2x/4x or v3 4x/8x bit, disables fast writes, enables AGP through the backend, then initializes `rdev->mc.agp_base`, `gtt_size`, `gtt_start`, and `gtt_end`.

For older pre-R200 chips, successful init also sets a workaround bit pattern in `RADEON_AGP_CNTL`. Error paths release the AGP backend after failed info retrieval, too-small apertures, or enable failures. `radeon_agp_resume()` simply re-runs init when `RADEON_IS_AGP` is set. `radeon_agp_suspend()` delegates to `radeon_agp_fini()`, which releases the backend if acquired.

## State And Persistence Behavior

The file mutates `rdev->agp` state (`bridge`, `agp_info`, `acquired`, `enabled`, `mode`, list head and aperture metadata) and `rdev->mc` GTT placement (`agp_base`, `gtt_size`, `gtt_start`, `gtt_end`). It also reads and may overwrite the global/module-level `radeon_agpmode` when an illegal user-provided value is replaced with the computed default.

The AGP backend state is persistent across the active driver lifetime but must be released on suspend/fini and reacquired on resume. Hardware register state is not assumed persistent; resume calls the full init path.

## Dependencies And Integration Points

The file depends on Linux PCI and AGP backend APIs, DRM device wrappers, Radeon device state from `radeon.h`, Radeon register access macros, and AGP register constants from Radeon headers. It integrates with `radeon_asic.c` because AGP can be disabled elsewhere and replaced by PCI/PCIe GART callbacks, while this file handles the true AGP aperture path.

The memory-controller setup feeds Radeon GART/TTM memory management. The chosen AGP mode depends on hostbridge capabilities, Radeon status registers for older chips, the user `radeon.agpmode` parameter, and subsystem-specific quirks gathered from historical bug reports.

## Risks And Edge Cases

Legacy hardware compatibility is the main risk. Too aggressive an AGP mode can cause hangs, while too conservative a mode hurts performance. The quirk table is exact-match and subsystem-sensitive, so a near-identical board not in the table may still fail. The code intentionally disables fast writes, reflecting known instability risk.

There are subtle ownership risks around backend acquire/release on error paths and resume. The 32 MiB aperture minimum avoids unusable apertures but can disable AGP on firmware with small aperture settings. Chips bridged from AGP to PCIe skip the AGP status register and trust the host mode, so incorrect bridge reporting can affect mode selection.

## Test Signals

Regression signals include boot logs showing AGP acquisition, selected AGP mode, aperture size, and GTT address range; suspend/resume with AGP reinitialization; module-parameter tests for legal and illegal `radeon.agpmode`; known-quirk hardware booting at the forced mode; failure handling for no bridge, unsupported chipset, and tiny aperture; and GPU memory stress tests using GTT/TTM on AGP systems. Watch for `Unable to acquire AGP`, `Unable to get AGP info`, `AGP aperture too small`, and `Unable to enable AGP` messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_agp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_asic.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_asic.c

## Purpose

`radeon_asic.c` is the Radeon driver's ASIC dispatch registry. It binds each supported Radeon chip family to a `struct radeon_asic` table containing callbacks for initialization, suspend/resume, reset, register access, GART/VM, rings, IRQs, display, copies, surfaces, hotplug, power management, dynamic power management, and page flips. It also initializes register accessor callbacks and normalizes device feature flags such as CRTC count, UVD presence, VCE presence, clock-gating flags, and power-gating flags.

The file is not the implementation of individual hardware engines; instead it is the central switchboard that lets generic Radeon code call `rdev->asic->...` without open-coded family checks throughout the driver.

## Important APIs, Types, And Functions

`radeon_invalid_rreg()` and `radeon_invalid_wreg()` are fail-fast dummy callbacks used for register apertures that are not valid until replaced by family-specific accessors. `radeon_register_accessor_init()` installs these invalid defaults, chooses the PCIe register mask, and assigns memory-controller, PLL, and PCIe-port register accessor callbacks based on chip family.

`radeon_invalid_get_allowed_info_register()` returns `-EINVAL` for families without a userspace-safe info-register allowlist. `radeon_agp_disable()` clears `RADEON_IS_AGP`, forces the device into PCIe or PCI mode depending on family, swaps the active GART callback set to PCIe or PCI helpers for affected older chips, and sizes the internal GART from `radeon_gart_size`.

The static `struct radeon_asic_ring` tables describe per-ring operations: IB execution/parsing, fence emission, semaphore emission, command-submission parsing, ring and IB tests, lockup detection, VM flush, and read/write pointer access. Families progress from one legacy graphics ring (`r100_gfx_ring`, `r300_gfx_ring`, `rv515_gfx_ring`) to R600 graphics plus DMA and optional UVD rings, Cayman/SI multi-CP and DMA rings with VM support, Trinity VCE rings, and CIK graphics/compute/SDMA/VCE rings.

The static `struct radeon_asic` instances cover `r100`, `r200`, `r300`, `r300_asic_pcie`, `r420`, `rs400`, `rs600`, `rs690`, `rv515`, `r520`, `r600`, `rv6xx`, `rs780`, `rv770`, `evergreen`, `sumo`, `btc`, `cayman`, `trinity`, `si`, `ci`, and `kv`. Each table chooses family-appropriate callbacks for lifecycle, display, GART/VM, copy engines, IRQ processing, hotplug sensing, power management, DPM, and page flips.

The exported `radeon_asic_init(struct radeon_device *rdev)` is the main API. It selects one of those tables from `rdev->family`, adjusts capabilities and flags, and returns `-EINVAL` for unsupported families.

## Control Flow

Initialization starts in `radeon_asic_init()`, which first calls `radeon_register_accessor_init()`. It sets a default CRTC count of one or two based on `RADEON_SINGLE_CRTC`, clears `has_uvd` and `has_vce`, and then switches on `rdev->family`.

Older families select simple legacy tables: R100/RS100/RV100/RV200/RS200 use `r100_asic`; R200/RV250/RS300/RV280 use `r200_asic`; R300/R350/RV350/RV380 choose the PCIe-specific table only if `RADEON_IS_PCIE` is set; R420-class chips use AtomBIOS callbacks unless no BIOS is present, in which case clock and backlight callbacks are patched back to legacy functions. Integrated RS and RV families then select tables with chipset-specific memory-controller, IRQ, HPD, and display callbacks.

R600 and newer families add DMA rings, UVD rings, DPM callbacks, and richer display/hotplug handling. Evergreen and Northern Islands families adjust `num_crtc` to four or six depending on display hardware. Cayman, Trinity, SI, CI, and KV add VM callbacks and multiple CP/DMA/compute/media rings. The switch also sets `has_uvd`, `has_vce`, `cg_flags`, and `pg_flags` with per-family exceptions such as RS780 device IDs without UVD, Hainan without display/UVD/VCE, Oland without VCE, and Kaveri/Kabini/Mullins APU CRTC counts.

After family selection, IGP devices have memory-clock PM callbacks disabled because memory clocks are not independently controlled like discrete VRAM. Finally, module-level `radeon_uvd` and `radeon_vce` switches can force `has_uvd` or `has_vce` false.

## State And Persistence Behavior

The primary state mutation is `rdev->asic`, which becomes the persistent callback table for the device lifetime. The function also mutates `rdev->num_crtc`, `rdev->has_uvd`, `rdev->has_vce`, `rdev->cg_flags`, `rdev->pg_flags`, register accessor function pointers (`mc_rreg`, `mc_wreg`, `pll_rreg`, `pll_wreg`, `pciep_rreg`, `pciep_wreg`), `pcie_reg_mask`, and in `radeon_agp_disable()` the bus-type flags and `rdev->mc.gtt_size`.

Most static tables are shared globals. One important edge is that `radeon_asic_init()` directly patches fields inside static ASIC tables in a few cases, such as R420 without BIOS and IGP memory-clock callback disabling. Because those tables are global, this assumes driver/device usage patterns where such mutation does not create conflicting expectations for another device using the same table.

## Dependencies And Integration Points

The file depends on almost every Radeon generation implementation declared by `radeon_asic.h` and other Radeon headers: R100 through CIK/KV, AtomBIOS, ring/fence/semaphore/IB code, command submission parsers, display engines, IRQ blocks, GART and VM code, UVD/VCE media blocks, DPM implementations, and copy engines. It also depends on kernel PCI, console, and VGA arbitration headers for surrounding driver integration.

Generic Radeon subsystems integrate through the selected function tables. Examples include memory management calling GART and VM callbacks, command submission using ring callbacks, DRM modesetting using display and page-flip callbacks, interrupt handling using `irq.set` and `irq.process`, runtime power management using PM/DPM callbacks, and debug/ioctl paths using `get_allowed_info_register`.

## Risks And Edge Cases

The major risk is wrong family-to-callback mapping. A single incorrect function pointer can corrupt registers, emit invalid ring packets, flush the wrong TLB, expose unsafe registers, or report unsupported display/media blocks. Feature gating is equally important: incorrectly enabling UVD/VCE or the wrong CRTC count can make later initialization touch nonexistent hardware.

The static-table patching for no-BIOS R420 and IGP memory-clock callbacks is a maintainability risk because it mutates shared dispatch tables rather than per-device copies. AGP disabling rewrites GART callbacks after initial ASIC selection and must stay consistent with family capabilities. New family additions must update both the callback tables and the switch logic, including clock-gating, power-gating, UVD/VCE, CRTC, and register accessor behavior.

## Test Signals

Useful signals include boot coverage for each chip family group, confirmation of selected ASIC table behavior through init/resume/reset paths, ring tests and IB tests for graphics/DMA/compute/UVD/VCE rings, CS parser tests, GART and VM fault/flush tests, display bring-up with correct CRTC count, page flips and vblank counters, HPD sensing, suspend/resume, DPM state transitions, thermal/fan controls on SI/CI, and module options disabling UVD/VCE. Logs showing unsupported family `-EINVAL`, invalid register callback `BUG_ON`, failed ring tests, or media-engine init on devices marked without those engines are strong regression indicators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_asic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_asic.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_asic.h -->
