# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 32530-34962

## Scope

This chunk is generated AMD DCN 3.1.6 register field metadata. It contains C preprocessor constants only: paired `__SHIFT` and `_MASK` macros for fields in display timing, OPTC, DC perfmon, HPD, DisplayPort, and DIG/HDMI registers, plus generated register/address-block comments. There are no functions, structs, enums, branches, loops, allocations, includes, or software-owned data structures in this range.

The reviewed span contains 2,433 lines, with 1,093 shift definitions and 1,080 mask definitions. The count mismatch is caused by chunk boundaries: the range begins with the final `OTG2_OTG_SPARE_REGISTER` shift/mask pair from the previous OTG instance, then covers complete OTG3/OPTC/HPD/DP0 blocks, and ends inside `DIG0_HDMI_GENERIC_PACKET_CONTROL5` before the corresponding mask definitions for that register. Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU Display Core hardware metadata rather than distributed filesystem code.

## Purpose And Hardware Surface

The purpose of this header slice is to define bit positions and masks for DCN 3.1.6 display engine registers. The companion `dcn_3_1_6_offset.h` header supplies register addresses and base indices; this `*_sh_mask.h` header supplies the field layouts used by AMDGPU Display Core and DMUB register helpers to pack writes and decode readbacks.

The hardware surface covered in this chunk includes:

- The tail of `OTG2_OTG_SPARE_REGISTER`, then the full `dce_dc_optc_otg3_dispdec` block for timing generator instance 3.
- OPTC miscellaneous controls in `dce_dc_optc_optc_misc_dispdec`, including DWB/GSL source selection, OPTC clock controls, ODM memory power controls/status, and a spare register.
- DC perfmon counter 17 control, state, compare, high, and low value registers.
- Hot-plug-detect blocks `HPD0` through `HPD4`, each with interrupt status/control, HPD control, fast training, and toggle filter timing fields.
- The `DP0` DisplayPort encoder block, including link control, pixel format, MSA, stream control, DPHY/training/CRC, secondary data packets, MST/MSE allocation, DSC, panel replay/ALPM-like controls, GSP controls, and double-buffer status.
- The beginning of the `DIG0` digital encoder block, covering front-end control, output CRC/test-pattern/random-pattern/FIFO status, HDMI metadata/control/status/audio/ACR/VBI/infoframe controls, generic packet enable controls, generic packet 8-14 controls, and the start of immediate generic packet send control.

## Important Definitions

The exported API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives a field's low-bit position.
- `<REGISTER>__<FIELD>_MASK` gives the corresponding register mask.
- `//<REGISTER>` comments group fields by generated register name.
- `// addressBlock: ...` comments mark the hardware aperture from which the following register names were generated.

Important OTG3 definitions include:

- Timing programming fields such as `OTG3_OTG_H_TOTAL`, horizontal/vertical blanking, sync start/end/polarity, vertical total min/max/mid, and dynamic refresh rate controls.
- Trigger, flow, and synchronization fields in `OTG3_OTG_TRIGA_CNTL`, `OTG3_OTG_TRIGB_CNTL`, `OTG3_OTG_FORCE_COUNT_NOW_CNTL`, `OTG3_OTG_GSL_*`, `OTG3_OTG_GLOBAL_CONTROL*`, and `OTG3_OTG_TRIG_MANUAL_CONTROL`.
- Run-state and update controls such as `OTG3_OTG_CONTROL`, `OTG3_OTG_MASTER_EN`, `OTG3_OTG_UPDATE_LOCK`, `OTG3_OTG_DOUBLE_BUFFER_CONTROL`, `OTG3_OTG_MASTER_UPDATE_MODE`, `OTG3_OTG_MASTER_UPDATE_LOCK`, and `OTG3_OTG_PIPE_UPDATE_STATUS`.
- Readback/status fields for scan position, frame counts, interlace/stereo state, snapshots, global sync, CRC data, and static screen detection.
- Display timing helper fields for vertical interrupt positions, VSTARTUP/VUPDATE/VREADY, vupdate keepout, DSC start position, constant DTO phase/modulo, and DRR event/status windows.

Important OPTC/perfmon/HPD definitions include:

- `DWB_SOURCE_SELECT`, `GSL_SOURCE_SELECT`, `OPTC_CLOCK_CONTROL`, `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS`, which support display writeback routing, global sync routing, clock gating, and ODM memory power management.
- `DC_PERFMON17_*` fields for selecting counters, clearing/starting/freezing the perfmon, defining comparison values, and reading high/low counter state.
- `HPD<n>_DC_HPD_INT_STATUS`, `HPD<n>_DC_HPD_INT_CONTROL`, `HPD<n>_DC_HPD_CONTROL`, `HPD<n>_DC_HPD_FAST_TRAIN_CNTL`, and `HPD<n>_DC_HPD_TOGGLE_FILT_CNTL` for connector detect state, RX interrupt state, delayed sense, interrupt acknowledge/mask/polarity, connection/disconnection filter windows, and fast-training signaling for HPD instances 0-4.

Important DP0 and DIG0 definitions include:

- DisplayPort stream/link fields in `DP0_DP_LINK_CNTL`, `DP0_DP_PIXEL_FORMAT`, `DP0_DP_CONFIG`, `DP0_DP_VID_STREAM_CNTL`, `DP0_DP_VID_TIMING`, `DP0_DP_VID_N`, `DP0_DP_VID_M`, and `DP0_DP_LINK_FRAMING_CNTL`.
- DPHY and training controls such as `DP0_DP_DPHY_CNTL`, `DP0_DP_DPHY_TRAINING_PATTERN_SEL`, symbol/error/scrambler controls, PRBS, CRC enable/control/result, MST CRC status, fast training, HBR2 eye pattern, and bit-swap controls.
- Secondary packet/audio/MST controls in `DP0_DP_SEC_CNTL*`, `DP0_DP_SEC_FRAMING*`, `DP0_DP_SEC_AUD_*`, `DP0_DP_SEC_TIMESTAMP`, `DP0_DP_SEC_PACKET_CNTL`, `DP0_DP_MSE_*`, `DP0_DP_MSA_*`, `DP0_DP_MSO_CNTL*`, `DP0_DP_DSC_*`, `DP0_DP_SEC_METADATA_TRANSMISSION`, `DP0_DP_ALPM_CNTL`, and `DP0_DP_GSP*`.
- DIG/HDMI fields for source selection, output CRC, clock/test/random patterns, FIFO status, HDMI packet generation, deep color/scrambling/keepout, audio packets, ACR source/priority, VBI packet sending, audio/MPEG infoframe controls, generic packet continuous/send/update-lock bits, and immediate generic packet send/pending bits.

## Control Flow

This header has no executable control flow. Runtime sequencing is supplied by AMDGPU Display Core code that includes `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h`, builds register/field tables with token-pasting macros, and then uses register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `FD_MASK`, and `FD_SHIFT`.

A typical use path is:

1. DCN316 resource construction or DMUB setup selects a hardware block instance, for example OTG3, HPD2, DP0, or DIG0.
2. The offset header provides the MMIO register address/base index.
3. This header provides the bit shift and mask for the target field.
4. A register helper reads, updates, or writes the packed field while preserving unrelated bits.
5. Display hardware latches the programmed value, reports status, or clears an interrupt according to the register's hardware semantics.

The macros do not encode operation ordering. Callers remain responsible for sequencing around blanking windows, update locks, stream enable/disable, link training, HPD interrupt acknowledgement, DRR/vtotal changes, DSC enablement, audio/infoframe packet updates, and write-one-to-clear status bits.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes stateful MMIO fields inside the GPU display block.

Configuration-like hardware state includes programmed timing totals, sync/blanking windows, trigger routing, flow control, master enable, interlace/stereo control, global sync lock/update behavior, ODM memory power settings, DP stream/link/DPHY/secondary-packet configuration, DSC and MST allocation settings, DIG source selection, HDMI packet controls, and generic packet send modes. Status/readback state includes current scan position, frame counts, CRC outputs, static-screen detection, global sync status, pipe update pending bits, perfmon counter values, HPD sense/RX interrupt status, DPHY CRC/training status, MST slot status, FIFO status, HDMI status, and generic packet pending bits.

The persistence boundary is hardware lifetime: values remain in registers until changed by the driver, reset by hardware, lost during GPU reset/power gating, or overwritten by firmware or another display path. The header itself does not retain runtime state.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.1.6 register-address header, especially `dcn_3_1_6_offset.h`, because masks/shifts are useful only when paired with the matching register offsets. The exact header is included by DCN316 Display Core resource code and DMUB support: `display/dc/resource/dcn316/dcn316_resource.c` and `display/dmub/src/dmub_dcn316.c` include both the offset and shift/mask headers.

Integration points include:

- `dmub_dcn316.c`, which builds `dmub_srv_dcn316_regs` using `FD_MASK` and `FD_SHIFT` over DCN31 field lists.
- DCN316 resource construction, which uses the generated constants through block-specific register tables for timing generators, hub/display pipes, stream encoders, HPD handlers, and related Display Core objects.
- DCE/DCN helper headers such as stream encoder register-field lists, where fields like `DIG0_HDMI_GENERIC_PACKET_CONTROL0`, `DP0_DP_PIXEL_FORMAT`, `DP0_DP_SEC_CNTL`, and `DIG0_HDMI_CONTROL` are consumed through common mask/shift table macros.
- Interrupt service and HPD paths, which depend on the HPD status/control masks matching hardware so sense, RX IRQ, ack, mask, and polarity fields are interpreted correctly.
- Link encoder, stream encoder, timing generator, DSC, MST, audio/infoframe, CRC, and diagnostics paths that use these macros for MMIO programming and readback.

## Risks And Review Notes

- Because this is generated hardware metadata, an incorrect bit position or mask compiles cleanly but can silently program the wrong field. The likely symptoms are display timing failures, HPD interrupt storms or missed detects, DP link-training failures, bad MST/DSC/secondary packet behavior, invalid HDMI audio/infoframes, or broken CRC diagnostics.
- The chunk boundary is not register-aligned. Consumers of this research should not infer that `OTG2_OTG_SPARE_REGISTER` or `DIG0_HDMI_GENERIC_PACKET_CONTROL5` are incomplete in the source file; they are incomplete only in this work-item slice.
- Repeated HPD blocks and repeated DP/DIG packet fields are vulnerable to copy/generation drift. A single instance mismatch can affect only one connector or stream encoder, making failures appear board- or port-specific.
- Some status fields are not ordinary read/write state. Interrupt status/ack/clear fields, pending bits, CRC readbacks, training status, and dynamic refresh timing event bits have side effects or timing constraints defined by hardware and driver code, not by these macros.
- DCN316 uses common DCN31-era helper lists where field availability must match the generated header. Removing or renaming a macro here can break table initialization at compile time; changing a value can pass compile and fail only on hardware.

## Test Signals

Useful validation signals are mostly integration and hardware-display tests rather than unit tests for this header:

- Build coverage for AMDGPU Display Core and DMUB DCN316 paths, especially translation units that include `dcn_3_1_6_sh_mask.h` and instantiate field tables with `FD_MASK`/`FD_SHIFT`.
- Multi-connector hotplug tests across HPD0-HPD4, checking plug/unplug detection, delayed sense, RX IRQ handling, interrupt masking/acknowledgement, and debounce/filter behavior.
- DP link bring-up and retraining on DP0, including different pixel encodings/depths, HBR rates, training patterns, DPHY CRC checks, scrambling, fast training, MST slot allocation, DSC enablement, and secondary data packet transmission.
- OTG3 display-mode tests covering timing programming, vertical interrupts, update locks, DRR/vtotal changes, stereo/interlace modes if supported, CRC capture, and scan-position/frame-counter readback.
- HDMI/DIG0 tests for source selection, deep color, scrambling, audio packet generation, ACR, VBI packets, infoframes, generic packets, AVMUTE/general-control behavior, and immediate-send pending status.
- Runtime diagnostics such as `dmesg` display-core errors, HPD interrupt logs, DP AUX/link-training failures, CRC mismatch reports, blanking/flicker during mode sets, and audio/infoframe analyzer results.
