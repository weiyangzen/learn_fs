# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 12416-14925

## Scope And Purpose

This chunk is a generated AMD DCN 3.0.3 shift/mask register header slice. It does not contain executable functions or C types; instead it defines preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for memory-mapped display registers. The matching register addresses live in `dcn_3_0_3_offset.h`; this file supplies the field layout used by the AMD display core helpers to compose, update, read, and acknowledge hardware registers safely.

The slice starts at the end of the `CM1_CM_GAMCOR_RAMB_REGION_32_33` region table, covers most of the DPP1 color-management register fields, crosses several OPP/OPTC address blocks, and ends partway through `OTG0_OTG_GLOBAL_SYNC_STATUS`. In this range there are 2,125 `#define` entries and 349 register/comment markers. The register groups covered here are:

- `CM1_*` color-management fields for blend gamma, shaper, 3D LUT, HDR multiplier, memory power control/status, coefficient format, dealpha, and debug index/data.
- `DC_PERFMON8_*` and `DC_PERFMON9_*` display performance monitor counters and control/status fields.
- `FMT0_*` and `FMT1_*` output formatter fields for clamp, dynamic expansion, bit depth, spatial/temporal dithering, stereo, 4:2:0 memory mapping, and 4:2:2 output.
- `DPG0_*` and `DPG1_*` display pattern generator controls, dimensions, colors, offset, and status.
- `OPPBUF0_*`, `OPPBUF1_*`, `OPP_PIPE0_*`, `OPP_PIPE1_*`, `OPP_PIPE_CRC0_*`, `OPP_PIPE_CRC1_*`, `OPP_TOP_*`, `OPP_ABM_CONTROL`, and `DSCRM0/1_*` output-pixel-processor buffer, pipe, CRC, top clock, ABM, and DSC forwarding fields.
- `ODM0_*` and `ODM1_*` OPTC input fields for underflow, data source, format, bytes per pixel, width, clock, memory config, and spare registers.
- `OTG0_*` timing generator fields for horizontal/vertical timing, triggers, force-count, flow, stereo/3D, status snapshots, interrupts, update locking, blank color, vertical interrupts, CRC, static screen, GSL vsync gap, clock/reset, and vstartup/vupdate/vready/global-sync status.

## Important APIs, Types, And Macros

The public surface of this chunk is macro names. Each field appears as a pair such as `OTG0_OTG_H_TOTAL__OTG_H_TOTAL__SHIFT` and `OTG0_OTG_H_TOTAL__OTG_H_TOTAL_MASK`, or as similarly structured register/field pairs for CM, OPP, ODM, FMT, DPG, and perfmon blocks. AMD display code uses token-pasting helper macros to turn these constants into typed register tables:

- `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)` in DMUB code expand against these definitions when constructing common DMUB register field tables for DCN303.
- `SF(reg, field, mask_sh)` and `OPP_SF(reg, field, mask_sh)` expand to either the shift or mask constant and populate per-block shift/mask structs.
- `REG_SET`, `REG_SET_N`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, and `REG_READ` call sites in the display core depend on these shift/mask values when writing packed register fields.
- IRQ construction macros in `irq_service_dcn303.c`, especially `IRQ_REG_ENTRY`, paste block, instance, register, and field names to select enable, clear, and status bits.

There are no C structs declared in the header chunk, but it is consumed into structs elsewhere. In `dcn303_resource.c`, the DCN303 resource pool builds `dcn3_dpp_shift/mask`, `dcn20_opp_shift/mask`, `dcn_optc_shift/mask`, `dcn30_mpc_shift/mask`, and `dce_hwseq_shift/mask` instances from macros that ultimately resolve into this header. The same resource construction creates DPP, OPP, timing-generator, MPC, DSC, hubp, and hardware-sequencer objects with these field layouts.

## Register Areas Covered

The `CM1` section defines DPP1 color-management field layouts. The blend gamma (`CM_BLNDGAM`) block includes mode/select/current status, LUT index/data/control, RAM A/B PWL start/end/slope/base/offset values per RGB channel, and 34 region definitions for each RAM. Region registers pack two regions per 32-bit register, using low bits for one region's LUT offset and segment count and high bits for the next region. The shaper block has similar RAM A/B region tables plus per-channel offsets/scales and LUT write masks. The 3D LUT block defines mode, index, data, 30-bit data, read/write control, output normalization, and RGB output offsets. Memory power fields (`CM_MEM_PWR_CTRL`, `CM_MEM_PWR_STATUS`, `CM_MEM_PWR_CTRL2`, `CM_MEM_PWR_STATUS2`) expose force, disable, light/deep sleep, shutdown, and status bits for the color-management RAMs.

The `DC_PERFMON8` and `DC_PERFMON9` sections define event select, counted-value selection, increment/run control, active/status, counter selection, perfmon enable/reset/start mode, counter state, and high/low counter value fields. These are instrumentation surfaces rather than normal display programming paths, but a bad field definition can still break diagnostics or performance counter collection.

The `FMT0` and `FMT1` blocks describe output formatter state for two output pixel processors. They include per-component clamp min/max, dynamic expansion enable/mode, pixel encoding, subsampling mode/order, bit-depth truncation and dithering controls, random seeds, clamp format, side-by-side stereo, 4:2:0 memory power force, and 4:2:2 output control. `dcn10_opp.h` maps a subset of these fields into OPP masks/shifts used by OPP construction and programming.

The `DPG0` and `DPG1` blocks define display pattern generator enable/source, ramp parameters, dimensions, RGB/YCbCr color values, segment offsets, and status. `OPPBUF0/1` and `OPP_PIPE0/1` cover OPP buffer active width, pixel repetition, segmentation, overlap/padding, 3D active-space parameters, buffer control, and pipe clock enable. `OPP_PIPE_CRC0/1` define CRC enable/source/stereo controls, masks, and CRC result registers. These blocks are useful for output validation, diagnostics, and self-test style paths.

The `ODM0` and `ODM1` sections describe OPTC input and underflow state. The global-control register includes soft reset, underflow interrupt enable/type/status/clear/current, and double-buffer pending. Other registers define data source selection, data format, bytes per pixel, input width, input clock gate/on/enable, memory config, and spare data. These constants feed timing-generator and OPTC code when display data is split or merged across OPP/OTG paths.

The `OTG0` section is the largest in this chunk. It defines the timing generator's core timing fields (`OTG_H_TOTAL`, blank start/end, sync start/end/polarity, vtotal min/mid/max/control, vertical blank/sync), trigger A/B configuration, manual trigger bits, force-count status, flow control, stereo/3D control and status, pixel-data readback, scanout/frame counters, status-position fields, update locks, double-buffer control, blank color, vertical interrupt positions and clear/enable/status bits, CRC control/window/data/signature masks, static-screen detection/control, GSL vsync-gap status, clock gate/reset/busy bits, and the start of global-sync interrupt/status fields.

## Control Flow And Runtime Use

This file has no runtime control flow by itself. Its control-flow impact is indirect and compile-time: register helper macros embed these constants into code that performs runtime MMIO reads and writes.

For resource construction, `dcn303_resource.c` includes `dcn_3_0_3_sh_mask.h` and constructs block-specific shift/mask tables. `dcn303_dpp_create()` passes the DPP table into `dpp3_construct`; `dcn303_opp_create()` passes the OPP table into `dcn20_opp_construct`; `dcn303_timing_generator_create()` passes the OPTC/OTG table into `dcn30_timing_generator_init`; `dcn303_mpc_create()` passes the MPC shift/mask table into `dcn30_mpc_construct`; and `dcn303_hwseq_create()` stores HWSEQ shift/mask pointers. Once constructed, higher-level display operations call `REG_*` helpers through these objects, and the helpers use the shifts/masks from this header to place field values in the correct bits.

For interrupts, `irq_service_dcn303.c` includes the same header and creates `irq_source_info_dcn303`. The vblank and vupdate paths use `OTG_GLOBAL_SYNC_STATUS` fields such as `VSTARTUP_INT_EN`, `VSTARTUP_EVENT_CLEAR`, `VUPDATE_NO_LOCK_INT_EN`, and `VUPDATE_NO_LOCK_EVENT_CLEAR`; vline setup uses `OTG_VERTICAL_INTERRUPT0_CONTROL` fields such as interrupt enable and clear. If a mask in this chunk is wrong, an IRQ source may fail to enable, fail to acknowledge, or acknowledge a neighboring bit.

For CRC and diagnostics, OPTC code such as `optc2_configure_crc()` writes `OTG_CRC_CNTL2` fields for DSC and stream-combine modes, while later OPTC state dump paths read many `OTG_CRC*`, static-screen, global-sync, and status registers. The data path is therefore: display code selects a semantic field, helper macros combine the field's value with this header's mask/shift, then the register access layer writes or reads the packed MMIO word.

## State And Persistence Behavior

The header itself persists no state. The state described by this chunk lives in hardware registers and internal display RAMs:

- Color LUT, shaper, blend gamma, and 3D LUT fields configure persistent DPP color pipeline state until reprogrammed, reset, power-gated, or lost across suspend/resume.
- Memory power-control fields affect whether color-management RAMs are forced on, shut down, or placed into light/deep sleep; incorrect values can corrupt later LUT programming or waste power.
- OPP/FMT/DPG/CRC/ODM/OTG registers hold live display-pipe configuration. Many of these fields are double-buffered or have pending/current status bits so writes may not take effect until a timing boundary.
- Interrupt status and clear fields are edge-sensitive hardware state. Clear bits such as `*_EVENT_CLEAR`, `OTG_VERTICAL_INTERRUPT*_CLEAR`, and CRC pending/status bits should be treated as write-one-to-clear or hardware-defined side-effect fields according to the register spec.
- Counter, CRC, static-screen, snapshot, frame-count, and performance-monitor fields expose observed hardware state and can change asynchronously with scanout.

The persistence boundary is the GPU display hardware, not software storage. Kernel modeset, atomic commits, power management, DMUB firmware interaction, IRQ handlers, and debug/state-dump paths all rely on the field definitions remaining aligned with the ASIC specification.

## Dependencies And Integration Points

This chunk depends on the generated DCN303 offset header for register addresses and on Sienna Cichlid base-index definitions for segment selection. It is directly included by DCN303 DMUB setup, the DCN303 IRQ service, and `dcn303_resource.c`. Through resource construction it integrates with:

- DPP color pipeline code (`dpp3_construct`, DPP register-list macros, color-management and transfer-function programming).
- OPP/output formatting code (`dcn20_opp_construct`, formatter/dither/clamp/OPP buffer and OPP pipe controls).
- OPTC/timing-generator code (`dcn30_timing_generator_init`, vertical interrupts, timing programming, CRC, static screen, GSL, stereo/3D, and global sync).
- IRQ service code that maps DC IRQ source abstractions to register enable/ack/status bits.
- DMUB service register tables built from `DMUB_COMMON_FIELDS`.
- Debug and diagnostics paths that read CRC, static-screen, perfmon, status-position, frame-count, snapshot, and global-sync registers.

The field naming also matches generic macro tables shared across DCN generations. For example, OPP and OPTC helper headers use `FMT0_*`, `OPPBUF0_*`, `OTG0_*`, and `ODM0_*` field names as canonical instance-zero templates and then apply instance-specific register addresses separately. This makes spelling and bit layout compatibility important across the resource-construction layer.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A bad shift or mask still compiles, but writes the wrong bits. For timing and interrupt fields this can produce blank displays, missed vblank/vline/vupdate IRQs, stuck update locks, incorrect vertical-total behavior, or scanout instability. For color-management fields it can produce wrong gamma, shaper, 3D LUT, HDR multiplier, or coefficient behavior, including subtle color corruption that is hard to trace back to a generated constant.

Packed region registers are especially error-prone. Blend-gamma and shaper region definitions store two region offsets/segment counts per word with repeated bit positions (`0x0`, `0xc`, `0x10`, `0x1c`) and masks (`0x000001FF`, `0x00007000`, `0x01FF0000`, `0x70000000`). Any off-by-one region name, copied mask, or skipped region can misalign a PWL LUT segment table while leaving neighboring regions apparently valid.

Status/control registers mix writable control bits with read-only/current/pending/status bits in the same word, such as `CM_BLNDGAM_CONTROL`, `ODM*_OPTC_INPUT_GLOBAL_CONTROL`, `OTG_STATUS`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_CLOCK_CONTROL`, and `OTG_GLOBAL_SYNC_STATUS`. Read-modify-write helpers must use masks precisely so they do not clear or set unrelated status/clear bits.

Interrupt and clear fields have side effects. Misusing `OTG_GLOBAL_SYNC_STATUS` or `OTG_VERTICAL_INTERRUPT*_CONTROL` masks can cause event storms, lost acknowledgements, or stale interrupt status. CRC control also includes one-shot pending bits and multiple data-window/result fields, so register dump and CRC-configuration code must treat control, window, and result registers differently.

Generated header drift is another risk. This file is part of a DCN303-specific hardware ABI; manually editing constants or merging values from nearby DCN versions can compile because names are similar, but the hardware layout may differ. The safest maintenance path is regeneration from the authoritative ASIC register database plus comparison against adjacent generation headers and live hardware behavior.

## Test Signals

There are no unit tests for this header chunk alone. Useful validation signals come from build coverage, hardware bring-up, display functional tests, and diagnostics:

- Compile coverage for DCN303 display code should catch missing or misspelled macro names in `dcn303_resource.c`, `irq_service_dcn303.c`, DMUB setup, and shared OPP/OPTC/DPP macro tables.
- Kernel modeset and atomic-commit tests on DCN303 hardware should verify that DPP, OPP, ODM, and OTG objects construct successfully and can light displays across common resolutions, pixel encodings, refresh rates, stereo/3D disabled/enabled paths, and dynamic refresh behavior.
- IRQ tests or runtime traces should confirm vblank, vertical line, vupdate-no-lock, pflip, and HPD-related IRQ paths enable and acknowledge correctly. The strongest signals for this chunk are vblank/vline events using `OTG_GLOBAL_SYNC_STATUS` and `OTG_VERTICAL_INTERRUPT0_CONTROL`.
- Color pipeline tests should exercise blend gamma, shaper, 3D LUT, HDR multiplier, and LUT RAM A/B programming, then compare CRC or measured output for expected color transforms.
- CRC/debug paths should configure OTG and OPP CRC, read CRC result registers, validate CRC windows, and inspect static-screen/status/snapshot/perfmon dumps without unstable or impossible values.
- Power-management and suspend/resume testing should check CM memory power control/status, OTG clock control, double-buffer pending state, update locks, and reset behavior after display off/on cycles.

Because this is a hardware register-layout header, the most valuable regression signal is not a pure software assertion; it is successful DCN303 display operation with interrupts, color programming, CRC/debug reads, and power transitions all exercising the generated masks and shifts together.
