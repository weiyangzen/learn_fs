# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_6_0_sh_mask.h lines 9120-11899

## Scope

This chunk is the tail section of AMD's generated GMC 6.0 shift/mask header. It covers lines 9120-11899, with 2,778 preprocessor definitions: 1,389 `_MASK` constants and 1,389 matching `__SHIFT` constants, followed by the file-closing `#endif`. The range contains no functions, structs, enums, storage objects, branches, allocation, locking, or direct MMIO access. Its public interface is a set of compile-time bitfield constants for Southern Islands / GMC v6 memory-controller, crossbar, XPB, memory PLL, GPUVM, and PRT registers.

The source path is under `sources/distributed-fs/ceph-client`, but this file is AMD GPU register metadata and has no Ceph filesystem behavior.

## Purpose

`gmc_6_0_sh_mask.h` supplies bit positions and masks for registers whose addresses are defined in the companion `gmc_6_0_d.h` header. Driver code combines these constants with register helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()`, or with direct shifts and masks, to compose and decode 32-bit hardware register values.

The naming convention is consistent:

- `<REGISTER>__<FIELD>_MASK` is the raw field mask in the 32-bit register.
- `<REGISTER>__<FIELD>__SHIFT` is the field's least significant bit.

This chunk describes the later GMC v6 register families: memory sequencer training/status fields, GDDR transmit framing, write timing and low-power write timing mirrors, shared memory-channel layout, memory-controller training error counters, VM aperture and GART/page-table controls, MC client write grouping, MC crossbar arbitration and credit controls, XPB peer/routing/BAR controls, memory PLL controls, VM context fault and invalidation fields, L2 VM cache controls, and partially resident texture aperture controls.

## Important APIs, Types, And Macro Families

There are no C APIs or local types. The macros are the API, and their effective type is an integer constant used as part of a `u32` register value.

Important macro groups in this chunk are:

- `MC_SEQ_TRAIN_WAKEUP_MASK` at lines 9120-9159. These fields mask wakeup events for D0/D1 ARF, REDC, WEDC, command/data FIFO readiness, idle, DPM, low-power training, software wakeup, timer, TSM, TCG, SCLK/SRBM readiness, MCLK frequency changes, and PHY power-gating events.
- `MC_SEQ_TSM_*` at lines 9160-9253 plus `MC_TSM_DEBUG_*` at lines 9722-9827. These define the training state machine control, counters, flags, DBI/EDC/WCDR payload fields, capture/debug index/data fields, breakpoint fields, and debug readbacks for multiple byte counters.
- `MC_SEQ_TXFRAMING_*` at lines 9254-9445. These describe DQ, DBI, EDC, WCDR, and FCK nibble mappings for bytes 0-3 and memory channels D0/D1.
- `MC_SEQ_VENDOR_ID_*`, `MC_SEQ_WCDR_CTRL`, `MC_SEQ_WR_CTL_2`, `MC_SEQ_WR_CTL_D0/D1`, and their `_LP` variants at lines 9446-9603. These cover vendor ID readbacks, write clock/data recovery controls, write data delay, ODT delay, DQS timing, DAT_DLY, WCK timing, DQ/DQM timing, and low-power mirror registers used by the Southern Islands DPM path.
- `MC_SHARED_BLACKOUT_CNTL`, `MC_SHARED_CHMAP`, and `MC_SHARED_CHREMAP` at lines 9604-9629. These fields control memory-controller blackout and report or remap channel layout.
- `MC_TRAIN_EDCCDR_*`, `MC_TRAIN_EDC_STATUS_*`, and `MC_TRAIN_PRBSERR_*` at lines 9630-9721. These expose EDC/CDR training values and PRBS error counters/status fields by channel.
- `MC_VM_*` and `VM_*` at lines 9828-9975 and 11514-11897. These are the most directly used macros in `gmc_v6_0.c`: AGP base/bottom/top, display-controller write hit-region controls, framebuffer location and offset, per-client L1 TLB debug/status, MX L1 TLB control, system aperture low/high/default registers, VM context controls, page-table base/start/end addresses, protection fault defaults/status, context disable bits, invalidate request/response bits, L2 cache controls/status, PRT apertures, and PRT fault policy.
- `MC_WR_*` at lines 9976-10105. These field groups classify write clients such as CB, DB, EXT, GFX, LCL, OTH, SYS, HUB, TC0, and TC1 with watermark, group, and enable style controls.
- `MC_XBAR_*` at lines 10106-10257. These define memory crossbar address decode, arbitration, max burst, channel tri-remap, performance monitor select/result, read/write request and return credits, priority credits, remote controls, spare registers, and two-channel control.
- `MC_XPB_*` at lines 10258-11269. These describe XPB client latency-generator config slots 0-36, clock gating, interface config/status, local BAR address, map-invert flush controls, P2P BARs and setup/debug/delta fields, peer system BARs, performance knobs, pipe status, route destination maps, route source apertures, sticky and write-one-clear sticky status, sub-control flags, uncorrectable thresholds, write-combine buffer status/config, and XDMA peer/routing variants.
- `MPLL_*` at lines 11270-11513. These expose memory PLL analog/digital controls and status: AD function/status, mode control, main control, DQ lane status/function control, function control words, sequencer microcode words, spread-spectrum controls, and PLL timing.

## Control Flow

This header has no runtime control flow. Runtime control is in the including driver code:

1. Southern Islands code includes `gmc/gmc_6_0_d.h` and `gmc/gmc_6_0_sh_mask.h`.
2. The caller selects a register address such as `mmVM_CONTEXT1_CNTL`, `mmVM_L2_CNTL`, `mmMC_SHARED_CHMAP`, or `mmMC_SEQ_WR_CTL_D0_LP`.
3. The caller composes or decodes a 32-bit value using the macros directly or through `REG_SET_FIELD()` / `REG_GET_FIELD()`.
4. MMIO helpers such as `RREG32()`, `WREG32()`, or ring packets perform the hardware read/write.

Concrete consumers include `gmc_v6_0.c`, which programs memory apertures, GART contexts, L1/L2 TLBs, VM context fault policy, PRT apertures, and TLB invalidations; `gfx_v6_0.c`, which emits command-stream VM flushes through `mmVM_INVALIDATE_REQUEST`; and `si_dpm.c`, which maps active MC timing registers to `_LP` low-power mirror registers such as `MC_SEQ_WR_CTL_D0_LP`, `MC_SEQ_WR_CTL_D1_LP`, and `MC_SEQ_WR_CTL_2_LP`.

## State And Persistence Behavior

The macros themselves store no state and have no persistence. The hardware registers they describe are stateful:

- Memory sequencer training, TSM, WCDR, EDC/CDR, PRBS, and MPLL fields reflect or control memory bring-up, clocking, lane framing, and training state. Some bits are live status, some are control bits, and some are debug snapshots.
- `_LP` memory timing registers persist low-power timing/programming alternatives used by DPM transitions. `si_dpm.c` copies active timing registers into low-power mirrors and builds a VBIOS-derived MC register table around these addresses.
- `MC_SHARED_BLACKOUT_CNTL` changes CPU/MC access behavior during MC stop/resume in `gmc_v6_0.c`. Incorrect persistence across suspend/resume or reset can block framebuffer access.
- `MC_SHARED_CHMAP` is read to derive memory channel count and VRAM bus width in `gmc_v6_0_mc_init()`.
- `MC_VM_SYSTEM_APERTURE_*`, `MC_VM_AGP_*`, `MC_VM_FB_LOCATION`, and page-table address fields persist the GPU address map until reprogrammed or reset.
- `VM_CONTEXT0_CNTL` and `VM_CONTEXT1_CNTL` enable context translation and fault behavior. Context 0 is programmed for the PCIE GART; contexts 1-15 are configured for application VMIDs.
- `VM_INVALIDATE_REQUEST` and `VM_INVALIDATE_RESPONSE` are live synchronization registers for GPU TLB/cache invalidation domains.
- `VM_L2_CNTL*` and `MC_VM_MX_L1_TLB_CNTL` determine GPUVM cache/TLB behavior and are rewritten during GART enable/disable.
- `VM_CONTEXT*_PROTECTION_FAULT_*` fields hold fault default addresses, faulting logical page address, VMID, client ID, read/write direction, and protection class. They are diagnostic state updated by hardware.
- `VM_PRT_CNTL` and `VM_PRT_APERTURE*` persist partially resident texture aperture policy and are changed when PRT support is enabled or disabled.
- XPB and XBAR fields describe routing, credits, P2P BARs, sticky faults, and performance counters. Their values can be live status, configuration, or sticky write-one-clear state depending on the register.

The header does not encode reset values, access permissions, write-one-clear semantics, reserved-bit policy, read side effects, timing constraints, or required ordering. Those semantics come from hardware documentation and the surrounding driver sequences.

## Dependencies

This chunk depends on:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_6_0_d.h` for matching `mm*` register addresses. The macros in this chunk are meaningful only when paired with that generation's address header.
- AMDGPU register helpers such as `REG_SET_FIELD()`, `REG_GET_FIELD()`, `RREG32()`, `WREG32()`, and `amdgpu_ring_emit_wreg()`.
- Southern Islands GMC/GFX code in `amdgpu/gmc_v6_0.c` and `amdgpu/gfx_v6_0.c`.
- Southern Islands power-management code in `pm/legacy-dpm/si_dpm.c`, which includes both `gmc_6_0_d.h` and this shift/mask header and uses the MC timing mirror register names from this chunk.
- Firmware and VBIOS-derived memory-controller tables used by `gmc_v6_0_mc_load_microcode()` and `si_initialize_mc_reg_table()`. The header provides bit metadata around the register set; firmware/VBIOS tables provide many actual values.

## Integration Points

Key integration points are:

- MC stop/resume in `gmc_v6_0.c`: `MC_SHARED_BLACKOUT_CNTL__BLACKOUT_MODE` is used to blackout and unblackout the memory controller around access changes.
- VRAM and aperture setup in `gmc_v6_0.c`: `MC_VM_SYSTEM_APERTURE_LOW_ADDR`, `MC_VM_SYSTEM_APERTURE_HIGH_ADDR`, `MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR`, `MC_VM_AGP_BASE`, `MC_VM_AGP_TOP`, `MC_VM_AGP_BOT`, and `MC_VM_FB_LOCATION` define the visible GPU memory map.
- Channel-width discovery in `gmc_v6_0_mc_init()`: `MC_SHARED_CHMAP__NOOFCHAN_MASK` and `MC_SHARED_CHMAP__NOOFCHAN__SHIFT` decode memory channel count and combine with RAM configuration to set `adev->gmc.vram_width`.
- GART enable/disable in `gmc_v6_0.c`: `MC_VM_MX_L1_TLB_CNTL`, `VM_L2_CNTL`, `VM_L2_CNTL2`, `VM_L2_CNTL3`, `VM_CONTEXT0_*`, and `VM_CONTEXT1_*` fields configure page-table depth, block size, context enable, fault defaults, and TLB/cache behavior.
- TLB flush paths: `gmc_v6_0_flush_gpu_tlb()` and `gmc_v6_0_emit_flush_gpu_tlb()` write `VM_INVALIDATE_REQUEST` bits for VMIDs 0-15, and `gfx_v6_0_ring_emit_vm_flush()` waits for the invalidate sequence in the command stream.
- Fault handling: `gmc_v6_0_set_fault_enable_default()` changes default handling for range, dummy-page, PDE0, valid, read, and write faults; `gmc_v6_0_vm_decode_fault()` decodes `VM_CONTEXT1_PROTECTION_FAULT_STATUS` fields such as `VMID`, `PROTECTIONS`, memory client ID, and access direction.
- PRT support in `gmc_v6_0_set_prt()`: `VM_PRT_CNTL` toggles fault suppression and invalid-entry storage for CB/TC/L1/L2 behavior, while `VM_PRT_APERTURE{0..3}_{LOW,HIGH}_ADDR` defines reserved partially resident texture ranges.
- Southern Islands DPM memory tables: `si_dpm.c` maps active memory timing registers to low-power mirrors, including `MC_SEQ_WR_CTL_D0`, `MC_SEQ_WR_CTL_D1`, and `MC_SEQ_WR_CTL_2` families from this chunk.
- Debug and performance tooling: `MC_TSM_DEBUG_*`, `MC_XBAR_PERF_MON_*`, `MC_XPB_PIPE_STS`, sticky XPB fields, TLB debug/status, and fault status fields provide readback surfaces for diagnosing memory-controller, VM, crossbar, and peer-routing behavior.

## Risks And Edge Cases

- Header/address mismatch is the primary risk. Using GMC 6.0 masks with another generation's address header can compile when names overlap but program the wrong bit layout.
- The chunk begins in the middle of the overall generated header and ends at the final `#endif`; earlier fields for related registers are outside this range. Merge tooling must combine adjacent chunk notes before drawing whole-file conclusions.
- `VM_CONTEXT0_*` and `VM_CONTEXT1_*` have similar field names but different runtime roles. Context 0 is the kernel/GART context, while context 1 controls the template for contexts 1-15 in this driver.
- Page-table and address fields are page-number fields. `gmc_v6_0.c` writes values shifted by 12 or 22 bits; feeding byte addresses directly would corrupt aperture, AGP, GART, PRT, or fault default programming.
- `VM_INVALIDATE_REQUEST` uses one bit per VMID/domain. Incorrect shifts or stale VMID assumptions can leave old translations live or invalidate the wrong context.
- `VM_L2_CNTL*` and `MC_VM_MX_L1_TLB_CNTL` are cache/TLB policy registers. Bad values can cause VM faults, stale PTE/PDE use, or broad GPU memory corruption rather than a localized failure.
- Fault-control bits have default, interrupt, and save variants with similar names. Confusing them can suppress fault reporting, create interrupt storms, or lose fault diagnostics.
- PRT enable intentionally disables some VM faults for unmapped accesses. `gmc_v6_0_set_prt()` warns when doing this; tests must distinguish expected PRT behavior from accidental fault masking.
- `_LP` timing registers must match VBIOS/DPM expectations. Copying or remapping the wrong MC sequence register can break memory clock transitions or low-power state entry.
- Full-width masks in this chunk describe payload registers such as debug data, vendor IDs, AGP/page numbers, counters, or route apertures. A `0xffffffffL` mask is not evidence that arbitrary writes are safe.
- XPB sticky and sticky-W1C registers have similar names but different clearing semantics. Treating write-one-clear status as normal read/write state risks losing fault evidence.
- XBAR and XPB routing/BAR fields affect peer/system routing and credits. Incorrect values can cause hangs or unreachable apertures in P2P/XDMA or multi-client memory traffic.
- MPLL and memory training controls are sequencing-sensitive. Incorrect direct writes can destabilize memory clocks or training and are generally only safe in prescribed firmware/bring-up flows.

## Test And Validation Signals

Useful validation for this generated-header chunk is mostly build, static, and hardware smoke coverage:

- Build Southern Islands AMDGPU objects that include the header, especially `gmc_v6_0.c`, `gfx_v6_0.c`, and `pm/legacy-dpm/si_dpm.c`.
- Static generated-header checks that every `_MASK` has the matching `__SHIFT`, field masks align with shifts, field names match `gmc_6_0_d.h` register names, and fields do not unexpectedly overlap within a register.
- Boot and modeset tests on Tahiti, Pitcairn, Verde, Oland, and Hainan class hardware to cover MC firmware load, MC blackout/unblackout, channel-map decoding, aperture programming, and framebuffer visibility.
- GART and GPUVM tests that allocate GPU mappings, emit VM flushes, exercise VMIDs 0-15, and verify `VM_INVALIDATE_REQUEST` behavior through graphics-ring flush paths.
- VM fault tests covering invalid, read, write, range, PDE0, and dummy-page faults, with checks that `VM_CONTEXT1_PROTECTION_FAULT_STATUS` decodes the expected VMID, client, access direction, and protection bits.
- PRT tests that toggle `gmc_v6_0_set_prt()`, validate aperture programming for all four PRT ranges, and confirm expected unmapped-access behavior without hiding unrelated VM faults.
- Suspend/resume and DPM memory-clock transition tests that exercise `_LP` MC timing register population from `si_dpm.c`.
- Memory-controller training diagnostics that watch TSM, EDC/CDR, PRBS error, WCDR, and MPLL status fields across boot, resume, and memory clock changes.
- Crossbar and XPB stress tests, when hardware support exists, using P2P/XDMA/system BAR traffic, high read/write pressure, and performance/sticky status readbacks.
