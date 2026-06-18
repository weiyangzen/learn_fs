# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h

Chunk: `subset-b-001877`
Covered source range: lines 30208-32632 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h`

## Purpose

This chunk is a generated AMD DCN 3.1.5 register-field mask header section. It contains C preprocessor constants for register bit positions and bit masks; it is not executable code and does not define functions, structs, storage, or runtime algorithms.

The requested range covers 2,425 source lines and 2,165 `#define` entries: 1,088 `__SHIFT` macros and 1,089 `_MASK` macros. It starts at the tail of the `OTG3_OTG_CRC_SIG_BLUE_CONTROL_MASK` register-family block, then covers the remainder of the `OTG3` timing-generator field surface, OPTC misc/memory-power fields, `DC_PERFMON17`, HPD0 through HPD4 hotplug-detect blocks, a complete DP0 transmitter field group, a complete DIG0 digital encoder/HDMI/TMDS field group, and the beginning of the DP1 transmitter field group through `DP1_DP_SEC_CNTL1`.

The chunk boundary matters. The first two macros in this range complete a register whose comment and first fields are in the previous chunk. The range ends in the middle of DP1 secondary-data-packet support: later `DP1_DP_SEC_FRAMING*`, DP1 audio, MSE/MST/MSO/DSC/ALPM/GSP, and subsequent display-output blocks are outside this work item.

## Important APIs, Types, And Macros

There are no callable APIs or data types here. The public interface is the generated macro contract used by AMD display register helpers:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask.
- The matching address/base-index constants live in `dcn_3_1_5_offset.h`; this file supplies only field layout.

Important macro families in this range include:

- `OTG3_OTG_*`: static-screen interrupt/status fields, 3D/stereo structure fields, GSL vsync-gap and GSL window controls, master update mode/lock/keepout fields, OTG clock/reset/busy fields, vstartup/vupdate/vready event fields, global sync interrupt/status/clear fields, manual trigger/flow controls, dynamic refresh-rate timing interrupts, vertical-total reach/change/trigger-window fields, constant-M DTO fields, DSC start position, pipe update status, and spare register bits.
- `DWB_SOURCE_SELECT`, `GSL_SOURCE_SELECT`, `OPTC_CLOCK_CONTROL`, `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS`: shared OPTC-side source-selection, clock, and output-data-merger memory-power controls.
- `DC_PERFMON17_*`: performance counter/event selection, run/active/interrupt controls, count-value configuration, state readback, and high/low counter registers for the DC perfmon17 block.
- `HPD0_DC_HPD_*` through `HPD4_DC_HPD_*`: hotplug interrupt status, delayed sense, HPD RX interrupt status/control, interrupt ack/mask/polarity/timer fields, HPD enable/connection timer, fast-training delay/select/enables, and connect/disconnect toggle-filter timers.
- `DP0_DP_*`: complete DisplayPort main-link field definitions for link status, pixel format, MSA colorimetry/misc/timing, DP configuration and lane count, video stream enable/deferred-disable/status, FIFO steering, video M/N timing, link framing, HBR2 eye/test patterns, VBID, video disable interrupts, DPHY training/symbol/scrambler/PRBS/CRC/FEC controls, fast training, secondary-data packet controls, audio N/M and timestamp fields, MSE stream-allocation-table programming/status, MSA timing parameters, MSO, DSC, metadata transmission, ALPM, GSP8-GSP11, and GSP enable double-buffer status.
- `DIG0_*`: digital encoder frontend/backend control, output CRC, clock/test/random pattern generation, FIFO status/recalibration/error fields, HDMI metadata and core control/status, HDMI audio/ACR/VBI/infoframe/generic packet controls, generic-control packets, HDMI double-buffering, AFMT audio clock control, TMDS controls, stereo sync, sync character patterns, DC balancing, DIG version, and force-disable.
- `DP1_DP_*`: the beginning of the second DisplayPort main-link instance with the same generated shape as DP0, but only through `DP1_DP_SEC_CNTL1` in this chunk.

## Control Flow

This header has no internal control flow. All behavior occurs in code that includes the generated masks and shifts and passes them to register access helpers.

The runtime pattern is:

1. DCN315 display code includes `dcn_3_1_5_offset.h` and `dcn_3_1_5_sh_mask.h`.
2. Register-list macros choose addresses from the offset header.
3. Mask/shift-list macros choose field definitions from this header.
4. Block constructors store those addresses, masks, and shifts in per-block register tables.
5. Runtime display code uses helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, field extractors, and polling helpers to perform MMIO read/modify/write operations.

Concrete consumers in this tree include `display/dc/resource/dcn315/dcn315_resource.c`, `display/dc/irq/dcn315/irq_service_dcn315.c`, `display/dc/gpio/dcn315/hw_factory_dcn315.c`, `display/dc/gpio/dcn315/hw_translate_dcn315.c`, and `display/dmub/src/dmub_dcn315.c`. `dcn315_resource.c` builds DCN315 resource tables and uses generated field-list expansion for hardware sequencer and DIO-related fields. `irq_service_dcn315.c` builds HPD, HPD RX, pflip, GPIO, and underflow IRQ source tables. The generic IRQ code reads HPD sense/status fields and writes HPD interrupt polarity/ack fields using these generated definitions. DMUB support includes the same ASIC-specific mask namespace for firmware-facing register definitions.

## State And Persistence Behavior

The header itself is stateless. It performs no I/O, allocates no memory, and persists only as constants compiled into display-driver objects.

The hardware fields described here are persistent register state in the DCN display hardware until changed by driver writes, firmware writes, block reset, display power gating, ASIC reset, suspend/resume restore, or link/modeset reprogramming. Important state categories include:

- OTG3 timing and update state: static-screen status/interrupts, 3D/stereo counters, global sync event latches, vstartup/vupdate/vready interrupt state, master update lock, GSL status, DRR/VRR vertical-total programming, constant-M DTO phase/module values, DSC start coordinates, and pipe update status.
- Shared OPTC/ODM state: DWB/GSL source routing, OPTC clock enable/reset/busy status, ODM memory power control requests, and memory power status.
- Perfmon17 state: selected performance events, run/active mode, interrupt/latch behavior, counter state, and high/low counter readbacks.
- HPD state: current and delayed hotplug sense, HPD and HPD RX interrupt latches, ack/mask/polarity fields, debounce/toggle filter timers, and fast-training delay controls.
- DP0/DP1 link state: link training/status, pixel/MSA attributes, stream enable/deferred-disable, DPHY training and test-pattern state, scrambler/FEC/PRBS/CRC state, fast-training state, MST/MSE scheduling, MSO/DSC controls, ALPM controls, and secondary-packet/audio/metadata/GSP state.
- DIG0 HDMI/TMDS state: encoder enable/routing, output CRC/test pattern state, FIFO status, HDMI packet scheduling, audio/ACR timing, infoframe/generic-packet double buffering, deep-color/scrambling controls, AFMT audio source, and TMDS balancing/control-character state.

Several fields are status or write-one-clear/ack style rather than plain configuration. Examples include HPD interrupt acks, DP video stream-disable ack/status, DPHY CRC result-valid/status, fast-training complete ack, HDMI error ack/status, generic-packet pending/deadline status, MSE SAT update/status, and OTG global-sync/static-screen event clear fields. The generated macros do not encode access type or ordering; the calling driver sequences must do that correctly.

## Dependencies And Integration Points

Direct dependencies are small:

- the C preprocessor;
- the matching generated address header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`;
- AMD display register helper conventions such as `SF`, `SR`, `SRI`, `SRII`, `HWS_SF`, `REG_SET`, `REG_UPDATE`, `REG_GET`, `get_reg_field_value`, and `set_reg_field_value`.

Functional integration is broader:

- OPTC and hardware sequencer paths depend on the `OTG3`, OPTC clock, GSL, DWB, ODM memory-power, and pipe-update fields for modeset timing, atomic-update synchronization, dynamic refresh-rate behavior, pipe status, and power management.
- IRQ service and GPIO/HPD translation paths depend on the `HPD0` through `HPD4` fields for connector hotplug, HPD RX, polarity inversion after ack, and debounce/filter behavior.
- DP link and stream encoder paths depend on the `DP0` and `DP1` fields for DisplayPort SST/MST link training, MSA/VBID programming, stream enable/disable, link compliance patterns, FEC/scrambler/CRC, DSC/MSO, secondary packets, audio timing, ALPM, and generic packet double buffering.
- DIG/HDMI/TMDS paths depend on `DIG0` fields for HDMI mode setup, packet scheduling, ACR/audio clocking, deep color, scrambling, TMDS control symbols, test patterns, output CRC, and force-disable behavior.
- DMUB code includes this mask header alongside offset definitions so DCN315 firmware-service register structures can share the same ASIC-specific field layout.

Instance prefixes are part of the ABI between generated headers and register-list macros. `OTG3`, `HPD0`-`HPD4`, `DP0`, `DIG0`, and `DP1` must remain aligned with the matching offset-header instances and the resource pool's declared hardware counts.

## Risks And Edge Cases

The primary risk is silent register-field drift. A wrong shift or mask can still compile and can make register helpers modify the wrong bits. High-impact examples in this chunk include OTG3 update locks and DRR timing, HPD interrupt ack/polarity, DP stream enable and DPHY training fields, DSC/MSO controls, HDMI packet controls, and ODM memory-power fields.

Chunk boundaries split logical blocks. The first lines complete `OTG3_OTG_CRC_SIG_BLUE_CONTROL_MASK` from the previous chunk, and the DP1 block continues after this chunk. Merge/reconciliation must avoid treating this slice as complete coverage for the OTG3 CRC-signal mask register or for DP1.

Repeated instance families are easy to miswire. HPD0-HPD4, DP0/DP1, and DIG0 share similar field names with different prefixes. A token-paste or table-index mistake can send hotplug handling, link training, packet programming, or HDMI controls to the wrong connector or encoder.

Status/ack/clear fields require access-type discipline. Treating latches, acks, reset-done bits, event-clear bits, or readback fields as ordinary configuration can drop HPD events, fail to clear interrupts, race fast-training completion, or misreport CRC/FIFO/MSE state.

DisplayPort and HDMI behavior is mode-sensitive. Some fields are only exercised with MST, DSC, MSO, FEC, high bit rates, deep color, audio, generic secondary packets, panel replay/ALPM, or compliance patterns, so field-layout errors may escape basic single-monitor modeset tests.

Generated macro consumers rely on exact names. Renaming or removing a field can break compile-time table initialization; worse, a same-shaped field with a different instance prefix can compile if selected accidentally by a macro expansion pattern.

## Test Signals

Useful validation signals are mostly build-time and hardware-facing:

- Build DCN315 display code with `dcn315_resource.c`, `irq_service_dcn315.c`, GPIO HPD translation/factory code, DMUB DCN315 support, stream/link encoder code, and OPTC/HWSEQ paths enabled. Missing or renamed macros should fail at compile time.
- Compare `dcn_3_1_5_sh_mask.h` against `dcn_3_1_5_offset.h` and adjacent generated ASIC versions for expected register names, instance counts, and field-layout continuity at chunk boundaries.
- Exercise OTG3 modesets and atomic updates: timing totals, vstartup/vupdate/vready interrupts, master update lock, GSL/global-sync behavior, DRR/VRR vertical-total changes, DSC start position, pipe update status, static-screen events, and CRC readbacks.
- Validate HPD0 through HPD4 with connect/disconnect and HPD RX events, checking debounce/toggle filtering, delayed sense, ack, polarity updates, interrupt masking, and absence of interrupt storms.
- Run DP0 and DP1 link tests where routed: SST/MST modes, multiple link rates/lane counts, FEC, scrambler, PRBS/compliance patterns, DPHY CRC, fast training, stream enable/deferred-disable, MSA/VBID programming, DSC/MSO, ALPM, and GSP/secondary-packet scheduling.
- Exercise DIG0 HDMI/TMDS paths: HDMI enable/status, deep color, scrambling, audio/ACR packet timing, VBI/infoframe/generic packet scheduling, double-buffer updates, AFMT audio clocking, TMDS control symbols, FIFO status, output CRC, and force-disable.
- Check suspend/resume and power-gating restoration for OTG3, OPTC/ODM memory-power state, HPD filters, DP/DIG stream state, and HDMI/DP packet-generation state.
- Use perfmon17 smoke tests by selecting known display events, starting/stopping the counter, reading high/low values, and checking interrupt/active/state fields behave consistently.

## Notes For Final Merge

Merge this chunk with adjacent chunks for the same source file before producing the final per-file report. The previous chunk owns the beginning of `OTG3_OTG_CRC_SIG_BLUE_CONTROL_MASK`; this chunk owns the remainder of OTG3, shared OPTC/perfmon/HPD blocks, complete DP0 and DIG0 blocks, and the start of DP1; the next chunk owns the rest of DP1 and later DIO blocks. The final file-level document should describe the full header as generated DCN315 register-field metadata rather than as handwritten runtime logic.
