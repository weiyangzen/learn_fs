# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 51951-54426

## Scope

This chunk is a generated AMD DCN 2.0 register shift/mask header slice. It does not define executable code, structs, enums, or functions. Its public surface is a dense set of C preprocessor constants named as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`, used by AMDGPU display register helpers to compose, update, and decode memory-mapped hardware registers.

The line range starts in the middle of the `DC_PERFMON22_PERFMON_CVALUE_INT_MISC` definition and ends in the middle of `DMCUB_INTERRUPT_TYPE`; adjacent chunks own the omitted leading and trailing fields. Within this chunk the complete major blocks are DSC/DSCC instances 2 through 5, perfmon instances 23 through 26, and most DMCUB region/interrupt masks.

## Purpose

The constants describe bit positions and bit masks for DCN 2.0 display hardware:

- Tail of `DC_PERFMON22`: performance monitor interrupt status/acknowledge bits and counter value readback fields.
- `DSC_TOP[2-5]`: Display Stream Compression top-level clock/debug controls for DSC instances 2, 3, 4, and 5.
- `DSCCIF[2-5]`: DSC input interface configuration, including underflow recovery/status, pixel format, component depth, picture width/height, and double-buffer update pending state.
- `DSCC[2-5]`: DSC codec configuration, PPS programming fields, rate-control tables, overflow/underflow interrupt status enables, memory power controls, error counters, fullness telemetry, and debug bus rotation.
- `DC_PERFMON[23-26]`: perf counter controls and value/status readback blocks associated with the DSC display decoder perfmon address blocks.
- `DMCUB_*`: Display Microcontroller Unit (DMUB/DMCUB) address translation windows for regions 0, 1, 2, 4, 5, 6, 7 and region 3 code-window slots 0 through 7, plus interrupt enable, ack, status, and partial interrupt type fields.

## Important APIs, Types, and Macro Families

There are no callable APIs in this file. The relevant interface is the macro naming contract consumed by the AMD display register access layer:

- `REG_SET`, `REG_UPDATE`, `REG_GET`, and related helpers concatenate a register name and field name through helper macros such as `FN(reg_name, field)` in `display/dmub/src/dmub_reg.h`.
- Register offset headers such as `dcn_2_0_0_offset.h` provide `reg<REGISTER>` addresses; this header provides the paired field shifts and masks.
- `DMUB_SR(...)` and `DMUB_SF(...)` style lists in DMUB generation headers collect offsets and field definitions into per-ASIC register tables.

Important field groups in this chunk:

- `DSC_TOPn_DSC_TOP_CONTROL`: `DSC_CLOCK_EN`, `DSC_DISPCLK_R_GATE_DIS`, and `DSC_DSCCLK_R_GATE_DIS`.
- `DSCCIFn_DSCCIF_CONFIG0/1`: input underflow controls/status, pixel format, bits per component, double-buffer pending, picture width, and picture height.
- `DSCCn_DSCC_CONFIG0/1`: ICH reset policy, slice counts, alternate ICH encoding, rate control buffer model size, and ICH disable.
- `DSCCn_DSCC_INTERRUPT_CONTROL_STATUS`: status and interrupt-enable bits for rate buffer overflow/underflow and rate-control model overflow lanes 0 through 3.
- `DSCCn_DSCC_PPS_CONFIG0` through `PPS_CONFIG22`: DSC PPS fields including version, PPS identifier, line buffer depth, bits per component/pixel, chroma/RGB mode flags, picture/slice size, initial delays, scale intervals, BPG offsets, flatness QPs, RC model size, RC target offsets, RC buffer thresholds, and range min/max QP plus BPG offsets for ranges 0 through 14.
- `DSCCn_DSCC_MEM_POWER_CONTROL`: default low-power state plus force/disable/state fields for normal and native 4:2:2 memories.
- `DSCCn` telemetry registers: squared error lower/upper per component, max absolute error, rate buffer max fullness, rate control buffer max fullness, and test debug bus rotation.
- `DC_PERFMONn_*`: counter enable/clear/freeze, perfmon selection, counter state, high/low value halves, interrupt status/ack bits, and read selection fields.
- `DMCUB_REGION*`: low/high offset halves, top address plus enable bit, and region 3 CW base/top/offset controls.
- `DMCUB_INTERRUPT_ENABLE`, `DMCUB_INTERRUPT_ACK`, `DMCUB_INTERRUPT_STATUS`, and partial `DMCUB_INTERRUPT_TYPE`: timer, inbox, outbox, GPINT, undefined address fault, instruction fetch fault, and data write fault bit definitions.

## Control Flow

This header has no runtime branches or direct control flow. Runtime behavior emerges when driver code includes this header and calls the register helper macros:

1. A block-specific driver chooses a hardware register by symbolic name.
2. The helper uses the corresponding `reg<REGISTER>` offset from the offset header.
3. The helper applies this header's `SHIFT` and `MASK` constants to pack or extract a field value.
4. MMIO read/write helpers perform the actual hardware transaction.

For DSC programming, higher-level display code computes DSC PPS and rate-control parameters from the negotiated mode and compression settings, then writes the relevant `DSCCn_DSCC_PPS_CONFIG*`, `DSCCIFn_*`, and `DSC_TOPn_*` fields. For DMCUB programming, DMUB code configures memory windows and enables/acknowledges mailbox and GPINT interrupts through the DMCUB region and interrupt registers.

## State and Persistence Behavior

The macros themselves are compile-time constants and hold no state. The state they address is hardware state:

- DSC/DSCC fields persist in display engine registers until reset, power gating, or explicit reprogramming.
- Several DSC blocks advertise double-buffer update-pending fields; these indicate staged register updates that become active on the relevant display timing boundary rather than immediately.
- Underflow, overflow, fault, interrupt status, max-fullness, and error counters are hardware-observed state. Some status bits pair with interrupt enable and ack bits in the same or sibling register families.
- DMCUB region registers define address translation/protection windows for firmware-visible memory ranges. Top-address enable bits make those windows active or inactive.
- DMCUB interrupt enable bits persist as interrupt routing policy until driver changes or hardware reset. Ack masks clear latched interrupt sources when written according to the register helper semantics.

## Dependencies and Integration Points

This header is paired with `dcn_2_0_0_offset.h` and is included by DCN 2.0 display-related code, including DMUB, clock manager, IRQ service, GPIO factory, resource setup, and GMC code under the AMDGPU tree. It also follows the same generated naming schema used by later DCN headers, so shared driver macros can target different ASIC generations by swapping offset/mask tables.

The most direct integration points for this chunk are:

- DSC encoder setup paths that program `DSC_TOPn`, `DSCCIFn`, and `DSCCn` registers for compressed DisplayPort/eDP links.
- IRQ service tables that need enable/status/ack masks for DMCUB outbox, inbox, GPINT, and fault interrupts.
- DMUB initialization and diagnostic paths that configure and inspect DMCUB region windows and interrupt state.
- Performance monitor tooling or debug paths that use `DC_PERFMON23` through `DC_PERFMON26` counters to observe display decoder or DSC behavior.

## Risks and Maintenance Notes

- The file is generated and highly repetitive. Manual edits risk creating a mismatch between `SHIFT`, `MASK`, and the hardware register specification.
- The chunk boundary cuts through `DC_PERFMON22_PERFMON_CVALUE_INT_MISC` and `DMCUB_INTERRUPT_TYPE`; reviewers should consult adjacent chunks before drawing conclusions about those complete registers.
- DSC PPS fields are tightly packed. A wrong shift or mask can silently corrupt compression parameters, causing link training failures, visual corruption, bandwidth underestimation, or DSC underflow/overflow interrupts.
- DMCUB region masks control firmware-visible address windows. Incorrect address masks, high/low offset handling, or enable bits can break firmware boot, command mailboxes, trace buffers, or fault isolation.
- Interrupt enable/status/ack bits must remain aligned with IRQ service tables. A mismatch can leave interrupts stuck, unacknowledged, or invisible to the driver.
- Several field names are replicated across instances 2 through 5. Instance numbering mistakes can program the wrong DSC engine when multiple pipes are active.

## Test Signals

Useful validation signals for changes touching this area include:

- Successful compile of AMDGPU display and DMUB code using `dcn_2_0_0_sh_mask.h`; undefined field names or duplicate macro errors catch naming drift.
- Display modes requiring DSC on DCN 2.0 hardware light up reliably, especially multi-monitor and high-bandwidth modes that exercise DSC instances beyond 0 and 1.
- No DSC input underflow, rate buffer overflow/underflow, or rate-control model overflow bits are observed during mode set, hotplug, suspend/resume, or bandwidth stress.
- DMCUB firmware boots, mailboxes work, and outbox/inbox/GPINT interrupts are delivered and acknowledged without interrupt storms.
- DMCUB fault status bits for undefined address, instruction fetch, and data write faults remain clear during normal boot and display operation.
- Perfmon readback returns sane high/low counter values and interrupt status/ack behavior when perf counters are enabled for the DSC/perfmon blocks.
