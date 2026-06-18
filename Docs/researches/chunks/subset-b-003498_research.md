# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc21_enum.h lines 15194-21030

## Scope

This chunk is a generated AMDGPU SOC21 enum/value slice. It starts inside the tail of `SPI_PERFCNT_SEL`, then covers complete enum and value sections for shader processor input/output, shader queue, geometry engine, vertex grouper/tessellator, graphics block/global register bus manager, command processor, shader export, depth buffer, setup/rasterization, and the opening part of primitive hub performance selectors. It ends in the middle of `PH_PERFCNT_SEL` at `PH_PERF_SEL_SC5_PA3_DATA_FIFO_RD`; that enum continues in the next chunk.

The file is metadata only. It declares `typedef enum` value sets and `#define` constants that give numeric encodings for SOC21 register fields, packet fields, performance counter selectors, debug windows, and shader/geometry state. There are no functions, structs with storage, allocation paths, locks, branches, loops, MMIO reads/writes, or persistence code in this range.

Although the repository path is under a `ceph-client` source mirror, this chunk is AMD GPU register metadata. It does not implement distributed filesystem behavior.

## Purpose

`soc21_enum.h` gives semantic names to integer values that are written into or decoded from SOC21 hardware registers. The matching offset and shift/mask headers identify register addresses and bit positions; this enum header identifies the legal values that may occupy those fields.

The covered range includes:

- SPI output, sample, LDS, sprite-coordinate, and shader export/format enums.
- SQ and SQG enums for memory address/alignment modes, instruction types, issue reasons, resource descriptors, texture sampling controls, thread-trace masks, wave types, exception and wait-count partition constants, and large SQ performance selectors.
- COMP and GE enums for context-state data/control types plus geometry engine performance selectors.
- VGT and WD input-assembler/draw enums for primitive topology, source/index type, tessellation modes, geometry-stage enables, output path/primitive selection, DMA swap/buffer mode, and event type encodings.
- GB, GL1, TA, TEX, TCP, TD, GL2, and GRBM performance selectors plus texture/sampler/cache-policy enums.
- CP/CPC/CPF/CPG perf counter and latency/window selectors, scratch atomic operations, ME/pipe/ring IDs, perfmon state values, VMID/config-space constants, source-ID constants, and SPM state values.
- SX blend/downconversion/optimization and performance selectors.
- DB depth/stencil, PRT fault, flush event, pixel-pipe, Z mode/order, and large DB performance selector enums.
- PA/SU performance selector values for primitive assembly, clipping, setup, small primitive culling, scan converter sends, and geometry front-end activity.
- The first 661 entries of `PH_PERFCNT_SEL`, covering SC0 through part of SC5 primitive-hub arbitration and PA FIFO activity selectors.

## Important APIs, Types, and Constants

The public surface is the enum and macro namespace. Important complete enum groups in this chunk include:

- `SPI_PNT_SPRITE_OVERRIDE`, `SPI_PS_LDS_GROUP_SIZE`, `SPI_SAMPLE_CNTL`, `SPI_SHADER_EX_FORMAT`, and `SPI_SHADER_FORMAT`.
- `SH_MEM_ADDRESS_MODE`, `SH_MEM_ALIGNMENT_MODE`, `SQG_PERF_SEL`, `SQ_CAC_POWER_SEL`, `SQ_EDC_INFO_SOURCE`, `SQ_IBUF_ST`, `SQ_IMG_FILTER_TYPE`, `SQ_IND_CMD_CMD`, `SQ_IND_CMD_MODE`, `SQ_INST_STR_ST`, `SQ_INST_TYPE`, `SQ_LLC_CTL`, `SQ_NO_INST_ISSUE`, `SQ_OOB_SELECT`, and the large `SQ_PERF_SEL`.
- SQ resource and texture enums such as `SQ_RSRC_BUF_TYPE`, `SQ_RSRC_FLAT_TYPE`, `SQ_RSRC_IMG_TYPE`, `SQ_SEL_XYZW01`, `SQ_TEX_ANISO_RATIO`, `SQ_TEX_BORDER_COLOR`, `SQ_TEX_CLAMP`, `SQ_TEX_DEPTH_COMPARE`, `SQ_TEX_MIP_FILTER`, `SQ_TEX_XY_FILTER`, `SQ_TEX_Z_FILTER`, plus thread-trace include/exclude masks and shifts.
- `SQ_WAVE_TYPE`, with the alias macro `SQ_WAVE_TYPE_PS0`, and related `SQIND_*`, `SQ_GFXDEC_*`, `SQDEC_*`, `SQPERF*DEC_*`, exception, inserted-instruction, wait-count, and dependency-counter constants.
- `CSCNTL_TYPE` and `CSDATA_TYPE` with their `*_WIDTH` constants.
- `GE1_PERFCOUNT_SELECT`, `GE2_DIST_PERFCOUNT_SELECT`, and `GE2_SE_PERFCOUNT_SELECT`.
- VGT/WD draw enums including `VGT_DI_PRIM_TYPE`, `VGT_EVENT_TYPE`, `VGT_GS_MODE_TYPE`, `VGT_OUT_PRIM_TYPE`, `VGT_TESS_PARTITION`, `VGT_TESS_TOPOLOGY`, `WD_IA_DRAW_SOURCE`, and `WD_IA_DRAW_TYPE`.
- Cache/texture/performance enums including `CHA_PERF_SEL`, `CHCG_PERF_SEL`, `CHC_PERF_SEL`, `GL1A_PERF_SEL`, `GL1C_PERF_SEL`, `GL1H_REQ_PERF_SEL`, `TA_PERFCOUNT_SEL`, `TEX_*`, `TA_TC_*`, `TCP_*`, `TD_PERFCOUNT_SEL`, `GL2A_PERF_SEL`, and `GL2C_PERF_SEL`.
- Global/command processor enums such as `GRBM_PERF_SEL`, `GRBM_SE0_PERF_SEL` through `GRBM_SE7_PERF_SEL`, `PIPE_COMPAT_LEVEL`, `CPC_*`, `CPF_*`, `CPG_*`, `CP_ALPHA_TAG_RAM_SEL`, `CP_ME_ID`, `CP_PERFMON_ENABLE_MODE`, `CP_PERFMON_STATE`, `CP_PIPE_ID`, `CP_RING_ID`, and `SPM_PERFMON_STATE`.
- Shader export and depth/stencil/raster enums such as `SX_BLEND_OPT`, `SX_DOWNCONVERT_FORMAT`, `SX_OPT_COMB_FCN`, `SX_PERFCOUNTER_VALS`, `CompareFrag`, `ConservativeZExport`, `DFSMFlushEvents`, `DbMemArbWatermarks`, `DbPRTFaultBehavior`, `DbPSLControl`, `ForceControl`, `OreoMode`, `PerfCounter_Vals`, `PixelPipeCounterId`, `PixelPipeStride`, `RingCounterControl`, `StencilOp`, `ZLimitSumm`, `ZModeForce`, `ZOrder`, `ZSamplePosition`, `ZpassControl`, and `SU_PERFCNT_SEL`.

The macros in this range define constants rather than typed enums. Examples include SQ indirect debug partition offsets/sizes, SQ decoder address ranges, maximum SGPR/VGPR counts, exception bit encodings, shader wait-counter partitions, `SEM_*` response values, IQ retry/interrupt types, VMID size, secure/non-secure source IDs, and config/context/persistent register-space boundaries.

`PH_PERFCNT_SEL` is intentionally incomplete in this chunk. Lines 20369-21030 cover its start through `SC5_PA3_DATA_FIFO_RD`, including repeated per-SC/per-PA selectors for arbitration cycles, starvation/stall signals, send credits, graphics-pipe transitions, PA FIFO read/write/empty/full/null/event/overflow/EOP/EOPG/deallocation activity, and scan-converter windows.

## Control Flow and Data Flow

This header has no executable control flow. Its data flow is compile-time substitution:

1. A register field is identified by a generated offset header and shift/mask header, for example SOC21 GFX, SPI, SQ, VGT, TA/TCP/TD, CP, SX, DB, PA, or PH register metadata.
2. Driver or tooling code selects one of these enum constants as the semantic field value, such as a primitive type, draw source, texture clamp mode, cache policy, shader export format, perfmon state, or performance counter selector.
3. The value is packed into the target field with AMDGPU helper macros such as `REG_SET_FIELD()` or decoded from a register dump with the matching mask/shift constants.
4. Hardware interprets the resulting integer according to the SOC21 register specification.

Search results in this tree show `soc21_enum.h` included by KFD queue management (`amdkfd/kfd_device_queue_manager_v11.c`) and SOC21-related interrupt handling code referencing SOC21 constants from the same enum/header family. Many constants in this chunk are also mirrored by later-generation enum headers such as `soc24_enum.h`, which is a strong signal that this file is part of the generated ASIC register ABI rather than standalone driver logic.

For performance counters, the runtime flow is usually: select an event ID from enums such as `SQ_PERF_SEL`, `TA_PERFCOUNT_SEL`, `TCP_PERFCOUNT_SELECT`, `GL2C_PERF_SEL`, `GRBM_PERF_SEL`, `CPC_PERFCOUNT_SEL`, `SX_PERFCOUNTER_VALS`, `PerfCounter_Vals`, `SU_PERFCNT_SEL`, or `PH_PERFCNT_SEL`; program that selector into a perf counter select register; start/stop or sample the counter through CP/SPM/perfmon controls; then decode the count with knowledge of the selected hardware block.

## State and Persistence Behavior

The chunk stores no software state and persists nothing to disk. The declared constants describe hardware-visible values whose state lives in GPU registers, command processor state, debug/trace engines, performance counters, and shader/geometry/raster/cache units.

Configuration enums represent state that can persist in registers until reset, power loss, context switch, or later driver programming. Examples include shader memory modes, texture sampler modes, VGT draw/topology/tessellation modes, DB Z/stencil control, SX export formats, CP perfmon mode/state, and cache policy fields.

Performance selector enums do not themselves hold counts. They select which live hardware signal is accumulated by a counter. The selected event and counter state can be volatile, context-dependent, shader-engine-specific, or reset by perfmon control writes.

Several macro groups describe address ranges or partition geometry, such as SQ indirect-register partition offsets, SQ decoder ranges, config/context/persistent spaces, and wait-counter bit partitions. These are static ABI facts for this ASIC generation, not mutable driver state.

The header does not document reset values, valid sequencing, read-only versus write-only behavior, sticky bits, write-one-to-clear semantics, privilege restrictions, or whether a field is context-saved. Consumers must rely on hardware specs and the register programming sequences in AMDGPU.

## Dependencies and Integration Points

Direct dependencies and integration points are:

- SOC21 generated register offset and shift/mask headers under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/`, which define where these enum values are packed.
- AMDGPU register helper conventions, especially token-pasting field helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()`.
- KFD and GFX queue-management code that includes `soc21_enum.h` for generation-specific enum values.
- SOC21 interrupt and queue code in the AMDGPU/KFD tree that relies on related SOC21 constants to classify client/source IDs and queue behavior.
- Performance monitoring paths for SQ/SQG, GE, VGT, GL1/GL2, TA/TCP/TD, GRBM, CPC/CPF/CPG, SX, DB, SU, and PH blocks.
- Register dump, trace, and diagnostic tooling that maps raw selector numbers back to names.
- Later-generation enum headers such as `soc24_enum.h`; these are not dependencies at compile time, but they provide cross-generation comparison points for selector drift and renamed events.

This header sits at an ABI boundary between driver code and hardware. The enum names may look like ordinary C types, but the numeric values are the important contract.

## Risks and Edge Cases

- The chunk begins in the middle of `SPI_PERFCNT_SEL`; the earlier SPI performance selector values are outside this work item. Reconciliation should combine with the previous chunk before describing the full SPI selector enum.
- The chunk ends in the middle of `PH_PERFCNT_SEL`; only SC0 through part of SC5 are present here. The next chunk must provide the remaining PH selectors and the closing typedef.
- Most constants are unscoped C enum values or preprocessor macros. Name collisions are possible across included generated headers, and several names are generic (`UNDEF`, `FORCE_ENABLE`, `RINGID0`, `PIPE_ID0`, etc.).
- Numeric encodings are ASIC-generation-specific. Reusing SOC21 values with SOC24, GFX8, or another generated enum header can silently program the wrong event or mode even when names are similar.
- Performance selector enums are dense, large, and repetitive. A single off-by-one value can select a different hardware signal while still compiling and producing plausible counter data.
- Repeated selector patterns across shader engines, scan converters, PA lanes, GRBM SE instances, and cache pipes are easy to misread. Consumers must choose the correct instance-specific selector, not just a similarly named signal.
- Some enum values encode sensitive control behavior, such as CP scratch atomic ops, perfmon state transitions, debug/trace include masks, SQ indirect partitions, DB flush events, and VGT events. Writing these values in the wrong sequence can affect running GPU work or diagnostics.
- The header does not validate ranges. Passing an enum value into the wrong register field is a normal C integer operation and may not be caught at build time.
- Several value groups describe live hardware states or debug windows. Reading or writing corresponding registers while engines are active can race with hardware unless the caller follows block-specific quiesce/polling rules.

## Test and Validation Signals

Useful validation is mainly compile-time, generator, and hardware-integration coverage:

- Build AMDGPU/KFD paths that include `soc21_enum.h`, especially SOC21 GFX/KFD queue-management and perf/trace code, to catch missing or colliding names.
- Generator checks should verify that enum values are monotonic where expected and match the authoritative SOC21 register database for `SQ_PERF_SEL`, `VGT_DI_PRIM_TYPE`, `VGT_EVENT_TYPE`, `TA_PERFCOUNT_SEL`, `TCP_PERFCOUNT_SELECT`, `GL2C_PERF_SEL`, `GRBM_*`, `CP_*`, `PerfCounter_Vals`, `SU_PERFCNT_SEL`, and `PH_PERFCNT_SEL`.
- Cross-check each enum group against matching shift/mask field widths. For example, primitive type, texture clamp/filter, cache-policy, perfmon state, pipe/ring IDs, and performance selector fields must be wide enough for the maximum value used by SOC21.
- Register-dump decoders should map known raw values back to these names and should reject or label out-of-range values instead of assuming all fields share a common enum.
- Perf counter smoke tests on SOC21 hardware should program representative selectors from SQ, GE, TA/TCP/TD, GL2, GRBM, CP, SX, DB, SU, and PH and verify counters increment under workloads that exercise the corresponding block.
- Graphics pipeline tests should cover VGT draw source/index/primitive/topology/tessellation values, DB compare/stencil/Z modes, SX export/downconversion formats, and SPI shader export/sample settings through normal rendering paths.
- KFD/compute tests should exercise SQ memory modes, wave/instruction type reporting, CP queue/pipe/ring IDs, and perfmon enable/state transitions where those fields are visible to queue setup or debug paths.
- Trace/debug validation should cover SQ thread-trace include/exclude masks, SQ indirect register partition offsets, inserted-instruction IDs, exception bit values, and wait-counter/dependency partition constants.

## Chunk Boundary Notes

Merge/reconciliation should treat this document as a middle slice of `soc21_enum.h`. The previous chunk is needed for the start of `SPI_PERFCNT_SEL`, and the next chunk is needed for the remainder of `PH_PERFCNT_SEL`. Complete per-file research should preserve the fact that this range contains both typed enums and macro value groups, and that it is generated hardware ABI metadata rather than executable driver logic.
