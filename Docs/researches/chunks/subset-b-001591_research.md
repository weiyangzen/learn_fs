# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 25076-27514

## Scope

This chunk covers lines 25076-27514 of the generated-style AMD DCN 1.0 register shift/mask header. It contains only C preprocessor constants: no functions, structs, enums, inline helpers, or executable control flow. The chunk starts inside the `OTG4_OTG_STEREO_CONTROL` macro family and ends after `DIO_CLK_CNTL` masks, just before `DIO_POWER_MANAGEMENT_CNTL`.

The slice contains 2439 source lines and 2157 `#define` lines. Its exported surface is a set of globally visible `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros used with companion DCN 1.0 register offset headers and AMDGPU display MMIO/indexed-register helpers.

## Purpose

The macros describe bit positions and already-positioned masks for several DCN 1.0 display controller blocks:

- Tail of OPTC/OTG instance 4: stereo control, snapshot capture, timing interrupts, double-buffer/update control, test patterns, blank/black colors, CRC windows and signatures, static-screen detection, 3D structure control, global sync lock, vertical update windows, dynamic refresh-rate control, manual triggers, request control, and spare register fields.
- Full OPTC/OTG instance 5: horizontal and vertical timing totals, blanking/sync positions, trigger A/B controls, force-count and force-vsync controls, flow control, AV sync counter, blanking and pipe abort controls, interlace and field state, pixel readback, current position/frame counters, stereo state/control, snapshot controls, interrupt controls, update locks, test patterns, colors, CRC, static-screen, global sync, vertical update keepout, global control, DRR, request, and spare fields.
- OPTC misc and performance monitor blocks: DWB/GSL source selection, OPTC clock-control/spare fields, and `DC_PERFMON18` perf counter/perfmon selection, state, interrupt, and counter-value fields.
- DIO DAC block: DAC enable/source selection, DAC CRC configuration and readback, sync tristate/stereosync selection, autodetect control/status/interrupt fields, forced output/data fields, powerdown/control/comparator fields, DFT config, and FIFO status.
- DIO I2C and generic I2C blocks: display DDC engine control, arbitration, interrupt, software/hardware status, per-DDC speed/setup, transaction descriptors, data FIFO/index fields, EDID detect, read-request interrupt, generic I2C control/status/speed/setup/transaction/data/pin-selection.
- DIO misc block: scratch registers, VCE audio stream select, DIO memory power status/control for I2C/DP/HDMI/AFMT memories, and DIO clock gating controls for DIO, DVO, DACA, reference clock, and DIGA-DIGG.

## Important Macro Families

All field constants follow the generated naming convention:

- `REGISTER__FIELD__SHIFT` gives the bit offset.
- `REGISTER__FIELD_MASK` gives the field mask in final register position.
- Fields whose hardware names end in `MASK` generate names like `OTG5_OTG_CRC_SIG_RED_GREEN_MASK__OTG_CRC_SIG_RED_MASK__SHIFT` and `..._MASK_MASK`; this double `MASK` form is intentional generated output, not a typo.

The `OTG4_*` portion continues an instance already opened before this range. It focuses on late timing-generator controls: snapshots, interrupt masks/types, update locks, double-buffer update-pending bits, test-pattern generation, blank and black color programming, vertical interrupts, CRC control/windows/data/signature masks, static-screen detection, 3D stereo structure, global sync lock, vertical startup/update/ready timing, global control, manual trigger/flow control, range timing interrupt status, dynamic refresh rate, and request controls.

`OTG5_*` mirrors the OPTC/OTG timing-generator layout for the next instance. It includes the primary modeset timing fields (`H_TOTAL`, `H_BLANK_START/END`, `H_SYNC_A`, `V_TOTAL`, `V_TOTAL_MIN/MAX/MID`, `V_BLANK`, `V_SYNC_A`), runtime status fields (`OTG_STATUS`, position counters, frame counters, HV count, nominal vertical position), trigger and force-count controls, update/double-buffering controls, color/test-pattern/CRC diagnostics, stereo and interlace state, global sync controls, vertical update keepout, DRR control, and request generation.

The OPTC misc/perfmon section exposes source muxes for DWB and GSL, clock gating for the OPTC block, a spare register, and a full `DC_PERFMON18` counter set. The perfmon macros select events and counted-value inputs, control increment mode and restart/count-off behavior, report active state and interrupt latches, select stop conditions, and read low/high counter values.

The DAC macros describe the legacy analog-output path. They cover enable and source selection, RGB/control CRC masking and readback, sync tristate and stereosync, load/autodetect control with threshold and sense fields, autodetect interrupt enable/status/ack/type, forced blank/sync/data outputs, powerdown controls, comparator enable/output, DAC power controls, DFT bits, and FIFO overflow/underflow flags.

The I2C macros define both the DC DDC hardware engines and a generic I2C controller. They include soft reset, go/send-reset, transaction count, DDC selection, arbitration, interrupt enable/status/ack/type, software status, DDC1-DDC6 and VGA hardware status, per-channel reference-divider/threshold/prescale/setup limits, transaction direction/start/stop/stop-on-NACK/count fields, data read/write and index fields, EDID-detect configuration, read-request interrupts, and generic SCL/SDA pin selection.

The DIO misc macros expose software scratch space, VCE audio stream select, memory power state/control for I2C, DP links A-G, HDMI instances 0-6, AFMT instances 0-5, and clock gate disable bits for display, reference, DVO, DAC, and DIG links.

## APIs, Types, and Functions

There are no callable APIs, C types, or functions in this chunk. The macros form a low-level ABI-like contract between generated ASIC register data and hand-written AMDGPU display code.

The header is included by DCN 1.0 resource setup, DCN 1.0 IRQ service, DCN 1.0 GPIO factory/translation code, and DCN 2.0 GPIO translation code. Fields in this chunk are also consumed indirectly through shared DCE helper structures and macros, especially I2C and DAC helpers such as `dce_i2c_hw` and `dce_link_encoder`. Callers pair these mask/shift constants with address macros from `dcn_1_0_offset.h` and access them through register helpers such as `REG_UPDATE`, `REG_GET`, and related AMD display macros.

## Control Flow

The header has no runtime control flow. Hardware programming flow is implied by the register fields:

1. Select the target block and instance, such as `OTG4`, `OTG5`, `DC_PERFMON18`, DAC, DC I2C, generic I2C, or DIO misc.
2. Read the matching MMIO register using the companion offset macro and display register-access helper.
3. Clear or preserve fields with `*_MASK`, position new values with `*__SHIFT`, and write the composed register value back.
4. For timing generator programming, hold update locks or use double-buffer controls, program totals/blanking/sync/update windows, then allow the update to latch at the intended vertical boundary.
5. For interrupts and latched status, read status bits and write the corresponding `*_CLEAR`, `*_ACK`, or `*_AK` fields according to hardware semantics.
6. For I2C, program speed/setup and transaction descriptors/data, assert `GO`, then poll status and interrupt bits for completion, NACK, timeout, or arbitration events.
7. For perfmon/CRC/autodetect diagnostics, configure selection and masks, enable measurement, then read status or counter/signature fields.

The sequencing-sensitive areas are OTG update locks and pending bits, vertical total/DRR programming, global sync lock and manual trigger controls, write-one-to-clear interrupt/status fields, I2C transaction ordering, DAC autodetect setup/status clearing, memory power force/disable bits, and clock gate disable bits.

## State and Persistence

The header stores no software state and has no persistence of its own. Its constants describe hardware register state that persists until reset, power-management transitions, display mode changes, firmware/hardware action, or explicit driver writes.

Important state domains in this chunk include:

- OTG4/OTG5 timing state: totals, blanking, sync positions, counters, frame count, interlace/stereo state, vertical update windows, global sync status, update pending/lock bits, DRR state, snapshot captures, CRC signatures, static-screen detection, and test-pattern/blank/black color values.
- Interrupt state: OTG snapshot, force-count, force-vsync, trigger, vsync, GSL gap, vertical interrupt, range timing, DAC autodetect, DC I2C, generic I2C, and read-request interrupt status/ack/mask/type fields.
- Diagnostic state: CRC windows and accumulated RGB/blue signatures, pixel readback, perfmon active/report/counter values, DAC comparator/autodetect status, FIFO overflow/underflow flags, I2C status and data indexes.
- Power and clock state: DIO memory power states and force/disable controls for I2C, DP, HDMI, and AFMT subblocks, plus DIO/DVO/DAC/reference/DIG clock gate disables.
- Scratch and integration state: full-width DIO scratch registers and VCE audio stream selection.

Because these are hardware-facing constants, callers must preserve reserved bits and use the correct access path and width. Full-width fields such as scratch registers and CRC/perfmon counter pieces can be safely represented as 32-bit values, while packed state fields require masking before interpretation.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor, but it is meaningful only with the rest of the DCN 1.0 generated register headers and AMD display register helper infrastructure.

Primary integration points are:

- `display/dc/resource/dcn10/dcn10_resource.c`, which includes the header for DCN 1.0 resource and register table setup.
- `display/dc/irq/dcn10/irq_service_dcn10.c`, which uses DCN 1.0 mask/shift data for interrupt source programming and acknowledgement.
- `display/dc/gpio/dcn10/hw_factory_dcn10.c`, `display/dc/gpio/dcn10/hw_translate_dcn10.c`, and `display/dc/gpio/dcn20/hw_translate_dcn20.c`, which include the header for GPIO/DDC mapping and translation.
- Shared DCE display helpers for timing generators, I2C/DDC, link encoders, DAC/autodetect, performance monitoring, CRC, and power/clock controls.
- Hardware programming paths for modeset timing, vblank/vsync IRQs, DisplayPort global sync, dynamic refresh rate, diagnostics, EDID/DDC transactions, analog output handling, and DIO memory/clock power management.

The repeated `OTG4` and `OTG5` layouts are especially important for instance-indexed timing-generator code. Repeated DDC speed/setup/status fields and DIG/DP/HDMI/AFMT power fields are similar integration signals: driver tables should select the intended instance instead of synthesizing names manually.

## Risks

The main risk is silent hardware misprogramming. Incorrect shifts or masks compile normally but can write the wrong bit, corrupt adjacent fields, fail to acknowledge interrupts, or leave reserved bits changed. Failures would likely appear as modeset instability, missing vblank/vsync events, incorrect DRR timing, broken global sync, invalid CRC/test-pattern diagnostics, I2C/DDC timeouts, bad EDID reads, DAC detect failures, audio-stream selection errors, or power-management glitches.

Boundary risk exists for this chunk. It starts after the beginning of `OTG4_OTG_STEREO_CONTROL` and ends before `DIO_POWER_MANAGEMENT_CNTL`, so the final per-file reconciliation should merge adjacent chunk notes before treating the OTG4 stereo-control and DIO power-management areas as complete.

The OTG update and timing fields are timing-sensitive. Programming totals, blanking, vertical total min/max/mid, update locks, or `OTG_UPDATE_INSTANTLY` at the wrong time can create visible glitches or transient invalid modes. DRR and global sync fields are similarly sensitive because they affect frame pacing and multi-pipe synchronization.

Status/ack/clear fields require the hardware access semantics, not just the bit layout. Blind read/modify/write can acknowledge or clear latched status unexpectedly, especially for vertical interrupts, range timing interrupts, DAC autodetect, and I2C completion/error bits.

The generated `*_MASK_MASK` names are easy to misread. They represent fields whose hardware names include `MASK`; renaming or normalizing them would break consistency with generated code and existing call sites.

DIO power and clock gating bits can affect multiple display links. Incorrect force/disable settings may make DDC, DP, HDMI, AFMT, DAC, or DIG blocks appear intermittently unavailable, particularly across suspend/resume and hotplug paths.

## Test Signals

Useful validation signals for this chunk are mostly static plus hardware integration tests:

- Build coverage for DCN 1.0 display resource, IRQ, GPIO, timing, I2C, and link-encoder code that includes or indirectly consumes `dcn_1_0_sh_mask.h`.
- Generated-header consistency checks that every `REGISTER__FIELD__SHIFT` has an aligned mask, repeated OTG instances preserve equivalent field layouts, and duplicate macro names do not collide.
- Diff or regeneration checks against the authoritative DCN 1.0 ASIC register database.
- Modeset tests across pipes using OTG4/OTG5, including timing totals, blank/sync positions, frame counters, interlace/stereo, update-lock behavior, vblank/vsync interrupts, global sync, and DRR.
- CRC/test-pattern/static-screen diagnostic tests that program windows and masks, then verify nonzero and stable signature readback.
- IRQ tests for snapshot, force-count, force-vsync, trigger, vertical interrupt, range timing, DAC autodetect, and I2C status/ack/mask/type fields.
- DDC/EDID tests on all DDC channels and generic I2C pins, covering speed/setup programming, transaction sequencing, NACK/timeout/arbitration handling, and data FIFO indexes.
- DAC/autodetect tests for load detection, forced output, comparator state, powerdown controls, and FIFO status where analog-output hardware is present.
- Suspend/resume and runtime power tests that verify DIO memory power state/control and DIO clock gate fields return to expected values and do not break hotplug, EDID, DP/HDMI, AFMT, or DAC behavior.

## Cross-Chunk Notes

This is one interior slice of a large generated header. The final per-file document should reconcile this with the previous chunk for the beginning of `OTG4_OTG_STEREO_CONTROL` and with the following chunk for `DIO_POWER_MANAGEMENT_CNTL` and the remaining DIO/PHY/audio/display-output register definitions.
