# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 27515-29881

## Scope

This chunk covers lines 27515-29881 of AMD's generated DCN 1.0 register shift/mask header. It contains 2367 source lines, 2176 `#define` lines, and 165 register/address-block comments. There are no C functions, structs, enums, or inline helpers; the exported surface is a large set of preprocessor constants that give bit shifts and already-positioned masks for DCN display I/O registers.

The range starts in the tail of the `DIO_CLK_CNTL` macro family and ends in the middle of `DP_AUX5_AUX_GTC_SYNC_CONTROLLER_STATUS`. It covers DIO clock/reset/power interrupt controls, HPD0-HPD5 hot-plug blocks, `DC_PERFMON19`, and DP AUX channel blocks AUX0 through most of AUX5.

## Purpose

The macros describe DCN 1.0 display I/O register fields so AMDGPU display code can build read/modify/write values without open-coded bit positions. Each generated field follows the convention:

- `REGISTER__FIELD__SHIFT` gives the field's bit offset.
- `REGISTER__FIELD_MASK` gives the field mask in final register position.
- If the hardware field is itself named `*_MASK`, the generated name becomes `REGISTER__FIELD_MASK__SHIFT` and `REGISTER__FIELD_MASK_MASK`; these double-`MASK` names are intentional generated output.

The first section covers DIO-level controls: display/ref clock gate-disable bits, power-management reset/busy status, stereo sync selection, DIO and DIG soft resets, AFMT memory-power status, AFMT/TMDS clock gate controls, HDMI RX-status timer configuration, PSP and generic DIO interrupt status/message/clear fields.

The HPD sections repeat the same layout for `HPD0` through `HPD5`. They expose hot-plug status, current and delayed sense, RX interrupt status, connect/disconnect toggle filter timer values, interrupt ack/polarity/enable fields, RX interrupt ack/enable fields, connection and RX interrupt timer programming, HPD enable, fast-train delay/enable controls, and connect/disconnect debounce/filter delay fields.

`DC_PERFMON19` exposes one display performance-monitor instance. Its fields cover event selection, counted-value selection, increment mode, hardware control selection, run-enable mode, count-off/start/restart controls, interrupt enable/status/ack, active state, counter selection, counted-value type, hardware stop selectors, count-off selector, packed per-counter states for counters 0-7, report count, clock enable, run-enable start/stop selectors, high/low counter values, and per-counter interrupt status/ack bits.

The DP AUX sections define repeated register layouts for `DP_AUX0` through `DP_AUX5`. Each instance includes AUX enable/reset/reset-done, link-status read controls, HPD selection, HPD-disconnect ignore, mode detection, impedance calibration request, test/deglitch/spare bits, software transaction control, arbitration between software and DMCU users, interrupt status/ack/mask fields for software/LS/GTC events, software and link-service status/error fields, data/index access windows, TX/RX DPHY timing/status, and GTC sync error/controller/status fields. The requested slice stops before the full AUX5 GTC sync controller/status layout is present.

## Important APIs, Types, and Functions

This chunk has no callable APIs, data types, or executable functions. Its important API is the macro namespace itself. Consumers combine these masks and shifts with companion register offsets from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h` and AMD display register helpers.

Relevant consumer patterns in this tree include:

- `display/dc/gpio/dcn10/hw_factory_dcn10.c` and `display/dc/gpio/dcn10/hw_translate_dcn10.c`, which include `dcn_1_0_sh_mask.h` for DCN10 GPIO/HPD register translation.
- `display/dc/irq/dcn10/irq_service_dcn10.c`, which includes the DCN 1.0 mask header for IRQ source metadata.
- `display/dc/irq/irq_service.c`, where HPD ack code reads `HPD0_DC_HPD_INT_STATUS.DC_HPD_SENSE_DELAYED` and flips `HPD0_DC_HPD_INT_CONTROL.DC_HPD_INT_POLARITY` after generic acknowledgement.
- `display/dc/dce/dce_aux.h`, where `DCN10_AUX_MASK_SH_LIST` maps fields such as `DP_AUX0_AUX_CONTROL.AUX_EN`, `AUX_RESET`, `AUX_RESET_DONE`, arbitration fields, `AUX_SW_GO`, `AUX_SW_DATA`, `AUX_SW_REPLY_BYTE_COUNT`, `AUX_SW_DONE`, and `AUX_SW_DONE_ACK` into the generic AUX engine field table.
- `display/dc/dio/dcn10/dcn10_link_encoder.h`, where link-encoder field lists use `DP_AUX0_AUX_CONTROL.AUX_HPD_SEL`, `AUX_LS_READ_EN`, `DP_AUX0_AUX_DPHY_RX_CONTROL0.AUX_RX_RECEIVE_WINDOW`, and `HPD0_DC_HPD_CONTROL.DC_HPD_EN`.

Although the chunk defines all six AUX and HPD instances, several generic field-list macros are written against instance 0 and rely on per-instance register-offset arrays or generated macros elsewhere to select the actual hardware instance.

## Control Flow

The header itself has no runtime control flow. Runtime flow is implied by the register fields:

1. Select the correct DCN 1.0 offset/register instance, such as HPD0 versus HPD5 or AUX0 versus AUX5.
2. Read a register with AMD display MMIO helpers such as `dm_read_reg()` or generation-specific register wrappers.
3. Extract fields with the generated mask and shift, or clear and set fields before writing a modified value back.
4. For HPD events, read sense/status, acknowledge latched interrupt bits, and adjust polarity so the next edge is detected.
5. For AUX transactions, arbitrate register access, program request bytes in `AUX_SW_DATA`, start the transaction with `AUX_SW_GO`, poll or interrupt on `AUX_SW_DONE`, read reply byte count/data, and inspect timeout/overflow/HPD-disconnect/protocol-error fields.
6. For perfmon, enable the monitor clock, choose event/counter controls, start or stop counting, handle threshold/interrupt status, and read low/high counter values.

Sequencing is external to this header. The macros do not say which bits are read-only, write-one-to-clear, self-clearing, sticky, reserved, or safe only while the block is disabled.

## State and Persistence

The file stores no software state and persists nothing at runtime. Its constants describe hardware-backed state in the DCN 1.0 display I/O block.

State represented by this chunk includes:

- DIO clock gating, test clock selection, reset assertion, soft-reset controls, AFMT memory-power state, HDMI RX-status timer status, and DIO-to-PSP/generic interrupt messages.
- HPD sense, delayed sense, RX interrupt status, hot-plug interrupt polarity/enables/acks, debounce/toggle filter timers, fast-train trigger timing, and per-pin enable state for six HPD pins.
- Perfmon19 event selection, counter modes, active/running state, report count, interrupt latches, selected counter state, and 48-bit-style value readback split across low/high fields.
- AUX channel enable/reset state, software/DMCU arbitration state, software and link-service request/done/error state, AUX data FIFOs/index windows, DPHY timing and active/RX/TX state, GTC sync error counters, and GTC sync lock/error controller state.

These hardware states can persist until driver writes, hardware self-clears, interrupt acknowledgement, link retraining, hotplug state transitions, DMCU/firmware activity, display power gating, suspend/resume, or ASIC reset changes them.

## Dependencies and Integration Points

The direct dependency is only the C preprocessor, but the constants are meaningful only with the matching DCN 1.0 offset header and DC display register-access framework. The practical integration points are:

- DCN10 GPIO factory/translation and IRQ-service construction.
- Common HPD interrupt acknowledgement and hotplug polarity handling.
- Generic DCE/DCN AUX engine code that uses per-generation field lists for DP AUX transactions and DPCD access.
- DCN10 link encoder construction and setup paths that select AUX/HPD routing and link-service behavior.
- Display performance-monitor debug, diagnostics, or telemetry paths that can program `DC_PERFMON19`.
- Low-level power-management and hardware-sequencing code that may gate DIO clocks, reset DIO/DIG blocks, or inspect memory-power status.

The same register-family names appear in nearby DCE/DCN generations. Callers must include the mask/shift header that matches the ASIC generation and its offset header; identical field names do not guarantee identical addresses or complete field availability across generations.

## Risks

Incorrect masks or shifts compile cleanly but can silently program the wrong hardware bits. In this chunk, likely symptoms include missed or repeated hotplug interrupts, wrong HPD polarity after acknowledgement, AUX transaction timeouts, corrupted AUX reply parsing, broken DPCD/EDID reads, DisplayPort link-training failures, disabled AUX/HPD routing, inaccurate perf counters, or stuck DIO/DIG reset/clock gating.

Status and acknowledgement fields are especially sensitive. `*_ACK`, `*_CLEAR`, status, and mask fields often live in the same register. A careless read/modify/write can acknowledge an event unintentionally or preserve a stale mask bit. The generated names do not encode write-one-to-clear versus read-only semantics.

Repeated HPD/AUX instances create copy or generation risks. HPD0-HPD5 and AUX0-AUX5 should have parallel layouts, but a one-bit drift affects only one connector path and may appear as board- or port-specific failure. Conversely, assuming all instances exist on every ASIC or board can touch unimplemented registers.

The AUX arbitration fields expose shared access between software and DMCU. Programming AUX without respecting `AUX_SW_USE_AUX_REG_REQ`, pending status, and done-using-register fields can conflict with firmware or queued link-service operations.

Boundary risk exists for this research chunk. It starts after the beginning of `DIO_CLK_CNTL` and ends before the complete `DP_AUX5_AUX_GTC_SYNC_CONTROLLER_STATUS` and following `DP_AUX5_AUX_GTC_SYNC_STATUS` definitions. The final per-file report should merge adjacent chunks before treating those register families as complete.

## Test Signals

Useful validation signals are mostly static and hardware-integration oriented:

- Kernel build coverage for DCN10 display code that includes `dcn_1_0_sh_mask.h`, especially GPIO, IRQ, AUX, and link-encoder paths.
- Generated-header consistency checks that every `REGISTER__FIELD__SHIFT` has a matching mask, masks align with their shifts, and repeated HPD/AUX instances have identical field layouts where expected.
- Regeneration or diff checks against the authoritative AMD DCN 1.0 register database.
- Hotplug tests on all physical connector paths, including connect/disconnect debounce, delayed sense, RX IRQ, polarity flipping after ack, suspend/resume, and fast-train timing.
- AUX/DPCD/EDID tests across all available AUX channels, covering normal replies, reply byte counts, timeout, overflow, HPD disconnect during transaction, malformed AUX response status bits, and DMCU/software arbitration.
- Link-training smoke tests for DisplayPort connectors, since AUX, HPD routing, DPHY timing, and fast-train fields are prerequisites for stable training.
- Perfmon tests that program `DC_PERFMON19`, start and stop counters, read low/high values, and exercise counter interrupt status/ack fields.
- Power-management tests that enter/exit display power states and verify DIO clock gate, soft reset, AFMT memory-power status, and AUX/HPD state recover correctly.

## Cross-Chunk Notes

This is one interior slice of a 54345-line generated header. Earlier chunks should describe the start of the DIO clock-control register family before line 27515. Later chunks should complete `DP_AUX5_AUX_GTC_SYNC_CONTROLLER_STATUS`, add `DP_AUX5_AUX_GTC_SYNC_STATUS`, and continue the remaining DCN 1.0 register mask definitions. The final per-file document should treat this header as generated hardware metadata, not algorithmic driver code.
