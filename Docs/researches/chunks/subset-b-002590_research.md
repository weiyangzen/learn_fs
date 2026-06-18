# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h lines 9894-12404

## Scope

This chunk covers a late slice of the generated AMD GC 12.1.0 register offset header. It starts inside the `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_comp_wgsdec` compute WGS block, immediately after earlier compute dispatch dimension/start/thread registers, and ends in the `gfx_se_sqind` indirect SQ index block after `ixSQ_WAVE_TTMP7`.

The range contains 2,391 preprocessor definitions: 1,215 register or indirect-index constants and 1,176 matching `_BASE_IDX` constants. It is pure hardware metadata. There are no C functions, structs, enums, storage objects, include dependencies, locks, allocations, sysfs/debugfs entries, or executable branches in this chunk.

Major covered areas are:

- WGS compute dispatch, program, scratch, static-thread-management, relaunch, user-data, interrupt, RS64 microcontroller, suspend/resume, aperture, cache, scratch, latency, metadata, and status registers.
- Shader-engine GL1/GL1X arbitration, compression, UTCL, clock/power, CAC, DIDT/EDC, and power-estimation registers.
- Shader-engine performance counter low/high data registers and selector/control registers for GE2, GRBMH, PA, SPI, PC, SQ, SQG, SX, TA, TD, TCP, GL1C/GL1XC, CB, DB, RMI, PA_PH, UTCL1, WGS, GL1A, and GL1XA.
- SQ thread-trace buffer, mask, token, write-pointer, halt, restore, status, and counter registers.
- Per-block clock-gating and clock-control registers for SPI, PC, VGT/GS/NGG, PA, SQ/SQG/SP, SX, TA, TD, DB, CB, RMI, SE CAC, PA_PH, TCP, LDS, UTCL1, GRBMH, SC, GL1C/GL1A, and GL1XC/GL1XA.
- User topology and remap registers for GL1 pipe steering, hash config, shader-array config, RB backend disable, RMI redundancy, shader-rate config, WGP/RB remapping, and system aperture default address.
- GCVM, GCMC, GCUTC, GCUTCL2, GCVML2, GC ATC L2, and GC L2TLB address blocks for aperture location, L2 translation/cache control, page faults, contexts, invalidate engines, page-table ranges, performance counters, ATS/IOMMU controls, per-VF framebuffer apertures, and PSP/hypervisor-visible translation controls.
- `gfx_se_sqind` indirect indexes for wave debug/status, program counter, allocation, exception, trap, scratch, hardware ID, scheduler, XNACK, performance snapshot, and TTMP register reads.

Although this tree is under a `ceph-client` source mirror, this file is AMDGPU graphics hardware register metadata and does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header section is to provide the compile-time address ABI between GC 12.1.0 driver code and graphics/compute/translation hardware. Each ordinary register is represented by:

- `reg<REGISTER>`, the SOC15-style register offset.
- `reg<REGISTER>_BASE_IDX`, the register aperture/base selector used by AMDGPU register helpers.

This chunk also includes `ixSQ_*` constants. Those are not MMIO register offsets in the same style as `reg...`; they are indirect SQ wave/debug indexes consumed through SQ indirect access helpers. In local GC 12 code, `gfx_v12_0.c` uses `wave_read_ind()` with indexes such as `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_LO`, `ixSQ_WAVE_PC_HI`, `ixSQ_WAVE_HW_ID1`, `ixSQ_WAVE_HW_ID2`, `ixSQ_WAVE_GPR_ALLOC`, `ixSQ_WAVE_LDS_ALLOC`, and related wave state indexes when collecting wavefront state.

The companion `gc_12_1_0_sh_mask.h` file supplies bit shifts and masks for many of these register names, and `gc_12_1_0_default.h` supplies generated reset/default values where available. This offset header only names addresses and base indices.

## Important Macro Families

### WGS Compute and WGS Decoder State

The chunk begins in the middle of WGS compute dispatch state. Covered compute registers include `regWGS_COMPUTE_PERFCOUNT_ENABLE`, program pointer registers `regWGS_COMPUTE_PGM_LO/HI`, dispatch packet and scratch base registers, program resource registers, VMID, resource limits, static thread management or destination-enable aliases for shader engines, temporary ring size, restart coordinates, thread trace enable, dispatch IDs, request control, user accumulators, shader checksum, dispatch interleave, relaunch and wave restore address registers, prescaled dimensions, and 16 `regWGS_COMPUTE_USER_DATA_*` registers.

The subsequent `wgsdec` block exposes broader WGS firmware and scheduler state: interrupt info/context IDs, error/endian state, generated base address, WGS clock control, ME1 microcode address/data/checksum ports, suspend context-save base/size/stack/workgroup-state controls, OS pipes, suspend/resume requests, DDID base/control, RS64 program counter/vector/interrupt/control registers, machine interrupt enable/pending registers, data/instruction cache controls, timer compare registers, GP registers, indexed data-memory access, local/instruction/scratch apertures, RS64 perfcount and exception state, code/data base and bounds, interrupt status/free counts, ME1 pipe priority controls, IC base/control, ucode version, busy/stall/status registers, scratch index/data, latency statistics, TC performance counter window selection, metadata base/control, IQ timers, halt hysteresis, and RS64 thread control.

These names are integration points for compute dispatch setup, firmware loading, suspend/resume, diagnostic register dumps, performance monitoring, and low-level scheduler state inspection. The header does not define sequencing for those operations; it only supplies the offsets used by driver or firmware-facing code.

### Shader-Engine Arbitration, Power, CAC, and DIDT

The GL1 and GL1X decoder ranges define arbitration controls, DRAM burst masks/controls, status registers, replica fine-grain clock-gating overrides, credit/free-delay registers, compression mode, compressor overrides, and UTCL0 control/status/retry windows.

The `pfonly_secacdec`, `pwrdec`, `sc_pwrdec`, and `gl1_pwrdec` ranges cover shader-engine cost/activity and power behavior: `regSE_CAC_CTRL_*`, CAC soft override/value/window registers, `regDIDT_EDC_*` throttle/threshold/stall/status/overflow/power-delta/performance-counter registers, CAC weight tables for LDS, TCP, SQ, SP, SQC, CU, UTCL1, GL1C, and SPI, indirect CAC index/data access, and per-block clock-gating controls. These registers are typically tied to power-management policy, EDC protection, telemetry, and golden-register programming rather than ordinary queue submission.

### Performance Counters and Thread Trace

The `perfddec` block supplies low/high result registers for many shader-engine counters: GE2, GRBMH, PA_SU, PA_SC, SPI, PC, SQ, SQG, SX, TA, TD, TCP, GL1C, GL1XC, CB, DB, RMI, PA_PH, UTCL1, WGS, GL1A, and GL1XA. The `perfsdec` block supplies the paired selector/control registers for those counters, including secondary `SELECT1` registers where a block supports multiple packed selections or modes.

Important related control names include `regTCP_PERFCOUNTER_FILTER`, `regTCP_PERFCOUNTER_FILTER2`, `regTCP_PERFCOUNTER_FILTER_EN`, `regTCP_PERFCOUNTER_SET_DEFINE`, `regCB_PERFCOUNTER_FILTER`, `regRMI_PERF_COUNTER_CNTL`, `regSQG_PERFCOUNTER_CTRL`, `regSQG_PERFCOUNTER_CTRL2`, `regSQG_PERF_SAMPLE_FINISH`, `regSQ_PERFCOUNTER_CTRL`, and `regSQ_PERFCOUNTER_CTRL2`.

The same performance selector range includes SQ thread trace registers: buffer sizes and base addresses for two buffers, trace control, shader mask, token mask, write pointer, halt, power-off restore, status/status2, draw and marker counters for GFX and HP3D, dropped counter, and finish-done debug. These offsets are central to profiling and debug flows that collect wave or instruction activity.

### Clock Gating, Topology, and Remap

The power and hypervisor-adjacent shader-engine ranges define a large set of clock controls: `regGFX_ICG_*`, `regCGTT_*`, `regSQ_*_CLK_CTRL`, `regICG_*`, `regDB_CGTT_CLK_CTRL_0`, GL1/GL1X MGCG overrides, and GL1/GL1X clock controls. These names are used when initializing clock-gating policy, overriding clock gating for debug, or applying ASIC-specific golden settings.

Topology and remap state includes `regGL1_PIPE_STEER_LSB/MSB`, `regGL1_HASH_CFG`, `regGC_USER_SHADER_ARRAY_CONFIG`, `regGC_USER_RB_BACKEND_DISABLE`, `regGC_USER_RMI_REDUNDANCY`, `regGC_USER_SHADER_RATE_CONFIG_1`, `regGRBMH_WGP_SA0_REMAP_CNTL`, `regGRBMH_WGP_SA1_REMAP_CNTL`, `regGRBMH_RB_SA0_REMAP_CNTL`, and `regGRBMH_RB_SA1_REMAP_CNTL`. These registers describe harvested or remapped units and memory/cache routing. They must match the real ASIC topology.

### GCVM, GCMC, UTCL2, ATC L2, and L2TLB Translation Blocks

The second half of the chunk is dominated by graphics VM and translation-cache registers. It includes:

- `gcvmsharedpfdec` and `gcvml2pfdec` registers for system aperture defaults, active function ID, UTCL2 busy/group fault status, L2 control/status, dummy page fault, invalidation control, protection-fault control/status/address/default address, identity apertures, physical offset, group RT classes, bank-selection, parity, ICG, GCR control, walker throttling/debug, GPUVA VMID translation-assist request/response, credit-safety controls, UTCL2 FED VMID/ACK state, IH fault interrupt controls, and TLB retry/status registers.
- `gcvmsharedvcdec` and `gcvml2vcdec` registers for framebuffer, AGP, and system aperture base/top/low/high addresses, MX L1 TLB control, 16 VM context controls, context disable, invalidate-engine semaphores/requests/acks for engines 0-17, invalidate address ranges, context page-table base/start/end registers for contexts 0-15, per-PF/VF PTE cache fragment sizes, PCIe atomic support, retry-on-atomic control, and performance-counter data/config/result-control registers.
- `gcvml2prdec`, `gcatcl2prdec`, `gcl2tlbprdec`, `gcvml2pldec`, `gcatcl2pldec`, and `gcl2tlbpldec` registers for ATS, northbridge MMIO and DRAM windows, steering, XGMI/LFB/GPUIOV, host mapping, cacheable/local/LPDDR address ranges, APT control, ATC L2 control/cache-data/status/debug/bank/fault state, L2TLB TMZ/mtype/framebuffer-compression/retry-timeout/reserved-space status, and performance counters.
- Hypervisor/PSP-facing shared, VML2, ATC L2, and L2TLB registers: per-VF framebuffer size/offset for VF0-VF7 in this chunk, local framebuffer offset/start/end/lock control, translation bypass by VMID, secure master, IOMMU host translation enable/control/performance optimization, GPUVA translation assist control, translation fault controls, compression overrides, router control, miscellaneous control, and TLB CAM ECC control.

These blocks are integration points for GFXHUB/VM initialization, page-table programming, TLB invalidation, fault handling, ATS/IOMMU enablement, SR-IOV partitioning, XGMI and host-memory apertures, and VM performance monitoring.

### SQ Indirect Wave Indexes

The final `gfx_se_sqind` block defines indirect SQ indexes, not paired `reg..._BASE_IDX` offsets. Covered indexes include local debug status/control, wave active/valid/idle state, wave mode/status/privileged state, GPR/LDS/DVGPR allocation, instruction-buffer status/debug/flush, performance snapshot data and PC, exception flags, trap control, scratch base, hardware IDs, scheduler mode, XNACK state/mask, PC low/high, and TTMP0-TTMP7.

These constants are consumed through indirect SQ debug accessors, such as the GC 12 wave dump path in `gfx_v12_0.c`. They are mostly diagnostic/debugger-facing and should not be treated as direct MMIO offsets.

## Control Flow

There is no runtime control flow in this header chunk. Its effect is compile-time symbol substitution:

1. GC 12.1.0-aware code includes this offset header with matching shift/mask/default headers.
2. Driver code passes `reg...` constants and their `_BASE_IDX` values into SOC15/IP register access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_IP`, `WREG32_SOC15_IP`, `SOC15_REG_OFFSET`, or higher-level AMDGPU helpers.
3. Debug code passes `ixSQ_*` constants to SQ indirect access routines instead of direct MMIO helpers.
4. Hardware and firmware implement the behavior behind each address. This generated file does not encode ordering, polling, permission, volatility, or reset rules.

## State and Persistence Behavior

The header stores no software state and persists nothing. It names hardware-visible state that can be persistent, volatile, sticky, self-clearing, read-only, write-only, write-one-to-clear, indexed, or firmware-owned depending on the specific register.

Important state represented by this chunk includes WGS dispatch and user-data state, WGS firmware/microcode/suspend context, WGS apertures and caches, performance counter selections and results, SQ thread-trace buffers and status, clock-gating policy, CAC/DIDT/EDC thresholds and telemetry, topology/remap/harvest state, GCVM apertures and contexts, page-table base/start/end ranges, invalidate engine semaphores/requests/acks, protection-fault status and addresses, GPUVA translation-assist request/response windows, ATC L2 and L2TLB fault/status/cache/debug state, per-VF framebuffer aperture state, IOMMU/ATS/XGMI/host-mapping controls, and SQ wave debug state.

Persistence is hardware-defined. Configuration registers may survive until reprogramming, power gating, suspend/resume, GPU reset, or ASIC reset. Counters and status registers change as workloads execute. Fault and interrupt status can be sticky. Invalidation, translation-assist, microcode, indexed RAM/data, and thread-trace registers usually require strict sequencing in the consuming code.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention and must stay synchronized with the rest of the GC 12.1.0 generated set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h` for bitfield shifts and masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_default.h` for reset/default values where generated.
- GC 12 driver code that includes `gc/gc_12_1_0_offset.h`; locally `soc_v1_0.c` includes this header as part of the GC 12.1.0 register namespace.
- `gfx_v12_0.c`, which demonstrates the `ixSQ_*` integration pattern by collecting wave state with `wave_read_ind()`.
- GFXHUB/VM code paths for page tables, context ranges, invalidation, fault handling, ATS/IOMMU, and aperture programming. Some nearby local examples for related GCVM names appear in golden-register code such as `imu_v11_0_3.c`; GC 12.1.0 consumers use the matching generation's offsets.
- Profiling and debug tooling paths that program performance counter selectors/results and SQ thread trace.
- Power-management, clock-gating, and golden-register initialization paths for CGTT/ICG/CAC/DIDT/EDC controls.
- Virtualization/SR-IOV paths that rely on per-function IDs, per-VF framebuffer apertures, VM partitioning, translation bypass, secure/PSP controls, and host/XGMI apertures.

## Risks and Edge Cases

- Offset or `_BASE_IDX` drift compiles cleanly but can redirect MMIO reads/writes to unrelated hardware state. In these register families, that can cause queue hangs, VM faults, wrong page-table programming, lost invalidation acks, bad profiling data, firmware failures, or GPU reset problems.
- The chunk starts mid-address-block. The first full WGS compute registers, including dispatch initiator, dimensions, start coordinates, and thread counts, are immediately before this range. A final per-file report must merge adjacent chunks before making complete WGS compute claims.
- Many register families are mechanically repetitive but not identical. Performance counters differ by block and counter number; some have `SELECT1`, filters, set definitions, or result-control registers while others do not.
- WGS microcode, suspend/resume, RS64, indexed memory, and cache registers are sequencing-sensitive. The offset header does not say which writes are commands, which statuses must be polled, or which paths are firmware-owned.
- Clock, CAC, DIDT, and EDC controls can affect power, throttling, and stability. Treating them as ordinary debug knobs risks performance regressions, false telemetry, or hardware protection issues.
- Thread-trace and SQ indirect indexes are diagnostic paths. Confusing `ixSQ_*` indexes with direct `reg...` offsets, or using the wrong indirect selector, can return misleading wave state or perturb debug flows.
- GCVM context and invalidation blocks are dense and high impact. A wrong context base/start/end, invalidate request/ack, aperture, fault, or translation-assist offset can produce memory corruption, stale translations, page faults, or VM timeout recovery.
- Per-VF framebuffer and GPUIOV/XGMI/IOMMU controls are privilege-sensitive. Incorrect programming can break isolation, expose the wrong aperture, or leave a VF with inconsistent memory visibility.
- ATC L2 and L2TLB fault/status/debug registers mix performance, debug, translation, and fault-handling concerns. Misaddressed writes can hide real faults or corrupt ATS/TLB behavior.
- The chunk ends inside the SQ indirect index list. Later indexes after `ixSQ_WAVE_TTMP7` are outside this chunk and must be reconciled by the next chunk before summarizing all SQ indirect coverage.

## Test and Validation Signals

Useful validation is mostly generated-header consistency plus runtime GPU coverage:

- Build AMDGPU with GC 12.1.0 support enabled. Missing or renamed macros should surface in files that include `gc_12_1_0_offset.h` and matching mask/default headers.
- Mechanically compare this range against the authoritative GC 12.1.0 register database, verifying every `reg...` offset has the intended `_BASE_IDX` and that `ixSQ_*` indexes are not given base-index companions.
- Cross-check this offset chunk against `gc_12_1_0_sh_mask.h` and `gc_12_1_0_default.h` so field/default definitions reference valid register names.
- Exercise compute dispatch and shader workloads that cover WGS program/user-data/resource/scratch/VMID state, suspend/resume, queue restart/relaunch, and WGS status/error paths.
- Run profiler/performance-counter tests for GE2, GRBMH, PA, SPI, PC, SQ/SQG, SX, TA/TD/TCP, GL1C/GL1XC, CB/DB, RMI, PA_PH, UTCL1, WGS, GL1A, and GL1XA counters, including filter and result-control registers.
- Validate SQ thread trace and wave-state dumps on GC 12 hardware, checking buffer programming, write pointers, halt/status bits, dropped counters, and `ixSQ_*` wave readback fields.
- Run clock-gating, power-gating, suspend/resume, and golden-register tests that cover CGTT/ICG, CAC, DIDT, EDC, and GL1/GL1X power registers.
- Exercise VM bring-up and memory-management tests: context creation/destruction, page-table base/start/end programming, TLB invalidation engines 0-17, fault injection/reporting, dummy-page handling, identity aperture paths, ATS/IOMMU toggles where supported, and page-table walker throttling/debug.
- Exercise SR-IOV or partitioned-GPU validation where available: active function ID, per-VF framebuffer size/offset, host/XGMI apertures, translation bypass, secure/PSP controls, and local framebuffer lock behavior.
- Use register dumps on matching GC 12.1.0 hardware to confirm key block ranges align with the generated comments: WGS around base `0x31a00`/`0x31c00`, shader-engine performance data/select ranges around `0x34000`/`0x36000`, power controls around `0x3c000`, VM/UTCL2 PF/VC ranges around `0xa000`-`0xa5e0`, privileged/PL/HV/PSP ranges around `0x35380`-`0x3fa00`, and SQ indirect indexes from base `0x0`.

## Cross-Chunk Notes

This document is intentionally limited to lines 9894-12404. The first line is a `_BASE_IDX` companion for `regWGS_COMPUTE_PIPELINESTAT_ENABLE`, whose register offset is immediately before the chunk. The chunk also starts after the beginning of the WGS compute address block and ends before the full `gfx_se_sqind` indirect index table is complete. The merge/reconciliation lane should combine this with adjacent chunks before producing the final per-file research for `gc_12_1_0_offset.h`.
