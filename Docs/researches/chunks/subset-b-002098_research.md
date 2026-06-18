# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 24332-26548

## Purpose

This chunk is part of the generated DCN 3.5.1 shift/mask header for AMD display hardware. It does not implement functions or own runtime control flow; it defines compile-time bit positions and masks for MMIO register fields consumed by AMDGPU display code through generated register-access macros.

The covered range spans Display I/O, HPD, DC perfmon, DisplayPort AUX, and VPG generic packet fields. It starts in the middle of the `DC_I2C_READ_REQUEST_INTERRUPT` field group: the shift definitions and the first `DC_I2C_DDC1_READ_REQUEST_OCCURRED_MASK` line are immediately before this chunk, while lines 24332-24360 contain the rest of the masks. It also ends in the middle of `VPG0_VPG_MPEG_INFO0`, with only `VPG_MPEG_INFO_CHECKSUM` and `VPG_MPEG_INFO_MB0` shifts inside the chunk; the remaining shifts and masks continue after line 26548.

## Important macros and register fields

- `DC_I2C_READ_REQUEST_INTERRUPT__*` covers DDC1-DDC6 and DDCVGA read-request interrupt masks. Each DDC channel has `READ_REQUEST_OCCURRED`, `READ_REQUEST_INT`, `READ_REQUEST_ACK`, and `READ_REQUEST_MASK` fields packed in four-bit groups, plus global `DC_I2C_DDC_READ_REQUEST_ACK_ENABLE` and `DC_I2C_DDC_READ_REQUEST_INT_TYPE` bits. Because the chunk begins at line 24332, it omits the `DDC1_READ_REQUEST_OCCURRED_MASK` definition at line 24331 but includes the rest of the group.
- `DIO_SCRATCH0` through `DIO_SCRATCH7` expose full 32-bit scratch register payload masks. These are broad software/hardware mailbox-style registers rather than narrowly typed bitfields.
- `DIO_DP_ALPM_WAKEUP_INTERRUPT_STATUS` provides per-DIG wake status bits for `DIGA` through `DIGG`, supporting DisplayPort ALPM wake detection.
- `DIO_MEM_PWR_STATUS`, `DIO_MEM_PWR_CTRL`, and `DIO_MEM_PWR_CTRL2` define I2C and DP link memory light-sleep state, disable, and force bits for DPA-DPG. These fields are power-management controls/status for the Display I/O block.
- `DIO_POWER_MANAGEMENT_CNTL`, `DIO_HDMI_RXSTATUS_TIMER_CONTROL`, and `DIO_LINKA_CNTL` through `DIO_LINKF_CNTL` describe reset/busy controls, HDMI RX status timer behavior, and link-to-HPO encoder selection. Link control fields include `ENC_TYPE_SEL`, `HPO_HDMI_ENC_SEL`, and `HPO_DP_ENC_SEL`.
- `HPD0_DC_HPD_*` through `HPD4_DC_HPD_*` repeat hot-plug-detect status, toggle filter, fast-train, interrupt control, and control fields for five HPD instances in this chunk. They include sense/status bits, RX interrupt status, connection/disconnection filter timers, interrupt enables/acks, and polarity/routing controls.
- `DC_PERFMON16_*` defines one display performance monitor instance. It includes counter low/high reads, counter control, perfmon enable/state, counter-state windowing, counter profile/debug state, current-value latch controls, overflow/clear/status bits, and interrupt select/read-select fields.
- `DP_AUX0_*` through `DP_AUX4_*` repeat the AUX-channel field layout for five DP AUX instances. The blocks include AUX enable/reset/control, software transaction control/data/status, LTTPR link-service data/status, AUX register arbitration, interrupts, DPHY TX/RX timing controls and status, GTC sync control/error/status, and AUX PHY wake handshakes.
- `VPG0_VPG_GENERIC_PACKET_ACCESS_CTRL`, `VPG0_VPG_GENERIC_PACKET_DATA`, `VPG0_VPG_GSP_FRAME_UPDATE_CTRL`, `VPG0_VPG_GSP_IMMEDIATE_UPDATE_CTRL`, `VPG0_VPG_GENERIC_STATUS`, `VPG0_VPG_MEM_PWR`, and `VPG0_VPG_ISRC1_2_*` describe VPG0 generic packet RAM access, byte packing, frame/immediate update triggers for generic packet slots 0-14, update-pending status bits, conflict status/clear, VPG memory power, and ISRC data indexing/data bytes.

## Control flow and usage model

There is no direct control flow in this header. The runtime pattern is generated-register expansion:

1. DCN 3.5.1 code includes `dcn_3_5_1_offset.h` and this `dcn_3_5_1_sh_mask.h`.
2. Macros such as `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `SRI(...)`, and `SE_SF(...)` expand these constants into register tables or read/modify/write helpers.
3. Driver code writes packed register values or extracts status fields by combining the address from the offset header with the mask and shift from this header.

The strongest local examples are `display/dmub/src/dmub_dcn351.c`, which initializes DMUB DCN35 register masks/shifts from the generated macros, and `display/dc/irq/dcn351/irq_service_dcn351.c`, which uses DCN 3.5.1 HPD interrupt masks to fill `irq_source_info` entries. VPG field names from this chunk also align with `display/dc/dcn31/dcn31_vpg.h`, where `DCN31_VPG_MASK_SH_LIST` maps `VPG0_VPG_*` masks/shifts into `struct dcn31_vpg_shift` and `struct dcn31_vpg_mask`.

## State and persistence behavior

The macros are stateless constants. The state they describe lives in DCN hardware registers and is reset or reprogrammed by display IP initialization, GPU reset, suspend/resume, hotplug handling, link training, modeset, DMUB coordination, or VPG packet programming.

State categories in this chunk are hardware-visible:

- DDC/I2C read-request bits are interrupt/status/ack/mask state for connector-side DDC transactions.
- DIO scratch registers are 32-bit mutable storage and must be treated as shared hardware state.
- DIO memory power and ALPM wake fields reflect power-gated/light-sleep state and wake events across DisplayPort link blocks.
- HPD fields persist as interrupt routing, ack, filter timing, polarity, and live/delayed sense state for connectors.
- AUX control/status fields represent an active transaction engine. `AUX_SW_GO`, `AUX_SW_DONE`, `AUX_LS_UPDATED_ACK`, arbitration request/done bits, reset bits, and PHY wake bits are ordering-sensitive hardware handshakes.
- VPG generic packet fields persist packet data, update triggers, pending bits, and conflict state; stale VPG data or pending update bits can affect InfoFrame/metadata transmission until cleared or overwritten.

## Dependencies and integration points

- The companion `dcn_3_5_1_offset.h` supplies address macros for the register names in this chunk, for example `regDC_I2C_READ_REQUEST_INTERRUPT`, `regDIO_SCRATCH0`, `regDIO_DP_ALPM_WAKEUP_INTERRUPT_STATUS`, `regDIO_MEM_PWR_STATUS`, `regDIO_LINKA_CNTL`, `regHPD0_DC_HPD_INT_STATUS`, `regDP_AUX0_AUX_CONTROL`, `regDP_AUX4_AUX_PHY_WAKE_CNTL`, `regVPG0_VPG_GENERIC_PACKET_ACCESS_CTRL`, and `regVPG0_VPG_MPEG_INFO0`, all on base index 2 in the checked offset header.
- `dmub_dcn351.c` depends on this header to populate DMUB-facing DCN35 register metadata for DCN 3.5.1 hardware.
- `irq_service_dcn351.c` depends on the HPD masks to build per-source interrupt enable/ack/status records used by the DC interrupt service layer.
- VPG consumers depend on the `VPG0_VPG_*` layout through the shared DCN31 VPG abstractions, because later DCN versions reuse those field names and structures.
- DP AUX fields integrate with the display link/DDC/AUX stack, DisplayPort link training, LTTPR access, HDCP/CPIRQ handling through AUX, and GTC synchronization support.
- DIO link selection fields integrate with DCN link encoder assignment, especially HPO HDMI/DP encoder routing.

## Risks and edge cases

- Chunk-boundary incompleteness: this range omits one mask at the beginning of `DC_I2C_READ_REQUEST_INTERRUPT` and most of `VPG0_VPG_MPEG_INFO0` at the end. Any per-register final report must reconcile adjacent chunks before treating those groups as complete.
- Generated header drift: a wrong mask/shift silently corrupts hardware programming. Repeated blocks such as `DP_AUX0` through `DP_AUX4` and `HPD0` through `HPD4` are vulnerable to instance-copy mistakes.
- Reserved-bit corruption: many registers contain sparse fields. Callers must use read/modify/write helpers or preserve unknown bits, especially for DIO power control, AUX control, HPD control, and perfmon state.
- Handshake ordering: AUX reset/done, AUX software-go/done, arbitration request/done, interrupt ack, and PHY wake go/pending/ack fields should be written in the expected hardware sequence. Setting or clearing a bit with the right mask at the wrong time can wedge transactions or lose interrupts.
- Status-versus-ack ambiguity: HPD, AUX, GTC sync, and perfmon groups contain status, mask, and ack/clear fields in nearby bits. Using an ack mask as a status test, or vice versa, can cause missed events.
- Width truncation: packed fields such as `AUX_HPD_SEL`, `AUX_SW_WR_BYTES`, timer intervals, reply byte counts, GTC thresholds, perfmon counter selects, and VPG data indexes have limited widths. Callers must validate values before shifting.
- Power impact: DIO and VPG memory light-sleep disable/force fields can affect idle power, wake latency, and resume behavior.
- Partial instance coverage: this chunk contains HPD0-HPD4 and DP_AUX0-DP_AUX4 but not necessarily every possible connector instance for the ASIC; consumer tables must match the actual hardware instance count.

## Test signals

- Build-test DCN 3.5.1 AMDGPU display with `dmub_dcn351.c` and `irq_service_dcn351.c` enabled. Missing or misspelled generated macros should fail compilation.
- Add or run generated-header consistency checks that compare `DP_AUX0`-`DP_AUX4` field layouts and `HPD0`-`HPD4` field layouts for identical shifts/masks where the hardware instances are expected to match.
- Validate offset/mask pairing by checking that every register family used by consumers has both `reg...` address macros in `dcn_3_5_1_offset.h` and matching `__SHIFT`/`_MASK` symbols in this header.
- Runtime HPD tests: plug/unplug and HPD RX interrupt scenarios should set status bits, honor masks, and clear through the documented ack bits without losing later events.
- Runtime AUX tests: EDID reads, DPCD reads/writes, link training, LTTPR access, CPIRQ handling, AUX timeout/error injection, and suspend/resume should exercise `AUX_SW_STATUS`, `AUX_LS_STATUS`, arbitration, interrupt, reset, DPHY, GTC sync, and PHY wake fields.
- Power-management tests: monitor DIO and VPG memory power state fields across idle, display on/off, ALPM wake, suspend/resume, and link reconfiguration.
- VPG packet tests: write generic packet and ISRC data through the VPG path, request frame/immediate updates, observe pending bits clear, and verify conflict status/clear behavior.
- Perfmon tests: configure `DC_PERFMON16` counters, latch current values, verify overflow/clear behavior, and confirm interrupt/mask fields do not interfere with normal display interrupts.
