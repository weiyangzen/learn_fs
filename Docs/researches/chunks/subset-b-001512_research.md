# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_enum.h lines 4749-6129

## Purpose

This chunk is the tail of the generated AMD DCE 11.0 enum header. It begins inside the large `DebugBlockId` enum, completes that enum, then defines 157 more `typedef enum` blocks before closing the `DCE_11_0_ENUM_H` include guard.

The enums provide symbolic names for numeric values that are written into, read from, or decoded from DCE/GCN-era AMD GPU register fields. The covered domains include debug block selection, surface endian and tiling encodings, color/depth/image/buffer formats, texture/tile addressing controls, cache and memory power policies, HPD and DisplayPort debug controls, DCE display-output soft reset selectors, DOUT I2C/DDC control values, and `BLNDV` blending/update-lock/debug controls. There is no executable logic in this range; its purpose is to keep register programming code tied to generated ASIC field definitions rather than scattered numeric literals.

## Important APIs, Types, And Functions

This chunk exports C enum types only. It defines no functions, structs, inline helpers, or preprocessor macros.

Important type groups:

- `DebugBlockId`, `DebugBlockId_BY2`, `DebugBlockId_BY4`, `DebugBlockId_BY8`, and `DebugBlockId_BY16`: debug block ID encodings. The main enum is completed here with entries for TCP, DB, TCC, SPS, TA, TD, and LDS blocks. The `_BY*` variants are downsampled selector tables that preserve every second, fourth, eighth, or sixteenth block ID for narrower debug selector fields.
- `SurfaceEndian`, `ArrayMode`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, `SampleSplitBytes`, `NumPipes`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `ShaderEngineTileSize`, `NumGPUs`, `MultiGPUTileSize`, `RowSize`, and `NumLowerPipes`: memory-layout and address-configuration encodings for tiled GPU surfaces.
- `ColorTransform`, `CompareRef`, `ReadSize`, `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, `QuadExportFormatOld`, `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, and `IMG_NUM_FORMAT`: render, image, buffer, depth/stencil, compression-mask, export, and numeric-format encodings. `SurfaceFormat` and `IMG_DATA_FORMAT` are the broadest tables in this group and include packed integer, float, block-compressed, FMASK, and reserved encodings.
- `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, `BankWidthHeight`, and `MacroTileAspect`: surface-addressing and tile-layout metadata used by GPU memory swizzle/tile selection fields.
- `GATCL1RequestType`, `TCC_CACHE_POLICIES`, `MTYPE`, `PERFMON_COUNTER_MODE`, and `PERFMON_SPM_MODE`: memory/cache translation request, cache-policy, memory-type, and performance-monitor mode values.
- `SurfaceTiling`, `SurfaceArray`, `ColorArray`, `DepthArray`, and `ENUM_NUM_SIMD_PER_CU`: smaller display/surface metadata enums, including the `NUM_SIMD_PER_CU = 0x4` hardware constant.
- `MEM_PWR_FORCE_CTRL`, `MEM_PWR_FORCE_CTRL2`, `MEM_PWR_DIS_CTRL`, `MEM_PWR_SEL_CTRL`, and `MEM_PWR_SEL_CTRL2`: memory power-management controls for force, disable, and dynamic light/deep sleep or shutdown selection.
- `HPD_INT_CONTROL_ACK`, `HPD_INT_CONTROL_POLARITY`, `HPD_INT_CONTROL_RX_INT_ACK`, `DPDBG_*`, `PM_ASSERT_RESET`, `DAC_MUX_SELECT`, and `TMDS_DVO_MUX_SELECT`: hot-plug detect interrupt status/ack polarity, DisplayPort debug enable/input/error/overflow handling, power-management reset assertion, DAC muxing, and TMDS/DVO color mux selectors.
- `DACA_SOFT_RESET`, `I2S0_SPDIF0_SOFT_RESET`, `I2S1_SOFT_RESET`, `SPDIF1_SOFT_RESET`, `DB_CLK_SOFT_RESET`, `FMT0_SOFT_RESET` through `FMT5_SOFT_RESET`, `MVP_SOFT_RESET`, `ABM_SOFT_RESET`, `DVO_SOFT_RESET`, `DIGA/DIGB/DIGC/DIGD/DIGE/DIGF/DIGG_FE/BE_SOFT_RESET`, `DPDBG_SOFT_RESET`, and `DIGLPA/DIGLPB_FE/BE_SOFT_RESET`: one-bit soft reset values for display, audio, formatter, digital encoder/front-end/back-end, DisplayPort debug, and low-power digital paths.
- `GENERICA_STEREOSYNC_SEL` and `GENERICB_STEREOSYNC_SEL`: stereo-sync source selectors for D1 through D6 plus a reserved value.
- `DCO_DBG_BLOCK_SEL` and `DCO_DBG_CLOCK_SEL`: DCO debug mux block and clock selectors spanning DCO, ABM, DVO, DAC, MVP, FMT instances, DIGFE/DIG/DPFE/DP blocks, AUX channels, perfmon/audio output, low-power digital blocks, DISPCLK/SCLK/reference clocks, symbol clocks, and audio/module clocks.
- `DOUT_I2C_*`: DOUT I2C/DDC control enums for transfer start/stop, controller reset, DDC line selection, transaction count, debug reference selection, software arbitration, abort, register-request handoff, ACK cleanup, DDC speed threshold, pad drive setup, EDID detection mode, NACK stop policy, data index writes, EDID reset behavior, and read-request interrupt type.
- `BLNDV_*`: vertical blender controls for blending mode, stereo type/polarity, feedthrough, alpha/multiplied alpha behavior, stereo/subsample mode, frame/field alternation, forced next-frame/top polarity, PTI and SuperAA gamma controls, underflow interrupt ack/mask, v-update locks for DCP graphics/surface/cursor/scaler/blender state, conversion mux selection, and test debug write enable.

The final exported item in this chunk is `#endif /* DCE_11_0_ENUM_H */`, which closes the file's include guard.

## Control Flow

There is no runtime control flow. The effective flow is compile-time type availability:

1. A DCE 11.0 consumer includes `dce_11_0_enum.h`, typically alongside generated register address and shift/mask headers.
2. The compiler sees named enum constants for valid register-field values.
3. Driver code passes those constants into register composition, debug selection, surface setup, interrupt control, reset, or I2C/DDC programming paths elsewhere in the AMDGPU driver.
4. Repeated inclusion is guarded by `DCE_11_0_ENUM_H`; this chunk supplies the closing `#endif`, so file integrity depends on this tail remaining present.

The enums themselves encode state-machine choices that are interpreted by hardware blocks. For example, DOUT I2C transfer flow is represented as `STOP_TRANSFER` versus `START_TRANSFER`; arbitration can abort a current transfer or request I2C register ownership; BLNDV v-update lock values gate whether related display-plane updates are held; and soft reset enums represent asserted/deasserted reset bits. The transition logic is in the MMIO-writing code, not in this header.

## State And Persistence Behavior

The header stores no software state and performs no persistence. Its values are stable ABI-like constants for this generated ASIC register interface.

State changes happen only when other driver code uses these enum constants to program registers. Those writes can persist in hardware until overwritten, until the relevant display or GPU block is reset, or until device suspend/resume or full GPU reset reinitializes the block. The most stateful consumer-facing groups are:

- Soft reset enums, which can hold DCE sub-blocks in reset when the corresponding register bit remains asserted.
- Memory power enums, which can force memory arrays into light sleep, deep sleep, or shutdown modes and override dynamic behavior.
- DOUT I2C/DDC enums, where `GO`, arbitration, abort, ACK cleanup, NACK policy, and EDID reset values affect an in-progress monitor communication transaction.
- BLNDV update-lock and underflow interrupt enums, which affect display-plane update timing and interrupt status handling.
- Debug selector enums, which route internal block or clock signals to debug paths without changing normal display data flow unless misused.

Because these are generated numeric encodings, the most important persistence property is version coupling: values must match DCE 11.0 hardware documentation and the companion generated register field definitions. The header has no local runtime guard against stale or wrong enum values.

## Dependencies

The chunk depends on context from the rest of `dce_11_0_enum.h`:

- The license, include guard start, and earlier enum definitions are outside this range.
- `DebugBlockId` starts before line 4749; this chunk only contains its tail and its closing typedef.
- The final `#endif` here must match the include guard opened at the top of the file.

External dependencies are conventional for generated AMD ASIC headers:

- Consumers need the matching DCE 11.0 register-address and shift/mask headers to know which register fields accept these values.
- AMDGPU display, DC/DCE, DAL, KMS, debug, power-management, and I2C/DDC paths are expected to use these symbolic encodings while performing MMIO through driver register helpers.
- Hardware documentation or the register-generation database is the authority for the numeric assignments. The enum names imply direct mapping to register field values; the C compiler only checks syntax and type names, not hardware correctness.

There are no Linux kernel library dependencies in this chunk beyond ordinary C enum parsing.

## Integration Points

The integration surface is broad but low-level:

- GPU debug and diagnostics use the `DebugBlockId*`, `DCO_DBG_BLOCK_SEL`, `DCO_DBG_CLOCK_SEL`, and `DPDBG_*` selectors to route internal debug signals or configure overflow/error handling.
- Display memory and scanout/resource setup code can use surface endian, array mode, tiling, pipe, bank, tile split, sample split, format, and numeric-format enums when programming DCE-visible surface descriptors or compatible GPU registers.
- Render/depth/image related users depend on `ColorFormat`, `SurfaceFormat`, `IMG_DATA_FORMAT`, `BUF_DATA_FORMAT`, `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, and export-format tables to keep hardware format encodings consistent across display and graphics definitions.
- Power-management paths use memory power-control enums and soft reset enums while sequencing DCE block resets, display clock/reset behavior, audio/display output reset, and low-power digital paths.
- Connector and monitor-management code integrates through HPD interrupt enums and DOUT I2C/DDC enums used for EDID reads, DDC channel selection, transaction counting, arbitration, ACK clearing, read-request interrupts, and reset behavior.
- Blender/display-pipe code integrates through `BLNDV_*` values for current/other pipe blending, stereo modes, feedthrough, alpha handling, subsampling, SuperAA gamma, underflow interrupt processing, and v-update locking across DCP graphics/surface/cursor/scaler/blender subcomponents.

Since this is a generated shared header, changing any numeric value is a cross-cutting hardware contract change, not a local refactor.

## Risks And Edge Cases

- The chunk begins mid-`DebugBlockId`; any final per-file research must merge it with the preceding chunk to describe the full debug block table.
- Many enums use reserved values. Callers should avoid treating every numeric value in the bit width as a supported mode.
- `_BY2`, `_BY4`, `_BY8`, and `_BY16` debug block tables intentionally skip entries. Generic code must choose the variant matching the register field width and hardware selector stride.
- Format enums have overlapping-looking names across `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, and `IMG_DATA_FORMAT`, but they are not interchangeable. A value valid for one field may be invalid or mean something else in another field.
- Some tables contain legacy or compatibility variants, such as `QuadExportFormatOld`, which should not be assumed equivalent to newer export encodings.
- `BLNDV_SM_CONTROL2_SM_MODE` uses even values (`0x0`, `0x2`, `0x4`, `0x6`), which suggests field bits may include mode substructure or reserved low-bit combinations. Code that increments modes sequentially would be wrong.
- One-bit reset, ACK, mask, enable, and lock enums often use `_0/_1`, `FALSE/TRUE`, or action names. The active semantic can vary by field; for example an ACK value of `1` may clear an interrupt, while a mask value of `1` may mask or enable depending on the field definition.
- DOUT I2C/DDC values can affect physical DDC transactions. Wrong arbitration, abort, ACK, or NACK-stop programming can break EDID reads or leave a bus transaction in an unexpected state.
- Soft reset enums are especially risky if used without paired deassertion and polling; leaving a DCE sub-block reset can disable display, audio, AUX/DDC, or debug functionality.
- The final include-guard close is in this chunk. Truncation after the enum tail can produce global build failures for any translation unit including this header.

## Test Signals

Useful validation is primarily build-time, generation-time, and hardware bring-up oriented:

- Kernel/driver builds that include `dce_11_0_enum.h` should compile cleanly, proving enum syntax and the closing include guard are intact.
- Generated-header comparison should verify every enum value against the DCE 11.0 register source database, especially repeated debug-block downsampling tables and copy-patterned soft reset enums.
- Static checks can flag duplicate or out-of-range values in field-specific enums where the hardware field width is known.
- Register programming tests should compose fields with the companion mask/shift headers and verify readback values decode to the expected enum constants.
- Display hotplug and EDID tests should exercise HPD and DOUT I2C/DDC paths across DDC1-DDC6 and VGA DDC selection where hardware exposes those ports.
- Display pipe tests should cover BLNDV blending modes, stereo/subsampling modes, v-update locks, underflow interrupt ack/mask handling, and SuperAA gamma controls on supported ASICs.
- Suspend/resume, modeset, and GPU reset tests should verify that soft reset and memory power-management enum use does not leave DCE sub-blocks, DDC, audio, or digital encoders stuck in reset or forced power states.
- Debug and perf diagnostics should verify that DCO/DP debug block and clock selector values route the expected internal signals without corrupting normal display output.
