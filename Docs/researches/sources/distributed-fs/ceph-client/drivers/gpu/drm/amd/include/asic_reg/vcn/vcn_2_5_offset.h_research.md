# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_2_5_offset.h

## Purpose

`vcn_2_5_offset.h` is a generated-style AMDGPU ASIC register offset table for the VCN 2.5 media block. It contains no executable code; it provides preprocessor constants that name memory-mapped register offsets and the register base index used by SOC15 register access helpers. The paired include `vcn_2_5_sh_mask.h` supplies bit masks and shifts for many of the registers defined here.

The header is included directly by the VCN 2.5 and JPEG 2.5 driver implementations:

- `drivers/gpu/drm/amd/amdgpu/vcn_v2_5.c`
- `drivers/gpu/drm/amd/amdgpu/jpeg_v2_5.c`

Those drivers use these constants with macros such as `SOC15_REG_OFFSET()`, `SOC15_REG_ENTRY_STR()`, `RREG32_SOC15()`, `WREG32_SOC15()`, `WREG32_P()`, `SOC15_WAIT_ON_RREG()`, and `WREG32_SOC15_DPG_MODE()` to program Arcturus-era VCN/JPEG decode, encode, scheduler, power-gating, interrupt, ring-buffer, memory-interface, and RAS registers.

## Important APIs, Types, and Constants

This file exports only C preprocessor constants guarded by `_vcn_2_5_OFFSET_HEADER`.

Each hardware register normally appears as a pair:

- `mm<REGISTER_NAME>`: register offset within the corresponding SOC15 register base aperture.
- `mm<REGISTER_NAME>_BASE_IDX`: index into the SOC15 base-address table. In this header, low JPEG/MMSCH/JRBC/JMI/common JPEG registers use base index `0`, while power-gating, core UVD/VCN, ECPU, MPC, RBC, LMI, MDM, and RAS registers use base index `1`.

The file defines 908 register-related macros. Important groups include:

- MMSCH virtual-function context registers: `mmMMSCH_VF_VMID`, `mmMMSCH_VF_CTX_ADDR_LO`, `mmMMSCH_VF_CTX_ADDR_HI`, `mmMMSCH_VF_CTX_SIZE`, `mmMMSCH_VF_MAILBOX_HOST`, and `mmMMSCH_VF_MAILBOX_RESP`.
- JPEG decode path registers: `mmUVD_JPEG_CNTL`, JPEG ring-buffer base/read/write/size registers, JPEG interrupt registers, pitch registers, tiling-surface registers, address-mode/config registers, GPCOM command/data registers, scratch registers, and soft reset.
- JPEG encode path registers: `mmUVD_JPEG_ENC_*`, `mmJPEG_ENC_*`, encode GPCOM, clock-gating control, scratch, and soft reset.
- JPEG ring-buffer controller registers: `mmUVD_JRBC_*` and `mmUVD_JRBC_ENC_*`, including ring write/read pointers, ring control, indirect buffer size/status, preemption commands, fence data, and scratch registers.
- JPEG memory/JMI registers: `mmUVD_JMI_*`, `mmUVD_LMI_JPEG_*`, `mmUVD_LMI_JRBC_*`, `mmUVD_LMI_EJRBC_*`, VMID registers, 64-bit BAR low/high address registers, swap controls, and performance counters.
- Common JPEG interrupt and clock/power controls: `mmJPEG_SYS_INT_EN`, `mmJPEG_SYS_INT_STATUS`, `mmJPEG_SYS_INT_ACK`, `mmJPEG_MASTINT_EN`, `mmJPEG_IH_CTRL`, `mmJRBBM_ARB_CTRL`, `mmJPEG_CGC_*`, `mmJPEG*_CGC_MEM_CTRL`, `mmJPEG_SOFT_RESET2`, and JPEG perf bank registers.
- VCN/UVD power and DPG registers: `mmUVD_PGFSM_CONFIG`, `mmUVD_PGFSM_STATUS`, `mmUVD_POWER_STATUS`, `mmUVD_JPEG_POWER_STATUS`, `mmUVD_DPG_LMA_*`, `mmUVD_DPG_PAUSE`, scratch registers, harvesting, free counter, global address config, and general-purpose counters.
- Core decode engine registers: `mmUVD_STATUS`, soft reset and clock-gating controls, GPCOM VCPU/SYS command/data registers, interrupt registers, job/context/no-op registers, decode ring buffers `mmUVD_RB_*`, output ring buffer registers, context-index/data registers, frame surface registers, version, and general-purpose scratch registers.
- VCPU/ECPU cache and control registers: `mmUVD_VCPU_CACHE_OFFSET*`, `mmUVD_VCPU_CACHE_SIZE*`, non-cache regions, `mmUVD_VCPU_CNTL`, processor ID, and trace registers.
- MPC, RBC, semaphore, and job-start registers: `mmUVD_MPC_*`, `mmUVD_RBC_*`, `mmUVD_SEMA_*`, `mmUVD_ENGINE_CNTL`, and `mmUVD_JOB_START`.
- LMI address and arbitration registers: `mmUVD_LMI_RBC_*`, `mmUVD_LMI_VCPU_*`, `mmUVD_LMI_MMSCH_*`, `mmUVD_LMI_ARB_CTRL2`, VMID multi-registers, latency counters, `mmUVD_LMI_CTRL2`, `mmUVD_LMI_CTRL`, `mmUVD_LMI_STATUS`, perf counters, and MC credits.
- MDM/DMA busy-state registers: `mmMDM_DMA_CMD`, `mmMDM_DMA_STATUS`, `mmMDM_DMA_CTL`, `mmMDM_ENC_PIPE_BUSY`, and `mmMDM_WIG_PIPE_BUSY`.
- VCN/JPEG 2.6 RAS additions retained in this VCN 2.5 offset header: `mmUVD_RAS_VCPU_VCODEC_STATUS`, `mmUVD_RAS_MMSCH_FATAL_ERROR`, `mmVCN_RAS_CNTL`, `mmUVD_RAS_JPEG0_STATUS`, and `mmUVD_RAS_JPEG1_STATUS`.

## Register Block Layout

The source organizes constants by hardware address block comments. The listed base addresses are documentation for the generated offsets and help reviewers map offsets back to the ASIC register model:

| Address block | Base address | Main role |
| --- | ---: | --- |
| `uvd0_mmsch_dec` | `0x1e000` | MM scheduler VF context and mailbox registers |
| `uvd0_jpegnpdec` | `0x1e200` | JPEG decode control, ring, tiling, interrupt, and GPCOM registers |
| `uvd0_uvd_jpeg_enc_dec` | `0x1e300` | JPEG encode interrupt/control/scratch registers |
| `uvd0_uvd_jpeg_enc_sclk_dec` | `0x1e380` | JPEG encode status, surfaces, GPCOM, CGC, and reset registers |
| `uvd0_uvd_jrbc_dec` | `0x1e400` | JPEG decode ring-buffer controller and preemption registers |
| `uvd0_uvd_jrbc_enc_dec` | `0x1e480` | JPEG encode ring-buffer controller and preemption registers |
| `uvd0_uvd_jmi_dec` | `0x1e500` | JPEG memory interface, VMID, BAR, swap, and performance registers |
| `uvd0_uvd_jpeg_common_dec` | `0x1e700` | JPEG common interrupts and arbitration |
| `uvd0_uvd_jpeg_common_sclk_dec` | `0x1e780` | JPEG clock gating, memory CGC, reset, and perf bank registers |
| `uvd0_uvd_pg_dec` | `0x1f800` | VCN power gating, DPG, scratch, harvesting, and address config |
| `uvd0_uvddec` | `0x1fa00` | Core VCN/UVD status, interrupts, command processor, rings, context, and surfaces |
| `uvd0_ecpudec` | `0x1fd00` | VCPU cache, non-cache, control, ID, and trace registers |
| `uvd0_uvd_mpcdec` | `0x20310` | Motion/processing controller address-config and mux/perf registers |
| `uvd0_uvd_rbcdec` | `0x20370` | Ring-buffer controller, semaphore, engine control, and job-start registers |
| `uvd0_uvdgendec` | `0x20470` | General decode address-config and CGC registers |
| `uvd0_lmi_adpdec` | `0x20870` | Local memory interface BAR, VMID, arbiter, latency, status, and credits |
| `uvd0_uvdnpdec` | `0x20bd0` | MDM DMA and pipe busy registers |

## Control Flow and Runtime Use

There is no control flow in the header itself. Runtime control flow appears where driver code expands these macros into addresses and performs MMIO reads/writes.

In `vcn_v2_5.c`, the constants participate in:

- register discovery/debug tables via `SOC15_REG_ENTRY_STR(VCN, 0, mmUVD_POWER_STATUS)` and similar entries in `vcn_reg_list_2_5`;
- VCN start/resume programming, including `mmUVD_GFX8_ADDR_CONFIG`, `mmUVD_GFX10_ADDR_CONFIG`, `mmUVD_LMI_CTRL2`, `mmUVD_RB_ARB_CTRL`, and `mmUVD_VCPU_CNTL`;
- DPG-mode programming through `SOC15_DPG_MODE_OFFSET(VCN, 0, <register>)`;
- MMSCH setup by writing `mmMMSCH_VF_CTX_ADDR_LO`, `mmMMSCH_VF_CTX_ADDR_HI`, `mmMMSCH_VF_VMID`, and `mmMMSCH_VF_CTX_SIZE`;
- stop/suspend sequencing by polling `mmUVD_LMI_STATUS`, setting `mmUVD_LMI_CTRL2` stall bits, and waiting for clean LMI conditions.

In `jpeg_v2_5.c`, the constants participate in:

- JPEG register-list export through `SOC15_REG_ENTRY_STR(JPEG, 0, mmUVD_JRBC_RB_WPTR)` and neighboring JPEG registers;
- JPEG ring initialization by writing VMID, ring control, 64-bit ring BAR low/high registers, read/write pointers, and ring size;
- JPEG write-pointer management through either doorbells or direct `mmUVD_JRBC_RB_WPTR` MMIO access;
- JPEG interrupt setup through common JPEG interrupt registers such as `mmJPEG_SYS_INT_EN`.

The practical flow is: driver init selects the VCN/JPEG 2.5 implementation, includes this offset table, combines a register macro and its `_BASE_IDX` with SOC15 IP instance data, computes the MMIO offset, then reads/writes hardware registers. Incorrect constants therefore affect probe, power transitions, firmware boot, command submission, interrupt routing, ring operation, and reset/recovery.

## State and Persistence Behavior

The header owns no memory, locks, persistent state, runtime structures, or side effects. Its constants describe hardware state locations. Persistent and semi-persistent behavior arises in the consuming driver and device:

- Ring state is stored in hardware registers such as `mmUVD_JRBC_RB_RPTR`, `mmUVD_JRBC_RB_WPTR`, `mmUVD_RB_RPTR*`, `mmUVD_RB_WPTR*`, ring base BAR registers, and ring size registers.
- Firmware and VCPU state is controlled through cache region registers, VCPU control, GPCOM registers, scratch registers, and context registers.
- Power and clock state is controlled through PGFSM, DPG, CGC, and LMI control/status registers.
- Address translation and memory access state is controlled through VMID registers and BAR low/high address pairs.
- Error and reliability state is surfaced through RAS status/control registers and interrupt/status registers.

Because these are MMIO offsets, the state lifetime is hardware-defined. Values can be reset by ASIC reset, IP block reset, power gating, GPU reset, or firmware sequencing; they are not persisted by this header.

## Dependencies

Direct dependencies are minimal:

- Standard C preprocessor support.
- The consumer must include the file only in contexts where macro names such as `mmUVD_*`, `mmJPEG_*`, and `mmMMSCH_*` do not conflict with another ASIC generation's offset header.

Operational dependencies come from the AMDGPU SOC15 register framework:

- `soc15.h` and `soc15d.h` supply register access helpers that expect both the `mm...` offset macro and `mm..._BASE_IDX` macro.
- `vcn_2_5_sh_mask.h` supplies masks/shifts, for example fields under `UVD_LMI_CTRL2__*`, `UVD_RB_ARB_CTRL__*`, `JPEG_SYS_INT_EN__*`, and MMSCH VMID fields.
- VCN/JPEG driver code supplies the IP block, hardware instance index, ring, firmware, power-management, interrupt, and RAS logic.

## Integration Points

Key integration points are:

- VCN 2.5 implementation: `drivers/gpu/drm/amd/amdgpu/vcn_v2_5.c` includes this file and uses it for media-engine boot, resume, DPG, MMSCH, ring, memory-controller, RAS, and stop paths.
- JPEG 2.5 implementation: `drivers/gpu/drm/amd/amdgpu/jpeg_v2_5.c` includes this file and uses it for JPEG register lists, ring setup, interrupts, and write-pointer access.
- SOC15 base-address tables: every `_BASE_IDX` value must match the IP base register table used by the ASIC. Base-index mismatches are as dangerous as offset mismatches because the computed absolute MMIO address changes.
- Debug and register-dump paths: `SOC15_REG_ENTRY_STR()` entries preserve human-readable register names for selected VCN/JPEG registers.
- Hardware generation compatibility: the file is adjacent to other generated offset headers such as `vcn_2_0_0_offset.h`, `vcn_3_0_0_offset.h`, and legacy UVD offset headers. The same macro names may have different offsets or base indices across generations.

## Risks and Maintenance Notes

- Register offset drift: if this generated table does not match the actual VCN 2.5 ASIC register map, driver MMIO accesses can target unrelated registers. Effects include firmware boot failure, hangs, broken JPEG decode/encode rings, bad interrupt routing, memory corruption, or failed reset/power transitions.
- Base-index drift: a correct offset with the wrong `_BASE_IDX` still computes the wrong absolute address through SOC15 helpers.
- Cross-generation macro name reuse: many names also exist in VCN 2.0, VCN 3.0, and UVD headers. Including multiple generation offset headers in the same C translation unit can cause macro redefinition conflicts or silent wrong-generation usage if include ordering changes.
- Generated-file edits: manual changes are difficult to audit because the file is a flat macro list. Regeneration from the authoritative ASIC register database is safer than hand editing individual constants.
- Incomplete paired masks: adding a register offset here without a corresponding field definition in `vcn_2_5_sh_mask.h` limits safe bit manipulation in consumers and can lead to literal bit operations.
- Low/high BAR pairing: 64-bit address registers appear as low/high pairs. Consumers must write the correct pair for the same block and hardware instance.
- Multi-instance behavior: VCN/JPEG 2.5 code handles up to two hardware instances on Arcturus. The offset table is instance-neutral; consumers must pass the correct instance index to SOC15 helpers.
- RAS naming note: the file includes a short block labeled `VCN 2_6_0 regs` and `JPEG 2_6_0 regs`. Consumers enabling those registers on VCN 2.5-family hardware should be checked against ASIC feature detection and hardware documentation.

## Test Signals

Useful validation signals for this header are mostly integration and hardware-facing:

- Kernel build coverage for `amdgpu` with VCN/JPEG 2.5 enabled; preprocessing should not report macro redefinitions or missing `_BASE_IDX` companions.
- Boot/probe logs on matching hardware should show successful VCN/JPEG IP discovery, firmware load, and ring initialization without MMIO timeout errors.
- Register dump/debugfs paths using `vcn_reg_list_2_5` and `jpeg_reg_list_2_5` should resolve plausible addresses and values.
- JPEG decode ring tests should advance `mmUVD_JRBC_RB_WPTR`/`mmUVD_JRBC_RB_RPTR`, signal interrupts, and complete jobs.
- VCN decode tests should submit jobs through the core rings, see expected read/write pointer movement, and avoid `SOC15_WAIT_ON_RREG()` timeouts on status registers such as `mmUVD_LMI_STATUS`.
- Suspend/resume, runtime power-gating, and dynamic power-gating paths should not hang while manipulating PGFSM, DPG, CGC, LMI, or VCPU registers.
- GPU reset/recovery tests should verify soft reset, ring reinitialization, and LMI clean/stall sequencing.
- RAS-capable hardware tests should confirm that status/control registers defined at the end of the file are only used when supported and produce expected error-reporting behavior.
- Static checks can compare this header against the authoritative generated register database or against known-good upstream VCN 2.5 offset headers to catch accidental manual drift.
