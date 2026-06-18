# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 22321-24774

## Scope

This chunk is a generated AMD GC 9.1 shift/mask header slice. It contains 2,154 `#define` constants grouped by register-name comments. The range starts inside the `CPG_PERFCOUNTER1_SELECT` field list and ends at `RLC_SRM_INDEX_CNTL_ADDR_0`, so both ends require adjacent chunks for complete register-family coverage. There are no functions, structs, enums, variables, allocation paths, locks, or executable statements here.

The covered register groups are:

- Command-processor performance counter selectors and controls for CPG, CPC, CPF, TC counter windows, latency stats, draw-object tracking, and draw-window masks.
- GRBM global and per-shader-engine busy performance counter selectors.
- Graphics pipeline performance counter selectors for WD, IA, VGT, PA/SU, PA/SC, SPI, SQ, SX, GDS, TA, TD, TCP, TCC, TCA, CB, DB, RLC, RMI, ATC L2, and MC VM L2.
- RLC streaming performance monitor ring, mux selection, segment sizing, sample-delay, clock-control, and interrupt/memory-control fields.
- RLC core, safe-mode, SMU/RLCV command, timer, load-balancing, clock-gating, power-gating, CU power status, SERDES master mask/busy, GPM scratch/general, interrupt, and save/restore memory command fields.

## Purpose

The purpose of this header segment is to expose the bit layout of GC 9.1 hardware registers to AMDGPU driver code. The paired offset header supplies register addresses; this file supplies the field encodings used to compose or decode 32-bit MMIO register values.

The generated API pattern is consistent:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for that field.

Most consumers use these constants through register helpers such as `REG_SET_FIELD()`, `REG_GET_FIELD()`, SOC15 MMIO accessors, or local read-modify-write helpers. This chunk is therefore compile-time hardware metadata rather than runtime logic.

## Important Macro Families

### CP, GRBM, And Pipeline Perf Counters

The first half of the chunk is dominated by performance counter selection registers. CP blocks use `CPG_*`, `CPC_*`, and `CPF_*` selector fields such as `CNTR_SEL0..3`, `SPM_MODE`, and `CNTR_MODE0..3`, plus global `CP_PERFMON_CNTL` state and sample-enable bits. `CPF_TC_PERF_COUNTER_WINDOW_SELECT` and `CPG_TC_PERF_COUNTER_WINDOW_SELECT` define index, always, and enable fields for TC performance windows. `CPF_LATENCY_STATS_SELECT`, `CPG_LATENCY_STATS_SELECT`, and `CPC_LATENCY_STATS_SELECT` expose index, clear, and enable controls for latency statistics.

`GRBM_PERFCOUNTER0_SELECT`, `GRBM_PERFCOUNTER1_SELECT`, and `GRBM_SE0_PERFCOUNTER_SELECT` through `GRBM_SE3_PERFCOUNTER_SELECT` select GRBM-level events and user-defined busy/clean masks for blocks such as DB, CB, VGT, TA, SX, SPI, SC, PA, CP, IA, GDS, BCI, RLC, TC, WD, UTCL2, EA, and RMI.

The graphics pipeline selectors include `WD`, `IA`, `VGT`, `PA_SU`, `PA_SC`, `SPI`, `SQ`, `SX`, `GDS`, `TA`, `TD`, `TCP`, `TCC`, `TCA`, `CB`, `DB`, `RLC`, and `RMI` families. Common fields are `PERF_SEL`, `PERF_SEL1`, `PERF_SEL2`, `PERF_SEL3`, `CNTR_MODE`, `SPM_MODE`, `PERF_MODE`, and companion `*_SELECT1` registers. Field widths vary: many blocks use 10-bit selectors, `SQ` uses 9-bit selectors plus `SQC_BANK_MASK`, `SQC_CLIENT_MASK`, and `SIMD_MASK`, while CB and RMI selectors use narrower 9-bit event masks.

Specialized controls include:

- `SPI_PERFCOUNTER_BINS`, which packs four min/max bin ranges.
- `SQ_PERFCOUNTER_CTRL`, with shader-stage enables, per-ME/pipe disable bits, poll-before-read, and shader-engine masking.
- `SQ_PERFCOUNTER_MASK` and `SQ_PERFCOUNTER_CTRL2`, with counter masking and force/VMID filtering.
- `VGT_PERFCOUNTER_SEID_MASK`, which controls shader-engine ID ignore masking.
- `CB_PERFCOUNTER_FILTER`, with operation, format, clear, MRT, sample-count, and fragment-count filters.
- `RMI_PERF_COUNTER_CNTL`, with transaction/event/TC enables, event windows, CID/VMID filters, burst-length threshold, soft reset, and SPM selection.

### UTCL2 And VM L2 Perf Counters

The `gc_utcl2_atcl2pfcntldec` address block defines `ATC_L2_PERFCOUNTER0_CFG`, `ATC_L2_PERFCOUNTER1_CFG`, and `ATC_L2_PERFCOUNTER_RSLT_CNTL`. Each counter config has event start/end selection, mode, enable, and clear fields. The result-control register chooses a counter, defines start/stop triggers, enables any counter, clears all, and can stop all counters on saturation.

The `gc_utcl2_vml2pldec` address block mirrors that shape for `MC_VM_L2_PERFCOUNTER0_CFG` through `MC_VM_L2_PERFCOUNTER7_CFG` and `MC_VM_L2_PERFCOUNTER_RSLT_CNTL`. These fields support memory-management/L2 performance observation rather than graphics-pipe event selection.

### RLC SPM And Perfmon

The RLC streaming performance monitor section includes:

- `RLC_SPM_PERFMON_CNTL`, with ring mode and sample interval.
- `RLC_SPM_PERFMON_RING_BASE_LO`, `RLC_SPM_PERFMON_RING_BASE_HI`, and `RLC_SPM_PERFMON_RING_SIZE`, which describe the memory ring used for streamed samples.
- `RLC_SPM_PERFMON_SEGMENT_SIZE`, with global and SE line counts.
- `RLC_SPM_SE_MUXSEL_ADDR/DATA` and `RLC_SPM_GLOBAL_MUXSEL_ADDR/DATA`, which expose mux selection RAM windows.
- Per-block `RLC_SPM_*_PERFMON_SAMPLE_DELAY` registers for CPG, CPC, CPF, CB, DB, PA, GDS, IA, SC, TCC, TCA, TCP, TA, TD, VGT, SPI, SQG, SX, and RMI.
- `RLC_SPM_RING_RDPTR`, `RLC_SPM_SEGMENT_THRESHOLD`, `RLC_PERFMON_CLK_CNTL`, `RLC_PERFMON_CNTL`, and `RLC_PERFCOUNTER0/1_SELECT`.
- `RLC_SPM_MC_CNTL`, `RLC_SPM_INT_CNTL`, and `RLC_SPM_INT_STATUS`, which describe SPM memory-client attributes and interrupt state.

The chunk also includes `RLC_GPU_IOV_PERF_CNT_*` fields for virtualization-visible performance counter control, write/read address windows keyed by VFID and counter ID, and 4-bit data values.

### RLC Core, Power, And Save/Restore

The `gc_rlcpdec` block defines RLC control and status fields:

- `RLC_CNTL` enables/steps the F32 RLC core, controls retry, and can disable the read cache.
- `RLC_STAT` exposes RLC, GPM, SPM, SRM, MC, and thread busy bits.
- `RLC_SAFE_MODE`, `RLC_RLCV_SAFE_MODE`, `RLC_SMU_SAFE_MODE`, `SMU_RLC_RESPONSE`, `RLC_RLCV_COMMAND`, and `RLC_SMU_MESSAGE` define command, message, and response mailboxes among RLC, RLCV, and SMU paths.
- `RLC_REFCLOCK_TIMESTAMP_*`, `RLC_GPU_CLOCK_COUNT_*`, `RLC_CAPTURE_GPU_CLOCK_COUNT`, `RLC_GPU_CLOCK_32_RES_SEL`, and `RLC_GPU_CLOCK_32` describe timestamp and clock-count readback.
- `RLC_GPM_TIMER_INT_0..3`, `RLC_GPM_TIMER_CTRL`, and `RLC_GPM_TIMER_STAT` define RLC GPM timer intervals, enable bits, and status bits.
- `RLC_INT_STAT`, `RLC_FIREWALL_VIOLATION`, `RLC_GPM_STAT`, and `RLC_CU_STATUS` expose interrupt, fault-address, power-management, and work-pending status.
- `RLC_LB_CNTL`, `RLC_LB_CNTR_MAX`, `RLC_LB_CNTR_INIT`, `RLC_LOAD_BALANCE_CNTR`, `RLC_LB_INIT_CU_MASK`, `RLC_LB_ALWAYS_ACTIVE_CU_MASK`, `RLC_LB_PARAMS`, and `RLC_THREAD1_DELAY` configure CU load balancing and power-gating heuristics.
- `RLC_MGCG_CTRL`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, `RLC_CGCG_RAMP_CTRL`, `RLC_PG_CNTL`, `RLC_PG_DELAY`, `RLC_PG_DELAY_2`, `RLC_PG_DELAY_3`, `RLC_DYN_PG_STATUS`, `RLC_DYN_PG_REQUEST`, `RLC_STATIC_PG_STATUS`, `RLC_PG_ALWAYS_ON_CU_MASK`, `RLC_MAX_PG_CU`, `RLC_AUTO_PG_CTRL`, and `RLC_SMU_GRBM_REG_SAVE_CTRL` cover clock gating, light/deep sleep, power gating, per-CU power status/request masks, and SMU handshakes.

The SERDES and save/restore area includes `RLC_SERDES_RD_MASTER_INDEX`, read data ports, CU/non-CU master write masks, `RLC_SERDES_WR_CTRL`, `RLC_SERDES_WR_DATA`, CU/non-CU busy status, `RLC_GPM_GENERAL_0..7`, `RLC_GPM_SCRATCH_ADDR/DATA`, GPM log and interrupt disable/force registers, and `RLC_SRM_*` ARAM/DRAM/GPM/RLCV command fields. The chunk ends after `RLC_SRM_INDEX_CNTL_ADDR_0`, so the following index-control registers and any remaining SRM fields belong to the next chunk.

## Control Flow

There is no direct control flow in this header. Runtime behavior is supplied by AMDGPU code that includes the generated header and performs MMIO access. Typical flows are:

1. Driver code selects a GC 9.1 register address from the paired offset header.
2. It composes a value by shifting field values by `__SHIFT` and constraining them with `_MASK`, usually through helper macros.
3. It writes the register, or reads a register and decodes fields through the matching mask/shift pair.
4. For status or command-like fields, surrounding driver code handles ordering, polling, timeouts, and reset/suspend sequencing.

Performance-counter flows program selector and mode fields, optionally set filters, VMID/CID masks, bins, sample delays, or SPM muxes, run a workload, then read counters or streamed samples. RLC flows are more stateful: safe-mode entry/exit, SPM ring setup, timer configuration, clock/power-gating control, SERDES commands, SRM transfers, and SMU/RLCV mailboxes require hardware-specific sequencing outside this header.

## State And Persistence Behavior

The macros hold no software state. They describe hardware state that persists in GC registers until reset, power loss, firmware reinitialization, or explicit driver writes.

Performance counter selectors, filters, windows, and SPM modes persist as programmed hardware configuration and directly affect collected profiling data. Counter result-control bits such as clear, enable, start/stop trigger, and saturation behavior are command/configuration fields whose effects depend on hardware state.

RLC SPM state includes memory ring base/size, read pointer, mux selection RAM contents, segment size/threshold, sample delays, memory-client attributes, interrupts, and global/per-block perfmon state. Misprogrammed base addresses or sizes affect DMA-like writes to the SPM ring.

RLC core and power-management fields represent durable control state and live status. Clock-gating, CGCG/CGLS, load-balancing, power-gating, per-CU request/status masks, and SMU handshakes can remain active across workloads. Status registers such as `RLC_STAT`, `RLC_GPM_STAT`, SERDES busy registers, timer status, and SPM interrupt status are live observations that may change asynchronously with firmware and hardware activity.

SRM, SERDES, scratch, and mailbox fields are indirect access windows or command/status registers. Their data registers do not represent ordinary persistent kernel memory; they represent hardware/firmware-visible storage or command FIFOs whose interpretation depends on current RLC/SRM state.

## Dependencies And Integration Points

This chunk depends on the generated AMD register database for GC 9.1 and must stay synchronized with:

- `gc_9_1_offset.h`, which provides register addresses and address-block mappings for the names defined here.
- Adjacent generated headers such as default-value files and other GC 9.1 register namespaces.
- AMDGPU SOC15 register access helpers and bitfield helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()`.
- GC 9.1 graphics, compute, KFD, profiling, virtualization, clock/power-management, reset, and firmware-control paths that program CP, GRBM, SQ, memory L2, RLC, SPM, and SRM registers.

The path is under a `ceph-client` source mirror, but this file is AMD GPU driver hardware metadata. It has no Ceph protocol behavior, distributed filesystem data path, network persistence, or storage consistency logic.

## Risks And Edge Cases

- These are untyped preprocessor constants. Incorrect masks or shifts can compile cleanly and produce wrong MMIO writes.
- The chunk starts inside `CPG_PERFCOUNTER1_SELECT` and ends inside the RLC SRM index-control area. Whole-file analysis must merge adjacent chunks before making complete claims about those families.
- Repeated performance-counter families look similar but have different selector widths and upper-bit meanings. For example, SQ selectors include SQC/SIMD masks, CB/RMI selectors use narrower event fields, and some pipeline counters only expose a single `PERF_SEL`.
- Selector/mode field swaps can produce plausible but wrong profiling results, which are hard to catch with normal build tests.
- Clear, enable, force, reset, safe-mode command, capture, and interrupt-force bits are not all ordinary persistent settings. Treating command-like bits as passive configuration can cause lost samples, stuck status bits, or firmware sequencing failures.
- RLC SPM ring base/size and mux fields influence hardware writes into memory. Bad values can corrupt profiling buffers or make samples unreadable.
- RLC power and clock fields can affect liveness, power draw, and suspend/resume behavior. Leaving overrides asserted or programming delay/hysteresis fields incorrectly can hide idle state, prevent gating, or destabilize wakeup paths.
- SERDES and SRM windows require busy/FIFO sequencing. Writing command fields without respecting `FIFO_FULL`, `FIFO_EMPTY`, or master busy status can race the firmware/hardware access path.
- Virtualization performance counter fields use VFID and counter IDs. Incorrect programming can attribute data to the wrong virtual function or break PF/VF isolation assumptions.

## Test Signals

Useful validation signals include:

- Build AMDGPU and AMDKFD code paths that include GC 9.1 headers; missing or renamed macros should surface at compile time.
- Compare this generated header against the authoritative GC 9.1 register database and the paired `gc_9_1_offset.h` to catch drift in field masks or register names.
- Exercise performance counter programming on GC 9.1 hardware across CP, GRBM, WD, IA, VGT, PA, SPI, SQ, SX, GDS, TA, TD, TCP, TCC/TCA, CB, DB, RLC, RMI, ATC L2, and MC VM L2 blocks. Look for zero, saturated, or misattributed counters.
- Validate SQ counter filtering with SQC bank/client masks, SIMD masks, shader-stage enables, pipe disables, force enable, and VMID filtering.
- Run SPM collection with ring base/size, segment sizing, global/SE mux selection, sample delays, memory-client attributes, interrupts, and ring read-pointer handling.
- Test RLC bring-up, safe mode, SMU/RLCV mailbox responses, timers, clock counters, GPM thread reset, CP DMA completion flags, and interrupt status under normal boot, suspend/resume, reset, and GPU fault recovery.
- Exercise clock-gating and power-gating paths that touch RLC MGCG, CGCG/CGLS, PG control, per-CU dynamic/static masks, SMU handshakes, and load-balance controls while checking for hangs and power telemetry regressions.
- Validate SERDES and SRM command flows with busy/FIFO polling, read/write data ports, scratch access, and ARAM/DRAM command status.

## Cross-Chunk Notes

The previous chunk is required for the full beginning of the CP performance-counter selector area, including the missing start of `CPG_PERFCOUNTER1_SELECT`. The next chunk is required for the remainder of the `RLC_SRM_INDEX_CNTL_*` family and any later GC 9.1 RLC/SRM definitions. The final per-file research document should merge this chunk with `subset-b-002632` through `subset-b-002644` before summarizing the complete `gc_9_1_sh_mask.h` file.
