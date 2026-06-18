# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 24959-27395

## Scope And Purpose

This chunk is part of AMDGPU's generated DCN 3.0.1 shift/mask header. It contains C preprocessor constants only: there are no functions, structs, enums, storage objects, loops, branches, or local runtime policy. The exported interface is a set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros that describe bit positions and already-positioned masks for memory-mapped display-controller registers.

The requested range starts at the tail of the `OTG2` output timing generator block, contains the full `dce_dc_optc_otg3_dispdec` block, then moves through OPTC miscellaneous registers, an OPTC performance-monitor block, DIO I2C/DDC registers, DIO miscellaneous clock/power/reset registers, HPD blocks 0 through 3, and ends after the first fields of `DC_PERFMON16_PERFCOUNTER_CNTL2`.

The file's practical purpose is to let DCN 3.0.1 display code use common register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `SF`, `SRI`, `LE_SF`, `I2C_SF`, and related register-list macros while this generated header supplies the ASIC-specific field layout. The companion `dcn_3_0_1_offset.h` supplies the matching register addresses and base indices.

Although this repository path is under `sources/distributed-fs/ceph-client`, this source is AMD display hardware metadata. It has no Ceph, filesystem, distributed-storage, or network protocol behavior.

## Register Blocks Covered

The first section completes the `OTG2` timing generator slice from `OTG2_OTG_UPDATE_LOCK` through `OTG2_OTG_SPARE_REGISTER`. It covers double-buffer update state, master enable, blank color, vertical interrupt slots, CRC controls/windows/results, static-screen detection, stereo/3D controls, global sync lock, vstartup/vupdate/vready positions, global sync status, DRR timing status and control, DTO constants, DSC start position, pipe update status, and spare state. The earlier `OTG2` timing fields live in the previous chunk.

`dce_dc_optc_otg3_dispdec` is fully represented. `OTG3` starts at `OTG3_OTG_H_TOTAL` and runs through `OTG3_OTG_SPARE_REGISTER`. It mirrors the per-timing-generator layout used by other OTG instances: horizontal and vertical timing, vtotal min/max/mid control, trigger A/B controls, forced count and flow control, stereo/interlace, live status/counters, snapshots, interrupt routing, update locks, CRC, static-screen detection, GSL, DRR, DSC, pipe update status, and spare register fields.

`dce_dc_optc_optc_misc_dispdec` covers OPTC-wide routing, clocks, and ODM memory power:

- `DWB_SOURCE_SELECT` selects OTG sources for DWB0, DWB1, and DWB2.
- `GSL_SOURCE_SELECT` selects ready sources for GSL0-2 and timing sync.
- `OPTC_CLOCK_CONTROL` exposes OPTC display-clock gating, clock-on status, and test clock selection.
- `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL2`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS` describe force/disable/status fields for ODM memories 0-11 and unassigned/vblank memory power modes.
- `OPTC_MISC_SPARE_REGISTER` exports an 8-bit spare field.

`dce_dc_optc_optc_dcperfmon_dc_perfmon_dispdec` covers performance monitor 15. It defines counter control, counted-value type, hardware stop and count-off selection, per-counter states, perfmon state/report-count control, count-off interrupt enable/status/ack/type, clock enable, run-enable start/stop selectors, comparison value high/low fields, and readback high/low registers.

`dce_dc_dio_dout_i2c_dispdec` covers the display I2C/DDC engine. It includes global I2C control and arbitration, interrupt status/ack/masks for software and DDC hardware engines, software status, DDC1-DDC4 hardware status, DDC1-DDC4 speed/setup, four queued transaction descriptors, the indexed data register, EDID detect control, and DDC read-request interrupt fields.

`dce_dc_dio_dio_misc_dispdec` covers DIO scratch registers, DIO memory power status/control, DIO clock gating/status, DIO power management, DIG soft reset controls, HDMI RX status timer, and generic interrupt message/clear fields.

`dce_dc_dio_hpd0_dispdec` through `dce_dc_dio_hpd3_dispdec` define the first four hot-plug-detect blocks. Each HPD instance has the same layout: interrupt/sense status, interrupt control/ack/polarity/enable, connection and RX interrupt debounce timers, fast-train delays/enables, and connect/disconnect toggle filter delays.

The final lines start `dce_dc_dio_dio_dcperfmon_dc_perfmon_dispdec` by defining `DC_PERFMON16_PERFCOUNTER_CNTL` and the beginning of `DC_PERFMON16_PERFCOUNTER_CNTL2`. The rest of performance monitor 16 continues in the next chunk.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The important exported surface is the macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a hardware register field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask already shifted into its register position.
- Register-heading comments such as `//OTG3_OTG_CRC_CNTL` group fields by hardware register name.
- Address-block comments such as `// addressBlock: dce_dc_dio_hpd0_dispdec` identify generated hardware blocks and replicated instances.

The most important OTG2/OTG3 macro families are timing and scanout fields (`OTG_H_TOTAL`, `OTG_H_BLANK_START_END`, `OTG_V_TOTAL`, `OTG_V_BLANK_START_END`, `OTG_STATUS_POSITION`), frame-phase update fields (`OTG_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_MASTER_UPDATE_MODE`, `OTG_MASTER_UPDATE_LOCK`), GSL fields (`OTG_GLOBAL_SYNC_STATUS`, `OTG_GSL_CONTROL`, `OTG_GSL_WINDOW_X/Y`), DRR fields (`OTG_DRR_TIMING_INT_STATUS`, `OTG_DRR_V_TOTAL_*`, `OTG_DRR_CONTROL`), vertical interrupt controls, and CRC controls/windows/results.

The important OPTC misc fields are the source selectors and ODM memory power controls. `DWB_SOURCE_SELECT` and `GSL_SOURCE_SELECT` feed display writeback and global sync lock routing. `ODM_MEM_PWR_CTRL*` and `ODM_MEM_PWR_STATUS` provide compact repeated fields for memory power force, disable, mode, and state.

The important I2C/DDC fields are `DC_I2C_GO`, soft/send/status reset bits, DDC select, transaction count, arbitration request/done bits for software and DMCU users, software completion/error status bits, DDC hardware status/read-request bits, DDC speed/setup timing fields, per-transaction read/write/start/stop/count fields, and indexed data/index-write fields.

The important HPD fields are `DC_HPD_INT_STATUS`, `DC_HPD_SENSE`, `DC_HPD_SENSE_DELAYED`, `DC_HPD_RX_INT_STATUS`, interrupt ack/polarity/enable fields, connection/RX timers, fast-train delay/enables, and toggle filter delays. These are replicated for HPD0, HPD1, HPD2, and HPD3.

## Control Flow

This header has no local control flow. Runtime control flow is created by consumers that include `dcn_3_0_1_offset.h` and this shift/mask header, then build register tables and issue MMIO register operations through AMD display helpers.

A typical use pattern is:

1. DCN 3.0.1 resource or DMUB code includes the generated offset and mask headers.
2. Register-list macros paste logical register names into offset, mask, and shift identifiers.
3. Driver modules call helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, or instance-aware variants.
4. Those helpers use these constants to isolate or pack the requested field in a 32-bit hardware register value.

For OTG and OPTC fields, the runtime sequencing lives in the timing generator, hardware sequencer, IRQ, writeback, and global-sync-lock paths. For I2C/DDC, sequencing lives in the DCE/DC I2C hardware engine: callers program transaction descriptors, load or drain the indexed data register, assert `DC_I2C_GO`, then poll or handle software/hardware completion and error bits. For HPD, IRQ and GPIO paths read sense/status fields and write ack or enable fields around hotplug events.

The chunk does not encode whether a field is read-only, write-one-to-clear, self-clearing, sticky, clock-gated, or safe only in a particular display phase. Those semantics come from the hardware specification and higher-level AMD display code.

## State And Persistence Behavior

The file itself stores no state and persists nothing. It describes hardware register state whose lifetime is controlled by display-controller hardware, the AMD display driver, DMUB/DMCU firmware, clock and power management, hotplug events, modesets, suspend/resume, and GPU reset.

OTG configuration state includes timing totals, blank/sync intervals, trigger controls, blank colors, CRC windows, vertical interrupt line positions, update-lock settings, GSL windows, DRR ranges, DTO constants, DSC start position, and static-screen settings. OTG live state includes current blank/sync/active status, counters, frame counts, snapshot readbacks, global sync and DRR event status, CRC results, pending double-buffer updates, and pipe update pending/locked indicators.

OPTC misc state includes display writeback and GSL source routing, clock gating/status, and ODM memory power force/disable/mode/state fields. Bad values can persist until corrected by a later hardware-sequencer pass, power transition, or reset.

I2C/DDC state spans command setup, ownership/arbitration, queued transaction descriptors, indexed data-buffer position and write direction, software and hardware status bits, EDID-detect state, and interrupt status/ack/mask fields. Some bits are command latches, some are live status, and some are event acknowledgements.

DIO and HPD state includes scratch registers, memory and clock power controls, DIG soft reset bits, HDMI RX timer control, generic interrupt message/clear fields, HPD debounce/filter timers, HPD sense status, and HPD interrupt enable/ack/polarity. HPD sense and delayed sense are live connector signals, while debounce timers and interrupt enables are configuration state.

Performance monitor state includes selected events, counted value type, start/stop/count-off controls, active state, comparison values, interrupt status/ack, and counter readbacks. Performance monitor values are diagnostic/runtime counters rather than persistent software data.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h`, which defines matching register addresses and base indices. Examples in this range include `mmOTG2_OTG_UPDATE_LOCK`, `mmOTG3_OTG_H_TOTAL`, `mmDWB_SOURCE_SELECT`, `mmGSL_SOURCE_SELECT`, `mmOPTC_CLOCK_CONTROL`, `mmODM_MEM_PWR_CTRL*`, `mmDC_PERFMON15_*`, `mmDC_I2C_CONTROL`, `mmDIO_MEM_PWR_STATUS`, `mmHPD0_DC_HPD_INT_STATUS`, and `mmDC_PERFMON16_PERFCOUNTER_CNTL`.

Visible include sites for the DCN 3.0.1 generated headers are `display/dc/resource/dcn301/dcn301_resource.c` and `display/dmub/src/dmub_dcn301.c`. Those files build the DCN 3.0.1 resource and DMUB register surfaces from generated offsets and masks.

The OTG and OPTC portions integrate with shared DCN timing-generator code. `display/dc/optc/dcn30/dcn30_optc.h` defines common DCN 3.0 OPTC register and shift/mask lists that include `GSL_SOURCE_SELECT`, `DWB_SOURCE_SELECT`, many `OTG_*` timing/status/CRC/DRR/GSL fields, and the pipe update status fields represented in this chunk. `display/dc/optc/dcn20/dcn20_optc.c` uses `GSL_SOURCE_SELECT` and `DWB_SOURCE_SELECT` at runtime to select GSL-ready sources and writeback sources.

The I2C/DDC fields integrate with `display/dc/dce/dce_i2c_hw.c`, `display/dc/dce/dce_i2c_hw.h`, `display/dc/gpio/ddc_regs.h`, and `display/dc/gpio/hw_ddc.c`. These paths define the register/mask structures and perform DDC transactions for EDID and link detection by programming `DC_I2C_CONTROL`, `DC_I2C_ARBITRATION`, `DC_I2C_SW_STATUS`, `DC_I2C_TRANSACTION*`, `DC_I2C_DATA`, DDC setup/speed, and EDID-detect fields.

The HPD fields integrate with display IRQ and GPIO handling. `display/dc/irq/irq_service.c` contains generic HPD sense/polarity handling around `HPD0_DC_HPD_INT_STATUS` and `HPD0_DC_HPD_INT_CONTROL`, while link encoder headers use HPD control/sense fields to enable hotplug detection and read connector state. Cross-generation link encoder code also uses `DIO_CLK_CNTL` fields for display, reference, symbol, and HDCP clock gating, matching the DIO clock families present here.

The ODM memory power mode fields integrate with DC hardware sequencer paths. For example, DCN hardware sequencer code programs `ODM_MEM_PWR_CTRL3` fields such as `ODM_MEM_UNASSIGNED_PWR_MODE` and `ODM_MEM_VBLANK_PWR_MODE` during display initialization or power policy setup.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong shift or mask can still compile, but read/modify/write helpers will touch the wrong bits, truncate field values, leave stale bits behind, or decode live status incorrectly.

Chunk boundaries matter. The range starts in the middle of the `OTG2` block after earlier timing fields and ends in the middle of the `DC_PERFMON16` block. Whole-file reconciliation must merge this slice with adjacent chunks before describing complete OTG2 or DC_PERFMON16 coverage.

OTG timing fields are phase-sensitive. Incorrect masks for update locks, double-buffer pending bits, vertical interrupt positions, GSL windows, vstartup/vupdate/vready positions, DRR trigger windows, or DSC start position can cause missed updates, stuck update locks, unstable variable refresh, broken vblank/vupdate IRQs, visible timing glitches, or CRC/readback mismatches.

Repeated instance layouts are easy to review incorrectly. OTG2 and OTG3 share many field names under different prefixes, and HPD0-HPD3 are structurally identical. A generation or copy error in one instance can affect only one display pipe or connector and escape broad smoke tests.

I2C/DDC fields mix command, ownership, status, interrupt, and indexed data access in a compact register set. Confusing `ACK`, `MASK`, `INT`, `REQ`, `DONE`, `GO`, `ABORT`, or `INDEX_WRITE` fields can hang DDC transfers, corrupt the transaction buffer, leave the engine owned by the wrong client, or make EDID/hotplug detection unreliable.

HPD fields are event-sensitive. Bad debounce/filter timers can create missed or bouncing hotplug events. Wrong polarity or ack masks can invert connector state, leave interrupts asserted, or suppress RX interrupt handling used by DisplayPort sideband and link-maintenance paths.

Clock, reset, and memory power fields have broad blast radius. Incorrect DIO/OPTC clock gating or DIG reset masks can shut off active display paths or prevent link training. Wrong ODM/DIO memory power force/disable values can create failures that appear only during vblank power transitions, multi-stream ODM use, or low-power state changes.

Performance monitor registers are diagnostic but still stateful. Incorrect counter selection, count-off, interrupt ack, or read-select fields can produce misleading performance data or unexpected perfmon interrupts.

## Test Signals

Build-time signals are direct: missing or stale macros used by DCN 3.0.1 resource, DMUB, OPTC, I2C/DDC, GPIO, IRQ, or hardware-sequencer register lists should fail compilation around `SF`, `SRI`, `REG_FIELD`, `REG_GET`, `REG_SET`, `REG_UPDATE`, `LE_SF`, `I2C_SF`, or generated `*_MASK`/`__SHIFT` identifiers.

Generated-register validation should cross-check every mask in this line range against the matching `dcn_3_0_1_offset.h` register names and against the ASIC register database. Cross-generation diffs against nearby DCN headers are useful, but expected ASIC deltas must be reviewed rather than normalized away.

Runtime display signals include successful modesets on pipes using OTG2 and OTG3, stable vblank/vupdate IRQ delivery, no stuck global/update locks, correct DRR behavior, correct DSC start placement where DSC is active, advancing frame and HV counters, and CRC capture values that match expected scanout content.

I2C/DDC and HPD tests are high value for this chunk: EDID reads over DDC1-DDC4, hotplug connect/disconnect storms, delayed HPD sense validation, DisplayPort RX interrupt handling, suspend/resume with monitors connected, and link detection on each exposed connector. Regression symptoms include missing EDID, NACK/timeout loops, stuck software I2C status, repeated HPD interrupts, or connectors that never report present.

DIO/OPTC power and clock tests should cover blanking transitions, multi-display ODM paths, display writeback routing, GSL synchronization, link training, runtime power management, and resume from low-power states. Performance monitor validation can read counters before/after selected display activity and confirm interrupt ack/status bits behave as expected.

Because this is generated register metadata rather than algorithmic code, the strongest tests combine build coverage, generated-header consistency checks, register-state dumps on DCN 3.0.1 hardware, and hardware smoke tests that exercise the affected display pipes, DDC engines, HPD blocks, and power-management states.

## Cross-Chunk Notes

This is chunk 11 of `dcn_3_0_1_sh_mask.h`. The previous chunk owns the earlier `OTG2` registers, including timing and trigger fields before `OTG2_OTG_UPDATE_LOCK`. The next chunk continues after the partial `DC_PERFMON16_PERFCOUNTER_CNTL2` definitions and should be consulted for the full DIO perfmon 16 layout and later generated blocks.
