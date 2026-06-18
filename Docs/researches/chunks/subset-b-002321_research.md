# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 78684-81059

## Purpose

This chunk is generated AMD DPCS 4.2.0 register field metadata for the `DPCSSYS_CR3` display PHY/control-register space. It contains no executable C logic; it exports preprocessor constants that describe bit positions and bit masks for 245 hardware register blocks in one oversized header. The chunk has 2,132 `#define` entries: 1,066 `__SHIFT` constants and 1,066 matching `_MASK` constants.

The visible register groups cover three related CR3 hardware regions:

- `DPCSSYS_CR3_RAWAONLANEX_*`: raw always-on lane digital fields for RX DFE/adaptation, signal detection, calibration, TX/RX disable overrides, firmware calibration/adaptation configuration, lane transceiver mode, and TX/RX DCC controls.
- `DPCSSYS_CR3_SUPX_*`: supervisor/common PHY fields for ID codes, refclock/bandgap controls, MPLLA/MPLLB dividers, HDMI clocking, spread-spectrum clocking, fractional-N PLL values, charge-pump values, ASIC input mirrors, analog bandgap/prescaler/RTUNE controls, MPLL power-control status/timers/calibration, RTUNE status/config counters, and analog override outputs.
- `DPCSSYS_CR3_LANEX_*`: lane-level digital/ASIC TX and RX override/mirror fields, loopback, AC JTAG, TX request/pstate/rate/width/data-enable/drive controls, RX CDR/VCO/equalizer/termination controls, lane-master and repeat/shift handshakes, OCLA gates, and TX power-state programming for P0, P0s, P1, and the beginning of P2.

The source tree path is under a local `ceph-client` mirror, but this file is AMDGPU display-driver hardware metadata rather than distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, local includes, allocations, or locks in this chunk. The API surface is the generated macro namespace:

- `DPCSSYS_CR3_<register>__<field>__SHIFT`: the bit offset of a field within a DPCS register.
- `DPCSSYS_CR3_<register>__<field>_MASK`: the bit mask for the same field.

Every field visible in this range has both a shift and a mask definition. The largest complete register block in the chunk is `DPCSSYS_CR3_RAWAONLANEX_DIG_FAST_FLAGS`, with 16 fields and 32 generated macro lines. Common field shapes include single-bit enable/value pairs, multi-bit numeric fields such as DFE tap values, PLL multipliers, fractional-N values, RTUNE values, TX main/pre/post cursors, RX VCO load values, pstate/rate/width selectors, and many `RESERVED_*` masks that protect unused upper bits.

Important macro families in this slice include:

- DFE, RX adaptation, and fast-calibration controls: `DIG_DFE_*_VDAC_OFST`, `DIG_RX_ADPT_*`, `DIG_RX_ADAPT_DONE`, `DIG_FAST_FLAGS`, and `DIG_FAST_FLAGS_2`.
- Signal detection and RX analog controls: `DIG_RX_LOS_MASK_CTL`, `DIG_RX_SIGDET_*`, `DIG_RX_OVRD_OUT_*`, `DIG_SIGDET_OUT_*`, and `DIG_RX_VREFGEN_EN`.
- Calibration and DCC fields: `DIG_CAL_*`, `DIG_RX_DCC_CAL_*`, `DIG_TX_DCC_*`, `DIG_MPLL_BG_CTL`, `DIG_LANE_CMNCAL_*_STATUS`, and `DIG_MPLL_DISABLE`.
- Firmware and lane-mode fields: `DIG_FW_MM_CONFIG`, `DIG_FW_ADPT_CONFIG`, `DIG_FW_CALIB_CONFIG`, `DIG_LANE_XCVR_MODE_*`, and `DIG_TXRX_OVRD_IN`.
- Supervisor PLL/refclock fields: `SUPX_DIG_REFCLK_OVRD_IN`, `SUPX_DIG_MPLLA_*`, `SUPX_DIG_MPLLB_*`, `SUPX_DIG_ASIC_IN`, `SUPX_DIG_LVL_ASIC_IN`, charge-pump fields, SSC peak/stepsize fields, and HDMI/divider clock fields.
- Analog supervisor fields: `SUPX_ANA_PRESCALER_CTRL`, `SUPX_ANA_RTUNE_CTRL`, `SUPX_ANA_BG*`, `SUPX_ANA_MPLLA_*`, `SUPX_ANA_MPLLB_*`, plus digital analog override outputs such as `SUPX_DIG_ANA_MPLLA_OVRD_OUT_*`, `SUPX_DIG_ANA_MPLLB_OVRD_OUT_*`, `SUPX_DIG_ANA_RTUNE_OVRD_OUT`, and `SUPX_DIG_ANA_BG_OVRD_OUT`.
- Lane TX/RX fields: `LANEX_DIG_ASIC_LANE_*`, `LANEX_DIG_ASIC_TX_*`, `LANEX_DIG_ASIC_RX_*`, `LANEX_DIG_ASIC_RX_EQ_*`, `LANEX_DIG_ASIC_RX_CDR_VCO_*`, and `LANEX_DIG_TX_PWRCTL_TX_PSTATE_*`.

## Control Flow

This chunk has no runtime control flow. The runtime sequence is supplied by AMD display code that includes the matching offset and mask headers and then token-pastes register and field names into register helper tables.

The observed integration path for this specific header is `display/dc/resource/dcn31/dcn31_resource.c`, which includes both `dpcs/dpcs_4_2_0_offset.h` and `dpcs/dpcs_4_2_0_sh_mask.h`. That file materializes `DPCS_DCN31_REG_LIST(id)` into link encoder register tables and appends `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` / `DPCS_DCN31_MASK_SH_LIST(_MASK)` to the link encoder shift and mask tables. The helper pattern in display code then feeds `REG_GET`, `REG_SET`, `REG_UPDATE`, and related macros with register offsets from the offset header and field metadata from this mask header.

The constants in this chunk do not encode hardware sequencing. Consumers still must order refclock, bandgap, PLL, RTUNE, TX/RX power state, lane width/rate, DFE/adaptation, signal detection, and calibration programming according to the link encoder and PHY initialization flows.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes MMIO-backed hardware state. The represented state is broad:

- RX equalization/adaptation state, including DFE tap values, CTLE/VGA/ATT adaptation results, slicer controls, bypass/error values, RX IQ phase adjustment, RX adaptation-done flags, and fast-start/continuous calibration flags.
- Calibration and signal-detection state, including LOS mask counters, HF/LF signal-detect filters and thresholds, signal-detect override inputs/outputs, DCC calibration codes, TX DCC bank address/data/continuous enable, RTUNE set/status/config counters, and supervisor analog compare/status bits.
- Clocking and PLL state for MPLLA/MPLLB, including coarse tune, disable flags, divider/HDMI clock controls, PLL enable/standby/reset/calibration bits, fractional-N quotient/remainder/denominator fields, SSC peak/stepsize fields, charge-pump proportional/integral fields, power-control status, timers, DAC max range, and spread type.
- Analog supervisor state, including bandgap selections, prescaler and RTUNE analog controls, MPLL analog miscellaneous/control/test/ATB fields, analog override outputs, PMIX controls, and bandgap/reset/ref-vreg override outputs.
- Lane TX/RX state, including loopback/ACJTAG controls, TX request/pstate/rate/width/data-enable/disable/beacon/cursor/HDMI mode/DC-coupling/reset fields, RX request/data/pstate/rate/width/CDR/SSC/align/termination/PWM/equalizer fields, lane master/repeater shift handshakes, and TX P0/P0s/P1/P2 power-state enable/reset/data/RX-detect/VBOOST/DCC-cal bits.

Persistence is entirely hardware-defined. Some fields are configuration bits that likely retain values until modeset, power gating, suspend/resume, or reset; others are status, mirror, calibration-result, override-enable, or self-clearing/handshake bits. The header does not identify access direction or side effects, so any read/modify/write behavior must be inferred from hardware programming guides and consuming driver code.

## Dependencies And Integration Points

This chunk depends on consistency with adjacent generated AMD register headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h` supplies the matching `ixDPCSSYS_CR3_*` register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h` defines the `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST` macros that select DPCS fields for link encoder register structs.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` includes this file and builds the concrete DCN 3.1 link encoder register, shift, and mask tables.
- The display register helper layer consumes the resulting tables through token-pasted field names and helper macros such as `FD`, `FN`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

The chunk is part of a generated family. Searches show equivalent register names in related `dpcs_4_2_2`, `dpcs_4_2_3`, and broader `dcn_4_1_0` mask headers, sometimes with different masks or reserved layouts. That makes ASIC-version pairing important: the 4.2.0 offset and shift/mask headers should be used together, not mixed with another revision.

## Risks And Edge Cases

- Bitfield drift is the central risk. These are untyped preprocessor constants, so a wrong shift/mask can compile cleanly while corrupting adjacent fields or programming the wrong hardware behavior.
- Offset/mask version mismatches are dangerous. The register offsets live in `dpcs_4_2_0_offset.h`, while this chunk only supplies field layout; mixing revisions can silently target valid offsets with invalid bit layouts.
- Many fields affect live PHY behavior: PLL enable/reset/calibration, refclock/bandgap control, RTUNE, TX/RX pstate/rate/width, TX drive cursors, RX CDR/VCO/equalizer settings, signal detect, loopback, and lane master/shift handshakes. Incorrect values can cause link-training failures, blank display, intermittent hotplug, poor signal margin, audio/video instability over HDMI/DP, or resume failures.
- Override fields commonly have value and enable bits. Setting an override value without the matching enable, or leaving an enable asserted after calibration/debug use, can create mode-specific or board-specific failures.
- Reserved masks are present throughout the chunk. Read/modify/write helpers should preserve reserved bits unless the hardware programming sequence explicitly requires otherwise.
- The chunk boundaries are artificial. The first lines continue the tail of `DPCSSYS_CR3_RAWAONLANEX_DIG_DFE_DATA_EVEN_LOW_VDAC_OFST` from the previous chunk, and the final line stops at the `TX_P2_ANA_DCC_COMP_CAL_EN_MASK` field before the trailing reserved mask for `DPCSSYS_CR3_LANEX_DIG_TX_PWRCTL_TX_PSTATE_P2`.

## Test Signals

Because this file is generated metadata, direct unit tests are unlikely. Useful validation signals are compile-time and hardware-path oriented:

- Build coverage for AMDGPU display configurations that include DCN 3.1 resources; missing or renamed macros should fail when `dcn31_resource.c` expands the DPCS register and mask lists.
- Static consistency checks can verify each visible `__SHIFT` macro has a matching `_MASK` macro and that the selected field names match the register/mask list declarations in `dcn31_dio_link_encoder.h`.
- ASIC-version checks should ensure `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h` are paired in include sites.
- Runtime display smoke tests should cover DP and HDMI link bring-up, link training across lane counts and rates, hotplug/EDID, suspend/resume, MST where applicable, and modes that exercise TX power states P0/P0s/P1/P2.
- Hardware debug signals include DPCS register dumps before and after link training, PLL lock/calibration status, RTUNE status, signal-detect outputs, RX adaptation done/status, and comparison against known-good register dumps for the same ASIC revision.
