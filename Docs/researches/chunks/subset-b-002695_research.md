# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 24637-27087

## Scope

This chunk covers generated shift and mask macros for GC 9.4.3 graphics-core registers. It begins in the tail of `GRBM_PERFCOUNTER0_SELECT`, continues through broad performance counter selector coverage, and ends inside the `RLC_SRM_RLCV_COMMAND` field list. The covered range includes:

- Global and per-shader-engine GRBM performance counter selector fields.
- WD, IA, VGT, PA_SU, PA_SC, SPI, SQ, SX, GDS, TA, TD, TCP, TCC, TCA, CB, DB, RLC, RMI, ATC_L2, MC_VM_L2, and L2TLB performance counter configuration fields.
- RLC streaming performance monitor ring, segment, mux select, sample delay, and memory-client/interrupt controls.
- RLC GPU IOV performance counter access windows.
- GDFLL EDC hysteresis control and status fields.
- RLC core control, status, safe-mode, SMU/RLCV command, timers, interrupts, load balancing, clock-gating, power-gating, clock counter, GPM thread, serdes, scratch, log, interrupt force/disable, and save/restore memory fields.

The file is a generated hardware register bitfield map. This chunk defines preprocessor constants only. It contains no C functions, structs, variables, executable branches, or software storage.

## Purpose

The purpose of this header section is to provide the bit-level ABI between GC 9.4.3 hardware registers and AMDGPU/KFD driver code. Each field is represented by the generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for a field.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask for extracting or composing that field.

Driver code pairs these macros with register address definitions from `gc_9_4_3_offset.h` and helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, and `SOC15_REG_OFFSET`. The constants are therefore not business logic by themselves; they are the authoritative encoding used when software programs MMIO state for profiling, power management, virtualization, firmware coordination, and low-level graphics-core control.

## Important Macro Families

### Performance Counter Selection

The first major section is dominated by performance counter selector macros. These registers choose which hardware event each block-local counter observes and how the counter is filtered or counted.

Common selector patterns appear across many blocks:

- `*_PERFCOUNTER0_SELECT` often exposes `PERF_SEL`, `PERF_SEL1`, `CNTR_MODE`, `PERF_MODE1`, and `PERF_MODE`, supporting packed selection of multiple event lanes plus counter modes.
- Matching `*_PERFCOUNTER0_SELECT1` registers often expose `PERF_SEL2`, `PERF_SEL3`, `PERF_MODE2`, and `PERF_MODE3`.
- Later counters in the same block may be simpler, with only `PERF_SEL` and `PERF_MODE`.
- Some blocks use narrower event selectors. For example, GRBM uses a 6-bit `PERF_SEL`; SQ uses a 9-bit `PERF_SEL` plus SQC bank/client masks, SPM mode, SIMD mask, and performance mode; CB and RMI selectors use 9-bit event masks.

Covered graphics and shader blocks include GRBM, WD, IA, VGT, PA_SU, PA_SC, SPI, SQ, SX, GDS, TA, TD, TCP, TCC, TCA, CB, DB, RLC, and RMI. This makes the chunk a central source for profiling and debug paths that program GC 9.4.3 counters.

Specialized control registers in this group include:

- `GRBM_PERFCOUNTER*_SELECT` and `GRBM_SE*_PERFCOUNTER_SELECT`, which combine event selection with user-defined busy/clean masks for major graphics blocks such as DB, CB, VGT, TA, SX, SPI, SC, PA, CP, IA, GDS, RLC, TC, WD, UTCL2, EA, and RMI.
- `VGT_PERFCOUNTER_SEID_MASK`, which filters VGT counting by shader-engine ID.
- `SPI_PERFCOUNTER_BINS`, which defines four min/max bin ranges for SPI counter bucketing.
- `SQ_PERFCOUNTER_CTRL`, `SQ_PERFCOUNTER_MASK`, and `SQ_PERFCOUNTER_CTRL2`, which gate SQ counting by shader stage, counter rate, flush behavior, VMID mask, shader mask, and forced enable.
- `CB_PERFCOUNTER_FILTER`, which enables and selects operation, format, clear, MRT, sample-count, and fragment-count filters before CB counter samples are accepted.
- `RMI_PERF_COUNTER_CNTL`, which selects transaction/event/TC enables, event windows, CID/VMID filters, burst-length threshold, soft reset, and SPM selection.

### RLC Streaming Performance Monitor

The `RLC_SPM_*` section defines the streaming performance monitor path owned by RLC:

- `RLC_SPM_PERFMON_CNTL` selects ring mode and sample interval.
- `RLC_SPM_PERFMON_RING_BASE_LO`, `_HI`, and `_RING_SIZE` define the capture buffer address and size.
- `RLC_SPM_PERFMON_SEGMENT_SIZE` and `RLC_SPM_SEGMENT_THRESHOLD` describe global and per-SE sample segmentation.
- `RLC_SPM_SE_MUXSEL_ADDR/DATA` and `RLC_SPM_GLOBAL_MUXSEL_ADDR/DATA` provide indirect RAM-style programming windows for sample source mux selections.
- `RLC_SPM_RING_RDPTR` exposes the software-visible read pointer.
- Per-block `RLC_SPM_*_PERFMON_SAMPLE_DELAY` registers tune sample timing for CPG, CPC, CPF, CB, DB, PA, GDS, IA, SC, TCC, TCA, TCP, TA, TD, VGT, SPI, SQG, SX, and RMI.
- `RLC_SPM_PERFMON_SAMPLE_DELAY_MAX` caps the maximum sample delay.
- `RLC_SPM_MC_CNTL`, `RLC_SPM_INT_CNTL`, and `RLC_SPM_INT_STATUS` configure the memory-client attributes and interrupt control/status for SPM output.

These fields are stateful hardware controls: software programs a ring, muxes, segment sizes, and delays, then relies on RLC and hardware blocks to stream samples into memory.

### RLC and IOV Performance Counter Windows

`RLC_PERFMON_CNTL`, `RLC_PERFCOUNTER0_SELECT`, and `RLC_PERFCOUNTER1_SELECT` define RLC-local performance counter state. `RLC_PERFMON_CNTL` exposes a small `PERFMON_STATE` field and a sample-enable bit.

The `RLC_GPU_IOV_PERF_CNT_*` registers expose a virtualization-aware counter access path:

- `RLC_GPU_IOV_PERF_CNT_CNTL` enables, selects mode, and resets the IOV performance counter mechanism.
- `RLC_GPU_IOV_PERF_CNT_WR_ADDR` and `_RD_ADDR` select a VF ID and counter ID.
- `RLC_GPU_IOV_PERF_CNT_WR_DATA` and `_RD_DATA` carry the small per-counter data payload.

These fields are tied to SR-IOV or partitioned-GPU operation and should be treated as privileged RLC/virtualization control, not generic user-facing performance counter state.

### UTCL2, VM L2, and L2TLB Counters

The address-block sections for `xcd0_gc_utcl2_atcl2pfcntldec`, `xcd0_gc_utcl2_vml2pldec`, and `xcd0_gc_utcl2_l2tlbpldec` cover translation and VM-cache performance counters:

- `ATC_L2_PERFCOUNTER0_CFG` and `ATC_L2_PERFCOUNTER1_CFG` select ATC L2 event ranges, modes, enable bits, and clear bits.
- `ATC_L2_PERFCOUNTER_RSLT_CNTL` selects a counter result and defines start/stop triggers, enable-any, clear-all, and stop-on-saturate behavior.
- `MC_VM_L2_PERFCOUNTER0_CFG` through `MC_VM_L2_PERFCOUNTER7_CFG` provide the same style of selection, mode, enable, and clear fields for VM L2 performance counters.
- `MC_VM_L2_PERFCOUNTER_RSLT_CNTL` controls result selection and aggregate start/stop/clear behavior for the VM L2 group.
- `L2TLB_PERFCOUNTER0_CFG` through `L2TLB_PERFCOUNTER3_CFG` and `L2TLB_PERFCOUNTER_RSLT_CNTL` do the same for L2 TLB events.

These registers connect graphics-core profiling to address translation and VM behavior. They are useful for memory-management performance analysis but can be confused with similarly named GMC/MMHUB counter blocks in other generated headers.

### GDFLL EDC Hysteresis

`GDFLL_EDC_HYSTERESIS_CNTL` and `GDFLL_EDC_HYSTERESIS_STAT` provide graphics dynamic frequency loop fields related to EDC hysteresis:

- `max_hysteresis` configures a hysteresis limit.
- `edc_frequency_status` and `hysteresis_count` report observed status.

These fields are power/frequency-management state and should remain coordinated with the SMU and platform power policy.

### RLC Core, Safe Mode, Timers, and Interrupts

The `xcd0_gc_rlcpdec` portion starts a broad RLC control block:

- `RLC_CNTL` exposes RLC enablement, central queue, RLCM, SRM, clock counter, sleep, save/restore, safe mode, request-table invalidation, register-write gating, and queue-selection fields.
- `RLC_CGCG_CGLS_CTRL_2`, `RLC_MGCG_CTRL`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, and `RLC_CGCG_RAMP_CTRL` describe clock-gating, light-sleep, ramp, and override controls.
- `RLC_STAT` and `RLC_GPM_STAT` expose RLC sleep, wait-for-idle, 3D-full, GPM idle, power/clock status, context processing, register save/restore, CU power transitions, clock-gating override status, ROM execution, and power-gating error state.
- `RLC_SAFE_MODE`, `RLC_RLCV_SAFE_MODE`, `RLC_SMU_SAFE_MODE`, `SMU_RLC_RESPONSE`, `RLC_RLCV_COMMAND`, and `RLC_SMU_MESSAGE` form command/response channels between software, RLC, RLCV, and SMU-controlled safe-mode or command flows.
- `RLC_REFCLOCK_TIMESTAMP_LSB/MSB`, `RLC_GPU_CLOCK_COUNT_LSB/MSB`, `RLC_CAPTURE_GPU_CLOCK_COUNT`, `RLC_CLK_COUNT_GFXCLK_*`, `RLC_CLK_COUNT_REFCLK_*`, `RLC_CLK_COUNT_CTRL`, `RLC_CLK_COUNT_STAT`, `RLC_GPU_CLOCK_32_RES_SEL`, and `RLC_GPU_CLOCK_32` define timestamp, clock-count capture, run/reset/sample controls, and valid/resync status.
- `RLC_GPM_TIMER_INT_0..3`, `RLC_GPM_TIMER_CTRL`, and `RLC_GPM_TIMER_STAT` define timer intervals, enables, status bits, and enable synchronization.
- `RLC_INT_STAT`, `RLC_GPM_INT_DISABLE_TH0`, `RLC_GPM_INT_FORCE_TH0`, and `RLC_GPM_INT_FORCE_TH1` expose interrupt status and thread-specific interrupt disable/force masks.

Several fields in this group are command-like or latch-like rather than durable configuration. Examples include safe-mode command bits, GPU clock capture, timer status/enable synchronization, interrupt force fields, and clock-count sample/reset bits.

### RLC Power Gating and Load Balancing

The chunk includes many per-CU and graphics power-gating fields:

- `RLC_PG_CNTL` controls graphics power gating, dynamic/static per-CU power gating, graphics pipeline PG, overrides, CP PG disable, CHUB/SMU handshake behavior, clock slowdown on power-up/down, ultra-low-voltage enable, and SMU handshake disable.
- `RLC_DYN_PG_STATUS`, `RLC_DYN_PG_REQUEST`, `RLC_STATIC_PG_STATUS`, `RLC_CU_STATUS`, `RLC_LB_INIT_CU_MASK`, `RLC_LB_ALWAYS_ACTIVE_CU_MASK`, and `RLC_PG_ALWAYS_ON_CU_MASK` expose or request CU-level power state and masks.
- `RLC_PG_DELAY`, `RLC_PG_DELAY_2`, and `RLC_PG_DELAY_3` tune power-up/down, command propagation, memory sleep, serdes timeout, per-CU timeout, and CGCG-before-CGPG delays.
- `RLC_LB_CNTL`, `RLC_LB_CNTR_MAX`, `RLC_LB_CNTR_INIT`, `RLC_LOAD_BALANCE_CNTR`, `RLC_LB_PARAMS`, `RLC_THREAD1_DELAY`, `RLC_MAX_PG_CU`, and `RLC_AUTO_PG_CTRL` control load-balancing counters and automatic power-gating thresholds.
- `RLC_SMU_GRBM_REG_SAVE_CTRL` starts GRBM register save behavior under SMU/RLC coordination.

These fields describe persistent hardware policy and observed state. Incorrect programming can change power sequencing, CU availability, or clock-gating behavior.

### RLC GPM, Serdes, Scratch, and SRM Access

The tail of the chunk covers RLC internal machinery:

- `RLC_GPM_THREAD_RESET`, `RLC_GPM_THREAD_PRIORITY`, and `RLC_GPM_THREAD_ENABLE` control/reset and prioritize four GPM threads.
- `RLC_GPM_CP_DMA_COMPLETE_T0/T1`, `RLC_UCODE_CNTL`, `RLC_FIREWALL_VIOLATION`, `RLC_GPM_GENERAL_0..7`, `RLC_GPM_SCRATCH_ADDR/DATA`, `RLC_GPM_LOG_SIZE`, `RLC_GPM_LOG_CONT`, `RLC_GPR_REG1`, and `RLC_GPR_REG2` provide firmware-visible completion, control, scratch, log, and general-purpose state.
- `RLC_SERDES_RD_PENDING`, `RLC_SERDES_RD_MASTER_INDEX`, `RLC_SERDES_RD_DATA_0..2`, `RLC_SERDES_WR_CU_MASTER_MASK`, `RLC_SERDES_WR_NONCU_MASTER_MASK`, `RLC_SERDES_WR_NONCU_MASTER_MASK_1`, `RLC_SERDES_WR_CTRL`, `RLC_SERDES_WR_DATA`, `RLC_SERDES_CU_MASTER_BUSY`, `RLC_SERDES_NONCU_MASTER_BUSY`, and `RLC_SERDES_NONCU_MASTER_BUSY_1` define read/write selection, power up/down command bits, command/data payloads, master masks, and busy state for CU and non-CU serdes operations.
- `RLC_MEM_SLP_CNTL` controls memory light-sleep delays and disable controls for IRAM, DRAM, ARAM, and GPR storage.
- `RLC_SRM_CNTL`, `RLC_SRM_ARAM_ADDR/DATA`, `RLC_SRM_DRAM_ADDR/DATA`, `RLC_SRM_GPM_COMMAND`, `RLC_SRM_GPM_COMMAND_STATUS`, and the beginning of `RLC_SRM_RLCV_COMMAND` define save/restore memory enable, auto-increment, indirect ARAM/DRAM address/data access, command queue fields, and FIFO empty/full status.

The chunk ends before the complete `RLC_SRM_RLCV_COMMAND` field set is visible, so any merged file-level report should stitch this section to the next chunk.

## Control Flow and State Behavior

There is no software control flow in this chunk. Its impact is compile-time: C code expands these macros to compose and decode 32-bit MMIO register values.

The state described here lives in hardware. Important state includes performance event selection, counter enable/clear/result selection, RLC SPM ring base/size/read pointer and mux programming, per-block SPM sample timing, RLC/IOV counter windows, translation/cache counter controls, GDFLL EDC hysteresis, RLC enable/safe-mode/SMU command state, RLC timer and interrupt state, clock-count capture state, power-gating and load-balancing policy, GPM thread controls, serdes command/busy state, scratch/log storage, and SRM command FIFO state.

Some fields are persistent configuration until rewritten. Others are status bits, command strobes, reset bits, clear bits, or indirect address/data windows. Consumers must follow the sequencing rules in the owning AMDGPU/KFD code and the hardware specification, especially for safe-mode handshakes, SMU messages, SPM ring setup, result-control clear/enable bits, RLC timer status, serdes read/write busy polling, and SRM FIFO command submission.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `gc_9_4_3_offset.h` supplies the register addresses and base indices for the names whose fields are defined here.
- `gc_9_4_3_default.h` supplies reset/default values where generated for this ASIC.
- AMDGPU helper macros consume the `__SHIFT` and `_MASK` definitions to avoid open-coded bit positions.

Direct includes in this tree show GC 9.4.3 integration through:

- `drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c`, which includes `gc_9_4_3_offset.h` and `gc_9_4_3_sh_mask.h` for graphics-core initialization and control.
- `drivers/gpu/drm/amd/amdgpu/gfxhub_v1_2.c`, which includes the same GC 9.4.3 headers for GFXHUB-related register programming.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gc_9_4_3.c`, which bridges AMDGPU and KFD behavior on this generation.
- `drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v9.c`, which includes `gc_9_4_3_sh_mask.h` for queue-management register field encodings.

Implied consumers include performance/debug paths that program GC counters and RLC SPM, power-management paths that coordinate RLC/SMU clock and power-gating state, virtualization paths that access RLC GPU IOV counters, and firmware/RLC bring-up paths that enable RLC, check status, manage safe mode, and inspect timer/interrupt/serdes/SRM state.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can program adjacent hardware fields, causing hangs, incorrect counters, bad power sequencing, lost interrupts, broken virtualization accounting, or firmware/RLC failures.
- Repeated performance-counter families are mechanically similar but not identical. Selector width and presence of `PERF_SEL1`, `SELECT1`, `CNTR_MODE`, filters, and SPM mode fields vary by block.
- The chunk starts and ends mid-family. It begins after `GRBM_PERFCOUNTER0_SELECT` has already started and ends inside `RLC_SRM_RLCV_COMMAND`, so consumers of generated documentation must reconcile adjacent chunks before treating either family as complete.
- RLC SPM setup combines address/data windows, ring memory, mux RAM, segment sizing, sample delays, and interrupt controls. Missing ordering or pointer handling can produce corrupt samples or stalled collection.
- Counter result-control registers contain enable, clear, start/stop trigger, and stop-on-saturate fields. Treating clear or enable bits as ordinary passive state can disrupt profiling.
- RLC safe-mode, SMU message, RLCV command, and SRM/serdes fields are handshake-oriented. They require polling and timeout policy outside this header.
- Power-gating and clock-gating fields are platform-sensitive. Incorrect `RLC_PG_CNTL`, delay, CU mask, load-balancing, or clock-count control programming can affect power transitions, CU availability, or suspend/resume stability.
- Virtualization-related IOV performance counter fields are privilege-sensitive and should remain isolated to PF/hypervisor-aware paths.

## Test and Validation Signals

Useful validation is mostly integration-oriented:

- Build coverage for AMDGPU and KFD code that includes `gc_9_4_3_sh_mask.h`; this catches missing or renamed macros and incompatible generated headers.
- GC 9.4.3 bring-up, reset, suspend/resume, and RLC firmware tests should exercise `RLC_CNTL`, `RLC_STAT`, safe-mode registers, SMU/RLCV command paths, timers, interrupts, and GPM status.
- Performance counter tests should program representative counters across GRBM, WD, IA, VGT, PA, SPI, SQ, SX, GDS, TA/TD/TCP/TCC/TCA, CB/DB, RLC, RMI, ATC_L2, MC_VM_L2, and L2TLB, then verify expected event increments and result-control clear/enable behavior.
- RLC SPM validation should check ring base/size setup, mux select programming, segment sizing, read-pointer movement, per-block sample delays, interrupt status, and memory-client attributes.
- Power-management tests should cover RLC clock-gating, graphics power-gating, per-CU power-gating masks, auto-PG thresholds, clock-count capture, and SMU handshake behavior.
- SR-IOV or partitioning tests should verify the RLC GPU IOV performance counter address/data windows use the correct VF ID and counter ID fields.
- Low-level RLC diagnostic tests should exercise serdes busy polling, read/write data selection, GPM scratch/log access, SRM ARAM/DRAM indirect windows, and SRM command FIFO empty/full status.

## Unresolved Cross-Chunk References

The first visible line is the final shift definition for `GRBM_PERFCOUNTER0_SELECT`; the earlier fields in that register are in the previous chunk. The last visible lines are the beginning of `RLC_SRM_RLCV_COMMAND` and stop after `RLC_SRM_RLCV_COMMAND__RESERVED_16_MASK`; the remaining fields and masks for that command register are in the next chunk. The merge/reconciliation lane should combine adjacent chunk reports before producing a final file-level document.
