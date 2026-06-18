# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 19454-21872

## Purpose

This chunk is a generated AMD DPCS 4.2.3 shift/mask register-field slice for the `DPCSSYS_CR0` DisplayPort/PHY control system. It contains no executable C code; it publishes preprocessor constants that describe bit positions and masks for hardware registers. These constants are paired with `dpcs_4_2_3_offset.h` and consumed by AMDGPU display code through register-table and field helper macros.

The range covers 2,168 `#define` entries over 2,419 source lines. It spans 252 unique register-field macro groups, mostly for `DPCSSYS_CR0_RAWAONLANEX`, `DPCSSYS_CR0_SUPX`, and `DPCSSYS_CR0_LANEX` digital/analog control registers. The source boundaries are artificial: the first lines continue `DPCSSYS_CR0_RAWAONLANEX_DIG_FAST_FLAGS_2` from the previous chunk, and the final line stops inside `DPCSSYS_CR0_LANEX_DIG_RX_CDR_CDR_CTL_4`, leaving later masks to the next chunk.

Although the path is under a `ceph-client` mirror, this header is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, callbacks, locks, allocations, or direct MMIO operations in this chunk. The exported interface is only the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: field mask used to isolate, pack, or update the field.

Major register families in this chunk:

- `DPCSSYS_CR0_RAWAONLANEX_DIG_*`: raw always-on lane controls for fast calibration flags, common-lane RCAL status, TX/RX disable overrides, RX loss-of-signal and signal-detect filtering, RX signal-detect calibration thresholds/codes, RX VREF generation, analog calibration codes, RX/TX DCC calibration and bank access, MPLL bandgap timing, signal-detect output overrides/readbacks, firmware calibration/adaptation data, transceiver mode overrides, and TX DCC configuration.
- `DPCSSYS_CR0_SUPX_DIG_*`: supervisor digital controls for ID code, reference-clock and MPLL A/B divider/HDMI-clock overrides, MPLL A/B override inputs, SSC peak/stepsize controls, charge-pump and gain-scaling overrides, supervisor output overrides, prescaler and level overrides, debug/status, ASIC input mirrors, bandgap input, MPLL power-control state/status/timers/calibration/DAC readback, clock/reset power-up timers, reference VPHUD, RTUNE debug/config/status/set values, analog override outputs, analog status, bandgap override output, and MPLL PMIX override outputs.
- `DPCSSYS_CR0_SUPX_ANA_*`: supervisor analog field definitions for prescaler, RTUNE, bandgap, switch power measurement, MPLL A/B misc/override/ATB/control/reserved registers, and MPLL A/B analog tuning.
- `DPCSSYS_CR0_LANEX_DIG_ASIC_*`: lane ASIC interface override and readback registers for TX, RX, RX equalization, RX CDR/VCO, OCLA, lane mode, and analog PHY buses. These expose override-value and override-enable pairs, ASIC input mirrors, and output/status fields used by low-level PHY bring-up and diagnostics.
- `DPCSSYS_CR0_LANEX_DIG_TX_PWRCTL_*`: TX per-pstate control fields for P0, P0S, P1, and P2, covering TX disable, clock enable, serializer enable, DCC enable, termination, VREG, TX idle, CM enable, AFE enable, signal enable, and power-good indications. The same family includes TX power-up timing fields and TX DCC DAC bank/address/range/ack controls.
- `DPCSSYS_CR0_LANEX_DIG_RX_PWRCTL_*`: RX per-pstate control fields for P0, P0S, P1, and P2, covering RX AFE, VREG, clock, CDR, deserializer, termination, and signal-detect power states, plus RX power-up timing.
- `DPCSSYS_CR0_LANEX_DIG_RX_VCOCAL_*`: RX VCO calibration controls, timers, and status fields for fixed counts, internal-gain calibration, VCO reset/cal reset, continuous calibration, DPLL calibration, frequency tune start/steps, skip bits, startup/update/counter settle timers, FSM state, calibration done, final counter value, VCO too-fast/correct/up status, and analog CDR/VCO readbacks.
- `DPCSSYS_CR0_LANEX_DIG_RX_*`: XAUI comma mask, RX LBERT control/error counter, and RX CDR control fields for phase detector selection, polarity, realignment, spread-spectrum on/off counters, and DPLL gain override values.

## Control Flow

This header has no runtime control flow. It participates in control flow only after inclusion by AMDGPU display resource code. In this tree, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` includes both `dpcs/dpcs_4_2_3_offset.h` and `dpcs/dpcs_4_2_3_sh_mask.h`, making these macros available to DCN 3.1.6 display resource tables.

The runtime pattern is:

1. DCN 3.1.6 resource initialization selects the DPCS 4.2.3 offset and shift/mask headers.
2. Register-list and mask/shift-list macros token-paste register and field names into typed register tables.
3. Link encoder, PHY, AUX/DDC, hotplug, panel, power-management, and debug paths use common AMD display helpers such as register read/write/update/get operations against those tables.
4. Hardware state machines perform the actual analog calibration, MPLL programming, RTUNE, pstate transitions, lane power-up/down sequencing, VCO calibration, CDR tracking, signal-detect filtering, DCC calibration, and LBERT counting.

The macros describe bit layout only. They do not encode read/write direction, reset values, polling order, delays, self-clearing behavior, write-one-to-clear behavior, or ownership by firmware versus driver.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It names MMIO-backed hardware state:

- Calibration state: fast-calibration skips and shortcuts, RCAL init/done, RX signal-detect thresholds and calibration codes, VREF/VPHUD/calibration-code registers, RX and TX DCC calibration values, RTUNE set/status values, MPLL calibration state, and RX VCO calibration status.
- Override state: TX/RX disable overrides, signal-detect output overrides, transceiver mode overrides, reference-clock and MPLL A/B override inputs, charge-pump/gain overrides, supervisor/level/prescaler overrides, analog override outputs, and lane ASIC TX/RX override enable/value pairs.
- Clock and PLL state: reference-clock controls, MPLL A/B divider and HDMI-clock fields, SSC peak/stepsize/spread type, MPLL power-control state/status/timers, DAC max range and analog DAC output, PMIX override outputs, and clock/reset power-up timers.
- Lane power state: TX and RX pstate fields, pstate-specific power enables and power-good readbacks, TX and RX power-up timer fields, TX DCC DAC controls, lane mode/readback, and OCLA/debug state.
- Receive path state: RX loss-of-signal masking, signal-detect filtering, RX VCO calibration, CDR phase detector and spread-spectrum gain settings, XAUI comma mask, LBERT mode/sync/error counter, and RX CDR/VCO ASIC inputs.

Persistence is hardware-defined. Configuration values generally remain until another modeset, link-training pass, suspend/resume path, power-gating transition, firmware action, or GPU reset rewrites them. Status, done, ack, calibration, error, and counter fields may be latched, sampled, sticky, self-clearing, or only valid while the associated clock and power domains are active. The generated header does not state those access semantics.

## Dependencies And Integration Points

This file must stay synchronized with AMD's generated DPCS 4.2.3 register database and with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h`. A shift/mask macro is meaningful only with the matching register address and ASIC base index from the offset header.

Primary integration points:

- `dcn316_resource.c`, which includes the DPCS 4.2.3 offset and shift/mask headers for DCN 3.1.6 resource setup.
- DIO/link-encoder register tables that need lane, PLL, pstate, CDR, VCO, DCC, and signal-detect field locations for DisplayPort and HDMI PHY programming.
- Low-level PHY sequencing code that waits on power-good, calibration-done, VCO status, CDR state, RTUNE status, and signal-detect readbacks.
- Display diagnostics and bring-up flows that use LBERT, OCLA, debug, ASIC input/output mirrors, scratch-like config fields, and analog override/status registers.
- Firmware-adjacent paths that may program or read firmware adaptation/calibration registers and override fields during PHY calibration or training.

## Risks And Edge Cases

- These are untyped preprocessor constants. A bad shift or mask can compile cleanly while updating the wrong hardware bits.
- This is generated metadata. Manual edits risk divergence from AMD's register database, firmware assumptions, and the matching offset header.
- The chunk begins mid-register at `DPCSSYS_CR0_RAWAONLANEX_DIG_FAST_FLAGS_2`; the first several shift fields and the register comment are in the previous chunk. It ends mid-register at `DPCSSYS_CR0_LANEX_DIG_RX_CDR_CDR_CTL_4`, with remaining masks in the next chunk.
- Many fields are override-enable/value pairs. Setting a value without the matching enable bit, or leaving an override enabled after diagnostics, can force the PHY away from normal firmware or hardware-state-machine control.
- Pstate, power-good, clock-enable, serializer/deserializer, CDR, VREG, AFE, signal-detect, and termination fields are sequencing-sensitive. Wrong ordering can leave lanes powered but nonfunctional, fail link training, or increase idle power.
- Analog and calibration fields such as MPLL charge pump, RTUNE, VCO calibration, VREF/VPHUD, DCC, SSC, PMIX, and signal-detect thresholds can pass basic tests but fail at high link rates, after thermal drift, or with marginal cables.
- Status/counter fields such as LBERT error count, calibration done, VCO correct/up, and power-good readbacks may be transient or domain-dependent; polling them without ensuring clocks and power are active can produce false failures.

## Test Signals

Useful validation for this chunk is mostly generated-header and hardware-integration focused:

- Build AMDGPU display support for the DCN 3.1.6 path that includes `dpcs_4_2_3_sh_mask.h`; renamed or missing macros should fail during resource table compilation.
- Mechanically check that visible `__SHIFT` and `_MASK` pairs align within this range while allowing the known boundary exceptions at the beginning and end of the chunk.
- Diff the DPCS 4.2.3 field layout against AMD's generated source and compare repeated families against nearby DPCS 4.2.x headers where layouts are expected to match.
- Exercise DisplayPort and HDMI link training across lane counts, link rates, hotplug, suspend/resume, and DP-alt/USB-C scenarios, watching for stuck waits on pstate power-good, VCO calibration, CDR, signal-detect, RTUNE, or DCC status.
- Run PHY diagnostic paths that use LBERT, OCLA, analog override/status, and ASIC input/output mirrors, then verify normal link operation after overrides are released.
- Monitor kernel logs for AUX timeouts, link-training CR/EQ failures, PLL/VCO calibration timeouts, signal-detect instability, blank displays after resume, high idle power from stuck pstate fields, and connector-specific failures tied to CR0 lane programming.

## Cross-Chunk Notes

This is chunk 9 of `dpcs_4_2_3_sh_mask.h`. The final per-file research should merge this with `subset-b-002393` for the beginning of `DPCSSYS_CR0_RAWAONLANEX_DIG_FAST_FLAGS_2` and with `subset-b-002395` for the rest of `DPCSSYS_CR0_LANEX_DIG_RX_CDR_CDR_CTL_4` and following RX CDR definitions.
