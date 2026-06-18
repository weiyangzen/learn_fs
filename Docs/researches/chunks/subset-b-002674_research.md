# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 17356-19701

## Scope

This chunk covers generated shift and mask macros from the AMD GC 9.4.2 register mask header. The range starts with the final mask for `CB_PERFCOUNTER3_SELECT`, then covers complete register bitfield definitions for DB, RLC SPM/perfmon, RLC GPU IOV performance-counter access, RMI performance counters, and the first large portion of the `gc_pwrdec` power/clock-control block. It ends inside the `CGTT_SX_CLK_CTRL4` field list; the rest of that register belongs to the next chunk.

The file is declarative only. It defines C preprocessor constants for hardware register fields and does not contain functions, structs, variables, executable statements, or local storage.

## Purpose

The purpose of this header section is to provide the bit-level ABI used by AMDGPU code when programming GC 9.4.2 MMIO registers. Each field is represented in the generated convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask used to isolate or compose the field.

Driver code combines these macros with AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, and `WREG32_SOC15`. The matching `gc_9_4_2_offset.h` header provides the register addresses, while this file provides the field encodings for those addresses.

## Important Macro Families

### DB, RLC, and RMI Performance Counters

The chunk begins in the performance counter selector area. `DB_PERFCOUNTER0_SELECT` through `DB_PERFCOUNTER3_SELECT` expose the depth-buffer block's event selection and mode fields. Counters 0 and 1 include paired secondary select registers (`DB_PERFCOUNTER0_SELECT1` and `DB_PERFCOUNTER1_SELECT1`) with `PERF_SEL2`, `PERF_SEL3`, `PERF_MODE2`, and `PERF_MODE3`. The regular layout uses 10-bit event selectors, a 4-bit `CNTR_MODE` field where present, and upper-nibble performance mode fields.

`RLC_PERFCOUNTER0_SELECT` and `RLC_PERFCOUNTER1_SELECT` provide the same style of event selector and mode fields for the RLC block. `RLC_PERFMON_CLK_CNTL_UCODE`, `RLC_PERFMON_CLK_CNTL`, and `RLC_PERFMON_CNTL` configure RLC perfmon clock behavior and global perfmon enables/resets, including `PERFMON_STATE`, `PERFMON_ENABLE_MODE`, `PERFMON_ENABLE`, `PERFMON_RESET`, `PERFCOUNTER_RESET`, and `PERFCOUNTER_ENABLE`.

`RMI_PERFCOUNTER0_SELECT` through `RMI_PERFCOUNTER3_SELECT` and `RMI_PERF_COUNTER_CNTL` define event selection for the render memory interface. Counters 0 and 2 have secondary select registers; the control register exposes counter enable, select enable, and counter reset bits.

### RLC Streaming Performance Monitor

The `RLC_SPM_*` section describes RLC-managed streaming performance monitor state. `RLC_SPM_PERFMON_CNTL` contains ring mode and sample interval fields. `RLC_SPM_PERFMON_RING_BASE_LO`, `RLC_SPM_PERFMON_RING_BASE_HI`, and `RLC_SPM_PERFMON_RING_SIZE` describe the output ring buffer location and size. `RLC_SPM_RING_RDPTR` exposes the ring read pointer.

`RLC_SPM_PERFMON_SEGMENT_SIZE`, `RLC_SPM_PERFMON_SEGMENT_SIZE_CORE1`, and `RLC_SPM_SEGMENT_THRESHOLD` divide sampled data into global and shader-engine segments. The line-count fields cover global, SE0, SE1, SE2, and core1 SE3/SE4/SE5 streams, so consumers must account for the multi-SE topology described by GC 9.4.2.

`RLC_SPM_SE_MUXSEL_ADDR/DATA` and `RLC_SPM_GLOBAL_MUXSEL_ADDR/DATA` are indirect selector windows for programming per-shader-engine and global mux selection data. The sample-delay registers cover many GC blocks: CPG, CPC, CPF, CB, DB, PA, GDS, IA, SC, TCC, TCA, TCP, TA, TD, VGT, SPI, SQG, SX, and RMI. Each uses an 8-bit `PERFMON_SAMPLE_DELAY` field plus reserved upper bits. `RLC_SPM_PERFMON_SAMPLE_DELAY_MAX` gives a maximum delay field.

### RLC GPU IOV Performance Counter Window

`RLC_GPU_IOV_PERF_CNT_CNTL`, `RLC_GPU_IOV_PERF_CNT_WR_ADDR`, `RLC_GPU_IOV_PERF_CNT_WR_DATA`, `RLC_GPU_IOV_PERF_CNT_RD_ADDR`, and `RLC_GPU_IOV_PERF_CNT_RD_DATA` define a virtualization-aware indirect access path for performance counter state. The control register contains fields for counter ID, register offset, operation type, reset trigger, read-valid status, read count, instance ID, `GRBM_GFX_INDEX`, and an `UNMAPPED` flag. The address/data registers hold 32-bit write and read payloads.

These fields are part of the PF/VF performance monitoring path rather than ordinary graphics dispatch setup. Correct use depends on RLC/IOV sequencing and privilege context.

### Power Decode and Clock-Gating Controls

The chunk enters `addressBlock: gc_pwrdec` after the RMI performance counter definitions. `CGTS_SM_CTRL_REG` exposes coarse-grain tree shader controls for block ID, register ID, read/write enable, instance index, broadcast, forced clock gating, and forced light sleep. `CGTS_RD_CTRL_REG` and `CGTS_RD_REG` provide a readback path for clock-gating/power-control state.

`CGTS_TCC_DISABLE`, `CGTS_USER_TCC_DISABLE`, `CGTS_TCC_DISABLE2`, and `CGTS_USER_TCC_DISABLE2` define TCC disable masks for the first and extended TCC groups. These fields are topology-sensitive because they can hide cache blocks from the active graphics configuration.

The largest portion of the chunk is the generated per-CU `CGTS_CU*_..._CTRL_REG` set for CU0 through CU15:

- `CGTS_CU*_SP0_CTRL_REG` and `CGTS_CU*_SP1_CTRL_REG` define SP lane groups (`SP00`, `SP01`, `SP10`, `SP11`) and their `OVERRIDE`, `BUSY_OVERRIDE`, `LS_OVERRIDE`, and `SIMDBUSY_OVERRIDE` fields.
- `CGTS_CU*_LDS_SQ_CTRL_REG` defines LDS and SQ gating/light-sleep override fields.
- `CGTS_CU*_TA_SQC_CTRL_REG` defines TA and, for several CUs, SQC gating/light-sleep override fields. Some CU entries expose only TA fields, so consumers cannot assume every repeated register has identical field coverage.
- `CGTS_CU*_TCPI_CTRL_REG` defines TCPI gating/light-sleep override fields plus reserved upper bits for CUs 0 through 15.

The ending portion covers block-level clock-gating timing controls: `CGTT_SPI_PS_CLK_CTRL`, `CGTT_SPIS_CLK_CTRL`, `CGTT_SPI_CLK_CTRL`, `CGTT_PC_CLK_CTRL`, `CGTT_BCI_CLK_CTRL`, `CGTT_PA_CLK_CTRL`, `CGTT_SC_CLK_CTRL0..2`, and `CGTT_SQG_CLK_CTRL`. These use common fields such as `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_STALL_OVERRIDE*`, and `SOFT_OVERRIDE*`, with block-specific `DIV_ID` or reserved fields where applicable.

`SQ_ALU_CLK_CTRL`, `SQ_TEX_CLK_CTRL`, and `SQ_LDS_CLK_CTRL` define `FORCE_CU_ON_SH0` and `FORCE_CU_ON_SH1` masks, allowing shader-array scoped forcing of SQ subunit clocks. `SQ_POWER_THROTTLE` and `SQ_POWER_THROTTLE2` define min/max power, phase offset, max power delta, short-term interval size, long-term interval ratio, and reference-clock selection for SQ power ramp/throttle behavior.

The chunk ends in `CGTT_SX_CLK_CTRL0..4`. It contains complete definitions for controls 0 through 3 and the beginning of control 4. These registers follow the same delay/hysteresis plus soft-stall/soft-override pattern used by other `CGTT_*_CLK_CTRL` registers.

## APIs, Types, and Functions

There are no callable APIs, types, or functions in this chunk. The effective API surface is the generated macro namespace consumed by AMDGPU C code. The important contract is name stability and exact bitfield encoding for GC 9.4.2:

- Register address macros come from the sibling offset header.
- Field shift/mask macros come from this header.
- Default/reset values, when generated, come from the sibling default header.
- Driver code relies on the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` spelling used by AMD's SOC15 register helper macros.

## Control Flow

This header has no runtime control flow. It influences control flow indirectly because compile-time macros determine which bits AMDGPU writes or reads when enabling performance counters, programming RLC SPM, using the RLC GPU IOV perf-counter window, changing TCC/CU availability masks, or enabling/disabling clock and light-sleep controls.

Hardware-side sequencing is not encoded here. For example, RLC SPM ring and muxsel programming requires owning code to set base/size/segment fields, program selector windows, manage sample intervals and delays, and read ring pointers in a valid order. Similarly, `RLC_GPU_IOV_PERF_CNT_CNTL` read-valid and reset fields require the surrounding IOV code to perform proper polling and timeout handling.

## State and Persistence Behavior

The header itself persists no state. The fields describe persistent or latched state inside GC 9.4.2 hardware until reset, firmware reinitialization, suspend/resume restoration, or explicit driver writes.

Important hardware state represented by this chunk includes DB/RLC/RMI performance event selection, RLC perfmon enables/resets, SPM ring buffer addresses and size, SPM segment sizes and thresholds, per-block SPM sample delays, SPM mux selector RAM access, RLC GPU IOV performance-counter indirect access state, TCC disable masks, per-CU power-gating/light-sleep overrides, shader-array force-on masks, SQ power throttle parameters, and block-level CGTT delay/hysteresis/override state.

Some fields are configuration bits, some are command/reset triggers, and some are readback/status bits. Examples include `PERFMON_RESET`, `PERFCOUNTER_RESET`, `PERF_CNT_RESET`, and `PERF_CNT_READ_VALID`. Treating trigger or status fields as ordinary persistent configuration can leave counters stale, cause incomplete reads, or desynchronize performance monitor setup.

## Dependencies and Integration Points

This chunk depends on generated AMD register-header conventions and is meaningful only with the matching GC 9.4.2 register-address header. It is typically included through AMDGPU GFX 9.4.x code paths that configure graphics, compute, power, and profiling behavior.

Important integration points in the source tree include:

- GFX 9.4.x AMDGPU initialization and reset code, which includes GC register headers and programs RLC, clock-gating, and golden-register state.
- Performance/profiling paths that configure DB, RLC, RMI, and SPM event selection, sample timing, ring buffers, and mux selection.
- SR-IOV or partition-aware paths that use `RLC_GPU_IOV_PERF_CNT_*` fields to access virtualized performance counter state.
- Power-management and clock-gating code that coordinates `CGTS_*`, `CGTT_*`, SQ force-on, and SQ throttle fields with SMU/RLC firmware policy.
- Topology/harvest handling that must keep `CGTS_TCC_DISABLE*` and `CGTS_USER_TCC_DISABLE*` values consistent with actual cache availability.

Cross-generation similarity is high, but these masks should not be reused across other GC versions. Similar register names in GC 9.4.3, GC 10, or GC 11 headers can differ in reserved fields, instance counts, or field widths.

## Risks

- Bitfield drift is high impact. An incorrect shift or mask can write unrelated MMIO fields and cause hangs, bad performance data, broken power gating, or invalid topology exposure.
- The repeated per-CU `CGTS_CU*` families are mechanically similar but not perfectly identical. Some `TA_SQC` registers omit SQC fields, and generated consumers must not assume all CU registers have the same subfields.
- SPM fields combine memory-backed ring configuration, selector-window programming, sample timing, and read pointers. Missing sequencing, alignment, or polling rules can corrupt samples or stall profiling flows.
- `RLC_GPU_IOV_PERF_CNT_*` fields are privilege- and virtualization-sensitive. Incorrect instance, `GRBM_GFX_INDEX`, operation type, or reset/read-valid handling can return stale data or cross the wrong VF/PF context.
- TCC disable and user-disable masks are topology-sensitive. Wrong values can expose disabled cache slices or hide valid ones.
- Clock-gating and light-sleep overrides affect power, performance, and stability. Forcing clocks on/off or overriding busy/light-sleep signals without SMU/RLC coordination can cause power regressions or hardware hangs.
- SQ power throttle fields are validated by field widths in some power-management code. Values outside the encoded ranges can silently truncate if consumers fail to range-check before shifting.
- This chunk starts after the `CB_PERFCOUNTER3_SELECT` family has begun and ends inside `CGTT_SX_CLK_CTRL4`, so adjacent chunks must be consulted for complete family-level documentation.

## Test and Validation Signals

Useful validation is mostly build-time and hardware-integration based:

- Build AMDGPU with GC 9.4.2 support enabled to catch missing, renamed, or conflicting macros.
- Exercise GFX 9.4.x initialization, reset, suspend/resume, and clock-gating toggles to verify `CGTS_*`, `CGTT_*`, SQ force-on, and SQ throttle fields remain consistent with firmware policy.
- Run performance counter tests for DB, RLC, and RMI event selection, including counters with secondary select registers and counters with only primary selection fields.
- Validate RLC SPM setup by checking ring base/size programming, segment size and threshold programming, per-block sample delays, mux selector writes, read pointer updates, and sample data integrity.
- Test SR-IOV/per-partition profiling flows that use `RLC_GPU_IOV_PERF_CNT_*`, especially reset, read-valid polling, instance selection, and `GRBM_GFX_INDEX` handling.
- Validate topology-sensitive TCC disable masks on harvested and fully enabled parts.
- Use power and stability tests to catch regressions from clock-gating overrides: idle power, load power, resume from low-power states, heavy graphics/compute load, and reset recovery.

## Unresolved Cross-Chunk References

The first line is the final `CB_PERFCOUNTER3_SELECT__PERF_MODE_MASK` definition, so the complete CB counter selector family is in the previous chunk. The final lines begin `CGTT_SX_CLK_CTRL4` but do not include its complete mask list; the following chunk must provide the rest of that register and subsequent power-control definitions.
