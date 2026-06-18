# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h lines 10141-12728

## Purpose

This chunk is a generated AMD DCN 4.1.0 register-offset table for the display I/O, DisplayPort, auxiliary-channel, hot-plug-detect, DSC, PHY mux, and the first HPO top-level register blocks. It contains no executable functions or C types; its API surface is the C preprocessor contract of `#define reg...` numeric offsets and matching `#define reg..._BASE_IDX` segment selectors.

Within lines 10141-12728 the file defines 1,190 register offset macros and 1,190 paired base-index macros. Most entries use `_BASE_IDX 2`, which is resolved by DCN401 code through `ctx->dcn_reg_offsets[2]` or the compile-time `DCN_BASE__INST0_SEG2` base. The final `HPO_TOP_*` entries use `_BASE_IDX 3`, marking the transition from legacy DIO/DCOH display blocks into HPO address space.

## Hardware Surface

The chunk begins inside the `dcn_dcec_dio_dp2_dispdec` block and then covers these major address blocks:

- `DP2` and `DP3` DisplayPort stream/link encoder registers: link control, pixel format, MSA colorimetry/misc/timing, stream control, steer FIFO, TU control, DPHY training/scrambler/CRC/status, secondary data packets, audio M/N, MST/MSE slots, ALPM, symbol counters, panel replay, MSO, and generalized sideband packet controls.
- `DIG2` and `DIG3` digital encoder front/back-end registers: FE enable/clock/CRC, back-end clock/control/enable, TMDS/HDMI control, HDMI generic/info/audio packet registers, HDMI GCP/ACR/ACR status, AFMT control, HDCP interrupt and I2C controls, and per-DIG version registers.
- `DIG0` through `DIG3` AFMT blocks: audio format control, channel status, infoframe and generic packet controls, 60958/60958 CS values, HBR packetization, audio CRC, VBI packet controls, SPD and HDR metadata packet programming, and double-buffer control.
- `DIG0` through `DIG3` DME and VPG blocks: metadata engine control/status/register set and video packet generator generic packet/header/subpacket controls.
- DIO support blocks: HDCP 1.x/HDCP 2.x control/status, DOUT I2C setup/speed/EDID/multisync/sw-status registers, DIO misc memory-power and clock gating, stream mapper control, and DCIO/uniphy lane/PHY control registers.
- Panel and compression blocks: PWRSEQ0 panel power sequencing/blacklight/PWM/ALPM/thermal-override registers and DSC0-DSC3 DSCC, DSCCIF, and DSC top registers.
- DCOH blocks: top-level DCOH controls, PHY mux0-3 controls, DP_AUX0-3 AUX engines, and HPD0-3 hot-plug interrupt/control/filter registers.
- HPO start: `HPO_TOP_CLOCK_CONTROL` and `HPO_TOP_HW_CONTROL`, both in base index 3.

## APIs, Types, And Macros

The important exported symbols are the generated register macros themselves. Each usable hardware register is represented by two macros:

- `reg<block>_<REGISTER>`: the register's offset within the generated address space, for example `regDP2_DP_TU_CNTL`, `regDIG2_DIG_FE_CNTL`, `regDIG2_TMDS_CNTL`, `regDP_AUX0_AUX_CONTROL`, `regHPD0_DC_HPD_INT_STATUS`, and `regHPO_TOP_CLOCK_CONTROL`.
- `reg<block>_<REGISTER>_BASE_IDX`: the segment selector passed to `BASE(...)`, for example `regDP_AUX0_AUX_CONTROL_BASE_IDX` and `regHPD0_DC_HPD_INT_STATUS_BASE_IDX`.

There are no locally declared structs, enums, inline helpers, or functions in this chunk. Runtime objects such as `aux_engine_regs`, `link_enc_aux_regs`, `link_enc_hpd_regs`, `link_enc_regs`, `stream_enc_regs`, `vpg_regs`, `afmt_regs`, `dsc_regs`, and HPO encoder register tables are populated by other DCN401 source files using the names defined here.

## Control Flow

This header has no runtime control flow. Its control-flow role is compile-time macro expansion:

1. DCN401 source includes `dcn_4_1_0_offset.h` with the paired `dcn_4_1_0_sh_mask.h`.
2. A consumer defines `BASE(seg)` as either `ctx->dcn_reg_offsets[seg]` or a compile-time segment constant such as `DCN_BASE__INST0_SEG2`.
3. Register-list macros expand with helpers such as `SR`, `SRI`, `SRI_ARR`, or `REG`, forming addresses as `BASE(reg..._BASE_IDX) + reg...`.
4. The populated register tables are handed to shared AMD display constructors and access helpers, which later perform MMIO reads/writes through the normal display core paths.

The naming convention is therefore part of the control path: `SRI(DC_HPD_INT_STATUS, HPD, 0)` expands to `regHPD0_DC_HPD_INT_STATUS_BASE_IDX` plus `regHPD0_DC_HPD_INT_STATUS`, while `SRI_ARR(DP_LINK_CNTL, DP, 2)` expands through the `regDP2_*` symbols.

## State And Persistence

The header itself stores no state and persists nothing. It maps symbolic names to hardware MMIO offsets. The persistent state affected by users of this chunk lives in display hardware registers: link training state, HPD interrupt status and acknowledgement bits, AUX transaction control/status, HDMI/DP packet generator configuration, DSC enable/status, panel power sequencing, PHY mux selection, clock gating, memory power control, and HPO top-level clock/hardware controls.

Because some registers are status or acknowledgement registers, incorrect offsets can have lasting runtime effects even though the header is static: HPD interrupts can be missed or left asserted, AUX transactions can time out, link training can program the wrong lane or DPHY block, and display stream/audio metadata can be emitted incorrectly.

## Dependencies And Integration Points

Direct dependencies are limited to the C preprocessor and the generated AMD register-header convention. The functional dependency is the paired shift/mask file, `dcn_4_1_0_sh_mask.h`; offset names here must match bitfield mask and shift names there.

Observed DCN401 integration points include:

- `display/dc/resource/dcn401/dcn401_resource.c` includes this header and uses `BASE(reg..._BASE_IDX) + reg...` in `SR`, `SRI`, and array variants to initialize AUX, I2C, DIO, link encoder, HPD, stream encoder, VPG, AFMT, APG, HPO, DSC, and hardware sequencer register tables.
- `dcn401_aux_engine_create()` initializes four AUX engines from the `DP_AUX0-3` register families before constructing `dce110_aux_engine` instances.
- `dcn401_link_encoder_create()` initializes AUX, HPD, and link encoder register tables, using the `DP_AUX*`, `HPD*`, `DIG*`, `DCIO`, and PHY-related symbols in this chunk for physical connector and link-encoder control.
- `dcn401_stream_encoder_create()`, `dcn401_vpg_create()`, and `dcn401_afmt_create()` map DIO stream encoder instances to the `DIG*`, VPG, and AFMT register families in this chunk.
- `dcn401_hpo_dp_stream_encoder_create()` and `dcn401_hpo_dp_link_encoder_create()` sit at the HPO transition; this chunk contributes `HPO_TOP_*`, while later file chunks continue the HPO stream/link encoder register space.
- `display/dc/irq/dcn401/irq_service_dcn401.c` uses `SRI(DC_HPD_INT_STATUS, HPD, n)` and related HPD control symbols to build HPD and HPD RX interrupt source entries.
- `display/dc/gpio/dcn401/hw_translate_dcn401.c` includes the same generated offset/mask pair for GPIO/HPD/DDC offset translation, although its specific GPIO register names mostly come from earlier parts of the header.
- `display/dmub/src/dmub_dcn401.c`, the DCN401 clock manager, and the GPIO factory also include this header, so generated-symbol compatibility is shared across display core, firmware mailbox, clocks, interrupts, and connector setup.

## Risks

The primary risk is silent hardware misprogramming. These macros are compile-time constants, so an incorrect offset or base index can still compile cleanly while reads and writes target the wrong MMIO register. That is especially dangerous for paired register families where names differ only by instance number, such as `DP2` versus `DP3`, `DIG2` versus `DIG3`, `DP_AUX0-3`, `HPD0-3`, and `DSC0-3`.

Base-index drift is another high-impact risk. Most entries in this range use segment 2, but `HPO_TOP_CLOCK_CONTROL` and `HPO_TOP_HW_CONTROL` use segment 3. If a consumer assumes one segment for the whole chunk, HPO registers resolve to the wrong address space.

The chunk also contains several cross-generation-looking layouts. Some offsets match DCN 3.5/3.6/4.2 families while others, notably DP AUX and HPD offsets, differ from older DCN 3.x files. Reusing register lists across ASIC versions without the exact generation's offset header can compile and fail only at hardware bring-up time.

Register-family completeness matters. Constructors initialize fixed arrays for four AUX engines, four HPD blocks, four DIO stream encoders, multiple VPG/AFMT instances, and four DSC blocks. Missing or renamed generated macros break builds; wrong but present symbols can cause instance aliasing.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware/display runtime checks:

- Compile DCN401 display code with `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h` together; missing macro errors in resource, IRQ, DMUB, GPIO, or clock-manager code are immediate generated-header regressions.
- Add or run register-table sanity checks that compare initialized DCN401 table entries against expected `ctx->dcn_reg_offsets[base_idx] + offset` values for representative symbols such as `DP_AUX0_AUX_CONTROL`, `HPD0_DC_HPD_INT_STATUS`, `DIG2_DIG_FE_CNTL`, `DP2_DP_LINK_CNTL`, and `HPO_TOP_CLOCK_CONTROL`.
- Exercise connector hotplug and HPD RX paths; expected signals are HPD interrupts mapping to the right `DC_IRQ_SOURCE_HPDx`/`HPDxRX` entries, acknowledgement clearing the interrupt, and no stuck HPD status bits.
- Exercise AUX/DDC transactions for all physical connectors; expected signals are successful EDID reads, DP DPCD reads, timeout behavior only on absent sinks, and no cross-connector AUX aliasing.
- Exercise DP and HDMI modes on DIG2/DIG3-era mappings, including audio, infoframes, MST/MSO, DSC, ALPM/panel replay where supported, and link training. Failures often appear as blank display, unstable link training, missing audio, wrong colorimetry, or malformed secondary data packets.
- Exercise DSC0-DSC3 and HPO display paths separately, because the HPO top registers in this chunk switch to base index 3 and later HPO blocks continue outside this chunk.
