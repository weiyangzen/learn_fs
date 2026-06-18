# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002283`: lines 1-2473, `Docs/researches/chunks/subset-b-002283_research.md`
- `subset-b-002284`: lines 2474-4859, `Docs/researches/chunks/subset-b-002284_research.md`
- `subset-b-002285`: lines 4860-7245, `Docs/researches/chunks/subset-b-002285_research.md`
- `subset-b-002286`: lines 7246-9631, `Docs/researches/chunks/subset-b-002286_research.md`
- `subset-b-002287`: lines 9632-11973, `Docs/researches/chunks/subset-b-002287_research.md`

## Chunk Research

### subset-b-002283: lines 1-2473

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h lines 1-2473

## Scope

This chunk is the opening slice of AMDGPU's generated DPCS 4.2.0 register-offset header. It contains preprocessor constants only: no callable functions, structs, enums, storage objects, or local executable control flow. The exported contract is a set of `reg*` MMIO register offsets, paired `reg*_BASE_IDX` constants, and `ix*` indirect control-register indices for DPCS/RDPCS/UNIPHY display PHY programming.

The covered range starts with the license and include guard, then defines direct display register blocks for DPCSSYS CR address/data windows, two panel power sequencers, five RDPCSTX instances, DCIO global/chip GPIO blocks, and UNIPHY1-4 reserved macro-control offsets. It then begins the `dpcssys_cr0_rdpcstxcrind` indirect register space and continues through CR0 supervisor/common registers, lane 0-3 PHY/PCS register indices, raw common indices, raw lane 0-3 indices, and the first nine raw always-on lane 0 indices. The CR0 indirect block continues after line 2473 in the next chunk.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMD display hardware metadata. It has no Ceph, filesystem, distributed-storage, network, or persistent-disk behavior.

## Purpose

The purpose of this header range is to bind logical DPCS 4.2.0 display PHY register names to ASIC-specific numeric offsets. Runtime display code can include this header, usually with the companion shift/mask header and register helper macros, to program DisplayPort/HDMI PHY, link, AUX/DDC, GPIO, panel power, clock, PLL, lane training, calibration, and diagnostic registers without hard-coding raw addresses in C code.

The direct `reg*` blocks in this chunk cover:

- `DPCSSYS_CR0` through `DPCSSYS_CR4` address/data apertures at direct offsets `0x2934/0x2935`, `0x2a0c/0x2a0d`, `0x2ae4/0x2ae5`, `0x2bbc/0x2bbd`, and `0x2c94/0x2c95`.
- `PWRSEQ0` and `PWRSEQ1` panel power-sequencer and backlight/PWM registers, including GPIO enable/control/mask/Y, panel power control/state/delays/reference dividers, PWM control/period/lock, and spare registers.
- `RDPCSTX0` through `RDPCSTX4`, each with control, clock, interrupt, PLL update, CR address/data, SRAM control, scratch/spare, debug, PHY control 0-17, PHY fuse 0-3, RX load value, DP-alt-mode/DMCU controls, and PLL override offsets.
- Global DCIO control: generic registers, DCIO and reference clock control, UNIPHY A-E link and channel crossbar control, write-command delay, pin straps, intercept state, backlight PWM frame-start display select, genlock/swaplock pads, and soft reset.
- DCIO chip GPIO/AUX/DDC controls: generic GPIO, DDC1-5, DDCVGA, genlock, HPD, power-sequencer GPIO enables, pad strength, PHY AUX control, TX/RX/pull-up enables, AUX control 0-5, and AUX/I2C pad power-good.
- UNIPHY1-4 reserved macro-control ranges, each exposing `UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED57` at instance-strided direct offsets.

The `ixDPCSSYS_CR0_*` block maps the indirect CR register indices reached through the CR0 address/data window. In this chunk it covers supervisor digital/analog MPLL and RTUNE controls, lane 0-3 ASIC override/status and TX/RX power/calibration/equalization registers, raw common registers, raw lane PCS/FSM/IRQ/PMA/TX/RX controls, and the start of raw always-on lane calibration/adaptation state.

## Important APIs, Types, And Macros

There are no C APIs or concrete types in this chunk. The important interface is the generated macro namespace:

- `reg...` constants are direct register offsets used by AMD display register-access helpers.
- `reg..._BASE_IDX` constants select the register aperture/base index. Every direct register in this chunk uses base index `2`.
- `ixDPCSSYS_CR0_...` constants are indirect register indices, not direct MMIO offsets. They are selected through a CR address register such as `regDPCSSYS_CR0_DPCSSYS_CR_ADDR` or `regRDPCSTX0_RDPCS_TX_CR_ADDR` and read/written through the matching data register.

The most important direct register families are the repeated RDPCSTX instances. Each instance has the same shape and an instance stride in direct address space: control and clock registers, interrupt control for DP-alt-mode and FIFO conditions, PLL update data/address override registers, SRAM control, scratch/debug, PHY controls 0-17, fuse registers used for lane tuning data, and DP-alt-mode/DMCU handoff controls. These offsets are the top-level access points for RDPCS transmitter setup and status.

The DPCSSYS CR address/data aliases are notable. For example, the CR0 address/data definitions are numerically identical to `regRDPCSTX0_RDPCS_TX_CR_ADDR` and `regRDPCSTX0_RDPCS_TX_CR_DATA`; CR1-CR4 similarly line up with RDPCSTX1-4. Consumers must treat these as access-window aliases over the same hardware offsets rather than independent storage.

The power-sequencer registers are the panel and backlight control surface in this chunk. `PANEL_PWRSEQ_CNTL`, `PANEL_PWRSEQ_STATE`, `PANEL_PWRSEQ_DELAY1`, `PANEL_PWRSEQ_DELAY2`, `PANEL_PWRSEQ_REF_DIV1/2`, `BL_PWM_CNTL`, `BL_PWM_CNTL2`, `BL_PWM_PERIOD_CNTL`, and `BL_PWM_GRP1_REG_LOCK` define the offsets used by panel enable/disable and backlight PWM programming.

The DCIO and GPIO registers are the connector-side integration surface. `UNIPHY*_LINK_CNTL` and `UNIPHY*_CHANNEL_XBAR_CNTL` bind logical links to physical channel routing. `DC_GPIO_DDC*`, `DC_GPIO_HPD_*`, `PHY_AUX_CNTL`, `DC_GPIO_AUX_CTRL_*`, `DC_GPIO_RXEN`, `DC_GPIO_PULLUPEN`, and `AUXI2C_PAD_ALL_PWR_OK` are the offset metadata for AUX, DDC, HPD, and pad-power programming.

The CR0 indirect index map is grouped by address ranges. Supervisor indices start at `0x0000` and include ID code, reference clock overrides, MPLLA/MPLLB override, spread-spectrum, ASIC input/output, analog bandgap, prescaler, RTUNE, MPLL power/timer/calibration, and status registers. Lane indices use `0x1000`, `0x1100`, `0x1200`, and `0x1300` regions. Raw common indices start at `0x2000`. Raw lane indices use `0x3000`, `0x3100`, `0x3200`, and `0x3300`. Raw always-on lane 0 begins at `0x4000` and is cut off by this chunk.

## Control Flow

This header has no executable control flow. Runtime behavior is created by code that includes generated offset and shift/mask headers, expands register tables, and issues MMIO or indirect CR reads and writes through AMDGPU display helpers.

A typical use path is:

1. Display resource or PHY code selects the DPCS 4.2.0 register set for the ASIC.
2. Register-list macros paste logical names onto generated constants such as `regRDPCSTX0_RDPCSTX_PHY_CNTL0`, `regDC_GPIO_HPD_A`, or `ixDPCSSYS_CR0_LANE1_DIG_RX_CDR_STAT`.
3. Direct offsets are passed to normal register helpers for MMIO reads/writes; field layout comes from the matching shift/mask header rather than this offset file.
4. Indirect CR accesses first write an `ixDPCSSYS_CR0_*` index through the selected CR address register, then access the corresponding CR data register.
5. Higher-level link, PHY, AUX/DDC, HPD, panel-power, backlight, DP-alt-mode, or diagnostics code decides sequencing, delays, polling, and error handling.

The file therefore encodes address identity, not policy. It does not describe when clocks must be enabled, when a PLL is stable, how long panel power delays must run, or how DP link training should react to status.

## State And Persistence Behavior

The file itself stores no runtime state and persists nothing. It describes hardware state whose lifetime is controlled by display initialization, modesets, hotplug events, link training, AUX/DDC transactions, panel power transitions, runtime power management, suspend/resume, and GPU reset.

State represented by this chunk includes:

- RDPCS transmitter enable/reset, clock, FIFO, SRAM, interrupt, debug, scratch, PLL update, DP-alt-mode, and PHY control state.
- PHY tuning and calibration state, including MPLLA/MPLLB override and spread-spectrum values, RTUNE, TX equalization, termination, DCC DAC, RX CDR/VCO/adaptation, lane status, and raw FSM/IRQ/PMA/PCS state.
- Connector routing and pad state: UNIPHY link/channel crossbars, AUX/DDC GPIO state, HPD GPIO state, genlock/swaplock pads, pull-ups, RX/TX enables, and AUX/I2C pad power-good.
- Panel and backlight state: power-sequencer GPIO state, panel control/state/delay/reference-divider registers, PWM control/period, group lock, and spare state.
- Diagnostic/readback state such as ID code, ASIC input/output mirrors, analog status, load values, lane counters/status, FIFO status, and IRQ status/clear indices.

Bad register values can remain active until the affected block is reprogrammed, reset, power-cycled, or the GPU is reset. Some state is reconstructed by normal modeset or resume paths, but this generated header has no save/restore logic.

## Dependencies And Integration Points

The direct companion is the DPCS 4.2.0 shift/mask header in the same generated register family, which defines bit positions and masks for these offsets. This header supplies addresses and indices; the companion supplies field geometry.

Important integration points visible in the tree include:

- AMD display register helper and resource construction patterns that consume generated `reg*`, `*_BASE_IDX`, `*_SHIFT`, and `*_MASK` constants to build typed register tables.
- AMD ASIC enum headers such as `soc24_enum.h`, which define symbolic values for RDPCSTX controls including clock enables, soft resets, FIFO state, DP-alt-mode interrupt conditions, PHY reference ranges, DP TX rate/width/pstate, and PHY control enumerations.
- Atom firmware data structures that map board or VBIOS tuning values such as TX equalization main/pre/post and vboost level to RDPCSTX PHY fuse/control registers.
- DCIO/AUX/DDC/HPD code paths that depend on `DC_GPIO_*`, `PHY_AUX_CNTL`, and `DC_GPIO_AUX_CTRL_*` offsets to drive connector detection and sideband communication.
- Panel power and backlight code paths that depend on the `PWRSEQ*` and `BL_PWM*` offsets when sequencing embedded panels.
- PHY/link programming code that must distinguish direct RDPCSTX offsets from indirect CR indices and pair each instance with the correct CR address/data window.

The namespace is generation-specific. Similar DPCS/RDPCS/UNIPHY names appear in other AMD register headers, but offsets, instance counts, reserved ranges, and indirect index maps are not interchangeable across ASIC versions.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. Offset constants compile cleanly even when wrong, but a bad address can read or write a different register, route the wrong link, leave clocks or resets in an unexpected state, or make status polling look valid while observing the wrong hardware.

Direct-versus-indirect confusion is a high-risk edge case. `reg*` constants are direct offsets with base indices, while `ixDPCSSYS_CR0_*` values are CR-space indices. Passing an `ix*` constant to a direct MMIO helper, or writing a `reg*` offset through a CR index path, would target the wrong address space.

Instance aliasing is also important. The DPCSSYS CR address/data registers overlap the RDPCSTX CR address/data names for each instance. That is useful for macro compatibility, but consumers must not assume duplicated definitions represent separate hardware registers.

Lane asymmetry is visible in this slice. Lanes 1 and 2 include expanded RX power, VCO calibration, CDR, adaptation, analog RX, MPHY RX, and AON-related state, while lanes 0 and 3 in this region expose a smaller TX/status-oriented set. Code that blindly assumes identical lane register availability can reference missing macros or program unsupported lane controls.

Panel power and backlight registers are user-visible and timing-sensitive. Incorrect offsets or mismatched fields can produce blank panels, incorrect backlight PWM, unsafe panel sequencing, stuck panel-power state, or lock bits that prevent later brightness changes.

AUX/DDC/HPD offsets are connector-critical. Errors can break EDID reads, hotplug detection, AUX transactions, or pad power sequencing, which may present as missing displays rather than obvious register failures.

PHY/PLL/lane-training offsets are link-stability-sensitive. Bad MPLL, spread-spectrum, RTUNE, TX equalization, RX CDR/adaptation, power-state, or IRQ indices can cause intermittent link training failures, high error rates, blanking, or failures isolated to particular link rates, lane counts, cables, connectors, or DP-alt-mode paths.

Chunk-boundary risk is real. The document covers only lines 1-2473. It stops inside the CR0 raw always-on lane 0 register list at `ixDPCSSYS_CR0_RAWAONLANE0_DIG_DFE_ODD_REF_LVL`; the rest of CR0 and all later CR1-CR4 indirect spaces are outside this chunk and must be merged before drawing complete-file conclusions.

## Test Signals

Useful validation is mostly generated-header, build, and hardware-behavior oriented:

- Compile coverage for all AMDGPU display code that includes DPCS 4.2.0 generated offset and shift/mask headers.
- Generated-register consistency checks that every direct `reg*` used by resource tables exists, has the expected `_BASE_IDX`, and has matching fields in the companion shift/mask header.
- Indirect-access tests that verify CR address/data windows select expected `ixDPCSSYS_CR0_*` indices and that direct MMIO helpers are not used for indirect indices.
- Cross-generation and register-database diffs against AMD's authoritative DPCS 4.2.0 source to catch offset drift, missing reserved entries, incorrect instance strides, or accidental reuse from a neighboring ASIC.
- Panel tests for power-on/off, suspend/resume, backlight PWM enable/period/duty programming, lock/unlock behavior, and eDP panel timing.
- Connector tests for HPD, DDC/EDID, AUX transactions, pad power-good, pull-up/RX/TX enable state, UNIPHY link routing, and channel crossbar programming.
- Link/PHY tests across DisplayPort and HDMI rates, lane counts, training patterns, DP-alt-mode transitions, hotplug, runtime PM, and GPU reset.
- Diagnostics tests for RDPCSTX interrupt status/clear behavior, FIFO error paths, scratch/debug access, PHY fuse readback, PLL update override paths, and lane/raw FSM status.

Regression symptoms from bad constants include missing displays, failed EDID/AUX/HPD, black or flickering panels, incorrect backlight, stuck panel power state, DP link training failures, HDMI/DP rate-specific instability, DP-alt-mode failures, broken suspend/resume restore, misleading PHY diagnostics, or failures isolated to DPCS 4.2.0 ASICs.

## Cross-Chunk Notes

This is not a standalone source module. It is a generated register-layout slice inside `dpcs_4_2_0_offset.h`. The following chunk owns the rest of `DPCSSYS_CR0_RAWAONLANE0` and later CR0 indices, and later chunks own CR1-CR4 indirect spaces plus tail special cases. The merge/reconciliation lane should treat this document as the direct DPCSSYS/PWRSEQ/RDPCSTX/DCIO/UNIPHY opening plus the beginning of the CR0 indirect register map.

### subset-b-002284: lines 2474-4859

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h lines 2474-4859

## Scope

This chunk is part of the generated AMD DPCS 4.2.0 register offset header. It contains preprocessor constants only: `ix...` register-index aliases mapped to hexadecimal offsets inside the DPCS client register aperture. There are no C functions, structs, branches, allocations, locks, direct MMIO accesses, or persistence mechanisms in this source range.

The slice covers 2,386 source lines and 2,382 `#define` entries. It starts inside the CR0 RAWAON lane 0 always-on receiver register list at `ixDPCSSYS_CR0_RAWAONLANE0_DIG_RX_PHSADJ_LIN` (`0x4009`) and ends inside the CR1 RAWAON lane 2 list at `ixDPCSSYS_CR1_RAWAONLANE2_DIG_RX_SIGDET_CONFIG` (`0x4250`). Neighboring chunks are needed to reconstruct the full CR0 RAWAON lane 0 prologue and the CR1 RAWAON lane 2 tail.

## Purpose

The purpose of this chunk is to publish the DPCS 4.2.0 offset namespace used by AMDGPU display and PHY code to address DisplayPort/PHY control/status registers. The values are not field masks; they are register offsets or indirect register indices that are paired with companion shift/mask headers and the driver's register access helpers.

Major covered areas:

- CR0 always-on lane receiver/DFE/adaptation aliases for RAWAON lanes 0 through 3 plus a generic `RAWAONLANEX` block.
- CR0 support/supervisor aliases covering ID code, level and reference-clock overrides, MPLLA/MPLLB ASIC inputs, PLL override inputs, SSC, bandgap/reference power timing, rtune, and analog status/override outputs.
- CR0 lane-generic aliases for ASIC handoff/mirror registers, TX/RX P-state and power-up timing, TX DCC, RX VCO/CDR/DPLL/adaptation/statistics, MPHY low-speed controls, and analog TX/RX override/status registers.
- CR0 raw memory and raw lane aliases for PCS, FSM, IRQ, PMA, TX/RX control, loopback/test, and lane state observation.
- CR1 support/supervisor aliases with the same PLL, clock/reset, rtune, bandgap, and analog status model as CR0, but reset to a CR1-local offset namespace beginning at `0x0000`.
- CR1 per-lane aliases for lanes 0 through 3, where lanes 1 and 2 include the full TX/RX PHY register families while lanes 0 and 3 in this chunk expose the smaller TX/ASIC subset present in this range.
- CR1 raw common and raw lane aliases for common control/status, PCS/FSM/IRQ/PMA cross-fabric state, and lane controller observability.
- CR1 RAWAON lane 0, lane 1, and most of lane 2 always-on receiver/DFE/adaptation aliases.

## Important Macros and Register Families

The exported API is the generated macro naming contract:

- `ixDPCSSYS_CR<n>_<BLOCK>_<REGISTER>` names an indexed DPCS register for client router instance `CR<n>`.
- The hexadecimal value is the register's DPCS internal offset or index. For repeated lane blocks the low byte commonly identifies the register inside the lane, while the high nibble/byte selects lane or sub-block.
- Generic `LANEX`, `RAWLANEX`, and `RAWAONLANEX` entries describe per-lane templates; numbered `LANE0..3`, `RAWLANE0..3`, and `RAWAONLANE0..3` entries bind the same register families to concrete lanes.
- These offset constants must be used with companion generated shift/mask headers such as `dpcs_4_2_0_sh_mask.h` when code needs to update individual fields.

Important covered families include:

- Always-on receiver calibration and adaptation: `RAWAONLANE*` and `RAWAONLANEX` entries for AFE ATT/CTLE IDAC offsets, RX IQ/phase adjustment, DFE phase/data/bypass/error offsets, DFE even/odd reference levels, RX adaptation ATT/VGA/CTLE/DFE tap status, adaptation done, fast flags, slicer controls, common calibration status, and calibration code readbacks.
- Always-on signal detect and DCC controls: RAWAON aliases for RX LOS mask/filtering, signal-detect calibration/high-frequency/low-frequency code, VREF generator enable, TX DCC bank address/data/control/config, MPLL background control, signal-detect override/input, firmware MM/adaptation/calibration configuration, lane transceiver mode override/input, and RX signal-detect configuration.
- Supervisor and common PLL controls: `SUP` and `SUPX` entries for ID code, reference clock and level overrides, MPLLA/MPLLB ASIC inputs, charge-pump/divider/HDMI-clock overrides, SSC peak/step/spread type, PLL power/control/timers/status/calibration/DAC outputs, bandgap and reference power timing, rtune configuration/status/set values, and analog override/status mirrors.
- ASIC lane handoff registers: `LANE*` and `LANEX` `DIG_ASIC_*` entries for lane override inputs, TX/RX override inputs/outputs, ASIC-owned TX/RX inputs and outputs, RX equalization and CDR/VCO ASIC inputs, OCLA selection, and lane control observability.
- TX power, DCC, and diagnostics: `DIG_TX_PWRCTL_TX_PSTATE_P0/P0S/P1/P2`, `TX_PWRUP_TIME_0..5`, DCC CR bank access, DCC DAC control/range/select/ack/address, TX clock alignment, and TX LBERT control.
- RX power, VCO, CDR, DPLL, adaptation, and statistics: RX P-state and power-up timing, VCO calibration controls/timers/status, XAUI comma mask, RX LBERT control/error count, CDR control/status, DPLL frequency and bounds, adaptation config/reset/status, slicer and DAC-control selection, statistic match/mask/control/counter/sample registers, and statistic stop/calibration-comparator clock controls.
- Analog and MPHY integration registers: `DIG_ANA_*`, `ANA_TX_*`, `ANA_RX_*`, and `DIG_MPHY_*` entries for analog TX/RX override outputs, termination codes, equalization, DCC DAC, RX AFE/CTLE/VGA/slicer/calibration DAC controls, signal detect, analog test-bus measurement, MPHY PWM, low-speed termination, and PWM clock stability.
- Raw lane controller and interrupt registers: `RAWLANE*` and `RAWLANEX` entries for PCS transmit/receive overrides and PCS I/O mirrors, FSM fast-state monitors for RX startup/adaptation/calibration/power-up/VCO and TX common mode/RX detect, IRQ request/clear/mask entries for RX/TX reset/request/rate/P-state/adaptation/phase calibration/loopback/DCC, and PMA cross-fabric override/status registers.

## Control Flow and Runtime Integration

This header has no executable control flow. Runtime behavior is indirect:

1. AMDGPU display or PHY code includes this generated DPCS 4.2.0 offset header with the matching 4.2.0 shift/mask header.
2. Register tables, macro accessors, or generated init paths select an `ix...` offset for the appropriate CR instance and lane namespace.
3. Register helpers use that offset to address the DPCS register, optionally applying companion field shift/mask constants for read/modify/write operations.
4. The hardware performs the actual state transition: PLL power-up, reference clock/bandgap sequencing, lane TX/RX P-state changes, DCC/VCO/CDR/adaptation calibration, signal-detect setup, statistics collection, interrupt status updates, or PCS/PMA handoff.

The represented hardware flow is typically: configure supervisor PLL/reference/rtune resources, select ASIC-owned or software-override lane controls, sequence TX/RX power states and delay timers, perform DCC/VCO/CDR/adaptation calibration, expose or consume PCS/PMA/ASIC handoff signals, and read status/diagnostic offsets to validate link readiness.

## State and Persistence Behavior

The file itself has no mutable state. All state described by these macros lives in DPCS hardware registers.

The hardware state represented by this chunk includes:

- Supervisor state: MPLLA/MPLLB power, calibration, spread-spectrum, timer, charge-pump, divider, HDMI-clock, rtune, bandgap, reference-clock, and analog status/override registers.
- Lane power state: TX and RX P0/P0S/P1/P2 controls, TX/RX power-up timers, MPHY PWM/termination/stable-clock controls, and analog clock/data/refgen/termination enables.
- Calibration state: RX VCO and CDR/DPLL controls/status, RX DCC calibration code readbacks, TX DCC DAC/bank controls, AFE/CTLE/VGA/DFE/slicer offsets, phase/IQ adjustment, common calibration status, and firmware calibration/adaptation configuration.
- Handoff and override state: ASIC, PCS, PMA, raw lane, and always-on lane override inputs/outputs for TX, RX, equalization, CDR/VCO, signal detect, transceiver mode, DCC, and lane mapping.
- Diagnostics and observability: LBERT controls/errors, RX statistics match/counter/sample registers, FSM fast-state/status monitors, IRQ status/clear/mask registers, OCLA selections, analog status, and test-bus measurement registers.

Persistence is limited to the hardware register lifetime. Values can be lost or require reprogramming after GPU reset, DPCS client router reset, lane reset, power gating, display engine reset, suspend/resume, hotplug-triggered retraining, or link mode/rate/lane-count changes. Higher-level driver state and silicon tables remain the durable source of truth.

## Dependencies

This chunk depends on:

- Companion generated DPCS 4.2.0 field metadata headers, especially the matching shift/mask header, because offsets alone do not describe bit layout.
- AMDGPU display register access infrastructure that understands DPCS indexed registers and the `ixDPCSSYS_*` naming convention.
- The silicon register database that generated this file; manual edits must remain synchronized with other generated headers and register tables.
- DisplayPort/link encoder, PHY bring-up, power-management, diagnostics, and validation code that selects CR0/CR1 and lane-specific DPCS offsets.
- Correct mapping between generic `LANEX`/`RAWLANEX`/`RAWAONLANEX` templates and concrete lane instances when generated tables or helper macros expand per-lane access.

The offsets in CR0 and CR1 intentionally use different base namespaces in this range. CR0 contains higher CR0 template/raw/supervisor ranges such as `0x7000`, `0x8000`, `0x9000`, `0xa000`, and `0xe000`, while CR1 restarts supervisor offsets at `0x0000`, lane offsets at `0x1000..0x1300`, raw/common offsets at `0x2000..0x3300`, and RAWAON offsets at `0x4000..0x4250` in this chunk.

## Integration Points

Primary integration points are the macro names consumed by AMDGPU register tables and register helpers. A consumer naming an offset such as `ixDPCSSYS_CR1_LANE2_DIG_RX_CDR_CDR_CTL_0` or `ixDPCSSYS_CR0_RAWAONLANEX_DIG_RX_ADPT_DFE_TAP3` relies on this header for the exact DPCS 4.2.0 register index.

Integration surfaces include:

- Link and lane power sequencing through TX/RX P-state and power-up-time offsets.
- PHY calibration through supervisor PLL, TX DCC, RX VCO/CDR/DPLL, common calibration, and raw/always-on calibration status offsets.
- Link training and signal integrity through adaptation, AFE/CTLE/VGA/DFE/slicer, signal-detect, phase/IQ, and equalization handoff offsets.
- Display engine and PHY ownership handoff through ASIC, PCS, PMA, and raw lane override/input/output offsets.
- Diagnostics through LBERT, RX statistic counters/matchers, FSM monitors, IRQ status/clear/mask, OCLA selection, and analog test-bus/status offsets.
- Multi-lane access through repeated lane families, where a wrong concrete lane prefix can program a valid but incorrect lane.

## Risks and Failure Modes

- Incorrect offset values can program the wrong hardware register even when the field shift/mask is correct, causing link training, power sequencing, or calibration failures that compile cleanly.
- CR0/CR1 namespace confusion is high risk because similar register families recur under different offset bases. A valid CR0 offset used in a CR1 path, or the reverse, can silently target unrelated hardware.
- Lane prefix mistakes can produce asymmetric failures that appear only for particular lane counts, lane mappings, rates, connectors, or hotplug sequences.
- Generic `LANEX`/`RAWLANEX`/`RAWAONLANEX` template offsets must stay aligned with numbered lane instances. Divergence can break generated table expansion or lane-generic helper code.
- Override and handoff offsets are sensitive. Writing an ASIC/PCS/PMA override register instead of an observed input/output mirror can force software ownership of signals that hardware sequencing expects to control.
- Power and timing offsets are order-sensitive. Bad P-state or power-up timer addresses can leave analog supplies, clocks, deserializers, or CDR/VCO resources enabled too early, too late, or not at all.
- Calibration and status aliases can have side effects or stale-read hazards depending on hardware semantics. Misaddressed DCC ack, VCO status, adaptation done, IRQ clear, or statistic stop registers can hide real failures.
- This chunk starts and ends mid-family, so final per-file synthesis must reconcile partial boundary coverage with neighboring chunks before claiming complete RAWAON lane coverage.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Compile-time coverage: DPCS 4.2.0 display/PHY code builds without missing `ixDPCSSYS_CR0_*` or `ixDPCSSYS_CR1_*` offset symbols.
- Generated-header consistency: every offset consumed by register tables has a matching shift/mask register name in companion generated headers where field access is required.
- Register-table sanity: CR0 and CR1 instances use the correct namespace bases, and repeated lane/register families preserve expected spacing across lane instances.
- DP/link smoke tests: hotplug, modeset, link retraining, lane-count changes, link-rate changes, suspend/resume, GPU reset, and power-gating recovery on displays that exercise CR0 and CR1 paths.
- PHY bring-up checks: supervisor PLL readiness, rtune/bandgap/reference-clock setup, TX/RX P-state transitions, VCO/CDR/DPLL lock, DCC acknowledgement, adaptation done, and signal-detect readback.
- Signal-integrity checks: AFE/CTLE/VGA/DFE/slicer convergence, phase/IQ adjustment, RX statistics counters, LBERT error counts, and stable behavior across cable/sink/link-rate combinations.
- Interrupt and observability checks: raw lane IRQ request/clear/mask behavior, FSM fast-state monitors, OCLA selections, PCS/PMA/ASIC input/output mirrors, and analog status/test-bus readbacks.

## Chunk Notes

This is a source-tree-aligned chunk report only. It intentionally does not create the final per-file synthesis for `dpcs_4_2_0_offset.h`; that merge is left for the reconciliation lane after all chunks for this generated header are available.

### subset-b-002285: lines 4860-7245

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h lines 4860-7245

## Scope

This chunk is part of AMD DPCS 4.2.0 generated ASIC register metadata. It contains C preprocessor definitions for indirect PHY/register-file offsets, not executable code. The covered range starts at the final `DPCSSYS_CR1_RAWAONLANE2` always-on lane offset, continues through the remaining `DPCSSYS_CR1` raw always-on lane, supervisor, lane, and raw-lane aliases, then enters the `dpcssys_cr2_rdpcstxcrind` address block and covers most of the CR2 indirect register map through `DPCSSYS_CR2_SUPX_ANA_MPLLA_ATB2`.

The definitions are consumed by AMD display/link encoder register-list macros and register access helpers. They provide the numeric CR-space offsets that pair with shift/mask metadata from the sibling `dpcs_4_2_0_sh_mask.h` file and with the outer `regDPCSSYS_CR*_DPCSSYS_CR_ADDR` / `regDPCSSYS_CR*_DPCSSYS_CR_DATA` MMIO access windows defined earlier in this offset header.

## Purpose

The purpose of this header range is to encode the hardware address contract for DPCS CR1 and CR2 DisplayPort/PHY control registers:

- CR1 lane 3 and lane-X always-on receive calibration/adaptation offsets, including AFE/CTLE/DFE calibration, RX phase adjustment, signal detect, vref, DCC, MPLL, firmware configuration, and transceiver-mode controls.
- CR1 supervisor-X digital and analog offsets for ID code, reference clock overrides, MPLLA/MPLLB overrides, spread-spectrum clocking, charge-pump controls, prescaler, level, ASIC input mirrors, bandgap, RTUNE, MPLL power/timer/calibration, analog status, and MPLL analog registers.
- CR1 lane-X digital/analog and raw-lane-X offsets for ASIC override/in/out, TX power control, RX power control, RX stat counters, TX/RX analog overrides, MPHY low-speed controls, PCS transfer controls, RX adaptation/FSM fast paths, OCLA, and ATE hooks.
- CR2 supervisor digital/analog offsets at low CR addresses, followed by lane 0-3 per-lane digital/analog offsets. Lanes 1 and 2 expose the fuller RX-side register set, while lanes 0 and 3 in this chunk expose the reduced TX/stat-oriented subset.
- CR2 raw common offsets for common/MPLL control, SRAM initialization, firmware/PCS ID codes, AON common RTUNE values, power-gate and supervisor overrides, vref stats, and reference range/misc configuration.
- CR2 raw lane 0-3 offsets and lane-X aliases for PCS transfer, RX adaptation direction/FOM, FSM fast startup/adaptation/calibration sequencing, TX/RX control, PLL state, loss-of-signal, data-enable overrides, continuous offset/adaptation status, and ATE overrides.
- CR2 raw always-on lane 0-3 and lane-X offsets for per-lane AON calibration/status mirrors, including DFE, RX adapt, signal detect, vref, RX DCC calibration, TX DCC bank programming, MPLL background control, firmware configuration, and transceiver mode.
- CR2 supervisor-X aliases beginning at 0x8000. The range ends mid-block after the first MPLLA analog test-bus offsets, so later supervisor-X analog offsets are outside this chunk.

This is source-tree-aligned low-level display PHY metadata. Its correctness determines whether later display/link code reaches the intended PHY control/status register when programming or diagnosing link clocks, lane power, lane training, DP alternate mode behavior, analog calibration, and PHY firmware-assisted adaptation.

## Important APIs, Types, And Macros

There are no C functions or types declared in this chunk. The important interface is the generated macro namespace:

- `ixDPCSSYS_CR1_*` and `ixDPCSSYS_CR2_*` define indirect CR-space offsets. Driver code uses these through indexed register macros such as `SRI_IX()` and related register-list helpers.
- `DPCSSYS_CR1_*` and `DPCSSYS_CR2_*` prefixes identify the DPCS CR instance. Earlier in the same file, each CR instance has an address/data MMIO pair used to access these indirect offsets.
- `SUP`, `SUPX`, `RAWCMN`, `LANE{0..3}`, `LANEX`, `RAWLANE{0..3}`, `RAWLANEX`, `RAWAONLANE{0..3}`, and `RAWAONLANEX` encode the hardware sub-block and whether the define is instance-specific or an X alias.
- Suffixes such as `MPLLA_OVRD_IN`, `MPLLB_SSC_STEPSIZE_*`, `TX_PWRCTL_*`, `RX_PWRCTL_*`, `RX_STAT_*`, `ANA_*`, `PCS_XF_*`, `FSM_*`, `RX_CTL_*`, `RX_DCC_CAL_*`, and `TX_DCC_*` describe the target register function.

Important register families in this chunk include:

- `DPCSSYS_CR1_RAWAONLANE3_DIG_*` and `DPCSSYS_CR1_RAWAONLANEX_DIG_*` at offsets 0x4300-0x4351 and 0x7000-0x7051.
- `DPCSSYS_CR1_SUPX_DIG_*` and `DPCSSYS_CR1_SUPX_ANA_*` at offsets 0x8000 and above.
- `DPCSSYS_CR1_LANEX_DIG_*`, `DPCSSYS_CR1_LANEX_ANA_*`, `DPCSSYS_CR1_RAWMEM_DIG_*`, and `DPCSSYS_CR1_RAWLANEX_DIG_*` at offsets 0x9000, 0x90e0, 0xd000, and 0xe000 ranges.
- `DPCSSYS_CR2_SUP_DIG_*` / `SUP_ANA_*` at 0x0000-0x0096.
- `DPCSSYS_CR2_LANE0..3_DIG_*` and `DPCSSYS_CR2_LANE0..3_ANA_*` at 0x1000-0x13ff.
- `DPCSSYS_CR2_RAWCMN_DIG_*` at 0x2000-0x2040.
- `DPCSSYS_CR2_RAWLANE0..3_DIG_*` at 0x3000-0x33c8.
- `DPCSSYS_CR2_RAWAONLANE0..3_DIG_*` and `DPCSSYS_CR2_RAWAONLANEX_DIG_*` at 0x4000-0x4351 and 0x7000-0x7051.
- `DPCSSYS_CR2_SUPX_DIG_*` and the beginning of `DPCSSYS_CR2_SUPX_ANA_*` at 0x8000-0x804a.

The corresponding field definitions live in DPCS shift/mask headers. The display stack's link encoder code references related DPCS/RDPCS fields through macros such as `LE_SF()`, `SRI_IX()`, `SRII()`, `REG_GET()`, and `REG_UPDATE()`.

## Control Flow

This chunk has no runtime control flow. It affects runtime behavior when register helper macros expand symbolic register names into offsets:

- A display resource constructor selects the ASIC generation's register tables.
- Link encoder or HPO DP link encoder constructors populate register addresses from generated offset macros.
- Runtime link programming calls use helpers such as `REG_GET()` and `REG_UPDATE()` to read or write PHY/link fields.
- For indirect DPCS CR registers, the access path programs the CR address selector and reads/writes the paired CR data register. The `ixDPCSSYS_CR*_*` constants in this chunk are the selector values.
- Link bring-up, training, power transitions, DP alternate mode, and diagnostics then depend on these offsets reaching the intended PHY sub-block.

Concrete flows influenced by these offsets include link encoder checks of DP alternate mode disable state, writes to DPALT disable acknowledgment, reference clock enable/disable, lane TX/RX power-state changes, MPLL and spread-spectrum programming, raw-lane FSM/adaptation controls, and reads of RX/stat/analog status. The field-level shifts and masks are elsewhere; this chunk supplies the target register identity.

## State And Persistence Behavior

The file itself stores no software state. It describes persistent hardware register state and readback locations:

- Supervisor and supervisor-X registers hold PLL, reference clock, spread-spectrum, charge pump, bandgap, prescaler, RTUNE, power timer, and analog override state. These settings persist in the DPCS PHY until reset, power collapse, or explicit reprogramming.
- Lane digital registers hold ASIC override inputs, TX/RX power-state programming, DCC bank controls, TX clock alignment, loopback/BERT controls, MPHY controls, and per-lane status-counter configuration.
- Lane analog registers hold TX and RX analog override, measurement, termination, equalization, slicer, calibration, signal-detect, and test-bus state.
- Raw common and raw lane registers expose lower-level common/MPLL, PCS, FSM, adaptation, OCLA, and ATE state. Many of these are diagnostic or calibration paths and may be live only while the PHY or firmware controller is active.
- Always-on raw lane registers expose calibration/status mirrors that can remain relevant across parts of the normal lane power sequence, including RX adapt done/FOM, DFE/phase/vref values, signal detect, DCC calibration codes, and firmware configuration.
- Status-style offsets such as `*_STATUS`, `*_STAT`, `*_FAST_FLAGS`, `*_ADAPT_DONE`, `*_INIT_PWRUP_DONE`, `*_SRAM_INIT_DONE`, and `*_OVRD_OUT` reflect hardware state rather than software-owned values. Misaddressing these can produce misleading diagnostics without an obvious compile failure.

Persistence is hardware-dependent. The header does not express reset values, write-one-to-clear behavior, ordering requirements, or access widths; consumers must rely on the ASIC register specification and matching shift/mask metadata for that.

## Dependencies And Integration Points

Primary dependencies:

- The same file's earlier `regDPCSSYS_CR*_DPCSSYS_CR_ADDR` and `regDPCSSYS_CR*_DPCSSYS_CR_DATA` macros provide the outer MMIO windows for CR0-CR4 indirect access. This chunk provides many of the inner selector offsets for CR1 and CR2.
- `dpcs_4_2_0_sh_mask.h` supplies field shifts and masks that pair with these offsets.
- AMD display register-access macros depend on the generated symbol names being exact. `SRI_IX()` style macros concatenate block, instance, and register names into the `ixDPCSSYS_CR*_*` constants represented here.
- Link encoder code in the display tree uses DPCS/RDPCS register tables and field lists to manage DisplayPort PHY/link behavior. Older DCN link encoder code directly references DPCS CR raw-lane RX override registers, while HPO DP encoder code uses RDPCS PHY control fields for DPALT and lane state.
- `soc21_enum.h` contains enum values for RDPCSPIPE controls such as clock, FIFO, interrupt, DPALT, and PHY programming. Those enums provide semantic values that can be written through register offsets/masks in the DPCS/RDPCS register interface.

Concrete integration signals in this tree:

- `display/dc/dcn201/dcn201_link_encoder.h` uses `SRI_IX(RAWLANE*_DIG_PCS_XF_RX_OVRD_IN_*)` with `DPCSSYS_CR` instances and field-list entries for `DPCSSYS_CR0_RAWLANE0_DIG_*`; this is the same generated indirect-register family represented for CR1/CR2 in this chunk.
- `display/dc/dcn201/dcn201_link_encoder.c` reads and updates RDPCS DPALT control fields during DP alternate mode handling.
- `display/dc/dio/dcn20/dcn20_link_encoder.h` lists many RDPCS PHY fields for lane power, TX enable/disable, MPLL divider/fractional/SSC programming, FIFO control, and clock control. DPCS 4.2.0 offsets are the generation-specific address side of equivalent link/PHY programming.
- `display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.*` and `display/dc/hpo/dcn32/dcn32_hpo_dp_link_encoder.c` use RDPCSTX/RDPCS register tables for HPO DP link encoders and inspect `RDPCS_PHY_DPALT_DISABLE`.
- DCN resource files such as `dcn31_resource.c`, `dcn314_resource.c`, `dcn315_resource.c`, and `dcn316_resource.c` instantiate RDPCSTX register lists for multiple link encoders. Newer DCN 4.x resource files show related lists commented out in some configurations, which makes generation-specific coverage important.

## Risks

- Generated-header drift is high impact. A wrong offset can compile cleanly while redirecting a CR access to a different PHY register.
- CR instance confusion is easy in this range. CR1 and CR2 contain many similarly named `SUP`, `SUPX`, `LANE`, `LANEX`, `RAWLANE`, `RAWLANEX`, `RAWAONLANE`, and `RAWAONLANEX` symbols with repeated offset patterns. A CR1/CR2 prefix mismatch can target the wrong link instance.
- Lane symmetry is partial. Lanes 1 and 2 expose fuller RX power/control/analog sets than lanes 0 and 3 in this chunk. Code assuming every lane has identical offsets can reference nonexistent or wrong addresses.
- X aliases require care. `LANEX`, `RAWLANEX`, `RAWAONLANEX`, and `SUPX` are alias-style register sets, not ordinary per-lane instance names. Consumers must know how the hardware maps the X register path.
- The chunk starts and ends on partial block boundaries. It begins with the final CR1 RAWAONLANE2 offset and ends partway through CR2 SUPX analog definitions, so whole-file analysis must merge adjacent chunks before drawing completeness conclusions.
- PLL, SSC, charge-pump, power-state, and DCC offsets are sensitive. Misprogramming can cause link-training failure, unstable clocks, display blanking, high error rates, or resume failures.
- Calibration/status offsets are often used only during difficult diagnostic paths. Incorrect offsets may escape normal boot tests and surface only under marginal signal integrity, DP alt-mode toggles, link-rate changes, or low-power transitions.
- Raw/ATE/OCLA paths can expose manufacturing or debug controls. Accidental writes through a bad register table could perturb live link operation or produce misleading debug captures.

## Test Signals

Useful validation signals for changes touching this header or its generator:

- Compile coverage for the display driver with DPCS 4.2.0 headers enabled. Missing or renamed symbols should fail in register-list or field-list macro expansion.
- Mechanical diff against vendor-generated DPCS 4.2.0 register headers or the authoritative register database. For generated offset headers, this is the strongest validation signal.
- Boot/probe smoke tests on ASICs using DPCS 4.2.0, confirming display resource creation and link encoder initialization without invalid MMIO/CR access.
- DisplayPort link bring-up across lane counts and link rates, including HBR/HBR2/HBR3/UHBR where applicable, to exercise MPLL, SSC, lane power, TX/RX adaptation, and raw-lane FSM offsets.
- DP alternate mode and USB-C retimer/dock scenarios, validating DPALT disable/acknowledge handling and PHY mux/ref-clock behavior.
- Hotplug, unplug, suspend/resume, and low-power display idle tests to catch stale supervisor/lane power state, MPLL power timer, SRAM init, and always-on calibration issues.
- Link-training stress with eye/PHY margin diagnostics, BERT/loopback where available, and RX stat counter readback to validate stat/status offsets.
- Protected debug validation using OCLA/ATE/test-bus paths only in controlled environments, confirming debug offsets read expected lane/common state without disrupting normal display output.

## Notes For Merge Lane

This chunk should be reconciled with neighboring `dpcs_4_2_0_offset.h` chunks before producing the final per-file report. The range is entirely generated register metadata, but it crosses a major address-block boundary at `dpcssys_cr2_rdpcstxcrind` and has partial boundaries at both ends. The final report should describe the full DPCS 4.2.0 offset file alongside its matching shift/mask header and the display link encoder register-table consumers.

### subset-b-002286: lines 7246-9631

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

### subset-b-002287: lines 9632-11973

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h lines 9632-11973

## Purpose

This chunk is a generated AMD DPCS 4.2.0 register-offset header slice. It contains no executable C logic; it publishes preprocessor constants for DisplayPort PCS / PHY control registers used by AMDGPU display code.

The requested range contains 2,330 `#define` entries. It starts at the tail of the `DPCSSYS_CR3` indirect CR address space, covers the full `addressBlock: dpcssys_cr4_rdpcstxcrind`, and ends with a small `RDPCSPIPE*_RDPCSPIPE_PHY_CNTL6` shift/mask and register-offset shim. The CR4 block provides indirect-register offsets for supervisor/common PLL state, per-lane digital and analog PHY controls, raw always-on lane registers, raw common registers, raw memory windows, and raw lane PCS/PMA/FSM/IRQ/TX/RX controls.

Although this file is under a local `ceph-client` source tree, this chunk is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this chunk. The exported interface is macro metadata:

- `ixDPCSSYS_CR3_*`: indirect DPCS CR3 register offsets. This chunk only contains the CR3 tail, ending CR3 lane analog TX/RX offsets, raw memory windows, and raw lane PCS/PMA/FSM/IRQ/TX/RX offsets.
- `ixDPCSSYS_CR4_*`: indirect DPCS CR4 register offsets. This is the dominant block in the range and covers the complete CR4 generated namespace.
- `RDPCSPIPE0_RDPCSPIPE_PHY_CNTL6__*` and `RDPCSPIPE1_RDPCSPIPE_PHY_CNTL6__*`: local shift/mask definitions for `RDPCS_PHY_DPALT_DP4`, `RDPCS_PHY_DPALT_DISABLE`, and `RDPCS_PHY_DPALT_DISABLE_ACK` bits.
- `regRDPCSPIPE[0-4]_RDPCSPIPE_PHY_CNTL6` plus `_BASE_IDX`: direct MMIO offsets for the two real RDPCSPIPE instances, aliased across five logical transmitters.

The main CR4 offset families are:

- `SUP_DIG` and `SUP_ANA`: supervisor/common control offsets for ID code, reference-clock overrides, MPLLA/MPLLB dividers, HDMI clocking, SSC peak/stepsize programming, charge-pump controls, prescalers, bandgap/level controls, RTUNE, MPLL analog readback/override, and common output/status registers.
- `SUPX_DIG` and `SUPX_ANA`: extended supervisor offsets for alternate-bus, ATB, PLL calibration, PFD, DCC, PLL miscellaneous, reserved, and LC tank controls.
- `RAWCMN_DIG_*`: raw common digital offsets for MPLL loop observation/control, fast FSM state/status, ATE override and status, PLL status, clock observation, and common/raw memory access helpers.
- `RAWAONLANE[0-3]` and `RAWAONLANEX`: always-on per-lane offsets for PCS/PMA boundary controls, reset/power-state request and acknowledge IRQs, DCC on-demand IRQs, PMA lane override/status, raw TX/RX control, RX PWRUP controls, and rate controls.
- `LANE[0-3]` and `LANEX`: per-lane digital and analog offsets for PCS/PMA transfer signals, FSM controls/status, IRQ controls, TX/RX override paths, equalization/adaptation, DCC status, PMA lane/supervisor interfaces, TX FSM/clocking/DCC, RX FSM/LOS/data/adaptation status, ATE controls, and analog TX/RX calibration, termination, ATB, CDR, squelch, and power controls.
- `RAWLANE[0-3]` and `RAWLANEX`: raw per-lane offsets for the same PCS/PMA/FSM/IRQ/TX/RX/ATE surfaces, generally used through indirect CR addressing.
- `RAWMEM_DIG_ROM_CMN0_B0_R0` and `RAWMEM_DIG_RAM_CMN0_B0_R0`: raw ROM/RAM memory windows.

The `LANEX`, `RAWLANEX`, and `RAWAONLANEX` forms are generic lane-X aliases alongside explicit lane 0-3 instances. In this chunk, CR4 has 1,189 lane-family defines, 625 raw-lane defines, 278 supervisor defines, 52 raw-common defines, and 2 raw-memory defines.

## Control Flow

This header has no runtime control flow. Its constants are consumed by register-table construction and by register-helper macros in the AMD display driver:

1. `dcn31_resource.c` includes `dpcs_4_2_0_offset.h` and the matching `dpcs_4_2_0_sh_mask.h`.
2. DCN31 resource initialization expands `DPCS_DCN31_REG_LIST(id)` into per-link encoder register tables, including `RDPCSTX_PHY_CNTL*`, `RDPCSPIPE_PHY_CNTL6`, `RDPCS_TX_CR_ADDR`, and `RDPCS_TX_CR_DATA`.
3. Runtime link encoder paths use shared `REG_GET`, `REG_UPDATE`, and related helpers against those tables.
4. DPCS indirect accesses use the direct CR address/data registers from earlier chunks of this same file together with `ixDPCSSYS_CR*_*` offsets from this and adjacent chunks.
5. USB-C DP-alt-mode legacy detection reads `RDPCS_PHY_DPALT_DISABLE` and `RDPCS_PHY_DPALT_DP4` from either `RDPCSTX_PHY_CNTL6` or `RDPCSPIPE_PHY_CNTL6`, depending on ASIC revision and transmitter routing.

The macros do not encode sequencing. PHY power-up/down, MPLL setup, lane rate/width programming, DP alt-mode query order, reset acknowledgement, training, suspend/resume restore, and interrupt acknowledgement are all controlled by consumer code and hardware rules outside this header.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible DPCS state:

- Supervisor/common state for reference clocks, MPLLA/MPLLB programming, SSC, PLL calibration, prescalers, bandgap, RTUNE, and analog test/readback buses.
- Per-lane PCS/PMA state for TX/RX override paths, lane number, data enable, rate/width, equalization/adaptation, termination, PMA interfaces, and loopback/test controls.
- FSM and calibration state for RX startup, RX adaptation, AFE/DFE/reflvl/IQ calibration, VCO wait/calibration, continuous calibration/adaptation, DCC flags/status, and common calibration status.
- IRQ state for RX/TX reset/request/rate/pstate/adaptation events, lane transceiver mode changes, RX phase-2 calibration, RX-to-TX serial loopback, and DCC on-demand events.
- Analog TX/RX state for DCC DACs, power overrides, termination code, clocks, CDR, squelch, calibration, ATB measurement/force registers, and reserved silicon fields.
- DP-alt-mode state in `RDPCSPIPE_PHY_CNTL6` for whether DP alt mode is disabled, whether 4-lane DP-alt operation is present, and the disable acknowledgement bit.

Persistence is hardware-defined. Configuration fields generally remain until the driver reprograms the link, the PHY is reset or power-gated, suspend/resume restores state, or a GPU/ASIC reset occurs. Status and IRQ fields may be read-only, sticky, write-one-to-clear, self-clearing, or only valid while relevant DPCS clocks and power domains are active. The offset header does not describe those access semantics.

## Dependencies And Integration Points

This generated offset header must stay synchronized with the matching generated shift/mask header and AMD's DPCS 4.2.0 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h` supplies field shifts and masks for the offsets named here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` directly includes this file and builds DCN31 link encoder and HPO DP link encoder register/shift/mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h` defines `DPCS_DCN31_REG_LIST()` and `DPCS_DCN31_MASK_SH_LIST()`, which expect the `RDPCSTX*`, `RDPCSPIPE*`, and DPCS CR register names from this generated header family.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.c` uses `RDPCSTX_PHY_CNTL6` and `RDPCSPIPE_PHY_CNTL6` fields to detect USB-C DP-alt-mode disablement and 2-lane versus 4-lane DP-alt capability on legacy paths.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.h` and `.c` include `RDPCSTX_PHY_CNTL6[5]` in HPO DP link encoder state and read `RDPCS_PHY_DPALT_DISABLE`.

The behavioral integration point for this chunk is display link bring-up, especially DCN31 DisplayPort/USB-C PHY handling. The CR4 indirect offsets describe low-level PHY and lane state, while the RDPCSPIPE tail directly supports DP-alt-mode decisions that can cap link lane count or decide whether a USB-C DP path is usable.

## Risks And Edge Cases

- These constants are untyped preprocessor values. A wrong offset, base index, shift, or mask can compile cleanly while reading or writing the wrong hardware register or bit.
- The file is generated metadata. Manual edits can diverge from the authoritative AMD register database, the matching `dpcs_4_2_0_sh_mask.h`, firmware expectations, or silicon documentation.
- The chunk boundary is artificial. It starts in the CR3 tail and then covers CR4; the CR3 address block starts in earlier chunks, and whole-file conclusions require merge-lane reconciliation.
- `LANEX` and `RAWLANEX` aliases sit beside explicit lane 0-3 offsets. Consumers must select the correct generic or per-lane symbol; mixing them can silently target the wrong indirect lane context.
- The `RDPCSPIPE only has 2 instances` note is important. Logical instances 2 and 4 alias instance 0, and logical instance 3 aliases instance 1. Code that assumes five independent RDPCSPIPE register banks can misread DP-alt-mode state or mask a per-transmitter issue.
- The DP-alt-mode fields affect link capability. A bad `RDPCS_PHY_DPALT_DP4` or `RDPCS_PHY_DPALT_DISABLE` definition can incorrectly permit four lanes on a two-lane USB-C alt-mode path, cap a valid four-lane path to two lanes, or report the connector as unavailable.
- Low-level PHY controls are timing and power sensitive. Wrong MPLL, DCC, RX adaptation, CDR, termination, power, or calibration offsets can cause link training failures, intermittent high-rate failures, hotplug-only failures, or resume-only regressions.
- IRQ and status offsets are side-effect-sensitive. Confusing request, acknowledge, clear, mask, or status registers can produce missed PHY events, stuck reset handshakes, or interrupt storms.
- Analog/test-bus and ATE registers should not be treated as ordinary runtime controls. Accidental writes can disturb calibration, lane measurement, or production-test state.

## Test Signals

Useful validation combines generated-header consistency checks with display link behavior:

- Build AMDGPU display support for DCN31. Missing or renamed macros should surface in `dcn31_resource.c`, `dcn31_dio_link_encoder.h`, and `dcn31_hpo_dp_link_encoder.h`.
- Mechanically compare lines 9632-11973 against AMD's authoritative DPCS 4.2.0 register database and the adjacent DPCS 4.2.x generated headers where the CR4 layout is expected to match.
- Cross-check every `ixDPCSSYS_CR4_*` register used by the matching shift/mask header has a corresponding offset here, and verify the `RDPCSPIPE*_RDPCSPIPE_PHY_CNTL6` shift/mask definitions match the field layout used by `DPCS_DCN31_MASK_SH_LIST()`.
- Add or run static checks for lane-family consistency across `LANE0-3`, `LANEX`, `RAWLANE0-3`, `RAWLANEX`, `RAWAONLANE0-3`, and `RAWAONLANEX`, while allowing intentional per-lane address differences.
- Exercise DisplayPort and USB-C DP-alt-mode links on DCN31-class hardware across all transmitters, including 2-lane and 4-lane alt-mode docks/cables. Expected signals are correct max lane-count selection, successful link training, and no false unavailable-link reports.
- Test ASIC revision paths that choose `RDPCSTX_PHY_CNTL6` versus `RDPCSPIPE_PHY_CNTL6`, especially Yellow Carp B0 handling in `dcn31_dio_link_encoder.c`.
- Exercise hotplug, unplug, suspend/resume, link retraining, low-power entry/exit, high bit-rate modes, and HPO DP paths while watching for DPCS register timeouts, stuck reset acknowledgements, failed calibration/adaptation, DP-alt-mode misdetection, and training instability.
- Use register dumps around `RDPCS_TX_CR_ADDR`/`RDPCS_TX_CR_DATA` indirect accesses to confirm CR4 offsets address the intended supervisor, lane, raw lane, raw common, and raw memory windows.

## Cross-Chunk Notes

The previous chunk owns most of the `DPCSSYS_CR3` address block. This chunk begins at the final CR3 lane and raw-lane offsets, then owns the full `DPCSSYS_CR4` indirect address block and the RDPCSPIPE compatibility tail before the file's `#endif`. The final per-file research document should merge this with earlier chunks before making whole-file claims about all DPCS 4.2.0 instances, all direct MMIO offsets, or all indirect CR address spaces.
