# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 17599-20110

## Chunk Scope

This chunk is a generated AMD DCN 3.1.5 register shift/mask header fragment. It contains 2,114 preprocessor definitions: 1,057 `__SHIFT` constants and 1,057 matching `_MASK` constants. There is no executable C code, no structs, and no functions in this range. Its API surface is the macro namespace consumed by AMD display register helpers to pack, unpack, and update hardware register fields.

The slice covers the tail of DPP2 color management, DPP2 top/perfmon controls, DPP3 converter/cursor/scaler controls, and the beginning-to-mid section of DPP3 color management. The requested boundary ends at line 20110 in the middle of `CM3_CM_SHAPER_RAMB_END_CNTL_G`; later fields for that register and later CM3 shaper RAMB registers are outside this chunk.

## Purpose

The purpose of this chunk is to describe bit positions and masks for display pipe processor register fields. These constants let driver code use generic AMD DC helpers such as field-write/read macros without hardcoding numeric bit ranges at each call site. The values are hardware ABI, not algorithmic behavior: correctness depends on matching the silicon register specification for DCN 3.1.5.

Major covered hardware areas:

- `CM2_*`: DPP2 color management tail, including blend gamma RAMB regions, HDR multiplier, memory power control/status, dealpha, coefficient formats, shaper LUT/RAM A/B definitions, 3D LUT, and debug registers.
- `DPP_TOP2_*`: DPP2 top-level clock gates, soft reset, CRC value/control, and host read-rate fields.
- `DC_PERFMON13_*`: DPP2 display performance monitor counter control, state, interrupt/status, counter value, high/low readback fields.
- `CNVC_CFG3_*` and `CNVC_CUR3_*`: DPP3 converter format, color keyer, pre-CSC, pre-degamma, realpha, and cursor format/color fields.
- `DSCL3_*`: DPP3 scaler coefficient RAM, mode/taps, ratios, init phases, overscan, recout/MPC geometry, line-buffer state, memory power, and output buffer controls.
- `CM3_*`: DPP3 color management controls for post-CSC, gamut remap, bias, gamma correction RAM A/B, blending gamma RAM A/B, HDR multiplier, memory power, dealpha, coefficient format, and the beginning of shaper LUT/RAM A/B.

## Important APIs and Macro Patterns

Every field is exported as two macros:

- `<REGISTER>__<FIELD>__SHIFT`: the least significant bit position for the field.
- `<REGISTER>__<FIELD>_MASK`: the register mask for that field.

Driver-side register helpers combine these two values to clear, shift, set, and read fields. The include is pulled into DCN 3.1.5 integration files including `display/dmub/src/dmub_dcn315.c`, `display/dc/irq/dcn315/irq_service_dcn315.c`, `display/dc/gpio/dcn315/hw_factory_dcn315.c`, `display/dc/gpio/dcn315/hw_translate_dcn315.c`, and `display/dc/resource/dcn315/dcn315_resource.c`. General helper macros in `display/dc/dm_services.h` construct references such as `reg_name__reg_field_MASK` and `reg_name__reg_field__SHIFT`, so spelling and suffix format are part of the public compile-time contract.

Notable macro groups in this chunk:

- Gamma/shaper region pairs use a repeated two-region packing layout: region `N` LUT offset at bit 0 or 16, region segment count at bit 12 or 28, with masks like `0x000001FFL`, `0x00007000L`, `0x01FF0000L`, and `0x70000000L`.
- Color-matrix coefficient pairs pack two 16-bit fields per register, for example `C11_C12`, `C13_C14`, through `C33_C34`, with masks `0x0000FFFFL` and `0xFFFF0000L`.
- Many status/control fields have corresponding current or pending status bits, such as `CM*_UPDATE_PENDING`, `*_MODE_CURRENT`, `SCL_UPDATE_PENDING`, and `CUR0_UPDATE_PENDING`.
- Full-register read/value fields use `0xFFFFFFFFL`, for example performance monitor low values and debug data.

## Control Flow

There is no runtime control flow in the chunk. The effective control flow is at compile time:

1. A DCN 3.1.5 C source includes this header together with matching offset headers.
2. Register-list macros in resource or block-specific source files expand field names into the corresponding `_MASK` and `__SHIFT` constants.
3. Runtime code calls register access helpers to update memory-mapped display registers.
4. The helper uses the constants to preserve unrelated fields, encode new field values, or extract current hardware state.

Because the constants are generated, review should focus on structural consistency: every shift should have a mask, each register field should fit within 32 bits, and mirrored pipes/blocks should keep the same layout unless the ASIC spec says otherwise.

## State and Persistence Behavior

The file itself persists no state. The state described by the macros is hardware state in display registers:

- Color management state includes LUT indices/data, RAM A/B region tables, CSC/gamut matrices, bias, HDR multiplier, shaper and 3D LUT modes.
- Power-management state includes memory force/disable bits and status fields for gamma correction, blending gamma, shaper, 3D LUT, scaler LUT/line-buffer groups, and OBUF memory.
- Synchronization/readback state includes update-pending, mode-current, CRC, perfmon active, counter state, interrupt status/ack, and cursor/scaler update-pending bits.

Persistence is therefore governed by hardware register lifetime, display pipeline programming sequences, resets, and power gating. Wrong masks can persist incorrect hardware state until the affected block is reprogrammed or reset.

## Dependencies and Integration Points

This chunk depends on:

- Matching DCN 3.1.5 offset headers that define the register addresses for these field masks.
- AMD display helper macros in `display/dc/dm_services.h`, especially helpers that concatenate register and field names with `_MASK` and `__SHIFT`.
- DC resource construction for DCN 3.1.5, where block register lists and mask/shift lists are assembled into per-block register tables.
- Block implementations for color management, cursor/converter, scaler, CRC, perfmon, and power management that expect these fields to match the actual hardware.

Integration boundaries visible in the chunk:

- `addressBlock: dce_dc_dpp2_dispdec_dpp_top_dispdec` starts DPP2 top-level fields after CM2 color-management fields.
- `addressBlock: dce_dc_dpp2_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` starts performance-monitor fields.
- `addressBlock: dce_dc_dpp3_dispdec_cnvc_cfg_dispdec`, `cnvc_cur`, `dscl`, and `cm` start DPP3 converter, cursor, scaler, and color-management field definitions.

## Risks

- A wrong shift or mask silently corrupts neighboring bits in memory-mapped registers. This can break color processing, scaling, cursor display, CRC testing, perf counters, power gating, or pipeline reset behavior.
- Generated naming is fragile: helper macros rely on exact `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT` spelling. Renames or missing definitions become compile failures in downstream register-list expansions.
- Mirrored blocks such as CM2/CM3, RAMA/RAMB, and channel-specific R/G/B controls are highly repetitive. Copy-generation mistakes are easy to miss by eye but can affect only one pipe, one RAM bank, or one color channel.
- The chunk boundary is mid-`CM3_CM_SHAPER_RAMB_END_CNTL_G`; any final merged research must reconcile this chunk with the next one before claiming complete coverage of CM3 shaper RAMB behavior.
- Many fields control memory power or reset. Incorrect masks for `*_MEM_PWR_FORCE`, `*_MEM_PWR_DIS`, `*_MEM_PWR_STATE`, or `*_SOFT_RESET` can lead to hangs, blank output, readback timeouts, or display corruption that appears far from the original register write.
- CRC and perfmon masks are test/debug infrastructure. Bugs here may not affect normal display output but can invalidate diagnostics, automated display tests, or performance analysis.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/display integration tests:

- Build coverage for DCN 3.1.5 display code catches missing or misspelled macros used by resource, IRQ, GPIO, DMUB, or block register-list code.
- Static consistency checks can verify that the chunk has paired `__SHIFT` and `_MASK` definitions; this slice has 1,057 of each.
- Register-generation diff tests against the authoritative ASIC register database should flag changed bit positions, masks, or omitted fields.
- Display smoke tests should exercise DPP2/DPP3 paths with scaling, cursor, CSC/gamut/color management, gamma/blending LUT programming, and power transitions.
- CRC tests can validate `DPP_TOP2_DPP_CRC_*` fields by enabling one-shot or continuous CRC and comparing stable expected values for known frames.
- Perfmon tests can program `DC_PERFMON13_*` counters, check active/state transitions, interrupt status/ack behavior, and high/low counter readback.
- Suspend/resume, hotplug, and modeset tests are important for memory power and soft-reset fields because stale or incorrect power state masks can cause intermittent failures after block gating or reinitialization.
