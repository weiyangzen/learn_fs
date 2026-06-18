# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 69108-71473

## Scope

This chunk is a generated AMD DPCS 4.2.0 shift/mask header segment for CR3 lane register fields. It contains only C preprocessor constants: `__SHIFT` macros identify field bit positions and `_MASK` macros identify the corresponding bit masks. The covered range starts inside `DPCSSYS_CR3_LANE2_DIG_TX_PWRCTL_TX_PSTATE_P0` mask definitions, continues through most lane 2 digital/analog PHY field definitions, and then enters lane 3 through ASIC/TX power/RX statistics/TX analog override definitions. It has no executable code, types, storage objects, or functions.

## Purpose

The header gives register-field metadata for low-level AMD display PHY programming. Driver code combines these masks and shifts with the matching address definitions from `dpcs_4_2_0_offset.h` to update 16-bit DPCS CR registers without hard-coding bit positions. In this range, the fields describe:

- Lane 2 TX power-state controls, TX power-up timing, DCC DAC controls, TX clock alignment, TX/RX LBERT, RX power-state controls, RX VCO calibration, CDR/DPLL controls, RX adaptation controls/status, RX statistic counters, MPHY controls, digital analog override/status signals, and lane 2 analog TX/RX registers.
- Lane 3 ASIC override/input/output fields, TX power-state and timing controls, TX DCC DAC controls, TX clock alignment, TX LBERT, RX statistic counters, and the beginning of TX analog override/equalization fields.

## Important APIs, Types, And Macros

There are no APIs or types in this chunk. The important interface is the generated macro convention:

- `DPCSSYS_CR3_LANE*_...__FIELD__SHIFT`: bit offset for `FIELD`.
- `DPCSSYS_CR3_LANE*_...__FIELD_MASK`: mask for the same field after shifting.
- Register comments such as `//DPCSSYS_CR3_LANE2_DIG_RX_ADPTCTL_ADPT_CFG_0` delimit field groups and correspond to `ix...` address macros in the companion offset header.

Notable lane 2 groups include:

- `DIG_TX_PWRCTL_TX_PSTATE_P0/P0S/P1/P2`: per-power-state TX enables for refgen, VCM hold, analog/digital clocks, reset, serial, data, RX detect allowance, VBOOST allowance, and DCC compensation calibration.
- `DIG_TX_PWRCTL_TX_PWRUP_TIME_0..5`: power sequencing delays for refgen, clock enable, VCM hold, VBOOST disable, RX detect, reset, and serial enable.
- `DIG_TX_PWRCTL_DCC_*`: CR bank address/data, DCC DAC control/range/selection/ack/address.
- `DIG_RX_PWRCTL_RX_PSTATE_*` and `DIG_RX_PWRCTL_RX_PWRUP_TIME_*`: RX analog enable, clock/AFE controls, DFE/adaptation enable, CDR tracking, and RX startup timing.
- `DIG_RX_VCOCAL_*`, `DIG_RX_CDR_*`, `DIG_RX_DPLL_*`: VCO calibration, CDR configuration/status, and DPLL frequency/bounds.
- `DIG_RX_ADPTCTL_*`: adaptation configuration and tap/status reporting for ATT, VGA, CTLE, DFE taps, slicer levels, DAC selections, and CR bank access.
- `DIG_RX_STAT_*`: pattern match, sample count, statistic counter, clock, valid-loss, and stop controls.
- `DIG_ANA_*` and `ANA_*`: digital-to-analog override outputs/status plus raw analog TX/RX controls such as term code, equalization, RX clock/CDR, slicer, power, squelch, calibration, ATB measurement, and reserved analog registers.

Notable lane 3 groups include:

- `DIG_ASIC_*`: lane loopback, TX request/PSTATE/rate/width/data and training override controls, ASIC input/output status, RX output status, and handshake/control override fields.
- `DIG_TX_PWRCTL_*`: lane 3 equivalents of the TX power-state, timing, DCC, clock-align, and LBERT controls.
- `DIG_RX_STAT_*`: lane 3 statistic pattern/counter/clock/stop definitions.
- `DIG_ANA_TX_*`: lane 3 TX analog override output, term-code, DCC, and equalization fields; this chunk ends while this family is still in progress.

## Control Flow

This file contributes no runtime control flow. At compile time it lets C code build register values with operations of the form "clear bits using `_MASK`, insert shifted field value using `__SHIFT`, then write to the hardware register address." Runtime sequencing is implemented by display/PHY code outside this header. The implied control paths are hardware sequences such as TX/RX power state transitions, RX VCO/CDR calibration, adaptation, statistics collection, LBERT test setup, and analog override programming.

## State And Persistence

The macros are stateless compile-time constants. The state they describe lives in DPCS hardware registers, not in this header. Register values are volatile hardware state and can be reset by GPU reset, display engine reset, power-gating, suspend/resume, link disable, or PHY reinitialization. Reserved field masks are included so callers can preserve or explicitly avoid touching undocumented bits during read-modify-write sequences.

## Dependencies

This header depends on the ASIC register generation pipeline staying synchronized with AMD hardware specifications. It is normally used with:

- `dpcs_4_2_0_offset.h` for register addresses such as lane 2 offsets around `0x1220` and lane 3 offsets around `0x1320`.
- AMD DRM display/DC code that performs MMIO or indexed DPCS CR register access.
- Common register helper macros in the AMD GPU driver that combine mask/shift constants for read-modify-write operations.

The chunk is independent of Ceph logic despite living under the repository's imported Linux source tree.

## Integration Points

These definitions integrate with display link bring-up, link training, DisplayPort/PHY diagnostic paths, and board/ASIC-specific tuning code. The TX power and analog equalization fields affect transmitter startup and signal quality. RX VCO, CDR, DPLL, adaptation, slicer, and statistic fields affect receiver lock and margining. The LBERT and RX statistic fields are integration points for PHY validation and debug. Lane-specific prefixes are important: lane 2 and lane 3 macros are structurally similar but map to different physical-lane register addresses.

## Risks

- The range begins after the `__SHIFT` definitions for `DPCSSYS_CR3_LANE2_DIG_TX_PWRCTL_TX_PSTATE_P0`; adjacent chunk data is needed for a complete per-register summary.
- The range ends in the middle of lane 3 TX analog override definitions, so the following chunk must complete that register family.
- Copy/paste or generation errors in masks/shifts would cause silent hardware misprogramming; the compiler cannot validate that a field mask matches the actual register layout.
- Writing reserved bits or failing to preserve them can destabilize analog PHY behavior.
- Lane 2 and lane 3 names are highly repetitive; using the wrong lane macro with the wrong offset can program a different physical lane.
- Power-state, reset, VCO/CDR, DCC, and analog override fields are timing-sensitive and can cause link training failures, display blanking, or intermittent high-rate link instability if programmed out of sequence.

## Test Signals

Useful validation signals for changes touching this generated header or consumers of these fields include:

- Kernel build coverage for AMDGPU display code with this header included.
- Static checks that every `__SHIFT` field has a matching `_MASK` field and that masks fit the expected 16-bit DPCS CR register width unless the register is known wider.
- Display bring-up on ASICs using DPCS 4.2.0, including boot display, hotplug, suspend/resume, modesets, and GPU reset recovery.
- Link-training coverage across lane counts and rates, especially configurations using CR3 lane 2 or lane 3.
- DP/HDMI stress tests, high-bandwidth modes, multi-monitor configurations, and retraining after HPD events.
- Debug/validation paths that exercise LBERT, RX statistic counters, CDR/VCO calibration status, DCC DAC selection/acknowledgement, and analog override/status readback.
