# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002837`: lines 1-2477, `Docs/researches/chunks/subset-b-002837_research.md`
- `subset-b-002838`: lines 2478-4976, `Docs/researches/chunks/subset-b-002838_research.md`
- `subset-b-002839`: lines 4977-7451, `Docs/researches/chunks/subset-b-002839_research.md`
- `subset-b-002840`: lines 7452-7789, `Docs/researches/chunks/subset-b-002840_research.md`

## Chunk Research

### subset-b-002837: lines 1-2477

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_offset.h lines 1-2477

## Purpose

This chunk is the opening portion of the generated AMDGPU MMHUB 9.4.1 register-offset header. It provides C preprocessor constants for MMHUB hardware register addresses and their SOC15 base-index selector values. The matching `mmhub_9_4_1_sh_mask.h` header defines bit layouts inside those registers; this offset header names the registers and gives the numeric offsets used by SOC15 register access helpers.

The covered range defines the include guard and the first 1,212 register offsets, plus 1,211 matching `_BASE_IDX` constants. The hardware blocks covered here are:

- `mmhub_dagb_dagbdec0` through `mmhub_dagb_dagbdec4`, base addresses `0x68000`, `0x68200`, `0x68400`, `0x68600`, and `0x68800`.
- `mmhub_ea_mmeadec0` and `mmhub_ea_mmeadec1`, base addresses `0x68a00` and `0x68f00`.
- The beginning of `mmhub_ea_mmeadec2`, base address `0x69400`, ending in this chunk at `mmMMEA2_ADDRDEC0_COL_SEL_LO_CS23`.

The file has no executable code, type definitions, or data storage. Its job is to make generated ASIC register names available to AMDGPU MMHUB v9.4 code at compile time.

## Important APIs, Types, And Macros

The public surface is entirely macro definitions:

- Include guard: `_mmhub_9_4_1_OFFSET_HEADER`.
- Register offset macros: `mm<REGISTER_NAME>` with a hexadecimal register offset.
- Register base selector macros: `mm<REGISTER_NAME>_BASE_IDX`, all equal to `1` in this chunk.

The `DAGB` decoder blocks are mechanically repeated for `DAGB0` through `DAGB4`. Each complete block contains 126 register offsets in a `0x80`-wide range. `DAGB0` spans `0x0000..0x007f`, `DAGB1` spans `0x0080..0x00ff`, `DAGB2` spans `0x0100..0x017f`, `DAGB3` spans `0x0180..0x01ff`, and `DAGB4` spans `0x0200..0x027f`. The repeated families include:

- Read-client and write-client entries: `mmDAGB*_RDCLI0..15` and `mmDAGB*_WRCLI0..15`.
- Read/write global controls: `RD_CNTL`, `WR_CNTL`, `RD_GMI_CNTL`, `WR_GMI_CNTL`, `RD_ADDR_DAGB`, `WR_ADDR_DAGB`, and `WR_DATA_DAGB`.
- Clock-gating controls: `RD_CGTT_CLK_CTRL`, `WR_CGTT_CLK_CTRL`, `L1TLB_*_CGTT_CLK_CTRL`, and `ATCVM_*_CGTT_CLK_CTRL`.
- Burst and lazy-timer controls for read address, write address, write data, and output paths.
- Virtual-channel controls: `RD_VC0_CNTL..RD_VC7_CNTL` and `WR_VC0_CNTL..WR_VC7_CNTL`.
- Credit and pending-status registers: TLB/data/misc credits, `RDCLI_*_PENDING`, `WRCLI_*_PENDING`, FIFO empty/full, and read/write credit-full status.
- Coherency override registers: `WRCLI_GPU_SNOOP_OVERRIDE` and `WRCLI_GPU_SNOOP_OVERRIDE_VALUE`.
- Diagnostics and counters: `DAGB_DLY`, `CNTL_MISC`, `CNTL_MISC2`, `PERFCOUNTER_LO`, `PERFCOUNTER_HI`, `PERFCOUNTER0_CFG`, `PERFCOUNTER1_CFG`, `PERFCOUNTER2_CFG`, `PERFCOUNTER_RSLT_CNTL`, and reserved slots.

The `MMEA` address-decode blocks are also repeated, with complete blocks for `MMEA0` and `MMEA1`. Each complete block has 233 register offsets. `MMEA0` spans `0x0280..0x0394`, and `MMEA1` spans `0x03c0..0x04d4`. These blocks include:

- DRAM, GMI, and IO client-to-group and group-to-virtual-channel maps.
- DRAM, GMI, and IO lazy timers, CAM controls, page-burst controls, priority aging, priority queuing, fixed priority, urgency, urgency masking, and priority quantum registers.
- Address normalization ranges: `ADDRNORM_BASE_ADDR*`, `ADDRNORM_LIMIT_ADDR*`, offset registers, DRAM/GMI hole controls, and non-power-of-two channel configuration.
- Address decoder controls: bank configuration, hash selection for DRAM/GMI banks, PC, chip-select fields, harvest enable, and per-address-decoder chip-select base/mask/config/select/column/rank-map registers.
- MAM client-to-group maps, MAM group-to-virtual-channel maps, MAM priority controls, and MAM D0-D3 memory controls.
- SDP arbitration and resource controls: `SDP_ARB_DRAM`, `SDP_ARB_GMI`, `SDP_ARB_FINAL`, per-target priorities, credits, tag/VCC/VCD reserves, and `SDP_REQ_CNTL`.
- Miscellaneous observability and reliability registers: `MISC`, `LATENCY_SAMPLING`, performance counters, `EDC_CNT`, `EDC_CNT2`, `EDC_CNT3`, DSM controls, `CGTT_CLK_CTRL`, `EDC_MODE`, `ERR_STATUS`, `MISC2`, and `ADDRDEC_SELECT`.

The `MMEA2` block begins at `0x0500` and this chunk covers 115 offsets through the early `ADDRDEC0` column-select registers. The rest of `MMEA2`, plus later `MMEA3..7` and VM/L2/L1 register families, are outside this chunk.

## Control Flow

There is no runtime control flow in this header. Control flow is created by AMDGPU code that includes the header and passes these macros into SOC15 register helpers. The relevant consumer is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, which includes:

- `mmhub/mmhub_9_4_1_offset.h`
- `mmhub/mmhub_9_4_1_sh_mask.h`
- `mmhub/mmhub_9_4_1_default.h`

Typical use follows this pattern:

1. Driver code names a register with a macro from this file, for example `mmDAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, `mmDAGB0_CNTL_MISC2`, or `mmMMEA0_EDC_CNT`.
2. SOC15 helper macros combine the offset with the `MMHUB` IP block, instance number, and base-index information.
3. Read/write helpers such as `RREG32_SOC15_OFFSET()`, `WREG32_SOC15_OFFSET()`, `SOC15_REG_ENTRY()`, `SOC15_REG_ENTRY_OFFSET()`, and `SOC15_REG_FIELD()` access the hardware register or describe it for RAS handling.
4. If fields are manipulated, the paired shift/mask header supplies `REG_SET_FIELD()`, `REG_GET_FIELD()`, or direct mask operands.

Two concrete control patterns depend on the offsets in this chunk:

- `mmhub_v9_4_init_snoop_override_regs()` computes the distance between `mmDAGB1_WRCLI_GPU_SNOOP_OVERRIDE` and `mmDAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, then iterates over DAGB instances to set SDMA GPU snoop override bits. The fixed `0x80` spacing between DAGB blocks is part of that contract.
- `mmhub_v9_4_update_medium_grain_clock_gating()` computes the distance between `mmDAGB1_CNTL_MISC2` and `mmDAGB0_CNTL_MISC2`, then toggles clock-gating disable bits over the DAGB instances using offsets from this header and masks from the shift/mask header.

## State And Persistence Behavior

The header itself is stateless. It persists only as source metadata compiled into register access expressions. The state described by these offsets lives in MMHUB hardware registers:

- DAGB arbitration and flow-control state for read/write clients, virtual channels, maximum burst sizes, lazy timers, pending request status, credits, and FIFO state.
- DAGB clock and power control state through CGTT and `CNTL_MISC2` registers.
- DAGB coherency override state, notably SDMA-related write-client GPU snoop override configuration.
- MMEA memory-address routing state for DRAM, GMI, IO, and MAM paths.
- MMEA address normalization and address-decoder state that maps memory addresses onto banks, pseudo-channels, chip selects, harvested channels, and memory-controller layout.
- MMEA SDP arbitration, priority, credit, reserve, and request-control state.
- MMEA reliability and diagnostics state, including EDC counters, error status, DSM controls, latency sampling, and performance counters.

Values written to these hardware registers persist until reset, reprogramming, power-state transitions, firmware/hardware ownership changes, or device removal. Driver initialization, GART enablement, reset recovery, suspend/resume, RAS query/reset, and clock-gating transitions must assume that MMHUB state can need reprogramming or rereading after those events.

## Dependencies And Integration Points

Primary dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c` is the direct MMHUB 9.4 consumer.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h` supplies matching bit shifts and masks for the registers named here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_default.h` supplies matching default values.
- SOC15 access infrastructure in `soc15.h` and `soc15_common.h` interprets the `mm*` offsets and `_BASE_IDX` constants.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c` selects `mmhub_v9_4_funcs`/RAS hooks for applicable devices and contains related golden-register programming for DAGB/MMEA names in the broader GMC v9 code.

Important integration details:

- The `DAGB` block spacing is used arithmetically by the driver. If any offset drifted from the generated `0x80` spacing, loops that program multiple DAGB instances would access the wrong registers.
- `mmhub_v9_4.c` uses `MMHUB_NUM_INSTANCES` and `MMHUB_INSTANCE_REGISTER_OFFSET` for hub instances, while this header supplies offsets inside a hub instance.
- RAS support in `mmhub_v9_4.c` builds `soc15_reg_entry` arrays for `MMEA*_EDC_CNT`, `MMEA*_EDC_CNT2`, `MMEA*_EDC_CNT3`, and `MMEA*_ERR_STATUS`; this chunk provides the complete `MMEA0` and `MMEA1` offsets and only the early part of `MMEA2`.
- Register names are generated from AMD hardware specifications and are internal kernel-driver ABI, not userspace ABI.

## Risks And Edge Cases

- Cross-generation mismatch: these offsets must be paired with the MMHUB 9.4.1 shift/mask/default headers. Combining offsets from this header with masks from another ASIC generation can compile but access or program the wrong hardware fields.
- Arithmetic spacing dependency: code derives per-instance distances from `DAGB1 - DAGB0` offsets. Mechanical changes to only one repeated block would break all looped DAGB programming.
- Base-index risk: every `_BASE_IDX` in this chunk is `1`. Changing base-index values without corresponding SOC15 table changes would redirect register accesses even if offsets remain correct.
- Partial block boundary: this research chunk stops inside `MMEA2`. RAS and address-decoder analysis for `MMEA2` is incomplete until later chunks cover the remaining `MMEA2` registers.
- Hardware-side consequences: incorrect DAGB offsets can affect SDMA coherency, outstanding request limits, clock gating, pending-status reporting, and performance-counter selection. Incorrect MMEA offsets can affect memory address decoding, channel/bank hashing, harvested-memory configuration, SDP arbitration, and RAS error reporting.
- Generated-file maintenance risk: the repeated register families make manual edits hard to audit. Regenerating from the authoritative hardware database is safer than hand-editing individual constants.
- Reserved and gap handling: the header includes explicit `RESERVE*` names and also leaves numeric holes in some blocks. Callers should not infer that every missing offset is safe or available.

## Test Signals

Useful validation signals are mostly build-time, register-access, and hardware-behavior checks:

- Compile AMDGPU configurations that include `mmhub_v9_4.c`; unresolved `mmDAGB*` or `mmMMEA*` names indicate offset-header drift.
- Check generated-header consistency: each register offset in this chunk should have the matching `_BASE_IDX` macro, and repeated `DAGB` blocks should preserve the `0x80` stride.
- Exercise GART/MMHUB initialization on MMHUB 9.4 hardware, especially paths that call `mmhub_v9_4_gart_enable()` and then initialize snoop overrides, TLB/cache settings, system domain, VMID configuration, and invalidation.
- Verify SDMA coherency behavior after `mmhub_v9_4_init_snoop_override_regs()`; failures may point at `WRCLI_GPU_SNOOP_OVERRIDE` offsets or block-stride assumptions.
- Validate clock-gating toggles with `mmhub_v9_4_set_clockgating()` and `mmhub_v9_4_get_clockgating()`; incorrect `DAGB*_CNTL_MISC2` offsets should show up as flags not matching hardware state or as register access errors.
- Run RAS query/reset paths for MMHUB v9.4 and confirm `MMEA0`/`MMEA1` EDC counters and error-status registers read coherently.
- Compare against hardware golden settings and generated register dumps when available, especially for `DAGB` client programming and `MMEA` priority/address-decoder state.

## Chunk Scope Notes

This document covers only lines 1-2477 of `mmhub_9_4_1_offset.h`. The source file continues beyond this point with the rest of `MMEA2`, later `MMEA` instances, and additional MMHUB register blocks. The final per-file research document should reconcile this chunk with later chunk documents before drawing conclusions about the complete MMHUB 9.4.1 register map.

### subset-b-002838: lines 2478-4976

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_offset.h lines 2478-4976

## Scope

This chunk covers the middle of the generated MMHUB 9.4.1 register offset header. It starts in the tail of the `mmhub_ea_mmeadec2` block at `mmMMEA2_ADDRDEC0_COL_SEL_HI_CS01` and ends in the beginning of `mmhub_dagb_dagbdec6` at `mmDAGB6_RDCLI_TLB_PENDING`. The covered range is a pure preprocessor register map: it contains `#define` constants for MMIO register offsets plus matching `_BASE_IDX` constants, with no C functions, structs, data storage, or executable control flow.

The chunk defines 1,214 register offset macros and 1,213 matching base-index macros. Most macros use base index `1`; the legacy aliases `mmMC_VM_XGMI_LFB_CNTL` and `mmMC_VM_XGMI_LFB_SIZE` use base index `0`. The visible address blocks are:

- Tail of `mmhub_ea_mmeadec2`, including MMEA2 address decoder, IO arbitration, SDP, performance counter, EDC, DSM, clock, error, and address-decoder selection registers.
- Full `mmhub_ea_mmeadec3` and `mmhub_ea_mmeadec4` blocks, with repeated DRAM/GMI/IO client grouping, priority, address normalization, address hashing, channel/row/column mapping, performance counter, EDC, DSM, and clock/error families.
- `mmhub_pctldec0`, covering MMHUB deep-sleep, power-gating/deep-sleep slice controls, RENG RAM windows, and state-save range/exclusion registers for UTCL2 and slices 0 through 4.
- L1 and L2 translation blocks: `mmhub_l1tlb_vml1dec`, `mmhub_l1tlb_vml1pldec`, `mmhub_l1tlb_vml1prdec`, `mmhub_utcl2_atcl2dec`, `mmhub_utcl2_vml2pfdec`, and the large `mmhub_utcl2_vml2vcdec` VM-context window.
- Shared VM PF/VC/HV windows for MMIO apertures, framebuffer/system aperture settings, cacheable/local HBM ranges, XGMI LFB, VF framebuffer offsets, MARC windows, IOMMU, PCIe ATS, active function ID, and GPU IOV enablement.
- ATC L2 and VM L2 performance counter control/result windows.
- Complete `mmhub_dagb_dagbdec5` and the first read-side part of `mmhub_dagb_dagbdec6`, defining DAGB client, credit, virtual-channel, pending, clock-gating, FIFO, and perfcounter registers.

## Purpose

`mmhub_9_4_1_offset.h` is a generated hardware ABI header. This chunk gives AMDGPU code symbolic names for MMHUB MMIO register offsets on ASICs using the MMHUB 9.4.1 register map. The paired `_BASE_IDX` constants tell SOC15-style register helpers which base segment to combine with the offset when calculating the final MMIO address.

The constants here are consumed with AMDGPU register access helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and field helpers that pair this offset header with the sibling `mmhub_9_4_1_sh_mask.h` bit definitions. The offset header says where each register lives; the mask header says how to encode fields inside the register; the driver logic supplies sequencing, reset, timeout, and policy.

## Important Macro Families

### MMEA2/MMEA3/MMEA4 EA Blocks

The MMEA sections describe memory/EA address decode and arbitration blocks. The chunk begins after most of MMEA2 has already been emitted, but it still includes MMEA2 `ADDRDEC0` tail registers, full `ADDRDEC1` and `ADDRDEC2` channel-select/register-map families, global normalizer controls, IO client-to-group mappings, IO priority/urgency/quantum controls, SDP arbitration/priority/credit/tag reserve controls, performance counter registers, EDC counters, DSM controls, clock-gating control, error status, miscellaneous controls, and `ADDRDEC_SELECT`.

`MMEA3` and `MMEA4` are complete and follow the same generated shape:

- DRAM and GMI read/write client-to-group maps, group-to-VC maps, lazy timers, CAM controls, page-burst controls, fixed/age/queuing/urgency priority registers, urgency masking, and priority quantum registers.
- Address normalization base/limit/offset windows `ADDRNORM_BASE_ADDR0..5`, `LIMIT_ADDR0..5`, selected offset registers, DRAM/GMI hole controls, and non-power-of-two channel configuration.
- Address decoder bank/misc configuration, DRAM/GMI hash registers for banks, pseudo-channel, chip-select, and harvest-enable state.
- Three address decoder instances `ADDRDEC0..2`, each with base addresses for chip-selects and secondary chip-selects, address masks, address configuration, address/column selectors, and row-map selectors.
- IO, SDP, performance counter, EDC, DSM, clock, error, miscellaneous, and decoder-select registers.

These names are primarily used by memory controller initialization, discovery, diagnostics, and low-level bring-up code that needs to route memory requests across HBM/DRAM, GMI/XGMI, IO groups, chip-selects, banks, pseudo-channels, and harvested resources.

### PCTL Power and State-Save Block

`PCTL0` defines MMHUB power/deep-sleep control and register-save address ranges. It starts with global control, deep-sleep override, and power-gating ignore registers, then repeats slice-local `DAGB_BUSY`, `DS_ALLOW`, `DS_ALLOW_IB`, `MISC`, `RENG_EXECUTE`, `RENG_RAM_INDEX`, and `RENG_RAM_DATA` registers for slices 0 through 4 plus UTCL2.

The state-control families define five save ranges and two exclusion sets for UTCL2 and each slice. These offsets are integration points for suspend/resume, power gating, deep-sleep entry/exit, and register save/restore paths. Because these are offset constants only, they do not encode which ranges should be enabled or when the RENG RAM windows can be safely accessed.

### L1 TLB, ATC L2, and VM L2 Control

The L1 block exposes `VML1_0_MC_VM_MX_L1_TLB0_STATUS` through `TLB7_STATUS`, plus L1 performance counter select/result registers. The ATC L2 block exposes control, cache-data, status, memory-power, clock-gating, DSM index/control, and runtime-class registers.

`VML2PF0` covers VM L2 control and global fault handling registers: L2 control/status, dummy page fault control/address, protection fault controls/status/address/default address, context identity aperture registers, L2 bank-select reserved context IDs, cache parity, runtime class, and clock-gating control. These offsets are central to GPUVM translation, fault reporting, identity mapping, and low-level TLB/cache management.

### VM Context Window

`VML2VC0` is the densest VM section in this chunk. It defines:

- VM context control registers for contexts 0 through 15 plus `VM_CONTEXTS_DISABLE`.
- Invalidate engine semaphore, request, acknowledge, and address-range registers for engines 0 through 17.
- Page-table base, start, and end address low/high registers for contexts 0 through 15.

This block is a direct integration point for VM context setup and TLB invalidation. Driver code programs page-table roots and apertures, issues invalidate requests through engine-specific request registers, then waits for matching acknowledge state. The header itself has no polling logic; incorrect offsets here would send invalidation or page-table programming to the wrong engine/context and can cause stale translations, page faults, or GPU hangs.

### Shared VM PF/VC/HV Windows

`VMSHAREDPF0` contains PF-side memory aperture and steering registers: NB MMIO base/limit, PCI control/arbitration, top-of-DRAM values, framebuffer offset, system aperture default address, VM steering, shared virtualization reset request, memory power, cacheable DRAM ranges/control, local HBM range/lock, APT control, and XGMI local framebuffer controls. The bare `mmMC_VM_XGMI_LFB_CNTL` and `mmMC_VM_XGMI_LFB_SIZE` aliases in this area use base index `0`, unlike the nearby MMHUB-specific base-index-1 symbols.

`VMSHAREDVC0` contains VC-visible framebuffer location, AGP aperture, system aperture low/high, and MX L1 TLB control offsets. `VMSHAREDHV0` contains virtualization/hypervisor-visible registers: per-VF framebuffer size/offset for VFs 0 through 15, IOMMU MMIO/control/performance controls, four MARC base/relocation/length windows, PCIe ATS control for PF and VFs 0 through 15, UTCL2 clock-gating, active function ID, and XGMI GPU IOV enablement.

These families connect MMHUB memory translation to SR-IOV, GPU IOV, XGMI, PCIe ATS, and physical aperture partitioning. They are privilege-sensitive and usually coordinated with PF/hypervisor paths rather than ordinary queue execution.

### Performance Counter Windows

The chunk provides performance counter result and configuration offsets in several blocks:

- MMEA2/MMEA3/MMEA4 `PERFCOUNTER_LO`, `PERFCOUNTER_HI`, `PERFCOUNTER0_CFG`, `PERFCOUNTER1_CFG`, and result control.
- L1 TLB performance config/result via `VML1PL0` and `VML1PR0`.
- ATC L2 performance result/config via `ATCL2PFCNTR0` and `ATCL2PFCNTL0`.
- VM L2 performance config/result via `VML2PL0` and `VML2PR0`.
- DAGB5 performance counter result/config/result-control.

The offsets support debug/profiling code, but event IDs, modes, and result control fields come from the matching shift/mask header and hardware documentation.

### DAGB5 and DAGB6

`DAGB5` is complete in this chunk and defines a read/write data/address gateway block. It includes read clients `RDCLI0..15`, read control/GMI/address/output/lazy/clock controls, read address DAGB burst/lazy controls, read virtual-channel controls `RD_VC0..7`, TLB credit, and read-side pending status registers. It then mirrors the same shape for write clients `WRCLI0..15`, write control/GMI/address/output/data/lazy/clock controls, write address/data DAGB burst/lazy controls, write virtual-channel controls, TLB/data/misc credits, GPU snoop override controls, write pending status registers, FIFO full/empty and credit-full status, performance counters, and reserved offsets.

`DAGB6` begins at base address `0x74200` and is only partially covered: this chunk includes the read-side client, control, GMI, address, output, lazy, clock, VC, TLB credit, and pending registers through `RDCLI_TLB_PENDING`. The write-side and tail registers for DAGB6 belong to the next chunk. DAGB registers are relevant to memory request routing, virtual-channel arbitration, credit management, clock gating, and hang diagnostics.

## Control Flow and State Behavior

There is no executable control flow in this header. The compile-time behavior is macro substitution: AMDGPU code names a register such as `mmVML2VC0_VM_INVALIDATE_ENG0_REQ`, the compiler substitutes the numeric offset, and register helper macros combine that offset with the base index and block base to form an MMIO access.

The state represented by this chunk lives in GPU hardware. Some registers are durable configuration state, such as address decoder mapping, VM context page-table bases, aperture limits, PCTL save ranges, priority/credit controls, and virtualization apertures. Others are latched or live status registers, such as TLB status, L2 status, fault status/address, DAGB pending/FIFO/credit state, EDC counters, and error status. Some registers are command or handshake registers, especially VM invalidation request/ack/semaphore registers, virtualization reset request, RENG execute windows, and indirect RAM index/data windows.

Persistence across suspend, reset, or power gating is not expressed in this header. PCTL state-save ranges and exclusion sets imply that other driver code selects which MMHUB/UTCL2/slice registers are saved or skipped during power-state transitions.

## Dependencies and Integration Points

This file depends on the generated AMD ASIC register-header convention:

- Sibling `mmhub_9_4_1_sh_mask.h` defines field shifts and masks for the offsets named here.
- Sibling default headers, when present, define reset/default values.
- AMDGPU SOC15/MMIO helpers consume the `mm*` offset and `*_BASE_IDX` macros.
- The names and offsets must match the hardware register database for MMHUB 9.4.1.

Likely source-tree integration points include MMHUB/GMC initialization, GPUVM setup, fault handling, TLB invalidation, XGMI/HBM aperture setup, SR-IOV/GPU IOV partitioning, suspend/resume register save/restore, power-management deep-sleep gating, performance counter plumbing, and hang/debug dumps that read DAGB, TLB, fault, pending, and credit state.

Cross-chunk dependencies are important. This chunk starts inside `MMEA2`, so the beginning of that address block is in the previous chunk. It ends inside `DAGB6`, so the remaining write-side and tail DAGB6 offsets are in the next chunk. A final merged report should join those families before making whole-file conclusions about complete block coverage.

## Risks

- Offset drift is high impact. A wrong register offset or base index can write a different MMHUB register than intended, which may corrupt VM context state, address decode, virtualization apertures, power-state save ranges, or DAGB routing.
- Repeated generated families are easy to mis-edit. MMEA3 and MMEA4 are nearly identical, as are repeated VM context, invalidate-engine, VF, slice, and DAGB client groups. A single skipped index or copied value can be hard to spot by review.
- Base-index mismatches matter. Most macros here use `_BASE_IDX 1`, while `mmMC_VM_XGMI_LFB_CNTL` and `mmMC_VM_XGMI_LFB_SIZE` use `_BASE_IDX 0`; code that assumes one base for all nearby symbols can access the wrong segment.
- VM invalidation sequencing is fragile. The header exposes semaphore/request/ack/range offsets but not ordering or timeout rules. Consumers must still issue invalidates and wait for acknowledgements correctly.
- Virtualization and aperture registers are privilege-sensitive. Per-VF framebuffer offsets, PCIe ATS controls, MARC windows, active function ID, GPU IOV, and XGMI LFB controls can break isolation or address translation if programmed with wrong offsets or wrong field encodings.
- PCTL and deep-sleep registers interact with power management. Bad save ranges, exclusion sets, or slice deep-sleep controls can cause state loss across suspend/resume or power-gated transitions.
- DAGB credit and pending registers are likely used for hang diagnosis. Incorrect offsets can hide the true blocked client or make recovery code act on the wrong gateway block.

## Test and Validation Signals

Useful validation is mostly build, bring-up, and hardware integration coverage:

- Build AMDGPU with MMHUB 9.4.1 support enabled to catch missing or renamed register macros.
- Boot/init tests on matching ASICs should cover GMC/MMHUB bring-up, address-decoder setup, HBM/GMI/XGMI aperture programming, and memory request routing.
- GPUVM tests should cover VM context page-table base/start/end programming, context enable/disable, TLB invalidation engines 0 through 17, and L2/L1 fault/status reporting.
- Page-fault and protection-fault tests should verify `VML2PF0` status/address/default-address paths report the expected fault information.
- Suspend/resume, BACO, power-gating, and deep-sleep tests should exercise `PCTL0` deep-sleep, state-save range, exclusion, RENG, and slice controls.
- SR-IOV/GPU IOV validation should cover per-VF framebuffer offsets, PCIe ATS controls, MARC windows, active function ID, shared virtualization reset, and XGMI GPU IOV enablement.
- Performance/debug tests should read and program MMEA, L1/L2, ATC, and DAGB performance counter config/result registers.
- Hang/debug dumps should confirm DAGB5 and DAGB6 read-side pending, FIFO, credit, and VC status offsets line up with hardware-visible blocked clients.

## Unresolved Cross-Chunk References

This chunk begins in the middle of `mmhub_ea_mmeadec2`; prior MMEA2 DRAM/GMI/address-normalization/hash and `ADDRDEC0` leading registers are not included here. It ends in the middle of `mmhub_dagb_dagbdec6`; the DAGB6 write-side, data-credit, pending, FIFO, perfcounter, and reserve registers are not included here. The merge/reconciliation lane should combine adjacent chunk reports before producing a final per-file research document for `mmhub_9_4_1_offset.h`.

### subset-b-002839: lines 4977-7451

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_offset.h lines 4977-7451

## Scope

This chunk covers a generated AMD MMHUB 9.4.1 register-offset header slice. It starts inside the `mmhub_dagb_dagbdec6` address block at `mmDAGB6_RDCLI_TLB_PENDING_BASE_IDX`, then covers all of `mmhub_dagb_dagbdec7`, three MMEA decoder blocks, the second PCTL block, the `:1` L1/UTC virtual-memory blocks, and the opening portion of `mmhub_utcl2_vml2vcdec:1`. It ends at `mmVML2VC1_VM_CONTEXT9_PAGE_TABLE_START_ADDR_LO32_BASE_IDX`, before the remaining context start/end address macros.

The slice contains 2,431 `#define` lines: 1,215 register offset macros and 1,216 `_BASE_IDX` companion macros. Every register in this range uses `_BASE_IDX 1`, reflecting the SOC15 register base instance used by the generated offset table. There are no C functions, structs, enums, storage definitions, includes, or runtime logic here. Although the source tree path is under a local `ceph-client` mirror, this file is AMDGPU hardware register metadata, not distributed filesystem code.

## Purpose

The purpose of this header section is to name MMHUB 9.4.1 register offsets so AMDGPU code can program or read the correct MMIO locations through SOC15 register helpers. The companion `mmhub_9_4_1_sh_mask.h` header defines field shifts and masks; this file supplies the register names, offsets, and base-index selection that those fields attach to.

The covered registers describe:

- DAGB slice 6 tail and DAGB slice 7 traffic arbitration, credits, pending state, status, and performance counters.
- MMEA slices 5, 6, and 7 memory-client grouping, DRAM/GMI/IO/SDP arbitration, address normalization, error, and observability registers.
- PCTL1 deep-sleep, power-gating, RENG RAM, and state-save range controls for UTCL2 plus five slices.
- L1 TLB status and UTCL2/VML2 performance, invalidate, fault, and context-page-table registers for hub instance `:1`.

## Important Macro Families

### DAGB6 Tail And DAGB7

The first lines complete `DAGB6` by providing the `_BASE_IDX` for `mmDAGB6_RDCLI_TLB_PENDING`, then define read-side `OARB` and `OSD` pending offsets, all write clients `WRCLI0..15`, write control and GMI control, address/data DAGB routing controls, output burst and lazy-timer controls, clock-gating controls, write VC controls `WR_VC0_CNTL..WR_VC7_CNTL`, TLB/data/misc credits, GPU snoop override registers, write pending-state registers, FIFO/credit fullness status, performance counters, and reserved offsets through `mmDAGB6_RESERVE13`.

The `mmhub_dagb_dagbdec7` block begins at base address `0x74400` and is complete in this chunk. It defines the same broad DAGB pattern for slice 7: read client offsets, read aggregate control, read-side burst/timer/clock/VC/credit/status/performance registers, write client offsets, write-side control and pending registers, FIFO/fullness observability, and reserve registers. These macros are consumed as register names such as `mmDAGB7_RDCLI0`, `mmDAGB7_RD_CNTL`, `mmDAGB7_WR_CNTL`, and `mmDAGB7_PERFCOUNTER*_CFG`.

### MMEA5, MMEA6, And MMEA7

The `mmhub_ea_mmeadec5`, `mmhub_ea_mmeadec6`, and `mmhub_ea_mmeadec7` blocks start at base addresses `0x74a00`, `0x74f00`, and `0x75400`. Each block has the same generated register layout, with macro prefixes `mmMMEA5_`, `mmMMEA6_`, and `mmMMEA7_`.

Each MMEA block defines client-to-group and group-to-VC mapping registers for DRAM, GMI, IO, and SDP traffic; read and write lazy timers; CAM controls; page-burst controls; priority aging, queueing, fixed-priority, urgency, urgency masking, and quantum registers; address-normalization base/limit/offset entries; GMI peer/link address normalization entries; per-destination credit and write-credit controls; channel control/status; clock-gating controls; debug and reserve registers; and `ERR_STATUS`.

These offsets are the address side of MMHUB external-address arbitration. They let driver code configure how memory clients are grouped, how those groups map onto virtual channels, how arbitration policy differs between DRAM/GMI/IO/SDP paths, and how normalized address windows are represented.

### PCTL1

The `mmhub_pctldec1` block starts at base address `0x76300`. It defines `mmPCTL1_CTRL`, MMHUB deep-sleep interface and override registers, power-gating/deep-sleep ignore controls, per-slice DAGB busy and deep-sleep-allow registers for slices 0 through 4, UTCL2 and slice misc registers, RENG execute/index/data registers, and state-controller save ranges and exclusion sets.

The repeated `STCTRL_REGISTER_SAVE_RANGE0..4` and `STCTRL_REGISTER_SAVE_EXCL_SET0..1` families appear for UTCL2 and for each slice `SLICE0..SLICE4`. These offsets are used by power-management or reset flows that need hardware-assisted register save/restore boundaries and exclusions.

### L1 TLB And UTCL2/VML2 Instance 1

The `mmhub_l1tlb_vml1dec:1` block at base address `0x76500` defines `mmVML1_1_MC_VM_MX_L1_TLB0_STATUS` through `TLB7_STATUS`. The following `mmhub_l1tlb_vml1pldec:1` and `mmhub_l1tlb_vml1prdec:1` blocks define performance counter low/high/config offsets for the L1 TLB pipe-left and pipe-right blocks.

The `mmhub_utcl2_atcl2dec:1` block at base address `0x76600` covers ATCL2 memory power and performance counter offsets. The `mmhub_utcl2_vml2pfdec:1` block at `0x76700` covers VML2 prefetch controls, fault-clear/status/address registers, default-page and snapshot controls, VMID lookup range registers, and performance counters.

The `mmhub_utcl2_vml2vcdec:1` block starts at base address `0x76800` and is only partially covered here. This chunk includes VM L2 control and protection fault controls, bank select and cache controls, performance counters, invalidate request and acknowledgment registers for engines 0 through 17, invalidate address range low/high registers for engines 0 through 17, context page-table base address low/high registers for contexts 0 through 15, and context page-table start address low/high registers through context 9 low. The remaining context start and end address registers continue in the next chunk.

## Control Flow

This header has no executable control flow. Its effect is compile-time symbol substitution: AMDGPU code references a macro such as `mmVML2VC1_VM_INVALIDATE_ENG0_REQ` or `mmMMEA7_ERR_STATUS`, the preprocessor substitutes the register offset, and SOC15 register accessors combine that offset with the relevant base instance selected by `_BASE_IDX`.

The runtime sequencing belongs to consumers in MMHUB, GMC, VM, reset, clock-gating, power-management, and diagnostics code. Those consumers decide when to program DAGB QoS/credit state, when to configure MMEA arbitration and address normalization, when PCTL1 register-save or deep-sleep controls may be changed, and when VML2 invalidate/fault/context registers are written or polled.

## State And Persistence Behavior

The file itself stores no software state and persists nothing. It describes MMIO-backed hardware state. Register contents generally persist in hardware until reset, power-gating, suspend/resume restore, driver reprogramming, or hardware self-update, depending on the individual register semantics defined by the ASIC.

Important hardware state represented by this slice includes DAGB per-client arbitration and pending masks, write snoop overrides, credit accounting, FIFO/fullness status, and performance counters; MMEA memory-client grouping, priority and urgency policy, address normalization windows, destination credits, channel/debug state, and error status; PCTL1 deep-sleep and state-save configuration; L1 TLB status; VML2 prefetch/fault/snapshot/performance state; VML2 invalidate request/ack state; and VML2 per-context page-table base/start address state.

Several register names imply side effects or sequencing sensitivity even though this header cannot encode those rules: fault clear, invalidate request/acknowledge, performance counter clear or result controls, deep-sleep overrides, RENG execute controls, and state-save range programming. Consuming code must preserve the hardware-defined read/modify/write, polling, and ordering requirements.

## Dependencies And Integration Points

This chunk depends on AMD's generated MMHUB 9.4.1 register database. It must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h`, which supplies the field-level shifts and masks for these register names.
- Other generated MMHUB 9.4.1 headers, including default-value headers when present.
- SOC15 base-address tables and AMDGPU register accessor macros such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

Expected consumers are AMDGPU MMHUB/GMC code paths for ASICs using MMHUB 9.4.1. Integration points include GPU VM hub setup, VM context page-table programming, VM invalidate issuance and acknowledgment polling, memory-client QoS setup, DRAM/GMI/IO/SDP arbitration setup, GMI peer addressing, clock-gating and deep-sleep policy, reset and suspend/resume register save/restore, fault reporting, error decoding, and performance/debug counter collection.

The `:1` suffix in the address-block comments and macro names such as `mmVML1_1_*` and `mmVML2VC1_*` is significant. It distinguishes the second MMHUB/UTCL2/VML2 instance from instance 0. Code that mixes instance-0 offsets with these instance-1 macros can target the wrong hub.

## Risks And Edge Cases

- Offset drift is high impact. A wrong value can direct MMIO reads or writes to an unrelated MMHUB register while still compiling cleanly.
- `_BASE_IDX` consistency matters. Every macro in this chunk uses base index `1`; using access helpers with a different base instance can corrupt another hub or silently read stale state.
- The chunk boundaries are artificial. This slice starts after the `mmDAGB6_RDCLI_TLB_PENDING` offset itself and ends before all `VML2VC1` context start/end address registers are present, so final file-level analysis must merge neighboring chunks before making complete claims.
- Repeated generated families are copy-sensitive. `DAGB6`/`DAGB7`, `MMEA5`/`MMEA6`/`MMEA7`, and context or invalidate-engine arrays have many near-identical names where a one-digit index error changes the hardware client, memory slice, VM context, or invalidate engine.
- VM invalidate registers are sequencing-sensitive. Request, acknowledge, and address-range registers must be programmed and polled in the order required by hardware; this header provides only addresses.
- VM context page-table base and start address registers are split low/high. Consumers must pair the correct low/high halves and preserve address alignment and logical page-number width.
- PCTL1 deep-sleep and register-save controls affect power and reset behavior. Bad ranges or exclusions can leave hardware state unrestored or block low-power entry.
- MMEA arbitration and address-normalization registers affect real memory routing and QoS. Bad group maps, VC maps, priority policies, credit limits, or address windows can cause starvation, incorrect peer/GMI routing, or memory faults.
- Status, fault, and error registers may be sticky, clear-on-write, or read-side-effecting depending on the hardware definition. Generic read/modify/write patterns are risky unless matched to the field semantics in the shift/mask and programming guides.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU with MMHUB 9.4.1 support enabled; renamed, missing, or malformed macros should surface as compile failures in MMHUB/GMC/VM users.
- Mechanically compare this offset header with AMD's authoritative register database and verify that each register macro has the expected `_BASE_IDX` and matching field definitions in `mmhub_9_4_1_sh_mask.h`.
- Cross-check repeated register families for contiguous offsets and expected cardinality: DAGB7 clients and VC controls, MMEA5/6/7 matching layouts, PCTL1 UTCL2 plus slices 0-4 state-save ranges, VML2 invalidate engines 0-17, and VM contexts 0-15.
- Exercise GPU VM workloads that create, update, and invalidate page tables; verify invalidate acknowledgments complete and VM faults decode through the expected `VML2PF1`/`VML2VC1` registers.
- Run memory traffic across DRAM, GMI, IO, and SDP paths under graphics, compute, SDMA, and peer traffic; watch for hangs, throttling, starvation, or unexpected fault/error status.
- Test suspend/resume, GPU reset, and clock/deep-sleep transitions that depend on PCTL1 state-save and deep-sleep controls.
- Validate performance/debug paths by programming DAGB, L1TLB, ATCL2, VML2PF, and VML2VC counters and confirming low/high counter reads and result-control behavior.
- Where supported, inject or observe VM and MMHUB faults and confirm address/context/engine attribution is plausible for the instance-1 registers covered here.

## Cross-Chunk Notes

The previous chunk is needed for the beginning of `mmhub_dagb_dagbdec6`, including the offset half of `mmDAGB6_RDCLI_TLB_PENDING`. The next chunk is needed for the rest of `VML2VC1_VM_CONTEXT*_PAGE_TABLE_START_ADDR_*`, the corresponding end address registers, and any later MMHUB 9.4.1 offset blocks. The final per-file document should reconcile those boundaries before summarizing the complete `mmhub_9_4_1_offset.h` register map.

### subset-b-002840: lines 7452-7789

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_offset.h lines 7452-7789

## Scope

This chunk is the tail of the generated AMD MMHUB 9.4.1 register-offset header. It contains only C preprocessor register-address macros and `_BASE_IDX` companion macros; there are no functions, structs, enums, or executable control-flow statements in the chunk. The covered range closes the `mmhub_utcl2_vml2vcdec:1` VM-context address block, then defines instance-1 shared PF/VC/HV MMHUB aperture and virtualization registers, ATC L2 and VM L2 performance-counter registers, and finally the header guard terminator.

The header is included by `drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c` along with the matching `mmhub_9_4_1_sh_mask.h` and `mmhub_9_4_1_default.h` files. The offset macros are the symbolic register numbers passed to AMDGPU/SOC15 access helpers such as `SOC15_REG_OFFSET()`, `RREG32_SOC15_OFFSET()`, and `WREG32_SOC15_OFFSET()`.

## Purpose

The purpose of this chunk is to publish the hardware register map for the second MMHUB instance's VM-facing address blocks on MMHUB 9.4.1 ASICs. Each `mm...` macro gives the register index within the SOC15 MMHUB register space, and each `_BASE_IDX` macro selects base-index `1` for the SOC15 register lookup tables. Driver code can then address the register either directly by the instance-1 symbol or by using an instance-0 symbol plus `MMHUB_INSTANCE_REGISTER_OFFSET` when programming both hubs.

The range is important to GPU memory-management setup because it names registers for:

- VM context page-table start and end bounds for `VML2VC1`.
- Shared PF-visible aperture, default page, DRAM/HBM, XGMI, and reset controls for `VMSHAREDPF1`.
- Shared VC-visible framebuffer, AGP, system aperture, and L1 TLB control for `VMSHAREDVC1`.
- Hypervisor/SR-IOV controls for per-VF framebuffer partitioning, MARC regions, IOMMU/ATS, active function selection, clock gating, and XGMI GPUIOV enables for `VMSHAREDHV1`.
- ATC L2 and VM L2 performance-counter programming and result registers for instance 1.

## Register Groups

### VML2VC1 page-table address bounds

The first part of the chunk continues the `mmhub_utcl2_vml2vcdec:1` address block. It starts mid-series at `mmVML2VC1_VM_CONTEXT9_PAGE_TABLE_START_ADDR_HI32` and then defines start-address low/high pairs for contexts 10 through 15:

- `mmVML2VC1_VM_CONTEXT9_PAGE_TABLE_START_ADDR_HI32` at `0x3a9e`.
- `mmVML2VC1_VM_CONTEXT10_PAGE_TABLE_START_ADDR_LO32` through `mmVML2VC1_VM_CONTEXT15_PAGE_TABLE_START_ADDR_HI32`, covering offsets `0x3a9f` through `0x3aaa`.

It then defines page-table end-address low/high pairs for VM contexts 0 through 15:

- `mmVML2VC1_VM_CONTEXT0_PAGE_TABLE_END_ADDR_LO32` and `_HI32` at `0x3aab` and `0x3aac`.
- Sequential pairs through `mmVML2VC1_VM_CONTEXT15_PAGE_TABLE_END_ADDR_LO32` and `_HI32` at `0x3ac9` and `0x3aca`.

The matching shift/mask header identifies the LO32 fields as `LOGICAL_PAGE_NUMBER_LO32` and the HI32 fields as `LOGICAL_PAGE_NUMBER_HI4`. The matching default header initializes these start/end bounds to zero. In `mmhub_v9_4.c`, the driver primarily uses the instance-0 `VML2VC0` names plus `hubid * MMHUB_INSTANCE_REGISTER_OFFSET` and per-context distances to program both MMHUB instances, so these `VML2VC1` names are the generated direct-address aliases for the same second-instance hardware window.

### VMSHAREDPF1 shared PF controls

The `mmhub_utcl2_vmsharedpfdec:1` block begins at source line 7543 with base address comment `0x76b90`. This group defines offsets `0x3ae4` through `0x3af9`:

- Northbridge/MMIO and PCI aperture controls: `MC_VM_NB_MMIOBASE`, `MC_VM_NB_MMIOLIMIT`, `MC_VM_NB_PCI_CTRL`, `MC_VM_NB_PCI_ARB`, `MC_VM_NB_TOP_OF_DRAM_SLOT1`, `MC_VM_NB_LOWER_TOP_OF_DRAM2`, and `MC_VM_NB_UPPER_TOP_OF_DRAM2`.
- Framebuffer and default-page controls: `MC_VM_FB_OFFSET`, `MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB`, and `MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_MSB`.
- Routing, reset, and low-power controls: `MC_VM_STEERING`, `MC_SHARED_VIRT_RESET_REQ`, and `MC_MEM_POWER_LS`.
- Aperture and locality controls: `MC_VM_CACHEABLE_DRAM_ADDRESS_START`, `MC_VM_CACHEABLE_DRAM_ADDRESS_END`, `MC_VM_APT_CNTL`, `MC_VM_LOCAL_HBM_ADDRESS_START`, `MC_VM_LOCAL_HBM_ADDRESS_END`, and `MC_VM_LOCAL_HBM_ADDRESS_LOCK_CNTL`.
- XGMI and cacheable-DRAM controls: `MC_VM_XGMI_LFB_CNTL`, `MC_VM_XGMI_LFB_SIZE`, and `MC_VM_CACHEABLE_DRAM_CNTL`.

The paired mask header shows these registers carry MMIO base/limit fields, MMIO enable, VGA-hole, top-of-memory, physical page-number pieces for the system aperture default address, default steering, PF/VF reset request bits, local HBM start/end windows, lock state, PF XGMI local-framebuffer region/size, and cacheable-DRAM aperture enable. The paired default header sets most to zero, with notable non-zero defaults including `MC_VM_NB_PCI_ARB_DEFAULT` (`0x00000008`), `MC_VM_STEERING_DEFAULT` (`0x00000001`), `MC_MEM_POWER_LS_DEFAULT` (`0x00000208`), and `MC_VM_LOCAL_HBM_ADDRESS_END_DEFAULT` (`0x000fffff`).

`mmhub_v9_4_init_system_aperture_regs()` programs the analogous instance-0 PF default-address registers using `mmVMSHAREDPF0_MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB/MSB` plus a hub offset. This chunk's `PF1` definitions are therefore part of the same register map for the second MMHUB instance and must stay numerically aligned with the PF0 stride scheme.

### VMSHAREDVC1 shared VC aperture and TLB controls

The `mmhub_utcl2_vmsharedvcdec:1` block has base address comment `0x76c00` and defines offsets `0x3b00` through `0x3b07`:

- `mmVMSHAREDVC1_MC_VM_FB_LOCATION_BASE` and `_TOP` for framebuffer location discovery.
- `mmVMSHAREDVC1_MC_VM_AGP_TOP`, `_BOT`, and `_BASE` for AGP aperture programming.
- `mmVMSHAREDVC1_MC_VM_SYSTEM_APERTURE_LOW_ADDR` and `_HIGH_ADDR` for logical system aperture bounds.
- `mmVMSHAREDVC1_MC_VM_MX_L1_TLB_CNTL` for the L1 TLB, advanced driver model, memory type, and ATC enable bits.

The shift/mask header gives `FB_BASE`, `FB_TOP`, `AGP_TOP`, `AGP_BOT`, `AGP_BASE`, logical low/high aperture fields, and TLB fields such as `ENABLE_L1_TLB`, `SYSTEM_ACCESS_MODE`, `SYSTEM_APERTURE_UNMAPPED_ACCESS`, `ENABLE_ADVANCED_DRIVER_MODEL`, `MTYPE`, and `ATC_EN`. The default header sets `MC_VM_MX_L1_TLB_CNTL_DEFAULT` to `0x00002501`.

`mmhub_v9_4_get_fb_location()` reads `VMSHAREDVC0` framebuffer base/top for MMHUB0. `mmhub_v9_4_init_system_aperture_regs()` and `mmhub_v9_4_init_tlb_regs()` write the corresponding VC registers using `mmVMSHAREDVC0...` plus a per-hub offset. These `VMSHAREDVC1` direct names represent the second instance's same register family and are coupled to the constant `MMHUB_INSTANCE_REGISTER_OFFSET` used by that code.

### VMSHAREDHV1 virtualization, IOMMU, ATS, and XGMI controls

The `mmhub_utcl2_vmsharedhvdec:1` block has base address comment `0x76c80` and defines offsets `0x3b20` through `0x3b5e`. It is the largest group in this chunk.

The first sixteen registers, `mmVMSHAREDHV1_MC_VM_FB_SIZE_OFFSET_VF0` through `_VF15`, provide per-virtual-function framebuffer size and offset control. The mask header shows each packs `VF_FB_SIZE` in the low 16 bits and `VF_FB_OFFSET` in the high 16 bits. These fields are central to SR-IOV framebuffer partitioning because a bad size/offset pair would map a VF to the wrong physical VRAM window.

The next register, `mmVMSHAREDHV1_VM_IOMMU_MMIO_CNTRL_1`, is followed by four MARC region groups:

- `MC_VM_MARC_BASE_LO_0` through `_3`.
- `MC_VM_MARC_BASE_HI_0` through `_3`.
- `MC_VM_MARC_RELOC_LO_0` through `_3`.
- `MC_VM_MARC_RELOC_HI_0` through `_3`.
- `MC_VM_MARC_LEN_LO_0` through `_3`.
- `MC_VM_MARC_LEN_HI_0` through `_3`.

These define up to four memory address relocation/control regions with split low/high base, relocation, and length fields. The paired defaults are all zero for the MARC registers.

The block then defines IOMMU and PCIe ATS controls:

- `mmVMSHAREDHV1_VM_IOMMU_CONTROL_REGISTER`.
- `mmVMSHAREDHV1_VM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER`.
- `mmVMSHAREDHV1_VM_PCIE_ATS_CNTL`.
- `mmVMSHAREDHV1_VM_PCIE_ATS_CNTL_VF_0` through `_VF_15`.

The per-VF ATS offsets are contiguous from `0x3b4c` through `0x3b5b`, which makes them suitable for indexed programming if the caller uses the generated stride correctly. The default header initializes the ATS registers to zero.

The block ends with:

- `mmVMSHAREDHV1_UTCL2_CGTT_CLK_CTRL` at `0x3b5c`, default `0x00000080`.
- `mmVMSHAREDHV1_MC_SHARED_ACTIVE_FCN_ID` at `0x3b5d`.
- `mmVMSHAREDHV1_MC_VM_XGMI_GPUIOV_ENABLE` at `0x3b5e`.

The mask header indicates `MC_VM_XGMI_GPUIOV_ENABLE` has enable bits for VF0 through VF15 plus an `ENABLE_PF` bit at bit 31. This ties the block into multi-function and XGMI GPU I/O virtualization behavior.

### ATC L2 performance counters

The `mmhub_utcl2_atcl2pfcntrdec:1` block at base address comment `0x76dc0` defines result registers:

- `mmATCL2PFCNTR1_ATC_L2_PERFCOUNTER_LO` at `0x3b70`.
- `mmATCL2PFCNTR1_ATC_L2_PERFCOUNTER_HI` at `0x3b71`.

The `HI` register includes both counter high bits and a compare-value field in the mask header. These registers are paired with the control block below.

The `mmhub_utcl2_atcl2pfcntldec:1` block at base address comment `0x76dd0` defines:

- `mmATCL2PFCNTL1_ATC_L2_PERFCOUNTER0_CFG` at `0x3b74`.
- `mmATCL2PFCNTL1_ATC_L2_PERFCOUNTER1_CFG` at `0x3b75`.
- `mmATCL2PFCNTL1_ATC_L2_PERFCOUNTER_RSLT_CNTL` at `0x3b76`.

The mask header gives each config register `PERF_SEL`, `PERF_SEL_END`, `PERF_MODE`, `ENABLE`, and `CLEAR` fields. The result-control register selects the counter and trigger behavior, with `ENABLE_ANY`, `CLEAR_ALL`, and `STOP_ALL_ON_SATURATE`. The default result-control value is `0x04000000`, corresponding to the stop-on-saturate default bit in the paired mask definitions.

### VM L2 performance counters

The `mmhub_utcl2_vml2pldec:1` block at base address comment `0x76e00` defines eight VM L2 performance-counter configuration registers:

- `mmVML2PL1_MC_VM_L2_PERFCOUNTER0_CFG` through `_7_CFG`, offsets `0x3b80` through `0x3b87`.
- `mmVML2PL1_MC_VM_L2_PERFCOUNTER_RSLT_CNTL` at `0x3b88`.

The config fields mirror the ATC L2 counter config pattern: select range, mode, enable, and clear. The result-control register similarly selects a counter, start/stop triggers, global enable, clear-all, and stop-on-saturate behavior. Its default is also `0x04000000`.

The `mmhub_utcl2_vml2prdec:1` block at base address comment `0x76e40` defines the VM L2 performance-counter result pair:

- `mmVML2PR1_MC_VM_L2_PERFCOUNTER_LO` at `0x3b90`.
- `mmVML2PR1_MC_VM_L2_PERFCOUNTER_HI` at `0x3b91`.

The low register is the 32-bit counter low field. The high register carries a 16-bit high counter field plus a 16-bit compare-value field. These registers are observability hooks rather than core VM setup knobs.

## APIs, Types, and Macros

There are no runtime APIs or C types declared in this chunk. The exported interface is the macro namespace itself:

- `mm<register>` macros are integer register offsets.
- `mm<register>_BASE_IDX` macros are all `1`, selecting the MMHUB base-index table used by SOC15 register accessors.
- The symbols depend on the companion `mmhub_9_4_1_sh_mask.h` field macros for safe bit manipulation through `REG_SET_FIELD()` and on `mmhub_9_4_1_default.h` reset values where driver code wants a known hardware default.

The integration API is indirect: callers pass these constants to AMDGPU register helpers such as `SOC15_REG_OFFSET(MMHUB, instance, reg)`, `RREG32_SOC15_OFFSET(MMHUB, instance, reg, offset)`, and `WREG32_SOC15_OFFSET(MMHUB, instance, reg, offset, value)`.

## Control Flow

This chunk has no local control flow. Runtime sequencing lives in `mmhub_v9_4.c`:

- `mmhub_v9_4_init()` computes VM hub register addresses and register distances from generated offsets.
- `mmhub_v9_4_gart_enable()` iterates over `MMHUB_NUM_INSTANCES` and programs GART, system aperture, TLB, cache, snoop override, VM context, and invalidation registers.
- `mmhub_v9_4_init_system_aperture_regs()` writes shared VC and PF aperture/default-address registers for each hub.
- `mmhub_v9_4_init_tlb_regs()` writes shared VC L1 TLB control.
- `mmhub_v9_4_setup_vmid_config()` writes VM-context start/end ranges for VMIDs using context address distances.

The direct `...1` symbols in this chunk are generated aliases for instance-1 registers, while much of the current setup code addresses instance 1 by taking the `...0` symbol and adding `MMHUB_INSTANCE_REGISTER_OFFSET`. This means the numerical spacing between the instance-0 and instance-1 definitions is part of the driver's implicit control-flow contract.

## State and Persistence

The chunk itself has no memory allocation, persistence, or software state. It defines hardware state locations. Values written to these registers persist in MMHUB hardware until changed by the driver, reset by the device, or affected by power-management/virtualization transitions.

The most stateful hardware areas represented here are:

- VM context page-table start/end bounds, which gate GPU virtual-address validity.
- Shared aperture registers, which define framebuffer, AGP, and system logical windows.
- PF default-page physical addresses and protection behavior, which determine fault redirection behavior.
- HV/SR-IOV framebuffer size/offset and ATS controls, which partition and translate memory for VFs.
- Performance-counter config/result registers, which retain counter selections, enable states, clear requests, and sampled counts until reprogrammed.

Defaults are documented in `mmhub_9_4_1_default.h`, but driver initialization actively overwrites many aperture/TLB/VM registers from `adev->gmc`, `adev->vm_manager`, and other runtime device state.

## Dependencies and Integration Points

Primary dependencies:

- SOC15 register access infrastructure in AMDGPU (`RREG32_SOC15*`, `WREG32_SOC15*`, `SOC15_REG_OFFSET`).
- `mmhub_9_4_1_sh_mask.h` for field-level masks and shifts.
- `mmhub_9_4_1_default.h` for reset/default values.
- `amdgpu_vmhub` fields such as `ctx_distance`, `ctx_addr_distance`, and invalidation-engine distances, which are derived from adjacent generated offsets.
- Runtime GPU memory-management state in `adev->gmc`, `adev->vm_manager`, `adev->gart`, `adev->mem_scratch`, and SR-IOV state from `amdgpu_sriov_vf(adev)`.

Important integration points:

- GART setup depends on correct VM page-table base/start/end offsets.
- VMID configuration depends on the context address stride matching the generated register layout.
- System aperture setup depends on shared VC/PF register offsets and the same second-instance stride represented by the `...1` macros.
- SR-IOV and XGMI virtualization code can use the HV registers in this chunk for VF framebuffer slicing, active-function targeting, ATS control, and XGMI GPUIOV enablement.
- Performance tooling can program the ATC L2 and VM L2 perf-counter config/result registers to observe translation and cache behavior.

## Risks and Edge Cases

- Offset drift is high impact. These macros are generated hardware ABI constants; an incorrect value can make the driver read or write a different MMHUB register without compile-time errors.
- Instance alignment is critical. `mmhub_v9_4.c` uses `MMHUB_INSTANCE_REGISTER_OFFSET` (`0x3000`) with instance-0 symbols to reach the second hub. The direct instance-1 offsets in this chunk must remain consistent with that addressing model.
- Context-bound writes must preserve 64-bit page-number splitting. LO32 and HI32 page-table range registers encode low 32 bits plus a high 4-bit field; callers must continue to shift GPU addresses consistently before writing.
- SR-IOV partitioning errors can cross isolation boundaries. The per-VF `FB_SIZE_OFFSET`, ATS, active-function, and XGMI GPUIOV registers are security-sensitive because they define which VF can access which memory and interconnect resources.
- Default zero values do not imply safe runtime configuration. Many aperture and virtualization registers reset to zero but need explicit programming from device topology and memory layout before normal GPU VM operation.
- Performance-counter registers may be shared diagnostic state. Counter config, clear, and result-control writes can perturb concurrent observability or debug tooling if not serialized at a higher layer.
- The header closes with `#endif`; missing or duplicate guard closure would affect every include site, but this generated file currently has a conventional guard around the whole offset namespace.

## Test Signals

Useful validation signals for this chunk are mostly build-time, register-map consistency, and hardware bring-up checks:

- The AMDGPU driver compiles with `mmhub_v9_4.c` including `mmhub_9_4_1_offset.h`, `_sh_mask.h`, and `_default.h` together.
- Static checks confirm every `mm...` symbol in this chunk has a matching `_BASE_IDX`, and corresponding `_DEFAULT` and shift/mask definitions where applicable.
- Register spacing checks confirm context start/end pairs are contiguous, per-VF arrays are contiguous, and instance-1 offsets remain reachable through the instance-0 symbol plus `MMHUB_INSTANCE_REGISTER_OFFSET`.
- Runtime GART enable succeeds without VM fault storms, GPU page faults resolve to the expected default/dummy page when configured, and `adev->gmc.fb_start/fb_end`, AGP aperture, and system aperture values match hardware expectations.
- SR-IOV validation should verify VF framebuffer windows, ATS enablement, active function selection, and XGMI GPUIOV enable bits under PF and VF modes.
- Performance-counter smoke tests should be able to program ATC L2 and VM L2 counter config registers, clear counters, enable counting, and read non-stuck LO/HI results under translation traffic.
