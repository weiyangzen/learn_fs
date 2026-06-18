# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 51052-53401

## Purpose

This chunk is the tail of the generated DCN 3.5.1 register shift/mask header for AMD display hardware. It contains only preprocessor constants, not executable code. Each `#define` maps a hardware register field to its bit shift (`__SHIFT`) or mask (`_MASK`) so the display driver can use common register helpers (`REG_SET`, `REG_UPDATE`, `REG_GET`, and macro-generated register structures) without hard-coding bit positions in functional code.

The covered range spans multiple display pipeline blocks:

- MPCC MCM 1D LUT region and memory power fields.
- OPP clock gate reporting disable.
- OTG0-OTG3 long-vblank, DLPC snapshot/resync, CRC readback-window, and DRR count fields.
- DP0-DP4 stream/link symbol counters, ALPM scrambled-zero control, MSA transmission enable, and MST stream allocation table encryption bits.
- DIG0-DIG4 front-end/back-end clock, enable, FIFO, HDMI mode, and stream-mapper fields.
- AFMT0-AFMT5 ACP audio packet fields.
- DIO DPIA mux, I2C clock-enable, DIO status/clock-gating, PSP interrupt, stream mapper, UNIPHY channel enable, DLPC intercept/reset, GPIO drive, and panel power-sequence fields.
- DSCC/DSC top configuration and interrupt fields.
- HDMI FRL/link/stream/TB encoder fields, including generic packet scheduling, ACR N/CTS, metadata packets, CRC, encryption, buffers, memory power, and FIFO status.
- DP stream encoder, DP sym32 encoder, DP DPHY sym32, and DPIA microcontroller/perf-counter fields.
- Azalia F2 and F0 endpoint ACP packet fields.

## Important APIs, Types, And Macros

This header does not declare C types or functions. Its public surface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field bitmask.
- Repeated instance prefixes (`OTG0`-`OTG3`, `DP0`-`DP4`, `DIG0`-`DIG4`, `AFMT0`-`AFMT5`, `DSCC0`-`DSCC3`, `DP_SYM32_ENC0`-`3`, `DP_DPHY_SYM320`-`1`, `AZF0ENDPOINT0`-`4`) encode hardware instance selection.

The main consumers are the register-list and field-list macros in the DC resource and block headers. For DCN 3.5.1, `dcn351_resource.c` includes `dcn/dcn_3_5_1_offset.h` and this `dcn/dcn_3_5_1_sh_mask.h`, then expands macros such as `SR`, `SRI`, `SR_ARR`, `SR_ARR_INIT`, and `*_MASK_SH_LIST(...)` to populate block-specific register, shift, and mask structs. Examples visible from the integration path include:

- AUX engines using `DP_AUX0_AUX_CONTROL__AUX_RESET_MASK` as the common reset mask while instance-specific register offsets are generated separately.
- DIO and HW sequencer mask lists pulling clock-gating, reset, DIO, DPIA, and power fields into typed mask/shift tables.
- Audio code accessing Azalia codec endpoint registers indirectly through indexed register writes, with ACP-related fields represented here for packet control and endpoint state.

## Control Flow

There is no runtime control flow in this chunk. Control flow is indirect:

1. DCN 3.5.1 resource construction includes this header during compilation.
2. Resource initialization macros copy selected constants into register-block tables.
3. Runtime display code calls register helpers with symbolic field names.
4. The helper macros combine a register address from offset headers with the shift/mask constants from this header to write or read the correct bits.

The header therefore acts as a compile-time hardware ABI layer. If a field definition is wrong, the fault appears later as bad MMIO programming in unrelated-looking display code.

## State And Persistence Behavior

The constants describe fields that control or report hardware state, but the header itself stores no state and persists nothing. Hardware state represented by this range includes:

- Persistent-until-reset programming state such as HDMI packet controls, generic packet line scheduling, ACR values, DIG clock enables, stream mapper targets, DIO DPIA mux source selection, GPIO drive impedance, panel power-sequence drive settings, and DSC/DSCC configuration.
- Volatile status/readback state such as OTG CRC window readbacks, long-vblank counters, DP symbol counters, DP link cycle counters, HDMI CRC results, FIFO error/status bits, DPIA interrupt/status bits, and memory power-state readbacks.
- Power-management state such as MPCC MCM LUT memory power controls, HDMI borrow-buffer memory power controls, DSC dynamic clock gating, DIO clock gates, OPP fine-grain clock gate reporting, and DPIA clocks/resets.

Because many masks cover clock, reset, power, and packet scheduling fields, incorrect values can survive across modesets until the affected block is reset or reprogrammed.

## Dependencies And Integration Points

This file depends on the matching DCN 3.5.1 offset header for register addresses. The shift/mask names must match the register names used by block-specific resource macros in `drivers/gpu/drm/amd/display`.

Key integration points:

- `dc/resource/dcn351/dcn351_resource.c` includes this header and builds DCN 3.5.1 resource tables for AUX, DIO, HW sequencer, clock, DSC, stream/link encoders, audio, I2C, and related display blocks.
- `dc/dce/dce_aux.h` defines common AUX register and field-list macros; the resource layer supplies the DCN-specific shifts/masks.
- DIO/DPIA fields integrate USB4 DisplayPort Input Adapter routing, mux control, clocking, reset, local interrupts, hidden-port status, glue enable, and performance counters. Higher-level DPIA behavior also involves DMUB commands and notifications for AUX-over-DPIA and bandwidth allocation.
- DP/DIG/HDMI/AFMT fields integrate with stream encoder and link encoder programming for DisplayPort, HDMI, FRL/TMDS, audio info/ACP packets, MST encryption status, ALPM, and symbol-count diagnostics.
- OTG/OPTC/DLPC fields integrate timing-generator behavior, dynamic refresh/long-vblank handling, CRC capture, and display logic power control snapshots.
- Azalia endpoint fields integrate with the display audio path, including indexed endpoint register access and ACP packet support.

## Risks

- Generated-header drift: the constants must match the ASIC register specification and the matching offset header. A stale or mismatched mask silently corrupts unrelated fields in MMIO writes.
- Instance symmetry assumptions: many blocks repeat identical field layouts across instances. If one instance differs but retains copied masks, only specific pipes/connectors fail.
- Clock/reset/power hazards: DIO, DIG, HDMI, DSC, DPIA, OPP, and MPCC power fields can hang or blank displays if toggled with an incorrect bit position.
- Packet scheduling hazards: HDMI generic packet, metadata, ACP, ACR, and audio fields are timing-sensitive. Wrong masks can cause missing HDR/Dolby Vision metadata, audio clock drift, invalid infoframes, or link training failures.
- Security/status ambiguity: DP MST SAT encryption enable/status fields and HDMI encryption control fields are only bit definitions here. Incorrect field mapping can misreport or misprogram encrypted transport state.
- Diagnostics fragility: CRC, symbol-count, FIFO, and DPIA perf-counter fields are often used for validation and debug. Bad masks can hide real hardware failures or create misleading test signals.

## Test Signals

Since this chunk is compile-time register metadata, direct unit tests are unlikely. Useful validation signals are integration and hardware-facing:

- Successful build of AMD display code using `dcn_3_5_1_sh_mask.h` with no missing macro names in DCN 3.5.1 resource initialization.
- Display bring-up on DCN 3.5.1 hardware across DP, HDMI, eDP/panel, and USB4 DPIA paths.
- Modeset and link-training tests covering DP0-DP4, DIG0-DIG4, HDMI FRL/TMDS, DSC, and DPIA-routed endpoints.
- Audio validation for HDMI/DP audio, ACP packet programming, ACR N/CTS stability, and Azalia endpoint access.
- CRC/debugfs or display validation tests that read OTG/HDMI/DP CRC and symbol counter status fields.
- Power-management tests for suspend/resume, display idle, clock gating, memory low-power states, and DPIA reset/interrupt handling.
- MST/HDCP or encrypted-transport validation for DP SAT encryption status and HDMI encryption-related fields where supported.
