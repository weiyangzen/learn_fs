# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega10_enum.h lines 1-7650

## Scope

Work item `subset-b-003507` covers the first 7,650 lines of `vega10_enum.h`, a large AMDGPU Vega10 register enum header. The source file is 22,532 lines total, so this is a chunk report only; the complete per-file report must be synthesized later after all chunks for this header are available. This chunk begins at the license and include guard and ends immediately after the completed `AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_CAPABILITIES_EAPD_CAPABLE` enum, with the next enum/comment boundary starting after line 7650.

## Purpose

This header provides named integer constants for Vega10 hardware register fields. The declarations are almost entirely `typedef enum` blocks whose enumerators map human-readable field values to exact hardware bit-pattern values. Code that programs Vega10 GPU, display, audio, performance, or memory/tile registers can include this file and use names instead of raw numbers when building register writes, interpreting register reads, or matching generated register documentation.

The chunk contains 707 `typedef enum` declarations. It does not define functions, structs, persistent data objects, inline helpers, or executable control flow. Its behavior is therefore compile-time and ABI-like: the semantic contract is the stability and correctness of enum names and numeric values.

## Important APIs And Types

The public surface in this chunk is the set of enum type names and enumerator constants. Important groups include:

- Header/compatibility declarations: `_vega10_ENUM_HEADER` guards the file; `_DRIVER_BUILD` and `GL_ZERO` conditionally expose `GL__*` aliases that map GL-style blend factors to `BLEND_*` enum values defined elsewhere in the larger header or a related include path.
- `GDS_PERFCOUNT_SELECT`: Global Data Share performance counter selector values, including bank/address conflicts, write/read buffer activity, per shader-engine/shader-array GDS operations, and GWS signals.
- Chip memory and address configuration enums: `MEM_PWR_FORCE_CTRL`, `MEM_PWR_DIS_CTRL`, `MEM_PWR_SEL_CTRL`, `RowSize`, `SurfaceEndian`, `ArrayMode`, `NumPipes`, `NumBanksConfig`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `NumRbPerShaderEngine`, `NumGPUs`, `NumMaxCompressedFragments`, `ShaderEngineTileSize`, `MultiGPUTileSize`, and `NumLowerPipes`.
- Surface, texture, and buffer formats: `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, `IMG_NUM_FORMAT`, `IMG_NUM_FORMAT_FMASK`, `IMG_NUM_FORMAT_N_IN_16`, `IMG_NUM_FORMAT_ASTC_2D`, and `IMG_NUM_FORMAT_ASTC_3D`.
- Tiling/swizzle fields: `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `SeEnable`, `NumBanks`, `BankWidth`, `BankHeight`, `BankWidthHeight`, `MacroTileAspect`, `SWIZZLE_TYPE_ENUM`, `TC_MICRO_TILE_MODE`, `SWIZZLE_MODE_ENUM`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, and `SampleSplitBytes`.
- Cache/MMU/fault/perf fields: `GATCL1RequestType`, `UTCL1RequestType`, `UTCL1FaultType`, `TCC_CACHE_POLICIES`, `MTYPE`, `RMI_CID`, `PERFMON_COUNTER_MODE`, and `PERFMON_SPM_MODE`.
- Display and audio pipeline blocks: `AZSTREAM`, `BLNDV`, `LBV`, `CRTC`, `FMT`, `HPD`, `LB`, `DIG`, `DCP`, `DC_PERFMON`, `SCL`, `SCLV`, `DPRX_SD`, `AZF0STREAM`, `BLND`, `AZF0ENDPOINT`, and `AZF0INPUTENDPOINT` register field enums.

Representative value contracts visible in this chunk:

- `ArrayMode` encodes linear, 1D/2D/3D tiled, thick, X-thick, and PRT tiled modes from `0x0` through `0xf`.
- `IMG_DATA_FORMAT` maps image resource format encodings from invalid, scalar/vector integer formats, packed depth formats, ETC2/BC/ASTC compression formats, FMASK, and `N_IN_16` forms through `0x3f`.
- `SWIZZLE_MODE_ENUM` maps linear, 256B, 4KB, 64KB, and variable swizzle modes with Z/S/D/R variants and X variants.
- `CRTC_*` enums model display controller timing, triggers, update locks, snapshots, interrupts, CRC selection, external timing sync, static-screen behavior, 3D structure, sync polarity, horizontal repetition, and dynamic refresh update modes.
- `HDMI_*`, `TMDS_*`, `DIG_*`, and `AFMT_*` enums model HDMI packet generation, audio clock regeneration, infoframe send/continuous modes, TMDS test/control patterns, digital encoder source routing, HPD selection, and audio FIFO/CRC controls.
- `DCP_*` enums model graphics plane enablement, tiling/swizzle fields, format/depth, endian/crossbar selection, gamma/degamma/regamma/color-space paths, cursor configuration, LUT access, CRC, GSL sync, XDMA underflow/flip handling, and surface counters.
- `PERFCOUNTER_*` and `PERFMON_*` enums model display perf counter value selection, increment modes, run/count-off control, interrupt modes, counter states, and global/local state selection.
- `SCL_*` and `SCLV_*` enums model scaler filter RAM indexing, phases, filter types, RGB/YCbCr scale/bypass modes, tap counts, replicate factors, update locks, coefficient completion, sharpening, and interrupt masks.
- `AZALIA_F0_CODEC_*` enums model HD-audio converter and pin widget capabilities, including widget type, LR swap, power control, digital capability, connection lists, unsolicited response, processing, striping, format override, amplifier capability, channel capability, pin capabilities, multichannel mode, HBR capability, DP enablement, and EAPD capability.

## Control Flow

There is no runtime control flow in this chunk. The only preprocessing flow is:

- `_vega10_ENUM_HEADER` prevents multiple inclusion.
- `_DRIVER_BUILD` and `GL_ZERO` determine whether the `GL__*` blend aliases are created.
- `ENUMS_GDS_PERFCOUNT_SELECT_H` guards the `GDS_PERFCOUNT_SELECT` typedef specifically, which matters because similar ASIC enum headers define the same type name.

Every other item in the chunk is a straight enum declaration. Runtime code elsewhere decides when to write these values to registers, poll status fields, or interpret hardware output.

## State And Persistence Behavior

This chunk stores no runtime state and performs no persistence. The enum constants are compiled into users of the header as integer constants. Persistent effects occur only indirectly when a consumer writes one of these values into hardware registers or firmware/shared-memory packets. Because register programming values become externally visible hardware state, enum numeric stability is the key state contract.

Several enums represent status/acknowledge/clear semantics, for example `*_ACK`, `*_CLEAR`, `*_INT_MASK`, `*_UPDATE_LOCK`, `*_UPDATE_PENDING`, `*_UPDATE_TAKEN`, `*_RESET`, and `*_RESET_ACK`. The header only names those values; it does not implement the read-modify-write ordering or polling loops needed to use them safely.

## Dependencies

This chunk has minimal direct C dependencies:

- It depends on enum support from the C compiler.
- The GL alias block depends on `BLEND_ZERO`, `BLEND_ONE`, `BLEND_SRC_COLOR`, and related `BLEND_*` identifiers being visible when `_DRIVER_BUILD` is not set and `GL_ZERO` is absent. Those identifiers are not defined in lines 1-7650, so they must come from later portions of the header or from another included generated enum/register header.
- The duplicated `GDS_PERFCOUNT_SELECT` guard suggests the same type name can appear in multiple ASIC headers; inclusion order and guard state can affect whether this typedef is emitted.

No Linux kernel headers are included directly in this chunk, and there are no macros for register offsets or bit masks here; those normally live in nearby generated register headers.

## Integration Points

Direct source search in the AMD GPU subtree shows `amdkfd/kfd_device_queue_manager_v9.c` includes `vega10_enum.h`. The enum names also appear in sibling generated ASIC headers such as `navi10_enum.h`, `soc21_enum.h`, and SMU enum headers, which indicates a shared generated-register-header pattern across GPU generations.

Likely consumers in the Vega10 stack include:

- KFD/queue-manager code configuring Vega10 queue, memory, and performance state.
- AMDGPU display code programming CRTC, FMT, HPD, LB, BLND/BLNDV, DIG/HDMI/TMDS/AFMT, DCP, SCL, and Azalia registers.
- Register pack/unpack code that combines these enum values with register field masks/shifts from companion `*_sh_mask.h` and `*_d.h` headers.
- Diagnostic/perf tooling that selects hardware counters using `GDS_PERFCOUNT_SELECT`, `PERFMON_*`, and `PERFCOUNTER_*` values.

Because this is a generated-style enum header, its primary integration role is as a chip-specific vocabulary layer aligned to the Vega10 hardware register specification.

## Risks

- Numeric drift is the main risk. Changing an enum value without matching the hardware spec can silently program the wrong register field value and cause display failure, incorrect surface layout, memory faults, broken audio, invalid performance counters, or GPU hangs.
- Name drift across ASIC headers is risky. The same enum type or enumerator names appear in nearby generation-specific headers; including multiple ASIC headers can collide unless guarded or isolated carefully.
- Some aliases intentionally share values, such as `MTYPE_WC` and `MTYPE_RW` both using `0x1`. Consumers must treat names as semantic aliases rather than unique values.
- Reserved values are explicitly represented. Code should avoid selecting `*_RESERVED*` entries unless hardware documentation requires them for a particular workaround.
- Some generated names contain spelling inconsistencies, for example `SCL_PSCL_ENANBLE`, `PAHSE`, `OCCURED`, `CAPABLILITY`, and `PROCESING`. Renaming these for spelling would break source compatibility with existing users.
- Boolean-looking fields are not uniformly active-high/active-low in meaning. For example `MASK`, `ACK`, `CLEAR`, `RESET`, `DISABLE`, and `ENABLE` enums must be interpreted against the specific register field.
- The chunk boundary occurs at an enum/comment transition in the Azalia input endpoint section; later chunks are needed to complete the whole source-file understanding and any remaining endpoint capability enums.

## Test Signals

Useful validation signals for this chunk are compile-time and hardware-facing:

- Build AMDGPU/KFD code paths that include `vega10_enum.h`, especially `amdkfd/kfd_device_queue_manager_v9.c`, with warnings enabled to catch duplicate typedefs or missing `BLEND_*` dependencies.
- Run static checks that compare enum numeric values against the generated register specification or the upstream kernel header version for Vega10.
- Run `rg`/include-order checks for duplicate enum type names across `vega10_enum.h`, `navi10_enum.h`, `soc21_enum.h`, and SMU enum headers.
- Exercise display modeset tests that cover CRTC timing/update locks, FMT depth/dither/CRC, HPD interrupts, LB underflow/line-buffer status, DIG/HDMI/TMDS programming, DCP plane/cursor/LUT paths, and scaler coefficient/update paths.
- Exercise audio-over-HDMI/DP tests that validate AZSTREAM, AFMT, and Azalia endpoint fields, including infoframes, audio clock regeneration, HBR capability, and FIFO reset behavior.
- Run GPU memory/surface layout tests that validate `ArrayMode`, `SWIZZLE_MODE_ENUM`, `IMG_DATA_FORMAT`, tiling, pipe/bank, and endian values against rendered images, compute buffers, and page-fault behavior.
- Exercise perf counter tests that program `GDS_PERFCOUNT_SELECT`, `PERFMON_*`, and `PERFCOUNTER_*` selectors and verify expected counter movement under known workloads.

## Cross-Chunk Notes

This chunk is only the first part of `vega10_enum.h`. Later chunks should verify:

- Whether `BLEND_*` values referenced by the early GL alias block are defined later in the file or through another include path.
- Whether remaining Azalia input endpoint enums continue immediately after line 7650.
- Whether the file eventually closes the `_vega10_ENUM_HEADER` include guard cleanly.
- Whether later portions introduce additional enum blocks, macros, or declarations that alter the whole-file dependency and integration picture.
