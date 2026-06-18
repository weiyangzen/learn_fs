# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 80957-83452

## Scope

This chunk is a generated AMD DCN 3.2 register shift/mask slice. It contains no executable C logic; it exports preprocessor constants that map hardware register fields to bit positions and masks for the DCN 3.2 display PHY/register-access layer. The requested range has 2,073 `#define` entries grouped under 423 register comments.

The slice starts inside the tail of `C20_PHY_CR0_RAWLANEAON2_DIG_RX_AFE_RTRIM`, then covers the rest of a large `RAWLANEAON2` receiver-calibration/adaptation block, the beginning and most of the analogous `RAWLANEAON3` TX/RX calibration block, and finally enters the per-lane ASIC override/input namespace under `C20_PHY_CR0_LANEX_DIG_ASIC_*`. The last requested line stops inside `C20_PHY_CR0_LANEX_DIG_ASIC_TX_ASIC_IN_0`, so adjacent chunks are required for complete register-family coverage.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this chunk is to provide exact bit-field metadata for DCN 3.2 C20 PHY control/status registers. Runtime AMDGPU display code combines these `__SHIFT` and `_MASK` constants with the corresponding register-offset definitions to read, write, set, or update fields through generated register helper macros.

Major hardware domains represented here are:

- `C20_PHY_CR0_RAWLANEAON2_DIG_RX_*`: receiver analog-front-end, reference/VDAC, DFE, IQ, duty-cycle-correction, adaptation, signal-detect, CDR, PMA override, and RX input/output field definitions for raw lane AON2.
- `C20_PHY_CR0_RAWLANEAON3_DIG_TX_*`: transmitter firmware-state, SRAM recovery, CCA timing, startup/continuous algorithm control, fast flags, high-power protection, lane transceiver-mode override, initial power-up done, TX overrides, MPLLA/MPLLB DCC calibration banks, TX DCC code readback, calibration-bank selection, and TX input fields for raw lane AON3.
- `C20_PHY_CR0_RAWLANEAON3_DIG_RX_*`: the same receiver calibration/adaptation surface as lane AON2, including VDAC offsets, DFE offsets, DCC banks, IQ calibration, adaptive equalization banks, TX EQ direction/polarity thresholds, adaptation controls, CDR detector/recovery timing, and RX overrides.
- `C20_PHY_CR0_LANEX_DIG_ASIC_*`: lane-level ASIC-facing loopback, transceiver-mode, TX override, TX status override, and TX ASIC input fields.

## Important API Surface

There are no functions, structs, enums, variables, local includes, allocation paths, or locks in this chunk. The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

Important macro families include:

- RX calibration offsets: `*_DIG_RX_REF_VDAC_OFST`, `*_REF_EXT_VDAC_OFST`, `*_REF_EE_VDAC_OFST`, `*_REF_EO_VDAC_OFST`, `*_DFE_*_VDAC_OFST`, `*_SETUP_REF_*_IDAC_OFST`, `*_AFE_*_IDAC_OFST`, `*_VDAC_RANGE_SEL`, and `*_AFE_RTRIM`.
- RX DCC and IQ banks: `*_DIG_RX_DCC_CTRL_RANGE_BANK_[0-3]`, `*_DCC_FULL_*_BANK_[0-3]`, `*_DCC_HALF_*_BANK_[0-3]`, `*_IQ_CAL_BANK_[0-3]`, `*_CAL_DONE_BANK_[0-3]`, aggregate `*_DCC_*_CODE`, `*_IQ_CAL`, `*_IQ_CTL_0`, `*_IQ_CTL_1`, and `*_CAL_BANK_SEL`.
- RX adaptation banks: `*_ADPT_ATT_BANK_[0-1]`, `*_ADPT_VGA_BANK_[0-1]`, `*_ADPT_CTLE_BANK_[0-1]`, `*_ADPT_DFE_TAP[1-5]_BANK_[0-1]`, per-slicer tap1 offset valid/data registers, `*_ADPT_IQ_BANK_[0-1]`, `*_ADPT_REF_ERR_BANK_[0-1]`, and `*_ADAPT_DONE_BANK_[0-1]`.
- RX algorithm controls: `*_STARTUP_CAL_ALGO_CTL_*`, `*_STARTUP_ADAPT_ALGO_CTL_0`, `*_CONT_ALGO_CTL`, `*_FAST_FLAGS`, `*_ADPT_CTL_0` through `*_ADPT_CTL_28`, `*_IQ_MARGIN_RANGE`, `*_CDR_DETECTOR_CTL`, and `*_CDR_RECOVERY_TIME`.
- RX external controls and status: `*_RX_OVRD_IN_0`, `*_RX_SIGDET_EN_MASK_CTL`, `*_RX_SIGDET_FILT_CTL`, `*_RX_OVRD_OUT_0`, `*_RX_PMA_OVRD_OUT_0`, `*_RX_IN_0`, and `*_RX_OUT_0`.
- TX control and calibration on AON3: `*_TX_FW_STATES_*`, `*_TX_SRAM_REC_*`, `*_TX_STARTUP_ALGO_CTL_0`, `*_TX_CONT_ALGO_CTL_0`, `*_TX_FAST_FLAGS_0`, `*_TX_MPLLA_DCC_*_BANK_[0-3]`, `*_TX_MPLLB_DCC_*_BANK_[0-3]`, `*_TX_MPLLA_CAL_DONE*`, `*_TX_MPLLB_CAL_DONE*`, `*_TX_CAL_DONE`, `*_TX_DCC_*_CODE`, and `*_TX_CAL_BANK_SEL`.
- Lane ASIC override/input fields: `C20_PHY_CR0_LANEX_DIG_ASIC_LANE_OVRD_IN`, `*_TX_OVRD_IN_0` through `*_TX_OVRD_IN_5`, `*_TX_OVRD_OUT`, `*_LANE_ASIC_IN`, and the start of `*_TX_ASIC_IN_0`.

These macros are normally consumed indirectly through AMD display register helper layers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, field-list macros, and token-pasting helpers that combine register names with field names.

## Control Flow

This header chunk has no local runtime control flow. Runtime sequencing is supplied by the AMDGPU display and DMUB code that includes the DCN 3.2 generated headers:

1. DCN 3.2 resource, IRQ, GPIO, clock-manager, DMUB, and low-level GPU code include `dcn_3_2_0_sh_mask.h` together with matching offset/base headers.
2. Register table macros paste symbolic register and field names into constants such as `C20_PHY_CR0_RAWLANEAON3_DIG_RX_DCC_CTRL_RANGE_BANK_2__FULL_VAL_MASK`.
3. Register helper code uses the masks and shifts to construct read-modify-write operations, status reads, or poll conditions against MMIO-backed display PHY registers.
4. Higher-level display code sequences PHY power-up, link/PLL preparation, lane mode selection, TX/RX calibration, equalization/adaptation, signal detection, and status/interrupt handling.

The macros do not encode ordering requirements. Consumers must still ensure clocks and power domains are available, select the intended lane or bank, avoid changing calibration fields while hardware owns them, and poll completion/status fields where the hardware protocol requires it.

## State And Persistence

The chunk stores no software state and persists nothing on disk. It describes hardware state inside DCN 3.2 PHY and lane-control registers.

The represented hardware state includes:

- RX analog and digital calibration values for reference levels, VDAC/IDAC offsets, AFE trim, DFE phase/data/bypass/error offsets, IQ calibration limits, and DCC full/half-rate values.
- Banked calibration/adaptation state for four DCC/IQ calibration banks and two RX adaptation banks.
- RX adaptation state for attenuation, VGA, CTLE, DFE taps, IQ/ref-error tracking, tap offset validity, adaptation-done flags, startup/continuous skip flags, fast paths, and margin/CDR controls.
- RX/TX PMA and signal-detect state, including low/high-frequency signal detect, filter/mask controls, PMA override outputs, and CDR recovery timing.
- TX firmware, SRAM recovery, clock-calibration algorithm controls, MPLLA/MPLLB DCC calibration banks, calibration done fields, lane mode, HP protection, power-up done, and TX input/override state.
- Lane ASIC-facing loopback, transceiver mode, reset/clock/data-enable/request/power-state/rate/width/PLL-selection controls, equalization cursor overrides, drive/deskew/VREG/DCC update controls, and TX acknowledgement/detect/calibration status fields.

Register persistence is hardware-defined. Configuration fields usually survive until reprogramming, power gating, suspend/resume, modeset/link retraining, or ASIC reset. Completion, status, sticky, self-clearing, and write-one-to-clear fields may have side effects that are not visible from this generated mask header alone.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.2 register database and must match the companion offset header for the same ASIC generation. The masks and shifts are only meaningful when paired with the correct register address macros and SOC15/DCN base-address selection.

Direct include sites for `dcn/dcn_3_2_0_sh_mask.h` in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`

The most relevant integration points are DCN 3.2 link/PHY bring-up, DisplayPort/HDMI lane programming, DMUB register access, IRQ/status handling, GPIO/AUX/DDC translation, clock/power management, and any diagnostic or firmware-assisted path that reads PHY calibration/adaptation status.

The same `C20_PHY_CR0_RAWLANEAON*` names also appear in generated DPCS headers such as `dpcs_4_2_3_sh_mask.h`, indicating that this register namespace is shared or mirrored across generated display PHY metadata. Cross-header consistency matters, but generation-specific differences should not be flattened by hand.

## Risks And Edge Cases

- A wrong shift or mask can compile cleanly while programming the wrong PHY bits. The highest-risk fields here are calibration controls, DCC/IQ bank selection, lane mode, reset, rate/width, PLL selection, TX cursor/equalization, and status/clear fields.
- The chunk boundaries are artificial. The first lines are only the tail of `RAWLANEAON2_DIG_RX_AFE_RTRIM`, and the final lines stop inside `LANEX_DIG_ASIC_TX_ASIC_IN_0`; complete file-level conclusions require neighboring chunks.
- Repeated lane and bank families are copy-sensitive. AON2 versus AON3, banks 0-3, adaptation banks 0-1, MPLLA versus MPLLB, and override versus ASIC-input variants are structurally similar but not interchangeable.
- Calibration and adaptation fields are sequencing-sensitive. Writing skip, fast, bank-select, DCC, IQ, DFE, CTLE, or CDR fields while firmware or hardware calibration is active can cause link-training failures or unstable receive margins.
- Reserved fields are heavily represented. Read-modify-write helpers must preserve reserved bits where required, and generated masks must not encourage callers to write undefined fields.
- Status and override registers mix values with enable bits. Misusing `*_OVRD_VAL` without its matching `*_OVRD_EN`, or clearing/polling status fields with the wrong mask, can create failures that only appear during link retraining, suspend/resume, or specific lane rates.
- The constants are untyped preprocessor macros. Static type checking will not catch a field from the wrong register or generation if token-pasting still produces a defined symbol.

## Test Signals

Useful validation signals for this chunk are:

- Build AMDGPU with DCN 3.2 support enabled; missing or renamed macros should fail in DCN 3.2 resource, IRQ, GPIO, clock-manager, DMUB, or low-level GPU integration code.
- Mechanically verify that each complete field in lines 80957-83452 has both a `__SHIFT` and `_MASK` definition, with exceptions only for the intentionally truncated boundary register blocks.
- Diff the generated macros against AMD's authoritative DCN 3.2 register source and against companion generated headers such as the matching `dcn_3_2_0_offset.h`.
- Run display hardware tests that exercise PHY bring-up and link retraining across supported connectors, rates, lane counts, power states, and suspend/resume paths.
- Validate DisplayPort/HDMI behavior that depends on lane calibration: hotplug, EDID/AUX/DDC, link training, high link rates, audio/video stability, MST if supported, and repeated modesets.
- Watch kernel logs and display diagnostics for AUX timeouts, link-training failures, signal-detect instability, stuck calibration-done bits, CDR recovery failures, underflow, blank screens, or resume-only regressions.
- Where hardware diagnostics permit it, read back DCC/IQ/adaptation/calibration done fields after training and compare against expected firmware or register-database values.

## Chunk Notes

This research covers only the requested line range. The final merged per-file report should reconcile this slice with adjacent chunks before making complete claims about all `C20_PHY_CR0_RAWLANEAON2`, `C20_PHY_CR0_RAWLANEAON3`, or `C20_PHY_CR0_LANEX_DIG_ASIC` register fields.
