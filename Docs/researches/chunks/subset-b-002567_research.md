# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h lines 7471-9953

## Chunk Scope

This chunk is a generated AMD GC 12.0.0 register offset header segment. It contains C preprocessor constants only: each visible register macro maps a symbolic `reg...` name to a 32-bit register offset value, and each companion `reg..._BASE_IDX` macro maps that register to a SOC15 base-index selector. There are no functions, structs, enums, callbacks, locks, allocations, branches, or software-owned storage declarations in this range.

The range contains 2,403 `#define` lines: 1,202 register offset definitions and 1,201 `_BASE_IDX` definitions. The count is intentionally uneven because the chunk ends at `regSQG_PERFCOUNTER7_LO`; its companion `regSQG_PERFCOUNTER7_LO_BASE_IDX` is on the next source line outside this work item. The chunk also begins inside an existing SPI address block from the previous chunk before the first local address-block marker.

Visible address-block markers in this slice cover these GC graphics/shader-engine register regions:

- Tail of a preceding SPI block: live wave counters, debug reads, trap-screen pointers, and crawler configuration.
- `gc_gfx_se_gfx_se_tpdec` at `0x9400`: TD/TA control, status, power, DSM, and scratch registers.
- `gc_gfx_se_gfx_se_rbdec` at `0x9800`: DB/CB/GB backend debug, FIFO, arbitration, memory, backend map, and cache-control registers.
- `gc_gfx_se_gfx_se_spipdec2` at `0x9c80`: SPI PQEV and export-throttle controls.
- `gc_gfx_se_rmi_gfx_se_rmidec` at `0x2e200`: RMI request-interface control, status, scoreboard, xbar, UTCL1, formatter, clock, CID-map, spare, and redundancy registers.
- `gc_gfx_se_gfx_se_utcl1dec` at `0x9fb0`: GCR PIO and PMM controls/status.
- `gc_gfx_se_gfx_se_shdec` at `0xb000`: shader program addresses/resources/user data for PS/GS/VS/HS, SQ configuration controls, shader trap/debug, and SQC performance-snapshot registers.
- `gc_gfx_se_gfx_se_spipdec` at `0xc700`: SPI interpolation, thread-grouping, LDS, barycentric, and attribute-ring controls.
- `gc_gfx_se_gfx_se_tcpdec` at `0xca80`: TCP UTCL1 control/status, debug, cache, address/config, and invalidation-related registers.
- `gc_gfx_se_gfx_se_rasdec` at `0xce00`: GL1/SPI/SQ/SQC/TCP/TD/TA RAS and EDC count/control registers.
- `gc_gfx_se_gfx_se_gfxdec0` at `0x28000`: the largest block in this chunk, covering DB render/depth/stencil state, PA/SC viewport and rasterizer state, VGT and GE geometry state, CB color-buffer state, blend state, SX controls, depth/color base addresses, DB/CB clear words, clip/viewport transforms, and indexed multi-slot state families.
- `gc_gfx_se_gfx_se_pfvf_padec` at `0x2a500`: PF/VF-accessible PA/SC screen, trap-screen, binning, primitive-filter, and sample-pattern registers.
- `gc_gfx_se_gfx_se_pfvf_sqdec` at `0x2a780`: PF/VF-accessible SQ counters, watermarks, ring sizes, and WGP reserved-resource registers.
- `gc_gfx_se_gfx_se_pfonly_spidec`, `pfonly_utcl1dec`, `pfonly_tcpdec`, and `pfonly2_spidec`: PF-only SPI, UTCL1, TCP, and per-CU resource-reservation controls.
- `gc_gfx_se_gfx_se_gfxudec` at `0x30000`: user/config-like GE/VGT/PA/SC/SQ/SQC/TA/DB/SPI/CB/SX state, shader engine metrics, and debug state.
- `gc_gfx_se_gfx_se_gl1dec` at `0x33400`: GL1C/GL1A/GL1X/GL1I/GL1XC cache invalidation, status, control, event, and debug registers.
- `gc_gfx_se_gfx_se_pfonly_secacdec` at `0x33a00`: SE CAC control/status, accumulator, and block-weight registers.
- `gc_gfx_se_gfx_se_perfddec` at `0x34000`: GE2, GRBMH, PA_SU, PA_SC, SPI, PC, SQ, and SQG performance counter data registers.

Although the repository path includes `ceph-client`, this file is AMDGPU hardware metadata, not Ceph filesystem logic.

## Purpose

`gc_12_0_0_offset.h` supplies symbolic register offsets for AMD GC 12.0.0 graphics-core programming. Consumers combine these offsets with SOC15 register helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, and `WREG32_SOC15_OFFSET`. The companion `gc_12_0_0_sh_mask.h` file supplies bit shifts and masks for fields inside the registers named here.

This slice focuses on shader-engine and graphics-pipeline register addressability:

- Shader processor input (`SPI`) state for shader program pointers, resource descriptors, user data, accumulators, trap-screen state, LDS/thread-grouping controls, interpolation and attribute-ring configuration, live wave counts, and SPI performance counters.
- Shader queue (`SQ`) and shader cache (`SQC`) controls for config, status, counters, wave/dispatch behavior, trap/debug state, thread trace user data, reserved resources, and performance data.
- Texture/data path blocks (`TA`, `TD`, `TCP`, `UTCL1`, `GL1*`) for texture address/data controls, cache invalidation/status, UTCL1 request/fault paths, compression/arbitration, GL1 cache events, and debug access.
- Render backend blocks (`DB`, `CB`, `GB`, `SX`) for depth/stencil/color render state, backend maps, framebuffer/depth buffer base addresses, blend state, cache-control/debug, occlusion counters, and backend disable/topology registers.
- Primitive assembly, scan conversion, and geometry blocks (`PA`, `SC`, `VGT`, `GE`, `PC`) for viewport, scissor, clipping, rasterization, binning, screen extents, primitive rings, transform feedback, tessellation/offchip parameters, line stipple, sample pattern, primitive filtering, and performance counters.
- Request-interface and reliability blocks (`RMI`, `RAS`, `SE_CAC`) for request routing/status, scoreboard/xbar state, UTCL1 interaction, RAS/EDC counters, and shader-engine current/activity accounting.
- SR-IOV split ownership blocks: `PFVF` regions expose selected state to both physical and virtual functions, while `PFONLY` regions name privileged controls that should normally remain PF/firmware owned.

The header is part of the hardware ABI between AMDGPU driver code, generated register databases, firmware/golden-register programming, and the GC 12 silicon register map. It does not describe policy by itself; it gives the exact numeric offsets that policy code uses when it programs the GPU.

## Important APIs, Types, And Macros

There are no callable APIs or local types. The exported interface is the generated macro namespace.

Key macro families in this chunk:

- SPI debug, trap, and wave-observation registers: `regSPI_LB_DATA_PERWGP_WAVE_PS`, `regSPI_LB_DATA_PERWGP_WAVE_CS`, `regSPI_WF_ACTIVE_COUNT_GFX`, `regSPI_WF_ACTIVE_COUNT_HPG`, `regSPIS_DEBUG_READ`, `regBCI_DEBUG_READ`, `regSPI_P0_TRAP_SCREEN_*`, `regSPI_P1_TRAP_SCREEN_*`, `regSPI_GFX_CRAWLER_CONFIG`, and `regSPI_CS_CRAWLER_CONFIG`.
- TD/TA controls: `regTD_CNTL`, `regTD_STATUS`, `regTD_POWER_CNTL`, `regTD_DSM_CNTL*`, `regTA_CNTL`, `regTA_CNTL_AUX`, `regTA_CNTL2`, `regTA_STATUS`, and scratch registers.
- DB/CB/GB backend controls in `rbdec`: `regDB_DEBUG*`, `regDB_CREDIT_LIMIT`, `regDB_WATERMARKS`, `regDB_FIFO_DEPTH*`, `regDB_RING_CONTROL`, `regDB_EXCEPTION_CONTROL`, `regDB_MEM_CONFIG`, `regDB_ARB_CONFIG`, `regDB_DFD_INDIRECT_*`, `regDB_FGCG_*`, `regCC_RB_BACKEND_DISABLE`, `regGB_ADDR_CONFIG`, `regGB_BACKEND_MAP`, `regGB_GPU_ID`, and `regCB_HW_CONTROL*`.
- RMI controls/status: `regRMI_GENERAL_CNTL*`, `regRMI_GENERAL_STATUS`, `regRMI_SUBBLOCK_STATUS*`, `regRMI_XBAR_CONFIG`, `regRMI_DEMUX_CNTL`, `regRMI_UTCL1_CNTL*`, `regRMI_UTC_UNIT_CONFIG`, `regRMI_TCIW_FORMATTER*`, `regRMI_SCOREBOARD_*`, `regRMI_XBAR_ARBITER_CONFIG*`, `regRMI_CLOCK_CNTRL`, `regRMI_UTCL1_STATUS`, `regRMI_RB_GLX_CID_MAP`, `regRMI_XNACK_DEBUG`, `regRMI_SPARE*`, and `regCC_RMI_REDUNDANCY`.
- UTCL1/GCR/PMM registers: `regGCR_PIO_CNTL`, `regGCR_PIO_DATA`, `regPMM_CNTL`, `regPMM_STATUS`, `regGCR_PIO_INDEX`, and `regGCR_PIO_DATA_2`.
- Shader program and user-data register families: `regSPI_SHADER_PGM_*_PS`, `regSPI_SHADER_USER_DATA_PS_0` through `_31`, `regSPI_SHADER_USER_ACCUM_PS_*`, GS/ES program and user-data registers, VS program and user-data registers, HS program and user-data registers, shader checksums, and shader request/output config registers.
- SQ and SQC controls: `regSQ_CONFIG`, `regSQ_PERFCOUNTER_CTRL`, `regSQG_CONFIG`, `regSQ_THREAD_TRACE_*`, `regSQ_WAVE_*`, `regSQ_DEBUG_*`, `regSQ_WAVE_STATUS`, `regSQ_CMD`, `regSQ_IND_*`, `regSQC_CONFIG`, `regSQC_CACHES`, and SQC performance-snapshot registers.
- SPI pipeline controls: `regSPI_PS_INPUT_*`, `regSPI_BARYC_CNTL`, `regSPI_TMPRING_SIZE`, `regSPI_GDBG_*`, `regSPI_SHADER_LATE_ALLOC_*`, `regSPI_SHADER_PGM_RSRC4_*`, `regSPI_CONFIG_CNTL*`, `regSPI_GS_THROTTLE_CNTL*`, `regSPI_ATTRIBUTE_RING_*`, `regSPI_PS_INPUT_CNTL_0` through `_31`, and `regSPI_SHADER_COL_FORMAT`.
- TCP registers: `regTCP_UTCL1_CNTL`, `regTCP_UTCL1_STATUS`, `regTCP_DEBUG`, `regTCP_CHAN_STEER_*`, `regTCP_CNTL`, `regTCP_ADDR_CONFIG`, `regTCP_INVALIDATE`, `regTCP_STATUS`, `regTCP_CNTL2`, `regTCP_CREDIT`, `regTCP_COMPRESSION_CNTL`, and `regTCP_ARB`.
- RAS/EDC registers: `regGL1_EDC_CNT`, `regSPI_EDC_CNT`, `regSQ_EDC_CNT*`, `regSQC_EDC_*`, `regTCP_EDC_CNT*`, `regTD_EDC_CNT`, `regTA_EDC_CNT`, `regGE_EDC_CNT`, `regGL1_EDC_MODE`, `regSPI_EDC_MODE`, `regSQ_EDC_MODE`, `regTCP_EDC_MODE`, and related parity/control entries.
- `gfxdec0` render state families: `regDB_RENDER_CONTROL`, `regDB_DEPTH_VIEW*`, `regDB_RENDER_OVERRIDE*`, `regDB_DEPTH_SIZE_XY`, `regDB_Z_INFO`, `regDB_STENCIL_INFO`, DB read/write base registers, `regDB_DEPTH_CONTROL`, `regDB_STENCIL_CONTROL`, `regDB_EQAA`, `regDB_ALPHA_TO_MASK`, `regPA_SC_VPORT_*`, `regPA_CL_*`, `regVGT_*`, `regGE_*`, `regPA_SU_*`, `regPA_SC_*`, `regCB_COLOR*`, `regCB_BLEND*`, `regSX_*`, `regDB_HTILE_*`, `regCB_DCC_*`, and repeated viewport/scissor/window/clip color families.
- PF/VF and PF-only control families: `regPA_SC_SCREEN_EXTENT_*`, `regPA_SC_*_TRAP_SCREEN_*`, `regPA_SC_BINNER_*`, `regPA_SC_PRIM_FILTER_*`, `regSQ_WGP_*`, `regSQ_PERF_SNAPSHOT_*`, `regUTCL1_*`, `regTCP_*`, and `regSPI_RESOURCE_RESERVE_*`.
- GL1 cache controls: `regGL1C_GL1C_ADDR_MATCH_MASK`, `regGL1C_CNTL`, `regGL1C_STATUS`, `regGL1C_CTRL*`, `regGL1A_*`, `regGL1X_*`, `regGL1I_*`, `regGL1XC_*`, and `regGL1C_DEBUG`.
- Shader-engine CAC registers: `regSE_CAC_CNTL`, `regSE_CAC_STATUS`, `regSE_CAC_ACC_*`, `regSE_CAC_WEIGHT_*`, `regSE_CAC_IND_INDEX`, and `regSE_CAC_IND_DATA`.
- Performance data registers: `regGE2_SE_PERFCOUNTER*_LO/HI`, `regGRBMH_PERFCOUNTER*_LO/HI`, `regPA_SU_PERFCOUNTER*_LO/HI`, `regPA_SC_PERFCOUNTER*_LO/HI`, `regSPI_PERFCOUNTER*_LO/HI`, `regPC_PERFCOUNTER*_LO/HI`, `regSQ_PERFCOUNTER*_LO`, and `regSQG_PERFCOUNTER*_LO/HI`.

The `_BASE_IDX` values are part of the interface. In this chunk, early shader-engine block registers use base index `0`, while later large per-block/user/config/performance regions use base index `1`. SOC15 helper macros depend on that base index to compute the correct MMIO address for the selected GC instance.

## Control Flow

This header has no software control flow. Runtime sequencing lives in the AMDGPU and AMDKFD code that includes the generated register headers.

Observed direct GC 12 include users in this tree include:

- `drivers/gpu/drm/amd/amdgpu/gfx_v12_0.c`
- `drivers/gpu/drm/amd/amdgpu/gfxhub_v12_0.c`
- `drivers/gpu/drm/amd/amdgpu/gfxhub_v12_1.c`
- `drivers/gpu/drm/amd/amdgpu/mes_v12_0.c`
- `drivers/gpu/drm/amd/amdgpu/imu_v12_0.c`
- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v12.c`
- `drivers/gpu/drm/amd/amdgpu/soc24.c`
- `drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v12.c`
- `drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v12.c`

In those consumers, offset macros from this file are passed to SOC15 accessors and register-list helpers. Typical runtime flows that rely on this address metadata are:

- GFX bring-up and reset paths load GC 12 firmware, initialize RLC/CP/MEC/MES-related state, program golden registers, and access GC registers through `RREG32_SOC15`/`WREG32_SOC15`.
- Graphics command stream submission programs context registers that correspond to many `gfxdec0`, `gfxudec`, shader, DB/CB, PA/SC, VGT, SPI, and SQ offsets in this chunk.
- KFD and MES queue-management paths use GC 12 shader and queue register definitions, via the same generated namespace, to build and manage compute queues and MQDs.
- VM hub paths mostly use other regions of `gc_12_0_0_offset.h`, but they share the same offset/header scheme and base-index semantics.
- IMU/RLC golden-register programming references some offsets in this chunk directly; for example `imu_v12_0.c` programs `regRMI_GENERAL_CNTL` golden values.
- Performance-monitoring and diagnostics read the per-block performance counter data registers here after selection/configuration registers, some of which are in adjacent chunks.

The header does not encode ordering requirements. For example, it names render, cache, trap, invalidation, and performance-counter registers, but it does not say when to quiesce the GPU, which domains must be powered, whether a write is packet-only versus MMIO-safe, whether a register is read-only or write-one-to-clear, or which PF/VF entity is allowed to touch it.

## State And Persistence Behavior

The file persists no software state. It names hardware registers whose state persists according to GPU block lifetime: until explicit driver/firmware rewrite, command-stream context switch, golden-register restore, graphics reset, full GPU reset, power-gating loss, suspend/resume restore, or SR-IOV PF/VF ownership rules.

Important hardware state represented by this chunk includes:

- Shader program state: program base addresses, resource words, user-data SGPR mappings, checksums, request controls, late allocation, and shader accumulators for PS/GS/VS/HS.
- Graphics render context: depth/stencil/color buffer metadata, render overrides, viewport/scissor/window state, clip and guard-band state, primitive/rasterizer controls, blend controls, clear values, tile/compression metadata addresses, sample locations, binning and primitive filtering, and trap-screen windows.
- Cache and data-path state: TCP/GL1/UTCL1 invalidation/status/debug controls, texture address/data path controls, GL1 cache event controls, compression controls, and address configuration.
- Backend topology and routing: GB address/backend map registers, CB/DB hardware controls, backend disable state, RMI demux/xbar/scoreboard/status, and CID mapping.
- Reliability and accounting state: RAS/EDC counters, EDC modes, SE CAC accumulators and weights, SQ/SQC/TCP/SPI/TA/TD counters, and block-specific performance counters.
- Debug and trace state: SQ thread-trace user data, SQ wave/debug registers, SPI crawler/trap-screen registers, indirect debug selectors/data, and live wave counters.
- SR-IOV partitioned state: PF/VF-accessible state in `pfvf_*` blocks, plus privileged PF-only controls for SPI, UTCL1, TCP, and SE CAC.

Because this header only supplies offsets, it does not distinguish context-switched command-stream state from static golden registers or live status counters. Consumers must preserve those distinctions. Whole-register writes to status/debug/cache/control registers are especially sensitive because reserved bits, sticky status bits, self-clearing request bits, and firmware-owned fields are not marked in this file.

## Dependencies And Integration Points

The closest generated companion is `gc_12_0_0_sh_mask.h`, which defines bitfield shift/mask macros for the registers named here. Other generated companions in the same `asic_reg/gc` directory provide default values and additional register generations. Consumers depend on the spelling and numeric offsets in this file matching the GC 12.0.0 register database exactly.

Primary integration points:

- SOC15 register access: `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, and field helpers combine these `reg...` offsets with the GC hardware instance and base-index data.
- GFX v12 core driver: command processor, RLC, graphics-ring, shader-engine, golden-register, hang/reset, and debug paths include this header as part of the GC 12 register ABI.
- MES v12 and KFD v12: compute scheduling, MQD setup, queue management, and debug paths include the GC 12 masks and offsets to describe hardware queue/shader state.
- IMU/RLC initialization: golden-register tables can write offsets from this chunk, including RMI controls, during firmware-assisted setup.
- Graphics user-mode driver command streams: many `gfxdec0`/`gfxudec` registers are context or user/config registers normally written by packets generated outside the kernel, while the kernel still needs correct symbolic names for validation, debugging, reset dumps, and golden state.
- Performance and profiling: per-block `*_PERFCOUNTER*_LO/HI` registers integrate with the perf counter selection/control registers in adjacent chunks and with profiling tools that sample shader-engine counters.
- SR-IOV: `PFVF` and `PFONLY` address blocks make ownership explicit at the register-map level. Kernel code must honor PF/VF restrictions when adding direct MMIO programming.

The macros are syntactically just C preprocessor constants, so accidental cross-generation inclusion can still compile. The semantic dependency is the GC generation: using GC 12.0.0 offsets with another GC version's masks, defaults, or hardware can silently address the wrong register.

## Risks And Maintenance Notes

- Generated offset drift is high impact. A single wrong numeric offset can program an unrelated hardware register while compiling cleanly.
- The chunk boundaries are artificial. The start is the tail of a prior SPI block, and the end omits the `_BASE_IDX` for `regSQG_PERFCOUNTER7_LO`; the final per-file report must reconcile adjacent chunks before treating these families as complete.
- `_BASE_IDX` values are part of address calculation. Changing base index `0` versus `1` is as dangerous as changing the offset itself.
- This slice mixes live status, debug, command/context state, cache invalidation controls, trap controls, and performance counters. The header does not mark access direction, side effects, volatility, privilege, or synchronization requirements.
- Render state families are large and repetitive. Off-by-one errors in indexed families such as viewport transforms, scissor windows, CB color targets, blend controls, PS input controls, resource-reserve registers, or performance counters can produce slot-specific rendering or profiling failures.
- PF-only and PF/VF blocks need careful ownership checks under SR-IOV. A register name being available in the header does not imply that VF code may write it.
- Performance counter data registers in this chunk are only the data side of a larger mechanism. Selection, enable, freeze, and counter-reset controls are partly outside this range, so validation must include adjacent chunks.
- RAS/EDC and SE CAC registers are often tied to reliability, telemetry, and power/activity accounting. Uncoordinated writes can hide errors, perturb accounting, or conflict with firmware.
- Many `gfxdec0`/`gfxudec` registers are normally packet-programmed context state. Direct MMIO writes from kernel paths can race command submission unless the GPU is idle, reset, or otherwise synchronized.
- Debug/trap/thread-trace registers may expose or alter per-wave execution state. Reads and writes should be limited to debug flows that understand wave selection and trap-screen sequencing.

## Test Signals

Useful validation is mostly generated-data, build-time, and hardware-integration oriented:

- Preprocess/compile GC 12 paths that include `gc_12_0_0_offset.h` and `gc_12_0_0_sh_mask.h`: `gfx_v12_0.c`, `gfxhub_v12_0.c`, `gfxhub_v12_1.c`, `mes_v12_0.c`, `imu_v12_0.c`, `amdgpu_amdkfd_gfx_v12.c`, KFD v12 queue/MQD managers, and `soc24.c`.
- Static checks that every register offset in the full generated file has exactly one `_BASE_IDX` companion, with explicit chunk-boundary exceptions only during chunk-level research.
- Cross-check offset/header generation against the authoritative GC 12.0.0 register database, especially base-index transitions at address-block boundaries and repeated indexed families.
- Boot and resume GC 12.0.0 hardware with golden-register programming enabled; verify no register access faults, no early GPU hangs, and expected IMU/RLC programming of entries such as `regRMI_GENERAL_CNTL`.
- Run graphics workloads that exercise DB/CB/PA/SC/VGT/GE/SPI/SQ state: depth/stencil, blending, MSAA/EQAA, scissor/viewport arrays, tessellation, geometry shaders, transform feedback, primitive filtering, binning, and color/depth compression.
- Run compute/KFD/MES workloads that exercise SQ/SPI queue and shader-state programming, including context switches, preemption, queue teardown, and reset recovery.
- Validate cache and invalidation behavior with texture-heavy, render-to-texture, VRAM/system-memory, compression, and VM pressure workloads; watch for stale data, corruption, or hangs around TCP/GL1/UTCL1 controls.
- Exercise SR-IOV PF and VF configurations to confirm PF-only registers are not accessed from VF paths and PF/VF shared registers behave as expected.
- Run RAS/EDC injection or fault-observation tests where available, confirming GL1/SPI/SQ/SQC/TCP/TD/TA counters and modes report expected events.
- Sample performance counters for GE2, GRBMH, PA_SU, PA_SC, SPI, PC, SQ, and SQG while running known workloads; verify low/high pairing, freeze/reset sequencing, and counter selection from adjacent chunks.
- Use debugfs or driver register-dump paths during idle/reset/debug scenarios to ensure debug, trap, thread-trace, and indirect-data registers can be read without side effects outside the intended diagnostic windows.

## Chunk Notes For Merge

This document is source-tree aligned and covers only lines 7471-9953 of `gc_12_0_0_offset.h`. Adjacent chunks should provide the preceding SPI block context before `regSPI_LB_DATA_PERWGP_WAVE_PS` and the continuation after `regSQG_PERFCOUNTER7_LO`, beginning with its missing `_BASE_IDX` and the rest of the SQG/performance-counter region. The final per-file report should treat `gc_12_0_0_offset.h` as generated GC 12.0.0 register-address metadata consumed by AMDGPU GFX, VM hub, MES, KFD, IMU/RLC, debug, SR-IOV, and performance-monitoring paths.
