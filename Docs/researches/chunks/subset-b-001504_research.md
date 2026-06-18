# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_sh_mask.h

Chunk: `subset-b-001504`
Covered source range: lines 4130-7763 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_sh_mask.h`

## Purpose

This chunk is a generated AMD DCE 10.0 register field mask header segment. It contains C preprocessor constants for extracting, composing, and clearing bit fields in display-controller registers used by Southern Islands/VI-era AMDGPU display, display-core resource tables, PowerPlay/SMU, and BACO paths.

The range is not executable code. It defines 3,634 `#define` lines for 794 register names. The constants follow the common AMD register-header convention:

- `<REGISTER>__<FIELD>_MASK` is the field mask in a 32-bit register.
- `<REGISTER>__<FIELD>__SHIFT` is the matching right-shift count.

The covered range spans several large DCE areas:

- tail `UNIPHY_MACRO_CNTL_RESERVED*`, large `DCRX_PHY_MACRO_CNTL_RESERVED*`, and `DPHY_MACRO_CNTL_RESERVED*` full-register reserved blocks;
- DCP graphics primary plane, overlay plane, surface address, pitch, update, DFQ, flip, interrupt, XDMA recovery/underflow, cursor, LUT, CRC, color-conversion, denorm, clamp, keying, degamma, gamut-remap, regamma, alpha, hardware rotation, and stereo-sync fields;
- DIG front-end/back-end, FIFO, test-pattern, output CRC, DISPCLK switch, HDMI, AFMT audio/infoframe/generic-packet, TMDS, LVDS, and lane-enable fields;
- DMCU control, firmware address/checksum, ERAM/IRAM host access, event trigger, microcontroller interrupt status/routing, master/slave mailbox registers, DMCU debug, and DMCU perfmon interrupt status/routing fields.

The companion address header for these fields is `dce_10_0_d.h`. For example, this chunk's field names map to address macros such as `mmGRPH_CONTROL`, `mmHDMI_CONTROL`, `mmAFMT_AUDIO_PACKET_CONTROL`, `mmDMCU_CTRL`, and `mmDMCU_PERFMON_INTERRUPT_STATUS1` through `mmDMCU_PERFMON_INTERRUPT_STATUS5`.

## Important APIs, Types, And Macros

There are no functions, structs, typedefs, or enums in this chunk. The exported surface is entirely preprocessor macros consumed by register helper APIs such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, and `WREG32`.

Important macro families in this range:

- `UNIPHY_MACRO_CNTL_RESERVED*`, `DCRX_PHY_MACRO_CNTL_RESERVED*`, and `DPHY_MACRO_CNTL_RESERVED*`: full-width `0xffffffff` reserved-control words for display PHY and receiver PHY macro blocks. These are hardware-facing reserved/debug register windows; callers should not infer behavior from the header alone.
- `GRPH_*`: primary graphics-plane programming. `GRPH_CONTROL` covers depth, bank geometry, format, address translation, tiling array mode, pipe config, micro-tile mode, and color expansion. Surface address, high-address, pitch, x/y offset, visible start/end, in-use, compression, DFQ, page-flip interrupt, flip-rate, stereo-sync, XDMA recovery, and XDMA underflow fields are also defined.
- `OVL_*` and `OVLSCL_*`: overlay enable, tiling/format, address, pitch, start/end, update locking, DFQ, edge-pixel fill, secondary surface, and stereo-sync fields.
- `PRESCALE_*`, `INPUT_CSC_*`, `OUTPUT_CSC_*`, `COMM_MATRIXA_TRANS_*`, `COMM_MATRIXB_TRANS_*`, `DENORM_CONTROL`, `OUT_ROUND_CONTROL`, `OUT_CLAMP_CONTROL_*`, `KEY_*`, `DEGAMMA_CONTROL`, `GAMUT_REMAP_*`, and `REGAMMA_*`: color pipeline controls for bias/scale, color-space conversion matrices, component clamping, color-key ranges, gamut remap coefficients, LUT access, regamma region segmentation, and piecewise regamma parameters.
- `CUR_*`: cursor enable/mode, expansion, stereo behavior, surface address/high address, size, position, hot spot, color registers, update lock/pending/taken, request filtering, and cursor stereo control.
- `DC_LUT_*` and `DCP_CRC_*`: display LUT read/write mode, index, PWL data, 30-bit color, VGA access, write enable masks, autofill, control, black/white offsets, and CRC control/current/last/mask fields.
- `DCP_GSL_CONTROL`, `DCP_LB_DATA_GAP_BETWEEN_CHUNK`, `DCP_TEST_DEBUG_*`, `DCP_DEBUG*`, `ALPHA_CONTROL`, and `HW_ROTATION`: group-sync-lock, line-buffer data gap, debug-index/data, cursor alpha blend, and rotation support.
- `DIG_*`: digital front-end/back-end source selection, start, stereo-sync, symbol clocks, TMDS pixel encoding/color format, output CRC, clock/test/random patterns, FIFO status/recalibration, DISPCLK switch permission/interrupt, lane enables, and debug-index/data fields.
- `HDMI_*`: HDMI keepout, deep color, status/error, audio packet delay/count, ACR packet source/auto-send/N multiple, VBI packet controls, infoframe sends/continuation/line placement, generic packet controls, and general-control AVMUTE/packing fields.
- `AFMT_*`: audio formatting and packet payload controls, including audio channel enable, DP audio stream ID, HBR/60958 overrides, ISRC packets, AVI/MPEG infoframe payload bytes, generic packet bytes, ACR values/status, audio-info payload, IEC 60958 channel status fields, audio CRC, FIFO overflow, sample send, channel swap, audio source select, and DTO debug fields.
- `TMDS_*` and `LVDS_*`: TMDS sync/control characters, debug data, DC balancer, generated control bits, LVDS 24-bit/format/second-channel/polarity controls.
- `DMCU_*`: display microcontroller reset/enable/power-management ignore, interrupt masking, program/firmware address windows, firmware checksum, ERAM/IRAM host access and auto-increment, software interrupts, internal interrupt status, static-screen interrupt status, display power-gating IHC interrupts, vblank routing, DMCU-to-host and DMCU-to-UC masks, XIRQ/IRQ selection, scratch, interrupt count, firmware checksum sampling, clock gating, master/slave communication data and command mailboxes, test debug, perfmon interrupt status, and perfmon interrupt-to-UC enables.

Generated names ending in field names such as `*_MASK` produce macro identifiers like `GRPH_INTERRUPT_CONTROL__GRPH_PFLIP_INT_MASK_MASK` and `DMCU_INTERRUPT_TO_HOST_EN_MASK__UC_INTERNAL_INT_MASK_MASK`. These are not duplicate suffix mistakes in this file; they mean the hardware field itself is named `..._MASK`, and the generated macro appends `_MASK` for the bit mask.

## Control Flow

This header has no runtime control flow. It contributes compile-time numeric constants that are used by other AMDGPU code.

Typical runtime flow in consumers is:

1. Select a DCE instance by adding a CRTC, DIG, or AFMT offset to an address macro from `dce_10_0_d.h`.
2. Read the register using `RREG32` or a display-core register helper.
3. Clear a field with the `*_MASK` macro.
4. Place a new value with the matching `__SHIFT` macro, often through `REG_SET_FIELD` or `REG_UPDATE`.
5. Write the register with `WREG32`, or poll/read status fields to observe hardware state.

Concrete examples in this tree include `dce_v10_0.c` setting HDMI audio/infoframe fields using `REG_SET_FIELD`, writing `AFMT_AUDIO_PACKET_CONTROL2__AFMT_AUDIO_CHANNEL_ENABLE__SHIFT`, and clearing `GRPH_CONTROL__GRPH_ARRAY_MODE_MASK` in the panic flush path to disable display tiling before scanout.

For DCP and DIG blocks, the effective sequencing is controlled by register side effects rather than C code in this header. Surface-update locks, pending/taken bits, page-flip interrupt bits, DFQ reset/ack bits, LUT write-index/data fields, CRC enable/result fields, HDMI/AFMT update bits, FIFO error ack bits, DMCU interrupt clear bits, and perfmon interrupt clear bits are all examples where the caller must follow hardware ordering.

## State And Persistence Behavior

The file itself has no mutable state and no persistence. The constants are compiled into translation units that include the header.

The state represented by these masks is hardware state in DCE 10.0 MMIO registers. Persistence depends on the register class:

- plane configuration such as `GRPH_CONTROL`, `OVL_CONTROL1`, surface addresses, pitch, viewport coordinates, color pipeline, cursor state, and LUT/regamma state persists until reprogrammed, a mode set changes it, suspend/resume restores it, or the display block/GPU is reset;
- update/pending/taken, interrupt occurred/clear, FIFO error ack, CRC result/done, DMCU event, and perfmon interrupt bits are transient hardware status/control bits;
- DMCU ERAM/IRAM access controls, firmware address/checksum, mailbox data/command registers, scratch registers, and clock-gating controls model state shared between host driver and display microcontroller firmware;
- HDMI/AFMT packet and audio state affects what is transmitted on a display link until disabled, overwritten, or the encoder is reconfigured;
- reserved PHY macro controls may have hardware-specific behavior that is intentionally not described by these generated names.

Several fields have write-one-to-clear or clear/ack semantics implied by names such as `*_INT_CLEAR`, `*_ACK`, and `*_OVERFLOW_ACK`. Treating these as ordinary persistent bits can lose interrupts or leave status latched.

## Dependencies And Integration Points

Direct dependencies are the C preprocessor and the AMDGPU register-helper conventions. The address companion is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_d.h`

Important include and use sites in this source tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v10_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vi.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v8_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce100/dce100_resource.c`
- PowerPlay/SMU and BACO files such as `iceland_smumgr.c`, `tonga_smumgr.c`, `fiji_smumgr.c`, `polaris10_smumgr.c`, `smu7_common.h`, `fiji_baco.c`, and `tonga_baco.c`.

The DCP macros integrate with DRM CRTC/plane setup, framebuffer scanout, panic-flush scanout recovery, color management, page flips, cursor programming, and display CRC/debug paths.

The DIG/HDMI/AFMT/TMDS/LVDS macros integrate with encoder setup, audio packet programming, HDMI AVI/audio infoframe generation, ACR/N/CTS setup, audio channel routing, DP/HDMI stream encoder code, link test patterns, and debug/CRC capture.

The DMCU macros integrate with display microcontroller firmware loading/control, static-screen and ABM/backlight-related interrupts, display power-gating notifications, vblank routing to firmware, host/firmware mailbox communication, and perfmon interrupt routing.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These macros are untyped constants, so the compiler cannot verify that a mask belongs to the register being accessed, that the corresponding shift is used, or that the value fits within the field width.

This assigned range has two expected chunk-boundary artifacts. It starts at `UNIPHY_MACRO_CNTL_RESERVED1__UNIPHY_MACRO_CNTL_RESERVED__SHIFT`; the matching mask is immediately before line 4130. It ends at `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK2__DCFE1_PERFMON_COUNTER0_INT_TO_UC_EN_MASK`; the matching shift is immediately after line 7763. File-level reconciliation should account for adjacent chunks.

Generated `*_MASK_MASK` identifiers are easy to mishandle in ad hoc checks. A naive pair checker may report false mask/shift mismatches unless it treats the hardware field name separately from the generated suffix.

Plane and overlay fields are highly sensitive. Wrong tiling, pipe config, pitch, high address, surface offset, viewport end, compression surface, or DFQ setting can produce corrupted scanout, GPU memory faults, underflow, or blank display. Panic and recovery paths rely on a small subset, such as clearing `GRPH_ARRAY_MODE`, and should avoid unrelated register churn.

Update-lock and pending/taken bits require careful sequencing. Programming a surface address or LUT/regamma payload without respecting update locks and double-buffering can cause tearing, partial updates, or stale hardware state.

Color pipeline fields are numeric hardware encodings, not self-describing color-space objects. Incorrect prescale, CSC, clamp, degamma, gamut-remap, regamma, denorm, or rounding fields can cause visible color shifts that build tests will not catch.

HDMI/AFMT packet fields carry protocol-visible data. Incorrect AVI infoframe bytes, checksum, line placement, audio layout/channel enable, IEC 60958 channel numbers, ACR source, or packet send/continuous bits can break sink detection, audio playback, deep-color modes, or compliance testing.

DMCU reset, firmware address, RAM host access, interrupt mask/routing, mailbox command, and clock-gating bits can desynchronize the host driver and display microcontroller. Incorrect clear/mask behavior can lose interrupts; incorrect reset/enable sequencing can hang DMCU-assisted features.

Reserved PHY macro register definitions should be treated as addressable hardware words, not as permission to write arbitrary values. The header does not document side effects, legal values, or ASIC stepping differences.

## Test Signals

Useful validation signals are a mix of generated-header consistency, build coverage, and hardware behavior:

- Build AMDGPU configurations that include `dce_10_0_sh_mask.h`, especially DCE 10.0 display, VI-era GPU support, PowerPlay/SMU, and BACO paths.
- Run a generated-header consistency check that pairs each `*_MASK` with a matching `__SHIFT`, while allowing the two chunk-boundary artifacts and preserving hardware field names that themselves end in `_MASK`.
- Cross-check register names in this chunk against address macros in `dce_10_0_d.h`, including `GRPH_*`, `OVL_*`, `DIG_*`, `HDMI_*`, `AFMT_*`, `TMDS_*`, `LVDS_*`, and `DMCU_*`.
- Exercise DCE 10.0 modesets, page flips, cursor updates, framebuffer panic flush, suspend/resume, and multi-CRTC display operation on supported hardware.
- Validate HDMI/DP audio by checking AFMT channel enable, IEC 60958 channel status update, audio sample send, ACR behavior, and sink-side playback after mode changes.
- Use display CRC or visual tests to catch color-pipeline regressions in LUT, regamma, CSC, gamut-remap, clamp, and dither-related paths.
- Monitor DMCU/ABM/static-screen/display-power-gating interrupt behavior, including occurred/clear bits and host/UC routing masks.
- Exercise debug paths carefully: DIG/TMDS test patterns, output CRC, FIFO status, AFMT audio CRC, XDMA underflow counters, and DCP/DIG/DMCU indexed debug registers can expose field-layout mistakes without relying only on normal modeset success.
