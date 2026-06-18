# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 34690-37088

## Scope

This chunk is a generated AMD DCN 3.0.2 ASIC register shift/mask header slice. It contributes preprocessor constants only: 2,171 `#define`s over 212 register names, with 1,093 `__SHIFT` constants and 1,078 `_MASK` constants. There are no C functions, structs, storage objects, or executable control flow in the chunk. The chunk starts at the tail of `DP0_DP_DPHY_FAST_TRAINING_STATUS`, covers the rest of the DIO/DIG0 and DIO/DIG1 display encoder register field map, and ends in the `VPG2_VPG_GSP_FRAME_UPDATE_CTRL` definitions.

## Purpose

The file provides the bit layout contract for Dimgrey Cavefish/DCN 3.0.2 display hardware registers. This chunk specifically maps field positions and bit masks for DisplayPort, HDMI/DIG, VPG generic secondary packets, AFMT audio formatter, DME metadata, and related display encoder control/status registers. Runtime driver code does not hard-code these numeric bit positions directly; it builds shift and mask tables from these generated names and passes those tables into reusable DCN 3.0 display block implementations.

## Register Areas Covered

- `DP0_*`: completes the DisplayPort instance 0 group, including secondary-data-packet control (`DP_SEC_CNTL*`), audio M/N and timestamp fields, MST/MSE allocation and status, MSA timing parameters, MSO controls, DSC packet controls, data-bypass controls, VBID miscellaneous fields, adaptive link power management (`DP_ALPM_CNTL`), and generic secondary packet controls `DP_GSP8_CNTL` through `DP_GSP11_CNTL`.
- `VPG1_*`: video packet generator instance 1 generic-packet access/data, frame-update and immediate-update controls for generic packets 0-14, generic packet conflict/status bits, memory power bits, ISRC access/data, and MPEG info registers.
- `AFMT1_*`: audio formatter instance 1 VBI/audio packet controls, audio info bytes, IEC 60958 channel-status registers, CRC/ramp/status fields, audio source selection, infoframe update, and memory power fields.
- `DME1_*`: metadata engine instance 1 enable, HUBP requestor id, stream type, memory light-sleep control, and memory power state fields.
- `DIG1_*`: digital front-end/output encoder instance 1 HDMI and TMDS control/status, generic HDMI packet controls 0-14, audio clock regeneration packets, infoframe controls, output CRC, test/random patterns, FIFO status, backend enable, lane enable, and force-disable fields.
- `DP1_*`: DisplayPort instance 1 link, pixel format, MSA, stream, DPHY training, PHY symbol/CRC/scramble controls, secondary packet/audio/MST/DSC/MSO/data-bypass/metadata/ALPM/GSP fields.
- `VPG2_*`: starts video packet generator instance 2, covering generic packet access/data and most of `VPG2_VPG_GSP_FRAME_UPDATE_CTRL`; the next chunk continues this VPG2 block.

## Important API and Type Contracts

This chunk's "API" is the macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the right-shift count for extracting or inserting a hardware bitfield.
- `<REGISTER>__<FIELD>_MASK` gives the register-width bit mask for that field.
- Register comments such as `//DP1_DP_SEC_CNTL` and address-block comments group fields by hardware block. The actual register addresses live in `dcn_3_0_2_offset.h`; this header supplies only field layout.

The values are consumed through macro indirection in `display/dc/resource/dcn302/dcn302_resource.c`:

- `SF(reg_name, field_name, post_fix)` expands to `.field_name = reg_name ## __ ## field_name ## post_fix`, so generated constants initialize typed shift/mask structs.
- `SRI(reg_name, block, id)` binds per-instance register addresses from the offset header, while this chunk supplies matching field layouts.
- `DCN3_VPG_MASK_SH_LIST(__SHIFT/_MASK)` and `DCN3_AFMT_MASK_SH_LIST(__SHIFT/_MASK)` initialize `struct dcn30_vpg_shift`, `struct dcn30_vpg_mask`, `struct dcn30_afmt_shift`, and `struct dcn30_afmt_mask`.
- `SE_COMMON_MASK_SH_LIST_DCN30(__SHIFT/_MASK)` initializes `struct dcn10_stream_encoder_shift` and `struct dcn10_stream_encoder_mask` for DP/HDMI/DIG stream encoder operations.

The practical dependent types are defined outside this generated header, especially in `display/dc/dcn30/dcn30_vpg.h`, `display/dc/dcn30/dcn30_afmt.h`, and `display/dc/dio/dcn30/dcn30_dio_stream_encoder.h`.

## Control Flow and Runtime Use

The chunk has no local branches or calls. Runtime control flow enters through DCN 3.0.2 resource creation:

1. `dcn302_resource.c` includes `dcn_3_0_2_offset.h` and this `dcn_3_0_2_sh_mask.h`.
2. Static register arrays and shift/mask structs are initialized at compile time using the generated constants.
3. `dcn302_resource_construct()` creates the DIO resource pool and stream encoders.
4. `dcn302_stream_encoder_create()` maps a DIG engine id to VPG and AFMT instances, calls `dcn302_vpg_create()` and `dcn302_afmt_create()`, and passes the resulting register/shift/mask tables to `dcn30_dio_stream_encoder_construct()`.
5. Later display operations use the reusable encoder, VPG, and AFMT methods to program DP secondary packets, HDMI infoframes, audio packets, DSC PPS packets, metadata packets, MST slot allocation, FIFO/status handling, and related hardware controls via these field definitions.

## State and Persistence

All state represented by this chunk is hardware register state. The header itself persists no software state and allocates no memory. Fields ending in `_PENDING`, `_STATUS`, `_ACK`, `_OCCURED`, `_CLR`, `_UPDATE`, or `_SEND_ACTIVE` are status/handshake bits in display hardware. Examples include VPG frame/immediate update pending bits, DP GSP send pending/deadline-missed bits, DP fast-training complete/ack bits, FIFO error/ack bits, and generic packet conflict clear/status bits. Misprogramming these fields can leave the driver waiting for an update, failing to clear a status, or writing a control bit into the wrong hardware field.

## Dependencies and Integration Points

- Depends on the matching DCN 3.0.2 register offset header for `mm...` register addresses and base indices.
- Depends on `dcn302_resource.c` macro glue (`SF`, `SRI`, `BASE`) to convert generated constants into block-specific tables.
- Integrates with DCN 3.0 reusable implementations for stream encoder, VPG, AFMT, DCE audio, link encoder, and resource-pool construction.
- The DP/HDMI/VPG/AFMT/DME definitions are part of the display path used by AMDGPU DC for modeset, audio enablement, info packet programming, DSC metadata, MST/MSO behavior, link training support, and power-management controls.
- Instance-specific groups (`DP0`, `DP1`, `DIG1`, `VPG1`, `AFMT1`, `DME1`, partial `VPG2`) must stay aligned with the instance numbering used by `VPG_DCN3_REG_LIST(id)`, `AFMT_DCN3_REG_LIST(id)`, and `SE_DCN3_REG_LIST(id)`.

## Risks

- Generated-header drift is the main risk: if masks/shifts do not match the hardware spec or the paired offset header, the compiler still succeeds but runtime register writes target wrong bits.
- Field-name drift breaks macro expansion at build time. For example, a missing `DP0_DP_SEC_CNTL__DP_SEC_GSP0_ENABLE_MASK` would break `SE_COMMON_MASK_SH_LIST_DCN30(_MASK)`.
- Instance asymmetry is risky. The generic mask/shift tables are often built from instance 0 names and reused across instances, so the bit layouts for `DP0`/`DP1`, `VPG0`/`VPG1`/`VPG2`, and `AFMT0`/`AFMT1` must remain equivalent where the common structs assume equivalence.
- Status/control bit confusion is possible because adjacent fields often pair command and pending bits, such as frame update versus frame update pending or send versus send pending.
- This chunk cuts off in the middle of the `VPG2` block, so whole-file analysis must reconcile the continued VPG2 definitions in the next chunk.

## Test and Validation Signals

- Compile coverage is strong for referenced names: missing or renamed macros fail initialization of DCN 3.0.2 shift/mask structs in `dcn302_resource.c`.
- Runtime smoke signals include successful modesets on DCN 3.0.2 hardware, DP link training, HDMI and DP audio, HDMI infoframes, DP secondary data packets, DSC PPS packet delivery, MST/MSO operation, and absence of FIFO/link-training/status timeout errors.
- Debugging signals include register dumps for DP/DIG/VPG/AFMT blocks, packet update pending bits clearing, GSP send status progressing, and expected audio/video info packets observed by sink-side compliance tools.
- Regression tests should compare generated mask/shift values with the authoritative ASIC register database, because many errors in this header are semantically invisible to normal build tests.
