# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 17778-20327

## Scope

This chunk covers generated shift and mask macros from the AMD GC 12.0.0 register bitfield header. It begins at the field definitions for `GE2_DIST_PERFCOUNTER3_HI` without that register's leading comment, then covers complete blocks for CP/GC performance counter selection, RLC SPM and accumulator control, GDFLL/GRTAVFS/RTAVFS indirect power-management windows, RLC hypervisor-visible status and memory windows, GL2/channel pipe steering, CP hypervisor microcode and instruction-cache address fields, GRBM hypervisor selection/data windows, and much of the RLC core control/power/clock/doorbell section. It ends in the middle of `RLC_GPM_LEGACY_INT_DISABLE`, after the `STORE_LOAD_TIMER3_EXPIRED_T0` field and before any later fields in that same register.

The file is a generated hardware interface header. This chunk defines preprocessor constants only: it contains no C functions, structs, variables, persistent storage, runtime branches, or executable control flow.

## Purpose

The purpose of this range is to supply the bit-level ABI used by AMDGPU code when reading and writing GC 12.0.0 graphics, command-processor, RLC, performance-monitor, power-management, and virtualization registers. Each register field normally appears as a pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for composing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask for isolating that field.

The sibling offset header for this ASIC generation provides register addresses. This `*_sh_mask.h` file provides the field layout used by helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, `WREG32_SOC15`, and firmware/hardware programming paths that compose register values directly.

## Important Macro Families

### Performance Counter Values and Selection

The chunk starts with low/high 32-bit performance counter value fields for `GC_EA_CPWD`, `GC_EA_SE`, `GL2C`, `GL2A`, `CHC`, `RLC`, `GCR`, and `CHA`. These registers expose the lower and upper halves of hardware counters through full-width `PERFCOUNTER_LO` and `PERFCOUNTER_HI` masks.

The following `gc_gfx_cpwd_cpwd_perfsdec` address block defines selector registers used to choose events and counter modes for many GC blocks:

- CP front-end blocks: `CPG_PERFCOUNTER*`, `CPC_PERFCOUNTER*`, and `CPF_PERFCOUNTER*`.
- Command-processor global control: `CP_CP_PERFMON_CNTL`.
- TC performance windows and latency statistic selectors: `CPF_TC_PERF_COUNTER_WINDOW_SELECT`, `CPG_TC_PERF_COUNTER_WINDOW_SELECT`, `CPC_TC_PERF_COUNTER_WINDOW_SELECT`, and `*_LATENCY_STATS_SELECT`.
- Draw-window/object counters: `CP_DRAW_OBJECT`, `CP_DRAW_OBJECT_COUNTER`, `CP_DRAW_WINDOW_*`, and `CP_DRAW_WINDOW_CNTL`.
- GRBM, geometry, cache, channel, RLC, GCR, and CHA performance selectors: `GRBM_PERFCOUNTER*`, `GE1_PERFCOUNTER*`, `GE2_DIST_PERFCOUNTER*`, `GC_EA_*`, `GL2C_*`, `GL2A_*`, `CHC_*`, `RLC_PERFCOUNTER*`, `GCR_*`, and `CHA_*`.

The selector pattern is regular. `*_SELECT` registers usually pack `PERF_SEL` and `PERF_SEL1` 10-bit event selectors plus `CNTR_MODE`/`PERF_MODE` fields in the high bits. `*_SELECT1` registers usually pack `PERF_SEL2`, `PERF_SEL3`, and mode fields for additional events. Single-counter forms expose only `PERF_SEL` plus a high-bit mode field. These macros are consumed by profiling, debugfs, perf, and internal diagnostic paths that program hardware counters.

### CP Performance Monitor Control and Draw Windows

`CP_CP_PERFMON_CNTL` exposes state fields for CP performance collection, SPM performance state, enable mode, sample enable, and start/end offset fields. This is a control register rather than a passive counter register, so incorrect field packing can leave the CP performance monitor stopped, permanently sampling, or sampling the wrong interval.

The draw-window/object macros define object identity, object counter, upper/lower draw-window bounds, and draw-window control fields such as included/excluded draw ranges and clock-enable behavior. They are integration points for command-processor performance capture that needs to filter by draw scope rather than count across all submitted work.

### RLC Streaming Performance Monitor and Accumulator

The `RLC_SPM_*` section is the densest stateful block in this chunk. It describes the RLC-owned streaming performance monitor path and its accumulator:

- `RLC_SPM_PERFMON_CNTL` selects ring mode, sample interval start/type, and sample interval.
- `RLC_SPM_PERFMON_RING_BASE_LO/HI`, `RLC_SPM_PERFMON_RING_SIZE`, `RLC_SPM_RING_WRPTR`, and `RLC_SPM_RING_RDPTR` define the sample ring buffer and producer/consumer pointers.
- `RLC_SPM_SEGMENT_THRESHOLD` and `RLC_SPM_PERFMON_SEGMENT_SIZE` define segment thresholds and split global versus shader-engine sample segments.
- `RLC_SPM_GLOBAL_MUXSEL_*` and `RLC_SPM_SE_MUXSEL_*` provide indirect address/data ports for selecting global and per-SE sampled signals.
- `RLC_SPM_ACCUM_DATARAM_*`, `RLC_SPM_ACCUM_SWA_DATARAM_*`, and `RLC_SPM_ACCUM_CTRLRAM_*` expose accumulator data/control RAM windows.
- `RLC_SPM_ACCUM_STATUS`, `RLC_SPM_ACCUM_CTRL`, and `RLC_SPM_ACCUM_MODE` expose the accumulator lifecycle, including done, overflow, armed, FIFO-empty, idle, pending rearm, abort, start, reset, rearm, 32-bit mode, accumulation mode, shader-array/engine selection, and SWA accumulation mode fields.
- Threshold/sample-count/write-count registers define how many samples are requested and how accumulator memory is interpreted.
- `RLC_SPM_PAUSE`, `RLC_SPM_STATUS`, `RLC_SPM_GFXCLOCK_LOWCOUNT`, `RLC_SPM_GFXCLOCK_HIGHCOUNT`, `RLC_SPM_GTS_TRIGGER_VALUE_*`, and `RLC_SPM_MODE` support pause control, status polling, clock/sample timing, global timestamp triggers, and mode selection.

Several fields in this family are command strobes, not durable settings. For example, start/reset/rearm/sample-wire fields in `RLC_SPM_ACCUM_CTRL` should be treated as hardware actions, while `RLC_SPM_ACCUM_STATUS` and `RLC_SPM_STATUS` should be polled or sampled to verify completion, overflow, idle, abort, and sample-count state.

### RSPM Request/Response Ports

`RLC_SPM_RSPM_REQ_DATA`, `RLC_SPM_RSPM_REQ_OP`, `RLC_SPM_RSPM_RET_DATA`, `RLC_SPM_RSPM_RET_OP`, and the matching `RLC_SPM_SE_RSPM_*` registers define request and response windows for RSPM access. `RLC_SPM_RSPM_CMD` and `RLC_SPM_RSPM_CMD_ACK` expose command and acknowledgement bits. These are indirect hardware ports; callers must respect request/ack sequencing and should not treat the data registers as ordinary persistent storage.

### Dynamic Frequency, Voltage, and RTAVFS Access

The chunk includes small address blocks for graphics dynamic frequency/voltage support:

- `GDFLL_EDC_HYSTERESIS_CNTL` and `GDFLL_EDC_HYSTERESIS_STAT` define EDC hysteresis configuration and observed status.
- `XVMIN_XVMIN_WR_DATA` provides a write-data field for XVMIN programming.
- `GRTAVFS_RTAVFS_REG_ADDR`, `GRTAVFS_RTAVFS_WR_DATA`, `GRTAVFS_RTAVFS_RD_DATA`, `GRTAVFS_RTAVFS_REG_CTRL`, and `GRTAVFS_RTAVFS_REG_STATUS` define an indirect RTAVFS register access window with read/write enables and acknowledgement/data-valid status.
- `GRTAVFS_TARG_FREQ` and `GRTAVFS_TARG_VOLT` carry requested target frequency and voltage plus request/valid bits.
- `GRTAVFS_SOFT_RESET`, `GRTAVFS_PSM_CNTL`, `GRTAVFS_CLK_CNTL`, and `GFX_ICG_GRTAVFS_CTRL` define reset override, PSM sampling/count configuration, clock mux override, and dynamic clock-gating override.
- A separate `gc_gfx_cpwd_grtavfs_rtavfs_rtavfs_rtavfs_reg_blk` block exposes direct `RTAVFS_RTAVFS_REG_ADDR` and `RTAVFS_RTAVFS_WR_DATA` field definitions.

These macros integrate with power-management and firmware-mediated flows. Wrong field composition can request incorrect voltage/frequency targets, break an indirect access sequence, or force clock selection/clock gating in a way that affects the entire graphics block.

### RLC Hypervisor Status, Microcode, and Memory Windows

The `gc_gfx_cpwd_cpwd_hypdec` block exposes RLC-side status and privileged access fields:

- `RLC_SDMA0_STATUS` through `RLC_SDMA3_STATUS` and matching busy-status registers provide full-width status snapshots for SDMA engines.
- `RLC_HYP_SEMAPHORE_0..3` provide small `CLIENT_ID` fields for privileged synchronization.
- `RLC_BUSY_CLK_CNTL` and `RLC_CLK_CNTL` define RLC busy-off latency, GRBM busy-off latency, and many clock-gating override bits for RLC subblocks such as SRM, IMU, SPM, GPM, common logic, TC, register access, SRAM, LX6 core, UTCL2, IH gasket, and bridge.
- `RLC_IH_COOKIE` and `RLC_IH_COOKIE_CNTL` expose interrupt-cookie data, credit, and reset-counter control.
- `RLC_HYP_RLCG_UCODE_CHKSUM` exposes the RLCG microcode checksum.
- `RLC_GPM_UCODE_ADDR/DATA`, `RLC_GPM_IRAM_ADDR/DATA`, `RLC_LX6_DRAM_ADDR/DATA`, `RLC_LX6_IRAM_ADDR/DATA`, `RLC_GPM_SCRATCH_ADDR/DATA`, `RLC_SRM_DRAM_ADDR/DATA`, and `RLC_SRM_ARAM_ADDR/DATA` expose indirect address/data windows into microcode, instruction RAM, data RAM, scratch, and SRM memory.
- `RLC_GTS_OFFSET_*` and `RLC_GTS_OFFSET_SNAP_*` provide global timestamp offset and snapshot fields.

The address/data pairs are stateful indirect ports. Driver or firmware code normally writes an address register and then reads/writes the matching data register. Races, missing barriers, or wrong address masks can corrupt firmware-visible state.

### Pipe Steering and User Disable Masks

`GL2_PIPE_STEER_0..3` map graphics pipes 0-7 to GL2 channels across queue groups. Each pipe mapping uses a 3-bit channel field, with separate registers for pipes 0-3 and 4-7 and queue groups Q0-Q3. `CH_PIPE_STEER` maps pipes 0-3 with 2-bit fields and a mode bit.

`GC_USER_FULL_SA_UNIT_DISABLE`, `GRBM_GC_USER_SA_UNIT_DISABLE`, `GC_USER_GL2C_DISABLE_0`, and `GC_USER_GL2C_DISABLE_1` expose user-visible shader-array and GL2C disable masks. These fields are tied to harvesting, fusing, partitioning, or repair state. Programming them incorrectly can expose disabled hardware, hide working units, or misroute cache traffic.

### CP Hypervisor Microcode and Instruction/Data Cache Fields

The `gc_gfx_cpwd_cpwd_cphypdec` block describes command-processor privileged windows:

- Context-range registers: `CP_HYP_CONTEXT_RANGE_BASE` and `CP_HYP_CONTEXT_RANGE_END`.
- PFP, ME, and MEC microcode address/data ports: `CP_HYP_PFP_UCODE_ADDR/DATA`, `CP_PFP_UCODE_ADDR/DATA`, `CP_HYP_ME_UCODE_ADDR/DATA`, `CP_ME_RAM_RADDR`, `CP_ME_RAM_WADDR`, `CP_ME_RAM_DATA`, `CP_HYP_MEC1_UCODE_ADDR/DATA`, and `CP_MEC_ME1_UCODE_ADDR/DATA`. Address registers include a high `PIPE_SEL` bit where applicable.
- Microcode checksum registers: `CP_HYP_PFP_UCODE_CHKSUM`, `CP_HYP_ME_UCODE_CHKSUM`, and `CP_HYP_MEC_ME1_UCODE_CHKSUM`.
- Instruction-cache base/control/operation fields for PFP, ME, CPC, and MES: base low/high, VMID, execute-disable, cache policy, per-pipe/scope/temporal fields where present, invalidate-cache, invalidate-complete, prime-start-PC, prime-cache, and primed status.
- MES data-cache base and bound fields: `CP_MES_DC_BASE_*`, `CP_MES_MDBASE_*`, `CP_MES_MIBOUND_*`, and `CP_MES_MDBOUND_*`.
- Version and RS64 memory-bound fields: `CP_HYP_PFP_UCODE_VERS`, `CP_HYP_ME_UCODE_VERS`, `CP_GFX_RS64_DC_BASE*`, `CP_GFX_RS64_MIBOUND_*`, and MEC data/cache bound fields.

These macros support firmware loading, privileged CP setup, cache invalidation/priming, and MES/MEC/GFX RS64 memory aperture programming. The cache operation bits include both command and completion fields, so tests should verify that code waits for completion rather than only issuing the command bit.

### GRBM Hypervisor Selection and Remap

The `gc_gfx_cpwd_cpwd_grbm_hypdec` block defines indirect GRBM selection/data fields:

- `GRBM_GFX_INDEX_SR_SELECT` and `GRBM_GFX_INDEX_SR_DATA` select and expose instance, shader array, shader engine, WGP, broadcast, and VF/PF state.
- `GRBM_GFX_CNTL_SR_SELECT` and `GRBM_GFX_CNTL_SR_DATA` select and expose GRBM graphics-control state.
- `GC_IH_COOKIE_0_PTR` provides an interrupt-cookie pointer field.
- `GRBM_SE_REMAP_CNTL` and `GRBM_GRBM_SA_REMAP_CNTL` define shader-engine and shader-array remap fields.

These are virtualization and topology integration points. Selection register writes affect what subsequent data-register accesses mean, so callers must serialize access to the indirect pair.

### RLC Core Control, Interrupts, Timers, Clocks, Doorbells, and Power

The `gc_gfx_cpwd_cpwd_rlcdec` block in this chunk covers RLC core state:

- `RLC_CNTL`, `RLC_F32_UCODE_VERSION`, `RLC_STAT`, `RLC_ACTIVE_MASK`, `RLC_GFX_SE_STATUS`, and reference-clock timestamp registers define basic RLC enablement, version, busy/idle/interrupt state, activity masks, shader-engine status, and timestamp counters.
- `RLC_GPM_TIMER_INT_0..4`, `RLC_GPM_TIMER_CTRL`, and `RLC_GPM_TIMER_STAT` define GPM timer values, modes, enable/clear flags, and timer status.
- `RLC_GPM_LEGACY_INT_STAT`, `RLC_GPM_LEGACY_INT_CLEAR`, `RLC_INT_STAT`, and the start of `RLC_GPM_LEGACY_INT_DISABLE` define legacy interrupt status/clear/disable fields for SPP PVT changes, EOF, PG control, and store/load timer events visible in this range.
- `RLC_MGCG_CTRL`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, and `RLC_CGCG_RAMP_CTRL` define medium-grain/clock-gating, clock-throttling, light sleep, controller, sleep-mode, ramp, delay, and override fields.
- `RLC_JUMP_TABLE_RESTORE`, `RLC_PG_DELAY_2`, `RLC_PG_DELAY`, `RLC_PG_DELAY_3`, `RLC_PG_CNTL`, `RLC_DYN_PG_STATUS`, `RLC_DYN_PG_REQUEST`, `RLC_PG_ALWAYS_ON_WGP_MASK`, `RLC_MAX_PG_WGP`, `RLC_AUTO_PG_CTRL`, and `RLC_STATIC_PG_STATUS` define RLC-controlled power-gating behavior, delay values, dynamic/static WGP power status/request masks, always-on WGPs, max powered-up WGP limits, and automatic power-gating thresholds.
- `RLC_GPU_CLOCK_COUNT_*`, `RLC_CAPTURE_GPU_CLOCK_COUNT`, `RLC_CLK_COUNT_*`, `RLC_CLK_COUNT_CTRL`, `RLC_CLK_COUNT_STAT`, `RLC_GPU_CLOCK_32_RES_SEL`, and `RLC_GPU_CLOCK_32` define clock capture, counter selection, busy/done state, and 32-bit clock outputs.
- `RLC_UCODE_CNTL`, `RLC_GPM_THREAD_RESET`, `RLC_GPM_CP_DMA_COMPLETE_T0/T1`, `RLC_GPM_THREAD_INVALIDATE_CACHE`, `RLC_GPM_THREAD_PRIORITY`, `RLC_GPM_THREAD_ENABLE`, and `RLC_GPM_INT_DISABLE_TH0` control RLC/GPM firmware execution, thread reset, DMA completion, cache invalidation, priority, enablement, and interrupt masking.
- `RLC_RLCG_DOORBELL_CNTL`, `RLC_RLCG_DOORBELL_STAT`, `RLC_RLCG_DOORBELL_0..3_DATA_LO/HI`, and `RLC_RLCG_DOORBELL_RANGE` define RLCG doorbell control, status, per-doorbell payload data, and lower/upper address range fields.
- `RLC_SERDES_RD_INDEX`, `RLC_SERDES_RD_DATA_0..3`, `RLC_SERDES_MASK`, `RLC_SERDES_CTRL`, `RLC_SERDES_DATA`, and `RLC_SERDES_BUSY` define serial-deserializer read selection, masks, command/address/data fields, busy state, read FIFO state, and pending-read status.
- `RLC_GPM_GENERAL_0..7`, `RLC_GPM_GENERAL_16`, `RLC_GPR_REG1`, and `RLC_GPR_REG2` provide full-width firmware/general-purpose fields.

Many of these macros represent live hardware control rather than static description. Interrupt clear fields may be write-one-to-clear, doorbell fields can trigger firmware work, power-gating fields can change active WGP state, and clock-gating overrides can affect power and hang behavior.

## Dependencies and Integration Points

This header depends on C preprocessor inclusion and on the matching GC 12.0.0 register offset definitions. It does not include other files itself in this range, but AMDGPU source typically uses these macros together with ASIC-specific offset headers and register helper macros from the AMD GPU driver stack.

The main integration surfaces are:

- AMDGPU graphics IP initialization and teardown code that programs RLC, CP, GRBM, and topology registers.
- Firmware loading and verification paths for CP PFP/ME/MEC, RLC GPM, LX6, SRM, and related microcode memory windows.
- Performance monitoring and profiling paths that configure CP, GRBM, GE, GL2, CHC, RLC, GCR, CHA, GC_EA, RLC SPM, and accumulator counters.
- Power-management paths that coordinate GDFLL, RTAVFS/GRTAVFS, clock gating, clock counting, dynamic power gating, and WGP masks.
- Virtualization/SR-IOV or hypervisor paths that use RLC hypervisor semaphores, SDMA busy/status registers, GRBM VF/PF selection, CP hypervisor context ranges, and privileged microcode/cache windows.

## State and Persistence Behavior

The macros themselves have no runtime state. The hardware registers they describe are stateful and often persistent across parts of a GPU reset domain until firmware, driver initialization, or a hardware reset rewrites them.

Important stateful patterns in this chunk include:

- Indirect address/data windows: CP microcode, RLC GPM/IRAM/LX6/SRM memory, RTAVFS, GRBM selection/data, RSPM request/response, SPM muxsel, accumulator RAM, and SERDES access all depend on a prior address/select/command register write.
- Producer/consumer state: SPM ring base/size/wrptr/rdptr and segment configuration persist during a capture session.
- Command and acknowledgement fields: RTAVFS read/write enables and acks, SPM/RSPM command/ack fields, cache invalidate/prime commands and completion bits, clock-count clear/start/done bits, and SERDES busy/pending fields require sequencing.
- Global hardware policy state: clock-gating overrides, power-gating masks/delays, WGP masks, GL2/CH pipe steering, and voltage/frequency target fields can affect all users of the graphics block.

## Risks

- Generated-header drift: masks and shifts must match the GC 12.0.0 hardware specification. A single wrong mask in this header can silently corrupt register programming across many call sites.
- Partial-register chunk boundary: this chunk begins after the `GE2_DIST_PERFCOUNTER3_HI` comment and ends before all `RLC_GPM_LEGACY_INT_DISABLE` fields are visible. The merge lane should reconcile adjacent chunks before making whole-register conclusions for those two boundary registers.
- Indirect-port races: address/data pairs and select/data pairs require serialization. Concurrent users of GRBM, RLC memory windows, RTAVFS, SPM muxsel, RSPM, or SERDES registers can read or write the wrong target.
- Write-one or strobe semantics: status clear, start, reset, invalidate, prime, clock-count, timer clear, doorbell, and command bits should not be modified through naive read-modify-write unless the hardware semantics are verified.
- Privilege and reset-domain sensitivity: CP/RLC microcode, hypervisor, clock/power, and virtualization fields may only be valid in PF/privileged contexts or during tightly ordered firmware initialization.
- Topology/harvest sensitivity: pipe steering and disable masks can misrepresent available hardware if programmed without fuse/harvest awareness.

## Test Signals

Useful validation signals for code that consumes this chunk include:

- Compile coverage for all GC 12.0.0 AMDGPU objects that include this header and use these field names.
- Static checks that every `_MASK`/`__SHIFT` pair composes and extracts expected values with `REG_SET_FIELD`/`REG_GET_FIELD`, especially high-bit fields such as `PIPE_SEL`, mode fields, clock-gating overrides, and cache-control bits.
- Hardware or emulator tests that program performance counters, verify nonzero low/high counter reads, and confirm selector/mode fields route expected events.
- RLC SPM tests that allocate a ring, configure mux selections, start sampling/accumulation, observe write-pointer movement, and poll done/overflow/idle status.
- Firmware-loading tests that write CP/RLC address/data windows, verify checksum/version registers, and wait for instruction-cache invalidate/prime completion bits.
- Power-management tests that exercise RTAVFS/GRTAVFS indirect read/write acknowledgement, target frequency/voltage request/valid bits, and clock-count status without leaving override bits asserted.
- Virtualization or privileged-mode tests that verify GRBM VF/PF selection, RLC semaphores, SDMA busy/status snapshots, and CP hypervisor context-range behavior.
- Reset/resume tests that confirm RLC clock/power/doorbell/timer/interrupt fields are restored in the expected order after GPU reset, suspend/resume, or mode changes.
