# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 197622-199999

## Purpose

This chunk is part of a generated AMDGPU DCN 3.2 register field mask/shift header. It contains no executable C logic; its purpose is to publish compile-time constants for bitfield access to DCN 3.2 `C20_PHY_CR4` PHY lane registers.

The range covers the tail of the Lane 1 RX analog/receiver field definitions and the beginning-to-mid portion of the Lane 2 PHY lane definitions. Each register field is represented by paired macros:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit position.
- `REGISTER__FIELD_MASK` gives the already-positioned mask used for extraction or insertion.

Driver code combines these constants with register addresses from `dcn_3_2_0_offset.h` and accesses hardware through the display and amdgpu register access layers. The file is therefore a hardware layout contract: correctness depends on exact generated masks and shifts, not on local algorithms.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or storage objects in this chunk. The macro namespace is the API surface.

The chunk begins in the final mask line for `C20_PHY_CR4_LANE1_DIG_ANA_XF_RX_VCO_OVRD_OUT_1`, then covers Lane 1 RX analog crossover and calibration registers including:

- VCO/CDR tuning and overrides: `RX_VCO_OVRD_OUT_2`, CDR frequency tune clock/value, and override enable bits.
- RX calibration controls: `RX_CAL_0`, `RX_CAL_1`, VDAC range select, calibration DAC control/select/enable, DCC calibration DAC range, slicer calibration, and comparator enable fields.
- Analog front-end controls and overrides: attenuation level, VGA gain, AFE rate, CTLE pole/boost, bias, VCM adjustment, RTRIM, slicer control, scope/debug selection, loopback, IQ sync and IQ calibration bypass/data controls.
- RX status and sideband exchange fields: termination-code override/status, `RX_STAT_OUT_0/1`, `RX_STAT_IN_0`, and sampling selectors for DFE, bypass, and phase paths.
- Raw analog control registers: `RX_ANA_CREG00` through `RX_ANA_CREG11` and `RX_ANA_CREG0_OVRD`/`RX_ANA_CREG1_OVRD`.

It then switches to Lane 2 and defines a large portion of the lane's TX and RX PHY control surface:

- Lane and ASIC-side overrides: `LANE_OVRD_IN`, `ASIC_TX_OVRD_IN_0..5`, `ASIC_TX_OVRD_OUT`, `ASIC_LANE_ASIC_IN`, `ASIC_TX_ASIC_IN_*`, `ASIC_TX_ASIC_OUT`, `ASIC_TX_OVRD_MISC`, and the corresponding RX override/ASIC handoff registers.
- Lane 2 TX power, timing, calibration, and test controls: TX pstate registers `P0/P0S/P1/P2`, power-up timing registers, TX control/status, DCC IDAC offset/status controls, statistics counters, clock alignment, LBERT pattern/error-test controls, level calculation, FIFO control, TX analog crossover override/status/equalization fields, TX termination-code overrides, and TX analog `CREG` fields.
- Lane 2 RX power and receiver controls: RX pstate and power-up timing, RX control/status, VCO calibration controls/timers/status, RX LBERT control/error count, CDR controls/status, DPLL frequency and bounds, and receiver adaptation configuration/status.
- Lane 2 adaptation controls at the end of the chunk: `RX_ADPTCTL_ADPT_CFG_0..9`, reset bits for ATT/VGA/CTLE/DFE/DCC/AFE adaptation paths, and status fields for attenuation, VGA, and the beginning of CTLE adaptation status.

Most fields are 16-bit register slices, with explicit `RESERVED_*` masks included. The names indicate a hardware split between direct analog register fields (`ANA_XF_*`), ASIC/PHY handoff and override controls (`ASIC_*_OVRD_*`), link test/debug blocks (`LBERT`, statistics, scope), clock/data recovery and DPLL (`CDR`, `VCOCAL`, `DPLL`), and equalization/adaptation controls (`ADPTCTL`, CTLE, VGA, DFE, ATT).

## Control Flow

This file has no runtime control flow. It is a flat list of preprocessor constants.

A typical consumer flow is:

1. Select a DCN 3.2 register address from `dcn_3_2_0_offset.h`, usually through a generated register table or macro wrapper in display/amdgpu code.
2. Read a 32-bit register value through the DCN register access helpers.
3. Extract a field with `(value & REGISTER__FIELD_MASK) >> REGISTER__FIELD__SHIFT`, or clear and insert a value using the same pair.
4. Write the register back only when the hardware programming sequence permits changing that field.

The control-sensitive behavior exists in the hardware registers described here. Examples include forcing TX/RX resets, overriding pstate/rate/width/data-enable requests, enabling loopback, selecting calibration sources, starting or bypassing calibration clocks, driving CDR/VCO/DPLL parameters, changing CTLE/VGA/DFE adaptation knobs, and clearing or resetting adaptation paths. The header does not encode safe ordering, delay, polling, or power-state requirements.

## State And Persistence Behavior

The header stores no software state and has no persistence mechanism. It describes hardware state in the DCN PHY.

The described hardware state includes lane power states, clock readiness, PHY reset/data-enable/request handshakes, link-test configuration, TX/RX calibration values, analog override enables, CDR/VCO/DPLL frequency state, RX equalization/adaptation thresholds and step sizes, sampled status counters, and final/adapted AFE or equalizer codes.

Persistence depends on the specific register semantics and platform sequencing. Some fields are static strap or status observations, some are self-clearing trigger clocks or start bits, some are sticky status/error indicators, and many are override controls that remain active until firmware or driver code clears them, the display PHY block is reset, the link is retrained, or power management gates the block. The mask header does not distinguish read-only, write-only, self-clearing, sticky, or reserved fields beyond the generated field names.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.2 register map and its matching address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h`

Direct includes of the DCN 3.2 offset and mask headers in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`

The exact `C20_PHY_CR4_LANE*` symbols are primarily register-map metadata, not a normal function API. They are integrated indirectly through generated register tables, display core hardware sequencers, DMUB/DCN32 support, clock management, GPIO/HPD/DDC translation, interrupt programming, and low-level amdgpu/DCN register access macros.

Although this source is under a local `ceph-client` mirror, this chunk has AMDGPU display PHY semantics. It has no Ceph filesystem protocol, distributed-storage, or filesystem persistence behavior.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong mask or shift can compile cleanly while reading the wrong status bit, programming a neighboring field, or leaving an intended override disabled.

High-risk fields include override enables and reset controls. Misusing `*_OVRD_EN`, `RESET_OVRD_*`, pstate/rate/width overrides, data-enable/request overrides, loopback bits, and adaptation reset bits can force a PHY lane away from the hardware sequencer's expected state, block link bring-up, or leave stale calibration active across a modeset or resume.

Calibration and analog fields are also sensitive. CDR/VCO/DPLL tuning, VDAC/DAC control, DCC calibration, CTLE/VGA/DFE/ATT thresholds and adaptation gains, AFE bias/VCM/trim, termination codes, and slicer controls directly affect signal integrity. Incorrect constants can produce intermittent display link failures that only reproduce on specific lanes, bit rates, cables, panels, or power-transition paths.

Status fields can be misleading if decoded with the wrong bit layout. Fields such as `ASM1_DONE`, adaptation state/code values, DPLL frequency bounds, VCO calibration status, LBERT errors, TX/RX statistics, and termination-code outputs are likely used for bring-up diagnostics or hardware workarounds; a mask bug can point debugging at the wrong lane or analog path.

The generated lane namespaces are repetitive. Lane 1 and Lane 2 blocks have similar register names with different base offsets, making copy/generation mistakes hard to notice in review. A valid-looking macro attached to the wrong lane prefix would fail only when that physical lane is exercised.

This chunk has artificial line-boundary splits. It starts after the beginning of `C20_PHY_CR4_LANE1_DIG_ANA_XF_RX_VCO_OVRD_OUT_1` and ends before the remaining fields of `C20_PHY_CR4_LANE2_DIG_RX_ADPTCTL_CTLE_STATUS` and subsequent Lane 2 adaptation status registers. The final per-file merge should treat those as chunk boundaries, not source-file omissions.

## Test Signals

Useful validation signals are mostly build-time, register-map, and hardware-behavior oriented:

- Kernel build coverage for DCN 3.2 display/amdgpu paths that include `dcn_3_2_0_sh_mask.h`; malformed or missing macros should surface as compile failures.
- Generated-register consistency checks comparing every `*_MASK`/`*__SHIFT` pair against AMD's source register database and the adjacent address definitions in `dcn_3_2_0_offset.h`.
- Display link bring-up tests across all relevant physical lanes, rates, lane counts, and connector types that exercise TX/RX power, reset, data-enable, CDR, DPLL, equalization, and calibration paths.
- Suspend/resume, runtime power management, hotplug, modeset, and link-retraining tests that confirm override and calibration state is restored or cleared as expected.
- PHY diagnostics that read VCO calibration status, CDR status, DPLL frequency/bounds, adaptation status codes, `ASM1_DONE`, LBERT error counters, and TX/RX statistics to confirm decoded values match expected hardware behavior.
- Signal-integrity and compliance testing for high-bit-rate display modes, where bad CTLE/VGA/DFE/DCC/DPLL masks would appear as training failures, link drops, visual corruption, or lane-specific error accumulation.

Regression symptoms from bad constants include display links failing only on some lanes, reduced maximum link rate, repeated retraining, blank screens after resume or hotplug, unstable high-bandwidth modes, incorrect PHY debug readouts, and diagnostics showing adaptation completion or error state on the wrong field.

## Cross-Chunk Notes

Earlier chunks of `dcn_3_2_0_sh_mask.h` define the beginning of the DCN 3.2 register mask namespace, including earlier Lane 1 PHY TX/RX and the first part of the Lane 1 RX VCO override registers. Later chunks continue Lane 2 RX adaptation status and the rest of the DCN 3.2 mask header. The final per-file research document should treat the full header as one generated hardware register layout contract rather than independent algorithms per chunk.
