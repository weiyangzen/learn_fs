# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 28641-31001

## Scope

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice. It covers lines 28641-31001 and defines 2,137 preprocessor constants: 1,069 `__SHIFT` macros and 1,068 `_MASK` macros. The one-count mismatch is a chunk-boundary artifact: the range starts in the middle of `DPCSSYS_CR1_LANE1_DIG_ANA_TX_TERM_CODE_CLK_OVRD_OUT`, after its register comment but before all of its shifts and masks.

The content is declarative hardware metadata. It has no C functions, structs, enums, runtime storage, branches, loops, locks, memory allocation, or direct MMIO operations. Its public surface is the macro namespace that AMDGPU display code uses together with matching DPCS offset headers and register helper macros.

## Purpose

The header provides symbolic bitfield locations for ASIC display PHY registers. Each hardware field is exported as a shift and mask so driver code can encode, decode, and preserve fields during register read-modify-write sequences without embedding raw bit constants.

This range covers the tail of CR1 lane 1 analog/digital analog PHY definitions, then a large portion of CR1 lane 2. The lane 2 area starts at ASIC override and ASIC input/output registers, continues through TX/RX power-state and calibration controls, RX CDR/adaptation/statistics blocks, MPHY controls, and ends in the middle of lane 2 digital analog RX controls.

## Important APIs, Types, And Macros

There are no callable APIs or local types. The effective API is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field.
- `<REGISTER>__<FIELD>_MASK`: field mask used for extraction, clearing, or insertion.

Important macro families in this chunk:

- `DPCSSYS_CR1_LANE1_DIG_ANA_*`: lane 1 digital-to-analog override/status fields for TX equalization, RX power/control/VCO, calibration DACs, AFE, scope, slicer, signal change clocks, term-code override, MPHY override, signal-detect override, and TX DCC DAC override.
- `DPCSSYS_CR1_LANE1_ANA_TX_*` and `DPCSSYS_CR1_LANE1_ANA_RX_*`: lane 1 analog register masks for TX power/measurement, alternative test bus, DCC DAC/control, termination code, override clocks, TX misc/reserved fields, RX clocks, CDR/deserializer, slicer control, RX power, squelch, calibration, analog test bus, and reserved RX fields.
- `DPCSSYS_CR1_LANE2_DIG_ASIC_*`: lane 2 PCS/ASIC boundary fields for lane override, TX/RX override inputs, ASIC inputs, ASIC outputs, RX EQ/VCO inputs, OCLA debug selection, and extra override registers.
- `DPCSSYS_CR1_LANE2_DIG_TX_PWRCTL_*`: lane 2 TX power-state tables for P0/P0S/P1/P2, TX power-up timing, DCC CR bank address/data access, DCC DAC control/range/selection/ack/address, TX clock alignment, and TX LBERT control.
- `DPCSSYS_CR1_LANE2_DIG_RX_PWRCTL_*`: lane 2 RX power-state tables for P0/P0S/P1/P2 and RX power-up timing.
- `DPCSSYS_CR1_LANE2_DIG_RX_VCOCAL_*`: RX VCO calibration control, timing, and status fields.
- `DPCSSYS_CR1_LANE2_DIG_RX_CDR_*` and `DPCSSYS_CR1_LANE2_DIG_RX_DPLL_*`: CDR control/status and DPLL frequency/bound registers.
- `DPCSSYS_CR1_LANE2_DIG_RX_ADPTCTL_*`: RX adaptation configuration, reset, ATT/VGA/CTLE/DFE status, slicer and DAC selection, DFE data/error offset, and CR bank address/data fields.
- `DPCSSYS_CR1_LANE2_DIG_RX_STAT_*`: programmable RX status pattern/match/statistics controls, sample count, counters, stop control, and calibration comparator clock controls.
- `DPCSSYS_CR1_LANE2_DIG_MPHY_*`: MPHY PWM, low-speed termination, and analog PWM clock-stable count fields.
- `DPCSSYS_CR1_LANE2_DIG_ANA_*`: lane 2 digital analog TX/RX override fields, including TX term code, TX EQ, RX control/power/VCO/calibration/DAC/AFE/scope/slicer/IQ controls. The chunk ends after `DPCSSYS_CR1_LANE2_DIG_ANA_RX_ANA_IQ_SENSE_EN`; subsequent lane 2 analog fields continue in the next chunk.

## Register Areas Covered

The lane 1 section is primarily analog-facing. It exposes TX equalization override legs and pre/post controls, RX control and power override enables, CDR VCO overrides, calibration mux/DAC controls, AFE attenuation/gain/CTLE, eye-scope controls, slicer controls, IQ phase/sense controls, signal-change update clocks, analog status, RX/TX termination override fields, MPHY override fields, signal-detect override fields, TX DCC DAC controls, TX power/measurement registers, test bus routing, TX/RX clock controls, CDR/deserializer controls, RX power and squelch settings, calibration settings, and analog test-bus measurement selectors.

The lane 2 ASIC interface section maps override values and hardware readbacks around the PCS/PHY boundary. It includes TX reset/request/rate/width/pstate/data-enable controls, RX reset/request/rate/width/pstate/adaptation controls, low-power detect, loopback, term-code and equalization settings, VCO/CDR references, DETRX and ACK readbacks, and OCLA observability.

The lane 2 power-control sections define per-state TX and RX analog/digital enables, resets, serial/clock/data enables, RX adaptation/DFE flags, RX fast-start behavior, and timing counters. Separate DCC bank and DAC fields indicate indexed calibration or tuning access inside the lane.

The lane 2 RX calibration/adaptation/statistics sections expose VCO calibration start/range/mode/status, CDR and DPLL tuning, adaptation configuration weights and thresholds, completed adaptation codes for ATT/VGA/CTLE/DFE taps, slicer level fields, DAC control selectors, CR bank access, programmable match/stat counters, and stop/sample controls. These are diagnostic and tuning surfaces around RX link training and equalization.

The final lane 2 analog section mirrors part of the lane 1 digital analog block, beginning with TX override and term-code fields and running through RX IQ sense enable. It is a continuation point for the next chunk, which should cover the remaining lane 2 analog signal-change and status definitions.

## Control Flow

This header has no local control flow. Runtime behavior is supplied by AMDGPU display code that includes this header, combines these masks with register offsets, and performs register reads, writes, updates, polling, or interrupt/statistic handling.

Typical runtime flow implied by the field names is:

1. Select the ASIC generation and include the matching DPCS 4.2.0 offset and shift/mask headers.
2. Use register helper macros to compose field values from `__SHIFT` and `_MASK` constants.
3. Program lane TX/RX power-state tables, reset state, data enable, pstate, rate, width, and DCC/VCO/CDR settings during link bring-up or resume.
4. Poll ACK, status, stable, VCO calibration, adaptation done, CDR/DPLL, and statistic fields while training or diagnosing a link.
5. Use override-enable bits only for controlled debug, calibration, or hardware sequencing paths, then return hardware-owned fields to normal control.

The header does not encode sequencing requirements. Consumers must follow the DPCS hardware specification for reset ordering, clock enabling, pstate transitions, term-code clocks, self-clearing update clocks, CDR/VCO tuning, DCC calibration, RX adaptation, LBERT operation, and status counter clearing/stopping.

## State And Persistence Behavior

No software state is stored here. The macros describe hardware register fields whose values live in ASIC register state.

- Override registers can hold software-forced TX/RX reset, request, pstate, rate, width, data enable, term-code, equalization, AFE, slicer, VCO, CDR, DCC, and MPHY values until reset, power-domain loss, or later writes.
- Status and ASIC output registers expose live or latched hardware observations such as ACKs, DETRX, CDR/VCO state, adaptation codes, calibration done bits, LBERT errors, statistic counters, and analog status fields.
- Power-state table fields persist the programmed behavior for P0/P0S/P1/P2 transitions and power-up timing, but this file does not define reset values or retention across suspend, GPU reset, or power gating.
- Self-clearing clock/update fields, clear/stop controls, and statistic counters require access semantics from the hardware spec; the mask header only describes bit positions.
- Reserved fields are named and masked so generated helpers can preserve or describe the full register layout. They should not be treated as general-purpose writable storage.

## Dependencies And Integration Points

The direct companion is the generated DPCS 4.2.0 offset header, expected to define matching `ixDPCSSYS_CR1_LANE*...` register addresses. This file is used through the C preprocessor and AMDGPU/DC register helper idioms that token-paste register and field names into shift/mask constants.

Integration points include:

- AMDGPU DRM display code under `drivers/gpu/drm/amd`, especially DC link encoder, PHY, link-training, power-management, and diagnostics code for DPCS 4.2.0 ASICs.
- DisplayPort, HDMI, USB-C/DP Alt Mode, and internal MPHY paths that need lane TX/RX reset, rate, width, pstate, data-enable, equalization, termination, and calibration controls.
- RX adaptation and link-training flows that consume ATT/VGA/CTLE/DFE, slicer, CDR, DPLL, VCO calibration, and signal-detect fields.
- Factory validation or debug flows that use LBERT, OCLA, analog test bus, scope, MPHY override, ATE-like overrides, and statistic counters.
- Generated sibling headers in DPCS/DCN trees. The same naming scheme appears in adjacent ASIC generations, so generation mismatch can compile if macro names overlap but still describe the wrong hardware layout.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask can compile cleanly while programming the wrong silicon bit.
- This chunk starts and ends mid-logical area. The previous chunk owns the beginning of lane 1 term-code clock override context, and the next chunk owns the rest of lane 2 digital analog RX definitions.
- The register surface mixes writable configuration, override enable bits, self-clearing clocks, read-only status, counters, stop/clear controls, and reserved fields. Treating all fields as ordinary writable configuration can leave overrides active, clear status unexpectedly, or corrupt reserved bits.
- Lane 1 and lane 2 blocks are structurally similar but not identical in this slice. Copying masks across lanes or assuming every lane has the same visible chunk coverage can hide generation or lane-index errors.
- Power-state, reset, clock, CDR/VCO, DCC, and adaptation fields are sequencing-sensitive. Updating them while the link is active can destabilize display output or break training.
- RX adaptation status values depend on analog behavior. Software-only checks cannot prove that masks match hardware semantics without hardware readback.
- Broad CR bank address/data and statistics controls can target internal indexed state. Consumers need value validation and must preserve bank/address sequencing.

## Test Signals

Useful validation signals for this chunk are mostly build-time, generated-header, and hardware-integration oriented:

- Compile/preprocess AMDGPU display code that includes `dpcs_4_2_0_sh_mask.h`; missing or renamed macros should fail in register helper users.
- Mechanical checks that complete register groups have paired `__SHIFT` and `_MASK` definitions. For this exact slice, expect 1,069 shifts and 1,068 masks because of the partial first register.
- Diff against the authoritative AMD DPCS 4.2.0 register database and the matching `dpcs_4_2_0_offset.h` to confirm register/field names, masks, and bit positions.
- Cross-generation comparison against nearby generated DPCS/DCN headers only where the IP block is expected to be compatible, with care not to substitute another generation's values.
- Runtime link validation on DPCS 4.2.0 hardware: DP/HDMI link training, lane-count/rate changes, hotplug, suspend/resume, GPU reset recovery, low-power transitions, and DP Alt Mode attach/detach when applicable.
- Register readback during PHY bring-up to confirm TX/RX reset, request/ACK, pstate, rate, width, data enable, term code, VCO calibration, CDR/DPLL lock/tuning, DCC calibration, RX adaptation status, and statistic counters move through expected values.
- Diagnostic validation for LBERT, OCLA, analog test bus, RX scope/slicer controls, MPHY PWM/termination controls, and RX statistic match/counter paths, including cleanup checks that override-enable bits are returned to normal.

## Chunk Notes For Merge

This document intentionally covers only lines 28641-31001 of `dpcs_4_2_0_sh_mask.h`. The final per-file report should merge this with adjacent chunks to describe the whole generated DPCS 4.2.0 register bitfield map. For reconciliation, note that this chunk begins inside lane 1 term-code clock override definitions and ends immediately before `DPCSSYS_CR1_LANE2_DIG_ANA_RX_ANA_CAL_DAC_CTRL_EN`.
