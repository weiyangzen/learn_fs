# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h lines 7246-9631

## Scope

This chunk is part of the generated AMD DPCS 4.2.0 ASIC register offset header. It contains preprocessor address constants only: every exported symbol has the form `ixDPCSSYS_*` and maps a DPCS register name to a numeric indirect-register offset. There are no C functions, structs, typedefs, branches, locks, allocations, direct MMIO reads/writes, or persistent software data structures in this range.

The slice covers 2,386 source lines and 2,382 `#define` entries. It starts in the middle of the CR2 `SUPX` analog MPLLA block at `ixDPCSSYS_CR2_SUPX_ANA_MPLLA_ATB3` and ends in the CR3 `LANEX` digital analog/signal-detect aliases at `ixDPCSSYS_CR3_LANEX_DIG_ANA_SIGDET_OVRD_OUT_2`. Neighboring chunks are required to reconstruct the full CR2 address block before line 7246 and the remaining CR3 `LANEX`/tail definitions after line 9631.

## Purpose

The purpose of this header chunk is to publish exact register addresses for DPCS 4.2.0 PHY/display hardware blocks. Runtime AMDGPU display and link code combines these offset macros with companion shift/mask headers and register access helpers to program DisplayPort/PHY lanes, PLLs, calibration engines, PCS/PMA interfaces, and diagnostic paths without hard-coding numeric addresses in driver logic.

Major covered areas:

- Tail of CR2 `SUPX` common/supervisor PLL, bandgap, RTUNE, clock/reset, and analog override/status offsets.
- CR2 `LANEX` per-lane alias offsets for ASIC-facing TX/RX overrides, TX/RX power sequencing, RX VCO/CDR/DPLL/adaptation/statistics, MPHY controls, analog TX/RX overrides, and analog test-bus registers.
- CR2 raw memory and raw lane offsets for ROM/RAM, PCS/PMA crossbar, fast-lane FSM, IRQ status/clear/masks, TX/RX control, ATE hooks, OCLA, DCC, and lane-number/equalization handoff registers.
- Start of the CR3 address block, including CR3 supervisor/common PLL registers, lane 0-3 per-lane offsets, raw common offsets, raw lane 0-3 offsets, raw always-on lane 0-3 offsets, `RAWAONLANEX` aliases, `SUPX` aliases, and `LANEX` aliases.
- Repeated register layouts where the same functional names appear at different base ranges for concrete lanes (`LANE0`..`LANE3`) and indexed/all-lane aliases (`LANEX`, `RAWLANEX`, `RAWAONLANEX`, `SUPX`).

## Important Macros and Address Families

The exported API is the generated macro naming contract:

- `ixDPCSSYS_<CR instance>_<block>_<register>` gives the DPCS indirect register offset consumed by AMD register access code.
- CR prefixes distinguish hardware instances, mainly `CR2` for the ending part of the prior address block and `CR3` for the new block beginning at line 7646.
- Suffixes such as `SUP`, `SUPX`, `LANE0`..`LANE3`, `LANEX`, `RAWCMN`, `RAWLANE*`, `RAWLANEX`, `RAWAONLANE*`, and `RAWAONLANEX` encode the address space or alias style, not C types.

Important groups in this chunk include:

- CR2 `SUPX` common PLL/register aliases: `ANA_MPLLA_*`, `ANA_MPLLB_*`, `DIG_MPLLA_MPLL_PWR_CTL_*`, `DIG_MPLLB_MPLL_PWR_CTL_*`, `DIG_CLK_RST_*`, `DIG_RTUNE_*`, and `DIG_ANA_*` offsets cover MPLL A/B controls, SSC spread type, bandgap/reference clock power-up timing, resistor tuning, and analog override/status readback.
- CR2 `LANEX` lane aliases: `DIG_ASIC_*`, `DIG_TX_PWRCTL_*`, `DIG_RX_PWRCTL_*`, `DIG_RX_VCOCAL_*`, `DIG_RX_CDR_*`, `DIG_RX_DPLL_*`, `DIG_RX_ADPTCTL_*`, `DIG_RX_STAT_*`, `DIG_MPHY_*`, `DIG_ANA_*`, and `ANA_TX_*`/`ANA_RX_*` offsets represent a parameterized lane window at `0x9000` through `0x90ff`.
- CR2 raw lane and raw memory: `RAWMEM_DIG_ROM_CMN0_B0_R0`, `RAWMEM_DIG_RAM_CMN0_B0_R0`, `RAWLANEX_DIG_PCS_XF_*`, `RAWLANEX_DIG_FSM_*`, `RAWLANEX_DIG_IRQ_CTL_*`, `RAWLANEX_DIG_PMA_XF_*`, `RAWLANEX_DIG_TX_CTL_*`, `RAWLANEX_DIG_RX_CTL_*`, and ATE offsets expose lower-level firmware, PCS, PMA, IRQ, and calibration control surfaces.
- CR3 supervisor/common offsets: `CR3_SUP_DIG_*` and `CR3_SUP_ANA_*` cover ID codes, refclk/MPLL overrides, SSC parameters, ASIC inputs, prescaler, RTUNE, bandgap, analog MPLL controls, MPLL power control, clock/reset, and digital-to-analog override/status registers.
- CR3 concrete lane windows: `CR3_LANE0` and `CR3_LANE3` contain a reduced TX/statistics/analog-TX-oriented subset, while `CR3_LANE1` and `CR3_LANE2` include full TX and RX power, VCO, CDR, DPLL, adaptation, statistics, MPHY, analog TX/RX, and analog register windows. This asymmetry is part of the generated register map and should not be normalized by hand.
- CR3 raw common/lane windows: `CR3_RAWCMN_DIG_*` covers common raw control, MPLL state, SRAM init, OCLA, firmware ID, and AON common RTUNE values. `CR3_RAWLANE0`..`RAWLANE3` repeat PCS/PMA/FSM/IRQ/TX/RX-control/ATE offsets at `0x3000`, `0x3100`, `0x3200`, and `0x3300`.
- CR3 raw always-on lane windows: `CR3_RAWAONLANE0`..`RAWAONLANE3` and `CR3_RAWAONLANEX` define AFE/CTLE/DFE offsets, slicer controls, adaptation results, signal-detect calibration, RX/TX DCC calibration, firmware MM/adaptation/calibration config, lane transceiver mode, and TX DCC configuration.
- CR3 alias windows: `CR3_SUPX_*` repeats supervisor offsets at the `0x8000` alias range, and `CR3_LANEX_*` repeats lane offsets at the `0x9000` alias range. The chunk ends before the complete `LANEX` analog/register tail is visible.

## Control Flow and Runtime Integration

This header has no executable control flow. Runtime behavior is indirect:

1. AMDGPU display or PHY code includes this offset header for DPCS 4.2.0.
2. Register descriptor tables or access macros pair `ixDPCSSYS_*` offsets with matching field definitions from generated shift/mask headers.
3. Display/link code uses read, write, masked-update, or polling helpers to access the DPCS indirect register space.
4. Hardware implements the actual control flow: PLL setup, clock/reference sequencing, TX/RX power-state transitions, VCO/CDR/DPLL calibration, adaptation, DCC, IRQ signaling, statistics collection, OCLA/ATE observation, and signal-detect/readback behavior.

The represented hardware flow is typically: initialize common supervisor resources and PLLs, configure raw/common firmware or calibration state when needed, select concrete lane or alias windows, sequence TX/RX power and reset timing, run VCO/CDR/DCC/adaptation calibration, manage PCS/PMA handoff between firmware/hardware/software overrides, and poll raw or lane status registers for completion and link quality.

## State and Persistence Behavior

The file itself has no mutable state. All state described by these offsets lives in hardware registers.

Hardware state represented by this chunk includes:

- Common/supervisor state: ID and firmware identification, refclk/MPLL override inputs, SSC parameters, MPLL A/B power control and timers, bandgap/reference power timing, RTUNE values, analog override outputs, SRAM init status, and common OCLA selection.
- Lane power state: TX and RX P-state registers, power-up timers, clock alignment, MPHY low-speed PWM/termination/stable-clock controls, and analog TX/RX enable/override registers.
- Calibration state: MPLL calibration, RX VCO calibration controls/status, CDR controls/status, DPLL frequency/bounds, TX/RX DCC bank/data/control/config registers, AFE/CTLE/VGA/DFE adaptation results, slicer and phase-adjust values, signal-detect calibration, and firmware calibration configuration.
- Diagnostics and observability: RX statistics match/control/counter registers, LBERT control/error offsets, OCLA selectors, ATE override paths, IRQ status/clear/mask registers, raw FSM status/monitor registers, PCS/PMA input/output mirrors, analog test-bus measurement registers, and raw adaptation figure-of-merit offsets.
- Alias state: `SUPX`, `LANEX`, `RAWLANEX`, and `RAWAONLANEX` offsets expose indexed or broadcast-style views over common/lane resources. Correct alias interpretation is supplied by the hardware access path, not by this header.

Persistence is limited to hardware register lifetime. Values can be reset or need reprogramming after GPU reset, DPCS reset, lane reset, display engine reset, power gating, suspend/resume, hotplug-triggered retraining, firmware reload, or link mode/rate/lane-count changes. Durable policy remains in higher-level driver state, BIOS/firmware tables, and silicon configuration, not in this generated header.

## Dependencies

This chunk depends on matching generated DPCS 4.2.0 shift/mask headers and AMDGPU register-access infrastructure. Offset constants alone identify where a register is located but not which bits are safe to read, write, clear, or poll.

It also depends on:

- The silicon register database used to generate this offset header and companion field headers.
- AMD display/link/PHY code that consumes `ixDPCSSYS_*` names through register tables and helper macros.
- Correct address-space selection for CR2 versus CR3 and for concrete lane windows versus alias windows.
- Firmware and hardware microcontrollers that may own raw FSM, calibration, DCC, PCS/PMA, and always-on lane registers during parts of link bring-up.
- Naming stability across generated offset and shift/mask headers. A consumer of `ixDPCSSYS_CR3_LANE2_DIG_RX_CDR_CDR_CTL_0`, for example, relies on a matching `DPCSSYS_CR3_LANE2_DIG_RX_CDR_CDR_CTL_0` field definition in the companion header.

Manual edits are risky unless synchronized with the generator inputs, companion headers, and every table or macro reference that relies on these generated names.

## Integration Points

Primary integration points are AMDGPU display and PHY register tables, register helper macros, and link training code that access DPCS 4.2.0 indirect registers by generated symbol.

Important integration surfaces include:

- PLL and clock bring-up: CR2/CR3 `SUP`/`SUPX` MPLL A/B, SSC, refclk, bandgap, RTUNE, and clock/reset offsets.
- Lane power sequencing: `DIG_TX_PWRCTL_*`, `DIG_RX_PWRCTL_*`, `DIG_MPHY_*`, and analog TX/RX power/clock/termination offsets.
- Receiver calibration and link quality: `DIG_RX_VCOCAL_*`, `DIG_RX_CDR_*`, `DIG_RX_DPLL_*`, `DIG_RX_ADPTCTL_*`, `RAWAONLANE*` adaptation, DFE, slicer, phase, signal-detect, RX DCC, and calibration-code offsets.
- PCS/PMA and firmware coordination: `RAWLANE*`/`RAWLANEX` PCS crossbar, PMA crossbar, fast FSM, IRQ, ATE, TX/RX control, master MPLL loop, and firmware config offsets.
- Diagnostics and validation: RX statistics, LBERT, OCLA, raw FSM status, IRQ clear/mask paths, analog test-bus and measurement registers, ATE override registers, and ID/FW/SRAM status registers.
- Multi-lane mapping: concrete lane offsets (`LANE0`..`LANE3`, `RAWLANE0`..`RAWLANE3`, `RAWAONLANE0`..`RAWAONLANE3`) coexist with `LANEX`/`RAWLANEX`/`RAWAONLANEX` aliases. Consumers must choose the expected address namespace for the operation.

## Risks and Failure Modes

- Wrong offsets can compile cleanly while programming a different hardware register, causing failed link bring-up, bad PLL programming, calibration timeout, unstable CDR/DPLL lock, or broken signal detection.
- CR2/CR3 prefix mistakes can route an operation to the wrong DPCS instance. This is especially hard to diagnose when both instances expose similarly named lanes and aliases.
- Lane alias misuse can affect the wrong lane or an unintended indexed/broadcast window. `LANEX`/`RAWLANEX`/`RAWAONLANEX` should not be treated as mechanically equivalent to `LANE0`..`LANE3`.
- The generated map is intentionally asymmetric: CR3 lane 0 and lane 3 have fewer visible RX/control offsets in this chunk than lanes 1 and 2. Refactoring that assumes identical lane surfaces risks adding invalid references.
- Raw FSM, IRQ clear, ATE, PCS/PMA, firmware, and calibration registers may have side effects on read or write. Incorrect offset pairing with field masks can clear interrupts, force test modes, override firmware-owned paths, or disrupt calibration state.
- Power and timing offsets are sequence-sensitive. Incorrect TX/RX P-state or power-up timer access can leave analog supplies, clocks, CDR/VCO, deserializers, or DCC paths enabled too early, too late, or not at all.
- This chunk starts and ends mid-address-map. A final per-file report must reconcile CR2 definitions before line 7246 and CR3 definitions after line 9631 to avoid treating this slice as a complete register map.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Compile-time coverage: AMDGPU display/PHY code builds without missing or renamed `ixDPCSSYS_CR2_*` and `ixDPCSSYS_CR3_*` offset symbols.
- Generated-header consistency: every consumed offset macro has a matching companion shift/mask register name, and repeated lane families preserve expected base-offset patterns.
- Register table sanity: CR2 and CR3 tables select the correct address block, and concrete lane entries are not accidentally replaced with `LANEX` aliases or vice versa.
- DP/link smoke tests: hotplug, modeset, link retraining, lane-count changes, link-rate changes, suspend/resume, GPU reset, and power-gating recovery on displays exercising CR2/CR3 paths.
- PHY bring-up checks: supervisor PLL lock, MPLL calibration, bandgap/reference timing, TX/RX P-state transitions, RX VCO calibration done, CDR/DPLL lock/frequency readback, DCC ack/status, and adaptation completion.
- Diagnostics: RX statistic counters, LBERT error reporting, IRQ status/clear/mask behavior, OCLA selection, raw FSM status monitors, PCS/PMA mirrors, ATE hooks, analog test-bus readback, and signal-detect calibration/readback.

## Chunk Notes

This is a source-tree-aligned chunk report only. It intentionally does not create the final per-file synthesis for `dpcs_4_2_0_offset.h`; that merge is left for the reconciliation lane after all chunks for this generated header are available.
