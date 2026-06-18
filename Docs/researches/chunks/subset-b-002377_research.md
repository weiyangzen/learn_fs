# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 95293-97714

## Scope

This chunk covers lines 95293-97714 of the generated AMD DPCS 4.2.2 shift/mask header. It is a partial view of one oversized source file; the final source-file research document should be produced later by the chunk merge lane.

The chunk contains 2,084 `#define` constants grouped under 338 register-comment blocks. All definitions are preprocessor constants, not executable logic. Each hardware field normally appears as a pair of macros:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

These constants describe bit positions and bit masks for DPCS CR4 raw-lane, PCS/PMA, interrupt, FSM, ATE, and always-on-lane registers used by AMD display code.

## Purpose

The header provides compile-time metadata for programming DisplayPort/DPCS PHY registers on DCN 3.1.5-era AMD display hardware. This chunk is centered on `DPCSSYS_CR4`, especially:

- tail definitions for `RAWLANE3` PCS transmit/receive control, PMA bridge, finite-state-machine, interrupt, test, and calibration registers;
- repeated `RAWAONLANE0`, `RAWAONLANE1`, and the beginning of `RAWAONLANE2` always-on lane status/control fields for RX adaptation, DFE, signal detect, MPLL, calibration, DCC, and firmware configuration.

The companion offset header (`dpcs_4_2_2_offset.h`) supplies register addresses such as `ixDPCSSYS_CR4_RAWAONLANE1_DIG_RX_SIGDET_CONFIG` and `ixDPCSSYS_CR4_RAWAONLANE2_DIG_RX_LOS_MASK_CTL`; this header supplies the field layout needed to read, mask, shift, and update those registers correctly.

## Important APIs, Types, and Macros

There are no C functions, structs, enums, or runtime APIs in this chunk. The important exported surface is the macro namespace consumed by AMD display register helpers.

Key macro families in the chunk include:

- `DPCSSYS_CR4_RAWLANE3_DIG_PCS_XF_*`: PCS cross-interface fields for TX/RX resets, requests, rates, widths, power states, MPLL state, VCO/ref load values, RX adaptation, RX/TX pre/main/post direction, lane number, ATE overrides, equalization, termination, and phase-2 calibration.
- `DPCSSYS_CR4_RAWLANE3_DIG_FSM_*`: FSM override/status fields, fast calibration/adaptation selectors, common-calibration status, register/memory lock bits, TX DCC flags/status, OCLA enable bits, TX EQ update flag, RCAL status, and RX IQ phase offset.
- `DPCSSYS_CR4_RAWLANE3_DIG_IRQ_CTL_*`: interrupt request, clear, and mask bits for RX reset/request/rate/pstate/adaptation events, lane transceiver-mode changes, RX phase-2 calibration events, loopback events, on-demand DCC events, and TX reset/request events.
- `DPCSSYS_CR4_RAWLANE3_DIG_PMA_XF_*`: PMA bridge fields for lane/MPLL enables, supervisor state, TX/RX override outputs, RTUNE control, MPHY override, RX adaptation override output, and PMA-side signal state.
- `DPCSSYS_CR4_RAWLANE3_DIG_TX_CTL_*` and `DPCSSYS_CR4_RAWLANE3_DIG_RX_CTL_*`: TX/RX FSM, clock, DCC, OCLA, LOS mask, data-enable override, off-channel continuous status, and adaptation continuous status fields.
- `DPCSSYS_CR4_RAWLANE3_DIG_PCS_XF_ATE_*`: automated-test-equipment override definitions for RX/TX PCS inputs, data enables, loopback, beacon, async data, LOS LFPS, LOS threshold, adaptation, VCO, and ref-load overrides.
- `DPCSSYS_CR4_RAWAONLANE[0-2]_DIG_*`: repeated per-lane always-on definitions for adaptation readback, DFE offsets, RX phase/slicer controls, MPLL/RCAL status, adaptation control words, RX/TX disable overrides, LOS/signal-detect controls, analog stats, PMA signal overrides, signal-detect calibration, DCC calibration codes, TX DCC bank access, MPLL bandgap controls, firmware config, lane transceiver mode, and DCC/sigdet config.

The densest multi-field registers in this chunk are `FAST_FLAGS`, `FAST_FLAGS_2`, `PCS_XF_ATE_OVRD_IN`, `PMA_XF_TX_OVRD_OUT`, `PCS_XF_TX_OVRD_IN_1`, `PCS_XF_RX_PCS_IN`, and `IRQ_CTL_IRQ_MASK`.

## Control Flow

The chunk has no local control flow. Its values participate in control flow indirectly when AMD display code uses register-helper macros such as `REG_GET`, `REG_UPDATE`, `LE_SF`, `SRI`, and related DC resource-table initializers.

Observed integration in the surrounding tree:

- `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes both `dpcs/dpcs_4_2_2_offset.h` and this `dpcs/dpcs_4_2_2_sh_mask.h`.
- The same resource file builds DPCS register, shift, and mask tables with `DPCS_DCN31_REG_LIST(id)` and `DPCS_DCN31_MASK_SH_LIST(__SHIFT/_MASK)`.
- Runtime code later uses those tables through AMD display register access helpers, so these macros become the bitfield contract for register reads/writes rather than direct function calls.

Because this is generated register metadata, any meaningful runtime sequence is owned by the display link encoder, HPO encoder, resource, hardware sequencer, or PHY programming code that consumes these constants.

## State and Persistence Behavior

This chunk does not allocate memory or persist software state. Its constants describe persistent hardware register state in DPCS PHY blocks:

- request/ack/reset bits represent hardware handshakes for PCS/PMA TX and RX paths;
- power, width, rate, MPLL, VCO, ref-load, and pstate fields represent lane configuration state;
- adaptation, DFE, CTLE, VGA, slicer, signal-detect, and phase-adjust fields expose analog calibration state;
- interrupt mask/clear/status fields represent sticky or event-driven hardware state;
- `*_OVRD_*` fields can force hardware behavior away from normal FSM-driven values;
- `FAST_FLAGS` and calibration-status fields capture fast-path calibration enablement and completion state.

The values are persistent only as compiled constants in the driver binary; the actual state lives in MMIO/indirect DPCS registers on the GPU.

## Dependencies

Direct dependencies are preprocessor-level only:

- the header guard `_dpcs_4_2_2_SH_MASK_HEADER`;
- matching register-address definitions in `dpcs_4_2_2_offset.h`;
- AMD display register-access macros that expect `__SHIFT` and `_MASK` naming conventions.

The chunk is tightly coupled to the DPCS 4.2.2 hardware register specification. Neighbor headers (`dpcs_4_2_0_sh_mask.h`, `dpcs_4_2_3_sh_mask.h`) contain similar definitions but with version-specific line placement and sometimes literal formatting, so cross-version substitution should be treated as hardware-sensitive.

## Integration Points

The primary integration point is AMDGPU display core for DCN 3.1.5 resources. The dcn315 resource code includes this header and the companion offset header, defines DPCS base segments, and populates link encoder mask/shift structures.

The definitions are also part of a generated ASIC register include tree under `drivers/gpu/drm/amd/include/asic_reg/dpcs/`. Code that builds per-link encoder resources, DisplayPort PHY controls, or DPCS/RDPCS register tables depends on the names and masks matching both the offset header and the actual silicon register layout.

Within this chunk, integration boundaries include:

- PCS-side link training and lane control via TX/RX request, reset, rate, width, pstate, MPLL, and adaptation fields;
- PMA-side analog control via MPLL enables, RTUNE, MPHY, RX/TX PMA override, signal detect, and calibration fields;
- interrupt plumbing via `DIG_IRQ_CTL_*` request, clear, and mask definitions;
- debug/test flows via ATE override registers and OCLA fields;
- firmware or microcontroller policy hooks via `FW_MM_CONFIG`, `FW_ADPT_CONFIG`, and `FW_CALIB_CONFIG` always-on-lane registers.

## Risks and Edge Cases

- Bitfield drift is the primary risk. A wrong shift or mask can silently program the wrong hardware bit, causing link-training failure, display blanking, unstable signal detect, broken calibration, or bad interrupt behavior.
- Override fields are high risk because many pairs include both value and enable bits. Setting an override value without the corresponding enable bit, or leaving an enable bit asserted after debug/test use, can force the PHY into an unexpected state.
- Repeated lane blocks are easy to copy incorrectly. `RAWAONLANE0`, `RAWAONLANE1`, and `RAWAONLANE2` share many field layouts, but callers must still use the matching register address for the intended lane.
- Reserved masks are present throughout. Runtime code should avoid writing reserved bits except through documented reset values or read-modify-write helpers that preserve them.
- Interrupt clear and mask registers have similar names but different semantics. Mixing `*_IRQ`, `*_IRQ_CLR`, and `*_IRQ_MSK` fields can lose events or leave interrupts permanently masked.
- This chunk starts after the beginning of `DPCSSYS_CR4_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN` and ends inside `DPCSSYS_CR4_RAWAONLANE2_DIG_RX_SIGDET_FILT_CTRL`; final whole-file research must merge with adjacent chunks to capture complete register families.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware-integration oriented:

- successful AMDGPU/DC display compilation with `dcn315_resource.c` including `dpcs_4_2_2_sh_mask.h`;
- no duplicate or missing macro errors when generating `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)`;
- static comparison against the vendor register database or neighboring generated headers for expected DPCS 4.2.2 field positions;
- display link-training and hotplug tests on DCN 3.1.5 hardware using multiple lanes/rates, watching for RX/TX request/ack, pstate/rate, MPLL, signal-detect, and adaptation regressions;
- interrupt behavior tests that exercise RX request/rate/pstate/adaptation, lane mode, phase-2 calibration, DCC, and TX request/reset events;
- PHY calibration diagnostics that confirm `FAST_FLAGS`, DCC/RCAL/MPLL status, RX adaptation done, and signal-detect calibration fields report sane values.

## Chunk Notes for Merge Lane

This chunk should be merged with adjacent chunks of the same header to build a source-file-level report. Adjacent context is needed for the complete `DPCSSYS_CR4_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN` block before line 95293 and the rest of `DPCSSYS_CR4_RAWAONLANE2` after line 97714.
