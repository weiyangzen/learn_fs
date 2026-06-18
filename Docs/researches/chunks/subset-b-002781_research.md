# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_sh_mask.h lines 16392-18711

## Scope

This chunk covers the tail of the `MMEA3` MMHUB EA decoder register field definitions and most of the next decoder instance, `aid_mmhub_ea_mmeadec4`, exposed as `MMEA4_*` shift and mask macros. The range starts inside `MMEA3_LATENCY_SAMPLING`, continues through the `MMEA3` performance-counter, uncorrectable/correctable error, DSM/error-injection, clock-gating, EDC, error-status, and miscellaneous control fields, and then defines the corresponding `MMEA4` client grouping, arbitration, priority, credit, performance, reliability, DSM, clock, EDC, and error-status fields through `MMEA4_MISC2`.

The file is a generated AMDGPU register-mask header. It contains no functions, structs, storage, or executable control flow. Its API surface is the set of C preprocessor constants that other AMDGPU MMHUB code uses when composing or decoding 32-bit memory-mapped register values.

## Purpose

The purpose of this chunk is to provide bit-accurate symbolic names for fields in MMHUB EA MMEA decoder instances 3 and 4 on `mmhub_1_8_0` ASICs. These fields let driver code express hardware programming in terms of client IDs, request groups, virtual channels, priority/urgency policy, SDP arbitration, credits, latency sampling, performance counters, ECC/parity status, error injection, and clock/error control instead of hard-coded numeric shifts and masks.

The `MMEA4` definitions mirror the pattern used for earlier MMEA decoder instances. They describe how DRAM, GMI, and IO read/write traffic is grouped, mapped to virtual channels, delayed, prioritized, throttled, blocked, counted, and diagnosed. The final per-file research pass should reconcile this chunk with the preceding and following chunks because `mmhub_1_8_0_sh_mask.h` is a single generated register map split only for research-size reasons.

## Important APIs And Register Families

The public API in this chunk is the macro naming convention:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit of a field.
- `REGISTER__FIELD_MASK` gives the field mask already positioned in the register word.
- Consumers normally combine these with AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, or local read/modify/write helpers from the surrounding driver tree.

Important register families in this range include:

- `MMEA3_LATENCY_SAMPLING`, `MMEA4_LATENCY_SAMPLING`: two latency samplers with enable/select bits for DRAM, GMI, IO, read, write, atomic-return, atomic-no-return, and virtual-channel filters.
- `MMEA3_PERFCOUNTER_*`, `MMEA4_PERFCOUNTER_*`: low/high counter words, compare value, per-counter configuration (`PERF_SEL`, `PERF_SEL_END`, `PERF_MODE`, `ENABLE`, `CLEAR`), and result control (`PERF_COUNTER_SELECT`, start/stop triggers, enable-any, clear-all, stop-on-saturate).
- `MMEA3_UE_ERR_STATUS_*`, `MMEA4_UE_ERR_STATUS_*`: uncorrectable-error status, address validity, encoded address, memory ID, ECC/parity indicators, error-info validity, error-info payload, UE and FED counters, and reserved high bits.
- `MMEA3_CE_ERR_STATUS_*`: correctable-error status at the end of the `MMEA3` block, with valid/address/memory fields and high-word ECC, error-info, CE count, poison, and reserved bits.
- `MMEA3_DSM_*`, `MMEA4_DSM_*`: data SRAM/memory diagnostic and fault-injection controls for DRAM read/write command/page/data memories, GMI read/write command/page/data memories, IO read/write command/data memories, read/write return tag memories, and MAM D0-D3 memories.
- `MMEA4_DRAM_*`, `MMEA4_GMI_*`, `MMEA4_IO_*`: client-ID to group maps, group-to-virtual-channel maps, lazy request accumulation, CAM control, page/group burst limits, age/fixed/queue/urgency priorities, urgency masking per client ID, and quantum thresholds for the DRAM, GMI, and IO traffic classes.
- `MMEA4_SDP_*`: shared data path arbitration for DRAM/GMI/final arbitration, per-class priorities, tag and response credits, per-VC tag/VCC/VCD reservations, request pass/password overrides, request chain overrides, inner-domain mode, and read/write/atomic block levels.
- `MMEA4_MISC` and `MMEA4_MISC2`: relative priority mode, early write-return per VC, link-manager dynamic/reconnect/halt/idle settings, chain-switch preferences, client-group swapping, IO read/write priority enable, request blocking status, and DRAM/GMI read/write throttles.
- `MMEA4_CGTT_CLK_CTRL`, `MMEA4_EDC_MODE`, `MMEA4_ERR_STATUS`: clock-gating delays/overrides, EDC/FED/FUE handling, bypass/propagation policy, SDP response status, data parity error, error clearing, busy-on-error behavior, fatal interrupt controls, level interrupt mode, and client FUE flag.

## Control Flow

There is no direct control flow in this chunk. It is a declarative bitfield table.

Runtime control flow appears in the driver code that includes this header. Typical use is:

1. Read a 32-bit MMHUB register from the appropriate MMIO address header.
2. Use a `*_MASK` and `*_SHIFT` pair, or a higher-level field helper, to extract or update one field.
3. Write the composed value back during ASIC initialization, clock/power configuration, memory-hub tuning, RAS setup, performance collection, or debug/error-injection flows.

The macros are also used in branch decisions when driver code decodes status registers. For example, status-valid and address-valid fields gate whether an error record is meaningful, while fatal-interrupt and busy-on-error fields affect how initialization or recovery paths configure hardware behavior.

## State And Persistence Behavior

The header itself has no persistent state and performs no I/O. State changes occur only when another compilation unit uses these constants to program memory-mapped MMHUB registers.

The hardware state represented by these fields is persistent at the device-register level until reset or reprogramming. Important state classes include:

- Arbitration and quality-of-service state: client-to-group maps, group-to-VC maps, lazy accumulation, priority, urgency, burst, quantum, throttle, request-block, and chain-switch settings.
- Credit and reservation state: SDP tag limits, read/write response credits, per-VC tag reservations, and VCC/VCD credit reservations.
- Diagnostic state: latency-sampling filter selection, performance-counter configuration and current counter words.
- Reliability state: uncorrectable and correctable error status, ECC/parity flags, error counters, poison/FED/FUE status, fatal-interrupt policy, and clear-error bits.
- Test and fault-injection state: DSM irritator data, single-write enables, per-memory error-injection enables, injection-delay selection, and global injection delay.
- Power/clock state: clock-gating delay, hysteresis, soft stall/override bits, and EDC bypass/propagation controls.

Because these are hardware register definitions, incorrect use can persist until GPU reset and can affect memory request ordering, fairness, error reporting, or debug behavior across later driver operations.

## Dependencies And Integration Points

This header depends on the corresponding MMHUB address header for register offsets. The `_sh_mask.h` file supplies field-level layout, while code elsewhere needs the register address definitions to perform MMIO reads and writes. It also depends on the AMDGPU convention for generated ASIC headers: field names are stable tokens consumed by register helper macros and by ASIC-specific initialization tables.

Integration points include:

- AMDGPU MMHUB initialization and IP block code that configures client groups, virtual channels, priority policy, clock gating, and SDP credits for `mmhub_1_8_0`.
- RAS and error-handling paths that read `UE_ERR_STATUS`, `CE_ERR_STATUS`, `EDC_MODE`, and `ERR_STATUS` fields to classify ECC, parity, poison, FED/FUE, fatal, and response-status conditions.
- Performance and debug tooling paths that configure `PERFCOUNTER*`, `LATENCY_SAMPLING`, and result-control fields.
- Hardware validation and bring-up paths that use DSM/error-injection fields for targeted memory/register-file fault injection.
- Generated-register consistency with sibling decoder instances (`MMEA0` through `MMEA4` and later chunks), because much of the programming model is replicated per EA decoder.

Although this repository path sits under a Ceph client source import, the file is part of the Linux AMDGPU DRM hardware register interface, not Ceph filesystem logic.

## Risks And Edge Cases

The main risk is bitfield drift from the hardware specification. A wrong shift or mask can silently program the wrong field in a 32-bit MMIO register, affecting unrelated hardware behavior in the same word.

Several registers pack many independent fields tightly. The client-to-group maps place sixteen 2-bit client group fields in a single word, urgency masking places one bit per client ID across all 32 bits, and SDP priority/reservation registers pack multiple per-group or per-VC values. Callers must preserve unrelated bits during read/modify/write operations.

Fields with side effects need special care. `CLEAR`, `CLEAR_ALL`, `CLEAR_ERROR_STATUS`, DSM single-write enables, error-injection enables, request blocking, clock overrides, EDC bypass, and fatal-interrupt controls are not passive metadata. Accidentally setting them while updating adjacent fields could clear diagnostic state, inject errors, suppress protection, stall requests, or change interrupt delivery.

Status fields and control fields share naming conventions but have different access semantics. For example, `REQUESTS_BLOCKED`, `BUSY_ON_ERROR`, `FUE_FLAG`, `STATUS_VALID_FLAG`, and address-valid bits should generally be interpreted as hardware-reported state, while group maps, priority values, credits, and throttle bits are programmed policy. Code review should verify access direction against the register spec, not just the macro name.

The chunk boundary starts inside the `MMEA3` section and ends before the `MMEA4_CE_ERR_STATUS_*` definitions are complete in the next chunk. Any merged per-file report should avoid treating this document as a complete account of either decoder instance.

## Test Signals

High-signal validation is mostly compile-time and hardware/driver-behavior oriented:

- Build AMDGPU code paths that include `mmhub_1_8_0_sh_mask.h` so generated macro names and suffixes remain available to all consumers.
- Compare this header against the authoritative AMD register database for `mmhub_1_8_0`, especially packed client maps, urgency masks, SDP credit/reservation fields, DSM/error-injection fields, and `ERR_STATUS` side-effect bits.
- Exercise register helper unit tests or static checks, where available, to ensure representative `REG_SET_FIELD`/`REG_GET_FIELD` calls produce the expected masks and shifts for multi-bit fields such as client group, virtual channel, priority, credit, and injection delay.
- On hardware or simulator, read back programmed DRAM/GMI/IO group and priority settings after MMHUB initialization and confirm only intended fields changed.
- Use RAS/error-injection validation to confirm `UE_ERR_STATUS`, `CE_ERR_STATUS`, `EDC_MODE`, `ERR_STATUS`, and DSM injection controls report and clear expected ECC/parity/FED/FUE events.
- Use performance-counter and latency-sampling smoke tests to confirm counter enable/clear/select bits, start/stop triggers, and sampler filters select the intended traffic class and virtual channels.
