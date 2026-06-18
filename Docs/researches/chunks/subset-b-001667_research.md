# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 27468-29926

## Purpose

This chunk is part of AMD's generated DCN 2.1 register field mask header. It defines preprocessor constants for display timing generator / output timing generator (OTG) register bit positions and masks. The covered range starts in the `dce_dc_optc_otg0_dispdec` block, contains the complete repeated field definitions for `dce_dc_optc_otg1_dispdec` and `dce_dc_optc_otg2_dispdec`, and ends at the first timing fields of `dce_dc_optc_otg3_dispdec`.

The file does not implement executable logic. Its purpose is to provide stable compile-time metadata used by AMDGPU display code to construct register access tables and field-update helpers for Renoir/DCN21 hardware.

## Chunk Shape

- Line range: 27468-29926.
- Macro volume in this range: 2144 `#define` entries, consisting of 1071 `*_SHIFT` definitions and 1073 `*_MASK` definitions.
- Prefix coverage: late `OTG0` definitions, full `OTG1` and `OTG2` definitions, and the start of `OTG3`.
- Each register field generally appears as a pair:
  - `<REGISTER>__<FIELD>__SHIFT`
  - `<REGISTER>__<FIELD>_MASK`

## Important Register Areas

- Timing geometry: `OTG_H_TOTAL`, `OTG_H_BLANK_START_END`, `OTG_H_SYNC_A`, `OTG_V_TOTAL`, `OTG_V_TOTAL_MIN`, `OTG_V_TOTAL_MAX`, `OTG_V_TOTAL_MID`, `OTG_V_BLANK_START_END`, `OTG_V_SYNC_A`, and related polarity/control fields. These fields describe the horizontal and vertical timing programmed for an active display pipe.
- Dynamic refresh / variable timing: `OTG_V_TOTAL_CONTROL`, `OTG_DRR_CONTROL`, and `OTG_V_TOTAL_LAST_USED_BY_DRR` expose fields used when the driver adjusts vertical totals for DRR/VRR behavior.
- Triggering and synchronization: `OTG_TRIGA_CNTL`, `OTG_TRIGB_CNTL`, manual trigger registers, `OTG_FORCE_COUNT_NOW_CNTL`, `OTG_GSL_CONTROL`, `OTG_GSL_WINDOW_X/Y`, and `OTG_GSL_VSYNC_GAP` describe trigger source selection, pipe selection, edge detection, GSL master/slave behavior, and sync windows.
- Master/update locking: `OTG_UPDATE_LOCK`, `OTG_MASTER_UPDATE_LOCK`, `OTG_GLOBAL_CONTROL0/1/2/3`, and `OTG_VUPDATE_KEEPOUT` define fields that gate when timing and pipe state updates are applied.
- Interrupt and event status: `OTG_GLOBAL_SYNC_STATUS`, `OTG_VERTICAL_INTERRUPT0/1/2_CONTROL`, `OTG_V_TOTAL_INT_STATUS`, `OTG_VSYNC_NOM_INT_STATUS`, and `OTG_RANGE_TIMING_INT_STATUS` define enable, status, event, clear, mask, and interrupt-type bits.
- Display state/status readback: `OTG_STATUS`, `OTG_STATUS_POSITION`, `OTG_NOM_VERT_POSITION`, `OTG_STATUS_FRAME_COUNT`, `OTG_STATUS_VF_COUNT`, `OTG_STATUS_HV_COUNT`, interlace/stereo status, pixel readback registers, and snapshot status/control/position/frame fields.
- Blank/black/color handling: `OTG_BLANK_CONTROL`, `OTG_BLANK_DATA_COLOR`, `OTG_BLANK_DATA_COLOR_EXT`, `OTG_BLACK_COLOR`, and `OTG_BLACK_COLOR_EXT` describe color channel packing and blanking behavior.
- CRC and validation: `OTG_CRC_CNTL`, `OTG_CRC_CNTL2`, CRC window controls, CRC data registers, and CRC signature mask controls define the hardware CRC capture and readback surfaces used for display validation.
- Pipe update tracking: `OTG_PIPE_UPDATE_STATUS` exposes pending/taken/clear bits for flip, DC register update, cursor update, and vupdate keepout status.
- Miscellaneous control: `OTG_CLOCK_CONTROL`, `OTG_REQUEST_CONTROL`, `OTG_DSC_START_POSITION`, `OTG_STATIC_SCREEN_CONTROL`, `OTG_3D_STRUCTURE_CONTROL`, `OTG_PIPE_ABORT_CONTROL`, and `OTG_SPARE_REGISTER`.

## APIs, Types, and Macro Contracts

This chunk exports C preprocessor symbols only. There are no functions, structs, enums, storage objects, or inline helpers in the chunk itself. The important API contract is naming consistency:

- Register names are prefixed by hardware instance, for example `OTG1_OTG_GLOBAL_SYNC_STATUS`.
- Field names are embedded after a double underscore, for example `VSTARTUP_INT_EN`.
- Consumers concatenate tokens to form `OTG<n>_<register>__<field>_MASK` or `OTG<n>_<register>__<field>__SHIFT`.

The DCN21 display stack includes this header from:

- `display/dmub/src/dmub_dcn21.c`, where `FD_MASK` and `FD_SHIFT` use generated masks/shifts for DMUB register tables.
- `display/dc/irq/dcn21/irq_service_dcn21.c`, where IRQ table macros form OTG mask names for vblank, vupdate-no-lock, and vertical-line interrupt programming.
- `display/dc/resource/dcn21/dcn21_resource.c`, where DCN21 resource construction pulls generated addresses and masks into hardware object register tables.
- DCN21 GPIO factory/translator files, for shared generated DCN21 register metadata outside this specific OTG chunk.

The chunk also aligns with the common OPTC abstraction under `display/dc/optc/dcn10/dcn10_optc.h`, whose field lists include many of these names (`OTG_MASTER_UPDATE_LOCK`, `OTG_V_TOTAL`, `OTG_TRIGA_CNTL`, CRC fields, DRR fields, update-lock DB fields). Those field lists are used to populate typed mask/shift tables for timing generator code.

## Control Flow and Runtime Behavior

There is no runtime control flow in this header. Runtime behavior appears when other compilation units use these constants in register helpers:

- IRQ setup in `irq_service_dcn21.c` maps DC IRQ sources to OTG registers. For example, `vupdate_no_lock_int_entry(reg_num)` expands to an `OTG<reg_num>_OTG_GLOBAL_SYNC_STATUS` enable bit `VUPDATE_NO_LOCK_INT_EN` and ack bit `VUPDATE_NO_LOCK_EVENT_CLEAR`. `vblank_int_entry(reg_num)` similarly uses `VSTARTUP_INT_EN` and `VSTARTUP_EVENT_CLEAR`.
- Resource and OPTC initialization code uses generated addresses from the matching `dcn_2_1_0_offset.h` plus these masks/shifts to build per-pipe register tables. Later display operations use those tables to program timing, triggers, blanking, CRC capture, update locks, and dynamic vertical totals.
- Register helper macros normally read/modify/write only the masked field, so the correctness of every write depends on the mask and shift matching the hardware register layout exactly.

## State and Persistence

The macros are immutable compile-time constants. They do not persist state directly.

The state they address is hardware state in DCN OTG blocks:

- Programmed timing state persists in MMIO registers until overwritten, reset, or power-gated.
- Event/status bits such as vstartup, vupdate, range timing update, and flip/update-taken bits can be sticky until cleared through corresponding `*_CLEAR` fields.
- Master/update lock fields can delay or gate when pending pipe state becomes visible to scanout.
- CRC data, frame counters, current position counters, and interlace/stereo status are readback-oriented state derived from live scanout.

The chunk therefore affects persistence indirectly by determining which bits the driver writes or clears in hardware registers.

## Dependencies and Integration Points

- Depends on the matching generated offset header `dcn_2_1_0_offset.h`; masks/shifts alone do not identify MMIO addresses.
- Depends on generated base segment symbols from `renoir_ip_offset.h` in DCN21 users.
- Integrated through AMD display register helper macros such as `FD_MASK`, `FD_SHIFT`, field-list `SF(...)` expansion, and IRQ table token concatenation.
- Closely coupled to DCN21/Renoir hardware generation. Copying these definitions to a different DCN generation without matching offsets and hardware field layout would be unsafe.
- Related semantic enums for some fields live in ASIC enum headers such as `navi10_enum.h` and `soc24_enum.h`, but this header itself only provides bit layout.

## Risks

- A wrong mask or shift silently targets the wrong hardware bits, causing display timing corruption, missed interrupts, stuck update locks, CRC mismatches, bad DRR behavior, or blank/black-frame errors.
- Because consumers build symbol names through token concatenation, renaming a macro or dropping one field becomes a compile-time failure in dependent DCN21 code.
- Instance repetition is easy to corrupt mechanically. `OTG1` and `OTG2` must preserve the same field layout while binding to their own instance addresses from the offset header.
- Status and clear bits share registers in several areas. Incorrect masks for `*_EVENT_CLEAR`, `*_TAKEN_CLEAR`, or interrupt clear fields can accidentally clear unrelated events or leave sticky interrupts asserted.
- Update lock and GSL fields are timing-sensitive. Bad values can make pipe updates occur outside intended vblank/vupdate windows, causing visible artifacts or synchronization loss across pipes.

## Test Signals

- Build signal: DCN21 AMDGPU display objects compile. Missing or renamed symbols should surface in `dmub_dcn21.c`, `irq_service_dcn21.c`, `dcn21_resource.c`, and OPTC register table construction.
- IRQ signal: vblank, vupdate-no-lock, and vertical-line interrupts can be enabled, acknowledged, and do not storm. Relevant masks are in `OTG_GLOBAL_SYNC_STATUS` and `OTG_VERTICAL_INTERRUPT0_CONTROL`.
- Mode-set signal: displays light correctly across OTG0/1/2/3-capable pipes with correct sync polarity, blanking intervals, and frame counters.
- DRR/VRR signal: vertical total min/max/mid programming behaves correctly and `OTG_DRR_CONTROL` readback reflects expected totals.
- Update-lock signal: atomic flips, cursor updates, and DC register updates transition through pending/taken bits in `OTG_PIPE_UPDATE_STATUS` without getting stuck.
- CRC signal: display CRC capture over configured windows produces stable values for static frames and changes predictably when content changes.
- Multi-pipe sync signal: GSL/master update lock paths synchronize pipes without vupdate-no-lock events under synchronized display scenarios.
