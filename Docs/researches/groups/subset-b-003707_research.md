# Research: subset-b-003707

This grouped report covers the PL111 platform helpers, the QXL virtual GPU DRM driver files, and selected Radeon build/ATOM BIOS headers. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_drv.c

Purpose: This is the top-level DRM/KMS AMBA driver for ARM PrimeCell PL110/PL111 CLCD hardware. It allocates `struct drm_device`, attaches PL111 private state, initializes panel or bridge output discovery from device tree graph endpoints, registers the display pipe, and binds the AMBA IDs for vanilla PL110, PL111, and Nomadik LCDC variants.

Important APIs, types, and functions: `pl111_amba_probe()` is the main probe path; `pl111_modeset_init()` sets `drmm_mode_config_init()`, min/max mode limits, bridge/panel attachment, vblank setup, and polling. `pl111_gem_import_sg_table()` refuses PRIME imports when device-specific reserved memory is active. `pl111_amba_remove()` and `pl111_amba_shutdown()` drive DRM unregister and atomic shutdown. The file also defines `pl110_variant`, `pl111_variant`, and `pl110_nomadik_variant` with pixel formats, register quirks, vblank quirks, and fbdev depth.

Control flow: AMBA probe allocates private state, initializes reserved memory, reads optional `max-memory-bandwidth`, chooses PL110/PL111 interrupt/control register offsets, ioremaps MMIO, lets `pl111_versatile_init()` override platform variant data, calls `pl111_nomadik_init()`, disables interrupts, requests the IRQ, initializes modesetting, registers DRM, then creates the client/fbdev setup. Modeset init walks all OF endpoints looking for a panel or bridge, defers only if no usable endpoint exists and at least one endpoint requested deferral, wraps panels in `drm_panel_bridge_add_typed()`, calls `pl111_display_init()`, attaches the bridge to the simple display pipe, and initializes vblank unless the variant declares it broken.

State and persistence: Persistent runtime state lives in `pl111_drm_dev_private`: selected variant, register mappings, panel/bridge pointers, MMIO offsets, reserved-memory flag, and memory bandwidth. Hardware state is not restored from prior boot state; comments explicitly call out missing hardware-state readback and a known pageflip/vsync race. Device-specific reserved memory changes import behavior and is released on probe failure/remove.

Dependencies and integration points: The file integrates Linux AMBA bus matching, OF graph endpoint discovery, DRM atomic helpers, GEM DMA helpers, DRM panel/bridge infrastructure, fbdev DMA client setup, reserved-memory APIs, and platform helpers in `pl111_versatile.c` and `pl111_nomadik.c`. `pl111_display_init()`, `pl111_irq()`, and `pl111_debugfs_init()` are provided by other PL111 driver files.

Risks: Endpoint probing can be subtle because `-EPROBE_DEFER` is only acted on after scanning every endpoint. PRIME import is intentionally disabled with device-local memory, which may surprise generic userspace. The driver documents a pageflip completion race around base-address programming and vblank IRQs. Platform helper failures before registration must keep panel bridge cleanup and reserved-memory release balanced.

Test signals: Probe on device-tree systems with panel-only, bridge-only, missing-endpoint, and deferred-endpoint configurations; boot on PL110, PL111, Nomadik, and Versatile/RealView boards; validate fbdev depth and supported formats per variant; exercise suspend/shutdown atomic paths; confirm PRIME import returns `-EINVAL` when reserved memory is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_nomadik.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_nomadik.c

Purpose: This Nomadik-specific helper switches the ST-Ericsson Nomadik PMU display mux into CLCD mode so the PL110-derived LCDC block, not the alternate MDIF block, drives the display path.

Important APIs, types, and functions: `pl111_nomadik_init(struct drm_device *dev)` looks up the PMU syscon via compatible string `stericsson,nomadik-pmu` and updates `PMU_CTRL_LCDNDIF` at `PMU_CTRL_OFFSET`. It is exported with `EXPORT_SYMBOL_GPL`.

Control flow: The function is intentionally opportunistic: if the PMU syscon is not present, it returns without error so multiplatform kernels can probe non-Nomadik PL111 devices. If the syscon exists, it clears the `LCDNDIF` bit through `regmap_update_bits()` and emits a DRM info message.

State and persistence: The only state change is persistent hardware register state in the PMU syscon, outside the DRM device itself. There is no local cache and no cleanup path to restore MDIF routing.

Dependencies and integration points: Depends on Linux MFD syscon/regmap APIs and is called from `pl111_amba_probe()` after Versatile variant detection and before IRQ/modeset initialization. It complements the Nomadik variant metadata in `pl111_drv.c`.

Risks: Silent return on syscon lookup failure is intentional but can hide device-tree binding mistakes. The mux write is unconditional once the PMU node exists, so systems sharing the PMU with another display pipeline rely on correct platform configuration.

Test signals: Boot a Nomadik/STn8815 device tree with PMU syscon present and verify the info log plus CLCD output; boot non-Nomadik PL111 systems and ensure this helper is a no-op; inspect PMU register values after probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_nomadik.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_nomadik.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_nomadik.h

Purpose: This header exposes the Nomadik mux helper to the PL111 core while compiling to a no-op on kernels without `CONFIG_ARCH_NOMADIK`.

Important APIs, types, and functions: Declares `pl111_nomadik_init(struct drm_device *dev)` when Nomadik architecture support is enabled; otherwise provides a static inline empty function with the same signature.

Control flow: There is no runtime control flow beyond the compile-time configuration branch. The PL111 core can call `pl111_nomadik_init()` unconditionally.

State and persistence: The header owns no state. It controls whether the PMU mux write in `pl111_nomadik.c` is linked into the build.

Dependencies and integration points: Included by `pl111_drv.c`; indirectly depends on `struct drm_device` being visible enough for the declaration. The no-op form keeps generic ARM multiplatform builds from needing Nomadik PMU support.

Risks: The file declares `struct device` but the visible API uses `struct drm_device`; correctness relies on included DRM declarations from the including translation unit. If include ordering changes, a forward declaration for `struct drm_device` may be needed.

Test signals: Compile PL111 with and without `CONFIG_ARCH_NOMADIK`; verify no unresolved symbol or missing type warning; run probe on both configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_nomadik.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_versatile.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_versatile.c

Purpose: This file provides platform-specific setup for ARM Integrator, Versatile, RealView, and Versatile Express boards using PL110/PL111 CLCD blocks. It maps syscon compatibles to variant metadata, register callbacks, connector mux programming, and DVI mux decisions.

Important APIs, types, and functions: `pl111_versatile_init()` is the exported entry point. Internal callbacks include `pl111_integrator_enable()`, `pl111_impd1_enable()/disable()`, `pl111_versatile_enable()/disable()`, and `pl111_realview_clcd_enable()/disable()`. `pl111_vexpress_clcd_init()` handles VExpress-specific motherboard/core-tile DVI muxing through `devm_regmap_init_vexpress_config()`. Static `pl111_variant_data` instances override formats, fbdev depth, broken clockdivider/vblank flags, and register selection.

Control flow: The init path finds a matching syscon node from `versatile_clcd_of_match`; non-reference designs return success without changes. VExpress uses a special path that scans root child nodes for core-tile PL111/HDLCD, decides whether motherboard or daughterboard should own DVI, writes the FPGA mux, and selects the VExpress variant. Integrator systems can be redirected to an IM-PD1 syscon if present. Other platforms convert the syscon node to a regmap and install variant callbacks and metadata based on the matched enum.

State and persistence: A file-static `versatile_syscon_map` is used by enable/disable callbacks to write platform control registers. `priv->variant`, `priv->variant_display_enable`, `priv->variant_display_disable`, `priv->ienb`, and `priv->ctrl` are persistent driver state for the probed device. The actual connector/mux settings persist in platform syscon registers until changed by firmware or another driver.

Dependencies and integration points: Integrates OF matching, syscon/regmap, platform devices, VExpress config APIs, DRM format definitions, and `pl111_drm_dev_private`. The display pipeline later calls the installed enable/disable callbacks when programming the CLCD.

Risks: `versatile_syscon_map` is global, so multiple matching CLCD instances would share callback backing state. VExpress probe can intentionally return `-ENODEV` to deactivate the motherboard CLCD when core-tile graphics owns DVI; that needs to be interpreted as platform selection, not a generic failure. Format-to-mux programming is limited to known DRM formats and logs errors for unhandled formats.

Test signals: Boot each supported ARM reference design; validate syscon bits for RGB/BGR/555/888 modes; test VExpress configurations with motherboard-only CLCD, core-tile CLCD, and core-tile HDLCD; confirm broken-vblank and clock-divider flags change behavior in the core driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_versatile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_versatile.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_versatile.h

Purpose: This header declares the Versatile-family initialization hook used by the PL111 core.

Important APIs, types, and functions: `pl111_versatile_init(struct drm_device *dev, struct pl111_drm_dev_private *priv)` is the only exported API. The header includes `pl111_drm.h` and forward-declares `struct device` and `struct pl111_drm_dev_private`.

Control flow: No runtime control flow exists here. The declaration lets `pl111_drv.c` invoke the platform override before IRQ and modeset setup.

State and persistence: No state is owned by the header. It defines the dependency contract between core probe and platform variant setup.

Dependencies and integration points: Integrated with `pl111_versatile.c` and `pl111_drv.c`. It depends on DRM and PL111 private type definitions being available during compilation.

Risks: Any signature drift between this declaration and the implementation breaks the PL111 core build. Because the header includes the private PL111 header, it may propagate more internal definitions than strictly needed.

Test signals: Compile PL111 with this header included from the core driver and validate that `pl111_versatile_init()` links and is called during probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_versatile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/Kconfig

Purpose: This Kconfig entry exposes the QXL virtual GPU DRM driver as `DRM_QXL`, a tristate driver for SPICE/QXL virtualized desktop integration.

Important APIs, types, and functions: The configuration depends on `DRM`, `PCI`, and `HAS_IOPORT`, and selects DRM client selection, KMS helper, TTM, TTM helper, DRM exec, and CRC32 support. The help text warns that a matching X.org QXL userspace driver is expected for kernel modesetting.

Control flow: Build-time only: selecting `DRM_QXL=y/m` causes the qxl object list in the Makefile to build into `qxl.o` or the kernel image.

State and persistence: No runtime state. The selected symbols alter the available driver code and dependencies at kernel build time.

Dependencies and integration points: Integrates with PCI, DRM core, TTM memory management, KMS helpers, and CRC32 used by monitor config validation in `qxl_display.c`.

Risks: `HAS_IOPORT` is essential because QXL uses `outb()` I/O port commands. Removing selected helpers would cause link or runtime feature failures. The warning about userspace compatibility is meaningful: enabling KMS without compatible userspace may regress virtual desktop behavior.

Test signals: Build QXL as built-in and module; verify dependency closure selects TTM/CRC32/DRM_EXEC; boot under QEMU/SPICE with and without matching userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/Makefile

Purpose: This Makefile defines the QXL DRM driver object composition.

Important APIs, types, and functions: `qxl-y` lists all translation units: driver entry, KMS/display, TTM/object/GEM, command/image/draw/debugfs/IRQ/dumb/ioctl/release/PRIME. `obj-$(CONFIG_DRM_QXL) += qxl.o` binds the aggregate object to Kconfig.

Control flow: Build-time only. Kbuild compiles each listed `.o` and links them into `qxl.o` when `DRM_QXL` is enabled.

State and persistence: No runtime state. The file controls which code participates in the module.

Dependencies and integration points: Mirrors the split declarations in `qxl_drv.h`; adding or removing a source file must stay synchronized with exported prototypes and driver feature registration.

Risks: Missing an object silently becomes a link failure for referenced symbols, while stale objects can retain dead code. Because QXL spans many tightly coupled files, object-list drift is high impact.

Test signals: `make drivers/gpu/drm/qxl/` for module and built-in configurations; inspect `qxl.o` symbol resolution for all functions declared in `qxl_drv.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_cmd.c

Purpose: This file implements QXL guest/host command-ring handling, I/O-port commands, release-ring garbage collection, surface ID allocation/reaping, and host surface create/destroy operations.

Important APIs, types, and functions: `qxl_ring_create/free/push()`, `qxl_check_idle()`, `qxl_push_command_ring_release()`, `qxl_push_cursor_ring_release()`, `qxl_queue_garbage_collect()`, and `qxl_garbage_collect()` manage ring communication and completed releases. I/O helpers include `qxl_io_update_area()`, `qxl_io_create_primary()`, `qxl_io_destroy_primary()`, `qxl_io_memslot_add()`, `qxl_io_reset()`, and `qxl_io_monitors_config()`. Surface helpers include `qxl_surface_id_alloc/dealloc()`, `qxl_hw_surface_alloc/dealloc()`, and `qxl_surface_evict()`.

Control flow: Ring push waits or busy-spins when the producer has filled the host-visible ring, copies a command into the current slot, advances `prod`, and notifies the host when requested. Async I/O commands serialize through `async_io_mutex`, track `irq_received_io_cmd`, issue `outb()`, and wait up to five seconds for an IRQ. Garbage collection pops release IDs from the host release ring, follows `next` chains through mapped release info, frees releases, and wakes release waiters. Surface allocation gets an ID from `surf_id_idr`, creates a `QXL_SURFACE_CMD_CREATE` release, fences involved BOs, pushes it, and later mirrors destroy through `QXL_SURFACE_CMD_DESTROY`.

State and persistence: Runtime state includes ring headers in guest VRAM RAM header, `release_idr`, `surf_id_idr`, `last_alloced_surf_id`, `primary_bo`, wait queues, atomic IRQ counters, and per-BO `surface_id`/`hw_surf_alloc`. Host-visible state persists in QXL device memory and is reset or rebuilt during device initialization and resume.

Dependencies and integration points: Depends on QXL protocol structs in `qxl_dev.h`, BO helpers in `qxl_object.c`, release helpers in `qxl_release.c`, IRQ wait queues from `qxl_irq.c`, and TTM reservation/fence behavior. Command pushes are used by display, draw, cursor, ioctl, and surface management paths.

Risks: Ring fullness, memory barriers, and IRQ wait sequencing are concurrency-sensitive. `qxl_bo_physical_address()` assumes stable BO resource placement while mapping commands. Surface reaping can stall on fences and must avoid races with IDR lookups and eviction. Async I/O timeout treats missing host response as device disappearance.

Test signals: Stress command-ring and cursor-ring saturation; trigger host release-ring chains; allocate more surfaces than `rom->n_surfaces` to exercise reaping; test update-area bounds; suspend/resume to rebuild memslots; run under QEMU with IRQ loss or delayed host processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_debugfs.c

Purpose: This file exposes debugfs diagnostics for QXL IRQ counters, live buffer objects, and TTM memory managers.

Important APIs, types, and functions: `qxl_debugfs_init(struct drm_minor *minor)` registers built-in debugfs files and calls `qxl_ttm_debugfs_init()`. `qxl_debugfs_add_files()` lets other QXL components register additional `drm_info_list` tables up to `QXL_DEBUGFS_MAX_COMPONENTS`. Readers include `qxl_debugfs_irq_received()` and `qxl_debugfs_buffers_info()`.

Control flow: When `CONFIG_DEBUG_FS` is enabled, driver debugfs init registers `irq_received` and `qxl_buffers`. IRQ output prints total, display, cursor, I/O command, and error counters. Buffer output walks `qdev->gem.objects`, counts bookkeeping fences using `dma_resv_iter`, and prints size, pin count, and release count.

State and persistence: Debugfs state is held in `qdev->debugfs[]` and `debugfs_count`, plus the runtime counters and GEM list being observed. It does not mutate device state except adding debugfs entries.

Dependencies and integration points: Uses DRM debugfs helpers, QXL GEM object lists, DMA reservation fence iteration, and QXL TTM debugfs setup. It is reached through the DRM driver `.debugfs_init` callback in `qxl_drv.c`.

Risks: `qxl_debugfs_buffers_info()` walks the GEM object list without taking `qdev->gem.mutex`, so debugfs reads during object churn depend on external serialization or may be diagnostically racy. Component registration must not exceed the fixed maximum.

Test signals: Mount debugfs and read `irq_received`, `qxl_buffers`, `qxl_mem_mm`, and `qxl_surf_mm` after modesets, cursor updates, and draw activity; build with and without `CONFIG_DEBUG_FS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_dev.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_dev.h

Purpose: This header embeds QXL/SPICE device protocol definitions used to communicate between the guest DRM driver and the virtual QXL host device.

Important APIs, types, and functions: It defines protocol enums for SPICE image/bitmap/surface/clip/brush/cursor types, QXL device revisions, PCI range indices, I/O command numbers, interrupt bits, ring sizes, ROM/RAM header layout, command and release structures, draw/cursor/surface/image/bitmap structures, monitor config structures, and packed protocol data types such as `QXLPHYSICAL`.

Control flow: There is no executable control flow; runtime files populate these packed structs in guest-visible VRAM or surface memory and notify the host via command rings or I/O ports. The append-only comments document ABI constraints for QXL revision compatibility.

State and persistence: Structures in this header describe persistent shared memory layout: `struct qxl_rom` is host-provided read-only configuration, `struct qxl_ram_header` is guest/host shared command and status memory, and command payloads persist until the host completes releases.

Dependencies and integration points: Included by `qxl_drv.h` and used across command, display, image, draw, ioctl, and release code. Values must match spice-protocol/QXL host implementations, especially packed layout and integer widths.

Risks: Numeric value or packing changes would break guest/host ABI. Many structs contain variable-length tails, so size calculations in callers must avoid overflow and account for packed layout. Endianness and alignment assumptions are protocol-sensitive.

Test signals: Compile-time structure size checks would be valuable; runtime validation includes successful QEMU/SPICE boot, command submission, cursor updates, monitor config exchange, and surface create/destroy across QXL revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_display.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_display.c

Purpose: This file implements QXL KMS display support: virtual CRTCs/connectors, client monitor configuration, primary and cursor planes, framebuffer dirty handling, dumb-shadow handling, mode validation, vblank, and monitor config objects.

Important APIs, types, and functions: Public functions include `qxl_display_read_client_monitors_config()`, `qxl_create_monitors_object()`, `qxl_destroy_monitors_object()`, `qxl_modeset_init()`, and `qxl_modeset_fini()`. Internal helpers cover CRC-validated ROM monitor config copying, connector detect/get_modes, `qxl_primary_atomic_update/disable/check()`, cursor creation/update/move/hide, plane prepare/cleanup, CRTC atomic flush/enable/disable, and monitor config sending.

Control flow: Modeset init creates a host-visible monitors config BO, initializes DRM mode config, creates suggested offset properties and the QXL hotplug property, then builds `qxl_num_crtc` CRTC/output pairs and initializes vblank. Client monitor changes are read from ROM with CRC retry, copied into `client_monitors_config`, update connector suggested offsets under modeset lock, and trigger HPD/hotplug. Atomic primary updates create/destroy the primary host surface as needed, apply cursor state, and draw dirty framebuffer regions into QXL commands. Cursor plane changes create QXL cursor BOs or move/hide via cursor releases.

State and persistence: Persistent runtime state includes `monitors_config_bo`, mapped `monitors_config`, `client_monitors_config`, per-CRTC cursor BOs, `dumb_shadow_bo`, `dumb_heads`, primary BO state, connector properties, and vblank events. Host-visible monitor config address is stored in `ram_header->monitors_config`; it is rebuilt on init/resume.

Dependencies and integration points: Uses DRM atomic helpers, simple encoders, virtual connectors, GEM framebuffer helpers, QXL draw/image/cmd/release/object helpers, CRC32, and QXL protocol monitor structures. It is called from `qxl_drv.c` probe/resume/freeze paths and from the IRQ worker on client monitor config interrupts.

Risks: Client monitor config depends on ROM CRC stability and bounded retries. Dumb-shadow aggregation copies multiple dumb heads into one primary surface and must keep offsets coherent. Cursor BO creation pins and maps user BOs and assumes 64x64 ARGB cursor input. Atomic event handling uses vblank timer helpers rather than hardware vblank.

Test signals: Multi-monitor hotplug through SPICE client changes; modes over VRAM size boundaries; atomic page flips with vblank events; cursor image and move tests; dumb buffer scanout on multiple heads; dirtyfb clipping; suspend/resume monitor object recreation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_draw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_draw.c

Purpose: This file converts framebuffer dirty regions into QXL draw commands using bitmap image objects and clip rectangles.

Important APIs, types, and functions: `qxl_draw_dirty_fb()` is the exported drawing entry point. Internal helpers allocate clip BOs, set up `struct qxl_clip_rects`, allocate draw releases, and initialize `struct qxl_drawable` with copy operation metadata.

Control flow: For a dirtyfb call, the function allocates a drawable release, computes the bounding box of clip rectangles, allocates clip and image BOs attached to the release, reserves all release BOs, creates a `QXL_DRAW_COPY` drawable, maps the source framebuffer BO, initializes a QXL bitmap image from the dirty area, fills clip rectangles, fences the release BO list, and pushes the drawable to the command ring. Error paths back off reservations and free allocated image/clip/release objects.

State and persistence: The function creates transient release, image, and clip BOs that remain live until the host returns their release IDs. It reads framebuffer BO contents and writes host-visible QXL command payloads.

Dependencies and integration points: Called from `qxl_display.c` atomic primary updates and framebuffer `.dirty`. Depends on `qxl_image_alloc_objects()`, `qxl_image_init()`, release helpers, BO mapping helpers, and QXL command ring push.

Risks: Clip rectangles are aggregated into a single bounding image, so large sparse dirty regions can copy more data than necessary. The first clip rectangle is modified by `dumb_shadow_offset`, which mutates caller-provided clip storage. Error cleanup must avoid freeing releases after successful push. TODOs note missing optimized fill handling and known clip-list performance concerns.

Test signals: Dirtyfb with zero clips, multiple clips, annotated copy clips, dumb-shadow offsets, 24/32-bit formats, sparse dirty regions, and forced allocation/reservation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_draw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_drv.c

Purpose: This is the QXL PCI DRM driver entry point. It matches QXL PCI devices, manages probe/remove/shutdown and power-management transitions, registers DRM ioctls, and defines the `struct drm_driver`.

Important APIs, types, and functions: `qxl_pci_probe()`, `qxl_pci_remove()`, `qxl_pci_shutdown()`, `qxl_drm_release()`, suspend/resume/freeze/thaw/restore helpers, `qxl_ioctls[]`, `qxl_driver`, and `qxl_pci_driver`. Module parameters include `modeset` and `num_heads`.

Control flow: Probe rejects devices older than revision 4, allocates `struct qxl_device` with `devm_drm_dev_alloc()`, enables PCI, removes conflicting apertures, grabs legacy VGA I/O for old VGA revisions, initializes the QXL device, initializes modeset, starts polling, registers DRM, and starts DRM clients. Remove unregisters DRM, shuts down atomic state, stops polling, and releases VGA resources; final device cleanup happens through the DRM `.release` callback. PM freeze suspends mode config, destroys monitor object, evicts surfaces/VRAM, waits command/release rings idle, and saves PCI state; resume resets or reinitializes device state and recreates monitors.

State and persistence: Driver-level persistent state includes PCI drvdata, module parameters, DRM registered state, VGA arbitration ownership, and QXL device allocations. On suspend, host-visible surfaces and VRAM are evicted and monitor state is rebuilt rather than persisted.

Dependencies and integration points: Integrates Linux PCI, VGA arbitration, aperture helpers, DRM module helpers, atomic suspend/resume helpers, fbdev TTM ops, PRIME import hooks, QXL KMS/device/object/ioctl code, and PM core.

Risks: Cleanup ordering is explicitly noted as non-trivial: `qxl_device_fini()` is in `.release`, not `pci_remove()`. Busy waits for command ring idle can spin if the host stops consuming commands. Revision checks and VGA legacy I/O handling are critical for older virtual devices.

Test signals: PCI probe/remove cycles, module unload, suspend/resume/hibernate, revision 3 rejection, VGA and display-other class devices, all DRM ioctls, fbdev client setup, and QEMU/SPICE smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_drv.h

Purpose: This is the central private header for the QXL DRM driver. It defines driver constants, core runtime structures, conversion macros, and cross-file function prototypes.

Important APIs, types, and functions: Key structs include `qxl_bo`, `qxl_gem`, `qxl_crtc`, `qxl_output`, `qxl_mman`, `qxl_memslot`, `qxl_release`, `qxl_drm_image`, `qxl_debugfs`, and `qxl_device`. It declares command, display, GEM, dumb, TTM, image, release, draw, debugfs, PRIME, IRQ, surface, and ioctl APIs. `qxl_bo_physical_address()` computes QXL physical addresses from BO placement and memslot high bits.

Control flow: The header itself has no runtime control flow, but it defines the shared control contract between probe, KMS, object management, command submission, and ioctls. Inline address computation chooses main vs surface memslot based on TTM memory type.

State and persistence: `struct qxl_device` aggregates nearly all persistent driver state: PCI resource bases, ROM/RAM mappings, rings, BO managers, memslots, IDRs, release counters, wait queues, IRQ counters, work structs, primary/dumb-shadow state, monitor config, and debugfs registry. `qxl_bo` persists per-buffer surface and mapping state.

Dependencies and integration points: Includes DRM core, GEM, TTM, DRM exec, DMA fences, QXL UAPI, and `qxl_dev.h`. It is included by nearly every QXL translation unit, so it is the coupling point for subsystem boundaries.

Risks: `qxl_bo_physical_address()` has a TODO about locking while reading BO resource placement. Struct fields have mixed locking rules; comments identify `gem.mutex`, `tbo.reserved`, spinlocks, and mutexes, but callers must obey them. Any struct layout changes can affect many files.

Test signals: Full QXL build after prototype or struct changes; lockdep under modeset/draw/ioctl stress; surface memory vs VRAM address validation; sparse/static analysis for missing declarations and locking misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_dumb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_dumb.c

Purpose: This file implements DRM dumb-buffer creation for QXL.

Important APIs, types, and functions: `qxl_mode_dumb_create()` fills `struct drm_mode_create_dumb`, maps 16 bpp to `SPICE_SURFACE_FMT_16_565` and 32 bpp to `SPICE_SURFACE_FMT_32_xRGB`, creates a CPU-domain GEM object with QXL surface metadata, marks the resulting BO as dumb, and returns handle/pitch/size.

Control flow: The function computes pitch and page-aligned size, rejects unsupported bpp, creates a GEM handle through `qxl_gem_object_create_with_handle()`, marks `qobj->is_dumb = true`, drops the local object reference, and updates the ioctl args.

State and persistence: The created BO persists as a GEM/TTM object and carries `is_dumb` plus `surf` metadata. It may later be assigned a shared dumb shadow BO by the display plane preparation path.

Dependencies and integration points: Called by DRM core through `.dumb_create` in `qxl_drv.c`. It depends on GEM creation in `qxl_gem.c`, BO conversion macros, and SPICE surface formats from `qxl_dev.h`.

Risks: Pitch calculation uses simple multiplication without explicit overflow checks. Dumb BOs are initially CPU-domain and need display code to manage shadows for scanout. Only 16 and 32 bpp are supported.

Test signals: `modetest`/kms dumb buffer creation for 16 and 32 bpp, rejection of other bpp values, large dimensions near overflow/VRAM limits, mmap/map offset flow, and scanout through primary planes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_dumb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_gem.c

Purpose: This file wraps QXL BO allocation in DRM GEM object lifecycle and handle management.

Important APIs, types, and functions: `qxl_gem_object_create()`, `qxl_gem_object_create_with_handle()`, `qxl_gem_object_free()`, `qxl_gem_object_open()`, `qxl_gem_object_close()`, `qxl_gem_init()`, and `qxl_gem_fini()`.

Control flow: Object creation aligns to at least a page, calls `qxl_bo_create()`, exposes the embedded TTM GEM object, and tracks the BO on `qdev->gem.objects` under `gem.mutex`. Handle creation creates a DRM handle and either returns the object reference to the caller or drops the allocation reference. Free evicts any QXL surface and finalizes the TTM BO; fini force-deletes still-active user objects.

State and persistence: Maintains the per-device GEM object list and per-object GEM/TTM references. Surface state can be torn down during free before TTM finalization.

Dependencies and integration points: Used by QXL ioctls, dumb creation, monitors object creation, and object funcs in `qxl_object.c`. Relies on DRM GEM handles, TTM BO lifecycle, and QXL surface eviction.

Risks: If `drm_gem_handle_create()` fails, the local object reference is not explicitly dropped in this function, which should be audited against DRM ownership expectations. Force-delete indicates userspace leaked objects and is a last-resort cleanup path. Open/close are no-ops, so per-file accounting is not tracked.

Test signals: GEM allocation and handle creation failures, object close/unload with live handles, debugfs GEM list consistency, and memory leak checks on driver unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_image.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_image.c

Purpose: This file allocates and initializes QXL bitmap image objects used by draw commands.

Important APIs, types, and functions: `qxl_image_alloc_objects()` creates a `qxl_drm_image`, its descriptor BO, and one data chunk BO; `qxl_image_init()` copies framebuffer pixels into the chunk and fills `struct qxl_image`; `qxl_image_free_objects()` releases image/chunk BOs.

Control flow: Allocation creates a release-associated image BO and chunk BO sized for `height * stride` plus protocol headers. Initialization offsets source data by x/y, writes chunk metadata, copies contiguous or row-by-row pixel data across pages into the chunk, fills image descriptor fields, maps depth 1/24/32 to SPICE bitmap formats, marks images top-down, and stores the chunk physical address in the bitmap.

State and persistence: Image and chunk BOs are transient release-owned GPU-visible objects. Their contents persist until the host consumes and releases the draw command.

Dependencies and integration points: Used by `qxl_draw_dirty_fb()`. Depends on release-attached BO allocation, QXL BO atomic mapping helpers, SPICE image protocol definitions, and QXL physical address computation.

Risks: The code has explicit TODO/FIXME notes for integer overflow and variable chunk counts. It supports only 1, 24, and 32 bpp; 16 bpp dirty paths would fail. The chunk uses framebuffer stride rather than packed line size due to rendering concerns, which affects memory size and host interpretation.

Test signals: Dirty draw paths for 24/32 bpp, unsupported-depth rejection, very large dirty rectangles, non-contiguous row copying where `stride != linesize`, and allocation failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_image.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_ioctl.c

Purpose: This file implements QXL-specific DRM ioctls for allocation, mapping, execbuffer submission, explicit update areas, capability queries, and surface allocation.

Important APIs, types, and functions: Public ioctl handlers include `qxl_alloc_ioctl()`, `qxl_map_ioctl()`, `qxl_execbuffer_ioctl()`, `qxl_update_area_ioctl()`, `qxl_getparam_ioctl()`, `qxl_clientcap_ioctl()`, and `qxl_alloc_surf_ioctl()`. Internal helpers process relocations through `apply_reloc()`, `apply_surf_reloc()`, `qxlhw_handle_to_bo()`, and `qxl_process_single_command()`.

Control flow: Execbuffer processing accepts only draw commands, validates command size and user pointers, allocates a release BO, copies the command payload after the release-info header, stamps `mm_time`, copies relocation metadata from userspace, resolves GEM handles into release BO lists, reserves/validates all BOs, applies physical-address or surface-ID relocations, fences objects, and pushes the command ring. Update-area ioctl validates rectangle ordering, looks up/reserves the BO, validates placement, ensures a surface ID, and issues an update-area I/O command.

State and persistence: Ioctls create GEM BOs, release objects, relocation writes into BO memory, host-visible surfaces, and command submissions. User handles persist until closed; releases persist until host completion.

Dependencies and integration points: Registered in `qxl_drv.c`; depends on QXL UAPI structs, DRM GEM lookup, usercopy helpers, TTM validation, release helpers, BO mapping, command ring pushes, and QXL protocol relocation semantics.

Risks: User input is high-risk: command sizes, relocation counts, offsets, and surface allocation sizes need overflow and bounds scrutiny. `qxl_alloc_surf_ioctl()` computes `size = abs(stride) * height + abs(stride)` without explicit overflow checks. Relocation writes assume destination offsets are valid within mapped BO pages.

Test signals: Fuzz QXL ioctls with invalid handles, bad pointers, high relocation counts, oversized command sizes, invalid update rectangles, negative stride surface allocation, and interrupted command-ring waits; run normal xf86-video-qxl acceleration paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_irq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_irq.c

Purpose: This file installs the QXL IRQ handler and dispatches host interrupt events to wait queues, release garbage collection, and monitor-config work.

Important APIs, types, and functions: `qxl_irq_init()` initializes wait queues, work item, atomic counters, requests the shared PCI IRQ, and enables `QXL_INTERRUPT_MASK`. `qxl_irq_handler()` handles display, cursor, I/O command, error, and client monitor config interrupts. `qxl_client_monitors_config_work_func()` calls into display monitor parsing.

Control flow: The IRQ handler atomically exchanges `ram_header->int_pending` with zero, returns `IRQ_NONE` if no bits were pending, increments counters, wakes display/cursor/I/O waiters, schedules release collection on display interrupts, schedules monitor config work on monitor interrupts, re-enables the interrupt mask, and notifies the host that IRQ state was updated.

State and persistence: Maintains atomic IRQ counters, `irq_received_error`, wait queues, and `client_monitors_config_work`. Host interrupt state lives in the shared RAM header and is cleared by the handler.

Dependencies and integration points: Depends on PCI IRQs, QXL RAM header, wait queues used by `qxl_cmd.c`, garbage collection, and monitor config reading in `qxl_display.c`. Initialized during `qxl_device_init()` before async memslot I/O commands.

Risks: `request_irq()` failure returns `1` rather than the exact negative error code. Error interrupts only warn and increment a counter; reset recovery is TODO. Correct ordering between clearing pending bits, re-enabling masks, and host notification is critical.

Test signals: Generate display/cursor/io interrupts under draw/cursor/update traffic; trigger SPICE monitor hotplug; inspect debugfs IRQ counters; test shared IRQ behavior; simulate request_irq failure if possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_kms.c

Purpose: Despite the name, this file performs low-level QXL device initialization and teardown: PCI BAR mapping, ROM validation, TTM initialization, RAM header/ring setup, memslot programming, and final cleanup.

Important APIs, types, and functions: `qxl_device_init()`, `qxl_device_fini()`, `qxl_reinit_memslots()`, `qxl_check_device()`, `setup_slot()`, `setup_hw_slot()`, and the GC work function.

Control flow: Init stores DRM drvdata, initializes mutexes/GEM, records BAR bases, creates write-combining mappings for VRAM and surface RAM, ioremaps ROM, validates ROM magic and device info, initializes BO/TTM, maps the RAM header, creates command/cursor/release ring wrappers over RAM header ring storage, initializes release and surface IDRs/locks, resets the device, installs IRQs, programs main and surface memslots, and initializes GC work. Fini releases current release BOs, asks host to free resources, waits briefly for release count to drain, flushes GC work, evicts surfaces and VRAM, finalizes GEM/TTM, frees rings/mappings, and unmaps ROM/RAM.

State and persistence: Initializes nearly all persistent `qxl_device` fields: resource bases/sizes, mappings, ROM/RAM pointers, ring wrappers, IDRs, locks, memslot metadata, and work structs. Host-visible device state is reset during init and partially rebuilt during resume through memslot reinitialization.

Dependencies and integration points: Called by PCI probe/release in `qxl_drv.c`; depends on PCI BAR layout, io_mapping, ioremap_wc, QXL protocol ROM/RAM layout, TTM/object init, IRQ init, command helpers, and memslot high-bit address encoding.

Risks: BAR selection for surface RAM falls back from 64-bit BAR 4 to 32-bit BAR 1; mapping failures must clean up in exact reverse order. `gc_work.func` is used as an initialization-complete guard. Fini waits only one second for release count to drain before eviction, so delayed host completion can expose cleanup races.

Test signals: Probe on QXL devices with 64-bit and 32-bit surface BARs; invalid ROM magic; forced mapping/ring allocation failures; suspend/resume memslot rebuild; unload with outstanding releases; TTM debugfs memory manager visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_kms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_object.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_object.c

Purpose: This file implements QXL BO creation, placement selection, mapping, pinning, reference management, surface-ID checks, and full VRAM/surface eviction helpers.

Important APIs, types, and functions: `qxl_bo_create()`, `qxl_ttm_placement_from_domain()`, `qxl_bo_pin()/unpin()`, `qxl_bo_pin_locked()/unpin_locked()`, `qxl_bo_pin_and_vmap()`, `qxl_bo_vmap_locked()`, `qxl_bo_vunmap_locked()`, `qxl_bo_kmap_atomic_page()`, `qxl_bo_kunmap_atomic_page()`, `qxl_bo_ref()/unref()`, `qxl_bo_check_id()`, `qxl_surf_evict()`, and `qxl_vram_evict()`.

Control flow: BO creation allocates a QXL BO, initializes embedded GEM, chooses TTM placements from domain, initializes a reserved TTM BO, optionally pins it, and returns it unreserved. Mapping functions maintain `kptr` and `map_count` for vmap state, while atomic page mapping uses write-combining io mappings for VRAM/surface memory and falls back to vmap for system memory. `qxl_bo_check_id()` lazily allocates and creates a host surface for surface-domain BOs.

State and persistence: Per-BO state includes TTM resource placement, placement arrays, map state, pin count, surface metadata, `surface_id`, `hw_surf_alloc`, and optional shadow pointer. Device state includes GEM object list mutations and global memory managers evicted by helper functions.

Dependencies and integration points: Used throughout QXL display, draw, image, release, ioctl, PRIME, and KMS code. Depends on TTM, DRM GEM object funcs, io_mapping, QXL command surface creation, and the object header inline reserve helpers.

Risks: Mapping fallback calls `qxl_bo_vmap_locked()` and later unmaps in `qxl_bo_kunmap_atomic_page()`; callers must hold reservation where required. `qxl_bo_create()` returns directly after failed `ttm_bo_init_reserved()` without releasing the initialized GEM object, which should be audited. Surface creation on validation can fail after assigning an ID, requiring cleanup scrutiny.

Test signals: BO allocation in VRAM, surface, and CPU domains; pin/vmap nesting and map_count behavior; eviction of surface BOs during TTM moves; PRIME vmap paths; forced allocation/TTM validation failures; lockdep with reservation assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_object.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_object.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_object.h

Purpose: This header declares QXL BO helper APIs and provides inline reservation wrappers.

Important APIs, types, and functions: Inline `qxl_bo_reserve()`, `qxl_bo_unreserve()`, and `qxl_bo_size()` wrap TTM reservation and size access. The header declares BO creation, pinning, mapping, reference, placement, and QXL BO type-check helpers implemented in `qxl_object.c`.

Control flow: The only executable logic is inline reservation: it calls `ttm_bo_reserve()` interruptibly, logs non-restart failures, and returns the error. Unreserve directly calls `ttm_bo_unreserve()`.

State and persistence: No state is owned by the header; it manipulates per-BO TTM reservation state through inline helpers.

Dependencies and integration points: Included by most QXL C files that need BO access. It depends on `qxl_drv.h`, DRM device access from `bo->tbo.base.dev`, and TTM reservation semantics.

Risks: Because reservation is exposed as an inline helper, all callers share the same blocking behavior (`interruptible=true`, no deadlock ctx). Misuse inside already-reserved paths would deadlock; locked variants in `qxl_object.c` must be used when the reservation is already held.

Test signals: Compile all QXL files after prototype changes; lockdep for double reservations; static analysis for unbalanced reserve/unreserve and pin/unpin paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_object.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_prime.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_prime.c

Purpose: This file provides minimal PRIME/dma-buf hooks for QXL GEM objects, intentionally disabling cross-driver sharing while allowing local pin and vmap operations.

Important APIs, types, and functions: `qxl_gem_prime_pin()`, `qxl_gem_prime_unpin()`, `qxl_gem_prime_get_sg_table()`, `qxl_gem_prime_import_sg_table()`, `qxl_gem_prime_vmap()`, and `qxl_gem_prime_vunmap()`.

Control flow: Pin/unpin convert GEM to `qxl_bo` and call locked BO pin helpers. SG-table export and import return `-ENOSYS`, reflecting the comment that no other driver should share buffers with this virtual device. Vmap/vunmap call locked QXL BO map helpers.

State and persistence: No independent state. The functions alter BO pin count and map count/kptr through object helpers.

Dependencies and integration points: Hooked through `qxl_object_funcs` and the DRM driver `.gem_prime_import_sg_table`. Depends on callers holding the required reservation for locked pin/map operations.

Risks: The PRIME helpers use locked BO helpers directly; if DRM core invokes them without the BO reservation held, reservation assertions or races are possible. Returning `-ENOSYS` for sharing is intentional but limits dma-buf interoperability.

Test signals: PRIME import/export attempts should fail cleanly; local vmap/vunmap should maintain map_count; pin/unpin under dma-buf style paths should pass lockdep/reservation assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_prime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_release.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_release.c

Purpose: This file manages QXL release objects, which are host-completed command payloads represented as DMA fences and backed by suballocated pinned release BOs.

Important APIs, types, and functions: `qxl_alloc_release_reserved()`, `qxl_alloc_surface_release_reserved()`, `qxl_release_list_add()`, `qxl_release_reserve_list()`, `qxl_release_backoff_reserve_list()`, `qxl_release_fence_buffer_objects()`, `qxl_release_map()/unmap()`, `qxl_release_from_id_locked()`, and `qxl_release_free()`.

Control flow: Release allocation creates an IDR entry and sequence number, increments release count, suballocates a fixed-size slot from a current release BO by type, adds the BO to the release list, writes the release ID into the mapped payload, and returns it reserved for command construction. Reservation uses `drm_exec` to lock all involved BOs and validates them, including lazy QXL surface ID creation. Fencing initializes a DMA fence and attaches it to all BO reservations. Free removes the release from IDR, deallocates deferred surface IDs, frees BO refs, signals/drops the fence if initialized, or directly frees the release otherwise.

State and persistence: Persistent state includes `release_idr`, `release_seqno`, `release_count`, per-type `current_release_bo[]` and offsets, per-release BO lists, DMA fence state, and optional `surface_release_id`. Release payloads live in pinned VRAM BOs until host completion.

Dependencies and integration points: Used by command, display, draw, image, ioctl, and surface paths. Depends on DRM exec, DMA fences, TTM reservations, QXL BO mapping, command release-ring completion, and surface ID deallocation.

Risks: Release BO suballocation and destroy-surface command pairing are delicate; destroy releases can share the create release BO at offset `+64`. If a pushed command never returns, fences and release IDs can leak until cleanup. `qxl_fence_wait()` notifies OOM while waiting, coupling fence waits to host pressure behavior.

Test signals: Draw/cursor/surface release completion, chained release-ring IDs, fence wait and timeout behavior, allocation rollover across release BO pages, surface create/destroy release pairing, and forced host OOM notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_release.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_ttm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_ttm.c

Purpose: This file implements QXL's TTM memory manager integration for system memory, VRAM, and surface RAM.

Important APIs, types, and functions: `qxl_ttm_init()`, `qxl_ttm_fini()`, `qxl_ttm_io_mem_reserve()`, `qxl_ttm_debugfs_init()`, and TTM device callbacks including `qxl_evict_flags()`, `qxl_ttm_tt_create()`, `qxl_bo_move_notify()`, `qxl_bo_move()`, and delete-memory notification.

Control flow: TTM init creates a `ttm_device`, initializes a VRAM range manager sized by `rom->ram_header_offset / PAGE_SIZE`, initializes a private surface-memory range manager sized by surface BAR pages, and logs memory sizes. Move notification evicts host surfaces before BOs leave `TTM_PL_PRIV`; move handles null/system transitions and otherwise uses memcpy moves after waiting. I/O memory reserve maps VRAM and surface resources to write-combined bus offsets.

State and persistence: Persistent memory-manager state lives in `qdev->mman.bdev` and its VRAM/PRIV range managers. BO moves can clear host surface allocation state through eviction.

Dependencies and integration points: Called from QXL low-level init/fini and object init/fini. Depends on TTM range managers, QXL BO type checks, surface eviction command path, PCI BAR base addresses, and DRM anon inode/vma offset manager.

Risks: Surface eviction during TTM moves must happen before memory disappears from host visibility. VRAM manager size excludes RAM header and uses surface0 memory assumptions. Failed second manager init does not unwind the first manager/device in this function, which cleanup paths should audit.

Test signals: BO moves between VRAM/PRIV/SYSTEM, eviction under memory pressure, debugfs range managers, mmap bus offsets, initialization failure injection, and surface BO migration while commands are pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_ttm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/Kconfig

Purpose: This Kconfig file exposes the legacy Radeon DRM/KMS driver and optional userptr support.

Important APIs, types, and functions: `DRM_RADEON` is a tristate depending on `DRM`, `PCI`, and `AGP || !AGP`. It selects firmware loading, DRM/KMS/display helpers, TTM/DRM_EXEC, framebuffer I/O helpers, sound HDA component integration, power supply, hwmon, backlight, interval trees, I2C/algobit, and ACPI video/WMI dependencies when applicable. `DRM_RADEON_USERPTR` selects `MMU_NOTIFIER`.

Control flow: Build-time only. Enabling `DRM_RADEON` includes the Radeon driver object list; enabling userptr forces full user pointer invalidation support through MMU notifier.

State and persistence: No runtime state. The selected dependencies determine compiled-in feature support for firmware, memory management, display, audio, power, and ACPI integration.

Dependencies and integration points: Integrates the Radeon driver with PCI/AGP, DRM KMS, TTM, display helpers, fbdev emulation, HDA audio, power/hwmon/backlight, I2C, and ACPI subsystems.

Risks: Select chains are broad; changing them can produce missing symbols or feature regressions on ACPI/x86, audio, backlight, or userptr configurations. The userptr option changes MMU notifier dependency and memory invalidation behavior.

Test signals: Build matrix for built-in/module, AGP enabled/disabled, ACPI x86/non-x86, fbdev emulation, HDA, and userptr; boot on representative Radeon ASICs and verify firmware loading/display/audio/power hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/Makefile

Purpose: This Makefile defines how the Radeon DRM driver and its generated register-safety headers are built.

Important APIs, types, and functions: It builds host tool `mkregtable`, generates `*_reg_safe.h` files from `reg_srcs/%`, declares per-object dependencies on generated headers, and composes `radeon-y` from core, ASIC, KMS, memory, command submission, display, power-management, audio, DMA, UVD, VCE, VM, and optional ACPI/VGA switcheroo objects.

Control flow: Kbuild first builds `mkregtable`, generates register safe-list headers through `if_changed,mkregtable`, then compiles object files that depend on those headers. `obj-$(CONFIG_DRM_RADEON) += radeon.o` links the aggregate module/built-in.

State and persistence: No runtime state. Generated headers persist in the build output tree and affect command submission/register validation code.

Dependencies and integration points: Tied to Radeon Kconfig, Kbuild host programs, generated register source files, and all Radeon subsystem translation units. Optional objects are gated by `CONFIG_MMU_NOTIFIER`, `CONFIG_VGA_SWITCHEROO`, and `CONFIG_ACPI`.

Risks: Missing generated-header dependencies can cause stale or absent register safety tables. The large object list must stay synchronized with source files and feature config. Host tool failures break builds before driver compilation.

Test signals: Clean and incremental builds; touch `reg_srcs/*` and confirm regeneration; build with optional configs toggled; verify `radeon.o` contains expected ASIC/power/video/audio objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ObjectID.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ObjectID.h

Purpose: This header defines Radeon/ATOM BIOS graphics object IDs for GPUs, encoders, connectors, routers, and generic objects, plus macros for composing BIOS object enum IDs.

Important APIs, types, and functions: Defines object type values, encoder object IDs, connector object IDs, router/generic IDs, enum IDs, object bit masks/shifts, `CONSTRUCTOBJECTFAMILYID()`, and many `*_ENUM_ID*` constants such as internal LVDS/TMDS/DAC/UNIPHY encoders and DVI/VGA/HDMI/DisplayPort/eDP/MXM connectors.

Control flow: No executable control flow. Driver code includes these macros to decode ATOM BIOS object tables and map BIOS-described display topology to DRM encoder/connector objects.

State and persistence: No runtime state. Numeric constants are ABI-like vocabulary shared with BIOS table contents and must remain stable.

Dependencies and integration points: Used by Radeon ATOM BIOS parsing and display/connector setup code. Values correspond to AMD internal ObjectID definitions and BIOS object table encodings.

Risks: Numeric changes break BIOS parsing for real hardware. Some aliases intentionally share values, such as ALMOND and NUTMEG object IDs, and comments document shared DAC/TV/LVDS/eDP cases. `_X86_` packing pragmas are legacy and should not be casually altered.

Test signals: Parse ATOM BIOS object tables across Radeon generations; compare decoded connector/encoder topology with expected board outputs; compile all architectures that include the header; regression-test HDMI/DP/eDP/LVDS/MXM mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ObjectID.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atom-bits.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atom-bits.h

Purpose: This header provides small helpers and macros for reading little-endian byte, word, and dword values from an ATOM BIOS image.

Important APIs, types, and functions: Inline functions `get_u8()`, `get_u16()`, and `get_u32()` read from a BIOS byte pointer. Macros `U8/U16/U32` access `ctx->ctx->bios`, `CU8/CU16/CU32` access `ctx->bios`, and `CSTR()` returns a char pointer into `ctx->bios`.

Control flow: Reads are simple byte-indexed loads composed into little-endian integers. There is no bounds checking; callers provide valid BIOS offsets and context shape.

State and persistence: No owned state. The functions read immutable or caller-managed BIOS memory.

Dependencies and integration points: Used by Radeon ATOM interpreter/parser code. The macros assume specific local variable names and nested context structure, making this a parser-internal header rather than a generic utility.

Risks: Lack of bounds checking means malformed BIOS offsets can read outside the mapped image unless callers validate table sizes. The macros depend on implicit `ctx` names and structure layout. Endianness is hard-coded little-endian by byte composition, which is correct for ATOM BIOS but must not be replaced with native casts.

Test signals: ATOM BIOS parser tests on valid and malformed images; fuzz table offsets; build on big-endian and little-endian architectures; static analysis for unchecked offsets before macro use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atom-bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atom-names.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atom-names.h

Purpose: This header provides debug-only string tables for ATOM BIOS operation, table, and I/O-space names.

Important APIs, types, and functions: Under `ATOM_DEBUG`, it defines `ATOM_OP_NAMES_CNT` with `atom_op_names[]`, `ATOM_TABLE_NAMES_CNT` with `atom_table_names[]`, and `ATOM_IO_NAMES_CNT` with `atom_io_names[]`. Without `ATOM_DEBUG`, all counts are zero and no arrays are emitted.

Control flow: Build-time conditional only. Debug code can index these arrays for readable trace/log output when ATOM interpreter debugging is enabled.

State and persistence: Static string tables are compile-time read-only diagnostic data. No runtime driver state is modified.

Dependencies and integration points: Includes `atom.h` for ATOM opcode/table definitions and is used by Radeon ATOM parser/interpreter debug paths.

Risks: Counts must match array contents and opcode/table numbering. Debug names can become stale if ATOM opcodes or table indices change. Arrays are `char *` rather than `const char *`, which is historically common but less strict.

Test signals: Build with and without `ATOM_DEBUG`; enable ATOM debug traces and verify opcode/table names line up with interpreted BIOS commands; bounds-check any debug indexing against the count macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atom-names.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atom-types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atom-types.h

Purpose: This header defines ATOM BIOS integer aliases and an endianness flag for Radeon ATOM parsing.

Important APIs, types, and functions: Provides `USHORT`, `ULONG`, and `UCHAR` typedefs for fixed-width integer types and sets `ATOM_BIG_ENDIAN` to `1` or `0` depending on `__BIG_ENDIAN`.

Control flow: Build-time preprocessor branching only. Consumers use the flag to adapt ATOM parser behavior for host endianness.

State and persistence: No runtime state. The definitions shape compilation of ATOM-related code.

Dependencies and integration points: Included by ATOM parser and BIOS table headers; depends on Linux integer types and the compiler/architecture defining `__BIG_ENDIAN` where appropriate.

Risks: Legacy aliases can obscure exact widths if included with other platform headers defining similar names. Endianness detection must match the kernel's architecture defines; incorrect value would corrupt BIOS interpretation on big-endian systems.

Test signals: Compile Radeon on big-endian and little-endian targets; parse known ATOM BIOS images and verify multi-byte fields through `atom-bits.h` readers; run sparse/build checks for typedef conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atom-types.h -->
