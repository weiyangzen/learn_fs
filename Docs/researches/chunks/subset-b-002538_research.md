# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 29639-32347

## Purpose

This chunk is generated AMD GC 11.0.3 register bitfield metadata. It contains no executable C code; it exports preprocessor constants that describe the `SHIFT` and `MASK` layout of 32-bit graphics-core MMIO registers. Runtime driver code combines these constants with the matching address definitions from `gc_11_0_3_offset.h` and helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and table-driven golden-register writers.

The selected range starts in the `CP_ME_COHER_CNTL` field family, then covers graphics frontend, primitive assembly, shader, line/stipple/trap-screen, SQ trace userdata, GDS atomic/GWS/OA/streamout counters, SPI controls, a large `gc_cprs64dec` command-processor RS64/MES/MEC/GFX register block, `gc_gl1dec`, `gc_chdec`, and the start of `gc_gl2dec`. The chunk ends at line 32347 in the middle of `GL2C_CM_CTRL2`; later lines contain the remaining masks for that register and the following GL2C registers.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, allocation sites, or C control structures in this slice. The API is the generated macro contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit used to encode or extract a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for the same field.
- Register comments such as `//CP_MES_CNTL` and address-block comments such as `// addressBlock: gc_cprs64dec` group the macros by hardware register and decode block.

Major register families in this chunk:

- CP coherency and indexed draw setup: `CP_ME_COHER_CNTL`, `CP_ME_COHER_SIZE(_HI)`, `CP_ME_COHER_BASE(_HI)`, and `CP_ME_COHER_STATUS` describe CP ME cache/coherency operation ranges and destination-base enable bits for CB/DB/general destinations. `GRBM_GFX_INDEX` exposes instance, SA, and SE selection plus broadcast-write bits used by per-instance register programming.
- Geometry/frontend setup: `VGT_PRIMITIVE_TYPE`, `VGT_INDEX_TYPE`, `GE_MIN_VTX_INDX`, `GE_MAX_VTX_INDX`, `GE_INDX_OFFSET`, `GE_MULTI_PRIM_IB_RESET_EN`, `VGT_NUM_INDICES`, `VGT_NUM_INSTANCES`, `VGT_TF_RING_SIZE`, `VGT_HS_OFFCHIP_PARAM`, `VGT_TF_MEMORY_BASE(_HI)`, `VGT_INSTANCE_BASE_ID`, `GE_CNTL`, `GE_USER_VGPR1..3`, `GE_USER_VGPR_EN`, `GE_STEREO_CNTL`, `GE_PC_ALLOC`, `GE_GS_FAST_LAUNCH_WG_DIM(_1)`, and `VGT_GS_OUT_PRIM_TYPE` describe draw index bounds, tessellation/transform-feedback memory, primitive-group/subgroup sizing, stereo/view controls, and optional user VGPR payloads.
- Raster/trap/screen and shader debug: `PA_SU_LINE_STIPPLE_VALUE`, `PA_SC_LINE_STIPPLE_STATE`, `PA_SC_SCREEN_EXTENT_MIN/MAX`, P3D/HP3D/plain trap-screen enable/coordinate/count registers, `SQ_THREAD_TRACE_USERDATA_0..7`, `SQC_CACHES`, and `TA_CS_BC_BASE_ADDR(_HI)` provide line stipple state, screen extents, trap-screen diagnostics, shader thread-trace userdata, SQC cache validity/busy bits, and texture address base fields.
- GDS, GWS, OA, atomics, and streamout: `DB_OCCLUSION_COUNT*`, `GDS_RD_*`, `GDS_WR_*`, `GDS_WRITE_COMPLETE`, `GDS_ATOM_*`, `GDS_GWS_RESOURCE_CNTL`, `GDS_GWS_RESOURCE`, `GDS_GWS_RESOURCE_CNT`, `GDS_OA_*`, `GDS_STRMOUT_DWORDS_WRITTEN_*`, `GDS_GS_*`, and `GDS_STRMOUT_PRIMS_NEEDED/WRITTEN_*` define low-level GDS read/write windows, atomic operand/result registers, global-wave-sync resource allocation fields, ordered-append ring/counter fields, and streamout statistics.
- SPI controls: `SPI_CONFIG_CNTL`, `SPI_CONFIG_CNTL_1`, `SPI_CONFIG_CNTL_2`, `SPI_WAVE_LIMIT_CNTL`, `SPI_GS_THROTTLE_CNTL1/2`, `SPI_ATTRIBUTE_RING_BASE`, and `SPI_ATTRIBUTE_RING_SIZE` describe shader-processor interface behavior including export/GS throttle limits, wave limits, interpolation and parameter-cache policy, LDS/CU grouping, attribute-ring address/size, and related workaround or clock/perf controls.
- `gc_cprs64dec`: this is the densest block. It defines RS64/MES/MEC/GFX command-processor control and debug fields, including program-counter starts, interrupt/vector addresses, machine-status/cause/bad-address/IP/cycle/time/instret identity-style registers, scratch index/data, instruction pointers, icache and dcache operation controls, pipe priorities and process quantum, doorbell controls, general-purpose registers, local/instruction/scratch aperture base/mask/control registers, perf counters, pending interrupts, interrupt data slots, and 16 dcache aperture base/mask/control triplets for MES, MEC, and GFX RS64 paths.
- MES and MEC control highlights: `CP_MES_CNTL` and `CP_MEC_RS64_CNTL` contain invalidate-icache, pipe reset, pipe active, halt, and step fields. `CP_MES_DC_OP_CNTL`, `CP_MEC_DC_OP_CNTL`, and `CP_GFX_RS64_DC_OP_CNTL` expose dcache invalidate, completion, bypass, and in the GFX RS64 case volatile/writeback control bits. `CP_MES_DOORBELL_CONTROL1..6` expose doorbell offset/enabled/hit bits for scheduling and queue wakeup.
- GFX RS64-specific fields: `CP_GFX_CNTL`, `CP_GFX_RS64_INTERRUPT0/1`, `CP_GFX_RS64_INTR_EN0/1`, paired `MIP`, `MTIMECMP`, GP, instruction-pointer, pending-interrupt, and dcache aperture families describe two GFX RS64 contexts/lanes plus their local memory windows and interrupt state.
- `gc_gl1dec`: `GL1_ARB_CTRL`, `GL1_DRAM_BURST_MASK`, `GL1_ARB_STATUS`, `GL1_DRAM_BURST_CTRL`, `GL1I_GL1R_REP_FGCG_OVERRIDE`, `GL1C_CTRL`, `GL1C_STATUS`, `GL1C_UTCL0_CNTL2`, `GL1C_UTCL0_STATUS`, `GL1C_UTCL0_RETRY`, and `GL1C_CTRL2` describe GL1 arbitration, burst policy, fine-grain clock-gating overrides, GL1 cache force-hit/miss/no-fill modes, GL2 request/data credits, tag/tracker/FIFO busy and stall diagnostics, UTCL0 fault/retry/PRT state, snoop/burst/big-page behavior, and inflight limits.
- `gc_chdec`: `CH_ARB_CTRL`, `CH_DRAM_BURST_MASK`, `CH_ARB_STATUS`, `CH_DRAM_BURST_CTRL`, `CHA_CHC_CREDITS`, `CHA_CLIENT_FREE_DELAY`, `CHI_CHR_REP_FGCG_OVERRIDE`, `CH_VC5_ENABLE`, `CHC_CTRL`, `CHC_STATUS`, `CHCG_CTRL`, and `CHCG_STATUS` describe channel-hub arbitration, memory/IO burst-gather policy, client/free-delay knobs, virtual-channel enablement, clock-gating overrides, request/data credits, virtual FIFO and tracker stalls, and VC0/VC1 busy/full status.
- `gc_gl2dec` start: `GL2C_CTRL`, `GL2C_CTRL2`, `GL2C_STATUS`, `GL2C_ADDR_MATCH_MASK`, `GL2C_ADDR_MATCH_SIZE`, `GL2C_WBINVL2`, `GL2C_SOFT_RESET`, `GL2C_CM_CTRL0`, `GL2C_CM_CTRL1`, `GL2C_CM_STALL`, and the first part of `GL2C_CM_CTRL2` cover L2 cache sizing, writeback and latency FIFOs, metadata/compression cache behavior, hit-under-miss/probe/fill policy, writeback/invalidate status, soft reset, address-match filtering, compression-manager hash/burst/recompression controls, and the beginning of partial-write/VRS/DCC-error-detection controls.

## Control Flow

This header has no direct runtime control flow. Its indirect operational flow is:

1. A GC 11.0.3 driver file includes `gc/gc_11_0_3_offset.h` and `gc/gc_11_0_3_sh_mask.h`.
2. The driver selects a register address from the offset header, for example `regGRBM_GFX_INDEX`, `regCP_MES_CNTL`, `regCP_MEC_RS64_CNTL`, `regCP_GFX_RS64_DC_OP_CNTL`, `regGL1C_CTRL`, or `regGL2C_CTRL2`.
3. The driver composes or decodes a value using these field masks through `REG_SET_FIELD`, `REG_GET_FIELD`, or table masks.
4. The value is sent to hardware through SOC15 register access, IMU/RLC RAM programming, MES scheduling setup, KFD queue management, GFX reset, cache invalidation, or diagnostic paths.

Observed integration in this source tree includes `amdgpu/gfx_v11_0_3.c`, `amdgpu/imu_v11_0_3.c`, and `amdgpu/gfxhub_v3_0_3.c` including this exact GC 11.0.3 mask header. Shared GC 11 paths such as `amdgpu/gfx_v11_0.c`, `amdgpu/mes_v11_0.c`, and `amdgpu/amdgpu_amdkfd_gfx_v11.c` show how the same macro families are used: `GRBM_GFX_INDEX` selects SE/SA/instance routing, `CP_MES_CNTL` starts/stops and resets MES pipes, `CP_MEC_RS64_CNTL` resets/halt/activates MEC pipes, and `CP_GFX_RS64_DC_OP_CNTL` drives dcache invalidation with polling for completion.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It describes hardware-visible register state. Persistence, latching, read-only/write-only behavior, and self-clearing behavior are defined by the GPU hardware and by the driver sequences that use these macros.

The represented hardware state includes CP coherency operation ranges, selected graphics instances through `GRBM_GFX_INDEX`, frontend draw parameters, GE/VGT/tessellation and transform-feedback state, raster/trap-screen diagnostics, SQ trace userdata, SQC cache state, GDS/GWS/OA resources and counters, streamout counters, SPI throttle and attribute-ring state, MES/MEC/GFX RS64 program counters, machine and interrupt state, pipe reset/active/halt state, doorbell hit/enables, local memory aperture mappings, dcache/icache operation bits, GL1/CH/GL2 cache and fabric arbitration configuration, busy/stall status bits, and compression-manager policy.

Some fields are persistent configuration until reset or reprogramming, such as aperture bases/masks, cache policy, burst controls, pipe priorities, and GL1/GL2 cache sizing. Others are live or sticky status, such as `*_STATUS` busy/stall flags, doorbell hit bits, timer-expired bits, dcache invalidate completion bits, GDS write-complete flags, and counter registers. Some are command-like strobes or self-clearing control bits, including cache invalidation, writeback/invalidate, soft reset, pipe reset, and error-status clear controls. This generated header does not encode those semantics, so consumers must preserve reserved/unrelated bits and follow the ASIC-specific sequencing in the owning driver code.

## Dependencies And Integration Points

The immediate companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h`, which supplies the `reg*` addresses and base indices for the same register names. Reset/default values are supplied by sibling generated default headers and by golden-register tables.

Important integration points:

- `amdgpu/gfx_v11_0_3.c` includes this header for GC 11.0.3-specific GFX/RAS handling. The file reads RLC FED status registers and uses `REG_GET_FIELD`, demonstrating the expected field-decoding contract for this ASIC.
- `amdgpu/imu_v11_0_3.c` includes this header and programs an IMU/RLC RAM golden table. The table includes neighboring GC registers such as GCEA, GCVM, GB, and PSP-debug entries; this chunk's GL/CP/GDS/SPI fields use the same mask/address pairing mechanism.
- `amdgpu/gfxhub_v3_0_3.c` includes the same GC 11.0.3 headers for GFXHUB VM/cache setup. Although many VM fields live outside this chunk, it depends on the same generated-mask namespace.
- `amdgpu/gfx_v11_0.c` uses `GRBM_GFX_INDEX` field macros to select shader engines/arrays/instances, `CP_GFX_RS64_DC_OP_CNTL` to invalidate GFX RS64 dcache, and `CP_MEC_RS64_CNTL` to reset, halt, and activate MEC pipes.
- `amdgpu/mes_v11_0.c` uses `CP_MES_CNTL` field macros when loading, activating, halting, and resetting MES firmware pipes.
- `amdgpu/amdgpu_amdkfd_gfx_v11.c` uses `GRBM_GFX_INDEX` to steer KFD/compute register access to the desired SE/SA/instance.
- Hardware or firmware validation tooling can also consume the generated `SHIFT`/`MASK` pairs to compare against register databases, decode dumps, and validate golden settings.

## Risks And Edge Cases

- Header/offset mismatch is high risk. These GC 11.0.3 masks must be paired with the matching GC 11.0.3 offset/default definitions; cross-generation names often look similar while field positions differ.
- The chunk boundary is artificial. It begins after `CP_ME_COHER_CNTL__DEST_BASE_0_ENA__SHIFT` and ends before the remaining `GL2C_CM_CTRL2` masks, so the final per-file merge must reconcile adjacent chunks before describing those registers as complete.
- Dense control registers such as `CP_MES_CNTL`, `CP_MEC_RS64_CNTL`, `CP_GFX_RS64_DC_OP_CNTL`, `SPI_CONFIG_CNTL_1`, `GL1C_CTRL`, `CHC_CTRL`, and `GL2C_CTRL2` mix command, status, reset, clock-gating, cache, and workaround bits. A wrong shift or mask can reset the wrong pipe, leave firmware halted, break cache invalidation, corrupt attribute-ring setup, or change fabric/cache policy.
- Repeated register families are vulnerable to copy or generation errors. The MES/MEC/GFX RS64 GP registers, interrupt data slots, local aperture triplets, and `CP_*_DC_APERTURE0..15_*` families must remain internally consistent.
- Visible `SPARE`, `UNUSED`, `CHICKEN_BITS`, and full-width masks do not mean arbitrary writes are safe. Consumers need reset-default masks and read-modify-write discipline to avoid reserved or debug-only bits.
- `GRBM_GFX_INDEX` controls register broadcast versus targeted instance writes. Misprogramming it can accidentally broadcast a per-instance operation or only update one SE/SA/instance, causing asymmetric state and hard-to-debug hangs or performance anomalies.
- Cache/fabric status fields can be live and timing-sensitive. Polling `GL1C_STATUS`, `CHC_STATUS`, `CHCG_STATUS`, `GL2C_STATUS`, or dcache completion bits needs proper timeouts and reset handling in consumers.
- GDS/GWS/OA and streamout counters are attribution-sensitive. Misdecoded masks can report incorrect resource ownership, wrong atomic operand/result data, or misleading streamout/occlusion counts.
- GL2 compression-manager fields affect DCC/recompression/partial-write behavior. Incorrect use of the partial `GL2C_CM_CTRL2` fields visible in this chunk can surface as DCC corruption, VRS regressions, stale metadata, or performance cliffs.

## Test Signals

Useful validation is mostly generated-header consistency, build coverage, and hardware integration:

- Build AMDGPU, AMDKFD, MES, IMU, GFXHUB, and display paths that include `gc_11_0_3_sh_mask.h` with `gc_11_0_3_offset.h`.
- Generated-header checks should verify every visible `__SHIFT` has its intended `_MASK`, masks align with shifts, register field masks do not overlap except documented aliases/full-register fields, and register names have matching offsets in `gc_11_0_3_offset.h`.
- Static comparison against the authoritative GC 11.0.3 register database should focus on repeated CP RS64 aperture families, doorbell controls, pipe-control bits, GL1/CH/GL2 cache controls, and the partial `GL2C_CM_CTRL2` boundary.
- MES firmware load/start/stop/reset tests should exercise `CP_MES_CNTL`, doorbell controls, process quantum, interrupt, scratch, and program-counter fields.
- GFX reset and queue tests should exercise `CP_MEC_RS64_CNTL`, `CP_GFX_RS64_DC_OP_CNTL`, local aperture setup, icache/dcache invalidation, and polling for invalidate completion.
- KFD compute queue tests should cover `GRBM_GFX_INDEX` instance steering and GDS/GWS resource behavior under multi-SE/SA configurations.
- Graphics tests should stress indexed draws, primitive restart, tessellation, transform feedback, stereo, line stipple, screen extents, GS fast launch, SPI wave throttling, and attribute-ring programming.
- Cache/fabric tests should inspect GL1, CH, and GL2 busy/stall counters and status after reset, suspend/resume, heavy memory traffic, metadata/DCC workloads, writeback/invalidate, and soft reset sequences.
- Debug and reliability tests should validate occlusion/streamout counters, SQ thread trace userdata, GDS atomics/OA behavior, and fault/status decoding without writing reserved or debug-only fields in production paths.
