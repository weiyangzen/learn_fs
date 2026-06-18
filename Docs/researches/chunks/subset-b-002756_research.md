# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_offset.h lines 2458-4934

## Scope

This chunk covers the middle-to-late portion of the generated MMHUB 1.7 register offset header. It starts with the tail of the `MMEA1` range at `regMMEA1_EDC_CNT3` and `regMMEA1_MISC_AON`, then covers complete `MMEA2` through `MMEA5` address blocks, MMHUB L1 TLB status and performance counter offsets, PCTL deep-sleep/power-control offsets, ATC L2 and L2 TLB offsets, VM L2 control/fault/performance offsets, and the beginning of the VM-context register table through `regVM_CONTEXT13_PAGE_TABLE_END_ADDR_HI32`.

The chunk contains preprocessor constants only. Each hardware register is represented by a `reg...` offset macro plus a matching `reg..._BASE_IDX` macro. There are no C functions, structs, variables, executable control flow, or software storage in this header section.

Covered address blocks include:

- `mmhub_ea_mmeadec2` at base address `0x69600`, 217 register offsets from `regMMEA2_DRAM_RD_CLI2GRP_MAP0` through `regMMEA2_MISC_AON`.
- `mmhub_ea_mmeadec3` at base address `0x69b00`, 217 register offsets with the same layout for `MMEA3`.
- `mmhub_ea_mmeadec4` at base address `0x6a000`, 217 register offsets with the same layout for `MMEA4`.
- `mmhub_ea_mmeadec5` at base address `0x6a500`, 217 register offsets with the same layout for `MMEA5`.
- `mmhub_l1tlb_vml1dec`, `mmhub_l1tlb_vml1pldec`, and `mmhub_l1tlb_vml1prdec` for L1 TLB status and counters.
- `mmhub_pctldec0` for MMHUB power-control and slice deep-sleep control.
- `mmhub_utcl2_atcl2dec`, `mmhub_utcl2_atcl2pfcntldec`, and `mmhub_utcl2_atcl2pfcntrdec` for ATC L2 control, status, cache data, DSM, clock, and performance counters.
- `mmhub_utcl2_l2tlbdec`, `mmhub_utcl2_l2tlbpldec`, and `mmhub_utcl2_l2tlbprdec` for L2 TLB status, GPUVA/VMID translation-assist windows, and L2 TLB counters.
- `mmhub_utcl2_vml2pfdec`, `mmhub_utcl2_vml2pldec`, `mmhub_utcl2_vml2prdec`, and `mmhub_utcl2_vml2vcdec` for VM L2 control, protection-fault, invalidation, per-context, and page-table aperture registers.

## Purpose

This header section provides the address portion of the MMHUB 1.7 MMIO ABI used by AMDGPU code. The offset macros are consumed by SOC15 register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY`, and `SOC15_REG_ENTRY_OFFSET`. The sibling `mmhub_1_7_sh_mask.h` header supplies the field masks and shifts for many of the same register names, while this file tells the driver where the registers live within the MMHUB IP block.

For MMHUB, these offsets are central to memory-management bring-up: framebuffer and AGP aperture setup, GART page-table base programming, VMID context ranges, VM invalidation request/ack windows, L1/L2 TLB control, MMHUB RAS error counting, ATC/L2 status, and clock/power-management hooks.

## Important Macro Families

### MMEA2 Through MMEA5 Address-Decode Ranges

The dominant part of the chunk is four repeated MMEA address-decode blocks, `MMEA2`, `MMEA3`, `MMEA4`, and `MMEA5`. Each block has the same 217-register shape. The major groups are:

- DRAM read/write client-to-group, group-to-VC, lazy, CAM, page-burst, priority-age, priority-queueing, fixed-priority, urgency, and priority-quantum registers.
- GMI read/write equivalents, including urgency masking.
- Address-normalization windows: base, limit, offset, megabase, megalimit, DRAM/GMI hole controls, and non-power-of-two channel configuration.
- Address-decode controls for bank/misc configuration, DRAM/GMI harvest enable, base addresses, address masks, address configuration, address selection, MAM, and secondary chip-select entries.
- XGMI decode link and hash/offset controls.
- DRAM and GMI page-insert controls.
- Channel and address-index multiplexing controls.
- Clock-gating, EDC mode, error status, corrected/uncorrected error status, EDC counters, and always-on miscellaneous registers.

The repeated layout matters because driver code and diagnostics often treat these ranges as an indexed hardware family. `amdgpu/mmhub_v1_7.c` builds RAS tables over `regMMEA2_EDC_CNT`, `regMMEA3_EDC_CNT`, `regMMEA4_EDC_CNT`, `regMMEA5_EDC_CNT`, matching `EDC_CNT2`/`EDC_CNT3`, and the corresponding `ERR_STATUS` registers.

### L1 TLB and L1 Performance Counter Offsets

The L1 TLB section defines status offsets for `regMC_VM_MX_L1_TLB0_STATUS` through `regMC_VM_MX_L1_TLB7_STATUS`. It also defines `regMC_VM_MX_L1_PERFCOUNTER0_CFG` through `regMC_VM_MX_L1_PERFCOUNTER3_CFG`, `regMC_VM_MX_L1_PERFCOUNTER_RSLT_CNTL`, and the low/high counter result registers.

The actual L1 TLB control register used by `mmhub_v1_7_init_tlb_regs()` appears outside this chunk, but these status and counter windows are part of the same MMHUB VM front end. They support debug, profiling, and validation of TLB activity after the driver enables the L1 TLB and advanced driver model.

### PCTL0 Power-Control Offsets

`PCTL0` covers MMHUB deep-sleep and slice controls:

- Global control and deep-sleep override registers.
- Power-gating ignore controls.
- Per-slice `CFG_DAGB_BUSY`, `CFG_DS_ALLOW`, `CFG_DS_ALLOW_IB`, and `SLICE*_MISC` offsets for slices 0 through 5.
- `regPCTL0_UTCL2_MISC` for shared UTCL2-related power-control state.

These offsets are integration points for clock-gating, deep-sleep, and power-management paths. Their values are hardware control-plane state, not persistent software state.

### ATC L2 and L2 TLB Offsets

The ATC L2 block exposes control, status, cache data, DSM, memory power, clock, and MM group real-time-class registers:

- `regATC_L2_CNTL`, `regATC_L2_CNTL2`, `regATC_L2_CNTL3`, and `regATC_L2_CNTL4`.
- `regATC_L2_STATUS` and `regATC_L2_STATUS2`.
- `regATC_L2_CACHE_DATA0..3`, plus 4K, 32K, and 2M DSM index/control registers.
- `regATC_L2_MISC_CG`, `regATC_L2_MEM_POWER_LS`, and `regATC_L2_CGTT_CLK_CTRL`.
- ATC L2 performance counter configuration and low/high result registers.

`amdgpu/mmhub_v1_7.c` reads and writes `regATC_L2_MISC_CG` in medium-grain clock-gating updates, so offset drift here can break power-management behavior even though the header itself has no logic.

The L2 TLB block defines `regL2TLB_TLB0_STATUS`, GPUVA/VMID translation-assist request and response low/high registers, plus L2 TLB performance-counter config/result offsets.

### VM L2 Control, Fault, and Performance Offsets

The VM L2 block includes:

- VM L2 controls and status: `regVM_L2_CNTL`, `regVM_L2_CNTL2`, `regVM_L2_CNTL3`, and `regVM_L2_STATUS`.
- Dummy page fault control and address registers.
- protection-fault default address, status, control, control2, and instance registers.
- Context invalidate control, invalidate request, acknowledge, and per-engine address-range low/high registers.
- UTCL2 EDC mode/status/config and VM L2 performance counters.

`mmhub_v1_7_init()` records several of these offsets into `adev->vmhub[AMDGPU_MMHUB0(0)]`, including the first invalidation request/ack registers and protection-fault status/control registers. It also computes invalidate-engine spacing from adjacent offset macros. That makes the exact numeric progression of `regVM_INVALIDATE_ENG0_REQ`, `regVM_INVALIDATE_ENG1_REQ`, and the address-range offsets part of the driver's implicit contract.

### VM Context and Page-Table Aperture Offsets

The `mmhub_utcl2_vml2vcdec` section begins the per-VMID context table. This chunk includes:

- `regVM_CONTEXT0_CNTL` through `regVM_CONTEXT15_CNTL`.
- `regVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32/HI32` through context 15.
- `regVM_CONTEXT0_PAGE_TABLE_START_ADDR_LO32/HI32` through context 15.
- `regVM_CONTEXT0_PAGE_TABLE_END_ADDR_LO32/HI32` through context 13 high; contexts 14 and 15 end-address registers continue in the next chunk.

These offsets are directly used by `mmhub_v1_7_setup_vm_pt_regs()` and `mmhub_v1_7_init_gart_aperture_regs()`. The driver writes context 0 page-table base, start, and end registers during GART setup and computes `ctx_addr_distance` as the difference between context 1 and context 0 page-table base offsets.

## Control Flow and State Behavior

This chunk has no runtime control flow. It changes behavior by defining compile-time constants that driver code uses to address MMIO registers.

The persistent state described by the macros is hardware state:

- MMEA DRAM/GMI routing, address-normalization, address-decode, harvest, XGMI, page-insert, clock-gating, and EDC/RAS state.
- L1 and L2 TLB status and performance counter configuration/result state.
- MMHUB PCTL deep-sleep and slice power-control state.
- ATC L2 cache, DSM, clock-gating, memory power, and performance counter state.
- VM L2 control, fault-default-address, fault status/control, invalidation request/ack, invalidate address ranges, and EDC state.
- Per-VMID context controls, page-table base addresses, and page-table virtual address ranges.

Some registers are durable configuration while others are status, counters, request/ack windows, or error latches. The header does not encode ordering, polling, reset, privilege, or timeout rules. Those rules live in the AMDGPU MMHUB implementation and hardware documentation.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `mmhub_1_7_sh_mask.h` supplies masks and shifts for field-level access to many registers named here.
- `soc15_common.h` and `soc15.h` provide the SOC15 register access macros that combine IP block, instance, base index, and offset.
- `amdgpu/mmhub_v1_7.c` includes this header directly and is the primary local consumer in this source tree.

Observed integration points include:

- `mmhub_v1_7_get_fb_location()`, which reads `regMC_VM_FB_LOCATION_BASE` and `regMC_VM_FB_LOCATION_TOP` from adjacent VM aperture definitions.
- `mmhub_v1_7_setup_vm_pt_regs()`, which writes `regVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32/HI32` plus a VMID-scaled offset.
- `mmhub_v1_7_init_gart_aperture_regs()`, which writes context 0 page-table start/end registers covered by this chunk.
- `mmhub_v1_7_init_system_aperture_regs()`, which uses VM L2 protection-fault default/control registers in this register family.
- `mmhub_v1_7_init()`, which stores VM hub offsets and computes context and invalidate-engine register distances from adjacent macros.
- `mmhub_v1_7_update_medium_grain_clock_gating()`, which accesses `regATC_L2_MISC_CG`.
- MMHUB RAS tables in `mmhub_v1_7.c`, which reference `MMEA2` through `MMEA5` EDC counters and error-status registers from this chunk.

The same source tree also has `mmhub_v1_8.c` and `mmhub_1_8_0_offset.h` with similar but not identical register offsets. Consumers must include the matching MMHUB generation; copying an offset between generations can silently address the wrong register.

## Risks

- Offset drift is high impact. A wrong numeric offset can make the driver read or write a different MMHUB register while still compiling cleanly.
- The repeated `MMEA2` through `MMEA5` blocks are mechanically similar. A single copied prefix or skipped offset can corrupt RAS accounting, address decoding, or memory-routing diagnostics for only one range.
- RAS integration depends on matching offset and mask headers. `SOC15_REG_ENTRY(MMHUB, 0, regMMEA*_EDC_CNT*)` pairs with `SOC15_REG_FIELD(MMEA*_EDC_CNT*, ...)`; mismatched names or generations can produce incorrect SEC/DED counts.
- VM context spacing is assumed by code, not individually enumerated at every call site. If `regVM_CONTEXT1_PAGE_TABLE_BASE_ADDR_LO32 - regVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32` changes unexpectedly, VMID page-table programming can target the wrong context.
- Invalidate-engine spacing is similarly inferred from adjacent macros. Bad `regVM_INVALIDATE_ENG*` offsets can break TLB invalidation and lead to stale translations.
- Page-table base, start, and end registers split 64-bit address state into low/high 32-bit registers. Address shift errors in callers or wrong offsets in this header can expose invalid virtual memory ranges.
- PCTL and ATC clock-gating offsets touch power-management state. Incorrect offsets can cause hangs, missed idle states, or power regressions that are hard to attribute to a generated header.
- The chunk ends mid-family at `regVM_CONTEXT13_PAGE_TABLE_END_ADDR_HI32`; the final merged report must connect it to the next chunk for context 14/15 end-address registers and later VM aperture registers.

## Test and Validation Signals

Useful validation is mostly integration and hardware-facing:

- Build AMDGPU with MMHUB 1.7 enabled to catch missing or renamed offset macros.
- Exercise GART and VM bring-up paths that program context 0 page-table base/start/end registers.
- Run VM invalidation tests or GPU workloads that require page-table updates; failures may implicate `regVM_INVALIDATE_ENG*` request/ack/address-range offsets or context distance calculations.
- Validate suspend/resume, reset, and medium-grain clock-gating paths that read or write ATC/PCTL clock and power-control registers.
- Query and reset MMHUB RAS counters, checking `MMEA2` through `MMEA5` SEC/DED counts and `ERR_STATUS` handling.
- Use fault-injection or invalid-address tests to verify VM L2 protection-fault default address, status, and control paths.
- Run performance/debug validation for L1 TLB, ATC L2, L2 TLB, and VM L2 performance counters to confirm counter config/result offsets match the hardware.
- Compare generated `mmhub_1_7_offset.h` against the authoritative register database during header regeneration, especially around repeated MMEA blocks and the VM context table.

## Unresolved Cross-Chunk References

The chunk starts after most of the `MMEA1` block has already been defined and only includes the `MMEA1_EDC_CNT3` and `MMEA1_MISC_AON` tail. It also stops before the VM context table is complete: `VM_CONTEXT14_PAGE_TABLE_END_ADDR_*`, `VM_CONTEXT15_PAGE_TABLE_END_ADDR_*`, and later VM/MC aperture registers are in the following chunk. The merge/reconciliation lane should stitch those neighboring chunks together for the final per-file report.
