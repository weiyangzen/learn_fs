# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h lines 5830-8638

## Scope

This chunk is part of a generated AMD NBIO 6.1 default-value header. It contains C preprocessor `#define` constants only; there are no functions, structs, variables, branches, loops, locks, allocations, or direct register accesses in this range.

The assigned slice starts in the middle of the `smnDWC_E12MP_PHY_X4_NS_X4_0_LANE3` register-default block, immediately after lane 3 RX override input defaults have already begun. It then covers the rest of lane 3 PHY defaults, common raw PHY memory table defaults, raw per-lane always-on defaults for lanes 0-3, shared `SUPX` PLL/support defaults, generic `LANEX` defaults, and the start of `RAWCMNX` common memory defaults. It ends in the middle of `RAWCMNX_DIG_MEM_CMN4_B6`; later `RAWCMNX` rows are outside this work item.

Although the path is under a local `ceph-client` source mirror, this file is AMDGPU hardware register metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this chunk is to publish hardware reset or generator-provided default values for NBIO 6.1 PCIe/PHY SMN registers associated with a Synopsys DWC E12MP x4 PHY instance (`DWC_E12MP_PHY_X4_NS_X4_0`). Runtime AMDGPU code can use these constants as known baseline values, comparison values, or generated metadata alongside the matching offset and shift/mask headers.

Each macro follows the generated naming pattern:

- `smnDWC_E12MP_PHY_X4_NS_X4_0_<REGISTER_OR_TABLE_ENTRY>_DEFAULT`
- a literal 32-bit hexadecimal value such as `0x000003e8`, `0x00000000`, or table-programming values under `RAWCMN` and `RAWCMNX`.

The paired register-address and field-layout metadata live in `nbio_6_1_offset.h`, `nbio_6_1_sh_mask.h`, and `nbio_6_1_smn.h`. The principal in-tree include users are `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c` and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h`.

## Important Macro Families

The opening `LANE3` section completes the lane 3 digital ASIC, TX, RX, and analog default block. It includes TX/RX override inputs and outputs, TX power-state and power-up timing defaults, RX power-state and power-up timing defaults, RX VCO calibration control/time/status defaults, RX alignment masks, LBERT control/error defaults, CDR control/status defaults, DPLL frequency/bounds defaults, RX adaptation configuration/status defaults, DFE and slicer DAC offset defaults, RX statistics comparator/counter defaults, digital-to-analog override outputs, analog RX DAC/AFE/scope/slicer/IQ defaults, and lane-level analog TX/RX override, ATB, termination, boost, calibration, and measurement defaults.

The `RAWCMN_DIG_MEM_CMN2` through `RAWCMN_DIG_MEM_CMN6` sections dominate the middle of the chunk. These are common PHY memory table defaults arranged as bank/row macros (`B<n>_R<n>`). The values are opaque generated programming entries rather than self-describing bitfields in this header. They likely seed firmware or hardware micro-table state for common PHY calibration, equalization, PLL, sequencer, or initialization behavior.

The `RAWLANE0` through `RAWLANE3` groups define per-lane raw always-on digital defaults. The covered fields include RX adaptation IQ/FOM/phase-adjust state, adaptation tap/status registers, slicer controls, DCC calibration code defaults, loss-of-signal mask and signal-detect filter/calibration defaults, override outputs, VREF generator defaults, and signal-detect configuration. Most values are zeroed status or disabled override defaults, with a few repeated nonzero calibration/control seeds.

The `SUPX` group contains support/common PLL and clocking defaults such as `MPLLA_*`, clock control, transmit clock, RX PPM control, power-down, spread-spectrum clocking, and ASIC input/output defaults. These constants sit between raw lane-specific data and generic lane templates, reflecting shared PHY support logic rather than one physical lane.

The `LANEX` group provides generic lane-template defaults similar to the earlier concrete `LANE3` block. It covers ASIC override inputs/outputs, TX/RX power-state and timing defaults, RX VCO calibration, CDR, DPLL, adaptation, DFE/slicer, statistics, digital analog overrides, and analog TX/RX defaults. The `LANEX` template can be used by generated consumers or documentation to describe defaults common to all lanes, while concrete `LANE0`-`LANE3` blocks describe lane-specific register names.

The final `RAWCMNX_DIG_MEM_CMN2` through partial `RAWCMNX_DIG_MEM_CMN4` section mirrors the common raw memory-table pattern for an `X` common instance. This chunk includes complete `RAWCMNX` CMN2 and CMN3 blocks and runs through `RAWCMNX_DIG_MEM_CMN4_B6_R8_DEFAULT`; the remaining CMN4 and later entries continue after line 8638.

## Control Flow

There is no executable control flow in this header chunk. Runtime behavior is indirect:

1. AMDGPU NBIO or power-management code includes this header together with the matching offset, shift/mask, and SMN headers.
2. Code selects an NBIO/PCIe/PHY register address from generated address metadata.
3. Register helpers such as `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, and `REG_GET_FIELD` read, compare, compose, or write values.
4. Default constants from this file may be used as reset baselines, generator cross-checks, or initialization reference values for PHY and NBIO paths.

The active NBIO 6.1 implementation in `nbio_v6_1.c` programs memory-controller access, doorbell apertures and ranges, interrupt control, clock gating, light sleep, LTR/ASPM-related registers, and PCIe-facing state. This chunk does not itself perform those operations; it supplies generated constants that must remain consistent with the register database used by those operations.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. The values describe hardware-backed state in the GPU NBIO/PCIe PHY block. Real state lives in device registers, hardware sequencers, firmware-programmed PHY tables, Linux PCIe policy, and AMDGPU driver state.

The represented hardware state includes lane 3 TX/RX override and calibration settings, TX and RX low-power state timings, RX CDR/DPLL/adaptation state, DFE and slicer offsets, RX statistics counters and match controls, analog TX/RX overrides and measurements, common PHY raw memory tables, raw per-lane always-on adaptation/signal-detect defaults for lanes 0-3, common PLL/support defaults, and generic all-lane template defaults.

Many macros have `0x00000000` defaults, indicating disabled overrides, reset status values, or unprogrammed counters. Nonzero defaults are concentrated in power-state timing, calibration, DPLL/CDR, adaptation, slicer/DFE offsets, termination, and raw common memory table entries. The header does not encode access permissions, write-one-to-clear semantics, sequencing requirements, polling delays, firmware ownership, or whether a default is a true silicon reset value versus a generated initialization expectation.

## Dependencies And Integration Points

The primary dependencies are the other generated NBIO 6.1 headers:

- `nbio_6_1_offset.h` for register offsets.
- `nbio_6_1_sh_mask.h` for field shifts and masks.
- `nbio_6_1_smn.h` for SMN-addressed register definitions.

Direct include integration appears in `amdgpu/nbio_v6_1.c`, where NBIO 6.1 runtime logic uses generated register metadata for device initialization, doorbells, interrupt routing, clock gating, memory access enablement, and PCIe policy. `pm/powerplay/hwmgr/vega10_inc.h` also includes the NBIO 6.1 default, offset, and shift/mask headers alongside THM, MP, and GC register metadata for Vega10-era power-management code.

Hardware integration points include PCIe link bring-up and retraining, PHY calibration, TX/RX power transitions, ASPM/LTR and light-sleep behavior, clock gating, suspend/resume, reset, interrupt routing, doorbell aperture setup, signal-detect behavior, and diagnostics that inspect RX adaptation, CDR, DPLL, LBERT, or lane statistics.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts after lane 3 defaults have already begun and ends before the `RAWCMNX` common memory table is complete.
- These are untyped preprocessor constants. Wrong values, stale generated output, or macro-name drift can compile cleanly while changing hardware programming semantics.
- The `RAWCMN` and `RAWCMNX` memory-table entries are opaque in this header. Reviewers cannot infer bit ownership or side effects from the macro names alone, so validation must compare against the authoritative register-generation source or hardware documentation.
- Lane-specific and generic lane-template sections are highly repetitive. Copy/generation errors can swap `LANE3`, `LANEX`, or `RAWLANE<n>` data without producing compile errors.
- PHY defaults are signal-integrity sensitive. Incorrect CDR, DPLL, VCO calibration, RX adaptation, DFE, slicer, TX termination, TX boost, or power timing defaults can produce intermittent link training failures, width/speed downgrades, AER noise, suspend/resume failures, or platform-specific instability.
- Some status-looking defaults are zeroed counters or hardware-updated registers. Treating them as writable initialization values in runtime code could clear useful diagnostic state or fight hardware ownership.
- Common PLL/support defaults affect all lanes. A single bad `SUPX`, `RAWCMN`, or `RAWCMNX` entry may surface as multi-lane link failure rather than a localized lane issue.
- This source path lives under a Ceph mirror, but the content is GPU hardware metadata. Cross-subsystem tooling must avoid classifying this chunk as filesystem logic.

## Test Signals

Useful validation is mostly build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 6.1/Vega10 support enabled; missing or renamed generated macros should surface through `nbio_v6_1.c`, `vega10_inc.h`, or transitive generated-header includes.
- Compare the macro names and ordering against `nbio_6_1_offset.h`, `nbio_6_1_sh_mask.h`, and `nbio_6_1_smn.h` to ensure each default value still aligns with the intended register name and SMN address.
- Diff this generated header against the authoritative AMD register database or a known-good kernel import when refreshing hardware metadata.
- Boot affected Vega10/NBIO 6.1 hardware and verify PCIe link width/speed, retraining, ASPM/LTR behavior, clock gating, light sleep, suspend/resume, and reset paths.
- Exercise high-bandwidth PCIe DMA and interrupt-heavy workloads to expose marginal PHY settings, lost interrupts from related NBIO setup, or link instability.
- Monitor `lspci -vv`, kernel PCIe/AER logs, AMDGPU debug output, and platform error counters for receiver errors, replay timeouts, link downtraining, equalization failures, or unexpected correctable/uncorrectable errors.
- Use available PHY diagnostics, LBERT hooks, lane statistics, or vendor debug tooling to inspect CDR/DPLL lock, RX adaptation convergence, signal detect, DFE/slicer behavior, and per-lane error rates.

## Chunk Notes

- Lines 5830-5987 complete concrete `LANE3` PHY defaults.
- Lines 5988-7278 cover `RAWCMN_DIG_MEM_CMN2` through `RAWCMN_DIG_MEM_CMN6` bank/row table defaults.
- Lines 7279-7705 cover raw always-on per-lane defaults for `RAWLANE0` through `RAWLANE3`.
- Lines 7706-7778 cover `SUPX` shared PLL/support defaults.
- Lines 7779-7952 cover generic `LANEX` lane-template defaults.
- Lines 7953-8638 cover `RAWCMNX_DIG_MEM_CMN2`, `RAWCMNX_DIG_MEM_CMN3`, and the beginning of `RAWCMNX_DIG_MEM_CMN4`.
