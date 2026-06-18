# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h lines 7653-10193

## Scope And Purpose

This chunk is part of the generated AMD DCN 3.2.0 register-offset header. It contains C preprocessor constants only: `reg...` symbols for MMIO register offsets and matching `reg..._BASE_IDX` symbols used by the Display Core register-access helpers. There are no functions, structs, enums, branches, loops, allocations, locks, or software-owned state objects in this range.

The chunk starts in the middle of the OPP/FMT2 register block at `regFMT2_FMT_CLAMP_COMPONENT_G` and ends in the middle of the DIG4 HDMI audio-clock-recovery block at `regDIG4_HDMI_ACR_44_0`. Within those boundaries it covers the later OPP pipe/output formatter registers, ODM/OPTC input and timing-generator registers, HPD interrupt/control registers, and five DisplayPort/DIG link encoder instances. The constants are hardware ABI: they bind DCN32 display code to concrete register addresses for modeset timing, output-pixel formatting, hotplug handling, stream encoding, link training, DisplayPort secondary-data packets, HDMI packets, CRC/debug readback, and related power/clock controls.

The range contains 2,393 `#define` lines: 1,197 register-offset macros and 1,196 `_BASE_IDX` macros. Almost every register offset has a paired base-index macro. The one-count difference is due to the chunk boundary starting after `regFMT2_FMT_CLAMP_COMPONENT_R_BASE_IDX` and before `regFMT2_FMT_CLAMP_COMPONENT_G`.

## Hardware Surface Covered

The first portion finishes output-pixel-processor coverage for pipe instances 2 and 3:

- `FMT2` and `FMT3` formatter registers for clamp components, dynamic expansion, bit depth, dither seeds, clamp control, side-by-side stereo, 4:2:0 memory mapping, and 4:2:2 handling.
- `OPPBUF2` and `OPPBUF3` output buffer control and 3D parameter registers.
- `OPP_PIPE2` and `OPP_PIPE3` pipe-control registers.
- `OPP_PIPE_CRC2` and `OPP_PIPE_CRC3` CRC control, mask, and result registers.
- `DPG3` display pattern generator control, ramp, dimensions, color, offset, and status.
- `DSCRM0` through `DSCRM3` DSC forward-configuration registers.
- `OPP_TOP_CLK_CONTROL` and `OPP_ABM_CONTROL` top-level OPP clock and ABM control surfaces.

The middle portion covers OPTC/ODM display timing and composition input:

- `ODM0` through `ODM3` input global control, data-source select, data-format control, bytes-per-pixel, width control, input clock, memory config, and spare registers.
- `OTG0` through `OTG3`, each with 104 offset macros for horizontal/vertical timing, blanking, sync, total/min/max/mid, trigger controls, stereo/interlace, pixel readback, status/counters, vertical interrupts, CRC windows/data/masks, static screen detection, 3D structure, global sync lock/control, GSL windows, VUPDATE keepout, DRR timing/control, DTO, request control, DSC start position, pipe update status, and spare registers.
- `GSL_SOURCE_SELECT`, `GSL_GROUP_ENABLE`, `GSL_MASTER_UPDATE_LOCK`, and OPTC misc/debug/spare registers.

The last portion covers DIO hotplug and stream/link encoder registers:

- `HPD0` through `HPD4` hotplug interrupt status, RX interrupt timer, RX interrupt control, HPD control, and toggle filter control.
- `DP0` through `DP4`, each with 83 DisplayPort register offsets. These include link control, training pattern selection, voltage/pre-emphasis pattern controls, DPHY control/status/CRC/fast-training, MSA timing and colorimetry, video M/N and stream controls, secondary-data packet controls, audio M/N, timestamps, MST/MSE rate and slot-allocation registers, DSC/MSO controls, metadata transmission, ALPM and AUX-less ALPM registers, generic SDP controls, and DP database controls.
- `DIG0` through `DIG3`, each with 53 stream encoder register offsets for DIG front-end control, output CRC/test patterns, FIFO controls, HDMI metadata/control/status/audio/ACR/VBI/infoframe/generic-packet controls, guard-band control, AFMT control, backend enable/control, TMDS controls, stereosync, sync character patterns, clock control, and force-disable.
- `DIG4` is partial in this chunk. It starts at `regDIG4_DIG_FE_CNTL` and reaches `regDIG4_HDMI_ACR_44_0`; its later HDMI ACR, AFMT, backend, TMDS, clock, and force-disable definitions continue after line 10193.

## Important Macros And API Shape

The exported API is the generated macro namespace consumed by DCN32 resource tables:

- `reg<INSTANCE>_<REGISTER>` gives the register offset value, for example `regOTG0_OTG_H_TOTAL`, `regODM0_OPTC_INPUT_GLOBAL_CONTROL`, `regDP0_DP_LINK_CNTL`, `regDIG0_DIG_FE_CNTL`, and `regHPD0_DC_HPD_INT_STATUS`.
- `reg<INSTANCE>_<REGISTER>_BASE_IDX` gives the register base index used by low-level MMIO helpers to select the right address space/base. In this chunk the display engine blocks use base index `2`.
- Address-block comments document the generated hardware block grouping and base address for each repeated instance.
- The register-offset header must be paired with the matching `dcn_3_2_0_sh_mask.h` field layout. Offset macros locate registers; shift/mask macros describe fields inside those registers.

The main instance families are regular and index-driven:

- OPP/FMT/DPG/OPPBUF definitions are used to build per-OPP register tables.
- ODM/OTG definitions are used to build per-OPTC register tables.
- HPD definitions are used to build per-connector hotplug GPIO/register tables.
- DP and DIG definitions are used to build link encoder and stream encoder register tables.

The chunk has partial boundaries. `FMT2` lacks the preceding `FMT_CLAMP_COMPONENT_R` line in this work item, and `DIG4` lacks the final part of the instance. Merge/reconciliation should combine neighboring chunks before treating those blocks as complete.

## Control Flow And State Behavior

This header has no executable control flow. Runtime flow is table-driven:

1. DCN32 resource code includes `dcn/dcn_3_2_0_offset.h`.
2. Register-list macros such as `OPP_REG_LIST_DCN30_RI(id)`, `OPTC_COMMON_REG_LIST_DCN3_2_RI(inst)`, `HPD_REG_LIST_RI(id)`, `SE_DCN32_REG_LIST_RI(id)`, and `LE_DCN31_REG_LIST_RI(id)` expand to generated register-offset symbols from this header.
3. Resource initialization fills register-address structures such as `dcn20_opp_registers`, `dcn_optc_registers`, `dcn10_link_enc_hpd_registers`, `dcn10_stream_enc_registers`, and `dcn10_link_enc_registers`.
4. Display Core objects perform read/write or read/modify/write operations through those tables, while companion shift/mask tables determine bit packing.
5. Hardware latches configuration or exposes status through the addressed registers.

The state represented by this chunk is hardware state, not persistent software state. Persistent or semi-persistent hardware configuration includes timing generator totals/sync/blanking, ODM input source and pixel format, OPP formatter bit depth/dither/clamp setup, DSC forwarding selection, DP link/training/MSA/video-stream controls, HDMI packet and audio clock-regeneration configuration, HPD filtering/control, and clock/power gating settings. Volatile state includes OTG frame/count/status readbacks, CRC results, HPD interrupt status, DP DPHY status/CRC/fast-training status, MSE status, HDMI status, DIG output CRC results, and debug/readback registers.

The macros do not encode sequencing, access width, polling requirements, clear-on-write behavior, or read-only/write-only semantics. Callers must still observe modeset locks, link-training order, vblank/update-lock sequencing, HPD interrupt rules, and register field preservation.

## Dependencies And Integration Points

Primary local users include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`, which includes this offset header and initializes DCN32 register tables for AFMT, stream encoders, HPD, link encoders, OPP, and OPTC.
- `drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.h`, which defines the `*_RI` register-list macros that expand to register-offset/base-index symbols from this generated header.
- `drivers/gpu/drm/amd/display/dc/opp/dcn20` and `display/dc/dcn30/dcn30_opp.h`, which define OPP/DPG register structures and field tables consumed by `OPP_REG_LIST_DCN30_RI(id)`.
- `drivers/gpu/drm/amd/display/dc/optc/dcn30` and related OPTC code, which consume the OTG/ODM timing, update-lock, CRC, DRR, and GSL registers exposed through `OPTC_COMMON_REG_LIST_DCN3_2_RI(inst)`.
- `drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h`, which defines link encoder register and field lists for DP/DIG link-control surfaces.
- `drivers/gpu/drm/amd/display/dc/dcn30/dcn30_afmt.h` and stream encoder code, which integrate HDMI/DP packet, audio, metadata, MSA, and DIG front-end registers.
- `drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c` and IRQ code, which include this header for HPD and interrupt register mapping.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`, `display/dc/irq/dcn32/irq_service_dcn32.c`, `display/dc/gpio/dcn32/*`, and `amdgpu/gmc_v11_0.c`, which also include the DCN32 generated offset header for low-level DCN32 register access or service initialization.

These offsets are meaningful only in combination with the matching generated shift/mask header and the DCN register access macros (`SR`, `SRI`, `SR_ARR`, `SRI_ARR`, and related RI variants). A compile can succeed with wrong numeric offsets, so behavioral validation matters as much as symbol presence.

## Risks And Maintenance Notes

- Numeric drift from the authoritative DCN 3.2.0 register database is the main risk. A wrong offset or base index can program the wrong MMIO register while still compiling.
- Repeated instances are easy to corrupt during generation or manual patching. Swapping `DP2`/`DP3`, `DIG3`/`DIG4`, `OTG1`/`OTG2`, or `ODM` instance numbers would misroute a display pipe or link encoder.
- This chunk starts inside `FMT2` and ends inside `DIG4`; final per-file research should not infer complete FMT2 or DIG4 coverage from this chunk alone.
- OTG/ODM registers are modeset-critical. Incorrect timing, blanking, sync, update-lock, DRR, or DSC-start-position offsets can cause blank screens, page-flip stalls, tearing, underflow, or timing interrupts in the wrong place.
- DP/DIG registers are link-critical. Incorrect link-control, training, DPHY, MSA, DSC, metadata, ALPM, or HDMI packet offsets can break link training, MST allocation, DSC streams, audio, HDR/metadata packets, or low-power entry/exit.
- HPD registers are interrupt-sensitive. Misaddressed status/control/toggle-filter registers can cause missed hotplug events, interrupt storms, or failure to debounce RX/HPD transitions.
- CRC and status registers are often used for diagnostics and automated tests. Wrong offsets can make validation tools report false failures or mask real display corruption.
- `_BASE_IDX` values are part of the address calculation contract. Treating them as boilerplate can break access on blocks that share names but live under different register bases.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build coverage for AMDGPU Display Core with DCN32 enabled. This catches missing or malformed generated symbols used by resource table expansion.
- Generated-header comparison against the authoritative DCN 3.2.0 register specification, with special attention to repeated `OTG0..3`, `ODM0..3`, `HPD0..4`, `DP0..4`, and `DIG0..4` instance strides.
- Boot and modeset smoke tests on DCN32 hardware with all available pipes: single-display, multi-display, clone/extend, resolution and refresh-rate changes, suspend/resume, and page-flip stress.
- DisplayPort link-training tests across lane counts/rates, MST and SST, DSC enabled/disabled, fast training, ALPM/AUX-less ALPM, and retraining after hotplug.
- HDMI tests covering video modes, audio clock regeneration, infoframes, generic packets, metadata packets, and TMDS/DIG backend enable/disable.
- HPD tests for plug/unplug, short pulses, RX interrupt handling, debounce/toggle filtering, and interrupt storm resistance.
- CRC/debug tests using OPP pipe CRC, OTG CRC windows/data, DP DPHY CRC, and DIG output CRC to confirm register dumps and validation tooling read the intended blocks.
- Variable refresh/DRR and vblank/update-lock tests, since this chunk includes OTG vertical interrupt, DRR, master update lock, GSL, and timing-status registers.

## Open Questions For Merge

- Merge should connect this chunk to the previous FMT2/OPP blocks and the next DIG4 continuation so partial-boundary blocks are described accurately at the per-file level.
- The final report should distinguish DCN32 legacy stream/DIG/DP encoder coverage from HPO DP encoder coverage, because this chunk covers the DP/DIG path while DCN32 resource code also initializes HPO-specific tables outside this address range.
