# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_7_2_sh_mask.h lines 14180-18444

## Purpose

This chunk is the final large slice of the generated AMD GFX 7.2 shader/register mask header. It contains C preprocessor constants that describe bit masks and bit shifts for 32-bit GPU registers used by the Southern Islands/CIK-era GFX7 AMDGPU stack. The range begins at the tail of `TCP_EDC_COUNTER`, covers texture/cache policy and watchpoint fields, GDS/GWS/OA register fields, VGT/IA/WD graphics pipeline fields, debug and performance-counter fields, and ends with DIDT indirect power-throttling controls for SQ, DB, TD, and TCP.

The file is declarative hardware binding data. It has no executable logic, but the constants are part of the ABI between driver code and GFX 7.2 hardware/firmware. Driver paths include this header with companion register-address headers such as `gfx_7_2_d.h` or `gfx_7_0_d.h`, then use the masks and shifts to compose MMIO writes, decode MMIO reads, or build PM4 packets that program graphics and compute state.

## Major Register Areas Covered

The first section defines cache and texture client fields. `TC_CFG_L1_LOAD_POLICY0/1`, `TC_CFG_L1_STORE_POLICY`, `TC_CFG_L2_LOAD_POLICY0/1`, `TC_CFG_L2_STORE_POLICY0/1`, and `TC_CFG_L2_ATOMIC_POLICY` expose per-policy low-bit fields for cache behavior. `TC_CFG_L1_VOLATILE` and `TC_CFG_L2_VOLATILE` provide volatile-control nibbles. `TCP_WATCH0..3_ADDR_H/L` and `TCP_WATCH0..3_CNTL` describe four TCP memory watchpoints, including address bits, mask, VMID, access mode, and valid bit. `TCP_BUFFER_ADDR_HASH_CNTL` and `TCP_EDC_COUNTER` appear at the chunk boundary through channel/bank hash and SEC/DED counter fields.

Clock-gating and local block controls follow. `TD_CGTT_CTRL`, `TA_CGTT_CTRL`, `CGTT_TCP_CLK_CTRL`, `CGTT_TCI_CLK_CTRL`, `CGTT_GDS_CLK_CTRL`, `CGTT_VGT_CLK_CTRL`, `CGTT_IA_CLK_CTRL`, and `CGTT_WD_CLK_CTRL` share the generated layout for on-delay, off-hysteresis, and soft override bits. `TCI_STATUS` and `TCI_CNTL_1/2` provide texture client interface status/control fields.

The GDS section is a dense map for global data share, global wave sync, and ordered append state. It includes `GDS_CONFIG`, `GDS_CNTL_STATUS`, `GDS_ENHANCE`, `GDS_ENHANCE2`, protection fault registers, SECDED counters, OA DED/error reporting, debug controls/data, direct read/write and burst access registers, `GDS_ATOM_*` atomic command/source/destination/readback fields, `GDS_GWS_RESOURCE*`, `GDS_OA_*`, `GDS_VMID0..15_BASE/SIZE`, `GDS_GWS_VMID0..15`, `GDS_OA_VMID0..15`, `GDS_GWS_RESET0/1`, `GDS_GWS_RESOURCE_RESET`, `GDS_COMPUTE_MAX_WAVE_ID`, and OA reset/restore masks. These fields support both allocation state and low-level command/debug plumbing for compute and graphics use of GDS/GWS/OA resources.

The VGT/IA/WD section covers front-end graphics state. Draw and event submission fields include `VGT_DRAW_INITIATOR`, `VGT_EVENT_INITIATOR`, `VGT_EVENT_ADDRESS_REG`, DMA base/index/type/size/control registers, index count/instance/primitive registers, primitive ID controls, vertex reuse and output deallocation, multi-primitive reset, output path, tessellation controls, group vector controls, FIFO depths, and copy-state fields. Geometry, tessellation, stream-out, and multi-VGT fields include `VGT_GS_MODE`, `VGT_GS_ONCHIP_CNTL`, `VGT_GS_OUT_PRIM_TYPE`, `VGT_CACHE_INVALIDATION`, `VGT_STRMOUT_*`, `VGT_SHADER_STAGES_EN`, `VGT_LS_HS_CONFIG`, `VGT_DMA_LS_HS_CONFIG`, `VGT_TF_PARAM`, `VGT_SYS_CONFIG`, `VGT_HS_OFFCHIP_PARAM`, `VGT_GS_INSTANCE_CNT`, `IA_MULTI_VGT_PARAM`, ESGS/GSVS ring sizes and offsets, and GS item sizes. `IA_CNTL_STATUS`, `IA_VMID_OVERRIDE`, `WD_CNTL_STATUS`, `GFX_PIPE_CONTROL`, `GFX_PIPE_PRIORITY`, `CC_GC_SHADER_ARRAY_CONFIG`, `GC_USER_SHADER_ARRAY_CONFIG`, `CC_GC_PRIM_CONFIG`, and `GC_USER_PRIM_CONFIG` connect this front-end state to shader-array and primitive routing controls.

The debug and performance-counter tail is intentionally repetitive. `WD_DEBUG_REG0..5`, `IA_DEBUG_REG0..9`, and `VGT_DEBUG_REG0..35` expose many internal ready/valid, FIFO, request, state-machine, primitive, tessellation, ring, and pipe status bits. `GDS_PERFCOUNTER*`, `VGT_PERFCOUNTER*`, `IA_PERFCOUNTER*`, and `WD_PERFCOUNTER*` define selector, mode, low, and high counter fields for perfmon reads. The final DIDT section defines indirect-register index/data fields and common DIDT controls for `SQ`, `DB`, `TD`, and `TCP`: enable/reset/clock override, reference clock, phase offset, min/max power, max power delta, interval sizing, long-term ratio, and weight tables `WEIGHT0_3`, `WEIGHT4_7`, and `WEIGHT8_11`.

## Important APIs, Types, and Functions

There are no functions, structs, typedefs, or enums in this chunk. The exported interface is the generated macro namespace:

- `REGISTER__FIELD_MASK` gives the bit mask for a field in a 32-bit register.
- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit position.
- Full-width fields use `0xffffffff` masks and shift zero, while repeated indexed registers use the register name to encode the instance, such as `GDS_VMID15_SIZE` or `TCP_WATCH3_CNTL`.

Representative consumers in this tree include `amdgpu/gfx_v7_0.c`, `amdgpu/amdgpu_amdkfd_gfx_v7.c`, `amdkfd/kfd_device_queue_manager_cik.c`, `pm/legacy-dpm/kv_dpm.c`, and powerplay/SMU management code. These files include `gca/gfx_7_2_sh_mask.h` and pair the macros with register-address constants from the GCA headers. Access helpers include direct MMIO helpers such as `RREG32`, `WREG32`, `RREG32_DIDT`, and `WREG32_DIDT`, field-write helpers such as `CGS_WREG32_FIELD_IND`, and command stream packet construction that writes register offsets and values into rings.

## Control Flow

This header has no runtime control flow. Its effective flow is compile-time expansion:

1. A GFX7 AMDGPU, KFD, or power-management source file includes the generated register offset and mask headers.
2. The code selects a register by hardware generation, VMID, queue, shader stage, or front-end block.
3. The caller combines masks and shifts with a desired field value, often by shifting manually or through a register-field helper.
4. The result is written to an MMIO register, an indirect DIDT register, or a PM4 packet payload, or a register read is decoded with the same field constants.

Several important hardware flows are implied by these masks. GFX initialization programs GDS VMID base/size and GWS/OA allocation defaults, VGT cache invalidation, GS vertex reuse, and queue/ring state. KFD debug support programs TCP watch address/control fields per VMID and address range. Command submission can emit GDS reset and `GDS_COMPUTE_MAX_WAVE_ID` writes when a compute IB needs GDS wave ID resynchronization. Power-management code reads and writes DIDT indirect registers to enable or disable per-block dynamic throttling based on platform capabilities.

## State and Persistence Behavior

The header stores no state. The state described by the macros lives in hardware registers and persists according to GPU reset, power-gating, clock-gating, queue selection, and driver save/restore sequencing.

GDS fields hold resource allocation and fault/debug state for VMIDs, GWS resource ownership, ordered append counters and addresses, atomic command operands and results, protection faults, ECC counters, and restore/reset data. These values affect command processor and shader-visible behavior until reprogrammed or reset. The `GDS_COMPUTE_MAX_WAVE_ID` flow is notable because the GFX7 driver writes it from a command stream path to resynchronize ME and GDS wave ID counters after certain compute workloads.

VGT, IA, and WD fields describe transient graphics pipeline state, but many are context-state registers saved/restored by clear-state tables, RLC firmware, or command stream setup. Stream-out configuration, tessellation rings, ESGS/GSVS rings, instance counts, primitive type, index limits, and shader stage enables must match the active pipeline state or draw/dispatch behavior can be corrupted.

TCP watchpoint fields are debug state scoped by address, mask, mode, valid bit, and VMID. DIDT fields are power-control state accessed through `DIDT_IND_INDEX` and `DIDT_IND_DATA`; they control throttling/ramping behavior for SQ, DB, TD, and TCP blocks and are toggled by legacy DPM and powerplay paths. Perf counter selector and counter registers are mutable profiling state; debug register fields are mostly readback/status or debug-only control surfaces, but the header itself does not annotate access type or clear semantics.

## Dependencies and Integration Points

The only syntactic dependency is the C preprocessor. Operationally, this chunk must stay synchronized with the generated GFX 7.2 register-offset and enum headers in `include/asic_reg/gca`, especially `gfx_7_2_d.h`, `gfx_7_2_enum.h`, and related GFX7/GMC/OSS/DCE headers included by the same driver files.

Important integration points are:

- `amdgpu/gfx_v7_0.c` includes this header, defines `amdgpu_gds_reg_offset[]` from GDS VMID/GWS/OA register addresses, initializes GDS and VGT state, writes `VGT_CACHE_INVALIDATION`, and emits `GDS_COMPUTE_MAX_WAVE_ID` packets for GDS wave ID reset handling.
- `amdgpu/amdgpu_amdkfd_gfx_v7.c` and `amdkfd/kfd_device_queue_manager_cik.c` include the header for CIK KFD queue management, VMID/queue targeting, and debug-register programming; related newer-generation KFD paths show the same TCP watchpoint field pattern.
- `pm/legacy-dpm/kv_dpm.c` uses `RREG32_DIDT`/`WREG32_DIDT` and `DIDT_SQ_CTRL0__DIDT_CTRL_EN_MASK` or `DIDT_DB_CTRL0__DIDT_CTRL_EN_MASK` to enable or disable dynamic throttling for supported blocks.
- `pm/powerplay/hwmgr/smu7_powertune.c` uses `CGS_WREG32_FIELD_IND` with DIDT block/control field names to program indirect DIDT fields from power-tuning tables.
- Clear-state and context-save code depends on VGT/IA/GDS register layouts being correct even when it writes literal register values rather than using every field macro directly.
- Perf, RAS, fault, and debug consumers depend on the masks to decode GDS protection faults, SECDED counters, VGT/IA/WD/GDS performance counters, and internal debug status.

## Risks and Edge Cases

The highest risk is silent hardware misprogramming. A bad mask or shift can compile cleanly while corrupting cache policy, watchpoint routing, GDS allocation, draw initiation, tessellation and stream-out state, performance counter selection, or DIDT power controls.

The chunk contains many repeated register families with near-identical layouts: policy arrays, four TCP watchpoints, sixteen GDS VMID entries, sixteen GDS GWS/OA VMID entries, GWS reset masks, dozens of VGT/IA/WD debug registers, and replicated DIDT layouts for multiple blocks. Generated or manual drift in one instance can be hard to detect by review because the repetition is expected.

Some fields are full-width data paths, some are side-effectful controls, and some are sticky status or counters. The header does not distinguish read-only, write-one-to-clear, write-only, indirect, or debug-only fields. Callers must know hardware sequencing for GDS atomics, GDS resets, cache invalidation, stream-out counters, TCP watchpoint validity, DIDT reset/enable bits, and clock-gating soft overrides.

The requested range starts mid-register at `TCP_EDC_COUNTER__DED_COUNT__SHIFT` and ends at the file guard. Earlier chunks are required for complete `TCP_EDC_COUNTER` and complete file-level context. Conversely, this chunk includes the final `#endif`, so line-based tools must not treat this as a standalone include file unless they also provide the opening guard and earlier definitions.

Generation/version skew is another practical edge case. `gfx_7_0.c` includes `gfx_7_0_d.h` while using `gfx_7_2_sh_mask.h`; that is an established local pattern for this CIK-era code, but it means address definitions and mask definitions must be validated as a matched hardware generation set rather than renamed independently.

## Test Signals

Useful validation signals are build-time, static-generation, and hardware-execution oriented:

- Kernel builds that enable AMDGPU GFX7, KFD CIK, legacy DPM, and powerplay should compile without missing or renamed GDS, VGT, IA, WD, TCP, TC, CGTT, or DIDT macros.
- A generated-header comparison against AMD's register database should verify every `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` pair in lines 14180-18444, including indexed GDS VMID/GWS/OA families and replicated DIDT blocks.
- Field round-trip checks can validate representative macros such as `TCP_WATCH0_CNTL__VMID/VALID`, `GDS_GWS_VMID0__BASE/SIZE`, `GDS_OA_RESET_MASK`, `VGT_CACHE_INVALIDATION__CACHE_INVALIDATION/AUTO_INVLD_EN`, `VGT_DRAW_INITIATOR`, `IA_MULTI_VGT_PARAM`, and `DIDT_SQ_CTRL0__DIDT_CTRL_EN`.
- GFX7 hardware tests should cover graphics draws, tessellation, geometry shader paths, stream-out, indexed and instanced draws, compute queues using GDS/GWS/OA, and the `AMDGPU_IB_FLAG_RESET_GDS_MAX_WAVE_ID` path.
- KFD debug tests should program and clear TCP watchpoints across all four watch address slots and multiple VMIDs, confirming address high/low, mask, mode, and valid fields route correctly.
- Power-management tests should toggle DIDT through both legacy DPM and powerplay paths and confirm SQ/DB/TD/TCP throttling state changes without breaking suspend/resume, power-gating, or clock-gating transitions.
- Perf/debug validation should verify GDS, VGT, IA, and WD performance counter selection/readback and debug/status decode against expected hardware events.
