# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_offset.h lines 5135-6193

## Scope

This chunk is the final 1,059-line slice of the generated AMD DCN 2.0.1 register offset header. The file ends at line 6193, so this range includes the tail of the display I/O offset map and the header guard terminator. It exports preprocessor constants only: memory-mapped register offsets named with `mm...` prefixes, per-register base-index constants named `mm..._BASE_IDX`, and indirect Azalia endpoint register indices named with `ix...` prefixes. There are no C functions, structs, enums, inline helpers, or local algorithms in this slice.

The visible hardware domains are:

- The tail of `dce_dc_dio_dout_i2c_dispdec`, including DDC/I2C transaction, data, EDID-detect, and read-request interrupt registers.
- `dce_dc_dio_dio_misc_dispdec` for DIO scratch registers, memory power controls/status, DIO/DIG clock controls, HDMI RX status timer, generic DIO interrupt message, and generic interrupt clear.
- `dce_dc_dio_hpd0_dispdec` and `dce_dc_dio_hpd1_dispdec` for two hot-plug-detect blocks.
- `dce_dc_dio_dp_aux0_dispdec` and `dce_dc_dio_dp_aux1_dispdec` for two DisplayPort AUX/I2C-over-AUX engines.
- `dce_dc_dio_dig0_dispdec` and `dce_dc_dio_dig1_dispdec` for two digital front-end and HDMI/AFMT/TMDS formatter instances.
- `dce_dc_dio_dp0_dispdec` and `dce_dc_dio_dp1_dispdec` for two DisplayPort link encoder instances.
- `dce_dc_dcio_dcio_dispdec` and `dce_dc_dcio_dcio_chip_dispdec` for DCIO, UNIPHY, pinstrap, GPIO/DDC/HPD/AUX pad, and pad-power control offsets.
- `azf0endpoint0_endpointind`, `azf0endpoint1_endpointind`, `azf0inputendpoint0_inputendpointind`, and `azf0inputendpoint1_inputendpointind` for HDA/Azalia display-audio endpoint and input-endpoint indirect indices.

## Purpose

The purpose of this chunk is to bind the DCN 2.0.1 display driver to the exact hardware register addresses for external display I/O, link encoding, AUX/DDC, HPD, HDMI/DP metadata, and display audio endpoint programming. The AMD display core avoids scattering raw register numbers through functional code; instead, resource and IRQ setup code includes this header and expands macros such as `SR`, `SRI`, `SRII`, and `SRI_IX` into per-block register tables.

In this chunk, most `mm...` register offsets have `_BASE_IDX` value `2`, which the DCN201 resource and IRQ code converts through `DMU_BASE__INST0_SEG2` before adding the register offset. The `ix...` constants are different: they are not memory-mapped MMIO offsets themselves, but endpoint-indirect register indices used with Azalia endpoint index/data registers. This distinction is a core integration contract for display audio.

## Important API Surface

The exported API surface is macro names and numeric constants. Important groups include:

- DDC/I2C control surface: `mmDC_I2C_TRANSACTION2`, `mmDC_I2C_TRANSACTION3`, `mmDC_I2C_DATA`, `mmDC_I2C_EDID_DETECT_CTRL`, and `mmDC_I2C_READ_REQUEST_INTERRUPT`.
- DIO shared state/control: `mmDIO_SCRATCH0` through `mmDIO_SCRATCH7`, `mmDIO_MEM_PWR_STATUS`, `mmDIO_MEM_PWR_CTRL`, `mmDIO_MEM_PWR_CTRL2`, `mmDIO_MEM_PWR_CTRL3`, `mmDIO_POWER_MANAGEMENT_CNTL`, `mmDIG_SOFT_RESET`, `mmDIO_CLK_CNTL`, `mmDIO_CLK_CNTL2`, and `mmDIO_CLK_CNTL3`.
- HPD instance registers: `mmHPD0_DC_HPD_INT_STATUS`, `mmHPD0_DC_HPD_INT_CONTROL`, `mmHPD0_DC_HPD_CONTROL`, `mmHPD0_DC_HPD_FAST_TRAIN_CNTL`, `mmHPD0_DC_HPD_TOGGLE_FILT_CNTL`, and matching `HPD1` forms.
- AUX instance registers: `mmDP_AUX0_AUX_CONTROL`, `mmDP_AUX0_AUX_SW_CONTROL`, `mmDP_AUX0_AUX_ARB_CONTROL`, `mmDP_AUX0_AUX_INTERRUPT_CONTROL`, `mmDP_AUX0_AUX_SW_STATUS`, `mmDP_AUX0_AUX_LS_STATUS`, data registers, DPHY TX/RX controls, and matching `DP_AUX1` forms.
- DIG/HDMI/AFMT/TMDS registers for instances 0 and 1: `DIG_FE_CNTL`, `DIG_OUTPUT_CRC_*`, `DIG_CLOCK_PATTERN`, `DIG_TEST_PATTERN`, FIFO/status, HDMI metadata/generic/audio/ACR/VBI/infoframe/GC/DB controls, AFMT ISRC/generic/audio/status/ramp/60958 controls, `DIG_BE_CNTL`, `DIG_BE_EN_CNTL`, `TMDS_*`, `DIG_VERSION`, `DIG_LANE_ENABLE`, and `AFMT_CNTL`.
- DP link registers for instances 0 and 1: `DP_LINK_CNTL`, `DP_PIXEL_FORMAT`, `DP_MSA_COLORIMETRY`, `DP_CONFIG`, `DP_VID_STREAM_CNTL`, `DP_DPHY_*`, CRC, fast training, secondary packet/audio timing, MST MSE allocation/status, MSA timing parameters, DSC controls, DP DB, VBID misc, metadata transmission, and DSC bytes-per-pixel.
- DCIO/PHY/GPIO registers: `mmDC_GENERICA`, `mmUNIPHYA_LINK_CNTL`, `mmUNIPHYA_CHANNEL_XBAR_CNTL`, `mmUNIPHYB_LINK_CNTL`, `mmUNIPHYB_CHANNEL_XBAR_CNTL`, `mmDCIO_WRCMD_DELAY`, `mmDC_PINSTRAPS`, `mmDCIO_CLOCK_CNTL`, `mmDCIO_SOFT_RESET`, `mmDC_GPIO_DDC1_*`, `mmDC_GPIO_DDC2_*`, `mmDC_GPIO_HPD_*`, `mmDC_GPIO_PAD_STRENGTH_1`, `mmPHY_AUX_CNTL`, `mmDC_GPIO_AUX_CTRL_1` through `_5`, and `mmAUXI2C_PAD_ALL_PWR_OK`.
- Azalia endpoint indices: converter format, stream/channel ID, digital converter, stream formats, supported rates, stripe/ramp/GTC controls, pin capabilities, unsolicited response, pin sense, widget control, channel speaker, audio descriptors 0-13, multichannel controls, lipsync/HBR, sink info 0-8, hot-plug control, configuration default, codec channel-status overrides, LPIB snapshot/timer, coding type, format changed, wireless display identification, remote keepalive, and audio enable/disable/format-change interrupt status. Input endpoint indices mirror input converter and input pin controls with channel allocation and infoframe fields.

The DCN201 inclusion sites found in this repository include `display/dc/resource/dcn201/dcn201_resource.c`, `display/dc/irq/dcn201/irq_service_dcn201.c`, and `display/dc/clk_mgr/dcn201/dcn201_clk_mgr.c`. `dcn201_resource.c` uses this offset header with the matching `dcn_2_0_1_sh_mask.h` field header, then macro-expands address lists into static register tables for audio, stream encoders, AUX engines, HPD blocks, link encoders, and other display blocks.

## Control Flow

There is no local control flow in this header. Runtime control flow is external and looks like this:

1. DCN201 resource initialization includes this header and defines helper macros such as `SR(reg_name)`, `SRI(reg_name, block, id)`, `SRII(...)`, and `SRI_IX(...)`.
2. Register-list macros from object headers, for example `AUD_COMMON_REG_LIST(id)`, `SE_DCN2_REG_LIST(id)`, `DCN2_AUX_REG_LIST(id)`, `HPD_REG_LIST(id)`, `LE_DCN_COMMON_REG_LIST(id)`, and `UNIPHY_DCN2_REG_LIST(phyid)`, paste symbolic names into this header's `mm...` or `ix...` constants.
3. The expanded constants populate typed register tables such as `dce_audio_registers`, `dcn10_stream_enc_registers`, `dcn10_link_enc_aux_registers`, `dcn10_link_enc_hpd_registers`, and `dcn10_link_enc_registers`.
4. Functional display code uses `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, `AZ_REG_READ`, `AZ_REG_WRITE`, HPD helpers, AUX helpers, and link/stream encoder methods against those register tables.
5. IRQ setup in `irq_service_dcn201.c` uses `SRI(DC_HPD_INT_STATUS, HPD, reg_num)` and similar generated expressions to set HPD status, enable, and acknowledge register addresses for `DC_IRQ_SOURCE_HPD1`, `DC_IRQ_SOURCE_HPD2`, `DC_IRQ_SOURCE_HPD1RX`, and `DC_IRQ_SOURCE_HPD2RX`.

Hardware sequencing is therefore enforced by the consuming code, not by this header. For example, the stream encoder controls when `DIG_FE_CNTL.DIG_START` is updated, link encoder code handles DP/TMDS setup and training state, AUX code performs arbitration and transfer polling, and audio code writes Azalia endpoint registers through index/data indirection.

## State and Persistence

The header itself has no software state, storage, or persistence beyond compile-time constants. The constants point at hardware state that persists in MMIO registers until hardware reset, power-gating transitions, driver reprogramming, or a register-specific clear/ack operation.

State represented by this chunk includes:

- DDC/I2C transaction descriptors and data FIFOs used for EDID and monitor-side I2C access.
- HPD sense, interrupt enable, interrupt acknowledge, fast-training, and toggle-filter state for the two physical connector-detect paths.
- AUX engine control, arbitration, SW/LS status, data, DPHY TX/RX tuning, and interrupt state used by DisplayPort link management and DP AUX transactions.
- DIG front-end, HDMI packet/metadata/audio, AFMT, TMDS, and DP stream state used while a display stream is active.
- DP link training, PHY pattern, scrambler, CRC, MST slot allocation, secondary data packet, DSC, VBID, and metadata transmission state.
- DCIO soft reset, clock control, UNIPHY link/channel crossbar, GPIO DDC/HPD/AUX pads, pad strength, and AUX/I2C pad-power state.
- Azalia endpoint codec state for display audio capabilities, descriptors, pin-sense/hot-plug, ELD/sink info, channel/speaker setup, HBR/lipsync reporting, LPIB snapshots, and audio status interrupts.

Because these are hardware register addresses, a bad offset can leave the driver writing a different register than intended. The visible effects may persist until a full display modeset, DC reset, GPU reset, or suspend/resume cycle reinitializes the affected blocks.

## Dependencies and Integration Points

This chunk is tightly coupled to:

- `dcn_2_0_1_sh_mask.h`, which supplies the field masks and shifts for the registers whose addresses are defined here.
- `cyan_skillfish_ip_offset.h`, which provides the `DMU_BASE__INST0_SEG*` base segments used by DCN201 `BASE(...)` expansion.
- Display resource construction in `display/dc/resource/dcn201/dcn201_resource.c`, where these constants are assembled into register tables for two audio, stream encoder, AUX, HPD, and link encoder instances.
- DCN201 IRQ setup in `display/dc/irq/dcn201/irq_service_dcn201.c`, which uses `HPD0`/`HPD1` status/control offsets for hot-plug and HPD RX interrupt mapping.
- DCN201 link encoder code in `display/dc/dcn201/dcn201_link_encoder.c`, which receives register tables containing DP, UNIPHY, AUX, and HPD offsets and then delegates most operations to DCN10/DCN20 link encoder helpers.
- DCE/DCN shared audio code in `display/dc/dce/dce_audio.c`, which uses Azalia endpoint index/data accessors and the `ixAZF0...` endpoint indices represented in this chunk.
- DCE/DCN shared AUX, HPD, stream encoder, and link encoder helpers under `display/dc/dce`, `display/dc/dio/dcn10`, `display/dc/dio/dcn20`, and `display/dc/dcn20`.

The repeated instance layout is part of the contract. DCN201 resource code creates arrays with two stream encoders, two AUX register sets, two HPD register sets, two link encoders, and two audio register sets. This chunk mirrors that with `DIG0`/`DIG1`, `DP0`/`DP1`, `DP_AUX0`/`DP_AUX1`, `HPD0`/`HPD1`, `UNIPHYA`/`UNIPHYB`, and `AZF0ENDPOINT0`/`AZF0ENDPOINT1` definitions.

## Risks

- Offset drift is high impact. If any `mm...` value is wrong, register helper calls still compile but target the wrong MMIO address, causing display bring-up failure, missing HPD events, bad AUX/DDC transactions, failed link training, broken HDMI/DP audio, or writes into unrelated DCN state.
- `mm..._BASE_IDX` values are as important as the offsets. A correct offset with an incorrect segment index would calculate the wrong absolute MMIO address in DCN201 resource and IRQ code.
- Instance-copy mistakes can affect only one connector path. `HPD0` versus `HPD1`, `DP_AUX0` versus `DP_AUX1`, `DIG0` versus `DIG1`, and `DP0` versus `DP1` are nearly parallel blocks with different offsets; one mismatched constant may reproduce only on a specific port or PHY.
- Indirect `ixAZF0...` constants must not be treated as direct MMIO offsets. They are endpoint register indices written through Azalia endpoint index/data registers. Confusing `mm` and `ix` address spaces would corrupt audio programming.
- Clear/ack/status registers are sensitive. HPD, AUX, AFMT, generic DIO, and Azalia audio interrupt status fields can be sticky or write-one-to-clear in the corresponding mask header. A wrong register address or shared helper mapping can miss events or clear the wrong event.
- Power and reset registers carry broad blast radius. `DIO_MEM_PWR_CTRL*`, `DIO_POWER_MANAGEMENT_CNTL`, `DIG_SOFT_RESET`, `DCIO_CLOCK_CNTL`, and `DCIO_SOFT_RESET` can disable or reset active display I/O blocks if programmed at the wrong time.
- The chunk starts mid-I2C block at `mmDC_I2C_TRANSACTION2` and ends with the file-level `#endif`. Whole-file reconciliation must combine it with earlier chunks to describe the complete I2C block and the rest of the DCN 2.0.1 register map.

## Test Signals

Good validation signals for this chunk are mostly compile-time coverage plus hardware/display behavior:

- A full AMDGPU display build should catch missing or renamed macros in DCN201 resource, clock manager, IRQ, audio, AUX, HPD, stream encoder, and link encoder code.
- Header-generation or static-diff checks against AMD's register database and adjacent generated headers such as `dcn_2_0_0_offset.h`, `dcn_2_1_0_offset.h`, and matching `dcn_2_0_1_sh_mask.h` should flag unexpected offset, base-index, or instance-count changes.
- Connector tests should verify HPD plug/unplug, HPD RX, HPD toggle filtering, and IRQ acknowledgement on both connector instances.
- DisplayPort tests should exercise AUX reads/writes, DPCD access, link training, fast training, CRC/test patterns, MST slot allocation/status, DSC enablement, and secondary packet/metadata transmission on both DP links.
- HDMI/TMDS tests should cover mode set, TMDS encoder setup, HDMI infoframes, ACR/audio packet programming, generic metadata packets, AFMT status, and display audio hot-plug behavior.
- EDID/DDC tests should validate I2C transaction programming, data handling, EDID detect, and read-request interrupt behavior.
- Suspend/resume, runtime power management, display hotplug storms, and multi-monitor modes should show no stuck DIO/DCIO resets, pad-power failures, AUX pad power-not-OK state, missed HPD interrupts, or audio endpoint status regressions.

## Chunk Notes

This is a generated constants-only slice, so the research value is the hardware coverage and integration contract rather than local logic. The chunk is especially important for DCN201 external-display behavior because it contains the two-instance register maps for HPD, AUX, DIG, DP, UNIPHY, GPIO pads, and Azalia display-audio endpoint indices. Any edits to these constants should be treated as hardware-spec changes and validated against both generated register sources and real display-path behavior.
