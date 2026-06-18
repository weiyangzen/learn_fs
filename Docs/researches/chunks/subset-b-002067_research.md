# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 24345-26561

## Scope And Purpose

This chunk is part of AMD's generated DCN 3.5.0 register shift/mask header. It contains C preprocessor constants for hardware register bitfields, not executable driver logic. The macros define bit positions and positioned masks for display I/O, hot-plug detect, performance-monitor, DisplayPort AUX, and the beginning of VPG generic packet registers.

The requested range contains 2,217 `#define` lines: 1,108 `__SHIFT` macros and 1,109 `_MASK` macros. The imbalance is caused by chunk boundaries. The range starts inside the already-open `DC_I2C_READ_REQUEST_INTERRUPT` register, where earlier DDC1-DDC6 shift fields are in the previous chunk, and ends inside `VPG0_VPG_ISRC1_2_DATA`, before the remaining byte fields and masks for that register.

The substantive hardware covered here is the display I/O service surface around DDC/I2C read-request interrupts, scratch registers, DIO memory power and link encoder selection, HPD instances 0 through 4, `DC_PERFMON16`, DP AUX instances 0 through 4, and the first VPG0 generic packet and ISRC packet data registers.

## Important Constants And Register Areas

`DC_I2C_READ_REQUEST_INTERRUPT` provides read-request status, interrupt, acknowledge, and mask bits for DDC1 through DDC6 and DDCVGA, plus global read-request acknowledge-enable and interrupt-type bits. Because the chunk begins mid-register, the visible DDC6/DDCVGA shifts must be reconciled with the earlier shifts before whole-register documentation is final.

`DIO_SCRATCH0` through `DIO_SCRATCH7` expose eight full-width 32-bit scratch registers. These are generic DIO state slots; their meaning is supplied by higher-level firmware or driver conventions rather than by this shift/mask header.

The DIO power and link-selection registers include:

- `DIO_DP_ALPM_WAKEUP_INTERRUPT_STATUS` bits for DIGA through DIGG DisplayPort ALPM wakeup status.
- `DIO_MEM_PWR_STATUS`, `DIO_MEM_PWR_CTRL`, and `DIO_MEM_PWR_CTRL2`, covering I2C and DPA-DPG light-sleep force/disable/state fields.
- `DIO_POWER_MANAGEMENT_CNTL`, with reset and all-busy-off fields.
- `DIO_HDMI_RXSTATUS_TIMER_CONTROL`, with enable, type, status, mask, and 12-bit interval fields.
- `DIO_LINKA_CNTL` through `DIO_LINKF_CNTL`, each selecting encoder type and HPO HDMI/DP encoder routing.

`HPD0` through `HPD4` repeat the same hot-plug-detect register layout: interrupt status, interrupt control, timing/control, fast-train delay controls, and toggle-filter delay controls. The status fields include HPD sense, delayed sense, RX interrupt status, and connect/disconnect filter timer values. The control fields include acknowledge, polarity, enable, RX interrupt acknowledge/enable, connection/RX timers, HPD enable, AUX TX delay, fast-train delay, and connect/disconnect debounce delays.

`DC_PERFMON16` defines one display performance-monitor block. It includes perfcounter control and secondary control, eight packed counter-state fields, perfmon run/report/interrupt control, interrupt-status/ack fields for counters 0 through 7, low/high value registers, and read-select fields. These macros are used to program event selection, run-enable behavior, count-off conditions, interrupt handling, and counter readback.

`DP_AUX0` through `DP_AUX4` are repeated DisplayPort AUX controller instances. For each instance the chunk defines:

- AUX enable/reset, local-side read, HPD-disconnect behavior, mode detection, HPD select, impedance calibration request, test/deglitch, and spare bits.
- Software transaction control, arbitration between software and DMCU users, software/local-side done interrupts, and GTC sync interrupt fields.
- Software and local-side status words with done/request, timeout state, timeout, overflow, HPD disconnect, partial-byte, non-AUX mode, invalid stop/start/sync, receive-no-detect, reply byte count, CP IRQ, update, and arbitration status fields.
- Software and local-side data window fields, including 8-bit data, 5-bit index, read/write, and auto-increment-disable controls.
- AUX PHY TX/RX timing controls and status readbacks, including precharge, receive windows, transition filtering, threshold allowance, timeout length, TX/RX state, and half-symbol-period fields.
- AUX GTC sync control, error thresholds, controller status, sync transaction status, and PHY wake control.

The final `VPG0` block starts video packet generator generic packet programming. It includes indexed generic packet byte access, 15 generic packet frame-update bits with matching pending bits, 15 immediate-update bits with matching pending bits, lock/conflict status, VPG GSP memory power state, and the beginning of ISRC1/2 indexed data access. The last visible register, `VPG0_VPG_ISRC1_2_DATA`, is incomplete in this chunk.

## APIs, Types, And Functions

There are no functions, structs, enums, or inline helpers in this chunk. The API surface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT` gives the field's bit position within a 32-bit MMIO register.
- `REGISTER__FIELD_MASK` gives the positioned mask for that field.
- Repeated instance prefixes such as `HPD0_`, `DP_AUX3_`, and `VPG0_` bind the field layout to a specific hardware instance.

Consumers pair these macros with matching DCN 3.5.0 register-address macros from the corresponding offset header and with AMD display register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, and generated register-field lists. This header supplies bit layout only; enum meanings, legal values, access ordering, and side effects come from the hardware programming guide and caller-side DCN code.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior occurs when AMD display code reads or writes the described MMIO registers.

The implied DDC/I2C and HPD flows are interrupt-oriented. Hardware latches read-request or hotplug status bits; the driver reads status fields, writes acknowledge bits, controls masks/enables, and uses debounce or fast-train timing fields to tune connector event handling. Incorrect acknowledge or mask handling can produce missed hotplug events, interrupt storms, or stale RX interrupt status.

The implied DP AUX flow is transactional. Driver code configures AUX control and PHY timing, arbitrates register ownership, writes indexed transaction data, starts software or local-side requests, waits for done/status bits, handles timeout and protocol error fields, and acknowledges interrupts. GTC sync fields add a secondary state machine for lock acquisition, error thresholds, retry behavior, and critical-error acknowledgement.

The implied DIO and VPG power flows are stateful hardware control flows. Light-sleep force/disable fields and memory power state readbacks must be coordinated with active display paths. VPG generic packet update controls let software request frame-bound or immediate packet updates and poll pending bits until hardware consumes them.

`DC_PERFMON16` defines a performance-monitor control flow: select events and counted values, configure start/stop/count-off behavior, enable reporting or interrupts, run the counter, then read low/high value registers and acknowledge counter interrupts.

## State And Persistence

The file itself stores no mutable state. It defines how software addresses state held in display hardware registers.

Persistent hardware state represented in this chunk includes interrupt masks and acknowledgements, DIO scratch values, memory light-sleep force/disable choices, encoder routing selections, HPD debounce/timer controls, perfmon event and run-control configuration, AUX transaction buffers and arbitration state, AUX PHY timing controls, GTC sync lock/error state, VPG generic packet bytes, VPG update-pending state, and VPG memory power state.

Most of this state persists until reset, suspend/resume reinitialization, modeset programming, or a later register update. Status and acknowledge fields are side-effect-prone: reading status does not necessarily clear it, while writing an ack bit can clear a latched event. Indexed data registers such as AUX SW/LS data and VPG generic packet data depend on an index field and optional auto-increment behavior, so the current index is also part of the effective hardware state.

## Dependencies And Integration Points

This generated header depends on the matching DCN 3.5.0 register offset header and the AMDGPU display register helper framework. The numeric values are ASIC-generation-specific and should not be mixed with other DCN versions unless the generated register database proves compatibility.

Important integration points include:

- DRM connector detection and hotplug handling through HPD status, control, timing, and interrupt fields.
- DDC/I2C and DisplayPort AUX code paths for EDID reads, DPCD access, link training, HDCP/CP IRQ processing, and sideband operations.
- DIO runtime power-management code that controls I2C and DP memory light sleep and observes memory power state.
- Display link encoder routing for DIO_LINKA-F and HPO HDMI/DP encoder selection.
- Display performance diagnostics that program `DC_PERFMON16` counters and collect low/high values.
- Video packet generator paths that load generic and ISRC packets for HDMI/DP infoframes and other stream metadata.

The repeated DP AUX and HPD layouts are especially important integration contracts. Higher-level code often indexes into per-instance register tables; token naming and field consistency across instances must remain stable for generated field-list macros and per-link code to work.

## Risks And Edge Cases

Generated-header drift is the main risk. A wrong shift or mask compiles cleanly but can direct writes to the wrong bit, causing missed HPD events, broken AUX transactions, incorrect encoder routing, bad power-state transitions, or corrupted packet updates.

Chunk boundaries create local incompleteness. The first visible register is only the tail of `DC_I2C_READ_REQUEST_INTERRUPT`, and the last visible register is only the start of `VPG0_VPG_ISRC1_2_DATA`. Whole-register validation for those two registers must include adjacent chunks.

AUX arbitration fields include aliases that intentionally share a bit position, such as `AUX_SW_USE_AUX_REG_REQ` and `AUX_SW_PENDING_USE_AUX_REG_REQ`, and similarly for DMCU ownership. Validation scripts must allow these semantic aliases instead of treating every overlapping mask as an error.

Interrupt fields combine status, mask, enable, and acknowledge bits in adjacent positions. Callers must preserve unrelated fields during read-modify-write operations and use established ack semantics; open-coded writes can accidentally clear pending events or unmask unwanted interrupts.

Indexed data windows are ordering-sensitive. Programming AUX or VPG packet bytes with the wrong index or auto-increment setting can silently write the wrong byte lane. VPG frame-update and immediate-update pending bits must be observed before assuming packet data is active.

Power and PHY timing fields affect active links. DIO/VPG memory power, AUX reset, AUX PHY receive thresholds, timeout windows, and GTC sync error thresholds can affect link training, HPD handling, EDID reads, and timing synchronization. These should be changed only through the ASIC-specific display sequences that understand hardware timing requirements.

## Test And Validation Signals

Build validation should include DCN 3.5.0 AMD display objects that include `dcn_3_5_0_sh_mask.h` and instantiate HPD, AUX, DIO, perfmon, and VPG register lists. Missing or renamed macros usually surface at compile time; wrong numeric values usually require generated-data diffing or hardware tests.

Useful generated-data checks include:

- Compare this range against the authoritative DCN 3.5.0 register database.
- Verify every complete register has matching shift and mask fields, while allowing the incomplete first and last registers.
- Diff repeated layouts across `HPD0` through `HPD4` and `DP_AUX0` through `DP_AUX4`, allowing only intentional instance prefix changes and documented aliases.
- Check masks for non-overlap within each complete register, except for explicit alias fields in AUX arbitration and interrupt-mask naming patterns.
- Cross-check matching offset-header entries for every register prefix used here.

Runtime signals include stable hotplug detection across connect/disconnect and RX interrupt events, successful DDC/EDID and DP AUX/DPCD transactions on all exposed links, clean link training without AUX timeout/overflow protocol errors, correct CP IRQ/update status handling, working perfmon counter reads and interrupts, correct VPG generic/ISRC packet updates, and no display regressions across suspend/resume, runtime power management, multi-monitor modesets, and HPD storms.

## Research Notes

This is source-tree-aligned chunk research only. It intentionally writes only `Docs/researches/chunks/subset-b-002067_research.md`. Whole-file research for `dcn_3_5_0_sh_mask.h` must merge adjacent chunks to complete `DC_I2C_READ_REQUEST_INTERRUPT` at the start and `VPG0_VPG_ISRC1_2_DATA` at the end.
