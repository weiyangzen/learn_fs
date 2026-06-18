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
