# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 16930-19506

## Scope

This chunk is a generated AMD GC 9.4.3 shader/register mask header slice. It starts at the tail of `TCP_UTCL1_CNTL2` mask definitions, contains complete TCP status/perf/error-injection groups, the `xcd0_gc_gdspdec` GDS register block, the `xcd0_gc_rasdec` RAS signature block, and the beginning of the `xcd0_gc_gfxdec0` graphics pipeline state block. It ends inside `SPI_PS_INPUT_CNTL_19`, after its `CYL_WRAP_MASK`; the remaining masks for that register are in the next chunk.

The range contains 2,140 `#define` entries. They follow the generated convention `REGISTER__FIELD__SHIFT` for bit positions and `REGISTER__FIELD_MASK` for the corresponding 32-bit field masks. The file is declarative only: it exports constants used by AMDGPU and KFD code that writes or decodes GC 9.4.3 hardware registers.

## Purpose

`gc_9_4_3_sh_mask.h` provides the bitfield half of the GC 9.4.3 register ABI. This slice covers fields for texture cache/L1 VM status, GDS allocation and reset, graphics RAS signatures, depth/stencil and raster state, render target masks, viewport and clip state, and pixel shader input interpolation controls.

The constants are meant to be paired with `gc_9_4_3_offset.h`, which supplies the matching `reg...` offsets and base indices. Runtime driver code combines these masks and shifts with SOC15 helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, `REG_GET_FIELD`, and packet-emission helpers. This avoids open-coded bit numbers in ASIC-specific paths.

## Important API Surface

- `TCP_UTCL1_CNTL2` tail masks describe L1 VM/cache control bits including memory-type override disable, any-line-valid, GPUVM invalidation mode, forced snoop, forced GPUVM invalidation acknowledgement, 2M-to-64K fragmentation, and thrashing protection/enablement. The matching shifts start before this chunk.
- `TCP_UTCL1_STATUS` exposes fault, retry, PRT, and timeout detection bits for TCP UTCL1 diagnostics.
- `TCP_DSM_CNTL2` provides error-injection enable/select fields for TCP cache RAM, LFIFO RAM, command FIFO, VM FIFO, DB RAM, UTCL1 LFIFO0/LFIFO1, and a global TCP inject delay field.
- `TCP_PERFCOUNTER_FILTER` and `TCP_PERFCOUNTER_FILTER_EN` define filter values and enables for TCP performance counter collection, including buffer/flat/dimension mode, data and numeric formats, software mode, sample count, opcode type, GLC/SLC, compression, and address mode.
- `GDS_VMID0_BASE/SIZE` through `GDS_VMID15_BASE/SIZE` define per-VMID GDS address windows. `GDS_GWS_VMID0` through `GDS_GWS_VMID15` define per-VMID GWS base/size fields. `GDS_OA_VMID0` through `GDS_OA_VMID15` define per-VMID ordered-append allocation masks.
- `GDS_GWS_RESET0`, `GDS_GWS_RESET1`, `GDS_GWS_RESOURCE_RESET`, `GDS_OA_RESET_MASK`, and `GDS_OA_RESET` expose reset controls for global wave sync and ordered-append resources. `GDS_ENHANCE`, `GDS_OA_CGPG_RESTORE`, and GDS context-switch status/counter registers describe GDS behavior across compute, graphics, VS, PS0-PS7, and GS contexts.
- `RAS_SIGNATURE_CONTROL`, `RAS_SIGNATURE_MASK`, and `RAS_*_SIGNATURE*` define signature collection or comparison fields for SX, DB, PA, VGT, SQ, SC, IA, SPI, TA, TD, CB, and BCI blocks.
- `DB_RENDER_CONTROL`, `DB_COUNT_CONTROL`, `DB_DEPTH_VIEW`, `DB_RENDER_OVERRIDE`, `DB_RENDER_OVERRIDE2`, `DB_Z_INFO`, `DB_STENCIL_INFO`, `DB_DFSM_CONTROL`, depth/stencil base/clear/bounds registers, and HTILE fields define depth-buffer state, compression/decompression behavior, Z/stencil formats, tile/compression layout, clear/copy operations, and override modes.
- `PA_SC_*` and `PA_CL_*` families define screen/window/generic/viewport scissors, clip rectangles, edge rules, hardware offsets, raster configuration, tile steering, viewport scale/offset, viewport Z min/max, user clip planes, and near-clip Z programming.
- `CB_TARGET_MASK`, `CB_SHADER_MASK`, `CB_BLEND_*`, `CB_DCC_CONTROL`, `COHER_DEST_BASE*`, and CP context identifiers define color output masks, blend constants, DCC control, coherency destination bases, and current CP performance/context identity fields.
- `SPI_PS_INPUT_CNTL_0` through the partial `SPI_PS_INPUT_CNTL_19` define pixel shader input mapping and interpolation controls: attribute offsets, default values, flat shading, cylindrical wrap, point-sprite texture selection, duplicate controls, FP16 interpolation mode, secondary attribute defaults, and attribute-valid bits.

There are no C functions, structs, enums, inline helpers, or runtime APIs in this chunk. The macro namespace itself is the exported interface.

## Control Flow

The header has no executable control flow. Its effective flow is compile-time inclusion followed by runtime register access in consumer code:

1. A GC 9.4.3 driver path includes this header and the offset header.
2. The code selects a register offset such as `regGDS_VMID0_BASE`, `regGDS_GWS_VMID0`, `regTCP_UTCL1_STATUS`, or a DB/PA/SPI graphics state register.
3. It composes, modifies, or decodes a 32-bit value by applying the relevant `__SHIFT` and `_MASK` constants, often through register-field helper macros.
4. It writes the value through MMIO, RLC-safe register paths, or command stream packet emission, or it reads status bits for diagnostics.

The GDS families imply indexed control flows. In `gfx_v9_4_3.c`, initialization loops write `regGDS_VMID0_BASE`, `regGDS_VMID0_SIZE`, `regGDS_GWS_VMID0`, and `regGDS_OA_VMID0` with offsets derived from the VMID to remove GDS/GWS/OA access for compute and user graphics VMIDs. Ring emission later programs the same resource windows for a target VMID, using `GDS_GWS_VMID0__SIZE__SHIFT` to pack GWS size with GWS base.

The DB/PA/CB/SPI families are graphics pipeline state definitions. They are normally consumed by command streams, clear-state tables, state setup code, or debugging paths rather than by local loops in the header. The RAS and TCP status/error-injection fields are diagnostic or service flows: code reads status/signature registers, checks the field masks, and may configure injection or performance-counter filters during validation and RAS handling.

## State and Persistence Behavior

The macros are stateless compile-time constants. The state they describe lives in GC 9.4.3 hardware registers and persists according to hardware reset, power-gating, context-switch, firmware, and driver programming rules.

GDS VMID base/size, GWS, and OA registers control per-VMID access to shared on-chip resources. Incorrect values can persist until rewritten by firmware, a ring packet, driver initialization, suspend/resume restore, or GPU reset. VMID0 is treated specially by the GC 9.4.3 graphics code so HWS firmware can preserve save/restore entries while other VMIDs are cleared during initialization.

DB, PA, CB, and SPI fields represent graphics context state. Their values are usually part of command-submission or context state and can survive within a context until another packet, clear-state load, context switch, or reset changes them. Depth/stencil compression controls, DCC state, scissor/viewport ranges, clip planes, raster configuration, and pixel shader input routing directly affect rendered output and memory accesses.

TCP, RAS, and GDS status/counter fields describe live hardware conditions such as VM faults, retries, PRT events, timeouts, RAS signatures, context-switch counts, and reset/resource status. This header does not encode access semantics such as read-clear, write-one-to-clear, privilege level, required ordering, or reserved-bit policy; those constraints belong to the hardware spec and the consuming driver code.

## Dependencies and Integration Points

- Depends only on the C preprocessor and its include guard, but semantically depends on AMD's generated GC 9.4.3 register database.
- Must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_offset.h`, which supplies offsets such as `regGDS_VMID0_BASE`, `regGDS_VMID0_SIZE`, `regGDS_GWS_VMID0`, `regGDS_OA_VMID0`, and `regTCP_UTCL1_STATUS`.
- Included by GC 9.4.3 consumers including `amdgpu/gfxhub_v1_2.c`, `amdgpu/gfx_v9_4_3.c`, `amdgpu/amdgpu_amdkfd_gc_9_4_3.c`, and `amdkfd/kfd_device_queue_manager_v9.c`.
- Integrates with SOC15 register helpers, GRBM/SRBM selection, RLC-safe writes, and command stream packet emission. The GDS macros are directly used by `gfx_v9_4_3.c` when clearing per-VMID GDS/GWS/OA access and when emitting GDS resource switches.
- Integrates with KFD because compute VMIDs, shared memory settings, traps, and queue management rely on the same GC 9.4.3 register model.
- Integrates with RAS and debug paths through TCP UTCL1 status, TCP error-injection controls, performance-counter filters, and per-block RAS signature fields.

## Risks and Edge Cases

- Bitfield drift is the main risk. A wrong shift or mask can silently write a valid but incorrect hardware bit, causing VMID isolation failures, resource leakage, wrong depth/stencil behavior, rendering corruption, missed fault detection, or bad diagnostics.
- This chunk is boundary-partial. It begins after the `TCP_UTCL1_CNTL2__SPARE_MASK` line, so the corresponding shifts and first mask for that register are outside the range. It ends before the rest of `SPI_PS_INPUT_CNTL_19` and before `SPI_PS_INPUT_CNTL_20`, so merge tooling must not treat those register groups as complete here.
- Repeated VMID and viewport families are easy to mis-generate. Off-by-one indexing in `GDS_VMIDn`, `GDS_GWS_VMIDn`, `GDS_OA_VMIDn`, `PA_SC_VPORT_*`, `PA_CL_VPORT_*`, or `SPI_PS_INPUT_CNTL_n` definitions would compile cleanly but affect the wrong VMID, viewport, or shader input.
- GDS/GWS/OA fields affect isolation and scheduling. Programming an incorrect base, size, or reset mask can grant a VMID unintended access to shared resources or break HWS/KFD context save/restore assumptions.
- DB/CB/PA/SPI fields are high visual-correctness risk. Errors in depth/stencil formats, compression metadata, scissor bounds, viewport transform, raster configuration, color masks, DCC control, or interpolation control can produce subtle rendering defects rather than immediate failures.
- Status, signature, and injection fields mix observation and control. This header does not distinguish passive status bits from destructive reset or injection controls, so caller-side discipline and hardware documentation are required.

## Test Signals

- Build AMDGPU/KFD with GC 9.4.3 enabled to catch missing, renamed, or duplicate macro definitions and mismatches with token-pasting register helpers.
- Generated-header validation should compare this chunk against the authoritative GC 9.4.3 register database and verify every `__SHIFT`/`_MASK` pair, repeated VMID family, viewport family, and `SPI_PS_INPUT_CNTL_n` family.
- Runtime GC 9.4.3 smoke should boot, submit graphics and compute queues, exercise VMID allocation, KFD queue creation, suspend/resume, and GPU reset while checking for VM faults, hangs, and RAS warnings.
- GDS-specific tests should verify initialization clears non-VMID0 GDS/GWS/OA access, firmware can enable target compute VMIDs, and ring-emitted GDS switches program expected base/size values.
- Graphics validation should include depth/stencil clears, decompression, stencil masks, DCC behavior, scissor and viewport clipping, clip planes, blend constants, color target masks, and pixel shader input interpolation.
- RAS/debug validation should inspect `TCP_UTCL1_STATUS`, TCP performance counter filters, error-injection paths, and `RAS_*_SIGNATURE*` decoding against known-good hardware traces or injected faults.
