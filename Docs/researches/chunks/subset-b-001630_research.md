# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 49386-51950

## Purpose

This chunk is part of AMDGPU's generated DCN 2.0 register field mask/shift header. It contains no executable C logic; it publishes compile-time bit layout constants for display-controller MMIO registers. Each field has paired macros:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit position.
- `REGISTER__FIELD_MASK` gives the already-positioned bit mask.

Driver code combines these macros with matching register addresses from `dcn_2_0_0_offset.h` and AMD display helper macros such as `SF(...)`, `REG_SET`, `REG_UPDATE`, and MMIO read/write helpers. Correctness is therefore a hardware ABI contract. A wrong mask or shift can compile cleanly but program the wrong GPIO, AUX, HPD, Display Stream Compression, or performance-monitor bit.

The range covers three main register surfaces:

- Tail fields for DC GPIO/HPD/AUX and panel power-sequencing controls, including HPD enable/output status, BLON/DIGON/ENA_BL/VSYNC/HSYNC power-sequence GPIO fields, pad strength, PHY AUX controls, AUX channel muxing, pull-ups, RX enables, TX enables, and AUX/I2C pad power status.
- Seven repeated `DCIO_UNIPHY<N>_UNIPHY_MACRO_CNTL_RESERVED0..47` blocks for UNIPHY instances 0-6. These expose full-width reserved control words rather than decoded named fields.
- DSC instance 0 and 1 register fields, including DSC top clock/debug controls, DSCCIF interface configuration, DSCC slice/PPS programming, DSCC rate-buffer overflow/underflow interrupt status, DSCC memory power controls, error counters, fullness-level diagnostics, test debug bus rotation, and DSC performance monitor counters. The chunk ends partway through `DC_PERFMON22_PERFMON_CVALUE_INT_MISC`; later fields belong to the next chunk.

Although this source tree is stored under a local `ceph-client` path, this header is AMDGPU display-driver hardware metadata. It has no Ceph filesystem protocol behavior, no distributed filesystem control flow, and no filesystem persistence semantics.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or runtime APIs in this chunk. The macro namespace is the public surface consumed by generated register tables.

The GPIO and AUX section exposes:

- `DC_GPIO_HPD_EN` and `DC_GPIO_HPD_Y` fields for HPD pad enablement, Schmitt/slew controls, select bits, spare bits, and observed/output HPD values for HPD1-HPD6. This chunk starts with `DC_GPIO_HPD_EN` mask definitions; the corresponding shift definitions are in the previous chunk.
- `DC_GPIO_PWRSEQ_MASK`, `DC_GPIO_PWRSEQ_A`, `DC_GPIO_PWRSEQ_EN`, and `DC_GPIO_PWRSEQ_Y` fields for panel power sequence pins such as `BLON`, `DIGON`, `ENA_BL`, `VSYNC_IN`, and `HSYNC_IN`. These macros define mask, pull-down disable, receiver, output assignment, enable, and value fields.
- `DC_GPIO_PAD_STRENGTH_1` and `DC_GPIO_PAD_STRENGTH_2` fields for pad drive strength, including GENLK, RX/TX HPD, sync, generic strength, external reset, 27 MHz reference, power-sequence pads, and reference source selection.
- `PHY_AUX_CNTL` fields for AUX/DDC pad wake, receive select, mode, pull-down/enable controls, per-AUX RX selection for AUX1-AUX6, and AUX calibration/bias controls.
- `DC_GPIO_TX12_EN`, `DC_GPIO_RXEN`, and `DC_GPIO_PULLUPEN` fields for data/clock/HPD/AUX/power-sequence transmit, receive, and pull-up enables.
- `DC_GPIO_AUX_CTRL_0` through `DC_GPIO_AUX_CTRL_5` fields for AUX/DDC muxing and pad control across AUX/DDC channels and generic GPIO-backed AUX routes.
- `AUXI2C_PAD_ALL_PWR_OK` fields indicating whether AUX/I2C pads for DDC1-6 and AUX1-6 report all-power-OK.

The UNIPHY section is mechanically repeated:

- `DCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED0..47` through `DCIO_UNIPHY6_UNIPHY_MACRO_CNTL_RESERVED0..47` each define a full-width `UNIPHY_MACRO_CNTL_RESERVED` field with shift 0 and mask `0xFFFFFFFFL`.
- These are placeholders for PHY macro control words without decoded bit names in this generated header. Their presence still matters because address and mask tables can expose them for low-level PHY workarounds or diagnostic access.

The DSC/DSCC section exposes two parallel DSC engines:

- `DSC_TOP0_DSC_TOP_CONTROL` and `DSC_TOP1_DSC_TOP_CONTROL` define `DSC_CLOCK_EN`, display-clock gating disable, and DSCC clock gating disable fields. `DSC_TOP*_DSC_DEBUG_CONTROL` defines debug enable and test-clock mux selection.
- `DSCCIF0_DSCCIF_CONFIG0/1` and `DSCCIF1_DSCCIF_CONFIG0/1` define input interface underflow recovery/status/interrupt enable, input pixel format, double-buffer update pending, group mode, and slice-in-line counters.
- `DSCC0_DSCC_CONFIG0/1` and `DSCC1_DSCC_CONFIG0/1` define slice topology, ICH reset/encoding controls, and rate-control buffer model size. `DSCC*_DSCC_STATUS` exposes double-buffer update pending.
- `DSCC*_DSCC_INTERRUPT_CONTROL_STATUS` defines rate-buffer overflow and underflow status bits for buffers 0-3, rate-control buffer model overflow status bits for models 0-3, matching interrupt enables, native 4:2:2 buffer overflow/underflow status and interrupt enables, DSC picture-finished and slice-finished interrupt enable/status bits, and a double-buffer update request.
- `DSCC*_DSCC_PPS_CONFIG0..22` encode most of the Display Stream Compression picture parameter set: DSC version, PPS identifier, line-buffer depth, bits per component/pixel, VBR/simple/native format flags, RGB conversion, block prediction, chunk size, picture and slice dimensions, initial transmit/decode delays, scale values and intervals, BPG offsets, initial/final offsets, flatness QP, rate-control model size, edge factor, quantization increment limits, target offsets, rate-control buffer thresholds 0-13, and range min/max QP plus BPG offsets for ranges 0-14.
- `DSCC*_DSCC_MEM_POWER_CONTROL` defines default memory low-power state, memory power force/disable/state, and native 4:2:2 memory power force/disable/state.
- `DSCC*_DSCC_*_SQUARED_ERROR_*`, `DSCC*_DSCC_MAX_ABS_ERROR*`, `DSCC*_DSCC_RATE_BUFFER*_MAX_FULLNESS_LEVEL`, and `DSCC*_DSCC_RATE_CONTROL_BUFFER*_MAX_FULLNESS_LEVEL` expose quality/error and buffer fullness diagnostics.
- `DSCC*_DSCC_TEST_DEBUG_BUS_ROTATE` defines debug bus rotation fields for debug buses 0-3.
- `DC_PERFMON21_*` and `DC_PERFMON22_*` define performance counter controls, counter state selection, perfmon control, run-enable start/stop selectors, interrupt status bits, and counter value registers for the DSC0 and DSC1 performance-monitor address blocks.

## Control Flow

This header chunk has no runtime control flow. It is preprocessor data.

Runtime control appears in consumers that instantiate register descriptors:

1. DCN 2.0 display code includes `dcn/dcn_2_0_0_offset.h` and `dcn/dcn_2_0_0_sh_mask.h`.
2. Resource and hardware-object headers use macro expansion patterns such as `SRI(...)`, `SF(...)`, and `DSC_SF(...)` to bind register addresses, masks, and shifts into typed register tables.
3. DSC setup code uses those tables to enable DSC clocks, program DSCCIF/DSCC PPS registers from `drm_dsc`/AMD DSC configuration structures, request double-buffered updates, and check status or error registers.
4. GPIO/DDC/HPD factory code uses the same generated mask/shift pattern to build HPD and DDC register tables for physical connectors, AUX/I2C pads, and generic GPIO paths.
5. IRQ, hotplug, modeset, panel power, DSC enable/disable, and diagnostic paths perform MMIO read-modify-write operations through the generated tables.

The macros themselves do not enforce legal sequencing. For example, they cannot ensure that DSC clock enable precedes PPS writes, that double-buffer update requests are acknowledged before stream enable, that interrupt status bits are cleared with the correct write semantics, or that AUX/HPD GPIO pad changes happen only while the link is in a safe state.

## State And Persistence Behavior

The file stores no software state and has no persistence mechanism. It describes state held in GPU display hardware registers.

The represented state includes:

- Connector and pad state: HPD enable/value, AUX/DDC muxing, receiver and pull-up enables, pad power-good status, and PHY AUX calibration/control.
- Panel power-sequence state: BLON/DIGON/ENA_BL/VSYNC/HSYNC masks, output assignments, enables, receiver state, and observed/output values.
- PHY state: UNIPHY reserved macro control words for seven PHY instances.
- DSC programming state: clock/debug controls, interface format and group mode, slice topology, full PPS register payload, memory power mode, double-buffer update pending/request status, overflow/underflow interrupt status, and native 4:2:2 memory or buffer state.
- Diagnostics and counters: squared-error accumulators, max absolute error, rate-buffer fullness, rate-control buffer fullness, debug bus rotation, perfmon counter control/state, interrupt status, and counter values.

Persistence depends on hardware semantics outside this header. Some fields are normal read/write control bits, some are read-only status or diagnostic counters, some are sticky interrupt bits that require acknowledgement, some are self-clearing requests, and many are reset by display power gating, link disable, suspend/resume, mode reset, DSC block reset, or ASIC reset. The generated macros do not record access type, reset value, volatility, write-one-to-clear behavior, or whether a field is safe to access while clocks are gated.

## Dependencies And Integration Points

This chunk depends on the matching generated address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h`

Direct include points for `dcn_2_0_0_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

The most direct consumer for the DSC part of this chunk is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.h`. Its `DSC_REG_LIST_DCN20(id)` lists the DSC top, DSCC, DSCCIF, error, fullness, and debug registers represented here, while `DSC_REG_LIST_SH_MASK_DCN20(mask_sh)` expands fields such as `DSC_TOP0_DSC_TOP_CONTROL__DSC_CLOCK_EN`, `DSCC0_DSCC_PPS_CONFIG*`, `DSCC0_DSCC_MEM_POWER_CONTROL`, and `DSCCIF0_DSCCIF_CONFIG0` into shift and mask tables.

The GPIO/AUX/HPD part integrates through `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c` and related headers such as `hpd_regs.h`, `ddc_regs.h`, and GPIO register definitions. That code constructs arrays of HPD and DDC register descriptors for six physical HPD/DDC instances plus VGA/generic fallback entries.

The broader display resource integration is in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`, which includes this generated header while assembling the DCN 2.0 resource pool for pipes, links, clocks, DSC objects, AUX/I2C, audio, panel controls, interrupts, and memory hub/display blocks.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A bad generated constant usually does not cause a compile error; it causes the register helper layer to update the wrong bit or fail to preserve adjacent bits during read-modify-write.

GPIO/AUX/HPD risks include broken hotplug detection, incorrect HPD polarity/value sampling, AUX/I2C transactions routed to the wrong pad, missing DDC access, stuck pull-ups, incorrect pad receiver enables, or panel power pins asserted in the wrong order. These failures surface as missing displays, unreliable hotplug, EDID read failures, blank embedded panels, or unstable link training.

Pad strength and PHY AUX controls are electrical-risk fields. Incorrect drive-strength, wake, receive-select, mode, or calibration masks can produce board-specific failures that appear only on long cables, marginal sinks, or low-power transitions. UNIPHY reserved fields are especially risky because the header provides no semantic names; any consumer must rely on external hardware documentation or workaround tables.

DSC PPS fields are high-impact. Incorrect shifts for bits per pixel/component, picture size, slice size, chunk size, delays, BPG offsets, QP ranges, buffer thresholds, or native 4:2:0/4:2:2 flags can make compressed streams fail to light, produce corrupted pixels, violate DisplayPort DSC requirements, or trigger rate-buffer overflows and underflows.

Interrupt/status fields are sensitive to access semantics not captured here. Misusing `DSCC*_DSCC_INTERRUPT_CONTROL_STATUS` or perfmon status masks can leave stale status bits, miss real buffer overflows, cause repeated interrupts, or acknowledge the wrong condition.

Memory-power and clock-control fields have sequencing risk. Incorrect `DSC_CLOCK_EN`, clock-gating disable, or DSCC memory power masks can make later DSC register writes ineffective, read stale diagnostic state, or cause resume/modeset-only failures.

The repeated structure creates copy-generation risk. DSCC0 and DSCC1 fields should be equivalent with only the instance prefix changed. UNIPHY0-6 reserved blocks are 48-register repeats. A single off-by-one instance, missing field, or copied mask from the wrong register would only fail on a specific PHY or DSC engine.

The line range boundaries are artificial. This chunk begins after the `DC_GPIO_HPD_EN` shift definitions and ends before the complete `DC_PERFMON22_PERFMON_CVALUE_INT_MISC` field list. The final per-file merge should treat those as chunk boundaries, not missing source content.

## Test Signals

Useful validation signals are mostly compile-time plus hardware behavior:

- Kernel or module build coverage for DCN 2.0 display paths that include `dcn_2_0_0_sh_mask.h`.
- Generated-header consistency checks comparing every `*_MASK` and `*__SHIFT` pair in this range against AMD's register database and the matching addresses in `dcn_2_0_0_offset.h`.
- Static checks that every field referenced by `DSC_REG_LIST_SH_MASK_DCN20(...)`, HPD/DDC mask lists, IRQ tables, and resource tables has both mask and shift macros.
- DisplayPort DSC enablement tests at multiple resolutions, refresh rates, bits per component, slice counts, and native 4:2:0/4:2:2/RGB modes. Good signals include stable link training, correct image output, no DSCC rate-buffer overflow/underflow status, and no double-buffer update stuck pending.
- Hotplug and AUX/DDC tests across all physical connectors, including EDID reads, HPD storm handling, link retraining, suspend/resume, DPMS, and connector unplug/replug stress.
- Embedded panel power-sequence tests for BLON/DIGON/ENA_BL behavior, backlight enable, panel wake/sleep, and resume from low-power states.
- DSC diagnostic reads for squared-error, max-absolute-error, rate-buffer fullness, and rate-control buffer fullness. Values should be sane for known streams and not show persistent overflow/underflow after modeset.
- Perfmon tests that configure `DC_PERFMON21` and `DC_PERFMON22` events, start/stop counters, observe active/state bits, read low/high values, and verify interrupt status/ack behavior where supported.
- Hardware lab or compliance tests for DisplayPort DSC streams and AUX/HPD electrical behavior, especially on marginal cables and high-bandwidth modes.

Regression symptoms from bad constants include missing connector detection, EDID read failures, blank or flickering DSC modes, corruption only when DSC is enabled, failures isolated to one DSC engine or one connector, interrupt storms, stale overflow status, stuck double-buffer updates, resume-only display failures, and perf counters that never start or report impossible values.

## Cross-Chunk Notes

Earlier chunks of `dcn_2_0_0_sh_mask.h` define the preceding DC GPIO fields and the beginning of `DC_GPIO_HPD_EN`, including shifts paired with the initial masks in this chunk. Later chunks continue from `DC_PERFMON22_PERFMON_CVALUE_INT_MISC` and proceed through the remaining DCN 2.0 register mask namespace. The final per-file research document should treat the full header as one generated DCN 2.0 hardware register-layout contract rather than as independent algorithmic code.
