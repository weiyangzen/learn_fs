# Research: subset-b-003760

Grouped research for VC4 DRM driver sources under `sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/`. Each section preserves its original source path for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_crtc.c

## Purpose
`vc4_crtc.c` implements VC4 PixelValve-backed DRM CRTC support. In this hardware family, a PixelValve generates output timings, pulls scanout data from the HVS FIFO, and feeds an encoder such as HDMI, DSI, DPI, VEC, SMI, or TXP. The file binds PixelValve platform devices as component CRTCs, configures timing registers during atomic modesets, handles vblank/page-flip events, initializes CRTC state and primary planes, maps PixelValve-to-encoder compatibility, and exposes PixelValve registers through debugfs.

## Important APIs, Types, And Functions
- Register access is routed through `CRTC_READ()` and `CRTC_WRITE()`, which intentionally call `kunit_fail_current_test()` to catch accidental hardware access in unit tests.
- `vc4_crtc_get_cob_allocation()` reads HVS COB/FIFO allocation from generation-specific HVS registers and returns the allocated pixel count for scanout-position estimation.
- `vc4_crtc_get_scanout_position()` is the DRM vblank timestamp helper. It samples HVS status, converts HVS composition position into PixelValve scanout position, compensates for FIFO depth, handles interlace field offset, and uses `t_vblank` in vblank IRQ context.
- `vc4_crtc_config_pv()` programs PixelValve timing, interlace, DSI-specific active width, mux, FIFO full level, pixel repetition, output clock select, and enable-control bits.
- `vc4_crtc_disable()`, `vc4_crtc_atomic_disable()`, and `vc4_crtc_atomic_enable()` sequence the HVS, PixelValve, encoder callbacks, vblank state, and hardware reset during atomic transitions.
- `vc4_crtc_disable_at_boot()` detects firmware-left HDMI PixelValves on BCM2711/BCM2712 variants and powers down the associated HDMI path before KMS owns it.
- `vc4_crtc_handle_vblank()`, `vc4_crtc_handle_page_flip()`, and `vc4_crtc_irq_handler()` process `PV_INT_VFP_START`, timestamp vblank, send events, manage vblank refs, and unmask HVS underrun after a page flip lands.
- Async page-flip support is implemented by `vc4_async_page_flip_common()`, `vc4_async_set_fence_cb()`, `vc4_async_page_flip()`, `vc5_async_page_flip()`, and `vc4_page_flip()`, using dma-reservation fences before updating the primary plane address.
- State functions `vc4_crtc_duplicate_state()`, `vc4_crtc_destroy_state()`, and `vc4_crtc_reset()` manage `struct vc4_crtc_state`, including display-list MM nodes and assigned HVS channels.
- Hardware description tables `bcm2835_pv*_data`, `bcm2711_pv*_data`, and `bcm2712_pv*_data` define PixelValve names, FIFO depth, pixels-per-clock, HVS outputs/channels, and legal encoder types.
- `__vc4_crtc_init()` and `vc4_crtc_init()` are reusable CRTC constructors; `__vc4_crtc_init()` exists partly for KUnit injection of planes and callback tables.

## Control Flow
Component probing calls `vc4_crtc_dev_probe()`, adds `vc4_crtc_ops`, and eventually `vc4_crtc_bind()` allocates `struct vc4_crtc`, maps registers, initializes debugfs regset metadata, creates the primary plane and CRTC, assigns encoder possible masks, clears interrupts, requests the shared PixelValve IRQ, and stores driver data.

During atomic enable, DRM calls `vc4_crtc_atomic_enable()`. The function enters the DRM device, verifies HVS enablement, enables vblank accounting before HVS list updates, calls `vc4_hvs_atomic_enable()`, runs encoder `pre_crtc_configure`, programs PixelValve timing through `vc4_crtc_config_pv()`, sets `PV_CONTROL_EN`, invokes encoder pre/post enable hooks, and sets `PV_VCONTROL_VIDEN`. Disable follows the reverse shape: vblank is turned off, `PV_VCONTROL_VIDEN` is cleared and polled, a BCM2711 HDMI FIFO workaround delay is applied, encoder post-disable/powerdown hooks run, the PixelValve FIFO is reset, and the HVS channel is stopped.

Page flip control splits into synchronous atomic flips and async flips. For async flips, the driver allocates `struct vc4_async_flip_state`, holds framebuffer and vblank references, updates the primary plane state immediately, waits for the framebuffer object's dma-reservation READ fence if present, then updates the plane address and emits the event once the fence signals. On GEN_4, BO usecount is manually balanced because the async path bypasses normal prepare/cleanup hooks.

The interrupt path reads `PV_INTSTAT`; on v-front-porch start it clears the bit, records `t_vblank`, lets DRM handle vblank, and checks whether the HVS display list pointer has reached `current_dlist` before sending a queued page-flip event. The handler uses both `dev->event_lock` and `vc4_crtc->irq_lock` to coordinate with atomic display-list updates.

## State And Persistence Behavior
Persistent runtime state lives in `struct vc4_crtc`: mapped registers, the platform device, static PixelValve data, last vblank timestamp, legacy gamma LUT arrays, a pending page-flip event pointer, current HVS display-list offset/channel, `feeds_txp`, and `irq_lock`. Atomic per-commit state lives in `struct vc4_crtc_state`: HVS display-list MM allocation, assigned channel, TV margins, HVS load estimate, TXP arming, and transition flags. Hardware state persists in PixelValve registers, HVS display-list/channel state, and encoder clock select fields.

The file also updates global encoder state through `encoder->possible_crtcs` and `vc4_encoder->clock_select` in `vc4_set_crtc_possible_masks()`. It tracks firmware-initialized scanout only long enough to disable it at boot. Debugfs state is non-persistent metadata pointing at live registers.

## Dependencies And Integration Points
This code depends on DRM atomic helpers, vblank helpers, fb DMA helpers, component framework, runtime PM, platform IRQ/resource APIs, and the VC4 HVS/plane/encoder helpers declared in `vc4_drv.h`. It integrates tightly with `vc4_hvs.c` for channel assignment and display-list programming, `vc4_plane.c` for primary planes and async framebuffer address updates, encoder drivers through `struct vc4_encoder` callbacks, HDMI-specific boot disable handling, and `vc4_debugfs.c` for regset publication.

Generation-specific behavior is pervasive: GEN_4 has manual async BO usecount cleanup and color-management support; GEN_5+ uses `PV_MUX_CFG`; GEN_6_C uses `SCALER6_*`, `PV_PIPE_INIT_CTRL`, and different HVS enable/status registers; PixelValve 4 has a hard-coded FIFO level quirk.

## Risks And Edge Cases
- Scanout-position reporting is an approximation based on HVS status plus FIFO size; vblank readings intentionally synthesize positions when the PixelValve is not consuming FIFO lines.
- FIFO full-level constants include hardware quirks for GEN_4 and PixelValve 4; regressions can manifest as underruns, stalls, or page-flip timeouts.
- `vc4_crtc_disable()` contains a timing-sensitive `mdelay(20)` workaround for BCM2711 HDMI stuck-pixel behavior; shortening or reordering it risks visible one-pixel shifts on mode changes.
- Async flips manually balance framebuffer, fence, vblank, and BO usecount references. Error paths and fence-callback paths are sensitive to leaks, double puts, and event ownership mistakes.
- Boot-time disable assumes a small set of compatible strings and `PV_CONTROL_CLK_SELECT == 0`; unexpected firmware muxing is warned and skipped.
- The CRTC supports only one encoder at a time and warns when DRM state carries multiple encoders.
- Register access is wrapped with `drm_dev_enter()` in many but not all helper contexts; callers must ensure hot-unplug and power sequencing are valid.

## Test Signals
- KUnit tests can exercise CRTC initialization and state helpers without hardware; register macros intentionally fail current tests if they accidentally touch MMIO.
- Runtime validation should include boot with firmware display active, mode enable/disable loops, BCM2711 HDMI repeated mode changes, async page flips with busy BO fences, interlaced VEC/HDMI modes, DSI modes, and vblank timestamp sanity.
- Debugfs register dumps (`crtc*_regs`) provide hardware-state signals after mode enable/disable and underrun/page-flip failures.
- DRM atomic test coverage should look at margin changes forcing plane display-list regeneration, duplicate/reset/destroy state behavior, and HVS channel/MM node lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_debugfs.c

## Purpose
`vc4_debugfs.c` centralizes VC4 debugfs setup for DRM minors and provides a small helper for exposing 32-bit hardware register sets. It does not own hardware policy; instead it connects HVS, BO, V3D, CRTC, DPI, DSI, and other module-provided `debugfs_regset32` definitions to DRM debugfs entries.

## Important APIs, Types, And Functions
- `vc4_debugfs_init()` is the DRM driver's `debugfs_init` callback. It always attempts HVS debugfs setup and conditionally adds BO/V3D debugfs when `vc4->v3d` exists.
- `vc4_debugfs_regset32()` is the seq-file show callback used for register dumps. It retrieves the `struct debugfs_regset32` from `entry->file.data`, enters the DRM device with `drm_dev_enter()`, and prints registers with `drm_print_regset32()`.
- `vc4_debugfs_add_regset32()` wraps `drm_debugfs_add_file()` so component drivers can register named register-dump files with the common show implementation.

## Control Flow
At `drm_dev_register()` time, DRM calls `vc4_debugfs_init()` for each minor. That function invokes module-specific debugfs initializers and uses `drm_WARN_ON()` to surface failures without aborting driver registration. Later, individual component late-register hooks such as CRTC, DPI, and DSI call `vc4_debugfs_add_regset32()` with their regset metadata. When users read a debugfs file, `vc4_debugfs_regset32()` prints live registers if the DRM device is still present.

## State And Persistence Behavior
This file stores no long-lived private state. Persistent debugfs entries are owned by DRM core, while the register-set metadata is owned by the component structures that pass it in. Reads are live hardware snapshots and are guarded by `drm_dev_enter()` so unplugged devices return `-ENODEV`.

## Dependencies And Integration Points
The file depends on DRM debugfs infrastructure, DRM printers, seq_file, Linux debugfs, platform-device-visible component regsets, and `vc4_drv.h` declarations. It integrates with HVS, BO cache, V3D, CRTC, DPI, and DSI modules by providing the shared register-dump plumbing.

## Risks And Edge Cases
- Debugfs reads touch MMIO through `drm_print_regset32()`; invalid regset lifetime or missing `drm_dev_enter()` would be hazardous, but this helper guards device lifetime.
- `vc4_debugfs_init()` only adds BO/V3D debugfs when `vc4->v3d` is present, so display-only VC5/VC6 devices intentionally lack those entries.
- Failures are warnings, not probe failures. Debugfs absence should not be treated as functional driver failure.

## Test Signals
- Build with and without `CONFIG_DEBUG_FS` to confirm the helper declaration and call sites compile.
- On hardware, verify expected files such as HVS, V3D, BO, CRTC, DSI, and DPI reg dumps appear only for present blocks.
- Unplug/removal or simulated `drm_dev_enter()` failure should make register reads fail cleanly rather than dereferencing removed hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_dpi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_dpi.c

## Purpose
`vc4_dpi.c` implements the VC4 DPI encoder component. It drives the MIPI DPI type 4 / Nokia ViSSI-style parallel display output block, maps DPI registers, validates the hardware ID, configures bus format and sync polarity, controls pixel/core clocks, attaches the next bridge or panel, and publishes DPI registers through debugfs.

## Important APIs, Types, And Functions
- `struct vc4_dpi` holds the embedded `vc4_encoder`, platform device, mapped registers, pixel/core clocks, and debugfs regset.
- `DPI_READ()` and `DPI_WRITE()` access MMIO and fail KUnit tests if used in unit-test context.
- `vc4_dpi_encoder_enable()` constructs the `DPI_C` control word from connector media bus formats, bus flags, and mode sync flags, writes the register, sets the pixel clock rate to the mode clock, and enables the pixel clock.
- `vc4_dpi_encoder_disable()` disables the pixel clock.
- `vc4_dpi_encoder_mode_valid()` rejects interlaced modes.
- `vc4_dpi_init_bridge()` resolves and attaches a downstream bridge or panel from device tree.
- `vc4_dpi_bind()` allocates and initializes the encoder component, validates `DPI_ID`, acquires clocks, enables the core clock, registers cleanup, initializes the DRM encoder/helper callbacks, attaches the downstream bridge, and stores driver data.
- `vc4_dpi_late_register()` registers the `dpi_regs` debugfs dump.

## Control Flow
The platform driver adds a component in `vc4_dpi_dev_probe()`. During master bind, `vc4_dpi_bind()` maps the DPI registers, validates the hardware ID value `0x00647069`, obtains `core` and `pixel` clocks, enables the core clock for register access, initializes a `DRM_MODE_ENCODER_DPI` encoder, installs helper callbacks, and attaches the next bridge if present in device tree. During a modeset, DRM calls the helper enable path after the CRTC is configured. The enable function discovers the connector currently using this encoder to infer the bus format, writes DPI output format/order/polarity bits, programs the pixel clock, and turns the clock on. Disable only turns off the pixel clock; core clock lifetime is tied to the component bind and devm action.

## State And Persistence Behavior
Long-lived state is limited to `struct vc4_dpi`: mapped registers and clock handles. Runtime hardware state is the `DPI_C` register and clock enable/rate state. The driver does not keep a cached copy of the selected bus format; it re-derives the value on each enable from connector display info.

## Dependencies And Integration Points
The file depends on DRM bridge/panel/of helpers, DRM encoder helpers, connector display-info bus formats and flags, Linux clock framework, component framework, and `vc4_drv.h` shared encoder/debugfs helpers. It integrates with the PixelValve CRTC through `VC4_ENCODER_TYPE_DPI`, allowing `vc4_crtc.c` to set `possible_crtcs` and `clock_select` for compatible PixelValves.

## Risks And Edge Cases
- The bus format is inferred from the connector rather than negotiated through the full bridge chain. Complex bridge chains with non-uniform bus formats can be misconfigured.
- Unknown media bus formats only log an error and keep the current default/partial configuration.
- If no connector or bus format is available, the driver defaults to 18-bit RGB666 output.
- Core clock is enabled for the component lifetime; suspend/runtime PM assumptions differ from encoders that gate all clocks per enable.
- Interlaced modes are rejected; any downstream panel requiring interlace is unsupported.

## Test Signals
- Device-tree probe should verify correct bridge attachment behavior for both connected and absent downstream endpoints.
- Mode tests should cover RGB888, BGR888, RGB/BGR666, RGB565, padded formats, negative-edge pixel data, data-enable polarity, composite sync, and missing sync polarity.
- Runtime hardware checks should confirm `DPI_ID`, `DPI_C`, and pixel-clock rate via debugfs and clock summaries after enable.
- KUnit or mocked tests should avoid direct register macros unless intentionally validating MMIO-guard behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_dpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_drv.c

## Purpose
`vc4_drv.c` is the top-level Broadcom VC4/VC5/VC6 DRM platform driver. It defines DRM driver objects and ioctls, handles component master binding, configures DMA masks and firmware handoff, initializes GEM for GEN_4, binds display/GPU subcomponents, loads KMS, registers the DRM device, and registers/unregisters all VC4 component platform drivers at module load/unload.

## Important APIs, Types, And Functions
- `vc4_ioremap_regs()` is a shared helper around `devm_platform_ioremap_resource()`.
- `vc4_dumb_fixup_args()` enforces minimum pitch and size for dumb buffers; `vc5_dumb_create()` applies it before DMA dumb allocation.
- `vc4_get_param_ioctl()` exposes V3D hardware IDs and feature booleans for GEN_4 userspace.
- `vc4_open()` and `vc4_close()` allocate/free `struct vc4_file`, initialize/close perfmon state, and release any per-file binner BO use.
- `vc4_drm_ioctls[]` maps VC4 render ioctls including submit, waits, BO creation/mapping/tiling/labels, hang state, madvise, and perfmon APIs.
- `vc4_drm_driver` includes modeset, atomic, GEM, render, and syncobj features with VC4 ioctl support. `vc5_drm_driver` is display/GEM-only and omits render ioctls.
- `vc4_match_add_drivers()` builds a component match list by discovering devices bound to each VC4 component platform driver.
- `vc4_drm_bind()` performs the primary bind sequence for the DRM device.
- `vc4_drm_unbind()` unplug/shutdowns the DRM device on component unbind.
- `vc4_drm_register()` and `vc4_drm_unregister()` register the subcomponent drivers and platform master driver.

## Control Flow
At module init, `vc4_drm_register()` refuses to load when firmware-only DRM drivers are requested, registers all component drivers, then registers the `vc4-drm` platform driver. Its probe builds a component match over HVS, HDMI, VEC, DPI, DSI, TXP, CRTC, and V3D devices and adds a component master.

When the component master binds, `vc4_drm_bind()` selects `vc4_drm_driver` for GEN_4 and `vc5_drm_driver` for newer generations. It sets a 32-bit or 36-bit coherent DMA mask, applies DMA-range configuration from matching HVS/V3D nodes, allocates `struct vc4_dev`, initializes BO cache and GEM only for GEN_4, initializes DRM mode config, obtains Raspberry Pi firmware if present, removes conflicting framebuffer devices, asks firmware to stop its display driver, binds all components, registers automatic unbind cleanup, creates additional planes, loads KMS, disables firmware-left PixelValves, registers the DRM device, and sets up the fbdev/client output with RGB565.

Unbind calls `drm_dev_unplug()`, `drm_atomic_helper_shutdown()`, and clears driver data. Platform shutdown also calls atomic shutdown to quiesce scanout.

## State And Persistence Behavior
The master allocates `struct vc4_dev` as the DRM device private object and sets `vc4->gen` and `vc4->dev`. For GEN_4 it initializes BO cache, GEM job state, purgeable BO state, power locks, and per-file perfmon context via open/close. Component binding populates shared pointers such as `vc4->hvs` and `vc4->v3d` in other files. Driver registration persists until module unload; DRM device registration persists until unbind/remove.

Firmware handoff is one-shot per bind: conflicting aperture devices are removed and `RPI_FIRMWARE_NOTIFY_DISPLAY_DONE` is sent when firmware support is available. DMA mask and DMA-range configuration are process-wide device settings.

## Dependencies And Integration Points
This file depends on Linux platform/component frameworks, OF matching, DMA configuration, aperture conflict removal, runtime PM, Raspberry Pi firmware API, DRM core/atomic/fbdev/GEM helpers, and all VC4 subdrivers. It is the central integration point for `vc4_hvs_driver`, `vc4_hdmi_driver`, `vc4_vec_driver`, `vc4_dpi_driver`, `vc4_dsi_driver`, `vc4_txp_driver`, `vc4_crtc_driver`, and `vc4_v3d_driver`.

The component driver order is intentional: HVS before HDMI and TXP/CRTC so HDMI can inspect HVS limits and TXP possible-CRTC masks are correct. GEN_4 userspace ABI is exposed through `uapi/drm/vc4_drm.h`; newer generations share display infrastructure but not VC4 render ioctl support.

## Risks And Edge Cases
- Component discovery depends on platform devices already associated with the registered component drivers; missing OF nodes or deferred probes can delay master bind.
- GEN gating is critical: invoking GEN_4 render ioctls or GEM scheduler on VC5/VC6 returns `-ENODEV`.
- Firmware handoff failures are only warnings for display-done notification, but aperture removal failure aborts bind.
- DMA mask differences matter for BCM2712/GEN_6_C 36-bit addressing.
- Open/close paths assume `struct vc4_file` only for GEN_4 render-capable devices.
- Driver unregister order unregisters component drivers before the platform master driver in `vc4_drm_unregister()`, matching current code but worth watching for teardown ordering interactions.

## Test Signals
- Probe tests should cover GEN_4, GEN_5, and GEN_6_C compatible strings, with and without firmware node, and with absent V3D.
- Userspace ABI tests should verify `GET_PARAM`, `SUBMIT_CL`, wait, BO, madvise, and perfmon ioctls on GEN_4, and absence/failure on VC5/VC6.
- KMS boot tests should confirm firmware framebuffer removal, firmware display handoff, CRTC boot disable, plane creation, and client setup.
- Component-order regressions show up as missing encoders/CRTC masks, HDMI mode-limit misdetection, or failed component bind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_drv.h

## Purpose
`vc4_drv.h` is the shared internal contract for the VC4 DRM driver. It defines device, BO, fence, V3D, HVS, plane, encoder, CRTC, execution, shader-validation, perfmon, and platform data structures; generation constants; register access helpers; wait helpers; and cross-file function prototypes for the VC4 display and render subsystems.

## Important APIs, Types, And Functions
- `enum vc4_gen` differentiates GEN_4, GEN_5, GEN_6_C, and GEN_6_D behavior.
- `struct vc4_dev` embeds `struct drm_device` and carries global state: generation, component pointers, BO cache/labels, purgeable pool, dma-fence context, GEM job lists/seqnos/locks/waitqueue, perfmon state, binner BO allocation, underrun counter, power lock/refcount, hangcheck timer/work, and KMS private objects.
- `struct vc4_bo` extends `drm_gem_dma_object` with tiling, cache/list hooks, shader validation info, labels, active usecount, madvise state, and a madv lock.
- `struct vc4_fence` embeds `dma_fence` and stores the DRM device and VC4 seqno used by fence signaling.
- `struct vc4_hvs`, `struct vc4_hvs_state`, and `struct vc4_plane_state` model HVS registers, display-list/LBM/UPM allocators, FIFO state, plane display-list state, scaling, bandwidth/load, and prefetching.
- `enum vc4_encoder_type`, `struct vc4_encoder`, `struct vc4_crtc_data`, `struct vc4_pv_data`, `struct vc4_crtc`, and `struct vc4_crtc_state` define display topology, encoder hooks, PixelValve capabilities, CRTC event/vblank/display-list state, and atomic channel/margin/load state.
- MMIO macros `V3D_READ/WRITE`, `HVS_READ/WRITE`, `HVS_READ6/WRITE6`, and `VC4_REG32` standardize hardware access and KUnit guard behavior.
- `struct vc4_exec_info` captures one userspace GPU submission: BO array, dma fence, seqno, command-list addresses, shader/uniform pointers, validator flags, tile/binning metadata, unref list, render write BOs, perfmon, and binner BO reference state.
- Inline helpers `vc4_first_bin_job()`, `vc4_first_render_job()`, and `vc4_last_render_job()` are list accessors used by GEM scheduling and hangcheck.
- `__wait_for`, `_wait_for`, and `wait_for` provide a sleep-and-retry timeout pattern that rechecks the condition after timeout.
- The prototype section publishes APIs across BO, CRTC, debugfs, driver, DPI, DSI, fence, GEM, HDMI, VEC, TXP, IRQ, HVS, KMS, plane, V3D, validation, shader validation, and perfmon modules.

## Control Flow
This header does not execute control flow directly, but it shapes the call graph. The top-level driver allocates `struct vc4_dev`; component drivers populate its HVS/V3D/display members; CRTC/encoder/HVS/plane code uses the display structs and callbacks during atomic commits; GEM ioctls allocate and queue `struct vc4_exec_info`; IRQ and workqueue handlers update seqnos and job lists; BO and madvise code track active use and purgeability; perfmon APIs attach counters to job submissions.

The macros also shape hardware access: callers must have an in-scope `vc4` or `hvs` variable for V3D/HVS macros, and KUnit tests are protected from accidental live register IO.

## State And Persistence Behavior
Nearly all persistent driver state is declared here. `vc4_dev` persists for the DRM device lifetime. BO objects persist across GEM handles and dma-buf sharing. `vc4_exec_info` persists from submit ioctl until job completion cleanup. `vc4_crtc_state`, `vc4_hvs_state`, and `vc4_plane_state` are tied to atomic state lifetimes. Perfmon objects are refcounted per userspace-managed object lifetime. Purgeable BO state transitions are stored in each BO and global purgeable lists.

## Dependencies And Integration Points
The header depends on Linux debugfs, delay, OF, refcount, uaccess, KUnit test-bug hooks, and DRM atomic/device/encoder/fourcc/GEM DMA/managed/MM/modeset APIs. It integrates all VC4 source files by exposing platform driver symbols, internal helper APIs, and shared data contracts. It also includes the public VC4 UAPI definitions that define ioctl payloads.

## Risks And Edge Cases
- Changes to shared structs can affect many files and the exact locking/lifetime assumptions around job lists, BO usecounts, HVS MM nodes, and CRTC IRQ state.
- `enum vc4_kernel_bo_type` warns that `vc4_bo.c` label names must be kept in sync.
- Register macros assume local variable names (`vc4`, `hvs`) and will fail to compile or access the wrong context if copied carelessly.
- `wait_for` sleeps and calls `might_sleep()`, so it is not valid in atomic contexts.
- `struct vc4_exec_info` has many validator-populated fields; incomplete initialization can become a security issue because userspace command lists are being validated and relocated.
- The header contains ABI-facing relationships but should not expose unstable internal changes to userspace beyond the included UAPI.

## Test Signals
- Build coverage is the first signal: almost every VC4 file includes this header, so type/prototype mismatches surface broadly.
- KUnit tests should verify that helper constructors can inject CRTC callbacks and that MMIO macros catch accidental hardware access.
- Lockdep and KASAN are useful for shared lifetime changes around job lists, BO purgeability, CRTC state destruction, and HVS MM allocations.
- ABI tests should focus on ioctl structs included through `uapi/drm/vc4_drm.h`, while internal-structure changes need render submission, KMS atomic, hot-unplug, suspend/resume, and debugfs smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_dsi.c

## Purpose
`vc4_dsi.c` implements the VC4 DSI0/DSI1 encoder, DRM bridge, and MIPI DSI host. It supports DSI video-mode panel/bridge output, MIPI DSI command transfers, D-PHY timing/ULPS management, clock exposure for PHY-derived clocks, a DMA register-write workaround for broken BCM2835 DSI1 AXI writes, interrupt-driven transfer completion, and debugfs register dumps.

## Important APIs, Types, And Functions
- `struct vc4_dsi_variant` describes port number, broken AXI workaround requirement, debugfs name, and register table.
- `struct vc4_dsi` embeds `vc4_encoder`, `mipi_dsi_host`, and `drm_bridge`, and stores mapped registers, downstream bridge, DMA workaround resources, variant, MIPI lane/channel/format/divider/mode flags, escape/PHY/pixel clocks, PHY fixed-factor clocks, transfer completion state, and debugfs regset.
- `dsi_dma_workaround_write()` writes registers normally or via DMA memcpy when `reg_dma_chan` is present, because BCM2835 DSI1 cannot accept ARM AXI writes.
- `DSI_PORT_READ/WRITE/BIT` abstract DSI0/DSI1 register and bit differences.
- `vc4_dsi_ulps()` and `vc4_dsi_latch_ulps()` enter/exit Ultra Low Power State and wait for ULPS/STOP status.
- `dsi_hs_timing()` and `dsi_esc_timing()` convert D-PHY timing requirements to hardware register units.
- Bridge callbacks `vc4_dsi_bridge_mode_fixup()`, `pre_enable()`, `enable()`, `disable()`, `post_disable()`, and `attach()` configure adjusted mode timing, clocks, PHY registers, DISP0/DISP1, and downstream bridge chaining.
- `vc4_dsi_host_transfer()` builds MIPI DSI packets, splits long payloads across command and pixel FIFOs, enables completion/error interrupts, waits up to one second, handles RX packets, and resets FIFOs on failure.
- Host callbacks `vc4_dsi_host_attach()` and `detach()` record panel parameters, enforce video mode, add/remove the bridge, and add/remove the component.
- IRQ handlers `vc4_dsi_irq_defer_to_thread_handler()` and `vc4_dsi_irq_handler()` handle error bits and transfer completion, with a threaded path for DMA-write variants.
- `vc4_dsi_init_phy_clocks()` registers fixed-factor byte/ddr2/ddr clocks derived from the DSI PHY clock for CPRMAN consumers.
- `vc4_dsi_bind()` performs full DRM component bind for a host-attached DSI device.

## Control Flow
Platform probe allocates the bridge/host object with `devm_drm_bridge_alloc()`, initializes bridge metadata and host ops, stores driver data, and registers the MIPI DSI host. When a panel/bridge attaches, `vc4_dsi_host_attach()` copies lane/channel/format/mode settings, computes the PixelValve divider, rejects non-video mode, adds the DRM bridge, and adds this platform device as a VC4 component. The component master later calls `vc4_dsi_bind()`, which gets the variant, maps registers, validates the DSI ID, sets up DMA-write resources for broken DSI1 if needed, initializes transfer completion, requests IRQ, acquires clocks, finds the downstream bridge, sets the escape clock to 100 MHz, exposes PHY clocks, initializes the DRM encoder, enables runtime PM, and attaches the internal DSI bridge to the encoder.

During atomic enable, bridge `pre_enable()` resumes runtime PM, reads the adjusted CRTC mode, sets PHY PLL rate, resets DSI and FIFOs, configures analog PHY power/reset/current settings, enables escape/PHY/pixel clocks, calculates HS and escape timing registers, enables lanes and clock lane, configures timeouts and display FIFOs, ungates the block, releases AFE reset, exits ULPS, and sets DISP0 for video or command mode. `enable()` then sets `DSI_DISP0_ENABLE`. Disable clears that bit, while post-disable turns off clocks and drops runtime PM.

MIPI command transfer is asynchronous at the hardware level but synchronous to the caller: `vc4_dsi_host_transfer()` prepares packet registers/FIFOs, enables completion interrupts, writes the packet header/control to launch, waits for `xfer_completion`, restores always-enabled error interrupts, optionally reads response data, and resets command state/FIFOs on error.

## State And Persistence Behavior
Persistent object state includes variant, lane count, channel, format, divider, mode flags, clocks, DMA resources, downstream bridge pointer, and transfer completion fields. Runtime PM controls module power during bridge enable. Hardware state persists in DSI control, PHY, timing, timeout, interrupt, DISP0/DISP1, and FIFO registers. `xfer_result` and `xfer_completion` are per-transfer synchronization state updated by IRQ context.

The host is registered at platform probe and unregistered at remove. The component is only added after a MIPI device attaches, which means DSI without an attached panel/bridge does not participate in VC4 master binding.

## Dependencies And Integration Points
This file depends on Linux component, DMA engine/mapping, completion, clock, OF address, platform, runtime PM, and DRM bridge/panel/MIPI DSI/OF helpers. It integrates with the VC4 CRTC through `VC4_ENCODER_TYPE_DSI0/DSI1` and PixelValve clock select, with downstream panels/bridges through DRM bridge chaining and MIPI host ops, with CPRMAN through exposed PHY fixed-factor clocks, and with debugfs through shared regset helpers.

## Risks And Edge Cases
- The code comments state DSI1 video mode is the tested path; DSI0 and non-video command-mode panel operation are either limited or rejected.
- `vc4_dsi_host_attach()` returns `0` for unknown format and non-video mode after logging errors, which may leave attach semantics surprising even though it avoids adding the component in the non-video case.
- Long packet handling assumes pixel FIFO capacity; it warns if `pix_fifo_len >= DSI_PIX_FIFO_DEPTH` but does not otherwise reject before writing.
- RX long packet reads use `DSI1_RXPKT_FIFO`, which is relevant to port differences and should be scrutinized for DSI0 behavior.
- DMA register writes can sleep; DSI1 uses `IRQF_ONESHOT` and a threaded handler so writes to clear interrupts are not done in hard IRQ context.
- Clock enable error paths in `pre_enable()` return early after some resources may already be enabled; bridge/core teardown behavior must be validated.
- ULPS entry/exit relies on status bits and timeouts; failures log warnings and attempt partial recovery.

## Test Signals
- Hardware tests should cover DSI1 video-mode panel boot, mode changes, suspend/resume, runtime PM enable/disable, ULPS transitions, and MIPI command transfers with and without RX.
- BCM2835 DSI1 needs explicit testing of DMA register-write setup, IRQ thread clearing, and transfer completion.
- DSI0 tests should focus on ID validation, register offset abstraction, lane limits, and RX behavior.
- Clock tests should verify escape clock rate, PHY PLL rate, derived byte/ddr clocks, and PixelValve divider-adjusted mode timing.
- Debugfs `dsi*_regs`, interrupt error logs, and transfer timeout/reset messages are key observability signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_fence.c

## Purpose
`vc4_fence.c` provides the `dma_fence_ops` implementation used by VC4 GEN_4 GEM job submissions. The fence represents completion of a VC4 V3D job sequence number and allows dma-reservation objects and DRM syncobjs to observe GPU work completion.

## Important APIs, Types, And Functions
- `vc4_fence_get_driver_name()` returns `"vc4"`.
- `vc4_fence_get_timeline_name()` returns `"vc4-v3d"`.
- `vc4_fence_signaled()` converts the generic `dma_fence` to `struct vc4_fence`, retrieves `struct vc4_dev`, and reports signaled when `vc4->finished_seqno >= f->seqno`.
- `vc4_fence_ops` publishes these callbacks to `dma_fence_init()` in `vc4_gem.c`.

## Control Flow
Fences are allocated and initialized in `vc4_queue_submit()` when a job is assigned a seqno. The fence is attached to dma-reservation objects and optionally installed into an output syncobj. Completion is normally signaled explicitly by GEM/IRQ job completion code, while the `signaled` callback provides state-based verification using `finished_seqno`.

## State And Persistence Behavior
This file defines no independent persistent state. Each `struct vc4_fence` stores a DRM device pointer and seqno. The global completion state is `vc4->finished_seqno`, protected/updated by the GEM/IRQ path outside this file. The fence lifetime is managed by dma-fence refcounting and the job cleanup path.

## Dependencies And Integration Points
It depends on `vc4_drv.h` for `struct vc4_fence`, `to_vc4_fence()`, and `to_vc4_dev()`, plus the kernel dma-fence API included through that header. It integrates with `vc4_gem.c` for fence allocation, reservation attachment, syncobj replacement, wait semantics, and job cleanup.

## Risks And Edge Cases
- Correctness depends on monotonic `finished_seqno` updates and proper locking in the GEM/IRQ code.
- If a job is force-completed during reset, GEM must signal and drop the fence; this file only answers the signaled query.
- `get_driver_name` and timeline name are used for debugging and fence introspection; changing them can affect userspace diagnostics.

## Test Signals
- Submit jobs with output syncobjs and wait through dma-fence/syncobj paths.
- Force GPU reset/hang handling and verify fences are signaled to avoid permanent waits.
- Inspect fence debug output to confirm `"vc4"` and `"vc4-v3d"` names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_gem.c

## Purpose
`vc4_gem.c` implements GEN_4 VC4 GEM render submission, job scheduling, dma-fence/syncobj integration, BO reservation/usecount handling, hang detection and recovery, hang-state capture, wait ioctls, and GEM madvise/purgeable state transitions. It is the central V3D userspace execution path for the VC4 render UAPI.

## Important APIs, Types, And Functions
- `vc4_queue_hangcheck()`, `vc4_hangcheck_elapsed()`, `vc4_reset_work()`, and `vc4_reset()` implement progress monitoring and reset scheduling.
- `struct vc4_hang_state`, `vc4_save_hang_state()`, `vc4_free_hang_state()`, and `vc4_get_hang_state_ioctl()` capture active job BOs and V3D registers for root-only hang diagnostics.
- `submit_cl()` writes V3D control-list current/end addresses and starts execution by writing the end register.
- `vc4_wait_for_seqno()`, `vc4_wait_seqno_ioctl()`, and `vc4_wait_bo_ioctl()` implement job seqno waits and BO reservation waits with timeout adjustment on interruption.
- `vc4_flush_caches()` and `vc4_flush_texture_caches()` clear V3D L2/slice caches before bin/render phases.
- `vc4_submit_next_bin_job()`, `vc4_move_job_to_render()`, and `vc4_submit_next_render_job()` schedule the hardware's binning thread 0 and render thread 1 queues.
- `vc4_attach_fences()` adds the job fence to read BO reservations and write BO reservations.
- `vc4_lock_bo_reservations()` uses `drm_exec` to lock BO reservations before fence attachment.
- `vc4_queue_submit()` assigns seqnos, initializes `struct vc4_fence`, installs output syncobjs, attaches fences, queues the job, and kicks the hardware if allowed by current render/perfmon state.
- `vc4_cl_lookup_bos()` looks up userspace BO handles, stores the object array, and increments VC4 BO usecounts.
- `vc4_get_bcl()` copies userspace bin CL, shader records, and uniforms; allocates the validated BCL BO; validates bin CL and shader records; and acquires binner memory if needed.
- `vc4_complete_exec()` releases fences, BO references/usecounts, temporary unref-list BOs, bin slots, binner BO, perfmon, V3D runtime PM, and the exec struct.
- `vc4_job_handle_completed()` and `vc4_job_done_work()` drain completed jobs from `job_done_list`.
- `vc4_submit_cl_ioctl()` is the main userspace submit path, validating flags/padding, acquiring PM, resolving BOs/perfmon/input sync, validating command lists, locking reservations, and queueing the job.
- `vc4_gem_init()` initializes job lists, locks, work/timer state, power/purgeable locks, fence context, and destruction action.
- `vc4_gem_madvise_ioctl()` implements `VC4_MADV_DONTNEED/WILLNEED` transitions and purgeability reporting.

## Control Flow
A userspace render submit enters `vc4_submit_cl_ioctl()`. The ioctl rejects non-GEN_4 devices, missing V3D, unknown flags, and invalid padding, then allocates `struct vc4_exec_info`, gets V3D runtime PM, initializes the unref list, looks up BO handles and increments BO usecounts, attaches a perfmon if requested, waits for an input syncobj fence unless it is from the same VC4 fence context, validates/copies the bin CL if present, builds the render CL through `vc4_get_rcl()`, locks all BO reservations, resolves the output syncobj, clears the stack-owned args pointer, and calls `vc4_queue_submit()`.

Queue submission runs under `job_lock`: it increments `emit_seqno`, initializes a dma fence with `vc4_fence_ops`, optionally replaces the output syncobj fence, attaches the fence to BO reservations, finalizes the `drm_exec` context, adds the job to `bin_job_list`, and starts binning immediately if the hardware queue is idle and perfmon compatibility allows it. Binning completion, render movement, render completion, and `finished_seqno` updates are driven by the IRQ code in other files; this file provides the queue operations and completion cleanup.

The hangcheck timer samples V3D current-address registers for the first bin/render jobs. If either address progresses, it rearms. If neither progresses for the interval, it schedules reset work, which captures hang state and power-cycles V3D through runtime PM before resetting IRQ/job state.

Madvise control looks up a BO, rejects unsupported/imported objects, locks the BO madv state, moves idle BOs into or out of the purgeable pool when transitioning between `WILLNEED` and `DONTNEED`, reports whether the BO was retained, and avoids resurrecting already purged objects.

## State And Persistence Behavior
Global GEM state is stored in `struct vc4_dev`: `emit_seqno`, `finished_seqno`, dma-fence context, bin/render/done job lists, `job_lock`, `job_wait_queue`, `job_done_work`, active perfmon, binner BO allocation bits, power lock/refcount, hangcheck timer/work, and purgeable pool. Each job persists as `struct vc4_exec_info` from ioctl allocation until completion cleanup. It owns references to BOs, temporary command-list BOs on `unref_list`, a fence, optional perfmon, binner BO slot/ref state, and validated command-list addresses.

Hang state persists in `vc4->hang_state` until the root-only ioctl consumes it or a newer state is discarded because one already exists. BO purgeability persists in each `struct vc4_bo` under `madv_lock` and in the global purgeable list/statistics.

## Dependencies And Integration Points
This file depends on Linux timers/workqueues, runtime PM, dma-fence arrays, signals, DRM exec/reservation/syncobj helpers, VC4 UAPI structs, V3D register definitions, validation helpers, BO helpers, V3D PM/bin BO helpers, IRQ reset, perfmon, and tracepoints. It integrates with:
- `vc4_fence.c` for dma-fence ops.
- `vc4_irq.c` for job completion, seqno advancement, IRQ reset, and queue progression.
- `vc4_validate.c` and `vc4_validate_shader.c` for command-list and shader safety.
- `vc4_bo.c` for BO allocation, usecounts, purgeable pool, labels, mmap, and tiling.
- `vc4_v3d.c` for runtime PM and binner BO resources.
- DRM syncobj/dma-reservation for explicit synchronization and implicit BO fences.

## Risks And Edge Cases
- Command submission is security-sensitive: userspace command lists, shader records, uniforms, and BO handles must be validated before hardware execution.
- Error paths in `vc4_submit_cl_ioctl()` must only call `drm_exec_fini()` after reservation locking succeeded; `vc4_complete_exec()` depends on partially initialized fields being either valid or NULL.
- BO usecount increments in `vc4_cl_lookup_bos()` have a custom rollback path because `vc4_complete_exec()` cannot know how many increments succeeded.
- Perfmon compatibility can block starting a new bin job while a render job with a different perfmon is active.
- Hang-state capture intentionally cannot guarantee BO contents remain stable after capture; it only keeps objects from being purged long enough to dump.
- Reset is scheduled from timer context because runtime PM reset can sleep.
- Fences are attached before hardware submission; if immediate completion races the ioctl, output syncobj replacement must already be visible.
- Madvise state has races with BO reuse/purge decisions controlled by `madv_lock`, usecounts, and purgeable list locks.

## Test Signals
- UAPI tests should cover submit with and without bin CL, invalid flags/padding, invalid BO handles, input syncobj waits, same-context syncobj skip, output syncobj signaling, wait seqno timeout/interruption, wait BO timeout adjustment, and madvise transitions.
- Fault-injection tests should cover allocation/copy_from_user/validation failures and ensure BO refs, usecounts, fences, PM refs, perfmon refs, and reservation locks are released.
- Hang tests should submit a stuck job, verify hangcheck reset, root hang-state retrieval, fence signaling, and subsequent queue recovery.
- Performance-counter tests should submit jobs with same/different perfmons and verify scheduling ordering and counter capture.
- Lockdep/KASAN/KCSAN are valuable around `job_lock`, `power_lock`, `madv_lock`, reservation locking, and job completion work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_gem.c -->
