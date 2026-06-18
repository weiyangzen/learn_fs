# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001503`: lines 1-4129, `Docs/researches/chunks/subset-b-001503_research.md`
- `subset-b-001504`: lines 4130-7763, `Docs/researches/chunks/subset-b-001504_research.md`
- `subset-b-001505`: lines 7764-11652, `Docs/researches/chunks/subset-b-001505_research.md`
- `subset-b-001506`: lines 11653-15163, `Docs/researches/chunks/subset-b-001506_research.md`
- `subset-b-001507`: lines 15164-16653, `Docs/researches/chunks/subset-b-001507_research.md`

## Chunk Research

### subset-b-001503: lines 1-4129

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_sh_mask.h lines 1-4129

## Scope And Purpose

This chunk is the first portion of the generated DCE 10.0 register field header for AMD display hardware. It defines C preprocessor constants for bit masks and bit shifts used to access fields inside display-engine registers. The paired address header, `dce_10_0_d.h`, names the MMIO registers (`mmPIPE0_PG_CONFIG`, `mmCRTC_CONTROL`, `mmDCCG_GATE_DISABLE_CNTL`, and so on); this file names the fields inside those registers.

The chunk covers the header guard, copyright/license block, and 4,104 `#define`s across 589 register names. The definitions are almost entirely mask/shift pairs in the form:

- `<REGISTER>__<FIELD>_MASK`
- `<REGISTER>__<FIELD>__SHIFT`

These constants are not executable code by themselves. They are the hardware contract consumed by the legacy `amdgpu` DCE paths, Display Core DCE 10.0 resource/hardware sequencing code, power-management code, and generic register helper macros that compose MMIO read-modify-write values.

The largest field groups in this chunk are CRTC timing/control, display GPIO/DDC/HPD/power-sequence pads, UNIPHY link/impedance controls, DCI/DMIF memory interface controls, DCCG clock controls, ABM/backlight controls, DCIO resets/debug, and per-pipe power-gating/status fields.

## Register Field API Surface

There are no functions, structs, enums, or storage declarations in this chunk. The API surface is the set of public macro constants included by C files that perform register access. Important groups include:

- `PIPE0_PG_*` through `PIPE5_PG_*`: per-display-pipe power gating force, enable, FSM readback, debug power status, requested/desired state, and power-status fields.
- `DC_IP_REQUEST_CNTL`, `DC_PGFSM_*`, `DC_PGCNTL_STATUS_REG`, and `DCPG_TEST_DEBUG_*`: display core power-gating request/FSM/debug fields.
- `BL1_PWM_*`, `DC_ABM1_*`, and `ABM_TEST_DEBUG_*`: backlight PWM, ambient backlight management, histogram/gain/luma statistics, ACE thresholds/slopes, double-buffer locks, missed-frame flags, and ABM debug indexing/data.
- `CRTC_*`: timing generator and scanout control, including DCFE clock gating, horizontal/vertical totals and blanks, sync A/B timing, triggers, flow control, stereo, master enable, blanking, interlace, counters, snapshots, start-line prefetch, interrupts, update locks, test patterns, overscan/blank/black colors, vertical interrupts, CRC windows/data, external timing sync, static-screen detection, 3D structure, and global-swap-lock fields.
- `MASTER_UPDATE_*`: master update lock and mode fields used to coordinate display-register updates.
- `DCCG_*`, `DISPCLK_*`, `SCLK_*`, `DPREFCLK_*`, `REFCLK_*`, `PIXCLK*_RESYNC_CNTL`, `CRTC[0-5]_PIXEL_RATE_CNTL`, and `DP_DTO[0-5]_*`: display clock generator, clock gating, clock turn-on/off delays, DTO phase/modulo, pixel-rate selection, add/drop pixel controls, FIFO error reporting, frequency-change ramping, and performance monitor fields.
- `SYMCLK[A-F]_CLOCK_ENABLE`, `DPDBG_CLK_FORCE_CONTROL`, `DVOACLK*`, and `DCCG_AUDIO_DTO*`: link symbol clock enables/force sources, debug clock forcing, DVO skew/clock selection, and audio DTO source/phase/module control.
- `CPLL_MACRO_CNTL_RESERVED*`, `PLL_MACRO_CNTL_RESERVED*`, `DAC_MACRO_CNTL_RESERVED*`, and `UNIPHY_MACRO_CNTL_RESERVED*`: full-register reserved macro-control fields retained for low-level programming sequences or compatibility with generated register tables.
- `DENTIST_DISPCLK_CNTL`: display clock and DP reference clock divider/change-toggle/done-toggle fields.
- `DCDEBUG_*`, `DBG_OUT_*`, `DCIO_DEBUG*`, `DCCG_TEST_DEBUG_*`, `DCI_TEST_DEBUG_*`, and `DCIO_TEST_DEBUG_*`: test muxes, debug bus selection, debug output pins, and index/data debug windows.
- `DMIF_*`, `DCI_*`, `PIPE[0-5]_DMIF_BUFFER_CONTROL`, `LOW_POWER_TILING_CONTROL`, and memory power status/control groups: display memory interface address layout, arbitration, chunk request accounting, underflow recovery, stutter/watermark status, buffer allocation, DCI clock gating, memory power forcing/disable/mode/status, and soft resets.
- `DC_GENERICA`, `DC_GENERICB`, `DC_PAD_EXTERN_SIG`, `DC_REF_CLK_CNTL`, and `DC_GPIO_DEBUG`: generic signal routing, clock/debug output selection, and DisplayPort receiver loopback/debug controls.
- `UNIPHYA` through `UNIPHYG` link/channel xbar controls and `UNIPHY_IMPCAL_LINK[A-G]`, `AUXP_IMPCAL`, `AUXN_IMPCAL`: physical-link pixel-valid reset, channel inversion, lane stagger, link enable masks, channel crossbar sources, impedance calibration enable/status/error/value/override controls, and AUX impedance calibration fields.
- `DC_GPU_TIMER_READ_CNTL`: display-domain start-position selection for GPU timer reads relative to display vblank events.
- `DCIO_*`: DCIO clock gating/ramp disable, external vsync muxing, soft resets for UNIPHY/DSYNC/DAC/DCRXPHY/DPHY blocks, DPHY lane selection, and DVO debug signals.
- `DC_GPIO_*`: generic GPIO, DVO data/control/clock, DDC1-DDC6, DDCVGA, sync, genlock/swaplock, HPD1-HPD6, panel power sequence, pad strength, AUX pad, I2C pad, DVO strength/vref/skew, and associated `MASK`, `A`, `EN`, and `Y` register fields.

## Control Flow And Usage Pattern

This header has no runtime control flow. Its values participate in control flow indirectly when driver code reads, modifies, or polls hardware registers.

The typical usage pattern is:

1. Include `dce_10_0_d.h` for register addresses and `dce_10_0_sh_mask.h` for field masks/shifts.
2. Use raw accessors such as `RREG32`/`WREG32`, or higher-level helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `REG_UPDATE`, and `REG_SET`, to compose values.
3. Apply a field mask to preserve unrelated register bits and use the shift constant to position the requested field value.
4. Poll status fields or write clear bits for interrupts, power-state transitions, update locks, missed-frame flags, CRC status, HPD/DDC/AUX pad state, and underflow/debug conditions.

Representative consumers include `amdgpu/dce_v10_0.c`, which includes this header next to `dce_10_0_d.h` and `dce_10_0_enum.h`, and Display Core DCE 10.0 files such as `display/dc/resource/dce100/dce100_resource.c` and `display/dc/hwss/dce100/dce100_hwseq.c`. Related VI-era paths in `gfx_v8_0.c`, `gmc_v8_0.c`, `vi.c`, BACO handlers, and SMU managers also include the same generated field header when they need shared display/DC bit definitions.

## State And Persistence Behavior

The file itself is stateless and produces no persistent data. The persistent state affected by these constants lives in hardware registers and hardware-managed latches:

- Power-gating fields can force, request, enable, or report display-pipe and memory power states.
- CRTC fields hold active timing, blanking, sync, stereo, trigger, CRC, snapshot, interrupt, static-screen, and update-lock state until driver code or hardware events change them.
- ABM/backlight fields hold PWM duty-cycle inputs/outputs, ambient/backlight source selection, histogram/luma readbacks, ACE thresholds/slopes, and double-buffer lock/update-pending state.
- DCCG/DCI/DCIO fields control clock gating, clock dividers, soft resets, debug routing, DTO accumulators, and memory power state.
- GPIO/DDC/AUX/HPD fields expose pad masks, enables, observed input values, pull/power behavior, AUX mode/polarity, and panel power-sequence outputs.

Several fields are edge- or event-oriented rather than simple configuration bits. Examples include `*_CLEAR`, `*_OCCURRED`, `*_UPDATE_PENDING`, `*_MISSED_FRAME`, `*_READ_IN_PROGRESS`, `*_CHGTOG`, `*_DONETOG`, and interrupt status/type/mask fields. Incorrect mask or shift values can leave state uncleared, clear the wrong event, or make polling loops wait forever.

## Dependencies And Integration Points

The primary dependency is the matching generated register-address file, `dce_10_0_d.h`. Register address macros and field mask/shift macros must stay synchronized: a correct field applied to the wrong `mm*` address is just as dangerous as a wrong mask.

The field naming convention is also a dependency. AMD register helper macros derive names by token pasting. A call that names register `CRTC_CONTROL` and field `CRTC_MASTER_EN` expects `CRTC_CONTROL__CRTC_MASTER_EN_MASK` and `CRTC_CONTROL__CRTC_MASTER_EN__SHIFT` to exist with exactly those spellings. Generated names with repeated words such as `*_MASK_MASK` are intentional where the hardware field name itself ends in `MASK`.

Integration points include:

- Legacy `amdgpu` DCE code for mode setting, vblank/vline/HPD interrupt handling, display enable/disable, CRTC master enable, scanout state, and atomic-style register programming.
- Display Core DCE 10.0 resource construction and hardware sequencing, which pass register lists, shifts, and masks into reusable DCE blocks such as timing generators, link encoders, stream encoders, memory input, transforms, output pixel processors, panel control, AUX, I2C, DMCU, and ABM.
- VI-era power management and BACO/SMU paths that need DCE field definitions while entering low-power states, managing display clocks, or coordinating static-screen/display events with the SMU.
- Adjacent generated headers for DCE 8.0, DCE 11.x, DCE 12.0, DCN, and DPCS blocks. Many field names are shared across hardware generations, so mismatches can produce compile-time errors in shared code or subtle behavior changes when a generation-specific include is selected.

## Risks And Edge Cases

The highest risk is silent hardware misprogramming. These macros are constants, so most errors compile cleanly while causing display failures at runtime.

Specific risks include:

- Mask/shift mismatch: a stale shift paired with a new mask can write neighboring fields in the same register.
- Width errors: fields such as CRTC counters, CRC window coordinates, DMIF request limits, GPIO drive strength, and ABM histogram/luma data have nonuniform widths; truncation or over-wide masks can corrupt adjacent configuration.
- Register-generation drift: DCE 10.0 shares many names with DCE 8.0, DCE 11.x, DCE 12.0, and DCN headers, but offsets and available fields vary. Copying a field across generations without validating the generated table can break only one ASIC family.
- Event clear/status confusion: interrupt, snapshot, force-vsync, trigger, static-screen, sync-loss, and missed-frame fields frequently pair status and clear bits in the same register. A bad definition can leave interrupts stuck or accidentally acknowledge events.
- Power/reset sequencing hazards: `PIPE*_PG_*`, `DCI_MEM_PWR_*`, `DCCG_*_GATE_DISABLE`, `DCIO_SOFT_RESET`, `DCCG_SOFT_RESET`, and `DCI_SOFT_RESET` fields affect clocked hardware domains. Wrong values can make subsequent register access unreliable.
- GPIO/DDC/AUX/HPD pad control hazards: duplicated `MASK`, `A`, `EN`, and `Y` layouts are easy to mix up. Incorrect masks can break monitor detection, AUX transactions, panel power sequencing, genlock/swaplock, or DVO output.
- Generated-name pitfalls: fields whose names end in `MASK` generate macros like `DC_GPIO_DDC1_MASK__DC_GPIO_DDC1CLK_MASK_MASK`; consumers must use the exact generated name rather than simplifying it.

## Test Signals

There are no unit tests for this header alone. Useful signals are build-time and hardware/driver behavior:

- Compile coverage of `amdgpu`, `amd/display`, and `pm/powerplay` users catches missing or misspelled generated macros, especially token-pasted `REG_*` field references.
- Display bring-up on DCE 10.0/VI hardware catches gross CRTC, DCCG, DCIO, UNIPHY, GPIO, and power-gating field errors through black screens, failed modesets, clock failures, or hung polling loops.
- DRM/KMS tests that exercise modeset, vblank, CRC capture, DPMS, hotplug, DDC/EDID reads, DisplayPort AUX, backlight/ABM, suspend/resume, and multi-display synchronization are the strongest behavioral checks.
- Power-management tests for BACO, clock gating, display idle/static-screen, and suspend/resume can reveal bad DCI/DCCG/DCIO memory-power and soft-reset fields.
- Register readback/debug tools are useful for comparing expected field placement against hardware documentation: read a register, apply the generated mask/shift, and confirm the decoded field changes only when the intended hardware setting changes.

Because the file is generated register metadata, review should focus on whether this header matches the authoritative DCE 10.0 register specification and remains paired with the correct `dce_10_0_d.h` address table. Normal code-level tests cannot prove every bit position without hardware or generated-table validation.

### subset-b-001504: lines 4130-7763

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

### subset-b-001505: lines 7764-11652

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_sh_mask.h lines 7764-11652

## Scope And Purpose

This chunk is a generated-style AMD DCE 10.0 register shift/mask header section. It contains only C preprocessor constants for bitfield masks and shifts; there are no functions, structs, enums, or executable branches. The mapped range starts mid-register at `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK2` and ends at `PLL_CNTL__PLL_VCOREF__SHIFT`, so the first and last register groups are partial chunk boundaries.

The purpose is to give AMDGPU and display code symbolic access to DCE 10.0 hardware fields for Display Microcontroller Unit interrupt routing, DisplayPort link/AUX handling, DVO output, framebuffer compression, formatter/dithering, line buffer and multi-view pipe state, scaler/filter setup, color management, unpinned graphics plane programming, legacy VGA compatibility, DAC calibration, and display PLL programming.

## Important APIs, Types, And Macro Families

The public interface is the macro namespace itself. Each register field is expressed as a paired `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` definition. Consumers typically use helpers such as `REG_SET_FIELD()` or direct `(value & MASK) >> SHIFT` / `(field << SHIFT) & MASK` expressions together with the sibling DCE 10.0 address header.

Important macro families in this chunk include:

- DMCU performance-monitor interrupt routing: `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK2` through `MASK5`, `DMCU_PERFMON_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1` through `SEL5`, and `DMCU_PERFMON_INTERRUPT_TO_HOST_EN_MASK1` through `MASK5` route DCI, DCO, DCCG, DCFE0-5, WB, DCRX, and DCFEV performance counter interrupts to the microcontroller, XIRQ/IRQ selection, or host.
- DMCU DPRX interrupt reporting and routing: `DMCU_DPRX_INTERRUPT_STATUS1`, `DMCU_DPRX_INTERRUPT_TO_UC_EN_MASK1`, and `DMCU_DPRX_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1` cover stream events, vertical interrupts, SDP/MSA reception, VBID toggles, DisplayPort PHY error thresholds, loss of alignment/deskw, excessive error events, AUX/I2C/CPU interrupts, and AUX message timeouts.
- DisplayPort main-link and secondary-data controls: `DP_LINK_CNTL`, `DP_PIXEL_FORMAT`, `DP_MSA_COLORIMETRY`, `DP_CONFIG`, `DP_VID_STREAM_CNTL`, `DP_STEER_FIFO`, `DP_MSA_MISC`, timing, `DP_DPHY_*`, CRC, fast-training, MSA overrides, secondary packet/audio/timestamp controls, and MST/MSE rate-allocation registers define link framing, lane count, pixel encoding, TU, training, PRBS, scrambling, CRC, audio packetization, and multi-stream bandwidth state.
- AUX and GTC synchronization: `AUX_CONTROL`, `AUX_SW_CONTROL`, `AUX_ARB_CONTROL`, `AUX_INTERRUPT_CONTROL`, `AUX_SW_STATUS`, `AUX_LS_STATUS`, `AUX_SW_DATA`, `AUX_LS_DATA`, `AUX_DPHY_*`, `AUX_GTC_SYNC_*`, and `DP_AUX_DEBUG_*` describe AUX transaction command/status, HPD/AUX arbitration, I2C-over-AUX, low-speed data, PHY controls, global-time-code sync, phase offset, and debug readback.
- DVO and FBC: `DVO_ENABLE`, `DVO_SOURCE_SELECT`, `DVO_OUTPUT`, `DVO_CONTROL`, DVO CRC/FIFO/debug fields, plus `FBC_CNTL`, `FBC_IDLE_*`, `FBC_COMP_*`, `FBC_IND_LUT*`, CSM/client-region fields, debug CSR fields, `FBC_MISC`, and `FBC_STATUS` describe digital video output and framebuffer compression control/status.
- Formatter, line buffer, and multi-view pipe: `FMT_*` fields cover clamping, dynamic expansion, forced output, bit-depth conversion, truncation, dithering, CRC, and debug. `LB_*` and `LBV_*` cover line-buffer format, memory sizing, vline/vblank interrupts, urgency/status, keying, counters, and debug for primary/video paths. `MVP_*` covers AFR flip behavior, FIFO status, in-band controls, CRC, receive counters, and debug.
- Scaler and viewport programming: `SCL_*` and `SCLV_*` fields define coefficient RAM access, mode, tap selection, filter scale ratios/init phases, manual/automatic replication, bypass/update controls, viewport and overscan rectangles, mode-change detection, chroma-plane video-scaler parameters, and test/debug access.
- Color management and gamma: `COL_MAN_*`, `INPUT_CSC_*`, `OUTPUT_CSC_*`, `PRESCALE_*`, `DENORM_CLAMP_*`, `GAMMA_CORR_*`, and debug fields describe CSC matrix coefficients, prescale values, denormal clamp ranges, gamma LUT index/data/write enable, and piecewise gamma-region controls for A/B segments.
- Unpinned graphics plane: `UNP_GRPH_*` fields cover enablement, format/tiling/bank/pipe controls, stereo, swap controls, primary/secondary luma/chroma surface addresses, high address words, pitch, offsets, start/end coordinates, update pending/lock behavior, in-use addresses, data-fabric queue status, flip interrupts, CRC, rotation, and debug.
- VGA compatibility and legacy indexed registers: `GENMO_*`, `SEQ*`, `CRT*`, `GRA*`, `ATTR*`, `VGA_RENDER_CONTROL`, `VGA_SOURCE_SELECT`, `VGA_SEQUENCER_RESET_CONTROL`, `VGA_MODE_CONTROL`, `VGA_MEMORY_BASE_ADDRESS*`, `D1VGA_CONTROL` through `D6VGA_CONTROL`, VGA interrupt/status/clear/debug/page fields, and `VGADCC_DBG_DCCIF_C` describe legacy VGA register access and routing onto modern display pipes.
- Analog DAC and PLL controls: `BPHYC_DAC_MACRO_CNTL`, `BPHYC_DAC_AUTO_CALIB_CONTROL`, `PLL_REF_DIV`, `PLL_FB_DIV`, `PLL_POST_DIV`, `PLL_SS_*`, `PLL_DS_CNTL`, `PLL_IDCLK_CNTL`, and the initial `PLL_CNTL` fields define DAC white level/bandgap/monitoring/calibration and display PLL dividers, spread spectrum, delta-sigma modulation, IDCLK outputs, differential post-divider behavior, current/drive strength, reset, power-down, bypass, post-divider source, and VCO reference bits.

## Control Flow And Data Flow

This header chunk has no runtime control flow. Its data flow is compile-time substitution into register access sequences in DCE 10.0 display, AMDGPU, and power-management code.

The implied hardware flows are still important:

- Interrupt routing fields select whether DMCU-visible performance and DPRX events are delivered to firmware, a selected XIRQ/IRQ line, or the host.
- DisplayPort programming combines link-control, pixel-format, timing, DPHY, CRC, secondary-data, and MST/MSE fields with per-encoder register offsets to bring up or validate a link.
- AUX programming writes command/address/data fields, arbitrates SW versus HPD/AUX access, then polls status, reply, timeout, defer, or error fields.
- Formatter, line-buffer, scaler, color-management, and unpinned-graphics fields are programmed in display pipe update sequences, often using locked/update-pending bits so plane, scaler, color, and timing state changes become visible at a safe point.
- FBC fields describe enable/compression/mode/LUT/state registers that compression management code can program and then inspect through status/debug fields.
- VGA fields bridge indexed legacy VGA state to DCE display pipes, including source selection, surface addresses, sequencer reset behavior, memory access status, interrupt masking, and page-address windows.
- PLL and DAC fields are low-level hardware sequencing inputs; callers must reset/power/calibrate/program dividers in the order required by the ASIC and board tables.

## State And Persistence Behavior

The header stores no state. Persistent and mutable state lives in DCE 10.0 MMIO registers, indexed VGA registers, display firmware/DMCU-visible interrupt state, display pipe shadow registers, framebuffer-compression state machines, AUX transaction state, DP link-training status, DAC calibration logic, and PLL hardware.

State classes represented by this chunk include:

- Latched or sticky event state: DMCU DPRX interrupt status, AUX interrupt/status bits, DP CRC results, DVO FIFO errors, FBC status, LB/LBV vline and vblank status, MVP FIFO/status counters, VGA access/interrupt status, and DAC calibration completion.
- Mutable configuration state: DP link enable/lane/pixel/timing/training, AUX command/arbitration/PHY settings, DVO output source, FBC enable/mode/LUTs, formatter dithering/truncation/CRC, line-buffer formats and urgency thresholds, scaler taps/ratios/viewports, CSC/gamma tables, UNP surface addresses and format, VGA mode/source/page controls, DAC calibration controls, and PLL divider/spread-spectrum controls.
- Shadowed update state: plane addresses, viewport/overscan, scaler coefficients, color-management tables, and unpinned graphics update locks/pending flags are designed to synchronize hardware-visible display changes.
- Hardware-derived diagnostic state: DP/AUX debug readbacks, FBC debug CSR data, MVP and VGA debug data, DPHY error/CRC counters, line-buffer status, and PLL/DAC monitor fields.

Incorrect constants can persist until the relevant block is reprogrammed or reset. For example, a wrong surface-address, scaler, gamma, or PLL mask can affect active scanout; a wrong interrupt mask can hide hotplug/AUX/DPRX errors; a wrong FBC field can leave compression in an invalid state; and a wrong VGA memory-control bit can expose or block legacy apertures.

## Dependencies And Integration Points

This header is included by DCE 10.0 display and VI-era AMDGPU code, including `amdgpu/dce_v10_0.c`, `amdgpu/vi.c`, `amdgpu/mxgpu_vi.c`, `amdgpu/gmc_v8_0.c`, `amdgpu/gfx_v8_0.c`, DC DCE100 resource/hwseq code, and legacy PowerPlay/SMU managers such as Tonga, Fiji, Iceland, and Polaris paths. It is normally paired with DCE 10.0 register address definitions and AMDGPU register helpers (`RREG32`, `WREG32`, `REG_SET_FIELD`, and offset-based CRTC/encoder access).

Concrete repository usage in this namespace includes `dce_v10_0.c` programming `FMT_BIT_DEPTH_CONTROL` through `REG_SET_FIELD()` for display dithering/truncation based on framebuffer depth. Similar DCE generations use the same mask/shift style directly, so these macros are part of a shared AMD display-driver idiom even when some fields in this chunk are consumed only on specific ASICs, boards, firmware paths, or diagnostic flows.

Major integration surfaces are:

- DRM/KMS mode setting, CRTC, encoder, connector, and plane code for display format, timing, scaler, viewport, color, and scanout-address programming.
- DisplayPort link training, MST allocation, secondary-data/audio packet generation, and AUX/I2C transaction handling.
- DMCU and host interrupt plumbing for performance counters, DPRX events, AUX events, vline/vblank-like line-buffer events, VGA events, and error/status clear flows.
- Power-management and BACO/SMU paths that include the header for display PLL, clock, DAC, compression, or DCE power/display state programming.
- Legacy VGA emulation and early boot/display handoff code that must map indexed VGA registers and VGA apertures onto DCE display pipes.
- Hardware diagnostics, debugfs-style readback, bring-up scripts, and ASIC validation paths that rely on debug indices/data, CRC results, PRBS/training, FBC status, and FIFO/error counters.

## Risks And Edge Cases

The primary risk is drift between generated constants and the DCE 10.0 register specification. Since many consumers write hardware with generic field helpers, the compiler cannot detect an incorrect mask value or shift position.

Specific high-risk areas in this chunk are:

- Chunk boundaries: line 7764 starts after the first field of `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK2`, and line 11652 stops before the rest of `PLL_CNTL`; full-register conclusions require adjacent chunk research.
- Repeated bit layouts across pipes and paths: DCFE0-5, D1-D6 VGA controls, LB/LBV, SCL/SCLV, and luma/chroma UNP address fields are easy to copy incorrectly because names differ only by pipe, plane, or component suffix.
- Interrupt mask/status naming: fields with `MASK_MASK`, `INT_MASK`, `STATUS`, `CLEAR`, `TO_UC_EN`, `TO_HOST_EN`, and `XIRQ_IRQ_SEL` have similar names but different semantics; confusing enable, mask, route, clear, and status bits can drop or storm interrupts.
- DisplayPort/AUX training sensitivity: incorrect DPHY, AUX timing, CRC, PRBS, or fast-training fields can cause link-training failures, AUX timeouts, or false error reporting.
- Atomic display updates: surface address, scaler, viewport, color, and update-lock bits must line up with hardware shadow/update behavior; wrong masks can produce tearing, bad scanout, or stale register programming.
- FBC and line-buffer state: compression and buffer-urgency fields affect memory bandwidth and scanout correctness; wrong values can cause corruption or underflow.
- VGA compatibility: legacy indexed registers, aperture paging, sequencer reset, and memory-disable bits can affect boot consoles, handoff, and host-visible VGA behavior.
- Analog and PLL programming: DAC calibration and PLL divider/spread-spectrum fields are board/ASIC-sensitive; bad masks can produce unstable clocks, no display output, or analog signal-quality failures.

## Test Signals

There are no unit tests for this header alone. Useful validation is mostly build, generated-header comparison, and hardware integration testing:

- Build AMDGPU and DC configurations that include `dce_10_0_sh_mask.h`; this catches missing or renamed macros but not wrong numeric values.
- Compare the chunk against the authoritative AMD DCE 10.0 register database or an upstream generated copy, paying special attention to the partial `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK2` and `PLL_CNTL` boundaries.
- Exercise DCE 10.0 display mode setting across multiple CRTCs and formats; verify `FMT_BIT_DEPTH_CONTROL`, scaler, viewport, color, line-buffer, and UNP surface programming by visual output and register readback.
- Run DisplayPort link-training, MST, audio/secondary-data, AUX/I2C, hotplug, and error-path tests that validate DP, AUX, DPRX, and DMCU interrupt fields.
- Validate vblank/vline, AUX, VGA, and DPRX interrupt mask/status/clear behavior with interrupt counters and timeout/error injection where possible.
- Test FBC enable/disable, idle behavior, compression status, and debug readback under scanout workloads.
- Exercise legacy VGA handoff or VGA-compatible modes to verify source selection, sequencer reset, aperture paging, VGA memory/reg access status, and D1-D6 pipe routing.
- Validate suspend/resume, power-management, DAC calibration, and PLL programming paths through display bring-up, clock readback, and signal/link stability tests.

### subset-b-001506: lines 11653-15163

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_sh_mask.h lines 11653-15163

## Purpose

This chunk is a generated-style DCE 10.0 register bitfield map. It defines `_MASK` and `__SHIFT` constants for 32-bit MMIO registers in the AMD display controller block, starting in the generic display PLL control fields and ending partway through the `DISP_INTERRUPT_STATUS_CONTINUE5` fields.

The range is not executable code. Its purpose is to let the DCE 10.0 driver, power-management code, and common register helpers read and write named hardware fields without open-coded bit positions. The covered register families describe display clock PLLs, VGA/PPLL variants, UNIPHY transmitter and link PLL controls, display pipe/gating watermarks, the Azalia/HD-audio controller and codec endpoint register windows, blender/writeback/converter blocks, DCFE/DCFEV clocks and memory power state, HPD interrupt control, scratch registers, VCE display control, and the display interrupt status cascade for pipes/connectors 1 through the start of 6.

## Important APIs, Types, And Functions

There are no C functions, structs, enums, or runtime APIs in this range. The important exported interface is the macro naming contract:

- `REGISTER__FIELD_MASK`: the bit mask for `FIELD` inside `REGISTER`.
- `REGISTER__FIELD__SHIFT`: the low-bit shift for the same field.
- Full-register fields, such as `PPLL_SPARE0__PLL_SPARE0_MASK` or `AZALIA_STREAM_DEBUG__STREAM_DEBUG_DATA_MASK`, use `0xffffffff` and shift `0`.
- Repeated instance fields use duplicated register families, for example `VGA25_PPLL_*`, `VGA28_PPLL_*`, `VGA41_PPLL_*`, `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, `SINK_DESCRIPTION0` through `SINK_DESCRIPTION17`, and `DISP_INTERRUPT_STATUS_CONTINUE*`.

The consumers are the AMDGPU register helpers and driver code that include this header alongside `dce_10_0_d.h`, which supplies the `mm...` register addresses. In `amdgpu/dce_v10_0.c`, the file is included directly and the interrupt map uses these constants, for example `DISP_INTERRUPT_STATUS__LB_D1_VBLANK_INTERRUPT_MASK` through `DISP_INTERRUPT_STATUS_CONTINUE5__LB_D6_VBLANK_INTERRUPT_MASK` and matching HPD masks. The same style is used with `REG_SET_FIELD`, `RREG32`, `WREG32`, and audio endpoint accessors in the display driver.

## Covered Register Families

The clock and PHY portion covers:

- `PLL_CNTL`, `PLL_ANALOG`, `PLL_VREG_CNTL`, `PLL_UNLOCK_DETECT_CNTL`, `PLL_DEBUG_CNTL`, `PLL_UPDATE_LOCK`, `PLL_UPDATE_CNTL`, `PLL_XOR_LOCK`, and `PLL_ANALOG_CNTL`. These fields cover PLL reset/power down, reference-clock selection, calibration, lock status, spread/update state, debug muxing, analog trims, and lock detector controls.
- `VGA25_PPLL_*`, `VGA28_PPLL_*`, and `VGA41_PPLL_*` reference, feedback, post-divide, and analog controls. These duplicate the PPLL programming shape for legacy VGA-related clocks.
- `DISPPLL_BG_CNTL`, `PPLL_DIV_UPDATE_DEBUG`, `PPLL_STATUS_DEBUG`, `PPLL_DEBUG_MUX_CNTL`, and spare PPLL words. These expose display PLL bandgap, divider-update handshake/debug, calibration/power-good status, and debug bus muxes.
- `UNIPHY_TX_CONTROL1` through `UNIPHY_TX_CONTROL4`, `UNIPHY_POWER_CONTROL`, `UNIPHY_PLL_FBDIV`, `UNIPHY_PLL_CONTROL1`, `UNIPHY_PLL_CONTROL2`, `UNIPHY_PLL_SS_*`, `UNIPHY_DATA_SYNCHRONIZATION`, `UNIPHY_REG_TEST_OUTPUT*`, `UNIPHY_ANG_BIST_CNTL`, `UNIPHY_TMDP_REG0` through `UNIPHY_TMDP_REG6`, `UNIPHY_TPG_*`, and `UNIPHY_DEBUG`. These describe DisplayPort/HDMI/LVDS PHY drive strength, pre-emphasis, voltage swing, PLL enable/reset/reference source, spread spectrum, data synchronization, BIST, impedance calibration, test-pattern generation, and debug readback fields.

The display pipe, audio, and memory/power portion covers:

- `DPG_PIPE_*` fields for arbitration weights, urgency watermarks, DPM and memory-clock-change gates, stutter/self-refresh behavior, non-latch stutter controls, repeater programming, and DPG debug/test access.
- Azalia root/function/codec/stream/controller fields, including immediate command interfaces, HD-audio global capabilities/control/status, CORB/RIRB DMA rings, stream descriptors, wall-clock and DMA position buffers, output/input converter fields, pin sense/configuration defaults, ELD-like sink description and audio descriptor storage, channel/speaker allocation, LPIB snapshots, hot-plug/unsolicited response controls, GTC embedding/debug counters, CRC engines, clock gating, DTO phase/module, DMA cache/isochronous attributes, memory power control/status, FIFO/latency counters, and stream debug.
- `BLND_*`, `SM_CONTROL2`, `WB_*`, and `CNV_*` fields for blender mode, alpha/flow control, stereo sync mode, update locks/status, underflow interrupts, writeback enable/error-correction/debug, and converter mode/window/source-size/color-space-conversion/CRC/debug controls.
- `DCFE_*` and `DCFEV_*` clock control, soft reset, debug, DMIFV clock, and DMIFV memory power control/status fields.
- `DC_HPD_*` fields for hot-plug sense, RX interrupt status, ack, polarity, enable, HPD logic enable, fast-training enable, and connect/disconnect debounce delays.
- `DCO_SCRATCH0` through `DCO_SCRATCH7` and `DCE_VCE_CONTROL`, which provide scratch words and display/VCE shared control bits.
- `DISP_INTERRUPT_STATUS` through `DISP_INTERRUPT_STATUS_CONTINUE5`, ending at `CRTC6_FORCE_VSYNC_NEXT_LINE_INTERRUPT`. These define the cascade of latched display events for scalers, blender underflow, line-buffer vline/vblank, CRTC snapshot/trigger/vsync/timing-sync/vertical events, DIG DP fast-training or stream-disable events, HPD/AUX completion events, DMCU/ABM events, writeback conflicts/overflows, performance monitor events, and continuation bits to the next status word.

## Control Flow

This header has no control flow. At compile time, it expands into constants used by higher-level code to build bit masks and shifts. At runtime, the behavior appears in consumers:

1. A driver reads a DCE 10.0 register address from `dce_10_0_d.h`.
2. It uses a mask and shift from this header directly, or through helpers such as `REG_SET_FIELD` and field-read macros.
3. It performs MMIO access with helpers such as `RREG32()` and `WREG32()`, sometimes adding per-instance offsets such as CRTC, HPD, DIG, or audio endpoint offsets.

The display interrupt status definitions are a concrete control-flow dependency. `dce_v10_0.c` builds an `interrupt_status_offsets[]` table mapping each status register to its vblank, vline, and HPD mask. IRQ handling can then index by CRTC/HPD instance and test the correct status bits rather than branching on individual register names.

## State And Persistence Behavior

The macros hold no software state and allocate nothing. They describe persistent hardware state stored in MMIO registers. Writes performed by consumers affect display engine state until overwritten, reset, power-gated, or reinitialized by firmware/driver paths.

The state represented by this chunk is broad and hardware-visible:

- PLL/PPLL/UNIPHY fields persist clock generation, link PHY calibration, drive levels, spread-spectrum, and lock/update handshakes.
- DPG/DCFE/DCFEV/Azalia memory power fields persist clock and power gating decisions that interact with display underflow avoidance and runtime power management.
- Azalia stream descriptor, CORB/RIRB, DMA position, codec endpoint, audio descriptor, sink description, and channel-allocation fields persist the HDMI/DP audio programming visible to the audio codec model and display sinks.
- HPD and display interrupt status/control fields persist latched hardware events and enable/ack state used by interrupt handling.
- Debug, CRC, scratch, and test-pattern fields persist diagnostic configuration and readback until changed or reset.

Because the constants encode raw hardware layout, any mismatch is effectively a state corruption bug in the consumer: a read may sample the wrong status bit, or a write may alter unrelated hardware fields.

## Dependencies

This chunk depends on the DCE 10.0 register-address header `dce_10_0_d.h`; the masks are only meaningful when paired with the corresponding `mm...` or indexed `ix...` register offsets. It also depends on AMDGPU's register helper conventions, especially field-setting/extraction macros that concatenate `REGISTER`, `FIELD`, `_MASK`, and `__SHIFT` names.

The major integration dependencies are:

- `drivers/gpu/drm/amd/amdgpu/dce_v10_0.c`, which directly includes this header for DCE 10.0 display, audio, HPD, watermark, and interrupt handling.
- ASIC initialization and virtualized GPU support paths, including `vi.c`, `mxgpu_vi.c`, `gfx_v8_0.c`, and `gmc_v8_0.c`, which include the DCE 10.0 mask header as part of the VI-generation register environment.
- Power-management code under `pm/powerplay`, including Tonga/Fiji/Iceland/Polaris SMU and BACO paths, which include the header and use DCE/DPG/clock/power field definitions when coordinating display watermarks, stutter state, and low-power transitions.
- Display/audio protocols outside this file: HDMI/DP audio capabilities, HD-audio CORB/RIRB mechanics, HPD/AUX interrupt semantics, and link PHY/PLL programming rules.

## Integration Points

The most visible integration point in the covered lines is the display interrupt cascade. `DISP_INTERRUPT_STATUS` through `DISP_INTERRUPT_STATUS_CONTINUE5` map events for CRTC/display pipes 1-6 and DIG/HPD/AUX blocks. The masks let IRQ code detect vblank/vline/HPD and let diagnostic code distinguish underflow, DP training, stream-disable, timing-sync, and ABM/DMCU events.

The HPD fields integrate connector detection and link training. `DC_HPD_INT_STATUS`, `DC_HPD_INT_CONTROL`, `DC_HPD_CONTROL`, `DC_HPD_FAST_TRAIN_CNTL`, and `DC_HPD_TOGGLE_FILT_CNTL` are used around connector hotplug sense, interrupt polarity, ack/enable, and debounce timing. Incorrect bit definitions here can cause missed hotplug events, interrupt storms, or inverted connect/disconnect detection.

The Azalia fields integrate the display engine with the HD-audio codec model. `dce_v10_0.c` uses indexed endpoint accesses for codec pin and converter registers, and these masks support sink audio descriptors, speaker/channel allocation, LPIB snapshots, HBR, unsolicited responses, codec power state, and audio stream format programming. This is the bridge between DRM connector/audio setup and the GPU's HDMI/DP audio function.

The PLL and UNIPHY fields integrate modesetting with clock/link programming, mostly through AtomBIOS or display helpers that need exact divider, lock, calibration, drive-strength, voltage-swing, and pre-emphasis fields. Even when a given consumer does not open-code every field in this header, the definitions form the ABI between generated register maps and clock/link management code.

The DPG/DCFE/DCFEV fields integrate display timing with power management. Watermark, stutter, NB p-state, memory power, and clock-gating fields coordinate scanout latency tolerance with SMU/DPM decisions. These definitions are therefore cross-owned by display and power-management paths.

## Risks And Edge Cases

- This is generated register metadata with no runtime validation. A single wrong mask or shift can silently target the wrong hardware bit.
- The chunk starts mid-register family at `PLL_CNTL`; earlier `PLL_REF_DIV`, `PLL_FB_DIV`, post-divide, spread-spectrum, and IDCLK fields are in the previous chunk. A merged per-file report should preserve that boundary.
- The chunk ends mid-family at `DISP_INTERRUPT_STATUS_CONTINUE5__CRTC6_FORCE_VSYNC_NEXT_LINE_INTERRUPT`; the rest of pipe-6 status and `DISP_INTERRUPT_STATUS_CONTINUE6` continue after this range.
- The macros are not namespaced by C types. Collisions are avoided only by generated naming discipline. Manual additions must preserve the exact `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` spelling expected by helper macros.
- Repeated audio descriptor, sink description, multichannel, and interrupt-status families are copy/paste sensitive. An off-by-one instance name or bit position can affect only one connector, stream, or pipe and be difficult to spot in broad testing.
- Some fields represent write-one-to-clear, sticky status, or hardware handshake state in consumers. Treating all masks as ordinary read/write fields can break interrupt acknowledgement, PLL update sequencing, HPD ack, or CRC/test completion.
- PLL, PPLL, UNIPHY, and HPD controls are timing-sensitive. Wrong programming can produce link instability, blank displays, failed DP training, or audio clock drift rather than clean software errors.
- Power-management fields such as DPG stutter, NB p-state, DCFEV memory power, and Azalia memory power interact with active scanout and audio DMA. Incorrect masks can manifest as underflow, hangs during suspend/resume, or rare display corruption.
- Many full-register masks intentionally use `0xffffffff`; consumers must still know whether the underlying register is read-only, write-only, sticky, or indexed through an address/data pair.

## Test Signals

Useful validation signals are mostly compile-time, hardware bring-up, and display/audio behavior:

- A DCE 10.0 kernel build should compile with this header included by `dce_v10_0.c`, PM, and VI-generation files, proving macro names match helper expectations.
- Static checks can compare every `_MASK`/`__SHIFT` pair for matching register/field names and verify repeated families have consistent instance coverage.
- Modesetting tests should cover HDMI, DisplayPort, and legacy/VGA-adjacent paths that exercise PPLL/UNIPHY programming, including link training, resolution changes, blank/unblank, and suspend/resume.
- IRQ tests should verify vblank, vline, HPD connect/disconnect, AUX completion, DP fast-training, stream-disable, and underflow events are detected and acknowledged on the correct pipe/connector.
- Audio tests should validate HDMI/DP audio enumeration, sink ELD/audio descriptor programming, sample-rate and channel layouts, HBR/non-audio modes, hotplug audio enable/disable, and LPIB position reporting.
- Power-management tests should watch for display underflow, audio glitches, or missed interrupts while toggling stutter, NB p-state changes, clock gating, BACO/suspend, and runtime DPM states.
- Register-dump comparison against known-good DCE 10.0 hardware documentation or generated headers should flag any drift in PLL, UNIPHY, Azalia, HPD, DCFE, and interrupt masks.

### subset-b-001507: lines 15164-16653

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_sh_mask.h lines 15164-16653

## Purpose

This chunk is the final section of the generated AMDGPU DCE 10.0 register field mask/shift header. It contains no executable C logic; it publishes compile-time constants that describe packed bit fields in display-controller hardware registers for ASICs using the DCE 10.0 register map.

Each field is represented as a pair of macros:

- `REGISTER__FIELD_MASK` is the already-positioned bit mask.
- `REGISTER__FIELD__SHIFT` is the least-significant bit position for that field.

Driver code uses these constants with register addresses from the matching DCE address header, `dce_10_0_d.h`, and normal AMDGPU register access helpers. This chunk covers the tail of the display interrupt status chain, DCO clock/power/reset and I2C/DDC field layouts, and the XDMA display DMA master/slave register field layouts. The file ends at the `DCE_10_0_SH_MASK_H` include guard footer.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or callbacks in this range. The macro namespace is the API surface consumed by DCE 10.0 display, interrupt, power-management, and diagnostics code.

Major macro groups in this chunk are:

- Display interrupt continuation registers: the range starts in `DISP_INTERRUPT_STATUS_CONTINUE5` and continues through `DISP_INTERRUPT_STATUS_CONTINUE9`. These fields expose CRTC6 timing and trigger interrupts, DIGF/DIGG DisplayPort training and stream-disable interrupts, HPD6/AUX6 interrupts, DCRX/DCCG/DCI/DCO/DCFE/WB performance-counter interrupts, CWB buffer-manager interrupts, AUX1-AUX6 GTC sync lock/error interrupts, and chained continuation bits such as `DISP_INTERRUPT_STATUS_CONTINUE6`, `CONTINUE7`, `CONTINUE8`, and `CONTINUE9`.
- DCO memory, clock, power, and reset controls: `DCO_MEM_PWR_STATUS`, `DCO_MEM_PWR_CTRL`, `DCO_MEM_PWR_CTRL2`, `DCO_CLK_CNTL`, `DCO_CLK_RAMP_CNTL`, `DPDBG_CNTL`, `DPDBG_INTERRUPT`, `DCO_POWER_MANAGEMENT_CNTL`, `DCO_SOFT_RESET`, `DIG_SOFT_RESET`, stereo sync selection, and DCO debug index/data registers.
- Display I2C/DDC controls: `DC_I2C_CONTROL`, `DC_I2C_ARBITRATION`, `DC_I2C_INTERRUPT_CONTROL`, `DC_I2C_SW_STATUS`, per-DDC hardware status for DDC1-DDC6 plus VGA, per-channel speed/setup registers, transaction slots `DC_I2C_TRANSACTION0` through `TRANSACTION3`, `DC_I2C_DATA`, `DC_I2C_EDID_DETECT_CTRL`, and `DC_I2C_READ_REQUEST_INTERRUPT`.
- Generic I2C controls: `GENERIC_I2C_CONTROL`, `GENERIC_I2C_INTERRUPT_CONTROL`, `GENERIC_I2C_STATUS`, `GENERIC_I2C_SPEED`, `GENERIC_I2C_SETUP`, `GENERIC_I2C_TRANSACTION`, `GENERIC_I2C_DATA`, pin selection, and pin debug fields.
- XDMA global/control fields: `XDMA_MC_PCIE_CLIENT_CONFIG`, local surface tiling, `XDMA_INTERRUPT`, clock-gating control, memory power control, BIF/PCIe interface status, performance measurement status, test/debug index/data, RBBM interface read/write timing, and power-gating sideband registers.
- XDMA master path fields: `XDMA_MSTR_CNTL`, status, memory client configuration, local/remote surface base addresses, local pitch, command and memory urgent controls, PCIe/memory NACK status, vsync/GSL checks, pipe control, read command sizing/prefetch, channel dimensions, active/frame height, remote GPU address, cache base/pitch/TLB power state, channel start, and performance measurement controls.
- XDMA slave path fields: `XDMA_SLV_CNTL`, memory client configuration, SLS pitch/width, read/write urgent controls, writeback rate, read latency min/max/average/timer registers, PCIe/memory NACK status, read-return buffer status, flip pending, channel stop/reset/active controls, and remote GPU address fields.

## Control Flow

This header has no runtime control flow. Every line is a preprocessor definition that becomes useful only when a consumer reads, modifies, or writes a hardware register.

A typical display-register access flow is:

1. Select the register address from `dce_10_0_d.h`, such as a `mmDISP_INTERRUPT_STATUS_CONTINUE*`, `mmDC_I2C_*`, or `mmXDMA_*` register.
2. Read the register through an AMDGPU MMIO helper.
3. Extract a field with `(value & REGISTER__FIELD_MASK) >> REGISTER__FIELD__SHIFT`, or clear and insert a new value with the same mask/shift pair.
4. Write the register back only if the field is writable and the surrounding display, clock, power, or DMA sequence permits it.

The interrupt continuation fields are normally used as a chain: if the high continuation bit is set in one status register, software must inspect the next status register to find additional pending sources. The macros do not implement the chain; they provide the exact bit positions for the interrupt handler or IRQ source mapping code.

The I2C/DDC and XDMA fields are more sequence-sensitive. I2C consumers program prescale/threshold/setup fields, populate transaction slots, trigger software requests, and poll or handle done/error/status bits. XDMA consumers must sequence master/slave enable, memory-ready, pipe/channel reset, surface address/pitch, urgent thresholds, cache invalidation, flip/GSL, NACK clear, and power-gating fields around display timing and memory-interface state.

## State And Persistence Behavior

The header stores no software state and has no persistence mechanism. It describes state that lives in DCE hardware registers.

State represented by this range includes pending display interrupt bits, performance-counter interrupt bits, DCO memory power status and transitions, clock/ramp configuration, reset assertion bits for DCO/DIG blocks, stereo sync routing, I2C engine ownership and transaction status, DDC line status, EDID-detect behavior, generic I2C pin routing, XDMA clock and memory power state, XDMA master/slave active/flush/flip state, programmed GPU and surface addresses, urgency thresholds, latency counters, NACK/error latches, and debug index/data selections.

Persistence depends on the underlying register. Some fields are read-only status snapshots, some are sticky interrupt/error bits that require a clear operation, some are writable configuration fields that remain programmed until reset or another driver write, and some reflect transient power-gating, clock-gating, DMA, or I2C transactions. The mask header does not encode access type, reset value, write-one-to-clear behavior, or safe ordering. Consumers must rely on the DCE hardware specification and existing AMDGPU sequencing.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register contract and its matching address definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_d.h`. The address header supplies register locations; this `*_sh_mask.h` header supplies bit layouts within those registers.

Direct include points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v10_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7_common.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/fiji_baco.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/tonga_baco.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/iceland_smumgr.c`

The interrupt status field names also integrate with AMD IRQ source metadata under `include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`, where AUX GTC sync and buffer-manager interrupt sources are associated with `DISP_INTERRUPT_STATUS_CONTINUE6`. Runtime consumers are display interrupt handling, hotplug/AUX handling, display I2C/EDID probing, clock and power-management flows, BACO/suspend-resume handling, display DMA/writeback paths, and low-level debug or register dump tooling.

Although the source tree path is under a local `ceph-client` mirror, this chunk is AMDGPU Linux kernel display-register metadata. It has no Ceph filesystem protocol logic, distributed-storage state, or filesystem persistence behavior.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong mask or shift can compile cleanly while decoding the wrong interrupt source, clearing the wrong status bit, programming the wrong I2C transaction field, or modifying neighboring XDMA control bits.

Interrupt continuation fields are particularly easy to mishandle because the status space is chained across multiple registers. Missing a continuation bit can leave pending interrupts unserviced; treating a continuation bit as a real endpoint can cause spurious handling. Field-name mismatches across CRTC, DIG, HPD, AUX, DCRX, DCCG, DCI, DCO, DCFE, WB, and buffer-manager sources can route an interrupt to the wrong handler.

I2C/DDC fields are sensitive to timing and ownership. Bad speed/setup/threshold values can break EDID reads, DisplayPort AUX-over-DDC paths, or VGA/DDC probing. Incorrect arbitration or software-request handling can wedge the I2C engine, leave transactions incomplete, or race with hardware/autonomous DDC users.

DCO clock, reset, memory-power, and power-management fields affect display block liveness. Incorrect reset or clock-ramp sequencing can leave display encoders, debug paths, or memory sub-blocks in unstable states, especially during modeset, suspend/resume, BACO entry/exit, or runtime power transitions.

XDMA fields carry high blast radius because they include memory client VMID/privilege/swap settings, 40-bit address halves, cache controls, urgent/stall thresholds, pipe/channel active/reset/flush/flip state, NACK clear bits, and latency/performance counters. Wrong field extraction can point DMA at the wrong surface, corrupt display data, mask PCIe/memory NACKs, stall a channel, or misreport performance and power-gating state.

This chunk begins in the middle of `DISP_INTERRUPT_STATUS_CONTINUE5`, so earlier fields for that register live in the previous chunk. It also closes the file, so the final merge should treat the boundary as a chunking artifact and not as a source-level reset of the macro namespace.

## Test Signals

Useful validation signals are mostly build, register-map, and hardware-behavior oriented:

- Kernel build coverage for AMDGPU configurations that include DCE 10.0 display and PowerPlay/SMU/BACO code; malformed or missing macros should produce compile failures in direct consumers.
- Static generated-header validation comparing every `*_MASK` and `*__SHIFT` pair in this range against AMD's register database and the adjacent register addresses in `dce_10_0_d.h`.
- Display IRQ tests that exercise CRTC6 vertical/timing events, HPD6, AUX6, DisplayPort fast-training/stream-disable, AUX GTC sync lock/error, performance-counter interrupts, and chained continuation handling.
- EDID and DDC/I2C tests across DDC1-DDC6 and VGA DDC, including arbitration, software transactions, read-request interrupts, timeout/error handling, and repeated hotplug or modeset cycles.
- Suspend/resume, runtime power-management, and BACO entry/exit tests that confirm DCO reset, DCO clock, memory power, and XDMA power/clock-gating states recover correctly.
- XDMA/display-DMA validation using surface address, pitch, channel dimension, urgent threshold, flip/GSL, cache invalidate, NACK/error, and latency/performance counter paths.
- Register dump or debugfs comparisons that decode raw MMIO values with these masks and verify the resulting fields match expected display hardware state.

Regression symptoms from bad constants include lost or storming display interrupts, hotplug or EDID failures, stuck I2C transactions, black screens after modeset or resume, BACO transition failures, XDMA channel stalls, incorrect remote/local surface addressing, unexpected PCIe or memory NACK behavior, and misleading display performance or power diagnostics.

## Cross-Chunk Notes

Earlier chunks of `dce_10_0_sh_mask.h` define the beginning and middle of the DCE 10.0 display register field namespace, including the first fields of `DISP_INTERRUPT_STATUS_CONTINUE5`. This chunk completes that register family, adds the DCO/I2C/XDMA tail of the file, and ends at the include guard close. The final per-file research document should describe the full header as one generated hardware register layout contract rather than as independent executable modules.
