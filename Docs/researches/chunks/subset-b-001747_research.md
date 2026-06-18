# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h lines 7835-10383

## Purpose

This chunk is generated AMDGPU DCN 3.0.2 display-controller register address metadata. It contains no executable C code; its public interface is a set of preprocessor constants that bind symbolic `mm...` register names to MMIO register offsets, with a paired `mm..._BASE_IDX` constant for each register.

The path is under a local `ceph-client` source mirror, but this file is AMD display hardware metadata, not Ceph filesystem logic. This slice covers the output timing generator and display I/O portions of the DCN302 offset namespace:

- The full `OTG0` register family, followed by full `OTG1` through `OTG4` timing-generator families.
- OPTC misc registers and the OPTC-side display perfmon block.
- DIO I2C, DIO misc, HPD0 through HPD4, DIO perfmon, and DP AUX0 through AUX4 blocks.
- DIG/VPG/AFMT/DME stream-encoder-related blocks for DIO instances 0, 1, and 2.
- Full DP0 and DP1 link/stream/secondary-data blocks, and the first 74 DP2 registers through `mmDP2_DP_GSP8_CNTL`.

Every register entry follows the generated ABI pattern used throughout AMD DC:

- `mmREGISTER` is the register's offset value.
- `mmREGISTER_BASE_IDX` selects the ASIC IP base segment used to compute the final MMIO address.

Consumers are expected to combine both pieces through register-list macros such as `SR()` and `SRI()` rather than hard-coding numeric addresses.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, or runtime APIs in this chunk. The important API is the generated macro namespace consumed by DCN302 display resource construction and register helper layers.

This line range contains 2,416 `#define` entries: 1,208 register-offset macros and 1,208 matching `_BASE_IDX` macros. All visible base-index values in this chunk are `2`, meaning these offsets are resolved through the DCN base segment selector used by the local `BASE(mm..._BASE_IDX)` helper in DCN302 resource code.

Major macro families:

- OTG timing generators: `mmOTG0_*` through `mmOTG4_*` define horizontal/vertical totals, blanking, sync, trigger controls, status counters, stereo/interlace state, snapshot controls, update locks, vertical interrupts, CRC windows/results, static screen and 3D controls, global sync lock controls, dynamic refresh-rate controls, DTO constants, DSC start position, and pipe update status.
- OPTC misc: `mmDWB_SOURCE_SELECT`, `mmGSL_SOURCE_SELECT`, `mmOPTC_CLOCK_CONTROL`, and ODM memory power/status/spare registers define cross-pipe output timing support outside a single OTG instance.
- OPTC perfmon: `mmDC_PERFMON17_*` defines counter control/state/current/high/low registers for output timing performance monitoring.
- DIO I2C and misc: `mmDC_I2C_*`, `mmDC_I2C_DDC1_*` through `mmDC_I2C_DDC5_*`, `mmDIO_SCRATCH*`, `mmDIO_MEM_PWR_*`, `mmDIO_CLK_CNTL`, `mmDIO_TEST_DEBUG_*`, and generic interrupt registers define display data channel access, DIO block memory/clock/power control, debug, scratch, and interrupt surfaces.
- Hotplug detect: `mmHPD0_*` through `mmHPD4_*` define HPD interrupt status/control, control, RX interrupt timer, and toggle filter controls for five connectors.
- DIO AUX: `mmDP_AUX0_*` through `mmDP_AUX4_*` define AUX control, timing, address, command, reply, software data, latency, GTC sync, DPHY TX, and PHY wake controls.
- VPG instances: `mmVPG0_*`, `mmVPG1_*`, and `mmVPG2_*` define generic packet access/data, frame/immediate update controls, status, memory power, ISRC data, and MPEG info registers.
- AFMT instances: `mmAFMT0_*`, `mmAFMT1_*`, and `mmAFMT2_*` define audio/VBI/infoframe packet controls, 60958 channel status, audio CRC, ramp controls, interrupt/status, audio source selection, and memory power.
- DME instances: `mmDME0_*`, `mmDME1_*`, and `mmDME2_*` define control and memory control for each DME block.
- DIG instances: `mmDIG0_*`, `mmDIG1_*`, and `mmDIG2_*` define front-end control, output CRC, test/clock/random patterns, FIFO status, HDMI metadata/audio/ACR/infoframe/generic-packet controls, TMDS controls, lane enable, version, and force-disable controls.
- DP instances: `mmDP0_*`, `mmDP1_*`, and partial `mmDP2_*` define DP link/video stream, pixel format, MSA, DPHY training/scramble/CRC/fast-training, secondary data packets, audio M/N, timestamp, MST/MSE allocation, MSO/DSC, metadata, ALPM, data bypass, GSP, and related status/control registers.

Address-block coverage in this chunk:

- `OTG0` starts at line 7835, but its `addressBlock` comment is just before the chunk. The register range is `mmOTG0_OTG_H_TOTAL` through `mmOTG0_OTG_SPARE_REGISTER`.
- `dce_dc_optc_otg1_dispdec`, base `0x200`, has 107 register offsets from `mmOTG1_OTG_H_TOTAL` to `mmOTG1_OTG_SPARE_REGISTER`.
- `dce_dc_optc_otg2_dispdec`, base `0x400`, has 107 register offsets from `mmOTG2_OTG_H_TOTAL` to `mmOTG2_OTG_SPARE_REGISTER`.
- `dce_dc_optc_otg3_dispdec`, base `0x600`, has 107 register offsets from `mmOTG3_OTG_H_TOTAL` to `mmOTG3_OTG_SPARE_REGISTER`.
- `dce_dc_optc_otg4_dispdec`, base `0x800`, has 107 register offsets from `mmOTG4_OTG_H_TOTAL` to `mmOTG4_OTG_SPARE_REGISTER`.
- `dce_dc_optc_optc_misc_dispdec`, base `0x0`, has 8 register offsets from `mmDWB_SOURCE_SELECT` to `mmOPTC_MISC_SPARE_REGISTER`.
- `dce_dc_optc_optc_dcperfmon_dc_perfmon_dispdec`, base `0x79a8`, has 9 register offsets from `mmDC_PERFMON17_PERFCOUNTER_CNTL` to `mmDC_PERFMON17_PERFMON_LOW`.
- `dce_dc_dio_dout_i2c_dispdec`, base `0x0`, has 26 register offsets from `mmDC_I2C_CONTROL` to `mmDC_I2C_READ_REQUEST_INTERRUPT`.
- `dce_dc_dio_dio_misc_dispdec`, base `0x0`, has 19 register offsets from `mmDIO_SCRATCH0` to `mmDIO_GENERIC_INTERRUPT_CLEAR`.
- HPD0 through HPD4 each have 5 register offsets, with per-instance bases `0x0`, `0x20`, `0x40`, `0x60`, and `0x80`.
- `dce_dc_dio_dio_dcperfmon_dc_perfmon_dispdec`, base `0x7d10`, has 9 register offsets from `mmDC_PERFMON18_PERFCOUNTER_CNTL` to `mmDC_PERFMON18_PERFMON_LOW`.
- AUX0 through AUX4 each have 19 register offsets, with per-instance bases `0x0`, `0x70`, `0xe0`, `0x150`, and `0x1c0`.
- DIG0, DIG1, and DIG2 each have VPG, AFMT, DME, DIG, and DP address blocks. DIG0 and DIG1 each include complete 78-register DP blocks in this chunk. DIG2 includes VPG/AFMT/DME/DIG and the first 74 registers of DP2.

## Control Flow

This header chunk has no direct control flow. It is declarative MMIO address data.

The runtime flow that uses these constants is provided by AMD DC code:

1. DCN302-specific resource code includes `dimgrey_cavefish_ip_offset.h`, `dcn/dcn_3_0_2_offset.h`, and `dcn/dcn_3_0_2_sh_mask.h`.
2. `dcn302_resource.c` defines `BASE(seg)` and register-table helpers such as `SR(reg_name)` and `SRI(reg_name, block, id)`.
3. Register-list macros expand symbolic names from this header into absolute register addresses, for example `BASE(mmOTG0_OTG_H_TOTAL_BASE_IDX) + mmOTG0_OTG_H_TOTAL`.
4. DCN302 resource constructors assign those populated tables to hardware block objects: timing generators, DIO, VPG, AFMT, audio, stream encoders, AUX engines, and I2C engines.
5. Runtime display paths use generic helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, and `REG_GET` through those tables to program mode timing, vertical interrupts, updates, HDMI/DP metadata, audio packets, AUX transactions, I2C transfers, and hotplug state.

The macros themselves do not encode sequencing. Correct ordering, waits, locking, and side-effect handling live in higher-level DC timing-generator, stream-encoder, AUX, I2C, hotplug, and link-training code.

## State And Persistence Behavior

This file stores no software state and persists nothing. It names MMIO-backed GPU display hardware state.

Hardware state represented by this chunk includes:

- Timing-generator programming: mode totals, blanking, sync polarity/positions, interlace/stereo, counters, master enable, update locks, global sync lock, DRR/VRR timing, DSC start position, and pipe update state.
- Interrupt and status surfaces: vertical interrupt positions/control registers, vtotal/vsync/DRR interrupt status, HPD interrupt status/control, DIO generic interrupt status/clear, AUX reply/status, DIG FIFO status, DP stream/link/training status, and perfmon counter state.
- CRC, readback, and diagnostics: OTG CRC windows/results, DIG output CRC, DP DPHY CRC, display perfmon counters, DIO debug and scratch registers.
- Display I/O sideband access: DDC/I2C setup/speed/status/transaction/data registers, AUX command/data/address/timing registers, HPD filter/timer controls.
- Stream-encoder and link state: HDMI packet/audio/ACR/generic/infoframe controls, TMDS controls, DP MSA timing, DP secondary-data packet controls, MST/MSE scheduling state, DSC/MSO/ALPM/GSP controls, and video stream enable/configuration.
- Memory and power controls: ODM memory power, DIO memory/clock control, VPG/AFMT memory power, and DME memory control.

Persistence is hardware-defined. Configuration registers generally remain effective until reprogramming, reset, or power-gating loss. Status, interrupt, FIFO, training, CRC, AUX, HPD, and perfmon registers may be read-only, sticky, write-one-to-clear, self-clearing, or side-effect-sensitive depending on the matching field definitions in `dcn_3_0_2_sh_mask.h` and the hardware programming guide.

## Dependencies And Integration Points

Primary dependency:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h` supplies matching field shift/mask constants for these register offsets.

Direct DCN302 include and base-address integration:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c` includes this offset header, the matching sh/mask header, and `dimgrey_cavefish_ip_offset.h`.
- The same file defines `BASE(seg)`, `SR(reg_name)`, and `SRI(reg_name, block, id)`, which are the core contracts that combine `mm..._BASE_IDX` and `mm...` into register addresses.
- `res_cap_dcn302` declares five timing generators, five audio blocks, five stream encoders, and five DDC engines; this matches the chunk's five OTG, HPD, I2C/DDC, AUX, and partially visible stream/link instance families.

Block construction paths that consume this chunk:

- `dcn302_timing_generator_create()` uses `optc_regs[]`, populated by `OPTC_COMMON_REG_LIST_DCN3_0(id)`. That register list consumes the `OTG*` timing/update/DRR/CRC macros, ODM/OPTC data-format and memory macros from adjacent chunks, and `DWB_SOURCE_SELECT` from this chunk.
- `dcn302_dio_create()` uses `DIO_REG_LIST_DCN10()`, which currently references `DIO_MEM_PWR_CTRL`.
- `dcn302_i2c_hw_create()` uses `I2C_HW_ENGINE_COMMON_REG_LIST(id)`, which consumes `DC_I2C_DDC{id}_SETUP`, `DC_I2C_DDC{id}_SPEED`, `DC_I2C_DDC{id}_HW_STATUS`, shared `DC_I2C_*` transaction/data/control registers, and time-base metadata from another chunk.
- `dcn302_aux_engine_create()` uses AUX engine register tables based on the DP AUX families, including `DP_AUX{id}_AUX_CONTROL`, command/address/data/reply/status/timing, and DPHY TX control.
- `dcn302_vpg_create()` uses `VPG_DCN3_REG_LIST(id)`, consuming generic status, packet access/data, and frame/immediate update controls from the `VPG0` through `VPG2` blocks in this chunk for the visible instances.
- `dcn302_afmt_create()` uses `AFMT_DCN3_REG_LIST(id)`, consuming AFMT infoframe, VBI/audio packet, source, 60958, and memory-power registers.
- `dcn302_stream_encoder_create()` maps `ENGINE_ID_DIGA` through `ENGINE_ID_DIGE` to VPG/AFMT/DIG instances and uses `SE_DCN3_REG_LIST(id)`. For instances visible in this chunk, this consumes DIG HDMI/TMDS/front-end/FIFO registers and DP link/MSA/secondary-data/DSC/MST packet registers.
- `dcn302_create_audio()` uses `AUD_COMMON_REG_LIST(id)`. Audio endpoint and DCCG audio DTO registers are defined in other chunks, while this chunk contributes the stream-side AFMT, HDMI, and DP secondary audio surfaces used with the audio path.

Important downstream behavior:

- Timing-generator code under `display/dc/optc/` uses these register tables for mode timing, update lock, CRC, DRR, global sync, and DSC/ODM handoff.
- Stream-encoder and link code under `display/dc/dio/` and `display/dc/link/` use the DIG/DP/VPG/AFMT/AUX/I2C/HPD offsets to configure HDMI, DisplayPort, sideband link management, audio packets, metadata packets, and hotplug detection.
- Interrupt service code for DCN302 uses the same hardware namespace when mapping source IDs and servicing HPD, vertical blank/update, and related display interrupts.

## Risks And Edge Cases

- These constants are hardware ABI. A wrong offset or wrong `_BASE_IDX` can compile cleanly while redirecting a register access to unrelated MMIO, causing blank displays, incorrect mode timing, missed vblank/HPD interrupts, failed AUX/I2C transfers, bad audio packets, link-training failure, or unstable power behavior.
- Offset and base-index macros are a pair. Changing one without the other breaks the `BASE(mm..._BASE_IDX) + mm...` address calculation used by `SR()` and `SRI()`.
- This chunk is highly instance-repetitive. OTG0 through OTG4, HPD0 through HPD4, AUX0 through AUX4, and DIG/DP/VPG/AFMT/DME instances differ mostly by numeric instance and base offset, making generated-header drift or off-by-one copy errors especially hazardous.
- The chunk starts after the `dce_dc_optc_otg0_dispdec` address-block comment. Merge/reconciliation should preserve that OTG0 belongs to the OTG0 block even though the comment is just outside this line range.
- The chunk ends inside the `dce_dc_dio_dp2_dispdec` block at `mmDP2_DP_GSP8_CNTL`. Later chunk research is required for the remaining DP2 register offsets and the rest of the DIO/DIG instance coverage.
- Several registers are access portals or sequenced state machines rather than ordinary storage, especially `*_ACCESS_CTRL`/`*_DATA`, I2C transaction/data registers, AUX command/data/reply registers, HPD interrupt status/control, and perfmon counters. Incorrect read/write ordering can target stale indexed state, clear events unexpectedly, or wedge sideband transactions.
- Timing-generator registers are often double-buffered or synchronized to vblank/update windows. The offsets do not reveal which writes must be update-locked, master-update-locked, or synchronized across pipes.
- HPD and AUX/I2C state is connector-facing. Bad offsets can look like monitor, cable, EDID, or link-training failures rather than an obvious register-table bug.
- DP secondary-data, GSP, DSC, MST/MSE, and metadata registers interact with stream timing. Inconsistent offsets can produce subtle failures such as missing HDR metadata, incorrect audio timing, broken DSC PPS packets, MST bandwidth allocation errors, or intermittent blanking.
- Access semantics and bit layout are not represented in this file. Callers must use the matching `dcn_3_0_2_sh_mask.h` fields and established programming sequences.

## Test Signals

Useful validation signals are compile-time register-table expansion plus hardware behavior on DCN302-class devices:

- Build AMDGPU display code with DCN302 enabled. Missing or renamed macros should fail where `dcn302_resource.c` expands `OPTC_COMMON_REG_LIST_DCN3_0`, `DIO_REG_LIST_DCN10`, `VPG_DCN3_REG_LIST`, `AFMT_DCN3_REG_LIST`, `SE_DCN3_REG_LIST`, AUX, I2C, and audio register lists.
- Diff this chunk against AMD's authoritative DCN 3.0.2 register database or adjacent generated headers to catch offset/base-index drift in OTG, DIO, AUX, HPD, DIG, and DP families.
- Exercise basic modesets on one through five active timing generators, verifying horizontal/vertical timing, vblank, page flips, update locks, DRR/VRR behavior, and DSC start position when DSC is enabled.
- Validate CRC capture/readback and perfmon paths where available, including OTG CRC windows/results and `DC_PERFMON17/18` counter registers.
- Test connector hotplug and unplug across all five HPD instances. Watch for missed HPD interrupts, interrupt storms, stale toggle-filter behavior, or incorrect source mapping.
- Read EDID and perform DDC operations across all five I2C engines; failures may show as EDID read errors, I2C arbitration timeouts, or incorrect DDC engine selection.
- Exercise DisplayPort AUX transactions across AUX0 through AUX4, including link training, DPCD reads/writes, sideband operations for MST where supported, and timeout/retry paths.
- Test HDMI and DP stream encoding on DIG0 through DIG2 at minimum, including HDMI infoframes, audio ACR, generic packets, DP MSA timing, secondary data packets, DSC PPS/GSP packets, and MST/MSE behavior.
- Run audio playback over HDMI and DisplayPort, checking AFMT audio packet generation, 60958 channel status, DP secondary audio M/N and timestamp paths, and underrun/log signals.
- Monitor kernel logs for DCN underflow, HPD/AUX/I2C timeout, link-training failure, page-flip timeout, vblank timeout, DSC metadata/PPS issues, MST allocation errors, FIFO errors, and display/audio corruption after any generated offset update.

## Cross-Chunk Notes

This is chunk 4 of `dcn_3_0_2_offset.h`, covering lines 7835-10383 of a larger generated header. The previous chunk contains the address-block comment immediately preceding `OTG0` and earlier DCN302 display-pipe blocks. The next chunk continues from line 10384, starting after `mmDP2_DP_GSP8_CNTL_BASE_IDX`, and is needed to complete DP2 and later generated register families. The final per-file research document should merge all chunks before making complete claims about DCN 3.0.2 offset coverage.
