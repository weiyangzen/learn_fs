# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 56404-58990

## Scope

This chunk is a generated AMD NBIO 6.1 shift/mask header segment for the DesignWare E12MP x4 PCIe PHY register namespace `DWC_E12MP_PHY_X4_NS_X4_0`. It contains C preprocessor constants only. There are no functions, structs, enums, variables, branches, loops, locks, allocations, reference counts, or direct MMIO accesses in this range.

The assigned range starts inside the tail of `DWC_E12MP_PHY_X4_NS_X4_0_LANEX_DIG_RX_DPLL_FREQ_BOUND_0`, continues through lane-X digital RX adaptation/statistics and analog TX/RX control masks, then covers a large sequence of raw common-memory table registers. It ends at `DWC_E12MP_PHY_X4_NS_X4_0_RAWCMNX_DIG_MEM_CMN4_B0_R9`; the next chunk continues `CMN4_B0_R10` and later raw-memory entries.

Although this file is under a local `ceph-client` source mirror, this path is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`nbio_6_1_sh_mask.h` supplies bit positions and masks for NBIO 6.1 registers. In this chunk, the constants describe fields in PCIe PHY lane-X digital receive adaptation, analog front-end/driver control, status collection, and raw PHY common-memory banks. Each meaningful field is represented by generated macro pairs:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for extracting or composing the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask for isolating, preserving, clearing, or setting the field.

Consumers pair these constants with register addresses from `nbio_6_1_offset.h` or `nbio_6_1_smn.h`, and with reset values from `nbio_6_1_default.h`. Runtime code normally applies the masks through AMDGPU register helpers and field helpers such as `RREG32`, `WREG32`, `RREG32_SOC15`, `WREG32_SOC15`, `REG_GET_FIELD`, `REG_SET_FIELD`, and `WREG32_FIELD15`, depending on the register aperture and call site.

## Important Macro Families

The opening lines finish `LANEX_DIG_RX_DPLL_FREQ_BOUND_0` and define `LANEX_DIG_RX_DPLL_FREQ_BOUND_1`. These fields expose DPLL frequency-bound enablement plus upper and lower frequency bounds. They are part of receive clock/data recovery guardrails and should be treated as link-stability-sensitive PHY tuning fields.

`LANEX_DIG_RX_ADPTCTL_ADPT_CFG_0` through `_9` define RX adaptation controller configuration. The fields include ASM1 loop timing (`N_TOP_ASM1`, `N_TGG_ASM1`, `N_WAIT_ASM1`), adaptation start, adaptation clock division, CTLE pole override value/enable, DFE tap analog disable, training pattern fields, CTLE/VGA/ATT/DFE/eye/TGG enable controls, CTLE/VGA/DFE thresholds, threshold offsets, adaptation update coefficients (`*_MU`), VGA saturation counters, attenuation thresholds, initial error values, and reserved high bits. These masks describe how firmware or driver code can start and constrain analog RX adaptation.

`LANEX_DIG_RX_ADPTCTL_RST_ADPT_CFG` and the following status registers expose reset controls and adaptation results. Reset bits cover attenuation, VGA, CTLE boost, CTLE pole, and DFE tap1 adaptation. Status registers report adapted attenuation, VGA, CTLE boost/pole, and DFE tap1 through tap5 codes, plus per-block `ASM1_DONE` indicators. These fields are useful for polling convergence and diagnosing failed or marginal link training.

The DFE offset, slicer, error, and bypass families define low-level analog sampling controls: even/odd high/low DFE data VDAC offsets, even/odd RX slicer controls, even/odd DFE error VDAC offsets, error slicer levels, and even/odd DFE bypass VDAC offsets. Most of these are 8-bit values with reserved upper bits, while slicer controls are narrow low-bit fields. Incorrect writes can shift slicer thresholds or DFE decision levels and degrade receiver margin.

`LANEX_DIG_RX_STAT_*` defines a programmable RX statistics/match block. It includes load values, a data mask, match controls, statistic-control registers, sample-count selection, statistic counters 0 through 6, calibration compare clock control, and additional match/stat controls. Fields cover match modes, polarity, mask selection, capture/sample controls, counter values, and clocking. These masks likely support PHY debug, calibration, and link-quality telemetry rather than core data path setup.

`LANEX_DIG_ANA_TX_*` describes digital-visible analog TX override outputs. The fields cover TX coefficient override outputs, power state controls, calibration and common/CM_EN outputs, serializer/deserializer selection, rate bits, enable flags, positive/negative data enables, common clock enables, termination up/down codes, EQ override outputs, VBOOST, and related reserved fields. This family is the bridge between digital configuration logic and physical TX driver/termination/equalization behavior.

`LANEX_DIG_ANA_RX_*` describes digital-visible analog RX control and status. It includes RX control overrides, RX power/VCO override outputs, RX calibration controls, DAC controls and override/select bits, AFE attenuation/VGA, CTLE, scope controls, slicer controls, IQ phase adjustment and sensing, calibration DAC enablement, signal-change enables, phase-adjust clock, and analog status words. These masks are central to receive analog front-end setup and diagnostics.

`LANEX_ANA_TX_*` and `LANEX_ANA_RX_*` expose non-`DIG_` analog lane registers. TX groups cover override measurement, power override, alternate bus controls, ATB1/ATB2, VBOOST, termination code up/down, IBOOST code, override clocking, and miscellaneous controls. RX groups cover ATB/IQ skew, DCC override, power controls, ATB regulator reference, CDR/AFE, second power control, miscellaneous override, calibration mux A/B, ATB measurements, termination, slicer controls, and ATB/VREG controls. These names indicate direct PHY analog tuning and measurement knobs.

The raw common-memory section starts at `RAWCMNX_DIG_MEM_CMN2_B0_R0` and runs through `CMN2_B7_R31`, `CMN3_B0_R0` through `CMN3_B7_R31`, and the beginning of `CMN4_B0_R0` through `CMN4_B0_R9`. Every register in this family has the same simple layout: `DATA__SHIFT` is `0x0` and `DATA_MASK` is `0xFFFFL`. These registers are opaque 16-bit data words in generated PHY common-memory banks, most likely consumed as table/configuration payloads rather than semantically named control fields.

## APIs, Types, And Functions

There are no C APIs, types, or functions in this chunk. The exported interface is the macro namespace for `DWC_E12MP_PHY_X4_NS_X4_0_*` fields.

Direct in-tree include points for `nbio_6_1_sh_mask.h` include `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, and Vega-era PowerPlay include aggregators such as `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h`. Those include sites do not imply every macro here is referenced directly; generated ASIC headers intentionally expose the complete register database for firmware tables, debug code, bring-up paths, and hardware-specific helpers.

## Control Flow

This header has no executable control flow. Runtime behavior occurs in including AMDGPU code:

1. Code selects a PHY/NBIO register address from the matching offset or SMN header.
2. It reads a register value through the AMDGPU register access layer, or prepares a write value for hardware programming.
3. It uses the `__SHIFT` and `_MASK` constants to extract fields, compose new fields, preserve unrelated fields, or compare status bits against expected state.
4. Hardware side effects occur only when the including code performs reads or writes; the macros themselves are inert compile-time constants.

For this range, likely runtime contexts are PCIe PHY bring-up, lane receiver adaptation, link training, equalization tuning, analog front-end calibration, debug/statistics capture, PHY table loading, suspend/resume restoration, and hardware characterization paths.

## State And Persistence Behavior

The header stores no software state and persists nothing. It describes bit layout for hardware state owned by the NBIO/PCIe PHY, platform firmware, AMDGPU initialization code, and possibly PHY microcode or table-loading flows.

Represented state includes DPLL frequency bounds, RX adaptation enable/start/timing/threshold/coefficient state, adaptation reset and convergence status, DFE tap results, slicer and VDAC offset values, RX statistics counters and match configuration, digital-to-analog TX/RX override outputs, analog TX/RX power/termination/equalization/calibration controls, analog status words, and opaque raw common-memory data words.

Some fields are static tuning values, some are software-programmed controls, and some are hardware-updated status/counter outputs. The masks do not encode reset defaults, access permissions, write-one-to-clear behavior, required ordering, polling timeouts, clock-domain crossing requirements, firmware ownership, or whether a value is safe to modify after link training. Those rules must come from the hardware programming sequence and companion default/offset data.

## Dependencies And Integration Points

The primary dependency is consistency with the generated NBIO 6.1 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h` and `nbio_6_1_smn.h` provide matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h` provides reset/default values for the same `DWC_E12MP_PHY_X4_NS_X4_0` register names.
- AMDGPU register helpers provide field extraction, read/modify/write, and SOC15/SMN access mechanics.

Integration is mainly with AMDGPU NBIO and PCIe PHY setup. `nbio_v6_1.c` includes the NBIO 6.1 mask/default/offset/SMN headers for ASIC-specific NBIO behavior. `mxgpu_ai.c` includes the same mask namespace for virtualization-era AI GPU handling. PowerPlay include bundles make these definitions available to Vega10/Vega12 power-management code, where PCIe link and PHY settings can interact with clock, power, and suspend/resume policy.

The raw common-memory macros also integrate with generated default values. Because the common-memory registers are semantically opaque `DATA` words, correctness depends heavily on matching offsets, defaults, bank/register order, and any table loader that expects the generated sequence to remain synchronized.

## Risks And Edge Cases

- Chunk boundaries are artificial. The first line is already inside `LANEX_DIG_RX_DPLL_FREQ_BOUND_0`, and the last line stops mid-way through the `RAWCMNX_DIG_MEM_CMN4_B0` bank.
- These are untyped preprocessor constants. A stale shift, wrong mask, or register-family typo can compile cleanly while programming a wrong PHY bitfield.
- PHY tuning fields are link-stability-sensitive. Incorrect DPLL bounds, CTLE/VGA/ATT/DFE enables, thresholds, update coefficients, slicer levels, VDAC offsets, termination, VBOOST, IBOOST, EQ, CDR/AFE, or power-control fields can cause link training failures, marginal signal integrity, intermittent PCIe errors, or power-state transition bugs.
- Adaptation status and statistics fields may be hardware-updated while software reads them. Consumers need appropriate polling, timeout, and stabilization behavior rather than assuming a single read is authoritative.
- Reserved masks are present throughout the generated layout. Read/modify/write sequences must preserve reserved bits unless the hardware programming guide explicitly requires otherwise.
- Several fields represent override outputs or override enables. Accidentally enabling overrides can bypass normal firmware/PHY adaptation behavior and make failures highly platform- or speed-dependent.
- Raw common-memory entries are all generic 16-bit `DATA` fields. Table order and address-bank pairing are the only visible structure in this header; off-by-one generation, missing entries, or pairing with the wrong default table can silently corrupt PHY initialization payloads.
- The `LANEX` naming suggests a lane-template or lane-X namespace. Consumers must pair these masks with matching lane/register offsets, not with another lane or PHY instance that merely has similar field names.
- The macros expose field width but not ownership. Some controls may be owned by firmware, PSP/SMU flows, or hardware state machines during link training; driver writes at the wrong time can race training or calibration.

## Test Signals

Useful validation is mostly generated-header consistency, build coverage, and hardware PHY/link testing:

- Build AMDGPU with NBIO 6.1, Vega10/Vega12, MxGPU, and relevant PCIe power-management options enabled. Missing or renamed macros should surface in include users or register helper call sites.
- Compare this chunk against regenerated `nbio_6_1_sh_mask.h`, `nbio_6_1_offset.h`, `nbio_6_1_smn.h`, and `nbio_6_1_default.h` to ensure register names, bank ordering, default values, and field widths remain synchronized.
- Static-check mask/shift pairs: each field mask should align with its shift and width, reserved masks should cover the documented unused bits, and the `RAWCMNX_DIG_MEM_*` entries should consistently expose only `DATA_MASK == 0xFFFFL`.
- On NBIO 6.1 hardware, exercise cold boot, warm reboot, suspend/resume, runtime power transitions, and PCIe link retraining while monitoring negotiated speed/width, AER counters, and link stability.
- Validate receiver adaptation by polling `ASM1_DONE` and adapted ATT/VGA/CTLE/DFE status fields during bring-up or debug flows, with timeout/error paths tested on marginal or forced-training scenarios.
- Run PCIe stress traffic across supported link speeds and power states to catch bad RX/TX equalization, DPLL, slicer, termination, or power-control definitions.
- Use platform PHY diagnostics, where available, to verify RX statistics counters, match controls, analog status fields, ATB measurement fields, and calibration-related registers report plausible values.
- For raw common-memory banks, compare loaded table data against expected firmware/register-database output and verify no bank/register sequence is skipped or shifted at the `CMN2`, `CMN3`, and `CMN4` boundaries.

## Chunk Notes

- Lines 56404-56412 finish DPLL frequency-bound masks and define the lower-bound register.
- Lines 56413-56642 cover RX adaptation controller configuration, resets, status, DFE/slicer offsets, and bypass/error-level controls.
- Lines 56643-56792 cover RX statistics, match, sample, counter, and calibration compare clock controls.
- Lines 56793-57057 cover digital analog TX/RX override, calibration, AFE/CTLE/slicer/scope, IQ, DAC, and status masks.
- Lines 57058-57424 cover analog lane TX/RX power, ATB, termination, boost, calibration, CDR/AFE, slicer, and VREG masks.
- Lines 57425-58190 cover `RAWCMNX_DIG_MEM_CMN2_B0_R0` through `CMN2_B7_R31`, all with 16-bit `DATA` fields.
- Lines 58193-58958 cover `RAWCMNX_DIG_MEM_CMN3_B0_R0` through `CMN3_B7_R31`, all with 16-bit `DATA` fields.
- Lines 58961-58990 begin `RAWCMNX_DIG_MEM_CMN4_B0_R0` through `CMN4_B0_R9`; the rest of `CMN4_B0` continues after this chunk.
