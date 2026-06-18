# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 9585-11943

## Scope And Purpose

This chunk is part of AMDGPU's generated DPCS 4.2.0 register bitfield mask header. It contains C preprocessor constants for shift positions and bit masks, not executable code. The constants describe how the display PHY/DPCS register interface encodes lane-specific TX, RX, analog, calibration, adaptation, status, and test/debug fields.

The requested range starts inside the lane 1 analog RX clock group, then completes lane 1 analog RX control/measurement fields, covers almost all of lane 2's digital and analog PHY bitfield definitions, and ends at the beginning of lane 3 digital ASIC lane override fields. The dominant pattern is one `__SHIFT` macro and one `_MASK` macro for each hardware register field. Driver code elsewhere can combine these definitions with register address definitions and AMD's register access helpers to build read-modify-write values without hard-coding bit positions.

## Register Groups Covered

The line range contains 2,141 `#define` lines. Major source-aligned blocks are:

- Lane 1 analog RX tail: `DPCSSYS_CR0_LANE1_ANA_RX_CLK_2` through `DPCSSYS_CR0_LANE1_ANA_RX_RESERVED1` define IQ phase adjustment, loopback clock, CDR/deserializer controls, slicer controls, AFE/DFE/deserializer/loopback power overrides, signal-detect threshold/response, calibration mux selection, ATB/regulator measurement controls, and reserved low-byte fields.
- Lane 2 digital ASIC override and direct inputs/outputs: `DPCSSYS_CR0_LANE2_DIG_ASIC_*` defines software override versions and normal ASIC versions of lane loopback, TX request/pstate/rate/width/MPLL/data enable, cursor/equalization, detect-RX, inversion, low-power detect, reset, RX CDR/VCO load values, adaptation enables, termination, ACK/valid/status, OCLA, repeat/master-lane clock synchronization, and MPHY/PWM controls.
- Lane 2 TX power control: `DPCSSYS_CR0_LANE2_DIG_TX_PWRCTL_*` describes per-power-state TX analog/digital enable recipes for P0, P0S, P1, and P2 plus power-up timing fields and DCC DAC control registers.
- Lane 2 RX power, VCO, CDR, adaptation, and statistics: `DPCSSYS_CR0_LANE2_DIG_RX_*` includes RX pstate recipes, RX power-up timers, VCO calibration control/time/status, XAUI comma mask, LBERT control/error count, CDR/SSC/DPLL controls and status, adaptation configuration/status/reset, pattern matching/stat counters, and statistic stop controls.
- Lane 2 digital-to-analog override outputs and analog controls: `DPCSSYS_CR0_LANE2_DIG_ANA_*` and `DPCSSYS_CR0_LANE2_ANA_*` define the values driven from digital logic into analog TX/RX blocks, plus direct analog TX/RX register fields for termination, DCC, ATB, EQ, scope, IQ phase, slicer, VCO, calibration DAC, power, and status.
- Lane 3 boundary: the final lines start `DPCSSYS_CR0_LANE3_DIG_ASIC_LANE_OVRD_IN`, proving this chunk ends mid-register-group before the complete lane 3 block.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or callable APIs in this chunk. The public interface is a generated macro namespace:

- `DPCSSYS_CR0_LANE<n>_*__<field>__SHIFT` gives the low bit position for a field.
- `DPCSSYS_CR0_LANE<n>_*__<field>_MASK` gives the unshifted 32-bit mask literal, usually occupying the low 16 bits because these CR lane registers appear to expose 16-bit register payloads through a wider C type.
- `RESERVED_*`, `NC*`, and `RSVD_*` fields document non-functional or undocumented bit ranges and are still emitted as masks so generated tables preserve exact register layout.

The intended consumers are AMDGPU display/DPCS code paths that write memory-mapped or indirect control registers using kernel register helper macros such as field preparation, field get/set, or read-modify-write wrappers. The source path under `drivers/gpu/drm/amd/include/asic_reg/dpcs` indicates this header participates in ASIC-specific display register programming, not in Ceph filesystem logic despite the repository subtree prefix.

## Control Flow

This header has no runtime control flow. Hardware control flow is implied by the register group layout:

- Override registers pair a data field with an `*_OVRD_EN`, `*_OVRD`, or `EN` bit. Driver code must set the enable bit when it wants the software-provided value to replace the normal PHY/ASIC signal.
- Pstate registers encode predefined TX and RX power sequencing states. Higher-level link training, mode-set, suspend/resume, or hotplug paths can select pstate behavior indirectly by programming these fields.
- Time registers encode wait/settle counters such as `TX_REFGEN_EN_TIME`, `TX_VCM_HOLD_TIME`, `RX_AFE_EN_TIME`, `RX_CLK_EN_TIME`, and VCO startup/update/counter settle times. These constants let sequencing code pack timing parameters consistently with hardware layout.
- Status registers expose ACK, valid, detect-RX, calibration done/result, VCO counter/final frequency, adaptation code, and LBERT error count fields for polling or diagnostics.

Because the chunk spans repeated lane blocks, lane index is part of the contract. A caller using a lane 1 mask against a lane 2 address, or using the partial lane 3 definitions at the end without the continuation in the next chunk, would program or decode the wrong hardware field.

## State And Persistence Behavior

The file itself is compile-time-only and persists no runtime state. The state affected by consumers is hardware register state in the display PHY:

- TX/RX enable, reset, clock, data, pstate, loopback, polarity inversion, width, rate, MPLL selection, and low-power fields control live lane behavior.
- Analog override fields can force TX term codes, EQ/cursor values, RX AFE gain/attenuation/CTLE, slicer controls, IQ phase, calibration muxes, VCO tuning, and termination behavior.
- Calibration, adaptation, DPLL, CDR, and SSC fields influence hardware training algorithms and may affect link stability until overwritten or the PHY is reset.
- Status and counter fields are read-only or observation-oriented from the driver's perspective, but their interpretation depends on prior programming of enable, reset, timing, and pattern-match fields.

Persistence is at the hardware register level. Values can survive across parts of a mode-set or training sequence until a lane reset, block reset, power-gate transition, or subsequent register write changes them. The macros themselves impose no locking, ordering, polling, or reset semantics.

## Dependencies And Integration Points

This header depends on a matching register address header for `dpcs_4_2_0` and on the AMDGPU display stack's common register access machinery. It integrates with:

- DPCS/RDPCS display link programming for DisplayPort/HDMI/PHY bring-up.
- Lane training and equalization code that sets TX cursors, post/pre emphasis, rate, width, data enable, CDR, DPLL, and adaptation parameters.
- Power management paths that program TX/RX pstate recipes and power-up/down timing.
- Debug, manufacturing, and validation tools that use ATB, OCLA, LBERT, scope, DCC DAC, VCO, and statistic counter fields.
- ASIC register generation tooling. The highly regular naming and repeated lane layout indicate this file is generated from hardware register specifications; manual edits would be fragile.

The constants are tightly coupled to the DPCS 4.2.0 hardware revision. Reusing them for another ASIC revision requires confirming that the address map and bitfield layout are identical.

## Risks And Edge Cases

- This chunk starts and ends mid-logical sequence: lane 1 `ANA_RX_CLK_2` begins before line 9585, and lane 3 `DIG_ASIC_LANE_OVRD_IN` continues after line 11943. Any merged documentation must reconcile adjacent chunks to avoid treating partial groups as complete.
- Mask/shift mismatches in generated headers are high-impact. A one-bit error in pstate, reset, VCO, DPLL, or override-enable fields can produce display link bring-up failures, unstable clocks, or lanes stuck in reset/low power.
- Reserved and `NC` fields are exposed as masks. Driver code should preserve reserved bits during read-modify-write unless hardware documentation explicitly requires writing a value.
- Many fields are only meaningful when paired with an override enable or self-clear-disable bit. Writing the value field alone may have no effect; leaving override enables set after diagnostics may interfere with normal link training.
- Lane-specific duplication invites copy/paste mistakes. Lane 2 masks should be used with lane 2 register addresses; lane 1 and lane 3 names are not interchangeable even when bit layouts match.
- Timing fields are packed into small bit widths. Out-of-range software values must be clamped or validated before shifting, otherwise high bits can spill into adjacent fields if the caller does not mask properly.
- Status fields such as VCO calibration done, RX adaptation status, LBERT overflow, and detect-RX results may be transient. Polling code needs hardware-appropriate timeouts and reset/clear handling outside this header.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, register-generation, and hardware-oriented:

- Build tests that include `dpcs_4_2_0_sh_mask.h` from representative AMDGPU display translation units and catch macro spelling or duplicate-definition problems.
- Generated-header consistency checks that verify every `__SHIFT` field has the expected `_MASK`, masks are contiguous for multi-bit fields, masks match the documented shift and width, and repeated lane 1/lane 2 layouts agree where the hardware spec says they should.
- Register access unit tests or static checks around field packing helpers to ensure values are masked before shifting and reserved bits are preserved in read-modify-write paths.
- Hardware or emulator tests for lane 2 link bring-up, pstate transitions, hotplug detect, DisplayPort/HDMI training, suspend/resume, and lane reset sequences.
- Diagnostic tests for ATB/OCLA/LBERT/stat counters, including counter overflow (`OV14`), sample stop, pattern match/mask programming, and VCO calibration status polling.
- Regression signals in kernel logs and display tests: link training failures, blank screens after mode-set, unstable high-bandwidth modes, repeated PHY reset/retrain messages, or mismatched RX/TX ACK/status polling after changes to generated register headers.
