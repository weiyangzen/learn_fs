# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a6xx.xml lines 4707-5025

## Scope And Purpose

This chunk is the final section of the Freedreno `a6xx.xml` register database. It closes the main A6XX shader/HLSQ-related domain and then defines several small register domains for PDC sequencing, debug-bus control, and CX miscellaneous fuse/cache registers. The XML is declarative register metadata used by the MSM/Freedreno register-generation pipeline; it defines register names, offsets, bitfields, enum references, variant constraints, address alignment, and intended usage tags, but no C functions, structs, executable branches, locks, allocations, or persistence code.

The first lines are the end of the `SP_CS_WGE_CNTL` definition from the previous chunk. In this range, the remaining fields define A7XX workgroup tiling dimensions used when both x and y workgroup counts exceed one. The chunk then covers A7XX compute dispatch sizing, A6XX HLSQ/SP load-state and bindless mirrors, event initiator sequencing registers, A6XX/A7XX/A8XX update-control differences, HLSQ initialization/debug/performance registers, CP event start/end markers, and the final PDC/DBGC/CX_MISC domains.

Although this source path is under a `ceph-client` mirror, the file is Qualcomm Adreno GPU register metadata, not Ceph filesystem logic.

## Important APIs, Types, And Register Families

The exposed "API" is the generated register namespace. Downstream generated headers and packet-building code consume names such as `REG_A6XX_SP_UPDATE_CNTL`, `A6XX_SP_UPDATE_CNTL_FS_STATE`, or `A7XX_CX_MISC_SW_FUSE_VALUE_RAYTRACING` rather than hand-coded offsets and masks.

Major definitions in this chunk include:

- `SP_CS_WGE_CNTL` tail fields: `WGTILEWIDTH` and `WGTILEHEIGHT` describe tiled A7XX workgroup launch dimensions. The adjacent documentation says tiling is used only when both fields are nonzero and both x/y workgroup counts are greater than one.
- `SP_CS_NDRANGE_7`: A7XX command register carrying last-workgroup local sizes. `LOCALSIZEX`, `LOCALSIZEY`, and `LOCALSIZEZ` occupy bits 2:11, 12:21, and 22:31, with the XML comment noting that the encoded local size is value minus one.
- `HLSQ_LOAD_STATE_FRAG_CMD`, `HLSQ_LOAD_STATE_FRAG_EXT_SRC_ADDR`, and `HLSQ_LOAD_STATE_FRAG_DATA`: HLSQ-side load-state registers, including a 16-byte-aligned 64-bit external source address.
- `HLSQ_CS_BINDLESS_BASE` and `HLSQ_BINDLESS_BASE`: A6XX-only five-entry 64-bit descriptor arrays mirroring `SP_CS_BINDLESS_BASE` and `SP_GFX_BINDLESS_BASE`. Each descriptor has `DESC_SIZE` using `a6xx_bindless_descriptor_size` and an address field stored at bits 2:63 with a right shift of two.
- `HLSQ_CS_CTRL_REG1`: A6XX compute control mirror with `SHARED_SIZE` and `CONSTANTRAMMODE`. `CONSTANTRAMMODE` uses `a6xx_const_ram_mode`, whose values represent constant/local-memory splits such as 128, 192, 256, and A7XX-only 512 constant length.
- `SP_DRAW_INITIATOR`, `SP_KERNEL_INITIATOR`, and `SP_EVENT_INITIATOR`: state-id and event-trigger registers. The A6XX offsets are `0xbb00` through `0xbb02`; A7XX+ uses `0xab1c` through `0xab1e`. Event fields use the shared `vgt_event_type` enum from `adreno_pm4.xml`.
- `SP_UPDATE_CNTL`: command register that clears pending `CP_LOAD_STATE6` loads. A6XX has per-stage state bits, CS/GFX UAV bits, shared-constant invalidation bits, and five-bit CS/GFX bindless invalidation ranges. A7XX keeps per-stage and UAV bits but expands CS/GFX bindless ranges to eight bases. A8XX keeps only the per-stage state bits in this XML definition.
- `SP_CS_BINDLESS_INVALIDATE` and `SP_GFX_BINDLESS_INVALIDATE`: bindless invalidation registers without bitfield expansion in this chunk.
- `SP_PS_CONST_CONFIG`: pixel-shader constant configuration for A6XX at `0xbb10` and A7XX+ at `0xab03`, both using `a6xx_xs_const_config`.
- `SP_SHARED_CONSTANT_GFX`: A7XX/A8XX shared constant arrays, length 64 for A7XX and length 128 for A8XX+.
- `HLSQ_SHARED_CONSTS`: A6XX enable bit for shared constants intended for Vulkan push constants. The XML documents the special CP load-state routing and dword-based `DST_OFF`/`NUM_UNIT` units.
- `HLSQ_2D_EVENT_CMD`: 2D event command register with state id and `vgt_event_type`.
- HLSQ init/debug/perf registers: `HLSQ_UNKNOWN_BE00`, `HLSQ_UNKNOWN_BE01`, `HLSQ_DBG_ECO_CNTL`, `HLSQ_ADDR_MODE_CNTL`, `HLSQ_UNKNOWN_BE08`, `HLSQ_PERFCTR_HLSQ_SEL[6]`, and `HLSQ_CONTEXT_SWITCH_GFX_PREEMPTION_SAFE_MODE`.
- A7XX+ SP unknown/zero command registers: `SP_AHB_READ_APERTURE`, `SP_UNKNOWN_0CE2`, `SP_UNKNOWN_0CE4`, and `SP_UNKNOWN_0CE6`.
- CP event boundary registers: `CP_EVENT_START`, `CP_EVENT_END`, `CP_2D_EVENT_START`, and `CP_2D_EVENT_END`, each carrying an 8-bit `STATE_ID`.
- `A6XX_PDC`: GPU PDC enable, sequence start, and four TCS command-bank groups (`GPU_TCS0_*` through `GPU_TCS3_*`) for control, enable bank, wait-for-completion bank, message id, address, and data.
- `A6XX_PDC_GPU_SEQ`: a single sequencer memory register `MEM_0`.
- `A6XX_CX_DBGC` and `A7XX_CX_DBGC`: CX debug-bus selectors, control, masks, byte-lane selectors, trace buffers, and the A7XX shifted `CFG_DBGBUS_SEL_A.PING_BLK_SEL` layout.
- `A6XX_CX_MISC`: system cache controls, A7XX+ TCM retention control, A8XX slice enable, A7XX+ software fuse bits for `FASTBLEND`, `LPAC`, and `RAYTRACING`, plus A8XX+ frequency-limit status fields `FINALFREQLIMIT` and `SOFTSKUDISABLED`.

## Control Flow And Runtime Behavior

This XML has no executable control flow. Runtime behavior is created after the rnndb/XML definitions are converted into C register definitions and used by the MSM/Freedreno driver, Mesa/Freedreno tooling, or other register consumers.

The key sequencing behavior described in the chunk is hardware-facing:

1. `CP_LOAD_STATE6` packets queue shader, UBO, texture, sampler, UAV, shared constant, and bindless state loads.
2. Writes to `SP_UPDATE_CNTL` clear selected pending load-state categories. The exact clear mask is generation-dependent: A6XX has five bindless bases and shared-constant bits, A7XX has eight bindless bases, and A8XX only declares per-stage state bits here.
3. `HLSQ_SHARED_CONSTS.ENABLE` changes how push/shared constants are allocated and loaded on A6XX. Graphics shared constants are written through `ST6_CONSTANTS/SB6_UAV` using `CP_LOAD_STATE6`, while the compute shared-constant pool is loaded via `CP_LOAD_STATE6_FRAG` with `ST6_UBO/ST6_UAV`; offsets and counts are in dwords instead of vec4 units.
4. Event processing uses a documented sequence: write an event command pipe register, write `CP_EVENT_START`, write the SP initiator with an event or draw initiator, write the corresponding PC initiator, issue SP and PC `CONTEXT_DONE`, and finally write `CP_EVENT_END`. The comment notes that writing `CP_EVENT_END` appears to actually trigger the context roll.
5. PDC registers program low-power controller/TCS command sequences through enable-bank, wait-for-completion, message-id, address, and data registers. Driver code writes these during GMU/PDC setup rather than during ordinary draw dispatch.

The source tree has direct C uses of some generated names from this chunk. `a6xx_gmu.c` writes `REG_A6XX_PDC_GPU_ENABLE_PDC`, reads/writes `REG_A7XX_CX_MISC_SW_FUSE_VALUE`, and uses the generated `A7XX_CX_MISC_SW_FUSE_VALUE_*` bit names to report or override raytracing/LPAC/fastblend capability bits. `a6xx_gpu.c` and `a8xx_gpu.c` also read the CX_MISC fuse and frequency-limit status fields. Many SP/HLSQ names are register-database contracts for generated headers and command-stream emitters even when this mirror does not show a direct C reference to every symbolic name.

## State And Persistence Behavior

The XML itself stores no runtime state. It describes hardware state that persists in GPU registers until overwritten, reset, power-collapsed, or restored by initialization/resume paths.

State represented by this chunk includes compute dispatch geometry, local-size encoding, HLSQ/SP load-state staging, bindless descriptor base addresses, constant/local-memory partition mode, shared constant enablement and contents, pending state-load invalidation masks, event state IDs, debug-bus selection and trace controls, PDC/TCS command configuration, software fuse capability bits, and A8XX frequency-limit status.

Several fields are sequencing-sensitive rather than ordinary configuration:

- `SP_UPDATE_CNTL` is a clear/control register for queued state loads, so stale or overbroad bits can drop pending shader resource updates.
- Event start/end registers and initiators are part of a strict context-roll/event protocol. `STATE_ID` values must match the surrounding event command stream.
- Bindless base descriptors include encoded descriptor size and shifted GPU addresses; alignment and descriptor-size interpretation must match the resource tables being referenced.
- `HLSQ_SHARED_CONSTS.ENABLE` changes constant-pool layout and CP packet units, so command-stream generation must keep the enable bit, constant register allocation, and load-state packet encoding consistent.
- CX_MISC fuse fields may represent hardware capability or SKU state. Some code writes software fuse overrides during GMU initialization, while later code reads the same register to decide whether features such as raytracing or LPAC should be exposed.
- `CX_MISC_SW_FUSE_FREQ_LIMIT_STATUS` is status-like and should be treated as hardware/firmware-owned readback rather than a normal driver-owned setting.

## Dependencies And Integration Points

This chunk depends on shared rnndb types and nearby `a6xx.xml` definitions:

- `vgt_event_type` from `adreno_pm4.xml` supplies event encodings such as `CONTEXT_DONE`, cache flushes, primitive counters, fragment/compute counters, and CCU invalidate events.
- `a5xx_address_mode` from `adreno_common.xml` supplies 32-bit versus 64-bit address-mode encoding for `HLSQ_ADDR_MODE_CNTL`.
- `a6xx_const_ram_mode`, `a6xx_bindless_descriptor_size`, `a6xx_xs_const_config`, and the SP/GFX bindless base arrays are defined earlier in `a6xx.xml` and referenced here.
- `PC_EVENT_INITIATOR` is defined earlier in the same XML and is explicitly part of the event sequence comment in this chunk.

Driver integration points include:

- GMU/PDC initialization through `a6xx_gmu.c`, especially `REG_A6XX_PDC_GPU_ENABLE_PDC` and CX_MISC fuse programming/readback.
- GPU capability discovery in A6XX/A8XX paths through generated `A7XX_CX_MISC_SW_FUSE_VALUE_*` and `A8XX_CX_MISC_SW_FUSE_FREQ_LIMIT_STATUS_*` fields.
- Command-stream emission for compute dispatch, shader state loading, bindless descriptor bases, shared constants/push constants, UAV/texture/sampler invalidation, and event/context-roll sequencing.
- Debug and profiling flows that select CX debug-bus signals or HLSQ performance counters.
- Register generation tooling that converts XML domains, arrays, variants, alignment, `usage` tags, and bitfield types into C macros/helpers.

Variant annotations are an important integration contract. Several logical registers keep the same name but move offsets or change field width across A6XX, A7XX, and A8XX. Consumers must select the generated definition for the active GPU generation rather than assuming offset or bit layout stability.

## Risks And Edge Cases

- The chunk starts inside `SP_CS_WGE_CNTL`; the register name and earlier bitfields are in the previous chunk. Final per-file reconciliation should merge that boundary before making complete claims about workgroup execution control.
- `SP_CS_NDRANGE_7` encodes local size as value minus one and begins at bit 2. Treating the field as a direct size or using the wrong shift can produce incorrect last-workgroup dimensions or invalid dispatches.
- `SP_UPDATE_CNTL` differs by generation. Reusing the A6XX five-base bindless/shared-constant layout on A7XX/A8XX, or using A7XX eight-base masks on A6XX, can silently clear the wrong pending state or fail to clear required state.
- Shared constants alter both constant-pool allocation and load-state packet units. If `HLSQ_SHARED_CONSTS.ENABLE`, `CP_LOAD_STATE6` packet type, `DST_OFF`, `NUM_UNIT`, and shader constant register allocation disagree, Vulkan push constants or compute constants can be corrupted.
- Bindless descriptors combine descriptor-size encoding with shifted GPU addresses. Bad descriptor-size values, missing 16-byte alignment, or address shift mistakes can point the shader core at the wrong descriptor table.
- Event initiator sequencing is timing- and order-sensitive. Missing `CONTEXT_DONE`, mismatched `STATE_ID`, or writing `CP_EVENT_END` too early can break context rolls, counters, cache flush completion, or timestamp/event completion semantics.
- Unknown registers (`HLSQ_UNKNOWN_BE00`, `HLSQ_UNKNOWN_BE01`, `HLSQ_UNKNOWN_BE08`, `SP_UNKNOWN_0CE2` and peers) should not be generalized beyond the documented usage and variants. Comments such as "all bits valid except bit 29" are reverse-engineering notes, not full public programming-model guarantees.
- Debug-bus fields are narrow and generation-shifted. A7XX moves `CFG_DBGBUS_SEL_A.PING_BLK_SEL` from bits 8:15 to bits 16:24, so cross-generation debug tooling can select the wrong block if it ignores variants.
- CX_MISC fuse bits control visible feature decisions. Incorrect register definitions or writes can expose unsupported capabilities, hide supported features, or misread A8XX speed-bin/frequency-limit status.
- PDC/TCS programming affects power-controller sequencing. Wrong offsets or bank/wait/message/address/data values can cause power transition hangs or incomplete low-power entry/exit.

## Test Signals

Useful validation signals for this chunk include:

- Regenerate the MSM/Freedreno register headers from `a6xx.xml` and build the DRM MSM Adreno driver; this catches malformed XML, missing enum/type references, duplicate variant conflicts, and generated-name drift.
- Build-test A6XX, A7XX, and A8XX configurations that consume generated `REG_A6XX_PDC_GPU_ENABLE_PDC`, `REG_A7XX_CX_MISC_SW_FUSE_VALUE`, `A7XX_CX_MISC_SW_FUSE_VALUE_{FASTBLEND,LPAC,RAYTRACING}`, and `A8XX_CX_MISC_SW_FUSE_FREQ_LIMIT_STATUS_FINALFREQLIMIT`.
- Runtime compute tests should cover A7XX workgroup tiling, last-workgroup local-size handling, and nontrivial x/y/z dispatch shapes.
- Vulkan push-constant and compute constant tests should exercise `HLSQ_SHARED_CONSTS`, `CP_LOAD_STATE6`, `CP_LOAD_STATE6_FRAG`, shared constant invalidation, and dword-based offset/count handling.
- Bindless-resource tests should use all valid bindless bases for the target generation, both 16-byte and 64-byte descriptor sizes where supported, and resource-table addresses that verify the stored address shift and alignment.
- Event tests should check cache flush/timestamp completion, primitive/fragment/compute counters, context roll completion, and 2D event paths while monitoring for hangs or missed completions.
- Suspend/resume and power-collapse tests should validate PDC programming, GMU initialization, TCS command sequencing, and restoration of HLSQ/SP state after reset.
- Debug/profiling validation should read HLSQ perf counters and CX debug-bus trace buffers, including the A7XX shifted selector layout.
- Capability discovery tests should compare reported raytracing, LPAC, fastblend, slice, and speed-bin/frequency-limit values against known SKU expectations and firmware/GMU behavior.

## Cross-Chunk Notes

The previous chunk is required for the start of `SP_CS_WGE_CNTL`, the compute dispatch register family, enum definitions, and the SP bindless base definitions mirrored by HLSQ in this range. This chunk closes `a6xx.xml`, so there is no following chunk for this source file content; the later merge/reconciliation lane should combine this terminal document with earlier chunks before producing a complete per-file report.
