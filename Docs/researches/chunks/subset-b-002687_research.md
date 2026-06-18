# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 4806-7180

## Purpose

This chunk is a generated AMD GC 9.4.3 shader/register field mask header segment. It exports C preprocessor constants for bit positions and 32-bit masks used by AMDGPU code when composing, updating, and decoding graphics-core registers. The declarations are hardware contract data rather than executable code: each register field is represented with `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros.

The covered range starts in the tail of the SPI block, then defines field masks for `xcd0_gc_tpdec`, `xcd0_gc_gdsdec`, `xcd0_gc_rbdec`, and the beginning of `xcd0_gc_ea_gceadec`. These blocks cover shader processor interface counters/trap-screen bases, texture data/address controls, global data share configuration and error reporting, depth/color render-backend controls and tiling configuration, and graphics cache/external-arbitration read/write priority mapping.

## Major Register Areas Covered

The opening SPI tail completes live wave/counter and trap-screen metadata. `SPI_CSQ_WF_ACTIVE_COUNT_6` and `_7` expose `COUNT` and `EVENTS` fields for command-stream queue wavefront activity counters. `SPI_LB_DATA_WAVES` and the `SPI_LB_DATA_PERCU_WAVE_*` registers expose packed per-stage live wave counts for HSGS, VSPS, and CS. `SPIS_DEBUG_READ` and `BCI_DEBUG_READ` are full-width or low-width debug data reads. The `SPI_P0_*` and `SPI_P1_*` trap-screen registers define low/high memory base fields for PSBA/PSMA and minimum VGPR/SGPR fields, giving debug or trap handling code generation-specific masks for program trap-screen memory and register thresholds.

The `xcd0_gc_tpdec` section defines TD and TA controls. `TD_CNTL`, `TD_STATUS`, and `TD_POWER_CNTL` include synchronization phase, CAC/chicken bits, LDS stall tuning, power throttle disable, round-to-zero, signed-format disable, SRAM/clock-gating related fields, busy status, and medium-grain clock-gating controls. TD and TA both define correctable and uncorrectable EDC status registers with common low/high layouts: status/address valid flags, error address, memory id, ECC/parity or other error type, detailed error info, event counters, FED counters, and poison bits for correctable paths. `TD_DSM_CNTL`, `TD_DSM_CNTL2`, `TA_DSM_CNTL`, and `TA_DSM_CNTL2` expose data-pattern, single-write, error-injection, delay-selection, and injection-delay masks for FIFO/RAM diagnostic self-test paths.

The TA half of `xcd0_gc_tpdec` covers texture address block behavior. `TA_POWER_CNTL` controls clock enable modes for input, LOD, and WDP logic. `TA_CNTL` exports credit fields for FX/SQ XNACK, TC data, aligner, and TD FIFO paths. `TA_CNTL_AUX` includes swizzle, texture fault override, gather4 behavior, and determinism-disable bits for specific opcode/sample/writeop/format cases. `TA_FEATURE_CNTL` exposes atomic coalescing and several FIFO/chicken fields. `TA_STATUS` reports PFIFO empty state and block busy state for input, FG, TA, FA, AL, and aggregate busy.

The `xcd0_gc_gdsdec` section defines global data share controls, status, fault registers, EDC counters, and diagnostic injection masks. `GDS_CONFIG` includes write-disable and per-shader-array GPR phase selection. `GDS_CNTL_STATUS` reports GDS, GRBM buffer, DS, GWS, order FIFO, conflict/clamp, and eight credit-busy bits. `GDS_PROTECTION_FAULT` and `GDS_VM_PROTECTION_FAULT` encode fault detection, write-disable, GRBM/GWS/OA/TMZ indicators, shader/CU/SIMD/wave or VMID information, and fault address fields. EDC-related registers include total GDS memory SEC/DED counts, GRBM SEC/DED counts, OA DED status by ME/pipe, OA physical and pipe SEC/DED counters, and low/high UE/CE error status records. `GDS_DSM_CNTL`, `GDS_DSM_CNTL2`, and `GDS_WD_GDS_CSB` support diagnostic irritator data selection, single-write enable, error injection, delay selection, and watchdog/counter fields across GDS memory, input queue, physical command/data RAM, and pipe memory.

The `xcd0_gc_rbdec` section is the largest part of the chunk. `DB_DEBUG` through `DB_DEBUG4` expose many depth-buffer debug, performance, workaround, coherency, cache, compression, fast-Z/stencil, pre-Z/post-Z, viewport, synchronization, and clock/power-related switches. `DB_CREDIT_LIMIT`, `DB_WATERMARKS`, `DB_SUBTILE_CONTROL`, cacheline/FIFO depth registers, exception/ring controls, RMI cache policy, DFSM configuration/watermarks/watchdog/flush controls, and DFSM counters describe backend pipeline capacity and scheduling behavior. Many of these fields are "debug" or "chicken" bits that may be programmed only for bring-up, workarounds, or hardware tuning.

The same `xcd0_gc_rbdec` block also defines render-backend and graphics-buffer topology data. `CC_RB_REDUNDANCY`, `CC_RB_BACKEND_DISABLE`, `GC_USER_RB_REDUNDANCY`, and `GC_USER_RB_BACKEND_DISABLE` encode failed/disabled backend masks and redundancy enable fields. `GB_ADDR_CONFIG` and `GB_ADDR_CONFIG_READ` expose tile/split/pipe/bank/rb/hash/interleave/PRT/screen-index layout fields. `GB_BACKEND_MAP`, `GB_GPU_ID`, and `CC_RB_DAISY_CHAIN` describe backend mapping, GPU id, and per-backend daisy-chain state. `GB_TILE_MODE0` through `GB_TILE_MODE31` repeat a compact tiling layout definition with fields such as micro tile mode, array mode, pipe config, tile split, sample split, bank dimensions/height, and macro tile aspect. `GB_MACROTILE_MODE0` through `_15` provide bank width/height, macro tile aspect, and number-of-banks fields. These masks are central to surface layout interpretation and must match the paired offset/register-definition headers.

The color buffer controls appear near the end of the render-backend section. `CB_HW_CONTROL`, `CB_HW_CONTROL_1`, `CB_HW_CONTROL_2`, and `CB_HW_CONTROL_3` expose blend/resolve/write-mask optimizations, CM/FC/CC/DC cache and FIFO sizing, read latency FIFO depths, arbitration assumptions, overwrite-combiner behavior, shader blend optimizations, nack/early-write-ack controls, blender clock gating, target-mask validation, and color cache prefetch count. `CB_HW_MEM_ARBITER_RD` and `_WR` define read/write arbiter modes, urgency age handling, group-age breaks, per-client weights, decay behavior, age/weight scaling, and "send lasts" handling. `CB_DCC_CONFIG` defines DCC overwrite-combiner depth/disable fields, constant encode disable, keyid/read-return FIFO depths, DCC cache eviction point, and DCC cache tag count.

The `xcd0_gc_ea_gceadec` section begins external arbitration/cache routing for DRAM and IO clients. `GCEA_DRAM_RD_CLI2GRP_MAP0/1` and `GCEA_DRAM_WR_CLI2GRP_MAP0/1` map client IDs 0-31 into four priority/groups using two-bit fields. `GCEA_DRAM_RD_GRP2VC_MAP` and `_WR_GRP2VC_MAP` map each group to a virtual channel. `GCEA_DRAM_RD_LAZY` and `_WR_LAZY` tune group delays, request accumulation thresholds, timeouts, and idle maxima. `GCEA_DRAM_RD_CAM_CNTL` and `_WR_CAM_CNTL` define CAM entry limits, GMI thresholds, hold-off timers, and same-group all-timer fields. Burst, priority aging, queuing, fixed priority, urgency, and priority quantum registers then define how DRAM requests are ordered. The chunk continues into IO arbitration with `GCEA_IO_RD/WR_CLI2GRP_MAP*`, combine/flush timers, group burst limits, and the beginning of IO read/write priority aging. The last register in this chunk, `GCEA_IO_WR_PRI_AGE`, is incomplete here; its masks continue in the next file chunk.

## Important APIs, Types, and Functions

There are no functions, structs, enums, or runtime APIs in this chunk. The public interface is the macro namespace itself:

- `*_SHIFT` constants define the least-significant bit offset for a hardware register field.
- `*_MASK` constants define the field's occupied bits in a 32-bit register value.
- Register comments such as `//TD_CNTL` and address block comments such as `// addressBlock: xcd0_gc_gdsdec` provide generated grouping metadata for readers and tooling.

AMDGPU code normally consumes these macros through register helper macros such as field set/get helpers and read/modify/write paths, paired with neighboring headers that define register offsets and possibly defaults. The macro names are therefore an internal hardware ABI for GC 9.4.3 driver code: renaming or changing a constant affects any token-pasting helper or direct bitwise expression that references it.

## Control Flow

This header has no runtime control flow. Its effective flow is compile-time inclusion:

1. A GC 9.4.3-specific AMDGPU source file includes generated register offset and mask headers.
2. Driver code selects the correct `REGISTER__FIELD__SHIFT` or `REGISTER__FIELD_MASK` constant for a register field.
3. The compiler folds the constants into MMIO, indirect-register, diagnostic decode, or register value construction code.
4. Hardware behavior changes only when the including driver code performs the actual register read or write.

The register groups imply external driver flows. Trap/debug paths can read SPI live-wave counters and program trap-screen bases. GPU initialization or workaround code can program TD/TA controls, clocks, credits, determinism, and chicken bits. Error-handling code can decode TD/TA/GDS EDC status and fault registers. Render-backend initialization programs topology, backend disables, tiling modes, DCC, cache/FIFO sizing, and arbitration. Performance or QoS tuning code can program GCEA client-to-group, group-to-VC, priority, urgency, lazy accumulation, and quantum fields.

## State and Persistence Behavior

The file itself stores no state and has no persistence behavior. All state described by these masks lives in GPU hardware registers.

The represented hardware state includes live SPI wave counters, trap-screen base addresses, TD/TA busy and power/clock controls, XNACK and FIFO credits, deterministic texture-addressing switches, EDC status/counters, diagnostic injection selectors, GDS protection fault records, DB/CB/GB backend configuration, tiling and macrotile modes, color/depth cache and FIFO sizing, render-backend disable/redundancy masks, and GCEA arbitration policy.

Persistence depends on hardware reset and driver lifecycle rather than this header. Values written using these masks may persist until GPU reset, driver reinitialization, suspend/resume restore, power-gating reset, or later register programming. Status and error fields may be latched, clear-on-read, write-one-to-clear, or otherwise side-effectful depending on the register; this generated mask header does not encode access type, reset value, locking, ordering, or side-effect semantics.

## Dependencies and Integration Points

This header depends only on the C preprocessor and the file-level include guard from the complete header. In practice it must be synchronized with AMD's generated register database and adjacent GC 9.4.3 headers that provide register offsets/base indices. Numeric masks in this file are meaningful only when paired with the correct generation, register address, and access path.

Primary integration points include:

- AMDGPU GC 9.4.3 initialization and workaround code for TD/TA, DB, CB, GB, GDS, and GCEA registers.
- Debug and hang-diagnosis paths that read SPI live wave counters, TD/TA/GDS/DB busy bits, and protection-fault or EDC status.
- RAS/error-handling paths that decode correctable/uncorrectable ECC, parity, poison, memory id, error address, and FED/counter fields.
- Render-backend topology and harvest handling that uses backend disable, redundancy, daisy-chain, GPU id, tile mode, macrotile mode, and address configuration fields.
- Surface layout and memory-management code that depends on `GB_ADDR_CONFIG*`, `GB_TILE_MODE*`, and `GB_MACROTILE_MODE*` values matching the actual ASIC.
- Performance, QoS, and memory-traffic tuning paths that program CB memory arbiters and GCEA DRAM/IO grouping, priority, urgency, quantum, lazy accumulation, and combine/flush behavior.

## Risks and Edge Cases

The main risk is definition drift from the GC 9.4.3 hardware specification. A wrong shift or mask can silently program the wrong bit, decode the wrong error field, misconfigure tiling, or corrupt arbitration policy without producing a compiler error.

Specific risks in this chunk include:

- The section starts and ends at chunk boundaries inside larger register families. The first SPI context was defined before line 4806, and `GCEA_IO_WR_PRI_AGE` is incomplete at line 7180, so consumers of this research should reconcile adjacent chunks before treating those families as complete.
- Repeated families such as `GB_TILE_MODE0-31`, `GB_MACROTILE_MODE0-15`, `GCEA_*_CLI2GRP_MAP0/1`, and read/write priority register pairs are vulnerable to generator or copy-pattern errors that are hard to review manually.
- Several fields are named `RESERVED`, `UNUSED`, `CHICKEN`, or `DEBUG`; callers must not assume these are safe for normal runtime programming just because masks exist.
- Status/error/fault registers and diagnostic injection controls may have side effects or privileged access constraints not represented here.
- Backend disable, redundancy, tile mode, macrotile mode, and address config masks are high blast-radius constants: incorrect values can break surface layout, memory addressing, harvest handling, or render backend routing.
- Arbitration and priority fields in CB/GCEA can affect fairness, latency, and deadlock-avoidance behavior. A wrong two-bit group mapping or priority quantum can cause workload-specific performance regressions rather than immediate failures.
- Full-width masks such as `0xFFFFFFFFL` and high-bit masks such as `0x80000000L` require callers to use unsigned/fixed-width register values and avoid sign-extension surprises in helper code.

## Test Signals

Useful validation signals are mostly compile-time, generated-data, and hardware-behavior checks:

- GC 9.4.3 AMDGPU builds should compile without missing or duplicate macro definitions after including this header with the matching offset headers.
- Static/generated validation should compare every `*_SHIFT` and `*_MASK` pair in this chunk against AMD's authoritative register database for GC 9.4.3.
- Field helper tests or compile-time assertions can verify representative set/get round trips for packed fields such as GCEA client groups, GDS fault VMID/address, TD/TA EDC counters, GB tile mode fields, and CB arbiter weights.
- Hardware bring-up on GC 9.4.3 devices should confirm TD/TA/GDS EDC injection and status decode paths report the expected memory id, address, ECC/parity, CE/UE, FED, and poison fields.
- Render-backend tests should cover backend harvesting/redundancy, tile/macrotile programming, DCC behavior, depth/stencil compression, fast clear, and surface layout correctness across color/depth formats.
- Hang and fault diagnostics should verify that SPI live-wave counters, TA/TD/GDS/DB busy bits, and GDS protection faults decode consistently with firmware traces or known fault-injection scenarios.
- Performance and QoS testing should watch for regressions after any GCEA or CB arbitration changes, especially read/write fairness, DRAM/IO virtual-channel mapping, urgency handling, lazy request accumulation, and priority quantum behavior.
