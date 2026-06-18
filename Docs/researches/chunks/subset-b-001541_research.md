# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 9644-12065

## Scope And Purpose

This chunk is a generated AMDGPU DCE 12.0 register field mask/shift header. It contains no executable C code; it publishes preprocessor constants that describe bit positions and bit masks for display-controller MMIO registers. Consumers combine these field macros with address macros from `dce_12_0_offset.h` and register helper macros to read, write, or update specific fields on DCE 12.0/Vega-era display hardware.

The requested range begins in the middle of the UNIPHY impedance-calibration table and then covers several display I/O domains:

- UNIPHY impedance calibration for links E/F, impedance calibration control for the E/F link pair, and calibration pulse-width fields for C/D and E/F link pairs.
- Low-power UNIPHY link controls and channel crossbar controls for `UNIPHYLPA` and `UNIPHYLPB`.
- DCIO DPCS TX/RX interrupt field definitions and DCIO semaphore fields.
- A large GPIO section for generic pins, DVO data/control/clock pins, DDC1-DDC6, DDCVGA, sync, genlock/swaplock, HPD, power-sequencing pins, pad strength, I2C pads, I2S/SPDIF pins, TX12/RX enable controls, and AUX/HPD analog pad controls.
- DSI/DAC/DPHY macro control and reserved fields.
- DPRX AUX receiver/transmitter controls, DMCU interrupt status/ack fields, indexed AUX/EDID/DPCD/message/KSV buffers, message pending flags, and scratch registers.
- DPRX DPHY DPCD-facing link-training fields, lane quality status, readiness/lock/alignment status, per-lane error thresholds and counters, block-symbol error counters, lane setup, dynamic deskew, bypass, and internal reset controls.

The path is under a local `ceph-client` mirror, but this specific file is AMDGPU Linux kernel display-driver hardware metadata. It does not define Ceph filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, or runtime APIs in this chunk. The exported API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the raw 32-bit field mask, typically with an `L` suffix.
- `<REGISTER>` names correspond to MMIO addresses defined in the companion `dce_12_0_offset.h`, for example `mmDC_GPIO_DDC1_A`, `mmDPRX_AUX_CONTROL`, or `mmDPRX_DPHY_INT_RESET`.

The UNIPHY/DCIO portion defines fields for `UNIPHY_IMPCAL_LINKE`, `UNIPHY_IMPCAL_LINKF`, `DCIO_IMPCAL_CNTL_EF`, `UNIPHY_IMPCAL_PSW_EF`, `UNIPHYLPA_LINK_CNTL`, `UNIPHYLPB_LINK_CNTL`, `UNIPHYLPA_CHANNEL_XBAR_CNTL`, `UNIPHYLPB_CHANNEL_XBAR_CNTL`, `DCIO_DPCS_TX_INTERRUPT`, `DCIO_DPCS_RX_INTERRUPT`, and `DCIO_SEMAPHORE0` through `DCIO_SEMAPHORE7`. These cover calibration enable/status/override values, low-power link enablement, pixel-valid reset and lane inversion/stagger controls, channel source muxing, and interrupt type/mask/occur bits for TX/RX PHY lanes.

The GPIO macros form a repeated register-family contract:

- `*_MASK` registers expose software mask and pull-down or receiver controls.
- `*_A` registers expose pin assignment/alternate-function selection bits.
- `*_EN` registers expose output-enable or function-enable bits.
- `*_Y` registers expose output value/readback fields.

This pattern appears for `DC_GPIO_GENERIC_*`, `DC_GPIO_DVODATA_*`, `DC_GPIO_DDC1_*` through `DC_GPIO_DDC6_*`, `DC_GPIO_DDCVGA_*`, `DC_GPIO_SYNCA_*`, `DC_GPIO_GENLK_*`, `DC_GPIO_HPD_*`, `DC_GPIO_PWRSEQ_*`, `DC_GPIO_I2CPAD_*`, and `DC_GPIO_I2S_SPDIF_*`. Additional GPIO control registers include pad drive strength (`DC_GPIO_PAD_STRENGTH_1`, `DC_GPIO_PAD_STRENGTH_2`, `DC_GPIO_I2CPAD_STRENGTH`, `DC_GPIO_I2S_SPDIF_STRENGTH`, `DVO_STRENGTH_CONTROL`), DVO reference/skew controls, `DC_GPIO_TX12_EN`, `DC_GPIO_RXEN`, `PHY_AUX_CNTL`, `AUXI2C_PAD_ALL_PWR_OK`, `DC_GPIO_PULLUPEN`, and `DC_GPIO_AUX_CTRL_0` through `DC_GPIO_AUX_CTRL_6`.

The DPRX AUX macros describe a DisplayPort receiver AUX engine: `DPRX_AUX_REFERENCE_PULSE_DIV`, `DPRX_AUX_CONTROL`, `DPRX_AUX_HPD_CONTROL1/2`, `DPRX_AUX_RX_STATUS`, `DPRX_AUX_RX_ERROR_MASK`, DPHY TX/RX timing controls, DPHY TX/RX status, DMCU hardware interrupt status and ack fields, CPU-to-DMCU and DMCU-to-CPU interrupt handshakes, and indexed storage/data ports for AUX, EDID, DPCD, messages, and KSV values.

The DPRX DPHY macros describe receiver-side DisplayPort link-training and error-monitoring surfaces: DPCD lane count, training pattern and MST enable fields; per-lane link-quality set/status fields; ready, comma lock, symbol recovery lock, interlane alignment, FIFO level, and wait-count fields; per-lane symbol/disparity/test-pattern error thresholds and counters; block-symbol interval/cp error counters; lane map/inversion fields; LFSR/error-correction controls; enhanced framing, MTP header count force, dynamic deskew match/control data, deskew bypass, and broad internal reset bits for lane align, static/dynamic deskew, 8b/10b decoder, lane count, inversion, lane reversal, enable, control, training, header parse, and SDOUT logic.

## Control Flow

This chunk has no runtime control flow. Every line is a `#define` that supplies a constant.

The runtime control flow is in consumers that include this header. DCE120 GPIO code shows the common pattern:

1. Include `dce_12_0_offset.h` for `mm<REGISTER>` addresses and `dce_12_0_sh_mask.h` for the field masks.
2. Compose an MMIO address through the local `REG(reg_name)` macro, which adds the SOC base segment from `vega10_ip_offset.h` to `mm<REGISTER>`.
3. Store or compare field masks such as `DC_GPIO_DDC1_A__DC_GPIO_DDC1DATA_A_MASK`, `DC_GPIO_HPD_A__DC_GPIO_HPD1_A_MASK`, or `DC_GPIO_GENLK_A__DC_GPIO_GENLK_CLK_A_MASK`.
4. Let generic register helper code perform field extraction or read-modify-write using the selected register address, mask, and shift metadata.

In `display/dc/gpio/dce120/hw_translate_dce120.c`, `offset_to_id()` maps `DC_GPIO_*_A` offsets and masks back to logical `GPIO_ID_*` and enum values. `id_to_offset()` maps logical DDC data/clock, generic, HPD, sync, and genlock/swaplock IDs to `DC_GPIO_*_A` offsets and matching field masks. It then derives the companion Y/EN/MASK offsets by adding or subtracting from the selected `*_A` register, relying on the generated address and field layout being regular.

In `display/dc/gpio/dce120/hw_factory_dce120.c`, the same mask header initializes `hpd_sh_mask`, `ddc_shift`, and `ddc_mask` tables through `HPD_MASK_SH_LIST()` and `DDC_MASK_SH_LIST()`. Those tables are handed to hardware GPIO/DDC/HPD objects so higher-level display code can manipulate pins without hard-coding bit positions.

For the AUX and DPRX DPHY sections, expected runtime flows are hardware and firmware oriented: program AUX timing/control fields, inspect RX/TX status, handle DMCU interrupt status/ack fields, index AUX/EDID/DPCD/message buffers, program link-training-visible DPCD fields, and read or clear receiver PHY error counters and alignment/deskew status. This header only supplies the bitfield constants; protocol sequencing lives in display core, firmware-facing DMCU code, or hardware initialization paths outside this chunk.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. It describes hardware-backed state in display MMIO registers.

The represented hardware state includes:

- Calibration state: UNIPHY impedance calibration enable/status/error, calibration values, overrides, pulse-width values, and arbitration state.
- Link and PHY state: low-power link enablement, channel inversion/crossbar selection, DPCS interrupt status/masks, and per-lane TX/RX interrupt occurrence bits.
- GPIO pin state: mux/assignment bits, mask bits, output enables, output/readback values, pull-down/pull-up controls, receiver enables, HPD and AUX analog pad filter/slew/bias controls, and drive-strength settings.
- DSI/DAC/DPHY macro state: DSI dual control and many reserved macro-control slots.
- DPRX AUX state: AUX/HPD control, RX/TX PHY timing and status, error masks, DMCU interrupt status/ack/mask bits, indexed AUX/EDID/DPCD/message/KSV storage, scratch registers, and pending flags.
- DPRX DPHY state: link-training-visible DPCD values, MST enable, lane quality pattern state, ready/lock/alignment status, error thresholds, sticky or sampled error counters, clear bits, lane mapping/inversion, deskew configuration, enhanced-frame state, and reset/bypass controls.

Persistence depends on the register and power domain. Control settings generally remain until another driver/firmware write, display engine reset, PHY reset, suspend/resume transition, power-gating transition, or full GPU reset. Status bits may reflect current hardware state, sampled state, sticky interrupt status, or write-one-to-clear/acknowledge behavior. The mask header does not encode access direction, reset defaults, self-clearing behavior, volatile status timing, or reserved-bit write requirements.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register header contract. It is normally paired with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h`, which defines the corresponding `mm<REGISTER>` address and `mm<REGISTER>_BASE_IDX` constants.
- DCE120 display code using SOC base offsets from `soc15_hw_ip.h` and `vega10_ip_offset.h`.
- AMD display register helpers such as `reg_helper.h`, plus block-specific register list headers such as `hpd_regs.h` and `ddc_regs.h`.

Direct include points for `dce_12_0_sh_mask.h` in this source tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_translate_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_factory_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c`

The strongest visible integration in this chunk is the DCE120 GPIO layer. `hw_translate_dce120.c` uses the GPIO field masks to translate between raw register/mask pairs and logical DDC, HPD, generic, sync, and genlock/swaplock pin identifiers. `hw_factory_dce120.c` packages generated masks and shifts into DDC and HPD hardware objects. Higher layers then use these objects for EDID/DDC communication, hotplug detection, connector routing, and display pin control.

The UNIPHY, AUX, and DPRX DPHY constants integrate with display link bring-up, DisplayPort AUX and link-training behavior, DMCU/firmware interrupt routing, debug/status collection, and receiver-side test or validation modes. Some macros may be unused in this Linux tree while still reflecting fields present in AMD's generated ASIC register database.

## Risks And Edge Cases

The main risk is silent bitfield drift. A wrong mask or shift compiles cleanly but causes consumers to read or write the wrong field in a live hardware register. For GPIO/DDC/HPD paths, that can mean the wrong pin is selected, an output is enabled unexpectedly, HPD detection is masked or filtered incorrectly, AUX/DDC pad mode is misprogrammed, or EDID reads fail.

The GPIO section has dense repeated patterns with small differences between DDC instances, HPD instances, generic pins, and companion `MASK/A/EN/Y` registers. Copy or generator mistakes are easy to miss by inspection. DCE120 translation code also assumes that for a selected `*_A` offset, the matching `*_Y`, `*_EN`, and `*_MASK` registers are at `+2`, `+1`, and `-1`; bad address or mask definitions break that abstraction.

Fields whose semantic names include `MASK` can produce confusing macro names such as `DC_GPIO_HPD_MASK__DC_GPIO_HPD1_MASK_MASK` or `DCIO_DPCS_TX_INTERRUPT__DCIO_DPCS_TXA_INT_MASK_MASK`. The first `MASK` is part of the hardware register or field name, while the second `_MASK` is the generated bit-mask suffix. Reviewers and manual patches must preserve this distinction.

Control and status semantics are not represented here. Many fields are likely write-one-to-clear, sticky status, read-only, self-clearing reset, reserved, or power-domain-sensitive. Using only the presence of a `_MASK` macro to infer writable behavior is unsafe.

The AUX/DPRX and DPHY sections include protocol-sensitive state. Incorrect AUX timing, DMCU interrupt ack/mask handling, DPCD indexed-buffer access, lane count/training pattern fields, deskew controls, or error counter clear bits can break DisplayPort receiver behavior, diagnostics, or firmware handshakes. Reset fields in `DPRX_DPHY_INT_RESET` cover many sub-blocks and could disrupt link recovery if toggled out of sequence.

The chunk boundary starts immediately after `DCIO_IMPCAL_CNTL_CD` masks and continues with `UNIPHY_IMPCAL_PSW_CD`, so the preceding lines in an earlier chunk define the matching `DCIO_IMPCAL_CNTL_CD` shifts. The range also ends in the middle of the `DPRX_DPHY_INT_RESET` field list, before later lines continue with remaining masks and threshold-exceeded status registers. The merge lane should treat these as chunk boundaries, not file-level omissions.

## Test Signals

Useful validation is mostly compile-time plus hardware display behavior:

- AMDGPU/DCE120 builds should compile without missing field definitions in all direct include sites.
- Generated-register validation can compare every field mask and shift in this chunk against AMD's source register database and confirm each field has the expected companion address in `dce_12_0_offset.h`.
- GPIO translation tests should verify DDC1-DDC6, DDCVGA, I2C pad, HPD1-HPD6, generic GPIOs, sync, and genlock/swaplock mappings round-trip through offset/mask to logical ID and back.
- EDID/DDC tests should cover all exposed DDC lines and the DDCVGA/I2C-pad paths because their field masks and offsets are selected from this chunk.
- Hotplug tests should watch HPD assertion/deassertion, interrupt masking, glitch filtering/slew settings, suspend/resume, and multi-monitor connector combinations.
- DisplayPort AUX tests should cover successful AUX transactions, timeout/error paths, HPD IRQ behavior, DMCU interrupt status/ack handling, and indexed AUX/DPCD/EDID/message buffer accesses.
- Link-training or receiver diagnostics should monitor DPRX DPHY ready, comma/SR lock, interlane alignment, lane-quality pattern detect, symbol/disparity/test-pattern counters, block-symbol interval errors, and clear-bit behavior.
- Low-power and reset tests should exercise display suspend/resume, link disable/enable, UNIPHY calibration state, DPRX DPHY reset fields, and AUX/HPD pad power controls.

Regression symptoms from bad constants include blank displays, failed EDID reads, hotplug storms or missed HPD events, AUX timeouts, incorrect DDC line selection, broken genlock/swaplock pins, unexpected GPIO output drive, DisplayPort link-training failures, persistent receiver error counts, failed recovery after reset, or failures that appear only on a specific connector, lane count, or DDC/HPD instance.

## Cross-Chunk Notes

Earlier chunks of `dce_12_0_sh_mask.h` define preceding DCE 12.0 display-controller field masks and the start of the UNIPHY impedance-calibration area. Later chunks continue after `DPRX_DPHY_INT_RESET` with the remaining DPRX DPHY status/interrupt masks and the rest of the generated display register-field namespace. The final per-file research should present the complete file as generated AMDGPU DCE 12.0 register mask/shift metadata rather than as algorithmic driver logic.
