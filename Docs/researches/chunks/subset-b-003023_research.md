# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 43980-46344

## Scope And Purpose

This chunk is a generated shift/mask section for the AMD NBIO 6.1 DWC E12MP PHY X4 register map. It contains bit-field metadata for the `DWC_E12MP_PHY_X4_NS_X4_0` SerDes/PCIe PHY lane registers, not executable driver logic. The exported interface is a large set of C preprocessor constants named as `<register>__<field>__SHIFT` and `<register>__<field>_MASK`.

The range begins at the final mask from `LANE1_ANA_TX_PWR_OVRD`, then covers the remainder of lane 1 analog TX/RX fields, most of lane 2 digital and analog fields, and the beginning of lane 3 digital ASIC-facing fields. I counted 207 register comment blocks in the chunk, with 2,158 `#define` entries: 1,082 shift constants, 1,076 mask constants, and 326 reserved-field definitions. By lane, the chunk covers 23 lane 1 blocks, 165 lane 2 blocks, and 19 lane 3 blocks.

The purpose of these constants is to let AMDGPU NBIO, power-management, and virtualization code pack and extract register fields safely when programming PHY lane power state, TX/RX analog behavior, VCO/CDR calibration, equalization/adaptation, loopback/BERT, status sampling, and ASIC/analog override paths. The matching address constants live in `nbio_6_1_offset.h`; this file supplies the bit positions and masks for the corresponding register payloads.

## Register Families Covered

The lane 1 portion covers analog TX and RX controls. TX fields include alternate bus routing, ATB measurement selectors, VBOOST enable/reference override, termination code up/down overrides, IBOOST code override, loopback/MPLL/word-clock overrides, and miscellaneous oscillator or RX-detect reference controls. RX fields cover IQ skew and ATB scope selection, DCC and loopback clock overrides, analog power controls for ACJT/clock/LOS/AFE/CDR/DCC/scope/slicer blocks, CDR/AFE and VCO calibration selection, measurement muxes, RX termination control, slicer controls, and ATB/vreg measurement hooks.

The lane 2 digital block is the largest part of the slice. It defines ASIC override inputs and outputs for lane-level loopback, TX reset/invert/data/REQ/LPD/PSTATE/RATE/WIDTH/MPLLB/detect/disable controls, TX beacon/IBOOST/VBOOST/main/pre/post cursor fields, RX reset/invert/data/REQ/LPD/PSTATE/RATE/WIDTH/adaptation/clock-divider controls, RX CDR and LOS controls, RX reference/VCO load overrides, RX EQ override fields, acknowledgement/loss/adaptation status outputs, and matching ASIC input/output views. These blocks describe both override registers, where software can force values, and ASIC-side registers, where integrated logic supplies or receives the lane control/status signals.

The lane 2 power-control and calibration fields include TX and RX P-state definitions for P0, P0s, P1, and P2, TX/RX power-up timing fields, RX power-up control, VCO calibration control/time/status registers, CDR control/status registers, DPLL frequency bounds, RX align mask, loopback BERT controls and error count, RX adaptation configuration, equalizer status, DFE tap status, slicer/VDAC offset controls, and statistical match/count registers. The analog lane 2 tail mirrors the lane 1 analog pattern for TX/RX overrides, measurement muxes, termination, slicer, and ATB/vreg controls.

The lane 3 portion starts the same digital ASIC-facing pattern as lane 2. In this slice it includes lane loopback override, TX override and ASIC input/output fields, RX override input/output fields, RX EQ override fields, RX CDR/VCO ASIC input fields, and the first lane 3 TX P-state P0 power-control fields before the chunk boundary.

## APIs, Types, And Functions

There are no functions, structs, enums, or callable APIs in this chunk. The only public surface is preprocessor metadata for register fields. Each field normally has:

- A `__SHIFT` constant describing the low bit position.
- A `_MASK` constant describing the field bit mask in the register value.
- Optional `RESERVED_*` or `NC*` fields that document unused or not-connected bits in the generated register layout.

Important field groups include `RESET`, `INVERT`, `DATA_EN`, `REQ`, `ACK`, `LPD`, `PSTATE`, `RATE`, `WIDTH`, `DISABLE`, `MPLLB_SEL`, `DETECT_RX_REQ`, `DETRX_RESULT`, `VBOOST_EN`, `IBOOST_LVL`, `TX_MAIN_CURSOR`, `TX_PRE_CURSOR`, `TX_POST_CURSOR`, `CDR_TRACK_EN`, `CDR_SSC_EN`, `ALIGN_EN`, `LOS_THRSHLD`, `RX_TERM_EN`, `RX_REF_LD_VAL`, `RX_VCO_LD_VAL`, `EQ_*`, `DFE_*`, `ADAPT_*`, and many analog `ovrd_*`, `*_reg`, and `meas_atb_*` fields.

The constants are expected to be used with AMDGPU register helper patterns that mask, shift, and combine fields before writes or after reads. The source-level integration points that include the NBIO 6.1 register package include `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, and PowerPlay include aggregators such as `vega10_inc.h` and `vega12_inc.h`.

## Control Flow

This header has no runtime control flow. All decisions, ordering, polling, and error handling are in consuming driver code or firmware/hardware state machines.

The implied runtime flows are hardware sequencing flows. A PHY bring-up or link-training path may select lane P-states, set TX/RX power-control bits, release resets, enable clocks and data paths, request TX/RX operation, and then poll ACK/status bits. A calibration path may program RX VCO/CDR control fields, wait for calibration status, and then use `RX_REF_LD_VAL`, `RX_VCO_LD_VAL`, or CDR status fields. Equalization and adaptation paths can configure CTLE/VGA/DFE fields or inspect adaptation status and per-tap status. Diagnostic paths can use LBERT, statistics counters, ATB measurement selectors, loopback, and RX/TX override paths.

Because this is a field definition header, it does not express which fields are write-one-to-clear, read-only, sticky, self-clearing, privilege-gated, or sequencing-sensitive. Consumers must rely on the hardware programming guide, generated offsets/defaults, and existing ASIC driver flows for those semantics.

## State And Persistence Behavior

The file stores no software state. It describes hardware register state in the NBIO 6.1 PHY lane block. Any persistence is in the hardware registers themselves and typically lasts only until reset, power-gating, BACO, or firmware/driver reinitialization changes the lane.

The state represented by this chunk falls into several categories:

- Lane control state: reset, invert, request/ack, low-power detect, P-state, rate, width, disable, loopback, and detect-RX controls.
- TX analog/electrical state: IBOOST, VBOOST, termination up/down codes, main/pre/post cursor settings, beacon enable, clock/word-clock/MPLL enable, and TX power timing.
- RX analog/electrical state: LOS, DCC, AFE, CDR/VCO, termination, slicer controls, IQ phase/skew, CTLE/VGA/DFE equalizer fields, and adaptation enable/status.
- Calibration and measurement state: VCO calibration controls/status, CDR status, DPLL frequency bounds, ATB mux selection, VDAC offsets, and statistics/sample counters.
- Override state: many `ovrd_*` and `*_reg` pairs let software or test logic bypass normal ASIC/PHY state-machine outputs.

The matching `nbio_6_1_default.h` file provides reset/default values for many corresponding registers, while `nbio_6_1_offset.h` provides addresses. This chunk alone cannot say whether a register retains state across suspend, runtime power-gating, or GPU reset; that behavior is determined by the NBIO/PHY power domain and driver sequencing.

## Dependencies And Integration Points

This chunk depends on the rest of the generated NBIO 6.1 register package. The paired offset header maps the register names to MMIO or SMN addresses, the default header records generated reset values, and this shift/mask header maps bit fields within each register. Consumers also depend on AMDGPU/SOC15 register access helpers for address construction, reads, writes, field updates, and polling.

The main integration domain is the AMDGPU NBIO/PCIe PHY stack. These definitions sit below higher-level code for PCIe/NBIO initialization, link bring-up, lane power management, clock gating, reset handling, SR-IOV or virtualization support, and diagnostics. PowerPlay include files aggregate the same generated register headers for ASIC-specific power-management code. `mxgpu_ai.c` includes NBIO 6.1 masks for multi-GPU/SR-IOV paths, though this particular chunk is PHY-lane oriented rather than mailbox-oriented.

The register naming shows that fields are lane-indexed and largely replicated. Lane 2 has a full digital and analog set in this chunk, while lane 1 and lane 3 are partial because the chunk boundaries split the generated header. The merge lane should reconcile this document with adjacent chunks to describe the complete four-lane PHY field map.

## Risks And Edge Cases

The highest risk is treating generated masks as ordinary constants without preserving their exact register pairing. Many field names repeat across lanes and across override/ASIC views; using a lane 2 mask with a lane 1 or lane 3 offset may compile but program the wrong hardware lane or bit field.

Reserved and `NC*` fields should not be modified casually. Even when masks are generated for reserved fields, driver code should normally preserve read values or write documented defaults, because reserved bits can have undocumented silicon behavior.

Override registers are powerful and hazardous. Fields such as `ovrd_en`, `EQ_OVRD_EN`, power overrides, clock overrides, CDR/VCO overrides, loopback overrides, and analog measurement mux overrides can bypass normal PHY sequencing. Leaving an override asserted after diagnostics can break link training, power management, or recovery from reset.

Analog and PHY timing fields are sequencing-sensitive. TX/RX P-state fields, power-up timers, VCO calibration timers, DPLL bounds, and CDR controls can affect link stability. Small mask or shift errors here may appear as intermittent PCIe training failures, recovery timeouts, increased error counts, or suspend/resume regressions rather than straightforward build failures.

The chunk boundary itself is an edge case for research and maintenance. It starts in the middle of `LANE1_ANA_TX_PWR_OVRD` and ends in the middle of lane 3 TX power-control definitions. Any final per-file report should avoid treating this range as a complete logical register family.

## Test Signals

The header is primarily validated by compilation and hardware or simulator execution. Useful signals include:

- Successful builds of AMDGPU NBIO 6.1, PowerPlay, and SR-IOV code that includes `nbio_6_1_sh_mask.h`.
- Register-field write traces showing masks and shifts create expected values for lane control, TX cursor, RX equalization, CDR/VCO, P-state, and timing registers.
- PCIe link bring-up and retrain tests across the affected ASIC generation, including width/rate negotiation and recovery from reset.
- Runtime power-management, suspend/resume, BACO, and clock-gating tests that exercise lane P-state and TX/RX power-control fields without timeouts.
- Diagnostics or bring-up tests for loopback, LBERT error count, RX statistics counters, ATB measurement selectors, and analog mux fields.
- Equalization/adaptation validation that observes expected CTLE/VGA/DFE status values and stable link error counters after programming override or default paths.
- SR-IOV or multi-function smoke tests where NBIO 6.1 masks are included through virtualization paths, checking that unrelated PHY field changes do not perturb mailbox, doorbell, or PF/VF behavior.

Because this file is generated, source-level review should focus on consistency with `nbio_6_1_offset.h`, `nbio_6_1_default.h`, adjacent lane chunks, and the ASIC register-generation source. Runtime regressions usually surface as hardware initialization, link stability, or power-transition failures rather than unit-test failures.
