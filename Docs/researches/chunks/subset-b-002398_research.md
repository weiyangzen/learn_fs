# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 29134-31563

## Scope

This chunk is a middle slice of the generated AMDGPU DPCS 4.2.3 shift/mask header. It contains C preprocessor constants for bit positions and bit masks in DPCSSYS CR1 DisplayPort/USB-C PHY control registers. The slice begins inside `DPCSSYS_CR1_LANE2_DIG_RX_DPLL_FREQ`, continues through lane-2 RX adaptation, statistics, MPHY, analog TX/RX controls, lane-3 ASIC/TX/RX/analog controls, raw common PLL/AON/common controls, and ends inside `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_TX_PCS_IN`.

The companion address definitions live in `dpcs_4_2_3_offset.h` as `ix...` register offsets; this file supplies only `__SHIFT` and `_MASK` constants used to compose, extract, and preserve fields for those offsets.

## Purpose

The constants in this chunk are register-field metadata for low-level display PHY programming. Driver code can combine a register offset such as `ixDPCSSYS_CR1_LANE3_DIG_TX_PWRCTL_TX_PSTATE_P0` with field constants such as `DPCSSYS_CR1_LANE3_DIG_TX_PWRCTL_TX_PSTATE_P0__TX_P0_DIG_CLK_EN_MASK` and matching `__SHIFT` values to update 16-bit register fields without hard-coding bit numbers.

The covered blocks expose:

- Lane 2 RX DPLL frequency bounds and receiver adaptation configuration/status.
- Lane 2 RX statistic match/counter controls and sample count registers.
- Lane 2 MPHY PWM/termination and analog override/status registers for TX, RX, signal detect, calibration, phase, DAC, slicer, and termination controls.
- Lane 3 ASIC-facing lane/TX/RX override and status interfaces.
- Lane 3 TX power-state sequencing, DCC DAC controls, clock alignment, loopback/error-test controls, RX statistics, and analog TX controls.
- Raw common PLL, spread-spectrum, lane FSM, SRAM-init, OCLA, firmware-ID, PCS raw-ID, AON RTUNE, power-gate, supply, VREF, reset-resource, and reference-range controls.
- The start of raw lane-0 PCS TX override and PCS input fields.

## Important Defines And Register Groups

There are no C functions, structs, enums, or runtime APIs in this chunk. The public surface is a dense set of `#define`s following the generated naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned field mask, usually suffixed with `L`.
- Register names are introduced by `//<REGISTER>` comments.
- Reserved fields are explicitly named, for example `RESERVED_15_10`, which helps full-width writers preserve undocumented bits.

Key lane-2 RX blocks include `DPCSSYS_CR1_LANE2_DIG_RX_DPLL_FREQ_BOUND_0/1`, `DPCSSYS_CR1_LANE2_DIG_RX_ADPTCTL_ADPT_CFG_0` through `_9`, adaptation reset/status registers for ATT, VGA, CTLE, and DFE taps 1-5, DAC/slicer controls, CR bank address/data, and RX statistic registers such as `MATCH_CTL*`, `STAT_CTL*`, `SMPL_CNT1`, `STAT_CNT_0` through `_6`, and `STAT_STOP`.

Lane-2 analog coverage includes digital override outputs like `DIG_ANA_TX_OVRD_OUT`, `DIG_ANA_TX_EQ_OVRD_OUT_0` through `_5`, `DIG_ANA_RX_CTL_OVRD_OUT`, `DIG_ANA_RX_PWR_OVRD_OUT`, `DIG_ANA_RX_VCO_OVRD_OUT_0` through `_2`, RX calibration/DAC/slicer/scope/IQ controls, status registers, MPHY overrides, signal-detect overrides, TX DCC DAC overrides, and corresponding analog TX/RX register fields such as `ANA_TX_PWR_OVRD`, `ANA_TX_TERM_CODE`, `ANA_RX_CLK_1/2`, `ANA_RX_CDR_DES`, `ANA_RX_PWR_CTRL1/2`, `ANA_RX_CAL1/2`, and ATB measurement/force fields.

Lane-3 coverage starts at the digital ASIC interface: `DIG_ASIC_LANE_OVRD_IN`, `DIG_ASIC_TX_OVRD_IN_0` through `_5`, `DIG_ASIC_TX_OVRD_OUT`, `DIG_ASIC_RX_OVRD_OUT_0`, and matching ASIC input/output registers. It then covers `DIG_TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, and `P2`; TX power-up timers; DCC CR-bank and DAC control/status registers; `DIG_TX_CLK_ALIGN_TX_CTL_0`; `DIG_TX_LBERT_CTL`; lane-3 RX statistic registers; and lane-3 analog TX override/equalization/status/termination/DCC fields.

Raw common registers include `DPCSSYS_CR1_RAWCMN_DIG_CMN_CTL`, MPLLA/MPLLB override, bandwidth, and spread-spectrum controls, `LANE_FSM_OP_XTND`, `MPLL_STATE_CTL`, `TX_CAL_CODE`, `SRAM_INIT_DONE`, `OCLA`, `SUP_ANA_OVRD`, raw PCS/firmware ID registers, AON RTUNE triplets for RX/TXDN/TXUP values 0-7, AON SRAM built-in-load config, power-gate override input/output, supply override input, VREF status, resource override/status, reference-range override, and MPLL power-down timing.

The chunk ends after defining the first fields for raw lane-0 PCS TX controls: `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_TX_OVRD_IN`, `_OVRD_IN_1`, and the initial part of `_TX_PCS_IN`. The remaining `_TX_PCS_IN` masks and subsequent raw lane-0 PCS RX/TX registers are outside this work item.

## Control Flow

This header has no executable control flow. Its influence appears when included by AMD display/PHY driver code that performs register reads, read-modify-writes, or field packing. The intended flow is:

1. Select the register offset from the matching `dpcs_4_2_3_offset.h` `ix...` symbol.
2. Use this header's `__SHIFT` and `_MASK` symbols to encode a field value or decode a register value.
3. Write or poll the hardware register through AMDGPU display register access helpers.

Because the chunk is generated data, order mostly follows the hardware address map. The lane-2 section completes a receive/analog lane, the lane-3 section begins another lane's ASIC/TX/RX/analog sequence, and the raw common/raw lane block starts the common/lane raw PCS address space.

## State And Persistence Behavior

The macros themselves hold no state and do not persist anything. They describe persistent hardware register bits. Any stateful behavior is in the DPCS hardware and the caller:

- Power-state, reset, request/acknowledge, and override bits can change physical PHY state until overwritten, reset, or power-cycled.
- Sticky/status fields such as RX statistic counters, adaptation done bits, DCC DAC acknowledgements, VREF calibration done, SRAM init done, and resource request/ack bits report hardware state rather than software memory.
- Reserved masks indicate fields that should generally be preserved during write updates to avoid clobbering undocumented hardware state.

## Dependencies And Integration Points

This chunk depends on consumers including the full header and the paired DPCS 4.2.3 offset header. The constants are ASIC-version-specific and should be used only with the corresponding DPCS 4.2.3 register map. Other versions such as DPCS 3.1.4 and 4.2.0 have similarly named headers but must not be assumed identical without checking their generated offsets and masks.

Integration points are the AMD DRM display stack and PHY/link-training code paths that program DisplayPort/USB-C PHY lanes, PLLs, transmitter power states, receiver adaptation, calibration, and diagnostics. The common access pattern is through register macros that take a register address plus mask/shift pairs; this file supplies the latter.

## Risks And Edge Cases

- The chunk starts and ends mid-register context. `DPCSSYS_CR1_LANE2_DIG_RX_DPLL_FREQ` begins before this slice, and `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_TX_PCS_IN` continues after it. A final per-file report must merge adjacent chunks before making whole-register claims.
- These constants are generated hardware contracts. Manual edits can silently break field packing, especially for high-impact controls such as PLL force, power-gate override, lane reset, DCC calibration, TX power states, RX adaptation, and raw PCS override enables.
- Many fields are one-bit `*_OVRD_EN` plus `*_OVRD_VAL` pairs. Setting the enable without the intended value, or failing to clear it, can leave the PHY under software override rather than normal hardware control.
- Several registers expose calibration, status, counter, and reserved fields in the same 16-bit word. Callers need read-modify-write discipline and reserved-bit preservation.
- Lane naming matters. This slice mixes CR1 lane 2, CR1 lane 3, raw common, and raw lane 0 fields; using a lane-2 field mask with a lane-3 or raw-lane register that only appears similar would be an integration bug.

## Test Signals

Useful validation signals for this chunk are compile-time and hardware-oriented rather than unit-testable algorithm behavior:

- Kernel/display driver code including `dpcs_4_2_3_sh_mask.h` should compile without duplicate or missing macro errors.
- Static checks can verify every `__SHIFT`/`_MASK` pair in this chunk matches the bit width implied by the field names and does not overlap adjacent non-reserved fields within the same register.
- Register-access tests or hardware bring-up logs should show correct DPCS lane initialization, TX power-state transitions, PLL force/ack behavior, RX adaptation completion, DCC DAC acknowledgement, SRAM init done, VREF calibration done, and RX statistic counter operation.
- Regression testing should focus on display link training, hotplug/link retraining, low-power state entry/exit, USB-C/DP alternate mode PHY switching, and diagnostics that read RX statistic or calibration status fields.
