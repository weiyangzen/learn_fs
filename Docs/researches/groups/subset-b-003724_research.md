# subset-b-003724 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r500_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r500_reg.h

## Purpose

`r500_reg.h` is a register-definition header for the legacy Radeon R300/R400/R500/RS600/RS690 display and memory-controller blocks. It provides symbolic MMIO and indirect MC register offsets plus bit masks/shifts used by the Radeon KMS driver to program pipe tiling, display controllers, cursors, DAC/TMDS/LVTMA transmitters, panel power sequencing, hardware I2C, HPD GPIOs, interrupts, and pre-R600/AVIVO memory mappings.

## Important APIs, Types, and Definitions

- R300/R400/R500 3D and pipe macros: `R300_GA_POLY_MODE`, `R300_GB_MSPOS0/1`, `R300_RB3D_DSTCACHE_CTLSTAT`, `R300_RB3D_ZCACHE_CTLSTAT`, `R400_GB_PIPE_SELECT`, `R500_DYN_SCLK_PWMEM_PIPE`, `R500_SU_REG_DEST`, `R300_GB_TILE_CONFIG`, and `R300_DST_PIPE_CONFIG`.
- Common command/status registers: `RADEON_CP_STAT`, `RADEON_RBBM_CMDFIFO_ADDR`, `RADEON_RBBM_CMDFIFO_DATA`, and `RADEON_ISYNC_CNTL` describe CP/RBBM synchronization and idle-wait bits.
- RS480/RS600/RS690 memory-controller and GART definitions: `RS480_NB_MC_INDEX/DATA`, `RS690_MCCFG_*`, `RS690_MC_INDEX/DATA/STATUS`, `RS600_MC_INDEX/DATA`, `RS600_MC_PT0_*`, `RS600_*_GART_*`, and associated aperture/page-table/cache bits.
- RV515/R520 memory-controller definitions: `RV515_MC_FB_LOCATION`, `R520_MC_FB_LOCATION`, `R520_MC_AGP_LOCATION`, `R520_MC_STATUS`, `R520_MC_CNTL0`, and channel-width masks used by RV515/R520 initialization.
- AVIVO display definitions: `AVIVO_D1CRTC_*`, `AVIVO_D2CRTC_*`, `AVIVO_D1GRPH_*`, `AVIVO_D2GRPH_*`, cursor registers, LUT registers, scaler/viewport/blank/vline status registers, and CRTC master controls.
- Encoder/output definitions: `AVIVO_DACA_*`, `AVIVO_DACB_*`, `AVIVO_TMDSA_*`, `AVIVO_LVTMA_*`, `R500_LVTMA_*`, `R600_LVTMA_*`, and bit-depth/dither flags.
- Panel/I2C/HPD/interrupt definitions: `AVIVO_LVTMA_PWRSEQ_*`, `AVIVO_LVDS_BACKLIGHT_CNTL`, `AVIVO_DC_I2C_*`, `AVIVO_DC_GPIO_DDC*`, `AVIVO_DC_GPIO_HPD_*`, and `AVIVO_DISP_INTERRUPT_STATUS`.

## Control Flow

This header has no runtime control flow. Its values are consumed by C implementation files through register-access macros such as `RREG32`, `WREG32`, `RREG32_MC`, `WREG32_MC`, and PLL/PCIe helper wrappers. Control flow is therefore indirect: display setup code selects CRTC/GRPH/cursor/transmitter offsets, memory setup code programs MC aperture and GART registers, and interrupt code checks/acks status bits defined here.

## State and Persistence Behavior

The state represented by this file lives in GPU hardware registers. Writes to MC aperture, display, DAC/TMDS/LVTMA, I2C, HPD, cache, and interrupt registers persist until overwritten by the driver, firmware, suspend/resume paths, or GPU reset. The header itself stores no state and declares no functions, but changing a macro changes the hardware contract for all call sites that include it.

## Dependencies and Integration Points

- Integrated by Radeon ASIC-specific code such as RV515/R520 setup, RS600/RS690 memory-controller code, AVIVO display mode-setting, hardware I2C, hotplug, and interrupt handling.
- Shares naming and bitfield conventions with generated-style headers such as `r520d.h` and `r600d.h`, but many entries here are hand-maintained legacy macros.
- Relies on the broader Radeon register access layer to route normal MMIO versus indexed MC register access correctly.
- Display mode code uses the AVIVO D1/D2 offset pattern to address the first and second CRTC blocks.

## Risks and Edge Cases

- Several definitions are legacy and hand-written; typos in names or values are easy to propagate because there is no type checking. Examples include misspelled `TRIANGE` names and an incomplete-looking `AVIVO_DACB_POWERDOWN_RED` macro without an explicit value.
- Duplicate or overlapping definitions such as `RS600_MC_STATUS` can hide earlier values and make future maintenance error-prone.
- R500 and R600 LVTMA register aliases differ by offset; choosing the wrong macro for an ASIC family can program the wrong transmitter register.
- Register writes are often read-modify-write at call sites, so incorrect clear masks or shifts can corrupt adjacent hardware fields.
- Some comments explicitly mark uncertainty, for example TMDS clock/dither behavior, so dependent code should be treated as hardware-quirk-sensitive.

## Test Signals

- Build coverage should compile all legacy Radeon display and MC paths that include this header to catch macro drift.
- Hardware smoke tests should cover R520/RV515 discrete cards, RS600/RS690 integrated chipsets, single and dual CRTC modes, cursor movement, LUT updates, LVDS panel power/backlight, DAC/TMDS/LVTMA outputs, and hotplug events.
- Suspend/resume tests should verify MC aperture restoration, display reprogramming, and HPD/I2C state after reset.
- Register trace comparisons against known-good kernels are useful when changing offsets or bit masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r500_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r520.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r520.c

## Purpose

`r520.c` implements ASIC setup, memory-controller programming, resume, and driver initialization for R520-family Radeon chips (`r520`, `rv530`, `rv560`, `rv570`, `r580`). It bridges older R100/R300/R420/RV515 helper code with R520-specific memory-controller registers and AVIVO-era pipe setup.

## Important APIs, Types, and Functions

- `r520_mc_wait_for_idle(struct radeon_device *rdev)`: polls `R520_MC_STATUS` via indexed MC access until `R520_MC_STATUS_IDLE` is set or `usec_timeout` expires.
- `r520_gpu_init(struct radeon_device *rdev)`: disables VGA rendering, applies an RV530 FIFO workaround, initializes R420 pipes, mirrors pipe-selection state into PLL register `0x000D`, and waits for MC idle.
- `r520_vram_get_type(struct radeon_device *rdev)`: reads `R520_MC_CNTL0` and derives VRAM bus width from channel count and channel-size bits.
- `r520_mc_init(struct radeon_device *rdev)`: determines VRAM/GTT layout, initializes VRAM sizes, handles AGP versus PCIe placement, and refreshes bandwidth info.
- `r520_mc_program(struct radeon_device *rdev)`: stops MC clients, waits idle, writes VRAM size and framebuffer/AGP apertures, then resumes MC clients.
- `r520_startup(struct radeon_device *rdev)`: programs MC, resumes clocks, initializes GPU pipes, enables PCIe GART when present, initializes writeback/fences/IRQs/CP/IB pool.
- `r520_resume(struct radeon_device *rdev)`: disables PCIe GART, starts clocks, resets before AtomBIOS posting, re-posts, restores surface registers, and restarts acceleration.
- `r520_init(struct radeon_device *rdev)`: performs first-time bring-up: scratch/surface/sanity setup, BIOS and AtomBIOS init, reset and post checks, clock/AGP/MC/BO/GART/PM initialization, safe-register setup, and startup.

## Control Flow

Initial load enters `r520_init`. The driver initializes scratch and surface tracking, restores safe defaults, fetches and validates AtomBIOS, resets the GPU before posting to avoid AtomBIOS hangs, checks whether the card is posted, initializes clocks and AGP if needed, configures the memory controller, initializes memory management and PCIe GART structures, sets safe userspace-accessible registers, initializes power management, and calls `r520_startup`.

`r520_startup` is the operational bring-up path used by both init and resume. It programs MC apertures while MC clients are stopped, starts clocks, configures graphics pipes, enables PCIe GART for PCIe devices, initializes writeback and CP fence infrastructure, installs IRQ support if needed, enables RS600-style IRQs, starts the legacy R100 CP with a 1 MiB ring, and initializes the IB pool.

Resume follows a similar path but first disables any active PCIe GART, starts clocks before reset, resets the GPU, runs `atom_asic_init`, starts clocks again after posting, reinitializes surfaces, and then delegates to `r520_startup`.

## State and Persistence Behavior

Persistent state is held in `struct radeon_device`: `mc` aperture and VRAM sizing fields, `flags`, AtomBIOS context, acceleration state, CP/ring/fence/IRQ state, GART objects, power-management state, and chipset configuration. Hardware state is programmed into MC framebuffer/AGP registers, HDP framebuffer location, PLL pipe-selection register, pipe/tiling registers, VGA render state, and CP/IRQ hardware.

`rv515_mc_stop`/`rv515_mc_resume` preserve and restore MC client state around aperture changes. `rdev->accel_working` is set optimistically before startup and cleared on startup failure. AGP devices skip PCIe GART placement, while non-AGP devices receive a GTT location and may enable the RV370 PCIe GART path.

## Dependencies and Integration Points

- Includes `radeon.h`, `radeon_asic.h`, `atom.h`, and `r520d.h`.
- Reuses helpers from older ASIC families: `rv515_vga_render_disable`, `r420_pipes_init`, `rv515_mc_stop`, `rv515_mc_resume`, `rv515_clock_startup`, `rv515_debugfs`, `rv515_set_safe_registers`, `r100_vram_init_sizes`, `r100_restore_sanity`, `r100_cp_init`, and `r100_cp_fini`.
- Integrates with common Radeon subsystems: AtomBIOS parsing/posting, AGP, PCIe GART, TTM/BO setup, writeback, fences, IRQ KMS, surfaces, IB pool, and power management.
- Uses `r520d.h` for generated-style register field macros and `r500_reg.h`-style constants indirectly through shared Radeon headers.

## Risks and Edge Cases

- `r520_mc_wait_for_idle` returns `-1` rather than a standard errno; callers treat nonzero as timeout, but new callers could mishandle it.
- MC programming assumes 32-bit-limited aperture fields and shifts addresses by 16; oversized or badly placed VRAM/GTT ranges need to be constrained before this path.
- `r520_gpu_init` writes PLL register `0x000D` with pipe state derived from multiple registers. Incorrect pipe detection can affect rendering pipe selection.
- Resume comments indicate reset ordering is important because AtomBIOS can otherwise enter an infinite loop.
- Startup failure cleanup in `r520_init` covers many acceleration resources, but failures after partial initialization must be checked carefully when adding new steps.
- The error message says "RV515 GPU" even though this file is R520-family specific.

## Test Signals

- Init/resume tests on R520/RV530/RV560/RV570/R580 hardware should verify successful AtomBIOS posting, MC idle polling, VRAM width detection, CP startup, IRQ delivery, and IB execution.
- AGP and PCIe variants need separate coverage because aperture programming and GART enablement diverge.
- Failure injection around BIOS parsing, reset, BO init, GART init, writeback, fences, IRQ init, CP init, and IB pool init should confirm cleanup and `accel_working` state.
- Register traces should confirm `CONFIG_MEMSIZE`, `MC_FB_LOCATION`, `MC_AGP_LOCATION`, `AGP_BASE`, `HDP_FB_LOCATION`, and pipe PLL writes match expected aperture layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r520.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r520d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r520d.h

## Purpose

`r520d.h` is a generated-style register and bitfield header for R520-era Radeon initialization. It defines system, host data path, command processor, RBBM status, memory-controller aperture, AGP base, and MC channel-configuration registers used mainly by `r520.c` and related legacy ASIC support.

## Important APIs, Types, and Definitions

- System aperture definitions: `R_0000F8_CONFIG_MEMSIZE` and its `S_`, `G_`, and `C_` helpers encode the visible/real VRAM size register.
- Host data path: `R_000134_HDP_FB_LOCATION` and `S_000134_HDP_FB_START` define the HDP framebuffer base field.
- Command processor status: `R_0007C0_CP_STAT` includes busy bits for MRU/MWU, command-stream units, CSF/CSQ variants, GUI/VID DMA, and overall CP busy state.
- RBBM status: `R_000E40_RBBM_STATUS` exposes command FIFO availability and busy bits for 2D/3D, VAP, RE, texture, timing, GA, CBA, and GUI activity.
- MC framebuffer/AGP aperture registers: `R_000004_MC_FB_LOCATION`, `R_000005_MC_AGP_LOCATION`, `R_000006_AGP_BASE`, and `R_000007_AGP_BASE_2`.
- R520 memory-controller type definitions: `R_000008_MC_CNTL0`, `S/G/C_000008_MEM_NUM_CHANNELS`, and `S/G/C_000008_MC_CHANNEL_SIZE`.

## Control Flow

This header has no executable control flow. `r520.c` uses its setters to pack aperture and base fields before indexed MC writes and uses its status offsets in reset diagnostics. The `S_` macros construct field values, `G_` macros extract fields, and `C_` masks clear fields for read-modify-write flows.

## State and Persistence Behavior

The header defines persistent hardware state but stores none itself. Writes to MC framebuffer and AGP aperture registers establish the GPU-visible VRAM/GTT map until the next MC reprogramming or reset. Reads from CP/RBBM status registers provide transient hardware activity snapshots used for diagnostics, lockup handling, and reset messages.

## Dependencies and Integration Points

- Directly included by `r520.c`.
- Follows the same register macro convention used by other Radeon generated headers such as `r600d.h`.
- Integrates with indexed MC accessors (`RREG32_MC`, `WREG32_MC`) and normal MMIO accessors (`RREG32`, `WREG32`).
- Complements broader R500/AVIVO definitions in `r500_reg.h`.

## Risks and Edge Cases

- These macros perform shifts and masks without type enforcement; callers must pass already-shifted address units where required by hardware.
- The `C_` masks are inverse masks. Misusing them as positive masks in new code would clear the wrong bits.
- Aperture setters use 16-bit fields for start/top values. Callers must constrain address ranges before packing.
- Status registers are snapshots and can change immediately after read; using them for anything stronger than polling/diagnostics requires care.

## Test Signals

- Compile tests should cover all call sites using `S_`, `G_`, and `C_` macros to catch syntax drift.
- Unit-style macro tests can validate representative pack/extract behavior for MC framebuffer, AGP location, AGP high base, channel count, and channel size fields.
- Hardware traces during `r520_mc_program` should show packed values matching `rdev->mc.vram_start`, `vram_end`, `gtt_start`, `gtt_end`, and `agp_base`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r520d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600.c

## Purpose

`r600.c` is the main ASIC support file for R600/RV6xx/RS780 and adjacent R7xx/Evergreen-era shared paths in the Radeon driver. It handles indirect register access, clock and display formatting helpers, dynamic power-management policy setup, HPD, PCIe/AGP GART, memory-controller programming, VRAM scratch allocation, reset and lockup detection, GPU block initialization, firmware loading, CP/ring/fence/semaphore emission, UVD setup, suspend/resume/init/fini lifecycle, interrupt-ring management, debugfs, HDP flushing, PCIe lane control, Gen2 link enablement, and GPU clock counter reads.

## Important APIs, Types, and Functions

- Indexed accessors: `r600_rcu_rreg/wreg`, `r600_uvd_ctx_rreg/wreg`, `rs780_mc_rreg/wreg`, and `r600_pciep_rreg/wreg` serialize indirect register windows with spinlocks.
- Public info/clock helpers: `r600_get_allowed_info_register`, `r600_get_xclk`, `r600_set_uvd_clocks`, `rv6xx_get_temp`, and `r600_get_gpu_clock_counter`.
- Display and HPD helpers: `dce3_program_fmt`, `r600_hpd_sense`, `r600_hpd_set_polarity`, `r600_hpd_init`, and `r600_hpd_fini`.
- Power helpers: `r600_pm_get_dynpm_state`, `rs780_pm_init_profile`, `r600_pm_init_profile`, and `r600_pm_misc`.
- Memory/GART helpers: `r600_pcie_gart_tlb_flush`, `r600_pcie_gart_init`, `r600_pcie_gart_enable`, `r600_pcie_gart_disable`, `r600_agp_enable`, `r600_mc_wait_for_idle`, `r600_vram_gtt_location`, `r600_mc_init`, `r600_mc_program`, `r600_vram_scratch_init`, and `r600_vram_scratch_fini`.
- Reset/lockup helpers: `r600_set_bios_scratch_engine_hung`, `r600_gpu_check_soft_reset`, `r600_gpu_soft_reset`, `r600_gpu_pci_config_reset`, `r600_asic_reset`, and `r600_gfx_is_lockup`.
- GPU/ring setup: `r6xx_remap_render_backend`, `r600_count_pipe_bits`, `r600_gpu_init`, `r600_init_microcode`, `r600_cp_load_microcode`, `r600_cp_start`, `r600_cp_resume`, `r600_ring_init`, `r600_cp_fini`, `r600_scratch_init`, `r600_ring_test`, `r600_ring_ib_execute`, and `r600_ib_test`.
- Synchronization packet emission: `r600_fence_ring_emit`, `r600_semaphore_ring_emit`, and `r600_copy_cpdma`.
- UVD lifecycle: `r600_uvd_init`, `r600_uvd_start`, and `r600_uvd_resume`.
- Device lifecycle: `r600_startup`, `r600_vga_set_state`, `r600_resume`, `r600_suspend`, `r600_init`, and `r600_fini`.
- Interrupt handling: `r600_ih_ring_init`, `r600_ih_ring_alloc`, `r600_ih_ring_fini`, `r600_rlc_stop`, `r600_rlc_resume`, `r600_irq_init`, `r600_irq_set`, `r600_irq_ack`, `r600_irq_disable`, `r600_get_ih_wptr`, and `r600_irq_process`.
- PCIe utilities: `r600_mmio_hdp_flush`, `r600_set_pcie_lanes`, `r600_get_pcie_lanes`, and `r600_pcie_gen2_enable`.

## Control Flow

Initial device bring-up enters `r600_init`. It creates debugfs state, reads and validates AtomBIOS, posts the card if needed, initializes scratch/surface/clock/fence subsystems, initializes AGP if present, derives MC VRAM/GTT layout, initializes BO memory management, loads PFP/ME/RLC and optional SMC firmware, initializes power management, prepares the graphics ring and optional UVD ring, initializes the interrupt handler ring, initializes PCIe GART structures, and calls `r600_startup`.

`r600_startup` enables PCIe Gen2 where allowed, creates a pinned VRAM scratch page before MC programming, programs MC apertures, enables either AGP translation or PCIe GART, initializes graphics block registers, starts writeback and fence rings, starts UVD fences when available, installs KMS IRQs, initializes the IH/RLC interrupt path, initializes the graphics ring object, loads CP microcode, resumes the CP, resumes UVD hardware, initializes the IB pool, and starts HDMI/audio support.

Suspend and resume are asymmetric. `r600_suspend` tears down PM runtime activity, audio, CP, UVD, IRQs, writeback, and PCIe GART. `r600_resume` runs AtomBIOS ASIC init without a pre-post reset, resumes DPM if used, marks acceleration active, and reuses `r600_startup`.

Interrupt handling uses a GPU-written IH ring. `r600_irq_init` allocates and pins the ring, disables interrupts, loads RLC firmware, programs IH base/writeback registers, clears active interrupt state, enables PCI bus mastering, and enables IH. `r600_irq_process` reads the hardware or writeback write pointer, serializes processing with `ih.lock`, acknowledges display-side status registers, decodes 16-byte interrupt vectors by `src_id` and `src_data`, dispatches vblank/pageflip/hotplug/audio/UVD/CP/DMA/thermal events, advances `IH_RB_RPTR`, schedules deferred work, and restarts if new vectors arrived.

## State and Persistence Behavior

Persistent driver state lives in `struct radeon_device`: `mc`, `gart`, `vram_scratch`, `ring[]`, `ih`, `wb`, `pm`, `irq`, `config.r600`, firmware pointers, BIOS/AtomBIOS data, UVD state, and acceleration flags. Hardware persistence includes MC aperture registers, VM/GART page-table base, tiling configuration, shader/pipe/backend configuration, CP ring base and pointers, scratch registers, IH ring base and pointers, RLC microcode state, interrupt masks, HPD polarity, UPLL programming, PCIe link settings, and BIOS scratch hang flags.

Spinlocks protect shared indirect index/data register pairs. BO reservation/pin/kmap lifecycles protect VRAM scratch and IH ring allocations. The interrupt path uses an atomic lock and memory barriers to order IH write-pointer reads against ring-vector reads. `gpu_clock_mutex` serializes GPU clock counter capture. `rdev->accel_working`, ring `ready` flags, `gart.ready`, `ih.enabled`, `has_uvd`, and PM requested/current indices are the main software state gates.

## Dependencies and Integration Points

- Kernel/DRM dependencies: firmware loader, PCI config access, debugfs/seq_file, DRM vblank helpers, workqueues, atomics, spinlocks, mutexes, BO/TTM memory management, and delay/polling helpers.
- Radeon common subsystems: AtomBIOS, AGP, GART, BO/GEM, writeback, fences, rings, IBs, semaphores, sync reservations, PM/DPM, audio, UVD, IRQ KMS, display connectors/encoders/CRTCs, and ASIC callback tables.
- Register headers: `r600d.h`, `rv770.h`, `evergreen.h`, `avivod.h`, and shared Radeon headers provide most register offsets and packet encodings.
- Firmware names declared with `MODULE_FIRMWARE` must match the `request_firmware` names selected by ASIC family.
- Public prototypes are exposed through `r600.h` and broader Radeon ASIC structures.

## Risks and Edge Cases

- The file spans multiple ASIC generations. Many branches depend on exact `family` ranges (`R600`, `RV6xx`, `RS780/RS880`, `RV770-RV740`, Evergreen APUs); a misplaced condition can program the wrong register block.
- GART and MC programming are order-sensitive. Scratch allocation must precede MC default-address programming, MC clients must be stopped around aperture updates, and TLB/HDP flush paths have R7xx-specific workarounds.
- Firmware size checks are strict for PFP/ME/RLC, while optional SMC firmware load failures are tolerated for some families. Missing required firmware disables acceleration.
- Several polling loops use `usec_timeout`; too-short timeouts can cause false failures, while hangs can delay init/reset paths.
- Interrupt processing relies on status-register snapshots from `r600_irq_ack`; IH vectors without matching asserted status bits are logged but still partially handled.
- IH overflow recovery intentionally jumps to `(wptr + 16) & ptr_mask`, which can drop old events to regain sync.
- `r600_set_surface_reg` and `r600_clear_surface_reg` are stubs returning success/no-op, so callers expecting hardware surface register programming would get silent nonbehavior.
- `r600_pcie_gart_fini` calls common GART finalization and then disables/frees table resources; lifecycle changes in common GART teardown should verify this order remains valid.
- PCI config reset and PCIe Gen2 link changes are hardware-sensitive and guarded by flags, but still touch low-level PCIe registers and chipset-specific workarounds.

## Test Signals

- Init/resume/suspend/fini tests on representative R600, RV610/RV630/RV670, RS780/RS880, RV770/RV730/RV710/RV740, and Evergreen-family devices should verify firmware load, MC/GART setup, ring tests, IB tests, UVD optional paths, IRQ delivery, and audio init.
- Ring tests should cover scratch writes, CP microcode load, fence emission with and without writeback events, semaphore wait/signal packets, IB scheduling, and CP DMA copies over chunk boundaries.
- Interrupt tests should cover vblank, pageflip, HPD1-HPD6, HDMI audio, UVD, CP EOP, DMA trap, thermal high/low, IH overflow recovery, MSI and non-MSI dummy read behavior.
- Reset tests should inject busy bits in GRBM/SRBM/DMA/display paths and verify soft reset masks, BIOS scratch hang flag updates, PCI config reset fallback, and post-reset ring recovery.
- Memory tests should validate VRAM/GTT placement for AGP, PCIe, large VRAM limiting, IGP direct mapping, sideport handling, GART TLB flush, and HDP flush workarounds.
- PM tests should cover dynpm up/down/default actions, multi-display restrictions, no-display clock modes, profile index selection, voltage updates, and PCIe lane changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600.h

## Purpose

`r600.h` is the private interface header for R600-family Radeon support. It forward-declares Radeon/DRM structures and exposes cross-file prototypes for R600 interrupt rings, audio/HDMI packet programming, GPU reset status, and DMA command-stream relocation parsing.

## Important APIs, Types, and Functions

- Forward declarations: `struct radeon_bo_list`, `struct radeon_cs_parser`, `struct r600_audio_pin`, `struct radeon_crtc`, `struct radeon_device`, and `struct radeon_hdmi_acr` keep this header lightweight.
- Reset/interrupt-ring APIs: `r600_gpu_check_soft_reset`, `r600_ih_ring_alloc`, and `r600_ih_ring_fini`.
- Audio/HDMI APIs: `r600_audio_enable`, `r600_set_audio_packet`, `r600_set_mute`, `r600_hdmi_audio_set_dto`, `r600_set_avi_packet`, `r600_hdmi_update_acr`, `r600_set_vbi_packet`, and `r600_hdmi_enable`.
- DMA CS parsing API: `r600_dma_cs_next_reloc` advances relocation lookup for R600 DMA command submission parsing.

## Control Flow

The header has no executable control flow. It defines the compile-time contract between implementation files such as `r600.c`, Radeon audio/HDMI code, DMA command-submission parsers, and ASIC callback tables. Callers include this header when they need R600-specific entry points without including the larger implementation details.

## State and Persistence Behavior

No state is stored in the header. The declared functions operate on persistent `struct radeon_device`, DRM encoder/CRTC, command parser, ring, audio pin, and HDMI ACR state owned by other modules. Allocation/free prototypes for the IH ring imply ownership transitions for `rdev->ih` BO and mapping state.

## Dependencies and Integration Points

- Depends on Linux integer aliases such as `u32`/`u8`, DRM encoder declarations, and Radeon core structures supplied by including translation units.
- Integrated by R600/R700 display audio, interrupt setup/teardown, reset/lockup detection, and DMA CS validation paths.
- Keeps audio packet and DMA relocation APIs visible across files while avoiding direct inclusion of full Radeon object definitions in this header.

## Risks and Edge Cases

- Because most types are forward-declared, including files must include the concrete DRM/Radeon headers before dereferencing those types.
- Prototype drift between this header and implementation files will break builds across several Radeon modules.
- `r600_gpu_check_soft_reset` exposes a low-level reset-mask contract; callers must interpret returned `RADEON_RESET_*` bits consistently with reset code.
- IH allocation/free functions manage GPU BO resources, so lifecycle callers must avoid double allocation/free and must coordinate with IRQ enablement state.

## Test Signals

- Build tests should include all R600 audio, IRQ, reset, and DMA parser files to catch signature drift.
- Lifecycle tests should pair `r600_ih_ring_alloc` and `r600_ih_ring_fini` through normal init/fini and suspend/resume paths.
- HDMI/audio tests should exercise DTO, ACR, AVI/VBI packet, mute, and enable flows through the prototypes declared here.
- DMA CS parser tests should verify relocation sequencing through `r600_dma_cs_next_reloc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600.h -->
