# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 117636-120106

## Purpose

This chunk is a generated AMD DCN 4.1.0 shift/mask header section for DPCS/DPCSSYS PHY-side display link registers. It defines C preprocessor constants for bit positions and masks, not executable code. The covered range describes the tail of the `DPCSSYS_CR2_RAWLANE3` interrupt-mask register, the rest of raw lane 3 IRQ/PMA/PCS/ATE/CTL field layouts, and almost all repeated `DPCSSYS_CR2_RAWAONLANE0` through `DPCSSYS_CR2_RAWAONLANE3` always-on lane calibration and adaptation fields.

The range contains 2,471 source lines, 2,113 `#define` lines, and 358 register-comment markers. It starts mid-register at `DPCSSYS_CR2_RAWLANE3_DIG_IRQ_CTL_IRQ_MASK__RX_ADAPT_REQ_IRQ_MSK_MASK` and ends at the comment for `DPCSSYS_CR2_RAWAONLANE3_DIG_CAL_IOFF_CODE`, before that register's field macros. Boundary fields for the first and last registers are therefore in neighboring chunks; consumers must include the whole generated header.

## Important macros and field groups

- `DPCSSYS_CR2_RAWLANE3_DIG_IRQ_CTL_*` exposes interrupt mask, status, and clear fields for raw lane 3 on controller/routing slice CR2. The chunk includes masks for RX adaptation request/disable, RX reset, lane transceiver-mode change, RX phase-2 calibration request/disable, RX-to-TX serial loopback, DCC on-demand, and a second mask register for TX reset/request. It also defines one-bit status and clear registers for lane transceiver mode, RX phase-2 calibration, RX-to-TX loopback, DCC on-demand, TX reset, and TX request.
- `DPCSSYS_CR2_RAWLANE3_DIG_PMA_XF_*` describes the PMA crossbar/control interface for raw lane 3. The fields cover lane MPLLA/MPLLB enable overrides, supervisor state overrides, TX and RX request/reset/data-enable overrides, beacon/asynchronous drive controls, serial and parallel loopback enables, RTUNE request/ack, MPHY state overrides, RX adaptation acknowledge/data/FOM paths, and PMA input status bits.
- `DPCSSYS_CR2_RAWLANE3_DIG_TX_CTL_*` and `DPCSSYS_CR2_RAWLANE3_DIG_RX_CTL_*` define lane-local TX/RX control and status fields. These include TX FSM state, TX run flag, TX clock enable, TX DCC continuous calibration status, RX FSM state, RX loss-of-signal mask count, RX data-enable override, OFFCAN and RX adaptation continuous status flags, and OCLA/UPCS observation fields.
- `DPCSSYS_CR2_RAWLANE3_DIG_PCS_XF_ATE_*` provides test and ATE override fields crossing between PCS and the lane analog/PHY side. These fields include RX and TX ATE override values/enables for calibration, data, terminations, signal-detect, VREF, DCC, TX equalization, MPHY control, PMA data-enable, and master MPLL loopback selection.
- `DPCSSYS_CR2_RAWAONLANE[0-3]_DIG_*` repeats the always-on lane register layout four times for lanes 0 through 3. Each lane instance has the same generated shape, with instance-specific macro prefixes.
- AON lane adaptation/readback fields include `AFE_ATT_IDAC_OFST`, `AFE_CTLE_IDAC_OFST`, `RX_ADPT_IQ`, `RX_ADAPT_FOM`, DFE summer/phase/data/bypass/error offsets, DFE even/odd reference levels, RX phase-adjust linear/map values, RX IQ phase adjust, RX adaptation ATT/VGA/CTLE/DFE tap fields, and `RX_ADAPT_DONE`.
- AON lane calibration and fast-mode fields include `INIT_PWRUP_DONE`, `FAST_FLAGS`, `FAST_FLAGS_2`, `LANE_CMNCAL_MPLL_STATUS`, `LANE_CMNCAL_RCAL_STATUS`, `MPLL_DISABLE`, `MPLLA_COARSE_TUNE`, `MPLLB_COARSE_TUNE`, `ADPT_CTL_0` through `ADPT_CTL_7`, TX DCC bank address/data/control fields, RX DCC calibration ICM/IDF/QCM/QDF code registers, and VREF/IOFF/ICONST calibration code fields.
- AON lane signal-detect and RX analog overrides include `RX_LOS_MASK_CTL`, `RX_SIGDET_FILT_CTRL`, `STATS`, `RX_OVRD_OUT_1`, `RX_OVRD_OUT_2`, `RX_OVRD_OUT_3`, `RX_SIGDET_CAL`, `RX_SIGDET_HF_CODE`, `RX_SIGDET_LF_CODE`, `RX_VREFGEN_EN`, `SIGDET_OUT_OVRD`, `SIGDET_OUT_IN`, and `RX_SIGDET_CONFIG`.
- AON lane firmware/configuration and TX/RX control fields include `FW_MM_CONFIG`, `FW_ADPT_CONFIG`, `FW_CALIB_CONFIG`, `LANE_XCVR_MODE_OVRD_IN`, `LANE_XCVR_MODE_IN`, `TX_DCC_CONFIG`, `TX_RX_DCC`, and `TX_RX_DCC_BYP_AC_CAP_IN`.

There are no functions, structs, enums, or callable APIs in this chunk. Its public interface is the generated macro naming contract: `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`. Those macros are intended to be paired with generated register-address macros from DPCS offset headers and consumed through AMD display register helper macros such as field mask/shift table builders and MMIO read/modify/write helpers.

## Control flow and usage model

This header has no runtime control flow. At runtime, AMDGPU display code includes generated offset and shift/mask headers, selects a register address, combines a field value with the matching shift and mask, and performs an MMIO register read/modify/write or readback. A typical flow is:

1. DCN 4.0.1 display, IRQ, GPIO, clock, or DMUB code includes `dcn/dcn_4_1_0_sh_mask.h` along with the relevant generated offset headers.
2. Register-list macros or direct helper invocations refer to `REG__FIELD_MASK` and `REG__FIELD__SHIFT` symbols.
3. The hardware programming path targets a DPCS raw lane or always-on lane register for CR2 and lane instance 0 through 3.
4. The caller preserves unrelated bits with a field-aware helper, writes override/configuration fields, polls status/done/ack fields, or clears interrupt/status bits through the corresponding clear register.
5. Hardware state changes as link training, lane calibration, power sequencing, signal-detect, TX/RX enable, or test/diagnostic paths progress.

The raw lane 3 fields are event and control oriented: interrupt masks gate lane events, status registers report one-bit events, clear registers acknowledge sticky events, and PMA/PCS override fields can force low-level link behavior. The AON lane groups are more calibration oriented: they expose adaptation measurements, calibration codes, fine-grained analog override values, and status bits for initialization, RCAL/MPLL calibration, signal detect, DCC calibration, and VREF behavior.

## State and persistence behavior

The macros themselves are compile-time constants and have no software state. The state they describe lives in memory-mapped display PHY/DPCS registers. Values can persist until changed by display link programming, link retraining, hotplug handling, display power gating, suspend/resume restore, DMCUB/DMUB firmware action, or GPU/display IP reset.

Several fields describe sticky or latched state rather than simple configuration. IRQ status and clear registers must be treated as event registers. `*_DONE`, `*_ACK`, `*_INIT`, `*_STATUS`, `*_OUT`, and adaptation/FOM fields are hardware-produced observations. Override registers usually pair an override value bit with an override-enable bit; leaving an enable asserted can force hardware away from its normal lane-training or calibration state. Calibration code registers, DCC banks, adaptation controls, and signal-detect tuning fields affect physical-link behavior and should be assumed hardware/firmware-sensitive.

The repeated `RAWAONLANE0` through `RAWAONLANE3` layout means state is per physical lane. Programming lane 0 does not configure lane 1 through 3, and cross-lane consistency matters for DisplayPort link width changes, lane remapping, training retries, USB-C/DP alt-mode routing, or PHY diagnostics.

## Dependencies and integration points

- The chunk belongs to `include/asic_reg/dcn/dcn_4_1_0_sh_mask.h`, a generated header included by DCN 4.0.1 display code such as `display/dc/resource/dcn401/dcn401_resource.c`, `display/dc/irq/dcn401/irq_service_dcn401.c`, `display/dc/gpio/dcn401/hw_translate_dcn401.c`, `display/dc/gpio/dcn401/hw_factory_dcn401.c`, `display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c`, and `display/dmub/src/dmub_dcn401.c`.
- Register addresses for the DPCS-style `DPCSSYS_CR2_*` names are represented in DPCS offset headers, for example `include/asic_reg/dpcs/dpcs_4_2_0_offset.h`, `dpcs_4_2_2_offset.h`, and `dpcs_4_2_3_offset.h`. In those maps, raw lane 3 IRQ mask and PMA registers live around `0x334d` through `0x336c`, and AON lane registers start around `0x4000` with per-lane blocks through the lane 3 signal-detect/calibration region.
- The generated masks integrate with AMD DC register helper conventions such as `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `REG_GET`, `REG_SET`, and register-table construction macros. `dmub_dcn401.c` demonstrates the field-table pattern by building mask and shift arrays from `DMUB_DCN401_FIELDS()`, although this specific raw-lane group is not directly named there.
- The field groups are part of the display PHY/DPCS layer rather than high-level CRTC, plane, or connector policy. They connect modeset/link-training code, firmware-mediated PHY control, interrupt handling, hotplug/link-loss diagnostics, and low-level manufacturing/test hooks to the actual register layout.
- Similar layouts appear in nearby generated DPCS/DCN mask headers for other ASIC versions. That repetition is important for detecting generated-register drift and for carrying PHY fixes across DCN/DPCS versions.

## Risks and edge cases

- Boundary incompleteness: the chunk begins after some `DPCSSYS_CR2_RAWLANE3_DIG_IRQ_CTL_IRQ_MASK` shift and mask fields and ends before the `RAWAONLANE3_DIG_CAL_IOFF_CODE` fields. Treating this range as a complete standalone catalog would miss boundary fields.
- Offset/mask mismatch: the macros only encode field bit positions. Using CR2 masks with a CR0/CR1/CR3 register address, or a lane 3 mask with a lane 0 address, can silently program the wrong PHY slice or lane.
- Reserved-bit corruption: many registers are 16-bit style field maps with large `RESERVED_*` masks. Full-register writes or ad hoc bit twiddling can corrupt reserved or write-sensitive fields. Callers should use mask-preserving helpers.
- Event-clear semantics: `*_IRQ_CLR`, `*_ACK`, and similar one-bit clear/status fields should not be handled like persistent configuration bits. Incorrect clearing can lose diagnostic information or leave interrupts asserted.
- Override enable hazards: PMA, PCS, RX, TX, signal-detect, and lane-mode override fields generally use value-plus-enable pairs. Setting a value without the intended enable does nothing; leaving an enable set can force TX/RX reset, disable PMA data, change termination/signal-detect behavior, or hold calibration out of automatic control.
- Link-training and calibration sensitivity: adaptation, DFE tap, DCC, MPLL, RCAL, VREF, signal-detect, and phase-adjust fields affect physical link margins. Incorrect values may only fail on certain link rates, cable quality, sink combinations, lane counts, or after warm resume.
- Per-lane consistency: the AON lane layout repeats four times. Bugs that update only one lane, use the wrong lane prefix, or mix readbacks across lanes can cause asymmetric failures that look like marginal hardware.
- Generated-header drift: this section is generated and should remain synchronized with offset headers and hardware specs. Manual edits or stale generated artifacts can compile cleanly while pointing field helpers at wrong bit positions.

## Test signals

- Build coverage for DCN 4.0.1/4.1.0 AMDGPU display code with generated headers enabled. Missing or renamed field macros should fail compilation in resource, IRQ, GPIO, clock, DMUB, or any lane/DPCS code that consumes these definitions.
- Header consistency checks comparing `DPCSSYS_CR2_RAWAONLANE0` through `RAWAONLANE3` field layouts. The repeated lane blocks should have matching field names, shifts, and masks except for their lane-number prefixes and chunk boundary truncation.
- Offset/mask reconciliation that verifies each complete `REGISTER__FIELD` group in this chunk has a matching DPCS offset macro in the relevant `dpcs_*_offset.h` file for the same ASIC/register family.
- Static checks for reserved-bit-safe register writes in any future call sites that use these fields. Writes should route through generated mask/shift helpers rather than open-coded constants.
- Runtime link tests on supported hardware across DP link rates and lane counts, including hotplug, link loss/retraining, suspend/resume, display power transitions, and USB-C/alt-mode routing where applicable.
- PHY diagnostic tests that monitor RX/TX IRQ status/clear behavior, lane transceiver mode changes, RX phase-2 calibration events, DCC on-demand events, TX request/reset events, and loopback controls.
- Calibration/adaptation validation using hardware diagnostics or firmware logs for `INIT_PWRUP_DONE`, `RX_ADAPT_DONE`, `LANE_CMNCAL_*`, DCC code readbacks, signal-detect status, VREFGEN status, and per-lane FOM/adaptation values.
