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
