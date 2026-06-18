# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 31002-33365

## Scope And Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice. It exports C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for DPCSSYS CR1 lane, common, raw-lane PCS, and raw-lane FSM registers. It contains no executable C code, no structs, no runtime variables, no locking, and no direct MMIO operations.

The requested range contains 2,137 `#define` entries over 2,364 lines: 1,068 shift definitions and 1,069 mask definitions. It starts mid-register with the two mask definitions for `DPCSSYS_CR1_LANE2_DIG_ANA_RX_ANA_IQ_SENSE_EN`, because that register's shifts are just before line 31002. It ends mid-register after `DPCSSYS_CR1_RAWLANE0_DIG_FSM_FAST_SUP__FAST_SUP_MASK`; the matching reserved mask is on line 33366 and later `RAWLANE0_DIG_FSM_*` fast-state fields continue in the next chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. Its purpose is to let display driver register helpers encode and decode DPCS register fields without open-coded bit constants.

## Important APIs, Types, And Macros

There are no callable APIs or local C types. The macro namespace is the API:

- `DPCSSYS_CR1_*__FIELD__SHIFT` gives the least-significant bit position of a field in a DPCS indirect register.
- `DPCSSYS_CR1_*__FIELD_MASK` gives the field mask used to isolate or update that field.
- Register comments such as `//DPCSSYS_CR1_LANE3_DIG_TX_PWRCTL_TX_PSTATE_P0` group the following field constants by hardware register.

Major macro families in this slice:

- Tail of lane 2 analog controls: RX IQ sense/calibration clocks, AFE update, status readback, RX termination override, MPHY/signal-detect overrides, TX DCC DAC overrides, TX fast-start/loopback, analog TX measurement/power/ATB/DCC/termination/clock/misc fields, analog RX clock/CDR/slicer/power/squelch/calibration/ATB fields, and lane 2 reserved analog registers.
- Lane 3 digital ASIC interface controls: lane/TX/RX override input and output fields, lane state, TX pstate/rate/divider/MPLL selection, TX equalization and DCC calibration fields, RX detect and calibration status bits, and digital ASIC input/output mirrors.
- Lane 3 TX power-control and debug fields: TX `P0`, `P0S`, `P1`, `P2` power-state programming, power-up timing registers, DCC CR bank address/data, DCC DAC control/range/select/ack/address, TX clock alignment, LBERT controls, RX statistic match/mask/sample/count/stop registers, and calibration-comparison clock control.
- Lane 3 digital-to-analog and analog TX fields: TX term-code overrides, TX EQ override groups, analog status, DCC DAC override groups, fast-start and clock-loopback controls, analog TX measurement, power, ATB, DCC, term-code, clock, misc, and reserved fields.
- Raw common CR1 controls: common control, MPLLA/MPLLB override and bandwidth/SSC override inputs, lane FSM operation extension, MPLL state control, TX calibration code, SRAM init status, OCLA observability, supervisor analog override, PCS/FW ID codes, always-on RTUNE RX/TX pull-down/pull-up values for indexes 0 through 7, SRAM bitline config, power-gating override/status, supervisor override, VREF stats, reset override/status, reference-range override, and miscellaneous common configuration.
- Raw lane 0 PCS transfer fields: TX/RX PCS override inputs and outputs, pstate/rate/width/LPD/MPLL selection, TX and RX request/reset/data-enable/async/beacon/loopback controls, RX adaptation ACK and figure-of-merit, directed TX pre/main/post cursor requests, lane number, ATE override inputs, RX EQ override fields, TX/RX termination controls, RX valid/clock status, and RX phase-2 calibration handshakes.
- Opening raw lane 0 FSM fields: manual FSM override command/jump/break controls, memory-address monitor, status monitor, and fast flags for RX startup, RX adaptation, AFE/DFE/bypass/reference/IQ calibration, AFE/DFE adaptation, and supervisor fast support.

Reserved field masks are part of the generated layout description. They are not a signal that driver code should write reserved bits as programmable state.

## Control Flow

This header has no runtime control flow. The effective flow is supplied by AMD display code:

1. DCN 3.1 resource code includes `dpcs/dpcs_4_2_0_offset.h` and this matching `dpcs/dpcs_4_2_0_sh_mask.h`.
2. DPCS register-list and shift/mask-list macros, such as `DPCS_DCN31_REG_LIST(id)` and `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` / `DPCS_DCN31_MASK_SH_LIST(_MASK)`, token-paste register and field names into register tables.
3. AMD display register helpers use the paired offset, shift, and mask constants to build read, write, update, get, and poll operations.
4. Hardware side effects occur only at those call sites. This chunk only defines where fields live inside the DPCS 4.2.0 register map.

The macros do not encode sequencing rules. Consumers must still order power-state transitions, clock/MPLL programming, RX detection, TX/RX reset handshakes, lane training, calibration/adaptation, interrupt or status clearing, and firmware/shared-ownership transitions correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-backed state in DPCSSYS CR1 registers:

- Per-lane analog TX/RX state for termination, equalization, DCC, signal-detect, squelch, slicer, CDR/deserializer, calibration DACs, IQ phase/sense, clock enables, loopback, measurement, ATB routing, and power overrides.
- Lane 3 digital state for power-state definitions, lane state, pstate/rate/divider, MPLL selection, TX/RX request and reset signaling, RX detection, TX EQ/DCC controls, LBERT/debug controls, and RX statistic counters.
- Raw common state for shared MPLLA/MPLLB override values, spread-spectrum control, RTUNE calibration values, SRAM init and bitline configuration, common power-gating override/status, supervisor override, VREF stats, reset status, reference range, and firmware/PCS ID code readbacks.
- Raw lane 0 PCS state for TX/RX override values, PCS input/output mirrors, low-power detect, rate/width, pstate, data enable, async/beacon signaling, RX valid, loopback, RX adaptation/FOM, directed TX coefficient requests, termination controls, EQ overrides, ATE override values, and phase-2 calibration handshakes.
- Raw lane 0 FSM state for manual command override, current state/status monitoring, memory-address monitoring, and fast-calibration/adaptation control flags.

Persistence is hardware-defined. Configuration and override fields generally last until the hardware block is reprogrammed, power-gated, reset, or restored after suspend/resume. Status, ACK, monitor, statistic, and calibration fields can be volatile, latched, self-clearing, write-one-to-clear, or valid only while the relevant lane/common clock and power domains are active. This generated header does not classify those access semantics.

## Dependencies And Integration Points

The immediate generated-header dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h`, which provides matching `ixDPCSSYS_CR1_*` offsets. For this range, the companion offset header maps examples such as `ixDPCSSYS_CR1_LANE3_DIG_TX_PWRCTL_TX_PSTATE_P0` at `0x1320`, `ixDPCSSYS_CR1_RAWCMN_DIG_CMN_CTL` at `0x2000`, and `ixDPCSSYS_CR1_RAWLANE0_DIG_FSM_FAST_SUP` at `0x302c`.

The direct include site in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, which includes both DPCS 4.2.0 generated headers and initializes DCN 3.1 DPCS register, shift, and mask tables. The relevant table macros come from DC link-encoder headers such as `display/dc/dio/dcn31/dcn31_dio_link_encoder.h`.

Runtime integration is through AMDGPU Display Core link and PHY code. These fields sit below DisplayPort/HDMI link encoder setup, lane power management, clock and MPLL programming, link training, RX detection, calibration/adaptation, diagnostic/statistic readback, loopback/LBERT/OCLA use, suspend/resume restoration, and low-level hardware debugging.

## Risks And Edge Cases

- Generated metadata drift is the main risk. A wrong shift or mask can compile cleanly while programming the wrong hardware bit, truncating a field, corrupting an adjacent field, or clearing a reserved/status bit.
- The chunk is highly repetitive across lane 2, lane 3, raw common, and raw lane 0 namespaces. Copy-generation mistakes may affect only one lane, one pstate, or one override path and only show up under specific connector mappings or lane counts.
- Chunk boundaries are artificial. The range begins with masks whose shifts are in the previous chunk and ends before the reserved mask for `RAWLANE0_DIG_FSM_FAST_SUP`. Adjacent chunks are needed before making complete per-register or per-file claims.
- Override fields commonly use value/enable pairs. Enabling an override with a stale value can force unintended pstate, rate, MPLL, reset, loopback, data-enable, termination, EQ, calibration, or ATE behavior; setting only the value field may have no effect.
- Calibration and analog fields are sequencing-sensitive. Incorrect DCC, CDR, VCO, slicer, IQ, signal-detect, squelch, termination, or RTUNE masks can cause marginal link training, intermittent blanking, bad signal integrity, or resume-only failures.
- Status, ACK, statistic, monitor, and FSM fields are side-effect-sensitive. Treating readback or clear-style bits as ordinary read/write controls can hide failures, lose interrupts/status evidence, or make polling loops time out.
- Raw common MPLL and reference-control fields can affect shared clock resources rather than a single lane. Bad masks here can break multiple links or modes at once.
- Reserved masks exist for generated completeness. Read-modify-write users must preserve reserved fields unless hardware documentation explicitly says otherwise.

## Test Signals

Useful validation is mostly generated-header consistency plus display hardware behavior:

- Build AMDGPU Display Core with DCN 3.1 support. Missing or renamed DPCS 4.2.0 macros should fail where `dcn31_resource.c` populates register, shift, and mask tables.
- Mechanically verify field-pair consistency in lines 31002-33365, allowing the known boundary exceptions for `LANE2_DIG_ANA_RX_ANA_IQ_SENSE_EN` and `RAWLANE0_DIG_FSM_FAST_SUP`.
- Cross-check every complete register group in this chunk against `dpcs_4_2_0_offset.h` and AMD's generated DPCS 4.2.0 register database.
- Compare corresponding lane 2 and lane 3 analog/TX/RX groups, and compare raw lane 0 PCS/FSM layouts with neighboring generated DPCS/DCN versions where the IP layout is expected to match.
- Exercise DisplayPort and HDMI bring-up across link rates and lane counts, including hotplug, modeset, link retraining, suspend/resume, and GPU reset. Watch for link-training fallback, blank displays, unexpected lane pstate, clock/MPLL lock failures, or repeated retraining.
- Validate calibration and diagnostic paths with register dumps or PHY traces: RX statistic counters, LBERT/OCLA output, DCC status, RX adaptation ACK/FOM, PH2 calibration, FSM state/status, RTUNE values, SRAM init, and power-gating status should decode coherently.
- Stress override and ATE-only paths only in controlled lab or manufacturing-style tests, because these fields can bypass normal autonomous PHY sequencing.

## Cross-Chunk Notes

The previous chunk owns the shifts for `DPCSSYS_CR1_LANE2_DIG_ANA_RX_ANA_IQ_SENSE_EN`. The next chunk owns the reserved mask for `DPCSSYS_CR1_RAWLANE0_DIG_FSM_FAST_SUP` and continues later `RAWLANE0_DIG_FSM_*` fields such as fast TX common-mode/RX-detect and RX power-up/VCO timing. The final per-file research document should merge those boundaries and describe the whole `dpcs_4_2_0_sh_mask.h` file as generated DPCS 4.2.0 register metadata, not handwritten driver logic.
