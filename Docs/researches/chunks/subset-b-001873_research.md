# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 20111-22625

## Purpose

This chunk is generated AMD DCN 3.1.5 register field metadata. It contains no executable C logic; it publishes preprocessor constants for MMIO register field shifts and masks used by AMDGPU display code when programming color-management, DPP, MPC, MPCC, output-gamma, performance-monitor, update-lock, DWB, and related display-composition blocks.

The requested range covers 2,515 physical lines with 2,101 `#define` entries: 1,052 `__SHIFT` macros and 1,057 `_MASK` macros. It begins inside the `CM3` shaper RAMB register family, after neighboring lines already defined the CM3 shaper RAMB start controls and most B/G end controls. It then covers CM3 shaper RAMB region descriptors, CM3 shaper/3DLUT memory-power and LUT access fields, DPP top and CRC/control fields for DPP3, DC performance-monitor block 14, MPCC0 through MPCC3 blend/composition controls, global MPC control/update-lock/DWB mux fields, DC performance-monitor block 15, complete MPCC_OGAM0 and MPCC_OGAM1 output-gamma/gamut-remap register families, and the beginning of MPCC_OGAM2 through `MPCC_OGAM2_MPCC_OGAM_RAMB_REGION_12_13`.

Although the repository path is under a `ceph-client` source mirror, this header is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, or allocation paths in this chunk. The interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

These constants are consumed with the matching DCN 3.1.5 offset header and register helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, `FD_SHIFT`, `SF`, and `SRI`. Direct DCN 3.1.5 users include `dmub_dcn315.c`, `irq_service_dcn315.c`, `hw_factory_dcn315.c`, `hw_translate_dcn315.c`, and `dcn315_resource.c`; the color and MPC families are also matched by generic DPP/MPC register-list and field-list macros under `display/dc/dpp` and `display/dc/mpc`.

Major register families in this slice:

- `CM3_CM_SHAPER_RAMB_*`, `CM3_CM_MEM_PWR_CTRL2`, `CM3_CM_MEM_PWR_STATUS2`, and `CM3_CM_3DLUT_*`: DPP instance 3 color-management shaper RAM B piecewise-linear region layout, shaper/HDR 3DLUT memory power control/status, 3DLUT mode/size/current mode, index/data writes, 30-bit data access, RAM selection, read/write control, output normalization, output offsets, and debug index/data.
- `DPP_TOP3_*`: DPP instance 3 top-level enable, clock gating, soft reset, CRC values/control, and host-read control.
- `DC_PERFMON14_*` and `DC_PERFMON15_*`: performance-counter and performance-monitor control/state/value registers for the DPP3 and MPC performance-monitor address blocks.
- `MPCC0_*` through `MPCC3_*`: MPCC top/bottom source selection, OPP routing, composition mode, alpha/blend control, update-lock selection, top/bottom gains, background color components, memory power controls for the MPCC and OGAM memories, and status fields.
- `MPC_*`, `ADR_CFG_*`, `ADR_VUPDATE_*`, `CFG_VUPDATE_*`, `CUR_VUPDATE_*`, and `MPC_DWB0_MUX`: global MPC clock/reset/CRC/perf controls, bypass background, host-read control, DPP pending status, update-lock set address/config/current state for sets 0 through 3, DWB mux selection/status, and pending/vertical-update coordination fields.
- `MPCC_OGAM0_*` and `MPCC_OGAM1_*`: complete output-gamma blocks for MPCC instances 0 and 1, including OGAM control/current state, LUT index/data/control, RAM A and RAM B start/end/base/slope/offset/region descriptors, gamut-remap coefficient format/mode, and two banks of gamut-remap matrix coefficients.
- `MPCC_OGAM2_*`: start of the same output-gamma family for MPCC instance 2, from OGAM control/LUT controls through RAM A and the beginning of RAM B region descriptors. The chunk ends before the instance-2 RAMB region table and gamut-remap matrix are complete.

## Control Flow

This header has no runtime control flow. Runtime sequencing is provided by AMD display code:

1. DCN 3.1.5 resource, GPIO, IRQ, and DMUB code include `dcn_3_1_5_offset.h` and this `dcn_3_1_5_sh_mask.h` header.
2. Register-list macros paste instance, register, and field names into constants such as `CM3_CM_3DLUT_MODE__CM_3DLUT_MODE_MASK`, `MPCC0_MPCC_CONTROL__MPCC_MODE_MASK`, or `MPCC_OGAM1_MPCC_OGAM_RAMA_REGION_0_1__MPCC_OGAM_RAMA_EXP_REGION0_LUT_OFFSET_MASK`.
3. Hardware abstraction tables store offsets plus field shifts/masks, then `REG_*` helper calls perform MMIO reads, writes, waits, and read-modify-write updates against those fields.
4. Display runtime paths use those tables during modeset, pipe composition, DPP color programming, MPCC blend programming, output-gamma and gamut-remap updates, memory power transitions, CRC/debug capture, performance monitoring, vertical-update lock coordination, DWB routing, and suspend/resume restoration.

The macros do not encode ordering or access semantics. Consumers must still respect hardware sequencing: power OGAM/3DLUT memories before writing LUT RAM, select the correct RAM bank before loading or switching LUTs, coordinate update locks with vupdate timing, wait on current/status fields before assuming a bank or mode is active, and avoid unsafe writes to status or debug fields.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on its own. It describes hardware register fields whose values live in the display ASIC.

Hardware state represented by these fields includes CM3 shaper region tables, CM3 3DLUT index/data/output normalization state, DPP3 enable/reset/CRC/debug state, MPCC source selection and blending state, MPCC memory power state, MPCC background colors and gains, MPC clock/reset/CRC/performance state, pending DPP/update-lock state, DWB mux routing state, MPCC_OGAM LUT bank selection and contents, PWL region geometry, gamut-remap matrix values, and current-mode/status fields.

Persistence is hardware-defined. Programming fields generally remain until another modeset/color update changes them, display blocks are power-gated, suspend/resume reinitializes the display engine, or the ASIC is reset. Status-like fields such as `*_CURRENT`, `*_STATUS`, `*_STATE`, `*_PENDING`, `*_MEM_PWR_STATE`, CRC values, and performance-counter values may be read-only, sticky, self-clearing, or write-one-to-clear depending on the register specification. This generated header only gives bit positions and masks; it does not define access type or side effects.

## Dependencies And Integration Points

The constants in this range must match `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h` and the DCN base-address definitions in the consumers. They are token-pasted by the display register helpers, so spelling, instance prefix, and mask width are part of the ABI between the generated register database and the C hardware-block tables.

Important in-tree integration points include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, which includes this header, defines DCN base segments, and expands resource register tables for DCN 3.1.5 hardware blocks.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`, which expands DMUB register masks and shifts through `DMUB_DCN315_FIELDS()` using `FD_MASK` and `FD_SHIFT`.
- `drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`, which includes the same offset and shift/mask headers for interrupt enable/ack register descriptions.
- `drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c` and `hw_translate_dcn315.c`, which use the generated DCN 3.1.5 register metadata for GPIO/AUX/DDC translation even though this specific chunk is mostly color/MPC-oriented.
- `drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp.h`, whose color-management field lists include CM shaper, 3DLUT, memory-power, debug, and DPP top fields that map to the CM3/DPP_TOP3 families in this chunk.
- `drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.h` and `dcn30_mpc.c`, whose MPCC/OGAM register lists and functions consume the MPCC, MPCC_OGAM, MPC update-lock, DWB, and memory-power fields represented here.

The chunk is boundary-sensitive. The previous chunk owns the earlier CM3 shaper RAMA/RAMB setup fields, including the start of RAMB end controls. The next chunk must finish MPCC_OGAM2 RAMB regions and the remaining instance-2 gamut-remap fields before final file-level research makes complete claims about MPCC_OGAM2.

## Risks And Edge Cases

- Shift/mask drift is the primary risk. These are untyped preprocessor constants; an incorrect mask can compile cleanly while writing the wrong hardware bits.
- The repeated MPCC and MPCC_OGAM families are copy-sensitive. A prefix error between MPCC0/1/2/3 or RAMA/RAMB can affect only one pipe, one LUT bank, or one color path, making failures mode-dependent.
- LUT programming is stateful. CM3 and MPCC_OGAM index/data/control fields depend on host selection, color write masks, active RAM bank, PWL enable/disable state, and memory power state. Updating the wrong bank or writing while memory is powered down can cause visible color corruption or failed updates.
- Update-lock and vupdate fields are timing-sensitive. Incorrect address/config/current update-lock masks can leave pipe state stuck pending, applied outside vblank, or mismatched across multi-plane composition.
- MPCC composition fields affect blending and routing. Bad top/bottom selection, OPP ID, gain, alpha, background, or mode fields can produce missing planes, incorrect blending, wrong output routing, or artifacts that only appear with overlays, MPO, or DWB.
- Status, CRC, perfmon, and debug registers may have non-obvious read/clear behavior. Generic read-modify-write against fields with side effects can lose events or corrupt counters.
- Full-width or broad masks such as background colors, coefficients, CRC values, and debug data need value-range discipline from consumers; the header does not validate fixed-point formats or coefficient sign/scale.

## Test Signals

Useful validation combines generated-header consistency, build coverage, and display behavior:

- Build AMDGPU display paths for DCN 3.1.5 so includes of `dcn_3_1_5_sh_mask.h`, `dcn315_resource.c`, DMUB, IRQ, GPIO, DPP, and MPC tables catch missing or renamed macros.
- Mechanically verify that complete fields in lines 20111-22625 have matching `__SHIFT` and `_MASK` definitions, while accounting for intentional boundary exceptions at the start of CM3 RAMB end controls and the end of MPCC_OGAM2 RAMB regions.
- Compare this chunk against AMD's authoritative DCN 3.1.5 register database and adjacent DCN generation headers where MPCC, OGAM, DPP, and perfmon layouts are expected to match.
- Exercise color-management paths on DCN 3.1.5 hardware: shaper LUT, 3DLUT, OGAM LUT, RAM A/RAM B bank switching, gamut-remap matrices, bypass modes, HDR/SDR transitions, and suspend/resume with color state restored.
- Test MPCC composition behavior with single-plane, multi-plane overlay, alpha blending, underlay/background color, pipe split, and DWB capture/routing scenarios.
- Validate vupdate/update-lock behavior during page flips, modesets, MPO transitions, and color updates, watching for stuck pending status or updates applied on the wrong frame.
- Validate memory-power sequencing by enabling/disabling OGAM and 3DLUT paths across blank/unblank and power-management transitions, checking waits on memory state and absence of LUT write failures.
- Use CRC, perfmon, and debug paths where available to detect whether DPP3/MPC register programming produces expected counters, CRC values, and no unexpected pending/error states.

## Cross-Chunk Notes

This chunk starts at `CM3_CM_SHAPER_RAMB_END_CNTL_R`; `CM3_CM_SHAPER_RAMB_START_CNTL_*` and the B/G end-control definitions are in the previous chunk. It ends inside `MPCC_OGAM2_MPCC_OGAM_RAMB_REGION_12_13`; the next chunk should continue with the remaining MPCC_OGAM2 RAMB region descriptors and then cover the instance-2 gamut-remap fields. The final per-file document should merge those boundaries before summarizing complete CM3 shaper RAMB or MPCC_OGAM2 behavior.
