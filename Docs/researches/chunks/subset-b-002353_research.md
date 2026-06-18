# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 38154-40593

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for display PHY register fields. It contains no executable C logic; its exported interface is a large set of C preprocessor constants that describe bit positions (`__SHIFT`) and masks (`_MASK`) for DPCS indirect hardware registers.

The requested range contains 2,083 `#define` entries across 2,440 lines and 357 commented register-group markers. It starts at `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_SLICER_CTRL_EVEN` and continues through the rest of CR1 always-on lane 1, then repeats the CR1 always-on lane programming surface for lane 2, lane 3, and the lane-X broadcast/template block. The latter part switches to CR1 supervisor (`SUPX`) digital and analog fields, including ID-code readback, reference-clock overrides, MPLLA/MPLLB override inputs, spread-spectrum and fractional PLL words, charge-pump overrides, ASIC input readback fields, common supervisor control, prescaler control, and bandgap enable. The range ends at the comment for `DPCSSYS_CR1_SUPX_ANA_RTUNE_CTRL`; that register's field definitions are in the next chunk.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The public surface follows the generated AMD register-field convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the hardware register.
- `<REGISTER>__<FIELD>_MASK`: the mask used to isolate, compose, or update that field.

The main macro families in this chunk are:

- CR1 raw always-on lane 1 tail: `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_SLICER_CTRL_EVEN` through `DPCSSYS_CR1_RAWAONLANE1_DIG_TX_DCC_CONFIG` define slicer controls, common MPLL/RCAL calibration status, adaptation control words, MPLL disable bits, fast calibration/adaptation flags, TX/RX disable overrides, LOS mask timing, signal-detect filtering, RX override outputs, signal-detect thresholds/codes, VREF/calibration codes, RX and TX DCC calibration/bank controls, MPLL bandgap control, signal-detect output override/readback, firmware mode/adaptation/calibration configuration, lane transceiver-mode override/readback, and RX signal-detect/TX DCC configuration.
- CR1 raw always-on lanes 2, 3, and X: `DPCSSYS_CR1_RAWAONLANE2_*`, `DPCSSYS_CR1_RAWAONLANE3_*`, and `DPCSSYS_CR1_RAWAONLANEX_*` repeat the full always-on lane pattern starting at AFE ATT/CTLE offset fields and covering RX adaptation IQ/FOM, DFE data/error/bypass/phase/ref-level offsets, RX phase adjust, MPLLA/MPLLB coarse tune, initial power-up done, ATT/VGA/CTLE/DFE tap adaptation values, adaptation-done bits, fast flags, slicer control, common calibration status, adaptation-control words, TX/RX overrides, LOS/signal-detect controls, calibration codes, DCC controls, firmware config, and transceiver-mode fields. The `LANEX` names usually serve register-table or broadcast/template paths rather than naming a single physical lane.
- CR1 supervisor digital identification and clock overrides: `DPCSSYS_CR1_SUPX_DIG_IDCODE_LO`, `IDCODE_HI`, `REFCLK_OVRD_IN`, `MPLLA_DIV_CLK_OVRD_IN`, `MPLLA_HDMI_CLK_OVRD_IN`, `MPLLB_DIV_CLK_OVRD_IN`, and `MPLLB_HDMI_CLK_OVRD_IN` expose ID-code readback, reference-clock source/enable/test override fields, and divider/HDMI clock override controls for MPLLA and MPLLB.
- CR1 MPLLA/MPLLB override programming: `DPCSSYS_CR1_SUPX_DIG_MPLLA_OVRD_IN_*`, `MPLLB_OVRD_IN_*`, `MPLLA_SSC_*`, `MPLLB_SSC_*`, `MPLLA_CP_OVRD_IN`, `MPLLB_CP_OVRD_IN`, and the gain-scheduled CP override registers define PLL enable, dividers, VCO range, standby, calibration force, fractional-N enable/update, SSC enable/up-spread/PMIX/word-div2/clock-sync controls, SSC peak and step-size split words, fractional numerator/remainder/denominator split words, and charge-pump proportional/integral override values and enables.
- CR1 supervisor control and readback: `DPCSSYS_CR1_SUPX_DIG_SUP_OVRD_IN`, `PRESCALER_OVRD_IN`, `SUP_OVRD_OUT`, `LVL_OVRD_IN`, `DEBUG`, `*_ASIC_IN_*`, `*_DIV_CLK_ASIC_IN`, `*_HDMI_CLK_ASIC_IN`, `ASIC_IN`, `LVL_ASIC_IN`, `BANDGAP_ASIC_IN`, `*_CP_ASIC_IN`, and `*_CP_GS_ASIC_IN` define supervisor reset/reference/RTUNE/test override fields, prescaler override fields, calibration and PLL lock readback, level/voltage controls, PLL ASIC input mirrors, divider/HDMI clock ASIC input mirrors, common PHY reset/reference/RTUNE state, VREF/vboost selections, bandgap enable, and charge-pump ASIC input mirrors.
- CR1 supervisor analog prescaler: `DPCSSYS_CR1_SUPX_ANA_PRESCALER_CTRL` defines analog prescaler ATB selection, VREG measurement, fast-start override, VREG boost, and hysteresis reference fields. The next marker, `DPCSSYS_CR1_SUPX_ANA_RTUNE_CTRL`, is present only as a comment at line 40593 in this chunk.

Most fields use 16-bit masks with an `L` suffix, matching the narrow DPCS indirect register fields used by these raw lane, always-on lane, supervisor, MPLL, and analog control blocks.

## Control Flow

This header has no runtime control flow. It participates in compile-time register metadata construction:

1. AMD display code for the matching DCN/DPCS generation includes the DPCS 4.2.2 offset header and this shift/mask header.
2. Version-specific register, shift, and mask tables token-paste or name these constants for hardware helper code.
3. Runtime display code uses register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` with those tables to program or read DPCS PHY state.
4. Real sequencing for link bring-up, RX adaptation, signal detection, DCC calibration, MPLL programming, reference-clock selection, RTUNE, power state transitions, diagnostics, and suspend/resume lives outside this generated header.

The macros describe only bit layout. They do not encode reset values, read-only/write-only status, write-one-to-clear behavior, self-clearing behavior, clock-domain constraints, power-domain validity, programming order, or timeout requirements.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR1 always-on lane and CR1 supervisor DPCS registers:

- Lane RX adaptation state includes AFE ATT/CTLE offsets, IQ adaptation, FOM, DFE phase/data/error/bypass offsets, DFE tap values, ATT/VGA/CTLE adaptation results, even/odd slicer controls, phase-adjust values, adaptation-done bits, fast adaptation/calibration flags, and free-form adaptation-control words.
- Lane calibration and signal-detect state includes common MPLL/RCAL init/done bits, RX LOS mask count, signal-detect filter controls, squelch/stat outputs, RX signal-detect thresholds and codes, VREF generator enable, IOFF/ICONST/VREFGEN calibration codes, RX DCC I/Q calibration code words, TX DCC bank address/data/continuous control, and signal-detect output override/readback.
- Lane override state includes RX/TX disable override values/enables, RX PMA squelch/VREF/termination/signal-detect override outputs, MPLLA/MPLLB disable/coarse-tune controls, MPLL bandgap control, lane transceiver-mode override/readback, firmware mode/adaptation/calibration configuration, RX signal-detect configuration, and TX DCC configuration.
- Supervisor and PLL state includes ID-code readback, reference-clock override, MPLLA/MPLLB divider and HDMI clock overrides, PLL enable/standby/divider/VCO/calibration/fractional-N controls, SSC peak and step-size values, fractional numerator/remainder/denominator words, clock-sync controls, charge-pump proportional/integral overrides, gain-scheduled charge-pump overrides, PLL lock readback, calibration outputs, PHY reset/reference/RTUNE state, level controls, bandgap enable, and analog prescaler controls.

Persistence is hardware-defined. Configuration fields normally remain until modeset/link reprogramming, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization changes them. Status, done, lock, calibration, and readback fields may be latched, sampled, self-clearing, or valid only while the corresponding lane, supervisor, reference-clock, and PLL power domains are active. This generated header does not define those semantics.

## Dependencies And Integration Points

This generated shift/mask file must stay synchronized with AMD's DPCS 4.2.2 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies matching `ixDPCSSYS_*` offsets. In that file, CR1 always-on lane 1 begins at offsets such as `0x4100` and this chunk starts at `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_SLICER_CTRL_EVEN` at `0x4121`; lane 2 starts at `0x4200`, lane 3 at `0x4300`, and lane X at `0x7000`.
- The same offset header maps CR1 supervisor/SUPX registers from `DPCSSYS_CR1_SUPX_DIG_IDCODE_LO` at `0x8000` through the MPLLA/MPLLB override, ASIC input, common supervisor, and analog prescaler region. For example, `DPCSSYS_CR1_SUPX_DIG_MPLLA_OVRD_IN_0` is at `0x8007`, `DPCSSYS_CR1_SUPX_DIG_MPLLA_ASIC_IN_0` is at `0x8024`, and `DPCSSYS_CR1_SUPX_ANA_RTUNE_CTRL` follows the chunk boundary at `0x8041`.
- AMD display DCN/DPCS resource code consumes these constants indirectly through generated register, shift, and mask tables rather than by open-coding bit values.
- Link encoder, PHY bring-up, DisplayPort/HDMI link training, clock programming, diagnostics, hotplug recovery, suspend/resume, and GPU reset code may interact with the hardware fields described here via the register helpers.
- Firmware and hardware state machines also share this register surface, especially for RX adaptation, signal detection, DCC calibration, MPLL calibration/lock, SSC/fractional PLL programming, RTUNE handshakes, power state entry/exit, and analog prescaler/bandgap controls.

Behaviorally, this range is below the user-facing display stack. It is the bit-layout contract used when the driver and firmware configure CR1 lanes and common supervisor/PLL resources for display PHY operation.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while causing the driver to update the wrong field, corrupt reserved bits, or decode hardware status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware expectations, and silicon documentation.
- Chunk boundaries are artificial. The previous chunk contains earlier lane 1 adaptation and DFE tap groups; this chunk starts at the first field of `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_SLICER_CTRL_EVEN`. This chunk ends with only the `DPCSSYS_CR1_SUPX_ANA_RTUNE_CTRL` marker; all RTUNE field definitions follow in the next chunk.
- The lane 2, lane 3, and lane-X blocks are highly repetitive. Generator or merge mistakes can affect only one lane, one broadcast/template name, or one duplicated A/B PLL side while nearby fields look correct by inspection.
- RX adaptation and signal-detect fields are sequencing-sensitive. Wrong masks around DFE taps, slicers, VDAC/IDAC offsets, adaptation-done bits, signal-detect thresholds, LOS masking, or RX DCC codes can lead to link-training failures, marginal equalization, false loss-of-signal, or misleading debug traces.
- Override registers bypass normal hardware state-machine choices. Misprogramming TX/RX disable, PMA squelch/termination/VREF/signal-detect, MPLL disable/coarse tune, firmware config, or transceiver-mode fields can leave a lane in a state that higher-level display code cannot easily diagnose.
- MPLLA/MPLLB and reference-clock fields affect shared clocking. Bad masks for PLL enable, dividers, HDMI dividers, VCO selection, fractional-N words, SSC controls, charge-pump overrides, clock-sync, standby, or calibration force can cause unstable clocks, black screens, retraining loops, audio/video timing problems, or mode-specific regressions.
- Status/readback and configuration fields are interleaved across similarly named `OVRD_IN`, `ASIC_IN`, and `OVRD_OUT` groups. Confusing these groups can make code write to readback-style fields or read stale override configuration instead of live hardware state.
- Reserved-bit masks are present throughout the generated header. Register update helpers must avoid relying on reserved fields as meaningful state, and hand-written values must preserve hardware-required reserved behavior.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.2. Missing, renamed, or malformed macros should fail where generated register, shift, and mask tables are initialized.
- Mechanically verify that every complete field in this range has the expected `__SHIFT` and `_MASK` pair, while treating the final `DPCSSYS_CR1_SUPX_ANA_RTUNE_CTRL` marker as a next-chunk boundary rather than a missing definition.
- Cross-check every complete register group in this chunk against `dpcs_4_2_2_offset.h`, especially the CR1 lane offsets (`0x4100`, `0x4200`, `0x4300`, `0x7000`) and CR1 supervisor offsets (`0x8000+`).
- Diff against AMD's source register database and nearby generated variants such as other DPCS 4.2.x shift/mask headers where hardware layout is expected to remain compatible.
- Exercise DisplayPort and HDMI link bring-up across supported rates, lane counts, PHY lanes, and power states. Expected signals are stable link training, correct RX adaptation completion, valid signal-detect behavior, correct MPLL selection/lock, and no stuck calibration status.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence or reinitialization mistakes in lane adaptation, signal-detect, DCC calibration, transceiver-mode, reference-clock, and MPLL fields.
- Validate clock-sensitive modes that stress MPLLA/MPLLB dividers, HDMI dividers, SSC, fractional PLL programming, charge pump settings, reference-clock source selection, and clock-sync controls. Watch for black screens, PHY lock failures, retraining loops, display corruption, or timing instability.
- Use register dumps or PHY debug traces during failing links to confirm DFE tap values, RX FOM/IQ, slicer settings, signal-detect thresholds/codes, DCC calibration words, transceiver-mode fields, PLL override inputs, ASIC input readbacks, lock status, and analog prescaler fields decode correctly.

## Cross-Chunk Notes

The previous chunk owns earlier CR1 raw always-on lane 1 adaptation fields through `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_ADPT_DFE_TAP5`. This chunk starts with `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_SLICER_CTRL_EVEN`, completes the rest of lane 1, covers complete lane 2, lane 3, lane-X, and most CR1 SUPX digital/supervisor/PLL readback groups, then stops at the `DPCSSYS_CR1_SUPX_ANA_RTUNE_CTRL` comment. The next chunk should provide the RTUNE field definitions and continue the CR1 SUPX analog register sequence. The final per-file research document should reconcile these boundaries before making whole-file claims about all DPCS 4.2.2 register groups.
