# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h lines 1-2405

## Scope

This chunk covers lines 1-2405 of `drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h` under the Ceph client source mirror. It includes the MIT license/header guard and the first two `dpcssys_*_rdpcstxcrind` address blocks:

- Full `dpcssys_cr0_rdpcstxcrind` offset map, starting at line 30 and running through the CR0 raw lane/X aliases.
- Start of `dpcssys_cr1_rdpcstxcrind`, from line 2096 through `ixDPCSSYS_CR1_LANE1_DIG_RX_STAT_STAT_CTL1` at line 2405.

Within the 1-2405 range there are 2,370 `ixDPCSSYS_*` register-offset macros: 2,062 for `CR0` and 308 for the beginning of `CR1`. The full source file is 7,215 lines; later chunks cover the rest of CR1/CR2 and the display decoder/PWRSEQ address maps.

## Purpose

This file is a generated ASIC register offset header for AMD DPCS version `3_1_4`. It provides symbolic C preprocessor constants for indexed DPCS register offsets used by AMDGPU display code. The names encode the hardware hierarchy:

- `DPCSSYS`: DisplayPort/PHY/clocking subsystem register namespace.
- `CR0` and `CR1`: clock/recovery or PHY register-bank instances. This chunk fully maps `CR0` and starts `CR1`.
- `SUP`, `SUPX`: supervisor/common PLL and analog support register regions.
- `LANE0` through `LANE3`, plus `LANEX`: per-lane PHY/DIG/ANA register regions and a generic lane alias.
- `RAWCMN`, `RAWLANE*`, `RAWAONLANE*`, `RAWLANEX`, `RAWAONLANEX`: raw common, raw per-lane, and always-on raw lane register views.

The header has no executable behavior. Its functional role is to keep hard-coded MMIO/indexed-register offsets out of C logic and to make call sites use named constants when programming or reading DPCS PHY state.

## Important API Surface

The only exported API is macro definitions guarded by `_dpcs_3_1_4_OFFSET_HEADER`. There are no structs, functions, enums, inline helpers, or storage definitions in this chunk.

Key macro families in the chunk:

- `ixDPCSSYS_CR0_SUP_DIG_*` and `ixDPCSSYS_CR1_SUP_DIG_*`: supervisor digital registers for ID code, refclk overrides, MPLLA/MPLLB overrides, SSC programming, MPLL power-control status/timers/calibration, clock/reset timing, RTUNE configuration/status, and analog override outputs.
- `ixDPCSSYS_CR0_SUP_ANA_*` / `ixDPCSSYS_CR0_SUPX_ANA_*`: analog supervisor controls for prescaler, RTUNE, bandgap, and power measurement.
- `ixDPCSSYS_CR0_LANE*_DIG_ASIC_*`: ASIC-facing per-lane override/input/output registers. Lane 0 and lane 3 in this chunk are mostly TX/status focused; lanes 1 and 2 include fuller RX calibration/adaptation sets.
- `ixDPCSSYS_CR0_LANE*_DIG_TX_PWRCTL_*`: TX p-state and power-up timing registers, with DCC DAC controls and `TX_LBERT_CTL`.
- `ixDPCSSYS_CR0_LANE*_DIG_RX_PWRCTL_*`, `RX_VCOCAL_*`, `RX_CDR_*`, `RX_ADPTCTL_*`, and `RX_STAT_*`: RX p-state, VCO calibration, CDR, adaptation, and receiver statistic/counter controls for RX-capable lane views.
- `ixDPCSSYS_CR0_LANE*_DIG_ANA_*` and `ixDPCSSYS_CR0_LANE*_ANA_*`: digital-to-analog override/status and raw analog TX/RX register offsets, including TX equalization, term-code, DCC, RX AFE, CTLE, slicer, phase, signal detect, and ATB measurement registers.
- `ixDPCSSYS_CR0_RAWCMN_DIG_*`: raw common controls for common lane FSM extension, MPLL state, SRAM init status, OCLA, PCS/FW ID codes, AON common RTUNE values, and common power/resource overrides.
- `ixDPCSSYS_CR0_RAWLANE*_DIG_*`: raw PCS/PMA/FSM/IRQ/TX/RX control views for each lane. These expose PCS crossbar override/input/output, RX adaptation acknowledgements/FOM, fast FSM calibration/adaptation steps, interrupt status/clear/mask registers, PMA crossbar, and TX/RX control status.
- `ixDPCSSYS_CR0_RAWAONLANE*_DIG_*`: always-on lane state such as AFE/DFE calibration offsets, adaptation results, signal-detect calibration, RX DCC calibration, TX DCC bank access, firmware config, and lane transceiver mode inputs.
- Generic aliases `CR0_RAWAONLANEX`, `CR0_SUPX`, `CR0_LANEX`, and `CR0_RAWLANEX`: X-suffixed offset templates for programming a selected lane/supervisor view through a common indexed aperture.

The macro values are offsets, not absolute CPU physical addresses. The file comments state `base address: 0x0` for both CR0 and CR1 indexed blocks in this chunk.

## Control Flow

There is no runtime control flow in this header. At compile time, including C files can reference these constants in register read/write expressions. Runtime ordering is determined by the caller, typically AMDGPU display, link training, PHY initialization, diagnostics, or power-management routines.

The implicit control pattern supported by these offsets is:

1. Select or address the DPCS indexed register aperture for the target CR/lane/register block.
2. Write override/control registers such as `*_OVRD_IN`, `*_PSTATE_*`, `*_MPLL_PWR_CTL_*`, `*_ADPT_CFG_*`, or IRQ clear/mask offsets.
3. Poll or read status registers such as `*_STAT`, `*_STATUS`, `*_ADAPT_DONE`, `*_INIT_PWRUP_DONE`, `*_VCO_STAT_*`, `*_LBERT_ERR`, or receiver statistic counters.
4. Use per-lane or X-alias offsets according to whether the code is targeting a fixed hardware lane or a generic lane-selected path.

Because this chunk is only offsets, it does not define access width, bit fields, masking, locking, polling loops, timeouts, or reset sequencing. Those are expected to come from paired mask/shift headers and from AMDGPU display code.

## State And Persistence

This header persists symbolic definitions in the compiled driver. It does not allocate memory or persist runtime state by itself.

The hardware registers named here represent volatile device state. Important state classes exposed by this chunk include:

- PLL and clock state: MPLLA/MPLLB overrides, SSC peak/stepsize/spread-type fields, MPLL power-control status/timers/calibration, refclk and prescaler controls.
- Power and reset state: TX/RX p-states, power-up timing, bandgap/ref power-up timing, reset-related IRQs, and low-speed/MPHY controls.
- Calibration/adaptation state: RTUNE values, RX VCO calibration, CDR/DPLL state, AFE/CTLE/VGA/DFE adaptation controls and status, DCC DAC and calibration banks.
- Diagnostic/test state: LBERT controls/errors, OCLA hooks, IRQ masks/clear/status, PCS/PMA raw override paths, statistic sample/match/counter registers, ATB measurement registers, and firmware ID/config registers.

Any persistence across suspend/resume, GPU reset, display hotplug, or mode set depends on higher-level AMDGPU display code reprogramming these hardware registers from driver state. This header only supplies the offsets required for that reprogramming.

## Dependencies

Direct dependencies are minimal:

- C preprocessor include guard `_dpcs_3_1_4_OFFSET_HEADER`.
- AMDGPU include conventions for ASIC register headers, especially `ix*` naming for indexed-register offsets.
- Pairing with adjacent generated register definition headers, commonly mask/shift headers for the same DPCS IP version, so callers can combine an offset macro with bit-field masks.

There are no Linux kernel includes, type dependencies, function declarations, or module-level dependencies in this chunk.

## Integration Points

Likely consumers are AMDGPU DRM display/DM/DCN code paths that configure DPCS PHY, DisplayPort/HDMI transmit lanes, link training, signal integrity, and PHY diagnostics. The integration contract is purely symbolic: a call site includes this header, selects a named `ixDPCSSYS_*` offset, and passes that offset to AMD register access helpers.

Important integration details:

- The offset namespace is IP-version-specific (`dpcs_3_1_4`), so it must match the ASIC/IP block selected by the driver. Using these offsets on a different DPCS revision can target the wrong hardware register.
- CR0 and CR1 macro values intentionally repeat many numeric offsets because they are separate indexed blocks. The instance prefix is part of the semantic address even when the offset literal is the same.
- X-suffixed macros (`LANEX`, `RAWLANEX`, `RAWAONLANEX`, `SUPX`) are not simple duplicates of lane-specific macros; they expose generic/indirect address windows starting at distinct ranges such as `0x7000`, `0x8000`, `0x9000`, and `0xe000`.
- This chunk stops mid-CR1, at lane1 RX stat control. Any research or generated final document must not infer that the CR1 map ends here.

## Risks And Edge Cases

- Register drift risk: generated headers must match the ASIC register database. A single stale offset can silently misprogram PHY power, PLL, training, or diagnostic controls.
- Instance confusion: CR0 and CR1 reuse many offset values. Callers must use the correct access path/address block, not just the numeric offset.
- Lane asymmetry: lane 0 and lane 3 sections in this chunk are smaller TX/stat-focused subsets, while lane 1/lane 2 and generic `LANEX` include fuller RX/adaptation/analog sets. Code that assumes every lane has every macro can fail at compile time or, worse, use the wrong alias.
- Raw and public views: `RAW*` register views expose lower-level PCS/PMA/FSM/IRQ/AON controls. These are more sensitive to sequencing and are likely intended for firmware bring-up, diagnostics, or tightly ordered PHY routines.
- Partial chunk boundary: line 2405 ends in the middle of the CR1 lane1 RX stat group. Consumers of this research should reconcile with later chunks before making file-level conclusions.
- Reserved or test-oriented registers: names containing `RESERVED`, `ATE`, `OCLA`, `ATB`, and `LBERT` should be treated cautiously. They may be hardware debug/test hooks, not stable product-facing programming interfaces.

## Test Signals

Useful validation for this header is mostly build-time and hardware-integration focused:

- Compile coverage: AMDGPU display objects that include `dpcs_3_1_4_offset.h` must compile with all referenced `ixDPCSSYS_*` names present.
- Header hygiene: include guard prevents duplicate definitions; no generated macro should collide with another macro name in the same IP-version namespace.
- Register database checks: regenerated offsets should diff cleanly against this header for DPCS 3.1.4. Review any numeric change in PLL, p-state, DCC, CDR, IRQ, or adaptation-related offsets.
- Runtime bring-up tests: display link training, hotplug, suspend/resume, GPU reset recovery, and modeset tests can reveal wrong offsets through link failures, PHY calibration timeouts, blank displays, or unstable high-rate links.
- Diagnostic paths: LBERT/OCLA/stat-counter reads should return plausible values when supported by hardware; IRQ clear/mask flows should not leave stale lane events asserted.
- Static sanity checks: the chunk contains 2,370 `ixDPCSSYS_*` defines; within this slice the CR0/CR1 split is 2,062/308. A changed count is not necessarily wrong, but it is a strong signal for register database or chunk-boundary review.
