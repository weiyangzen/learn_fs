# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h lines 10229-12818

## Purpose

This chunk is generated AMD DCN 3.1.5 display-controller register metadata. It is a C preprocessor offset header: each `reg...` macro names a hardware MMIO register offset, and each matching `reg..._BASE_IDX` macro selects the DCN base segment used to form the final address. The companion `dcn_3_1_5_sh_mask.h` header supplies field shifts and masks; this file supplies the register addresses consumed by AMDGPU display resource construction, GPIO/AUX/DDC helpers, IRQ setup, DMUB register access, link and stream encoders, panel control, DSC, and diagnostics.

Although the source path is under a local `ceph-client` mirror, this chunk is AMDGPU display-driver hardware metadata and has no distributed filesystem or Ceph behavior.

The requested range contains 2,378 `#define` lines: 1,189 register-offset macros and 1,189 `_BASE_IDX` macros. The equal count hides two artificial chunk-boundary splits: line 10229 starts with `regDIG2_HDMI_DB_CONTROL_BASE_IDX` while the corresponding offset is on line 10228, and line 12818 contains `regDME5_DME_CONTROL` while its `_BASE_IDX` is on line 12819.

## Register Blocks Covered

The chunk begins in the middle of the `DIG2` stream-encoder register block. It includes the base-index half of `DIG2_HDMI_DB_CONTROL`, then the rest of the DIG2 HDMI audio-clock-regeneration/status, AFMT top control, DIG backend control, TMDS, DIG version, and force-disable offsets.

It then covers full DisplayPort and DIG stream-encoder instances for `DP3`/`DIG3` and `DP4`/`DIG4`. The DP blocks include link control, pixel format, MSA colorimetry and timing, video stream control, DPHY controls, training pattern selection, symbols, 8b/10b, PRBS, scrambler, CRC, fast training, secondary-data packet/audio timing, MST/MSE scheduling, MSO, DSC handoff, metadata packet controls, DSC bytes-per-pixel, ALPM, GSP packet controls, and double-buffer status. The DIG blocks include front-end/backend controls, output CRC, clock/test/random pattern registers, FIFO/status, HDMI metadata and audio controls, infoframe and generic-packet controls, ACR programming for 32/44/48 kHz families, AFMT control, TMDS patterns/control characters/DC balance, version, and forced-disable.

The slice includes `AFMT0` through `AFMT5` audio-format blocks. `AFMT0` to `AFMT4` correspond to the legacy DIG instances, while `AFMT5` is under `dce_dc_hpo_hdmi_stream_enc0_afmt_afmt_dispdec`. These offsets cover VBI packet control, audio packet control, audio info registers, IEC 60958 channel-status registers, audio CRC, ramp controls, AFMT status, infoframe control, audio source control, and AFMT memory power.

It includes legacy `DME0` through `DME4` control offsets and `VPG0` through `VPG4` metadata/generic-packet blocks. The DME blocks are one control register per DIG instance in this range. The VPG blocks include generic packet access/data, frame-update control, immediate-update control, generic status, memory power, ISRC access/data, MPEG info, and SMU generic-packet status registers. The range also starts the HPO HDMI `DME5` block with `regDME5_DME_CONTROL`, but its base-index and memory-control lines are in the following chunk.

The `DP_AUX0` through `DP_AUX4` blocks provide per-channel AUX engine offsets for DisplayPort AUX/DDC-over-AUX transactions. Each includes AUX control, software control, arbitration, interrupt control, software/link-service status and data, DPHY TX/RX controls and status, GTC sync controls/status, and PHY wake control.

The shared DOUT I2C block provides display DDC/I2C controller offsets, including arbitration, control, interrupt, software status, DDC1 through DDC5 hardware status/speed/setup, transaction descriptors, data, EDID detect control, and read-request interrupt state.

The DIO miscellaneous block includes DIO scratch registers, memory-power status/control, clock controls, power-management control, DIG soft reset, HDMI RX-status timer control, generic interrupt message/clear, and link-type controls for DIO links A through F. The adjacent DIO perfmon block defines `DC_PERFMON18` counter-control, state, value, and high/low readback offsets.

The shared DCIO block exposes top-level display I/O controls: generic registers, clock/reference-clock controls, UNIPHY A through E link and channel crossbar controls, write-command delay, pinstraps, intercept state, BL PWM frame-start display select, genlock/swaplock pad controls, and DCIO soft reset. The DCIO-chip block exposes GPIO/pad registers for generic GPIO, DDC1 through DDC5, DDCVGA, genlock, HPD, panel power-sequence enables, pad strengths, AUX controls, TX/RX enables, pullups, PHY AUX control, and AUX/I2C pad power-good status.

The `UNIPHY0` through `UNIPHY4` address blocks publish `DCIO_UNIPHYx_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED57`. The generated names intentionally do not describe individual PHY-control semantics; they provide stable addresses for per-PHY macro slots used by low-level PHY programming, debug, dumps, or silicon bring-up.

The `PWRSEQ0` and `PWRSEQ1` blocks cover panel power sequencing and backlight PWM. They include power-sequence GPIO controls, panel sequence control/state/delays/reference dividers, backlight PWM control/control2/period, PWM group-register lock, second reference divider, and spare state.

The `DSCC0`, `DSCC1`, and `DSCC2` blocks provide Display Stream Compression compressor offsets, including config/status, interrupt-control/status, PPS config 0 through 22, memory-power control, squared-error readbacks, max-absolute-error readbacks, rate-buffer fullness, rate-control-buffer fullness, and debug-bus rotate. The matching `DSCCIF0` through `DSCCIF2` blocks provide input-interface config offsets, `DSC_TOP0` through `DSC_TOP2` provide top-level DSC control/debug offsets, and `DC_PERFMON19` through `DC_PERFMON21` provide DSC perfmon register sets.

The final complete HPO-related blocks in this chunk are `HPO_TOP`, `DP_STREAM_MAPPER`, and HPO perfmon `DC_PERFMON22`. `HPO_TOP` provides top-level HPO clock and hardware control. `DP_STREAM_MAPPER_CONTROL0` through `CONTROL3` are shared by HPO DP stream encoders to route stream data to HPO links. `DC_PERFMON22` provides HPO performance-counter control and readback.

## Important APIs, Types, And Macros

This header has no functions, structs, enums, variables, includes, locks, allocations, or direct persistence APIs in this range. Its API is the generated macro naming contract:

- `reg<INSTANCE>_<REGISTER>` gives a register offset.
- `reg<INSTANCE>_<REGISTER>_BASE_IDX` gives the base segment index used by `BASE(...)`.
- Address-block comments identify the generated hardware block and its local base address.
- Instance prefixes such as `DP3`, `DIG4`, `AFMT5`, `DP_AUX2`, `DSCC1`, `PWRSEQ0`, and `DC_PERFMON22` are part of the public register-table contract.

The main include sites for this exact DCN315 header in this tree are:

- `display/dc/resource/dcn315/dcn315_resource.c`
- `display/dc/irq/dcn315/irq_service_dcn315.c`
- `display/dc/gpio/dcn315/hw_factory_dcn315.c`
- `display/dc/gpio/dcn315/hw_translate_dcn315.c`
- `display/dmub/src/dmub_dcn315.c`

`dcn315_resource.c` expands these offsets into static register tables. For this chunk, important table macros include `VPG_DCN31_REG_LIST(id)`, `AFMT_DCN31_REG_LIST(id)`, stream-encoder register lists, `DCN2_AUX_REG_LIST(id)`, `LE_DCN31_REG_LIST(id)`, `UNIPHY_DCN2_REG_LIST(phyid)`, `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST(id)`, HPO link-encoder register lists, and `DSC_REG_LIST_DCN20(id)`. The generated offsets are bound to block constructors such as VPG, AFMT, AUX, link encoder, stream encoder, HPO stream/link encoder, and `dsc2_construct()`.

`dcn31_afmt.h` consumes the AFMT offsets through `AFMT_DCN31_REG_LIST(id)`, selecting address macros such as `AFMTx_AFMT_INFOFRAME_CONTROL0`, `AFMTx_AFMT_AUDIO_PACKET_CONTROL`, `AFMTx_AFMT_AUDIO_SRC_CONTROL`, `AFMTx_AFMT_60958_0/1/2`, and `AFMTx_AFMT_MEM_PWR`. The fields are taken from instance-0 names in the sh/mask header, while these offset macros select the per-instance MMIO addresses.

`dcn31_vpg.h` consumes VPG offsets through `VPG_DCN31_REG_LIST(id)`, selecting generic-packet status/access/data/update and memory-power registers. HPO stream creation in `dcn315_resource.c` maps HPO DP stream encoders to VPG instances beyond the legacy DIG instances, so instance ordering in the generated VPG/AFMT/DME namespace is a real runtime contract.

`dcn20_dsc.h` defines `DSC_REG_LIST_DCN20(id)`, which uses the DSCC, DSCCIF, and DSC_TOP offsets from this chunk. DCN315 resource construction creates three DSC instances with `dsc2_construct(dsc, ctx, inst, &dsc_regs[inst], &dsc_shift, &dsc_mask)`, so the DSCC0/1/2 offsets are the address layer for the generic DCN20 DSC implementation on DCN 3.1.5 hardware.

`dcn301_panel_cntl.h` defines the panel-control register-list pattern for `PANEL_PWRSEQx_*` and `BL_PWMx_*` registers. The PWRSEQ offsets in this chunk are the DCN315 address surface for embedded-panel power sequencing and backlight PWM programming.

`dcn31_hpo_dp_stream_encoder.h` consumes the HPO DP stream mapper offsets with `SR(DP_STREAM_MAPPER_CONTROL0)` through `CONTROL3`, and per-HPO stream encoder offsets in later chunks. In this range, the stream mapper registers are the shared routing controls that connect HPO stream encoders to HPO links.

`dmub_dcn315.c` includes this header and computes register offsets with `REG_OFFSET_EXP(reg_name)`, which expands to `BASE(reg##reg_name##_BASE_IDX) + reg##reg_name`. Only the subset named by DMUB register-list macros is used there, but DMUB participates in the same generated DCN315 address namespace.

`irq_service_dcn315.c` includes this header and its sh/mask companion for interrupt-source address and field metadata. GPIO factory/translate code includes the header for HPD, DDC, generic GPIO, and related DCIO-chip register mappings.

## Control Flow

This chunk has no runtime control flow. It is pure macro data. Runtime control flow is table driven:

1. DCN315 resource, IRQ, GPIO, and DMUB code include `dcn_3_1_5_offset.h` and `dcn_3_1_5_sh_mask.h`.
2. Register-list helper macros such as `SR`, `SRI`, `SRIR`, and `SRII` paste instance IDs into generated macro names.
3. Static register tables store resolved offsets for VPG, AFMT, stream encoders, AUX engines, link encoders, HPO encoders, DSC, panel control, GPIO, IRQ, and DMUB-visible blocks.
4. Runtime block code uses those tables with register helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and DMUB register-access macros.

The header does not encode sequencing rules. Driver code and hardware documentation must supply ordering for DP link training, AUX transactions, HDMI/AFMT packet updates, DME/VPG metadata programming, panel power sequencing, DSC PPS setup, HPO stream/link mapping, clock/power gating, interrupt acknowledgement, and perfmon control.

## State And Persistence Behavior

The file stores no software state and persists nothing on disk. It describes MMIO-backed hardware state in DCN 3.1.5 display blocks.

Configuration state represented by this chunk includes DP link and DPHY programming, DIG/HDMI/TMDS stream-encoder setup, AFMT audio packet setup, DME and VPG metadata packet setup, AUX DPHY timing and arbitration, DOUT I2C/DDC setup, DIO clock/reset/memory-power controls, DCIO link and pin routing, GPIO/HPD/DDC/AUX pad controls, UNIPHY macro slots, panel power and backlight PWM timing, DSC PPS/config/memory power, HPO top controls, and HPO stream mapping.

Live status and telemetry represented by this chunk includes DP CRC/training/MSE status, DIG output CRC and FIFO/status state, AFMT status and CRC results, VPG generic-packet conflict/status bits, AUX software/link-service/DPHY/GTC status, DDC/I2C hardware and software status, DIO memory-power status, DCIO pad/power-good state, panel power-sequence current/target state, DSCC status/interrupt/error/fullness counters, and perfmon counter state/readbacks.

Persistence is hardware-defined. Some registers remain programmed until modeset, suspend/resume restore, power gating, block reset, or ASIC reset. Others are read-only status, sticky status, write-one-to-clear interrupt/status, self-clearing request, indexed-window data, double-buffered packet state, or counter readback. The offset header alone does not distinguish those access classes.

## Dependencies And Integration Points

The highest-impact dependency is synchronization with `dcn_3_1_5_sh_mask.h`. Register tables combine offsets from this file with fields from the sh/mask header. A stale offset with a valid field mask can compile while programming the wrong register or interpreting the wrong status bit.

The DCN315 resource path is the primary integration point. `dcn315_resource.c` builds arrays for VPG instances 0 through 9, AFMT instances 0 through 5, stream encoders 0 through 4, AUX engines 0 through 4, link encoders, HPO stream encoders, HPO link encoders, and DSC instances 0 through 2. This chunk supplies a large portion of those address surfaces, especially for legacy DIO, DCIO, PWRSEQ, DSC, HPO top/mapper, and HPO HDMI AFMT.

The GPIO path integrates the DCIO-chip DDC, HPD, AUX, generic GPIO, PWRSEQ enable, pad strength, pullup, TX/RX enable, and power-good offsets. These addresses are used for connector detection, hotplug routing, DDC line control, AUX pad state, and panel-related GPIO behavior.

The AUX and DOUT I2C paths integrate with EDID reads, DisplayPort link training, DisplayPort sideband/AUX transactions, I2C-over-AUX behavior, and legacy DDC. AUX registers are per-channel; DOUT I2C provides a shared controller with per-DDC speed/setup/status registers.

The link and stream encoder paths integrate DP, DIG, AFMT, DME, VPG, DCIO, and UNIPHY offsets with VBIOS connector data and runtime engine allocation. A single connector path can involve a DIG stream encoder, DP link block, AUX channel, DCIO UNIPHY/link/xbar controls, HPD GPIOs, AFMT audio block, VPG/DME metadata block, and possibly DSC or PWRSEQ state.

The panel-control path integrates `PWRSEQ0`/`PWRSEQ1` and `BL_PWM0`/`BL_PWM1` offsets with embedded-panel power and backlight operations. The field-level code lives in the panel-control implementation, but this chunk provides the DCN315 addresses for target/current state, DIGON/BLON, PWM enable, period, fractional count, lock, and reference-divider programming.

The DSC path integrates DSCC/DSCCIF/DSC_TOP offsets with Display Mode Library decisions and the generic DCN20 DSC hardware implementation. Higher layers decide whether DSC is needed and calculate PPS values; the register tables from this chunk are what allow the implementation to program PPS/config/status/memory-power and read compression diagnostics.

The HPO path integrates `HPO_TOP` and `DP_STREAM_MAPPER_CONTROL0-3` with HPO DP stream/link encoders. DCN315 advertises HPO DP capability in resource setup, and HPO stream creation maps stream encoders, VPG/APG metadata/audio resources, and stream-mapper controls together.

The DMUB path integrates generated offsets into firmware service register access. `dmub_dcn315.c` maps DCN315 register names to `struct dmub_srv_dcn31_regs`; common DCN31 DMUB operations then use those addresses for reset, firmware windows, mailboxes, GPINT, diagnostics, and timing.

The IRQ path integrates generated offsets and masks into DCN315 interrupt-service tables. AUX/DDC, HPD, DIO, DSC, perfmon, or related display events depend on the offset/mask namespace matching the silicon register map.

## Risks And Edge Cases

Generated-header drift is the main risk. A wrong offset or base index can compile cleanly but point register helpers at the wrong MMIO address. In this chunk, likely symptoms include DP link-training failures, AUX/DDC timeouts, wrong connector hotplug state, HDMI audio or infoframe breakage, metadata packet corruption, panel power/backlight failures, DSC enable failures, HPO stream-routing failures, or misleading diagnostics.

Instance ordering is fragile. `DP3`/`DP4`, `DIG3`/`DIG4`, `AFMT0-5`, `VPG0-4`, `AUX0-4`, `UNIPHY0-4`, `PWRSEQ0-1`, `DSCC0-2`, and HPO resources are assembled into arrays and selected by engine IDs, channel IDs, transmitter IDs, or instance arithmetic. An off-by-one mapping can target a different physical connector or encoder while all macro names remain valid.

The range starts and ends at split definitions. The previous chunk owns the offset for `DIG2_HDMI_DB_CONTROL`; this chunk owns its `_BASE_IDX`. This chunk owns the offset for `DME5_DME_CONTROL`; the next chunk owns its `_BASE_IDX` and `DME5_DME_MEMORY_CONTROL`. File-level reconciliation must merge adjacent chunks before claiming complete coverage of those registers.

UNIPHY reserved registers are intentionally opaque. The `RESERVED0` through `RESERVED57` names should be treated as address-window coverage, not self-documenting behavior. Over-interpreting those names in tests or documentation can lead to incorrect claims.

DP/AUX programming is timing-sensitive. AUX arbitration, DPHY timing, wake controls, interrupt/status handling, and DP training controls can fail due to stale status, incorrect clear semantics, power-state changes, or wrong channel routing. Offset errors here often appear as timeouts rather than clear software faults.

HDMI/AFMT/VPG/DME programming is stateful and often double-buffered or update-triggered. Wrong packet, infoframe, audio-source, channel-status, DME, or generic-packet offsets can cause silent audio loss, incorrect infoframes, HDR/metadata failure, or compliance failures without a kernel crash.

Panel PWRSEQ and BL PWM offsets are high risk because bad writes can produce black screen, flicker, long delays, or unsafe embedded-panel sequencing. The target/current-state readbacks must be interpreted with the right instance and timing.

DSC offsets are high impact for high-bandwidth modes. PPS/config mismatch, memory-power mistakes, or wrong DSCCIF/DSC_TOP addresses can make modes fail only when compression is required, and error/fullness counters can become misleading if read from the wrong instance.

HPO stream-mapper offsets affect DP 2.x style routing. Incorrect HPO top or stream-mapper addresses can map the stream to the wrong link target or prevent HPO stream encoder activation, especially because HPO stream and link resources are allocated separately.

## Test Signals

Useful validation starts with build coverage. A DCN315-enabled AMDGPU build should catch missing or renamed macros in `dcn315_resource.c`, `irq_service_dcn315.c`, `hw_factory_dcn315.c`, `hw_translate_dcn315.c`, and `dmub_dcn315.c`.

Generated-header consistency checks should verify that every register offset has a matching `_BASE_IDX`, allowing the known boundary exceptions at `DIG2_HDMI_DB_CONTROL` and `DME5_DME_CONTROL`. Checks should also compare offsets and base indexes against AMD's authoritative DCN 3.1.5 register database and adjacent generated DCN 3.1.x headers where instances are expected to match.

Runtime display validation should exercise DP and HDMI modes on all covered DIG/DP/AUX channels, including link training, EDID reads, HPD, DDC fallback, audio packet generation, HDMI infoframes, output CRC, compliance patterns, and suspend/resume restore.

AUX/DDC validation should include AUX native transactions, I2C-over-AUX, legacy DDC reads on DDC1 through DDC5, arbitration conflict handling, interrupt clear behavior, wake/power transitions, and error paths that expose stale or misrouted status.

Panel validation should exercise eDP or embedded-panel power sequencing, DIGON/BLON transitions, backlight PWM period and fractional brightness programming, register-lock/update-pending behavior, and suspend/resume or backlight restore.

DSC validation should enable compressed modes on DSC instances 0 through 2, verify PPS programming, DSCCIF/top enablement, memory-power transitions, interrupt/status behavior, squared-error and max-abs-error readbacks, and rate-buffer/fullness counters.

HPO validation should exercise HPO DP stream allocation, stream mapper target selection, HPO top clock/hardware control, HPO perfmon counters, and mixed legacy/HPO resource use.

Diagnostic validation should read DIO, DSC, and HPO perfmon counters; DIO scratch/memory-power state; AFMT/VPG status; AUX status; and DSCC error/fullness counters to confirm that register tables point at the expected hardware instances.

## Cross-Chunk Notes

The previous chunk must be consulted for the `regDIG2_HDMI_DB_CONTROL` offset paired with the first line of this range. The next chunk must be consulted for `regDME5_DME_CONTROL_BASE_IDX` and the rest of the HPO HDMI DME5 block. The final per-file research document should merge those boundaries before making complete claims about DIG2 HDMI DB control or HPO HDMI DME5 coverage.
