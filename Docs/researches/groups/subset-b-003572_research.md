# subset-b-003572 research

Grouped research for the Exynos DRM files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos`. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_crtc.c

Purpose: this file adapts Exynos display-controller implementations to the DRM CRTC core. It owns `struct exynos_drm_crtc` allocation, helper callbacks, vblank event handling, possible-CRTC assignment for encoders, and the Tearing Effect callback dispatch used by command-mode panels.

Important APIs and functions: `exynos_drm_crtc_create()` allocates the Exynos wrapper, stores the output type, callback table, and implementation context, then calls `drm_crtc_init_with_planes()` and attaches `exynos_crtc_helper_funcs`. `exynos_drm_crtc_get_by_type()` scans `drm_for_each_crtc()` and returns the CRTC whose `type` matches an `enum exynos_drm_output_type`. `exynos_drm_set_possible_crtcs()` converts that result to an encoder `possible_crtcs` bitmask. `exynos_crtc_handle_event()` arms pending page-flip events on the next vblank. `exynos_drm_crtc_te_handler()` forwards panel TE signals to the hardware-specific callback.

Control flow: DRM atomic helpers enter this file through helper callbacks. Atomic enable calls the hardware `ops->atomic_enable()` first, then enables vblank accounting with `drm_crtc_vblank_on()`. Atomic disable reverses this order: vblank accounting is turned off, hardware is disabled, and a pending event is sent immediately if the state is no longer active. Atomic check, begin, flush, mode validation, mode fixup, vblank enable, and vblank disable are all thin dispatchers into the `exynos_drm_crtc_ops` supplied by FIMD, DECON, mixer, or another CRTC provider.

State and persistence: there is no persistent storage. State lives in the heap-allocated `exynos_drm_crtc`, its `ops`, `ctx`, output `type`, optional `pipe_clk`, and CRTC atomic state. Event state is coordinated under `crtc->dev->event_lock`.

Dependencies and integration points: this file depends on DRM atomic helper, encoder, probe helper, and vblank APIs plus Exynos plane and driver structures. It is consumed by display controllers such as FIMD and by bridge/encoder glue such as DPI, DSI, and MIC when selecting LCD CRTCs or relaying TE signals.

Risks: the code assumes `ops` is valid and that hardware callbacks tolerate the CRTC state being in the DRM helper phase in which they are called. `exynos_crtc_handle_event()` warns if `drm_crtc_vblank_get()` fails, so incorrect vblank enablement can surface as event loss. `exynos_drm_crtc_get_by_type()` casts all CRTCs to Exynos CRTCs, so mixed CRTC types in the device would be unsafe.

Test signals: useful tests are atomic modesets, page flips with and without vblank, command-mode TE page flips, encoder binding for each output type, and suspend/disable cases that must deliver outstanding events exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_crtc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_crtc.h

Purpose: this header publishes the Exynos CRTC helper API used by Exynos display controllers and output bridges. It is intentionally small and delegates type definitions to `exynos_drm_drv.h`.

Important APIs and types: it declares `exynos_drm_crtc_create()`, `exynos_drm_crtc_get_by_type()`, `exynos_drm_set_possible_crtcs()`, `exynos_drm_crtc_te_handler()`, and `exynos_crtc_handle_event()`. The core type is `struct exynos_drm_crtc`, defined in `exynos_drm_drv.h`, with `enum exynos_drm_output_type` identifying LCD, HDMI, and VIDI paths.

Control flow and integration: CRTC providers call `exynos_drm_crtc_create()` after creating their primary plane. Encoder/bridge glue calls `exynos_drm_set_possible_crtcs()` or `exynos_drm_crtc_get_by_type()` during bind. TE-capable DSI paths call `exynos_drm_crtc_te_handler()` to push panel synchronization back into the CRTC implementation.

State and persistence: the header stores no state. It exposes functions that manipulate DRM mode objects and Exynos wrapper state.

Dependencies: it includes `exynos_drm_drv.h`, making this header part of the internal Exynos DRM contract rather than a standalone public UAPI.

Risks: because the header exposes CRTC lookup by output type, call sites must handle `ERR_PTR(-ENODEV)` and avoid assuming that an LCD CRTC exists before all components bind. The TE helper requires a valid `struct drm_crtc *`.

Test signals: compile coverage with and without specific output drivers, DSI/DPI/MIC bind ordering, and command-mode panel page flips are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_crtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_dma.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_dma.c

Purpose: this file centralizes Exynos DRM DMA/IOMMU setup so display and processing subdevices share a consistent address space and DMA mapping device.

Important APIs: `exynos_drm_register_dma()` chooses the first registering subdevice as `priv->dma_dev`, creates or obtains `priv->mapping` when `CONFIG_EXYNOS_IOMMU` is active, and attaches each subdevice. `exynos_drm_unregister_dma()` detaches a subdevice. `exynos_drm_cleanup_dma()` releases the global mapping and clears the DMA device. Internal helpers `drm_iommu_attach_device()` and `drm_iommu_detach_device()` abstract ARM DMA-IOMMU and generic IOMMU-DMA paths.

Control flow: subdrivers call register during component bind and unregister during unbind. The first registration establishes the DMA mapping basis. For legacy `CONFIG_ARM_DMA_USE_IOMMU`, the code saves the original per-device DMA mapping in `*dma_priv`, detaches it, and attaches the shared Exynos mapping. On detach it restores the saved mapping. For `CONFIG_IOMMU_DMA`, it uses the domain associated with `priv->dma_dev` and calls `iommu_attach_device()` / `iommu_detach_device()`.

State and persistence: persistent runtime state is stored in `struct exynos_drm_private`: `dma_dev`, `mapping`, and each caller's `dma_priv`. The device virtual address window is fixed at `0x20000000` plus `0x40000000`.

Dependencies and integration points: this code depends on Linux DMA map ops, IOMMU APIs, optional ARM DMA-IOMMU APIs, and DRM private state from `exynos_drm_drv.h`. GEM allocation, framebuffer validation, G2D, FIMC, GSC, and FIMD all depend on the resulting DMA mapping.

Risks: attachment requires compatible DMA ops between the chosen DMA device and the subdevice; mismatches fail with `-EINVAL`. If a subdriver forgets unregister or passes the wrong `dma_priv`, legacy mapping restoration can be wrong. Non-IOMMU builds still set `dma_dev`, which affects GEM allocation through `to_dma_dev()`.

Test signals: probe all enabled subdrivers, deferred probe and module unload/reload, IOMMU and non-IOMMU kernels, PRIME import/export, and multi-device IPP jobs that DMA between GEM buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_dpi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_dpi.c

Purpose: this file implements the parallel DPI/RGB output glue for Exynos DRM. It creates a simple encoder and connector for panels connected to the FIMD RGB port or using display timings embedded under the FIMD node.

Important structures and APIs: `struct exynos_dpi` contains a `drm_encoder`, `drm_connector`, optional `drm_panel`, optional `videomode`, and the panel DT node. `exynos_dpi_probe()` parses DT and returns the embedded encoder pointer. `exynos_dpi_bind()` initializes a TMDS-style simple encoder, sets possible CRTCs to `EXYNOS_DISPLAY_TYPE_LCD`, and creates a DPI connector. `exynos_dpi_remove()` disables the panel path.

Control flow: probe allocates context, calls `exynos_dpi_parse_dt()`, and resolves a remote panel through `of_drm_find_panel()` if an RGB remote node exists. Bind runs later from FIMD component bind and registers the encoder/connector. Connector detection always reports connected. `get_modes` prefers local `display-timings`; if absent, it delegates to the panel. Encoder enable prepares and enables the panel; disable disables and unprepares it.

State and persistence: state is devm-managed context plus DRM connector/encoder objects. There is no retained userspace state. Panel power state is driven by encoder enable/disable.

Dependencies and integration points: this file uses OF graph, DRM panel, simple KMS helper, atomic connector helpers, and `exynos_drm_set_possible_crtcs()`. It is attached by FIMD when `ctx->encoder` is present.

Risks: detection is unconditional, so broken panel DT or missing physical connection is not reflected through connector status. `exynos_dpi_parse_dt()` returns `NULL` from probe on `-EINVAL`, meaning "no DPI" rather than a hard error. Panel lookup can defer via `ERR_PTR`.

Test signals: DT cases with display timings only, remote panel only, missing panel, deferred panel probe, connector mode enumeration, and panel prepare/enable sequencing during modeset and shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_dpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_drv.c

Purpose: this is the top-level Exynos DRM driver. It registers platform subdrivers, creates virtual devices where needed, owns the DRM driver object, exposes Exynos GEM/G2D/IPP/VIDI IOCTLs, and coordinates component-master binding of display and processing blocks.

Important APIs and data: `exynos_drm_driver` defines DRM features (`DRIVER_MODESET`, `DRIVER_GEM`, `DRIVER_ATOMIC`, `DRIVER_RENDER`), file operations, GEM dumb creation and PRIME import hooks, fbdev support, and IOCTL table. `exynos_ioctls[]` exposes GEM create/map/get, VIDI connection, G2D get/set/exec, and IPP get resources/caps/limits/commit. `exynos_drm_drivers[]` is the ordered registry of enabled component drivers, virtual devices, and FIMC devices shared with V4L2. `exynos_drm_bind()` and `exynos_drm_unbind()` are component master callbacks.

Control flow: module init first creates virtual platform devices for virtual entries, then registers every enabled platform driver. The virtual `exynos-drm` platform driver probes, builds a `component_match` by scanning devices registered for each component driver, and installs the component master. Bind allocates a `drm_device`, allocates `struct exynos_drm_private`, initializes mode config, calls `exynos_drm_mode_config_init()`, computes encoder clone masks from pre-existing encoder list, binds all components, initializes vblank, resets mode config, starts KMS polling, registers the DRM device, and runs `drm_client_setup()`. Unbind unregisters the DRM device, stops polling, shuts down atomic state, unbinds components, cleans mode config and DMA, frees private state, and drops the DRM device.

State and persistence: per-open state is `struct drm_exynos_file_private`, allocated in `exynos_drm_open()` and initialized by `g2d_open()`. Device-wide state lives in `struct exynos_drm_private`, including `g2d_dev`, `dma_dev`, `vidi_dev`, shared mapping, and atomic commit wait/lock fields. No disk persistence exists.

Dependencies and integration points: this file integrates Linux component framework, platform driver registry, DRM core, GEM, fbdev emulation, G2D, IPP, VIDI, DMA helpers, and all Exynos display engines. Ordering matters: connector drivers are placed after CRTC drivers because they need CRTC pipe masks.

Risks: partial bind failures must unwind every subsystem in the reverse order; this file has several staged `goto` paths, so missing cleanup would leak devices or mappings. `exynos_drm_match_add()` returns `-ENODEV` when no components are found. G2D open failure unwinds file-private allocation. Clone mask setup happens before `component_bind_all()`, so only encoders already created before that loop are included; this depends on local component behavior.

Test signals: module load/unload, firmware-driver-only mode, enabled/disabled Kconfig permutations, deferred probes, virtual VIDI creation/removal, G2D and IPP IOCTL smoke tests, fbdev setup, suspend/resume, and component-bind failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_drv.h

Purpose: this is the main internal contract for the Exynos DRM driver family. It defines shared plane, CRTC, clock, per-file, and device-private structures plus conditional helper stubs and external platform-driver declarations.

Important types: `enum exynos_drm_output_type` identifies NONE, LCD, HDMI, and VIDI outputs. `struct exynos_drm_plane_state` extends DRM plane state with clipped source/CRTC rectangles and 16.16 scaling ratios. `struct exynos_drm_plane` and `struct exynos_drm_plane_config` describe hardware windows and their formats/capabilities. `struct exynos_drm_crtc_ops` is the hardware callback table consumed by `exynos_drm_crtc.c`. `struct exynos_drm_crtc` wraps `drm_crtc` and stores output type, ops, implementation context, optional pipe clock, and I80 mode flag. `struct drm_exynos_file_private` stores G2D in-use command lists, event list, and userptr list. `struct exynos_drm_private` stores global device integration state.

Control flow and integration: display engines populate plane configs and CRTC ops, call shared plane and CRTC creation helpers, then export callbacks through this contract. The top-level driver stores `exynos_drm_private` in `drm->dev_private`, and helpers such as `to_dma_dev()` and `is_drm_iommu_supported()` use that pointer.

State and persistence: all state is runtime kernel memory. `pending`, `lock`, and `wait` exist for atomic commit synchronization across CRTCs. `mapping` and `dma_dev` are the DMA/IOMMU shared state.

Dependencies: this header depends on Linux module and DRM CRTC/device/plane headers. It conditionally declares DPI and FIMC helpers based on Kconfig, providing no-op or `-ENODEV` behavior when disabled.

Risks: the header relies on `drm->dev_private` being initialized before helpers are used. Capability flags must stay in sync with plane implementation support. Stub behavior can hide disabled features if call sites do not distinguish `NULL` encoder from deferred probe.

Test signals: compile all Kconfig combinations, CRTC/plane initialization for all display engines, IOMMU-supported and non-IOMMU GEM paths, G2D open/close file-private lifecycle, and DPI/FIMC disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_dsi.c

Purpose: this file is the Exynos glue around the shared Samsung DSIM MIPI-DSI bridge/host implementation. It supplies Exynos-specific host ops, creates a DRM encoder, and registers the DSIM host as a component.

Important APIs and data: `struct exynos_dsi` wraps the DRM encoder. `exynos_dsi_register_host()` allocates it, stores it in `dsim->priv`, sets `bridge.pre_enable_prev_first`, and adds component ops. `exynos_dsi_bind()` initializes the encoder and registers the MIPI DSI host. `exynos_dsi_host_attach()` attaches the DSIM bridge into the encoder chain, copies lane/format/mode flags from the MIPI DSI device, and updates the LCD CRTC `i80_mode` flag based on video vs command mode. `exynos_dsi_te_irq_handler()` forwards TE IRQs to the CRTC when video output is available.

Control flow: the platform driver's probe/remove are provided by `samsung_dsim_probe()` and `samsung_dsim_remove()`, with Exynos platform data selected by OF compatible. During host registration, component bind later creates the DRM encoder and registers the MIPI host. When a panel/device attaches, the bridge is attached, mode flags are stored, and hotplug is emitted if polling is enabled. Detach emits hotplug again. Unbind atomically disables the bridge and unregisters the host.

State and persistence: runtime state is in `samsung_dsim`, `exynos_dsi`, the DRM encoder, and the LCD CRTC `i80_mode` bit. There is no persistence.

Dependencies and integration points: depends on `drm/bridge/samsung-dsim.h`, DRM bridge/probe/simple encoder helpers, MIPI DSI host framework, component framework, and Exynos CRTC helpers. It integrates with MIC and FIMD through the LCD CRTC path and TE forwarding.

Risks: `exynos_dsi_host_attach()` calls `drm_bridge_attach()` without checking its return value. It assumes `exynos_drm_crtc_get_by_type()` returns a valid LCD CRTC and dereferences it directly. Unbind calls `dsim->bridge.funcs->atomic_disable()` directly, which assumes the bridge is initialized and its funcs are present.

Test signals: probe for each compatible platform data entry, panel attach/detach, command-mode DSI setting `i80_mode`, TE IRQ page flips, hotplug events, and component unbind during active display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fb.c

Purpose: this file implements Exynos framebuffer creation, validation, DMA-address lookup, and DRM mode-config setup.

Important APIs: `exynos_drm_framebuffer_init()` builds a `drm_framebuffer` from Exynos GEM objects and a `drm_mode_fb_cmd2`. `exynos_user_fb_create()` is the mode-config `.fb_create` hook and validates userspace handles, plane sizes, and offsets. `exynos_drm_fb_dma_addr()` returns the DMA address for a framebuffer plane plus its offset. `exynos_drm_mode_config_init()` sets global Exynos mode-config limits and atomic callbacks.

Control flow: userspace `ADDFB2` reaches `exynos_user_fb_create()`, which looks up each GEM handle through `exynos_drm_gem_get()`, computes minimum required size from height, pitch, and offset, and then delegates to `exynos_drm_framebuffer_init()`. The initializer rejects non-contiguous GEM buffers when no IOMMU mapping exists, fills the DRM fb structure, and registers it with `drm_framebuffer_init()`. Plane update paths such as FIMD call `exynos_drm_fb_dma_addr()` to program scanout addresses.

State and persistence: no file-static mutable state. Framebuffer state is held by DRM's framebuffer object and its `fb->obj[]` references. The mode config stores min/max dimensions, callback pointers, and normalized z-position behavior.

Dependencies and integration points: it depends on DRM atomic helpers, GEM framebuffer helpers, Exynos GEM, CRTC, fbdev, and driver-private IOMMU helpers. FIMD and other display controllers consume the DMA-address helper.

Risks: size validation relies on integer arithmetic over pitch, offset, and height; unusual large values need DRM core bounds to prevent overflow. Without IOMMU, non-contiguous buffers are explicitly rejected for scanout. `exynos_drm_fb_dma_addr()` returns 0 on out-of-range index after a warning, which would be a bad hardware address if callers ignored invalid index logic.

Test signals: addfb with single and multiplanar formats, invalid handles, undersized GEMs, noncontiguous GEMs with and without IOMMU, framebuffer destruction, dumb-buffer scanout, and atomic commits using `drm_atomic_helper_commit_tail_rpm`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fb.h

Purpose: this header exposes Exynos framebuffer helpers to display controllers and fbdev setup code.

Important APIs: it declares `exynos_drm_framebuffer_init()`, `exynos_drm_fb_dma_addr()`, and `exynos_drm_mode_config_init()`. It includes `exynos_drm_gem.h` because framebuffer creation takes arrays of `struct exynos_drm_gem *`.

Control flow and integration: fbdev emulation calls `exynos_drm_framebuffer_init()` after allocating a GEM buffer. Display controllers call `exynos_drm_fb_dma_addr()` during plane programming. The top-level driver calls `exynos_drm_mode_config_init()` after `drm_mode_config_init()`.

State and persistence: none in the header; it is an internal declaration surface.

Dependencies: DRM framebuffer types and Exynos GEM are required through included headers and forward declarations in C files.

Risks: callers must preserve GEM object references according to DRM framebuffer lifetime rules and only pass valid plane indices.

Test signals: compile all users, fbdev buffer creation, FIMD plane updates, and addfb paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fbdev.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fbdev.c

Purpose: this file provides fbdev emulation support for Exynos DRM by allocating a GEM-backed framebuffer and filling Linux `fb_info` fields for legacy framebuffer users.

Important APIs: `exynos_drm_fbdev_driver_fbdev_probe()` is the DRM fbdev driver callback. `exynos_drm_fb_mmap()` maps the fbdev framebuffer through GEM PRIME mmap. `exynos_drm_fb_destroy()` tears down the fb helper, removes the framebuffer, and releases the DRM client. `exynos_drm_fbdev_update()` fills fbdev metadata and points `screen_buffer` at the GEM kernel virtual address.

Control flow: when DRM fbdev setup asks for a surface, the probe computes pitch, pixel format, and allocation size from the requested surface size. It allocates a write-combined GEM with `kvmap=true`, creates a one-plane Exynos framebuffer around it, attaches helper funcs, and updates the `fb_info`. Errors unwind by cleaning the framebuffer or destroying the GEM.

State and persistence: fbdev state lives in `drm_fb_helper`, `fb_info`, the GEM object, and the DRM framebuffer. No persistent storage is used.

Dependencies and integration points: it depends on Linux fbdev APIs, DRM fb helper, GEM framebuffer helper, PRIME mmap, Exynos GEM, and Exynos framebuffer helpers. It is inserted into `struct drm_driver` through `EXYNOS_DRM_FBDEV_DRIVER_OPS`.

Risks: fbdev requires a kernel mapping, so GEM allocation must pass `kvmap=true`; failure would make `screen_buffer` invalid. `screen_size` is based on width, height, and cpp rather than pitch times virtual height, so unusual padding should be checked. Destroy order matters because fb helper, framebuffer, and DRM client references overlap.

Test signals: boot console/fbcon, mmap of `/dev/fb*`, fbdev teardown during driver unload, allocation failures, and legacy writes/draw ops on different bpp/depth combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fbdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fbdev.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fbdev.h

Purpose: this header conditionally exposes fbdev emulation support to the top-level Exynos DRM driver.

Important APIs: when `CONFIG_DRM_FBDEV_EMULATION` is enabled it declares `exynos_drm_fbdev_driver_fbdev_probe()` and defines `EXYNOS_DRM_FBDEV_DRIVER_OPS` as `.fbdev_probe = exynos_drm_fbdev_driver_fbdev_probe`. When disabled, the macro expands to `.fbdev_probe = NULL`.

Control flow and integration: `exynos_drm_drv.c` includes this macro in `struct drm_driver`, making fbdev support a compile-time feature without changing driver initialization logic.

State and persistence: none.

Dependencies: it forward-declares `struct drm_fb_helper` and `struct drm_fb_helper_surface_size` to avoid pulling fbdev headers into every user.

Risks: disabled builds must still compile all top-level driver code. Enabled builds depend on the C implementation and GEM/fb helpers being included.

Test signals: Kconfig builds with fbdev emulation enabled and disabled, plus runtime fbdev probe in enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fbdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fimc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fimc.c

Purpose: this file implements the FIMC IPP backend. FIMC performs memory-to-memory image processing: source DMA read, crop, colorspace/format handling, scaling, rotation/flip, and destination DMA write.

Important structures and APIs: `struct fimc_context` embeds `struct exynos_drm_ipp`, stores the DRM device, DMA-private mapping, current task, MMIO base, lock, clocks, scaler state, alias id, and IRQ. `struct fimc_scaler` stores prescaler and main scaler settings. The IPP callback table `ipp_funcs` points to `fimc_commit()` and `fimc_abort()`. `exynos_drm_check_fimc_device()` filters FIMC instances by DT alias and the `fimc_devs` module parameter.

Control flow: probe filters devices, builds a dynamic `exynos_drm_ipp_formats` table for linear and Samsung tiled formats with id-dependent limits, maps registers, requests IRQ, sets up clocks, enables runtime PM autosuspend, and adds a component. Bind registers DMA and registers the IPP instance with crop, rotate, scale, and convert capabilities. A committed IPP task resumes the device, stores `ctx->task`, programs source format/order/tile mode/size/window/address, programs destination format/rotation/size/address, computes scaler ratios, and starts capture/scaler/DMA. The IRQ clears interrupt state, detects overflow and frame end, resolves the completed buffer id, drops runtime PM, calls `exynos_drm_ipp_task_done()`, dequeues the destination buffer, and stops hardware. Abort resets hardware and completes the active task with `-EIO`.

State and persistence: mutable state includes `ctx->task`, scaler configuration, IRQ mask state, buffer sequence register state, runtime PM usage, and clock handles. No persistence beyond runtime kernel state exists.

Dependencies and integration points: depends on the Exynos IPP core, Exynos DMA registration, DRM fourcc/modifier definitions, FIMC register definitions in `regs-fimc.h`, clocks from the FIMC device and parent, component framework, and runtime PM. Userspace reaches it through IPP IOCTLs in the top-level driver.

Risks: programming order is hardware-sensitive; source/destination format, rotation, size, address, scaler, then start must remain consistent. Buffer sequencing and IRQ masking are protected by `ctx->lock`, but `ctx->task` itself is manipulated from commit, IRQ, and abort paths. Overflow returns `IRQ_NONE`, so task completion after overflow depends on later state. Clocks include parent writeback clocks, making probe fragile to DT clock names. Tiled format support has different limits and modifiers that must match userspace expectations.

Test signals: IPP get caps/limits for every FIMC alias, crop/scale/rotate/convert jobs, tiled NV12/NV21 jobs, abort while active, runtime autosuspend after completion, overflow/error injection, FIMC mask module parameter behavior, and repeated bind/unbind with IOMMU registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fimc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fimd.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fimd.c

Purpose: this file implements the FIMD display controller as an Exynos DRM CRTC provider. It programs LCD/I80 timings, window planes, DMA scanout addresses, blending, vblank/TE handling, and runtime power for several Samsung SoC variants.

Important structures and APIs: `struct fimd_driver_data` captures per-SoC register offsets and feature bits such as shadow registers, VIDOUT, VTSEL, MIC bypass, DP clock, hardware trigger, and BGR support. `struct fimd_context` holds clocks, MMIO, sysreg, CRTC, five planes, plane configs, interrupt flags, wait queues, atomic flags for window updates and triggering, and optional DPI encoder. `fimd_crtc_ops` supplies Exynos CRTC callbacks: enable/disable, vblank, atomic begin/flush/check, plane update/disable, and TE handler.

Control flow: probe reads DT properties, I80 timing child data, sysreg phandle, clocks, MMIO, IRQ, initializes wait state, probes optional DPI, enables runtime PM, and adds the component. Bind creates five Exynos planes with format/capability tables, creates the LCD CRTC around window 0, optionally exports a DP pipe clock, binds DPI, clears inherited channels when IOMMU is active, and registers DMA. Atomic enable resumes runtime PM and calls `fimd_commit()`. Atomic check computes a clock divider from the adjusted mode and rejects impossible clocks. Commit programs I80 or RGB timing registers, sysreg display path bypass bits, optional MIC bypass, display size, trigger mode, and `VIDCON0`. Plane update computes DMA start/end/stride, OSD position and size, pixel format, RGB order, burst length, blending, color key, and enables the window and shadow path. Atomic begin protects shadow registers; flush unprotects them and arms pending events. Disable turns all windows off, waits for vblank, clears `VIDCON0`, and suspends runtime PM.

State and persistence: runtime state is in `fimd_context`: `suspended`, `irq_flags`, `clkdiv`, `vidcon*`, I80 flags, wait queues, and atomics. Hardware registers are the effective display state; no disk persistence exists.

Dependencies and integration points: depends on DRM blend/fourcc/framebuffer/vblank APIs, Exynos CRTC/plane/fb helpers, Samsung FIMD register definitions, syscon/regmap, OF display timing, runtime PM, and component framework. It integrates with DPI panels, DSI command-mode TE through `te_handler`, MIC path sysreg bits, and shared DMA mapping.

Risks: many SoC feature flags alter register layout; wrong match data can program invalid registers. `fimd_clear_channels()` temporarily manipulates runtime PM and clocks to turn off inherited windows before DMA mapping. I80 trigger state uses atomics and can drop duplicate triggers intentionally. The TODO notes MIC bypass should be cleared when MIC is enabled, but the current code always sets the bypass bit. Small buffers require burst-length reduction to avoid tearing. Vblank wait has a 50 ms timeout.

Test signals: RGB and I80 panel modes, all five planes, alpha and pixel blend modes, BGR variants, small cursor/window buffers, TE-triggered command-mode flips, vblank enable/disable, suspend/resume, MIC path display, DP clock users, and SoC-specific compatible coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fimd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_g2d.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_g2d.c

Purpose: this file implements Exynos G2D render-node acceleration. It accepts userspace command lists, validates register writes and buffer bounds, maps GEM handles or userptr memory to DMA addresses, queues work to the G2D engine, sends optional completion events, and manages runtime PM.

Important structures and APIs: `struct g2d_data` is the device state: MMIO, IRQ, workqueue, DRM device, flags, command-list pool, runqueue, slab cache, and userptr pool limits. `struct g2d_cmdlist_node` wraps a DMA command list and mapped buffer descriptors. `struct g2d_runqueue_node` batches command lists submitted by a DRM file. `struct g2d_cmdlist_userptr` tracks pinned user pages, SG table, DMA address, refcount, and pool/list flags. IOCTL entry points are `exynos_g2d_get_ver_ioctl()`, `exynos_g2d_set_cmdlist_ioctl()`, and `exynos_g2d_exec_ioctl()`. File lifecycle hooks are `g2d_open()` and `g2d_close()`.

Control flow: bind allocates a DMA-visible pool of 64 command lists, registers DMA, and records `priv->g2d_dev`. `SET_CMDLIST` obtains a free node, optionally reserves an event, emits reset/interrupt setup commands, copies command arrays from userspace, validates register offsets, validates address registers separately, maps GEM/userptr buffers, appends `G2D_BITBLT_START`, and links the node into the file-private in-use list. `EXEC` splices the file-private command and event lists into a runqueue node, queues worker work, and optionally waits for completion. The worker completes the previous node, frees async nodes, resumes runtime PM for the next node, and writes the command-list DMA address plus start command. IRQ handling clears pending bits, sends per-command-list events on GCMD finish, continues DMA when appropriate, and on ACMD finish clears engine busy and wakes the worker. Close removes queued nodes for the file, waits for an active node to finish or resets after timeout, unmaps stale command lists, and frees userptr pool entries.

State and persistence: all state is runtime memory. Per-file state lives in `drm_exynos_file_private` lists. Device state includes free command-list pool, current and queued runqueue nodes, userptr pool accounting, workqueue, runtime PM state, and engine-busy/suspend flags.

Dependencies and integration points: depends on DRM file/event APIs, Exynos GEM, shared DMA mapping, Linux DMA APIs, user-page pinning, workqueues, completions, runtime PM, component framework, and G2D registers. The top-level driver exposes the IOCTLs and calls open/close hooks.

Risks: this is a high-risk userspace-facing path. It copies raw register/value pairs, so `g2d_check_reg_offset()` and `g2d_check_buf_desc_is_valid()` are critical to prevent arbitrary register writes or out-of-bounds DMA. Userptr uses long-term page pins and a capped pool; stale entries with same address but different size are removed from reusable lists. `SET_CMDLIST` currently returns `-EINVAL` without returning the command-list node if command counts exceed limits, which is a resource-leak risk from the visible control flow. Timeout reset in `g2d_wait_finish()` manually completes and PM-puts because the IRQ is lost. Concurrency depends on runqueue and command-list mutexes plus worker/IRQ handoff.

Test signals: malformed command offsets, oversized command counts, GEM and userptr buffers, invalid dimensions/stride/right-bottom values, async and sync execution, event delivery, close while queued/active, timeout reset, runtime suspend/resume, repeated command-list pool exhaustion, and DMA/IOMMU registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_g2d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_g2d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_g2d.h

Purpose: this header exposes the G2D IOCTL handlers and per-file open/close hooks to the top-level Exynos DRM driver, with stubs for builds without G2D.

Important APIs: when `CONFIG_DRM_EXYNOS_G2D` is enabled it declares `exynos_g2d_get_ver_ioctl()`, `exynos_g2d_set_cmdlist_ioctl()`, `exynos_g2d_exec_ioctl()`, `g2d_open()`, and `g2d_close()`. When disabled, IOCTL handlers return `-ENODEV`, `g2d_open()` returns success, and `g2d_close()` is a no-op.

Control flow and integration: `exynos_drm_drv.c` includes the IOCTL declarations in its `exynos_ioctls[]` table and calls `g2d_open()` / `g2d_close()` during DRM file open/postclose. The stub design lets the top-level file lifecycle stay uniform across Kconfig variants.

State and persistence: none in the header. Enabled builds cause per-file G2D list state to be initialized in the C implementation.

Dependencies: only DRM device/file types are required from the including context.

Risks: disabled builds expose IOCTL numbers but return `-ENODEV`; userspace must handle that. Enabled builds require `file->driver_priv` to be initialized before `g2d_open()` is called.

Test signals: Kconfig enabled/disabled builds, G2D IOCTL unavailable behavior, and file open/close with G2D disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_g2d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_gem.c

Purpose: this file implements Exynos GEM buffer allocation, handle creation, mmap, dumb buffers, and PRIME import/export helpers.

Important APIs: `exynos_drm_gem_create()` validates flags and size, initializes a GEM object, adjusts noncontiguous requests when no IOMMU exists, and allocates DMA memory. `exynos_drm_gem_create_ioctl()`, `exynos_drm_gem_map_ioctl()`, and `exynos_drm_gem_get_ioctl()` are userspace IOCTL handlers. `exynos_drm_gem_get()` looks up a GEM handle and returns an Exynos GEM wrapper with a reference. `exynos_drm_gem_dumb_create()` backs DRM dumb buffers. PRIME helpers are `exynos_drm_gem_prime_import()`, `exynos_drm_gem_prime_get_sg_table()`, and `exynos_drm_gem_prime_import_sg_table()`.

Control flow: creation aligns the requested size to a page, initializes the DRM GEM object and mmap offset, then allocates DMA memory with attributes derived from Exynos BO flags. Contiguous allocations set `DMA_ATTR_FORCE_CONTIGUOUS`; write-combined or non-cacheable allocations set `DMA_ATTR_WRITE_COMBINE`; non-fbdev buffers skip kernel mapping. Handle creation gives userspace a handle and drops the allocation reference. Mmap routes imported dma-bufs to `dma_buf_mmap()` and local buffers to `dma_mmap_attrs()` after setting VM flags and page protection. Destruction frees exporter-owned imports through PRIME helpers or frees local DMA memory, releases GEM state, and kfrees the wrapper.

State and persistence: each GEM object stores flags, size, DMA cookie, optional kernel address, DMA address, DMA attrs, and optional imported sg table. No persistence beyond object lifetime exists.

Dependencies and integration points: depends on DMA-BUF namespace, DMA allocation/mmap APIs, DRM GEM/dumb/PRIME/VMA helpers, Exynos DMA device selection, and Exynos BO flag UAPI. Framebuffer, fbdev, IPP, and G2D code consume GEM DMA addresses and references.

Risks: no-IOMMU systems cannot honor noncontiguous allocations and silently drop that flag after warning. PRIME import requires a contiguous DMA mapping as checked by `drm_prime_get_contiguous_size()`. `to_dma_dev()` must be initialized by subdriver DMA registration before allocation. Cacheability flags must match userspace expectations to avoid coherency issues.

Test signals: GEM create/map/get IOCTLs, dumb create with and without IOMMU, fbdev kernel mapping, mmap protections for cacheable/WC/noncached buffers, PRIME import/export of contiguous and noncontiguous sg tables, destruction under handle/import references, and DMA allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_gem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_gem.h

Purpose: this header defines the Exynos GEM object wrapper and declares buffer-management APIs used across the driver.

Important types and APIs: `struct exynos_drm_gem` embeds `drm_gem_object` and stores Exynos BO flags, page-aligned size, DMA cookie, optional `kvaddr`, DMA address, DMA attributes, and imported `sg_table`. `to_exynos_gem()` converts from base GEM object. `IS_NONCONTIG_BUFFER()` checks the Exynos noncontiguous flag. The header declares creation/destruction, IOCTL handlers, handle lookup/put, dumb-create, and PRIME helper functions.

Control flow and integration: framebuffer creation, fbdev allocation, IPP buffer setup, and G2D command-list mapping all use this type to resolve userspace handles to DMA addresses. The top-level DRM driver points GEM and dumb-buffer hooks at the declared functions.

State and persistence: the header describes object state; the actual state persists for the lifetime of each GEM object and referenced dma-buf.

Dependencies: requires DRM GEM types and Linux mm types. It also assumes Exynos BO UAPI definitions are visible through including C files.

Risks: all consumers must call `exynos_drm_gem_put()` after successful `exynos_drm_gem_get()`. Imported buffers may not have local allocation cookies and must be destroyed through PRIME import handling.

Test signals: refcount balance in fb, IPP, and G2D paths; compile coverage; and PRIME/dumb/GEM IOCTL behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_gem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_gsc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_gsc.c

Purpose: this file implements the GSCaler IPP backend. GSC is another memory-to-memory image processor supporting format conversion, crop, scale, rotation/flip, tiled formats, and DMA in/out.

Important structures and APIs: `struct gsc_context` embeds an IPP object and stores DRM/DMA state, current task, register base, clock array, scaler state, id, IRQ, and rotation flag. `struct gsc_scaler` tracks prescaler and main-scaler ratios. `struct gsc_driverdata` provides per-compatible clock names and IPP limits. The IPP backend callbacks are `gsc_commit()` and `gsc_abort()`.

Control flow: probe selects driver data, builds linear and tiled format tables with SoC-specific limits, acquires clocks, maps registers, requests IRQ, enables runtime PM autosuspend, and registers the component. Bind registers DMA and IPP capabilities. Commit resumes runtime PM, records the task, resets hardware, programs source format/rotation/size/address, destination format/size/address, computes prescaler ratios, loads horizontal and vertical coefficient tables based on scaling ratio, and starts one-shot memory-to-memory processing. IRQ detects overflow and frame-done status, dequeues source and destination buffer indices, marks runtime PM idle, and completes the IPP task with success or error. Abort resets and completes active work with `-EIO`.

State and persistence: state is in `gsc_context`: current task, scaler ratios, rotation flag, clock handles, runtime PM usage, and buffer mask registers. There is no persistent storage.

Dependencies and integration points: depends on IPP core, Exynos DMA mapping, DRM fourcc/modifier definitions, `regs-gsc.h`, platform/property APIs, runtime PM, clocks, and component framework. Userspace reaches it through IPP IOCTLs.

Risks: the file contains large hard-coded coefficient tables; wrong ratio selection can degrade scaling or program invalid coefficients. Reset waits up to `GSC_RESET_TIMEOUT`; failure returns `-EBUSY`. Source/destination buffer mask handling assumes single-buffer index 0 for submitted tasks. Tiled output uses Samsung 16x16 modifiers and must match hardware expectations. Runtime PM put on reset failure happens without `mark_last_busy`, unlike normal completion.

Test signals: caps/limits for exynos5250/5420/5433 compatibles, RGB/YUV/tiled formats, up/down scaling, rotations, crop, overflow/frame-done IRQs, reset timeout injection, abort while active, autosuspend, and clock enable rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_gsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_ipp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_ipp.c

Purpose: this file is the common Exynos Image Post Processing framework. It registers hardware IPP engines, exposes enumeration/capability/limit/commit IOCTLs, validates userspace tasks, manages GEM references and DMA addresses, serializes work per engine, and delivers optional completion events.

Important APIs and data: global `ipp_list` and `num_ipp` track registered engines. `exynos_drm_ipp_register()` initializes an engine's lock, todo list, waitqueue, callbacks, caps, format table, and id. `exynos_drm_ipp_unregister()` removes it. IOCTLs are `exynos_drm_ipp_get_res_ioctl()`, `exynos_drm_ipp_get_caps_ioctl()`, `exynos_drm_ipp_get_limits_ioctl()`, and `exynos_drm_ipp_commit_ioctl()`. `exynos_drm_ipp_task_done()` is the backend completion callback.

Control flow: userspace first enumerates IPP ids and format/limit data, then submits a commit with a packed parameter buffer. Commit validates flags, finds the IPP, allocates a task with default full-size rectangles and rotate-0, copies each parameter according to `exynos_drm_ipp_params_maps`, validates rectangles, capabilities, formats, pitch, plane GEM ids, size limits, alignment, and scale limits, then resolves source and destination GEMs. Test-only submissions stop after validation. Real jobs may reserve a DRM event, then enqueue the task. Nonblocking jobs return after enqueue and are cleaned up from a work item after completion; blocking jobs wait on the IPP waitqueue and abort on interruption. The scheduler runs one task at a time per IPP by moving the first todo entry to `ipp->task` and calling backend `commit()`.

State and persistence: each IPP object stores current task, todo list, spinlock, waitqueue, sequence counter, format table, and caps. Each task stores source/destination buffers, transform, alpha, event, flags, return code, and cleanup work. No disk persistence exists.

Dependencies and integration points: depends on DRM UAPI structures, DRM events, blend/rotation helpers, GEM lookup, Exynos GEM DMA addresses, and backend drivers such as FIMC and GSC. The top-level driver exposes these IOCTLs.

Risks: `ipp_list` lookup is not explicitly locked, relying on component serialization for modification and stable runtime registration. Packed userspace parameter parsing must reject unknown ids and undersized buffers. Validation must stay consistent with backend hardware; otherwise backend register programming can see impossible geometry. Blocking waits can be interrupted, invoking backend abort if the task is active. WARNs in unregister catch leaked active/todo tasks.

Test signals: enumeration two-pass behavior, caps/limits copyout, malformed parameter buffers, missing GEM ids, undersized buffers, unsupported format/modifier, crop/rotate/scale/convert capability rejection, test-only jobs, blocking and nonblocking completion, event sequence/timestamps, interrupted blocking wait, and backend unregister with empty queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_ipp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_ipp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_ipp.h

Purpose: this header defines the internal IPP backend contract and task data structures shared by the common IPP core and hardware backends.

Important types: `struct exynos_drm_ipp_funcs` declares nonblocking `commit()` and asynchronous-safe `abort()` callbacks. `struct exynos_drm_ipp` stores DRM/device pointers, list id, name, callback table, caps, supported formats, sequence, lock, current task, todo list, and waitqueue. `struct exynos_drm_ipp_buffer` combines UAPI buffer/rectangle data with GEM references, DRM format info, and per-plane DMA addresses. `struct exynos_drm_ipp_task` stores source/destination buffers, transform, alpha, cleanup work, flags, return code, and optional event. `struct exynos_drm_ipp_formats` maps fourcc/modifier/type to hardware limits.

Control flow and integration: backends call `exynos_drm_ipp_register()` in component bind and provide commit/abort callbacks. Backends call `exynos_drm_ipp_task_done()` from IRQ or abort paths. The common IOCTL code uses the struct fields to validate and schedule tasks. Macros `IPP_SRCDST_FORMAT`, `IPP_SRCDST_MFORMAT`, `IPP_SIZE_LIMIT`, and `IPP_SCALE_LIMIT` simplify backend format tables.

State and persistence: this header defines runtime scheduler and task state. No persistence exists.

Dependencies: it relies on DRM Exynos UAPI structures, DRM format info through C files, Exynos GEM, and `MAX_FB_BUFFER` from the driver header.

Risks: backend `commit()` must not wait synchronously and must eventually call task-done or the queue stalls. `abort()` must also complete the task. Disabled `CONFIG_DRM_EXYNOS_IPP` stubs return empty resources or `-ENODEV`.

Test signals: compile with IPP enabled/disabled, backend registration/unregistration, macro-generated limits, task completion from IRQ and abort, and IOCTL stub behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_ipp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_mic.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_mic.c

Purpose: this file implements the Exynos MIC display bridge. MIC appears to be a display path block that transforms/compresses panel timing data between FIMD/DSI-like paths and panel output, with separate RGB and I80 modes.

Important structures and APIs: `struct exynos_mic` stores device, MMIO base, sysreg regmap, two clocks, current I80 mode, current videomode, DRM bridge, and enabled flag. `mic_bridge_funcs` supplies bridge `mode_set`, `pre_enable`, and `post_disable`. Component ops bind the bridge to the encoder associated with the LCD CRTC.

Control flow: probe allocates a DRM bridge object, maps MIC registers, obtains the display syscon regmap and clocks, registers the bridge, enables runtime PM, and adds the component. Bind finds the LCD CRTC, scans encoders for matching `possible_crtcs`, stores driver_private, and attaches the MIC bridge to that encoder. During mode set it converts the DRM mode to `videomode` and copies the CRTC `i80_mode` flag. Pre-enable resumes runtime PM, configures sysreg path selection, software-resets MIC, programs porch timing for RGB mode, image size, output timing, and enables MIC registers. Post-disable clears path selection and runtime-PM puts the device. Runtime PM suspend/resume disables/enables both clocks in order.

State and persistence: state is protected by a global `mic_mutex`, including `enabled`, `i80_mode`, and `vm`. The hardware state is sysreg mux bits and MIC registers. No persistence exists.

Dependencies and integration points: depends on DRM bridge/encoder APIs, Exynos CRTC helpers, OF address/graph, syscon/regmap, clocks, runtime PM, and videomode conversion. It integrates into the LCD encoder chain and observes DSI command-mode state through the CRTC.

Risks: bind assumes an LCD CRTC exists and does not check `IS_ERR()` before using it. It selects an encoder by exact `possible_crtcs` equality, which can fail with clone/multi-CRTC masks. The mutex is global rather than per-device, limiting concurrency but simplifying shared path registers. Error messages in `mic_set_path()` say "read" for a failed write. MIC bypass in FIMD has a TODO, so MIC and FIMD sysreg settings may not be fully coordinated.

Test signals: exynos5433 MIC probe, bridge attach to LCD encoder, RGB and I80 modes, DSI command-mode transitions, runtime PM clock ordering, reset timeout, sysreg read/write failures, pre-enable error unwinding, and bridge disable/unbind while enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_mic.c -->
