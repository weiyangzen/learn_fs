# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_sh_mask.h lines 15145-17562

## Scope

This chunk is a generated-style AMD DCN 2.0.1 register field header segment. It contains only C preprocessor constants, not executable functions or structs. Each register field is exported as paired `__SHIFT` and `_MASK` macros so the AMD display driver can construct read/modify/write operations against memory-mapped display hardware registers.

The covered range starts in the `OTG1` timing generator block, continues through OPTC misc, DIO I2C, DIO power/clock/interrupt state, HPD0/HPD1, DP AUX0/AUX1, and ends inside the DIG0/TMDS encoder field set.

## Purpose

The chunk gives the DCN 2.0.1 display stack the bit layout for several display hardware units:

- `OTG1_*`: optical timing generator status, counters, snapshots, interrupts, CRC windows/results, static-screen detection, 3D/stereo state, global sync lock, GSL, DRR, DSC start position, and update-lock controls.
- `DWB_SOURCE_SELECT`, `GSL_SOURCE_SELECT`, `OPTC_CLOCK_CONTROL`: OPTC misc source routing and clock gating fields.
- `DC_I2C_*`: DDC/I2C controller command, arbitration, transaction, status, speed, setup, and data fields.
- `DIO_*`: DIO scratch registers, memory power state/control, clock gating, generic interrupt, and HDMI RX status timer fields.
- `HPD0_*` and `HPD1_*`: hot-plug-detect status, interrupt control, debounce/toggle filtering, fast train, and RX interrupt timing fields.
- `DP_AUX0_*` and `DP_AUX1_*`: DisplayPort AUX controller enable/reset, software and link-service transaction control, arbitration, interrupt, RX/TX data, PHY timing, and status fields.
- `DIG0_*`, `HDMI_*`, `AFMT_*`, `TMDS_*`: digital front/back end selection, HDMI packet/control/status, metadata/audio formatting, generic infoframe bytes, audio clock regeneration, IEC 60958 channel status, audio test/CRC, and TMDS pattern/control fields.

## Important APIs, Types, And Macros

There are no callable APIs in this range. The public surface is the macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least significant bit.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted register mask for that field.
- Field consumers combine these constants through AMD display register helper macros such as `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, `I2C_SF`, `AUX_SF`, `LE_SF`, and `SE_SF`.

Important register families in this chunk:

- `OTG1_OTG_STATUS`, `OTG1_OTG_STATUS_POSITION`, `OTG1_OTG_STATUS_FRAME_COUNT`, `OTG1_OTG_STATUS_VF_COUNT`, and `OTG1_OTG_STATUS_HV_COUNT` expose live scanout state and counters.
- `OTG1_OTG_INTERRUPT_CONTROL`, `OTG1_OTG_GLOBAL_SYNC_STATUS`, and `OTG1_OTG_RANGE_TIMING_INT_STATUS` define interrupt mask/type/status/clear fields.
- `OTG1_OTG_UPDATE_LOCK`, `OTG1_OTG_DOUBLE_BUFFER_CONTROL`, `OTG1_OTG_MASTER_UPDATE_LOCK`, and `OTG1_OTG_GLOBAL_CONTROL0..3` define atomic timing-update and double-buffering behavior.
- `DC_I2C_CONTROL`, `DC_I2C_ARBITRATION`, `DC_I2C_INTERRUPT_CONTROL`, `DC_I2C_SW_STATUS`, `DC_I2C_DDC1_HW_STATUS`, `DC_I2C_DDC2_HW_STATUS`, `DC_I2C_TRANSACTION0..3`, and `DC_I2C_DATA` define DDC command setup and status reporting.
- `DP_AUX0_AUX_*` and `DP_AUX1_AUX_*` are nearly parallel channel instances for AUX control, arbitration, interrupts, SW/LS status, data FIFOs, DPHY timing, and DPHY status.
- `DIG0_HDMI_*`, `DIG0_AFMT_*`, and `DIG0_TMDS_*` define stream encoder fields for HDMI/DP audio/video packet generation and TMDS control.

## Control Flow

This header has no runtime control flow. Runtime flow is indirect:

1. DCN 2.0.1 resource and block constructors include this header along with the matching address header.
2. Register-table macros bind register addresses with the `__SHIFT` and `_MASK` constants into per-block register, shift, and mask tables.
3. Display code calls accessor helpers such as `REG_UPDATE`, `REG_GET`, `I2C_SF`, `AUX_SF`, `LE_SF`, or `SE_SF`.
4. Those helpers use the constants from this header to pack field values into MMIO writes or unpack field values from MMIO reads.

Examples of downstream use in the tree include:

- `display/dc/dce/dce_i2c_hw.c` updates `DC_I2C_CONTROL` fields such as `DC_I2C_GO`, `DC_I2C_SOFT_RESET`, `DC_I2C_DDC_SELECT`, and `DC_I2C_TRANSACTION_COUNT`.
- `display/dc/dce/dce_i2c_hw.h` maps `DC_I2C_*` field definitions through `I2C_SF`.
- `display/dc/dce/dce_aux.h` maps `DP_AUX0_AUX_CONTROL` fields through `AUX_SF`.
- `display/dc/dio/dcn10/dcn10_link_encoder.h` and later link encoder headers map AUX/HPD fields through `LE_SF`.
- `display/dc/dce/dce_stream_encoder.h` and DIO stream encoder headers map HDMI/AFMT/DIG fields through `SE_SF`.
- `display/dc/irq/dcn201/irq_service_dcn201.c` includes this DCN 2.0.1 shift/mask header for interrupt-related register definitions.

## State And Persistence Behavior

The macros are compile-time constants and store no software state. The state they describe lives in hardware registers:

- OTG state includes scanline/frame counters, vblank/hblank status, update-lock state, double-buffer pending bits, static screen state, CRC status/data, GSL sync gap status, and DRR last-used total.
- I2C and AUX state includes transaction in-progress/done bits, arbitration ownership, timeout/overflow/NACK/error status, reply byte counts, and hardware/firmware request state.
- HPD state includes current sense, delayed sense, RX interrupt status, connect/disconnect debounce counters, and interrupt acknowledgements.
- DIO power and clock fields describe persistent hardware gating or memory power choices until changed by driver power-management code or hardware.
- HDMI/AFMT/TMDS fields configure packet generation, metadata/audio payload bytes, double-buffer transfer, audio FIFO/CRC status, and TMDS encoding/test patterns.

Several fields are write-one-to-clear or acknowledgement style by naming convention, including interrupt `*_ACK`, `*_CLEAR`, `*_CLR`, and `*_TAKEN_CLR` fields. Incorrect writes can drop pending interrupts or clear evidence before higher layers observe it.

## Dependencies

This chunk depends on the wider AMD display register framework:

- Matching address definitions in the paired DCN 2.0.1 offset/header files provide register addresses. This file only provides field positions and masks.
- AMD DC register accessor macros expect the exact `REG__FIELD__SHIFT` and `REG__FIELD_MASK` names.
- Linux AMDGPU display code supplies MMIO access, IRQ service plumbing, DDC/AUX transaction state machines, link encoder setup, stream encoder setup, and power management policy.
- Hardware register semantics are defined by DCN 2.0.1 ASIC behavior; the header does not validate field values or sequence constraints.

## Integration Points

The chunk participates in these higher-level subsystems:

- Display timing and vblank handling through OTG status, frame counters, global sync, vertical interrupt, update-lock, and GSL fields.
- Atomic modeset/programming safety through OTG double-buffer, master update lock, VUPDATE keepout, global update lock, and HDMI/metadata double-buffer status fields.
- Connector discovery and EDID/DDC through DC I2C and HPD fields.
- DisplayPort sideband communication through DP AUX0/AUX1 fields, including DPCD/EDID access, link training support, HPD-disconnect detection, and low-speed AUX monitor status.
- HDMI and DP stream encoding through DIG0 HDMI packet controls, audio infoframes, generic packets, MPEG/ISRC payloads, ACR values, AFMT audio status, and TMDS encoder controls.
- Power management through DIO memory power, light-sleep, and clock-gating fields for I2C, DP, HDMI, AFMT, and DME blocks.

## Risks And Edge Cases

- Mask/shift drift from the real ASIC specification is high impact. A single incorrect bit can cause silent misprogramming of timing, interrupts, I2C/AUX transactions, HDMI packets, or power gating.
- The chunk is instance-specific in places. `OTG1`, `HPD0/1`, `DP_AUX0/1`, and `DIG0` names must match the address/header instance mapping used by the resource tables; cross-instance copy mistakes can compile but program the wrong block.
- Several status/control registers share fields for SW, DMCU/firmware, and hardware ownership. Bad arbitration masks around `DC_I2C_ARBITRATION` or `DP_AUX*_AUX_ARB_CONTROL` can race firmware or leave a bus permanently owned.
- Interrupt control fields include mask/type/status/ack/clear bits packed together. Read-modify-write helpers must avoid unintentionally setting clear/ack bits.
- Double-buffer and update-lock fields have ordering constraints that are not represented in the macros. Callers must still sequence locks, writes, pending waits, and unlocks correctly.
- Power gating and memory power force/dis fields can disable hardware needed by active links if used outside the proper power-management path.
- AUX/I2C status includes many error bits such as timeout, overflow, HPD disconnect, invalid stop/start/sync, partial byte, and NACK indicators. Tests that only check success paths may miss broken masks for recovery paths.
- Later ASIC headers have similar names with changed fields. Backporting or copying tables between DCN generations needs exact generation matching.

## Test Signals

Good validation signals for this chunk are mostly integration and hardware-oriented:

- Build coverage for DCN 2.0.1 display paths, ensuring all register table macro expansions compile with this header.
- Modeset and vblank tests that exercise OTG status, frame counters, vertical interrupts, update locks, global sync, and double-buffer pending bits.
- Display CRC tests that read `OTG1_OTG_CRC*` data and verify window/mask programming.
- EDID/DDC tests through I2C on both DDC channels, including timeout, NACK, overflow, and arbitration recovery cases.
- DisplayPort AUX/DPCD link-training tests across AUX0 and AUX1, including HPD disconnect and low-speed read status paths.
- Hotplug tests on HPD0 and HPD1 for connect/disconnect debounce, RX interrupt acknowledgement, polarity, and interrupt enable behavior.
- HDMI/DP stream encoder tests that verify infoframes, generic packets, audio packet enablement, ACR N/CTS values, AFMT channel status, and TMDS mode fields.
- Runtime power-management tests that toggle DIO clock/memory power fields and verify active links, audio, AUX, and HPD continue or resume correctly.
