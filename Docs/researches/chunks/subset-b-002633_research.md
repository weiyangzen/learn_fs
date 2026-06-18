# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 2408-4822

## Purpose

This chunk is generated AMD GC 9.1 register bitfield metadata. It contains no executable C code; it publishes preprocessor `__SHIFT` and `_MASK` constants used by AMDGPU, AMDKFD, display, power-management, debug, RAS, and profiling paths to compose or decode MMIO register values for a GFX9/GC 9.1-class graphics block. The matching register addresses live in the companion GC 9.1 offset namespace, and many consumers in this tree also use the same field names through the broader GFX9 register include set.

The selected range covers the tail of SQC EDC counter definitions, a large SQ instruction and resource-descriptor encoding block, SQ indirect access and command fields, SQ lightweight/performance counters, SQ EDC and thread-trace token layouts, SQC instruction/data UTCL1 controls and status bits, then address blocks for `gc_shsdec`, `gc_tpdec`, `gc_gdsdec`, and the start of `gc_rbdec`. Concretely, the block spans shader/SQ instruction formats, buffer/image/sampler resource descriptors, scratch and wave execution state, SPI wavefront lifetime/debug/trap controls, texture data/address unit controls, GDS status/protection/EDC controls, depth-buffer/debug/cache/DFSM controls, color/render-backend redundancy, and graphics backend address configuration.

Although this repository subtree is under `ceph-client`, this file is AMD GPU driver hardware metadata, not Ceph filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, memory allocations, or direct I/O operations in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit of a hardware register field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register mask for that field.
- Consumers normally combine these with `mm*` or `reg*` register offsets and helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

Major register groups in this chunk:

- `SQC_EDC_CNT2` tail and `SQC_EDC_CNT3`: instruction/data SQC bank A/B ECC/EDC counters for tag RAMs, bank RAMs, UTCL1 miss FIFOs, hit/miss FIFOs, dirty-bit RAM, and UTCL1 LFIFO SEC/DED counters. The chunk starts after the first `SQC_EDC_CNT2` shift fields, so the full register definition depends on the preceding chunk.
- `SQ_REG_TIMESTAMP`, `SQ_CMD_TIMESTAMP`, `SQ_TIME_HI`, and `SQ_TIME_LO`: timestamp/time fields used by SQ debug, command, and tracing flows.
- `SQ_IND_INDEX` and `SQ_IND_DATA`: indirect SQ register access selection and payload fields, including wave, SIMD, thread, auto-increment, forced read, timeout, unindexed mode, and index fields.
- `SQ_CMD`: shader-queue command fields including command, mode, VMID check, data, wave ID, SIMD ID, queue ID, and VM ID. Comparable GFX paths use this to issue soft recovery commands targeting a VMID.
- `SQ_DS_*`, `SQ_EXP_*`, `SQ_FLAT_*`, `SQ_GLBL_*`, `SQ_MIMG_*`, `SQ_MTBUF_*`, `SQ_MUBUF_*`, `SQ_SCRATCH_*`, `SQ_SMEM_*`, `SQ_SOP*`, `SQ_VINTRP`, `SQ_VOP*`, `SQ_VOP_DPP`, and `SQ_VOP_SDWA*`: generated field layouts for instruction encodings. These describe operand registers, offsets, opcodes, cache control flags, segment selectors, data formats, destination selectors, modifiers, encodings, and SDWA/DPP-specific controls.
- `SQ_LB_CTR_*` and `SQ_LB_DATA*`: SQ lightweight counter control, event selection, per-CU masks, and counter data readback fields.
- `SQ_EDC_SEC_CNT`, `SQ_EDC_DED_CNT`, `SQ_EDC_INFO`, `SQ_EDC_CNT`, and `SQ_EDC_FUE_CNTL`: SQ EDC status/counter fields for LDS, SGPR, VGPR, source/VMID/wave metadata, and fatal uncorrectable error interrupt/block controls.
- `SQ_THREAD_TRACE_WORD_*`: hardware thread-trace token layouts for common/event/instruction/PC/userdata/issue/misc/perf/register/timestamp/wave/wave-start records. These fields decode token type, time deltas, shader/CU/SIMD/wave identity, register access metadata, instruction issue slots, counters, PCs, userdata, and threadgroup IDs.
- `SQ_WREXEC_EXEC_*`, `SQ_BUF_RSRC_WORD*`, `SQ_IMG_RSRC_WORD*`, `SQ_IMG_SAMP_WORD*`, `SQ_FLAT_SCRATCH_WORD*`, and `SQ_M0_GPR_IDX_WORD`: buffer, image, sampler, scratch, WREXEC, and relative-index descriptor fields. These encode GPU virtual addresses, record counts, strides, data/number formats, swizzle and cache properties, metadata addresses, compression, sampler clamp/filter/LOD behavior, border color, and relative operand controls.
- `SQC_ICACHE_UTCL1_CNTL*`, `SQC_DCACHE_UTCL1_CNTL*`, `SQC_ICACHE_UTCL1_STATUS`, and `SQC_DCACHE_UTCL1_STATUS`: SQC instruction/data cache UTCL1 controls for GPUVM response behavior, permission/fault modes, client IDs, LFIFO behavior, VMID invalidation, force-miss/in-order modes, EDC disable, GPUVM invalidation mode, snooping, performance-event filtering, fragment forcing, and fault/retry/PRT status.
- `SX_DEBUG_1`: SX-to-DB credit and blend/pixel optimization debug controls.
- `SPI_*`: shader processor interpolation/control registers covering PS max wave IDs, start phases, graphics reset counts, DSM and EDC controls, pixel-shader CU enable masks, wavefront lifetime sampling/limits/status for slots 0-20, SPI lightweight counters and per-CU wave data, static CU masks, GDS credits, SX export/scoreboard buffer sizes, CSQ active wavefront counts, and per-process trap-screen memory base/mask/GPR minima.
- `TD_*` and `TA_*`: texture data/address block controls and status. These include texture data precision/rounding/power/stall compatibility controls, TD DSM/error-injection/scratch/status fields, TA credits, auxiliary determinism and sampler behavior controls, busy status bits, and scratch fields.
- `GDS_*`: global data share configuration, busy/status fields, enhanced mode bits, protection fault and VM protection fault metadata, EDC counters for GDS memory/input queues/GRBM/onion-access paths, DSM/error-injection controls, watchdog counter, and physical/pipe EDC counters.
- `DB_*`: depth buffer debug and resource-control fields. These cover depth/stencil compression/debug reads, HiZ/HiS behavior, fast Z/stencil and culling disables, cache-force/miss/stall options, viewport and resummarization controls, over-rasterization/context-suspend fixes, credit limits, watermarks, subtile MSAA layout fields, free cacheline depths, FIFO depths, exception panic-disable controls, ring-counter controls, RMI cache policies, DFSM configuration/watermarks/in-flight limits/watchdog/flush events.
- `CC_RB_REDUNDANCY` and `CC_RB_BACKEND_DISABLE`: render-backend failure/redundancy enable and backend disable masks.
- `GB_ADDR_CONFIG` and `GB_BACKEND_MAP`: graphics backend/tile addressing configuration and backend mapping fields. `GB_ADDR_CONFIG` exposes pipe count, pipe interleave, compressed fragments, bank interleave/count, shader-engine tile size, shader-engine count, GPU count, multi-GPU tile size, RBs per shader engine, row size, lower-pipe count, and shader-engine enable. The chunk ends with only the `GB_GPU_ID` section comment; the `GB_GPU_ID` fields are in the next chunk.

Fields named `RESERVED`, `UNUSED`, `Unused`, or full-width `DATA` are still part of the generated hardware contract. They should not be interpreted as permission for arbitrary whole-register writes; consumers need the programming guide, reset values, and existing read-modify-write patterns.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from driver code that includes the generated GC/GFX register headers:

1. A consumer selects a GFX/GC register address from an offset header or an `mm*`/`reg*` macro.
2. It composes a register value with `REG_SET_FIELD`, decodes a register value with `REG_GET_FIELD`, or supplies a mask/value pair to golden-register programming.
3. AMDGPU register helpers perform MMIO reads/writes or ring-packet emission while the owning initialization, reset, queue, VM, profiling, display, RAS, or interrupt path handles ordering.

Observed integration examples in this tree include `gfx_v9_0.c` golden-register tables for GC 9.1 programming `DB_DEBUG2`, `GB_GPU_ID`, `TA_CNTL_AUX`, `TD_CNTL`, `GB_ADDR_CONFIG`, and `GB_ADDR_CONFIG_READ`; `gfx_v9_0_gpu_early_init()` decoding `GB_ADDR_CONFIG` fields into `adev->gfx.config.gb_addr_config_fields`; older and newer GFX soft-recovery paths composing `SQ_CMD` with `CMD`, `MODE`, `CHECK_VMID`, and `VM_ID`; and display code reading `GB_ADDR_CONFIG` to derive tiling/modifier pipe properties. RAS-related GFX9 code also defines sub-block coverage for SQ/SQC/TD/GDS-like EDC domains represented by this macro family.

The chunk describes field positions only. It does not encode legal access order, read/write permissions, self-clearing behavior, golden-setting values, firmware ownership, GRBM broadcast/indexing requirements, power-gating constraints, or whether a status/counter bit is sticky, clear-on-read, clear-on-write, or live.

## State And Persistence Behavior

The file stores no software state and persists nothing. It defines names for hardware state inside a GC 9.1 graphics block.

The represented hardware state includes:

- Shader instruction and descriptor ABI state: instruction encodings, scalar/vector operands, memory op flags, image/buffer/sampler resource descriptors, scratch descriptors, and relative indexing state.
- SQ debug/recovery state: SQ indirect register access, targeted SQ commands by wave/SIMD/queue/VMID, timestamps, WREXEC execution address fields, and soft-recovery command inputs.
- Profiling and trace state: SQ/SPI lightweight counters, per-CU masks, counter data registers, thread-trace token payloads, timestamp words, issue-token fields, performance counter token fields, register-access trace fields, and wave-start metadata.
- Error-detection state: SQC/SQ/SPI/GDS EDC counters, SEC/DED summaries, fatal uncorrectable error controls, EDC source metadata, TD/GDS/SPI DSM and error-injection controls, and instruction/data UTCL1 fault/retry/PRT status.
- Translation/cache state: SQC I-cache/D-cache UTCL1 behavior for response/fault modes, VMID invalidation, snooping, force-miss, cache-size/FIFO reductions, GPUVM invalidation acknowledgement, and performance-event VMID/read-write filters.
- Shader processor state: SPI CU masks, PS wave limits, start phases, trap-screen base/mask ranges, GDS credits, export/scoreboard buffer sizing, CSQ activity counters, and lifetime warning/status slots.
- Texture state: TD/TA credit, determinism, filtering, rounding, stall, scratch, DSM, and busy-status controls.
- GDS state: configuration, busy/status bits, GDS/GWS/OA/VM protection fault metadata, EDC counters, DSM/error-injection knobs, and watchdog state.
- Depth/render backend state: DB debug knobs, cache and FIFO depths, watermarks, subtile layout for MSAA modes, DFSM controls, panic-disable bits, RMI cache policy for depth/stencil/HTILE and color metadata traffic, render-backend disable/redundancy, backend mapping, and backend address configuration.

Persistence is hardware-defined. Some fields are configuration programmed during ASIC init, golden-register setup, queue setup, profiling setup, or debug enablement and persist until reset, suspend/resume, power-gating, or reinitialization. Others are live counters, status bits, error latches, trace-token decoders, interrupt/debug readbacks, or write-trigger controls. The macros alone do not identify volatility or side effects, so driver code must preserve unrelated bits and follow ASIC-specific sequencing.

## Dependencies And Integration Points

The closest companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_offset.h`, which provides register offsets for this ASIC family. In the current tree, `psp_v10_0.c` directly includes `gc/gc_9_1_offset.h`, while the main GFX9 driver code in `gfx_v9_0.c` uses GFX9 `mm*` names and common SOC15 helpers to program GC 9.1 hardware variants.

Important integration points:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c`: GC 9.1 golden-register tables, GFX early init, `GB_ADDR_CONFIG` decoding, DB/TA/TD programming, and RAS registration/query/reset/error-injection plumbing.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v8_0.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c`: related-generation examples of `SQ_CMD` composition for ring soft recovery, showing how the SQ command bitfield convention is consumed.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_plane.c`: display modifier code reads `GB_ADDR_CONFIG` fields in newer GFX paths to derive tiling pipe/picker properties; GC 9.1 uses related `GB_ADDR_CONFIG` semantics for GFX9 tiling calculations.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/*`: KFD interrupt and trap-handler code consumes SQ interrupt/resource descriptor conventions adjacent to these SQ/SPI definitions, especially for wave identity, trap/debug, and buffer resource metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_powertune.c`: power-management paths manipulate GFX EDC/GRBM-indexed blocks, which makes SQC/SQ/SPI/TD/DB EDC and debug field correctness relevant to power and error handling.

The generated masks integrate with AMDGPU register-access abstraction, GRBM broadcast/indexing, golden settings, firmware/RLC-owned initialization, PM4/ring emission, KFD queue/trap handling, GPU reset/recovery, display tiling metadata, RAS counters, and profiling/thread-trace tooling. Address-block comments in this chunk identify the hardware decoder regions: pre-existing SQ/SQC blocks, `gc_shsdec`, `gc_tpdec`, `gc_gdsdec`, and `gc_rbdec`.

## Risks And Edge Cases

- Header/offset mismatches are the primary correctness risk. `gc_9_1_sh_mask.h` field layouts must be paired with the matching GC 9.1 offsets or compatible GFX9 register names; using another GC generation can compile while programming the wrong bits.
- The chunk boundary is artificial. It starts in the middle of `SQC_EDC_CNT2` and ends at the `GB_GPU_ID` section comment without the field definitions. Adjacent chunks are required for complete per-register coverage.
- These macros are untyped constants. A wrong register/field pairing can silently corrupt shader descriptors, SQ commands, SQC cache controls, trace decoding, GDS protection status, DB cache policy, or backend tiling configuration.
- SQ instruction and descriptor fields are compiler/ABI sensitive. Incorrect resource-word packing, image/sampler metadata, scratch size/offset, or memory-op flags can cause invalid shader execution, memory faults, data corruption, or hangs.
- `SQ_CMD` fields are recovery/debug sensitive. Targeting the wrong VMID, SIMD, queue, or wave can fail to recover the intended ring or disturb unrelated work.
- Thread-trace token layouts are decode-only metadata in many consumers. If masks drift, trace tools may produce plausible but wrong wave, PC, counter, or register-access data.
- SQC UTCL1 controls include invalidation, fault-response, snoop, VMID, and force-miss behavior. Bad values can create stale translations, excessive misses, missed fault reporting, or workloads that hang under GPUVM pressure.
- EDC, DSM, and error-injection fields must be treated carefully. Enabling injection, disabling EDC, clearing counters, or interpreting SEC/DED summaries without block-specific sequencing can hide real RAS events or create artificial faults.
- SPI wavefront lifetime, trap-screen, CU-mask, and CSQ active-count registers affect scheduling/debug visibility. Wrong masks can lose traps, misattribute wavefronts, or disable intended CUs.
- TA/TD determinism, filtering, rounding, and stall controls can change texture sampling behavior or performance. Carrying assumptions from adjacent GFX generations is risky because subtle field differences are common in generated ASIC headers.
- GDS protection fault fields carry security- and isolation-relevant metadata such as VMID, TMZ, OA/GWS, write/read direction, and address fragments. Incorrect decoding can misdiagnose process isolation failures.
- DB debug and DFSM controls are performance and correctness sensitive. Disabling fast Z/stencil paths, resummarization, coherency stalls, or cache policies can produce rendering artifacts or severe performance regressions.
- `GB_ADDR_CONFIG` drives tiling and memory-layout interpretation. Incorrect pipe/bank/RB/SE/row-size decoding can break display modifiers, DCC, render backend mapping, scanout compatibility, or memory swizzle calculations.
- Reserved and unused fields should be preserved unless a hardware programming sequence explicitly supplies reset/golden values.

## Test Signals

Useful validation is mostly build coverage, generated-header consistency, and hardware smoke/stress coverage:

- Build AMDGPU/KFD/display paths that use GFX9/GC 9.1 register headers, especially `gfx_v9_0.c`, PSP GC 9.1 offset users, KFD interrupt/trap code, and display tiling/modifier paths.
- Generated-header consistency checks that every field in this line range has the expected shift/mask pair, repeated lifetime-status and counter layouts are regular, and the fields have matching register offsets in the relevant GC/GFX9 offset headers.
- Golden-register programming tests on GC 9.1/Raven-class hardware confirming `DB_DEBUG2`, `GB_GPU_ID`, `TA_CNTL_AUX`, `TD_CNTL`, `GB_ADDR_CONFIG`, and `GB_ADDR_CONFIG_READ` are programmed with expected mask/value pairs and survive resume/reset as intended.
- GFX early-init tests that decode `GB_ADDR_CONFIG` into pipe, bank, compressed-fragment, RB-per-SE, shader-engine, and pipe-interleave fields and compare against known ASIC/VBIOS topology.
- Ring recovery tests that trigger soft recovery and confirm `SQ_CMD` VMID-targeted commands do not disturb unrelated queues.
- Shader and compute smoke tests exercising buffer/image/sampler descriptors, scratch access, flat/global/scratch memory instructions, scalar/vector instruction encodings, wave32/64 behavior where applicable, and trap/debug modes.
- Thread-trace/profiling tests that enable SQ/SPI lightweight counters and thread trace, run known workloads, and verify token decode fields, timestamps, wave IDs, CU/SIMD IDs, PCs, register events, and counter payloads are plausible.
- SQC cache/VM tests that issue VMID invalidations, force fault/retry/PRT scenarios, and verify instruction/data UTCL1 status and invalidation behavior under GPUVM stress.
- RAS tests for SQ/SQC/SPI/TD/GDS/DB-related EDC counters, including SEC/DED count changes, source metadata, query/reset paths, and error-injection guardrails where supported.
- Texture and sampler conformance tests for TA/TD controls, especially filtering, LOD, anisotropy, determinism, rounding, and busy/stall behavior.
- GDS protection tests that exercise GDS/GWS/OA accesses under multiple VMIDs, validate protection fault metadata, and confirm TMZ/VM isolation behavior.
- Depth/render tests covering fast Z/stencil, HTILE, DCC/metadata traffic, MSAA subtile layouts, DB cache policies, DFSM flushing, and backend disable/redundancy handling.
- Regression indicators include valid workloads producing SQ/SQC/UTCL1 faults, missing expected GPUVM faults, corrupted trace decode, stuck counters, incorrect display modifiers or tiling, rendering artifacts in depth/stencil workloads, GDS protection faults with wrong VMID/address data, RAS counter drift, and ring timeouts during recovery.
