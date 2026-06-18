# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 22328-24771

## Scope

This chunk is a generated AMD GC 9.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is exposed as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros for composing and decoding 32-bit MMIO register values. There are no functions, structs, enums, variables, includes, allocation sites, locks, callbacks, or executable branches in this line range.

The selected lines start in the middle of the `RLC_SPM_PERFMON_SEGMENT_SIZE` definition, after that register's field shifts were emitted by the previous chunk. They then cover RLC streaming performance monitor selection, sample-delay, ring, and perf-counter controls; RMI, ATC L2, and MC VM L2 performance counter fields; a large `gc_rlcpdec` RLC management/power/register-save block; and the beginning of the `gc_pwrdec` CGTS power-control register set through `CGTS_CU8_LDS_SQ_CTRL_REG`. The range ends mid-register, after `CGTS_CU8_LDS_SQ_CTRL_REG__SQ_OVERRIDE_MASK`, so the remaining masks for that register and later CGTS CU entries belong to a later chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM graphics-core hardware metadata and is unrelated to Ceph or distributed filesystem behavior.

## Purpose

`gc_9_0_sh_mask.h` supplies bit layouts for AMD graphics core 9.0 hardware registers. Driver code combines these macros with the matching register-offset definitions from `gc_9_0_offset.h` and AMDGPU helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` instead of hard-coding bit positions.

This chunk focuses on runtime graphics management and observability surfaces:

- RLC SPM configuration: segment sizes, per-block sample delays, mux select address/data windows, ring read pointers, segment thresholds, interrupt control/status, and memory-controller controls used by the streaming performance monitor path.
- RLC and RMI perf counters: RLC perfmon enable/state/sample controls, RLC counter selectors, RLC GPU IOV performance counter addressing/data fields, RMI performance counter selectors, modes, VMID/CID filters, event windows, burst thresholds, soft reset, and SPM selection.
- ATC L2 and MC VM L2 performance counters: counter configuration, range selection, enable/clear bits, result counter selection, trigger fields, clear-all, enable-any, and saturate-stop controls.
- RLC control and status: RLC enable/status/safe-mode handshakes, SMU/RLCV command and response fields, reference-clock timestamps, GPM timers, interrupt status, load-balancing, microcode flags, GPM thread reset/priority/enable, CP DMA completion bits, firewall violation capture, GPU clock counters, and power-gating status/control.
- RLC power, clock, and register-save machinery: MGCG/CGCG/CGLS controls, clock-gating overrides, power-gating delays and masks, dynamic/static CU power status and requests, SERDES register-save master masks/busy state, scratch/general registers, SRM command windows, CSIB address/length fields, SMU messages/arguments, prewalker UTCL1 programming, R2I controls, UTCL2 controls, and double-shift/load-balance status.
- RLC UTCL1 translation controls and errors: GPM/SPM/prewalker UTCL1 control registers, busy/stall status, translated request error code/VMID/address fields for SPM and GPM threads, and XNACK redo/drop/bypass/invalidate/snoop controls.
- CGTS power controls: top-level CGTS slow mode/read controls, TCC disable masks, and repeated per-CU control registers for shader processors, LDS/SQ, TA/SQC, and TD/TCPF low-power/busy override controls.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The exported interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the raw bit mask for that field inside a 32-bit register value.
- Register addresses and base-index metadata come from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h`.
- Consumers normally use these symbols through AMDGPU register helpers, including field pack/unpack helpers, `RREG32*`/`WREG32*` MMIO accessors, SOC15 offset helpers, indexed register accessors, power-management paths, profiling paths, firmware/RLC code, and debugfs/register-dump tooling.

Important register groups in this range include:

- `RLC_SPM_PERFMON_SEGMENT_SIZE`, `RLC_SPM_*_PERFMON_SAMPLE_DELAY`, `RLC_SPM_SE_MUXSEL_*`, `RLC_SPM_GLOBAL_MUXSEL_*`, `RLC_SPM_RING_RDPTR`, `RLC_SPM_SEGMENT_THRESHOLD`, `RLC_SPM_MC_CNTL`, `RLC_SPM_INT_CNTL`, and `RLC_SPM_INT_STATUS`: RLC SPM sizing, selection, sampling, ring, memory, and interrupt fields.
- `RLC_PERFMON_CLK_CNTL`, `RLC_PERFMON_CNTL`, `RLC_PERFCOUNTER0_SELECT`, `RLC_PERFCOUNTER1_SELECT`, and `RLC_GPU_IOV_PERF_CNT_*`: RLC-local performance monitor state, counter selectors, and virtualization-aware counter read/write windows keyed by VFID and counter ID.
- `RMI_PERFCOUNTER*_SELECT`, `RMI_PERFCOUNTER*_SELECT1`, and `RMI_PERF_COUNTER_CNTL`: RMI performance event selection, counter modes, event windows, CID/VMID filters, burst thresholds, reset, and SPM routing.
- `ATC_L2_PERFCOUNTER*_CFG`, `ATC_L2_PERFCOUNTER_RSLT_CNTL`, `MC_VM_L2_PERFCOUNTER*_CFG`, and `MC_VM_L2_PERFCOUNTER_RSLT_CNTL`: ATC and VM L2 performance counter programming surfaces.
- `RLC_CNTL`, `RLC_STAT`, `RLC_SAFE_MODE`, `RLC_RLCV_SAFE_MODE`, `RLC_SMU_SAFE_MODE`, `RLC_RLCV_COMMAND`, `RLC_SMU_COMMAND`, `RLC_SMU_MESSAGE`, `SMU_RLC_RESPONSE`, `RLC_SMU_ARGUMENT_1`, and `RLC_SMU_ARGUMENT_2`: RLC enable/status and command/response handshakes among RLC, RLCV, and SMU.
- `RLC_REFCLOCK_TIMESTAMP_*`, `RLC_GPM_TIMER_INT_*`, `RLC_GPM_TIMER_CTRL`, `RLC_GPM_TIMER_STAT`, `RLC_GPU_CLOCK_COUNT_*`, `RLC_CAPTURE_GPU_CLOCK_COUNT`, `RLC_GPU_CLOCK_32_RES_SEL`, and `RLC_GPU_CLOCK_32`: timestamp, timer, and clock-count capture fields.
- `RLC_GPM_STAT`, `RLC_PG_CNTL`, `RLC_DYN_PG_STATUS`, `RLC_DYN_PG_REQUEST`, `RLC_STATIC_PG_STATUS`, `RLC_CU_STATUS`, `RLC_LB_INIT_CU_MASK`, `RLC_LB_ALWAYS_ACTIVE_CU_MASK`, `RLC_PG_ALWAYS_ON_CU_MASK`, `RLC_MAX_PG_CU`, `RLC_AUTO_PG_CTRL`, and `RLC_LBPW_CU_STAT`: power-gating, CU mask, load-balance, and live status fields.
- `RLC_MGCG_CTRL`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, `RLC_CGCG_RAMP_CTRL`, `RLC_CGCG_CGLS_CTRL_3D`, and `RLC_CGCG_RAMP_CTRL_3D`: medium-grain/coarse-grain clock-gating and light-sleep control, override, and ramp parameters.
- `RLC_SERDES_*`, `RLC_SRM_*`, `RLC_GPM_SCRATCH_*`, `RLC_GPM_GENERAL_*`, `RLC_CSIB_*`, and `RLC_JUMP_TABLE_RESTORE`: RLC register-save, scratch/general data, context-save instruction buffer, and restore-address fields.
- `RLC_GPM_UTCL1_CNTL_*`, `RLC_SPM_UTCL1_CNTL`, `RLC_PREWALKER_UTCL1_*`, `RLC_UTCL1_STATUS`, `RLC_UTCL1_STATUS_2`, `RLC_UTCL2_CNTL`, and `RLC_*_UTCL1_*ERROR_*`: RLC-facing translation/cache control and fault decode fields.
- `CGTS_SM_CTRL_REG`, `CGTS_RD_CTRL_REG`, `CGTS_RD_REG`, `CGTS_TCC_DISABLE`, `CGTS_USER_TCC_DISABLE`, and `CGTS_CU0_*` through the visible part of `CGTS_CU8_LDS_SQ_CTRL_REG`: CGTS slow-mode/readback, TCC disable, and per-CU block override/busy/light-sleep/SIMD-busy controls.

## Control Flow

This header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select the GC 9.0 generated register headers for the active ASIC.
2. Select a register address from `gc_9_0_offset.h`.
3. Use this file's shift/mask macros, usually through field helpers, to compose or decode a register value.
4. Read or write the register through MMIO, indexed register access, RLC-safe access, firmware/SMU-mediated flows, profiling paths, power-management paths, or debug tooling.

For RLC/SPM/perfmon code, higher-level consumers program selectors, sample delays, ring parameters, counter modes, and result triggers around profiling sessions or diagnostics. For RLC power management, consumers sequence safe-mode commands, SMU/RLC handshakes, power-gating masks, clock-gating controls, GPM thread state, and register-save operations during GPU bring-up, runtime power transitions, suspend/resume, and reset. For CGTS, consumers write per-CU override fields to force or observe low-power/busy states for shader/TCP/LDS/SQ/TA/SQC blocks. This file does not encode ordering constraints, polling loops, access permissions, clear-on-read/write-one-to-clear semantics, or side effects.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware-visible state:

- RLC SPM mux selections, sample delays, segment thresholds, ring pointers, interrupt enables, perfmon state, and performance counter selections are persistent hardware programming state until reset, power-gating loss, or driver reprogramming. Counter values and ring pointers can change while profiling is active.
- RLC safe-mode, RLCV, and SMU command/response registers are handshake surfaces. Their fields can transition asynchronously as firmware and hardware accept commands.
- RLC timestamps, GPU clock counters, GPM timer status, interrupt status, CP DMA completion bits, firewall violation address, power-gating status, UTCL1 status, and SERDES/SRM busy fields are live observation state. Some may be sticky or clear-sensitive according to hardware semantics outside this header.
- RLC power-gating, CU mask, clock-gating, ramp, delay, load-balance, GPM thread, SRM, and prewalker fields are control state that persists until overwritten, reset, firmware reinitialization, or a power-management transition.
- UTCL1/UTCL2 control fields affect translation behavior for RLC, GPM, SPM, and prewalker traffic. Error fields capture translated request error code, VMID, and address fragments for diagnostics.
- CGTS control registers persist as block-level power/busy/low-power override controls for individual CUs and functional units. Their status-like fields can reflect live hardware state and may differ across shader arrays or harvested CUs.

Reserved fields appear throughout the chunk. Consumers should preserve reserved bits during read-modify-write unless a hardware programming guide explicitly defines a full-register write value.

## Dependencies And Integration Points

The primary dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h`, which supplies matching offsets and base-index metadata. This generated shift/mask file must stay synchronized with the GC 9.0 register database and with the offset header.

Likely integration points in AMDGPU include:

- RLC firmware initialization, safe-mode entry/exit, RLCV command paths, SMU command/response flows, and reset recovery code that program `RLC_CNTL`, `RLC_SAFE_MODE`, `RLC_RLCV_SAFE_MODE`, `RLC_SMU_SAFE_MODE`, and related command/response registers.
- GFX power management code that controls RLC power-gating, CU power masks, load balancing, CGCG/CGLS/MGCG, 3D clock-gating controls, and CGTS per-CU overrides.
- Profiling and performance-monitoring code that configures RLC SPM, RLC perfmon counters, RMI counters, ATC L2 counters, and MC VM L2 counters.
- Virtualization or SR-IOV-aware graphics code using `RLC_GPU_IOV_PERF_CNT_*` fields to select virtual functions and counter IDs.
- Register-save/restore and context-management code that uses RLC SERDES, SRM, CSIB, scratch, and general registers.
- GPUVM and RLC translation diagnostics that decode RLC UTCL1/UTCL2 status and translated request error fields.
- Debugfs, register-dump, hang-triage, and hardware validation tools that decode live RLC status, timer, interrupt, power, busy, and CGTS per-CU state.

Because this is generated hardware metadata, concrete behavior lives in consumers through AMDGPU register-access wrappers and in firmware/hardware documentation rather than in this file.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask can compile cleanly while programming or decoding the wrong hardware bit.
- This chunk starts and ends mid-definition family. It starts with only the masks for `RLC_SPM_PERFMON_SEGMENT_SIZE`, and it ends inside `CGTS_CU8_LDS_SQ_CTRL_REG`; file-level research must reconcile these boundaries with adjacent chunks.
- Many registers are control or handshake surfaces, not passive data. Misprogramming RLC safe mode, SMU/RLCV commands, SRM commands, power-gating masks, or CGTS overrides can hang graphics, break firmware communication, or corrupt register-save flows.
- Performance counter layouts are repetitive but not identical. RMI counters 0 and 2 have extra selector registers for multiple events, while counters 1 and 3 are simpler; assuming a uniform layout can select the wrong events.
- ATC L2 and MC VM L2 counter result controls have trigger, enable-any, clear-all, and stop-on-saturate bits. Incorrect clear/enable sequencing can produce stale or lost profiling samples.
- Address fragments appear in multiple places: RLC CSIB high addresses are only 16 bits, UTCL1 error MSB fields are narrow, and prewalker address/size fields are split. Consumers must use the documented packing, not generic 64-bit assumptions.
- Some fields are one-bit pulses or sticky status bits, such as capture, reset, force, abort, interrupt, and completion fields. The shift/mask macros do not describe clear or pulse semantics.
- Reserved masks are large in many power-management and CGTS registers. Read-modify-write paths should preserve reserved values to avoid enabling undocumented hardware behavior.
- Per-CU CGTS registers are highly repetitive. Off-by-one register selection or copy/paste mistakes can affect the wrong CU or wrong functional unit, especially with harvested/disabled CUs.
- UTCL1 control fields include bypass, invalidate, drop, snoop, and VMID-dirty controls. Misuse can hide translation faults, force incorrect snooping, or interfere with XNACK retry behavior.

## Test Signals

Useful validation should combine generated-data checks, build coverage, and hardware/runtime diagnostics:

- Build AMDGPU code paths that include `gc_9_0_sh_mask.h` and `gc_9_0_offset.h`; missing, renamed, or malformed macros should surface at compile time.
- Mechanically compare this line range against AMD's authoritative GC 9.0 register database. Each complete field should have a matching shift and mask, and masks should align with the declared shift/width.
- Cross-check every register named in this chunk against `gc_9_0_offset.h` for matching address definitions and base indices.
- Run static consistency checks for repeated families: RLC SPM per-block sample delays, RMI counter selectors, ATC/MC VM L2 counter config registers, GPM timer fields, GPM thread fields, SRM index address/data windows, UTCL1 per-thread error registers, and CGTS per-CU control registers.
- Exercise GPU initialization, RLC firmware load, safe-mode handshakes, suspend/resume, runtime power transitions, and GPU reset on GC 9.0 hardware. Signals include successful RLC/SMU command completion, no stuck RLC busy status, stable clock/power status, and clean reset recovery.
- Validate profiling flows by programming RLC SPM, RLC/RMI counters, ATC L2 counters, and MC VM L2 counters against controlled workloads and checking that counters move, clear, and stop as expected.
- Test SR-IOV or virtualization paths, where available, by selecting VFID/counter IDs through `RLC_GPU_IOV_PERF_CNT_*` and verifying per-VF results.
- Stress power-gating and clock-gating transitions while sampling `RLC_GPM_STAT`, `RLC_CU_STATUS`, `RLC_DYN_PG_STATUS`, `RLC_STATIC_PG_STATUS`, and CGTS override/status fields for expected transitions.
- Inject or reproduce controlled GPUVM/RLC translation faults and verify that UTCL1 error code, VMID, and address fragments decode consistently with firmware or hardware traces.
- Run register-save/restore validation that exercises SERDES/SRM/CSIB fields and checks FIFO busy/empty, abort, and restored-state signals.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002624`. The previous chunk owns the beginning of `RLC_SPM_PERFMON_SEGMENT_SIZE`, including its register marker and shifts. This chunk then covers RLC SPM/perfmon, RMI/ATC/MC VM L2 performance counters, most of a dense RLC management and power block, and the beginning of CGTS per-CU power-control definitions. The next chunk should complete `CGTS_CU8_LDS_SQ_CTRL_REG` and continue the remaining `gc_pwrdec` CGTS register definitions. The final per-file research should merge these artificial chunk boundaries before describing the complete `gc_9_0_sh_mask.h` register map.
