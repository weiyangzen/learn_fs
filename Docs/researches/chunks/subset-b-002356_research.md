# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 45340-47692

## Scope

This chunk is a generated AMD DPCS 4.2.2 register shift/mask header slice for `DPCSSYS_CR2`. It contains 2,145 `#define` constants covering 209 register-field groups from the tail of supervisor MPLLA analog definitions through supervisor MPLLB, common supervisor digital controls, lane 0 PHY/TX/RX debug and power controls, and the beginning of lane 1 PHY/TX/RX controls. The source file is guarded by `_dpcs_4_2_2_SH_MASK_HEADER` and is included by the DCN 3.1.5 resource code together with `dpcs_4_2_2_offset.h`.

The chunk starts mid-register at `DPCSSYS_CR2_SUP_ANA_MPLLA_ATB1` masks and ends mid-register after the first fields of `DPCSSYS_CR2_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S`; neighboring chunks must provide the missing opening and closing fields when the full-file report is reconciled.

## Purpose

The header gives symbolic bit positions and bit masks for 16-bit DPCS PHY control/status registers. Driver code can combine the matching offset macro from `dpcs_4_2_2_offset.h` with a `*_SHIFT`/`*_MASK` pair from this file to build read-modify-write values without hard-coded bit literals. The represented hardware area is display PHY link support for CR2: PLL A/B setup, spread-spectrum and reset tuning, analog override outputs, lane-level ASIC override inputs/outputs, TX power-state programming, TX DCC DAC programming, RX status counters, and lane analog TX controls.

The macros are declarative. They do not allocate storage, execute code, or validate values. Correctness depends on consumers applying values within the mask width and writing only the hardware-defined bits.

## Important Definitions

The dominant pattern is:

- `REGISTER__FIELD__SHIFT`: low bit index for `FIELD`.
- `REGISTER__FIELD_MASK`: bit mask for `FIELD`, usually 16-bit wide and suffixed with `L`.
- `RESERVED_*` fields: hardware-reserved regions included so generated register layouts cover the full register width.

Major register families in this chunk:

- Supervisor analog MPLLA/MPLLB fields: `DPCSSYS_CR2_SUP_ANA_MPLLA_*` and `DPCSSYS_CR2_SUP_ANA_MPLLB_*` expose PLL analog test bus, charge pump, VREF, standby, lock calibration, bypass, divider, gearshift, and reserved control bits.
- Supervisor digital MPLL power control: `DPCSSYS_CR2_SUP_DIG_MPLLA_MPLL_PWR_CTL_*` and `DPCSSYS_CR2_SUP_DIG_MPLLB_MPLL_PWR_CTL_*` cover override enables, FSM/status bits, DAC range, lock/stable timers, PCLK stable timers, calibration, analog DAC output, and SSC spread type.
- Supervisor clock/reset and termination tuning: `DPCSSYS_CR2_SUP_DIG_CLK_RST_*`, `DPCSSYS_CR2_SUP_DIG_RTUNE_*`, and `DPCSSYS_CR2_SUP_DIG_ANA_*` cover bandgap and reference power-up timing, VPHUD control, RTUNE configuration/status/set values, analog override outputs for MPLLA/MPLLB/RTUNE/bandgap/PMIX, and analog status bits.
- Lane 0 ASIC digital controls: `DPCSSYS_CR2_LANE0_DIG_ASIC_*` defines lane loopback, TX override input/output, RX override/status output, and raw ASIC input/output observations.
- Lane 0 TX power and diagnostics: `DPCSSYS_CR2_LANE0_DIG_TX_PWRCTL_*`, `DPCSSYS_CR2_LANE0_DIG_TX_CLK_ALIGN_*`, `DPCSSYS_CR2_LANE0_DIG_TX_LBERT_*`, and `DPCSSYS_CR2_LANE0_DIG_RX_STAT_*` define TX P-state bit recipes, power-up timing, DCC DAC bank/DAC handshakes, clock alignment, transmit LBERT, and RX statistic match/counter controls.
- Lane 0 analog TX fields: `DPCSSYS_CR2_LANE0_DIG_ANA_TX_*` and `DPCSSYS_CR2_LANE0_ANA_TX_*` expose digital-to-analog override outputs for TX enable/reset/rate, term code, equalization, DCC DAC, and raw analog override/test-bus fields.
- Lane 1 counterpart fields: `DPCSSYS_CR2_LANE1_DIG_ASIC_*`, `DPCSSYS_CR2_LANE1_DIG_TX_PWRCTL_*`, `DPCSSYS_CR2_LANE1_DIG_TX_CLK_ALIGN_*`, `DPCSSYS_CR2_LANE1_DIG_TX_LBERT_*`, and the beginning of `DPCSSYS_CR2_LANE1_DIG_RX_PWRCTL_*` mirror lane 0 TX/ASIC controls while also including RX override input/equalization/CDR/VCO controls that were not present in this lane 0 slice.

## Control Flow

There is no runtime control flow in this header. Its effective flow is compile-time substitution:

1. DCN 3.1.5 resource code includes `dpcs/dpcs_4_2_2_offset.h` and `dpcs/dpcs_4_2_2_sh_mask.h`.
2. Register helper code selects an `ix...` offset such as `ixDPCSSYS_CR2_LANE0_DIG_TX_PWRCTL_TX_PSTATE_P0`.
3. The corresponding field macros are used to shift and mask a value, commonly through AMD display register helper macros.
4. Hardware observes the resulting MMIO/register transaction and updates PHY state or returns status.

Because this file is generated constants only, the logical state transitions live in hardware and in the calling driver code, not here. Still, the field names reveal state machines and handshakes: MPLL `FSM_STATE`/`MPLL_LOCK`, TX `REQ`/`TX_ACK`, RX `REQ`/`ACK`/`VALID`, DCC DAC `REQ`/`ACK`, status-counter `START`/`STOP`/`DONE`, and calibration result bits.

## State And Persistence

No software state is persisted by this chunk. Persistence is hardware register state:

- MPLLA/MPLLB power, reset, calibration, lock, standby, clock-enable, feedback-clock, divider, and gearshift fields persist until hardware reset or later register writes.
- TX P-state registers encode desired PHY behavior for P0, P0S, P1, and P2, including analog reference generation, VCM hold, clock enable, word clock enable, reset, serial enable, data enable, RX-detect allowance, VBOOST allowance, and DCC comparator calibration.
- Override registers can force hardware signals away from normal controller-generated values. These are particularly stateful because one bit commonly supplies a value and a paired `*_OVRD_EN` bit selects whether that value is active.
- Status and counter registers expose transient hardware observations such as lock, calibration, RX detection, sample counter completion, and statistic counters.

The mask constants are 32-bit C integer constants even though most represented registers are 16-bit. Reserved masks should be treated as do-not-write areas unless the consuming code is explicitly preserving readback values.

## Dependencies And Integration Points

This header depends on matching address/offset definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h`. For this chunk, relevant offset ranges include supervisor registers around `0x0064` through `0x0096`, lane 0 registers around `0x1000` through `0x10ef`, and lane 1 registers beginning around `0x1100`.

`sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes this header for the DCN 3.1.5 resource implementation. The macros therefore integrate with the AMD display core register abstractions and DPCS base segment definitions used to access the PHY.

This file also has version siblings such as `dpcs_3_1_4_sh_mask.h`, `dpcs_4_2_0_sh_mask.h`, and `dpcs_4_2_3_sh_mask.h`. The field shapes are similar across versions, but masks can differ in formatting or reserved coverage. Consumers must use the DPCS version matching the ASIC resource table.

## Risks

- Header/offset skew: a field macro from `dpcs_4_2_2_sh_mask.h` must be paired with the corresponding `ix...` offset from `dpcs_4_2_2_offset.h`; mixing versions can write correct-looking bits to the wrong register.
- Reserved-bit writes: the generated `RESERVED_*_MASK` definitions make reserved regions visible. Code that writes whole-register literals instead of masked read-modify-write can toggle reserved hardware behavior.
- Override enable hazards: many lane and PLL fields use value plus override-enable pairs. Setting only the value bit has no effect; setting only override enable can force an unintended default value.
- Lane symmetry assumptions: lane 0 and lane 1 share many TX definitions, but this chunk shows lane 1 RX override/equalization/CDR fields and OCLA fields in the same range. Generic lane code must account for actual per-lane register availability and offsets.
- Chunk boundary risk: `DPCSSYS_CR2_SUP_ANA_MPLLA_ATB1` and `DPCSSYS_CR2_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S` are incomplete in this slice; any generated per-file summary must merge adjacent chunks before claiming complete field coverage.
- Value-width risk: callers must clamp values to `FIELD_MASK >> FIELD_SHIFT`; this header only defines the mask and cannot prevent overflow before shifting.

## Test Signals

Useful validation signals for changes involving this header:

- Compile coverage for AMDGPU DCN 3.1.5 paths, proving `dcn315_resource.c` and related register macros still include cleanly.
- Static comparison of every `DPCSSYS_CR2_*` register in this chunk against `dpcs_4_2_2_offset.h` to ensure each field group has a matching `ix...` offset where expected.
- Generator/regression diffs against upstream AMD register headers or internal XML output, with special attention to reserved masks and fields whose masks cross byte boundaries.
- Runtime display bring-up on DCN315 hardware: link training, DisplayPort/HDMI output enable, hotplug/RX detect, low-power P-state transitions, spread-spectrum clocking, and suspend/resume can expose bad PLL, TX P-state, or reset timing fields.
- Debugfs/MMIO register readback checks for DCC DAC handshakes, MPLL lock status, TX/RX acknowledge fields, and RX statistic counter completion after driver-triggered operations.

## Cross-Chunk Notes

The full-file reconciliation lane should combine this report with adjacent chunk reports before producing the per-file document. In particular, it should recover the missing start of `DPCSSYS_CR2_SUP_ANA_MPLLA_ATB1` before line 45340 and the remaining `DPCSSYS_CR2_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S` fields after line 47692, then continue through later lane 1 RX power, VCO calibration, RX CDR, raw lane, and CR3/CR4 register blocks.
