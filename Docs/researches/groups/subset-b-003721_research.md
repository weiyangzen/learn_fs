# Research group subset-b-003721

Work item: `subset-b-003721`

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni.h

## Purpose

`ni.h` is a small private header for Northern Islands Radeon support. It exposes only the NI/Cayman helpers that other Radeon source files need without publishing the full implementation details from `ni.c`.

## Important APIs

- `cayman_cp_int_cntl_setup(struct radeon_device *rdev, int ring, u32 cp_int_cntl)` selects a CP ring through `SRBM_GFX_CNTL` and programs `CP_INT_CNTL`.
- `cayman_vm_decode_fault(struct radeon_device *rdev, u32 status, u32 addr)` prints a human-readable VM fault for Cayman/TN memory-client IDs and protection bits.
- `cayman_gpu_check_soft_reset(struct radeon_device *rdev)` inspects GPU status registers and returns a Radeon reset mask.

The only type declaration is the forward declaration for `struct radeon_device`, keeping this header independent of the full Radeon device definition.

## Control Flow and Integration

This header is included by peer Radeon implementation files that need reset, CP interrupt, or VM fault decoding support. For example, `ni_dma.c` calls `cayman_gpu_check_soft_reset()` from DMA lockup detection. The implementation is in `ni.c`; this header just publishes the narrow cross-file contract.

## State, Dependencies, and Persistence

`ni.h` owns no state and performs no persistence. Its declarations imply dependence on Radeon device state and hardware MMIO side effects in the implementations. Consumers must include suitable Radeon headers for `u32` and the complete `struct radeon_device` where they call these functions.

## Risks and Test Signals

The main risk is ABI drift inside the driver: if function signatures or reset-mask semantics change in `ni.c` without updating this header and callers, build failures or incorrect lockup handling follow. Build coverage of all Radeon objects using this header is the primary test signal, with runtime confirmation from DMA/GFX lockup paths and VM fault logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni_dma.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni_dma.c

## Purpose

`ni_dma.c` implements the Cayman-and-newer asynchronous DMA engine support for the Radeon driver. NI hardware has two DMA engines with a packet format distinct from PM4 graphics packets. This file manages DMA ring pointers, ring startup/shutdown, IB execution, lockup detection, and DMA-assisted GPU VM page-table updates.

## Important APIs and Functions

- `cayman_dma_get_rptr()`, `cayman_dma_get_wptr()`, and `cayman_dma_set_wptr()` translate between Radeon ring dword pointers and hardware byte-scaled DMA ring registers for DMA0/DMA1.
- `cayman_dma_ring_ib_execute()` emits a DMA indirect-buffer packet, pads to the required 8-DW alignment, and optionally writes the next read pointer to writeback memory.
- `cayman_dma_stop()`, `cayman_dma_resume()`, and `cayman_dma_fini()` stop, initialize/test, and tear down the two DMA rings.
- `cayman_dma_is_lockup()` maps a ring index to `RADEON_RESET_DMA` or `RADEON_RESET_DMA1` and combines `cayman_gpu_check_soft_reset()` with generic ring lockup testing.
- `cayman_dma_vm_copy_pages()`, `cayman_dma_vm_write_pages()`, `cayman_dma_vm_set_pages()`, `cayman_dma_vm_pad_ib()`, and `cayman_dma_vm_flush()` generate DMA IB commands for page table copies, PTE writes, contiguous PTE/PDE setup, padding, and VM TLB invalidation.

## Control Flow

Startup is handled by `cayman_dma_resume()`, which loops over DMA0 and DMA1. For each engine it disables semaphore timers, computes ring buffer size encoding, sets endian swap bits when needed, resets hardware read/write pointers, writes read-pointer writeback addresses, sets ring base, enables DMA IBs with forced VMID handling, disables context-empty interrupts, writes the initial write pointer, enables the ring, marks it ready, and runs `radeon_ring_test()`. If either ring test fails, that ring is marked not ready and the error propagates.

IB execution pads the current ring so the DMA indirect-buffer packet ends on an 8-DW boundary. When writeback is enabled it first writes a predicted next read pointer into writeback memory through a DMA write packet. It then writes the indirect-buffer packet containing the IB GPU address, length, high address bits, and VMID.

VM update helpers build commands into a caller-provided `struct radeon_ib`. Copy mode copies PTE data from GART memory to page-table memory. Write mode emits explicit PTE values, mapping system pages through `radeon_vm_map_gart()` when `R600_PTE_SYSTEM` is set. Set mode uses the DMA PTE/PDE packet for physically contiguous pages. VM flush writes the page-directory base register, flushes HDP, invalidates the selected VM context, and reads back `VM_INVALIDATE_REQUEST` through SRBM read polling.

## State and Persistence Behavior

The file mutates `rdev->ring[]` entries for DMA0 and DMA1, especially `wptr` and `ready`. It also uses `rdev->wb` for optional read-pointer writeback, `rdev->mc` for visible versus real VRAM size, and `rdev->asic->copy.copy_ring_index` to adjust the active VRAM aperture when DMA is used as the copy engine.

Hardware state is stored in DMA ring control/base/pointer registers and VM registers. Page-table update commands persist GPU VM mappings in VRAM or GART-backed page tables once executed by the DMA engine.

## Dependencies and Integration Points

`ni_dma.c` depends on Radeon ring helpers, writeback memory, VM helpers, reset-mask helpers from `ni.c`, DMA packet macros/registers from `nid.h`, and generic ASIC copy/TTM behavior. It is started and stopped from `ni.c` during Cayman startup, suspend, and finalization. Its VM functions are consumed by the Radeon VM manager when choosing DMA-based page-table updates.

## Risks and Edge Cases

- Ring pointer hardware uses byte addressing while Radeon rings use dword indices; the shifts and `0x3fffc` masks must stay consistent.
- DMA IB packets require strict 8-DW alignment. Missing padding can make the engine fetch malformed IBs.
- Writeback next-rptr prediction depends on packet sizes and padding; miscalculation can confuse software ring accounting.
- Page-table update chunk sizes are capped at `0xFFFFE` dwords; loops must reduce `count` correctly to avoid overruns or infinite loops.
- VM write mode truncates some 64-bit values into 32-bit IB slots intentionally as lower/upper dwords; changes must preserve packet layout.
- Lockup detection depends on `cayman_gpu_check_soft_reset()` correctly distinguishing DMA0 and DMA1.

## Test Signals

Important signals include successful DMA ring tests for both engines, working BO copy/fill operations when DMA is the copy ring, GPU VM page-table updates under system and VRAM memory, absence of VM faults after DMA flushes, and recovery behavior when either DMA ring is forced hung. Big-endian builds are a distinct build/runtime test because swap bits are conditionally programmed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni_dpm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni_dpm.c

## Purpose

`ni_dpm.c` implements dynamic power management for Northern Islands/Cayman Radeon GPUs. It parses ATOM PowerPlay tables, constructs driver-private NI power states, initializes SMC firmware tables, programs voltage/clock/memory timing data, manages clock gating and PCIe gen2 behavior, enables CAC/power containment, and performs runtime power-state transitions.

The file is highly stateful: it bridges VBIOS policy, driver dynamic limits, hardware registers, SMC SRAM layouts from `nislands_smc.h`, and runtime requested/current power states.

## Important APIs, Types, and Data

Static data includes Cayman CAC weight tables for XT/Pro/LE device IDs and register sequences for coarse/fine grain clock gating and light sleep.

Key helpers:

- `ni_get_pi()` and `ni_get_ps()` return NI-specific power-info and power-state private structures.
- `ni_dpm_vblank_too_short()` and `ni_apply_state_adjust_rules()` adjust requested states around display constraints, DC limits, blacklisted clocks, voltage dependencies, and monotonic clock/voltage requirements.
- `ni_dpm_force_performance_level()` sends SMC messages to force high, low, or automatic DPM levels.
- `ni_process_firmware_header()` reads SMC SRAM offsets for state, soft registers, MC register tables, fan, arb, CAC, and SPLL tables.
- `ni_init_smc_table()`, `ni_upload_sw_state()`, `ni_convert_power_state_to_smc()`, and related helpers synthesize `NISLANDS_SMC_STATETABLE` and `NISLANDS_SMC_SWSTATE` records.
- `ni_calculate_sclk_params()`, `ni_populate_sclk_value()`, `ni_populate_mclk_value()`, and `ni_init_smc_spll_table()` compute PLL register values and the SMC SPLL lookup table.
- `ni_initialize_mc_reg_table()`, `ni_populate_mc_reg_table()`, and `ni_upload_mc_reg_table()` parse/copy dynamic AC memory register tables and convert them to SMC format.
- `ni_initialize_smc_cac_tables()`, `ni_initialize_hardware_cac_manager()`, `ni_enable_smc_cac()`, and `ni_enable_power_containment()` configure CAC leakage/power tables and TDP clamping.
- `ni_dpm_setup_asic()`, `ni_dpm_enable()`, `ni_dpm_disable()`, `ni_dpm_pre_set_power_state()`, `ni_dpm_set_power_state()`, `ni_dpm_post_set_power_state()`, `ni_dpm_init()`, and `ni_dpm_fini()` are the main lifecycle entry points.

## Control Flow

`ni_dpm_init()` allocates `struct ni_power_info`, initializes embedded Evergreen/RV770 power info, reads platform capabilities, parses PowerPlay and extended power tables, builds a display-clock voltage dependency table, patches leakage placeholders, chooses default response times and reference dividers, sets clock-gating/power feature flags, reads voltage-control capabilities, chooses CAC weights by PCI device ID, enables default CAC/power-containment/SQ ramping policy, and normalizes DC clock limits.

`ni_dpm_setup_asic()` performs early hardware setup: load MC firmware, snapshot boot clock registers, read arb registers and memory type, advertise PCIe gen2 where ACPI supports performance requests, read current PCIe gen2 status, and enable ACPI PM.

`ni_dpm_enable()` is the main activation sequence. It programs default clock-gating sequences, enables voltage control and voltage tables, initializes dynamic AC memory tables, enables spread spectrum/thermal/display-gap/voltage-control support, enables dynamic PCIe gen2, uploads SMC firmware, reads SMC table offsets, copies MC arb timing from F0 to F1, initializes the SMC state table, SPLL table, arb index, MC register table, CAC tables, hardware CAC registers, TDP limits, response times, starts the SMC, notifies display state, enables SCLK/MCLK control, starts DPM, enables clock gating, enables thermal auto-throttle, and records the boot power state as current.

Power-state switching is split into three public phases. `ni_dpm_pre_set_power_state()` copies the requested state and applies display/DC/voltage adjustment rules. `ni_dpm_set_power_state()` restricts levels, adjusts UVD clocks before lowering engine clocks, disables power containment/CAC, halts SMC, optionally notifies UVD high-speed policy, uploads the new SMC software state and MC register table, programs memory timings, resumes SMC, asks SMC to switch state, adjusts UVD clocks after raising engine clocks, re-enables CAC and power containment, and updates TDP limits. `ni_dpm_post_set_power_state()` makes the requested state current.

`ni_dpm_disable()` reverses runtime policy: clears voltage control, disables thermal protection, power containment, CAC, spread spectrum, thermal auto-throttle, dynamic PCIe gen2, thermal IRQ, clock-gating sequences, DPM global enable, resets defaults, stops SMC, forces MC arb back to F0, and restores boot state as current.

## State and Persistence Behavior

`rdev->pm.dpm.priv` owns `struct ni_power_info`, which embeds Evergreen/RV770 state, clock-register snapshots, MC register tables, CAC data, SMC offsets, current/requested `struct ni_ps`, and scratch SMC table buffers. `rdev->pm.dpm.ps` owns parsed `struct radeon_ps` entries, each with a heap-allocated `struct ni_ps`.

The file writes persistent runtime policy into SMC SRAM using `rv770_copy_bytes_to_smc()` and `rv770_write_smc_sram_dword()`. It writes hardware registers for CAC weights, MC timing, PCIe link behavior, clock gating, PLL programming source tables, and soft registers. Current/requested power states are copied into `evergreen_power_info` with `ps_priv` redirected to stable storage inside `ni_power_info`.

Memory allocated in init is released by `ni_dpm_fini()`: per-state `ps_priv`, the power-state array, NI private info, display-clock dependency entries, and the extended power table.

## Dependencies and Integration Points

This file depends on ATOMBIOS PowerPlay table definitions, SMC layout definitions from `nislands_smc.h`, RV770/Evergreen/BTC/Cypress DPM helpers, Radeon PM core state, ACPI PCIe performance request helpers, clock-divider calculation, voltage table construction, thermal/IRQ support, UVD clock helpers, and MC firmware loading from `ni.c`.

It integrates with `ni.h`/`ni.c` for ASIC setup and MC firmware, with display code through vblank/display-clock constraints, with UVD through special UVD clock ordering and SMC notifications, with ACPI for PCIe gen2 requests, and with debugfs/PM reporting through current SCLK/MCLK and performance-level print helpers.

## Risks and Edge Cases

- Many functions assume valid parsed PowerPlay data and at least one performance level; malformed VBIOS tables can lead to failed init or invalid states.
- `ni_apply_state_adjust_rules()` mutates a copied requested state; callers must use the adjusted `eg_pi->requested_rps`, not the original pointer.
- DPM enable order is fragile: SMC firmware upload, header processing, state-table upload, SPLL table, arb index, CAC, TDP, and SMC start must happen in sequence.
- Endianness conversion is pervasive because SMC structures are big-endian. Missing `cpu_to_be*()`/`be*_to_cpu()` conversions corrupt firmware tables.
- CAC and power containment can be disabled dynamically on table/init failure, changing later behavior without failing the whole enable path in some cases.
- Dynamic AC timing depends on ATOM MC tables and limited SMC array sizes; bounds failures disable or fail the feature.
- Display constraints can force all MCLK/VDDCI levels to the highest requested value when multiple CRTCs or short vblank make switching unsafe.
- SMC message failures during forced levels, CAC, power containment, or state switch produce `-EINVAL` and can leave hardware in an intermediate policy state unless caller unwinds.
- `ni_dpm_init()` has early returns after allocation paths where cleanup responsibility must be understood by the caller or future edits.

## Test Signals

Validation should include boot with DPM enabled, successful SMC firmware upload and header parsing, no DPM enable error logs, stable idle/load SCLK and MCLK transitions, correct behavior under AC versus DC limits, multi-display and short-vblank scenarios that disable MCLK switching, UVD playback state changes, PCIe gen2 link switching, thermal auto-throttle behavior, CAC/power-containment messages, suspend/resume with DPM, and debugfs current performance-level output matching hardware load. VBIOS diversity is important: Cayman XT/Pro/LE boards, GDDR5 threshold variants, and boards with/without voltage GPIO and ACPI PCIe performance requests exercise distinct branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni_dpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni_dpm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni_dpm.h

## Purpose

`ni_dpm.h` defines the Northern Islands DPM private data model and exported helpers used by `ni_dpm.c` and adjacent Radeon power-management code. It is the structural contract between generic Radeon PM state and NI-specific SMC/CAC/MC timing implementation.

## Important Types and Constants

- `struct ni_clock_registers` snapshots SPLL/MPLL/MCLK/DLL/spread-spectrum registers used to build SMC clock states.
- `struct ni_mc_reg_entry` and `struct ni_mc_reg_table` hold VBIOS-derived memory-controller register timing entries plus SMC register address mappings and a validity bitmap.
- `enum ni_dc_cac_level` defines DC CAC table levels.
- `struct ni_leakage_coeffients`, `struct ni_cac_data`, and `struct ni_cac_weights` describe leakage formula inputs, runtime CAC table data, and per-chip hardware CAC weights.
- `struct ni_ps` is the NI private power-state payload: count, DC compatibility, and up to `NISLANDS_MAX_SMC_PERFORMANCE_LEVELS_PER_SWSTATE` RV7xx-style performance levels.
- `struct ni_power_info` is the main private DPM object. It embeds `struct evergreen_power_info` first, then NI clock snapshots, MC tables, flags, SMC offsets, CAC state, current/requested states, and scratch SMC structures.

Constants define SMC arb slots, MC register table driver slot base, and DPM2 power-containment/SQ-ramping parameters.

## Exported APIs

The header publishes `ni_copy_and_switch_arb_sets()`, current/requested power-state update helpers, UVD clock ordering helpers, `ni_dpm_vblank_too_short()`, and accessors `ni_get_pi()`/`ni_get_ps()`.

## Control Flow and State

The header itself has no executable control flow, but its layout drives `ni_dpm.c`. The comment `/* must be first! */` on `struct ni_power_info.eg` is critical: generic Evergreen/RV770 helper code can treat NI private data as an Evergreen power-info prefix. Current/requested state copies inside `ni_power_info` provide stable backing storage for `eg_pi->current_rps.ps_priv` and `eg_pi->requested_rps.ps_priv`.

## Dependencies and Integration Points

`ni_dpm.h` includes `cypress_dpm.h`, `btc_dpm.h`, and `nislands_smc.h`, so it depends on RV7xx/Evergreen/BTC performance-level structures and SMC table definitions. Consumers must already be in the Radeon driver environment with `struct radeon_device`, `struct radeon_ps`, integer types, and AtomBIOS constants available.

## Risks and Test Signals

Structure layout changes are high risk because SMC table sizes, array bounds, and prefix embedding are assumed by implementation code. Changes to CAC weights or DPM2 constants can alter thermal/power behavior. Build coverage catches signature and include issues; runtime DPM tests, SMC table upload success, and debugfs current-state reporting validate that the structures are populated consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni_dpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni_reg.h

## Purpose

`ni_reg.h` is a compact Northern Islands display-register definition header for DCE5-era Radeon hardware. It defines register offsets and bitfield helper macros for gamma, prescale, color-space conversion, degamma/regamma, DisplayPort MSE/MST scheduling, and digital front-end/back-end controls.

## Important Definitions

The header defines DCE5 register offsets such as `NI_INPUT_GAMMA_CONTROL`, `NI_PRESCALE_GRPH_CONTROL`, `NI_INPUT_CSC_CONTROL`, `NI_OUTPUT_CSC_CONTROL`, `NI_DEGAMMA_CONTROL`, `NI_REGAMMA_CONTROL`, `NI_DP_MSE_*`, `NI_DIG_BE_CNTL`, and `NI_DIG_FE_CNTL`.

Bitfield helpers include gamma/degamma/regamma mode encoders, CSC mode encoders, DP MSE rate and slot allocation fields, digital front-end source/mode/HPD selection, and digital front-end control fields for stereosync, dual-link, swap, and symbol clock.

## Control Flow and State

There is no executable control flow and no owned state. The macros are used by display programming code to compose values written through Radeon MMIO helpers. The persistent effect occurs only when another source file writes these register values to hardware.

## Dependencies and Integration Points

This header is included by NI/Cayman display and ASIC code that needs DCE5 register names without duplicating raw offsets. In this work item, `ni.c` includes it, though most heavy use of these display macros likely lives in other display files.

## Risks and Test Signals

- Bitfield macros assume caller-supplied `x` values fit the documented width; most mask locally before shifting, but semantic range validation is left to callers.
- A few DP MSE macros in this header reference `x` but are object-like macros rather than function-like macros, which is suspicious and would fail if expanded as constants. Existing callers may avoid those specific forms or define/use replacement macros elsewhere.
- Wrong offsets or shifts can break color management, DP MST/MSE timing, encoder routing, or link mode programming.

Build coverage catches malformed macro expansion when used. Runtime test signals include modeset success on NI DCE5 outputs, gamma/CSC programming behavior, DP MST stream allocation, HDMI/DVI/LVDS/DP encoder routing, and absence of display underruns or link-training regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni_reg.h -->
