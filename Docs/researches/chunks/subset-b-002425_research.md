# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 94882-97291

## Purpose

This chunk is generated AMDGPU Display Core register metadata for the DPCS 4.2.3 block. It defines C preprocessor constants for bit shifts and masks in the `DPCSSYS_CR4` extended-supervisor and lane-generic namespaces. There is no executable code in this range; the constants are hardware ABI data used with the companion `dpcs_4_2_3_offset.h` indexed-register addresses and AMD display register helper macros.

The requested range starts in the tail of `DPCSSYS_CR4_SUPX_ANA_MPLLB_OVRD` at the `RESET_REG`/reserved fields and ends inside `DPCSSYS_CR4_LANEX_ANA_TX_RESERVED2`. Inside those boundaries it contains 2,167 `#define` lines and 243 register-comment headings. Functionally, it covers the remainder of CR4 supervisor-X MPLLB analog controls, the full CR4 supervisor-X MPLL power-control/status/timer, clock/reset, RTUNE, and analog-override blocks, then the lane-generic `LANEX` digital ASIC interface, TX/RX power and calibration controls, RX adaptation/statistic controls, MPHY controls, digital-to-analog override/status fields, and the beginning of direct analog TX controls.

Although the repository path includes `sources/distributed-fs/ceph-client`, this header is imported GPU display PHY register metadata from the Linux AMDGPU driver tree. It is not Ceph filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, classes, variables, locks, allocation APIs, or direct I/O calls in this chunk. The only API surface is the generated macro naming contract:

- `DPCSSYS_CR4_<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index of a field.
- `DPCSSYS_CR4_<REGISTER>__<FIELD>_MASK` gives the already-shifted bit mask for the field.
- `RESERVED_*` and `NC*` field macros expose generated reserved or no-connect bit ranges. They describe layout, not feature ownership.

Most registers represented here are 16-bit DPCS CR-space registers, with masks such as `0x0001L`, `0x00FFL`, `0x0FC0L`, `0x8000L`, or `0xFFFFL`. Callers are expected to combine field values through AMDGPU display register helpers rather than hand-writing full register words. The shift/mask names are useful only when paired with matching `ixDPCSSYS_CR4_*` offsets from `dpcs_4_2_3_offset.h`; for example the companion offset header places `CR4_SUPX_ANA_MPLLB_ATB1` at `0x8056`, `CR4_SUPX_DIG_MPLLA_MPLL_PWR_CTL_MPLL_OVRD` at `0x8061`, `CR4_LANEX_DIG_ASIC_LANE_OVRD_IN` at `0x9000`, and `CR4_LANEX_ANA_TX_RESERVED2` at `0x90ed`.

Major macro families covered:

- `DPCSSYS_CR4_SUPX_ANA_MPLLB_*`: MPLLB analog ATB measurement muxing, current/charge-pump/reference controls, standby and lock/SPO calibration controls, DLL/divider/bypass controls, and reserved/no-connect ranges.
- `DPCSSYS_CR4_SUPX_DIG_MPLLA_MPLL_PWR_CTL_*` and `DPCSSYS_CR4_SUPX_DIG_MPLLB_MPLL_PWR_CTL_*`: duplicated MPLLA/MPLLB power-control override, FSM/status, DAC range, lock/stable/gearswitch/preset/PCLK timing, calibration override, analog DAC readback, and spread-spectrum spread-type override fields.
- `DPCSSYS_CR4_SUPX_DIG_CLK_RST_*`: bandgap and reference power-up timing fields plus reference `VPH`/`UD` controls.
- `DPCSSYS_CR4_SUPX_DIG_RTUNE_*`: RTUNE debug/config/status, RX/TXDN/TXUP set values and readback, count configuration, and TX calibration code fields.
- `DPCSSYS_CR4_SUPX_DIG_ANA_*`: supervisor digital-to-analog override outputs for MPLLA/MPLLB, RTUNE, bandgap, PMIX, and analog status readback.
- `DPCSSYS_CR4_LANEX_DIG_ASIC_*`: lane-generic ASIC-facing override inputs, ASIC input mirrors, output status, RX EQ/CDR/VCO inputs, TX/RX override output fields, and OCLA selection.
- `DPCSSYS_CR4_LANEX_DIG_TX_PWRCTL_*`: TX P-state programming for P0, P0S, P1, and P2, TX power-up timing, DCC CR-bank access, DCC DAC control/range/select/ack/address fields, clock-alignment controls, and TX LBERT controls.
- `DPCSSYS_CR4_LANEX_DIG_RX_PWRCTL_*`, `RX_VCOCAL_*`, `RX_CDR_*`, and `RX_DPLL_*`: RX P-state programming, RX power-up timings, VCO calibration controls/timers/status, RX alignment/LBERT, CDR controls/status, DPLL frequency, and DPLL frequency bounds.
- `DPCSSYS_CR4_LANEX_DIG_RX_ADPTCTL_*`: RX adaptation state-machine configuration, adaptation reset, ATT/VGA/CTLE/DFE status, slicer and VDAC offsets, DAC-control select registers, and adaptation CR-bank address/data fields.
- `DPCSSYS_CR4_LANEX_DIG_RX_STAT_*`: RX statistic load/mask/match controls, statistic controls, sample count, statistic counters, calibration compare clock control, and statistic stop fields.
- `DPCSSYS_CR4_LANEX_DIG_MPHY_*`: MPHY RX PWM, low-speed termination, and analog PWM clock-stable count controls.
- `DPCSSYS_CR4_LANEX_DIG_ANA_*` and `DPCSSYS_CR4_LANEX_ANA_TX_*`: lane digital-to-analog TX/RX overrides and status readbacks, signal-detect controls, DCC DAC overrides, fast-start/loopback/JTAG fields, direct analog TX measurement, power override, ATB muxing, DCC, termination, clock override, VREG/slew/pre/post and other TX miscellaneous controls.

## Control Flow

This header has no runtime control flow. It contributes constants to control flow implemented elsewhere:

1. DCN resource and link-encoder code includes `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`.
2. AMD display register tables and helper macros token-paste register and field names into offset, shift, and mask constants.
3. Runtime code selects a CR4 indexed register, reads or constructs a register value, inserts field values using the generated shifts and masks, and writes through DPCS CR address/data access paths.
4. DPCS hardware and PHY firmware perform the actual sequencing: MPLL power-up and lock, reference and bandgap settling, RTUNE calibration, TX/RX pstate changes, VCO/CDR/DPLL calibration, RX adaptation, statistics capture, signal detection, DCC control, and analog override readback.

The chunk does not encode ordering requirements. Consumers still need hardware-specific sequences, such as powering references before enabling MPLLs, preserving firmware-owned fields unless override ownership is intended, polling status fields before dependent transitions, and clearing diagnostic or override paths after use.

## State And Persistence Behavior

The macros are compile-time constants and store no software state. They describe volatile and semi-persistent state in DPCS CR-backed hardware registers.

State represented by the CR4 supervisor-X fields includes MPLL power-control FSM state, MPLL lock/cal/reset/analog-enable status, PCLK/FBCLK/output enables, lock and stable timers, gearsift/preset timing, PCLK enable/disable/power-down timers, analog DAC range/readback, SSC spread type, bandgap/reference power timing, RTUNE configured and observed values, RTUNE counters, supervisor analog override outputs, and analog status readback.

State represented by the lane-generic `LANEX` fields includes ASIC ownership/override values, TX and RX pstate enables, power-up and reset timings, DCC DAC requests/updates/acks, TX clock alignment and LBERT configuration, RX VCO calibration control/status, CDR/DPLL tuning/status, adaptation enable/reset/status values for ATT/VGA/CTLE/DFE/slicers, RX statistic matchers/counters, MPHY low-speed controls, TX/RX analog override values, signal-detect calibration values, analog status bits, direct analog TX power/test/ATB/DCC/termination/clock/VREG controls, and reserved/no-connect bit ranges.

Persistence is hardware-defined, not described by this header. Override and configuration fields can remain programmed until the display driver changes them, the PHY is power-gated, firmware retakes ownership, suspend/resume reinitializes the block, or an ASIC/display reset occurs. Status, counter, ack, done, stop, and clear-adjacent fields may be read-only, sticky, self-clearing, write-one-to-clear, or side-effect-sensitive depending on the hardware register definition. The shift/mask header does not record those access semantics.

## Dependencies And Integration Points

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h` supplies the matching CR4 indexed-register offsets. This mask header must stay synchronized with that offset header and the same generated hardware register database.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` directly includes both `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`, selecting this DPCS generation for the DCN 3.1.6 display resource path.
- AMD Display Core register helper infrastructure consumes these macros through generated field descriptors and token-pasted `REG_SET`, `REG_UPDATE`, `REG_GET`, `FD`, `SR`, `SRI`, and related helper patterns.
- Functional integration points include DisplayPort/HDMI PHY bring-up, HPO DP/link encoder resource initialization, link training, lane rate and lane-count transitions, USB-C/MPHY-related low-speed modes, TX/RX power management, RX adaptation, clock/data recovery, signal detection, suspend/resume restore, GPU reset recovery, and diagnostics such as OCLA, LBERT, ATB, DCC, RTUNE, and raw analog override paths.
- The `LANEX` prefix is lane-generic rather than a concrete lane number. Runtime code must combine the intended CR instance, lane selection, and offset/register access path correctly; structurally similar concrete `LANE0`-`LANE3` blocks in other parts of the file are not interchangeable by name alone.

## Risks And Edge Cases

- Bitfield drift is the main risk. These are untyped preprocessor constants, so an incorrect `__SHIFT` or `_MASK` can compile cleanly while programming the wrong PLL, clock, pstate, adaptation, signal-detect, DCC, or analog-control bit.
- The range starts and ends mid-register-family. The beginning of `DPCSSYS_CR4_SUPX_ANA_MPLLB_OVRD` is in the previous chunk, and `DPCSSYS_CR4_LANEX_ANA_TX_RESERVED2` continues after this chunk. The merge lane should use adjacent chunks before making whole-file conclusions.
- Reserved and `NC*` fields are present throughout analog and power-control groups. Full-register writes that do not preserve reserved bits can disturb undocumented hardware behavior.
- Many fields have value/override-enable pairs, such as `*_OVRD_EN`, `*_OVRD`, `*_REG`, or explicit ASIC override/input/output naming. Setting a value without the enable bit may do nothing; leaving override enables asserted after diagnostics can fight firmware or autonomous PHY state machines.
- Supervisor MPLLA/MPLLB groups are duplicated and similarly named. Copying a field between `MPLLA` and `MPLLB` or between supervisor-X and lane analog contexts can target a different clock path while still compiling.
- Status and control fields are close together. Callers must not assume that status masks, ack masks, counter masks, and clear/stop controls share the same write semantics.
- Calibration and analog knobs are sequencing-sensitive. Bad masks in MPLL power/timer/calibration, RTUNE, bandgap/reference power, TX/RX pstate, VCO/CDR/DPLL, RX adaptation, DCC, signal-detect, or direct analog TX controls can appear as blank displays, flicker, intermittent link-training failures, unstable high link rates, broken suspend/resume, or power states that never settle.
- The lane-generic `LANEX` suffix can hide physical-lane context. Register-table generation or debug code must ensure the CR4 access port and lane index match the hardware path under test.

## Test Signals

Useful validation is mostly generated-header and hardware-integration oriented:

- Build AMDGPU Display Core for the DCN 3.1.6 path that includes `dcn316_resource.c`; macro spelling, include ordering, and token-pasted field references should compile cleanly.
- Run generated-header consistency checks that every visible register-comment group has a matching `ixDPCSSYS_CR4_*` offset in `dpcs_4_2_3_offset.h`, every expected field has paired `__SHIFT` and `_MASK` defines, and active masks stay within the expected CR register width.
- Diff this CR4 supervisor-X and lane-generic slice against the authoritative AMD register source and nearby DPCS revisions such as `dpcs_4_2_2` or `dpcs_4_2_0`. Identical names can validate generation; any changed bit positions need ASIC-source confirmation.
- Exercise DisplayPort and HDMI runtime paths on hardware using this DPCS generation: boot display, hotplug, EDID/DPCD access, modeset, link training across rates and lane counts, multi-monitor operation, low-power transitions, suspend/resume, and GPU reset recovery.
- Inspect PHY diagnostics for MPLL power FSM/lock/calibration status, reference and bandgap timing behavior, RTUNE values/status, TX/RX pstate transitions, VCO calibration done/up/correct state, CDR/DPLL frequency bounds, RX adaptation ATT/VGA/CTLE/DFE status, signal-detect thresholds/calibration, DCC DAC ack/update state, LBERT counters, RX statistic counters, and analog status readbacks.
- Regression symptoms include blank or flickering displays, DP training retries/timeouts, HDMI clock instability, failures isolated to one lane or one connector, stuck ACK/done/status bits, stuck power/clock enables, unexpected IRQ or diagnostic behavior in consumers, elevated display power, and impossible counter or status values.

## Boundary Notes For Merge

The first visible lines are not a complete register block: they finish `DPCSSYS_CR4_SUPX_ANA_MPLLB_OVRD` with `RESET_REG` and reserved field metadata. The first full visible register heading is `DPCSSYS_CR4_SUPX_ANA_MPLLB_ATB1`. The final visible block is also incomplete: this chunk reaches `DPCSSYS_CR4_LANEX_ANA_TX_RESERVED2__RESERVED_15_8__SHIFT`, while the corresponding masks and subsequent analog RX blocks continue after line 97291.
