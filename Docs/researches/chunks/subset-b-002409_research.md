# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 55917-58381

## Purpose

This chunk is generated AMD DPCS 4.2.3 shift/mask metadata for the CR2 PHY register space. It contains no executable C logic; it publishes preprocessor constants that describe bit positions and masks for 16-bit indirect DPCS/PCS/PMA registers. Driver code pairs these field constants with the matching address/index constants from `dpcs_4_2_3_offset.h` when programming or reading DisplayPort/HDMI PHY state on DCN 3.1.6-class AMD display hardware.

The requested range covers 2,465 source lines and contains 2,138 `#define` lines grouped under 327 register-comment blocks. The first line is the tail of the prior `DPCSSYS_CR2_RAWAONLANE2_DIG_SIGDET_OUT_OVRD` block, then the chunk covers:

- The end of `DPCSSYS_CR2_RAWAONLANE2` signal-detect, firmware-adaptation, lane transceiver-mode, and TX DCC masks.
- Full `DPCSSYS_CR2_RAWAONLANE3` and generic `DPCSSYS_CR2_RAWAONLANEX` raw always-on lane mask sets for RX adaptation, DFE, CDR/VCO, signal detect, DCC calibration, MPLL background, firmware configuration, override outputs, and lane mode.
- `DPCSSYS_CR2_SUPX` supervisor digital and analog masks for ID, reference clock, MPLLA/MPLLB override, spread spectrum, prescalers, ASIC inputs, bandgap, analog MPLL controls, MPLL power-control/status, RTUNE timing/status, and analog override outputs.
- The start of the generic `DPCSSYS_CR2_LANEX` ASIC lane/TX/RX override mask set, ending inside `DPCSSYS_CR2_LANEX_DIG_ASIC_RX_OVRD_EQ_IN_0`.

Although this file lives under a local `ceph-client` mirror, the content is AMDGPU display-driver hardware metadata and is unrelated to Ceph filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, locks, or allocation APIs in this range. The interface is the generated macro convention:

- `DPCSSYS_CR2_<REGISTER>__<FIELD>__SHIFT`: bit offset for a field in a 16-bit DPCS CR2 register.
- `DPCSSYS_CR2_<REGISTER>__<FIELD>_MASK`: bit mask for that field.
- `DATA__SHIFT` and full-width `DATA_MASK` fields mark raw 16-bit payload registers where the whole register or a low contiguous subfield is meaningful.
- `RESERVED_*` shifts/masks document unused or reserved bits that consumers should preserve during read-modify-write sequences.

Important raw-lane field groups in this chunk:

- `RAWAONLANE2` tail: signal-detect output values, firmware memory/adaptation/calibration configuration, lane transceiver-mode override and observed mode, RX signal-detect filter counters, LF hold, and TX DCC configuration.
- `RAWAONLANE3` and `RAWAONLANEX`: AFE/CTLE IDAC offsets, IQ adaptation, figure-of-merit, DFE summer/phase/data/bypass/error offsets, even/odd reference levels, phase-adjust linear/map fields, coarse MPLLA/MPLLB tuning, initial power-up done, RX adaptation values for ATT/VGA/CTLE/DFE taps 1-5, slicer controls, common calibration MPLL/RCAL status, adaptation control registers 0-7, MPLL disable flags, TX/RX override inputs, RX LOS mask control, signal-detect filtering, lane stats, RX PMA override outputs, signal-detect calibration and code fields, VREF generation, calibration code fields, TX DCC bank address/data/continuous enable, MPLL background control, firmware configuration, lane transceiver mode, and RX signal-detect configuration.
- `FAST_FLAGS` and `FAST_FLAGS_2`: one-bit masks for skipping or accelerating RX/TX startup, adaptation, AFE/DFE/bypass/reference/IQ/DCC/VPHUD/VREF/signal-detect calibration, supervisor paths, TX common-mode/RX-detect handling, VCO wait/calibration, and RTUNE.

Important supervisor (`SUPX`) groups:

- Reference clock and HDMI-mode override fields: ref clock enable/source/range, bandgap enable, HDMI mode enable, and pre-high-power override.
- MPLLA/MPLLB programming fields: divider clock enable/multiplier, HDMI clock dividers, PLL enable/standby/VCO/force-calibration/fract-N/clock-sync fields, spread-spectrum enable/peak/step-size fields, fractional numerator/denominator fields, and charge-pump proportional/integral controls.
- Supervisor-level controls: override input/output, prescaler and level overrides, debug, ASIC input/status views, bandgap analog fields, analog MPLL misc/ATB/control/reserved fields, PLL power-control override/status/timer/calibration/DAC fields, and spread-type fields.
- RTUNE and analog status: RTUNE debug/configuration, RX/TX set values and status, timing counters, TX calibration code, analog MPLL override outputs, RTUNE override output, analog comparator/clock-detect status, bandgap override output, and PMIX override outputs.

Important generic lane (`LANEX`) groups at the end of the chunk:

- Lane-level loopback/AC-JTAG override fields.
- TX override fields for request, power state, rate, width, MPLL selection, data enable, Nyquist/beacon/disable/enables, main/pre/post cursors, HDMI mode, clock-ready, receiver-detect request/result, polarity inversion, low-power detect, DC coupling, PMA extended FIFO, MPHY mode, reset, and TX acknowledgement.
- RX override fields for request/data enable, power state, rate, width, RX reference/VCO load values, CDR track and spread-spectrum enables, alignment, clock shift, disable, low-power detect, inversion, AFE/DFE adaptation enable, termination, reset, and the beginning of equalization override fields (`EQ_ATT_LVL`, `EQ_AFE_GAIN`).

## Control Flow

This header has no runtime control flow. The driver supplies the sequencing:

1. `display/dc/resource/dcn316/dcn316_resource.c` includes `dpcs/dpcs_4_2_3_offset.h` and this matching shift/mask header.
2. DCN resource macros and register tables select an indirect CR2 index from the offset header, such as `ixDPCSSYS_CR2_RAWAONLANE3_DIG_FAST_FLAGS`, `ixDPCSSYS_CR2_SUPX_DIG_RTUNE_CONFIG`, or `ixDPCSSYS_CR2_LANEX_DIG_ASIC_RX_OVRD_EQ_IN_0`.
3. Code constructs field values by shifting to the `__SHIFT` position and applying the corresponding `_MASK`, usually as part of read-modify-write operations through DPCS CR address/data accessors.
4. Higher-level display code controls the actual ordering for link bring-up, PLL programming, spread-spectrum setup, PHY calibration, RX adaptation, signal-detect handling, lane power state, transmitter drive settings, HDMI/DP mode selection, hotplug/retrain, and diagnostics.

The macros do not encode access width beyond the visible 16-bit masks, nor do they identify read-only, write-one-to-clear, sticky, self-clearing, or timing-sensitive fields. Those semantics are hardware-defined and must come from the programming sequence and the surrounding AMD display code.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes hardware register fields that represent and control PHY state. The state is volatile and generally lasts only until the relevant PHY lane, PLL, display link, power domain, suspend/resume path, or ASIC reset reinitializes it.

The represented state includes:

- Per-lane RX analog/adaptation state: ATT, VGA, CTLE, DFE taps, slicer controls, reference levels, IQ/phase adjustment, CDR/VCO control, LOS/signal-detect filtering, VREF generation, DCC calibration code, and PMA override outputs.
- Per-lane TX state: DCC bank addressing/data, continuous DCC enable, TX request/power/rate/width, main/pre/post cursor overrides, beacon/Nyquist/disable flags, receiver-detect handshake, reset, polarity, DC coupling, and MPHY/HDMI-related enables.
- Common/supervisor state: reference clock source/range, bandgap, MPLLA/MPLLB enable/divider/standby/VCO/fract-N/spread-spectrum/charge-pump programming, analog MPLL control/status, PLL power-control timers/calibration/DAC outputs, RTUNE calibration setup/status, and analog comparator/clock-detect status.
- Debug and status state: ID code values, adaptation done/status fields, common calibration status, fast-calibration/skip flags, override output mirrors, and lane statistics.

Reserved masks are part of the state contract. Consumers should preserve reserved bits unless the hardware programming guide explicitly requires a value, because generated masks alone do not prove those bits are harmless.

## Dependencies And Integration Points

The primary dependency is the matching offset/index header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h` supplies CR2 indices for the register names whose fields are defined here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` directly includes both DPCS 4.2.3 headers together with DCN 3.1.6 register headers.

The broader integration pattern is generated register token pasting. Resource code builds register field structures from symbolic names, then link encoder, PHY, panel, and diagnostics paths use those structures through common AMDGPU display register helpers. This chunk's `DPCSSYS_CR2_*` masks are meaningful only when paired with the same-named CR2 offset constants and an access path that targets the CR2 DPCS instance. They are not direct MMIO addresses.

The repeated `RAWAONLANE3` and `RAWAONLANEX` groups are copy-sensitive. `RAWAONLANE3` names a concrete lane-specific set; `RAWAONLANEX` is the generic lane-X form used by generated tables. The `LANEX` block is also generic and may be instantiated by surrounding macros for individual lanes. Adjacent chunks are needed for the complete `LANEX_DIG_ASIC_RX_OVRD_EQ_IN_0` field set and for the rest of the file-level mask map.

## Risks And Edge Cases

- Shift/mask drift is the central risk. These are untyped preprocessor constants, so a wrong mask can compile cleanly while silently writing the wrong PHY bit.
- Offset/mask version mismatches are hazardous. Using `dpcs_4_2_3_sh_mask.h` with a different DPCS offset header can target the right-looking field layout against the wrong CR index.
- Read-modify-write handling matters. Reserved fields dominate many registers (`0xFF00`, `0xFFF0`, `0xFC00`, and similar masks are common), so writes that do not preserve reserved bits can disturb undocumented hardware behavior.
- Calibration and override fields are timing-sensitive. Fast flags, skip flags, force-calibration bits, RTUNE counters, VCO/CDR controls, DCC code fields, and PLL timers can cause intermittent link-training failures if written out of order or left asserted after debug use.
- PLL and spread-spectrum fields affect all lanes sharing a supervisor/PLL path. Bad MPLLA/MPLLB multiplier, divider, fractional, charge-pump, standby, or SSC programming can break a whole link or only specific rates.
- Signal-detect and LOS masks influence hotplug/link recovery. Incorrect signal-detect thresholds, filters, override values, or LOS mask fields can cause false link presence, missed receiver detect, HPD/retrain instability, or noisy diagnostics.
- Generic lane macros can be misapplied to the wrong lane instance. The concrete `RAWAONLANE3` and generic `RAWAONLANEX`/`LANEX` namespaces are similar but not interchangeable without the generated instance mapping.
- The chunk boundary is artificial. It starts with the last mask of a previous register block and ends partway through `DPCSSYS_CR2_LANEX_DIG_ASIC_RX_OVRD_EQ_IN_0`, so final per-file conclusions must reconcile adjacent chunks.

## Test Signals

- Build coverage for DCN 3.1.6 resource code is the baseline signal; renamed or missing field macros should fail wherever generated register structures reference them.
- Static consistency checks should verify that each non-raw field has both `__SHIFT` and `_MASK`, mask widths align with shift positions, reserved masks do not overlap named masks, and `dpcs_4_2_3_offset.h` contains matching CR2 indices for the register names in this range.
- Register-generation checks should compare this header with nearby generated versions (`dpcs_4_2_0`, `dpcs_4_2_2`, `dpcs_3_1_4`, or `dcn_4_1_0` where applicable) to catch accidental field-layout drift.
- Hardware display tests should exercise DP and HDMI link bring-up across lane counts and link rates, hotplug/retrain cycles, receiver-detect behavior, suspend/resume, and multi-display routing through the CR2 PHY instance.
- PHY-focused tests should watch for link-training failures, VCO/CDR lock instability, DCC or RTUNE calibration errors, signal-detect/LOS false positives, DP alternate-mode failures, lane-specific bit errors, and regressions that appear only after repeated modesets or power transitions.
- Debug validation should include readback of representative raw-lane, supervisor, RTUNE, and LANEX override/status registers after programming to confirm masks preserve reserved bits and field values round-trip as expected.
