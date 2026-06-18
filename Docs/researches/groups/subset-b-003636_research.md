# subset-b-003636 research

Grouped research for i.MX DCSS, legacy i.MX IPUv3 display, i.MX LCDC, and Ingenic DRM display controller files. Each source file section is delimited for deterministic splitting into the mapped source-tree-aligned research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-dtg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-dtg.c

## Purpose
Programs the i.MX8MQ DCSS display timing generator. It derives display, plane, context-load, vblank, and context-load-kick timing from DRM videomodes, controls channel enable and foreground alpha state, and owns the DTG interrupt lines used by the DCSS CRTC for vblank and context-load commits.

## Important APIs, types, and functions
- `struct dcss_dtg` stores the mapped DTG registers, context-loader link, cached display origin, control register image, alpha configuration, and `ctxld_kick` IRQ enable state.
- `dcss_dtg_init()` allocates and maps the DTG block, initializes the default overlay/video alpha control bits, and installs the context-load kick IRQ handler with `IRQF_NO_AUTOEN`.
- `dcss_dtg_sync_set()` programs total/display timing registers, sets the pixel clock, records display upper-left coordinates, and sets context-load and interrupt trigger lines.
- Plane/channel APIs are `dcss_dtg_plane_pos_set()`, `dcss_dtg_plane_alpha_set()`, `dcss_dtg_ch_enable()`, `dcss_dtg_global_alpha_changed()`, and `dcss_dtg_css_set()`.
- Runtime control and IRQ APIs are `dcss_dtg_enable()`, `dcss_dtg_shutoff()`, `dcss_dtg_vblank_irq_enable()`, `dcss_dtg_vblank_irq_clear()`, `dcss_dtg_vblank_irq_valid()`, and `dcss_dtg_ctxld_kick_irq_enable()`.

## Control flow
Initialization maps the register window and prepares a cached `control_status` value with overlay data mode, video alpha selection, and default foreground alpha. IRQ configuration masks line0/line1 interrupts, obtains the `ctxld_kick` IRQ by name, and registers the handler disabled.

Mode setup converts `struct videomode` porches and sync lengths into DCSS last-row/column and display-window coordinates, disables and reprograms the pixel clock, writes timing registers through `dcss_dtg_write()`, and places line interrupts so line1 acts as vblank and line0 kicks the context loader near the end of active scanout. `dcss_dtg_write()` writes live hardware only before `in_use` is set and always queues the same write to the context loader.

Plane updates offset plane rectangles by the current display origin and program channel top/bottom registers, with an all-zero rectangle used as the disable sentinel. Channel enable recomputes `TC_CONTROL_STATUS`, merges the current alpha mode, and writes it only if the cached value changes. Enable sets `DTG_START` through context load and marks the DTG in use; shutoff directly clears the hardware start bit and marks it idle. The line0 IRQ handler validates the interrupt source, calls `dcss_ctxld_kick()`, and clears the line0 interrupt.

## State and persistence
Persistent runtime state is in the `dcss_dtg` object allocated for the lifetime of the DCSS device. `control_status`, `alpha`, and `alpha_cfg` are cached software mirrors of hardware fields. `dis_ulc_x/y` persist from the most recent mode setup and are required for later plane coordinate conversion. Register writes are persisted both in the hardware block and in the DCSS context-loader buffer, with behavior depending on whether the block is already active.

## Dependencies and integration points
This file depends on the DCSS common MMIO helpers, `dcss_ctxld_write()`, `dcss_ctxld_kick()`, and pixel-clock ownership in `struct dcss_dev`. It is driven by the DCSS CRTC mode set, vblank enable/disable, and plane update paths. Its alpha behavior is tied to DRM plane alpha and format metadata, while its IRQ names and register base are supplied by the platform device resources.

## Risks
The timing equations include several `- 1` offsets and unusual vertical display-origin handling; regressions can shift active video, vblank, or context-load timing by a line or pixel. `dcss_dtg_plane_pos_set()` computes lower-right as upper-left plus width/height, so consumers must agree with the hardware's inclusive/exclusive convention. The context-load kick IRQ uses line0 and is separately masked and Linux-disabled; mismatched mask/enable state can leave commits stuck. Channel arrays assume valid `ch_num` in the range 0..2.

## Test signals
Useful signals include successful modeset with the requested pixel clock, vblank interrupt delivery on line1, context-loader progress after line0 IRQs, correct overlay position after panning or mode changes, foreground alpha behavior for formats with and without alpha, and suspend/remove paths that free the IRQ without interrupt warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-dtg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-kms.c

## Purpose
Creates and tears down the DRM/KMS device for the i.MX8MQ DCSS display subsystem. It wires the DCSS CRTC, encoder, bridge connector, vblank support, GEM DMA framebuffer support, fbdev/client setup, and atomic mode configuration into a single DRM device.

## Important APIs, types, and functions
- `dcss_kms_attach()` is the main attach path, using `devm_drm_dev_alloc()` with `struct dcss_kms_dev`.
- `dcss_kms_detach()` unregisters the DRM device, shuts down atomic state, disables CRTC vblank, cleans mode config, and deinitializes the CRTC.
- `dcss_kms_shutdown()` performs atomic shutdown for platform shutdown.
- Static objects include `dcss_kms_driver`, `dcss_drm_mode_config_funcs`, `dcss_mode_config_helpers`, and the simple encoder funcs.
- `dcss_kms_bridge_connector_init()` discovers the downstream panel/bridge from device tree, initializes the encoder, attaches the bridge without a connector, then creates a bridge connector.

## Control flow
Attach allocates a DRM device embedded in `dcss_kms_dev`, stores the DCSS hardware pointer in `drm->dev_private`, initializes mode limits and atomic helpers, initializes one vblank source, finds and attaches the downstream bridge, initializes the DCSS CRTC and its planes, resets mode objects, starts helper polling, registers the DRM device, and finally starts generic DRM client setup.

Error paths unwind in reverse: CRTC cleanup when registration fails and mode-config cleanup for earlier failures. Detach follows the runtime teardown path: unregister first to stop userspace entry, stop polling, run atomic shutdown, force vblank off, clean the mode config, deinitialize CRTC resources, and clear `dev_private`.

## State and persistence
The file owns the `struct drm_device` embedded in `struct dcss_kms_dev`, the associated encoder and connector pointer, and the link from DRM back to `struct dcss_dev` through `dev_private`. No persistent hardware state is stored here; it orchestrates lifecycle state in DRM core objects.

## Dependencies and integration points
Depends on DRM GEM DMA helpers, fbdev DMA helpers, atomic helpers, bridge connector helpers, vblank initialization, and device-tree bridge discovery. It integrates with the DCSS CRTC and plane code through `dcss_crtc_init()`/`dcss_crtc_deinit()` and is called by the broader DCSS platform driver after the hardware blocks have been initialized.

## Risks
Bridge discovery requires a valid downstream bridge; a panel returned without a bridge is treated as `-ENODEV`. The encoder is initialized before `dcss_crtc_init()`, so parse/attach failures must not leak encoder state. `drm->dev_private` is critical for plane and CRTC callbacks and must be cleared on failed attach/detach. Atomic shutdown is used in both detach and shutdown, so duplicate calls must remain harmless.

## Test signals
Build and probe should show one registered `imx-dcss` DRM device, one CRTC, one encoder, and one bridge connector. Runtime validation should cover bridge probe deferral, registration failure unwind, vblank initialization, fbdev/client setup, shutdown with an active mode, and hot-unplug or module removal without dangling polling or mode objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-kms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-kms.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-kms.h

## Purpose
Defines the small private KMS object model shared by the DCSS KMS, CRTC, and plane implementation files.

## Important APIs, types, and functions
- `struct dcss_plane` embeds `struct drm_plane` and stores the DCSS channel number.
- `struct dcss_crtc` embeds `struct drm_crtc`, keeps three plane pointers, the IRQ number, cached state pointer, and a flag controlling context-load IRQ disabling.
- `struct dcss_kms_dev` embeds the DRM device and contains the single DCSS CRTC, encoder, and connector pointer.
- Declarations expose `dcss_kms_attach()`, `dcss_kms_detach()`, `dcss_kms_shutdown()`, `dcss_crtc_init()`, `dcss_crtc_deinit()`, and `dcss_plane_init()`.

## Control flow
This header has no executable flow. It fixes object ownership boundaries: KMS allocation creates `dcss_kms_dev`, CRTC code owns `dcss_crtc`, and plane initialization returns `dcss_plane` instances indexed by z-position/channel.

## State and persistence
The declared structures persist for the lifetime of the DRM device. `ch_num` is the stable mapping from a DRM plane to the DCSS DPR/scaler/DTG hardware channel. `disable_ctxld_kick_irq` is CRTC-managed state used to coordinate context-load interrupt behavior.

## Dependencies and integration points
Includes DRM encoder definitions and relies on other included source files for the full `dcss_dev` type. It is the local integration contract among DCSS KMS setup, CRTC setup, and plane setup.

## Risks
The hardware has exactly three DCSS planes/channels in this model; changing that requires updating fixed arrays and zpos/channel assumptions across plane, CRTC, scaler, DPR, and DTG code. The public prototypes hide no ownership annotations, so callers must follow local cleanup ordering.

## Test signals
Compile coverage catches structure/prototype drift. Runtime signals are correct plane-to-channel mapping, valid connector/encoder access through `dcss_kms_dev`, and successful teardown of CRTC and planes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-kms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-plane.c

## Purpose
Implements DCSS DRM plane objects and the atomic plane programming path. It validates formats, modifiers, rotation, cropping, source size, and scaling limits, then programs DPR addresses/format/rotation, scaler setup, DTG position/alpha, and channel enable state.

## Important APIs, types, and functions
- Format lists are `dcss_common_formats`, `dcss_video_format_modifiers`, and `dcss_graphics_format_modifiers`.
- Plane lifecycle uses `dcss_plane_init()`, `dcss_plane_destroy()`, and `dcss_plane_format_mod_supported()`.
- Atomic hooks are `dcss_plane_atomic_check()`, `dcss_plane_atomic_update()`, and `dcss_plane_atomic_disable()`.
- Helper logic includes `dcss_plane_can_rotate()`, `dcss_plane_is_source_size_allowed()`, `dcss_plane_atomic_set_base()`, and `dcss_plane_needs_setup()`.

## Control flow
Plane initialization chooses Vivante tiled/super-tiled modifiers only for the primary plane, registers the universal plane, adds immutable zpos, scaling-filter, and rotation properties, and maps `zpos` to the DCSS channel number.

Atomic check rejects too-small sources, invalid scaling ratios from `dcss_scaler_get_min_max_ratios()`, unsupported rotation/modifier combinations, non-linear cropped scanout, and invalid modifiers. Atomic update fast-paths pure base-address flips when the old framebuffer exists, no modeset is needed, and geometry/format/modifier/rotation/filter did not change. Full setup computes clipped source/destination sizes, normalizes overlay linear modifiers, programs DPR format/resolution/rotation/address, selects scaler filter, configures scaling with rotation-aware source dimensions, sets DTG position and alpha, and enables DPR/scaler/DTG channels unless channel 0 is fully transparent. Disable clears DPR, scaler, DTG position, and DTG channel enable for that hardware channel.

## State and persistence
Plane state is mostly DRM atomic state. The file persists only `dcss_plane->ch_num`; hardware state is persisted in DPR/scaler/DTG blocks and in DCSS context-loader queued writes. Base address programming uses DMA addresses from the current GEM DMA framebuffer and handles packed RGB, packed YUV, and NV12/NV21 secondary plane addresses.

## Dependencies and integration points
Depends on DRM atomic helpers, GEM DMA framebuffer helpers, DRM blend/scaling/rotation properties, and DCSS DPR/scaler/DTG APIs. It integrates with `dcss_kms.h` object definitions and assumes `plane->dev->dev_private` is the live `struct dcss_dev`.

## Risks
`dcss_plane_can_rotate()` checks `rotation & supported_rotation`, which accepts a request if any requested bit overlaps a supported bit; unexpected compound rotation/reflection combinations need coverage. Cropping is disallowed only for non-linear buffers, so linear address calculations must stay correct for subsampled formats. The primary plane's alpha-zero path disables channel 0 and clears its rectangle, which can interact with global alpha and z-order assumptions. Error unwinding in `dcss_plane_init()` returns after property creation failures without explicitly cleaning the initialized plane.

## Test signals
Validation should include primary tiled and super-tiled RGB, overlay linear RGB, invalid overlay tiled modifiers, NV12/NV21 and packed YUV source-size limits, rotation/reflection combinations, scaling limits per channel, fast page flips that only update base addresses, alpha-zero primary disable, and cropped linear versus cropped tiled framebuffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-scaler.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-scaler.c

## Purpose
Programs the three-channel DCSS scaler block. It designs fixed-point Gaussian or nearest-neighbor filter coefficients, handles RGB/YUV format and chroma geometry, computes scaling increments, writes scaler coefficients through the context loader, and defers scaler control writes for interrupt-safe commit.

## Important APIs, types, and functions
- `struct dcss_scaler` owns the context-loader link and three `struct dcss_scaler_ch` channels.
- Public APIs are `dcss_scaler_init()`, `dcss_scaler_exit()`, `dcss_scaler_ch_enable()`, `dcss_scaler_get_min_max_ratios()`, `dcss_scaler_set_filter()`, `dcss_scaler_setup()`, and `dcss_scaler_write_sclctrl()`.
- Fixed-point/filter helpers include `mult_q()`, `div_q()`, `exp_approx_q()`, `dcss_scaler_gaussian_filter()`, `dcss_scaler_nearest_neighbor_filter()`, and `dcss_scaler_filter_design()`.
- Programming helpers include `dcss_scaler_format_set()`, `dcss_scaler_res_set()`, `dcss_scaler_fractions_set()`, `dcss_scaler_program_5_coef_set()`, `dcss_scaler_program_7_coef_set()`, `dcss_scaler_yuv_coef_set()`, `dcss_scaler_rgb_coef_set()`, `dcss_scaler_bit_depth_set()`, and `dcss_scaler_set_rgb10_order()`.

## Control flow
Initialization allocates the scaler object, maps three channel register windows at 0x400 spacing, and sets the context-loader context to `CTX_SB_HP`. Plane updates first select nearest-neighbor versus default filtering, then call `dcss_scaler_setup()` with source/destination sizes and format. Setup classifies the source as RGB, YUV420, YUV422, or 4:4:4-like RGB/YUV output, enables YUV and 8-line RTRAM when needed, computes luma/chroma fractions and chroma phase starts, designs and writes coefficients for luma and chroma, programs bit depth, 10-bit RGB component ordering, source/destination format, and luma/chroma resolutions.

Channel enable only updates cached `sdata_ctrl` and `scaler_ctrl` state and marks `scaler_ctrl_chgd` when the control word changed. `dcss_scaler_write_sclctrl()` is the interrupt-context path: it asserts the context-loader lock and writes changed `SCALER_CTRL` values with `dcss_ctxld_write_irqsafe()`.

## State and persistence
Each channel persists cached scaler data-control bits, scaler-control bits, changed flag, chroma start phases, and filter mode. Filter coefficients and geometry are queued into the DCSS context loader and take effect with the broader DCSS context switch. `dcss_scaler_exit()` directly clears hardware control registers for all channels.

## Dependencies and integration points
Depends on DCSS context-loader APIs, DRM format metadata, and Linux fixed-width math helpers including `div_s64()`. It is called by DCSS plane atomic updates for every full plane setup and by the CRTC/context-load path for interrupt-safe scaler-control commit.

## Risks
The coefficient generator uses custom fixed-point math and approximated exponentials; overflow, divide-by-zero, or normalization mistakes can produce bad filters. Several resolution writes subtract one from source/destination dimensions, so atomic checks must keep dimensions nonzero. Chroma-location constants are fixed to one location in setup, which may not match all content. The scaler-control write is intentionally delayed; missing `dcss_scaler_write_sclctrl()` calls can leave channel enable state stale. `vrefresh_hz` is accepted but unused, so timing-dependent scaler choices cannot currently vary with refresh rate.

## Test signals
Useful tests cover RGB565/8888/10-bit RGB formats, NV12/NV21 YUV420, packed YUV422, equal-size identity filtering, downscale/upscale extremes per channel, nearest-neighbor property selection, enable/disable transitions, interrupt-context scaler control writes, and visual checks for chroma alignment and 10-bit component order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-scaler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-ss.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-ss.c

## Purpose
Programs the DCSS subsampler/synchronization stage. It writes output timing, sync polarity, data-enable window, subsampling coefficients, clip values, and run/stop state through the DCSS context loader.

## Important APIs, types, and functions
- `struct dcss_ss` stores the mapped SS register base, context-loader reference, context id, and `in_use` flag.
- Lifecycle functions are `dcss_ss_init()` and `dcss_ss_exit()`.
- Programming functions are `dcss_ss_subsam_set()`, `dcss_ss_sync_set()`, `dcss_ss_enable()`, and `dcss_ss_shutoff()`.
- Local helper `dcss_ss_write()` mirrors pre-enable writes directly to hardware and always queues the context-loader write.

## Control flow
Initialization allocates the SS object, maps the register window, records the register base offset, and uses `CTX_SB_HP` for context-loader writes. `dcss_ss_subsam_set()` programs fixed coefficients and clipping for the subsampler path. `dcss_ss_sync_set()` converts a `videomode` into total display size, hsync/vsync start/end, data-enable upper-left/lower-right coordinates, and polarity bits. Enable writes `RUN_EN` through the normal write path and marks the block active; shutoff directly clears the hardware control register and marks it idle.

## State and persistence
Runtime state is limited to the mapped address, context-loader identity, and `in_use`. Hardware timing and coefficients persist in the SS registers and in the context-loader buffer. The `in_use` flag controls whether writes are immediate plus queued or queued only.

## Dependencies and integration points
Depends on DCSS common register helpers, `dcss_ctxld_write()`, and Linux videomode data. It is called by the DCSS CRTC mode path before enabling output, alongside DTG and scaler programming.

## Risks
Timing derivation has small off-by-one differences from DTG, notably `de_ulc_y` without a `- 1`, so the two blocks must remain hardware-consistent. The subsampling coefficients are fixed magic values and not recomputed by mode or format. Direct shutoff bypasses the context loader, which is intentional for stop but must be ordered with other blocks.

## Test signals
Signals include stable modeset across polarity combinations, correct data-enable window, no shifted/blank output after enable, clean stop on shutdown, and visual validation when subsampling is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-ss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/Kconfig

## Purpose
Defines Kconfig options for the legacy Freescale/NXP i.MX IPUv3 DRM stack and its output encoders: parallel display, TV/VGA encoder, LVDS display bridge, and i.MX6 HDMI.

## Important APIs, types, and functions
- `DRM_IMX` enables the core IPUv3 DRM driver, depends on DRM, `ARCH_MXC || COMPILE_TEST`, and `IMX_IPUV3_CORE`, and selects DRM client/KMS/GEM DMA/videomode helpers.
- `DRM_IMX_PARALLEL_DISPLAY` enables the parallel DPI output driver and selects bridge, bridge connector, display helper, panel bridge, legacy bridge, and videomode helpers.
- `DRM_IMX_TVE` enables the i.MX53 TV/VGA encoder and selects `REGMAP_MMIO`.
- `DRM_IMX_LDB` enables the i.MX53/i.MX6 LVDS bridge and selects syscon, DRM bridge helpers, panel bridge, and legacy bridge.
- `DRM_IMX_HDMI` enables the i.MX6 DesignWare HDMI wrapper and selects `DRM_DW_HDMI`.

## Control flow
Kconfig dependency resolution determines which objects in the adjacent Makefile are built. Output drivers depend on `DRM_IMX`, so they are available only when the component-based IPUv3 DRM core is enabled.

## State and persistence
No runtime state exists. The selected symbols persist in the kernel configuration and control module/built-in composition.

## Dependencies and integration points
Integrates the IPUv3 DRM code with the kernel's DRM, bridge, panel, regmap, syscon, common-clock, and IPUv3 core subsystems. It controls whether downstream component drivers can bind into the `imx-display-subsystem` master.

## Risks
Missing selects can produce build failures only for certain configurations, especially COMPILE_TEST. `DRM_IMX_HDMI` depends on `OF` and `DRM_IMX`, while the other output drivers bring in bridge helpers explicitly. Any dependency change must preserve module ordering and component-probe expectations.

## Test signals
Signals are configuration coverage: `allyesconfig`/`allmodconfig` build, `COMPILE_TEST` build on non-MXC architectures, modular load of `imxdrm` and optional encoders, and correct absence when `DRM_IMX` or `IMX_IPUV3_CORE` is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/Makefile

## Purpose
Builds the i.MX IPUv3 DRM core module and optional output encoder modules according to the Kconfig symbols.

## Important APIs, types, and functions
- `imxdrm-objs := imx-drm-core.o ipuv3-crtc.o ipuv3-plane.o` groups the core DRM master, CRTC, and plane code into the `imxdrm` module.
- `obj-$(CONFIG_DRM_IMX) += imxdrm.o` builds the core when enabled.
- Optional objects are `parallel-display.o`, `imx-tve.o`, `imx-ldb.o`, and `dw_hdmi-imx.o`.

## Control flow
There is no runtime control flow. Kbuild expands symbol-controlled `obj-*` assignments to compile built-in or module objects.

## State and persistence
No runtime state. The object list persists as the build contract between Kconfig symbols and source files.

## Dependencies and integration points
Connects Kconfig options to the component drivers consumed by the i.MX DRM master. The core object grouping is important because `imx-drm-core.c` registers both the master platform driver and the `ipu_drm_driver` exported by `ipuv3-crtc.c`.

## Risks
Removing `ipuv3-crtc.o` or `ipuv3-plane.o` from `imxdrm-objs` would break symbols used by the core. Optional encoder objects must remain separate because they are independently controlled and may be modules.

## Test signals
Build tests should confirm the `imxdrm` module contains the core/CRTC/plane objects and each optional Kconfig symbol emits its corresponding object or module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/dw_hdmi-imx.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/dw_hdmi-imx.c

## Purpose
Provides the i.MX6-specific wrapper around the Synopsys DesignWare HDMI bridge. It supplies PHY/MPLL/current configuration tables, mode validation limits, i.MX GPR mux programming, and an encoder component that connects the generic HDMI bridge to the IPUv3 DRM device.

## Important APIs, types, and functions
- `struct imx_hdmi` stores device, regmap, generic `dw_hdmi` handle, and bridge pointer.
- `struct imx_hdmi_encoder` embeds the DRM encoder and links back to `imx_hdmi`.
- `dw_hdmi_imx_encoder_enable()` writes the HDMI mux selection into `IOMUXC_GPR3`.
- `dw_hdmi_imx_atomic_check()` sets `imx_crtc_state` bus format to RGB888 and DI hsync/vsync pins to 2/3.
- `imx6q_hdmi_mode_valid()` and `imx6dl_hdmi_mode_valid()` enforce 13.5 MHz to 216 MHz pixel-clock limits.
- `dw_hdmi_imx_probe()`, `dw_hdmi_imx_bind()`, and `dw_hdmi_imx_remove()` implement platform/component lifecycle.

## Control flow
Probe allocates private state, obtains the IOMUXC GPR syscon regmap from the `gpr` phandle, probes the generic DesignWare HDMI core with SoC-specific platform data, finds the DRM bridge from device tree, and registers as an i.MX DRM component. Bind allocates a TMDS encoder, parses possible CRTCs from the encoder's OF node, installs helper callbacks, and attaches the generic HDMI bridge. Encoder enable determines the active input port and programs the SoC HDMI mux.

## State and persistence
Runtime state persists in `struct imx_hdmi` and in the generic `dw_hdmi` instance. The selected HDMI input mux persists in IOMUXC GPR registers until changed. CRTC bus format/pin state is propagated per atomic check through `struct imx_crtc_state`.

## Dependencies and integration points
Depends on the generic `dw_hdmi` bridge driver, syscon/regmap for `fsl,imx6q-iomuxc-gpr`, DRM component binding, OF CRTC parsing, and IPUv3 CRTC state from `imx-drm.h`. It is one optional component of the `imx-display-subsystem` master.

## Risks
The wrapper caps modes at 216 MHz despite comments that hardware could go higher with missing setup data. Probe must correctly unwind both the bridge reference and `dw_hdmi` instance on component registration failure. GPR mux programming depends on device-tree port numbering and may silently choose the wrong IPU DI if graph data is wrong.

## Test signals
Validation includes probe deferral until the DW-HDMI bridge and IPUv3 CRTC exist, HDMI modes below/above the clock limits, correct DI-to-HDMI mux selection for both IPUs, EDID-driven connector creation through the bridge, and cleanup on module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/dw_hdmi-imx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/imx-drm-core.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/imx-drm-core.c

## Purpose
Implements the component-master DRM device for legacy i.MX IPUv3 display systems. It creates the DRM device, binds IPU CRTCs and output components, owns atomic commit policy, GEM DMA/fbdev support, dumb-buffer pitch alignment, suspend/resume, and platform-driver registration.

## Important APIs, types, and functions
- `imx_drm_atomic_check()` wraps `drm_atomic_helper_check()`, rechecks modesets after plane checks, and calls `ipu_planes_assign_pre()`.
- `imx_drm_atomic_commit_tail()` sequences modeset disables, active plane commits without disable-after-modeset, modeset enables, flip-done waits, deferred plane disables, and hardware-done notification.
- `imx_drm_encoder_parse_of()` sets encoder possible CRTCs from device tree and returns `-EPROBE_DEFER` when no CRTC is registered yet.
- `imx_drm_dumb_create()` aligns dumb-buffer pitch to hardware's 8-pixel scanout requirement.
- `imx_drm_bind()`/`imx_drm_unbind()` are component master callbacks.
- `imx_drm_platform_probe()` uses `drm_of_component_probe()` with `compare_of()` to collect subcomponents.

## Control flow
Probe creates the component master for `fsl,imx-display-subsystem`, then sets a 32-bit coherent DMA mask. Bind allocates a DRM device, sets mode limits/helpers, initializes managed mode config and vblank for up to four CRTCs, stores the DRM pointer on the device, binds all CRTC/output components, resets modes, validates `legacyfb_depth`, starts polling, registers the DRM device, and starts a color-mode client setup. Unbind unregisters, stops polling, runs atomic shutdown, unbinds components, drops the DRM device, and clears drvdata.

Atomic commit deliberately waits for flip completion before executing deferred plane disables because IPUv3 plane disable ordering can interact with IDMAC/DC clock state. The component match helper special-cases IPU DI platform devices whose OF node lives in platform data and LDB channel nodes whose component device is the parent LDB.

## State and persistence
The module parameter `legacyfb_depth` persists as the preferred fbdev color depth, constrained to 16 or 32. The DRM device stores mode-config state, vblank state, bound components, and plane/CRTC atomic state. No hardware registers are written directly here; those are delegated to CRTC, plane, and encoder components.

## Dependencies and integration points
Depends on Linux component framework, DRM GEM DMA/fbdev/atomic helpers, OF graph component probing, IPUv3 core support, and `ipu_planes_assign_pre()` from the plane code. It exports `imx_drm_encoder_parse_of()` to output drivers and registers both the master driver and `ipu_drm_driver`.

## Risks
The second modeset check is required because plane checks may set `crtc_state->mode_changed`; removing it can accept invalid commits. Deferred disable handling is sensitive to flip-done waits and plane `disabling` flags. Component matching for LDB and IPU DI is device-tree-shape-specific. Dumb pitch alignment must match the CRTC's hactive alignment behavior.

## Test signals
Test signals include successful component binding with IPU DI plus HDMI/LVDS/TVE/parallel components, probe deferral until CRTCs exist, atomic commits that resize or reformat planes, deferred plane disable completion, fbdev depth parameter handling, dumb-buffer pitch alignment, and suspend/resume via `drm_mode_config_helper_suspend/resume()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/imx-drm-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/imx-drm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/imx-drm.h

## Purpose
Defines the private cross-file contract for the i.MX IPUv3 DRM stack, especially the custom CRTC atomic state shared between output encoders and the IPU CRTC.

## Important APIs, types, and functions
- `struct imx_crtc_state` embeds `struct drm_crtc_state` and adds `bus_format`, `bus_flags`, `di_hsync_pin`, and `di_vsync_pin`.
- `to_imx_crtc_state()` converts generic DRM CRTC state to the i.MX extension.
- Externally declares `struct platform_driver ipu_drm_driver`.
- Declares `imx_drm_encoder_parse_of()` for encoder possible-CRTC parsing.
- Declares `ipu_planes_assign_pre()` for the core atomic check.

## Control flow
No runtime control flow exists in the header. Output encoders fill `imx_crtc_state` during atomic checks, and `ipuv3-crtc.c` consumes those fields when configuring the IPU display interface.

## State and persistence
`imx_crtc_state` fields persist per atomic state object and are duplicated/reset/destroyed by the CRTC implementation. They are not global; each modeset carries the selected bus format, bus flags, and DI sync pin mapping.

## Dependencies and integration points
Ties together `imx-drm-core.c`, `ipuv3-crtc.c`, `ipuv3-plane.c`, and output drivers such as HDMI, LDB, TVE, and parallel display. It depends on DRM CRTC state definitions via included users.

## Risks
Any encoder that fails to populate bus format/flags or DI pins can leave the CRTC with zero/default signal configuration. The header's narrow API assumes only the core needs PRE assignment and only output drivers need OF encoder parsing.

## Test signals
Compile coverage catches signature drift. Runtime signals include correct bus format selection for all encoders and CRTC mode programming that reflects each encoder's hsync/vsync pins and bus flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/imx-drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/imx-ldb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/imx-ldb.c

## Purpose
Implements the i.MX53/i.MX6 LVDS Display Bridge component for the IPUv3 DRM stack. It parses LVDS channel nodes, configures split/dual-channel mode, bus mapping and width, LVDS DI muxes, clocks, and bridge connectors.

## Important APIs, types, and functions
- `struct imx_ldb` stores the GPR regmap, two channels, DI clocks, DI mux clocks and original parents, PLL clocks, cached `ldb_ctrl`, and optional i.MX6 LVDS bus mux descriptors.
- `struct imx_ldb_channel` stores channel number, child OF node, bridge pointer, and bus format.
- Encoder helpers include `imx_ldb_encoder_atomic_mode_set()`, `imx_ldb_encoder_enable()`, `imx_ldb_encoder_disable()`, and `imx_ldb_encoder_atomic_check()`.
- Probe/bind helpers include `imx_ldb_probe()`, `imx_ldb_bind()`, `imx_ldb_register()`, `imx_ldb_get_clk()`, `of_get_bus_format()`, and `imx_ldb_ch_set_bus_format()`.

## Control flow
Probe obtains the GPR syscon regmap, resets `IOMUXC_GPR2`, records optional i.MX6 mux descriptors, detects `fsl,dual-channel`, captures available `di*_sel` mux clocks and their original parents, and iterates LVDS child nodes. Each enabled child with a valid `reg` becomes a channel, gets a downstream bridge from the output port or a legacy bridge fallback, and resolves bus format from `fsl,data-mapping`/`fsl,data-width` or later panel data.

Bind registers each populated channel. Registration allocates an LVDS encoder, parses possible CRTCs from the channel node, obtains DI/PLL clocks, adds encoder helpers, attaches the downstream bridge without a connector, creates a bridge connector, and attaches it. Mode set computes serial and DI clock rates, sets PLL and DI clocks for single or dual mode, updates VS polarity bits, and applies data-width/JEIDA/SPWG mapping. Enable sets DI mux parents, enables dual clocks, programs channel-to-DI routing and optional external LVDS mux bits, then writes `IOMUXC_GPR2`. Disable clears channel enable bits, disables dual clocks, and restores the DI mux parent.

## State and persistence
`ldb_ctrl` is the persistent software image of the LVDS control register. Clock parent state is saved at probe and restored on encoder disable. Channel bus format persists from DT or display info. Hardware state persists in GPR2/GPR3 and clock tree configuration.

## Dependencies and integration points
Depends on syscon/regmap for IOMUXC GPR registers, common clock framework, DRM bridge connector helpers, panel/legacy bridge helpers, OF graph parsing, and `imx_crtc_state` for passing RGB bus format and bus flags to the IPU CRTC.

## Risks
Dual-channel mode ignores the second output child and assumes both channels are driven from the first logical channel. Clock parent changes and GPR writes are highly SoC- and device-tree-dependent. Invalid or missing data mapping fails probe unless a bridge can later provide bus formats. Mode clock warnings do not reject over-limit modes. Disable restores only the mux inferred from channel/mux registers.

## Test signals
Validation should cover i.MX53 and i.MX6q compatible data, single- and dual-channel LVDS, SPWG 18-bit, SPWG 24-bit, JEIDA 24-bit mappings, panel-provided bus formats, external LVDS mux ports, DI0/DI1 routing, clock parent restoration, and probe deferral for downstream bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/imx-ldb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/imx-tve.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/imx-tve.c

## Purpose
Implements the i.MX53 TVEv2 encoder component for the IPUv3 DRM stack, currently limited to VGA mode. It provides DAC/regmap setup, EDID-over-DDC connector modes, clock divider registration for the TVE DI clock, encoder mode programming, IRQ clearing, and regulator handling.

## Important APIs, types, and functions
- `struct imx_tve` stores mode, DI sync pins, MMIO regmap, DAC regulator, DDC adapter, TVE clock, DI mux clock, registered `tve_di` clock, and derived DI clock.
- Encoder/connector helpers include `imx_tve_encoder_mode_set()`, `imx_tve_encoder_enable()`, `imx_tve_encoder_disable()`, `imx_tve_atomic_check()`, `imx_tve_connector_get_modes()`, and `imx_tve_connector_mode_valid()`.
- Hardware helpers are `tve_enable()`, `tve_disable()`, `tve_setup_vga()`, `tve_setup_tvout()`, and `imx_tve_irq_handler()`.
- Clock-provider callbacks are `clk_tve_di_recalc_rate()`, `clk_tve_di_determine_rate()`, and `clk_tve_di_set_rate()`.
- Probe/bind functions are `imx_tve_probe()` and `imx_tve_bind()`.

## Control flow
Probe optionally resolves a DDC I2C adapter, parses `fsl,tve-mode`, rejects non-VGA modes, reads VGA hsync/vsync pin properties, maps MMIO through regmap with the `tve` clock, installs a threaded IRQ handler, enables the DAC regulator when present, obtains the high-speed TVE clock and IPU DI mux clock, registers a derived `tve_di` clock, validates the TVEv2 reset value, disables cable detection, and registers the component.

Bind creates a DAC or TVDAC encoder depending on mode, parses possible CRTCs, adds helper callbacks, initializes a VGA connector with optional DDC, and attaches it. Mode set configures the high-speed TVE clock at 2x the pixel rate, selects an oversampling divider, parents the IPU DI mux to `tve_di`, enables the IPU clock bit, then runs VGA setup. VGA setup writes DAC gains, RGB output mode, sync channel, input form, TV standard selector, and test mode. Enable turns on the clock and TVE enable bit and configures interrupts; disable clears enable and disables the clock.

## State and persistence
Runtime state persists in `struct imx_tve` and the registered clock provider. Regmap writes persist in TVE registers, including DAC gains, configuration, interrupt masks, and divider selection. The DAC regulator is enabled for device lifetime and disabled through devm action.

## Dependencies and integration points
Depends on DRM connector/encoder helpers, I2C DDC, regmap MMIO with clock support, common clock framework, regulator framework, OF properties, and `imx_crtc_state`. It integrates as an optional component under the i.MX DRM master.

## Risks
TVOUT mode is parsed but unimplemented and rejected; only VGA is usable. `mode_valid()` requires exact rounded TVE clock rates and can reject otherwise reasonable modes. The clock divider is encoded through TVE register bits, so clock and register state are coupled. The IRQ handler only clears status and does not report cable-detection changes. Probe validates a hardcoded reset value, which can fail on hardware left in a non-reset state by firmware.

## Test signals
Tests should cover VGA probe with and without DDC, missing hsync/vsync properties, mode validation at exact and inexact clock rates, regulator voltage warning path, TVE clock parent selection, suspend/remove cleanup, and visible VGA output with expected sync pins and RGB amplitude.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/imx-tve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/ipuv3-crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/ipuv3-crtc.c

## Purpose
Implements IPUv3 DRM CRTC components. It binds IPU display-interface/DC resources, creates the primary and optional overlay planes, programs display timing and DI signal configuration, handles vblank/page-flip events, and controls IPU/DC/DI/PRG enable sequencing.

## Important APIs, types, and functions
- `struct ipu_crtc` embeds `struct drm_crtc`, stores full and partial planes, IPU DC/DI handles, EOF IRQ, and pending vblank event.
- CRTC state management uses `imx_drm_crtc_reset()`, `imx_drm_crtc_duplicate_state()`, and `imx_drm_crtc_destroy_state()` for `struct imx_crtc_state`.
- Atomic helper callbacks include `ipu_crtc_mode_fixup()`, `ipu_crtc_mode_set_nofb()`, `ipu_crtc_atomic_check()`, `ipu_crtc_atomic_begin()`, `ipu_crtc_atomic_flush()`, `ipu_crtc_atomic_enable()`, and `ipu_crtc_atomic_disable()`.
- Resource/component functions include `ipu_get_resources()`, `ipu_put_resources()`, `ipu_drm_bind()`, `ipu_drm_probe()`, and exported `ipu_drm_driver`.

## Control flow
Component bind creates a primary IPU plane for the platform DMA channel, allocates a CRTC with that plane, stores the DI OF port, attaches helper funcs, obtains DC and DI resources from the parent IPU, optionally creates a DP foreground overlay plane, and registers the primary plane EOF IRQ disabled.

Mode fixup converts DRM mode to videomode, asks the IPU DI to adjust it, rejects zero sync lengths, and converts back. Mode set gathers attached encoder types to choose DI clocking mode, consumes bus format/flags and sync pins from `imx_crtc_state`, aligns hactive to 8 pixels by shrinking front porch if necessary, initializes DC sync and DI panel timing. Atomic enable turns on PRG, DC, DC channel, and DI. Atomic disable shuts down DC channel and DI, disables planes before removing the DC clock, disables DC and PRG, turns vblank off, and sends pending events if the CRTC is inactive.

Vblank enable/disable toggles the EOF IRQ. The IRQ handler calls `drm_crtc_handle_vblank()` and, when a page-flip event is pending, waits until all associated planes report no pending update before sending the event and dropping the vblank reference.

## State and persistence
`ipu_crtc` persists for the component lifetime and owns IPU DC/DI resource handles. Atomic CRTC state persists bus format, bus flags, and sync pins supplied by encoders. Pending page-flip event state lives in `ipu_crtc->event` until the EOF handler completes it.

## Dependencies and integration points
Depends on `video/imx-ipu-v3.h` APIs for DC, DI, PRG, and IDMAC resources, DRM vblank/event helpers, component framework, and `ipuv3-plane.c` for plane creation and pending-update checks. The platform data supplies DI/DC/DMA channel numbers and OF node identity.

## Risks
Disable ordering is safety-critical: planes must be disabled before DC clocks are removed to avoid undefined IDMAC/IPU state. Hactive alignment mutates timing and can underflow front porch on marginal modes. Event completion depends on plane pending checks, especially when PRE/PRG is used. `ipu_enable_vblank()` unconditionally enables an IRQ requested with `IRQF_NO_AUTOEN`, so mismatched disable counts would warn.

## Test signals
Validation includes modes needing DI adjustment, invalid zero sync lengths, DAC/LVDS/TVDAC/HDMI clock-flag selection, hactive alignment warnings, vblank enable/disable, page-flip event completion with PRE and non-PRE planes, overlay creation only when DP flow is available, and shutdown with active scanout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/ipuv3-crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/ipuv3-plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/ipuv3-plane.c

## Purpose
Implements IPUv3 DRM primary and overlay planes. It validates framebuffer geometry and IPU memory constraints, assigns optional PRE/PRG resources, configures IDMAC/DMFC/DP channels and CPMEM descriptors, handles separate alpha planes, and performs double-buffered base-address flips.

## Important APIs, types, and functions
- `struct ipu_plane_state` extends DRM plane state with `use_pre`.
- Format lists split all DP-capable formats from RGB-only formats, with optional PRE modifiers for Vivante tiled and super-tiled buffers.
- Public APIs are `ipu_plane_init()`, `ipu_plane_irq()`, `ipu_plane_disable()`, `ipu_plane_disable_deferred()`, `ipu_plane_atomic_update_pending()`, and `ipu_planes_assign_pre()`.
- Address helpers include `drm_plane_state_to_eba()`, `drm_plane_state_to_ubo()`, and `drm_plane_state_to_vbo()`.
- Atomic hooks are `ipu_plane_atomic_check()`, `ipu_plane_atomic_update()`, and `ipu_plane_atomic_disable()`.

## Control flow
Initialization chooses format lists based on whether the plane is attached to a DP flow, enables PRE modifiers when PRG is present, allocates the universal plane, adds zpos/color properties, and obtains IDMAC, optional alpha IDMAC, DMFC, and optional DP resources. Atomic check enforces no scaling, overlay-only positioning, minimum dimensions, EBA alignment, pitch limits, 8-pixel framebuffer width alignment, planar YUV U/V offset constraints, chroma-aligned source offsets, and separate-alpha address/pitch constraints. It forces a CRTC mode change when active plane size, format, pitch, or planar offsets change.

`ipu_planes_assign_pre()` runs during the core atomic check. It first adds affected planes for all affected CRTCs, then assigns scarce PRE channels to tiled buffers as a hard requirement and to eligible linear buffers as an optimization. Atomic update programs DP window/global-alpha state, computes width/height, optionally configures PRG/PRE and substitutes the internal SRAM EBA, updates DP colorspace on color/format changes, fast-paths base flips when no modeset is needed and PRE is not used, otherwise programs DMFC, CPMEM resolution/format/burst/stride/AXI ID/YUV offsets/separate alpha, enables double buffering, locks IDMAC bursts, and enables the plane. Atomic disable disables DP channel early and marks deferred disable for later core commit-tail cleanup.

## State and persistence
Plane objects persist resource handles and a `disabling` flag. Atomic plane state persists `use_pre`. Hardware state persists in IDMAC, CPMEM, DMFC, DP, and PRG/PRE channels. Double-buffered address state is updated in the inactive buffer for fast flips. Separate alpha uses a second IDMAC channel when the DRM format requires it.

## Dependencies and integration points
Depends on IPUv3 IDMAC/DMFC/DP/PRG/PRE APIs, DRM atomic helpers, GEM DMA framebuffer helpers, DRM color properties, and the core commit tail in `imx-drm-core.c` for deferred disables. It provides the vblank IRQ source for the CRTC through `ipu_plane_irq()`.

## Risks
Alignment and offset rules are hardware constraints; relaxing them can hang IDMAC or scan out wrong planes. Active geometry/format changes require a forced modeset so CRTC disable can stop planes safely. PRE assignment is global and scarce; tiled buffers fail if no PRE is available. The fast flip path returns without reprogramming when PRE is used, assuming PRG handles pending updates. Separate alpha paths must keep color and alpha buffers synchronized.

## Test signals
Coverage should include packed RGB, packed YUV, planar YUV, NV12/NV16, separate alpha formats, tiled modifiers with PRG/PRE, linear fallback without PRE, active format/size/pitch changes, chroma-unaligned crop rejection, double-buffered page flips, deferred disable completion, and DP overlay zpos/global-alpha behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/ipuv3-plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/ipuv3-plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/ipuv3-plane.h

## Purpose
Declares the IPUv3 DRM plane object and the plane APIs used by the CRTC and DRM core.

## Important APIs, types, and functions
- `struct ipu_plane` embeds `struct drm_plane` and stores IPU, IDMAC, alpha IDMAC, DMFC, DP flow, DMA channel number, and deferred-disable state.
- Declares `ipu_plane_init()`, `ipu_plane_irq()`, `ipu_plane_disable()`, `ipu_plane_disable_deferred()`, and `ipu_plane_atomic_update_pending()`.
- A legacy `ipu_plane_mode_set()` prototype remains declared even though this atomic implementation uses atomic update paths instead.

## Control flow
No runtime control flow exists here. The header defines ownership and callable entry points: CRTC creation calls `ipu_plane_init()`, CRTC IRQ setup calls `ipu_plane_irq()`, CRTC disable/commit-tail use disable helpers, and IRQ event completion uses `ipu_plane_atomic_update_pending()`.

## State and persistence
`struct ipu_plane` persists all hardware resource handles for a plane and the `disabling` flag that bridges atomic plane disable to deferred hardware shutdown after flip completion.

## Dependencies and integration points
Depends on DRM CRTC/plane types and forward declarations for IPUv3 resources. It is included by `imx-drm-core.c`, `ipuv3-crtc.c`, and `ipuv3-plane.c`.

## Risks
The header exposes internal resource fields, so other files can couple to implementation details. The stale-looking `ipu_plane_mode_set()` declaration can confuse readers and should be checked before any refactor.

## Test signals
Compile coverage catches API drift. Runtime signals are correct CRTC access to plane IRQs, pending-update checks, and deferred disable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/ipuv3-plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/parallel-display.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/parallel-display.c

## Purpose
Implements the i.MX IPUv3 parallel DPI display component. It bridges the IPU display interface to a downstream panel/bridge, negotiates bus formats and flags, supports legacy `interface-pix-fmt` device-tree overrides, and creates a bridge connector.

## Important APIs, types, and functions
- `struct imx_parallel_display` stores the selected bus format, next bridge, local bridge, and device pointer.
- Bridge callbacks include `imx_pd_bridge_attach()`, `imx_pd_bridge_atomic_check()`, `imx_pd_bridge_atomic_get_input_bus_fmts()`, and `imx_pd_bridge_atomic_get_output_bus_fmts()`.
- `imx_pd_bind()` creates the DRM encoder and bridge connector.
- `imx_pd_probe()` resolves the downstream bridge or legacy bridge, parses `interface-pix-fmt`, registers the local bridge, and adds the component.

## Control flow
Probe allocates a DRM bridge, looks for the output bridge at port 1, falls back to an i.MX legacy DPI bridge when no graph bridge exists, maps legacy string formats such as `rgb24`, `rgb565`, `bgr666`, and `lvds666` to media bus formats, registers the local bridge, and joins the component framework. Bind allocates a simple encoder, parses possible CRTCs, attaches the local bridge without a connector, creates a bridge connector, and attaches it.

During bus negotiation, output formats come from the legacy override, downstream display info, or the local supported list. Input formats validate the requested output and prefer the legacy DT format when it differs from the downstream output, preserving old board descriptions with physical swizzling. Atomic check copies downstream bus flags into both bridge bus configs and into `imx_crtc_state`, along with the selected input bus format and DI pins 2/3.

## State and persistence
The only persistent runtime setting is `imxpd->bus_format`, parsed from device tree or zero when negotiated from the panel. Per-commit bus format/flags persist in bridge state and `imx_crtc_state`.

## Dependencies and integration points
Depends on DRM bridge connector helpers, OF graph bridge lookup, i.MX legacy bridge support, and `imx_drm_encoder_parse_of()`. It integrates with the IPUv3 CRTC by supplying bus format, flags, and DI pins through atomic check.

## Risks
Legacy `interface-pix-fmt` can intentionally override the panel format, so changing precedence can break old DTs. Unsupported bus formats return no input formats or fail atomic check. `drm_bridge_attach()` in bind is not checked for failure in the current code path, so downstream attach issues could surface later.

## Test signals
Test cases should include graph bridges, legacy bridge fallback, each legacy pixel-format string, panel-provided bus formats, unsupported format rejection, bus flag propagation, probe deferral, and connector creation for DPI panels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/parallel-display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/lcdc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/lcdc/Kconfig

## Purpose
Defines the Kconfig option for the simple DRM driver for older Freescale i.MX LCDC display controllers.

## Important APIs, types, and functions
- `DRM_IMX_LCDC` is a tristate option for i.MX1, i.MX21, i.MX25, and i.MX27 LCDC displays.
- It depends on DRM and `ARCH_MXC || COMPILE_TEST`.
- It selects DRM client selection, GEM DMA helper, KMS helper, display helper, and bridge connector support.

## Control flow
Kconfig selection controls whether `imx-lcdc.o` is built by the local Makefile. There is no runtime control flow in the file.

## State and persistence
No runtime state exists. The symbol persists in kernel configuration and controls built-in/module availability.

## Dependencies and integration points
Integrates the LCDC driver with the DRM helper stack and bridge connector infrastructure needed by `imx-lcdc.c`.

## Risks
The driver relies on bridge lookup and GEM DMA helpers, so missing selects would surface as build failures in modular or COMPILE_TEST configurations. The option is independent from `DRM_IMX` because LCDC is a distinct older controller path.

## Test signals
Build `DRM_IMX_LCDC=y/m` with `ARCH_MXC` and with `COMPILE_TEST`, and verify the symbol can be disabled independently of the IPUv3/DCSS i.MX DRM drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/lcdc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/lcdc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/lcdc/Makefile

## Purpose
Connects the `DRM_IMX_LCDC` Kconfig symbol to the `imx-lcdc.o` driver object.

## Important APIs, types, and functions
- `obj-$(CONFIG_DRM_IMX_LCDC) += imx-lcdc.o` is the only build rule.

## Control flow
No runtime flow. Kbuild includes or omits the LCDC driver according to the Kconfig symbol.

## State and persistence
No runtime state exists; the build rule persists as the module composition contract.

## Dependencies and integration points
Ties the standalone LCDC DRM driver source to the kernel build system.

## Risks
Because the Makefile has one object, renaming or splitting `imx-lcdc.c` requires updating this rule.

## Test signals
Build coverage should produce `imx-lcdc.o` when `CONFIG_DRM_IMX_LCDC` is enabled and omit it when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/lcdc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/lcdc/imx-lcdc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/lcdc/imx-lcdc.c

## Purpose
Implements a simple DRM/KMS driver for older i.MX LCDC controllers. It uses a single simple display pipe, DMA-backed framebuffers, a downstream bridge connector, clock-gated register programming, EOF vblank interrupts, and strict mode limits.

## Important APIs, types, and functions
- `struct imx_lcdc` embeds `struct drm_device`, `struct drm_simple_display_pipe`, connector pointer, MMIO base, and IPG/AHB/PER clocks.
- Pipe callbacks are `imx_lcdc_pipe_enable()`, `imx_lcdc_pipe_disable()`, `imx_lcdc_pipe_check()`, and `imx_lcdc_pipe_update()`.
- Hardware programming is centralized in `imx_lcdc_update_hw_registers()` and `imx_lcdc_get_format()`.
- Lifecycle functions are `imx_lcdc_probe()`, `imx_lcdc_remove()`, and `imx_lcdc_shutdown()`.
- IRQ handling is in `imx_lcdc_irq_handler()`.

## Control flow
Probe allocates the DRM device, maps MMIO, finds the downstream bridge, obtains the three clocks, sets a 32-bit DMA mask, initializes managed mode config, creates a simple display pipe for RGB565/XRGB8888, initializes vblank, attaches the bridge and bridge connector, toggles all clocks once to reset a potentially bootloader-enabled LCDC, sets mode limits and helpers, requests the IRQ, registers the DRM device, and starts client setup.

Pipe enable programs LPCR polarity, TFT/color/bpp/clock divider fields, clears panning and hardware cursor bits, enables IPG and AHB clocks, calls the register update path with a full mode set, and enables EOF interrupts. Register update always writes the screen start address; for modesets it temporarily disables the PER clock if the old CRTC was enabled, programs frame size, horizontal/vertical porch/sync registers, format bpp, virtual page width, and re-enables PER if the new CRTC is enabled. Pipe update detects format or CRTC changes, updates registers, and arms or sends pending vblank events. Disable turns off clocks, completes any pending event, and disables EOF interrupts.

## State and persistence
DRM state persists in the embedded DRM device and simple pipe. Hardware state persists in LCDC registers such as LSSAR, LSR, LHCR, LVCR, LPCR, LVPWR, and LIER. Clock enable state is carefully managed because the controller starts directly when clocks are enabled and has no explicit enable bit.

## Dependencies and integration points
Depends on DRM simple display pipe, GEM DMA helpers with vmap/fbdev support, dirty framebuffer creation, bridge connector helpers, Linux clock framework, platform resources, and DRM vblank/event helpers. Device tree provides the MMIO region, IRQ, clocks, and downstream bridge.

## Risks
The controller has no enable bit, so incorrect clock ordering can start it with invalid register state. Mode checks enforce 64..1024 dimensions and hdisplay multiple of 16; unsupported panels fail atomic check. Frame size and porch fields have controller-specific encodings and offsets. `clk_div - 1` assumes a nonzero rounded divider. IRQ status is handled but not explicitly cleared in the handler, relying on controller semantics.

## Test signals
Validation should cover RGB565 and XRGB8888, mode size and hdisplay alignment rejection, bridge probe deferral, bootloader-left-on reset by clock toggling, page flips that only update LSSAR, format changes requiring full register update, vblank event delivery on EOF, and shutdown/remove with active output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/lcdc/imx-lcdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/Kconfig

## Purpose
Defines Kconfig options for the Ingenic DRM display controller driver, optional Ingenic IPU plane support, and JZ4780 DesignWare HDMI wrapper.

## Important APIs, types, and functions
- `DRM_INGENIC` is the main tristate driver, depending on MIPS or COMPILE_TEST, DRM, CMA, OF, and COMMON_CLK.
- The main option selects DRM bridge, client, panel bridge, KMS/display helpers, bridge connector, GEM DMA helper, and regmap support.
- `DRM_INGENIC_IPU` is a bool suboption that exposes the Ingenic IPU as a second primary plane.
- `DRM_INGENIC_DW_HDMI` is a tristate JZ4780 DW-HDMI wrapper depending on `MACH_JZ4780` and selecting `DRM_DW_HDMI`.

## Control flow
Kconfig controls which objects the Makefile builds and whether `ingenic-drm-drv.c` compiles IPU component-master support. `DRM_INGENIC_IPU` is a bool nested under the main driver, so it modifies the main module rather than creating a separate module choice.

## State and persistence
No runtime state exists. Selected symbols persist in kernel configuration and drive module composition.

## Dependencies and integration points
Integrates the Ingenic display driver with DRM helpers, CMA-backed GEM DMA, OF graph bridge/panel discovery, regmap MMIO, common clocks, and optional DW-HDMI.

## Risks
The HDMI wrapper depends on `MACH_JZ4780`, so COMPILE_TEST coverage for HDMI may be narrower than for the main DRM driver. Optional IPU support affects build composition and runtime component binding, so configuration combinations must be tested.

## Test signals
Build `DRM_INGENIC` with and without `DRM_INGENIC_IPU`, and build `DRM_INGENIC_DW_HDMI` on JZ4780 configs. Confirm selected helper dependencies avoid unresolved symbols in modular builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/Makefile

## Purpose
Builds the Ingenic DRM driver, optional IPU object, and optional DesignWare HDMI wrapper.

## Important APIs, types, and functions
- `obj-$(CONFIG_DRM_INGENIC) += ingenic-drm.o` builds the main module.
- `ingenic-drm-y = ingenic-drm-drv.o` makes the display controller driver the base object.
- `ingenic-drm-$(CONFIG_DRM_INGENIC_IPU) += ingenic-ipu.o` conditionally links IPU support into the main driver.
- `obj-$(CONFIG_DRM_INGENIC_DW_HDMI) += ingenic-dw-hdmi.o` builds the HDMI wrapper separately.

## Control flow
No runtime flow. Kbuild composes the main module and optional objects from Kconfig symbols.

## State and persistence
No runtime state exists. The Makefile records build-time module composition.

## Dependencies and integration points
Connects Kconfig options to the core Ingenic DRM source, the optional IPU integration source, and the DW-HDMI wrapper source.

## Risks
The IPU object is linked into `ingenic-drm.o`; mismatched `CONFIG_DRM_INGENIC_IPU` guards between sources can cause unresolved references. HDMI remains a separate module/object and must coordinate through OF graph rather than direct linking.

## Test signals
Build matrix should include main-only, main+IPU, HDMI-only dependencies satisfied, and all enabled together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-drm-drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-drm-drv.c

## Purpose
Implements the main DRM/KMS driver for Ingenic JZ47xx LCD controllers. It supports SoC-specific format/plane capabilities, descriptor-driven DMA scanout, optional OSD overlay and IPU plane integration, palette/gamma handling for C8, bridge/panel output discovery, vblank interrupts, non-coherent framebuffer syncing, and pixel-clock coordination.

## Important APIs, types, and functions
- Hardware descriptors are `struct ingenic_dma_hwdesc` and `struct ingenic_dma_hwdescs`, including an optional palette descriptor and extended JZ4780 descriptor fields.
- `struct jz_soc_info` describes per-SoC capabilities: device clock need, OSD/alpha support, non-coherent mapping, extended descriptors, broken F0 plane, max burst, max dimensions, and format lists.
- `struct ingenic_drm` is the private device object embedding DRM device, planes, CRTC, clocks, regmap, DMA descriptors, clock notifier state, and private atomic object.
- Atomic paths include `ingenic_drm_crtc_atomic_check()`, `ingenic_drm_crtc_atomic_begin()`, `ingenic_drm_crtc_atomic_flush()`, `ingenic_drm_crtc_atomic_enable()`, `ingenic_drm_crtc_atomic_disable()`, `ingenic_drm_plane_atomic_check()`, `ingenic_drm_plane_atomic_update()`, and `ingenic_drm_plane_atomic_disable()`.
- Bridge/encoder paths include `ingenic_drm_bridge_atomic_check()`, `ingenic_drm_bridge_atomic_enable()`, `ingenic_drm_bridge_atomic_disable()`, `ingenic_drm_bridge_atomic_get_input_bus_fmts()`, and `ingenic_drm_encoder_atomic_mode_set()`.
- Lifecycle functions include `ingenic_drm_bind()`, `ingenic_drm_probe()`, `ingenic_drm_unbind()`, suspend/resume, shutdown, module init, and module exit.

## Control flow
Probe either binds directly or creates a component master when IPU support is enabled and an IPU graph endpoint exists at port 8. Bind resolves SoC data, optionally attaches reserved memory, allocates the DRM device, initializes mode config, maps MMIO through regmap, obtains IRQ and clocks, allocates coherent DMA descriptor memory, initializes descriptor rings for F0/F1/palette, creates the primary plane on F1 when OSD exists or F0 otherwise, creates the CRTC, enables palette color management, optionally creates the OSD overlay and binds the IPU component, discovers all downstream panels/bridges from output port entries, creates one encoder/local bridge/connector per output, sets possible clone masks, requests IRQ, initializes vblank, enables clocks, configures OSD/alpha, registers a pixel-clock parent notifier, initializes the private atomic object, registers DRM, and starts client setup.

Atomic CRTC check validates gamma LUT size, ensures the private state is present, pulls F1/F0/IPU plane states on modesets, rejects simultaneous F1 and IPU use, and records `no_vblank` when all scanout planes are disabled. Plane check rejects broken F0 on affected SoCs, runs no-scaling DRM checks, enforces no positioning when OSD is absent, records whether the palette descriptor is needed for C8, forces modesets for OSD enable/disable/position/size/depth changes, and requests damage tracking for non-coherent systems. Plane update syncs non-coherent damage, writes descriptor address/command/next fields, fills extended descriptor fields when required, reprograms plane format/position on modesets, and updates palette data when color management changed.

Bridge atomic check stores the negotiated output bus config, adjusts 3x8-bit serial modes by tripling dot-clock timing fields while preserving display area, and validates supported bus formats. Encoder mode set programs LCD CFG/RGBC fields from connector type, bus format, bus flags, Sharp panel flag, descriptor mode, and sync polarity. CRTC flush updates timings and pixel clock, coordinating with the clock notifier mutex, and arms or sends vblank events. Bridge enable clears state and sets LCD enable; bridge disable requests LCD disable and polls the disabled bit.

## State and persistence
Persistent runtime state includes `struct ingenic_drm`, SoC capability table pointer, DMA descriptor memory, palette table, clock notifier flags, private atomic `use_palette`, plane enable bits, and `no_vblank`. Hardware state persists in LCD timing/config/OSD registers, DMA descriptor base registers, descriptor memory read by the LCD controller, OSD plane registers, pixel/lcd clocks, and optional reserved-memory mappings.

## Dependencies and integration points
Depends on DRM atomic, bridge, connector, color-management, GEM DMA, fbdev, and vblank helpers; regmap MMIO; common clocks and clock notifiers; OF graph panel/bridge lookup; reserved memory; optional component framework for IPU; and functions exported in `ingenic-drm.h` for IPU support. It integrates with `ingenic-dw-hdmi.c` through OF graph as a downstream bridge/connector path.

## Risks
Descriptor rings are hardware-facing and must remain coherent and correctly chained, especially when palette mode switches `DA0` to descriptor 2. `no_vblank` disables vblank when no planes are active, so event paths must handle that case. Pixel-clock parent changes wait for one vblank while holding a mutex; missing vblank or disabled CRTC scenarios can cause latency or deadlock risks. 3x8 serial timing rewriting is unusual and can regress modes if fields are not kept consistent. Non-coherent framebuffer sync relies on damage clips. Simultaneous IPU/F1 use is rejected only when IPU support is compiled and bound. The JZ4780 F0 plane is explicitly disabled as not working.

## Test signals
Validation should cover each compatible SoC table, OSD and non-OSD modes, F0/F1 format lists, C8 palette/gamma LUT size and palette descriptor chaining, page flips, OSD position/size modesets, bridge bus formats including 3x8 serial, TV connector mode selection, vblank IRQ enable/disable with no planes, clock-rate changes, suspend/resume, non-coherent damage flushing on JZ4770, IPU component binding and F1/IPU mutual exclusion, and clean module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-drm-drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-drm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-drm.h

## Purpose
Defines Ingenic LCD controller register offsets, bit fields, descriptor fields, and the small private API shared between the main Ingenic DRM driver and optional IPU support.

## Important APIs, types, and functions
- Register offsets cover timing/config/control/state/DMA descriptor registers, RGB configuration, OSD control/status, alpha/keying, IPU restart, plane position/size, and priority config.
- Bit definitions cover LCD mode selection, sync polarity, bus width, descriptor width, burst size, EOF/SOF interrupts, frame enable, palette enable, OSD F0/F1 enables, IPU source selection, color depth, RGB ordering, descriptor size/cpos fields, and priority thresholds.
- Exports `ingenic_drm_plane_config()`, `ingenic_drm_plane_disable()`, and `ingenic_drm_map_noncoherent()`.
- Declares `extern struct platform_driver *ingenic_ipu_driver_ptr` for optional IPU driver registration.

## Control flow
No executable control flow exists. The macros are consumed by register programming and descriptor construction in `ingenic-drm-drv.c` and by optional IPU code that needs to configure or disable shared LCD planes.

## State and persistence
No C state is defined, but the constants describe persistent hardware state in LCD controller registers and DMA descriptors. The declared functions operate on the main driver's private state found from `struct device`.

## Dependencies and integration points
Depends on Linux bit operation/types headers and forward declarations for device, DRM plane, plane state, and platform driver. It is the private integration point between the LCD controller driver, IPU integration, and any local code that needs shared register definitions.

## Risks
Register-field mistakes are high impact because they affect DMA descriptor interpretation, pixel format, interrupts, and output timing. The typo-like `JZ_LCD_CTRL_LSB_FISRT` name must remain consistent with users. Exposing plane config/disable to IPU code requires stable semantics around plane identity and device drvdata.

## Test signals
Build coverage catches macro/API drift. Runtime validation comes indirectly from correct mode setup, plane enable/disable, descriptor DMA operation, OSD/IPU integration, interrupts, and format programming on all supported SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-dw-hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-dw-hdmi.c

## Purpose
Provides the Ingenic JZ4780-specific platform wrapper for the generic Synopsys DesignWare HDMI bridge. It supplies PHY/MPLL/current tables, clock range validation, output-port selection, and devm cleanup.

## Important APIs, types, and functions
- Static platform data includes `ingenic_mpll_cfg`, `ingenic_cur_ctr`, `ingenic_phy_config`, and `ingenic_dw_hdmi_plat_data`.
- `ingenic_dw_hdmi_mode_valid()` restricts modes to 13.5 MHz through 216 MHz pixel clock.
- `ingenic_dw_hdmi_probe()` calls `dw_hdmi_probe()` and registers `ingenic_dw_hdmi_cleanup()` as a devm action.
- OF match supports `ingenic,jz4780-dw-hdmi`.

## Control flow
Probe is intentionally small: the generic DW-HDMI core is probed with Ingenic platform data and, if successful, registered for automatic removal with `devm_add_action_or_reset()`. The generic bridge uses `output_port = 1` to connect into the OF graph. Mode validation rejects very low clocks and clocks above 216 MHz because setup data for higher rates is missing.

## State and persistence
Runtime state is owned by the generic `dw_hdmi` instance returned from probe. This file stores no private struct. PHY configuration tables are static read-only data.

## Dependencies and integration points
Depends on the generic `drm/bridge/dw_hdmi` driver, OF platform matching, and DRM mode status definitions. It integrates with the Ingenic LCD controller driver through device-tree bridge discovery rather than direct symbol calls.

## Risks
The 216 MHz cap is conservative and may reject hardware-capable modes. Cleanup depends entirely on `dw_hdmi_remove()` through the devm action. The wrapper does not add Ingenic-specific mux or clock programming beyond generic DW-HDMI platform data, so board integration relies on device tree and the generic bridge.

## Test signals
Validation includes probing `ingenic,jz4780-dw-hdmi`, EDID and connector creation through the generic bridge, mode validation at 13.5 MHz and 216 MHz boundaries, graph connection via output port 1, and module removal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-dw-hdmi.c -->
