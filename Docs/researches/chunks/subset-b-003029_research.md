# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 58991-61665

## Scope

This chunk is a generated AMD NBIO 6.1 shift/mask header segment. It contains C preprocessor constants only; there are no functions, structs, variables, branches, loops, allocations, locks, reference counts, or direct register reads/writes in this range.

The assigned range is part of the DWC E12MP PCIe PHY register map for `X4_NS_X4_0`. It starts in the middle of the common raw digital memory table for common block `CMN4`, continues through all of `CMN5`, most of `CMN6`, then covers common PLL override controls, lane PCS transmit/receive controls, lane FSM controls/status, fast-calibration flags, and the beginning of always-on analog/DFE offset controls. The range ends at `DWC_E12MP_PHY_X4_NS_X4_0_RAWLANEX_DIG_AON_RX_IQ_PHASE_ADJUST`; the next lines continue with more AON tuning/adaptation registers.

Although this file is under a local `ceph-client` source mirror, this path is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this range is to publish bit positions and masks for NBIO 6.1 PCIe PHY registers. Each hardware field is represented by a pair of generated macros:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for extracting or composing the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask for isolating, clearing, preserving, or setting the field.

Consumers combine these masks with the matching generated register names/defaults and AMDGPU register helpers such as `RREG32`, `WREG32`, `RREG32_PCIE`, `WREG32_PCIE`, `SOC15_REG_OFFSET`, `REG_GET_FIELD`, and `REG_SET_FIELD`, depending on the aperture and call site. In this source tree, these exact PHY field names are not directly referenced by normal AMDGPU C files; the header is included as part of a larger generated NBIO register database that firmware bring-up, diagnostics, board-specific programming, and future code can consume.

## Important Macro Families

The first large family is `DWC_E12MP_PHY_X4_NS_X4_0_RAWCMNX_DIG_MEM_CMN4_B*_R*`. The chunk begins at `CMN4_B0_R10` and runs through `CMN4_B7_R31`. Every entry exposes a single 16-bit `DATA` field at shift `0x0` with mask `0xFFFFL`. These macros describe raw common digital memory words rather than decoded semantic fields, so the useful semantics live in the PHY microarchitecture and generated default values, not in the field names.

The next generated tables are complete `CMN5_B0_R0` through `CMN5_B7_R31` and `CMN6_B0_R0` through `CMN6_B6_R31`, also with one full-width 16-bit `DATA` field per word. These blocks are likely sequencer/configuration RAM or raw common tuning memory for the E12MP PHY. The repetition is intentional: each bank/register pair receives a distinct macro name even though the bit layout is identical.

`DWC_E12MP_PHY_X4_NS_X4_0_RAWCMNX_DIG_CMN_CTL` defines common digital control bits. The meaningful field in this chunk is `PHY_FUNC_RST`, with the rest of the 16-bit word reserved. This is a reset-sensitive control surface for the PHY common block.

The `RAWCMNX_DIG_MPLLA_*` and `RAWCMNX_DIG_MPLLB_*` families define common PLL override inputs. They include PLL bandwidth override value/enable fields, spread-spectrum range, fractional-N control, SSC clock select, SSC control override enable, and SSC enable override value/enable. These fields control or override MPLL A/B behavior and therefore sit on timing-critical PCIe clock generation paths.

The `RAWLANEX_DIG_PCS_XF_TX_*` macros describe lane PCS transmit control handshakes. `TX_OVRD_IN` includes `PSTATE`, low-power detect, datapath width, link rate, MPLL selection, MPLL enable, master MPLL state bits, and an override enable. `TX_OVRD_IN_1` adds reset/request/detect-rx/vboost/iboost override value and enable fields. `TX_PCS_IN` represents the non-override PCS input view with reset, request, power state, width, rate, MPLL selection/enables, master MPLL state, and detect-rx request. `TX_OVRD_OUT` and `TX_PCS_OUT` expose acknowledgement/result/status fields.

The `RAWLANEX_DIG_PCS_XF_RX_*` macros mirror the receive side. They include receive rate, width, power state, low-power detect, override enable, AFE/DFE adaptation enables, reset/request overrides, VCO load/low-frequency overrides, loss-of-signal threshold override, reference-load override, adaptation request/continuous/off-cancel continuous controls, PCS receive inputs, adaptation acknowledgement, adaptation figure of merit, and transmitter pre/main/post direction hints seen by the receiver path.

`RAWLANEX_DIG_PCS_XF_RX_PCS_IN_1` through `_4` define additional receive PCS tuning inputs: reference load value, VCO load value, equalizer attenuation, VGA1/VGA2 gain, CTLE boost/pole, and DFE tap1. These fields are directly tied to receive equalization and link training quality.

`RAWLANEX_DIG_PCS_XF_LANE_NUMBER` exposes a 4-bit lane number. `RAWLANEX_DIG_FSM_FSM_OVRD_CTL`, `FSM_MEM_ADDR_MON`, and `FSM_STATUS_MON` describe finite-state-machine control and observability: jump address, jump enable, command start, override enable, memory address monitor, FSM state, command address/data monitor, command-ready, ALU flags, wait-counter status, and read/write-mask disabled indicators.

The `RAWLANEX_DIG_FSM_FAST_*` registers are one-bit flags for fast PHY routines: RX startup calibration, RX adaptation, AFE calibration, DFE calibration, bypass calibration, reference-level calibration, IQ calibration, AFE/DFE adaptation, SUP, TX common mode, TX receiver detection, RX power-up, RX VCO wait, and RX VCO calibration. `RAWLANEX_DIG_FSM_CMNCAL_STATUS` reports common calibration init/done.

The final family in this chunk begins the always-on lane analog/DFE offset area. It includes AFE attenuation, CTLE, VGA1 IDAC offsets; DFE summer even/odd IDAC offsets; DFE phase even/odd and low even/odd VDAC offsets; RX phase adjust linear/map controls; DFE data even/odd high/low VDAC offsets; DFE bypass even/odd VDAC offsets; DFE error even/odd VDAC offsets; and RX IQ phase adjustment. Most of these are 8-bit offset fields with reserved upper bits; RX phase adjust uses 5-bit fields, and RX IQ phase adjustment uses a 7-bit field.

## APIs, Types, And Functions

There are no C APIs, types, or functions in this chunk. The exported interface is the macro namespace in `nbio_6_1_sh_mask.h`.

Direct include sites for this header in the source tree include `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, and PowerPlay include aggregators such as `pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h`. A search of AMDGPU C/H users under this tree did not find direct references to the exact `DWC_E12MP_PHY_X4_NS_X4_0_RAWCMNX` or `RAWLANEX` field names from this chunk; they appear to be generated hardware database definitions available to low-level code, diagnostics, or future register programming rather than actively used high-level driver symbols in this snapshot.

Matching generated defaults are present in `nbio_6_1_default.h`, including nonzero common memory defaults, default zeroed PCS/FSM status and control registers, default `0x80` for many AON analog/DFE offset registers, and default `0x7` for `RAWLANEX_DIG_AON_RX_IQ_PHASE_ADJUST`.

## Control Flow

There is no executable control flow in this header. Runtime behavior happens only in code that includes the generated register definitions:

1. Driver or diagnostic code selects a generated register address/name for the NBIO 6.1 PHY block.
2. It reads or writes the hardware register through the AMDGPU register access layer.
3. It extracts or composes a field using the `__SHIFT` and `_MASK` constants from this header.
4. It uses the resulting value to program PHY memory tables, reset the PHY common block, override PLL or PCS controls, observe PCS/FSM status, or tune receive adaptation and analog offsets.

For this range, the natural runtime contexts are PCIe PHY bring-up, link training, low-power state transitions, spread-spectrum/PLL tuning, TX/RX PCS override flows, receive adaptation/calibration, DFE/AFE offset programming, lane diagnostics, and hardware debug procedures.

## State And Persistence Behavior

The header stores no software state and persists nothing. It describes bit layout for hardware-backed state owned by the NBIO PCIe PHY, platform firmware, hardware initialization tables, and any AMDGPU code that programs or reads the PHY.

The represented hardware state includes raw common memory words, common PHY reset state, MPLL A/B bandwidth and spread-spectrum override controls, transmit and receive PCS request/acknowledge state, reset/request/detect-rx/vboost/iboost overrides, receive VCO/reference/load/equalization parameters, FSM override and monitor state, fast-calibration enable/status flags, common calibration status, and always-on analog/DFE offset values.

Some fields are software-programmed controls, some are hardware-updated status/monitor values, and the large `MEM_CMN*` tables may represent initialization or tuning RAM loaded from generated defaults. The masks do not encode reset defaults, read/write permissions, side effects, required sequencing, settle times, lane ownership, or firmware/driver ownership rules. Those constraints must come from the hardware spec, firmware scripts, or the matching default/register-address metadata.

## Dependencies And Integration Points

The primary dependency is consistency with the generated NBIO 6.1 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h` provides reset/default values for the same `DWC_E12MP_PHY_X4_NS_X4_*` register names.
- Other `nbio_6_1_*` generated headers provide the surrounding NBIO register address and SMN/configuration metadata for consumers that program the hardware.
- AMDGPU register helper macros provide the actual read/modify/write and field extraction mechanics.

Integration points are mostly low-level and hardware-facing: NBIO setup, PCIe link bring-up, MxGPU/SR-IOV platform initialization where PCIe PHY state affects virtualized devices, PowerPlay code that includes NBIO register definitions for ASIC-specific programming, firmware/PSP-mediated initialization flows, and debug tooling that compares live PHY state against generated defaults.

The PHY-level integration surface is broader than ordinary PCI configuration space. Incorrect use of these masks can affect PCIe clock generation, PLL spread spectrum, TX/RX datapath width/rate selection, link power state transitions, receive adaptation, equalization, DFE/AFE calibration, lane numbering, and PHY FSM progress.

## Risks And Edge Cases

- Chunk boundaries are artificial. The first line starts at `CMN4_B0_R10`, after the `CMN4` table has already begun, and the last line ends at `AON_RX_IQ_PHASE_ADJUST`, before the AON adaptation/tuning section is complete.
- The raw memory table macros are semantically opaque. Every `CMN4`, `CMN5`, and `CMN6` entry is just a full-width `DATA` field, so accidental bank/register transposition can compile cleanly while loading the wrong PHY tuning word.
- The generated names are long and repetitive. Copy/paste or code-generation drift across `CMN4`, `CMN5`, `CMN6`, `MPLLA`, `MPLLB`, TX, RX, and AON families could silently change the targeted PHY block or lane.
- Reserved-bit masks are present for many decoded registers. Read/modify/write code must preserve reserved bits unless the hardware documentation explicitly permits changing them.
- `PHY_FUNC_RST` can reset functional PHY state. Programming it without the required sequencing can disrupt PCIe links, surprise devices, or race with firmware-owned initialization.
- MPLL bandwidth and spread-spectrum overrides are timing-critical. Bad values can cause link training failures, clock instability, interoperability issues, or marginal behavior that appears only under temperature, voltage, or power-state changes.
- TX/RX PCS override enables bypass normal hardware/firmware control. Leaving overrides asserted can block link training, hold lanes in reset/request states, select wrong rate/width, or report stale acknowledgement/status.
- RX adaptation and equalization fields affect signal integrity. Wrong VCO load, reference load, LOS threshold, AFE/DFE enable, CTLE/VGA/DFE tap, phase, or IQ settings can produce intermittent PCIe errors rather than immediate deterministic failures.
- FSM override and jump controls are debug-like hooks. Misuse can force the PHY state machine into invalid states or hide true command-ready/error conditions.
- AON analog/DFE offset defaults are nonzero for many fields. Treating them as ordinary zero-init controls could degrade receiver margin even if the masks themselves look simple.

## Test Signals

Useful validation is mostly generated-header consistency, build coverage, and hardware/link testing:

- Build AMDGPU paths that include NBIO 6.1 headers, including `nbio_v6_1.c`, `mxgpu_ai.c`, and Vega10/Vega12 PowerPlay include users. Missing or renamed macros should surface at compile time only if a consumer names them directly.
- Compare this chunk against `nbio_6_1_default.h` to verify every `CMN4`, `CMN5`, `CMN6`, PCS, FSM, and AON register in the chunk has a matching default value where the generated database expects one.
- On NBIO 6.1 hardware, capture PCIe PHY register dumps before and after driver initialization and compare raw common memory, PLL override, PCS, FSM, and AON offset values against generated defaults and known-good firmware programming.
- Exercise cold boot, warm reboot, suspend/resume, runtime power management, GPU reset, and PCIe retraining while monitoring link speed/width, training status, AER counters, and PHY FSM status.
- Stress PCIe traffic under multiple link rates and widths to catch RX/TX PCS, equalization, and PLL regressions that only appear under sustained DMA or power-state transitions.
- Where supported by platform diagnostics, force or observe RX adaptation/calibration flows and verify `RX_ADAPT_ACK`, `RX_ADAPT_FOM`, `CMNCAL_STATUS`, and `FAST_*` flags transition as expected.
- Validate spread-spectrum and PLL override programming with board-specific SI/clocking checks; link stability should hold across supported temperature and voltage ranges.
- For virtualization or MxGPU scenarios, enable SR-IOV/VFs and stress guest traffic while checking that host PHY state remains stable and no VF-visible PCIe/AER errors accumulate.

## Chunk Notes

- Lines 58991-59726 finish `RAWCMNX_DIG_MEM_CMN4_B0_R10` through `CMN4_B7_R31`; `CMN4_B0_R0` through `B0_R9` are in the preceding chunk.
- Lines 59729-60494 cover complete `RAWCMNX_DIG_MEM_CMN5_B0_R0` through `CMN5_B7_R31`.
- Lines 60497-61166 cover `RAWCMNX_DIG_MEM_CMN6_B0_R0` through `CMN6_B6_R31`; later `CMN6` banks are not present before the decoded common/lane registers begin.
- Lines 61169-61218 cover common control and MPLL A/B bandwidth/SSC override inputs.
- Lines 61220-61452 cover TX/RX PCS interface, override, status, adaptation acknowledgement/figure-of-merit, direction, and lane-number fields.
- Lines 61454-61565 cover lane FSM override, monitor/status, fast-calibration flags, and common calibration status.
- Lines 61567-61665 begin AON AFE/DFE/RX phase/IQ offset definitions and stop before the following AON coarse tune/adaptation registers.
