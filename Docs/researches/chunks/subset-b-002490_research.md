# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 35037-37447

## Scope

This chunk is generated AMD GC 10.3.0 register field metadata. It contains only C preprocessor constants: each hardware register field is represented by a `__SHIFT` macro and a matching `__MASK` macro. There are no functions, structs, enums, global variables, includes, locks, allocations, callbacks, or executable branches in this range.

The selected lines begin in the middle of `CGTT_SC_CLK_CTRL1`, then cover a large clock-gating control block, the `addressBlock: gc_hypdec` command-processor/RLC hypervisor decode block, all visible SDMA0 hypervisor decode field masks, and the start of the SDMA1 hypervisor decode block through `SDMA1_PUB_REG_TYPE1`. Although the repository path is under a `ceph-client` source tree, this is AMDGPU DRM hardware metadata and is unrelated to Ceph filesystem logic.

## Purpose

`gc_10_3_0_sh_mask.h` describes bit layouts for AMD GC 10.3.0 graphics registers. Driver code pairs these constants with register-address definitions from `gc_10_3_0_offset.h` and, where useful, default values from `gc_10_3_0_default.h`. The constants let AMDGPU code compose read-modify-write updates and decode register readbacks without embedding literal bit positions throughout the driver.

This chunk serves four main purposes:

- It defines clock-gating and clock-stall override fields for graphics sub-blocks such as SC, SQ, SQG, SX, TD, TA, TCPI/TCPF, GDS, DB, CB, GL2A/GL2C, CP/CPF/CPC, RLC, RMI, GCR, UTCL1, GCEA, CAC, GRBM, GUS, and PH.
- It defines command-processor hypervisor decode fields for firmware upload and instruction-cache base/control registers for PFP, ME, CE, CPC, MEC, and MES engines.
- It defines GRBM, RLC, interrupt-cookie, GPU IOV, reset, timer, scheduler, semaphore, scratch, firmware, and SDMA status fields used by virtualization and reset/recovery paths.
- It defines SDMA0 and SDMA1 hypervisor decode masks for microcode windows, VM context state, active VF/PF identity, virtual reset requests, VF enablement, context-save register classes, public register classes, and status/control/performance register grouping.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The important interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Comment lines such as `//CGTT_SQ_CLK_CTRL` and `// addressBlock: gc_hypdec` group macros by hardware register or address block.
- Consumers normally use these constants indirectly through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, indexed-register accessors, golden-register tables, firmware loaders, reset code, and virtualization paths.

Major register families in this range:

- Clock gating controls: `CGTT_SC_CLK_CTRL1/2`, `CGTT_SQ_CLK_CTRL`, `CGTT_SQG_CLK_CTRL`, `SQ_ALU_CLK_CTRL`, `SQ_TEX_CLK_CTRL`, `SQ_LDS_CLK_CTRL`, `CGTT_SX_CLK_CTRL0` through `4`, `TD_CGTT_CTRL`, `TA_CGTT_CTRL`, `CGTT_TCPI_CLK_CTRL`, `CGTT_GDS_CLK_CTRL`, `DB_CGTT_CLK_CTRL_0`, `CB_CGTT_SCLK_CTRL`, `GL2C_CGTT_SCLK_CTRL`, `GL2A_CGTT_SCLK_CTRL`, `GL2A_CGTT_SCLK_CTRL_1`, `CGTT_CP_CLK_CTRL`, `CGTT_CPF_CLK_CTRL`, `CGTT_CPC_CLK_CTRL`, `CGTT_RLC_CLK_CTRL`, `RMI_CGTT_SCLK_CTRL`, `CGTT_TCPF_CLK_CTRL`, `GCR_CGTT_SCLK_CTRL`, `UTCL1_CGTT_CLK_CTRL`, `GCEA_CGTT_CLK_CTRL`, `SE_CAC_CGTT_CLK_CTRL`, `GC_CAC_CGTT_CLK_CTRL`, `GRBM_CGTT_CLK_CNTL`, `GUS_CGTT_CLK_CTRL`, and `CGTT_PH_CLK_CTRL0` through `3`. These use repeated `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_STALL_OVERRIDE*`, `SOFT_OVERRIDE*`, block-specific override, performance-monitor override, dynamic override, and register-clock override fields.
- Shader/WGP force-on controls: `SQ_ALU_CLK_CTRL`, `SQ_TEX_CLK_CTRL`, and `SQ_LDS_CLK_CTRL` expose `FORCE_WGP_ON_SA0` and `FORCE_WGP_ON_SA1` masks, allowing per-shader-array WGP clock behavior to be forced for ALU, texture, and LDS units.
- Command processor firmware and instruction-cache fields: `CP_HYP_*_UCODE_ADDR/DATA`, non-hypervisor `CP_*_UCODE_ADDR/DATA`, `CP_ME_RAM_RADDR/WADDR/DATA`, `CP_PFP/ME/CE/CPC/MES_IC_BASE_LO/HI/CNTL`, and `CP_*_IC_OP_CNTL` fields cover microcode address/data windows, instruction-cache base address windows, VMID selection, address clamping, execute-disable, cache policy, cache invalidation, and cache priming completion.
- MES memory-window fields: `CP_MES_MIBASE_*`, `CP_MES_MDBASE_*`, `CP_MES_LOCAL_BASE0_*`, `CP_MES_LOCAL_MASK0_*`, `CP_MES_LOCAL_APERTURE`, `CP_MES_MIBOUND_*`, and `CP_MES_MDBOUND_*` describe instruction/data/local aperture base, mask, and bound fields for MES-managed firmware memory.
- GRBM selection and remapping: `GFX_PIPE_PRIORITY`, `GRBM_GFX_INDEX_SR_SELECT/DATA`, `GRBM_GFX_CNTL_SR_SELECT/DATA`, `GRBM_CAM_INDEX`, `GRBM_HYP_CAM_INDEX`, `GRBM_CAM_DATA`, `GRBM_HYP_CAM_DATA`, `GRBM_CAM_DATA_UPPER`, `GRBM_HYP_CAM_DATA_UPPER`, and `GRBM_SE_REMAP_CNTL` expose pipe priority, selected shadow-register context, shader-engine/shader-array/instance targeting, broadcast controls, CAM remap address pairs, and per-SE remap enables for SE0 through SE7.
- RLC and GPU IOV controls: `RLC_GPU_IOV_VF_ENABLE`, `RLC_GPU_IOV_CFG_REG1/2/6/8`, `RLC_GPU_IOV_SCH_BLOCK`, `RLC_GPU_IOV_SCH_0` through `3`, `RLC_GPU_IOV_ACTIVE_FCN_ID`, `RLC_GPU_IOV_VM_BUSY_STATUS`, `RLC_GPU_IOV_VF_DOORBELL_STATUS` plus set/clear variants, `RLC_GPU_IOV_VF_MASK`, `RLC_GPU_IOV_INT_STAT`, `RLC_GPU_IOV_INT_DISABLE`, `RLC_GPU_IOV_INT_FORCE`, `RLC_GPU_IOV_SMU_RESPONSE`, `RLC_GPU_IOV_RLC_RESPONSE`, `RLC_GPU_IOV_VIRT_RESET_REQ`, `RLC_GPU_IOV_F32_CNTL`, and `RLC_GPU_IOV_F32_RESET` define VF enable/count, PF/VF active ID, scheduler commands, command status, context location/size/offset, VM busy state, doorbell state, interrupt routing, responses, reset requests, and F32 controls.
- RLC timers, reset, semaphores, and firmware windows: `RLC_RLCV_TIMER_INT_0/1`, `RLC_RLCV_TIMER_CTRL`, `RLC_RLCV_TIMER_STAT`, `RLC_PACE_TIMER_STAT`, `RLC_PACE_INT_FORCE`, `RLC_PACE_INT_CLEAR`, `RLC_HYP_SEMAPHORE_0` through `3`, `RLC_HYP_RESET_VECTOR`, `RLC_HYP_BOOTLOAD_SIZE`, `RLC_HYP_BOOTLOAD_ADDR_LO/HI`, `RLC_HYP_RLCG/RLCP/RLCV_UCODE_CHKSUM`, RLC GPM/PACE/GPU_IOV microcode address/data windows, RLCV/RLCP IRAM windows, SRM DRAM/ARAM windows, scratch windows, and GTS offset registers.
- SDMA status and hypervisor decode fields: RLC-level `RLC_SDMA0..3_STATUS` and `RLC_SDMA0..3_BUSY_STATUS`, GPU IOV `RLC_GPU_IOV_SDMA0..7_STATUS` and `BUSY_STATUS`, plus `addressBlock: gc_sdma0_sdma0hypdec` and `addressBlock: gc_sdma1_sdma1hypdec`.
- SDMA0/SDMA1 context and public register grouping: `SDMA0_CONTEXT_REG_TYPE0` through `3` and `SDMA1_CONTEXT_REG_TYPE0` through `3` enumerate ring-buffer, read/write pointer, write-pointer polling, IB, skip, context status, doorbell, CSA, preempt, AQL, minor pointer update, mid-command data, and reserved context classes. `SDMA0_PUB_REG_TYPE0` through `3` and visible `SDMA1_PUB_REG_TYPE0/1` enumerate microcode, VM, active function, context class, power, clock, control, status, atomic, UTCL1, performance, interrupt, scratch, timestamp, queue reset, and other public SDMA registers.

## Control Flow

This header has no runtime control flow. Runtime behavior is implied by driver users that include the generated register headers:

1. Select the correct register address from `gc_10_3_0_offset.h`, including the correct direct MMIO, indexed, hypervisor-decode, or SDMA-decode access path.
2. Read a current value or start from a default/golden value.
3. Use the `__MASK` and `__SHIFT` constants, usually through helper macros, to extract fields or compose an updated register value.
4. Write the value through the appropriate AMDGPU register accessor.
5. For command, reset, interrupt, firmware-load, or status fields, poll or wait on companion status bits in higher-level driver code.

The important sequencing is outside this file. Examples include enabling or overriding clock gates only during safe initialization or debug windows, loading CP/RLC/SDMA firmware through address/data registers in the expected order, invalidating or priming instruction caches before firmware execution, selecting GRBM shadow or CAM entries before data access, issuing GPU IOV scheduler commands and checking command status/responses, masking or clearing interrupts with the correct set/clear semantics, and coordinating SDMA context-save masks with preemption, FLR, suspend/resume, and reset recovery.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe fields in GPU hardware registers whose behavior is defined by the ASIC specification and the AMDGPU access sequence.

Clock-gating fields are hardware configuration state. Values may persist until graphics IP reset, function-level reset, suspend/resume reinitialization, power-gating loss, firmware reprogramming, or explicit driver writes. Fields named `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_STALL_OVERRIDE*`, and `SOFT_OVERRIDE*` influence whether sub-block clocks can gate, stall, or remain forced on.

Command-processor, RLC, and SDMA address/data windows are stateful hardware portals. The address register selects a firmware, RAM, IRAM, DRAM, ARAM, scratch, or context location, and subsequent data accesses operate on that selection. Incorrect interleaving between windows can corrupt firmware loading or diagnostics.

RLC/GPU IOV and SDMA virtualization fields include both durable configuration and volatile hardware-owned state. VF enable bits, active function IDs, scheduler configuration, context storage location, VM context bases, and doorbell masks are configuration. Status, busy, interrupt, response, timer, reset, checksum, and counter-like fields can change autonomously, be sticky, be write-one-to-clear, or be self-clearing depending on the register.

Reserved fields are part of the hardware ABI. This header exposes many `RESERVED`, `VOID_REG2`, and `RESERVED_FOR_PSPSMU_ACCESS_ONLY` masks; normal read-modify-write code should preserve them unless an ASIC programming guide, firmware contract, or golden-register table explicitly requires a value.

## Dependencies And Integration Points

This chunk depends on the rest of the generated GC 10.3.0 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h` supplies the matching register addresses for these field names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h` supplies reset/default values for many registers in the same generated family.
- AMDGPU GFX v10.3 code consumes these macros through SOC15 register helpers, golden-register tables, firmware loading paths, clock-gating setup, RLC initialization, GPU reset code, SDMA setup, and SR-IOV virtualization paths.
- CP/PFP/ME/CE/CPC/MEC/MES fields integrate with command processor firmware loading, instruction cache setup, MES firmware memory windows, queue management, and compute/graphics scheduling.
- RLC GPU IOV fields integrate with PF/VF scheduling, active function tracking, virtual function enablement, doorbell delivery, FLR handling, VM busy tracking, SMU/RLC response handshakes, interrupt routing, and context storage.
- SDMA0/SDMA1 fields integrate with DMA ring setup, VM context setup, microcode loading, SDMA public/status registers, AQL and IB handling, context save/restore, preemption, queue reset, and SDMA performance/status diagnostics.
- GRBM and SE remap fields integrate with instance-targeted register writes, shader-engine remapping, CAM table programming, broadcast write behavior, and debugging or virtualization control over per-engine state.

## Risks And Edge Cases

- Generated-header drift is high impact. A wrong mask or shift can compile cleanly while changing the wrong hardware bit in low-level graphics, firmware, reset, power, or virtualization paths.
- This chunk starts mid-`CGTT_SC_CLK_CTRL1` and ends mid-SDMA1 public-register coverage. Adjacent chunks are required for complete per-file conclusions about those register families.
- Clock-gating override fields can hide timing or power bugs. Forcing clocks on may improve debug stability but change power/performance behavior; forcing stalls or disabling gates at the wrong time can hang or throttle workloads.
- Address/data windows are order-sensitive. CP, RLC, and SDMA microcode, RAM, scratch, and IRAM/DRAM/ARAM windows rely on the selected address state; concurrent or misordered access can write plausible values to the wrong hardware location.
- Virtualization fields are security and isolation sensitive. Bad VF enablement, active function ID, doorbell status/mask, VM context, scheduler command, context storage, or FLR state can affect the wrong PF/VF or break isolation.
- Status, interrupt, reset, and response fields may have access semantics not visible here. Names like `STATUS`, `INT_CLEAR`, `SET`, `CLR`, `RESET_REQ`, `RESP`, `CHECKSUM`, and `BUSY_STATUS` are not enough to infer whether reads are destructive, writes are pulse-like, bits are sticky, or polling requires timeouts.
- SDMA context-register type masks must match the hardware context-save contract. Missing a ring pointer, IB field, CSA address, doorbell, preempt field, mid-command register, AQL register, or pointer-poll address can break preemption, reset, suspend/resume, or SR-IOV scheduling.
- Repeated SDMA0/SDMA1 register families invite copy/paste mistakes. The names are nearly symmetric, but using SDMA0 masks with SDMA1 addresses, or vice versa, can silently target the wrong engine.
- Reserved and PSPSMU-only fields must be preserved. Full-register writes that overwrite these bits can trigger undocumented behavior or conflict with firmware-owned state.
- GRBM broadcast and remap fields have wide blast radius. A bad instance index, SE/SA index, broadcast-write bit, or SE remap value can program only one instance, all instances, or the wrong physical shader engine.

## Test Signals

Useful validation is mostly build, generated-data consistency, and hardware integration:

- Kernel build coverage for AMDGPU files that include `gc_10_3_0_sh_mask.h`, especially GFX v10.3, RLC, SDMA, reset, SR-IOV, firmware loading, and golden-register paths.
- Static generated-header checks that every mask aligns with its shift, fields within a register do not overlap except for intentional full-width masks, and every register in this chunk has matching offset/default entries where expected.
- Cross-generation consistency checks against AMD's authoritative GC 10.3.0 register database, especially for repeated clock-gating, SDMA0/SDMA1, RLC GPU IOV, and CP firmware/cache families.
- Boot and ring tests on GC 10.3 hardware covering CP firmware load, RLC firmware load, SDMA0/SDMA1 firmware load, graphics and compute queues, and SDMA copy/fill paths.
- Clock-gating and power tests that exercise idle transitions, graphics load transitions, suspend/resume, runtime power management, performance counters, and debug modes that force clocks on or override stall behavior.
- SR-IOV and virtualization tests covering VF enable/disable, PF/VF active function IDs, doorbell status set/clear, scheduler commands and responses, VM busy status, virtual reset requests, FLR, and context save/restore storage.
- Reset and recovery tests covering cold boot, warm reset, VDDGFX exit, VF FLR exit, RLC/SDMA busy/status fields, RLC/SDMA checksums, interrupt-cookie behavior, and queue reset requests.
- SDMA-specific tests covering ring-buffer pointer handling, IB execution, write-pointer polling, CSA address use, preemption, AQL mode, mid-command state, UTCL1 status, atomic controls, and performance/status register readback.
- Regression indicators include GPU hangs, failed ring tests, SDMA timeouts, firmware checksum mismatch, bad VM faults, SR-IOV isolation failures, FLR timeouts, missing or stuck interrupts, unexpected busy bits, malformed debug dumps, power-management instability, or workload-specific performance changes after clock-gating or virtualization programming changes.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002490`. It covers lines 35037-37447 of `gc_10_3_0_sh_mask.h`. The final per-file research should merge it with adjacent chunks to recover the complete `CGTT_SC_CLK_CTRL1` definition before line 35037 and the remaining `SDMA1_PUB_REG_TYPE1`/later SDMA1 register families after line 37447.
