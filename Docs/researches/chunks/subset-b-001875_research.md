# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 25142-27729

## Purpose

This chunk is generated AMD DCN 3.1.5 register field metadata. It contains no executable C logic; it exposes preprocessor constants that describe bit positions and masks for fields in DCN display MMIO registers. Runtime code combines these `__SHIFT` and `_MASK` constants with the matching DCN 3.1.5 register-offset header to build field tables and read/modify/write hardware registers.

The requested range covers 2,588 source lines and 2,109 `#define` entries: 1,054 `__SHIFT` constants and 1,055 `_MASK` constants across 384 register names. The count is intentionally unbalanced because the artificial chunk boundaries cut through register definitions. The range starts inside `ABM1_DC_ABM1_HGLS_REG_READ_PROGRESS`, after some earlier shift definitions, and ends inside the `OTG0_OTG_CRC_CNTL` shift list before the remaining shifts and masks.

Although this file is under a local `ceph-client` source mirror, the content is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or exported runtime symbols in this range. The public surface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the hardware field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK`: the hardware field mask within the register.

These macros are meaningful only with the matching register offsets from `dcn_3_1_5_offset.h` and AMD display register helpers such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

Major register families in this chunk:

- Tail of `ABM1_*`: histogram/readback, local statistics, ambient/backlight management sample-rate controls, histogram bins/results, missed-frame/read-progress bits, and BL master lock.
- Full repeated `ABM2_*` and `ABM3_*` blocks: PWM ambient/user/target/current/final/minimum duty-cycle fields, ABM PWM control/sample-rate/lock fields, ACE offset/slope and threshold fields, IPCSC coefficient selection, HGLS read progress, HG/LS statistics, histogram bin/result windows, and BL master lock.
- `DPG0` through `DPG3`: display pattern generator enable/mode/dynamic range/bit depth/resolution fields, ramp control, dimensions, color channels, segment offsets, and double-buffer pending status.
- `FMT0` through `FMT3`: formatter clamp ranges, dynamic expansion, pixel encoding/subsampling, truncation, spatial/temporal dithering, random seeds, clamp format, side-by-side stereo width, 4:2:0 memory power controls, and 4:2:2 edge handling.
- `OPPBUF0` through `OPPBUF3` and `OPP_PIPE0` through `OPP_PIPE3`: OPP buffer active width, segmentation, overlap, pixel repetition, 3D parameters, padded-pixel count, pipe clock enable/on status, and digital bypass.
- `OPP_PIPE_CRC0` through `OPP_PIPE_CRC3`: CRC enable/continuous/stereo/interlace/pixel-source controls, CRC masks, and CRC result registers.
- `DSCRM0` through `DSCRM2`: DSC remapper forwarding configuration for slice-width and buffer-memory format.
- OPP top-level and perfmon registers: clock-gating/test-clock fields, ABM BLPWM routing, performance counter event/control/state/interrupt/ack/value fields.
- `ODM0` through `ODM3`: OPTC input soft reset, underflow interrupt/status/clear fields, segment source selection, DSC data format and bytes-per-pixel, segment/slice width, input clock control, memory selection, and spare register fields.
- Beginning of `OTG0`: horizontal/vertical timing totals, blanks, syncs, dynamic refresh-rate total control/status, trigger A/B controls, force-count controls, flow control, stereo/interlace, pixel readback, timing status/counts, forced vsync, snapshot, update lock, double-buffer pending bits, master enable, vertical interrupt 0-2 controls, and the first five CRC control shifts.

## Control Flow

This header has no runtime control flow. The practical control flow is supplied by DCN315 display code that includes this generated mask header:

1. DCN315-specific files include both `dcn/dcn_3_1_5_offset.h` and `dcn/dcn_3_1_5_sh_mask.h`.
2. Token-pasting helper macros resolve register/field names into offset, mask, and shift constants. For example, `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)` expand against generated names such as `OTG0_OTG_STATUS__OTG_V_BLANK_MASK`.
3. Higher-level display code performs the actual sequencing: programming ABM/PWM, configuring formatter and OPP state, enabling clocks, selecting ODM input segments, setting OTG timings, arming vertical interrupts, reading CRCs, and polling or clearing pending/status bits.

The masks do not encode access ordering, read-only/write-only semantics, sticky status behavior, or write-one-to-clear semantics. Consumers must follow hardware programming sequences from the display driver and ASIC specification.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on disk or in memory. It describes hardware register fields whose values live in the display engine.

Hardware state represented here includes:

- ABM/backlight state: ambient/user/target/current/final/minimum PWM levels, automatic ABM update/calculation controls, PWM update sample-rate counters, grouped register locks, ACE thresholds/slopes, HG/LS histogram and luma statistics, readback-in-progress flags, missed-frame flags, clear bits, and master locks.
- OPP/formatter state: pattern generator settings, clamp ranges, pixel encoding, chroma subsampling, bit-depth truncation and dithering controls, random seeds, 4:2:0 memory power state, OPP buffer segmentation and 3D parameters, OPP pipe clock/bypass state, and per-pipe CRC results.
- DSC/ODM state: DSC forwarding and remapping configuration, OPTC segment routing, DSC data format and bytes-per-pixel, segment/slice widths, input memory selection/status, input clock enable/on status, underflow occurrence/current/status bits, and double-buffer pending state.
- OTG0 state: timing totals and sync positions, dynamic vertical-total update status, trigger arm/delay/select state, force-count-now and flow-control state, stereo/interlace state, live pixel/timing counters, snapshot positions, update locks, timing double-buffer pending bits, master enable, vertical interrupt positions/status/clear bits, and the beginning of CRC configuration.
- Perfmon state: selected events, counter state, run-enable/stop selections, interrupt status/ack bits, and high/low counter values.

Persistence is hardware-defined. Configuration fields generally remain until a modeset, power-gating transition, suspend/resume restore, or ASIC reset changes them. Status, pending, interrupt, ack, clear, trigger, and missed-frame fields may be volatile, sticky, self-clearing, or write-one-to-clear depending on the register. This generated header only names the bit layout.

## Dependencies And Integration Points

Primary dependency:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`, which provides the companion register offsets and base-index information.

Observed include/integration sites in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c` includes the DCN 3.1.5 offset and mask headers and builds `dmub_srv_dcn315_regs` using `DMUB_DCN315_FIELDS()`, `FD_MASK`, and `FD_SHIFT`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c` includes the generated headers for DCN315 interrupt source descriptors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c` and `hw_translate_dcn315.c` include the same generated headers for GPIO register translation/factory setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes the DCN 3.1.5 headers while constructing DCN315 display resources, including DIO and stream encoder resources.

Broader integration is with AMDGPU display programming paths for backlight/ABM, output pixel processing, formatter programming, ODM/OPTC routing, OTG timing, display interrupts, CRC diagnostics, and performance monitoring. Repeated instance prefixes (`ABM2`, `ABM3`, `FMT0`-`FMT3`, `OPPBUF0`-`OPPBUF3`, `ODM0`-`ODM3`, `OTG0`) must stay aligned with the matching offset header and register tables.

## Risks And Edge Cases

- Shift/mask drift is the main risk. These are untyped integer constants, so a wrong bit position can compile cleanly while corrupting adjacent hardware fields at runtime.
- This chunk starts and ends mid-register. Final file-level reconciliation must merge the previous chunk's `ABM1_DC_ABM1_HGLS_REG_READ_PROGRESS` opening definitions and the following chunk's remaining `OTG0_OTG_CRC_CNTL` definitions before making complete-register claims.
- ABM and PWM fields include lock bits, pending bits, missed-frame flags, clear bits, sample-rate counters, and automatic update controls. Incorrect read/modify/write handling can leave brightness updates stale, lose missed-frame diagnostics, or program backlight levels on the wrong frame.
- Formatter and OPP fields are replicated for four pipes. A copy-generation error in only one instance may appear as a one-display or one-plane artifact, especially with 4:2:0/4:2:2 formats, dithering, stereo, segmentation, or CRC validation.
- Memory power fields such as formatter map420 memory controls must be coordinated with active use; forcing low-power state during active scanout can produce stale data or visible corruption.
- ODM/OPTC fields govern DSC data format, segment routing, slice width, input clocks, and underflow signaling. Wrong values can produce underflow interrupts, blank output, bad DSC slicing, or failures limited to multi-segment/ODM modes.
- OTG timing fields are highly order-sensitive. Misprogrammed totals, blanking, sync, dynamic refresh-rate limits, double-buffer update timing, or master enable state can cause lost vblank, unstable refresh, frame timing glitches, or hangs during modeset.
- Vertical interrupt fields combine enable, status, clear, type, and line-position controls. Incorrect ack/clear behavior can create stuck interrupts or missed vblank-style notifications.
- Perfmon fields include run gating and interrupt/ack controls. They are useful for diagnostics but can perturb measurement or produce stale counts if counter state and ack fields are not sequenced correctly.

## Test Signals

Useful validation for this chunk combines generated-header consistency checks with hardware-level display tests:

- Build DCN315 AMDGPU display code. Missing or renamed macros should fail at include sites such as DMUB register table construction, IRQ descriptors, GPIO translation, resource construction, and any direct register helper use.
- Mechanically verify that complete registers in lines 25142-27729 have paired `__SHIFT` and `_MASK` definitions. Expected exceptions are the opening `ABM1_DC_ABM1_HGLS_REG_READ_PROGRESS` partial register and the closing `OTG0_OTG_CRC_CNTL` partial register.
- Diff this slice against AMD's authoritative DCN 3.1.5 generated register database and neighboring DCN generation headers where repeated block layouts should remain compatible.
- Exercise backlight and ABM paths: brightness changes, ambient/user/target levels, automatic current-level updates, sample-rate changes, frame-start updates, suspend/resume, and panel power transitions.
- Validate formatter and OPP behavior across RGB/YCbCr, 4:2:0, 4:2:2, bit-depth truncation/dithering, stereo, segmented output, and CRC capture modes; watch for pipe-specific artifacts.
- Test ODM/DSC scenarios, including single-segment and multi-segment modes, DSC on/off, slice-width changes, clock gating transitions, and underflow interrupt reporting/clearing.
- Exercise OTG0 timing paths: modesets, vblank and vertical interrupt handling, dynamic refresh-rate changes, interlace/stereo modes, forced vsync, snapshot capture, update locks, double-buffer pending polling, and CRC enable/one-shot modes.
- Monitor kernel logs and display diagnostics for underflow, stuck pending bits, missed-frame flags, stale CRCs, lost vertical interrupts, timing update timeouts, brightness anomalies, or failures isolated to one repeated OPP/ODM/ABM instance.

## Cross-Chunk Notes

The previous chunk owns the start of `ABM1_DC_ABM1_HGLS_REG_READ_PROGRESS`, including the earlier in-progress and missed-frame shift fields. This chunk contains the clear shifts and masks plus the remaining ABM1 HG/LS statistics and histogram results. The next chunk continues `OTG0_OTG_CRC_CNTL` after line 27729 with additional CRC shifts and the mask definitions, then likely continues the rest of the OTG0/OPTC timing metadata. The final per-file report should reconcile these boundaries before summarizing complete address blocks for `dcn_3_1_5_sh_mask.h`.
