# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 34835-37214

## Scope

This chunk is a late slice of AMDGPU's generated DCN 3.0.0 register shift/mask header. It is not executable C; it exports preprocessor constants of the form `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` for display-controller MMIO fields. These definitions are paired with register addresses from `dcn_3_0_0_offset.h` and consumed by AMD display register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WAIT`, `SF`, `SRI`, `FD_MASK`, and `FD_SHIFT`.

The range starts at the tail of the `OTG5` timing-generator register family, then covers OPTC miscellaneous source/power controls, DC perfmon instance 19, DIO I2C/DDC infrastructure, DIO clock/reset/power controls, HPD0 through HPD5 hotplug-detect blocks, DC perfmon instance 20, and most of the DP AUX0 through DP AUX2 register families. It ends at the chunk boundary inside `DP_AUX2_AUX_GTC_SYNC_CONTROLLER_STATUS`, so later lines own the remaining status fields for that register and subsequent register families.

## Purpose

The header range describes bit positions and masks for DCN 3.0 display timing, display-output, I2C/DDC, HPD, DP AUX, memory-power, and diagnostic hardware. Its purpose is to let generation-specific DCN30 code use stable logical field names while the generated register database supplies ASIC-specific field layout.

Major hardware areas covered here are:

- `OTG5_*` fields for dynamic refresh-rate timing changes, DRR trigger windows, constant DTO phase/modulo programming, DSC start position, request control, pipe update status, and spare debug storage on timing generator 5.
- `DWB_SOURCE_SELECT`, `GSL_SOURCE_SELECT`, `OPTC_CLOCK_CONTROL`, and `ODM_MEM_PWR_*` fields for writeback source selection, genlock/swaplock ready-source routing, OPTC clock gating/status, and ODM memory power force/disable/status policy.
- `DC_PERFMON19_*` and `DC_PERFMON20_*` fields for event selection, counted-value selection, run/stop control, counter state, active status, interrupt enable/ack/status, and high/low counter reads.
- `DC_I2C_*` and `DC_I2C_DDC1` through `DC_I2C_DDC6` fields for the display I2C engine, DDC line selection, arbitration between SW/HW/DMCU users, transaction programming, FIFO/data indexing, EDID detection, read-request interrupts, speed/prescale thresholds, setup timing, and per-DDC hardware status.
- `DIO_*` fields for scratch registers, DIO memory power status/control, display-output clocks, power-management overrides, DIG soft reset lines, HDMI RX status timer settings, and generic DIO interrupt message/clear registers.
- `HPD0_*` through `HPD5_*` fields for hotplug sense/status, interrupt enable/ack/polarity, HPD RX interrupt control, HPD enable, filter/connect/disconnect delays, and fast-training timing.
- `DP_AUX0_*`, `DP_AUX1_*`, and `DP_AUX2_*` fields for DisplayPort AUX channel enable/reset/HPD selection, SW and LS AUX transactions, arbitration, interrupt controls, status/error reporting, data windows, DPHY TX/RX timing, GTC sync control/error/status, and PHY wake behavior where present in the range.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or persistent software objects in this chunk. The generated macro namespace is the API surface:

- `*_SHIFT` values provide the low bit number for a register field.
- `*_MASK` values provide the already-positioned mask used for extraction and read/modify/write.
- Address-block comments group fields under hardware blocks such as `dce_dc_optc_optc_misc_dispdec`, `dce_dc_optc_optc_dcperfmon_dc_perfmon_dispdec`, `dce_dc_dio_dout_i2c_dispdec`, `dce_dc_dio_hpd*_dispdec`, `dce_dc_dio_dio_dcperfmon_dc_perfmon_dispdec`, and `dce_dc_dio_dp_aux*_dispdec`.

The `OTG5_*` macros expose the same field shape used by the DCN30 timing-generator code for OTG instances. Important fields include `OTG_DRR_V_TOTAL_CHANGE_LIMIT`, `OTG_DRR_TRIGGER_WINDOW_START_X`, `OTG_DRR_TRIGGER_WINDOW_END_X`, `OTG_DRR_AVERAGE_FRAME`, `OTG_V_TOTAL_LAST_USED_BY_DRR`, `OTG_M_CONST_DTO_PHASE`, `OTG_M_CONST_DTO_MODULO`, `OTG_DSC_START_POSITION_X`, `OTG_DSC_START_POSITION_LINE_NUM`, and pipe-update status bits for pending flips, DC register updates, cursor updates, and vupdate keepout.

The OPTC/ODM miscellaneous macros cover shared routing and power fields. `DWB_SOURCE_SELECT` routes OPTC outputs into display writeback blocks. `GSL_SOURCE_SELECT` chooses ready sources and timing-sync source for genlock/swaplock flows. `OPTC_CLOCK_CONTROL` controls/report OPTC display-clock gating. `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL2`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS` describe force/disable and status bits for ODM memory banks 0-11 plus unassigned/vblank power modes.

The `DC_PERFMON19_*` and `DC_PERFMON20_*` macros form repeated diagnostic counter instances. Each instance has `PERFCOUNTER_CNTL`, `PERFCOUNTER_CNTL2`, `PERFCOUNTER_STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW` fields. These select events, counted value types, increment modes, hardware start/stop sources, count-off behavior, active state, interrupt handling, and counter readback.

The I2C/DDC macros describe the DC I2C controller used for DDC/EDID transactions. `DC_I2C_CONTROL` carries `DC_I2C_GO`, soft reset, send reset, DDC select, transaction count, and status reset fields. `DC_I2C_ARBITRATION` covers software request/done signals, hardware request, DMCU request, queued-go policy, arbitration status, and abort flags. `DC_I2C_INTERRUPT_CONTROL`, `DC_I2C_SW_STATUS`, `DC_I2C_DDCx_HW_STATUS`, `DC_I2C_DDCx_SPEED`, `DC_I2C_DDCx_SETUP`, `DC_I2C_TRANSACTION0` through `TRANSACTION3`, `DC_I2C_DATA`, `DC_I2C_EDID_DETECT_CTRL`, and `DC_I2C_READ_REQUEST_INTERRUPT` define the transaction engine and its interrupt/status surface.

The DIO macros cover display-output infrastructure rather than a single link. `DIO_MEM_PWR_STATUS`, `DIO_MEM_PWR_CTRL`, and `DIO_MEM_PWR_CTRL2` expose I2C and HPD memory power states and force/disable controls. `DIO_CLK_CNTL`, `DIO_CLK_CNTL2`, and `DIO_CLK_CNTL3` define display, reference, SOCCLK, symbol-clock, HDCP, fast-clock, and related gating/reporting fields. `DIG_SOFT_RESET` contains reset controls for DIG frontend/backend blocks, PHY wrappers, and HDCP paths. Scratch, HDMI RX timer, generic interrupt message, and interrupt clear fields provide low-level diagnostics and glue.

The HPD macros are repeated for HPD0 through HPD5. Each block contains delayed and live sense bits, interrupt pending/ack/enable/polarity fields, HPD RX interrupt controls, HPD enable, connection state/status, fast-training enable/status/delay/count fields, and toggle-filter connect/disconnect delays.

The DP AUX macros are repeated for AUX0, AUX1, and AUX2. `AUX_CONTROL` enables/resets AUX, selects HPD, configures low-speed read/update handling, HPD-disconnect behavior, mode detection, impedance calibration, test/deglitch, and spare bits. `AUX_SW_CONTROL`, `AUX_ARB_CONTROL`, `AUX_INTERRUPT_CONTROL`, `AUX_SW_STATUS`, `AUX_LS_STATUS`, `AUX_SW_DATA`, and `AUX_LS_DATA` describe transaction start/done, command type, reply handling, byte count, arbitration, interrupt/ack/mask, and data windows. `AUX_DPHY_*` fields tune and report TX/RX physical-layer timings. `AUX_GTC_SYNC_*` fields configure and report global-time-code synchronization attempts, lock acquisition, lock loss, phase/offset error states, and timeout handling.

## Control Flow

This header has no runtime control flow. Runtime behavior appears in consumers that combine these generated fields with register addresses and MMIO helper functions.

A typical control sequence is:

1. A DCN30 display component includes `dcn_3_0_0_offset.h` and this shift/mask header.
2. Generation-specific register tables are built with `SRI(...)`, `SR(...)`, `SF(...)`, `HWS_SF(...)`, `LE_SF(...)`, or related macros.
3. Driver code calls helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, or indexed AUX/I2C helper wrappers.
4. The helper uses the generated shift and mask constants to clear, insert, poll, or extract the desired field in a read/modify/write MMIO operation.
5. Hardware performs the actual state transition: timing update, DRR adjustment, ODM memory power change, HPD interrupt acknowledgement, I2C/DDC transaction, AUX request, AUX reset, DIO clock-gate change, DIG reset, or perf counter update.

Control-sensitive flows represented by this chunk include timing-generator DRR and DSC positioning through the `OTG5_*` fields, genlock/swaplock source selection through `GSL_SOURCE_SELECT`, display writeback routing through `DWB_SOURCE_SELECT`, ODM memory low-power programming through `ODM_MEM_PWR_CTRL*`, software I2C command setup and completion through `DC_I2C_*`, EDID and link-side DDC access through DDC setup/speed/status fields, HPD connect/disconnect interrupt handling through the `HPD*_DC_HPD_*` fields, DP AUX reset/request/reply flows through `DP_AUX*_AUX_*`, and diagnostic counter operation through `DC_PERFMON19_*` and `DC_PERFMON20_*`.

The macros do not encode ordering constraints. Callers must still know when a field is read-only, write-one-to-clear, sticky, self-clearing, double-buffered, safe only while the engine is idle, safe only during blank, or owned by firmware.

## State And Persistence Behavior

The file stores no software state and performs no persistence. It describes hardware register state that persists according to DCN/MMIO semantics until rewritten, reset, power-gated, clock-gated, or changed by hardware/firmware.

State represented in this chunk includes:

- OTG/OPTC state: DRR limits/windows, last DRR vtotal, DTO phase/modulo, DSC start position, request-control policy, pending pipe update bits, writeback source routing, GSL ready/timing sync routing, and OPTC clock status.
- ODM/DIO power state: ODM memory bank force/disable/status, unassigned/vblank memory power policy, I2C/HPD memory power force/disable/status, DIO clock gating, DIG soft-reset state, and DIO power-management overrides.
- Perfmon state: selected events, counted value type, increment mode, run-enable and hardware start/stop selection, count-off policy, counter active/state fields, interrupt enable/status/ack bits, and high/low counter values.
- I2C/DDC state: arbitration ownership, queued command state, transaction descriptors, data FIFO/index window, selected DDC line, DDC speed/prescale/setup timing, EDID detect controls, read-request interrupts, software status/errors, and per-DDC hardware status.
- HPD state: live and delayed sense values, connect/disconnect filters, interrupt enable/status/ack/polarity, HPD RX interrupt controls, HPD enable, connection status, and fast-training counters/status.
- DP AUX state: AUX enable/reset/reset-done, HPD selection, low-speed read mode, SW/LS request status, arbitration state, interrupt enables/acks/masks, reply byte counts, protocol error bits, data index/data windows, DPHY timing/status, GTC sync lock/error/offset status, and PHY wake controls.

Some fields are programming latches, some are live status readbacks, some are counters, and some are sticky interrupt or error bits that require explicit acknowledgement. Suspend/resume, hotplug, modeset, DisplayPort link training, EDID reads, DSC/DRR programming, runtime power management, HPD storms, AUX timeouts, and debug/perf tooling can all alter the underlying hardware state. The generated header does not document reset defaults, access permissions, lock ordering, ownership, or volatility.

## Dependencies And Integration Points

The direct generated companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, which provides register addresses and base indexes. This file provides the bit positions inside those addresses.

Direct include and usage points visible in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c` and `dmub_dcn302.c`, which include the DCN 3.0.0 offset and mask headers for firmware-side display register access tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn30/dcn30_optc.h`, which maps `OTG*_OTG_DRR_*`, `OTG*_OTG_M_CONST_DTO*`, `OTG*_OTG_DSC_START_POSITION`, `OTG*_OTG_PIPE_UPDATE_STATUS`, `DWB_SOURCE_SELECT`, and `GSL_SOURCE_SELECT` fields into timing-generator register and shift/mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn20/dcn20_optc.c`, which uses `GSL_SOURCE_SELECT` fields to program genlock/swaplock ready sources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn30/dcn30_hwseq.c` and `display/dc/hwss/dce/dce_hwseq.h`, which use `ODM_MEM_PWR_CTRL3` fields for ODM memory power policy during hardware sequencing.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`, which builds HPD and DDC register/shift/mask tables from the HPD and DDC macros in this header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`, which includes this header while translating DCN30 GPIO offsets and masks into logical GPIO IDs for DDC, HPD, generic, and GSL pins.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c` and `irq_service_dcn302.c`, which map HPD/HPDRX interrupt enable, status, and ack fields into DC IRQ source entries.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c_hw.c` and `.h`, which consume `DC_I2C_*`, `DC_I2C_DDCx_*`, `DIO_MEM_PWR_CTRL`, and `DIO_MEM_PWR_STATUS` style fields through generation-specific tables for hardware I2C/DDC transactions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_link_encoder.c` and `.h`, plus DCN30 resource construction, which rely on `DP_AUX*_AUX_*` and `HPD*_DC_HPD_*` fields for AUX channel reset, HPD selection, link encoder setup, DPCD access, and link training support.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`, which carries generation resource caps and AUX reset-mask constants derived from this register family.

Although the repository path sits under `sources/distributed-fs/ceph-client`, this chunk is AMDGPU display hardware metadata. It has no Ceph protocol logic, filesystem cache state, network messaging, or distributed-storage persistence behavior.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A generated shift or mask can be wrong while all C code still compiles, causing a read/modify/write helper to alter the wrong bit, fail to clear a sticky bit, corrupt an adjacent field, or poll a status bit that never changes.

Timing and display-output risks are visible. Incorrect `OTG5_OTG_DRR_*`, `OTG5_OTG_DSC_START_POSITION`, `OTG5_OTG_M_CONST_DTO*`, `OTG5_OTG_PIPE_UPDATE_STATUS`, `GSL_SOURCE_SELECT`, or `DWB_SOURCE_SELECT` masks can cause bad variable-refresh behavior, DSC slice/start-position errors, wrong output timing, missed pending-update detection, broken genlock/swaplock coordination, or display writeback sourced from the wrong OPTC.

Power and clock fields are sensitive. Bad `OPTC_CLOCK_CONTROL`, `ODM_MEM_PWR_CTRL*`, `ODM_MEM_PWR_STATUS`, `DIO_MEM_PWR_CTRL*`, `DIO_MEM_PWR_STATUS`, `DIO_CLK_CNTL*`, `DIO_POWER_MANAGEMENT_CNTL`, or `DIG_SOFT_RESET` constants can leave memory banks forced on, power-gate an active I2C/HPD/ODM path, prevent light sleep, reset the wrong DIG/HDCP/PHY path, or keep display-output clocks gated while link hardware is active.

I2C/DDC fields have user-visible failure modes. Incorrect `DC_I2C_CONTROL`, `DC_I2C_ARBITRATION`, `DC_I2C_SW_STATUS`, `DC_I2C_DDCx_SPEED`, `DC_I2C_DDCx_SETUP`, `DC_I2C_TRANSACTION*`, `DC_I2C_DATA`, `DC_I2C_EDID_DETECT_CTRL`, or read-request interrupt masks can break EDID reads, fail arbitration with firmware/hardware users, hang the software I2C engine, misprogram speed/timing, corrupt data FIFO indexing, or leave the engine owned by software after a failed transaction.

HPD risks include missed or repeated hotplug events. Bad `HPD*_DC_HPD_INT_STATUS`, `HPD*_DC_HPD_INT_CONTROL`, `HPD*_DC_HPD_CONTROL`, `HPD*_DC_HPD_FAST_TRAIN_CNTL`, or `HPD*_DC_HPD_TOGGLE_FILT_CNTL` fields can invert polarity, acknowledge the wrong event, mask HPD RX IRQs, misread live sense state, shorten filter delays, or destabilize fast-training behavior.

DP AUX risks affect DisplayPort link bring-up and runtime DPCD operations. Incorrect `DP_AUX*_AUX_CONTROL`, `AUX_SW_CONTROL`, `AUX_ARB_CONTROL`, `AUX_INTERRUPT_CONTROL`, `AUX_SW_STATUS`, `AUX_LS_STATUS`, `AUX_SW_DATA`, `AUX_LS_DATA`, `AUX_DPHY_*`, or `AUX_GTC_SYNC_*` fields can prevent AUX reset completion, target the wrong HPD, lose arbitration, misreport reply length, hide timeout/overflow/protocol errors, corrupt DPCD payload bytes, mis-tune AUX PHY timing, or break GTC sync lock maintenance.

Perfmon risks are diagnostic but still important. Wrong `DC_PERFMON19_*` or `DC_PERFMON20_*` fields can select the wrong event, leave counters active, miss interrupts, acknowledge the wrong source, or return misleading counter values during display performance and power investigations.

The range contains many repeated generated patterns: DDC1-DDC6 setup/status/speed registers, HPD0-HPD5 blocks, DP_AUX0-DP_AUX2 blocks, and perfmon instances 19-20. Instance suffix mistakes are hard to catch at compile time because macro names are structurally valid and often differ only by a digit.

Chunk-boundary risk is present at both ends. The chunk begins at `OTG5_OTG_DRR_V_TOTAL_CHANGE`, after earlier OTG5 fields were defined in the previous chunk, and ends inside the `DP_AUX2_AUX_GTC_SYNC_CONTROLLER_STATUS` field list. The final merge lane should treat those as artificial chunk boundaries, not hardware block boundaries.

## Test Signals

Useful validation signals are mostly generated-header checks plus DCN30 display behavior:

- Build coverage for DCN30/DCN302 display, DMUB, timing-generator, GPIO/DDC/HPD, IRQ, DIO/link encoder, I2C, and resource files that include `dcn_3_0_0_sh_mask.h`.
- Generated-register validation that every `*_MASK` in this chunk matches its corresponding `*__SHIFT`, does not overlap unintended fields, and matches AMD's authoritative DCN 3.0.0 register database and the companion `dcn_3_0_0_offset.h`.
- Modeset, variable-refresh-rate, DSC, and multi-display tests that exercise OTG5 DRR timing, DSC start position, DTO fields, pipe update pending/status fields, GSL source selection, and DWB source routing.
- ODM/OPTC/DIO power-management tests during boot, modeset, idle, vblank, suspend/resume, and hotplug, watching for incorrect memory-power status, clock-gate state, reset state, underflow, or resume failures.
- EDID/DDC tests across DDC1-DDC6 and VGA-style paths, including repeated reads, failed reads, DDC arbitration contention, slow devices, reset recovery, and speed/prescale variations.
- HPD and HPDRX interrupt tests that connect/disconnect monitors rapidly, verify debounce/filter behavior, check delayed and live sense values, acknowledge interrupts, and ensure polarity and mask bits behave correctly.
- DisplayPort link training and DPCD/AUX transaction tests over AUX0-AUX2, including AUX reset, SW and low-speed reads, timeout/overflow/error paths, reply byte count handling, HPD disconnect during AUX, and PHY timing sensitivity.
- GTC sync diagnostics that validate AUX GTC sync enablement, lock acquisition, lock lost, timeout, phase-adjust violation, offset error, retry, and status/readback fields.
- DC perfmon diagnostics for instances 19 and 20 that program event selection and run/stop modes, read high/low counter values, and verify counter interrupts and acknowledge behavior.

Regression symptoms from bad constants include blank or unstable display, wrong DRR behavior, DSC artifacts, broken display writeback, failed EDID detection, I2C engine hangs, missed or repeated hotplug events, failed DisplayPort link training, AUX timeouts on valid sinks, stuck AUX reset, incorrect HPD sense, failure to enter display low-power states, resume failures, and impossible perf/GTC/debug readbacks.

## Cross-Chunk Notes

This is not a standalone source module; it is one chunk of a large generated DCN 3.0.0 register layout contract. Neighboring chunks own the preceding OTG5 register definitions and the continuation of `DP_AUX2_AUX_GTC_SYNC_CONTROLLER_STATUS` plus subsequent DIO/register families. The later merge/reconciliation lane should combine this with other chunks into a single per-file view and avoid treating this artificial line range as a semantic source boundary.
