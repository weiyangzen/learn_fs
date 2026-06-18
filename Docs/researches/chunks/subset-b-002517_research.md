# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 32602-35135

## Purpose

This chunk is a generated AMD GC 11.0.0 register field mask header segment. It defines `__SHIFT` and `_MASK` constants for bitfields in Graphics Core registers so C driver code can construct, read, and modify register values without hard-coded bit positions. The lines in this chunk contain 2,138 `#define`s under 386 register/comment headings and span several hardware areas: graphics cache/color/depth/performance counters, RLC streaming performance monitor and accumulation controls, GRTAVFS/RTAVFS voltage-frequency interface registers, CP microcode/cache base registers, and a large RLC control/power-management/profiling section.

The file itself has no executable code. Its purpose is ABI-like register metadata for ASIC-specific driver paths that include `gc/gc_11_0_0_sh_mask.h` and pair these field definitions with address definitions from `gc_11_0_0_offset.h`.

## Important APIs, Types, and Macros

There are no functions or C types in this chunk. The exported interface is the macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: right-shift amount for a field.
- `<REGISTER>__<FIELD>_MASK`: field mask in the 32-bit register value.

Major macro groups in this chunk:

- Performance counter select fields for `GL2C`, `GL2A`, `GL1C`, `GL1A`, `GL1H`, `CHC`, `CHCG`, `CHA`, `CB`, `DB`, `RMI`, `GCR`, `PA_PH`, `UTCL1`, and `GUS`. These mostly expose `PERF_SEL`, `PERF_SEL1`, `PERF_SEL2`, `PERF_SEL3`, `CNTR_MODE`, `COUNTER_MODE`, and `PERF_MODE*` fields. `CB_PERFCOUNTER_FILTER` adds operation, format, clear, MRT, sample-count, and fragment-count filter selectors.
- RLC SPM/perfmon macros such as `RLC_SPM_PERFMON_CNTL`, `RLC_SPM_PERFMON_RING_BASE_LO/HI`, `RLC_SPM_RING_WRPTR/RDPTR`, `RLC_SPM_PERFMON_SEGMENT_SIZE`, mux select registers, accumulation dataram/ctrlram accessors, `RLC_SPM_ACCUM_STATUS`, `RLC_SPM_ACCUM_CTRL`, `RLC_SPM_ACCUM_MODE`, request/return RSPM registers, `RLC_SPM_RSPM_CMD`, and `RLC_SPM_RSPM_CMD_ACK`.
- RLC general perf and IOV counters: `RLC_PERFMON_CNTL`, `RLC_PERFCOUNTER0/1_SELECT`, and `RLC_GPU_IOV_PERF_CNT_*` address/data/control fields.
- GRTAVFS/RTAVFS fields in `gc_grtavfs_grtavfs_dec`, `gc_grtavfs_se_grtavfs_dec`, and `gc_grtavfsdec`, including target frequency, target voltage, request/valid bits, soft reset, PSM count/sample enable, register address/data, and clock select controls.
- CP hypervisor and firmware-facing fields in `gc_cphypdec`, including PFP/ME/MEC microcode address/data registers, ME RAM address/data registers, CP instruction-cache base/control/op registers, MES instruction/data base and bounds, RS64 data cache bases, and MEC data/instruction bounds. The `CP_*_IC_BASE_CNTL` fields expose VMID, address clamp, execute-disable, and cache policy settings.
- RLC control and state macros from `gc_rlcdec`, including `RLC_CNTL`, firmware version, busy status, refclock/GPU clock captures, GPM timers and interrupt status/clear/disable/force controls, GPM thread reset/priority/enable/cache-invalidate fields, RLCG/RLCV doorbell range/control/status/data registers, clock gating/power gating controls, serdes masks/status/control/data, SRM indexed command/data windows, UTCL1 controls/status/error capture, semaphores, PACE timer/interrupt controls, CP stat invalidation, and shader profiling controls such as `RLC_SPP_CTRL`, `RLC_SPP_SHADER_PROFILE_EN`, and `RLC_SPP_SSF_CAPTURE_EN`.

## Control Flow

This header contributes no direct control flow. Runtime control flow occurs in consumers that:

1. Include this header and the matching offset header.
2. Read a 32-bit MMIO register with helpers such as `RREG32_SOC15`.
3. Compose or extract fields via driver macros such as `REG_SET_FIELD` and `REG_GET_FIELD`, which depend on this file's `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` symbols.
4. Write the resulting value back with helpers such as `WREG32_SOC15`.

The chunk's register groups imply several hardware workflows:

- Performance monitoring selects a block counter source with `*_PERFCOUNTER*_SELECT*`, optional filters, modes, and RLC SPM mux/accumulation routing before sampling into rings or counters.
- RLC SPM setup programs ring base/size, mux selection, accumulation mode, thresholds, and sample counts, then observes status bits such as done, overflow, FIFO empty, and sequence-in-progress.
- CP microcode/cache setup writes microcode address/data or instruction-cache base/control fields and uses invalidate/prime operation bits to manage CP instruction caches.
- RLC power and clock management programs timers, clock count capture, power-gating enables/delays, auto power gating, clock-gating overrides, serdes commands, and doorbell handling.
- UTCL1 error/status flows expose busy, retry/fault/PRT detection, VMID, and address capture fields that consumers can poll or log during GPU memory translation faults.

## State and Persistence Behavior

The macros are compile-time constants and do not store state themselves. The state described by this chunk lives in GPU registers and firmware-accessible hardware blocks:

- Performance counter and SPM registers persist only as hardware register configuration until reset, suspend/resume reinitialization, ASIC reset, or driver reprogramming.
- Ring base, size, read/write pointer, mux select, and accumulation fields define where sampled performance data is written and how samples are segmented. Incorrect values can persist long enough to corrupt profiling output or cause invalid memory accesses by the hardware perf monitor path.
- CP microcode address/data and instruction-cache base/control registers affect firmware instruction memory/cache behavior. These are normally initialized by gfx/CP startup and resume flows.
- RLC power-management, timer, doorbell, and clock-gating fields persist as hardware control state and directly affect runtime power behavior, interrupt pacing, and RLC firmware communication.
- Status registers such as `RLC_STAT`, `RLC_GPM_TIMER_STAT`, `RLC_SPM_STATUS`, `RLC_UTCL1_STATUS`, `RLC_RLCG_DOORBELL_STAT`, and `RLC_RLCV_DOORBELL_STAT` expose volatile hardware state. Clear bits in interrupt/timer controls usually have side effects when written by consumers.

## Dependencies and Integration Points

This chunk is tightly coupled to:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h`, which provides the matching `reg...` register addresses and base indexes.
- AMDGPU register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`.
- GC 11 driver files that include this header, including `amdgpu/gfx_v11_0.c`, `amdgpu/amdgpu_amdkfd_gfx_v11.c`, `amdgpu/mes_v11_0.c`, `amdgpu/imu_v11_0.c`, `amdgpu/soc21.c`, `amdkfd/kfd_device_queue_manager_v11.c`, and `amdkfd/kfd_mqd_manager_v11.c`.
- CP firmware and MES setup paths. For example, gfx code sets `CP_PFP_IC_BASE_CNTL` fields such as `VMID`, `CACHE_POLICY`, `EXE_DISABLE`, and `ADDRESS_CLAMP` while configuring instruction-cache base behavior.
- Profiling/performance tooling paths that depend on the SPM, block performance counter, and shader profiling field layouts.
- Power management and clock-gating paths, especially RLC power-gating, CGCG/CGLS, serdes, SMU clock request, and PACE timer/interrupt controls.

## Risks and Edge Cases

- Generated header drift is the primary risk. If masks or shifts do not match the GC 11.0.0 hardware spec or the paired offset header, every consumer using `REG_SET_FIELD` can silently program the wrong bits.
- Similar register names across ASIC generations make accidental cross-generation reuse dangerous. Several fields are close to older GC/GFX versions but not identical; for example, shader profile fields in GC 11 have a reserved bit where older generations had VS-specific naming.
- Some paired select registers use non-obvious mode ordering. `CB_PERFCOUNTER0_SELECT1`, `DB_PERFCOUNTER*_SELECT1`, `RMI_PERFCOUNTER*_SELECT1`, and `PA_PH_PERFCOUNTER*_SELECT1` place `PERF_MODE3` at bits 27:24 and `PERF_MODE2` at bits 31:28, while other blocks may name mode fields in ascending order. Consumers should use field macros instead of assuming layout by suffix.
- Reserved masks are large in many RLC power/clock registers. Read/modify/write paths must preserve reserved bits unless the programming guide explicitly requires zeroing them.
- CP microcode and instruction-cache control fields are high impact. Incorrect `VMID`, base, bounds, `EXE_DISABLE`, cache policy, or invalidate/prime usage can break command processor firmware execution.
- RLC SPM ring base/size and accumulation controls can affect DMA-like hardware writes and profiling collection. Bad base/size, segment, or mux settings can produce bogus profiling data or hardware faults.
- Doorbell range/control fields for RLCG/RLCV must match queue/doorbell allocation policy; enabling an incorrect doorbell ID or range risks lost or misrouted firmware notifications.
- UTCL1 status/error fields combine fault type, VMID, and address fragments. Diagnostics must combine `_ERROR_1` and `_ERROR_2` correctly and account for volatile status.
- Interrupt clear/force/disable registers can have write-side effects. Tests and debug code should not treat every field as ordinary persistent configuration.

## Test Signals

Useful verification signals for this chunk are mostly build-time, register-programming, and hardware-observation based:

- Full AMDGPU build coverage for files including `gc_11_0_0_sh_mask.h`; missing or renamed macros should fail compilation in GC 11 paths.
- Static checks that every `REG_SET_FIELD(x, REGISTER, FIELD, value)` reference has matching `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` definitions in the selected ASIC header.
- Cross-check generated masks against `gc_11_0_0_offset.h` register coverage and against adjacent generated headers (`gc_11_0_0_default.h`, newer GC 11.x headers) for expected deltas.
- Runtime smoke tests for gfx init/resume/reset paths, especially CP instruction-cache setup and RLC firmware startup, because those paths use high-impact CP/RLC fields.
- Performance counter tests that program GL/CB/DB/RMI/GUS/PA_PH/UTCL1 counters and verify plausible counter deltas under known workloads.
- SPM profiling tests that validate ring base/size programming, write pointer movement, accumulation done/overflow status, and sample interval behavior.
- Power-management tests that exercise RLC power gating, clock gating, PACE timers, SMU clock request, and serdes busy/status polling through suspend/resume and reset.
- Fault-injection or debug tests that verify UTCL1 fault/retry/PRT status and error address/VMID capture decode correctly.
