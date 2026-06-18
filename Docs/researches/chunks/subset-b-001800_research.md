# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h lines 10249-12816

## Scope And Purpose

This chunk is part of the generated AMD DCN 3.1.2 register offset header. It exports preprocessor constants that map named display-controller registers to MMIO offsets, paired with `<register>_BASE_IDX` constants. The companion `dcn_3_1_2_sh_mask.h` header supplies field shifts and masks; this offset header supplies register addresses consumed by AMD display resource construction, link/stream encoders, AUX/DDC helpers, DMUB support, IRQ tables, panel control, DSC, and diagnostic register helpers.

The requested range is a large generated block covering DCN display I/O and early DSC offsets. It starts at the tail of DIG1 TMDS/version/disable definitions, then covers DP/DIG transmitter instances 2 through 4, AFMT audio packet blocks for DIG0 through DIG4, DME and VPG metadata blocks for DIG0 through DIG4, DP AUX instances 0 through 4, the shared DOUT I2C block, DIO miscellaneous and DIO perfmon offsets, shared DCIO and GPIO/DCIO-chip offsets, UNIPHY macro reserved offsets for UNIPHY1 through UNIPHY4, two panel power-sequencer instances, DSC encoder instances 0 and 1, associated DSCCIF/top/perfmon blocks, and the beginning of DSC encoder instance 2.

There are no functions, structs, branches, loops, or direct runtime side effects in this chunk. The exported surface is generated register metadata. Runtime behavior is produced when DCN 3.1 resource code expands register-list macros into tables and later code uses `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, `AUX_REG_*`, and related helper macros against those tables.

The range has partial logical boundaries. It begins in the last few DIG1 definitions from a previous address block and ends in the middle of `dce_dc_dsc2_dispdec_dscc_dispdec`, after `regDSCC2_DSCC_RATE_BUFFER2_MAX_FULLNESS_LEVEL_BASE_IDX`. The remaining DSCC2 fullness, rate-control fullness, debug, DSCCIF2, DSC_TOP2, perfmon, and later blocks continue after this chunk.

## Register Blocks Covered

The chunk opens with three tail definitions for DIG1: `regDIG1_TMDS_CTL2_3_GEN_CNTL`, `regDIG1_DIG_VERSION`, and `regDIG1_FORCE_DIG_DISABLE`. These are the last TMDS control/version/disable offsets for the DIG1 stream-encoder block whose earlier registers are outside this range.

`dce_dc_dio_dp2_dispdec`, `dce_dc_dio_dp3_dispdec`, and `dce_dc_dio_dp4_dispdec` provide DisplayPort link offsets for DP instances 2, 3, and 4. Each repeated instance includes link control, pixel format, MSA colorimetry/misc/timing parameters, video stream control, steering FIFO, DPHY internal/control/training/symbol registers, 8b/10b and PRBS/scrambler controls, CRC controls/results, fast training, secondary-data packet/audio timestamp controls, MST/MSE rate and slot allocation registers, HBR2 pattern controls, MSO controls, DSC handoff controls, metadata transmission, DSC bytes-per-pixel, ALPM, GSP packet controls 8 through 11, and GSP double-buffer status.

`dce_dc_dio_dig2_dispdec`, `dce_dc_dio_dig3_dispdec`, and `dce_dc_dio_dig4_dispdec` provide DIG stream-encoder offsets for instances 2 through 4. Each repeated block includes front-end control, output CRC control/result, clock/test/random patterns, FIFO status, HDMI metadata/control/status, HDMI audio/ACR/VBI/infoframe/generic packet controls, HDMI GC and DB controls, ACR N/CTS programming and status for 32/44/48 kHz families, AFMT top control, DIG backend enable/control, TMDS control characters/patterns/DC balance/control-bit registers, DIG version, and force-disable.

`dce_dc_dio_dig0_afmt_afmt_dispdec` through `dce_dc_dio_dig4_afmt_afmt_dispdec` provide AFMT offsets for audio and auxiliary packet formatting per DIG instance 0 through 4. Each instance carries VBI packet control, audio packet control, packed audio info registers, IEC 60958 channel-status registers, audio CRC control/result, ramp controls, AFMT status, infoframe control, interrupt status, audio source control, and AFMT memory-power offset.

`dce_dc_dio_dig0_dme_dme_dispdec` through `dce_dc_dio_dig4_dme_dme_dispdec` provide one `DME_CONTROL` offset per DIG instance. `dce_dc_dio_dig0_vpg_vpg_dispdec` through `dce_dc_dio_dig4_vpg_vpg_dispdec` provide Video Pattern Generator and metadata-packet offsets per DIG instance: generic packet control/status, generic packet update, GSP frame update, and two SMU generic packet status registers.

`dce_dc_dio_dp_aux0_dispdec` through `dce_dc_dio_dp_aux4_dispdec` provide DP AUX channel offsets for instances 0 through 4. Each AUX block includes AUX control, software control, arbitration, interrupt control, SW/link-service status, SW/link-service data registers, DPHY TX reference/control, DPHY RX control 0/1, DPHY TX/RX status, GTC sync control/error/controller/status, and PHY wake control.

`dce_dc_dio_dout_i2c_dispdec` provides the shared display-output I2C/DDC engine offsets. It includes controller/arbitration/interrupt/SW status, DDC1 through DDC5 hardware status, per-DDC speed and setup registers, transaction descriptors 0 through 3, data, EDID-detect control, and read-request interrupt.

`dce_dc_dio_dio_misc_dispdec` provides shared DIO scratch and control offsets. It includes scratch registers 0 through 7, DIO memory-power status/control, DIO clock controls, DIO power-management control, DIG soft reset, HDMI RX-status timer control, generic interrupt message/clear, and link-type controls for DIO links A through F. `dce_dc_dio_dio_dcperfmon_dc_perfmon_dispdec` provides the DIO perfmon 18 offsets: counter control, counter state, perfmon control, threshold/current-value misc, and high/low readback.

`dce_dc_dcio_dcio_dispdec` provides shared DCIO offsets such as `DC_GENERICA/B`, `DCIO_CLOCK_CNTL`, `DC_REF_CLK_CNTL`, UNIPHYA through UNIPHYE link and channel-xbar controls, write-command delay, pinstraps, intercept state, BL PWM frame-start display selection, genlock/swaplock pad controls, and DCIO soft reset.

`dce_dc_dcio_dcio_chip_dispdec` provides GPIO and pad-control offsets used around DDC, HPD, AUX, and panel power. It includes generic GPIO mask/A/EN/Y registers, DDC1 through DDC5 and DDCVGA GPIO register sets, genlock and HPD GPIO sets, PWRSEQ0/PWRSEQ1 enables, pad strengths, PHY AUX control, TX12 enable, AUX controls 0 through 5, RX enable, pullup enable, and AUX/I2C pad power-good status.

`dce_dc_dcio_dcio_uniphy1_dispdec` through `dce_dc_dcio_dcio_uniphy4_dispdec` are repeated UNIPHY macro reserved ranges. Each instance exposes `regDCIO_UNIPHYx_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED57`, with base offsets spaced by UNIPHY instance. These are not self-describing functional registers in the generated names; they are reserved PHY macro control slots whose field meanings, if any, are handled by lower-level PHY programming or silicon documentation.

`dce_dc_pwrseq0_dispdec_pwrseq_dispdec` and `dce_dc_pwrseq1_dispdec_pwrseq_dispdec` provide panel power-sequencer offsets for two instances. Each instance includes power-sequence GPIO enable/control/mask/A/Y, panel sequence control/state/delays/reference dividers, backlight PWM control/control2/period, PWM group register lock, a second reference divider, and spare register.

`dce_dc_dsc0_dispdec_dscc_dispdec` and `dce_dc_dsc1_dispdec_dscc_dispdec` provide complete DSCC offset sets for DSC encoder instances 0 and 1. Each includes DSCC config 0/1, status, interrupt-control/status, PPS config 0 through 22, DSCC memory-power control, squared-error readbacks for R/Y, G/Cb, and B/Cr channels, maximum absolute-error registers, rate-buffer maximum-fullness registers 0 through 3, rate-control-buffer maximum-fullness registers 0 through 3, and debug bus rotate.

`dce_dc_dsc0_dispdec_dsccif_dispdec` and `dce_dc_dsc1_dispdec_dsccif_dispdec` provide DSCCIF config 0/1 offsets. `dce_dc_dsc0_dispdec_dsc_top_dispdec` and `dce_dc_dsc1_dispdec_dsc_top_dispdec` provide DSC top control and debug control offsets. `dce_dc_dsc0_dispdec_dsc_dcperfmon_dc_perfmon_dispdec` and `dce_dc_dsc1_dispdec_dsc_dcperfmon_dc_perfmon_dispdec` provide DC perfmon 19 and 20 offsets for DSC instances 0 and 1.

The final block begins `dce_dc_dsc2_dispdec_dscc_dispdec` at base address `0x2e0` and covers DSCC2 config/status/interrupt, PPS config 0 through 22, memory-power control, squared-error registers, max-absolute-error registers, and rate-buffer maximum-fullness registers 0 through 2 before the chunk ends.

## Important APIs, Types, And Macros

The important API is the generated naming contract:

- `reg<block/register>` gives the register offset in the DCN 3.1.2 address space.
- `reg<block/register>_BASE_IDX` gives the segment/base index passed through `BASE()` or register-list helper expansion.
- Address-block comments such as `// addressBlock: dce_dc_dio_dp2_dispdec` and `// base address: 0x800` delimit generated hardware blocks and help correlate offsets with hardware instances.
- Instance prefixes are part of the API: `DP2`/`DP3`/`DP4`, `DIG2`/`DIG3`/`DIG4`, `AFMT0` through `AFMT4`, `DME0` through `DME4`, `VPG0` through `VPG4`, `DP_AUX0` through `DP_AUX4`, `PWRSEQ0`/`PWRSEQ1`, `DSCC0` through the beginning of `DSCC2`, and `DC_PERFMON18` through `DC_PERFMON20`.

`display/dc/resource/dcn31/dcn31_resource.c` is the main DCN display consumer. It includes `dcn/dcn_3_1_2_offset.h` and `dcn/dcn_3_1_2_sh_mask.h`, then expands these generated offsets into static register tables. The relevant tables in or touching this chunk include `AFMT_DCN31_REG_LIST(id)`, `VPG_DCN31_REG_LIST(id)`, `APG_DCN31_REG_LIST(id)` where adjacent APG/VPG metadata paths depend on the same stream-encoder ecosystem, `SE_DCN3_REG_LIST(id)`, `DCN2_AUX_REG_LIST(id)`, `LE_DCN31_REG_LIST(id)`, `UNIPHY_DCN2_REG_LIST(phyid)`, `DPCS_DCN31_REG_LIST(id)`, and `DSC_REG_LIST_DCN20(id)`.

`display/dc/dcn31/dcn31_afmt.h` maps the AFMT register-list interface to generated names such as `AFMTx_AFMT_INFOFRAME_CONTROL0`, `AFMTx_AFMT_VBI_PACKET_CONTROL`, `AFMTx_AFMT_AUDIO_PACKET_CONTROL`, `AFMTx_AFMT_60958_0/1/2`, and `AFMTx_AFMT_MEM_PWR`. The corresponding shift/mask list uses instance-0 field names from the companion sh/mask header while per-instance addresses come from this offset header.

`display/dc/dio/dcn31/dcn31_dio_link_encoder.h` maps link-encoder register lists to this chunk's DP, DIG, DIO link, AUX, and UNIPHY offsets. `LE_DCN31_REG_LIST(id)` adds `DPx_DP_DPHY_INTERNAL_CTRL` plus shared DIO link-control offsets A through F; the DCN31 link-encoder mask list includes DP FEC fields, TMDS control bits, AUX DPHY timing fields, and HPO encoder selection fields. `UNIPHY_DCN2_REG_LIST(phyid)` binds UNIPHY link/xbar registers for transmitter routing.

`display/dc/dio/dcn30/dcn30_dio_stream_encoder.h` and related stream-encoder code consume the DIG, HDMI, TMDS, AFMT, and DME-style offsets through stream-encoder register structures. Runtime code programs HDMI infoframes/audio, audio clocking, generic packet memory, DME metadata enable/requestor/stream type, and TMDS/DP encoder behavior through these generated addresses.

`display/dc/dsc/dcn20/dcn20_dsc.h` defines `DSC_REG_LIST_DCN20(id)` and `DSC_REG_LIST_SH_MASK_DCN20(...)`. In `dcn31_resource.c`, three DSC instances are constructed using `dsc2_construct(dsc, ctx, inst, &dsc_regs[inst], &dsc_shift, &dsc_mask)`. The DSCC0/1/2 offsets in this chunk are therefore the hardware register addresses used by the generic DCN20 DSC implementation for DCN 3.1 hardware.

`display/dc/dcn301/dcn301_panel_cntl.h` and `display/dc/dcn301/dcn301_panel_cntl.c` define/use the panel-control register-list pattern for `PANEL_PWRSEQx_*` registers. DCN31 resource construction inherits the panel-control model; the offsets here are the PWRSEQ-side addresses for panel power, DIGON/BLON sequencing, reference dividers, and backlight PWM state.

`display/dmub/src/dmub_dcn31.c` also includes this header and its sh/mask companion. It uses the generated `reg...` and `reg..._BASE_IDX` symbols through `REG_OFFSET_EXP(reg_name)` to build `dmub_srv_dcn31_regs` for DMUB firmware service access. Not every register in this chunk is necessarily in the DMUB register macro list, but this file is part of the same generated DCN31 register-address namespace.

`display/dc/irq/dcn31/irq_service_dcn31.c` includes the same generated headers for DCN31 IRQ registration. IRQ sources that refer to DIO, AUX, HPD, DSC, or other generated DCN31 registers depend on the offset/mask contract remaining synchronized.

## Functional Register Groups

The DP transmitter groups are the low-level address surface for link encoding. Link control, MSA timing, video stream enable, DPHY lane/training controls, CRC, fast training, secondary-data packets, MSE/MST allocation, MSO, DSC, metadata, and ALPM registers are the hardware endpoints for modesetting, link training, DSC-over-DP setup, MST scheduling, compliance patterns, and link diagnostics.

The DIG stream-encoder groups are the address surface for HDMI/TMDS and generic digital-output programming. They include HDMI metadata and audio packet controls, ACR timing registers, infoframe and generic packet controls, TMDS pattern/DC-balance registers, output CRC, test/random pattern generators, and front-end/backend enable controls. These offsets matter for HDMI audio, HDMI/DVI/TMDS output, generic infoframes, pixel packing, and output validation.

The AFMT groups provide per-DIG audio formatting and packet-insertion offsets. Runtime code uses the AFMT controls for audio info updates, audio source selection, channel enable/layout, IEC 60958 channel-status values, audio sample send, audio CRC diagnostics, and AFMT memory power. These registers interact with both HDMI and DP audio packet paths.

The DME and VPG groups are metadata-generation endpoints. DME control enables and routes dynamic metadata, while VPG generic packet controls/status/update registers schedule and report generated packet state. The nearby SMU generic packet status offsets indicate integration with firmware-managed packet/state reporting.

The AUX groups are the DP AUX/DDC-over-AUX physical and protocol control surface. AUX control, software control, arbitration, interrupt status, SW/LS data/status, DPHY timing/status, GTC sync, and wake controls are used during connector detection, EDID reads, DisplayPort link training, sideband transactions, and AUX wake/power transitions.

The DOUT I2C group is the non-AUX DDC engine address surface. It exposes per-DDC speed/setup, transaction descriptors, data, arbitration, interrupt/status, EDID-detect control, and read-request interrupt state. It is shared across physical DDC lines rather than replicated per DIG encoder.

The DIO miscellaneous and perfmon groups expose shared state around scratch registers, memory-power control/status, clock control, soft reset, generic interrupts, link-type controls, HDMI RX-status timing, and DIO performance counters. These are not per-stream encoder addresses, but shared display I/O control and telemetry endpoints.

The DCIO and DCIO-chip groups expose top-level pin, PHY, pad, GPIO, HPD, DDC, AUX, genlock/swaplock, backlight frame-start, reference-clock, and soft-reset offsets. These provide integration points between logical display links and physical pins/connectors.

The UNIPHY reserved macro-control ranges are per-PHY address windows. The generated names do not expose semantic fields, so direct named consumers are limited compared with DP/DIG/AUX/AFMT. They still define stable offsets for PHY macro access, register dumps, low-level bring-up, debug, or PHY programming sequences that address reserved slots.

The PWRSEQ groups are the panel power and backlight sequencing address surface. They describe GPIO power-sequence controls, panel target/current state, power-up/down delays, reference dividers, PWM enable/period/control, lock, and spare state for two panel sequence instances. They are particularly important for eDP or embedded-panel power sequencing.

The DSCC/DSCCIF/DSC_TOP groups provide the Display Stream Compression register-address surface. DSCC config, PPS config, memory power, interrupt/status, error counters, and fullness counters map to the generic DSC implementation. DSCCIF config addresses represent the input interface, and DSC_TOP addresses represent top-level DSC clock/debug control. The associated perfmon blocks expose DSC performance counter readback and control.

## Control Flow And State Behavior

This header has no direct control flow. The runtime flow is table driven: DCN31 resource construction expands the generated offset macros into register-address structures, passes those structures plus sh/mask tables into block constructors, and later hardware blocks use helper macros to perform MMIO reads/writes.

Most state described by these offsets is hardware register state. Configuration registers persist until reprogrammed, reset, power-gated, or overwritten by firmware/hardware sequencing. Examples include DP link setup, MSA timing, DIG/HDMI packet controls, AFMT audio controls, DME/VPG metadata configuration, AUX DPHY timing, DDC speed/setup, DIO clocks/resets, DCIO pin routing, PWRSEQ delays/PWM settings, DSC PPS parameters, and DSCC memory-power controls.

Status and telemetry registers are live hardware state. Examples include DP CRC/status, fast-training status, MSE slot-allocation status, DIG output CRC/FIFO/status, AFMT status/CRC/interrupt state, AUX SW/LS/DPHY/GTC status, I2C HW/SW status, DIO memory-power status, perfmon counter state/readback, panel power-sequence state, DSCC status/interrupt, DSC error counters, and maximum-fullness counters.

Several groups are ordering-sensitive. DP link training and AUX PHY setup require programming the correct channel instance and transmitter/UNIPHY route before training transactions. HDMI/AFMT packet updates often involve double-buffered packet memory and update bits. DME metadata programming has comments in the stream-encoder path requiring OTG master update lock when changing DME configuration. DSC PPS and slice/topology state must be coherent before enabling compressed output. Panel PWRSEQ delays and PWM controls must respect panel power timing and backlight sequencing.

State is also distributed across separate generated blocks. A display link can involve DIG stream-encoder offsets, DP link offsets, AUX offsets, DCIO UNIPHY/link/xbar offsets, HPD/GPIO offsets, AFMT offsets, VPG/DME offsets, and possibly PWRSEQ or DSC offsets. A correct runtime sequence depends on those register tables pointing to the same physical/logical instance mapping.

## Dependencies And Integration Points

This file must remain synchronized with `dcn_3_1_2_sh_mask.h`. Offset macros name the registers and their addresses; sh/mask macros name the fields in those registers. Register-list initializers often use offset macros from this file and field macros from the companion header in separate structures, so mismatch can produce compile failures or, worse, valid builds that write the wrong register or bit field.

The DCN31 display resource path is the main integration point. `dcn31_resource.c` includes this header, builds register arrays for AFMT, VPG, stream encoders, AUX, HPD, link encoders, HPO encoders, DSC, DWBC/MCIF writeback, and other DCN blocks, and constructs hardware block objects from those tables. For this chunk, the highest-impact covered tables are AFMT, AUX, link encoder, stream encoder/DME/VPG, PWRSEQ-related panel control, and DSC.

The link-encoder path integrates DP/DIG/AUX/DCIO/UNIPHY offsets with VBIOS connector information. Runtime transmitter routing relies on `TRANSMITTER_UNIPHY_A` through `TRANSMITTER_UNIPHY_E` mapping to `link_enc_regs[]`, while AUX channel selection uses `enc_init_data->channel - 1` to index the AUX register table. Any generated offset/index mismatch can route training or AUX transactions to the wrong physical connector.

The AFMT and stream-encoder paths integrate with audio, HDMI infoframe, and generic-packet code. AFMT registers are constructed separately from the core stream-encoder registers but act on the same DIG instance. The packet/audio code therefore depends on AFMT instance ordering matching DIG instance ordering.

The AUX and I2C/DDC paths integrate with connector discovery, EDID, DisplayPort training, sideband communication, and HPD behavior. AUX offsets are per-channel, while DOUT I2C registers are shared controller resources with per-DDC speed/setup/status offsets. These offsets also intersect with DCIO-chip GPIO and AUX pad controls.

The panel-control path integrates PWRSEQ offsets with embedded-panel power and backlight behavior. The DCN301 panel-control code reads/writes PWRSEQ target/current state, DIGON/BLON state, and BL PWM reference divider; DCN31 resource construction reuses that family of hardware programming for panel control.

The DSC path integrates DSCC offsets with the generic DCN20 DSC implementation. Higher-level mode validation and Display Mode Library code decide DSC feasibility and clocking; `dsc2_construct()` binds the generated offsets and masks so the DSC implementation can program PPS/config/status/memory-power and read telemetry for instances 0 through 2 on DCN31.

The DMUB path integrates generated offsets into firmware service register access. `dmub_dcn31.c` builds a DCN31 DMUB register table using `BASE(reg..._BASE_IDX) + reg...`; this makes generated address correctness important for firmware reset, inbox/outbox, interrupts, and any DMUB-visible DCN register operations.

The IRQ path integrates generated offsets/masks into DCN31 interrupt source tables. AUX, HPD, DIO, DSC, or related interrupt sources depend on this generated address namespace matching the silicon register map.

## Risks And Edge Cases

The primary risk is generated-header drift from the hardware register specification or from the companion sh/mask header. An incorrect offset can compile cleanly if the macro name still exists, but runtime code may program the wrong MMIO register. In this chunk, high-impact failures include broken DP link training, AUX/DDC timeouts, HDMI audio/infoframe corruption, incorrect DIG/UNIPHY routing, panel power sequencing failures, backlight PWM errors, DSC mode failures, or misleading diagnostic counters.

Instance ordering is a recurring edge case. DP2/3/4, DIG2/3/4, AFMT0-4, AUX0-4, and UNIPHY A-E style resources are assembled into arrays and indexed by engine/channel/transmitter IDs. Off-by-one mapping between logical DIG, physical transmitter, AUX channel, HPD source, and connector metadata can make a register table look valid while affecting a different port.

The chunk starts and ends inside larger logical groups. The DIG1 tail must be reconciled with the previous chunk for a full DIG1 report, and DSCC2 is incomplete here. The merge lane should not treat this chunk alone as complete coverage for DIG1 or DSC instance 2.

UNIPHY reserved macro-control registers are opaque. Their generated `RESERVED0` through `RESERVED57` names do not document field semantics, so the safest interpretation is address-window coverage rather than functional behavior. Tests or documentation that infer behavior solely from these names risk overclaiming.

DP and AUX programming is timing-sensitive. AUX DPHY timing registers, wake controls, arbitration, and interrupt/status registers are involved in transactions that can fail due to incorrect thresholds, stale status, power state, or wrong channel routing. DP link training also depends on coherent DP DPHY, MSA, link framing, FEC, MST/MSE, and physical UNIPHY state.

HDMI/AFMT packet programming is stateful and often double-buffered. Wrong offsets for generic packet controls, infoframes, audio source/control, or 60958 channel status can produce silent audio loss, incorrect infoframes, or display compliance failures without a kernel crash.

Panel PWRSEQ offsets are high risk because wrong panel power or PWM register writes can create black screen, flicker, long delays, or unsafe sequencing around embedded panels. Target-state and current-state readbacks must be interpreted with the correct instance and timing.

DSC programming is dense and cross-field dependent. PPS config offsets, slice/config registers, memory-power controls, and interrupt/status registers must match the sh/mask definitions and the selected DSC mode. Wrong DSCC offsets can show up as compressed-stream corruption, underflow/overflow, stuck update status, or invalid telemetry rather than a simple fault.

Perfmon and CRC/status registers are diagnostic state, not pure configuration. Tests must clear/select/enable/read them in the correct order. Stale DIO/DSC perfmon values or CRC state can mislead validation even when offsets are correct.

## Test Signals

Build-time coverage should catch missing or renamed macros in `dcn31_resource.c`, `dcn31_dio_link_encoder.h`, `dcn31_afmt.h`, `dcn30_dio_stream_encoder.h`, `dcn20_dsc.h`, `dmub_dcn31.c`, and `irq_service_dcn31.c`. High-signal compile failures include missing `regDP2_*`, `regDIG2_*`, `regAFMT*_AFMT_*`, `regDP_AUX*_AUX_*`, `regDIO_LINK*_CNTL`, `regUNIPHY*_LINK_CNTL`, `regPWRSEQ*_PANEL_PWRSEQ_*`, or `regDSCC*_DSCC_*` symbols.

DisplayPort validation should exercise DCN31 outputs on DP2/3/4-capable routes, including link training at multiple rates/lane counts, FEC where supported, MST/MSE allocation, DSC-over-DP, MSO where supported, ALPM, HPD events, suspend/resume, and AUX transactions. Useful signals are successful modesets, stable link training, no AUX timeouts, correct DPCD/EDID reads, and no unexpected DP CRC/training/status errors.

HDMI/TMDS validation should exercise DIG2/3/4 HDMI or DVI paths, including audio setup, ACR values, infoframe send/update, generic packets, TMDS output, output CRC/test patterns, and hotplug. Expected signals are correct audio playback/channel status, correct AVI/audio/vendor infoframes, no FIFO/CRC errors, and valid sink behavior across modes.

AFMT/VPG/DME validation should cover audio packet programming, 60958 channel-status updates, AFMT memory-power transitions, dynamic metadata enable/disable, VPG generic packet update/status, and metadata packet delivery. Runtime signals include correct packet captures on the sink/analyzer, no stale update status, and no AFMT interrupt anomalies.

AUX/I2C/DDC validation should cover EDID reads over AUX and DDC, repeated hotplug/unplug, AUX wake behavior, I2C transaction status, interrupt handling, and error recovery. Good signals are deterministic EDID/DPCD reads, bounded retry counts, and clean status after failed transactions.

Panel-control validation should exercise eDP panel power-up/down, backlight PWM enable/period/brightness, DIGON/BLON sequencing, suspend/resume, and panel off/on cycles. Useful signals are correct panel state readback, no excessive delays, stable brightness, and no black-screen regressions.

DSC validation should exercise compressed modes on DSC instances 0 through 2 where routing permits. Signals include correct PPS register dumps, successful modesets at DSC-required bandwidths, no DSCC underflow/overflow interrupts, no stuck update-pending/status bits, and sane DSCC fullness/error counters.

Diagnostic validation should include DIO and DSC perfmon counter clear/enable/readback flows and DP/DIG/AFMT CRC readback flows. These tests should assert that counters change only when expected and that clear/status sequencing prevents stale readbacks.
