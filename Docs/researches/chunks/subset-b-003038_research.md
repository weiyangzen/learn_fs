# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 81237-83977

## Scope

This chunk is a generated AMDGPU NBIO 6.1 shift/mask header segment. It contains C preprocessor constants only; there are no functions, structs, enums, global variables, branches, loops, allocation paths, locks, or direct hardware accesses in this range.

The assigned range starts in the middle of `DWC_E12MP_PHY_X4_NS_X4_1_LANEX_ANA_RX_ATB_VREG`, after that register's field shift macros and first mask macro were defined just above the chunk. It then covers a dense raw common digital memory table for the second `DWC_E12MP_PHY_X4_NS_X4` PHY instance. The chunk ends exactly at `DWC_E12MP_PHY_X4_NS_X4_1_RAWCMNX_DIG_MEM_CMN5_B4_R14__DATA_MASK`; `CMN5_B4_R15` and later rows continue in the following source lines.

Within the chunk there are 1,830 `#define` rows. Eight are the tail masks for `LANEX_ANA_RX_ATB_VREG`. The remaining 1,822 rows are paired `__DATA__SHIFT` and `__DATA_MASK` definitions for 911 `RAWCMNX_DIG_MEM` rows:

- complete `RAWCMNX_DIG_MEM_CMN2` banks `B0` through `B7`, registers `R0` through `R31`;
- complete `RAWCMNX_DIG_MEM_CMN3` banks `B0` through `B7`, registers `R0` through `R31`;
- complete `RAWCMNX_DIG_MEM_CMN4` banks `B0` through `B7`, registers `R0` through `R31`;
- partial `RAWCMNX_DIG_MEM_CMN5`, covering full banks `B0` through `B3` and `B4_R0` through `B4_R14`.

Although this path is under a local `ceph-client` mirror, this file is AMDGPU hardware register metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`nbio_6_1_sh_mask.h` is the generated bitfield-layout half of AMD's NBIO 6.1 register interface. For each generated register field it publishes compile-time constants of the form:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to position or extract a field;
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, clear, or set the field.

This specific chunk describes two kinds of PHY-related fields. The opening lines complete mask definitions for an analog RX ATB voltage-regulator control/status register under `LANEX`. Those bits cover IQC voltage-reference override, ATB measurement selection for IQC scope/IQC/DFE-bypass/DFE paths, regulator-reference overrides, and reserved upper bits. The rest of the chunk describes raw common digital memory rows for the `NS_X4_1` PCIe PHY. Each raw memory row exposes a single 16-bit `DATA` field at shift `0x0` with mask `0xFFFFL`.

The raw `CMN*_B*_R*` names are generated table coordinates rather than semantically rich field names. They are best treated as opaque Synopsys/AMD PHY programming or metadata rows unless cross-referenced with the authoritative register database and matching defaults. The adjacent `nbio_6_1_default.h` header contains defaults for these same rows, including `smnDWC_E12MP_PHY_X4_NS_X4_1_LANEX_ANA_RX_ATB_VREG_DEFAULT`, `smnDWC_E12MP_PHY_X4_NS_X4_1_RAWCMNX_DIG_MEM_CMN2_B0_R0_DEFAULT`, and `smnDWC_E12MP_PHY_X4_NS_X4_1_RAWCMNX_DIG_MEM_CMN5_B4_R14_DEFAULT`.

## Important Macro Families

`DWC_E12MP_PHY_X4_NS_X4_1_LANEX_ANA_RX_ATB_VREG` is the only named, non-raw field register visible in this chunk. The chunk includes masks for:

- `ovrd_iqc_vref_sel`;
- `meas_atb_vreg_iqc_scope`;
- `meas_atb_vreg_iqc`;
- `meas_atb_vreg_dfe_byp`;
- `meas_atb_vreg_dfe`;
- `ovrd_regref_iqc_scope`;
- `ovrd_regref_iqc`;
- `RESERVED_15_8`.

The corresponding shifts, plus the `ovrd_rx_slicer_ctrl_reg` field and mask, are immediately before this range. Any complete analysis or generator check for this register must include the previous chunk.

`DWC_E12MP_PHY_X4_NS_X4_1_RAWCMNX_DIG_MEM_CMN2_*` is complete in this slice. It covers eight banks, each with 32 raw 16-bit data rows. The uniform macro pattern is:

- `DWC_E12MP_PHY_X4_NS_X4_1_RAWCMNX_DIG_MEM_CMN2_Bn_Rm__DATA__SHIFT` set to `0x0`;
- `DWC_E12MP_PHY_X4_NS_X4_1_RAWCMNX_DIG_MEM_CMN2_Bn_Rm__DATA_MASK` set to `0xFFFFL`.

`DWC_E12MP_PHY_X4_NS_X4_1_RAWCMNX_DIG_MEM_CMN3_*` repeats the same complete eight-bank, 32-row-per-bank layout. No field subdivision is exposed beyond the full 16-bit `DATA` payload.

`DWC_E12MP_PHY_X4_NS_X4_1_RAWCMNX_DIG_MEM_CMN4_*` also repeats the same complete eight-bank layout. The repetition across `CMN2`, `CMN3`, and `CMN4` is significant because callers must still use the exact macro name matching the selected register/default row; the identical shift and mask values do not make the register rows interchangeable.

`DWC_E12MP_PHY_X4_NS_X4_1_RAWCMNX_DIG_MEM_CMN5_*` is partial at the end of this work item. It covers all of `B0`, `B1`, `B2`, and `B3`, then `B4_R0` through `B4_R14`. The source immediately after this range continues with `B4_R15`, so the final per-file merge should not present this chunk as a complete `CMN5` table.

## APIs, Types, And Functions

There are no callable APIs, C types, or functions in this chunk. The exported interface is the generated macro namespace consumed by C files that include `asic_reg/nbio/nbio_6_1_sh_mask.h` or `nbio/nbio_6_1_sh_mask.h`.

Direct include users in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, and Vega power-management include wrappers such as `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h`. These include sites do not imply that every macro in this chunk is referenced directly; generated ASIC register headers intentionally expose a broader register database than any individual driver path uses.

The constants are untyped preprocessor integer literals, mostly using an `L` suffix. They encode only field position and mask. They do not encode access width, address, reset value, read/write permission, write-one-to-clear behavior, hardware sequencing, timing, firmware ownership, or side effects.

## Control Flow

This header range has no local control flow. Runtime behavior is in including code:

1. AMDGPU code selects a register address or SMN/config-space access path from the generated offset/SMN metadata or from a higher-level hardware table.
2. The code reads a register or composes a value through AMDGPU register helpers.
3. It applies these `__SHIFT` and `_MASK` constants directly or through helpers such as `REG_GET_FIELD` and `REG_SET_FIELD`.
4. The decoded or composed value is used for PHY programming, diagnostics, reset handling, link bring-up, power-management policy, or hardware state comparison.

For the raw memory rows, the macros simply describe that the useful payload occupies bits 15:0. The order of rows in the header follows the generated register database, not an executable initialization sequence. Software must not infer programming order, polling requirements, or dependency ordering from this chunk alone.

## State And Persistence Behavior

The header stores no software state and persists nothing. It describes hardware-backed NBIO/PHY state for the `DWC_E12MP_PHY_X4_NS_X4_1` block.

The `LANEX_ANA_RX_ATB_VREG` masks correspond to analog RX voltage-regulator override and measurement-selection bits. Depending on the underlying hardware semantics, these may affect debug/measurement routing, slicer/IQC/DFE voltage references, analog test-bus observation, or reserved-bit preservation. The mask definitions alone do not identify which bits are firmware-owned, software-writable, debug-only, sticky, read-only, or safe to modify during live link operation.

The `RAWCMNX_DIG_MEM` rows represent raw common digital PHY table entries. Their state may be initialized by hardware reset values, firmware, driver programming, link-training firmware flows, or internal PHY state machines. The paired defaults in `nbio_6_1_default.h` show nonzero values for many of these rows, so treating the table as blank storage would be wrong. The rows are also likely reset-domain sensitive: GPU reset, PCIe/link reset, suspend/resume, runtime power transitions, or firmware reinitialization may change whether software-observed values match the generated defaults.

Since every raw row has the same `DATA` shift and mask, the macro names are the primary identity. Losing the `CMN`, bank, row, or `NS_X4_1` instance component can silently redirect code to the wrong PHY table entry while preserving plausible bit arithmetic.

## Dependencies And Integration Points

This chunk depends on consistency with the rest of AMD's generated NBIO 6.1 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h` provides matching `*_DEFAULT` values for the visible `LANEX_ANA_RX_ATB_VREG` and `RAWCMNX_DIG_MEM` rows.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h` and `nbio_6_1_smn.h` provide the broader generated address metadata used by NBIO consumers, though quick source lookup shows these exact raw rows are primarily mirrored in the default and shift/mask headers in this tree.
- AMDGPU register helper conventions provide the actual read/modify/write mechanics.

Runtime integration is with AMDGPU NBIO initialization, PCIe PHY/PCS setup, link management, clock/power transitions, GPU reset and resume flows, SR-IOV/MxGPU paths that include NBIO 6.1 metadata, and Vega power-management code that aggregates the generated register headers. Broader system integration includes platform firmware, PCIe link training, board-specific PHY tuning, and any diagnostic or debug tooling that reads raw NBIO/PHY state.

The repeated `NS_X4_0`, `NS_X4_1`, `NS_X4_2`, and `NS_X4_3` families elsewhere in this same header show that this chunk is specifically for the second x4 PHY instance. Cross-instance copy errors can be hard to see because the raw `DATA` shifts and masks are identical across instances.

## Risks And Edge Cases

- The chunk boundaries are artificial. The first lines are only the tail masks for `LANEX_ANA_RX_ATB_VREG`, and the final line stops mid `CMN5_B4`. Adjacent chunks are required for a complete logical view.
- These are generated, untyped macros. A generator drift, stale mask, or renamed row can compile cleanly while causing software to touch the wrong hardware bit or table entry.
- The raw memory rows expose only a full-width 16-bit `DATA` field. Without generator context, individual bit meanings inside those 16 bits are opaque.
- Identical `0x0` shifts and `0xFFFFL` masks across 911 raw rows make name identity more important than value identity. Accidentally using a `CMN3` row where a `CMN4` row is required will not be caught by type checking.
- The `NS_X4_1` instance component matters. Using an `NS_X4_0`, `NS_X4_2`, or `NS_X4_3` macro with an `NS_X4_1` address/default path can create cross-lane or cross-physical-instance PHY bugs.
- Analog RX override and ATB measurement bits may be unsafe to modify during normal operation unless the hardware specification or firmware contract explicitly permits it.
- Reserved masks such as `RESERVED_15_8_MASK` must be preserved according to the hardware spec. Blind writes based on visible masks can disturb reserved fields if the call site does not read-modify-write correctly.
- Raw PHY memory defaults are board-, ASIC-, and firmware-sensitive. Hand-editing rows or using defaults as blind writeback data can destabilize PCIe link training, equalization, low-power transitions, or signal integrity.
- Because exact address macros for the visible raw rows are not surfaced by a simple source search in the companion address headers, consumers may reach them through generated indirect tables or firmware paths. Reviewers should verify the intended access path before assuming ordinary SOC15 register access.

## Test Signals

Useful validation for this chunk is mostly generated-header consistency and hardware/link integration testing:

- Build AMDGPU configurations that include NBIO 6.1, Vega10/Vega12 power-management, and MxGPU/SR-IOV relevant paths. Missing, duplicated, or malformed macros should fail compile-time consumers.
- Run generated-header consistency checks across `nbio_6_1_sh_mask.h` and `nbio_6_1_default.h` for the `NS_X4_1` raw common memory rows, especially boundary rows `CMN2_B0_R0`, `CMN4_B7_R31`, `CMN5_B4_R14`, and the next-row continuation `CMN5_B4_R15`.
- Verify all raw rows in this chunk keep `DATA__SHIFT == 0x0` and `DATA_MASK == 0xFFFFL`; any deviation would be high-signal because the whole visible table is uniform.
- Compare `NS_X4_1` raw memory rows against corresponding `NS_X4_0`, `NS_X4_2`, and `NS_X4_3` generated families where the hardware database expects parity.
- Boot supported NBIO 6.1 hardware and confirm PCIe link speed/width stability, absence of unexpected AER noise, and stable operation across GPU reset, suspend/resume, and runtime power transitions.
- Exercise high-throughput DMA and PCIe power-management scenarios such as ASPM or clock-gating transitions to expose bad PHY table or analog RX field definitions.
- If diagnostic access is available, spot-check raw PHY memory readbacks against defaults after reset and after firmware/driver initialization, recognizing that firmware may legitimately change some rows.
- For debug paths that use `LANEX_ANA_RX_ATB_VREG`, validate that reserved bits are preserved and that measurement/override changes are gated to safe states.

## Chunk Notes

- Lines 81237-81244 are the tail of `LANEX_ANA_RX_ATB_VREG` mask definitions; this chunk does not include that register's comment, shifts, or first mask.
- Lines 81245-82012 cover complete `RAWCMNX_DIG_MEM_CMN2`.
- Lines 82013-82780 cover complete `RAWCMNX_DIG_MEM_CMN3`.
- Lines 82781-83548 cover complete `RAWCMNX_DIG_MEM_CMN4`.
- Lines 83549-83977 cover partial `RAWCMNX_DIG_MEM_CMN5`, ending at `B4_R14`.
