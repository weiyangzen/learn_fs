# Research: subset-b-003732

Grouped research for Radeon power-management, PRIME, and register-map files. Each section preserves the source path so the reconciliation lane can split it into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_pm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_pm.c

## Purpose

`radeon_pm.c` is the Radeon KMS driver's central power-management implementation. It coordinates legacy profile-based reclocking, legacy dynamic power management (`dynpm`), newer DPM power-state selection, sysfs knobs, hwmon telemetry/control, thermal work, suspend/resume, and debugfs reporting. The code translates user policy, AC/battery status, display topology, video-engine activity, thermal events, and ASIC capability callbacks into hardware clock, voltage, fan, and display-configuration changes.

## Important APIs, Functions, And Types

- `radeon_pm_get_type_index()` scans `rdev->pm.power_state[]` for a requested `enum radeon_pm_state_type` instance and falls back to `default_power_state_index`. R600/Evergreen code uses it when deriving profile tables from BIOS power states.
- `radeon_pm_acpi_event_handler()` reacts to ACPI power events. In DPM mode it updates `rdev->pm.dpm.ac_power` and toggles Aruba BAPM when available; in profile/auto mode it recalculates the profile and reclocks.
- Legacy profile helpers: `radeon_pm_update_profile()`, `radeon_set_power_state()`, `radeon_pm_set_clocks()`, `radeon_pm_compute_clocks_old()`, and `radeon_dynpm_idle_work_handler()`.
- DPM helpers: `radeon_dpm_single_display()`, `radeon_dpm_pick_power_state()`, `radeon_dpm_change_power_state_locked()`, `radeon_dpm_enable_uvd()`, `radeon_dpm_enable_vce()`, and `radeon_pm_compute_clocks_dpm()`.
- Lifecycle entry points: `radeon_pm_init()`, `radeon_pm_late_init()`, `radeon_pm_suspend()`, `radeon_pm_resume()`, and `radeon_pm_fini()`.
- User/monitoring interfaces are created through device attributes `power_profile`, `power_method`, `power_dpm_state`, `power_dpm_force_performance_level`, hwmon sensor attributes (`temp1_input`, `pwm1`, `freq1_input`, `in0_input`, etc.), and debugfs `radeon_pm_info`.
- The file depends heavily on state embedded in `struct radeon_device`: `rdev->pm`, `rdev->pm.dpm`, rings/fences, CRTC state, BIOS-derived power tables, firmware presence, and ASIC callback tables under `rdev->asic->pm` and `rdev->asic->dpm`.

## Control Flow

Initialization starts in `radeon_pm_init()`. It applies a DPM quirk table, chooses `PM_METHOD_DPM` or `PM_METHOD_PROFILE` based on GPU family, module parameter policy, firmware availability, IGP/dGPU status, and stability quirks, then dispatches to `radeon_pm_init_dpm()` or `radeon_pm_init_old()`. The old path initializes default/current clocks, reads ATOM or COMBIOS power modes, builds profile tables, registers hwmon when an internal thermal sensor exists, and initializes delayed `dynpm` work. The DPM path requires ATOM BIOS data, initializes hwmon and thermal work, calls the ASIC-specific DPM init/setup/enable callbacks, records boot/current/requested power states, and exposes debugfs.

`radeon_pm_late_init()` creates sysfs files after core PM setup. DPM exposes DPM state and forced-performance attributes plus legacy compatibility attributes; profile mode exposes legacy `power_profile` and `power_method` when multiple power states exist. This split matters because userspace-visible controls depend on both the selected PM method and whether DPM successfully enabled.

Legacy profile changes flow from sysfs or display topology updates into `radeon_pm_compute_clocks_old()`. It rebuilds `active_crtcs` and `active_crtc_count`, chooses profile indices via `radeon_pm_update_profile()`, then calls `radeon_pm_set_clocks()`. `radeon_pm_set_clocks()` takes `mclk_lock` and `ring_lock`, waits for each ready ring to drain with `radeon_fence_wait_empty()`, unmaps VRAM BO CPU mappings, takes vblank references for active CRTCs, and calls `radeon_set_power_state()`. The actual transition clamps requested SCLK/MCLK to defaults, optionally adjusts voltage/PCIe/misc before or after clock changes, waits for vblank in flicker-sensitive paths, and updates current indices/clocks only after programming succeeds. Display bandwidth/watermark data is refreshed after the switch.

`dynpm` is a delayed-work loop. `radeon_dynpm_idle_work_handler()` counts outstanding fences across ready rings every `RADEON_IDLE_LOOP_MS`; sustained queued work plans an upclock and idle periods plan a downclock after `RADEON_RECLOCK_DELAY_MS`. It then calls `radeon_pm_get_dynpm_state()` and `radeon_pm_set_clocks()` when the action timeout expires, rescheduling itself while active.

DPM clock computation flows through `radeon_pm_compute_clocks_dpm()`. It rebuilds new active CRTC masks/counts, counts high-pixel-clock connectors, refreshes AC power status, and calls `radeon_dpm_change_power_state_locked()` under `pm.mutex`. DPM power selection maps user states and internal overrides to BIOS power-state classifications: UVD, thermal, ACPI, ULV, boot, 3D performance, battery, balanced, and performance. Fallbacks walk from more specialized states to safer broad states when no exact BIOS match exists. A power-state change takes `mclk_lock` and `ring_lock`, calls ASIC pre-change hooks, updates bandwidth/display configuration, drains rings, programs the state with `radeon_dpm_set_power_state()`, runs post hooks, updates current display and power-state bookkeeping, and reapplies forced performance levels. Thermal activity forces low performance while preserving the user's requested forced level.

UVD/VCE integration sets `uvd_active`, `vce_active`, stream counters, and VCE level under `pm.mutex`, then recomputes clocks unless the ASIC supports direct UVD powergating. Thermal work selects internal thermal state or returns to the user state based on temperature thresholds or interrupt direction, toggles `thermal_active`, and recomputes clocks.

Suspend and resume split by PM method. Legacy suspend pauses active `dynpm` and cancels delayed work; legacy resume restores default clocks/voltages for Barts-Cayman MC firmware cases, resets current PM bookkeeping, restarts `dynpm` when needed, and recomputes clocks. DPM suspend disables DPM and resets current/requested state to boot; DPM resume redoes ASIC setup and enable, falling back to default clocks/voltages if DPM resume fails.

## State And Persistence Behavior

Most state is runtime-only in `rdev->pm` and the hardware registers programmed through ASIC callbacks. The file persists no state to disk. Important persistent-in-memory fields include:

- Legacy profile fields: `profile`, `profile_index`, `requested_power_state_index`, `requested_clock_mode_index`, `current_power_state_index`, `current_clock_mode_index`, `current_sclk`, `current_mclk`, `current_vddc`, `current_vddci`.
- Display state snapshots: `active_crtcs`, `active_crtc_count`, `req_vblank`, and DPM equivalents `new_active_crtcs`, `current_active_crtcs`, `new_active_crtc_count`, `single_display`, and `high_pixelclock_count`.
- DPM policy/state: `dpm.state`, `dpm.user_state`, `dpm.forced_level`, `dpm.ac_power`, `dpm.uvd_active`, `dpm.vce_active`, `dpm.thermal_active`, `current_ps`, `requested_ps`, and `boot_ps`.
- Work state: `dynpm_state`, `dynpm_planned_action`, `dynpm_action_timeout`, `dynpm_can_upclock`, `dynpm_can_downclock`, and delayed/workqueue objects.
- User-visible sysfs and hwmon objects are registered/unregistered at runtime; `sysfs_initialized` prevents duplicate sysfs creation.

Synchronization uses `pm.mutex` for PM policy and DPM state, `pm.mclk_lock` around memory-clock-sensitive regions, `ring_lock` while draining rings and programming transitions, vblank reference counting to keep vblank interrupts alive during transitions, and work cancellation on method changes/suspend/fini.

## Dependencies And Integration Points

The file integrates with Linux DRM/KMS (`drm_for_each_crtc`, vblank helpers, debugfs), TTM/GEM BO tracking (`rdev->gem.objects`, `ttm_bo_unmap_virtual()`), power-supply AC status, hwmon, PCI IDs, firmware gates (`rlc_fw`, `smc_fw`, `mc_fw`), ATOM/COMBIOS power-table parsing, Radeon rings/fences, display bandwidth code, and many ASIC-specific callbacks. `radeon_acpi.c` calls `radeon_pm_acpi_event_handler()`. Other Radeon display/clock files call `radeon_pm_get_type_index()` through the public declaration in `radeon.h`, while this private header only exposes the ACPI handler.

## Risks And Edge Cases

- Reclocking is sensitive to display timing. The code tries to avoid flicker by waiting for vblank, refusing some DPM single-display paths when vblank is too short or refresh is at least 120 Hz, and taking vblank refs, but modeset races can still produce "no vblank, can glitch" paths.
- Ring drain failures in legacy `radeon_pm_set_clocks()` abort without resetting the GPU, leaving recovery to higher layers. DPM ring-drain calls ignore return values while already in the transition.
- Sysfs setters use prefix `strncmp()` checks, so trailing text after a valid prefix may be accepted in several attributes.
- PX/switchable graphics checks prevent some sysfs/hwmon reads and writes while the ASIC is powered off; missing these checks in new interfaces would risk touching powered-down hardware.
- DPM fallback selection can choose broad performance/battery states when BIOS-specific internal states are missing. That is safer than NULL, but it may change power or thermal behavior on unusual BIOS tables.
- The DPM quirk table disables default DPM on known unstable boards only when policy permits; adding/removing quirks changes field stability.
- Fan control exposes percent-to-255 conversions and optional read/write modes depending on ASIC callback availability; partial callback implementations can create read-only or write-only attributes.
- Lifecycle ordering is important: sysfs/hwmon/debugfs objects must not outlive the backing `rdev`, delayed work must be canceled, and DPM must be disabled before freeing `pm.power_state`.

## Test Signals

Useful signals include successful build coverage with relevant Radeon Kconfig options, sysfs presence/absence for `power_profile`, `power_method`, `power_dpm_state`, and `power_dpm_force_performance_level`, hwmon attribute visibility matching DPM/fan/voltage callback support, debugfs `radeon_pm_info` output in both DPM and legacy modes, suspend/resume on DPM and profile GPUs, PX powered-off sysfs/hwmon error behavior, AC-plug/unplug events changing `ac_power` and selected states, UVD/VCE workloads triggering internal states, thermal interrupts forcing low performance, multi-monitor/high-refresh modes avoiding unsafe mclk changes, and ring-drain failure paths not deadlocking `ring_lock` or `mclk_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_pm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_pm.h

## Purpose

`radeon_pm.h` is a very small private Radeon PM header. In this tree it exposes only `radeon_pm_acpi_event_handler()` to other Radeon compilation units, keeping most PM implementation details in `radeon_pm.c` or in broader internal headers such as `radeon.h`.

## Important APIs, Types, And Functions

- Header guard: `__RADEON_PM_H__`.
- Prototype: `void radeon_pm_acpi_event_handler(struct radeon_device *rdev);`
- The declaration relies on `struct radeon_device` being visible or forward-declared by the includer; the header does not include `radeon.h` itself.

## Control Flow

There is no runtime control flow in the header. Its only role is compile-time linkage: users such as `radeon_acpi.c` include it so ACPI power-source or platform events can be forwarded into the PM implementation in `radeon_pm.c`.

## State And Persistence Behavior

The header owns no state and persists nothing. It gives callers access to a function that mutates runtime PM state inside `struct radeon_device`, but the state lives outside this file.

## Dependencies And Integration Points

The key integration is between ACPI/platform notification code and Radeon PM. Because the header is intentionally narrow, other PM entry points are declared elsewhere or kept local, reducing the amount of PM surface exposed through this private include.

## Risks And Edge Cases

- The header depends on include order for `struct radeon_device`; adding standalone prototypes using other types would require forward declarations or includes.
- The narrow API is good for encapsulation, but it can be confusing because `radeon_pm.c` exports additional non-static symbols, such as `radeon_pm_get_type_index()`, through other headers.
- Any signature change must be synchronized with `radeon_acpi.c` and the implementation.

## Test Signals

Compile coverage is the main signal. A missing declaration or include-order regression would surface as build failures in ACPI-enabled Radeon objects. Runtime validation belongs to the `radeon_pm_acpi_event_handler()` path: AC/battery events should update DPM/profile policy without touching powered-off PX hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_prime.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_prime.c

## Purpose

`radeon_prime.c` implements the Radeon KMS driver's PRIME/DMA-BUF GEM sharing hooks. It converts exported Radeon BO pages into scatter-gather tables, imports external DMA-BUF attachments as GTT-backed Radeon BOs, pins/unpins shared BOs for PRIME access, and blocks export of unsafe userptr-backed buffers.

## Important APIs, Functions, And Types

- `radeon_gem_prime_get_sg_table(struct drm_gem_object *obj)` converts a Radeon GEM object's TTM pages (`bo->tbo.ttm->pages`, `num_pages`) to an `sg_table` with `drm_prime_pages_to_sg()`.
- `radeon_gem_prime_import_sg_table(struct drm_device *dev, struct dma_buf_attachment *attach, struct sg_table *sg)` creates a Radeon BO backed by an imported SG table and the DMA-BUF reservation object.
- `radeon_gem_prime_pin(struct drm_gem_object *obj)` pins the BO into `RADEON_GEM_DOMAIN_GTT` and increments `prime_shared_count` on success.
- `radeon_gem_prime_unpin(struct drm_gem_object *obj)` unpins and decrements `prime_shared_count` when nonzero.
- `radeon_gem_prime_export(struct drm_gem_object *gobj, int flags)` rejects userptr-backed BOs with `-EPERM`, otherwise delegates to `drm_gem_prime_export()`.
- Key types are `struct drm_gem_object`, `struct radeon_bo`, `struct dma_buf_attachment`, `struct dma_resv`, and `struct sg_table`.

## Control Flow

Export-side SG table creation assumes the BO has a populated TTM translation table and passes its page array to DRM PRIME helpers. Full export goes through `radeon_gem_prime_export()`, which first calls `radeon_ttm_tt_has_userptr()` to prevent exporting memory owned by userspace userptr mappings, then returns the generic DRM GEM PRIME DMA-BUF.

Import starts with the attachment's `dma_buf->resv`. The function locks the reservation object, calls `radeon_bo_create()` with size `attach->dmabuf->size`, page alignment, non-kernel placement, GTT domain, the supplied SG table, and the shared reservation object, then unlocks regardless of success. On success it sets the GEM object function table to `radeon_gem_object_funcs`, adds the BO to `rdev->gem.objects` under `rdev->gem.mutex`, initializes `prime_shared_count` to one, and returns the GEM base object.

Pinning is deliberately simple: the BO is pinned into GTT with `radeon_bo_pin()`, and the shared count is incremented only when the pin succeeds. Unpin always calls `radeon_bo_unpin()` and then decrements the count defensively only if it is nonzero.

## State And Persistence Behavior

The file persists no disk state. Runtime state changes are on BOs and device lists:

- Imported BOs are created in GTT placement and tied to the DMA-BUF reservation object, enabling cross-driver fencing/reservation synchronization.
- `bo->tbo.base.funcs` is set so the imported object uses Radeon GEM object operations.
- Imported BOs are linked into `rdev->gem.objects` for normal Radeon GEM lifetime tracking.
- `prime_shared_count` tracks active PRIME sharing/pin references at the BO level.

## Dependencies And Integration Points

The implementation depends on Linux DMA-BUF reservation locking, DRM PRIME helpers, TTM TT page arrays, Radeon BO creation/pinning APIs, GEM object conversion helpers, and the Radeon DRM driver table. In this source tree, `radeon_drv.c` wires `.gem_prime_import_sg_table = radeon_gem_prime_import_sg_table`; other PRIME hooks may be inherited from DRM GEM helpers or wired elsewhere depending on kernel API shape.

## Risks And Edge Cases

- `radeon_gem_prime_get_sg_table()` assumes `bo->tbo.ttm` and its page array are valid. Calling it for an object without populated TTM pages would be unsafe.
- Import correctness depends on holding the DMA-BUF reservation lock while creating the BO with the shared reservation object. Changes to locking order could deadlock with exporter/importer paths.
- `prime_shared_count` is local bookkeeping, not a full lifetime mechanism by itself. Mismatched pin/unpin calls can underrepresent actual sharing, though the decrement is guarded against going below zero.
- Userptr export is explicitly forbidden. Removing that check could expose process-owned pages through DMA-BUF in ways the driver cannot safely migrate, pin, or revoke.
- Imported BOs are added to the global GEM object list; failure paths before that point must not leave partially linked objects.

## Test Signals

Useful validation includes PRIME import/export smoke tests with another DRM device, DMA-BUF fence synchronization tests, import failure injection around `radeon_bo_create()`, userptr GEM export returning `-EPERM`, repeated pin/unpin balance tests observing `prime_shared_count`, and device unload after imported DMA-BUF objects to confirm list/lifetime cleanup does not leak or double-free BOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_prime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_prime.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_prime.h

## Purpose

`radeon_prime.h` declares the private Radeon PRIME/DMA-BUF hook functions used by the Radeon DRM driver and related GEM code. It is a narrow interface around exporting, importing, pinning, unpinning, and CPU mapping PRIME-shared GEM objects.

## Important APIs, Types, And Functions

- `radeon_gem_prime_export(struct drm_gem_object *gobj, int flags)`
- `radeon_gem_prime_get_sg_table(struct drm_gem_object *obj)`
- `radeon_gem_prime_pin(struct drm_gem_object *obj)`
- `radeon_gem_prime_unpin(struct drm_gem_object *obj)`
- `radeon_gem_prime_vmap(struct drm_gem_object *obj)`
- `radeon_gem_prime_vunmap(struct drm_gem_object *obj, void *vaddr)`
- `radeon_gem_prime_import_sg_table(struct drm_device *dev, struct dma_buf_attachment *, struct sg_table *sg)`

The declarations rely on DRM and DMA-BUF types being visible from including files; the header does not add its own forward declarations.

## Control Flow

There is no runtime control flow in the header. It provides compile-time declarations for PRIME operations. `radeon_prime.c` implements export, SG-table creation, import, pin, and unpin in this source set. The header also declares vmap/vunmap functions; they are not implemented in the paired `radeon_prime.c` file reviewed here, so either they are obsolete declarations, implemented conditionally outside this subset in other kernel versions, or unused in this tree.

## State And Persistence Behavior

The header owns no state. The declared functions operate on GEM objects, BO pinning state, DMA-BUF reservation objects, and imported BO list membership, but all such state is managed in implementation files.

## Dependencies And Integration Points

The header connects the Radeon driver table and GEM/PRIME code to `radeon_prime.c`. `radeon_drv.c` uses at least the SG-table import declaration for `.gem_prime_import_sg_table`. The API depends on DRM core types, DMA-BUF attachment and SG-table types, and Radeon GEM object conventions.

## Risks And Edge Cases

- The vmap/vunmap declarations are not matched by implementations in `radeon_prime.c` in this tree. If a caller starts using them without adding definitions, the build will fail at link time.
- Because the header does not include or forward-declare its parameter types, include-order mistakes can create compile failures.
- Signature drift against DRM core PRIME hooks is a recurring maintenance risk when kernel DRM APIs change.

## Test Signals

Compile/link coverage is the primary header signal, especially with all PRIME hooks enabled. Additional runtime signals come from the implementation: successful DMA-BUF import, userptr export rejection, GTT pin/unpin balancing, and clean unload with imported/exported objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_prime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_reg.h

## Purpose

`radeon_reg.h` is a large legacy Radeon register and bitfield map. It provides symbolic constants for MMIO, PLL, PCI config, VGA, display, overlay/video, capture, 2D, 3D/TCL, command processor, PCIe GART, TV-out, scratch, and packet formats used by Radeon driver code. It also includes newer generation register headers (`r300_reg.h`, `r500_reg.h`, `r600_reg.h`, `evergreen_reg.h`, `ni_reg.h`, `si_reg.h`, `cik_reg.h`) so one legacy include can expose a broad Radeon register namespace.

## Important APIs, Types, And Definitions

This file defines no functions or C types. Its API is preprocessor constants. Major groups include:

- Memory controller and aperture registers: `RADEON_MC_AGP_LOCATION`, `RADEON_MC_FB_LOCATION`, `RADEON_CONFIG_APER_*`, `RADEON_CONFIG_MEMSIZE`, `RADEON_MEM_*`, `R300_MC_*`.
- PCI/AGP/PCIe constants: `RADEON_AGP_*`, `RADEON_CAP_*`, `RADEON_BUS_CNTL`, `RV370_BUS_CNTL`, MSI rearm bits, `RADEON_PCIE_LC_LINK_WIDTH_CNTL`, `RADEON_PCIE_TX_GART_*`.
- PLL and clock/power bits: `RADEON_CLOCK_CNTL_INDEX/DATA`, `RADEON_CLK_PWRMGT_CNTL`, `RADEON_MCLK_CNTL`, `RADEON_SCLK_CNTL`, `RADEON_SPLL_CNTL`, `RADEON_PPLL_*`, `RADEON_P2PLL_*`, `RADEON_PIXCLKS_CNTL`, `RADEON_TV_PLL_*`.
- Display/CRTC/LVDS/DAC/TMDS registers: `RADEON_CRTC*`, `RADEON_FP*`, `RADEON_LVDS*`, `RADEON_DAC*`, `RADEON_DISP_*`, BIOS scratch registers and display attach/DPMS bits.
- 2D engine and drawing registers: brush data, destination/source offsets and pitches, scissor registers, ROP constants, color compare, host data, GUI scratch, and wait/idle bits.
- Video/overlay/capture/TV-out blocks: `RADEON_OV0_*`, `RADEON_CAP0_*`, `RADEON_CAP1_*`, `RADEON_TV_*`, VIP bus registers.
- 3D/TCL/R200 registers: texture formats/filters/offsets, blend state, z/stencil state, viewport, vertex format, TCL matrices/materials/lights, R200 texture combiners and VAP state.
- Command processor and packet macros: ring buffer registers, indirect buffer registers, CSQ registers, CP packet type constants, packet3 opcodes, and decoding helpers such as `RADEON_CP_PACKET_GET_TYPE()`, `RADEON_CP_PACKET_GET_COUNT()`, `R100_CP_PACKET0_GET_REG()`, and `R600_CP_PACKET0_GET_REG()`.

## Control Flow

There is no runtime control flow. The file affects compiled code by substituting register offsets, masks, shifts, and packet encodings wherever included. The final decoding helper macros do perform compile-time expression expansion for packet parsing.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware state locations and bit meanings. State changes happen in driver code that reads or writes the registers named here. Because many constants correspond to hardware registers with side effects, incorrect use by callers can persist in GPU hardware state until reset, modeset, suspend/resume, or explicit reprogramming.

## Dependencies And Integration Points

This header is a shared contract between low-level Radeon subsystems: memory controller setup, display modesetting, PLL programming, acceleration command emission, CP/ring setup, IRQ/vblank handling, overlay/video paths, TV-out support, GART setup, and legacy 3D state. It integrates with generation-specific headers by including them at the top. Consumers typically pair these constants with register accessors/macros in Radeon core code, ASIC-specific files, and command submission parsing.

## Risks And Edge Cases

- The file begins with a warning that it was converted from `r128_reg.h` and contains definitions not fully audited for Radeon. That historical warning is still relevant: register names may be legacy, duplicated, or only valid on specific ASICs.
- Several constants intentionally alias the same numeric offsets across access spaces or generations, such as PCI config vs MMIO/PLL naming and repeated scratch/register names. Callers must know the correct register aperture and ASIC family.
- Duplicate names and overlapping concepts exist (`RADEON_AGP_BASE` appears in the early memory section and the AGP section; `RADEON_GUI_SCRATCH_REG*` and `RADEON_SCRATCH_REG*` share offsets). Refactors must avoid assuming uniqueness implies distinct hardware.
- Bit masks and shifts encode hardware ABI. A one-bit error can cause display corruption, GPU hangs, bad memory-controller setup, broken command parsing, or unsafe power/clock behavior.
- Newer generation headers are included into this namespace, increasing the chance of macro collisions and making include-order effects important.
- Some comments mark guesses, unknowns, or FIXME material. These should be treated as hardware documentation debt, not authoritative high-level behavior.

## Test Signals

The main validation signals are compile coverage of all consumers, command submission parser tests for packet decoding macros, modeset and vblank tests for CRTC/display constants, ring/CP initialization on affected ASIC generations, suspend/resume after PLL or memory-controller programming, IGT or similar display/PRIME/GEM workloads that exercise register programming, and hardware smoke tests across R100/R200/R300/R500/R600+ families because the same header spans many ASIC-specific register layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_reg.h -->
