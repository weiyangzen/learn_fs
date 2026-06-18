# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 10047-12576

## Scope

This chunk is part of the generated AMD DCN 3.1.5 shift/mask header. It covers 2,530 source lines and defines 1,054 `__SHIFT` macros paired with 1,054 `_MASK` macros for 386 hardware register fields. The range starts in the middle of the HUBP pipe 2 request block and continues through HUBP/HUBPREQ/HUBPRET/cursor/perfmon pipe 3 plus the beginning of DPP0 CNVC, cursor converter, DSCL scaler, and CM color-management registers.

Address blocks present in this chunk:

- `dce_dc_dcbubp2_dispdec_hubpret_dispdec`
- `dce_dc_dcbubp2_dispdec_cursor0_dispdec`
- `dce_dc_dcbubp2_dispdec_hubp_dcperfmon_dc_perfmon_dispdec`
- `dce_dc_dcbubp3_dispdec_hubp_dispdec`
- `dce_dc_dcbubp3_dispdec_hubpreq_dispdec`
- `dce_dc_dcbubp3_dispdec_hubpret_dispdec`
- `dce_dc_dcbubp3_dispdec_cursor0_dispdec`
- `dce_dc_dcbubp3_dispdec_hubp_dcperfmon_dc_perfmon_dispdec`
- `dce_dc_dpp0_dispdec_cnvc_cfg_dispdec`
- `dce_dc_dpp0_dispdec_cnvc_cur_dispdec`
- `dce_dc_dpp0_dispdec_dscl_dispdec`
- `dce_dc_dpp0_dispdec_cm_dispdec`

## Purpose

The file does not implement functions or runtime control flow. Its purpose is to provide compile-time field metadata for DCN 3.1.5 memory-mapped display registers. Each field gets a bit shift and bit mask constant named as:

`<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.

Display code includes this header together with `dcn_3_1_5_offset.h` to build register tables for DCN 3.1.5 hardware. Helper macros such as `HUBP_SF(...)`, `TF_SF(...)`, and local `SF(...)` variants expand these definitions into structures that the driver later uses with register read/modify/write helpers.

## Important Macro Families

This chunk contributes several major hardware domains:

- `HUBPREQ2_*`: tail of pipe 2 request-side surface programming, including surface control, flip control, flip interrupts, in-use addresses, expansion modes, TTU/QoS timing, VM aperture/TLB controls, prefetch/blank/flip/nominal timing parameters, cursor request timing, and request-memory power controls.
- `HUBPRET2_*`: pipe 2 return-side packing/crossbar, read-line windows, vblank/read-line interrupt control, read-line value/status, and memory power state fields.
- `CURSOR0_2_*`: pipe 2 cursor enable/mode, surface address, size, position, hot spot, stereo offsets, destination offset, cursor memory power, and DMDATA address/control/QoS/status/software data fields.
- `DC_PERFMON9_*`: performance counter 9 control, counter state selectors, perfmon global control, interrupt/status/ack fields, and high/low counter value fields.
- `HUBP3_*`, `HUBPREQ3_*`, `HUBPRET3_*`, `CURSOR0_3_*`, and `DC_PERFMON10_*`: the same HUBP/request/return/cursor/perfmon pattern for pipe 3. These include primary/secondary luma and chroma surface addresses, DCC/TMZ flags, VM fault/underflow/done bits, TTU/QoS settings, flip/prefetch/vblank/nominal timing, and memory power state bits.
- `CNVC_CFG0_*`: DPP0 format/color-conversion configuration, including pixel format, format-control clamps and conversion modes, FP bias/scale registers, color keyer ranges, alpha LUT, pre-dealpha/realpha, pre-CSC matrix A/B banks, coefficient format, and pre-degamma mode/select fields.
- `CNVC_CUR0_*`: DPP0 cursor converter fields for cursor enable, expansion, pixel inversion, ROM enable, cursor mode, alpha modulation, update pending, cursor colors, and FP scale/bias.
- `DSCL0_*`: DPP0 scaler and line-buffer fields covering coefficient RAM tap select/data, scaler mode and tap count, 2-tap hardcoded/sharp controls, manual replicate factors, luma/chroma horizontal/vertical scale ratios and filter init values, black color, update pending, autocal, overscan, OTG blanking, recout/MPC sizes, line-buffer format/memory/v-counter, DSCL/OBUF memory power, and OBUF behavior.
- `CM0_*`: start of DPP0 color-management fields, including CM bypass/update pending, post-CSC matrices, gamut-remap matrices, color bias, gamma-correction control/LUT access, RAMA region programming for segments 0 through 33, and the beginning of RAMB start/end controls.

## APIs, Types, and Functions

No C APIs, functions, structs, or enums are declared in this chunk. The externally consumed interface is the macro namespace itself. The macros are used indirectly through generated register-list initializers in AMD display code.

Important integration patterns visible outside this chunk:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes `dcn/dcn_3_1_5_offset.h` and this header, then defines `SR`, `SRI`, `SRII`, and related helpers for register addresses.
- DCN HUBP headers such as `display/dc/hubp/dcn31/dcn31_hubp.h` define `HUBP_MASK_SH_LIST_DCN31(mask_sh)` using `HUBP_SF(register, field, mask_sh)` entries. For pipe instances, the same field layout is instantiated across `HUBPREQ0`, `HUBPREQ1`, `HUBPREQ2`, `HUBPREQ3`, cursor, HUBPRET, and HUBP register names.
- DPP headers such as `display/dc/dpp/dcn10/dcn10_dpp.h` and later DPP variants use `TF_SF(...)` for many `DSCL0_*`, `CM0_*`, `CNVC_CFG0_*`, and `CNVC_CUR0_*` fields supplied in this chunk.
- DCN 3.1.5 specific users include `dmub/src/dmub_dcn315.c`, `dc/irq/dcn315/irq_service_dcn315.c`, `dc/gpio/dcn315/*`, and `dc/resource/dcn315/dcn315_resource.c`.

## Control Flow

This chunk has no executable branches. Its control-flow role is compile-time token expansion:

1. DCN315 source files include this header and the matching offset header.
2. Hardware-object headers expand register-address macros and field shift/mask macros into per-block register and shift/mask tables.
3. Runtime display code calls generic register helpers that consume those tables when programming plane addresses, flips, cursors, scaler ratios, color conversion, gamma LUTs, interrupts, perf counters, or memory-power controls.

For example, a `HUBP_SF(HUBPREQ0_DCSURF_SURFACE_CONTROL, PRIMARY_SURFACE_DCC_EN, mask_sh)` style entry depends on a matching `HUBPREQ*_DCSURF_SURFACE_CONTROL__PRIMARY_SURFACE_DCC_EN__SHIFT` and `_MASK` pair in this header. The runtime path does not know the literal bit value; it relies on the generated table.

## State and Persistence

The macros themselves are stateless and persistent only as compiled constants. The hardware fields they describe are stateful DCN registers. This chunk covers state with several lifetimes:

- Frame/flip state: surface base addresses, metadata addresses, `SURFACE_UPDATE_LOCK`, `SURFACE_FLIP_PENDING`, stereo flip bits, flip interrupt clear/status, and current/earliest in-use address snapshots.
- Plane memory interpretation: pixel format, tiling, pitch, viewport dimensions, DCC enable/independent block fields, TMZ protected-memory bits, VMID, VM aperture, and L1 TLB behavior.
- Timing/QoS state: TTU, vblank, flip, nominal, prefetch, per-line delivery, reference-frequency-to-pixel-frequency, and request expansion fields.
- Cursor and DMDATA state: cursor address/size/position/hotspot, cursor memory power, DMDATA address/control/QoS/status, and software payload data.
- Interrupt/perf state: HUBPRET vblank/read-line interrupt mask/type/clear/status fields and perfmon counter control/status/ack/value registers.
- DPP processing state: CNVC format/color keying/CSC/degamma/alpha settings, DSCL coefficient RAM and scaler/line-buffer configuration, and CM post-CSC/gamut/gamma-correction LUT state.
- Power state: HUBPREQ, HUBPRET, cursor, DSCL, and OBUF memory power force/disable/mode/status fields.

Because these are display engine registers, persistence is generally limited to the current hardware programming epoch and is reset or reprogrammed during mode set, pipe construction, plane updates, power transitions, or GPU reset.

## Dependencies

Direct dependencies are structural rather than `#include` dependencies inside this chunk:

- It must stay synchronized with `dcn_3_1_5_offset.h`, which supplies the corresponding register addresses and base indices.
- It depends on AMD's generated register naming convention. Consumer macros concatenate register and field tokens, so spelling changes are ABI-like changes for the driver source.
- It depends on the DCN 3.1.5 hardware register specification. The numerical masks and shifts must match silicon, firmware expectations, and the display microcontroller's view of the same registers.
- It depends on common register helper infrastructure such as `reg_helper.h`, `HUBP_SF`, `TF_SF`, and block-specific `*_MASK_SH_LIST_*` macros that materialize these constants into structures.

## Integration Points

Key integration surfaces for fields in this range:

- HUBP/HUBPREQ programming for plane setup, surface flips, DCC/TMZ, VM/DLG/TTU timing, prefetch, and memory-request sizing.
- HUBPRET programming for detector-buffer base selection, component crossbar mapping, read-line tracking, and vblank/read-line interrupts.
- Cursor programming for address, position, format/mode, pitch, magnification, stereo offset, DMDATA, and cursor memory power management.
- DC perfmon programming for display performance counter selection, run/stop conditions, interrupt status/ack, and counter readback.
- DPP CNVC programming for pixel conversion, clamping, color keying, pre-CSC matrices, degamma, and alpha processing.
- DPP DSCL programming for scaler coefficients, ratios, taps, recout/MPC geometry, line-buffer layout, autocal, and memory power.
- DPP CM programming for post-CSC, gamut remap, gamma correction LUT and piecewise region programming.

## Risks

- A wrong shift or mask silently programs the wrong hardware bits. Effects can range from display corruption, underflow, missed flips, or broken cursor to VM faults, bad protected-memory handling, or hangs.
- Register-family symmetry is important. Pipe 2 and pipe 3 fields mirror earlier pipe instances; a mismatch across instances can cause bugs that appear only on specific display pipes or multi-display configurations.
- Many fields are multi-bit packed values. Off-by-one masks can truncate high bits for dimensions, addresses, LUT regions, scale ratios, or timing quantities.
- Several fields are status/clear/ack bits. Incorrect masks for `*_CLEAR`, `*_ACK`, or interrupt status fields can lose interrupts, repeatedly signal stale events, or clear unrelated status.
- Power-control fields can force or disable internal memories. Bad masks here can leave display subblocks powered down while active, or prevent low-power entry.
- The chunk ends in the middle of the `CM0_CM_GAMCOR_RAMB_*` sequence, so any merged per-file analysis must continue into later chunks before making whole-file conclusions about CM gamma-correction coverage.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/driver behavior:

- Build coverage for DCN315 display code, especially `dcn315_resource.c`, DPP, HUBP, IRQ, GPIO, and DMUB users that include this header.
- Macro-expansion coverage: references through `HUBP_MASK_SH_LIST_DCN31`, DPP `TF_SF` lists, perfmon, IRQ, and GPIO tables should compile without missing macro names.
- KMS/display smoke tests on DCN 3.1.5 hardware: mode set, multi-plane composition, cursor movement, flips, stereo/flip interrupt paths, multi-display pipe allocation, suspend/resume, and GPU reset.
- Plane feature tests: DCC enabled/disabled, protected memory/TMZ surfaces, luma/chroma planar formats, rotation/mirror/alpha plane, scaling, and color-management/gamma/gamut changes.
- Runtime diagnostics: no HUBP underflow, DMDATA VM fault/underflow/late status, unexpected flip-pending stalls, repeated vblank/read-line interrupts, or perfmon readback anomalies.
- Register trace comparison against known-good DCN 3.1.5 tables or vendor-generated register dumps can catch accidental mask/shift drift.

## Cross-Chunk Notes

This chunk starts after earlier `HUBPREQ2` surface address definitions and ends before the full CM RAMB gamma-correction region is complete. The final per-file report should merge this with neighboring chunks to cover the entire generated header, the include guard, all address blocks, and the complete DPP color-management macro set.
