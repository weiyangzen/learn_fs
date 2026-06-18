# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h lines 10256-12835

## Purpose

This chunk is a generated AMD DCN 3.6.0 register-offset header slice. It contains preprocessor constants for display-controller MMIO offsets and the associated `_BASE_IDX` selector used by AMDGPU display register helpers. It has no executable C logic, but it is part of the ABI between the generated ASIC register database and DCN36 display code.

The requested range contains 2,381 `#define` lines: 1,191 register-offset macros and 1,190 `_BASE_IDX` macros. Every `_BASE_IDX` value in this slice is `2`, so consumers resolve these registers through `ctx->dcn_reg_offsets[2]` before adding the generated offset. The slice starts inside the DP2 block, then covers DIG2/DIG3/DIG4, AFMT/DME/VPG packet blocks for DIG0-DIG4, AUX0-AUX4, DPIA mux controls, DIO/I2C/misc/perfmon/DCIO/UNIPHY metadata, PWRSEQ0/PWRSEQ1, and the beginning of DSC/DSCC instances 0-2.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocation paths, or runtime APIs in this chunk. The exported interface is the generated macro namespace:

- `reg<REGISTER_OR_BLOCKED_REGISTER>` gives a numeric MMIO offset.
- `reg<REGISTER_OR_BLOCKED_REGISTER>_BASE_IDX` gives the DCN base-address-array index used when constructing a final address.
- No `ix...` indexed-register macros appear in this range.

Important register families in this slice:

- DP2 tail: `regDP2_*` exposes late DisplayPort encoder/PHY controls including DPHY fast-training/CRC status, secondary-data-packet controls, audio M/N readback, MSE rate/SAT controls and status, MSA timing, MSO, DSC control, ALPM/auxless ALPM, generic SDP enable/status, and stream/link symbol counters.
- DIG2-DIG4: each DIG front-end block exposes `DIG_FE_*`, output CRC, clock/test/random pattern, FIFO, HDMI metadata/control/status/audio/ACR/VBI/infoframe/generic packet/GC/DB controls, TMDS controls, DP video/config/pixel/link/steer/security/DPHY/CRC/MST/MSE/MSA/MSO/DSC/ALPM registers, and DIG back-end controls.
- AFMT0-AFMT4: audio formatter and packet registers cover `AFMT_CNTL`, memory power, audio source/dto/crc/infoframe, 60958 channel status words, VBI/ACP/audio packet controls, interrupt controls, ramp controls, and status.
- DME0-DME4 and VPG0-VPG4: metadata engine controls/memory and video packet generator memory, generic packet, GSP, MPEG, and ISRC controls.
- AUX0-AUX4: DP AUX control, arbitration, software data, LS status, GTC sync, DPHY RX/TX/ref/timer/status/debug registers, interrupt controls, and AUX PHY control.
- DPIA mux and DIO shared blocks: `DPIA_MUX0-3_*`, DIO I2C/DDC controls and status, DIO scratch registers, ALPM wake interrupt status, memory-power status/control, clock control, power management, HDMI RX-status timer, PSP interrupt status/clear, link A-F controls, stream mapper controls, and `DC_PERFMON18`.
- DCIO and GPIO/chip registers: generic DCIO controls, reference/clock controls, UNIPHY A-E link/channel crossbar controls, pinstraps, pattern generator, backlight PWM display select, GSL/genlock/swaplock pad controls, soft reset, DDC/generic GPIO controls, HPD pads, AUX PHY control, and four UNIPHY macro reserved register ranges.
- PWRSEQ0/PWRSEQ1: panel power sequencing GPIO, sequence control/state/delay/reference-divider registers, backlight PWM controls/period/lock, and spare registers.
- DSC/DSCC start: `DSCC0` and `DSCC1` are complete in this chunk, with config/status/interrupt, PPS config 0-22, memory power, squared-error counters, max absolute error counters, rate-buffer fullness, rate-control fullness, and debug-bus rotation registers. `DSCCIF0/1`, `DSC_TOP0/1`, and `DC_PERFMON19/20` are also complete. `DSCC2` begins at the end of the chunk and continues in the next chunk.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from AMDGPU display code that includes this generated metadata:

1. DCN36 resource, IRQ, and DMUB code include `dcn_3_6_0_offset.h` with `dcn_3_6_0_sh_mask.h`.
2. Register-list macros in display block headers token-paste names such as `regDIG2_DIG_FE_CNTL`, `regDP_AUX2_AUX_CONTROL`, `regAFMT3_AFMT_AUDIO_PACKET_CONTROL`, or `regDSCC1_DSCC_PPS_CONFIG0`.
3. Address-construction helpers add the relevant base address, for example `BASE(reg..._BASE_IDX) + reg...`, where `BASE_INNER(seg)` expands to `ctx->dcn_reg_offsets[seg]`.
4. DCN36 resource construction fills static register tables for DIO, link encoders, stream encoders, audio, VPG/AFMT/DME sub-blocks, AUX/I2C, DSC engines, hardware sequencing, IRQ service, and DMUB-facing tables.
5. Runtime hardware objects then access these addresses through register helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, AUX helpers, stream-encoder helpers, audio helpers, DSC helpers, IRQ helpers, and DMUB register access.

The macros do not encode sequencing. Consumers still have to order DP link training, HDMI/DP packet programming, audio setup, DME/VPG metadata updates, AUX transactions, I2C/DDC transfers, HPD/PSP interrupt handling, UNIPHY/DCIO routing, panel power/backlight sequencing, DSC PPS programming, DSC power transitions, CRC/perf counter reads, and soft-reset or clock/power transitions correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It names hardware registers whose state is owned by DCN 3.6.0 display blocks:

- DP/DIG state includes stream encoder setup, HDMI packet/audio/infoframe state, TMDS controls, DP training/test/CRC/debug state, MST/MSE scheduling state, MSA/MSO/DSC controls, ALPM controls, and stream/link symbol counters.
- AFMT/DME/VPG state includes audio formatter configuration, metadata packet memory, generic SDP/GSP/MPEG/ISRC packet controls, and interrupt state.
- AUX/I2C/DIO state includes AUX transaction control/status/data, DPHY analog/digital controls, DDC speed/setup/transaction/data registers, DIO memory-power and clock state, stream mapping, link routing, and interrupt/status registers.
- DCIO/UNIPHY state includes physical link routing, channel crossbars, GPIO/HPD/DDC pad state, PHY AUX controls, soft reset, pattern generation, backlight PWM display selection, and reserved macro control storage.
- PWRSEQ state includes panel GPIO configuration, panel power sequencing delays and state, PWM backlight period/duty/control, and PWM lock state.
- DSC state includes compressor config, PPS payload programming, memory power, status/interrupt state, error counters, rate-buffer/fullness telemetry, and perfmon counters.

Persistence is hardware-defined. Configuration values generally remain until a modeset, link retrain, panel power transition, DSC reconfiguration, power-gate cycle, suspend/resume, driver reset, or ASIC reset. Status, interrupt, CRC, perfmon, error, overflow, and debug registers may be read-only, sticky, self-clearing, write-one-to-clear, or only meaningful while the corresponding block is powered and clocked. This offset header does not describe those access semantics.

## Dependencies And Integration Points

This generated header must remain synchronized with AMD's DCN 3.6.0 register database and with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h`, which provides field shifts and masks for the same symbolic register names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c`, which includes this header and constructs DCN36 register tables with token-pasting helpers such as `SR`, `SRI`, `SRI_ARR`, `SR_ARR_I2C`, and `SRI_ARR_ALPHABET`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c`, where `dmub_srv_dcn36_regs_init()` resolves generated offsets through `REG_OFFSET_EXP(reg_name)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c`, which uses the same offset/shift/mask model for DCN36 interrupt source tables.
- DIO/link/stream/audio helper modules such as `dcn35_dio_stream_encoder`, `dcn35_dio_link_encoder`, `dcn31_dio_link_encoder`, `dce_audio`, `dce_aux`, `dce_i2c`, `dcn30_vpg`, `dcn31_vpg`, `dcn31_afmt`, and `dcn35_dsc`.

Direct local integration visible in `dcn36_resource.c` includes:

- `audio_regs_init(id)` for five exposed audio/AFMT instances plus additional audio table entries.
- `VPG_DCN31_REG_LIST_RI(id)` and `AFMT_DCN31_REG_LIST_RI(id)` for VPG and AFMT sub-blocks used by stream encoders and HPO stream encoders.
- `stream_enc_regs_init(id)` for five DIG stream encoder instances.
- `DCN2_AUX_REG_LIST_RI(id)` and AUX/I2C register-list macros for five AUX/DDC engines.
- `UNIPHY_DCN2_REG_LIST_RI(id, phyid)` for five digital link encoders backed by UNIPHY/DCIO controls.
- `DIO_REG_LIST_DCN10()` and `DIO_MASK_SH_LIST()` for shared DIO memory-power and clock controls.
- `DSC_REG_LIST_DCN20_RI(id)` and `DSC_REG_LIST_SH_MASK_DCN35()` for four DSC engines; this chunk fully covers DSC0 and DSC1 register names and starts DSC2.

## Risks And Edge Cases

- The constants are untyped preprocessor values. A wrong offset or `_BASE_IDX` can compile cleanly and route MMIO to the wrong block, wrong instance, or wrong address space.
- The chunk boundary is artificial. It starts in the middle of the DP2 register family and ends in the middle of `DSCC2`; adjacent chunks are required for whole-block conclusions.
- All base indices in this chunk are `2`. A single accidental base-index change would silently move an otherwise plausible register offset into a different DCN base segment.
- Repeated instance families are copy-sensitive. DIG2-DIG4, AFMT0-AFMT4, DME0-DME4, VPG0-VPG4, AUX0-AUX4, PWRSEQ0-1, UNIPHY1-4 reserved ranges, and DSCC0-2 use very similar macro names with different offsets.
- DIG/DP registers are central to link bring-up. Misaddressing can break DP training, MST/MSE allocation, DSC-over-DP enablement, ALPM, HDMI packet emission, TMDS setup, CRC diagnostics, or symbol counter reads.
- AFMT/DME/VPG mistakes can produce missing or stale audio, HDR/static metadata, MPEG/ISRC data, or generic SDP packets. These may present as sink-specific failures rather than immediate driver errors.
- AUX/I2C offsets are high-risk because they affect HPD/EDID/DPCD access, link training sideband transactions, LTTPR discovery, backlight control over AUX, and sink capability reads.
- DIO/DCIO/UNIPHY/link control mistakes can swap or disable physical links, misroute streams, mishandle HPD/DDC GPIO, or leave PHY/pad state inconsistent across suspend/resume.
- PWRSEQ and PWM registers are user-visible and timing-sensitive. Bad offsets can cause dark panels, flicker, incorrect brightness, or broken panel power sequencing.
- DSC offsets are field- and sequence-sensitive. Bad PPS/config/memory-power/status offsets can cause compressed-link corruption, blanking, link retraining failures, or misleading error/perf telemetry.
- Reserved UNIPHY macro registers should be treated as generated hardware metadata. Consumers should not infer semantics from their names without the ASIC programming guide.

## Test Signals

Useful validation combines generated-header consistency with DCN36 hardware behavior:

- Build AMDGPU display code with DCN36 enabled. Missing or renamed macros should fail in `dcn36_resource.c`, `dmub_dcn36.c`, `irq_service_dcn36.c`, or hardware-object register-list expansion.
- Mechanically compare this range with `dcn_3_6_0_sh_mask.h` and AMD's generated register database, checking that every consumed offset macro has a matching `_BASE_IDX` macro and field definitions where needed.
- Diff equivalent blocks against adjacent ASIC headers such as `dcn_3_5_0_offset.h`, `dcn_3_5_1_offset.h`, and later DCN headers to catch accidental instance swaps or unexpected offset/base-index shifts.
- Exercise DP and HDMI outputs on DCN36 hardware: hotplug, cold boot, modeset, high-refresh modes, MST, DSC, MSO where supported, link retraining, test patterns, CRC reads, ALPM transitions, and suspend/resume.
- Exercise audio and metadata paths: HDMI/DP audio, ACR/N/M readback, infoframes, generic packets, HDR metadata, MPEG/ISRC packets, and DME/VPG memory updates.
- Exercise AUX/DDC paths: EDID reads, DPCD reads/writes, LTTPR discovery, link training transactions, I2C-over-AUX, native I2C/DDC transfers, HPD storms, and AUX timeout/error recovery.
- Exercise panel power and backlight flows on eDP systems: panel enable/disable, DPMS, brightness changes, PWM locking, backlight-over-AUX fallback, and suspend/resume.
- Exercise DSC: enable/disable across multiple formats, bpc values, refresh rates, MST cases, error-counter reads, perfmon reads, power-gating transitions, and fallback to uncompressed modes.
- Monitor kernel logs and display diagnostics for register timeout messages, failed AUX/I2C transactions, missing EDID, link training failures, blank or flickering panels, audio dropouts, bad metadata, DSC corruption, HPD/PSP interrupt issues, and resume-only failures.

## Cross-Chunk Notes

This is chunk 5 of 6 for `dcn_3_6_0_offset.h`. Earlier chunks contain the file prologue and preceding DCN36 display register blocks, including the beginning of DP2. The next chunk continues `DSCC2` and the remaining generated register-offset namespace. The final per-file research document should merge adjacent chunks before making complete claims about all DCN36 DP/DIG instances, all PWRSEQ/DSC instances, or the full DCIO/UNIPHY register surface.
