# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 57192-59638

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for display PHY raw always-on lane registers under the CR2 indirect register space. It contains no executable driver logic; its public surface is preprocessor metadata that maps hardware register fields to bit positions (`__SHIFT`) and masks (`_MASK`).

The requested range contains 2,447 source lines, 2,071 `#define` entries, and 376 register-comment markers. It starts inside `DPCSSYS_CR2_RAWAONLANE0_DIG_RX_ADPT_ATT`: the register comment and `ATT_ADPT_VAL__SHIFT` are just before this chunk, while this range begins at `RESERVED_15_8__SHIFT` and the masks. It then covers the remainder of lane 0's raw always-on RX adaptation, calibration, signal-detect, DCC, firmware, and lane-mode fields; full corresponding blocks for `RAWAONLANE1`, `RAWAONLANE2`, and `RAWAONLANE3`; and most of the generic `RAWAONLANEX` template block. The range ends at the bare comment for `DPCSSYS_CR2_RAWAONLANEX_DIG_TX_DCC_CONT`; that register's shift and mask defines follow in the next chunk.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO accesses in this range. The only exported interface is generated macro names following the DPCS convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit index for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: mask used to read, compose, or update that field.

The main register families in this chunk are:

- RX adaptation readback and control: `DIG_RX_ADPT_ATT`, `DIG_RX_ADPT_VGA`, `DIG_RX_ADPT_CTLE`, `DIG_RX_ADPT_DFE_TAP1` through `TAP5`, `DIG_RX_ADPT_IQ`, `DIG_RX_ADAPT_FOM`, `DIG_RX_ADAPT_DONE`, and `DIG_ADPT_CTL_0` through `DIG_ADPT_CTL_7` expose attenuation, VGA, CTLE, DFE tap, IQ, figure-of-merit, done, and opaque adaptation-control fields.
- DFE, slicer, and phase state: `DIG_DFE_*_VDAC_OFST`, `DIG_DFE_*_REF_LVL`, `DIG_DFE_SUMMER_ODD_IDAC_OFST`, `DIG_RX_SLICER_CTRL_EVEN`, `DIG_RX_SLICER_CTRL_ODD`, `DIG_RX_PHSADJ_LIN`, `DIG_RX_PHSADJ_MAP`, and `DIG_RX_IQ_PHASE_ADJUST` describe even/odd data, error, bypass, phase, reference, and slicer adjustment values.
- Lane power, MPLL, and calibration status: `DIG_INIT_PWRUP_DONE`, `DIG_MPLLA_COARSE_TUNE`, `DIG_MPLLB_COARSE_TUNE`, `DIG_LANE_CMNCAL_MPLL_STATUS`, `DIG_LANE_CMNCAL_RCAL_STATUS`, `DIG_MPLL_DISABLE`, and `DIG_MPLL_BG_CTL` describe initial power-up, PH2 power-up, common calibration init/done, MPLL disable, coarse tune, and MPLL background wait/delay controls.
- Fast calibration/adaptation flags: `DIG_FAST_FLAGS` and `DIG_FAST_FLAGS_2` provide bitfields for accelerated RX startup/adaptation, AFE/DFE/bypass/reference/IQ calibration, supervisor and TX/RX-detect flows, RX power/VCO waits, continuous calibration/adaptation, TX/RX DCC calibration, VPHUD/VREF calibration, RTUNE skipping, and signal-detect calibration.
- TX/RX disable, lane mode, and firmware controls: `DIG_TXRX_OVRD_IN`, `DIG_LANE_XCVR_MODE_OVRD_IN`, `DIG_LANE_XCVR_MODE_IN`, `DIG_FW_MM_CONFIG`, `DIG_FW_ADPT_CONFIG`, and `DIG_FW_CALIB_CONFIG` define override enables/values, lane transceiver mode fields, and firmware configuration words.
- RX loss-of-signal, squelch, and signal-detect controls: `DIG_RX_LOS_MASK_CTL`, `DIG_RX_SIGDET_FILT_CTRL`, `DIG_STATS`, `DIG_RX_OVRD_OUT_1` through `DIG_RX_OVRD_OUT_3`, `DIG_RX_SIGDET_CAL`, `DIG_RX_SIGDET_HF_CODE`, `DIG_RX_SIGDET_LF_CODE`, `DIG_RX_VREFGEN_EN`, `DIG_SIGDET_OUT_OVRD`, `DIG_SIGDET_OUT_IN`, and `DIG_RX_SIGDET_CONFIG` describe LOS mask timing, signal-detect filters, squelch/VREF status, PMA squelch and termination overrides, signal-detect calibration thresholds/tunes, VREF generator enable, and filtered signal-detect outputs.
- RX and TX DCC/calibration code storage: `DIG_CAL_IOFF_CODE`, `DIG_CAL_ICONST_CODE`, `DIG_CAL_VREFGEN_CODE`, `DIG_RX_DCC_CAL_ICM_CODE_*`, `DIG_RX_DCC_CAL_IDF_CODE_*`, `DIG_RX_DCC_CAL_QCM_CODE_*`, `DIG_RX_DCC_CAL_QDF_CODE_*`, `DIG_TX_DCC_BANK_ADDR`, `DIG_TX_DCC_BANK_DATA`, `DIG_TX_DCC_CONT`, and `DIG_TX_DCC_CONFIG` expose DCC calibration code words, banked TX DCC access, DCC continuous mode, and configuration fields.

Most masks in this region are 16-bit-style values with an `L` suffix, matching the DPCS indirect register width used by these raw always-on lane blocks. The `RAWAONLANE0` through `RAWAONLANE3` blocks map to concrete lanes; `RAWAONLANEX` is the lane-X/template form with the same field layout and separate offsets.

## Control Flow

This header has no runtime control flow. It participates in compile-time construction of AMD display register tables:

1. Driver code for the matching ASIC generation includes the DPCS 4.2.2 offset header and this shift/mask header.
2. Version-specific register, shift, and mask tables token-paste these generated names into structures used by AMDGPU Display Core hardware helpers.
3. Runtime paths call register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` against those tables.
4. Actual sequencing for link bring-up, RX equalization, DFE/CTLE/VGA adaptation, signal detection, DCC calibration, MPLL/power management, lane-mode changes, and firmware-assisted PHY flows lives outside this generated header.

The macros only encode bit layout. They do not encode access type, reset value, ordering requirements, clock-domain requirements, polling timeout, write-one-to-clear behavior, self-clearing semantics, or read-only/write-only status.

## State And Persistence Behavior

This chunk stores no software state and persists nothing itself. It names hardware-visible state in the CR2 raw always-on lane register windows:

- Per-lane adaptation state includes attenuation, VGA, CTLE, DFE tap values, IQ values, FOM readback, adaptation done, DFE VDAC/IDAC offsets, even/odd reference levels, slicer controls, phase adjustment maps, and opaque adaptation control words.
- Per-lane power and PLL state includes initial and PH2 power-up done bits, MPLLA/MPLLB coarse-tune values, common MPLL/RCAL calibration init/done status, MPLL disable bits, and MPLL background wait/delay controls.
- Per-lane fast-flow state includes fast RX startup, adaptation, AFE/DFE, bypass, reference-level, IQ, supervisor, TX common-mode, RX-detect, RX power-up, VCO wait/VCO calibration, continuous calibration/adaptation, DCC, VPHUD/VREF, RTUNE skip, and signal-detect calibration flags.
- Signal-detect and RX front-end state includes LOS mask count, high/low-frequency signal-detect filter controls, PMA squelch status, VREF generator status/enable, PMA squelch/termination/signal-detect override values and enables, signal-detect calibration thresholds and tune codes, and filtered output override/readback fields.
- Calibration and DCC state includes IOFF, ICONST, VREFGEN, RX DCC ICM/IDF/QCM/QDF code words for banks 0 and 1, TX DCC bank address/data, TX DCC continuous enable, and TX DCC configuration.
- Firmware and mode state includes firmware microcode/configuration fields, firmware adaptation and calibration control bits, lane transceiver mode override and readback fields, and TX/RX disable overrides.

Persistence is hardware-defined. Configuration fields typically remain until a modeset/link reprogram, PHY power-gating event, suspend/resume, GPU reset, ASIC reset, firmware sequence, or driver initialization rewrites them. Status, done, calibration, and readback fields may be sampled, latched, self-clearing, or valid only while the relevant lane, MPLL, firmware, or always-on power domain is active. This header does not define those semantics.

## Dependencies And Integration Points

This file must stay synchronized with AMD's DPCS 4.2.2 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies the matching `ixDPCSSYS_*` offsets. The concrete lane windows use regular offset blocks, for example lane 0 `0x4000` through `0x4051`, lane 1 `0x4100` through `0x4151`, lane 2 `0x4200` through `0x4251`, lane 3 `0x4300` through `0x4351`, and lane-X/template offsets `0x7000` through `0x7051`.
- The immediate range begins at lane 0 offset `0x4017` (`RX_ADPT_ATT`) and proceeds through lane 0 offset `0x4051`; it then covers the complete lane 1, lane 2, and lane 3 raw always-on offset groups and the lane-X group through the `TX_DCC_CONT` boundary at `0x7047`.
- AMDGPU Display Core resource, link encoder, PHY, and diagnostics code consumes these generated masks through versioned register tables instead of hard-coding the bit values.
- Link training, hotplug/modeset, power management, firmware-controlled PHY calibration, DisplayPort/HDMI PHY bring-up, signal-detect handling, and debug register dumps are the most likely consumers of the state described here.
- Firmware and hardware state machines may also read or update the same registers, especially for fast adaptation/calibration, DCC tuning, signal-detect filtering, common calibration, and power-up completion.

Behaviorally, this chunk is below the user-facing display stack. It defines the raw bit layout needed when higher layers configure or diagnose per-lane PHY adaptation and calibration on DPCS 4.2.2 hardware.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while corrupting reserved bits, writing the wrong lane field, or decoding hardware status incorrectly.
- The header is generated metadata. Manual edits risk divergence from AMD's authoritative register database, firmware expectations, silicon documentation, and `dpcs_4_2_2_offset.h`.
- Chunk boundaries are artificial. The first register, `DPCSSYS_CR2_RAWAONLANE0_DIG_RX_ADPT_ATT`, is split: its comment and `ATT_ADPT_VAL__SHIFT` are in the previous chunk. The last register, `DPCSSYS_CR2_RAWAONLANEX_DIG_TX_DCC_CONT`, is also split: only the comment is inside this range, while its actual defines follow in the next chunk.
- Lane repetition is copy-sensitive. Lanes 1, 2, and 3 should remain layout-compatible with lane 0, and the `RAWAONLANEX` template should remain compatible with the concrete lane forms where intended. A generator error could affect one lane while neighboring lanes look correct.
- RX adaptation fields are link-training-sensitive. Incorrect masks around CTLE, VGA, attenuation, DFE taps, IQ, FOM, slicer, phase adjustment, or done bits can lead to unstable equalization, retraining loops, or misleading diagnostics.
- DCC and calibration fields affect electrical timing. Bad masks for RX DCC code words, TX DCC banked access, TX DCC continuous mode, VREF generator, IOFF/ICONST, or signal-detect calibration can cause black screens, marginal links, or rate-specific failures.
- Override fields can bypass normal state-machine behavior. Incorrect TX/RX disable, lane mode, PMA squelch, PMA termination, VREF, or signal-detect override masks may leave a lane in a state that higher-level display code cannot infer from normal status alone.
- Fast-flow flags combine many calibration/adaptation shortcuts in dense bitfields. Confusing `FAST_FLAGS` with `FAST_FLAGS_2`, or continuous-calibration bits with one-shot bits, can create timing bugs that only appear on specific links or after power transitions.
- Many registers include broad `RESERVED_*` masks. Any helper that updates a field by composing raw values must preserve reserved bits according to hardware rules; the generated mask names alone do not enforce safe read-modify-write behavior.

## Test Signals

Useful validation combines generated-header consistency checks with hardware behavior:

- Build AMDGPU display support for the ASIC generation that includes DPCS 4.2.2. Missing or renamed macros should fail where generated register, shift, and mask tables are initialized.
- Mechanically verify that every complete field in this range has a matching `__SHIFT` and `_MASK`, allowing the known boundary exceptions for the split `RAWAONLANE0_DIG_RX_ADPT_ATT` at the start and the bare `RAWAONLANEX_DIG_TX_DCC_CONT` comment at the end.
- Cross-check the field groups against `dpcs_4_2_2_offset.h`, especially lane 0 offsets `0x4017` through `0x4051`, lanes 1-3 offsets `0x4100` through `0x4351`, and lane-X offsets `0x7000` through `0x7047`.
- Diff this DPCS 4.2.2 generated output against AMD's source register database and nearby generated variants where lane layouts are expected to match.
- Exercise DisplayPort and HDMI link bring-up across available link rates, lane counts, power states, and PHY lanes. Expected signals are stable link training, adaptation completion, sane DFE/CTLE/VGA readback, no unexpected signal-detect loss, and no stuck calibration state.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence or reinitialization mistakes in adaptation, DCC, signal-detect, MPLL, firmware, and lane-mode fields.
- Use register dumps or PHY debug traces during failing links to confirm the masks decode attenuation, VGA, CTLE, DFE taps, slicer settings, phase adjust, FOM, fast flags, signal-detect status, DCC code words, VREF/calibration codes, and lane-mode fields correctly.
- Validate diagnostic and firmware-assisted paths that touch `FW_*`, `SIGDET_*`, `RX_OVRD_OUT_*`, `TXRX_OVRD_IN`, `LANE_XCVR_MODE_*`, and DCC bank registers, because those are likely to expose mask/shift mistakes without changing higher-level display API behavior.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DPCSSYS_CR2_RAWAONLANE0_DIG_RX_ADPT_ATT` and the earlier lane 0 raw always-on registers, including the AFE, DFE, phase-adjust, MPLL coarse-tune, and power-up fields before line 57192. This chunk covers the rest of lane 0, all of lanes 1-3, and most of the `RAWAONLANEX` template. The next chunk should finish `DPCSSYS_CR2_RAWAONLANEX_DIG_TX_DCC_CONT` and continue with the remaining lane-X raw always-on registers before the later CR2 supervisor/template sections.
