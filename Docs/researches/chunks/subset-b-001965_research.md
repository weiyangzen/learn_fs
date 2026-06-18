# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 88288-90769

## Purpose

This chunk is a generated AMD DCN 3.2.0 register shift/mask slice. It contains C preprocessor register-field metadata only: `__SHIFT` macros for field low-bit positions, `_MASK` macros for raw field masks, generated `//<REGISTER>` comments, and `// addressBlock:` comments. There are no executable functions, structs, enums, data allocations, branches, locks, persistence code, or direct MMIO reads/writes in this range.

The range starts in the tail of `C20_PHY_CR0_RAWLANEAONX_DIG_RX_STARTUP_CAL_ALGO_CTL_0`, where only the final mask definitions are visible, then covers a large C20 PHY CR0 RX-lane analog/digital calibration and adaptation register block. It continues into repeated lane0/lane1 PIPE LPC/VDR message-bus fields and then enters the C20 PHY CR1 supervisor digital block, including reference clock overrides, MPLLA/MPLLB override and ASIC input fields, RTUNE controls/status, clock/reset power-up timing, and the beginning of MPLLA power-control and SSC fields. The chunk ends on the `C20_PHY_CR1_SUP_DIG_MPLLA_SSC_SSC_RAMP` register comment without that register's field definitions, so adjacent chunks are required for complete file-level coverage.

Although the source path is under a local `ceph-client` tree, this file is AMDGPU Display Core hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the starting bit for a field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register mask for that field.
- `//<REGISTER>` comments group the following shift and mask macros by hardware register.
- `// addressBlock: <name>` comments identify the hardware address block for subsequent register groups.

This slice defines 2,094 `#define` lines: 1,042 shift macros and 1,052 mask macros. The extra masks come from the chunk starting after the shift definitions for `C20_PHY_CR0_RAWLANEAONX_DIG_RX_STARTUP_CAL_ALGO_CTL_0`.

Major macro families in this chunk are:

- `C20_PHY_CR0_RAWLANEAONX_DIG_RX_*`: RX startup calibration skip controls, startup adaptation skip controls, continuous calibration/adaptation skip controls, fast flags, VGEN/signal-detect/AFE/reference/DFE offset fields, IQ calibration fields, four banks of DCC/IQ calibration and done fields, calibration bank selection, live calibration code fields, adaptation result banks, DFE tap offsets and validity, adaptation control words, RX margin/CDR detector controls, RX override/input/output fields, and signal-detect filters.
- `C20_PHY_LANE0_PIPE0_UPCSLANE_PIPE_LPC_PHY_*` and `C20_PHY_LANE1_PIPE0_UPCSLANE_PIPE_LPC_PHY_*`: two repeated PIPE lane address blocks. Each lane has RX margin controls, elastic-buffer controls, RX/TX/HDP TX controls, common control, C20 VDR read/write address/data windows, custom SERDES/HDMI rate and width fields, LFPS control, VDR TX override fields, HDP VDR override fields, recalibration bank/force/skip controls, deskew enable, and recalibration override fields.
- `C20_PHY_CR1_SUP_DIG_IDCODE_*` and `C20_PHY_CR1_SUP_DIG_REFCLK_*`: supervisor ID-code and reference-clock override fields, including clock enable/divider/source/range, bandgap enable, short-lock override, nominal voltage select, clock-detect enable, and alternate low-power clock select.
- `C20_PHY_CR1_SUP_DIG_MPLLA_*` and `C20_PHY_CR1_SUP_DIG_MPLLB_*`: PLL clock-divider override fields, HDMI mode/divider controls, MPLLA/MPLLB enable and multiplier fields, bandwidth threshold fields, SSC override and ASIC input fields, MPLLB VCO/calibration override and ASIC fields, and early MPLLA power-control fields.
- `C20_PHY_CR1_SUP_DIG_SUP_*`, `ASIC_*`, `LVL_*`, `TXUP_*`, and `TXDN_*`: supervisor override inputs/outputs, lane/debug/status style fields, level ASIC inputs, and TX termination offset inputs.
- `C20_PHY_CR1_SUP_DIG_RTUNE_*`: RTUNE calibration enables, analog termination control, RTUNE state/status, RX/TX set values, RX/TX status values, TX termination code averages/up-down values, and fast RTUNE flags.
- `C20_PHY_CR1_SUP_DIG_CLK_RST_*`: bandgap/reference power-up timing and state-status fields.
- `C20_PHY_CR1_SUP_DIG_MPLLA_MPLL_PWR_CTL_*`: MPLLA calibration control, power-control status, VCO/PCLK/analog/feedback-clock timing, tune values, skip-cal tune values, coarse-tune FSM limits, short/long gearshift timing, output delay timing, and late calibration override enables.

Representative field names show the intended hardware role: `SKIP_RX_*_CAL_STARTUP`, `FAST_RX_*`, `*_VDAC_OFST`, `RX_DCC_*_BANK_*`, `RX_ADPT_*_BANK_*`, `RX_OVRD_*`, `START_MARGIN`, `C20_VDR_*`, `RECAL_*`, `REF_CLK_*`, `MPLLA_*`, `MPLLB_*`, `SSC_*`, `RTUNE_*`, `BG_*`, `FSM_STATE`, `MPLL_CAL_RDY`, `MPLL_OUTPUT_EN`, and `VCO_*_TIME`.

## Control Flow

There is no runtime control flow in this header. Runtime behavior is indirect:

1. DCN 3.2.0 code includes this mask/shift header with the matching register offset header.
2. Register-list tables and helper macros compose symbolic register names with field names, for example through helper families such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `FD`, and `FN`.
3. The generated shift and mask values are passed to MMIO helper code that performs masked writes or field extraction.
4. The hardware, not this header, defines the actual sequencing and side effects of calibration, adaptation, margining, VDR access, RTUNE, PLL, SSC, clock/reset, and status fields.

The macros do not encode ordering constraints. Consumers must still sequence PHY clock/reference setup, bandgap/reference power-up, MPLL enable/calibration, lane enable, VDR programming, RX/TX overrides, calibration/adaptation bank selection, margining, RTUNE calibration, and status polling according to the DCN32 PHY programming model.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes MMIO-backed hardware state:

- RX-lane calibration and adaptation state, including skip flags, fast-mode flags, calibrated analog offsets, DCC/IQ calibration codes, DFE tap offsets, adaptation result banks, signal-detect filters, CDR detector controls, and live RX input/output status.
- PIPE lane state for margining, elastic buffers, RX/TX/HDP TX control, VDR indirect access data/address registers, custom link rates, HDMI rate, LFPS, TX swing/pre/main/post overrides, recalibration controls, and deskew enablement.
- Supervisor PHY state for ID values, reference clock source/range/enable, bandgap enablement, PLL divider/multiplier/SSC/HDMI settings, PLL override versus ASIC input selection, RTUNE calibration and result fields, clock/reset power-up timers, and MPLLA power-control status.

Persistence is hardware-defined. Configuration fields can persist until modeset reprogramming, link disable, power gating, suspend/resume, or ASIC reset. Status and control fields such as `*_DONE`, `*_RDY`, `*_STATE`, `*_OVRD_EN`, `*_CAL_EN`, `*_RETRIGGER`, `START_MARGIN`, VDR access windows, and recalibration force/skip controls may be read-only, write-one-to-clear, self-clearing, sticky, or latched depending on the actual register specification. This header exposes only numeric bit positions and masks; it does not encode access type, reset value, volatility, or side-effect semantics.

## Dependencies And Integration Points

This header must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`, which supplies the corresponding register offsets and base-index constants. A mismatch between offset and mask/shift headers can compile cleanly while targeting the wrong MMIO field.

Direct include sites for `dcn_3_2_0_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`

Functional integration points are PHY and display-link programming paths rather than ordinary C call sites:

- DCN32 resource and hardware translation/factory code, which assembles generated offsets, masks, and shifts into per-block register tables.
- DMUB and display register helper code, where field macros are used through generated mask/shift tables and helper macros such as `FD(reg_field)` and `FN(reg_name, field)`.
- Link/PHY bring-up and modeset paths that configure C20 PHY CR0/CR1 fields for reference clocks, PLLs, RX/TX enablement, lane margining, recalibration, deskew, and calibration/adaptation behavior.
- Diagnostic, debug, and recovery paths that read status fields such as RTUNE results, bandgap/reference FSM state, MPLL state/readiness, signal-detect output, calibration done bits, adaptation done bits, and VDR readback fields.
- Cross-family generated register headers. The same C20 PHY field names also appear in related generated headers such as `dpcs_4_2_3_sh_mask.h`, so generator consistency matters across DCN/DPCS views of the same underlying PHY blocks.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong mask or shift can build successfully while silently corrupting PHY programming, PLL setup, calibration/adaptation behavior, margining, or status decoding.
- This chunk is partial at both boundaries. It starts after the shift macros for `C20_PHY_CR0_RAWLANEAONX_DIG_RX_STARTUP_CAL_ALGO_CTL_0` and ends before field definitions for `C20_PHY_CR1_SUP_DIG_MPLLA_SSC_SSC_RAMP`.
- Many fields have override-enable pairs, usually `<signal>` plus `<signal>_OVRD_EN`. Setting a value without the corresponding override enable, or leaving an override enable asserted after diagnostics, can create behavior that looks like a link-training or PHY calibration failure.
- The RX calibration/adaptation registers are banked and repeated. Confusing bank 0 through bank 3, or writing the live code fields instead of banked fields, can preserve stale calibration state or target the wrong adaptation result.
- Margining and destructive margining fields can intentionally degrade or stress the link. Bad field definitions or misuse can cause transient error bursts, training failure, or display blanking.
- VDR indirect address/data fields require access sequencing that this header does not describe. Incorrect ordering can read stale values or write the wrong internal PHY address.
- MPLLA/MPLLB, reference-clock, SSC, bandgap, and clock/reset timing fields are power/timing sensitive. Incorrect field widths can produce intermittent failures that depend on link rate, clock source, resume timing, or silicon stepping.
- RTUNE set/status fields mix calibration controls and results. Mis-decoding can make termination calibration appear valid when it is not, or cause recovery code to chase the wrong failure signal.
- Reserved masks are present throughout the range. Consumers should preserve reserved bits during masked updates unless the hardware programming guide explicitly requires otherwise.

## Test Signals

Useful validation for changes touching this chunk includes:

- Build AMDGPU/DCN32 display code with warnings treated seriously. Missing or renamed generated symbols should surface in DCN32 resource, DMUB, IRQ, clock, GPIO, and PHY/link users.
- Mechanically compare this line range against the authoritative AMD DCN 3.2.0 register database or a regenerated `dcn_3_2_0_sh_mask.h`. Every complete field in the chunk should have the expected paired shift and mask; the known exceptions are the chunk-boundary tail/head cases.
- Cross-check the companion `dcn_3_2_0_offset.h` so register names and field names align with the same generated address blocks.
- Exercise DCN32 hardware link bring-up across DP and HDMI modes, including cold boot, hotplug, suspend/resume, link-rate changes, and modesets that force PLL and PHY recalibration.
- Use register dumps around PHY bring-up and recovery. Masked writes should modify only intended bits, override-enable pairs should be asserted only when expected, and status fields such as calibration done, adaptation done, signal-detect output, MPLL ready, RTUNE state, and bandgap/reference FSM state should decode consistently.
- Exercise link margining and VDR access paths if available in diagnostics. Margin start/reset/status fields, VDR read/write address/data windows, recalibration force/skip fields, and deskew enable fields should behave consistently for lane0 and lane1.
- Watch for symptoms tied to this slice: intermittent link training failure, blank display after resume, wrong HDMI/DP rate selection, PLL lock/readiness timeout, unstable signal detect, calibration/adaptation timeout, unexpected RTUNE values, or failures that reproduce only under high link rates.

## Cross-Chunk Notes

The final per-file report should merge this research with the previous chunk for the beginning of `C20_PHY_CR0_RAWLANEAONX_DIG_RX_STARTUP_CAL_ALGO_CTL_0` and the following chunk for the `C20_PHY_CR1_SUP_DIG_MPLLA_SSC_SSC_RAMP` definitions and later CR1 PHY fields. This document should be treated as the worker-produced research artifact for lines 88288-90769 only.
