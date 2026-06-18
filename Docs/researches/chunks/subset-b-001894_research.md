# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h lines 10282-12823

## Scope

This chunk is a generated AMD DCN 3.1.6 register-offset header segment. It contains preprocessor constants only: each hardware register has a `reg...` offset macro and a paired `reg..._BASE_IDX` macro used by AMDGPU display code to compute the final MMIO address from a DCN base segment plus a per-register offset.

The requested slice covers 2,542 source lines and 2,390 `#define` lines: 1,195 register-offset macros and 1,195 matching base-index macros. All base-index values in this slice are `2`, meaning the consumers add the offsets to `DCN_BASE__INST0_SEG2` through the local `BASE(reg..._BASE_IDX)` expansion in DCN316 resource and DMUB code.

The chunk starts in the middle of the `DP1` DisplayPort encoder register family at `regDP1_DP_SEC_FRAMING2_BASE_IDX`, then covers the tail of `DP1`, complete `DIG1`, `DP2`, `DIG2`, `DP3`, `DIG3`, `DP4`, and `DIG4` blocks, AFMT/DME/VPG blocks for DIG0-DIG4, AUX0-AUX4, DOUT I2C, DIO misc/perfmon, DCIO common/chip GPIO, complete UNIPHY0-UNIPHY4 reserved macro-control ranges, and the first half of UNIPHY5. It ends at `regDCIO_UNIPHY5_UNIPHY_MACRO_CNTL_RESERVED30`; the `_BASE_IDX` for that register and UNIPHY5 reserved registers 31-57 continue after the requested range.

## Purpose

The purpose of this header segment is to give DCN316 display code compile-time names for MMIO offsets in the digital I/O path. These offsets are the address side of the generated register API; companion shift/mask headers define field packing. Driver code uses these macros to populate register tables for DisplayPort, HDMI/TMDS, stream encoders, audio metadata, AUX/I2C engines, GPIO/HPD/DDC pads, DCIO link routing, and UNIPHY link encoders.

This file does not implement algorithms. Its correctness is still operationally critical: if a generated offset or base index is wrong, higher-level C code can compile cleanly while programming the wrong hardware register.

## Register Families And Important Macros

The DisplayPort and stream-encoder portion covers:

- Tail of `DP1`, from secondary-data packet framing/audio timestamp registers through MSE/MST rate and slot-allocation table registers, MSA timing registers, MSO/DSC control, ALPM, generic secondary-packet controls `GSP8`-`GSP11`, and double-buffer status.
- Complete `DP2`, `DP3`, and `DP4` families, each with link control, pixel format, MSA colorimetry/misc/VBID, video stream control, DPHY training/scrambling/CRC/fast-training, secondary-data packet/audio registers, MST/MSE controls, MSO and DSC controls, metadata transmission, ALPM, and generic secondary packet controls.
- Complete `DIG1` through `DIG4` families, each with front-end control, output CRC, clock/test/random patterns, FIFO status, HDMI metadata/audio/ACR/VBI/infoframe/generic-packet controls, HDMI general control/status, TMDS control characters/sync/DC-balancer/control-bit registers, version, and force-disable.
- `AFMT0` through `AFMT4` audio-format blocks, including VBI/audio packet controls, audio info, IEC 60958 channel-status words, audio CRC, ramp controls, status, interrupt status, audio source control, and AFMT memory power.
- `DME0` through `DME4` with `DME_CONTROL` and `DME_DATA`, and `VPG0` through `VPG4` with generic-packet control/status, `VPG_GSP_FRAME_UPDATE`, and generic packet header/sub registers 0-7.

The link-side support blocks cover:

- `DP_AUX0` through `DP_AUX4`, each with AUX arbitration, control, software data, software control/reply data, interrupt control, transaction status, firmware status, low-level debug, PHY wake, and timeout-period registers.
- `dce_dc_dio_dout_i2c_dispdec`, including DDC/AUX software status for channels 1-5, DC GPIO AUX control registers, and HPD enable/rx interrupt/generic control registers for HPD1-HPD5.
- `dce_dc_dio_dio_misc_dispdec`, including `DIG_BE_CLK_CNTL`, `DIO_MEM_PWR_CTRL`, `DIO_INTERRUPT_CNTL`, display clock/gating control, test debug data/control, DCIO test debug index/data, DCIO debug clock control, DCFE/DCHUBBUB debug remap, DCIO debug control, and DCIOMON config/data.
- `DC_PERFMON18`, with performance monitor counter control/state, clock and counter enable, event selection, trigger/status, current-value interrupt, current-value low/high, and sampled low/high counter registers.

The DCIO and PHY-facing portion covers:

- `dce_dc_dcio_dcio_dispdec`, with generic DC registers, DCIO and reference-clock control, UNIPHYA through UNIPHYG link control and channel crossbar controls, write-command delay, DC pinstraps, intercept state, global swaplock/genlock pad control, backlight PWM frame-start display selection, and DCIO soft reset.
- `dce_dc_dcio_dcio_chip_dispdec`, with generic GPIO, DDC1-DDC5 and DDCVGA GPIO mask/A/enable/Y registers, genlock GPIO, HPD GPIO, panel power-sequence enables, pad strength, PHY AUX control, TX/RX/pullup controls, AUX control 0-5, and `AUXI2C_PAD_ALL_PWR_OK`.
- `dce_dc_dcio_dcio_uniphy0_dispdec` through `uniphy4`, each defining contiguous `DCIO_UNIPHYx_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED57` offsets.
- The beginning of `dce_dc_dcio_dcio_uniphy5_dispdec`, defining `DCIO_UNIPHY5_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED30` at the chunk boundary.

## Important APIs, Types, And Consumers

There are no functions, structs, or callable APIs in this header segment. The generated macro names are nevertheless consumed as a compile-time API by table-building macros in DCN316 code.

Important consumers found in the source tree include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes `dcn/dcn_3_1_6_offset.h` and `dcn/dcn_3_1_6_sh_mask.h`.
- The local `SR`, `SRI`, `SRII`, and related macros in `dcn316_resource.c`, which expand names like `regDP2_DP_LINK_CNTL` and `regDP2_DP_LINK_CNTL_BASE_IDX` into final register addresses.
- `stream_enc_regs[]`, populated by `SE_DCN3_REG_LIST(id)`, which uses the `DIG*` and `DP*` register families for stream encoder construction.
- `audio_regs[]`, `vpg_regs[]`, and `afmt_regs[]`, populated by `AUD_COMMON_REG_LIST`, `VPG_DCN31_REG_LIST`, and `AFMT_DCN31_REG_LIST`.
- `link_enc_aux_regs[]`, `aux_engine_regs[]`, and `i2c_hw_regs[]`, populated by AUX and I2C common register-list macros for connector discovery, DDC, AUX transactions, and link training support.
- `link_enc_regs[]`, populated by `LE_DCN31_REG_LIST`, `UNIPHY_DCN2_REG_LIST`, and DPCS lists; this is where the DCIO/UNIPHY link-control offsets participate in link encoder setup.
- `dio_regs`, populated by `DIO_REG_LIST_DCN10()`, which uses the DIO misc offsets such as `DIO_MEM_PWR_CTRL`.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`, which includes the same offset and sh/mask headers and builds `dmub_srv_dcn316_regs` with `REG_OFFSET_EXP(reg_name)`.

## Control Flow And Runtime Behavior

This header has no direct control flow. Runtime behavior appears when constructors bind these offsets into block-specific register tables and later hardware-object methods read or write those addresses through AMDGPU register helpers.

The typical flow is:

1. DCN316 resource construction includes the generated offset/sh/mask headers and defines `DCN_BASE__INST0_SEG*` values.
2. Register-list macros expand into static register-table instances, combining `BASE(reg..._BASE_IDX)` with `reg...` offsets.
3. Resource constructors pass those tables to hardware-object constructors such as `dcn10_dio_construct`, `dcn31_link_encoder_construct`, `dcn30_dio_stream_encoder_construct`, `dce_audio_create`, `vpg31_construct`, `afmt31_construct`, `dce110_aux_engine_construct`, and `dcn2_i2c_hw_construct`.
4. Link detection, HPD handling, DP AUX/DDC transactions, DisplayPort link training, HDMI/TMDS programming, secondary packet setup, audio-infoframe programming, VPG packet generation, and DCIO/UNIPHY link routing use the stored addresses through register-helper calls.
5. DMUB service initialization similarly turns selected macro names into the DCN316 register map used by firmware-facing display microcontroller code.

The hardware flows represented by this chunk include DP link/stream configuration, DP training/debug/CRC, MST slot allocation and rate programming, DSC/MSO transport controls, HDMI packet and ACR programming, audio packet/AFMT control, generic secondary packet transmission, AUX/DDC/I2C transactions, HPD and GPIO control, DCIO memory/clock/reset/debug control, performance counter reads, and UNIPHY link macro access.

## State And Persistence

The macros themselves hold no state and allocate no storage. They name registers whose values are persistent hardware state after writes by consumers.

Stateful hardware represented by this chunk includes:

- DisplayPort link configuration, training pattern selection, scrambler state, CRC enable/results, fast-training status, MST/MSE slot-allocation tables, MSO/DSC transport controls, ALPM controls, and secondary packet configuration.
- HDMI/TMDS state including metadata, audio, ACR, VBI/infoframe, generic-packet, general-control, and TMDS control-character programming.
- AFMT audio packet, IEC 60958, ramp, CRC, interrupt, source-control, and memory-power state.
- VPG packet headers/sub-packets and generic-packet update state.
- AUX and I2C engine transaction status, software reply data, interrupt controls, arbitration controls, timeout periods, and firmware/PHY wake status.
- HPD/DDC/GPIO register state, including input/output enable/mask/value registers and pad controls.
- DIO/DCIO clock, memory power, soft-reset, debug, pinstrap, genlock/swaplock, and reference-clock controls.
- `DC_PERFMON18` counter configuration and sampled counter state.
- UNIPHY macro-control reserved register values, which are low-level PHY/link state even though this generated header exposes them under reserved names.

These values persist until overwritten, reset by display or GPU reset paths, affected by power-gating/suspend-resume sequencing, or reinitialized during mode set, link retraining, connector hotplug handling, or DMUB/DC resource reconstruction.

## Dependencies And Integration Points

This chunk depends on the rest of the generated DCN316 register set and on common display block abstractions:

- `dcn_3_1_6_sh_mask.h` supplies companion field shifts and masks for the same registers.
- `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h` are included alongside this header for DPCS link encoder registers in DCN316 resource construction.
- `dcn316_resource.c` defines the base-segment constants and the `BASE(...)` expansion needed to turn `_BASE_IDX` values into final addresses.
- Stream encoder, link encoder, AUX, I2C, DIO, audio, AFMT, VPG, APG, HPD, and DPCS register-list macros come from the AMD display block headers included by `dcn316_resource.c`.
- `amdgpu_dm.c` selects the DCN316 resource pool and DMUB firmware path for matching ASICs, so this generated register map is part of the platform bring-up path.
- `dmub_dcn316.c` uses the same offset naming convention to create DMUB's DCN31-family register descriptor table.

The macro names are the integration contract. Removing or renaming a macro referenced by a register-list initializer causes a build failure. Changing a numeric offset or base index can pass compilation but break runtime register programming.

## Risks And Edge Cases

- The chunk starts and ends on partial logical families. The previous chunk contains the beginning of `DP1`, and the next chunk contains the paired `_BASE_IDX` for `regDCIO_UNIPHY5_UNIPHY_MACRO_CNTL_RESERVED30` plus the remaining UNIPHY5 reserved range. Merge documentation should not treat either family as complete from this chunk alone.
- Instance parity matters. `DP2`-`DP4`, `DIG1`-`DIG4`, `AFMT0`-`AFMT4`, `VPG0`-`VPG4`, `AUX0`-`AUX4`, HPD/DDC channels, and UNIPHY0-5 are structurally repeated. A generation error affecting only one instance may appear only on a specific connector, stream encoder, or PHY lane.
- Offsets and base indices are coupled. Every offset in this range pairs with base index `2`; changing either side can silently move accesses into unrelated MMIO space.
- Some registers are status or latch registers rather than plain configuration. AUX transaction status, HPD interrupt state, DP CRC results, perfmon counters, AFMT interrupts, and DIO/DCIO debug readback require correct read/clear/enable ordering in consumers.
- Reserved UNIPHY macro-control registers are especially risky because their semantic meaning is not visible in the generated name. Code should rely on the established link encoder/PHY abstractions instead of open-coding writes to those offsets.
- DP and HDMI packet-control registers affect protocol-visible data. Incorrect offsets can break audio, infoframes, HDR/metadata transport, MST allocation, DSC/MSO transport, or link training in ways that may depend on monitor capability.
- AUX/I2C and HPD/GPIO offsets are on the connector-discovery path; mistakes can look like EDID read failures, hotplug failures, or intermittent link training rather than a straightforward register-map bug.

## Test Signals

Useful validation signals for this chunk are mostly build, generated-header parity, and hardware display tests:

- Build the DCN316 AMDGPU display objects to catch missing or renamed `DP*`, `DIG*`, `AFMT*`, `VPG*`, `DP_AUX*`, `DC_GPIO*`, `DCIO*`, and `UNIPHY*` macros referenced by register-list initializers.
- Run generated-header consistency checks that every `reg...` offset in this range has a matching `reg..._BASE_IDX`, paying special attention to the line-range boundary where `regDCIO_UNIPHY5_UNIPHY_MACRO_CNTL_RESERVED30_BASE_IDX` is outside this chunk.
- Compare repeated instance families for expected stride/parity: `DP2`/`DP3`/`DP4`, `DIG1`/`DIG2`/`DIG3`/`DIG4`, `AFMT0`-`AFMT4`, `VPG0`-`VPG4`, `AUX0`-`AUX4`, and UNIPHY reserved blocks.
- Exercise connector hotplug, HPD interrupt handling, EDID reads over DDC/AUX, DP link training at multiple link rates/lane counts, AUX retry/timeout paths, and suspend/resume connector rediscovery.
- Exercise DP MST, MSE slot-allocation updates, MSO and DSC transport control, ALPM, DP secondary data/audio timestamps, metadata transmission, and DP CRC/debug paths.
- Exercise HDMI/TMDS output with audio, ACR for 32/44.1/48 kHz families, AVI/audio/vendor infoframes, generic packets, deep color, and TMDS test/CRC/debug paths.
- Exercise AFMT and VPG packet paths, including audio CRC/status/interrupt handling and generic packet frame-update behavior.
- Exercise DCIO/UNIPHY link encoder routing on every physical transmitter and validate that channel crossbar/link-control programming matches the selected connector.
- Use perfmon18 readback with a known event selection to validate counter enable/trigger/current-value/high-low register addressing.

## Open Questions For Merge Lane

- Confirm the previous chunk documents the start of `DP1` through `regDP1_DP_SEC_FRAMING2`.
- Confirm the next chunk completes `UNIPHY5` reserved registers 30-57 and captures the missing base-index macro for `RESERVED30`.
- In the final per-file report, group this slice as part of the DCN316 DIO/DCIO/link-encoder offset map rather than as standalone executable code.
