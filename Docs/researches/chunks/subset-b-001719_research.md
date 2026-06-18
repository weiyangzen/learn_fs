# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h lines 7846-10422

## Scope

This chunk is a generated AMD DCN 3.0.1 register offset slice. It contains preprocessor constants only: no functions, structs, enums, local storage, or executable branches. The exported contract is the `mm...` register-offset macro plus its paired `mm..._BASE_IDX` macro, consumed by AMD display register-table builders to form absolute MMIO register addresses.

The assigned range starts in the middle of the `DIG0` HDMI/TMDS register group and ends in the middle of `MPCC_OGAM0` output-gamma RAM A region definitions. It contains 1205 register-offset macros and 1204 visible `_BASE_IDX` companions; the last visible macro, `mmMPCC_OGAM0_MPCC_OGAM_RAMA_REGION_6_7`, is cut off before its `_BASE_IDX` line in the next chunk.

## Purpose

The purpose of this chunk is to map DCN 3.0.1 display hardware blocks to register offsets for display engine programming. The values are not policy and do not implement algorithms; they provide ASIC-specific address metadata for display link, audio/video packet, GPIO/AUX/DDC, DSC compression, writeback, display VM, and MPC composition paths.

Major hardware areas represented here are:

- DIO stream/link instances: tail of `DIG0`, then `DIG1`, `DIG2`, and `DIG3` front-end/HDMI/TMDS registers; `DP0` through `DP3` link, main-stream-attribute, DPHY, secondary-data packet, MST MSE, DSC, ALPM, and GSP registers.
- Video packet/audio formatter blocks for links 1-3: `VPG1` through `VPG3`, `AFMT1` through `AFMT3`, and small `DME1` through `DME3` memory/control register groups.
- DCIO top and chip registers: generic DCIO clocks, reference clock, UNIPHY link/channel xbar controls, panel power sequencing, backlight PWM, genlock/swaplock pads, soft reset, GPIO/DDC/HPD/PWRSEQ pad controls, AUX controls, and AUX/I2C pad power status.
- UNIPHY macro reserved ranges for `DCIO_UNIPHY1`, `DCIO_UNIPHY2`, and `DCIO_UNIPHY3`, each exposing reserved register slots 0-47 for PHY macro access.
- DSC instances 0-2: `DSC_TOP`, `DSCCIF`, `DSCC` configuration/PPS/error/rate-buffer registers and `DC_PERFMON17` through `DC_PERFMON19`.
- Writeback instance 0: DWB top/flow-control/CRC/overflow/host-read/reset/debug registers, `DC_PERFMON20`, and DWB color-processing registers for HDR multiplier, gamut remap A/B matrices, and output-gamma RAM A/B PWL descriptors.
- Display HVM: `DCHVM_CTRL0`, `DCHVM_CTRL1`, clock/memory controls, and RIOMMU control/status offsets.
- MPC/MPCC start: `MPCC0` through `MPCC3` composition selector/control/gain/background/memory/status registers and the start of `MPCC_OGAM0` output-gamma LUT/RAM A definitions.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The important interface is the generated macro namespace:

- `mm<REGISTER>` gives the per-ASIC offset for a display register.
- `mm<REGISTER>_BASE_IDX` gives the base segment index to pass through `BASE(...)`.
- Address block comments document the hardware block and local base address that generated each group.

Every complete register entry is intended to be consumed as `BASE(mmREG_BASE_IDX) + mmREG`. In DCN 3.0.1 display resource code, `dcn301_resource.c` includes this header and defines helpers such as `SR`, `SRI`, `SRII`, and `SRII2` that paste register names into resource-specific register tables. DMUB code also includes the same header and uses `REG_OFFSET(reg)` through `dmub_reg.h` to populate firmware-service register offsets.

Representative macro families in this chunk include:

- Link programming: `mmDP0_DP_LINK_CNTL` through `mmDP3_DP_GSP_EN_DB_STATUS`, covering DP link setup, pixel format, MSA, stream timing, training patterns, CRC, audio secondary-data packets, MST allocation, DSC enable/control, ALPM, and generic stream packets.
- HDMI/TMDS and audio packet programming: `mmDIG1_HDMI_CONTROL`, `mmDIG2_HDMI_GENERIC_PACKET_CONTROL*`, `mmDIG3_TMDS_CNTL`, `mmAFMT*_AFMT_AUDIO_*`, and `mmVPG*_VPG_GENERIC_PACKET_*`.
- DCIO/pads: `mmDCIO_CLOCK_CNTL`, `mmDC_REF_CLK_CNTL`, `mmUNIPHY[A-D]_LINK_CNTL`, `mmPANEL_PWRSEQ*_CNTL`, `mmBL_PWM*_CNTL`, `mmDC_GPIO_DDC*_MASK/A/EN/Y`, `mmDC_GPIO_HPD_*`, `mmDC_GPIO_AUX_CTRL_*`, and `mmAUXI2C_PAD_ALL_PWR_OK`.
- DSC: `mmDSC_TOP*_DSC_TOP_CONTROL`, `mmDSCCIF*_DSCCIF_CONFIG*`, `mmDSCC*_DSCC_CONFIG*`, `mmDSCC*_DSCC_PPS_CONFIG0..22`, error counters, rate-buffer fullness, and debug-bus rotation.
- Writeback: `mmDWB_ENABLE_CLK_CTRL`, `mmFC_MODE_CTRL`, `mmDWB_CRC_*`, `mmDWB_OVERFLOW_*`, `mmDWB_HDR_MULT_COEF`, `mmDWB_GAMUT_REMAP*`, and `mmDWB_OGAM_*`.
- MPC/MPCC: `mmMPCC0_MPCC_TOP_SEL` through `mmMPCC3_MPCC_STATUS` and the opening `mmMPCC_OGAM0_MPCC_OGAM_*` LUT/RAM A offsets.

## Control Flow

This chunk has no local control flow. Runtime control flow lives in the display driver objects that include the offset header and companion `dcn_3_0_1_sh_mask.h`.

Important flows represented by these offsets are:

1. DCN301 resource construction builds per-block register tables by expanding macros such as `SR`, `SRI`, and `SRII` over hardware-object register lists. The generated table values become addresses used by register helpers like `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`.
2. DMUB service setup includes this header in `dmub_dcn301.c` and initializes common DMUB register offsets with `REG_OFFSET(reg)`, using `BASE(mmREG_BASE_IDX) + mmREG`.
3. Link encoder and stream encoder flows program DP/HDMI/TMDS registers during modeset and link training. The DP offsets drive link count, pixel format, MSA, training-pattern, DPHY, secondary-data, MST allocation, DSC, and ALPM programming for link instances 0-3.
4. Audio/video packet flows use VPG and AFMT offsets to write generic packets, infoframes, HDMI audio/ACR controls, VBI packets, audio info/channel-status data, CRC controls, source selection, and memory-power controls.
5. DCIO GPIO/AUX/DDC/HPD flows read or write pad mask, data, enable, and output registers, plus panel/backlight sequencing registers, to support display detection, AUX/I2C transactions, hotplug handling, eDP panel power, and backlight PWM.
6. DSC flows program PPS/config registers, observe status/error/rate-buffer registers, and use per-DSC perfmon registers for compression and performance diagnostics.
7. DWB flows configure writeback clock/memory, frame-composition window/source sizes, CRC, overflow reporting, host reads, color conversion, gamut remap, and output gamma RAM descriptors.
8. MPC/MPCC flows configure composition source selection, OPP association, blending gains, background color, update-lock selection, memory power, and OGAM LUT state for composed output.

The macros do not encode hardware sequencing, volatile/status semantics, write-one-to-clear behavior, polling timeouts, lock ordering, or frame-boundary update rules. Callers must follow those rules in the DC, DIO, DSC, DWB, DCIO, DMUB, and MPC implementation files.

## State And Persistence Behavior

The header stores no software state and persists nothing by itself. It describes MMIO register locations whose hardware state persists until changed by the driver, firmware, reset, power gating, suspend/resume, display off/on transitions, or modeset reprogramming.

State represented by this chunk includes:

- Per-link DP/HDMI/TMDS state: link framing, pixel format, MSA timing/colorimetry, stream enable, training pattern, DPHY scrambler/CRC/test patterns, audio timing, secondary-data packet scheduling, MST stream-allocation table values, DSC link enable, ALPM control, and generic stream packet status.
- Per-link VPG/AFMT state: generic packets, GSP frame/immediate update controls, ISRC/MPEG info data, HDMI/DP audio packet controls, audio info/channel status, CRC, interrupts, source selection, and memory power.
- DCIO physical-interface state: UNIPHY link routing, channel crossbar selection, reference clocks, panel power sequencing, backlight PWM periods/duty controls, pad strength, GPIO/DDC/HPD/PWRSEQ direction and output values, AUX controls, and pad power-good status.
- DSC state: top-level enable/debug settings, DSCCIF config, DSCC PPS registers, memory power, compressor error accumulation, rate buffer fullness, and debug/perfmon counters.
- DWB state: flow-control source/window sizing, update control, CRC masks/values, host read controls, overflow counters, soft reset/debug, gamut-remap matrices, HDR multiplier, OGAM LUT index/data/control, and A/B PWL region descriptors.
- DCHVM state: display HVM control, clock/memory behavior, and RIOMMU control/status.
- MPC state: MPCC top/bottom input selection, OPP routing, blend control, gains, background color, memory power, status, and the beginning of MPCC OGAM LUT/RAM A state.

Many of these registers are live hardware controls or status registers. Some are double-buffered, banked, or synchronized to frame updates by surrounding display code. A wrong offset can therefore produce intermittent link, color, timing, or power bugs rather than a clean compile-time failure.

## Dependencies And Integration Points

The companion field-layout header is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h`. This offset header supplies register addresses; the shift/mask header supplies bit positions and masks inside those registers. Both are required for meaningful register access.

Primary integration points visible in this repository are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c`, which includes this header, defines `BASE`, `SR`, `SRI`, `SRII`, and related table-expansion helpers, and wires DCN301 hardware objects to generated register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c`, which includes this header and initializes DMUB service register offsets.
- DCN30/DCN301 DIO stream/link encoder, VPG, AFMT, DSC, DWB, DCIO, panel control, AUX/I2C, and MPC code that receives generated register tables from resource construction.
- ASIC base-address metadata such as `vangogh_ip_offset.h`, which provides `DCN_BASE__INST0_SEG*` values consumed by `BASE(mm..._BASE_IDX)`.
- Register helper macros in the AMD display stack, which turn the generated offsets and companion masks into MMIO reads, writes, updates, and waits.

Although this path is under `sources/distributed-fs/ceph-client`, the chunk is AMDGPU display hardware metadata. It has no Ceph filesystem behavior, no distributed protocol logic, and no persistent storage semantics beyond hardware register state.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A bad offset or base-index constant usually compiles cleanly but sends a register write/read to the wrong address. The result can be a visibly broken display, a power-management failure, or diagnostics that report plausible but wrong data.

Instance repetition is a major edge case. DP/DIG/VPG/AFMT/DME instances follow repeated address patterns with per-instance offsets, while DCIO and DSC/DWB blocks switch to different address ranges. Copy-generation mistakes can affect only one link or one DSC/DWB instance, producing connector-specific or mode-specific failures.

The chunk starts mid-`DIG0` and ends mid-`MPCC_OGAM0`; adjacent chunks are needed to validate complete DIG0 and MPCC_OGAM0 coverage. The visible final macro lacks its `_BASE_IDX` in this chunk, so any chunk-local checker must treat that as a range boundary artifact rather than a malformed header.

DP/DIG risks include failed link training, wrong pixel format or MSA values, blank screens, unstable audio, bad HDMI infoframes, MST allocation errors, DSC-on-link failures, ALPM regressions, TMDS test-pattern failures, or status polling against the wrong lane/link register.

DCIO/GPIO risks include missed hotplug events, broken AUX/I2C/DDC transactions, incorrect panel/backlight sequencing, stuck GPIO direction/output state, wrong UNIPHY routing, and suspend/resume bugs where pad or PHY state is restored to the wrong register.

DSC risks include invalid PPS programming, compressor status reads from the wrong instance, incorrect error/rate-buffer diagnostics, and failures only on modes requiring DSC bandwidth savings.

DWB risks include corrupted writeback frames, bad CRC/overflow diagnostics, incorrect source/window sizing, color conversion or gamma errors, and host-read/debug accesses hitting unrelated registers.

MPC/MPCC risks include wrong composition routing, incorrect blend gains or background colors, memory-power/status reads from wrong MPCCs, and output-gamma LUT corruption. Because the MPCC range changes `_BASE_IDX` from 2 to 3, base-index mistakes around line 10242 are especially high impact.

## Test Signals

Useful validation signals are a mix of generated-header checks and display behavior:

- Build coverage for DCN301 display and DMUB code that includes `dcn_3_0_1_offset.h` and `dcn_3_0_1_sh_mask.h`.
- Generated consistency checks that every complete `mmREG` macro has a matching `mmREG_BASE_IDX`, every register used by DCN301 register-list macros exists, and companion shift/mask definitions exist for fields used by code.
- Address-pattern checks across repeated instances: `DP0..DP3`, `DIG1..DIG3`, `VPG1..VPG3`, `AFMT1..AFMT3`, `DME1..DME3`, `DSC0..DSC2`, `DSCC0..DSCC2`, and `MPCC0..MPCC3` should match expected per-instance strides unless hardware metadata documents a deviation.
- Runtime link tests across all physical outputs: DP link training at multiple rates/lane counts, HDMI/TMDS modes, audio/ACR/infoframe behavior, MST, DSC-over-DP, ALPM, and hotplug/replug.
- AUX/DDC/panel/backlight tests: EDID reads, HPD interrupt handling, eDP panel power sequencing, backlight PWM changes, suspend/resume, runtime PM, and display off/on cycles.
- DSC tests with modes that require and do not require DSC, checking visual output, PPS programming, rate-buffer/error counters, and perfmon counters.
- DWB tests that capture known frame content, verify CRC and overflow behavior, exercise host reads, and validate gamut/OGAM paths.
- MPC/MPCC tests for multi-plane composition, blending, OPP routing, background color, output gamma, update locks, and transitions during modeset.

Regression symptoms from this chunk include black screens, link-training failures, connector-specific failures, missing audio or malformed infoframes, hotplug/DDC/AUX failures, panel/backlight sequencing problems, DSC-only mode failures, corrupted writeback output, bad gamma or blend output, stuck register waits, and misleading debug/performance counters.

## Cross-Chunk Notes

This is an artificial line-range slice of a large generated constants header. The final per-file report should merge this with adjacent chunks to describe complete DCN 3.0.1 offset coverage, especially the preceding `DIG0` register block and the continuation of `MPCC_OGAM0` after line 10422.
