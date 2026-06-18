# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h lines 1-2484

## Purpose

This chunk is generated AMD DPCS 4.2.3 register-offset metadata. It contains no executable C logic; it publishes preprocessor constants that map symbolic DisplayPort/Display PHY Control Subsystem register names to numeric offsets and, for direct MMIO registers, matching `_BASE_IDX` selectors. The values are consumed by AMDGPU display code to build register tables for DCN 3.1.6-class hardware.

The requested range is the first 2,484 lines of a larger 11,969-line header. It covers the license/header guard, direct MMIO offsets for DPCSSYS CR apertures, panel power sequencers, RDPCS transmitters/pipes, DCIO, GPIO, and UNIPHY reserved macro-control blocks, then begins the `dpcssys_cr0_rdpcstxcrind` indirect register address map. In this range there are 2,373 `#define` lines. The direct-register portion consistently pairs `reg...` offsets with `reg..._BASE_IDX`, and every direct `_BASE_IDX` in this chunk is `2`. The indirect CR-register portion uses `ixDPCSSYS_CR0_...` index constants without `_BASE_IDX` companions because those values are written through CR address/data windows rather than used as standalone MMIO offsets.

Although the path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, allocation paths, or locking primitives in this range. The interface is the generated macro namespace:

- `reg<block>_<register>`: a direct MMIO register offset in the DPCS/DCIO register space.
- `reg<block>_<register>_BASE_IDX`: the base-address segment selector used by register helper macros when computing an absolute MMIO address.
- `ixDPCSSYS_CR0_<register>`: an indirect CR register index for the CR0 RDPCS transmitter/PHY register window.

Major direct-register families in this slice:

- `regDPCSSYS_CR0` through `regDPCSSYS_CR4`: CR address/data access windows at repeated link offsets, each exposing `DPCSSYS_CR_ADDR` and `DPCSSYS_CR_DATA`.
- `regPWRSEQ0` and `regPWRSEQ1`: panel power-sequencer GPIO enable/control/mask/Y registers, panel power state/control/delay/reference-divider registers, backlight PWM control/period/lock registers, and spare registers.
- `regRDPCSTX0` through `regRDPCSTX4`: repeated RDPCS transmitter blocks for control, clock control, interrupt control, PLL update data, CR address/data access, SRAM control, scratch/spare/debug, PHY control registers 0-17, PHY fuse registers, DPALT/DMCU controls, `DPALT_CONTROL_REG`, `RDPCS_CNTL3`, and PLL update override address/data.
- `regRDPCSPIPE0` and `regRDPCSPIPE1`: pipe-level `RDPCSPIPE_PHY_CNTL6`. The chunk also contains explicit bring-up aliases for `regRDPCSPIPE2`, `regRDPCSPIPE3`, and `regRDPCSPIPE4`, with an in-file comment that the driver should not need RDPCS registers after bring-up cleanup.
- `regDC_*`, `regDCIO_*`, `regUNIPHYA` through `regUNIPHYE`, `regINTERCEPT_STATE`, `regPHY_AUX_CNTL`, and `regAUXI2C_PAD_ALL_PWR_OK`: DCIO clock/reference/pinstrap/reset/debug/link-routing registers, UNIPHY link and channel crossbar controls, GPIO mask/data/enable/Y registers for generic/DDC/HPD/genlock/power-sequencer pads, pad strength, AUX controls, pull-ups, RX enable, and AUX/I2C power-good state.
- `regDCIO_UNIPHY1` through `regDCIO_UNIPHY4`: each exposes `UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED57` as contiguous direct offsets for macro-level control/reserved slots.

The indirect CR0 table begins at line 1229 and includes:

- `ixDPCSSYS_CR0_SUP_DIG_*` and `ixDPCSSYS_CR0_SUP_ANA_*`: supervisor digital/analog ID, refclk override, MPLLA/MPLLB override, spread-spectrum, prescaler, ASIC input/status, bandgap, charge pump, power timing, RTUNE, and analog status indices.
- `ixDPCSSYS_CR0_LANE0` through partial `LANE3`: per-lane ASIC override/input/output, TX power-state and DCC controls, RX power/VCO/CDR/adaptation/status controls, LBERT, DPLL, MPHY, analog TX/RX override/status/calibration/measurement controls. The chunk covers full lane 0, lane 1, lane 2, and the TX/status-oriented beginning of lane 3.
- `ixDPCSSYS_CR0_RAWCMN_*`: common raw PCS/PHY control, MPLL override, SSC, lane FSM, SRAM init, OCLA, firmware/PCS ID, always-on RTUNE values, power-gating, VREF, resistor, and reference-range controls.
- `ixDPCSSYS_CR0_RAWLANE0` through partial `RAWLANE3`: PCS/PMA cross-interface overrides, RX adaptation and lane-numbering controls, FSM status/fast calibration controls, IRQ/status/clear/mask controls, PMA override/monitor registers, TX/RX control/status, and ATE/debug indices.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by the AMDGPU display driver:

1. DCN 3.1.6 resource code includes this file together with `dpcs_4_2_3_sh_mask.h`.
2. Resource/register table macros paste block names and instance IDs into constants such as `regRDPCSTX0_RDPCSTX_PHY_CNTL6`, `regPWRSEQ0_PANEL_PWRSEQ_CNTL`, or `ixDPCSSYS_CR0_LANE1_DIG_RX_CDR_CDR_CTL_0`.
3. Direct `reg...` values are combined with their `_BASE_IDX` segment to access MMIO registers through the driver register helpers.
4. Indirect `ix...` values are used as CR indices behind the CR address/data windows exposed by `regDPCSSYS_CR*_DPCSSYS_CR_ADDR`, `regDPCSSYS_CR*_DPCSSYS_CR_DATA`, and the equivalent RDPCS TX CR address/data aliases.
5. Higher-level display code performs the actual ordering for power sequencing, link enablement, PHY setup, PLL updates, DisplayPort/alternate-mode training, interrupt handling, and diagnostic reads.

The macros do not encode access permissions, timing, polling, read-modify-write masks, or side effects. Consumers must pair them with the matching shift/mask header and the hardware programming sequence for the active ASIC.

## State And Persistence Behavior

The chunk stores no software state and persists nothing to disk. It describes hardware state reachable through MMIO and CR-indirect access windows. The represented state includes:

- Panel/backlight sequencing state: GPIO ownership, panel power targets/current state, delay counters, PWM control/period/locking, and power-sequencer reference dividers.
- RDPCS transmitter and PHY state: clocks, interrupts, PLL update data/overrides, SRAM control, debug/scratch registers, PHY control and fuse-visible values, DPALT controls, and CR address/data windows.
- DCIO and GPIO state: DCIO clock/reference control, pinstraps, soft reset, link/channel crossbar mapping, genlock/swaplock pads, DDC/HPD/generic/power-sequence GPIO masks/data/enables/Y values, pad strengths, AUX controls, RX/pull-up enables, and pad power-good status.
- UNIPHY macro-control reserved state for several repeated PHY instances.
- CR0 supervisor/lane/common/raw-lane state: MPLL and spread-spectrum controls, power timing, RTUNE calibration, analog status, lane TX/RX power/CDR/VCO/adaptation/calibration, FSM and interrupt status, PMA/PCS override paths, and test/debug controls.

Persistence is hardware-defined. Configuration registers may retain values until modeset, power gating, suspend/resume, link reset, or ASIC reset. Status, interrupt, clear, calibration, debug, and override registers can be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive. This offset header does not identify those semantics; field definitions and consuming code determine correct access patterns.

## Dependencies And Integration Points

This chunk depends on AMD's generated DPCS 4.2.3 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h` for field shifts and masks.
- SOC/DCN base-address definitions used by AMDGPU register helpers to interpret `_BASE_IDX == 2`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which directly includes this offset header and the matching shift/mask header.

The broader integration pattern is generated-register token pasting. DCN resource code initializes register structures from symbolic names; HPO DP link encoder and panel-control paths consume RDPCS, DPCSSYS, DCIO, GPIO, and PWRSEQ register definitions through those structures. The companion mask header supplies fields such as RDPCS PHY DP alternate-mode disable bits and panel power-sequencer/backlight bits, while this file supplies only numeric addresses or CR indices.

The CR-indirect names are especially tied to the direct CR access windows in the same chunk: a driver must program an `ixDPCSSYS_CR0_*` index through the appropriate `DPCSSYS_CR_ADDR`/`DPCSSYS_CR_DATA` or RDPCS TX CR address/data pair for the target PHY instance. Using an `ix...` constant as a direct MMIO offset would be wrong.

## Risks And Edge Cases

- Offset or base-index drift is the central risk. These macros are untyped constants, so an incorrect address or `_BASE_IDX` can compile cleanly while targeting the wrong hardware register.
- Direct and indirect namespaces are easy to confuse. `reg...` constants are MMIO offsets with base-index companions; `ix...` constants are CR indices. Mixing the two access mechanisms can corrupt unrelated registers or fail silently.
- Repeated instance blocks are copy-sensitive. `CR0`-`CR4`, `RDPCSTX0`-`RDPCSTX4`, `PWRSEQ0`-`PWRSEQ1`, `UNIPHY1`-`UNIPHY4`, lanes, and raw lanes have regular spacing but are not interchangeable in a live modeset. Instance mistakes may only appear on a particular connector, lane count, panel path, or DP alternate-mode path.
- The `RDPCSPIPE2`-`RDPCSPIPE4` aliases are explicitly marked as bring-up hacks. Code that grows new dependencies on those aliases would preserve temporary hardware access assumptions and could break when the generated map or cleanup changes.
- Power-sequencing and GPIO registers are side-effect-sensitive. Wrong masks, enables, delays, or PWM/register-lock offsets can cause blank eDP panels, backlight failures, bad HPD/DDC/AUX behavior, or suspend/resume regressions.
- PHY and CR-indirect controls affect high-speed link training and calibration. Bad MPLL, RTUNE, DCC, CDR, VCO, RX adaptation, or lane override addresses can produce intermittent link failures, rate/lane-specific instability, DisplayPort alternate-mode failures, or diagnostics that only fail on certain boards.
- The chunk boundary is artificial. It stops inside the `RAWLANE3` CR0 raw-lane register table; adjacent chunks are required for the full `dpcs_4_2_3_offset.h` map and for any file-level conclusions about all DPCS instances.

## Test Signals

- Compile coverage for `dcn316_resource.c` and any generated register tables that include `dpcs_4_2_3_offset.h` is the baseline signal; missing or renamed macros should fail at build time.
- Static consistency checks are valuable: each direct `reg...` macro in this chunk should have a matching `_BASE_IDX`, all direct base indices in this slice should remain `2`, repeated instance blocks should preserve expected spacing, and `ix...` CR indices should not be paired with `_BASE_IDX`.
- Boot and modeset tests on DCN 3.1.6 hardware should exercise connector detection, HPD, DDC/EDID, AUX/DPCD access, eDP panel power sequencing, backlight PWM, suspend/resume, and multi-display routing through the DCIO/UNIPHY/RDPCS tables.
- DisplayPort link-training tests should cover multiple link rates and lane counts, DP alternate-mode paths, hotplug cycles, and error recovery so RDPCS TX, PLL, PHY, CR-indirect, raw-lane, and interrupt offsets are exercised.
- Hardware diagnostics should watch for register read/write timeouts, AUX failures, link-training failures, HPD storms, blank panels, missing backlight, PHY calibration errors, and lane-specific instability. These are the practical failure signatures for incorrect offsets in this header.
