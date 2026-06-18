# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_offset.h lines 4946-7413

## Scope

This chunk covers generated register offset macros for the AMD GC 9.4.3 graphics block. It starts inside `addressBlock: xcd0_gc_gfxudec` at command-processor pipeline statistics registers and runs through later address blocks:

- `xcd0_gc_gfxudec`: CP pipeline statistics, scratch, semaphore, DMA, coherency, indirect-buffer, draw/dispatch, VGT, PA, SQ thread trace, DB counters, GDS, and SPI configuration offsets.
- `xcd0_gc_gccanedec`: a small GC CANE register window.
- `xcd0_gc_perfddec` and `xcd0_gc_perfsdec`: performance counter data registers and selector/control registers for CP, GRBM, WD, IA, VGT, PA, SPI, SQ, SX, GDS, TA, TD, TCP, TCC, TCA, CB, DB, RLC, and RMI.
- UTCL2 performance blocks: ATC L2, MC VM L2, and L2TLB counter data, configuration, and result-control windows.
- `xcd0_gc_gdflldec`: GDFLL EDC hysteresis control/status offsets.
- `xcd0_gc_rlcpdec`: RLC control, timers, clock counts, power-gating, SERDES, scratch, SRM, SMU command, UTCL1/prewalker, interrupt, semaphore, DSM, and error-status offsets.
- `xcd0_gc_pwrdec`: CGTS compute-unit control registers, TCC disable controls, CGTT clock controls, SQ power throttle, and per-block clock-gating controls.
- `xcd0_gc_hypdec`: CP hypervisor microcode windows, GRBM shadow-register selection, RLC GPU IOV/SR-IOV scheduler, doorbell, timer, interrupt, SDMA status, and scratch/microcode offsets.
- `xcd0_gc_utcl2_vmsharedhvdec`: per-VF framebuffer aperture, MARC, IOMMU, ATS, active-function, and XGMI GPU IOV controls.
- `xcd0_gc_pspdec`: PSP-facing CP/GRBM/RLC security and firewall offsets.
- `sqind`: the first SQ indirect wave debug/status offsets.

The file is a generated C preprocessor register map. It defines `reg*` and `ix*` constants plus matching `_BASE_IDX` constants only. There are no C functions, structs, variables, algorithms, or in-header storage in this chunk.

## Purpose

The chunk provides the address side of the AMDGPU register ABI for GC 9.4.3. Driver code includes this header to convert symbolic register names into MMIO offsets for `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC_SHADOW_EX`, and related AMDGPU accessors.

Each normal register has the pattern:

- `regNAME`: the register offset within the GC IP block's register address space.
- `regNAME_BASE_IDX`: the generated base-index selector used by the SOC15 register helper layer.

The `sqind` entries use `ixSQ_*` names because they are indirect SQ indexes rather than ordinary `reg*` MMIO offsets. They are consumed through SQ indirect-index access paths, not by writing them as direct MMIO register addresses.

This header is paired with sibling generated headers such as `gc_9_4_3_sh_mask.h` for field shifts/masks and any available default headers for reset/default values. The offsets here identify which register to read or write; the mask header identifies how individual fields are encoded inside that register.

## Important Macro Families

### Command Processor, Draw State, and Pipeline Statistics

The opening `xcd0_gc_gfxudec` range maps user/context-facing CP registers:

- Pipeline counters: `regCP_NUM_PRIM_WRITTEN_COUNT*_LO/HI`, `regCP_NUM_PRIM_NEEDED_COUNT*_LO/HI`, `regCP_VGT_*_COUNT_*`, `regCP_PA_*_COUNT_*`, `regCP_SC_PSINVOC_COUNT*_LO/HI`, and `regCP_VGT_CSINVOC_COUNT_LO/HI`.
- Pipeline statistics control and destination: `regCP_PIPE_STATS_ADDR_LO/HI`, `regCP_PIPE_STATS_CONTROL`, `regCP_STREAM_OUT_CONTROL`, and `regCP_STRMOUT_CNTL`.
- Scratch and synchronization windows: `regSCRATCH_REG0..7`, `regSCRATCH_UMSK`, `regSCRATCH_ADDR`, `regCP_SIG_SEM_ADDR_*`, `regCP_WAIT_SEM_ADDR_*`, `regCP_SEM_WAIT_TIMER`, and `regCP_WAIT_REG_MEM_TIMEOUT`.
- Atomic and GDS pre-operation aliases for PFP and ME: `regCP_PFP_ATOMIC_PREOP_*`, `regCP_PFP_GDS_ATOMIC*_PREOP_*`, `regCP_ATOMIC_PREOP_*`, `regCP_ME_ATOMIC_PREOP_*`, and `regCP_ME_GDS_ATOMIC*_PREOP_*`.
- CP DMA and coherency registers: `regCP_DMA_ME_*`, `regCP_DMA_PFP_*`, `regCP_DMA_CNTL`, `regCP_DMA_READ_TAGS`, `regCP_COHER_*`, and `regCP_ME_COHER_*`.
- Ring/IB state: `regCP_RB_OFFSET`, `regCP_IB1_OFFSET`, `regCP_IB2_OFFSET`, preamble begin/end offsets, CE IB offsets, command-buffer size registers, and base/size registers for CE, IB1, IB2, and stream state buffers.
- Draw/dispatch operand registers: `regCP_DRAW_INDX_INDR_ADDR*`, `regCP_DISPATCH_INDR_ADDR*`, `regCP_INDEX_BASE_ADDR*`, `regCP_INDEX_TYPE`, and completion/predicate/status registers.

These offsets are integration points for graphics queue setup, indirect-buffer execution, CP DMA operations, streamout/statistics query handling, and fence/semaphore packet execution.

### Geometry, PA, SQ Thread Trace, DB, GDS, and SPI Windows

The same `gfxudec` block also maps front-end and shader/debug-facing state:

- `regGRBM_GFX_INDEX` selects shader engine, shader array, and instance targeting for many broadcast or per-instance register writes. GC 9.4.3 code uses it through `WREG32_SOC15_RLC_SHADOW_EX` and direct SOC15 helpers.
- VGT/IA/WD state includes `regVGT_PRIMITIVE_TYPE`, `regVGT_INDEX_TYPE`, streamout filled-size counters, vertex index bounds, instance counts, tessellation-factor memory, WD buffer bases, and `regIA_MULTI_VGT_PARAM`.
- PA/scissor/trap state includes line stipple, screen extents, trap screen enable/position/count registers, and stereo state.
- SQ thread trace state includes `regSQ_THREAD_TRACE_BASE`, `SIZE`, `MASK`, `TOKEN_MASK`, `PERF_MASK`, `CTRL`, `MODE`, `BASE2`, `WPTR`, `STATUS`, `HIWATER`, `CNTR`, and user data registers.
- DB counters include occlusion and Z-pass low/high counter pairs.
- GDS registers cover direct read/write burst windows, atomic operation setup/results, GWS resource accounting, ordered-append controls, and OA ring sizing.
- SPI registers include basic configuration and wave-limit control.

These offsets are not ordinary host data structures. They refer to hardware state that is selected by GC instance and often by `GRBM_GFX_INDEX` before access.

### Performance Counter Data and Selector Blocks

`xcd0_gc_perfddec` contains low/high counter data registers. `xcd0_gc_perfsdec` contains selector, control, filter, mux, sample-delay, and result-control registers. Together they form the performance-monitoring ABI for major graphics blocks:

- CP-side counters: `CPG`, `CPC`, `CPF`, latency stat data/select registers, TC performance counter window selects, and `regCP_PERFMON_CNTL`.
- Front-end and raster blocks: `GRBM`, `WD`, `IA`, `VGT`, `PA_SU`, `PA_SC`, `SPI`, `SQ`, and `SX`.
- Memory/cache blocks: `GDS`, `TA`, `TD`, `TCP`, `TCC`, `TCA`, `CB`, `DB`, `RLC`, and `RMI`.
- UTCL2 blocks: `regATC_L2_PERFCOUNTER_*`, `regMC_VM_L2_PERFCOUNTER_*`, `regL2TLB_PERFCOUNTER_*`, matching `*_CFG` registers, and `*_RSLT_CNTL` registers.

RLC SPM offsets in this range are especially important: `regRLC_SPM_PERFMON_CNTL`, ring base/size registers, SE/global muxsel address/data, per-block sample delay registers, ring read pointer, segment threshold, and `regRLC_SPM_PERFMON_SAMPLE_DELAY_MAX`. These are the address definitions used by profiling paths that stream sampled performance data through an RLC-managed memory ring.

### RLC Control, Firmware, Power, and Error State

`xcd0_gc_rlcpdec` maps the RLC control plane:

- Bring-up and safe-mode registers: `regRLC_CNTL`, `regRLC_STAT`, `regRLC_SAFE_MODE`, `regRLC_RLCV_SAFE_MODE`, `regRLC_SMU_SAFE_MODE`, `regRLC_RLCV_COMMAND`, and `regSMU_RLC_RESPONSE`.
- Timers and clocks: refclock timestamp pairs, `regRLC_GPM_TIMER_INT_*`, `regRLC_GPM_TIMER_CTRL`, `regRLC_GPM_TIMER_STAT`, GPU clock count pairs, capture registers, `regRLC_CLK_COUNT_*`, and clock-count control/status.
- Clock/power gating and load balancing: `regRLC_MGCG_CTRL`, `regRLC_PG_CNTL`, `regRLC_CGTT_MGCG_OVERRIDE`, `regRLC_CGCG_CGLS_CTRL*`, ramp control, dynamic/static PG status/request, CU masks, load-balance parameters, thread priority/enable, and max/always-on CU masks.
- RLC memory and firmware windows: GPM general registers, scratch address/data, SRM ARAM/DRAM/index-control address/data windows, SRM command/status/abort, CSIB address/length, SMU command/argument registers, and scheduler registers.
- UTCL1/prewalker/DSM/error paths: `regRLC_GPM_UTCL1_*`, `regRLC_SPM_UTCL1_*`, `regRLC_PREWALKER_UTCL1_*`, `regRLC_UTCL1_STATUS*`, `regRLC_UTCL2_CNTL`, `regRLC_DSM_*`, and corrected/uncorrected error status registers.
- Interrupt and synchronization offsets: RLC/GPM interrupt status, disable/force registers, CP EOF interrupt counters, spare interrupts, and `regRLC_SEMAPHORE_0..3`.

This block is central to GFX firmware bring-up, suspend/resume, reset, power management, performance monitoring, and error handling.

### CGTS, CGTT, and Power Block Offsets

`xcd0_gc_pwrdec` provides clock/power control offsets:

- `regCGTS_SM_CTRL_REG`, read-control/read-data registers, and TCC disable/user TCC disable registers.
- Per-CU CGTS control registers for CU0 through CU15, including `SP0`, `LDS_SQ`, `TA_SQC`, `SP1`, `TD_TCP`, and separate `TCPI` controls.
- Per-block CGTT clock controls for SPI, SPIS, PC, BCI, VGT, IA, WD, PA, SC, SQ, SQG, TD, TA, TCPI, TCX, DB, CB, TCC, TCA, CP, CPC, RLC, RMI, and TCPF.
- SQ power-throttle offsets and `regRLC_GFX_RM_CNTL`.

These offsets describe persistent hardware policy registers used to gate clocks, disable harvested units, or throttle shader resources. They must stay consistent with power-management policy, topology discovery, and SMU/RLC firmware expectations.

### Hypervisor, SR-IOV, VM, and Security Windows

`xcd0_gc_hypdec` maps privileged controls:

- CP microcode aliases: `regCP_HYP_PFP_UCODE_ADDR/DATA`, `regCP_PFP_UCODE_ADDR/DATA`, `regCP_HYP_ME_UCODE_ADDR/DATA`, `regCP_ME_RAM_RADDR/WADDR/DATA`, CE and MEC1/2 hypervisor/non-hypervisor address/data aliases, checksum registers, and `regCP_HYP_XCP_CTL`.
- RLC/GPM microcode and scratch: `regRLC_GPM_UCODE_ADDR/DATA`, `regRLC_GPU_IOV_UCODE_ADDR/DATA`, and `regRLC_GPU_IOV_SCRATCH_ADDR/DATA`.
- GRBM shadow-register selection: `regGRBM_GFX_INDEX_SR_SELECT/DATA`, `regGRBM_GFX_CNTL_SR_SELECT/DATA`, and `regGRBM_MCM_ADDR`.
- GPU IOV state: `regRLC_GPU_IOV_VF_ENABLE`, scheduler/config registers, active function ID, VM busy status, virtual reset request/response, F32 control/reset, interrupt status/disable/force, SMU response, SDMA0..7 status and busy-status registers, RLCV timer controls, VF doorbell status/set/clear, VF masks, and hypervisor semaphores.

`xcd0_gc_utcl2_vmsharedhvdec` extends virtualization and memory-management state with `regMC_VM_FB_SIZE_OFFSET_VF0..VF15`, MARC base/relocation/length low/high groups, IOMMU control/performance controls, PCIe ATS controls for PF and VF0..VF15, shared active function ID, and XGMI GPU IOV enable.

`xcd0_gc_pspdec` maps PSP/security-related offsets such as `regCPG_PSP_DEBUG`, `regCPC_PSP_DEBUG`, `regCP_PSP_XCP_CTL`, `regGRBM_SEC_CNTL`, GRBM IOV error FIFO data, DSM bypass, CAM index/data aliases, and `regRLC_FWL_FIRST_VIOL_ADDR`.

These ranges are privilege-sensitive. Many macros are valid only in PF, hypervisor, PSP, firmware-load, or diagnostic paths.

### SQ Indirect Wave Debug Indexes

The chunk ends at the start of the `sqind` address block with `ixSQ_DEBUG_STS_LOCAL`, `ixSQ_DEBUG_CTRL_LOCAL`, `ixSQ_WAVE_VALID_AND_IDLE`, `ixSQ_WAVE_MODE`, `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_TRAPSTS`, `ixSQ_WAVE_HW_ID`, `ixSQ_WAVE_GPR_ALLOC`, `ixSQ_WAVE_LDS_ALLOC`, and `ixSQ_WAVE_IB_STS`. These are indirect indexes for local SQ wave inspection and control, not direct register offsets.

## Control Flow and State Behavior

There is no executable control flow in this header. It affects runtime behavior by making symbolic register addresses available to compiled driver code.

The state represented by the macros is hardware-resident state. Important persistent or latched hardware state includes CP counters and ring/IB pointers, scratch and semaphore addresses, coherency ranges/status, draw/dispatch operands, SQ thread-trace buffers, DB/GDS counters and atomic windows, performance counter selections and samples, RLC firmware/safe-mode/timer/power-gating state, RLC SRM/GPM memory windows, clock-gating and throttle policy, SR-IOV scheduler and doorbell state, per-VF memory apertures, IOMMU/ATS state, security CAM/firewall state, and SQ wave debug status.

Some offsets name command or access windows rather than durable configuration. Examples include CP DMA command registers, GDS atomic operation registers, RLC capture/command/status pairs, SRM command windows, GRBM shadow-register select/data windows, CP/RLC microcode address/data ports, doorbell set/clear registers, and SQ indirect debug control. Correct users must follow the sequencing, polling, and timeout rules in the owning AMDGPU code and hardware specification; the offset header itself encodes only addresses.

## Dependencies and Integration Points

This chunk depends on the AMD generated register-header convention:

- `gc_9_4_3_offset.h` supplies register and index offsets.
- `gc_9_4_3_sh_mask.h` supplies field shifts and masks for many of the same register names.
- SOC15 access macros combine the GC IP block, GC/XCC instance, `_BASE_IDX`, and register offset into actual MMIO addresses.

Observed source-tree integration points include:

- `drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c`, which includes this header, writes `regGRBM_GFX_INDEX` through RLC-shadow-aware paths, reads `regRLC_CNTL`, and registers GC 9.4.3 debug access controls.
- `drivers/gpu/drm/amd/amdgpu/gfxhub_v1_2.c`, which includes this header for GC 9.4.3 address definitions used by the graphics hub.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gc_9_4_3.c`, which includes this header for KFD/compute integration on GC 9.4.3.
- Cross-generation AMDGPU code shows the same symbolic families used for firmware and register access patterns, for example `regGRBM_GFX_INDEX`, `regRLC_CNTL`, and `regCP_HYP_PFP_UCODE_ADDR` in nearby GFX 11/12 implementations. GC 9.4.3 consumers must still include the GC 9.4.3-specific offset/mask set because offsets and available registers can drift by generation.

The main external dependencies are the hardware register specification, RLC/CP/PSP/SMU firmware contracts, SR-IOV virtualization policy, and kernel AMDGPU helper APIs. The header is not useful independently of those consumers.

## Risks

- Offset drift is high impact. A wrong offset or base index can read or write a different hardware register, causing queue hangs, bad performance data, failed firmware load, broken power management, or loss of PF/VF isolation.
- The repeated performance-counter families are mechanically similar but not interchangeable. Counter counts, LO/HI ordering, selector availability, and block-specific control registers vary across CP, GRBM, SQ, memory, DB/CB, and RLC/RMI blocks.
- Several names are aliases for the same offset, such as CP ME/PFP/hypervisor microcode windows and atomic pre-operation registers. Consumers must choose the alias that matches privilege level and engine semantics, not infer that aliases are independent registers.
- `GRBM_GFX_INDEX` and the GRBM shadow-register select/data windows affect register targeting. Incorrect selection can program the wrong shader engine, shader array, instance, or VF/PF context.
- RLC, CGTS, CGTT, and SQ power-throttle registers affect firmware execution and clock/power state. Uncoordinated writes can desynchronize RLC/SMU policy, clock gates, or harvested-unit masks.
- SR-IOV, per-VF framebuffer aperture, IOMMU, ATS, doorbell, scheduler, and SDMA status offsets are isolation-sensitive. Incorrect programming can corrupt virtual function scheduling or memory partitioning.
- Indirect windows such as SRM RAM, CP microcode address/data, RLC GPU IOV scratch, GDS burst/atomic windows, and SQ wave debug indexes require strict address/data sequencing and status polling.
- The chunk begins and ends mid-file. The final merged per-file report must connect this research with adjacent chunks for the earlier part of `xcd0_gc_gfxudec` and the remaining SQ indirect register indexes.

## Test and Validation Signals

Useful validation is mostly build, bring-up, and hardware integration coverage:

- Compile AMDGPU and KFD code paths that include `gc/gc_9_4_3_offset.h`; missing or renamed macros should fail at build time.
- GC 9.4.3 bring-up and reset tests should exercise `regRLC_CNTL`, `regRLC_STAT`, safe-mode registers, RLC timers, clock counters, SMU command/response offsets, and GRBM targeting.
- Queue and command-submission tests should cover CP ring/IB offsets, CP DMA registers, scratch/semaphore registers, draw/dispatch indirect-address registers, completion status, and coherency registers.
- Performance tooling should validate counter LO/HI reads, selector programming, RLC SPM ring setup, mux selection, sample delays, result-control registers, and UTCL2 ATC/VM/L2TLB counter configuration.
- Debug/profiling tests should cover SQ thread trace, SQ indirect wave status indexes, DB occlusion/Z-pass counters, GDS atomic/OA windows, and GRBM instance selection.
- Power-management tests should cover CGTS/CGTT clock controls, TCC disable state, SQ throttle, RLC power-gating registers, and suspend/resume restoration.
- SR-IOV validation should exercise VF enablement, per-VF framebuffer size/offsets, MARC windows, IOMMU/ATS controls, doorbell set/clear/mask registers, scheduler state, SDMA status/busy status, virtual reset, and interrupt paths.
- Security/PSP diagnostics should verify GRBM security controls, IOV error FIFO data, CAM index/data aliases, DSM bypass handling, and RLC firewall violation reporting.
