# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 29459-31649

## Scope

This chunk is the final slice of the generated AMD GC 9.4.3 shader-mask header. It starts in the tail of `CGTS_CU9_TCPI_CTRL_REG`, completes the CU10-CU15 TCPI control masks, covers a large set of clock-gating and power/throttle register fields, then moves through GC hypervisor/IOV, VM shared hypervisor, PSP/security, GRBM, and SQ indirect debug register layouts. The range ends at the file's closing `#endif`.

The file is declarative hardware metadata. It contains preprocessor constants only: no C functions, structs, enums, runtime variables, loops, branches, allocations, locks, or callbacks.

## Purpose

`gc_9_4_3_sh_mask.h` defines bit positions and masks for GC 9.4.3 registers. Driver code combines these macros with the companion `gc_9_4_3_offset.h` register IDs and AMDGPU helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and indirect register accessors. The effective API pattern is:

- `<REGISTER>__<FIELD>__SHIFT` for the field's least-significant bit.
- `<REGISTER>__<FIELD>_MASK` for the raw 32-bit register mask.

This specific chunk provides field contracts for clock gating, RLC/CP microcode and virtualization control, VM/IOMMU/ATS virtualization, PSP/GRBM security and error reporting, SQ wave snapshot/debug state, and SQ interrupt payload decoding. Although the repository path is under a Ceph source mirror, this file is AMD GPU driver hardware metadata and has no distributed-filesystem behavior.

## Important Register Families

The first section finishes TCPI and clock-gating controls. `CGTS_CU10_TCPI_CTRL_REG` through `CGTS_CU15_TCPI_CTRL_REG` repeat the per-CU `TCPI`, `TCPI_OVERRIDE`, `TCPI_BUSY_OVERRIDE`, `TCPI_LS_OVERRIDE`, and `TCPI_SIMDBUSY_OVERRIDE` layout. `CGTT_*_CLK_CTRL` families then describe clock-gating delay, hysteresis, soft-stall, soft-override, group-override, and register-override fields for SPI, SPIS, PC, BCI, VGT, IA, WD, PA, SC, SQ, SQG, TCPI, DB, CB, TCC, TCA, CP, CPC, RLC, RMI, TCPF, and related blocks. `SQ_ALU_CLK_CTRL`, `SQ_TEX_CLK_CTRL`, and `SQ_LDS_CLK_CTRL` provide per-shader-array `FORCE_CU_ON` masks, while `SQ_POWER_THROTTLE` and `SQ_POWER_THROTTLE2` expose min/max power, phase offset, delta, interval, ratio, and reference-clock controls.

The `xcd0_gc_hypdec` section defines command-processor and RLC hypervisor-facing fields. It includes CP PFP/ME/CE/MEC microcode address/data/checksum registers, hypervisor variants of those programming surfaces, `CP_HYP_XCP_CTL` for physical XCC and die IDs, RLC GPM microcode access, GRBM indexed shadow-register select/data fields, RLC GPU IOV enable/config/status/doorbell/mask registers, RLC hypervisor semaphores, RLC clock controls, scheduler block metadata, active function IDs, interrupt status/disable/force fields, IOV microcode and scratch access, F32 enable/reset, SMU/RLC response registers, VF/PF virtual reset requests, and SDMA0-SDMA7 preempt/save/restore and busy-status fields.

The `xcd0_gc_utcl2_vmsharedhvdec` section is VM and virtualization metadata. It defines per-VF framebuffer size/offset registers for VF0-VF15, IOMMU enable and performance-optimization bits, MARC base/relocation/length low/high registers for four MARC regions, PCIe ATS control including shared STU/ATC enable and per-VF ATC enable, active shared function ID fields, and XGMI GPU IOV enable bits for VF0-VF15 plus PF.

The `xcd0_gc_pspdec` section covers PSP/security and GRBM debug/error surfaces. `CPG_PSP_DEBUG` and `CPC_PSP_DEBUG` describe privilege and VMID violation controls, with CPC-specific UTCL2 override and disable bits. `GRBM_SEC_CNTL` has a debug enable bit. `GRBM_IOV_ERROR_FIFO_DATA` packs IOV error address, VF ID, source ID, operation, VF/PF flag, overflow, and read-valid status. `GRBM_CAM_INDEX`, `GRBM_HYP_CAM_INDEX`, `GRBM_CAM_DATA`, and `GRBM_HYP_CAM_DATA` define CAM remap selectors/data. `RLC_FWL_FIRST_VIOL_ADDR` reports the first firewall violation status, operation, address, and aperture ID.

The `sqind` section is the SQ indirect wave/debug view. It defines `SQ_DEBUG_STS_LOCAL`, `SQ_DEBUG_CTRL_LOCAL`, `SQ_WAVE_VALID_AND_IDLE`, performance snapshot placeholders, `SQ_WAVE_MODE`, `SQ_WAVE_STATUS`, `SQ_WAVE_TRAPSTS`, `SQ_WAVE_HW_ID`, GPR/LDS allocation, instruction-buffer status/debug registers, PC and instruction dwords, `SQ_WAVE_TTMP0` through `SQ_WAVE_TTMP15`, `SQ_WAVE_M0`, and `SQ_WAVE_EXEC_LO/HI`. The final `SQ_INTERRUPT_WORD_*` families describe packed interrupt payloads for automatic events, common metadata, and wave-specific events in context-ID and high/low split forms.

## Control Flow

There is no control flow in the header itself. Runtime control flow is supplied by consumers:

1. GC 9.4.3-specific code includes `gc_9_4_3_offset.h` and this mask header.
2. The caller selects a direct register or an indirect/indexed register such as an SQ wave register.
3. Code composes or decodes a 32-bit value with the generated shift/mask macros, usually through `REG_SET_FIELD` or `REG_GET_FIELD`.
4. AMDGPU or KFD access helpers perform MMIO, SOC15, or indirect reads/writes.

In-tree GC 9.4.3 code includes this header from `drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c`; that file reads SQ wave state through `wave_read_ind()` using registers such as `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_LO`, `ixSQ_WAVE_EXEC_LO`, `ixSQ_WAVE_HW_ID`, `ixSQ_WAVE_GPR_ALLOC`, `ixSQ_WAVE_LDS_ALLOC`, `ixSQ_WAVE_TRAPSTS`, `ixSQ_WAVE_IB_STS`, `ixSQ_WAVE_IB_DBG0`, `ixSQ_WAVE_M0`, and `ixSQ_WAVE_MODE`. KFD queue-manager code for v9 also includes this mask header.

## State And Persistence Behavior

The macros persist no software state; they are compile-time constants. The hardware fields they describe are stateful and have different lifetimes:

- Clock-gating and power-throttle fields are configuration state. They persist in GC registers until ASIC reset, suspend/resume reprogramming, power-gating transitions, firmware sequences, or explicit driver writes.
- CP and RLC microcode address/data/checksum fields are programming windows for firmware-visible state. Their sequencing and side effects are controlled by microcode load and RLC/CP initialization paths, not by this header.
- RLC GPU IOV fields track virtualization scheduler commands, active functions, doorbells, VM busy state, SDMA save/restore state, interrupt state, and reset requests. Some fields are command/configuration knobs; others are status, sticky status, or response readbacks.
- VM shared hypervisor fields encode VF framebuffer windows, MARC relocation ranges, IOMMU/ATS enablement, active function identity, and XGMI GPU IOV enablement. These are isolation-sensitive device registers, not kernel data structures.
- GRBM/PSP/RLC firewall fields expose security/debug state such as violation controls and first-violation capture. Status fields may be latched, FIFO-backed, or clear-on-read/write according to hardware rules outside this header.
- SQ wave fields are a live per-wave snapshot. Values can change while waves execute, halt, trap, replay, drain, or context-save. TTMP, M0, EXEC, PC, status, trap status, and allocation fields describe the selected wave at the time of indirect access.
- SQ interrupt word fields describe payloads delivered through interrupt/context-ID paths; they are decoded at interrupt time and are not persistent driver storage.

Full-width masks such as `0xFFFFFFFFL` appear for data, scratch, microcode, status bitmap, and register-save fields. A full-width mask does not imply that arbitrary writes are safe.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.4.3 register database remaining synchronized across:

- `gc_9_4_3_sh_mask.h`, which supplies the field layouts researched here.
- `gc_9_4_3_offset.h`, which supplies matching register offsets and indirect indices.
- AMDGPU helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD`, which rely on exact generated macro spelling.
- SOC15 MMIO helpers and XCC-aware register-address normalization in `gfx_v9_4_3.c`.
- Indirect SQ access helpers used for wave dumps, hang diagnostics, and reset/debug paths.
- RLC and CP firmware loading, scheduler, and virtualization code that programs hypervisor, IOV, scratch, semaphore, and microcode windows.
- VM/MMU/IOMMU/ATS and SR-IOV paths that configure VF address windows, active function IDs, XGMI GPU IOV, and PCIe ATS.
- KFD queue, trap, and interrupt paths that use generation-specific SQ wave and interrupt payload layouts.

The macros are generation-specific. Similar field names in GC 9.1, GC 9.4.2, GC 10, GC 11, or GC 12 headers may have different widths, split formats, or register ownership.

## Risks And Edge Cases

- The chunk starts mid-register in `CGTS_CU9_TCPI_CTRL_REG`; the merged per-file report must reconcile the preceding `CU9` field definitions from chunk 12.
- Header/offset mismatch is the highest general risk. Pairing GC 9.4.3 masks with another generation's offset header can compile while programming incorrect bits.
- Clock-gating families are repetitive but not identical. Copying masks across blocks can set reserved bits, leave override bits unset, or force clocks on/off unexpectedly.
- RLC GPU IOV and VM shared hypervisor fields are isolation-sensitive. Incorrect VF enable, framebuffer offset/size, MARC relocation, ATS, active-function, or reset-request programming can break PF/VF isolation, scheduling, or recovery.
- Microcode address/data windows require strict sequencing. Misusing address masks, checksum fields, or hypervisor versus non-hypervisor aliases can corrupt firmware loading or diagnostics.
- SQ wave state is volatile and indirect. Callers must select the intended XCC/SE/SH/SIMD/wave context and tolerate races with wave execution and context save/restore.
- SQ interrupt payload layouts are generation-sensitive. The chunk provides both context-ID and high/low split forms; mixing the wrong form can misdecode wave ID, SIMD ID, CU ID, SE ID, privilege, or event bits.
- Reserved masks are present throughout the chunk. Read-modify-write consumers should preserve unknown bits unless the hardware programming sequence explicitly requires a full-register write.
- The final `#endif` means this is the end of the generated header; downstream merge should not expect later chunks for this source file.

## Test And Validation Signals

Useful validation is primarily build, static, and hardware based:

- Build AMDGPU and KFD code that includes `gc_9_4_3_offset.h` and `gc_9_4_3_sh_mask.h`, especially `gfx_v9_4_3.c` and `kfd_device_queue_manager_v9.c`.
- Preprocess or compile call sites using `REG_SET_FIELD`/`REG_GET_FIELD`; spelling drift in generated field names should fail at compile time when directly referenced.
- Static generated-header checks should verify that complete register groups have matching `__SHIFT` and `_MASK` pairs, masks align with shifts, and fields do not overlap except for documented full-width data/status registers.
- Cross-check register names in this chunk against the companion offset header for `CGTT_*`, `RLC_GPU_IOV_*`, `MC_VM_*`, `VM_PCIE_ATS_CNTL*`, `GRBM_*`, `SQ_WAVE_*`, and `SQ_INTERRUPT_WORD_*`.
- Runtime GC 9.4.3 bring-up should validate stable clock-gating initialization, CP/RLC firmware loading, RLC scheduler setup, IOV doorbell/status handling, VM/IOMMU/ATS configuration, suspend/resume, and GPU reset.
- SR-IOV or multi-function testing should exercise VF framebuffer windows, active function IDs, XGMI GPU IOV enables, virtual reset requests, SDMA save/restore status, and IOV error FIFO reporting.
- Debug and hang-dump tests should read SQ wave data through `gfx_v9_4_3_read_wave_data()` and verify plausible mode, status, trap, PC, instruction, allocation, IB, M0, and EXEC fields.
- KFD interrupt and trap tests should trigger thread-trace, timestamp, overflow, wave, trap, and context-save related paths and validate decoded `SQ_INTERRUPT_WORD_*` payloads against known hardware events.
