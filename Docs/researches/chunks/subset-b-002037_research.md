# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 25261-27725

## Purpose

This chunk is generated AMD DCN 3.2.1 register field metadata. It contains no executable C logic; it publishes `#define` constants for bit shifts and bit masks used to access fields inside display-controller MMIO registers. Consumers combine these constants with register-offset macros from the matching DCN 3.2.1 offset header and then use `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and related helpers to program the display hardware.

The requested range starts at the mask half of `OTG1_OTG_V_TOTAL_CONTROL`, so the first eight `OTG1` shift definitions live in the previous chunk. It then covers the remainder of the `dce_dc_optc_otg1_dispdec` timing-generator field map, all of the `dce_dc_optc_otg2_dispdec` and `dce_dc_optc_otg3_dispdec` field maps, the `dce_dc_optc_optc_misc_dispdec` miscellaneous OPTC/GSL/ODM masks, and the beginning of the `dce_dc_dio_hpd0_dispdec` hotplug-detect block. The range ends on the `HPD0_DC_HPD_CONTROL` comment before that register's field definitions, so HPD0 control fields are owned by the next chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, storage objects, includes, locking primitives, allocation paths, or runtime APIs in this slice. Its interface is the generated preprocessor namespace:

- `<register>__<field>__SHIFT`: the field's least significant bit position.
- `<register>__<field>_MASK`: the field's unshifted bit mask in the 32-bit MMIO register.

Major macro families in this chunk:

- `OTG1_*`, `OTG2_*`, and `OTG3_*`: output timing generator fields for vertical timing, horizontal timing, triggers, flow control, master enable, interlace, stereo/3D, pixel readback, status counters, snapshots, interrupts, update locks, double buffering, CRC windows and data, static screen detection, global sync lock, update windows, dynamic refresh rate, DSC start position, and pipe update status.
- `GSL_SOURCE_SELECT`: genlock/swaplock source selection fields for three GSL ready groups plus the timing-sync source.
- `OPTC_CLOCK_CONTROL`: OPTC display-clock gating/status/test-clock and fine-grain clock-gating override fields.
- `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS`: output data merger memory power force/disable/mode/status fields for memory banks 0 through 7.
- `OPTC_MISC_SPARE_REGISTER`: an 8-bit spare field.
- `HPD0_DC_HPD_INT_STATUS` and `HPD0_DC_HPD_INT_CONTROL`: HPD0 interrupt/sense/RX status, toggle filter timer values, interrupt ack, polarity, enable, RX ack, and RX enable fields.

The repeated OTG instance layout is intentionally near-identical across `OTG1`, `OTG2`, and `OTG3`. For each instance, masks such as `OTG*_OTG_H_TOTAL__OTG_H_TOTAL_MASK`, `OTG*_OTG_V_TOTAL_CONTROL__...`, `OTG*_OTG_INTERRUPT_CONTROL__...`, and `OTG*_OTG_PIPE_UPDATE_STATUS__...` are selected by token-pasting macros in DCN resource code.

## Control Flow

This header has no runtime control flow. The effective runtime flow is supplied by the display driver:

1. DCN 3.2.1 resource code includes the DCN 3.2.1 register offset and shift/mask headers.
2. Register-list macros instantiate per-pipe timing-generator tables. In DCN 3.2 era code, `OPTC_COMMON_REG_LIST_DCN3_2_RI(inst)` includes OTG registers such as `OTG_VSTARTUP_PARAM`, `OTG_V_TOTAL_CONTROL`, `OTG_TRIGA_CNTL`, `OTG_CRC_CNTL`, `OTG_GSL_CONTROL`, `OTG_DRR_CONTROL`, and `OTG_PIPE_UPDATE_STATUS`, and also includes `GSL_SOURCE_SELECT`.
3. The shift/mask macros from this file are placed in per-block field tables through `FN(reg, field)` style helpers.
4. Runtime modeset, page-flip, IRQ, link, HPD, and power-management code uses those tables to read, update, poll, clear, or acknowledge individual hardware fields.

The macros themselves do not encode ordering. Consumers must still sequence timing programming, double-buffer locks, vupdate/vstartup/vready windows, GSL synchronization, DRR changes, CRC capture, interrupt ack/clear, HPD enablement, and clock/power transitions correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes fields in MMIO-backed GPU state.

The OTG fields represent hardware state for:

- Mode timing: active totals, blanking ranges, sync start/end/polarity, divide mode, interlace, stereo, and 3D structure.
- Timing generator enablement and routing: master enable, output mux, current enable state, flow control, request mode, DSC start position, and manual trigger paths.
- Atomic update machinery: update locks, double-buffer controls, master update modes, global update/lock fields, vstartup/vupdate/vready positions, keepout windows, and pipe update pending bits.
- Interrupt and event surfaces: vtotal min events, nominal vsync, snapshot, force count, force vsync next line, external trigger A/B, GSL vsync gap, vertical interrupts 0 through 2, DRR timing/update/reach events, and interrupt mask/type/clear/ack fields.
- Diagnostics: live H/V status, frame/VF/HV counters, nominal vertical position, pixel readback, CRC windows/data/signature masks, static-screen status, clock-on status, global sync lock status, and spare registers.
- DRR support: min/max/mid vtotal, event active period, vtotal reach ranges, change limits, trigger windows, average-frame reporting, and last vtotal used by DRR.

The OPTC misc fields represent GSL source selection, OPTC clock-gating status/control, and ODM memory power policy/status. The HPD0 fields represent hotplug sense, delayed sense, HPD interrupt status, HPD RX interrupt status, filter timer readback, interrupt polarity, enables, and acknowledgements.

Persistence is hardware-defined. Configuration fields usually remain in the display block until a modeset, stream teardown, power gating, suspend/resume, or ASIC reset changes them. Status, counter, clear, ack, interrupt, and pending fields may be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive. This header only gives bit positions; it does not identify access type or side effects.

## Dependencies

This chunk depends on the AMD generated DCN 3.2.1 register database. It must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`, which provides the corresponding `mm...` register offsets and base indexes.
- DCN 3.2 resource macros such as `SRI_ARR(...)`, `SR_ARR(...)`, and `OPTC_COMMON_REG_LIST_DCN3_2_RI(inst)` in `drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.h`.
- Link encoder HPD register-list macros such as `HPD_REG_LIST_RI(id)`, which instantiate `DC_HPD_CONTROL`, `DC_HPD_INT_STATUS`, and `DC_HPD_TOGGLE_FILT_CNTL` register tables.
- Generic AMD display register helpers that use field tables built from these macros, including `generic_reg_update_ex()`, `REG_UPDATE`, `REG_SET`, and `REG_GET` patterns.
- IRQ source metadata under `drivers/gpu/drm/amd/include/ivsrcid/dcn/`, which maps many OTG interrupt fields to display interrupt source IDs and contexts.

Because these are preprocessor constants, the compiler only checks that names exist and expressions are syntactically valid. It cannot prove that a mask matches hardware.

## Integration Points

The central integration point is the DCN timing generator, often exposed in DC code as an OPTC or timing-generator object. Resource construction builds per-instance register and field tables for OTG pipes. Modeset and flip sequencing then uses those tables to program timing, enable or disable the CRTC, manage double-buffered updates, set DRR ranges, wait for update-pending bits, configure CRC capture, and collect status.

GSL fields integrate with global sync lock and swaplock/genlock sequencing. Hardware sequencing includes a `TG_SET_GSL_SOURCE_SELECT` step, and resource tables include `GSL_SOURCE_SELECT` so the driver can choose which OTG feeds timing synchronization and ready-source groups.

The ODM memory power fields integrate with display power management. They expose force/disable/status controls for per-bank output data merger memory, plus unassigned and vblank power modes. Incorrect field definitions here can affect power savings, wake latency, or display stability around blanking and pipe reconfiguration.

The HPD0 interrupt fields integrate with link encoder and connector-detection code. DCN link encoder helpers use the HPD register table to enable or disable HPD, and IRQ handling uses HPD status/control fields to detect cable plug/unplug events and DP AUX HPD RX interrupts.

This chunk is also tied to adjacent chunks. The first line is part of `OTG1_OTG_V_TOTAL_CONTROL`; its shift macros are immediately before the requested range. The final line is a register comment for `HPD0_DC_HPD_CONTROL`; the actual HPD0 control masks follow after the requested range.

## Risks And Edge Cases

- Field drift is the main risk. A wrong shift or mask can compile cleanly while causing the driver to write the wrong bits in a live MMIO register.
- Repeated OTG instances are copy-sensitive. `OTG1`, `OTG2`, and `OTG3` are structurally similar, but a single instance-specific typo may only fail on one pipe or one multi-display topology.
- The range starts inside a register definition. Any review of `OTG1_OTG_V_TOTAL_CONTROL` needs the preceding lines for the matching `__SHIFT` values.
- The range ends before `HPD0_DC_HPD_CONTROL` fields. This chunk can describe HPD0 status/control interrupt masks, but not the HPD0 enable/control-field layout that follows.
- Many fields are side-effect-sensitive. Interrupt `ACK`, `CLEAR`, and mask fields, update locks, double-buffer pending bits, DRR event controls, force-count controls, and HPD RX interrupt fields may require specific read/write ordering.
- Timing fields are mode-critical. Incorrect H/V totals, blanking, sync, vstartup, vupdate, vready, DSC start, or keepout masks can produce blank displays, underflow, flicker, missed page flips, or modes that work only at some refresh rates.
- DRR and VRR behavior depends on multiple fields across `V_TOTAL_*`, DRR range/change/trigger windows, and event status. Partial or mismatched definitions can cause stutter, missed vtotal transitions, or stuck interrupts.
- CRC and pixel readback fields are diagnostic but still user-visible through debug and test paths. Bad masks can create false CRC failures or hide real scanout corruption.
- Clock and memory power fields can be harmful if written while blocks are gated, reset, or actively scanning out. The header does not encode safe access windows.

## Test Signals

Useful validation signals combine generated-header checks with display hardware behavior:

- Build AMDGPU/DC with DCN 3.2/3.2.1 support enabled. Missing or renamed macros should fail during resource, timing-generator, HPD, and IRQ table construction.
- Mechanically compare every `__SHIFT` and `_MASK` in lines 25261-27725 against AMD's authoritative DCN 3.2.1 register database and against the matching `dcn_3_2_1_offset.h` register names.
- Check repeated instance consistency for `OTG1`, `OTG2`, and `OTG3`: equivalent registers should expose equivalent field names, shifts, and masks unless the hardware database intentionally differs.
- Exercise modesets and page flips on enough displays to use OTG1, OTG2, and OTG3, including enable/disable cycles, suspend/resume, fast updates, cursor updates, and pipe update pending waits.
- Test timing-sensitive modes: high refresh, low refresh, interlace if supported, stereo/3D if supported, DSC-enabled modes, ODM combinations, and DRR/VRR transitions.
- Validate IRQ behavior for vertical interrupts, vupdate/vstartup/vready events, DRR timing events, nominal vsync, snapshot/force count, GSL vsync gap, and HPD0 plug/unplug plus HPD RX interrupts.
- Use CRC capture and pixel-readback diagnostics to confirm CRC window programming, data readout, and signature masks behave as expected on each covered OTG instance.
- Watch kernel logs and display diagnostics for underflow, missed flips, stuck update locks, stuck interrupt status bits, HPD storms, AUX/HPD RX failures, link retraining loops, clock-gating issues, and resume failures.

## Cross-Chunk Notes

Previous chunks own the beginning of `dce_dc_optc_otg1_dispdec`, including the offset-aligned first half of `OTG1_OTG_V_TOTAL_CONTROL`. Later chunks own `HPD0_DC_HPD_CONTROL` fields and the rest of the HPD/DIO register-field namespace. The final per-file research document should merge those adjacent chunks before making complete claims about all OTG1 fields, all HPD0 fields, or the complete `dcn_3_2_1_sh_mask.h` hardware map.
