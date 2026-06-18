# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 2434-4853

## Purpose

This chunk is generated AMD DPCS 3.1.4 register field metadata. It exports C preprocessor constants only; each useful symbol is either a hardware field bit offset (`...__SHIFT`) or a pre-shifted bit mask (`..._MASK`) for DPCSSYS CR0 lane registers. Runtime AMD display code pairs these constants with `dpcs_3_1_4_offset.h` and register-helper macros to compose indexed DPCS/PHY register reads and writes without embedding numeric bit positions in the driver logic.

The requested range is a lane-oriented PHY slice. It begins inside `DPCSSYS_CR0_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0`, covers the rest of lane 1 RX/analog/debug field definitions, covers lane 2 ASIC/TX/RX field definitions through RX statistic counters, and ends after `DPCSSYS_CR0_LANE2_DIG_RX_STAT_STAT_CNT_4`. The slice contains 2,158 `#define` lines: 1,075 `__SHIFT` definitions and 1,083 `_MASK` definitions. The imbalance is expected for this line-bounded chunk because the first visible register started before line 2434; the chunk includes masks for fields whose shift definitions are partly in the preceding chunk.

Although the repository path is under a `ceph-client` source tree mirror, this file is AMDGPU display-driver hardware metadata and has no distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocation paths, locks, callbacks, or includes in this chunk. Its interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT`: zero-based bit position for a field in a 16-bit-style DPCS/PHY register.
- `<REGISTER>__<FIELD>_MASK`: field mask already shifted into register position, usually with an `L` suffix.

The important register families in this range are:

- `DPCSSYS_CR0_LANE1_DIG_RX_PWRCTL_*`: lane 1 RX p-state and power-up timing fields for analog AFE, clock/VREG, DESER, CDR, VCO frequency/calibration reset, continuous calibration, digital clock enable, and timing controls such as AFE/VREG/clock/rate/CDR/DESER enable waits.
- `DPCSSYS_CR0_LANE1_DIG_RX_VCOCAL_*`, `*_RX_CDR_*`, and `*_RX_DPLL_*`: lane 1 RX VCO calibration control/status/timing, CDR control/status, DPLL frequency, and DPLL bounds. Fields include calibration fixed counts, skip controls, startup/update/settle timing, VCO tuning/status, CDR PI update/gain controls, lock status, and frequency limits.
- `DPCSSYS_CR0_LANE1_DIG_RX_ADPTCTL_*`: lane 1 RX adaptation configuration and status for ATT, VGA, CTLE, DFE taps, VDAC offsets, slicer controls, error slicer levels, adaptation reset, DAC selector fields, and CR bank address/data.
- `DPCSSYS_CR0_LANE1_DIG_RX_STAT_*`: lane 1 statistic/match/sample/counter controls, including pattern masks, statistic/correlation source selection, counter enables, sample-done flags, calibration comparator clock controls, match controls, and stop controls.
- `DPCSSYS_CR0_LANE1_DIG_MPHY_*` and `DPCSSYS_CR0_LANE1_DIG_ANA_*`: lane 1 low-speed MPHY RX controls and digital-to-analog override/status fields for TX/RX power, termination, equalization, VCO, calibration, DAC selection, AFE/CTLE, scope, slicer, IQ/phase adjustment, signal detect, DCC DAC, and analog status readback.
- `DPCSSYS_CR0_LANE1_ANA_TX_*` and `DPCSSYS_CR0_LANE1_ANA_RX_*`: lane 1 analog register fields for TX override measurement, TX power override, alternate bus/ATB paths, DCC DAC, termination code/control, miscellaneous TX controls, RX power/squelch/calibration, and RX ATB measurements.
- `DPCSSYS_CR0_LANE2_DIG_ASIC_*`: lane 2 ASIC interface and override fields for lane loopback, enable, RX AC JTAG, TX/RX p-state and request signaling, rate/width, MPLLB selection, data enable, cursor settings, HDMI mode, clock readiness, RX detect, polarity, low-power detect, DC coupling, MPHY mode, reset, boost/equalization, signal detect, VCO/DAC controls, and status readback.
- `DPCSSYS_CR0_LANE2_DIG_TX_PWRCTL_*`, `*_TX_CLK_ALIGN_*`, and `*_TX_LBERT_*`: lane 2 TX p-state fields, TX power-up delays, TX DCC CR bank/DAC controls, clock alignment controls, and loopback/BER test controls.
- `DPCSSYS_CR0_LANE2_DIG_RX_PWRCTL_*`, `*_RX_VCOCAL_*`, `*_RX_CDR_*`, and `*_RX_DPLL_*`: lane 2 RX p-state/power timing, VCO calibration, CDR, DPLL, XAUI comma mask, and LBERT definitions, mirroring the lane 1 RX digital block with lane 2 names.
- `DPCSSYS_CR0_LANE2_DIG_RX_ADPTCTL_*` and `DPCSSYS_CR0_LANE2_DIG_RX_STAT_*`: lane 2 RX adaptation and statistics fields through `STAT_CNT_4` in this chunk. Remaining lane 2 statistic counter definitions continue after this range.

Most masks are small 16-bit hardware fields such as `0x0001L`, `0x00FFL`, `0x7FFFL`, or `0xFFFFL`, reflecting DPCS CR register layout rather than broad 32-bit display-pipe registers.

## Control Flow

This header has no direct control flow. Runtime behavior is created by consumers:

1. DCN 3.1.4 display resource code includes `dpcs_3_1_4_offset.h` and `dpcs_3_1_4_sh_mask.h`.
2. ASIC-specific register tables and token-pasting helper macros combine register names, field names, offsets, shifts, and masks.
3. Link, PHY, power-management, diagnostics, and bring-up code uses those generated symbols through register helpers to read, write, update, or poll DPCS fields.
4. Hardware and firmware sequencing decides when lane p-state, rate, CDR/DPLL/VCO calibration, RX adaptation, TX DCC, loopback, status counter, and analog override fields are programmed.

The macros do not encode sequencing rules. They do not identify whether a field is read-only, sticky, write-one-to-clear, timing-sensitive, reset-sensitive, or safe to modify while a link is active. Those semantics must come from AMD hardware specifications and the driver code that consumes the register database.

## State And Persistence Behavior

The chunk stores no software state and persists nothing to disk. It describes hardware-backed lane state:

- RX and TX power-state programming for lane 1 RX and lane 2 TX/RX p-states, including analog enables, clocks, VREG, CDR, DESER, VCO reset/calibration, and power-up timing.
- Clock-recovery state for VCO calibration, CDR control/status, DPLL frequency and bounds, lock indication, and calibration counters.
- RX equalization/adaptation state for ATT/VGA/CTLE/DFE tap settings, slicer levels, VDAC offsets, adaptation reset, and adaptation done/status bits.
- Diagnostic state for LBERT controls/errors, XAUI comma mask, statistic match/counter/sample controls, CR bank address/data access, ATB/analog measurement muxes, and OCLA-related lane 2 control.
- Analog override and status state for TX/RX termination, DCC DAC, equalization, signal detect, MPHY low-speed controls, DAC selectors, scope/slicer controls, phase/IQ adjustment, and analog status readback.

Persistence is device-local and reset/power-domain dependent. Values can survive until a modeset, link retrain, lane reset, power-gate transition, suspend/resume, or ASIC reset. Status/counter fields may change asynchronously as the physical lane trains, calibrates, enters low power, receives data, runs diagnostics, or exposes analog test paths.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h`, which provides the indexed register addresses. Examples from the matching offset range are lane 1 RX power/control registers at `0x1140` through the lane 1 analog RX/ATB area, and lane 2 ASIC/TX/RX registers beginning at `0x1200` with lane 2 RX adaptation registers at `0x1260` through `0x127f`.

The known include point in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`, which includes both the DCN 3.1.4 and DPCS 3.1.4 offset/mask headers before `reg_helper.h`. That makes these macros part of DCN314 resource initialization and register-table construction.

Functional integration is with the AMD display core rather than Ceph code. These fields support DisplayPort/PHY lane setup, lane-rate and p-state programming, link training, clock recovery, RX adaptation, analog trim/override, diagnostic counters, loopback/BERT paths, and manufacturing/debug access. The repeated `LANE1` and `LANE2` prefixes are part of the register-table naming contract; adjacent lane chunks should contain the corresponding lane 0/3 definitions.

## Risks And Edge Cases

- Shift/mask drift is high risk. These are untyped compile-time constants, so an incorrect bit position can compile cleanly while programming or reading the wrong PHY field.
- Offset/header mismatch can apply a correct mask to the wrong indexed register address. The mask header must stay synchronized with `dpcs_3_1_4_offset.h` and any generated register-table macros.
- Lane-instance mistakes are easy to miss. A `LANE1` versus `LANE2` table or copy error may only appear on links that use the affected physical lane.
- Override-enable fields are hazardous. `*_OVRD_EN`, power override, reset override, loopback, termination, equalization, DCC DAC, VCO, CDR, DPLL, and analog mux fields can force hardware away from normal sequencing.
- Status, counter, ack, and calibration fields may have side effects or timing requirements not represented here. Wrong masks can cause polling timeouts, lost diagnostic data, stuck calibration flows, or false link-training decisions.
- Boundary incompleteness matters for this research chunk. It starts after several `RX_PSTATE_P0` shift definitions and ends before later lane 2 statistic counter groups, so full per-register validation must include neighboring chunks.
- Constants use `L` suffixes and are often 16-bit masks; consumers should preserve expected unsigned extraction/update behavior and avoid sign or width assumptions when composing field values.

## Test Signals

Useful validation signals are a mix of generated-header consistency and hardware behavior:

- Build AMDGPU/DC with DCN314 support enabled so `dcn314_resource.c` and any register-table expansions catch missing, renamed, or malformed macros.
- Mechanically verify that every register field has a coherent `__SHIFT` and `_MASK` pair after merging adjacent chunks. For this exact line range, 1,075 shifts and 1,083 masks are expected because the start boundary is mid-register.
- Cross-check masks against `dpcs_3_1_4_offset.h` and neighboring lane definitions. Lane 1 and lane 2 repeated blocks should match where hardware layout is lane-replicated, while intentional omissions such as continuation past `STAT_CNT_4` should be handled at merge time.
- Exercise display links using the affected lanes: link training across lane counts and rates, hotplug, suspend/resume, p-state transitions, low-power entry/exit, and retraining after mode changes.
- Run PHY diagnostic paths where available: LBERT/loopback, statistic counters, CDR/DPLL/VCO calibration polling, RX adaptation status reads, DCC DAC access, and analog status/ATB measurement paths.
- Watch kernel logs and display diagnostics for lane-specific training failures, repeated retraining, stuck calibration or power-status bits, signal-detect failures, invalid counter reads, or display instability that points to an incorrect generated field definition.

## Cross-Chunk Notes

The previous chunk owns the start of `DPCSSYS_CR0_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0`. The following chunk continues after lane 2 RX statistic counter 4 with additional lane 2 statistic and later DPCS definitions. The final per-file report should reconcile adjacent chunks before making complete claims about all registers in `dpcs_3_1_4_sh_mask.h`.
