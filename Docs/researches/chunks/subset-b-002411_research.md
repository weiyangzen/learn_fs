# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 60804-63231

## Scope

This chunk is part of the generated AMD DPCS 4.2.3 register shift/mask header. It contains C preprocessor field metadata only: every exported symbol in the requested range is a `#define` for a hardware-register bit shift or bit mask. There are no C functions, structs, typedefs, enums, branches, locks, allocations, direct MMIO operations, or persistent software objects in this slice.

The range covers 2,428 source lines and 2,165 macro definitions across 261 register field blocks. The macro split is 1,160 `__SHIFT` definitions and 1,005 `_MASK` definitions. The chunk starts at the tail of `DPCSSYS_CR2_RAWLANEX_DIG_IRQ_CTL_RX_RATE_IRQ_CLR`, whose field shifts are in the prior chunk, then completes the CR2 `RAWLANEX` raw-lane IRQ/PMA/PCS/TX/RX/ATE area and crosses into the `dpcssys_cr3_rdpcstxcrind` address block. The CR3 portion covers supervisor/common digital and analog fields plus the beginning of concrete `LANE0` digital, TX power-control, RX statistics, and analog TX/DCC fields. The chunk ends in `DPCSSYS_CR3_LANE0_DIG_ANA_TX_DCC_DAC_OVRD_OUT_2`; later CR3 lane0 analog and subsequent lane/alias fields continue after this range.

Although this repository path is under `sources/distributed-fs/ceph-client`, this file is AMD GPU display hardware metadata. It has no Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header chunk is to publish exact bit positions and masks for DPCS 4.2.3 hardware registers. AMDGPU display/PHY code combines these field constants with matching `ixDPCSSYS_*` offsets from `dpcs_4_2_3_offset.h` and with generated register-table macros. That lets runtime code set, clear, poll, or decode individual hardware fields without embedding raw bit numbers throughout link, PHY, PLL, calibration, and diagnostics code.

The covered register-map areas are:

- CR2 `RAWLANEX` raw lane IRQ control fields for RX request/rate/P-state/adaptation/reset events, lane transceiver-mode events, phase-2 calibration events, RX-to-TX serial-loopback events, DCC on-demand events, and TX reset/request events. The chunk includes status, write-clear, and mask fields.
- CR2 `RAWLANEX` PMA transfer fields for lane/MPLL handshakes, supervisor state, TX request/reset/beacon/async/data enables, RX request/reset/rate/P-state/adaptation/phase-2 calibration/DCC controls, MPHY overrides, and RX adaptation handoff.
- CR2 `RAWLANEX` digital TX/RX controller fields, including TX/RX FSM power states, clock control, DCC and adaptation continuous status, OCLA/UPCS observation selectors, PCS/PMA ATE override inputs, master MPLL loop controls, and secondary override outputs.
- CR3 `SUP` digital fields for ID/refclk override, MPLLA/MPLLB div/HDMI clocks, PLL override banks, SSC peak/step-size, charge-pump controls, supervisor/prescaler/level overrides, debug, ASIC-input mirrors, bandgap inputs, MPLL power-control status/timers/calibration, clock/reset timing, RTUNE configuration/status, and analog override outputs.
- CR3 `SUP` analog fields for prescaler, RTUNE, bandgap, MPLLA/MPLLB miscellaneous/control/testbus/reserved banks, and analog MPLL override/status surfaces.
- CR3 `LANE0` fields for ASIC-facing lane/TX/RX overrides and readbacks, TX P-state programming, TX power-up timers, DCC DAC bank/address/data/control/ack fields, TX clock alignment, LBERT control, RX statistic matching/counting controls, analog TX override/status/termination/equalization, and TX DCC DAC override fields.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming scheme:

- `DPCSSYS_<instance>_<block>_<register>__<field>__SHIFT` gives the least significant bit index for a field.
- `DPCSSYS_<instance>_<block>_<register>__<field>_MASK` gives the bit mask for the same field.
- `CR2` and `CR3` identify DPCS CR instances. This chunk finishes a CR2 raw-lane alias window and starts an explicit CR3 indirect TX-CR address block.
- `RAWLANEX`, `SUP`, `LANE0`, `DIG`, and `ANA` encode raw lane alias, supervisor/common, concrete lane, digital, and analog register scopes.

Important field families in this slice include:

- IRQ fields: `RX_REQ_IRQ`, `RX_RATE_IRQ`, `RX_PSTATE_IRQ`, `RX_ADAPT_REQ_IRQ`, `RX_ADAPT_DIS_IRQ`, `RX_RESET_IRQ`, `LANE_XCVR_MODE_IRQ`, `RX_PH2_CAL_REQ_IRQ`, `RX_PH2_CAL_DIS_IRQ`, `LANE_RX2TX_SER_LB_EN_IRQ`, `DCC_ONDMD_IRQ`, `TX_RESET`, and `TX_REQ`, with corresponding clear and mask bits.
- PMA/PCS handoff fields: `LANE_MPLLA_EN_*`, `LANE_MPLLB_EN_*`, `SUP_STATE_OVRD_EN`, `TX_REQ_OVRD_*`, `TX_RESET_OVRD_*`, `TX_BEACON_EN_OVRD_*`, `RX_REQ_OVRD_*`, `RX_RESET_OVRD_*`, `RX_RATE_OVRD_*`, `RX_PSTATE_OVRD_*`, `RX_ADAPT_REQ_OVRD_*`, `RX_ADAPT_DIS_OVRD_*`, and `RX_PH2_CAL_*`.
- Supervisor clock/PLL fields: `REF_CLK_EN`, `REF_USE_PAD`, `REF_CLK_RANGE`, `BG_EN`, `HDMIMODE_EN`, `SUP_PRE_HP_OVRD`, MPLLA/MPLLB divider and HDMI clock fields, MPLL multiplier/fractional/frequency mode fields, SSC peak/step-size fields, charge-pump controls, MPLL lock/status/calibration/timer fields, and spread-type controls.
- RTUNE and analog support fields: `RTUNE_ACK`, `RTUNE_ENABLE`, `RTUNE_RDY`, `RTUNE_SET`, `TXDN_SET`, `TXUP_SET`, prescaler controls, bandgap trim/calibration/power fields, MPLL testbus/control/reserved fields, and analog override output fields for MPLLA/MPLLB/RTUNE/bandgap/PMIX.
- LANE0 power and link fields: `TX_P0*`, `TX_P0S*`, `TX_P1*`, `TX_P2*`, TX power-up timers, DCC DAC select/ack/address/control fields, TX clock alignment, LBERT enable/status bits, RX statistic pattern/mask/counter controls, analog TX enable/reset/data-rate/loopback/status fields, TX termination, TX equalization pre/post/leg-pull controls, and TX DCC calibration controls.

Most visible fields are 16-bit register fields with masks ending in `L`, including large `RESERVED_*` masks. The header does not declare reset values, access permissions, volatility, write-one-to-clear semantics, or firmware ownership; consumers must get those semantics from hardware documentation, generated offset tables, and the surrounding AMDGPU display code.

## Control Flow

This header has no runtime control flow. Its implicit use in the driver is:

1. DCN 3.1.6 resource code includes `dpcs/dpcs_4_2_3_offset.h` and `dpcs/dpcs_4_2_3_sh_mask.h`.
2. Generated register-list macros and AMD display register helpers pair an `ixDPCSSYS_*` offset with the matching field shift/mask constants from this file.
3. Link encoder, PHY, and display code perform indexed register reads, writes, masked updates, and polling through the AMDGPU display register-access layer.
4. Hardware and firmware execute the real sequencing for PLL setup, reference and bandgap power, lane power states, TX/RX request/acknowledge handshakes, calibration, adaptation, DCC, interrupt signaling, statistics, and test/diagnostic paths.

The hardware flow represented by this chunk is sequencing-heavy: mask or clear raw-lane interrupts, coordinate PCS/PMA requests and acknowledgements, configure common reference/MPLL/bandgap/RTUNE resources, program LANE0 TX power and analog behavior, run DCC and receiver-statistic collection, and read back status through IRQ, analog status, RTUNE, MPLL, OCLA/UPCS, LBERT, and statistic registers.

## State And Persistence Behavior

The macros are stateless compile-time constants. Mutable state lives in volatile DPCS hardware registers, not in this header.

State represented by this chunk includes:

- Interrupt state: raw-lane IRQ status bits, clear bits, and mask bits for RX, TX, lane-mode, calibration, adaptation, reset, DCC, and loopback events.
- PCS/PMA handshake state: request, acknowledge, reset, rate, P-state, beacon, async, data-enable, lane-loopback, and MPLL/supervisor state mirrors and override enables.
- Common CR3 state: reference-clock selection, bandgap enable and calibration, MPLLA/MPLLB programming and lock/calibration status, SSC values, prescaler values, RTUNE set/status values, clock/reset timing, and analog override/status state.
- LANE0 state: lane override enables, TX power states, TX power-up timing, DCC DAC programming and acknowledgements, TX clock alignment, LBERT controls, RX statistic sample/match/counter state, analog TX enable/reset/rate/termination/equalization controls, analog status, and TX DCC calibration controls.

Persistence is governed by hardware power and reset domains. Register values may survive only until a DPCS reset, GPU reset, display-engine reset, lane reset, power-gating transition, suspend/resume cycle, firmware reload, modeset, hotplug-triggered retrain, link-rate change, or lane-count change. Because this header provides only bit layout, it cannot indicate which fields are sticky, self-clearing, read-clear, write-one-to-clear, or firmware-owned.

## Dependencies

This chunk depends on AMD's generated DPCS 4.2.3 register database staying synchronized with the silicon and with firmware expectations. The shift/mask constants are useful only when paired with the correct offset and register-access path.

Key dependencies are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h`, which supplies the matching `ixDPCSSYS_*` offsets for the register names in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which directly includes both the DPCS 4.2.3 offset and shift/mask headers for DCN 3.1.6 resource construction.
- AMDGPU display register helper infrastructure that applies generated shift/mask metadata to indexed DPCS CR register reads, writes, and polls.
- Hardware and firmware state machines that may own raw IRQ, PCS/PMA, MPLL, RTUNE, DCC, RX adaptation, calibration, LBERT, OCLA/UPCS, and analog override/status fields at different points in bring-up.
- Correct CR instance and lane/alias selection. CR2 `RAWLANEX`, CR3 `SUP`, and CR3 `LANE0` have repetitive-looking fields but refer to different address windows and hardware resources.

## Integration Points

The main integration point is AMDGPU display PHY/link code that builds version-specific register tables for DPCS 4.2.3 hardware.

Important integration surfaces are:

- Interrupt handling and diagnostics through raw-lane IRQ status, clear, and mask fields. Mask/clear pairing must match the specific event fields and not cross from RX event bits to TX event bits in `IRQ_MASK_2`.
- PCS/PMA and firmware coordination through raw-lane transfer fields for requests, resets, rates, P-states, adaptation requests, phase-2 calibration, DCC, loopback, MPLL selection, and supervisor state.
- PLL and common-resource bring-up through CR3 supervisor refclk, MPLLA/MPLLB, SSC, charge-pump, prescaler, bandgap, RTUNE, clock/reset, MPLL power-control, timer, calibration, and analog override/status fields.
- LANE0 TX and analog programming through ASIC override inputs, TX P-state fields, TX power-up timing, DCC DAC controls, TX clock alignment, analog TX override/status, termination, equalization, and DCC calibration fields.
- Validation and debug paths through OCLA/UPCS selectors, ATE override fields, LBERT controls, RX statistic pattern/mask/count registers, analog status/testbus fields, and RTUNE/MPLL status readbacks.
- Generated register-table maintenance. Any consumer using `DPCSSYS_CR3_LANE0_*` masks must also use the CR3 LANE0 offset namespace; aliases such as `RAWLANEX` and concrete lanes are not mechanically interchangeable.

## Risks And Failure Modes

- A wrong shift or mask can compile cleanly while setting the wrong hardware bit. In this area that can cause blank displays, link-training timeouts, failed hotplug, unstable high-rate links, incorrect PLL setup, broken DCC calibration, bad receiver adaptation, or misleading diagnostic output.
- The chunk starts mid-register at the CR2 `RX_RATE_IRQ_CLR` mask definitions. Whole-register analysis must combine this report with the prior chunk before making complete claims about that register.
- CR2/CR3 prefix mistakes are easy because names repeat across DPCS instances and versions. Programming CR2 raw-lane fields when CR3 fields are intended, or vice versa, can leave the target path unconfigured while perturbing another path.
- Alias misuse is dangerous. `RAWLANEX` is a raw lane alias window, while `LANE0` is a concrete lane window and `SUP` is common/supervisor state; identical-looking field names can have different address and ownership semantics.
- Reserved-field masks dominate many registers. Consumers must preserve reserved bits during masked writes unless the hardware sequence explicitly says otherwise.
- Clear and status registers use similar names. Writing a status field instead of its `_CLR` companion, or using a mask field where a clear bit is required, can leave interrupts stuck or accidentally acknowledge events.
- PLL, bandgap, refclk, RTUNE, TX power-state, DCC, analog override, and RX statistic controls are sequencing-sensitive. Stale override enables or out-of-order writes can force the PHY away from firmware/hardware control.
- The header does not mark read-clear, write-one-to-clear, self-clearing, side-effect, power-domain-limited, or firmware-owned fields. Consumers must not infer safe polling or read/modify/write behavior from the macro layout alone.

## Test Signals

Useful validation signals for changes touching this generated header or its consumers include:

- Kernel build coverage for AMDGPU display code that includes `dpcs_4_2_3_sh_mask.h` through DCN 3.1.6 resource initialization.
- Generated-header consistency checks that every field macro in this range has a matching register offset in `dpcs_4_2_3_offset.h`, and that consumed offsets have corresponding shift/mask definitions.
- Version-diff checks against adjacent generated DPCS headers such as `dpcs_4_2_0_sh_mask.h`, `dpcs_4_2_2_sh_mask.h`, and DCN combined headers to catch generator drift, width changes, or moved fields.
- Static checks that each non-reserved field has a shift/mask pair, while tolerating chunk-boundary partial registers such as the initial `RX_RATE_IRQ_CLR` tail.
- Hardware smoke tests on affected AMD display ASICs: boot display, modeset, hotplug, link retraining, lane-count changes, link-rate changes, suspend/resume, GPU reset, and power-gating recovery.
- PHY bring-up traces showing correct refclk and bandgap enable, MPLLA/MPLLB lock and calibration, RTUNE ready/ack state, TX P-state transitions, DCC acknowledgements, PCS/PMA request/ack behavior, IRQ mask/clear behavior, and no stuck raw-lane IRQs.
- Diagnostic tests exercising LBERT, OCLA/UPCS selection, RX statistic counters, ATE override paths, analog TX status/readback, TX equalization/termination controls, and DCC DAC override/status fields.

## Chunk Notes

This is only the source-tree-aligned chunk report for `subset-b-002411`. It intentionally does not create a final per-file research document for `dpcs_4_2_3_sh_mask.h`; the merge/reconciliation lane should combine this report with adjacent chunks before making complete-file statements.
