# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 192840-195229

## Purpose

This chunk is generated AMD DCN 3.2 register field metadata for the C20 PHY CR4 block. It contains no executable C logic. Its API is a large set of preprocessor constants that describe bit positions and already-shifted masks for 16-bit PHY control, override, status, adaptation, calibration, and debug registers.

The requested range starts in the tail of `C20_PHY_CR4_LANE0_DIG_ANA_XF_TX_OVRD_OUT_3`, covers the remainder of many lane 0 TX and RX field groups, and ends inside `C20_PHY_CR4_LANE1_DIG_ASIC_TX_OVRD_IN_1`. Most of the range belongs to lane 0 receive-side metadata: ASIC override/actual input registers, RX power-state and VCO/CDR controls, adaptation and slicer-search configuration/status, RX statistic counters, IQ correction controls, analog crossbar override/status registers, RX AFE/DFE/IQC/calibration fields, and RX analog CREG fields. The final lines begin the equivalent lane 1 digital ASIC lane/TX override namespace.

Although this path is under a local `ceph-client` source mirror, this header is AMDGPU display-driver hardware metadata. It has no Ceph filesystem protocol behavior, distributed filesystem state, or storage persistence.

The exact line range contains 2,168 `#define` lines and 222 register comment markers. It is not a self-contained generated section: the first visible lines are masks whose matching shift definitions are in the previous chunk, and the final visible lines stop before the matching masks for the last lane 1 TX override register.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this chunk. The entire interface is the generated macro namespace:

- `C20_PHY_CR4_<register>__<field>__SHIFT`: low bit position for a field.
- `C20_PHY_CR4_<register>__<field>_MASK`: already-positioned bit mask for the same field.

Important register families covered by this chunk:

- `LANE0_DIG_ANA_XF_TX_*`: TX termination-code override, termination-code load clock, TX DCC enable/configuration/calibration, TX equalization override/status, TX analog status input/output, and TX analog CREG fields for resets, PLL/clock/data enables, VREG controls, loopback, DCC, term control, and miscellaneous analog overrides.
- `LANE0_DIG_ASIC_RX_OVRD_*` and `LANE0_DIG_ASIC_RX_ASIC_*`: digital RX override inputs, RX status override outputs, and actual ASIC RX input/output field layouts for reset, invert, data enable, request/ack/valid, low-power detect, power state, rate, width, CDR/DFE controls, signal-detect thresholds, VCO config, RX reference/VCO load values, and equalizer settings.
- `LANE0_DIG_ASIC_RX_OVRD_EQ_IN_*` and `LANE0_DIG_ASIC_RX_EQ_ASIC_IN_*`: equalizer override and actual fields for attenuator level, VGA gain, CTLE boost/pole, AFE rate/bias/VCM, DFE taps 1-5, eye/sample offset overrides for even/odd high/low paths, IQ, TIA bias, CTLE zero, and CTLE offset.
- `LANE0_DIG_RX_PWRCTL_*`: P0/P0S/P1/P2 RX power-state recipes, power-up timing, RX control/status fields, analog clock/VREG/AFE/CDR/deserializer/DFE enables, VCO reset/continuous-calibration bits, and power-state/status indicators.
- `LANE0_DIG_RX_VCOCAL_*`, `LANE0_DIG_RX_CDR_*`, `LANE0_DIG_RX_DPLL_*`, and `LANE0_DIG_RX_LBERT_*`: VCO calibration controls/timers/status, clock-data-recovery controls/status, DPLL frequency and bound fields, and loopback BERT control/error fields.
- `LANE0_DIG_RX_ADPTCTL_*`: adaptation configuration, reset, status, DFE tap status, slicer and DFE VDAC offsets, RX DCC IDAC offsets, fast flags, SSM configuration/final code, and threshold/mu/saturation fields for CTLE/VGA/ATT/DFE adaptation.
- `LANE0_DIG_RX_STAT_*`: statistic load/mask/match/control/sample/count registers, counter shadowing, stop control, calibration comparator clock control, and extended load values.
- `LANE0_DIG_RX_IQC_CTL_*`: IQ-correction reset/adjust/config/status fields for bypass and data adjustment control.
- `LANE0_DIG_ANA_XF_RX_*`: RX analog crossbar control/power/VCO/signal-detect/calibration/VDAC/DAC/AFe/scope/slicer/IQ/IQC/loopback/term-code/stat fields, including many `*_OVRD_EN` and self-clear-disable bits used for forced analog programming or one-shot update clocks.
- `LANE0_DIG_ANA_XF_RX_ANA_CREG00` through `CREG11` plus `CREG0_OVRD` and `CREG1_OVRD`: low-level RX analog configuration, measurement, regulator, ring, VREF, AFE, termination, ATB, calibration, and reserved/RFU fields.
- `LANE1_DIG_ASIC_LANE_OVRD_IN` and the beginning of `LANE1_DIG_ASIC_TX_OVRD_IN_0/1`: the next-lane lane-mode and TX override field layouts for serial/parallel loopback, transceiver mode, clock-ready/reset/invert/data/request/low-power/pstate/rate/width/alignment/MPLLB/detect-RX/flyover controls.

## Control Flow

This header has no runtime control flow. Runtime code supplies all sequencing:

1. DCN 3.2 display, DMUB, GPIO, IRQ, clock, GMC, or resource code includes `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`.
2. Register-table macros collect address offsets from the offset header and field metadata from this mask header. The common pattern uses helpers such as `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `FD(reg__field)`, `REG_GET`, `REG_UPDATE`, and DMUB register table initialization.
3. Driver code performs read-modify-write operations, polling, or raw indexed PHY access using the generated masks and shifts.

The macros do not encode ordering, valid values, read-only status, sticky status behavior, write-one-to-clear semantics, or whether a bit is self-clearing. Consumers must still sequence PHY power, resets, PLL/VCO/CDR calibration, link training, equalizer adaptation, DCC/IQC calibration, loopback, RX detect, signal-detect thresholds, and suspend/resume restore correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing. It describes MMIO or indexed PHY register state in DCN 3.2 display hardware.

The represented hardware state includes:

- Lane 0 TX analog state for term-code programming, DCC calibration, equalization taps, PLL/clock/data enables, resets, loopback, VREG controls, RX detect, and TX status readback.
- Lane 0 RX digital/ASIC state for reset/data/request/ack/valid handshakes, rate/width/pstate programming, signal-detect thresholds, CDR/VCO programming, DFE bypass, RX reference/VCO load values, and equalizer settings.
- Lane 0 RX power and calibration state for P-state recipes, VCO calibration timing/status, CDR/DPLL controls, loopback BERT, DCC/IQC controls, and RX statistic counters.
- Lane 0 adaptation state for CTLE/VGA/ATT/DFE enablement, thresholds, adaptation step sizes, reset controls, status codes, slicer and VDAC offsets, SSM scan configuration/results, and fast-settle flags.
- Lane 0 analog RX state for AFE, clock/VREG, CDR/VCO, deserializer, loopback, signal-detect calibration, DAC/VDAC range, IQ correction bypass/data overrides, AFE update clocks, sample selection, termination code, analog status, and analog CREG/RFU fields.
- The beginning of lane 1 lane/TX override state, which mirrors the lane 0 digital ASIC lane and TX override model from the preceding source region.

Persistence is hardware-defined. Programming fields generally retain their values until a modeset, PHY reconfiguration, power gating, suspend/resume, firmware action, or ASIC reset changes them. Status, statistic, IRQ-like, one-shot clock, calibration, and self-clear fields may change asynchronously or clear themselves. This generated header does not mark those categories beyond field names such as `STATUS`, `STAT`, `SELF_CLEAR_DISABLE`, `OVRD_EN`, `DONE`, `ABORTED`, or `RESET`.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.2 register database and must match the companion address definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`. The companion offset header identifies this area as the `c20_phy_cr4_rdpcspipecrind` address block and exposes indexed addresses such as `ixC20_PHY_CR4_LANE0_DIG_RX_ADPTCTL_VGA_STATUS`, `ixC20_PHY_CR4_LANE1_DIG_RX_ADPTCTL_VGA_STATUS`, and raw-lane IRQ mask offsets. Field masks in this chunk are only meaningful when paired with the matching CR4 indexed register address and access path.

Direct include sites for the DCN 3.2 offset/mask pair in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`

The most visible integration pattern is in DMUB/DCN register table setup: `dmub_dcn32.c` initializes register offsets, masks, and shifts using `REG_OFFSET_EXP(reg)`, `FD_MASK(reg, field)`, and `FD_SHIFT(reg, field)`. Resource, GPIO, IRQ, and clock-manager code uses the same generated-header contract to populate block-specific tables for later `REG_READ`, `REG_WRITE`, `REG_GET`, and `REG_UPDATE` operations. The C20 PHY-specific macros may be consumed directly by PHY/link bring-up, diagnostic, or firmware-facing code paths even when references are produced through macro expansion rather than plain-text symbol names.

## Risks And Edge Cases

- A wrong shift or mask silently corrupts packed PHY register updates. These are untyped preprocessor constants, so many errors compile cleanly and only appear as hardware behavior changes.
- The fields are low-level PHY controls. Bad constants around resets, PLL/VCO/CDR, clocks, DCC/IQC calibration, AFE/DFE/CTLE/VGA, termination, VREG, loopback, or pstate programming can cause link-training failures, blank displays, intermittent dropouts, high error rates, compliance failures, stuck calibration, or resume failures.
- Override bits are high risk. Many registers pair a value field with an `OVRD_EN` field; setting the wrong enable bit or using the wrong mask can force analog state unexpectedly or leave a requested override inactive.
- Self-clearing and one-shot update fields need careful sequencing. `*_CLK`, `*_UPDATE_EN`, `*_DAC_CTRL_EN`, `*_TERM_CLK`, and `SELF_CLEAR_DISABLE` fields may not behave like normal latched configuration bits.
- Status and statistic fields may be live, sticky, shadowed, or counter-like. Incorrect masks in `RX_STATUS`, `VCO_STAT`, `CDR_STAT`, `ADPTCTL_*_STATUS`, `SSM_FINAL_CODE`, and `RX_STAT_*` can mislead polling and diagnostics without directly causing a write failure.
- The artificial chunk boundaries matter. The range starts after some `TX_OVRD_OUT_3` shift definitions and ends before the masks for `LANE1_DIG_ASIC_TX_OVRD_IN_1`; a per-file report must merge adjacent chunks before making whole-register completeness claims.
- Repeated lane patterns are copy-generation sensitive. Lane 1 begins at the end of this chunk and should mirror lane 0 structure where hardware intends it; suffix drift between `LANE0` and `LANE1` names can affect only one physical lane.
- Reserved and RFU fields are present throughout the CREG and status spaces. Normal driver changes should not assign semantics to reserved masks without ASIC documentation or matching upstream generated data.

## Test Signals

Useful validation is mostly generated-header consistency plus display/PHY behavior:

- Build AMDGPU/DC with DCN 3.2 support enabled. Missing or renamed field macros should fail in DCN 3.2 resource, IRQ, GPIO, clock-manager, DMUB, and GMC compilation paths.
- Mechanically verify each complete register group in this range has matching `__SHIFT` and `_MASK` definitions for every field, while allowing the known boundary imbalance at the first and final registers.
- Diff the field layout against AMD's authoritative DCN 3.2 generated register database and against adjacent CR2/CR3/CR4 or lane 0/lane 1 patterns where the hardware blocks are expected to match.
- Exercise DisplayPort/USB-C PHY lanes that route through C20 PHY CR4: link training across rates and lane counts, hotplug, HPD IRQs, AUX/DPCD access where applicable, retraining, lane disable/enable, and suspend/resume.
- Validate analog PHY behavior under stress: CDR/VCO calibration completion, DCC and IQC calibration, RX adaptation convergence, signal-detect thresholds, equalizer tap readbacks, term-code updates, and loopback/BERT error counters.
- Use debug/register-dump tooling to confirm masks extract plausible values from `RX_ADPTCTL_*_STATUS`, `RX_VCOCAL_*`, `RX_CDR_STAT`, `RX_STAT_*`, and analog RX/TX status registers before and after link training.
- Watch kernel logs and display diagnostics for AUX or link-training timeouts, repeated HPD storms, stuck reset/calibration bits, PHY lane errors, CRC/test-pattern failures, underflow symptoms caused by link instability, and resume-only failures.

## Cross-Chunk Notes

Previous chunks define the start of the C20 PHY CR4 lane 0 digital ASIC and TX analog field namespace, including the shift definitions for the `TX_OVRD_OUT_3` masks visible at this chunk's first lines. Later chunks complete `LANE1_DIG_ASIC_TX_OVRD_IN_1` and continue the lane 1 C20 PHY field map. The final per-file research document should treat this as one slice of a generated DCN 3.2 C20 PHY register-field contract, not as an independent algorithmic module.
