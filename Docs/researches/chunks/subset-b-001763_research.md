# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 29916-32314

## Scope And Purpose

This chunk is a generated AMD DCN 3.0.2 register shift/mask table. It exports C preprocessor constants that describe hardware register field bit positions (`__SHIFT`) and field masks (`_MASK`) for memory-mapped display-controller registers. The matching address definitions live in `dcn_3_0_2_offset.h`; this file supplies the bit layout metadata consumed by the AMDGPU Display Core register helper layer.

The requested range contains 2,169 `#define` entries: 1,085 shift constants and 1,084 mask constants. The one-entry imbalance is caused by the chunk ending inside `DP_AUX1_AUX_DPHY_TX_REF_CONTROL`: it includes the `AUX_TX_REF_SEL`, `AUX_TX_RATE`, and `AUX_TX_REF_DIV` shifts and the first two masks, while the remaining mask for that register continues after line 32314.

There are no C functions, structs, enums, or runtime branches in this slice. Its API surface is the generated macro namespace used by symbol-pasting register list macros such as `SF`, `HWS_SF`, `SRI`, `REG_READ`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

## Register Blocks Covered

The chunk starts in the middle of the `dce_dc_optc_otg4_dispdec` address block and completes the later `OTG4` timing-generator fields. Covered OTG4 registers include count reset, manual and automatic force-vsync controls, stereo status/control, snapshot capture, interrupt control, update locks, double-buffer pending status, master enable, blank colors, vertical interrupts 0 through 2, CRC control/data/windowing, static-screen detection, 3D structure control, global-sync-lock (GSL) timing, master update windows, global update controls, dynamic refresh rate (DRR) status/control, M/N DTO constants, request mode, DSC start position, pipe update status, and a spare register.

The `dce_dc_optc_optc_misc_dispdec` block then defines mux, clock, and ODM memory-power fields: `DWB_SOURCE_SELECT`, `GSL_SOURCE_SELECT`, `OPTC_CLOCK_CONTROL`, `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL2`, `ODM_MEM_PWR_CTRL3`, `ODM_MEM_PWR_STATUS`, and `OPTC_MISC_SPARE_REGISTER`.

The `dce_dc_optc_optc_dcperfmon_dc_perfmon_dispdec` block covers `DC_PERFMON17`, including performance-counter event selection, counter state, monitor enable/state, counter off interrupt state, and low/high counter-value readback fields.

The `dce_dc_dio_dout_i2c_dispdec` block covers the display I2C/DDC engine. It includes `DC_I2C_CONTROL`, arbitration, interrupt control, software status, DDC1 through DDC5 hardware status/speed/setup, transaction descriptors 0 through 3, indexed data access, EDID detect control, and DDC read-request interrupt fields. DDC6/VGA-related fields are present in adjacent generated ranges, not this exact slice.

The DIO common block covers scratch registers, DIO memory power status/control, display and symbol clock gating, display interface power management, DIG front-end/back-end soft reset bits for DIGA through DIGG, HDMI RX status timer, generic interrupt message/clear registers, and `DC_PERFMON18`.

The HPD blocks cover `HPD0` through `HPD4`. Each instance includes hot-plug interrupt status, interrupt control, HPD enable/timers, fast-training delays/enables, and connect/disconnect toggle filter timing.

The final portion covers the complete `DP_AUX0` AUX controller field set and the beginning of `DP_AUX1`. `DP_AUX0` includes AUX enable/reset, HPD selection, software transaction control, arbitration, interrupts, software and link-service status/data windows, DPHY TX/RX timing/status, GTC sync controls/status/error fields, and PHY wake control. `DP_AUX1` is covered through control, software control, arbitration, interrupts, software/link-service status/data, and the beginning of DPHY TX reference control.

## Important APIs, Types, And Macros

The primary API contract is the generated name shape:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for that field.
- Comment markers such as `//OTG4_OTG_INTERRUPT_CONTROL` and `// addressBlock: dce_dc_dio_dp_aux0_dispdec` are generator structure only; they are not compiled C symbols.

Important macro families in this chunk are:

- `OTG4_OTG_*` for the fifth output timing generator instance's status, events, CRC, update-lock, GSL, DRR, and DSC-position fields.
- `DWB_SOURCE_SELECT`, `GSL_SOURCE_SELECT`, `OPTC_CLOCK_CONTROL`, and `ODM_MEM_PWR_*` for OPTC misc and ODM memory-power integration.
- `DC_PERFMON17_*` and `DC_PERFMON18_*` for OPTC/DIO performance monitor programming and readback.
- `DC_I2C_*` for DDC/I2C command, arbitration, per-DDC timing, transaction, data, EDID-detect, and interrupt fields.
- `DIO_*` and `DIG_SOFT_RESET` for DIO clock, memory-power, scratch, reset, and generic interrupt controls.
- `HPD0_*` through `HPD4_*` for connector hot-plug-detect sense, debounce, interrupt, and fast-train behavior.
- `DP_AUX0_AUX_*` and `DP_AUX1_AUX_*` for DisplayPort AUX/I2C-over-AUX transaction engines.

The concrete DCN 3.0.2 integration point is `display/dc/resource/dcn302/dcn302_resource.c`, which includes `dcn_3_0_2_offset.h` and this header. That resource file builds DIO, I2C, AUX, HPD, and link-encoder register tables and initializes shift/mask structs from these generated constants. For example, it uses `DIO_REG_LIST_DCN10()`, `I2C_HW_ENGINE_COMMON_REG_LIST(id)`, `I2C_COMMON_MASK_SH_LIST_DCN2(__SHIFT/_MASK)`, `DCN2_AUX_REG_LIST(id)`, and `HPD_REG_LIST(id)` to bind generic display-core code to the DCN 3.0.2 register map.

## Functional Field Groups

OTG4 timing and event fields describe a live scanout timing generator. Snapshot fields capture vertical/horizontal/frame counters. Vertical interrupt fields define line positions, polarity, enable/status/clear bits, and interrupt type. Global sync status fields expose VSTARTUP, VUPDATE, VUPDATE no-lock, VREADY, stereo select, and field-number events. Pipe update status fields report flip, DC register update, cursor update, and vupdate keepout state.

OTG4 update-lock and double-buffer fields coordinate when timing-sensitive changes latch. `OTG_UPDATE_LOCK`, `OTG_MASTER_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_GLOBAL_CONTROL*`, and `OTG_VUPDATE_KEEPOUT` provide the hardware side of frame-aligned update sequencing. Incorrect masks here can cause updates to latch too early, never latch, or race vblank/vupdate.

OTG4 CRC fields support validation and diagnostics. `OTG_CRC_CNTL`, `OTG_CRC_CNTL2`, CRC window controls, `OTG_CRC*_DATA_*`, and CRC signal masks configure capture source, capture windows, component masks, and readback values. These are important for display CRC selftests and diagnosing scanout corruption.

Static screen, stereo, 3D, and DRR fields describe specialized display modes. Static-screen controls enable CPU static-screen interrupts and override state. Stereo and 3D fields expose eye/field selection and 3D structure frame count. DRR fields expose vtotal reach/update interrupts, trigger windows, and last vtotal used by dynamic refresh.

I2C/DDC fields define the software and hardware transaction engine used for EDID and display sideband operations. The runtime sequence is to obtain I2C register ownership through `DC_I2C_ARBITRATION`, program DDC speed/setup and transaction registers, use `DC_I2C_DATA` as an indexed buffer, assert `DC_I2C_GO`, then poll or acknowledge `DC_I2C_SW_STATUS` and interrupt bits. Error status includes timeout, abort, buffer overflow, stopped-on-NACK, and per-transaction NACK bits.

HPD fields provide the connector-presence and HPD RX interrupt interface. The status registers report immediate and delayed HPD sense, RX interrupt state, and filter timer values. Control registers acknowledge interrupts, select polarity, enable HPD/RX interrupts, and program connection/RX timers. Toggle filter fields debounce connect/disconnect events.

DP AUX fields define the DisplayPort AUX controller and its PHY timing. Control fields enable/reset AUX, bind the AUX engine to an HPD source, ignore HPD disconnect for special cases, enable mode detection, request impedance calibration, and deglitch AUX input. Arbitration fields coordinate software and DMCU ownership. SW/LS status fields report done/request, timeout, overflow, HPD disconnect, malformed start/stop/sync/reply states, reply byte count, CP IRQ, and low-speed update status. Data registers are indexed byte windows. DPHY fields configure TX reference/rate/divider, precharge, RX windows, timeout, detection threshold, and expose TX/RX state. GTC sync fields configure and report global time-code sync over AUX.

Perfmon fields are diagnostic/profiling surfaces. `DC_PERFMON17` corresponds to the OPTC side and `DC_PERFMON18` to the DIO side in this generated range. Each exposes event selection, counter control, counter state, monitor state, counter-off interrupt control/status/ack, and low/high value readback.

## Control Flow And State Behavior

This header has no direct control flow. Runtime behavior is produced when display resource initialization binds offset macros and these shift/mask macros into register tables. Later, hardware modules call helper macros that use those tables to pack or extract fields in MMIO register values.

The state described by this chunk is hardware-resident and persists until changed by the driver, firmware/DMCU, hardware event logic, reset, or power management. Some fields are configuration state, such as HPD filter delays, DDC timing, AUX PHY timing, OTG blank color, CRC windows, DRR trigger windows, and clock-gating controls. Other fields are live status or event state, such as interrupt occurred/status bits, reset-done bits, clock-on/busy bits, pending-update bits, AUX/I2C reply/error bits, perf counter values, HPD sense, and memory-power status.

Several registers are stateful command/status interfaces. `DC_I2C_DATA` and `DP_AUX*_AUX_*_DATA` are indexed byte windows, so access order and index/autoincrement behavior matter. I2C and AUX ownership bits must be requested and released in order or transactions can be denied, race firmware, or leave a sideband engine busy. Interrupt ack/clear fields generally require writing the correct bit, not merely reading status.

Frame-synchronized OTG fields are especially ordering-sensitive. Update locks, double-buffer pending bits, VUPDATE/VREADY/VSTARTUP events, keepout windows, and GSL fields are used around atomic modeset and page-flip sequencing. A wrong shift or mask can manifest as missed vblank/vline events, stuck page flips, tearing, incorrect VRR timing, or only one pipe failing because this chunk is specific to `OTG4`.

## Dependencies And Integration Points

This header depends on the matching `dcn_3_0_2_offset.h` register address header. A field macro without a matching address macro, or an address mapped to the wrong field layout, can compile while silently programming the wrong bits.

`display/dc/resource/dcn302/dcn302_resource.c` is the main DCN 3.0.2 resource integration site. It includes this generated header, constructs DIO registers from `DIO_REG_LIST_DCN10()`, creates I2C engine tables for DDC instances 1 through 5, creates AUX tables for AUX instances 0 through 4, and creates HPD tables for HPD instances 0 through 4. The line-range content therefore feeds DIO construction, DDC/I2C hardware engines, DisplayPort AUX engines, HPD handling, and link encoder setup.

I2C/DDC fields integrate with `display/dc/dce/dce_i2c_hw.h` and `display/dc/dce/dce_i2c_hw.c`. Those paths define `struct dce_i2c_shift`, `struct dce_i2c_mask`, transaction action enums, arbitration/status enums, and the common I2C field lists. They use fields such as `DC_I2C_GO`, `DC_I2C_DDC_SELECT`, `DC_I2C_TRANSACTION_COUNT`, `DC_I2C_SW_USE_I2C_REG_REQ`, `DC_I2C_SW_DONE_USING_I2C_REG`, `DC_I2C_SW_STATUS`, `DC_I2C_DDC1_*`, transaction slot fields, and `DC_I2C_DATA`.

AUX fields integrate with `display/dc/dce/dce_aux.h`, `display/dc/dce/dce_aux.c`, and DCN link-encoder register definitions under `display/dc/dio/dcn10/` and `display/dc/dio/dcn20/`. `DCN2_AUX_REG_LIST(id)` maps per-instance `DP_AUX<n>` register addresses, while AUX mask lists consume the `DP_AUX0_AUX_*` field layout as the canonical per-instance field shape.

HPD fields integrate with GPIO and IRQ code, including `display/dc/gpio/hpd_regs.h`, hardware factory files under `display/dc/gpio/dcn*`, and generic IRQ handling in `display/dc/irq/irq_service.c`. The generated HPD fields back hotplug sense reads, polarity management, debouncing, RX interrupt enable/ack, and connector plug/unplug IRQ service.

OTG4 interrupt fields align with DCN IRQ source definitions under `include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`, where OTG4 vupdate, snapshot, force-count, force-vsync-next-line, trigger, GSL, vertical interrupt, DRR/range timing, static-screen, VSTARTUP, VREADY, and VSYNC-nominal events have source/context IDs. The higher-level timing-generator and hardware-sequencer code access these fields through generic OTG register tables assembled elsewhere in the same generated header family.

## Risks And Edge Cases

The chunk begins and ends mid-generated block. Earlier OTG4 timing fields appear before line 29916, and the `DP_AUX1_AUX_DPHY_TX_REF_CONTROL` mask list continues after line 32314. The final per-file report must reconcile those boundaries rather than treating this chunk as a complete standalone hardware description.

Repeated-instance families are copy-sensitive. HPD0 through HPD4 are structurally similar, and DP_AUX0/DP_AUX1 share nearly identical layouts. A one-instance generator error can affect only a specific connector or board routing, making regressions look monitor- or port-specific.

Ownership and arbitration fields are concurrency-sensitive. I2C and AUX engines can be requested by software and DMCU/firmware paths; wrong masks around `DC_I2C_ARBITRATION` or `DP_AUX*_AUX_ARB_CONTROL` can cause denied transactions, indefinite busy state, or races between driver and firmware.

Interrupt ack/mask/type fields use dense adjacent bits. A shifted mask in I2C, AUX, HPD, OTG, or perfmon interrupt control can either fail to clear an interrupt or mask the wrong source, leading to lost hotplug events, interrupt storms, missed DDC completion, or stuck AUX transactions.

Clock, reset, and memory-power fields affect block availability. Bad constants in `DIO_CLK_CNTL*`, `DIG_SOFT_RESET`, `DIO_MEM_PWR_*`, `OPTC_CLOCK_CONTROL`, or `ODM_MEM_PWR_*` can leave display blocks gated, reset, or unable to wake reliably.

Indexed data registers are prone to ordering bugs. `DC_I2C_DATA`, `DP_AUX0_AUX_SW_DATA`, `DP_AUX0_AUX_LS_DATA`, and the corresponding AUX1 data registers depend on index and autoincrement semantics; wrong field definitions can corrupt byte order or read/write the wrong FIFO slot.

## Test Signals

Useful validation signals include:

- Generated-header consistency checks that every visible field has the expected shift/mask pair, that masks are contiguous where the hardware spec expects contiguous fields, and that fields in repeated HPD/AUX instances match their intended siblings.
- Compile coverage of `dcn302_resource.c` with this header and `dcn_3_0_2_offset.h`, proving that resource tables, shift structs, and mask structs still resolve.
- Modeset and atomic page-flip tests that exercise OTG4, including vblank/vline delivery, VUPDATE/VREADY/VSTARTUP events, update-lock release, double-buffer pending completion, and cursor/flip pending status.
- Display CRC tests that use OTG CRC windows and readback fields to detect scanout mismatches.
- VRR/DRR tests on an OTG4-backed pipe, checking vtotal reach/update interrupts and trigger-window behavior.
- Hotplug tests across HPD0 through HPD4, including connect/disconnect debounce, delayed sense, RX interrupt ack/enable, and polarity handling.
- EDID/DDC reads across DDC1 through DDC5, including timeout/NACK/abort paths and DDC read-request interrupt acknowledgement.
- DisplayPort AUX transaction tests on AUX0 and AUX1, including successful native AUX/I2C-over-AUX reads and writes, HPD disconnect handling, timeout/error status decoding, reply byte count, and CP IRQ/low-speed update status where applicable.
- Power-management tests that suspend/resume or light-sleep DIO/I2C/AUX/DIG blocks while verifying that memory-power status, clock-on/busy, reset-done, and sideband transaction paths recover correctly.
