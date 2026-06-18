# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h lines 14270-17079

## Scope

This chunk is a generated AMD NBIO 6.1 default-register header segment. It contains only C preprocessor `#define` constants with reset/default values; there are no functions, structs, variables, allocation paths, locks, loops, branches, or direct register accesses in this range.

The whole assigned range is under the `smnDWC_E12MP_PHY_X4_NS_X4_2_*` namespace, describing default values for a Synopsys DWC E12MP x4 PCIe PHY instance. It starts in the tail of the concrete `LANE3` receive/stat and analog-default block, continues through large common PHY microcode/memory default tables, repeated raw per-lane PHY defaults for lanes 0 through 3, aggregate `SUPX`/`LANEX` defaults, and ends in the first eight entries of the `RAWCMNX_DIG_MEM_CMN5` table.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header range is to publish power-on or expected reset values for NBIO 6.1 PCIe PHY registers. Each macro follows the generated form:

- `smnDWC_E12MP_PHY_X4_NS_X4_2_<REGISTER_OR_TABLE_ENTRY>_DEFAULT`, the default value associated with one NBIO 6.1 SMN PHY register or generated table entry.

Runtime AMDGPU code can pair these constants with addresses from `nbio_6_1_offset.h` and bit definitions from `nbio_6_1_sh_mask.h` when validating hardware state, initializing register tables, comparing against defaults, or carrying generated register metadata through ASIC-specific include headers.

## Important Macro Families

The opening `LANE3` fragment covers the end of the physical lane 3 block. It includes receive-stat defaults such as match controls, statistic controls, sample/count registers, and calibration comparator clock control. It then covers digital-to-analog override outputs for TX termination/equalization and RX control/power/VCO/DAC/slicer/phase controls, followed by lane-level analog TX and RX defaults for measurement, power override, ATB paths, TX termination code, RX CDR/AFE, calibration muxes, termination, slicer, and VREG state.

The `RAWCMN_DIG_MEM_CMN2` through `RAWCMN_DIG_MEM_CMN6` families are dense generated memory-table defaults. `CMN2`, `CMN3`, `CMN4`, and `CMN5` each contribute 256 entries arranged as bank/register names `B<n>_R<n>`, while `CMN6` contributes 224 entries through `B6_R31`. These values look like firmware-style initialization words for common PHY digital control, sequencing, calibration, PLL, and training tables. Many entries are zero, while nonzero words such as `0x00005306`, `0x00001f4f`, `0x00000800`, `0x000001af`, and `0x0000ffff` recur in structured patterns.

The compact `RAWCMN_DIG_*` control block after the common memory tables defines common PHY controls for `CMN_CTL`, MPLLA/MPLLB bandwidth override, and spread-spectrum clocking override/enables. The defaults show both PLLs sharing the same bandwidth and SSC control defaults in this slice.

The `RAWLANE0` through `RAWLANE3` blocks repeat the same per-lane raw PHY layout. Each lane includes PCS transfer defaults for TX/RX override input/output, PCS input/output, RX adaptation acknowledgements, figure-of-merit, TX pre/main/post cursor direction, and lane number. The lane blocks also include FSM override/monitor/status defaults, fast calibration/adaptation state defaults, always-on AFE/DFE/RX/MPLL/RTUNE/init/adaptation defaults, IRQ request/clear/mask defaults, PMA transfer defaults, TX FSM/clock control, and RX FSM/loss-of-signal/data-enable/adaptation status defaults.

The `SUPX` block is an aggregate or indexed supervisor/common-PHY variant. It includes ID code, reference clock override, MPLLA/MPLLB override and ASIC input defaults, analog override outputs, MPLL power-control and timing thresholds, SSC phase/frequency values, analog MPLL/RTUNE/switch/bandgap defaults, and RTUNE config/status/set/stat registers.

The `LANEX` block is the aggregate per-lane variant. It mirrors the lane-level ASIC override, TX/RX power-state timing, RX VCO calibration, RX CDR/DPLL/adaptation, RX statistic collection, digital analog override, and lane analog TX/RX defaults without binding the names to a numeric lane. This is useful for generated code or documentation that references a lane-template register definition rather than `LANE0` through `LANE3`.

The closing `RAWCMNX_DIG_MEM_CMN2` through `RAWCMNX_DIG_MEM_CMN4` families mirror the earlier common memory tables for an indexed/common-template namespace. `RAWCMNX_DIG_MEM_CMN2`, `CMN3`, and `CMN4` are complete 256-entry tables in this chunk. The range then begins `RAWCMNX_DIG_MEM_CMN5` and stops at `B0_R7`, so the rest of `CMN5` and any later `RAWCMNX` defaults are outside this work item.

## Control Flow

There is no executable control flow in this header. Runtime behavior appears only when other AMDGPU code includes the generated constants:

1. ASIC-specific code selects an NBIO 6.1 register offset or SMN address from the matching generated address headers.
2. Driver code reads, writes, or compares a register through AMDGPU helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD`.
3. These `_DEFAULT` values may be used as generated metadata for reset-state comparison, table-driven initialization, debugging, or documentation of expected hardware state.

The chunk itself does not decide whether a value is writable, read-only, sticky, hardware-owned, volatile, or safe to restore after reset. Those semantics must come from the corresponding mask/header metadata, hardware documentation, and the NBIO/PCIe/PHY access path.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware reset/default state for an NBIO 6.1 PCIe PHY instance.

The represented state includes PHY common memory tables, PLL bandwidth and spread-spectrum defaults, lane PCS/ASIC/PMA override values, lane TX/RX power-state timing, fast calibration and adaptation defaults, AFE/DFE offset defaults, RX VCO/CDR/DPLL defaults, RX statistic counters and match controls, IRQ status/clear/mask defaults, and analog TX/RX measurement/termination/calibration defaults. Some registers describe static reset state, some are override controls, some are hardware status/monitor paths, and some look like initialization RAM words consumed by PHY sequencers or firmware-like hardware state machines.

The chunk boundaries are artificial. The first lines are the tail of a `LANE3` block that began before line 14270, and the final lines are only the start of `RAWCMNX_DIG_MEM_CMN5`. Whole-PHY analysis for those boundary families requires adjacent chunks.

## Dependencies And Integration Points

The primary dependencies are the generated NBIO 6.1 register headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h`, which supplies matching register addresses/offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h`, which supplies matching field shifts and masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_smn.h`, which supplies SMN-space addresses used by NBIO code.

Direct include integration appears in `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, which includes `nbio_6_1_default.h`, `nbio_6_1_offset.h`, `nbio_6_1_sh_mask.h`, and `nbio_6_1_smn.h`. Powerplay include aggregation for Vega-era hardware also includes this default header through `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h`; related Vega include paths consume the NBIO 6.1 offset and mask headers.

The broader runtime integration surfaces are AMDGPU NBIO/BIF setup, PCIe PHY bring-up, clock gating and light sleep policy, link training and retraining, suspend/resume, reset recovery, SR-IOV or passthrough scenarios that depend on stable PCIe link behavior, and diagnostics comparing hardware state against generated reset values.

## Risks And Edge Cases

- These are untyped preprocessor constants. A stale or misgenerated default value can compile cleanly and still mislead reset comparison, diagnostics, or table-driven initialization.
- The namespace is highly repetitive. Copy or generation drift between `LANE0`, `LANE1`, `LANE2`, `LANE3`, `LANEX`, `RAWCMN`, and `RAWCMNX` can silently associate a plausible value with the wrong lane or template register.
- The common memory-table blocks are dense and opaque. A single wrong `B<n>_R<n>` value can alter hardware sequencing, PLL setup, calibration, equalization, or link-training behavior without an obvious source-level symptom.
- Boundary coverage is incomplete. This chunk starts after the beginning of `LANE3` and stops after eight `RAWCMNX_DIG_MEM_CMN5` entries, so it should not be used alone to make whole-lane or whole-table completeness claims.
- PHY analog defaults are interoperability-sensitive. Incorrect TX termination/equalization, RX CDR/AFE, slicer, DFE, VCO, RTUNE, or PLL/SSC defaults can cause marginal links, speed downgrade, link training failures, resume failures, or platform-specific PCIe instability.
- IRQ and status defaults include request, clear, mask, monitor, and counter-style registers. Treating a status or clear register as an ordinary restore target can clear evidence or mask a live hardware event if runtime code uses these values naively.
- Default values do not encode access permissions or side effects. Some values may describe read-only status, hardware-updated state, write-one-to-clear bits, test/ATB paths, or fuse/ASIC input mirrors.

## Test Signals

Useful validation is mostly build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 6.1/Vega support enabled; missing, renamed, or duplicated generated macros should surface through `nbio_v6_1.c`, Vega powerplay include paths, or generated-header consumers.
- Cross-check this default range against `nbio_6_1_offset.h` and `nbio_6_1_sh_mask.h` for matching `DWC_E12MP_PHY_X4_NS_X4_2` register names, lane/template naming, and table ordering.
- On affected hardware, boot and confirm PCIe link speed/width, link retraining, ASPM/light-sleep behavior, and clock-gating transitions remain stable.
- Exercise suspend/resume, runtime power management, GPU reset, and driver unload/reload; PHY default drift often appears as resume link failures, delayed retraining, or unstable RX/TX calibration.
- Run graphics, compute, DMA, and interrupt-heavy workloads while watching for PCIe AER messages, lost interrupts, GPU hangs, link speed downgrade, or corrected-error storms.
- For systems with available diagnostics, compare readback of NBIO/PHY registers after reset or resume against the generated defaults, while excluding volatile status/counter/clear registers.

## Chunk Notes

- Lines 14270-14338 finish the concrete `LANE3` receive-stat, digital analog override, and analog TX/RX default blocks.
- Lines 14339-15586 cover `RAWCMN_DIG_MEM_CMN2` through `RAWCMN_DIG_MEM_CMN6`, with complete 256-entry `CMN2`-`CMN5` tables and a 224-entry `CMN6` table ending at `B6_R31`.
- Lines 15587-15593 cover compact `RAWCMN_DIG_*` common controls for common control, MPLLA/MPLLB bandwidth, and SSC defaults.
- Lines 15594-16065 cover repeated `RAWLANE0` through `RAWLANE3` raw per-lane PCS/FSM/AON/IRQ/PMA/TX/RX control defaults.
- Lines 16066-16138 cover the aggregate `SUPX` supervisor/common defaults.
- Lines 16139-16303 cover the aggregate `LANEX` lane-template defaults.
- Lines 16304-17079 cover complete `RAWCMNX_DIG_MEM_CMN2`, `CMN3`, and `CMN4` tables, then stop inside `RAWCMNX_DIG_MEM_CMN5` after `B0_R7`.
