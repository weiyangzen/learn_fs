# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 108927-111293

## Scope

This chunk is a generated AMDGPU NBIO 6.1 shift/mask header segment. It contains 2,155 `#define` field-layout macros across 2,367 source lines. There are no C functions, structs, enums, global variables, allocations, locks, or executable statements in this range.

The range covers part of the `DWC_E12MP_PHY_X4_NS_X4_3` PCIe PHY register namespace. It starts inside `SUP_ANA_MPLLA_ATB1`, continues through shared supervisor analog PLL/RTUNE measurement fields, then covers the beginning and most of lane 0 digital and analog PHY controls. It ends inside the lane 1 TX power-state register family at `LANE1_DIG_TX_PWRCTL_TX_PSTATE_P0S`, so both the opening and closing boundaries are artificial chunk splits rather than semantic source boundaries.

## Purpose

`nbio_6_1_sh_mask.h` is the generated bitfield definition half of AMD's NBIO 6.1 register interface. For each hardware register field it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position of the field.
- `<REGISTER>__<FIELD>_MASK`, the field mask used to isolate or update those bits.

Consumers combine these macros with matching offsets from `nbio_6_1_offset.h`, default/reset values from `nbio_6_1_default.h`, and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, and SOC15/NBIO SMN access helpers. This chunk describes low-level PCIe PHY state for PLL analog test bus selection, RTUNE, lane override/ASIC handoff, TX/RX power sequencing, VCO/CDR calibration, RX adaptation, statistics, and lane analog controls.

Although the repository mirror is under a Ceph client source tree, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

## Important Macro Families

The shared supervisor analog portion covers the tail of `SUP_ANA_MPLLA_ATB1`, then complete or near-complete groups for:

- `SUP_ANA_MPLLA_ATB2` and `SUP_ANA_MPLLA_ATB3`: measurement and override selection for MPLLA regulator, voltage pump, gain detector, fine control, magnitude control/reference, and analog test bus selection.
- `SUP_ANA_MPLLB_MISC`, `SUP_ANA_MPLLB_OVRD`, and `SUP_ANA_MPLLB_ATB1` through `ATB3`: MPLLB low-power/regulator miscellaneous bits, enable/calibration/feedback-clock/reset overrides, and analog measurement selection fields mirroring the MPLLA test-bus pattern.
- `SUP_ANA_RTUNE_CTRL`, `SUP_ANA_SWITCH_PWR_MEAS`, `SUP_ANA_SWITCH_MISC_MEAS`, and `SUP_ANA_BG`: resistor-tuning analog test-bus routing, power and miscellaneous measurement switches, temperature/reference selection, bandgap enablement, and associated reserved fields.
- `SUP_DIG_RTUNE_*`: digital RTUNE configuration/status and programmed/statistical RX, TX-down, and TX-up values.

The lane 0 digital ASIC interface portion defines:

- `LANE0_DIG_ASIC_LANE_OVRD_IN` and `LANE0_DIG_ASIC_LANE_ASIC_IN`: lane serial/parallel loopback controls and override enablement.
- `LANE0_DIG_ASIC_TX_OVRD_IN_*`, `TX_ASIC_IN_*`, and `TX_ASIC_OUT`: TX reset, invert, data enable, request, low-power disable, pstate, rate, width, MPLLB select, receiver-detect request, disable, beacon, iboost, vboost, main/pre/post cursor, acknowledgement, and receiver-detect result fields.
- `LANE0_DIG_ASIC_RX_OVRD_IN_*`, `RX_ASIC_IN_*`, and `RX_ASIC_OUT_0`: RX reset, invert, data enable, request, low-power disable, pstate, rate, width, clock and adaptation enables, CDR tracking/SSC, alignment, clock shift, disable, loss-of-signal threshold/filter, termination, acknowledge, LOS, valid, and adaptation-status fields.
- `LANE0_DIG_ASIC_RX_OVRD_EQ_IN_*` and `RX_EQ_ASIC_IN_*`: equalizer attenuation, VGA gain, CTLE boost/pole, DFE tap 1 through 5, and override enable fields.
- `LANE0_DIG_ASIC_RX_CDR_VCO_ASIC_IN_*`: RX CDR/VCO low-frequency, reference load, and VCO load values.

The lane 0 power, calibration, adaptation, and status portion defines:

- `LANE0_DIG_TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, and `P2`: per-TX-power-state enables for analog reference generator, VCM hold, clocks, reset, serializer, digital clock, data, and RX detect allowance.
- `LANE0_DIG_TX_PWRCTL_TX_PWRUP_TIME_*`: TX reference generator, clock, VCM hold, vboost disable, RX detect, reset, serializer timing, fast RX detect, FIFO bypass, and debug/test-bus selection.
- `LANE0_DIG_TX_LBERT_CTL`, `RX_LBERT_CTL`, and `RX_LBERT_ERR`: loopback bit-error-rate test mode, pattern, injected error, enable, sync, and error counters.
- `LANE0_DIG_RX_PWRCTL_RX_PSTATE_P0`, `P0S`, `P1`, and `P2`: per-RX-power-state enables for LOS, AFE, clock regulators, div16p5 clock, CDR/DCC/deserializer, VCO reset/calibration/continuous calibration, and digital clock.
- `LANE0_DIG_RX_PWRCTL_RX_PWRUP_TIME_*` and `RX_PWRUP_CTL_0`: RX startup timing, lock/signature count, fast/no wait controls, IDAC calibration hold, and clock-lane enable.
- `LANE0_DIG_RX_VCOCAL_*`: RX VCO calibration control, timing, load monitor, frequency monitor, control monitor, state, done, lock, retry, count, and calibration result fields.
- `LANE0_DIG_RX_CDR_CDR_CTL_*`, `RX_CDR_STAT`, `RX_DPLL_FREQ`, and `RX_DPLL_FREQ_BOUND_*`: CDR proportional/frequency gain, SSC counters, override values, observed gain state, DPLL frequency, and upper/lower frequency bounds.
- `LANE0_DIG_RX_ADPTCTL_*`: adaptation configuration, timing, CTLE/VGA/ATT/DFE enables, thresholds, step sizes, start/reset controls, status fields for ATT/VGA/CTLE/DFE taps, slicer controls, error/bypass VDAC offsets, and initialization error values.
- `LANE0_DIG_RX_STAT_*`: load values, data masks, match controls, statistic controls, sample count, statistic counters, and calibration-comparator clock control.

The lane 0 digital-to-analog and analog portions define:

- `LANE0_DIG_ANA_TX_*`: TX override outputs, termination code override outputs, EQ override outputs, TX pre/main/post cursor override routing, TX term-up/term-down, iboost/vboost, clock override, and TX miscellaneous fields.
- `LANE0_DIG_ANA_RX_*`: RX control/power/VCO override outputs, RX calibration, DAC controls, AFE attenuation/VGA, CTLE, scope, slicer, IQ phase adjust/sense, calibration DAC enable, analog signal-change gating, phase-adjust clocks, and analog status.
- `LANE0_ANA_TX_*` and `LANE0_ANA_RX_*`: analog measurement/override fields for TX power, alternate bus, ATB routing, vboost, termination, iboost, clock, miscellaneous controls, RX DCC, power control, CDR/AFE, calibration muxes, ATB measurement, termination, slicer control, and voltage-regulator measurement.

The lane 1 portion begins the same repeated pattern for `LANE1_DIG_ASIC_*`, including lane override, TX/RX override and ASIC input/output, RX equalization, RX CDR/VCO, and the start of TX power-control pstate fields. Its closing `LANE1_DIG_TX_PWRCTL_TX_PSTATE_P0S` group is truncated by the chunk boundary.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the preprocessor macro namespace. The macros are untyped integer literals, generally with an `L` suffix on masks. They encode only bit positions and masks.

These definitions do not encode register offsets, reset values, access size, read/write permission, side effects, latch semantics, polling requirements, firmware ownership, or sequencing constraints. Those meanings come from sibling generated headers, AMD's hardware register database, and the driver code that performs the actual NBIO/SMN/MMIO accesses.

## Control Flow

This header has no local control flow. Runtime control flow is external and typically follows this pattern:

1. AMDGPU NBIO, PCIe, power-management, reset, virtualization, or diagnostic code selects a register offset from `nbio_6_1_offset.h`.
2. It reads or composes a register value through AMDGPU register access helpers.
3. It uses this header's `*_MASK` and `*__SHIFT` constants to extract fields, preserve unrelated bits, or insert new field values.
4. The resulting hardware access participates in PHY initialization, link training, TX/RX power-state transitions, PLL/RTUNE setup, VCO/CDR calibration, RX adaptation, loopback/BERT diagnostics, statistics collection, reset handling, or debug dumps.

The meaningful control sequencing is therefore in call sites and hardware state machines, not in this header. Fields such as override enable, reset, request, calibration start, pstate, clock enable, RX adaptation enable, interrupt/status-style counters, and loopback controls are inputs to hardware-managed state machines and require correct ordering and timeout handling by users.

## State And Persistence Behavior

The header stores no software state. It names hardware state held in NBIO 6.1 PCIe PHY registers. Persistence depends on the GPU reset domain, PCIe link reset, PHY reset, suspend/resume save-restore behavior, SMU/firmware initialization, SR-IOV PF/VF ownership, and explicit driver writes.

Represented state includes shared PLL test-bus selection, MPLLB override and calibration controls, RTUNE configured and measured values, lane loopback controls, TX/RX override handshakes, power-state enable maps, startup timing, BERT mode/counters, VCO and CDR calibration status, DPLL bounds, RX equalization/adaptation configuration and results, statistic/match counters, analog override outputs, analog calibration selections, TX/RX termination and boost settings, slicer and phase-adjust controls, and lane analog measurement routes.

Several fields represent active hardware controls rather than passive storage. Reset, pstate, clock, request, override, calibration, RTUNE, BERT, CDR, adaptation, and analog power fields can change live PHY behavior. Call sites must avoid writing stale reserved bits, must preserve unrelated fields during read-modify-write, and must respect the hardware's ownership and sequencing rules.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 6.1 register data and must remain synchronized with companion headers:

- `nbio_6_1_offset.h` for register addresses corresponding to these `DWC_E12MP_PHY_X4_NS_X4_3_*` names.
- `nbio_6_1_default.h` for reset/default values where provided.
- AMDGPU register helper macros for field extraction and insertion.

Direct users of this generated header family in the mirrored tree include AMDGPU NBIO and virtualization/power-management code such as `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, and Vega include bundles under `drivers/gpu/drm/amd/pm/powerplay/hwmgr/`. Integration points include PCIe PHY bring-up, link training, reset, suspend/resume, SR-IOV/mxGPU handling, diagnostics, and low-level power/clock management.

The repeated `LANE0`/`LANE1` families are part of the same x4 PHY instance as surrounding chunks, so whole-file research needs adjacent chunks to complete the preceding `SUP_ANA_MPLLA_ATB1` and following lane 1 power-control and later lane families.

## Risks And Edge Cases

- Generated mask/shift drift can compile successfully while programming the wrong hardware bit. This is high risk for reset, PLL, RTUNE, CDR/VCO calibration, pstate, clock, adaptation, analog power, and override fields.
- The chunk starts and ends mid-family. The previous chunk is needed for the beginning of `SUP_ANA_MPLLA_ATB1`, and the next chunk is needed for the rest of `LANE1_DIG_TX_PWRCTL_TX_PSTATE_P0S` and later lane 1 definitions.
- Lane 0 and lane 1 blocks are intentionally repetitive. A lane-specific generated typo may affect only one physical lane, making failures appear as degraded link width, intermittent equalization failures, or lane-local diagnostics mismatches.
- Override fields can bypass normal hardware or firmware sequencing. Incorrect use can hold a lane in reset, force bad TX/RX parameters, disable adaptation, conflict with SMU ownership, or leave handshakes stuck.
- PLL, RTUNE, bandgap, and analog measurement controls affect shared or sensitive analog resources. Bad masks or writes can destabilize all lanes in the x4 PHY instance.
- Adaptation, VCO/CDR, and statistic status fields are meaningful only in the correct link and power state. Decoding them without checking done/valid/lock bits can produce misleading diagnostics.
- Reserved masks are useful for preserving register shape, but driver code should not intentionally set reserved bits unless the hardware programming guide requires preserving readback values.

## Test Signals

- Build AMDGPU with NBIO 6.1 support enabled; direct macro users should catch missing, renamed, or malformed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO 6.1 register database: shift/mask width, non-overlap within registers, reserved coverage, and matching offset/default entries.
- Compare repeated `LANE0` and `LANE1` register shapes in this chunk, and compare them with adjacent lane chunks, allowing only intentional hardware asymmetries.
- Runtime validation on NBIO 6.1/Vega-class GPUs should show stable PCIe link bring-up, negotiated width/speed, clean reset and suspend/resume, and no unexpected link flapping.
- PHY diagnostics should decode TX/RX pstate enables, VCO/CDR calibration status, DPLL bounds, RX adaptation results, statistic counters, RTUNE values, BERT state, and analog override/measurement routes consistently.
- Stress tests should include GPU reset, suspend/resume, SR-IOV PF/VF ownership paths, PCIe retraining, low-power transitions, and diagnostic register dumps to catch stale masks or incorrect field preservation.
