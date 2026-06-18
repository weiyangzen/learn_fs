# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 35326-37792

## Scope

This chunk is a generated AMD DCN 4.2.0 register shift/mask header slice. It covers lines 35326-37792 of `dcn_4_2_0_sh_mask.h`, beginning in the tail of `OTG1_OTG_STATIC_SCREEN_CONTROL`, defining the end of the `OTG1` timing-generator block, all visible `OTG2` and `OTG3` timing-generator field definitions, then entering shared OPTC miscellaneous, DC perfmon, and DC I2C/DDC field definitions. The slice contains 2,141 `#define` entries: 1,070 `__SHIFT` constants and 1,071 `_MASK` constants.

## Purpose

The file is not executable logic. It is the bitfield contract for MMIO registers used by the AMD display driver for DCN 4.2 hardware. Each macro maps a hardware register field to a shift offset and/or bit mask. Display code combines these values with register-offset macros from `dcn_4_2_0_offset.h` and helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `SF`, `SRI`, and `SR` to write or read specific hardware fields without hard-coded numeric bit positions in the driver logic.

Within this slice, the main hardware areas are:

- `OTG1`, `OTG2`, and `OTG3` output timing generator fields for display timing, vblank/vupdate/vready events, master-update locking, global swap lock, dynamic refresh rate, CRC, stereo/3D, interlace, vertical interrupts, static screen detection, P-state keepout, and pipe-update status.
- `GSL_SOURCE_SELECT`, `OPTC_DLPC_CONTROL`, `OPTC_CLOCK_CONTROL`, and `ODM_MEM_PWR_*` fields for OPTC-level synchronization, clock gating, and ODM memory power behavior.
- `DC_PERFMON15_*` fields for one display performance monitor instance, including counter selection, run/interrupt state, counter values, and counter interrupt acknowledgement.
- `DC_I2C_*` fields for display I2C/DDC arbitration, software and hardware completion interrupts, status/error bits, DDC line status, DDC speed, and the beginning of DDC1 setup.

## Important Macros And Field Families

The chunk is organized by comment headers naming registers, followed by paired `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros. There are no types or functions defined here.

Important OTG field families:

- `OTG*_OTG_H_TOTAL`, `OTG*_OTG_H_BLANK_START_END`, `OTG*_OTG_H_SYNC_A`, and `OTG*_OTG_H_SYNC_A_CNTL` describe horizontal totals, blanking, sync window, sync polarity, and horizontal timing divider mode.
- `OTG*_OTG_V_TOTAL`, `OTG*_OTG_V_TOTAL_MIN`, `OTG*_OTG_V_TOTAL_MAX`, `OTG*_OTG_V_TOTAL_MID`, and `OTG*_OTG_V_TOTAL_CONTROL` describe vertical totals and min/max/mid switching used for variable/dynamic refresh behavior.
- `OTG*_OTG_GLOBAL_SYNC_STATUS`, `OTG*_OTG_VSTARTUP_PARAM`, `OTG*_OTG_VUPDATE_PARAM`, and `OTG*_OTG_VREADY_PARAM` define timing event positions, event occurrence/status bits, clear bits, and interrupt enable/type fields.
- `OTG*_OTG_MASTER_UPDATE_LOCK`, `OTG*_OTG_GLOBAL_CONTROL0..4`, `OTG*_OTG_GSL_CONTROL`, `OTG*_OTG_GSL_WINDOW_X/Y`, and `OTG*_OTG_VUPDATE_KEEPOUT` define update-lock windows and global-swap-lock coordination.
- `OTG*_OTG_TRIGA_CNTL`, `OTG*_OTG_TRIGB_CNTL`, `OTG*_OTG_TRIGA_MANUAL_TRIG`, and `OTG*_OTG_TRIGB_MANUAL_TRIG` define trigger source selection, polarity, edge detection, frequency, delay, clear, and manual trigger bits.
- `OTG*_OTG_CONTROL`, `OTG*_OTG_CLOCK_CONTROL`, `OTG*_OTG_MASTER_EN`, and `OTG*_OTG_STATUS*` define enable state, clock/reset state, muxing, current counters, active/blanking state, and frame counts.
- `OTG*_OTG_INTERRUPT_CONTROL` and `OTG*_OTG_VERTICAL_INTERRUPT{0,1,2}_*` define CRTC/timing-generator interrupt sources, line positions, enable/status/clear/type fields.
- `OTG*_OTG_CRC_CNTL`, `OTG*_OTG_CRC*_DATA_*`, `OTG*_OTG_CRC*_WINDOW*_*`, and readback variants define output CRC selection, windows, readback coordinates, and CRC result fields used for display validation.
- `OTG*_OTG_DRR_*`, `OTG*_OTG_PSTATE_REGISTER`, `OTG*_OTG_PIPE_UPDATE_STATUS`, and `OTG*_OTG_PWA_FRAME_SYNC_CONTROL` define dynamic-refresh timing transitions, memory/P-state allow windows, pending update visibility, and PWA frame synchronization.

Important non-OTG families:

- `GSL_SOURCE_SELECT__GSL{0,1,2}_READY_SOURCE_SEL` selects ready sources for global swap lock.
- `OPTC_CLOCK_CONTROL__OPTC_FGCG_REP_DIS` controls an OPTC clock-gating behavior.
- `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS` define memory power-mode controls, block masks, and status fields for ODM memory.
- `DC_PERFMON15_PERFCOUNTER_CNTL`, `DC_PERFMON15_PERFCOUNTER_CNTL2`, `DC_PERFMON15_PERFCOUNTER_STATE`, `DC_PERFMON15_PERFMON_CNTL`, `DC_PERFMON15_PERFMON_CNTL2`, `DC_PERFMON15_PERFMON_CVALUE_INT_MISC`, `DC_PERFMON15_PERFMON_CVALUE_LOW`, `DC_PERFMON15_PERFMON_HI`, and `DC_PERFMON15_PERFMON_LOW` define one display perfmon counter bank, including event selection, cvalue selection, increment/run modes, interrupt status/ack fields, high/low counter values, and read selector bits.
- `DC_I2C_CONTROL`, `DC_I2C_ARBITRATION`, `DC_I2C_INTERRUPT_CONTROL`, `DC_I2C_SW_STATUS`, `DC_I2C_DDC{1..5}_HW_STATUS`, `DC_I2C_DDC1_SPEED`, and the start of `DC_I2C_DDC1_SETUP` define DDC/I2C bus ownership, soft reset/go/send-reset controls, transaction count and DDC select fields, completion interrupts, NACK/timeout/abort/status bits, hardware request/urgent/done bits, EDID detect status/state, prescale/timing, and DDC1 setup enable/drive/delay fields.

## Integration Points

This header is included by DCN 4.2 display code alongside `dcn_4_2_0_offset.h`, including:

- `display/dc/resource/dcn42/dcn42_resource.c`, where token-pasting macros such as `SR`, `SRI`, `SR_ARR`, and `SRI_ARR` build register-address tables from offset macros.
- `display/dc/optc/dcn42/dcn42_optc.h`, where `OPTC_COMMON_MASK_SH_LIST_DCN42(mask_sh)` maps timing-generator field names into `struct dcn_optc_shift` and `struct dcn_optc_mask` compatible data. Many fields in that list are defined in this chunk, including timing totals, update locks, GSL, CRC windows, vertical interrupts, DRR, P-state, and pipe-update fields.
- `display/dc/resource/dcn42/dcn42_resource.h`, where `TG_COMMON_REG_LIST_DCN42` creates per-instance OTG register arrays for `OTG0...OTG3` style register names. This chunk supplies the `OTG2` and `OTG3` field names for the same register families used by the timing generator.
- `display/dc/dce/dce_i2c_hw.h`, where `I2C_COMMON_MASK_SH_LIST_*` uses `I2C_SF(DC_I2C_DDC1_SETUP, ...)`, `I2C_SF(DC_I2C_CONTROL, ...)`, `I2C_SF(DC_I2C_ARBITRATION, ...)`, `I2C_SF(DC_I2C_DDC1_SPEED, ...)`, and `I2C_SF(DC_I2C_SW_STATUS, ...)`. The I2C definitions in this chunk populate `struct dce_i2c_shift` and `struct dce_i2c_mask`.
- `display/dc/gpio/dcn42/hw_translate_dcn42.c`, which includes this header for GPIO/DDC mask constants and register offset translation.
- `display/dc/irq/dcn42/irq_service_dcn42.c`, which includes this header for interrupt register field constants used by the DC IRQ service.

The chunk also depends on the naming conventions and register offsets generated in `dcn_4_2_0_offset.h`. A field macro here is only useful when its register has a matching `reg...` offset macro and when consumer field-list macros refer to the exact generated token.

## Control Flow And State Behavior

There is no direct control flow, memory allocation, locking, or persistence in this header. Runtime behavior comes from consumers:

1. DCN 4.2 resource initialization includes this header and `dcn_4_2_0_offset.h`.
2. Register-list macros build tables of MMIO offsets for timing generators, I2C engines, IRQ sources, clock/power blocks, and other DC components.
3. Mask/shift-list macros build field metadata tables, usually one table of shifts and one table of masks.
4. Register helpers use the offset, mask, and shift metadata to read/modify/write hardware registers during display bring-up, modeset, vblank/vupdate handling, CRC collection, I2C/DDC transactions, power management, and timing-generator synchronization.

The state controlled by these definitions is hardware state, not software-owned persistent state. Writes affect live display hardware registers; reads sample live hardware counters/status bits. Some fields are sticky status/interrupt bits with explicit clear/ack fields, such as vstartup/vupdate/vready event clears, vertical interrupt clears, perfmon interrupt ACK bits, and I2C done ACK bits. Some fields represent pending or busy state, such as `OTG_BUSY`, update-pending bits, I2C request/status bits, and perfmon active/status bits.

## Dependencies

Key dependencies are:

- The AMD DC register-generation naming scheme: `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`.
- `dcn_4_2_0_offset.h` for the corresponding register addresses and base-index values.
- DC register helper macros that expect a mask/shift pair to exist for each field named in local field-list macros.
- Hardware documentation/RTL for DCN 4.2 register bit positions. This header is effectively a generated view of that hardware contract.
- The Linux DRM AMD display stack, especially timing generator, resource, IRQ, GPIO/DDC, I2C, and hardware sequencer code.

## Risks And Fragile Areas

- Incorrect mask/shift values can silently program the wrong MMIO bits. That can affect display timing, vblank/vupdate interrupt delivery, update-lock behavior, CRC reporting, I2C/DDC bus access, power gating, or perfmon state.
- Token spelling is a hard ABI between this generated header and consumer macros. A renamed field that is not reflected in `OPTC_COMMON_MASK_SH_LIST_DCN42`, `I2C_COMMON_MASK_SH_LIST_*`, GPIO code, IRQ code, or resource register lists causes compile failures. A stale but still defined field can compile while targeting the wrong hardware semantics.
- The chunk begins and ends mid-register-family: it starts after the first `OTG1_OTG_STATIC_SCREEN_CONTROL` fields and ends before the remaining `DC_I2C_DDC1_SETUP` masks. Merge logic must preserve neighboring chunks to reconstruct the complete file-level research.
- Many OTG definitions are repeated per instance. Copy/generation errors that affect only `OTG2` or `OTG3` can produce instance-specific bugs, such as one display pipe failing while another works.
- Several status/clear/ack pairs are adjacent. A bit-position swap between status and clear/ack fields would be particularly risky because writes intended to acknowledge events could touch enable/type/status fields instead.
- I2C/DDC fields cover display detection and EDID reads. Bad masks around `DC_I2C_DDC_SELECT`, `DC_I2C_TRANSACTION_COUNT`, NACK/timeout bits, or DDC setup timing can break monitor detection or cause unreliable AUX/DDC fallback behavior.
- Power and clock fields such as `ODM_MEM_PWR_CTRL*`, `OPTC_CLOCK_CONTROL`, and `OTG_CLOCK_CONTROL` can create resume, blanking, or clock-gating failures if generated values do not match hardware.

## Test And Validation Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration checks:

- Build coverage for DCN 4.2 display code should catch missing or misspelled macro names referenced by `dcn42_resource.c`, `dcn42_resource.h`, `dcn42_optc.h`, `dce_i2c_hw.h`, IRQ service code, and GPIO/DDC translation code.
- Static consistency checks can verify that every `__SHIFT` in the chunk has a matching `_MASK` for the same `REGISTER__FIELD` and that masks are aligned with shifts.
- Register-generation diffs against AMD hardware register sources or adjacent ASIC versions can flag unexpected changes in repeated OTG2/OTG3 fields, especially where OTG instance fields should be identical.
- Runtime display tests should cover modeset, vblank/vupdate interrupts, vertical line interrupts, global update lock, GSL/multidisplay synchronization, VRR/DRR transitions, static screen signaling, P-state keepout behavior, and CRC collection.
- Connector tests should cover DDC/EDID detection over DDC1-DDC5, I2C timeout/NACK paths, software-vs-hardware I2C arbitration, and HPD/DDC interactions.
- Power-management tests should include suspend/resume and idle/display-off paths where `ODM_MEM_PWR_*`, I2C light sleep, OPTC clock gating, and OTG clock/reset status are exercised.

## Open Questions For Merge Lane

- Neighboring chunks should confirm the complete `OTG0` and `OTG1` definitions and the continuation of `DC_I2C_DDC1_SETUP` plus later DDC2-DDC6/VGA setup fields.
- The generated typo `OTG*_OTG_DRR_CONTOL2` appears in this chunk and likely matches the hardware-generated token. Consumers must use the exact spelling if they reference it.
- This chunk does not show final include guard closure or file-level generation metadata beyond the header start read separately; the merge lane should summarize those at whole-file scope.
