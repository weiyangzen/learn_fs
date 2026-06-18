# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 102363-104913

## Scope

This chunk is a large generated AMD DPCS 4.2.3 shift/mask header slice. The requested range spans 2,551 source lines, 2,120 `#define` entries, and 431 visible register-group comments. Every definition in this range is a `__SHIFT` macro; the matching `_MASK` macros are outside this slice. The range starts inside `C20_PHY_CR0_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S`, after that register group's first fields, and ends on the comment for `C20_PHY_CR0_LANE3_DIG_ASIC_TX_OVRD_IN_4`, before any fields for that lane 3 register appear.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior. It is declarative C preprocessor data for DPCS CR0 PHY register bit positions.

## Purpose

`dpcs_4_2_3_sh_mask.h` gives AMD display code symbolic names for bitfields in DPCS 4.2.3 hardware registers. Consumers pair these `__SHIFT` values with the companion `_MASK` values and register offsets to build, update, and decode indirect PHY registers without open-coding numeric bit positions.

This chunk documents a CR0 lane-local area:

- The tail of lane 1 RX power-control, VCO calibration, CDR, adaptation, statistics, IQ calibration, and digital-to-analog RX transfer fields.
- A complete lane 2 TX/RX digital and analog-transfer shift block, covering ASIC overrides, power sequencing, DCC, statistics, LBERT, TX/RX analog override outputs, status readback, and raw analog control register fields.
- The start of lane 3 digital ASIC TX override definitions, ending before `TX_OVRD_IN_4` fields.

The repeated lane structure is important: lane 2 largely mirrors lane 1 patterns, so small generator errors can be lane-specific while still compiling cleanly.

## Important APIs, Types, And Macros

There are no callable functions, structs, enums, global variables, allocations, locks, or runtime register accesses in this range. The exported interface is only generated preprocessor constants of the form:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a field within a DPCS hardware register.

The main macro families covered are:

- `C20_PHY_CR0_LANE1_DIG_RX_PWRCTL_*`: lane 1 RX power-state tables for P0S/P1/P2, RX power-up timing, manual RX clock/control fields, and RX power-state status.
- `C20_PHY_CR0_LANE1_DIG_RX_VCOCAL_*` and `C20_PHY_CR0_LANE1_DIG_RX_CDR_*`: lane 1 RX VCO calibration controls, timers, status readback, CDR control, SSC on/off counters, DPLL gain overrides, DPLL frequency values, and DPLL frequency bounds.
- `C20_PHY_CR0_LANE1_DIG_RX_ADPTCTL_*`: lane 1 RX adaptation configuration, reset, CTLE/VGA/ATT/DFE tap status, slicer controls, VDAC/IDAC offsets, DCC offsets, fast flags, and SSM configuration/final-code fields.
- `C20_PHY_CR0_LANE1_DIG_RX_STAT_*` and `C20_PHY_CR0_LANE1_DIG_RX_IQC_CTL_*`: lane 1 RX statistic load/match/control/counter fields and IQ calibration reset/config/status fields.
- `C20_PHY_CR0_LANE1_DIG_ANA_XF_RX_*`: lane 1 digital-to-analog RX control, power, signal-detect, VCO, calibration, DAC, AFE, scope, slicer, IQC, loopback, termination, status, and analog CREG fields.
- `C20_PHY_CR0_LANE2_DIG_ASIC_*`: lane 2 digital ASIC lane/TX/RX override inputs, ASIC input mirrors, output mirrors, RX signal-detect/VCO/equalization overrides, and miscellaneous override controls.
- `C20_PHY_CR0_LANE2_DIG_TX_*`: lane 2 TX power states, TX power-up timing, TX control/status, DCC controls, TX statistic collection, clock alignment, LBERT pattern/control fields, level calculation status, and FIFO control.
- `C20_PHY_CR0_LANE2_DIG_ANA_XF_TX_*`: lane 2 digital-to-analog TX override outputs, termination-code controls, DCC calibration controls/data, TX EQ override/status fields, analog status inputs, and analog TX CREG fields.
- `C20_PHY_CR0_LANE2_DIG_RX_*` and `C20_PHY_CR0_LANE2_DIG_ANA_XF_RX_*`: lane 2 RX power, VCO, CDR, adaptation, statistics, IQC, analog-transfer, and raw analog CREG fields corresponding closely to the lane 1 RX block.
- `C20_PHY_CR0_LANE3_DIG_ASIC_*`: the first lane 3 ASIC lane and TX override shifts through `TX_OVRD_IN_3`; `TX_OVRD_IN_4` is only introduced by comment at the chunk boundary.

Because this slice contains no `_MASK` definitions, any runtime use requires the later mask half of the generated header or adjacent chunk coverage. The shift names alone are not enough for a full `REG_UPDATE`-style read/modify/write unless paired with masks from the same generated namespace.

## Control Flow

This file has no local control flow. At runtime, behavior is supplied by AMDGPU display code that includes this header and uses generated register tables plus MMIO or indexed-register helpers.

The typical usage path is:

1. DCN316 display resource code includes `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`.
2. Register, shift, and mask tables are constructed with DCN31-style DPCS macros.
3. Link encoder, PHY bring-up, link training, modeset, hotplug, suspend/resume, or diagnostics code calls register helpers against those tables.
4. These `__SHIFT` constants tell the helper where to position field values inside the underlying 16-bit-style DPCS CR registers.

The header does not encode ordering constraints, wait loops, retry policy, access permissions, reset values, clear-on-read/write-one-to-clear behavior, or power-domain validity.

## State And Persistence Behavior

No software state is stored or persisted by this chunk. The named fields describe hardware-visible state in CR0 lane registers. Configuration state persists according to the ASIC's PHY, clock, reset, and power domains, not according to this header.

The lane 1 and lane 2 RX fields represent several hardware state areas:

- RX power-state tables and power-up timers for analog front-end enable, clock regulator/divider enables, clock DCC, deserializer, CDR, VCO reset/calibration, continuous calibration, digital clocks, DFE, and bypass slicer controls.
- VCO/CDR/DPLL state for calibration counters, startup/update/settle timers, VCO FSM state, calibration-done readback, DPLL frequency, and frequency bounds.
- RX adaptation state for CTLE, VGA, attenuation, DFE taps, slicer levels, adaptation reset, DFE data/error/bypass VDAC offsets, DCC phase/data/bypass IDAC offsets, fast flags, and SSM final-code calculation.
- RX statistic and IQC state for pattern masks, match controls, statistic sources, sample/stat counters, stop controls, calibration comparison clocks, IQ adjustment resets, and IQ calibration status.
- RX analog-transfer state for power overrides, signal-detect calibration, VCO overrides, AFE overrides, scope/slicer controls, loopback, termination, CREG analog controls, measurement/test-bus selections, and status readback.

The lane 2 TX fields represent TX power sequencing, DCC compensation, clock alignment, LBERT, statistic capture, TX EQ, termination, analog clock/reset/serial/data overrides, and analog TX CREG state. The lane 2 and lane 3 ASIC override fields include value plus enable pairs for forcing reset, request, pstate, rate, width, MPLL selection, RX detect request, equalization, signal-detect, VCO, loopback, and related lane handshakes.

Fields named `*_STATUS`, `*_STAT`, `*_STAT_OUT_*`, `*_ASIC_OUT`, `*_CAL_RESULT`, `*_ACK`, or `*_DONE` are readback-oriented by name. Fields named `*_OVRD_IN`, `*_OVRD_EN`, `*_PSTATE_*`, `*_PWRUP_TIME_*`, `*_CFG_*`, `*_CTL`, or `*_CREG*` are configuration-oriented by name. The actual read/write permissions and latch semantics must come from the hardware register database and the driver access layer.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, this generated header must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h`, which supplies the corresponding DPCS 4.2.3 register offsets.
- The later `_MASK` definitions in this same `dpcs_4_2_3_sh_mask.h` file.
- AMD's authoritative DPCS 4.2.3 register database and any firmware or validation scripts that consume the same CR0 lane register layout.

The direct include site for this DPCS 4.2.3 header in the tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`. That file includes the offset and shift/mask headers and initializes DCN31-style DPCS register, shift, and mask tables with `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST`. The DPCS table macros are declared in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h`.

Behaviorally, these fields integrate with display link bring-up below the user-visible display stack:

- DisplayPort and HDMI link training, rate changes, lane power transitions, and PHY reset/request sequencing.
- TX and RX analog calibration, DCC calibration, VCO/CDR lock, DPLL tuning, CTLE/VGA/DFE adaptation, and signal-detect handling.
- Link diagnostics and validation flows using LBERT, RX/TX statistic counters, match registers, analog test-bus selections, scope/slicer controls, and status readback.
- Hotplug recovery, suspend/resume, GPU reset, and modeset paths that must reinitialize lane-local PHY state and clear temporary override enables.

## Risks And Edge Cases

- This chunk is shift-only. A later merge or audit must pair these shifts with the correct masks before making whole-register claims.
- The range starts inside `LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S`, so the first two P0S fields are owned by the previous chunk. It ends on the `LANE3_DIG_ASIC_TX_OVRD_IN_4` comment with no fields for that register in this chunk.
- Generated-header drift is the main technical risk. A wrong shift compiles successfully but can place a value into an adjacent RX adaptation, VCO, CDR, power, EQ, DCC, termination, or override bit.
- Lane repetition makes errors easy to miss. Lane 2 mostly mirrors lane 1, but a single lane-specific mismatch can cause failures only on certain connector routing, link widths, or lane remapping paths.
- Override fields usually require coordinated value and enable bits. Setting only a value has no effect, while leaving an override enable asserted can hold the PHY away from normal state-machine control after diagnostics or recovery.
- RX adaptation, VCO/CDR, DPLL, DCC, and analog CREG fields are sequencing-sensitive. Incorrect bit positions can create unstable links, failed training, false status reads, bad calibration, or stuck polling loops.
- Status, control, reserved, and test fields are represented by identical macro syntax. Callers need hardware access metadata to avoid writing read-only/status bits or disturbing reserved/test-only regions.
- Some values are split across low/high or repeated counter registers. Partial updates to statistic loads, counters, VCO timing, DCC values, or analog measurement selectors can produce misleading debug output.

## Test Signals

Useful validation is mostly compile-time, generator-level, and hardware-integration oriented:

- Build AMDGPU display support for DCN316/DPCS 4.2.3 so missing or malformed macros are caught when DPCS register, shift, and mask tables are initialized.
- Mechanically verify the full header's generated consistency: every complete field should have a matching `__SHIFT` and `_MASK`, allowing chunk-boundary exceptions for the start of lane 1 `RX_PSTATE_P0S` and the end comment for lane 3 `TX_OVRD_IN_4`.
- Cross-check this slice against `dpcs_4_2_3_offset.h` and the DPCS 4.2.3 register source database, especially the lane 1 to lane 2 to lane 3 transitions.
- Compare repeated lane 1/lane 2/lane 3 field layouts where hardware expects symmetry, while preserving any intentional lane-specific differences.
- Exercise DP and HDMI link training across rates, widths, power states, and connector/lane mappings that use CR0 lanes 1, 2, and 3.
- Test hotplug, modeset, stream disable/enable, suspend/resume, GPU reset, and failed-link recovery paths while checking that temporary override-enable bits are cleared.
- Use register dumps or PHY traces during hardware tests to confirm RX power-state transitions, VCO calibration done/state, CDR/DPLL frequency state, adaptation done/status, DFE tap status, statistic counters, IQC status, signal-detect status, and TX/RX DCC status decode correctly.
- Run diagnostics where available for LBERT, RX/TX statistic matching, analog test-bus paths, scope/slicer controls, loopback, TX EQ override/readback, and termination-code override/readback.

## Chunk Notes For Merge

This document intentionally covers only lines 102363-104913 of `dpcs_4_2_3_sh_mask.h`. Adjacent chunks must provide the missing beginning of `C20_PHY_CR0_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S`, all matching mask definitions, and the fields following the `C20_PHY_CR0_LANE3_DIG_ASIC_TX_OVRD_IN_4` boundary. The final per-file research document should treat this source as generated AMD display PHY register metadata rather than handwritten runtime logic.
