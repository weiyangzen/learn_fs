# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h lines 1-2488

## Purpose

This chunk is the opening slice of the generated AMD GC 11.0.0 register offset header. It contains preprocessor constants that map Graphics Core hardware register names to SOC15-style register offsets and base-index selectors. It has no executable C code; its public interface is a large set of `#define reg...` names consumed by AMDGPU, AMDKFD, display, SDMA, MES, IMU, and GFX code when issuing MMIO reads and writes.

The requested range covers the file license/header guard and 2,395 `#define reg...` lines. Those lines are mostly register-offset and matching `_BASE_IDX` definitions. The chunk begins at the start of the file with SDMA0 decoder metadata, covers the complete SDMA0 and SDMA1 queue/register blocks in this early part of the header, then covers several GC-wide blocks including GRBM, CP debug/status, PA, SQ, SH/SPI, texture, GDS, render backend/color/depth/cache, and the beginning of GCEA memory/client arbitration. The chunk ends inside `gc_gceadec` after `regGCEA_IO_WR_COMBINE_FLUSH`; later GC 11.0.0 offset definitions are outside this chunk.

Although this file is under a local `ceph-client` source mirror, the content is AMDGPU graphics hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, sysfs/debugfs entries, or direct register accesses in this range. The API is the generated macro naming contract:

- `reg<REGISTER>` expands to the register offset used by SOC15 register-access helpers.
- `reg<REGISTER>_BASE_IDX` selects the register aperture/base index. In this chunk most ordinary GC and SDMA queue registers use base index `0`, while SDMA hypervisor, performance-select, and performance-data windows use base index `1`.

Major address blocks in this chunk are:

- `gc_sdma0_sdma0dec`, base `0x4980`: SDMA0 core control/status and queue register window. It defines global SDMA control, timestamps, power, GB address config, ring-buffer pointer fetch, watchdog, quantum, status, EDC, atomics, UTCL1/XNACK/TLBI, tiling, interrupts, scratch RAM, queue reset, firmware status, and queues 0-7. Each queue has a repeated register pattern for ring-buffer control/base/read/write pointers, read-pointer writeback address, indirect-buffer control/base/size/offset, skip/context status, doorbell/log/offset, CSA address, scheduling, preempt, write-pointer polling address, AQL control, minor pointer update, RB preempt, and mid-command state.
- `gc_sdma0_sdma1dec`, base `0x6180`: the same SDMA decoder layout for SDMA1, with offsets shifted to the `0x0600`-based register range and queues 0-7 ending at `regSDMA1_QUEUE7_MIDCMD_CNTL`.
- `gc_sdma0_sdma0hypdec` and `gc_sdma0_sdma1hypdec`: SDMA microcode address/data, self-load, broadcast microcode access, and F32 control registers for both SDMA engines.
- `gc_sdma0_sdma0perfsdec`, `gc_sdma0_sdma1perfsdec`, `gc_sdma0_sdma0perfddec`, and `gc_sdma0_sdma1perfddec`: SDMA performance-counter configuration/select registers and low/high result windows.
- `gc_grbmdec`, base `0x8000`: graphics register bus manager controls, status per shader engine, soft reset, clock enable, read/write error, trap, scratch, fence-range, invalid-pipe, UTCL2 invalidation range, power, interrupt, and violation data registers.
- `gc_cpdec`, base `0x8200`: command processor debug and status registers for CPC/CPF/PFP/ME/MEC paths, busy/stalled/free-count reports, header dumps, instruction pointers, context/preemption status, ring read pointers, write-pointer polling, ROQ/STQ/MEQ thresholds and availability, indexed command debug access, and privilege-violation address reporting.
- `gc_padec`, base `0x8800`: primitive assembler/geometry front-end registers such as VGT FIFO depths, WD/IA UTCL1 state, shader-array/backend disable configuration, GE status/rate controls, pipe control, PA clip/setup status, and FIFO-depth controls.
- `gc_sqdec`, base `0x8c00`: shader queue, scalar/vector front-end, LDS, SQC, SQG, arbitration, performance snapshot, interrupt auto-mask/message controls, watchpoint address/control registers, and indirect SQ command/index/data access.
- `gc_shsdec`, base `0x9000`: shader/SPI-related debug, wavefront limit/lifetime status, static WGP masks, GDS credits, export/scoreboard buffer sizes, CSQ wave-active counters, trap-screen ranges for partitions P0/P1, and SPI configuration registers.
- `gc_tpdec`, base `0x9400`: texture/TA/TD status, DSM controls, scratch, and TA control/status registers.
- `gc_gdsdec`, base `0x9700`: global data share configuration, status, protection-fault, VM-protection-fault, EDC counters, and DSM controls.
- `gc_rbdec`, base `0x9800`: depth/color/render backend debug, stutter, credit, watermark, FIFO-depth, ring, exception, SRAM/interface clock gating, RB redundancy/backend-disable, GB address/backend map/GPU ID, CB hardware controls, DCC config, cache-evict points, and global chicken bits.
- `gc_gceadec`, base `0xa800`: the first GCEA DRAM and IO client-to-group, group-to-VC, lazy, CAM, page-burst, priority aging/queuing/fixed/urgency/quantum, and combine-flush offsets. The GCEA block continues after this chunk.

## Control Flow

This header has no runtime control flow. It participates in compile-time register selection:

1. GC 11 generation driver files include this offset header, usually with the matching `gc_11_0_0_sh_mask.h` and sometimes `gc_11_0_0_default.h`.
2. Driver code passes `reg...` constants to AMDGPU register access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_IP`, `WREG32_SOC15_IP`, or lower-level `RREG32`/`WREG32` paths after deriving an absolute offset.
3. The `_BASE_IDX` value tells SOC15 helper logic which register base aperture to use for the named register.
4. The hardware behavior is implemented by the consuming driver code and silicon. This generated file only supplies addresses.

The strongest local pattern is SDMA queue addressing. `amdgpu_amdkfd_gfx_v11.c` computes SDMA RLC register ranges from `regSDMA0_QUEUE0_RB_CNTL`, uses the distance from `regSDMA0_QUEUE1_RB_CNTL` to step between queue windows, and uses the distance between `regSDMA1_QUEUE0_RB_CNTL` and `regSDMA0_QUEUE0_RB_CNTL` to switch engines. `sdma_v6_0.c` similarly calls `sdma_v6_0_get_reg_offset()` with these generated offsets before programming or reading queue registers.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It names hardware-visible state:

- SDMA engine state: control, power, firmware/microcode access, global timestamps, status/error/EDC counters, UTCL1/XNACK/TLBI state, atomics, queue reset, scratch RAM, and per-queue RB/IB/doorbell/preemption/scheduling/AQL/mid-command state.
- SDMA performance state: selected events, counter configuration, result controls, and low/high counter readback registers.
- GRBM state: graphics front-end status, per-shader-engine status, soft-reset controls, clock enable state, traps, scratch registers, error/violation reports, power controls, and fence/invalid-pipe metadata.
- CP state: command processor debug/status, busy/stalled state, micro-engine instruction/header dumps, queue thresholds/availability, ring read pointers, preemption/context status, and privilege-violation reporting.
- Geometry/shader state: primitive assembler, work distributor, input assembler, geometry engine, shader queue, SQC/LDS/SQG, SPI wavefront lifetime/status, WGP masks, GDS credits, trap-screen ranges, and watchpoint registers.
- Texture/GDS/RB/GCEA state: texture pipe status, global data share protection/EDC, depth/color backend debug/configuration/cache state, GB address/backend mapping, and DRAM/IO arbitration and priority policy registers.

Persistence and side effects are entirely hardware-defined. Some registers are configuration that retain values until driver reprogramming, power gating, suspend/resume, GPU reset, or ASIC reset. Other registers are status, counters, request/ack, write-one-to-clear, indexed windows, scratch, or self-clearing controls. This offset header does not encode access permissions, reset values, bitfields, volatility, or sequencing rules.

## Dependencies And Integration Points

This chunk must remain synchronized with AMD's GC 11.0.0 register database and companion generated headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h` supplies bit shifts and masks for many of the registers named here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_default.h` supplies reset/default values for many of the same register names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.c` includes this header and uses later and adjacent GC offsets for GFX bring-up, CP control, pipe reset, clock gating, and idle/status management. This chunk's GRBM, CP, SQ, PA, SPI, GDS, RB, and GCEA names are part of that register namespace even when individual uses are spread across the full file.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v6_0.c` includes this header and uses the SDMA queue offsets in this chunk for queue enable/disable, ring buffer programming, polling, and reset paths.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v11.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v11.c` consume the SDMA queue layout for KFD queue management and MQD/RLC register programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v11.c` uses GC 11 register naming while preparing compute queue descriptors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.c`, `imu_v11_0.c`, `gfxhub_v3_0.c`, `soc21.c`, `amdgpu_display.c`, and `display/amdgpu_dm/amdgpu_dm_plane.c` include this header as part of the SOC21/GC 11 register namespace.

The SDMA register offsets in this chunk are also structurally compared with later GC-generation headers such as `gc_11_0_3_offset.h`, `gc_11_5_0_offset.h`, `gc_12_0_0_offset.h`, and `gc_12_1_0_offset.h`. Consumers commonly assume repeated queue spacing and engine spacing are correct for the selected ASIC generation.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong offset or base index compiles cleanly and can redirect an MMIO access to the wrong register.
- The file is generated. Manual edits risk divergence from the authoritative hardware register database, companion shift/mask/default headers, firmware expectations, and silicon documentation.
- Chunk boundaries are artificial. This chunk starts at the real file beginning, but it ends in the middle of `gc_gceadec`; final per-file research should merge later chunks before making whole-file claims.
- SDMA queue layout is repetition-sensitive. KFD and SDMA code compute queue and engine offsets from the generated constants. A single bad queue stride, SDMA0/SDMA1 delta, or `_BASE_IDX` can break queue setup, doorbells, write-pointer polling, preemption, AQL mode, queue reset, or mid-command restore.
- SDMA registers include live pointer, doorbell, interrupt, scratch, and status windows. Misaddressed writes can corrupt active DMA rings, hang queues, lose interrupts, or wedge GPU reset/recovery paths.
- Microcode and broadcast SDMA registers use base index `1`. Treating them like ordinary SDMA queue registers would access a different aperture and may fail firmware loading or diagnostics.
- Performance counter select/result registers are split into configuration and data windows. Wrong offsets can yield misleading profiling data or interfere with active counters.
- GRBM soft reset, clock, and status offsets are central to GPU reset/idle paths. Mistakes can cause waits that never complete, incomplete resets, or accidental reset of the wrong graphics sub-block.
- CP debug/status and ring-read-pointer registers are used while diagnosing or controlling command submission. Bad offsets can hide queue hangs, report false busy/idle state, or corrupt indexed debug access through `CP_CMD_INDEX`/`CP_CMD_DATA`.
- SQ/SPI watchpoint, trap-screen, and wavefront lifetime registers are debugger- and fault-path sensitive. Offset drift may only appear under GPU debugging, trap, preemption, or shader fault workloads.
- RB/CB/DB and GCEA registers affect memory/backend behavior and arbitration. Bad programming may show up as rendering corruption, DCC/cache issues, poor QoS, or workload-specific memory stalls rather than an obvious compile-time failure.
- Several registers are status, error, counter, indexed data, or clear/control windows. The offset header does not identify read-only/write-only/write-one-to-clear semantics, so consumers must rely on the matching shift/mask docs and hardware programming guides.

## Test Signals

Useful validation combines generated-header consistency checks with runtime GPU coverage:

- Build AMDGPU with GC 11 support enabled. Missing or renamed macros should surface in `gfx_v11_0.c`, `sdma_v6_0.c`, `amdgpu_amdkfd_gfx_v11.c`, KFD MQD/queue-manager code, MES, IMU, gfxhub, SOC21, and display include users.
- Mechanically compare this range against AMD's GC 11.0.0 register database and verify each `reg...` offset has the intended `_BASE_IDX` companion.
- Cross-check this offset header against `gc_11_0_0_sh_mask.h` and `gc_11_0_0_default.h` so shift/mask/default definitions reference valid registers and no generated name drift exists.
- Run repetition checks across SDMA0 and SDMA1 queues 0-7. Expected signals are consistent per-queue stride, consistent queue member ordering, and the intended SDMA1 offset delta from SDMA0.
- Exercise SDMA rings and KFD SDMA queues: queue create/destroy, DMA copy/fill, doorbell submission, write-pointer polling, interrupt delivery, queue reset, preemption, AQL mode, suspend/resume, and GPU reset recovery.
- Exercise SDMA performance counters and confirm selected events produce sane low/high counter values without corrupting queue operation.
- Run graphics command submission and reset/idle tests that cover GRBM status, soft reset, CP busy/stalled status, CP ring pointers, and pipe cleanup/reset paths.
- Run compute and graphics workloads with preemption, wavefront faults/traps, shader watchpoints where supported, and KFD queue scheduling to cover SQ/SPI/CP debug-sensitive registers.
- Use register dumps on GC 11.0.0 hardware to confirm key offsets land in the expected block ranges: SDMA0 `0x0000`-based queue window, SDMA1 `0x0600`-based queue window, GRBM around `0x0da0`, CP around `0x0e20`/`0x0f3c`, SQ around `0x10a0`, SPI around `0x11b8`, RB/CB around `0x13ac`/`0x1422`, and GCEA around `0x17a0`.
- Run display or rendering stress that exercises RB/CB/DB and GCEA arbitration indirectly, watching for corruption, hangs, timeout recovery, and performance/QoS regressions.

## Cross-Chunk Notes

This chunk starts at the actual file beginning and includes the license, include guard, and first register blocks. It fully covers the early SDMA0/SDMA1 decoder, SDMA hypervisor, and SDMA performance windows, and it covers complete GRBM, CP debug/status, PA, SQ, SH/SPI, TP, GDS, and RB block slices present before line 2488. It stops inside `gc_gceadec` after `regGCEA_IO_WR_COMBINE_FLUSH`; the next chunk should continue the remaining GCEA and later GC 11.0.0 offset blocks. The final per-file research document should reconcile this chunk with later chunks before summarizing all GC 11.0.0 register coverage.
