# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 66437-68800

## Scope

This chunk is a generated AMD NBIO 6.1 shift/mask header segment for the Synopsys DesignWare E12MP x4 PCIe PHY namespace `DWC_E12MP_PHY_X4_NS_X4_1`. It contains C preprocessor constants only; there are no functions, structs, variables, branches, loops, allocations, locks, reference counts, or direct hardware accesses in this range.

The assigned range starts in the middle of `LANE1_DIG_ASIC_RX_OVRD_IN_0`, after the `RESET`, `INVERT`, `DATA_EN`, and `REQ` shift definitions that appear immediately above this chunk. It covers the rest of the lane-1 digital ASIC RX override register, the remaining lane-1 digital ASIC interface masks, lane-1 TX/RX power-control and VCO-calibration fields, lane-1 LBERT/CDR/DPLL/RX-adaptation/statistics fields, lane-1 digital and analog TX/RX control/status fields, then continues into the beginning of the equivalent lane-2 block. The final line is the `XAUI_COMM_MASK` mask for `LANE2_DIG_RX_RX_ALIGN_XAUI_COMM_MASK`; the `RESERVED_15_10` mask and later lane-2 RX LBERT/CDR fields are in the following chunk.

Although this file is located under a local `ceph-client` source mirror, the content is AMDGPU hardware register metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this range is to publish bit positions and masks for NBIO 6.1 PCIe PHY lane registers. Each hardware field is represented by a pair of macros:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when extracting or composing the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, clear, or set the field.

Consumers combine these field definitions with matching register address/default metadata from the NBIO register database. Runtime code normally reaches the registers through AMDGPU register helpers and field helpers such as `RREG32`, `WREG32`, `SOC15_REG_OFFSET`, `REG_GET_FIELD`, and `REG_SET_FIELD`, depending on the register aperture and call site.

## Important Macro Families

The lane-1 `DIG_ASIC_*` groups describe the digital boundary between ASIC control logic and the PHY lane. They include lane loopback controls, TX and RX override inputs, TX/RX ASIC inputs, TX/RX ASIC outputs, RX equalization inputs, RX CDR/VCO ASIC inputs, request/acknowledge handshakes, rate/width/power-state fields, polarity inversion, data enable, low-power detect, RX adaptation enable, RX/TX detect, beacon, boost, cursor, termination, loss-of-signal, and enable/status fields.

The lane-1 TX power-control groups define per-power-state enables and timing for `P0`, `P0S`, `P1`, and `P2`. The masks cover TX clock/data/driver/boost/ibias/VREG enable state, coefficient update behavior, rate-change timing, driver enable/disable timing, and similar power-up sequencing knobs.

The lane-1 RX power-control and VCO-calibration groups define receiver analog and digital power-state state, RX LOS/AFE/clock/VREG/divider/deserializer/CDR enables, VCO frequency/calibration reset and continuous calibration controls, RX adaptation power-up control, VCO startup/update/counter-settle timing, calibration control fields, and VCO status fields such as FSM state, calibration done, final counter value, VCO too-fast/correct/up indications, and analog CDR/clock status bits.

The lane-1 RX alignment, LBERT, CDR, and DPLL families expose protocol and diagnostic controls. They include XAUI comma mask fields, TX/RX LBERT mode/sync/error-count fields, CDR phase detector and realignment controls, lock and frequency status, DPLL frequency and bound fields, and related reserved masks.

The lane-1 RX adaptation and statistics groups are the densest part of this chunk. `DIG_RX_ADPTCTL_ADPT_CFG_0..9` and `RST_ADPT_CFG` describe adaptation configuration such as FOM, attenuation, VGA, CTLE, DFE tap behavior, dwell counts, calibration thresholds, lock/restart behavior, and adaptation reset selection. Status and offset groups report or program ATT/VGA/CTLE/DFE tap states, even/odd data and error slicer DAC offsets, bypass offsets, slicer controls, and error-slicer level. `DIG_RX_STAT_*` fields provide load values, data masks, match controls, status controls, sample counts, statistic counters, and calibration compare clock control.

The lane-1 digital analog (`DIG_ANA_*`) and analog (`ANA_*`) groups publish masks for TX/RX analog override outputs, termination-code override outputs, TX equalization override outputs, RX control/power/VCO overrides, RX calibration and DAC controls, AFE attenuation/VGA and CTLE, scope/slicer/IQ phase controls, analog status, TX measurement/power/alt-bus/ATB/VBOOST/termination/IBOOST/clock/misc controls, and RX ATB/DCC/power/CDR-AFE/misc/calibration mux/termination/slicer/VREG controls.

The lane-2 portion begins a repeated generated lane layout for the same PHY instance. This chunk includes lane-2 `DIG_ASIC_*`, TX/RX power-control, RX VCO-calibration, TX LBERT, and the first three definitions for RX XAUI comma masking. Lane-2 RX LBERT, CDR, adaptation, statistics, and analog families continue in later lines.

## APIs, Types, And Functions

There are no C APIs, types, or functions in this chunk. The exported interface is the generated macro namespace consumed by AMDGPU code that includes `nbio/nbio_6_1_sh_mask.h` or `asic_reg/nbio/nbio_6_1_sh_mask.h`.

Direct include sites for this header include `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, and PowerPlay include aggregators such as `pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h`. These include sites do not imply every macro in this chunk is referenced directly; generated hardware headers intentionally expose a larger register database than any one driver path uses.

## Control Flow

There is no executable control flow in this header. Runtime behavior happens in including code:

1. Driver, firmware-assist, or diagnostic code selects a NBIO/SMN PHY register for the target lane.
2. It reads the register through the AMDGPU register access layer.
3. It extracts fields with the corresponding `__SHIFT` and `_MASK` macros.
4. It composes new values for lane reset, override, power-state, calibration, equalization, loopback, diagnostic, or status-control programming, then writes the result back if the register is writable.

For this range, likely runtime contexts are PCIe PHY bring-up, link training, lane power-state transitions, suspend/resume, GPU reset recovery, RX adaptation and CDR/VCO calibration, TX equalization/termination tuning, loopback/BERT diagnostics, and low-level board or ASIC validation.

## State And Persistence Behavior

The header stores no software state and persists nothing. It describes bit layout for hardware-backed PHY state owned by NBIO, the PHY lane sequencers, firmware/hardware initialization, AMDGPU runtime code, and the PCIe link partner.

The represented state includes lane override requests, TX/RX handshakes, rate/width/power-state controls, TX cursor/boost/termination controls, RX equalization and adaptation controls, RX AFE/DFE/VGA/CTLE/slicer offsets, CDR/DPLL/VCO calibration controls and status, link test/error counters, statistic counters, and analog override/status state. Some fields are static tuning controls, some are hardware-updated status, some are counters, and some are write-sensitive reset/clear/override fields. The masks do not encode reset defaults, ownership, read/write permissions, side effects, timing requirements, or safe sequencing.

The paired `nbio_6_1_default.h` contains reset/default values for the same register families, including defaults such as lane-1 RX override and ASIC input zeros, nonzero lane-1 RX override/equalization and power-state timing values, VCO/CDR/DPLL/adaptation defaults, and lane-2 defaults through this chunk's boundary. The masks in this file must stay aligned with those defaults and any matching address definitions in the generated NBIO register database.

## Dependencies And Integration Points

The primary dependency is consistency with generated NBIO 6.1 register metadata:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h` provides reset/default values for these lane register names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_smn.h` and related generated address headers provide NBIO/SMN register address metadata for adjacent register families.
- AMDGPU register and field helper macros provide the read/modify/write and extraction mechanics.

Integration points include NBIO v6.1 initialization and query logic, MxGPU/SR-IOV paths that depend on stable PCIe link behavior, Vega10/Vega12 PowerPlay code that includes NBIO register definitions, PSP or firmware-mediated reset flows, display/resource code that consumes NBIO state indirectly, and hardware diagnostics that validate PHY tuning against generated register metadata. Broader integration is with PCIe link training, lane equalization, low-power states, runtime power management, suspend/resume, reset/FLR recovery, and platform-specific signal-integrity tuning.

## Risks And Edge Cases

- Chunk boundaries are artificial. The first line is inside `LANE1_DIG_ASIC_RX_OVRD_IN_0`, and the last line is inside `LANE2_DIG_RX_RX_ALIGN_XAUI_COMM_MASK`; adjacent chunks are required for complete register families.
- The macros are untyped preprocessor constants. A stale shift, wrong mask, or lane-number mixup can compile cleanly while programming the wrong field.
- Lane-1 and lane-2 names are highly repetitive. Copy/generation drift can produce subtle per-lane differences that are difficult to catch by visual inspection.
- Override and enable fields can bypass normal PHY sequencer ownership. Incorrect RX/TX reset, request, data-enable, disable, low-power, rate, width, or power-state programming can stall link bring-up or make link state inconsistent with driver policy.
- TX equalization, boost, cursor, termination, and analog controls are signal-integrity sensitive. Bad values can cause link training failures, high error rates, speed downgrades, or board-specific instability.
- RX AFE, CTLE, VGA, DFE, slicer, CDR, DPLL, and VCO fields are calibration-sensitive. Incorrect masks can break adaptation, lock detection, VCO calibration, or recovery after speed changes and suspend/resume.
- LBERT, statistic, and diagnostic fields may be counter-like, clear-on-write, or hardware-updated. Naive read/modify/write can lose diagnostic evidence or leave test modes active.
- Reserved masks are present throughout the generated data. Consumers must preserve reserved bits according to hardware requirements and should not infer writability from the presence of a mask.
- Applying lane-1 masks to lane-2 offsets, or vice versa, may produce plausible bit arithmetic while controlling the wrong physical lane.

## Test Signals

Useful validation is mostly build-time generated-header consistency plus hardware and platform integration testing:

- Build AMDGPU with NBIO 6.1, Vega10/Vega12, PowerPlay, and virtualization-relevant options enabled. Missing or renamed macros should surface in include users or register helper call sites.
- Compare this range against `nbio_6_1_default.h` and address metadata to confirm lane-1/lane-2 register names, field ordering, masks, and defaults remain synchronized.
- On NBIO 6.1 hardware, exercise cold boot, warm reboot, GPU reset, driver unload/reload, suspend/resume, and runtime power transitions while monitoring PCIe link speed, width, retraining, AER/link errors, and recovery latency.
- Run PCIe link stress, DMA traffic, and power-state transition tests across supported link speeds to catch RX/TX power-control, CDR/VCO, and adaptation regressions.
- Use hardware diagnostics or lab tooling where available to validate TX equalization/termination, RX adaptation status, DFE/CTLE/VGA/slicer behavior, VCO calibration done/up/correct status, and DPLL bounds.
- Exercise LBERT/loopback/statistic paths if exposed by platform tooling, verifying that mode, sync, error-count, sample-count, match-control, and counter fields behave as expected.
- For multi-lane links, verify lane-specific programming by comparing lane-1 and lane-2 readbacks and ensuring per-lane failures are not hidden by aggregate link status.

## Chunk Notes

- Lines 66437-66458 finish most of `LANE1_DIG_ASIC_RX_OVRD_IN_0`; the register comment and first four shift fields are above this chunk.
- Lines 66459-66786 cover lane-1 digital ASIC override/input/output and RX equalization/CDR/VCO interface fields.
- Lines 66787-66980 cover lane-1 TX/RX power-state, power-up timing, RX VCO calibration, RX alignment, and LBERT fields.
- Lines 66981-67434 cover lane-1 RX CDR, DPLL, adaptation configuration/status, and RX statistic fields.
- Lines 67435-67888 cover lane-1 digital analog and analog TX/RX control/status fields.
- Lines 67889-68800 start lane-2 and proceed through digital ASIC, TX/RX power control, RX VCO calibration, TX LBERT, and the first field mask for RX XAUI comma masking.
