# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 27309-29911

## Purpose

This chunk is generated AMD GC 10.1.0 register bitfield metadata. It contains no executable C logic; it exports preprocessor constants for bit shifts and masks used when programming or decoding Graphics Core command processor, geometry, shader, GDS, MES, GUS, GL1/CH, and GL2 cache/control registers. The companion register-address definitions live in `gc_10_1_0_offset.h`, and consumers combine offset, shift, and mask macros through AMDGPU/KFD register helpers or packet-building code.

The selected range contains 2,135 `#define` lines: 1,069 `__SHIFT` definitions and 1,066 `_MASK` definitions. It starts cleanly at `CP_WAIT_SEM_ADDR_LO` and ends inside `GL2C_CTRL3`; the final three `GL2C_CTRL3` masks (`COMP_TO_CONST_CAM_CHECK_ENABLE`, `FGCG_OVERRIDE`, and `SCRATCH`) are just outside this chunk. Although the source tree is under a local `ceph-client` mirror, this file is AMDGPU hardware metadata, not distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, memory allocations, callbacks, or runtime APIs in this slice. The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK`: 32-bit field mask used for read-modify-write, packet construction, or status decoding.

Major register families in this range are:

- Command processor and DMA registers: `CP_WAIT_SEM_ADDR_*`, `CP_DMA_PFP_*`, `CP_DMA_ME_*`, `CP_DMA_CNTL`, `CP_DMA_READ_TAGS`, and command-address registers define semaphore wait addresses, CP DMA source/destination addresses, cache policy, volatility, byte counts, raw-wait/write-combine behavior, command-buffer pointers, and DMA status.
- CP coherency and indirect-buffer state: `CP_COHER_*`, `CP_ME_COHER_*`, `CP_PFP_IB_CONTROL`, `CP_PFP_LOAD_CONTROL`, `CP_SCRATCH_*`, `CP_RB_OFFSET`, `CP_IB*_OFFSET`, `CP_*_BASE_*`, `CP_*_BUFSZ`, `CP_*_CMD_BUFSZ`, `CP_EOP_DONE_*`, `CP_DB_*`, `CP_CE_DB_*`, completion status, metadata base addresses, indirect draw/dispatch addresses, index base/type fields, and GDS backup address fields.
- Graphics front-end state: `RLC_GPM_PERF_COUNT_*`, `GRBM_GFX_INDEX`, `VGT_*`, `GE_*`, `WD_*`, and `IA_MULTI_VGT_PARAM_PIPED` fields cover GRBM shader-engine/instance targeting, primitive and index setup, transform-feedback and streamout sizes, vertex/index bounds, draw/instance counts, geometry-engine controls, user VGPR enables, stereo control, and work-distributor buffer bases.
- Rasterization, shader, texture, and depth counters: `PA_SU_LINE_STIPPLE_VALUE`, `PA_SC_*` screen extent/trap/stipple fields, `SQ_THREAD_TRACE_USERDATA_*`, `SQC_CACHES`, `SQC_WRITEBACK`, `TA_CS_BC_BASE_ADDR*`, `DB_OCCLUSION_COUNT*`, and `DB_ZPASS_COUNT*`.
- GDS atomics and synchronization: `GDS_RD_*`, `GDS_WR_*`, `GDS_WRITE_COMPLETE`, `GDS_ATOM_*`, `GDS_GWS_RESOURCE*`, and `GDS_OA_*` fields describe direct GDS read/write windows, burst access, atomic operation inputs/results, global wave sync resource bookkeeping, ordered-append counters, and associated ring/address controls.
- SPI remap and MES registers: `SPI_CONFIG_CNTL*_REMAP`, `SPI_WAVE_LIMIT_CNTL_REMAP`, then the `gc_cprs64dec` block with `CP_MES_*` program counter, trap vector, interrupt, scratch, machine CSR, timer/cycle, process-quantum, doorbell, general-purpose, debug-module, trigger, and perfcount control fields.
- GUS arbitration/QoS/diagnostics: the `gc_gusdec` block has `GUS_IO_*`, `GUS_DRAM_*`, `GUS_SDP_*`, `GUS_MISC*`, latency sampling, perf counters, error status, backdoor credits, L1 channel counters, and write-response FIFO control fields. These tune or report IO/DRAM priority aging, fixed priority, urgency, quantum, group burst, credits, latency, and errors.
- GL1/CH/GL2 cache and channel blocks: `gc_gl1dec`, `gc_chdec`, and `gc_gl2dec` define GL1 and channel arbitration, burst masks, pipe steering, status, GL1 cache status, CH/CHC/CHCG status, GL2 cache control, address match, writeback/invalidate done, soft reset, compression metadata controls, MDC prefetch, coherency behavior, and the first part of `GL2C_CTRL3`.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from driver code that includes the generated metadata and applies the fields to MMIO or packet words:

1. `amdgpu/gfx_v10_0.c`, `gfxhub_v2_0.c`, `mxgpu_nv.c`, `sdma_v5_0.c`, `nv.c`, `amdgpu_amdkfd_gfx_v10.c`, and KFD files such as `kfd_packet_manager_v9.c`, `kfd_mqd_manager_v10.c`, and `kfd_device_queue_manager_v10.c` include `gc_10_1_0_sh_mask.h`, usually with `gc_10_1_0_offset.h`.
2. Register helper macros and golden-register tables token-paste or directly reference register, field, shift, and mask constants.
3. GFX/KFD runtime paths program queue descriptors, doorbells, command rings, cache controls, DMA engines, GDS resources, MES scheduling registers, and cache arbitration registers.
4. Hardware executes the resulting command processor, shader, cache, GDS, and MES behavior; the macros only describe where fields sit inside 32-bit registers.

The chunk does not define ordering, locking, reset sequencing, timeout policy, packet format validity, read/write access type, or whether a status bit is sticky, self-clearing, read-only, or write-one-to-clear. Those rules live in AMDGPU/KFD code and the hardware programming guide.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed register state:

- CP state includes semaphore wait addresses, DMA source/destination/control values, indirect-buffer offsets and preamble ranges, scratch data, command-buffer base/size state, EOP completion controls, doorbell buffers, metadata bases, indirect draw/dispatch pointers, index state, and coherency request ranges.
- Graphics front-end state includes GRBM broadcast selection, primitive/index/instance counts, ring sizes, work-distributor base pointers, geometry engine control, line/screen trap/stipple state, and shader thread-trace userdata.
- GDS/GWS/OA state includes direct read/write cursors, atomic operands/results, synchronization resource counters, ordered-append counters, completion flags, and backup addresses.
- MES state includes scheduler program/trap vectors, interrupt and CSR state, scratch/general registers, process quantum, doorbell control, debug registers, timer/cycle counters, and performance counter control.
- GUS/GL1/CH/GL2 state includes arbitration policy, QoS weights, credits, latency sampling, error flags, L1 counters, cache control/status, coherency/compression metadata behavior, prefetch tuning, soft reset, and writeback/invalidate status.

Persistence is hardware-defined. Control fields generally last until rewritten, queue/context teardown, power gating, suspend/resume, GPU reset, or ASIC reset. Status, error, performance, counter, completion, and diagnostic fields can be live, latched, sticky, self-clearing, or valid only while the relevant clock/power domains are active. The generated shift/mask constants do not encode those access semantics.

## Dependencies And Integration Points

This chunk must remain synchronized with AMD's generated GC 10.1.0 register database and especially with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h`, which provides the matching `mm*`, `reg*`, or offset symbols for the same register names.
- AMDGPU GFX 10 code such as `gfx_v10_0.c`, which includes this header, applies golden settings for registers including `GL2C_CTRL3`, builds command packets, and controls graphics engine initialization, reset, and ring operation.
- KFD GFX 10 code such as `kfd_packet_manager_v9.c`, `kfd_mqd_manager_v10.c`, and `kfd_device_queue_manager_v10.c`, which uses GC register fields for queue management, MQD setup, doorbell/control paths, and compute scheduling.
- GFX hub, SDMA, virtualization, and SoC bring-up files that include GC offsets/masks when programming shared graphics, memory, or virtualization-facing hardware.
- Packet and helper definitions such as `soc15d.h`, where related `CP_COHER_CNTL` packet fields mirror several coherency bits exposed in this generated register header.

Important integration surfaces are command submission, CP DMA, acquire/release memory coherency, indirect buffers, queue and doorbell setup, shader/cache flush and invalidate, geometry front-end programming, streamout/transform feedback, GDS atomic/synchronization operations, MES scheduling and debug support, GUS QoS tuning, cache arbitration, and GL2 metadata/compression/cache behavior.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while corrupting adjacent fields, programming the wrong cache policy, or producing misleading status reads.
- Offset/header version mismatch is dangerous. Pairing this GC 10.1.0 mask header with a different GC offset header can silently target the wrong register layout.
- Several fields affect coherency, cache invalidation, writeback, CP DMA, and command buffer addresses. Incorrect values can cause stale memory, lost writes, ring hangs, GPU faults, or data corruption that appears far from the bad write.
- Address fields are split into low/high registers and sometimes use alignment-implied low bits. Consumers must preserve swap, high-address, and alignment fields rather than treating every address as a flat 32-bit value.
- CP, CE, PFP, ME, MES, and doorbell fields participate in command processor scheduling. Bad masks in queue or command-buffer setup can break only compute, only graphics, only preemption, or only a virtualization/SRIOV path.
- Status and counter fields are not ordinary read/write storage. Completion, perfcount, error, FIFO-full/empty, calibration, and busy fields may be read-only, sticky, self-clearing, or clear-on-write/read depending on hardware.
- GDS/GWS/OA and atomic fields are synchronization-sensitive. Incorrect resource index, counter, type, destination, or operation masks can break inter-wave synchronization or ordered append behavior without an immediate compile-time signal.
- The range crosses generated address-block boundaries and ends mid-register. Whole-file conclusions about GL2C coverage require the next chunk because `GL2C_CTRL3` is incomplete here.
- Reserved, scratch, and debug fields are exposed as masks. Driver code should preserve reserved bits and avoid enabling debug/test paths unless a validated ASIC sequence requires it.

## Test Signals

Useful validation combines generated-header checks with graphics/compute hardware coverage:

- Build AMDGPU and KFD GFX 10 paths that include `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h`; missing or renamed macros should surface in `gfx_v10_0.c`, KFD queue/MQD files, SDMA, GFX hub, and virtualization code.
- Static-check complete register groups in lines 27309-29911 for matching `__SHIFT` and `_MASK` definitions, allowing the known boundary exception where `GL2C_CTRL3` masks continue after line 29911.
- Cross-check this range against AMD's generated GC 10.1.0 register database and adjacent GC headers when validating ASIC-generation drift.
- Exercise graphics and compute rings, IB submission, CP DMA copies, acquire/release memory packets, cache flush/invalidate paths, queue creation/destruction, doorbell writes, preemption/reset, suspend/resume, and GPU reset.
- Run workloads that stress streamout, indirect draw/dispatch, index buffers, geometry front-end state, shader instruction/data cache invalidation, GDS atomics/GWS synchronization, ordered append, and MES scheduling.
- Inspect register dumps, debugfs output, KFD diagnostics, and kernel logs for ring timeouts, VM faults, CP/MES hangs, failed queue scheduling, stale-cache symptoms, GDS synchronization failures, GL2 writeback/invalidate stalls, GUS error flags, or unexpected GL1/CH/GL2 busy/full status.
- For performance-sensitive fields, compare counter and workload behavior before/after changes to GUS priority/credit registers and GL1/GL2 cache controls; regressions may show up as reduced throughput, elevated latency, or only on specific ASIC revisions.

## Cross-Chunk Notes

This document intentionally covers only lines 27309-29911 of `gc_10_1_0_sh_mask.h`. The previous chunk owns the preceding CP signal semaphore and `CP_WAIT_REG_MEM_TIMEOUT` fields. This chunk starts at `CP_WAIT_SEM_ADDR_LO`, spans several generated GC address blocks through the start of `GL2C_CTRL3`, and stops before the final three `GL2C_CTRL3` masks and the following `GL2C_LB_*` registers. The later merge/reconciliation lane should combine adjacent chunks before making final per-file claims about complete CP, GUS, GL1/CH, or GL2 register coverage.
