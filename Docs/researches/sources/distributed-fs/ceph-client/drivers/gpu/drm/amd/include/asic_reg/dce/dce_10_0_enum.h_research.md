# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_enum.h

## Purpose

`dce_10_0_enum.h` is a generated-style AMD DCE 10.0 register enumeration header. It contributes no executable code; it defines 159 `typedef enum` types whose constants encode hardware-visible field values for the DCE 10.0 display controller and related GPU register programming surfaces.

The file is guarded by `DCE_10_0_ENUM_H` and sits beside the DCE 10.0 register address and mask headers (`dce_10_0_d.h`, `dce_10_0_sh_mask.h`). In this tree it is directly included by `drivers/gpu/drm/amd/amdgpu/dce_v10_0.c`, which is the DCE v10 display IP implementation for amdgpu. The values in this header are therefore part of the low-level hardware ABI used when the driver writes display, GPIO, clock, power, color, surface-format, tiling, debug, and performance-monitoring fields.

## Important APIs, Types, and Constants

The file exports enum typedefs rather than functions. The most important groups are:

- DCIO routing and signal selection: `DCIO_DC_GENERICA_SEL`, `DCIO_DC_GENERICB_SEL`, `DCIO_DC_PAD_EXTERN_SIG_SEL`, `DCIO_DC_PAD_EXTERN_SIG_MVP_PIXEL_SRC_STATUS`, `DCIO_DCO_DCFE_EXT_VSYNC_MUX`, and `DCIO_DCO_EXT_VSYNC_MASK` map generic display signals, external pad sources, MVP pixel status, and external vsync routing to register field encodings.
- UNIPHY and link control: `DCIO_DC_GENERIC_UNIPHY_REFDIV_CLK_SEL`, `DCIO_DC_GENERIC_UNIPHY_FBDIV_CLK_SEL`, `DCIO_DC_GENERIC_UNIPHY_FBDIV_SSC_CLK_SEL`, `DCIO_DC_GENERIC_UNIPHY_FBDIV_CLK_DIV2_SEL`, `DCIO_UNIPHY_LINK_CNTL_MINIMUM_PIXVLD_LOW_DURATION`, `DCIO_UNIPHY_LINK_CNTL_CHANNEL_INVERT`, `DCIO_UNIPHY_LINK_CNTL_ENABLE_HPD_MASK`, and `DCIO_UNIPHY_CHANNEL_XBAR_SOURCE` describe PHY clock/test selections, lane inversion, hotplug mask behavior, and channel crossbar sources.
- GPIO, DDC, AUX, and pad behavior: `DCIOCHIP_HPD_SEL`, `DCIOCHIP_PAD_MODE`, `DCIOCHIP_AUXSLAVE_PAD_MODE`, `DCIOCHIP_INVERT`, `DCIOCHIP_PD_EN`, `DCIOCHIP_GPIO_MASK_EN`, `DCIOCHIP_GPIO_I2C_MASK`, `DCIOCHIP_GPIO_I2C_DRIVE`, `DCIOCHIP_GPIO_I2C_EN`, and width-specific mask/enable enums encode hotplug sampling, DDC versus DP pad mode, AUX versus I2C mode, polarity, powerdown permission, and GPIO masking/drive state.
- Panel power sequencing and backlight PWM: `DCIO_LVTMA_PWRSEQ_CNTL_TARGET_STATE`, `DCIO_LVTMA_PWRSEQ_CNTL_LVTMA_DIGON`, `DCIO_LVTMA_PWRSEQ_CNTL_LVTMA_BLON`, `DCIO_BL_PWM_CNTL_BL_PWM_FRACTIONAL_EN`, `DCIO_BL_PWM_CNTL_BL_PWM_EN`, `DCIO_BL_PWM_CNTL2_DBG_BL_PWM_INPUT_REFCLK_SELECT`, `DCIO_BL_PWM_GRP1_REG_LOCK`, and related group-update/readback enums encode LCD power, polarity, PWM enable, fractional PWM, frame-start update, and lock semantics.
- Genlock and swaplock: `DCIO_GSL_SEL`, `DCIO_GENLK_CLK_GSL_MASK`, `DCIO_GENLK_VSYNC_GSL_MASK`, `DCIO_SWAPLOCK_A_GSL_MASK`, `DCIO_SWAPLOCK_B_GSL_MASK`, `DCIO_GSL_VSYNC_SEL`, and the `DCIO_GSL0/1/2_*` enums describe global sync lock groups, timing sync sources, and global unlock sources.
- Clock, reset, timer, and calibration fields: `DCIO_CLOCK_CNTL_DCIO_TEST_CLK_SEL`, `DCIO_CLOCK_CNTL_DISPCLK_R_DCIO_GATE_DIS`, `DCIO_CLOCK_CNTL_DISPCLK_R_DCIO_RAMP_DIS`, `DCIO_DSYNC_SOFT_RESET`, `DCIO_DACA_SOFT_RESET`, `DCIO_DCRXPHY_SOFT_RESET`, `DCIO_DC_GPU_TIMER_START_POSITION`, `DCIO_DC_GPU_TIMER_READ_SELECT`, `DCIO_IMPCAL_STEP_DELAY`, and `DCIO_UNIPHY_IMPCAL_SEL` define selectable clocks, clock gating/ramping bits, soft-reset assertion values, timer readout sources, and impedance calibration controls.
- Color-management pipeline fields: `COL_MAN_UPDATE_LOCK`, `COL_MAN_DISABLE_MULTIPLE_UPDATE`, `COL_MAN_INPUTCSC_MODE`, `COL_MAN_INPUTCSC_TYPE`, `COL_MAN_INPUTCSC_CONVERT`, `COL_MAN_PRESCALE_MODE`, `COL_MAN_OUTPUT_CSC_MODE`, `COL_MAN_DENORM_CLAMP_CONTROL`, and `COL_MAN_GAMMA_CORR_CONTROL` encode update locking, input/output CSC selection, fixed-point conversion, prescale, denorm clamp, and gamma correction modes.
- Surface, image, buffer, and tiling formats: `SurfaceEndian`, `ArrayMode`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, `SampleSplitBytes`, `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, `IMG_NUM_FORMAT`, `TileType`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, and `MacroTileAspect` provide GPU memory layout and pixel/storage format encodings.
- Debug and performance monitoring: `DebugBlockId`, `DebugBlockId_OLD`, `DebugBlockId_BY2`, `DebugBlockId_BY4`, `DebugBlockId_BY8`, `DebugBlockId_BY16`, `PERFMON_COUNTER_MODE`, and `PERFMON_SPM_MODE` enumerate debug-client block IDs, reduced block-ID views, perf counter modes, and streaming performance monitor modes.
- Render/depth helper formats and memory policy: `ColorTransform`, `CompareRef`, `ReadSize`, `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, `QuadExportFormatOld`, `GATCL1RequestType`, `TCC_CACHE_POLICIES`, and `MTYPE` define fixed GPU field encodings that are shared with non-display register blocks.
- Memory power controls: `MEM_PWR_FORCE_CTRL`, `MEM_PWR_FORCE_CTRL2`, `MEM_PWR_DIS_CTRL`, `MEM_PWR_SEL_CTRL`, and `MEM_PWR_SEL_CTRL2` encode force, disable, and dynamic memory power-management requests.

Several enum names are broad (`ArrayMode`, `SurfaceFormat`, `DebugBlockId`, `PERFMON_COUNTER_MODE`) and also appear in sibling ASIC register enum headers. That is workable only when translation units include a compatible set of ASIC headers; it is a namespace collision risk if unrelated generations are mixed in one compilation unit.

## Control Flow

There is no runtime control flow in this header. Its only preprocessor control flow is the include guard:

- `#ifndef DCE_10_0_ENUM_H`
- `#define DCE_10_0_ENUM_H`
- enum declarations
- `#endif`

Runtime control flow appears in consumers such as `amdgpu/dce_v10_0.c`, which includes this header after DCE register address and mask headers. In that consumer, DCE initialization, HPD, CRTC, pageflip, audio, watermark, encoder, IRQ, suspend/resume, and reset paths use DCE register definitions while programming hardware. This enum header supplies named constants for register field values when those paths need symbolic encodings.

## State and Persistence Behavior

The file has no mutable state, static storage, persistent files, allocation, locking, or I/O. Its constants describe values that can become persistent only indirectly when driver code writes them into GPU registers. Those register writes affect hardware state across display mode changes, hotplug setup, power sequencing, debug routing, clock selection, memory tiling, performance monitoring, and suspend/resume transitions.

Because these enum values are hardware encodings, their numerical values are the important state contract. Renaming a constant is mostly a source compatibility issue; changing a numeric value changes the bits written to hardware and can break display bring-up, link training, GPIO/AUX/DDC behavior, backlight control, scanout formats, or debug/perf collection.

## Dependencies and Integration Points

This header has no C include dependencies of its own beyond standard enum syntax. Its integration points are:

- `drivers/gpu/drm/amd/amdgpu/dce_v10_0.c`, which directly includes `dce/dce_10_0_enum.h` beside `dce_10_0_d.h` and `dce_10_0_sh_mask.h`.
- DCE 10.0 register definitions in the same folder, where enum values correspond to fields named by the address and mask headers.
- amdgpu display IP code that interacts with DRM CRTC, encoder, connector, audio, HPD, vblank, pageflip, clock, and power-management paths.
- Sibling ASIC enum headers under `include/asic_reg/` and top-level generated headers such as `soc21_enum.h`, `soc24_enum.h`, and `navi10_enum.h`, which define many similarly named or identical enum typedefs for other GPU generations.

The broader source path is under `sources/distributed-fs/ceph-client`, but this particular file is Linux DRM/amdgpu hardware-register metadata. It does not participate in Ceph filesystem logic directly; it is part of the vendored or mirrored kernel driver source present in this tree.

## Risks and Sharp Edges

- Hardware ABI drift: every enum literal is a register-field encoding. Incorrect edits can silently write valid-looking but wrong bit patterns to DCE 10.0 hardware.
- Cross-generation collisions: generic typedef names such as `ArrayMode`, `SurfaceFormat`, `DebugBlockId`, and `PERFMON_COUNTER_MODE` are reused across multiple ASIC register headers. Including incompatible generations together can cause duplicate typedef errors or, worse, mistaken assumptions that equal names imply equal hardware semantics.
- Generated-file maintenance: the file appears generated from AMD register documentation. Manual style or spelling cleanup can damage traceability to hardware specs. Some literals intentionally preserve register-doc naming, including reserved values and apparent typos such as `DCIOCHIP_MASIK_5BIT_*` and `COL_MAN_MULTIPLE_UPDAT_EDISABLE`.
- Reserved encodings: many enums include `RESERVED` or duplicate names for specific numeric slots. Consumers must not assume all numeric values are safe to program merely because they have symbolic names.
- Width-sensitive masks: enums such as `DCIOCHIP_MASK_4BIT`, `DCIOCHIP_ENABLE_5BIT`, and `DCIOCHIP_ENABLE_2BIT` encode all-bits-set values for specific field widths. Reusing them for a different-width field would corrupt neighboring bits if not masked correctly.
- Display bring-up sensitivity: DCE routing, PHY, HPD, backlight, power-sequencing, and clock values are involved in visible display behavior and can regress only on affected boards, connectors, panels, or modes.

## Test Signals

Useful validation signals for changes involving this file are mostly compile-time and hardware/runtime driver signals:

- Build the amdgpu driver code that includes `amdgpu/dce_v10_0.c`; duplicate typedefs, missing enum names, or syntax problems should fail at compile time.
- Run static grep or generated-header comparison against the source register spec or known-good upstream DCE 10.0 header to ensure numeric encodings have not drifted.
- Exercise DCE v10 display paths on matching AMD hardware: boot with amdgpu, enumerate connectors, handle HPD plug/unplug, program modes on all CRTCs, perform page flips, blank/unblank displays, suspend/resume, and verify no display hangs or IRQ storms.
- Validate panel-specific behavior where relevant: eDP/LVDS power sequencing, `DIGON`/`BLON`, PWM enable and fractional PWM, and frame-start update behavior.
- Check debug/perf users if enum values are touched: debug block selection, perf counter mode programming, and SPM mode collection should still select the intended blocks and modes.
- For tiling and format enums, validate scanout/framebuffer formats, endian handling, cursor surfaces, and any path that derives register fields from `SurfaceFormat`, `ColorFormat`, `ArrayMode`, or tiling configuration.
