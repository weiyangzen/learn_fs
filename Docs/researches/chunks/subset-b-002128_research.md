# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 24995-27614

## Purpose

This chunk is a generated shift/mask register-field slice for AMD DCN 3.6 display hardware. It contains no executable functions, structs, or persistent C objects; its API surface is a dense set of `#define` constants named as `<register>__<field>__SHIFT` and `<register>__<field>_MASK`. These constants are paired with `dcn_3_6_0_offset.h` register offsets and consumed through AMDGPU Display Core register-table macros such as `SF`, `SRI`, `FD_MASK`, `FD_SHIFT`, `REG_SET`, and `REG_UPDATE`.

The covered lines start in the middle of the ABM0 adaptive-backlight histogram/luma block, then define complete ABM1, ABM2, and ABM3 backlight/ambient/luma/histogram groups, OPP pipe 0-3 display-pattern-generator, formatter, buffer, pipe-control, and pipe-CRC groups, DSCRM DSC-forwarding controls, OPP top clock controls, DC perfmon instance 16 fields, ODM0-ODM3 OPTC input controls, and the beginning of OTG0 timing/trigger fields.

## Important APIs and register groups

- `ABM0_DC_ABM1_*` in this chunk continues ABM0 with histogram/luma scanout readback fields: luma sums, min/max and filtered min/max luma, pixel counts, min/max pixel-value thresholds, histogram sample rates, bin shift flags/indexes, 24 histogram result registers, and `BL_MASTER_LOCK`.
- `ABM1_*`, `ABM2_*`, and `ABM3_*` repeat the full adaptive backlight block for additional instances. Each instance includes PWM input/output levels (`BL1_PWM_AMBIENT_LIGHT_LEVEL`, `USER_LEVEL`, `TARGET_ABM_LEVEL`, `CURRENT_ABM_LEVEL`, `FINAL_DUTY_CYCLE`, `MINIMUM_DUTY_CYCLE`), ABM enable/auto-update controls, backlight update sampling, group-2 locking/update-pending fields, ABM core enable, IPCSC coefficient selection, ACE offset/slope and threshold tables, HGLS read progress/missed-frame status, histogram controls, luma statistics, sample-rate counters, histogram bin programming, histogram result readbacks, and master locks.
- `DPG0_*` through `DPG3_*` define output-pixel-processor display pattern generator fields for generated test patterns, including enable/mode, dynamic range, bit depth, vertical/horizontal resolution selectors, ramp offsets/increments, active dimensions, solid color channels, segment offsets, double-buffer-pending status, and DPG-side CRC result readbacks.
- `FMT0_*` through `FMT3_*` define formatter controls for output clamping, dynamic expansion, dithering, spatial/temporal dither controls, truncation, frame-random and RGB random seeds, 420 phase lock/source/pixel encoding/subsampling controls, clamp component enable/select, side-by-side stereo selection, 420 memory selection/status, and 422 left-edge extra-pixel count.
- `OPPBUF0_*` through `OPPBUF3_*` expose OPP buffer segmentation, overlap pixel count, 3D structure configuration, 3D address flags, stereo line packing, and dynamic expansion memory power controls.
- `OPP_PIPE0_OPP_PIPE_CONTROL` through `OPP_PIPE3_OPP_PIPE_CONTROL` expose the OPP pipe enable bit and clock-on status bit.
- `OPP_PIPE_CRC0_*` through `OPP_PIPE_CRC3_*` define output-pipe CRC controls and masks: enable/continuous/one-shot, stereo/interlace modes, pixel/source select, pending status, and 16-bit CRC masks.
- `DSCRM0_DSCRM_DSC_FORWARD_CONFIG` through `DSCRM3_*` select per-instance DSC forwarding via `DSCRM_DSC_FORWARD_EN` and `DSCRM_DSC_OPP_PIPE_SOURCE`.
- `OPP_TOP_CLK_CONTROL` contains top-level OPP clock gating/enable/status fields for OPP and OPPFIFO.
- `DC_PERFMON16_*` defines display performance monitor counter setup, counter selection, counter state, perfmon enable/continuous/start/reset, mode/status, interrupt thresholds and clear/mask bits, and low/high counter readbacks.
- `ODM0_OPTC_*` through `ODM3_OPTC_*` define OPTC/ODM input global controls, segment data-source selection, DSC data format and bytes-per-pixel fields, segment and slice width fields, input clock gate/enable/on bits, memory selection/status, spare register, and underflow threshold fields.
- `OTG0_OTG_*` begins the timing-generator instance 0 block: horizontal total/blank/sync and polarity, horizontal timing divider mode, vertical total/min/max/mid and dynamic refresh controls, vertical count stop controls, vtotal event interrupt status/ack/mask, nominal-vsync interrupt clear, vertical blank/sync and mode, and the first `TRIGA` trigger control fields at the chunk boundary.

## Control flow and usage model

There is no local control flow in this header. The generated constants are declarative data for higher-level register tables.

A typical consumer flow is:

1. Include `dcn_3_6_0_offset.h` and this header for DCN 3.6 offsets and field encodings.
2. Populate per-block `regs`, `shift`, and `mask` tables in DCN36 resource initialization using macros such as `ABM_MASK_SH_LIST_DCN35`, `OPP_MASK_SH_LIST_DCN35`, and `OPTC_COMMON_MASK_SH_LIST_DCN3_6`.
3. Let block implementations call typed register helpers, which combine the stored offset with the field mask and shift when programming MMIO.

The DCN36 resource path in `display/dc/resource/dcn36/dcn36_resource.c` constructs ABM, OPP, and OPTC mask/shift tables from this header. `display/dmub/src/dmub_dcn36.c` also includes the same header and uses `FD_MASK`/`FD_SHIFT` to initialize DMCUB-visible DCN35-style register metadata for DCN36. The IRQ service for DCN36 includes this header for interrupt field definitions. Shared block code under `display/dc/dce`, `display/dc/opp`, and `display/dc/optc` consumes the register tables rather than hardcoding these bit positions.

## State and persistence behavior

The header itself has no mutable state and persists only as compile-time constants. The mutable state is in display-engine MMIO registers and follows hardware lifecycle rules: display bring-up, modesets, ABM policy changes, panel brightness updates, test-pattern programming, color/output-format programming, ODM combine transitions, dynamic refresh changes, interrupt handling, suspend/resume, and GPU/display-IP reset.

Stateful hardware surfaces in this chunk include:

- ABM PWM levels and ABM enable/auto-update bits, which determine how ambient light, user brightness, target ABM brightness, and final duty cycle are combined.
- ABM HGLS read-progress, sample-rate, histogram bin, luma-statistic, and missed-frame clear fields, which represent live frame-scanning and histogram/luma collection state.
- OPP DPG fields, which can replace normal pixel output with test patterns and are double-buffered through pending status.
- FMT clamp, dither, truncation, pixel encoding, 420/422, and stereo controls, which affect visible output formatting and must match stream timing and sink format.
- OPPBUF segmentation/overlap and 3D parameters, which are part of multi-segment/ODM and stereo/3D output plumbing.
- OPP pipe CRC controls and masks, which maintain live CRC capture state and one-shot/continuous pending bits for validation and diagnostics.
- OPTC/ODM data source, segment count, DSC bytes-per-pixel, slice width, input clock, memory selection, and underflow status fields, which must track ODM combine mode and output timing.
- OTG0 timing and vtotal fields, which define scanout timing and dynamic refresh behavior; wrong values persist until reprogrammed or reset and can immediately destabilize display output.

## Dependencies and integration points

- Requires the matching `dcn_3_6_0_offset.h` register addresses. A shift/mask define is only meaningful when the same-generation offset define selects the correct MMIO register.
- Depends on AMDGPU/DC register macro infrastructure (`SF`, `SRI`, `FD_MASK`, `FD_SHIFT`, `REG_SET*`, `REG_UPDATE*`) to create typed shift/mask tables and perform read-modify-write operations.
- Integrates with `dce_abm` and `dmub_abm_lcd` for adaptive backlight and luma/histogram programming.
- Integrates with DCN36 resource construction through `dcn36_resource.c`, where ABM, OPP, and OPTC register tables are initialized for four hardware instances.
- Integrates with OPP code (`dcn20_opp` and later OPP variants) for display pattern generation, blanking/test pattern setup, formatter controls, OPP buffer programming, and OPP CRC diagnostics.
- Integrates with OPTC/timing-generator code (`dcn32_optc`-style helpers used by DCN36) for OTG timing, ODM segment routing, DSC slice geometry, input clock control, underflow handling, and dynamic refresh/vtotal programming.
- Integrates with DC performance monitoring/debug paths through the `DC_PERFMON16_*` fields and with display validation paths that read pipe CRCs or underflow status.

## Risks and edge cases

- Generated-pair drift is the main correctness risk: masks from this file must match offsets from `dcn_3_6_0_offset.h`. Mixing generations can compile while writing the wrong hardware field.
- Instance confusion is easy because ABM1-3, DPG/FMT/OPPBUF/OPP_PIPE/CRC0-3, DSCRM0-3, and ODM0-3 are highly repetitive. A wrong instance index can produce pipe-specific brightness, format, CRC, underflow, or timing failures.
- Many fields are adjacent packed bitfields. Whole-register writes can clobber status, clear, reserved, or pending bits; consumers should use field-aware read-modify-write helpers unless hardware requires a direct write.
- Status/control naming is mixed in the same register families. Fields such as `*_STATUS`, `*_CURRENT`, `*_PENDING`, `*_INT_STATUS`, and `*_ACK` are not ordinary configuration fields and may clear or latch hardware state when written.
- ABM programming has ordering hazards around HGLS register locks, group update-at-frame-start controls, master locks, sample-rate reset bits, and missed-frame clear bits. Reprogramming during active scanout can create stale statistics or visible brightness jumps.
- Formatter and OPP buffer fields can create visible artifacts if pixel encoding, 420/422, truncation, dithering, segment width, or overlap fields do not match stream timing and link encoding.
- Pipe CRC one-shot/continuous controls and masks must be synchronized with frame boundaries; otherwise diagnostics may capture stale frames or partial updates.
- ODM and OTG fields are timing-critical. Segment count/source, DSC slice width, bytes-per-pixel, memory selection, vtotal min/max/mid, and trigger fields can break scanout, underflow, or dynamic refresh if programmed outside the timing-generator update sequence.
- This chunk begins mid-register group for ABM0 and ends mid-register group at `OTG0_OTG_TRIGA_CNTL`; final per-file reconciliation must include adjacent chunks before drawing complete conclusions about those two groups.

## Test signals

- Build with DCN36 enabled and verify `dcn36_resource.c`, `dmub_dcn36.c`, and `irq_service_dcn36.c` compile against this header and the matching offset header.
- Static consistency checks should compare repeated ABM, OPP, DSCRM, and ODM instances for expected identical field layout, while allowing instance-specific register offsets.
- ABM tests should cover panel brightness changes, ambient/user/target/current/final duty-cycle programming, histogram/luma readback, sample-rate reset behavior, missed-frame clear behavior, and suspend/resume brightness restoration.
- OPP formatter tests should exercise RGB/YCbCr, 420/422 modes, dithering/truncation, clamp controls, stereo/3D modes, and output-depth transitions.
- Display pattern generator tests should program solid color and ramp patterns on pipes 0-3, check double-buffer pending behavior, and validate blanking/test-pattern output.
- CRC diagnostics should run one-shot and continuous OPP pipe CRC capture on each pipe and confirm mask/source/stereo/interlace settings produce stable expected results.
- ODM/OPTC tests should cover bypass, 2:1/4:1 ODM combine where supported, DSC slice-width/bytes-per-pixel programming, input-clock enable/gating, memory selection, and underflow status/clear behavior.
- OTG timing tests should cover modeset timing, dynamic refresh/vtotal min/max/mid transitions, vtotal interrupt status/ack/mask, vsync-nominal interrupt clear, and trigger source/polarity/delay programming.
