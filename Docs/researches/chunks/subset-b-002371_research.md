# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 81069-83440

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for display PHY/control registers. It contains no executable C code; it publishes preprocessor constants that describe bit positions and bit masks for hardware register fields. Driver code pairs these constants with the companion `dpcs_4_2_2_offset.h` offsets and uses AMD display register helpers to build per-block shift/mask tables.

The requested range is a mid-file slice of a 103,633-line generated header. It contains 2,128 `#define` lines: 1,063 `__SHIFT` definitions and 1,065 `_MASK` definitions. The imbalance is caused by artificial chunk boundaries. The range starts inside `DPCSSYS_CR3_LANEX_DIG_ASIC_RX_EQ_ASIC_IN_1`, after the `EQ_DFE_TAP2` and `EQ_DFE_TAP1` shift lines but before their masks, and ends on the comment for `DPCSSYS_CR3_RAWLANEX_DIG_FSM_RX_IQ_PHASE_OFFSET`, whose field definitions are in the next chunk.

Although the source path sits under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this chunk. The public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position of a register field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate, preserve, or update that field.

The main register-field families in this range are:

- `DPCSSYS_CR3_LANEX_DIG_ASIC_*`: lane ASIC-facing RX/TX fields for RX equalization, RX CDR/VCO load values, RX ASIC output status, RX/TX override controls, TX override output controls, and OCLA clock/data observation enables.
- `DPCSSYS_CR3_LANEX_DIG_TX_PWRCTL_*`: TX power-state templates for `P0`, `P0S`, `P1`, and `P2`; TX power-up timing stages; and TX DCC CR-bank/DAC control, range, select, acknowledge, and address fields.
- `DPCSSYS_CR3_LANEX_DIG_RX_PWRCTL_*` and `DPCSSYS_CR3_LANEX_DIG_RX_VCOCAL_*`: RX power-state templates, RX power-up timing stages, RX VCO calibration control/time fields, and VCO calibration status.
- `DPCSSYS_CR3_LANEX_DIG_RX_*`: RX XAUI alignment mask, LBERT controls/error counters, CDR controls/status, DPLL frequency/bounds, adaptation configuration, adaptation reset, tap/status readbacks, DAC control selection, CR-bank access, statistical match/count controls, and statistic stop fields.
- `DPCSSYS_CR3_LANEX_DIG_MPHY_*`: MPHY RX PWM, low-speed termination, and analog PWM clock-stability counter fields.
- `DPCSSYS_CR3_LANEX_DIG_ANA_*` and `DPCSSYS_CR3_LANEX_ANA_*`: digital-to-analog override outputs and raw analog TX/RX controls for TX term code, TX equalization, RX power/VCO/calibration, DAC control, AFE ATT/VGA/CTLE, RX scope/slicer/IQ phase, signal-detect override, TX DCC DAC override, analog test-bus/measurement fields, analog power/clock/misc fields, RX CDR/slicer/squelch/calibration, and RX ATB measurement/force fields.
- `DPCSSYS_CR3_RAWMEM_DIG_*`: raw common ROM/RAM field masks for CR3 raw memory windows.
- `DPCSSYS_CR3_RAWLANEX_DIG_PCS_XF_*`: raw lane PCS transfer-interface fields for TX/RX override inputs/outputs, PCS input/output status, RX adaptation acknowledgement and figure-of-merit, directed TX pre/main/post cursor controls, lane number, ATE override, RX EQ delta-IQ override, TX/RX termination override/input, and phase-2 RX calibration.
- `DPCSSYS_CR3_RAWLANEX_DIG_FSM_*`: FSM override, memory-address monitor, FSM status monitor, fast RX/TX calibration/adaptation flags, common calibration status for MPLL and RCAL, CR register/memory lock bits, TX DCC flags/status, OCLA controls, and TX EQ update flag.

The power-state templates have repeated bit layouts. TX `P0/P0S/P1/P2` fields cover analog reference generation, VCM hold, analog clocks, word clock, reset, serial enable, digital clock enable, data enable, RX detect allowance, and DCC compensation calibration enable. RX `P0/P0S/P1/P2` fields similarly cover analog/digital clocks, resets, data, CDR tracking, termination, and related enable state. Those repeated layouts are intended for table-driven power sequencing by code outside this header.

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. DCN 3.1.5 resource code includes `dpcs/dpcs_4_2_2_offset.h` and this matching `dpcs/dpcs_4_2_2_sh_mask.h`.
2. Register-list macros in display resource and link-encoder headers token-paste generated register and field names into offset, shift, and mask initializers.
3. AMD display objects store those constants in register, shift, and mask tables.
4. Runtime code uses helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and poll/wait helpers to access MMIO or indexed DPCS CR registers through the generated constants.

The macros do not encode programming order. Consumers must still sequence PHY power state changes, TX/RX clock enables, CDR/VCO programming, DCC and RX calibration, PCS transfer handshakes, adaptation, interrupt/status handling, and suspend/resume restoration according to hardware rules.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes hardware-backed state for CR3 lane and raw-lane DPCS blocks:

- RX equalization and adaptation state, including ATT/VGA/CTLE controls, DFE tap status, DAC selection, slicer offsets, adaptation reset, and RX adaptation acknowledgement/FOM values.
- RX CDR, DPLL, and VCO state, including load values, frequency bounds, calibration enables, calibration timers, and calibration status.
- TX state, including power templates, power-up timing, term-code override, equalization override, DCC DAC programming, TX DCC status, and TX EQ update flags.
- Lane digital override state, including RX/TX override enable bits, clock/data enable overrides, lane-master/shift acknowledgement controls, termination controls, and MPHY low-speed/PWM controls.
- Analog observation and override state for TX/RX analog controls, ATB measurement paths, OCLA controls, and raw analog status.
- PCS transfer-interface state for TX/RX PCS inputs/outputs, loopback/test/ATE controls, lane numbering, RX phase-2 calibration, and TX/RX termination controls.
- FSM state and diagnostics, including override control, memory-address monitor, state/readiness/overflow/zero flags, fast calibration/adaptation selectors, common MPLL/RCAL init/done bits, CR lock bits, and OCLA bank enables.

Persistence is hardware-defined. Configuration fields generally remain until link reprogramming, PHY reset, power gating, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, acknowledge, done, lock, monitor, and calibration flags may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while the relevant DPCS power and clock domains are active. This generated header does not identify those access semantics.

## Dependencies And Integration Points

This chunk must stay synchronized with AMD's generated DPCS 4.2.2 register database and the matching offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies the corresponding `ix...` offsets. The registers in this chunk map to the CR3 `LANEX` address range around `0x9018-0x90ff`, raw memory windows at `0xa000` and `0xc000`, and raw lane PCS/FSM ranges around `0xe000-0xe03f`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` directly includes both DPCS 4.2.2 generated headers and builds DCN 3.1.5 link-encoder register/shift/mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h` defines the DPCS register and field-list macros used by DCN 3.1-family link encoders.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.h` uses DPCS/RDPCS generated metadata for HPO DP link-encoder PHY control registration.
- Shared AMD display register helper infrastructure consumes the generated values indirectly through table entries built by `SRI`, `SRII`, `LE_SF`, and related token-pasting macros.

Behaviorally, this range sits below the higher-level display link encoder. It describes the per-lane PHY, RX/TX adaptation, calibration, and diagnostic fields that link-training, PHY bring-up, power management, and hardware debug paths rely on, even when most field names are not referenced directly by hand-written C code.

## Risks And Edge Cases

- These constants are untyped preprocessor values. A wrong shift or mask can compile cleanly while writing the wrong DPCS CR bit, corrupting adjacent PHY state, or reading a misleading status field.
- The file is generated metadata. Manual edits can diverge from the authoritative AMD register database, the companion offset header, firmware assumptions, and silicon documentation.
- The chunk boundaries are not semantic. The first register group starts in the previous chunk, and the final `RX_IQ_PHASE_OFFSET` group starts only as a comment here and is defined in the next chunk.
- CR3 lane fields are one repeated slice of a broader DPCS namespace. A generator error limited to CR3 may only appear on a specific lane, connector, or link-encoder routing.
- PHY power, CDR/VCO, DPLL, DCC, and RX adaptation fields are sequencing-sensitive. Incorrect masks can cause link-training failures, unstable high-rate links, calibration timeouts, bad RX equalization, or failures that only appear after low-power transitions.
- Override and lock bits can bypass normal hardware sequencing. Writing the wrong override-enable or lock field may leave a lane stuck in test/debug mode, prevent firmware/hardware FSM updates, or interfere with normal link bring-up.
- Status and acknowledge fields are side-effect-sensitive. Misclassifying status, done, ack, lock, or clear semantics can produce busy waits that never finish, missed calibration completion, stale diagnostics, or interrupt/status storms in adjacent IRQ-control ranges.
- Analog and test-bus fields are hardware-revision-sensitive. Incorrect masks in ATB, OCLA, ATE, raw memory, or analog override areas can produce hard-to-reproduce board-specific failures or misleading lab diagnostics.

## Test Signals

Useful validation combines generated-header consistency checks with link/PHY behavior:

- Build AMDGPU display support with DCN 3.1.5 enabled. Missing or renamed macros should surface where `dcn315_resource.c` includes `dpcs_4_2_2_offset.h` and `dpcs_4_2_2_sh_mask.h` and initializes link-encoder DPCS tables.
- Mechanically verify that every field in lines 81069-83440 has the expected shift/mask pairing, while allowing the known artificial-boundary exceptions at `DPCSSYS_CR3_LANEX_DIG_ASIC_RX_EQ_ASIC_IN_1` and `DPCSSYS_CR3_RAWLANEX_DIG_FSM_RX_IQ_PHASE_OFFSET`.
- Cross-check each register group in this slice against `dpcs_4_2_2_offset.h` so every shift/mask group has a corresponding `ixDPCSSYS_CR3_*` offset.
- Diff this range against AMD's authoritative DPCS 4.2.2 register-field database and neighboring generated variants such as `dpcs_4_2_0_sh_mask.h` and `dpcs_4_2_3_sh_mask.h` where CR3 lane layouts are expected to be compatible.
- Exercise display link bring-up on hardware using this DPCS revision across all available connectors and lanes: hotplug, link training, link-rate/lane-count changes, DisplayPort alt-mode paths, suspend/resume, GPU reset, and repeated modesets.
- Validate high-rate and marginal-link cases that stress CDR/VCO/DPLL, equalization, DCC, RX adaptation, and termination programming. Expected signals are stable training, no stuck calibration done/ack polling, no unexpected link retrains, and clean PHY status readbacks.
- Use register dumps or debugfs-style diagnostics to confirm that TX/RX power templates, timing fields, calibration status, FSM state, and PCS transfer-interface fields match expected programming before and after power transitions.
- Watch kernel logs and display diagnostics for link-training failures, AUX/link instability caused by PHY misconfiguration, blank displays after resume, calibration timeouts, stuck FSM readiness, bad lane mapping, or failures isolated to one CR3-backed lane/encoder.

## Cross-Chunk Notes

The previous chunk owns the start of `DPCSSYS_CR3_LANEX_DIG_ASIC_RX_EQ_ASIC_IN_1`, including the `EQ_DFE_TAP2` and `EQ_DFE_TAP1` shift definitions. This chunk begins with the reserved shift and all masks for that register, then covers the rest of the CR3 lane ASIC, power, calibration, analog, raw PCS, and FSM groups through `DPCSSYS_CR3_RAWLANEX_DIG_FSM_CMNCAL_RCAL_STATUS`. The next chunk owns the `DPCSSYS_CR3_RAWLANEX_DIG_FSM_RX_IQ_PHASE_OFFSET` definitions and continues into CR3 raw-lane IRQ-control fields. The final per-file research document should merge adjacent chunks before making whole-file claims about all DPCS 4.2.2 fields or all CR3 lane behavior.
