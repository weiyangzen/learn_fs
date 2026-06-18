# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h lines 10193-12823

## Purpose

This chunk is a generated AMD DCN 3.2.1 register-offset header slice. It contains C preprocessor constants only: `reg...` macros for register offsets and paired `reg..._BASE_IDX` macros for selecting the base address segment used by the AMDGPU Display Core register helpers. There are no C functions, structs, enums, branches, allocation paths, locks, MMIO calls, or runtime persistence logic in this range.

The source tree path is under a local `ceph-client` mirror, but this file is AMDGPU display hardware metadata, not Ceph or distributed filesystem logic. The macros in this chunk support the DCN321 display resource layer and its lower-level DIO, DCIO, DSC, HPO, AFMT, VPG, APG, AUX, I2C, and stream encoder blocks.

The range is boundary-partial at both ends. It begins in the tail of the `DIG4` HDMI/TMDS encoder register block, after the block comment and base address from the previous chunk, and starts with `regDIG4_HDMI_ACR_44_0_BASE_IDX` followed by the remaining HDMI audio-clock-regeneration, AFMT, DIG backend, TMDS, version, and force-disable offsets. It ends inside the HPO DP stream encoder 3 VPG block at `regVPG9_VPG_MEM_PWR`; the rest of VPG9 and the following DP SYM32 encoder 3 block continue in the next chunk.

Within lines 10193-12823 there are 2,368 `#define` lines: 1,184 register offset macros and 1,184 matching `_BASE_IDX` macros. All visible `_BASE_IDX` values are `2`, except the range starts after a prior `DIG4` register value and includes the paired base-index macro for that prior register. Address-block comments identify 66 complete or partial hardware blocks after the initial `DIG4` continuation.

## Important APIs, Types, And Macros

The exported interface is the generated macro namespace:

- `reg<REGISTER_OR_BLOCKED_REGISTER>` expands to a hardware register offset value.
- `reg<REGISTER_OR_BLOCKED_REGISTER>_BASE_IDX` expands to a base-index selector, used by `BASE(reg..._BASE_IDX)` in DCN resource code.
- `// addressBlock:` and `// base address:` comments document the generated hardware register block and its nominal base.

The main macro families in this chunk are:

- `regDIG4_*`: the tail of DIO stream encoder instance 4 HDMI/TMDS state. Visible registers include HDMI ACR `32/44/48` values and status, `AFMT_CNTL`, backend enable/control, TMDS control characters, sync/DC-balancer patterns, generated control bits, version, and force-disable.
- `regAFMT0_*` through `regAFMT5_*`: audio formatting blocks for DIO DIG0-DIG4 plus HPO HDMI stream encoder 0. Each block has VBI packet control, audio packet controls, audio info registers, IEC 60958 channel status words, audio CRC control/result/status, ramp controls, infoframe control, interrupt status, audio source control, and memory power.
- `regDME0_*` through `regDME9_*`: data/meta engine control and memory-control registers for DIO stream encoders, HPO HDMI, and HPO DP stream encoders.
- `regVPG0_*` through partial `regVPG9_*`: video packet generator blocks. VPG0-VPG8 are complete in the chunk and include generic packet access/data, frame and immediate update controls, generic status, memory power, ISRC access/data, and MPEG info registers. VPG9 is partial and stops at `VPG_MEM_PWR`.
- `regDP_AUX0_*` through `regDP_AUX4_*`: five AUX channel register blocks with AUX control, arbitration, software control, reply/data FIFOs, interrupt control, LS status and data, GTC sync, debug/status, and PHY wake control.
- `regDC_I2C_*`, `regDC_I2C_DDC*`, `regDC_I2C_EDID*`, and related macros: DOUT I2C control, arbitration, setup, speed, sw status, transaction, data, DDC/EDID detect and setup, and interrupt registers.
- `regDIO_*`: DIO scratch registers, global swap lock, stream encoder control, DIO memory power, interrupt status/control, and link E/F control.
- `regDC_GENERICA` through `regDCIO_SOFT_RESET`: DCIO top-level generic, GPIO, interrupt, clock, power, debug, and reset registers.
- `regDC_GPIO_*`, `regDCIO_*`, `regUNIPHY*`, `regAUXI2C_PAD_*`, `regPHY_*`, and `regBL_PWM_*`: DCIO chip/pad control, hotplug and sync GPIO masks, AUX/I2C pad control, generic output masks, backlight PWM/BLON/VARY_BL control, UNIPHY clock and GPIO power gates, and pad power status.
- `regDCIO_UNIPHY0_*` through `regDCIO_UNIPHY4_*`: five UNIPHY macro-control reserved register banks, each exposing reserved offsets 0-57. These are generated placeholders or opaque DCIO/PHY control locations rather than typed behavior in this header.
- `regDC_GPIO_PWRSEQ_*`, `regPWRSEQ_*`, and `regPANEL_PWRSEQ_*`: panel/power-sequencer GPIO enables, masks, power control, backlight control, ref-divider values, status, reset/debug/debug index/data, and spare state.
- `regDSCC0_*` through `regDSCC3_*`: four Display Stream Compression controller blocks. Each includes config, picture size, slice dimensions, bits-per-pixel, rate-control buffers/offsets/scales/ranges, mux, status, debug, memory power, and test-debug registers.
- `regDSCCIF0_*` through `regDSCCIF3_*`: small DSC controller interface config pairs.
- `regDSC_TOP0_*` through `regDSC_TOP3_*`: DSC top-level control and debug-control pairs.
- `regHPO_TOP_*` and `regDP_STREAM_MAPPER_*`: HPO top clock/hardware control and four DP stream mapper controls.
- `regDP_STREAM_ENC0_*` through `regDP_STREAM_ENC3_*`: HPO DP stream encoder clock, input mux, audio control, clock-ramp-adjuster FIFO status controls, and spare registers.
- `regAPG0_*` through `regAPG3_*`: HPO DP audio packet generator control, debug generator, packet control, audio CRC controls/results, status/status2, memory power, and spare registers.
- `regDP_SYM32_ENC0_*` through `regDP_SYM32_ENC2_*`: HPO DP 32-symbol encoder blocks for instances 0-2. Each block includes encoder control, video FIFO, double-buffer controls, pixel format, video MSA0-MSA8, hblank control, SDP/GSP controls 0-14, audio and metadata packet controls, MSA/VBID/stream/panel-replay controls, video CRC controls/results/status, memory power, and spare registers.

## Address-Block Coverage

The generated block layout in this chunk is regular and instance-oriented:

- DIO stream/audio packet path: tail of `DIG4`, AFMT0-AFMT4, DME0-DME4, VPG0-VPG4.
- DIO sideband path: DP_AUX0-DP_AUX4, DOUT I2C, and DIO miscellaneous controls.
- DCIO path: DCIO top-level, DCIO chip/pad controls, and UNIPHY0-UNIPHY4 reserved macro-control banks.
- Panel and compression path: PWRSEQ0, DSC controller/interface/top blocks for DSC0-DSC3.
- HPO path: HPO top, DP stream mapper, HPO HDMI stream encoder 0 AFMT/DME/VPG, HPO DP stream encoders 0-3, APG0-APG3, DME6-DME9, VPG6-partial VPG9, and DP SYM32 encoders 0-2.

The complete block list observed after the initial `DIG4` continuation is:

`dce_dc_dio_dig0_afmt_afmt_dispdec`, `dce_dc_dio_dig1_afmt_afmt_dispdec`, `dce_dc_dio_dig2_afmt_afmt_dispdec`, `dce_dc_dio_dig3_afmt_afmt_dispdec`, `dce_dc_dio_dig4_afmt_afmt_dispdec`, `dce_dc_dio_dig0_dme_dme_dispdec`, `dce_dc_dio_dig0_vpg_vpg_dispdec`, `dce_dc_dio_dig1_dme_dme_dispdec`, `dce_dc_dio_dig1_vpg_vpg_dispdec`, `dce_dc_dio_dig2_dme_dme_dispdec`, `dce_dc_dio_dig2_vpg_vpg_dispdec`, `dce_dc_dio_dig3_dme_dme_dispdec`, `dce_dc_dio_dig3_vpg_vpg_dispdec`, `dce_dc_dio_dig4_dme_dme_dispdec`, `dce_dc_dio_dig4_vpg_vpg_dispdec`, `dce_dc_dio_dp_aux0_dispdec`, `dce_dc_dio_dp_aux1_dispdec`, `dce_dc_dio_dp_aux2_dispdec`, `dce_dc_dio_dp_aux3_dispdec`, `dce_dc_dio_dp_aux4_dispdec`, `dce_dc_dio_dout_i2c_dispdec`, `dce_dc_dio_dio_misc_dispdec`, `dce_dc_dcio_dcio_dispdec`, `dce_dc_dcio_dcio_chip_dispdec`, `dce_dc_dcio_dcio_uniphy0_dispdec`, `dce_dc_dcio_dcio_uniphy1_dispdec`, `dce_dc_dcio_dcio_uniphy2_dispdec`, `dce_dc_dcio_dcio_uniphy3_dispdec`, `dce_dc_dcio_dcio_uniphy4_dispdec`, `dce_dc_pwrseq0_dispdec_pwrseq_dispdec`, `dce_dc_dsc0_dispdec_dscc_dispdec`, `dce_dc_dsc0_dispdec_dsccif_dispdec`, `dce_dc_dsc0_dispdec_dsc_top_dispdec`, `dce_dc_dsc1_dispdec_dscc_dispdec`, `dce_dc_dsc1_dispdec_dsccif_dispdec`, `dce_dc_dsc1_dispdec_dsc_top_dispdec`, `dce_dc_dsc2_dispdec_dscc_dispdec`, `dce_dc_dsc2_dispdec_dsccif_dispdec`, `dce_dc_dsc2_dispdec_dsc_top_dispdec`, `dce_dc_dsc3_dispdec_dscc_dispdec`, `dce_dc_dsc3_dispdec_dsccif_dispdec`, `dce_dc_dsc3_dispdec_dsc_top_dispdec`, `dce_dc_hpo_hpo_top_dispdec`, `dce_dc_hpo_dp_stream_mapper_dispdec`, `dce_dc_hpo_hdmi_stream_enc0_afmt_afmt_dispdec`, `dce_dc_hpo_hdmi_stream_enc0_dme_dme_dispdec`, `dce_dc_hpo_hdmi_stream_enc0_vpg_vpg_dispdec`, `dce_dc_hpo_dp_stream_enc0_dispdec`, `dce_dc_hpo_dp_stream_enc0_apg_apg_dispdec`, `dce_dc_hpo_dp_stream_enc0_dme_dme_dispdec`, `dce_dc_hpo_dp_stream_enc0_vpg_vpg_dispdec`, `dce_dc_hpo_dp_sym32_enc0_dispdec`, `dce_dc_hpo_dp_stream_enc1_dispdec`, `dce_dc_hpo_dp_stream_enc1_apg_apg_dispdec`, `dce_dc_hpo_dp_stream_enc1_dme_dme_dispdec`, `dce_dc_hpo_dp_stream_enc1_vpg_vpg_dispdec`, `dce_dc_hpo_dp_sym32_enc1_dispdec`, `dce_dc_hpo_dp_stream_enc2_dispdec`, `dce_dc_hpo_dp_stream_enc2_apg_apg_dispdec`, `dce_dc_hpo_dp_stream_enc2_dme_dme_dispdec`, `dce_dc_hpo_dp_stream_enc2_vpg_vpg_dispdec`, `dce_dc_hpo_dp_sym32_enc2_dispdec`, `dce_dc_hpo_dp_stream_enc3_dispdec`, `dce_dc_hpo_dp_stream_enc3_apg_apg_dispdec`, `dce_dc_hpo_dp_stream_enc3_dme_dme_dispdec`, and partial `dce_dc_hpo_dp_stream_enc3_vpg_vpg_dispdec`.

## Control Flow

This header has no executable control flow. The runtime flow is indirect through generated register-list expansion:

1. `display/dc/resource/dcn321/dcn321_resource.c` includes `dcn/dcn_3_2_1_offset.h` and `dcn/dcn_3_2_1_sh_mask.h`.
2. Resource macros such as `SR`, `SR_ARR`, `SRI`, and `SRI_ARR` expand register names into actual offsets using `BASE(reg..._BASE_IDX) + reg...`.
3. DCN321 constructors populate per-block register tables for AUX engines, I2C engines, VPG, AFMT, APG, DIO stream encoders, HPO DP stream encoders, DSC blocks, DWB/MMHUBBUB, and other resource objects.
4. Runtime display code calls block-specific helpers, which use those tables with register helpers such as read/write/update/get/set wrappers to perform MMIO operations.
5. Hardware and firmware state machines, not this header, determine ordering for AUX transactions, I2C transactions, HDMI/TMDS packet generation, DSC programming, stream mapping, link enablement, HPO DP packet generation, panel power sequencing, and DCIO/PHY control.

Because this file only supplies numeric constants, sequencing rules are external. Consumers must still follow the DCN hardware programming model for power-up, link training, stream encoder setup, DSC configuration, audio packet programming, panel power transitions, HPO DP stream mapping, and suspend/resume.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It names MMIO-backed hardware registers whose values live in display hardware:

- AFMT, VPG, APG, DME, DIG, and stream encoder registers hold packet, audio, metadata, clock, video-stream, CRC, FIFO, status, spare, and memory-power state.
- AUX and I2C registers hold sideband transaction setup, data, arbitration, interrupt, status, and debug state for DP AUX, DDC, and EDID access.
- DCIO and UNIPHY registers hold pad, GPIO, power, clock, interrupt, reset, and opaque PHY macro-control state.
- PWRSEQ and panel registers hold panel power, reset, backlight, BLON, ref-divider, status, and debug state.
- DSC controller/interface/top registers hold compression configuration, rate-control, slice/picture, memory-power, status, and debug state.
- HPO top, DP stream mapper, HPO DP stream encoders, APG, VPG, DME, and DP SYM32 encoders hold high-performance output mapping, audio/video packet, Main Stream Attribute, VBID, SDP/GSP, metadata, panel replay, CRC, and memory-power state.

Persistence and side effects are hardware-defined. Some registers are configuration values that remain until a modeset, link retrain, power transition, suspend/resume, or ASIC reset. Others are status latches, FIFOs, clear-on-read or write-one-to-clear interrupt bits, self-clearing triggers, firmware-owned debug/scratch state, or power-gated memory controls. The generated offset header does not encode access type, reset value, volatility, locking, ownership, or required delays.

## Dependencies And Integration Points

This header must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h`, which supplies matching field shifts and masks. Offset/mask drift can compile successfully while causing masked reads or writes to target the wrong hardware register or bit fields.

The direct source include site found for this DCN 3.2.1 offset header is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`

Important integration points visible from that resource code include:

- `BASE(seg)`, `SR`, `SR_ARR`, `SRI`, `SRI_ARR`, `SR_ARR_I2C`, and `SRI_ARR_I2C`, which combine the generated `_BASE_IDX` and offset macros into concrete register table values.
- `dcn321_aux_engine_create()`, which instantiates five AUX engines using AUX register lists that map to `regDP_AUX0_*` through `regDP_AUX4_*`.
- `dcn321_i2c_hw_create()`, which instantiates five I2C hardware engines using DOUT I2C register constants.
- `dcn321_vpg_create()`, which initializes VPG instances 0-9. This chunk includes complete VPG0-VPG8 register offsets and the beginning of VPG9.
- `dcn321_afmt_create()`, which initializes AFMT instances 0-5. The chunk contains AFMT0-AFMT5 register-offset blocks.
- `dcn321_apg_create()`, which initializes APG0-APG3 for HPO DP audio packet generation.
- `dcn321_stream_encoder_create()`, which maps DIO engine IDs to VPG/AFMT/DIG register blocks and constructs DCN32 DIO stream encoders.
- `dcn321_hpo_dp_stream_encoder_create()`, which maps `ENGINE_ID_HPO_DP_0..3` to HPO stream encoder instances, VPG instances 6-9, and APG instances 0-3.
- `dcn321_dsc_create()`, which instantiates DSC0-DSC3 from the DSCC, DSCCIF, and DSC_TOP register families in this chunk.
- DCIO/link encoder construction and GPIO/pad translation paths, which consume DCIO, UNIPHY, HPD, AUX/I2C pad, backlight, and panel power-sequence register constants through shared DCN32/DCN321 helpers.

Functional dependencies include the AMDGPU register-helper layer, Display Core resource construction, DIO and HPO stream encoder implementations, AUX/I2C sideband engines, DCN32 DSC support, DCIO GPIO/pad helpers, panel/backlight control, and the hardware register database that generated this file.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong offset or `_BASE_IDX` can compile cleanly but direct MMIO reads/writes to the wrong display register.
- This chunk is not a standalone logical unit. It starts in the middle of the `DIG4` HDMI/TMDS block and ends in the middle of `VPG9`; merge/reconciliation must combine adjacent chunks for complete per-file coverage.
- Instance numbering is dense and easy to mis-map. DIO VPG/AFMT/DME instances 0-4, HPO HDMI instance 5, HPO DP VPG instances 6-9, APG instances 0-3, and DP SYM32 instances 0-2 in this range are related but not interchangeable.
- The HPO DP stream encoder mapping is asymmetric: HPO DP stream encoder `n` uses VPG `n + 6` and APG `n`. A correct-looking VPG macro from the wrong instance can send SDP/metadata/audio packet state to the wrong HPO stream.
- All visible base indices are `2`, but resource code still depends on `_BASE_IDX` macros. If a future generated file changes base-index assignment, hardcoded assumptions would break.
- AUX and I2C registers include transaction FIFOs, arbitration, reply, timeout, interrupt, and status registers. Writing a status or FIFO offset as though it were ordinary configuration can lose sideband transactions or mask hotplug/DDC failures.
- DCIO/UNIPHY blocks expose many reserved macro-control registers. Reserved or opaque registers should not be used without hardware documentation, even when generated offsets exist.
- Power and memory-power registers appear across AFMT, VPG, APG, DP SYM32, DIO, DCIO, DSC, and panel blocks. Incorrect programming can cause failures that only reproduce across display hotplug, suspend/resume, PSR/panel replay, backlight transitions, or clock/power gating.
- DSC rate-control and picture/slice offsets are highly parameter-sensitive. Offset drift can produce link-visible corruption rather than an immediate kernel failure.
- Status, interrupt, clear, control, data, and debug registers are indistinguishable at the preprocessor level. Callers need field masks and hardware access-type knowledge before writing to them.

## Test Signals

Useful validation for changes touching this chunk includes:

- Build AMDGPU Display Core with DCN321 support enabled. Missing or renamed generated macros should surface in `dcn321_resource.c` and the shared DIO/HPO/DSC/AUX/I2C register-list expansion paths.
- Mechanically compare lines 10193-12823 against the authoritative AMD register database or a regenerated `dcn_3_2_1_offset.h`. Every visible register macro should have the expected offset and exactly one matching `_BASE_IDX`.
- Cross-check corresponding field definitions in `dcn_3_2_1_sh_mask.h` for AFMT, VPG, APG, AUX, I2C, DCIO, PWRSEQ, DSCC, DP_STREAM_ENC, and DP_SYM32 register names.
- On DCN321 hardware, exercise DIO HDMI/TMDS and DP outputs across modesets, hotplug, audio enable/disable, infoframe/metadata updates, and suspend/resume.
- Exercise DP AUX and DDC/EDID paths on all five AUX/I2C instances. Monitor AUX reply/data/status registers, I2C arbitration, DDC detection, EDID detection, and interrupt behavior.
- Validate HPO DP stream encoder paths for all four HPO DP engines, paying special attention to the VPG6-VPG9 and APG0-APG3 instance mapping.
- Test DSC enablement across multiple streams and slice/rate-control configurations. Register dumps should show DSCC0-DSCC3 and DSCCIF/DSC_TOP offsets matching the selected instance.
- Test panel power and backlight sequences, including suspend/resume and blank/unblank, because PWRSEQ, BL PWM, BLON, and panel status registers in this chunk affect user-visible display bring-up.
- Use register dumps before and after modeset, link retrain, audio packet update, DSC programming, HPO stream mapping, and power transitions. Writes should land in the intended instance, reserved registers should remain stable, and memory-power/status bits should behave consistently with hardware documentation.

## Cross-Chunk Notes

The final per-file report should merge this chunk with the previous chunk for the complete `DIG4` HDMI/TMDS block and with the following chunk for the rest of `VPG9` plus `DP_SYM32_ENC3` and later DCN321 offset definitions. This document is intentionally limited to the assigned source range and should be treated as the source-tree-aligned chunk artifact for `subset-b-002025`.
