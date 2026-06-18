# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 39657-42335

## Purpose

This chunk is generated AMD GC 10.1 register field metadata for the AMDGPU graphics core. It contains no executable C logic; it publishes preprocessor `__SHIFT` and `__MASK` constants used by register helper macros to pack, update, and decode fields in MMIO or indirect GC registers. Consumers pair these names with the matching register address definitions in `gc_10_1_0_offset.h`, and often with default values from `gc_10_1_0_default.h`, to program Navi10-era graphics, memory-management, virtualization, SDMA, power, and profiling/debug blocks.

The selected range starts at the tail of a graphics pipe-priority field, then covers GRBM shadow-register targeting, GRBM CAM remap registers, interrupt-cookie pointers, a large RLC GPU IOV/hypervisor register group, SDMA0 and SDMA1 hypervisor/context metadata, shared GCVM virtualization and ATS fields, GC CAC and SE CAC indirect performance/power accounting controls, and SPM global/SE sample-delay registers. Although the repository path is under a `ceph-client` source tree, this file is AMDGPU hardware metadata and is unrelated to Ceph filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, locks, allocations, or callbacks in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` constants identifying the starting bit of a hardware field.
- `<REGISTER>__<FIELD>_MASK` constants identifying the full bit mask for that field.
- Register comments and `addressBlock` comments grouping fields by hardware block.
- Matching register offset names are defined in `gc_10_1_0_offset.h` as `mm*`, `reg*`, or `ix*`-style symbols, depending on the access path.

Major register families in this range:

- GRBM and CAM selection/remap: `GRBM_GFX_INDEX_SR_SELECT`, `GRBM_GFX_INDEX_SR_DATA`, `GRBM_GFX_CNTL_SR_SELECT`, `GRBM_GFX_CNTL_SR_DATA`, `GRBM_CAM_INDEX`, `GRBM_HYP_CAM_INDEX`, `GRBM_CAM_DATA`, `GRBM_HYP_CAM_DATA`, and upper-address companions. These fields select shader-engine/shader-array/instance targeting, broadcast writes, pipe/ME/VMID/queue context, and CAM address-to-remap-address entries.
- Interrupt and RLC virtualization plumbing: `GC_IH_COOKIE_0_PTR`, `RLC_IH_COOKIE`, `RLC_IH_COOKIE_CNTL`, RLC timer interrupt/control/status registers, pace timer status, interrupt status/force/disable fields, and cookie credit/reset fields.
- RLC GPU IOV and hypervisor state: `RLC_GPU_IOV_VF_ENABLE`, `RLC_GPU_IOV_CFG_REG1/2/6/8`, scheduler block and scheduler data registers, VM busy status registers, active function ID, VF/PF doorbell status/set/clear/mask, SDMA0/SDMA1 preempt/save/restore status, SMU/RLC response words, virtual reset requests, semaphores, reset-vector exit bits, bootload size/address fields, F32 enable/reset fields, scratch registers, microcode address/data windows, checksum registers, IRAM/DRAM/ARAM address/data windows, and timestamp offset registers.
- SDMA hypervisor blocks: `addressBlock: gc_sdma0_sdma0hypdec` and `gc_sdma1_sdma1hypdec` define ucode address/data fields, VM context base/control, active function ID, VF enable, virtual reset requests, context-register type masks, and VM control command fields for both SDMA engines. Context type masks enumerate which ring-buffer, IB, doorbell, CSA, status, preempt, mid-command, AQL, and pointer-poll registers are included in a context save/restore class.
- Shared GCVM hypervisor/virtualization block: `addressBlock: gc_gcvmsharedhvdec` includes per-VF framebuffer size/offset registers for VF0 through VF31, IOMMU MMIO/control/performance optimization fields, MARC base/relocation/length windows, PCIe ATS control for the PF and every VF, `GCUTCL2_CGTT_CLK_CTRL`, and `GCMC_SHARED_ACTIVE_FCN_ID`.
- GC CAC indirect block: `addressBlock: gccacind` defines stall-pattern controls for PCC and power-break throttling, stall/release lookup tables, CAC ID/control, override select/value registers, many per-block 16-bit weight fields, 32-bit or 40-bit accumulator fields, per-block override select/value fields, fixed-pattern performance counters, and `HW_LUT_UPDATE_STATUS`.
- SE CAC indirect block: `addressBlock: secacind` exposes SE-local CAC ID/control/override select/value registers.
- SPM sample-delay blocks: `addressBlock: spmglbind` and `spmind` define uniform `SAMPLEDELAY` and reserved-bit masks for global blocks (`GLB_CPG`, `GLB_CPC`, `GLB_CPF`, `GLB_GDS`, `GLB_GCR`, `GLB_PH`, `GLB_GE`, `GLB_GUS`, `GLB_CHA`, `GLB_CHCG`, `GLB_ATCL2`, `GLB_VML2`, SDMA, GL2A/GL2C, EA, CHC) and shader-engine/SA/WGP-local blocks (`SE_SPI`, `SE_SQG`, `SE_CBR`, `SE_DBR`, `SE_SA0*`, and early `SE_SA0WGP*` sample-delay registers).

The macro names encode access semantics only indirectly. Suffixes such as `STATUS`, `STAT`, `BUSY_STATUS`, `RESET_REQ`, `INT_CLEAR`, `FORCE`, `SET`, `CLR`, `RESP`, `UCODE_ADDR`, `UCODE_DATA`, `SCRATCH`, `ACC`, and `OVRD` strongly indicate status, command, reset, interrupt, firmware-loading, debug, accumulator, or override behavior, but this header does not itself declare read/write, sticky, write-one-to-clear, self-clearing, or polling requirements.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from AMDGPU consumers that include the GC 10.1 register headers and use helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_GOLDEN_VALUE`, indirect register accessors, and ASIC-specific register tables.

Typical consumer flow for fields in this range is:

1. Select the correct register address from `gc_10_1_0_offset.h`.
2. Read the register or start from a known initialization value.
3. Use the matching `__MASK` and `__SHIFT` constants to clear and insert a field, or to extract a field from a readback value.
4. Write the value through the correct access path: direct SOC15 GC MMIO, GRBM-indexed instance targeting, RLC/SDMA hypervisor windows, GCVM shared registers, GC CAC/SE CAC indirect registers, or SPM indirect sample-delay registers.
5. For command/status families, poll or wait on the corresponding status bits using timeouts defined in the calling driver code.

Important sequencing lives outside this file. Examples include selecting GRBM SE/SA/instance targets before per-instance register writes, masking or clearing IOV interrupt sources, issuing RLC GPU IOV commands and reading `CMD_STATUS`/response fields, enabling VF or PF virtualization state only after context storage is initialized, loading RLC/SDMA microcode through address/data windows, programming SDMA context-save masks before preemption or reset paths, enabling PCIe ATS only when IOMMU/ATC state is coherent, and updating CAC stall/power-break LUTs only when the hardware allows the LUT update to settle.

## State And Persistence Behavior

The file stores no software state and persists nothing to disk. It describes hardware-visible state in GC registers.

The represented hardware state includes GRBM broadcast/instance selection, CAM remap table entries, interrupt-cookie bookkeeping, RLC timers and interrupt bits, virtual-function enablement and IDs, scheduler command/status state, VM busy masks, doorbell status, semaphore ownership, reset exit reason bits, bootload and microcode window addresses, scratch and IRAM/DRAM/ARAM data, SDMA context-save classification, per-VF framebuffer aperture metadata, MARC relocation windows, IOMMU and ATS enablement, clock-gating overrides, CAC weights/accumulators/overrides, stall and power-break pattern tables, fixed-pattern performance counters, and SPM sample-delay values.

Persistence is hardware-defined rather than expressed in the macros. Some fields are configuration state that may remain until reset, power-gate, function-level reset, suspend/resume, or a later driver write. Others are live status, sticky interrupt status, write-one-to-clear bits, self-clearing command bits, command response words, or counters/accumulators that can change autonomously while the GPU is running. The many `RESERVED` masks are part of the hardware ABI: register updates should preserve them unless an ASIC programming guide or golden-register table explicitly requires a value.

## Dependencies And Integration Points

This chunk depends on consistency with the rest of the AMD register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h` supplies the matching register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_default.h` supplies reset/default values for many of the same register names.
- AMDGPU GC v10 code includes these generated headers for Navi10-class graphics hardware and uses SOC15 register helpers to apply golden settings, load firmware, set up rings and VM state, control RLC, and program SPM-related sample delays.
- RLC GPU IOV and SDMA virtualization fields integrate with SR-IOV, VF/PF scheduling, function-level reset handling, doorbells, VM busy tracking, context save/restore, and firmware or hypervisor cooperation.
- GCVM and ATS fields integrate with GPU virtual memory, IOMMU/ATC programming, PCIe address translation services, per-VF framebuffer apertures, and memory aperture relocation.
- CAC and power-throttling fields integrate with power-management firmware and driver power-tuning paths. Existing AMDGPU powerplay code accesses GC CAC indirect registers through `CGS_IND_REG_GC_CAC`, and SMU firmware interfaces expose GC CAC-related feature IDs on newer parts.
- SPM sample-delay fields integrate with profiling and hardware performance-monitor setup. GC v10 code programs SPM global and per-SE sample-delay indirect addresses/data using golden-value tables for this ASIC family.

## Risks And Edge Cases

- Header version mismatch is the largest risk. Combining `gc_10_1_0_sh_mask.h` with offset/default headers from another GC generation can compile while causing writes to the wrong register or field.
- The constants are untyped preprocessor macros. Field width mistakes, off-by-one shifts, stale generated data, or typoed register names can silently corrupt unrelated bits in low-level hardware registers.
- GRBM targeting fields are high blast-radius. Incorrect SE/SA/instance indices or broadcast-write bits can program only one hardware instance, all instances, or the wrong queue/VMID context.
- Virtualization and reset fields are sequencing-sensitive. VF enable, VF/PF doorbell state, scheduler command execution, VM busy masks, FLR requests, SDMA save/restore status, and active function ID must be coordinated with PF/VF ownership and hardware quiescence.
- Address/data microcode and scratch windows are stateful. Incorrect address increments, missing reset, wrong firmware version, or overlapping RLC/SDMA access can load invalid firmware or corrupt diagnostic/scratch state.
- SDMA context-register type masks must match the actual context save/restore contract. Missing a ring, IB, doorbell, CSA, preempt, mid-command, AQL, or pointer-poll field can break preemption, suspend/resume, SR-IOV scheduling, or engine reset recovery.
- GCVM/IOMMU/ATS settings affect memory isolation and address translation. Bad per-VF framebuffer apertures, MARC relocation, ATS enablement, or active-function selection can produce page faults, data isolation failures, hangs, or DMA to the wrong physical address.
- CAC and power-break tables can affect throttling behavior. Bad weights, thresholds, stall patterns, or LUT update sequencing can under-throttle, over-throttle, destabilize clocks/power, or distort telemetry used by power management.
- Accumulator and performance-counter fields may have clear/latch/wrap behavior not visible in this header. Driver diagnostics must understand whether reads are destructive, sticky, or racing hardware increments.
- Sample-delay fields are replicated across many blocks. A wrong indirect address or delay value can produce broken SPM traces only for one block, shader array, WGP, SDMA engine, GL2C slice, or EA path.
- The chunk boundary is artificial. It begins after the `GFX_PIPE_PRIORITY__HP_PIPE_SELECT__SHIFT` definition and ends in the early `SE_SA0WGP02TA1_SAMPLEDELAY` register; neighboring chunks are required for complete per-file analysis.

## Test Signals

Useful validation is mostly build, static, and hardware integration coverage:

- Build coverage for AMDGPU GC v10 code that includes `gc_10_1_0_offset.h`, `gc_10_1_0_sh_mask.h`, and `gc_10_1_0_default.h`.
- Generated-header consistency checks that every field mask matches its shift and width, fields within each register do not unintentionally overlap, and every register in this slice has a matching offset/default entry where expected.
- Golden-register and boot tests on GC 10.1 hardware, especially paths that program RLC clocks, SPM sample delays, GCVM/ATS, GRBM instance targeting, and SDMA/RLC firmware windows.
- SR-IOV and virtualization tests covering VF enable/disable, PF/VF doorbell status set/clear/mask, scheduler commands and responses, active function ID, FLR handling, VM busy tracking, and SDMA context save/restore.
- Reset and recovery tests covering cold boot, warm reset, VDDGFX exit, VF FLR exit, RLC/SDMA preempt/save/restore bits, microcode checksum/readback, and interrupt-cookie behavior.
- GPUVM/IOMMU tests covering per-VF framebuffer apertures, MARC base/relocation/length windows, ATS enablement, VM faults, and memory isolation.
- Power and telemetry tests covering GC CAC thresholds, weights, overrides, accumulators, stall/power-break LUT programming, fixed-pattern counters, and LUT update status.
- Profiling tests covering SPM global and SE sample-delay programming and trace sanity for CPG/CPC/CPF, GDS/GCR, PH/GE/GUS, SDMA0/1, GL2A/GL2C, EA, CHC, SPI/SQG/CBR/DBR, SA-local blocks, and WGP-local TA/TD/TCP sample delays.
- Regression indicators include GPU hangs, failed ring tests, VM faults, SR-IOV isolation failures, FLR timeouts, SDMA preemption failures, missing interrupts, bad microcode checksum, unstable power throttling, malformed SPM traces, or failures isolated to one VF, engine, shader array, or hardware block.
