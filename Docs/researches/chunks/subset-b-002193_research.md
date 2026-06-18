# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 103205-105623

## Chunk Scope

This chunk covers lines 103205-105623 of the generated DCN 4.1.0 register shift/mask header. It is a partial chunk of the full `dcn_4_1_0_sh_mask.h` file, not the final per-file research document. The visible range starts inside `DPCSSYS_CR1_LANEX_DIG_RX_ADPTCTL_DAC_CTRL_SEL_3`, continues through many `DPCSSYS_CR1_*` DisplayPort/PHY lane control/status registers, crosses the `addressBlock: dpcssys_cr2_rdpcstxcrind` boundary, and ends at the beginning of `DPCSSYS_CR2_SUP_DIG_LVL_OVRD_IN`.

The chunk is declarative C preprocessor data: every meaningful source line is a `#define` naming a hardware register bitfield shift or mask. There are no functions, structs, enums, static data objects, or executable branches in this range.

## Purpose

The purpose of this range is to expose bitfield layouts for DCN 4.1.0 DPCS/DPCSSYS hardware registers to AMDGPU display code. Driver code includes this header alongside offset headers and uses the `__SHIFT` and `_MASK` constants to compose register writes, extract register reads, and build register-field tables for the DCN 4.0.1/4.1 generation.

The covered hardware area is mostly link PHY and DisplayPort/USB-C serializer/deserializer plumbing:

- `DPCSSYS_CR1_LANEX_DIG_RX_STAT_*` describes RX statistic counters, pattern matching, sample-count control, comparator clock control, and statistic stop fields.
- `DPCSSYS_CR1_LANEX_DIG_MPHY_RX_*` exposes MPHY RX PWM, termination, and PWM clock-stability fields.
- `DPCSSYS_CR1_LANEX_DIG_ANA_*` and `DPCSSYS_CR1_LANEX_ANA_*` expose digital override/status views of analog TX/RX controls: TX clocks/data, termination codes, equalization, voltage regulation, slicers, DAC control, signal detect, DCC DACs, VCO, calibration, ATB measurement, and power controls.
- `DPCSSYS_CR1_RAWLANEX_DIG_PCS_XF_*`, `PMA_XF_*`, `FSM_*`, `IRQ_CTL_*`, `TX_CTL_*`, and `RX_CTL_*` expose raw-lane PCS/PMA transfer controls, finite-state-machine observation/fast-start controls, lane IRQ status/clear/mask bits, ATE overrides, adaptation handshakes, loopback, lane number, and TX/RX control/status fields.
- `DPCSSYS_CR2_SUP_DIG_*` starts a second address block for supervisor/common PHY digital controls, including ID code, reference clock overrides, MPLLA/MPLLB clock and spread-spectrum controls, fractional-N parameters, charge-pump overrides, RTUNE/TX calibration, prescaler controls, and common state outputs.

## Important APIs, Types, And Macros

This chunk exports macro constants only. The naming convention is:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the already-shifted bit mask for the same field.
- Comment lines such as `//DPCSSYS_CR1_RAWLANEX_DIG_FSM_FAST_RX_STARTUP_CAL` mark the register whose fields follow.
- The address block comment `// addressBlock: dpcssys_cr2_rdpcstxcrind` marks the transition from CR1 lane/rawlane register fields to CR2 supervisor register fields.

Representative field groups in this range:

- RX statistics and pattern matching: `DPCSSYS_CR1_LANEX_DIG_RX_STAT_LD_VAL_1`, `DATA_MSK`, `MATCH_CTL0` through `MATCH_CTL5`, `STAT_CTL0` through `STAT_CTL2`, `SMPL_CNT1`, `STAT_CNT_0` through `STAT_CNT_6`, `CAL_COMP_CLK_CTL`, and `STAT_STOP`.
- Analog override/status: `DPCSSYS_CR1_LANEX_DIG_ANA_TX_OVRD_OUT`, `ANA_TX_TERM_CODE_OVRD_OUT`, `ANA_TX_EQ_OVRD_OUT_0` through `_5`, `ANA_RX_CTL_OVRD_OUT`, `ANA_RX_PWR_OVRD_OUT`, `ANA_RX_VCO_OVRD_OUT_0` through `_2`, `ANA_RX_CAL`, `ANA_RX_DAC_CTRL`, `ANA_RX_AFE_ATT_VGA`, `ANA_RX_AFE_CTLE`, `ANA_RX_SCOPE`, `ANA_RX_SLICER_CTRL`, `ANA_STATUS_0`, `ANA_STATUS_1`, `ANA_SIGDET_OVRD_OUT_1/_2`, and `ANA_TX_DCC_DAC_OVRD_OUT`.
- Raw analog TX/RX fields: `DPCSSYS_CR1_LANEX_ANA_TX_OVRD_MEAS`, `ANA_TX_PWR_OVRD`, `ANA_TX_ALT_BUS`, `ANA_TX_ATB1/ATB2`, `ANA_TX_DCC_CTRL1`, `ANA_TX_TERM_CODE_CTRL`, `ANA_TX_OVRD_CLK`, `ANA_TX_MISC1/MISC2`, `ANA_TX_VREG_CTRL`, `ANA_RX_CLK_1/2`, `ANA_RX_CDR_DES`, `ANA_RX_SLC_CTRL`, `ANA_RX_PWR_CTRL1/2`, `ANA_RX_SQ`, `ANA_RX_CAL1/2`, `ANA_RX_ATB_*`, `ANA_RX_VDAC_RANGE`, `ANA_RX_CDR_VREG`, and `ANA_RX_VREG_CTRL`.
- PCS/PMA transfer fields: `DPCSSYS_CR1_RAWLANEX_DIG_PCS_XF_TX_OVRD_IN`, `TX_PCS_IN`, `TX_OVRD_OUT`, `RX_OVRD_IN`, `RX_PCS_IN`, `RX_OVRD_OUT`, `RX_ADAPT_ACK`, `RX_ADAPT_FOM`, `RX_TXPRE_DIR`, `RX_TXMAIN_DIR`, `RX_TXPOST_DIR`, `LANE_NUMBER`, `ATE_*`, `RX_EQ_*`, `TXRX_TERM_CTRL_*`, and `RX_PH2_CAL`.
- FSM and IRQ fields: `DPCSSYS_CR1_RAWLANEX_DIG_FSM_*` covers calibration/adaptation fast path toggles, flags, lock/status monitors, TX DCC flags/status, OCLA hooks, CMNCAL/RCAL status, and IQ phase offset. `DPCSSYS_CR1_RAWLANEX_DIG_IRQ_CTL_*` covers RX/TX reset/request/rate/pstate/adaptation/phase-cal/loopback/DCC IRQ bits, clear bits, and masks.
- CR2 supervisor fields: `DPCSSYS_CR2_SUP_DIG_REFCLK_OVRD_IN`, MPLLA/MPLLB div/HDMI clock overrides, `MPLLA_OVRD_IN_0..5`, `MPLLB_OVRD_IN_0..5`, `MPLLA/MPLLB_SSC_PEAK_*`, `MPLLA/MPLLB_SSC_STEPSIZE_*`, charge-pump override fields, `SUP_OVRD_IN`, `PRESCALER_OVRD_IN`, `SUP_OVRD_OUT`, and the first field of `LVL_OVRD_IN`.

The masks in this range are mostly 16-bit values with `L` suffixes because many DPCS indirect PHY registers expose 16-bit fields, even though they are manipulated through normal C integer operations. A few names include reserved fields; these are important because generated field tables often preserve the full register layout even when driver code should avoid writing reserved bits.

## Control Flow

There is no runtime control flow in the chunk. Behavior is created by downstream display code that uses these constants with AMD register helper macros and register accessors.

The effective usage pattern is:

1. A DCN 4.1.0 source file includes this shift/mask header and a matching offset header.
2. Register table macros bind `ix...` offsets to these `__SHIFT` and `_MASK` field constants.
3. Driver code reads or writes hardware registers using helpers that isolate fields by mask and shift.
4. Hardware, not this header, performs the actual control transitions: PHY lane startup, RX/TX calibration, adaptation, spread-spectrum PLL programming, IRQ reporting/clearing, and status counter updates.

The lack of code flow makes correctness entirely dependent on generated numeric constants matching the silicon register specification and the companion offset header.

## State And Persistence Behavior

This header itself stores no software state and has no persistence behavior. Its constants describe persistent and transient hardware state held in DPCS/DPCSSYS registers.

State represented by the chunk includes:

- RX statistic latches and counters (`STAT_CNT_*`, `SMPL_CNT1_DONE`, `SC1_START`, `SC1_STOP`).
- TX/RX analog override enables and values, which can force hardware states that would otherwise be controlled by PHY firmware or state machines.
- Calibration and adaptation request/status bits in raw-lane FSM fields.
- IRQ pending, clear, and mask fields for lane RX/TX events.
- Supervisor PLL state: MPLLA/MPLLB enable, divider, standby, frequency, fractional-N, spread-spectrum peak/stepsize, charge-pump, and clock synchronization controls.
- Common calibration and acknowledgement signals such as RTUNE, reference clock acknowledgement, background state, and TX calibration code fields.

Persistence is hardware-defined. Some bits are configuration fields that remain until reset or reprogramming; some are status/ack bits updated by hardware; some are write-one-to-clear style IRQ clear fields as implied by the `_IRQ_CLR` register names. Driver code must treat reserved fields as non-owned state and preserve them with read-modify-write where required.

## Dependencies

Direct dependencies are preprocessor-level:

- Include guard `_dcn_4_1_0_SH_MASK_HEADER` encloses the full header.
- Consumers include this file directly from DCN 4.0.1/4.1 display code, including `display/dmub/src/dmub_dcn401.c`, `display/dc/irq/dcn401/irq_service_dcn401.c`, `display/dc/resource/dcn401/dcn401_resource.c`, `display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c`, and DCN401 GPIO translation/factory files.
- The masks must line up with companion offset definitions in the generated register headers. The same register names appear in DPCS offset headers such as `dpcs_4_2_0_offset.h`, `dpcs_4_2_2_offset.h`, `dpcs_4_2_3_offset.h`, and `dpcs_3_1_4_offset.h`, which provide `ixDPCSSYS_*` address constants for comparable blocks.
- Downstream accessors in the AMD display driver expect the register/field macro naming scheme to be stable so token-pasting macros can refer to `<reg>__<field>__SHIFT` and `<reg>__<field>_MASK`.

There are no local library dependencies, allocation requirements, locking rules, or runtime initialization order within this header.

## Integration Points

The chunk integrates with the AMDGPU DC and DMUB display stack by providing silicon-specific field layout for DCN401-era hardware. Likely integration surfaces include:

- Link encoder and PHY programming paths that bring DisplayPort/USB-C lanes up and down, perform link training, change rates, or switch modes.
- Clock manager paths that program reference clocks, MPLL dividers, HDMI clock selection, fractional-N, and spread-spectrum settings.
- IRQ service paths that decode lane reset/request/rate/pstate/adaptation/phase-cal events and write clear/mask fields.
- GPIO and board-resource discovery code that indirectly depends on the same header for the full DCN401 register namespace.
- DMUB firmware interface support code that may need field definitions for register table initialization or debug operations.
- Hardware debug and bring-up tooling paths using OCLA, ATE, ATB, status monitors, fast FSM controls, and override registers.

Because this is a generated register header, its most important integration contract is consistency across three things: silicon documentation, offset headers, and the code-generated register tables in AMD display sources.

## Risks And Edge Cases

- A single wrong shift or mask can silently program the wrong PHY field, causing link-training failures, intermittent display blanking, bad equalization, incorrect PLL programming, or unhandled IRQ storms.
- CR1 lane/rawlane fields and CR2 supervisor fields share similar names but live under different indirect address blocks. Mixing an offset from one block with a mask from the other would compile but access the wrong hardware semantics.
- Many fields are one-bit controls beside wide reserved masks. Downstream code must not use the reserved masks as writable ownership unless the hardware spec explicitly allows it.
- Some names imply write-to-clear behavior (`*_IRQ_CLR`). Treating those as ordinary persistent state can drop interrupts or fail to acknowledge them.
- PLL and clock fields (`MPLLA_*`, `MPLLB_*`, `FRACN_*`, `SSC_*`, `CLK_SYNC_*`) are timing-sensitive. Incorrect mask widths can produce valid-looking register values that create unstable clocking.
- Analog override fields can bypass hardware state machines. Using these definitions in debug or bring-up paths without restoring automatic control can leave lanes in forced states across modesets or suspend/resume.
- The chunk begins and ends mid-register-context: it starts after the comment for `DPCSSYS_CR1_LANEX_DIG_RX_ADPTCTL_DAC_CTRL_SEL_3` and ends just after the first `DPCSSYS_CR2_SUP_DIG_LVL_OVRD_IN` shift. The merge lane must combine adjacent chunks before making whole-file claims about all fields.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration oriented:

- Kernel/AMDGPU build succeeds for DCN401 display code with this header included by DMUB, IRQ, resource, clock-manager, and GPIO sources.
- Register table generation or macro expansion tests catch missing `__SHIFT`/`_MASK` pairs for fields referenced by DCN401 code.
- Static comparison against the authoritative register database confirms each mask matches `((1 << width) - 1) << shift` and that every field belongs to the correct CR1 or CR2 address block.
- Display bring-up succeeds across DP and USB-C paths at multiple link rates/lane counts, with no link-training regressions.
- Modeset, hotplug, suspend/resume, and MST scenarios show no persistent forced analog override state and no IRQ clear/mask regressions.
- Clock and PLL tests verify stable MPLLA/MPLLB programming, fractional-N settings, spread-spectrum behavior, and HDMI/DP clock selection.
- Debug or manufacturing paths using ATE/ATB/OCLA and fast FSM controls still read/write expected fields when compared with hardware traces or register dumps.

## Research Notes For Merge Lane

This chunk should be merged with neighboring chunks of `dcn_4_1_0_sh_mask.h` before final file-level conclusions are written. The final report should emphasize that this file is generated, macro-only, and part of the AMD DCN register-definition layer. For this specific chunk, the central topic is DPCS/DPCSSYS lane PHY and supervisor bitfield definition rather than display policy or filesystem behavior.
