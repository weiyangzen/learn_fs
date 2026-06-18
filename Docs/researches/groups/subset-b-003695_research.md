# Research: subset-b-003695

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_gem.c

Purpose: Implements OMAPDRM GEM buffer objects, covering allocation, mmap fault handling, DMM/TILER remapping, PRIME export/import backing, page pinning, cache synchronization, debugfs description, and init/deinit of the user-GART used for tiled userspace mappings.

Important APIs/types/functions: `struct omap_gem_object` extends `drm_gem_object` with flags, dimensions, roll offset, lock, DMA address, pin count, sg table, TILER block, page array, DMA page addresses, and kernel vaddr. Internal user-GART types hold small page-aligned TILER blocks for faulting tiled buffers into CPU mappings. Public functions include `omap_gem_new`, `omap_gem_new_dmabuf`, `omap_gem_new_handle`, `omap_gem_dumb_create`, `omap_gem_dumb_map_offset`, `omap_gem_pin`, `omap_gem_unpin`, `omap_gem_get_sg`, `omap_gem_put_sg`, `omap_gem_mmap_offset`, `omap_gem_mmap_size`, `omap_gem_flags`, tiled address helpers, PM resume, and debugfs describe helpers.

Control flow: Object construction validates cache/tiled flags, chooses shmem, contiguous DMA, or imported dmabuf backing, aligns tiled dimensions, initializes GEM, optionally allocates DMA write-combined memory, and adds the object to `priv->obj_list`. Fault handling attaches shmem pages, then maps either direct PFNs for linear objects or pins a temporary user-GART entry for tiled objects. Pinning detects non-contiguous buffers and, for scanout with DMM, reserves and pins a TILER block to create a contiguous DMA aperture. SG export pins first, synchronizes dirty cached pages for DMA, then builds either one/tiled-row scatterlist entries from the aperture or page-sized entries from shmem pages.

State and persistence: State is in memory only: object lists, per-object mutex-protected page/DMA/pin/TILER state, and `priv->usergart`. Cached shmem coherence is tracked with `dma_addrs[i] == 0` meaning CPU-visible dirty page and nonzero meaning DMA-mapped. PM resume repins existing TILER blocks.

Dependencies and integration: Depends on DRM GEM, VMA manager, shmem, DMA mapping, PRIME, TILER/DMM helpers, `omap_drm_private`, and framebuffer/plane users that pin scanout buffers. `omap_gem_object_funcs` wires free/export/mmap/vm_ops into DRM core.

Risks: Pin error path sets `pin_cnt` before page/TILER failures and relies on later cleanup; tiled mmap uses a fixed two-entry user-GART and stack `pages[64]`; non-coherent cache management invalidates mappings and is sensitive to missed `omap_gem_dma_sync_buffer`; imported non-contiguous dmabufs require DMM; object destruction warns but cannot recover from leaked pins.

Test signals: Exercise dumb buffer create/map/mmap, PRIME export/import of contiguous and non-contiguous buffers, scanout with and without DMM, tiled mmap page faults, fbdev roll, suspend/resume with pinned TILER blocks, debugfs object listing, and error injection for DMA map/TILER reserve failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_gem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_gem.h

Purpose: Declares the OMAPDRM GEM object management interface used by the driver core, framebuffer, plane, fbdev, PRIME, PM, and debugfs code.

Important APIs/types/functions: Forward-declares DRM, dma-buf, page, seq_file, and VM types, plus `union omap_gem_size`. Exports init/deinit, optional PM resume, debugfs describe helpers, object constructors, dumb buffer callbacks, mmap size/offset helpers, PRIME import/export, roll, CPU/DMA synchronization, pin/unpin, page get/put, flag and tiled address helpers, and SG table get/put.

Control flow: This header is the contract between `omap_gem.c`, `omap_gem_dmabuf.c`, and other OMAPDRM units. Callers create GEM handles, pin buffers before scanout/DMA, query tiled geometry, and release pins/SG references through the paired APIs.

State and persistence: No storage is defined here, but the API exposes operations that mutate per-object pin/page/cache/TILER state and driver-wide DMM user-GART state.

Dependencies and integration: Included through `omap_drv.h` users and implemented by `omap_gem.c` and `omap_gem_dmabuf.c`; visible to DRM driver callbacks for dumb buffers and PRIME.

Risks: Many functions assume the passed `drm_gem_object` is an OMAP GEM object. Callers must balance `omap_gem_pin`/`omap_gem_unpin` and `omap_gem_get_sg`/`omap_gem_put_sg`, and tiled helper use is valid only for tiled pinned objects.

Test signals: Build coverage with and without `CONFIG_PM`, `CONFIG_DEBUG_FS`, and `CONFIG_DRM_FBDEV_EMULATION`; runtime tests should verify every declared paired API has balanced use in framebuffer, PRIME, and fbdev paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_gem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_gem_dmabuf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_gem_dmabuf.c

Purpose: Implements OMAPDRM PRIME/dma-buf export and import glue around the GEM memory manager.

Important APIs/types/functions: `omap_dmabuf_ops` supplies `map_dma_buf`, `unmap_dma_buf`, `release`, `begin_cpu_access`, `end_cpu_access`, and `mmap`. Public entry points are `omap_gem_prime_export` and `omap_gem_prime_import`.

Control flow: Export fills `DEFINE_DMA_BUF_EXPORT_INFO` using `omap_gem_mmap_size`, object reservation, OMAP dma-buf ops, and `drm_gem_dmabuf_export`. Attachment mapping calls `omap_gem_get_sg`; unmapping calls `omap_gem_put_sg`. CPU access rejects tiled buffers, then ensures backing pages exist. Import short-circuits self-import from the same device by taking a GEM reference; external imports attach to the dma-buf, map the attachment for `DMA_TO_DEVICE`, create an OMAP dmabuf-backed GEM object, and store the import attachment.

State and persistence: Exported dma-bufs hold the GEM object in `priv`; imported objects retain the attachment and SG table until GEM destruction via `drm_prime_gem_destroy`.

Dependencies and integration: Depends on DMA-BUF namespace, DRM PRIME helpers, `omap_gem_get_sg`, `omap_gem_new_dmabuf`, and GEM mmap helpers. The object funcs in `omap_gem.c` point `.export` here.

Risks: CPU access to tiled buffers is not implemented and returns `-ENOMEM`, which may surprise generic dma-buf users. Import maps attachments `DMA_TO_DEVICE`; bidirectional users depend on subsequent cache sync behavior. Error paths must balance `dma_buf_attach`, `get_dma_buf`, map, detach, and put operations.

Test signals: PRIME self-import should return the same GEM object with increased refcount; external import should reject non-contiguous buffers when DMM is unavailable; dma-buf mmap should use the OMAP GEM fault path; begin/end CPU access should fail for tiled buffers and succeed for linear shmem buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_gem_dmabuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_irq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_irq.c

Purpose: Manages DISPC interrupt installation, vblank/framedone toggling, synchronous waiters, and IRQ dispatch into CRTC error/vblank/framedone handlers.

Important APIs/types/functions: `struct omap_irq_wait` tracks wait queue, mask, and countdown. Public functions include `omap_irq_wait_init`, `omap_irq_wait`, `omap_irq_enable_framedone`, `omap_irq_enable_vblank`, `omap_irq_disable_vblank`, `omap_drm_irq_install`, and `omap_drm_irq_uninstall`.

Control flow: `omap_drm_irq_install` initializes wait state, builds a base IRQ mask for OCP errors, plane FIFO underflows, and manager sync-lost events, clears stale status, and registers `omap_irq_handler`. Vblank/framedone helpers update `priv->irq_mask` under `wait_lock` and rewrite DISPC IRQ enable bits together with all active waiter masks. The handler reads and clears status, flushes the posted write, dispatches per-pipe vsync/sync-lost/framedone events, logs OCP and underflow errors, decrements matching waiters, and wakes their queues.

State and persistence: Runtime state is `priv->irq_mask`, `priv->wait_list`, `priv->wait_lock`, and `priv->irq_enabled`. Wait objects are allocated per wait and freed after timeout or completion.

Dependencies and integration: Uses DISPC IRQ accessors, DRM vblank core, OMAP CRTC callbacks, and `omap_drm_private` pipe/plane bookkeeping.

Risks: `omap_irq_wait_init` does not check `kzalloc_obj` failure before dereference. `omap_irq_wait` returns `-1` instead of a standard errno on timeout. IRQ mask updates rely on callers respecting locking and DISPC runtime constraints. Underflow logging is ratelimited and only reports enabled underflow bits.

Test signals: Verify vblank enable/disable refcounting through DRM, framedone enable flow for atomic commits, waiter timeout and completion, IRQ uninstall idempotence, OCP and FIFO-underflow ratelimited logging, and multi-pipe dispatch to the correct CRTC index.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_irq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_irq.h

Purpose: Declares the OMAPDRM IRQ interface for vblank, framedone, install/uninstall, and masked interrupt waits.

Important APIs/types/functions: Exposes opaque `struct omap_irq_wait`, vblank/framedone enable functions, IRQ install/uninstall functions, and wait init/wait functions.

Control flow: Consumers initialize a wait object for an IRQ mask and count, then call `omap_irq_wait` with a timeout. DRM core calls vblank hooks, and driver init/teardown calls install/uninstall.

State and persistence: No direct state; declared functions manipulate `omap_drm_private` interrupt masks and wait lists.

Dependencies and integration: Included by CRTC/driver code that needs DISPC interrupt services. Depends only on Linux integer types and forward-declared DRM types.

Risks: Opaque wait object lifetime is owned by `omap_irq_wait`; callers must not reuse or free it. Timeout return is implementation-specific `-1`.

Test signals: Header compile tests across modules, plus caller audits for balanced `omap_irq_wait_init`/`omap_irq_wait` use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_overlay.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_overlay.c

Purpose: Owns allocation and lifecycle of OMAP hardware overlays and their assignment to DRM planes during atomic state validation.

Important APIs/types/functions: `omap_hwoverlays_init`, `omap_hwoverlays_destroy`, `omap_overlay_assign`, `omap_overlay_release`, and `omap_overlay_update_state`. Internal helpers map overlay IDs to names, find a free overlay with required caps and fourcc support, allocate overlay records, and free them.

Control flow: Initialization queries DISPC overlay count and capabilities and stores `struct omap_hw_overlay` entries in `priv->overlays`. During atomic check, planes call `omap_overlay_assign` against the transaction-global `hwoverlay_to_plane` map; dual-overlay planes request a second overlay and roll back on failure. Release clears the same global map. Atomic update/disable calls `omap_overlay_update_state` on previously held overlays, disabling hardware overlays no longer present in the committed global state.

State and persistence: Persistent state is `priv->overlays[]` and `priv->num_ovls`; per-transaction state is `omap_global_state->hwoverlay_to_plane`.

Dependencies and integration: Depends on DISPC overlay capability and format queries, OMAP global atomic state, and `omap_plane.c` for assignment/release calls.

Risks: Hardware overlay allocation is first-fit and can fail due to transaction ordering when formats/caps are constrained. Dual-overlay assignment must keep z-order and right/left split consistent with plane update logic. `omap_overlay_update_state` assumes a valid existing global state.

Test signals: Atomic commits with scaling, format changes, invisible planes, dual-wide planes, caps mismatch, and overlay exhaustion. Confirm disabled old overlays are turned off after reassignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_overlay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_overlay.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_overlay.h

Purpose: Defines the hardware overlay representation and declares overlay management APIs used by plane and driver setup code.

Important APIs/types/functions: `struct omap_hw_overlay` stores index, name, DISPC plane ID, and caps. Declares init/destroy, assign/release, and state-update functions.

Control flow: Planes hold pointers to overlay objects in their private atomic state, while global atomic state maps overlay index to DRM plane for the next commit.

State and persistence: No storage here; structure instances are allocated by `omap_overlay.c` and referenced by plane state.

Dependencies and integration: Depends on OMAP DSS enum types from broader driver headers and DRM atomic plane concepts.

Risks: Header forward declarations omit some concrete types locally and rely on include ordering through `omap_drv.h`. Overlay pointers in duplicated plane state are shallow references and require stable overlay object lifetime until driver teardown.

Test signals: Build coverage and atomic state duplication/destruction tests that ensure overlay pointers remain valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_overlay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_plane.c

Purpose: Implements OMAP DRM universal planes, atomic validation/update/disable, framebuffer pinning, overlay assignment, and plane properties.

Important APIs/types/functions: `struct omap_plane_state` extends `drm_plane_state` with main and right overlays. `struct omap_plane` stores the DISPC plane ID. Public functions are `omap_plane_init`, `omap_plane_install_properties`, and `is_omap_plane_dual_overlay`.

Control flow: `prepare_fb` pins the framebuffer after GEM helper preparation; cleanup unpins. Atomic check obtains global overlay state, validates scaling and CRTC bounds, detects need for scaling caps, rejects unsupported rotation, handles too-wide planes by requesting a right overlay, and assigns/reassigns hardware overlays when caps, format, or dual-overlay needs change. Atomic update builds `omap_overlay_info` from DRM state and framebuffer scanout data, then programs and enables one or two DISPC overlays. Atomic disable resets rotation/zpos defaults and updates old overlay state so unused hardware gets disabled.

State and persistence: Plane state carries overlay pointers across commits. Plane properties include rotation when DMM is present, zorder, alpha, blend mode, and optional YCbCr encoding/range. Framebuffer pin state is managed outside the plane in framebuffer/GEM code.

Dependencies and integration: Uses DRM atomic helpers, GEM prepare helpers, blend/color property helpers, framebuffer scanout helpers, overlay allocator, CRTC timing/channel helpers, and DISPC overlay setup/format capability APIs.

Risks: The max-size checks are coarse and final scaling limits may still fail in DISPC setup. Dual-overlay splitting depends on framebuffer scanout update generating matching left/right info and zorder+1. Negative CRTC positions and clipping are rejected rather than supported. Rotation requires DMM/TILER-backed framebuffer support.

Test signals: Atomic plane commits for primary and overlay planes, scaling up/down limits, YUV odd-width dual-overlay cases, rotation/reflection with DMM, alpha/blend/zpos properties, invisible-plane release, format reallocation, and DISPC setup failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_plane.h

Purpose: Declares the OMAP plane creation and common property helpers, plus a query for dual-overlay plane state.

Important APIs/types/functions: `omap_plane_init`, `omap_plane_install_properties`, and `is_omap_plane_dual_overlay`.

Control flow: Driver setup calls `omap_plane_init` per DISPC plane; CRTC setup can call `omap_plane_install_properties` to share rotation/zorder properties; framebuffer/CRTC paths can query dual-overlay state.

State and persistence: No storage; declared functions manipulate DRM plane objects and private OMAP plane state.

Dependencies and integration: Consumed by OMAP driver, CRTC, framebuffer, and overlay paths. Relies on DRM plane and mode object types.

Risks: `is_omap_plane_dual_overlay` assumes the state is an OMAP plane state. Header forward declaration for `struct drm_plane_state` is implicit through including contexts.

Test signals: Build and atomic tests that call the dual-overlay query only for OMAP planes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/tcm-sita.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/tcm-sita.c

Purpose: Provides the SiTA TILER container manager allocation algorithm for 1D and 2D slot reservation over a bitmap-backed container.

Important APIs/types/functions: `sita_init` constructs `struct tcm` and installs function pointers. Internal algorithms include `r2l_b2t_1d` for right-to-left/bottom-to-top 1D allocation, `l2r_t2b` for left-to-right/top-to-bottom aligned 2D allocation, `sita_reserve_1d`, `sita_reserve_2d`, `sita_free`, and `free_slots`.

Control flow: `sita_init` allocates a `tcm` plus bitmap, initializes dimensions and spinlock, and clears all slots. 1D reserve searches for a long enough free run, marks it, and converts the linear position to area coordinates. 2D reserve scans zero areas with alignment/offset constraints, checks row boundaries and subsequent row intersections, marks every row on success, and records the rectangle. Free converts an area back to start/width/height and clears bits.

State and persistence: Container state is in `tcm->bitmap`, protected by `tcm->lock`. The file has a static `mask[8]` scratch bitmap used under the same lock during 2D searches.

Dependencies and integration: Implements the function table declared in `tcm.h`; used by OMAP DMM/TILER code to reserve aperture slots for GEM and user-GART mappings.

Risks: Static `mask[8]` assumes slot stride fits that scratch size. The 2D allocator has an explicit TODO for overlapping 4K boundaries and FIXME for `slots_per_band > stride`. 1D search arithmetic around unsigned positions must avoid underflow. Allocation policy can fragment the bitmap.

Test signals: Reserve/free round trips for 1D and 2D areas, alignment and offset cases, full/fragmented containers, invalid zero dimensions, concurrent reserve/free under lock, and boundary cases at row ends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/tcm-sita.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/tcm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/tcm.h

Purpose: Defines the TILER container manager abstraction, area geometry helpers, and inline reserve/free/slice operations used by DMM/TILER code.

Important APIs/types/functions: `struct tcm_pt`, `struct tcm_area`, and `struct tcm` with reserve/free/deinit function pointers. Public inline helpers include `tcm_deinit`, `tcm_reserve_2d`, `tcm_reserve_1d`, `tcm_free`, `tcm_slice`, `tcm_area_is_valid`, `__tcm_is_in`, width/height/size helpers, `tcm_1d_limit`, and `tcm_for_each_slice`. `sita_init` is the concrete allocator constructor.

Control flow: Callers allocate a manager, reserve validated 1D or 2D areas through wrappers that set `area->is2d` and `area->tcm`, use geometry helpers to split or inspect areas, and call `tcm_free` to clear reservations and null the parent pointer.

State and persistence: `struct tcm` holds dimensions, LUT ID, y offset, lock, bitmap pointer, map size, and allocator callbacks. `struct tcm_area` persists reservation coordinates and parent pointer until freed.

Dependencies and integration: Implemented by `tcm-sita.c` and consumed by OMAP DMM/TILER block management. Uses Linux integer, bool, and spinlock types through including contexts.

Risks: Inline wrappers rely on caller-provided structures and assume width/height checks outside algorithms. `tcm_1d_limit` mutates an area in place. `__tcm_sizeof` returns `u16`, which can truncate very large slot counts. License block differs from neighboring GPL-only files and must remain respected.

Test signals: Compile all TILER users, validate area validity/slicing macros on multi-row 1D areas, test free idempotence on failed reserves, and verify size helpers on maximum container dimensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/tcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/Kconfig

Purpose: Defines the DRM panel framework menu and per-panel Kconfig symbols, dependencies, selected helper libraries, and user-facing descriptions.

Important APIs/types/functions: Top-level `DRM_PANEL` bool depends on `DRM`; `menu "Display Panels"` gates entries on `DRM && DRM_PANEL`. Listed symbols include the work-item panels such as `DRM_PANEL_ABT_Y030XX067A`, `DRM_PANEL_ARM_VERSATILE`, `DRM_PANEL_ASUS_Z00T_TM5P5_NT35596`, `DRM_PANEL_AUO_A030JTN01`, `DRM_PANEL_BOE_BF060Y8M_AJ0`, `DRM_PANEL_BOE_HIMAX8279D`, `DRM_PANEL_BOE_TD4320`, `DRM_PANEL_BOE_TH101MB31UIG002_28A`, and `DRM_PANEL_BOE_TV101WUM_LL2`, plus many other panel drivers.

Control flow: Kernel configuration selects panel drivers based on bus and support dependencies. SPI/regmap panels select `REGMAP_SPI` or `DRM_MIPI_DBI`; MIPI DSI panels depend on or select `DRM_MIPI_DSI`; many require `OF` and `BACKLIGHT_CLASS_DEVICE`; DSC/eDP panels select display helper libraries.

State and persistence: Kconfig symbols persist into `.config`, controlling object inclusion in the panel Makefile and module availability.

Dependencies and integration: Directly paired with `drivers/gpu/drm/panel/Makefile`. Symbol names must match `obj-$(CONFIG_...)` entries and source drivers.

Risks: Dependency mistakes surface as build failures or runtime probe gaps on platforms missing GPIO, regulator, backlight, DSI, SPI, syscon, or helper APIs. Help text contains some stale copy-paste descriptions, so it should not be used as a hardware authority without checking bindings/drivers.

Test signals: `make olddefconfig`, allmodconfig build coverage for panel drivers, dependency checks for each bus class, and symbol-to-Makefile consistency audits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/Makefile

Purpose: Maps DRM panel Kconfig symbols to built-in or modular object files.

Important APIs/types/functions: Contains one `obj-$(CONFIG_DRM_PANEL_...) += panel-... .o` entry per panel driver. Work-item entries map ABT, ARM Versatile, ASUS NT35596, AUO A030JTN01, BOE BF060, BOE Himax8279d, BOE TD4320, BOE TH101MB31IG002-28A, and BOE TV101WUM LL2 symbols to their objects.

Control flow: Kbuild includes an object when its Kconfig symbol is `y` or `m`, matching the driver registration macro used inside each source file.

State and persistence: No runtime state; build artifacts depend on `.config` and this mapping.

Dependencies and integration: Must stay in sync with `Kconfig`, source filenames, module names, and driver compatible tables.

Risks: A missing or mismatched object entry silently prevents a configured panel from building. Renames require synchronized Kconfig, Makefile, and source updates.

Test signals: allmodconfig/allyesconfig builds, script checks for every `DRM_PANEL_*` symbol having the expected object, and module load tests for selected panel drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-abt-y030xx067a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-abt-y030xx067a.c

Purpose: SPI/regmap DRM panel driver for Asia Better Technology Y030XX067A 320x480 DPI LCD panels.

Important APIs/types/functions: Defines register bit macros, `struct y030xx067a_info`, `struct y030xx067a`, `y030xx067a_init_sequence`, DRM panel funcs, SPI probe/remove, regmap config, display modes, and OF match data.

Control flow: Probe allocates a DPI `drm_panel`, initializes SPI regmap, reads match data, gets `power` regulator and reset GPIO, attaches optional OF backlight, and registers the panel. Prepare enables power, toggles reset, and writes the init register sequence. Enable sets `REG06_XPSAVE` and waits before backlight. Disable clears it; unprepare resets and disables power. `get_modes` duplicates 60 Hz and 50 Hz modes and sets bus format/flags.

State and persistence: Runtime state stores SPI, regmap, panel info, regulator, and reset GPIO. Register settings are reprogrammed on each prepare.

Dependencies and integration: Depends on SPI, REGMAP_SPI, GPIO, regulator, DRM panel, OF match data, media bus formats, and optional backlight phandle.

Risks: Any init sequence error aborts prepare and powers down. The panel has two modes but only marks preferred when there is exactly one, so neither mode is preferred here. Timing and register values are hardware-specific.

Test signals: SPI probe with compatible `abt,y030xx067a`, regmap write verification, reset polarity on hardware, mode enumeration for both refresh rates, backlight delay behavior, and remove path disable/unprepare idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-abt-y030xx067a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-arm-versatile.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-arm-versatile.c

Purpose: Platform DRM panel driver for ARM Versatile reference-design TFT panels detected through syscon CLCD identification registers.

Important APIs/types/functions: Defines SYS_CLCD and IB2 control bits, `struct versatile_panel_type`, `struct versatile_panel`, `versatile_panels[]`, DRM panel funcs, and platform probe.

Control flow: Probe obtains parent syscon regmap, reads `SYS_CLCD`, masks the panel ID, selects a matching panel descriptor, optionally finds the IB2 syscon for panels mounted on that board, and registers a DPI panel. Enable/disable update IB2 control bits when present. `get_modes` duplicates the detected panel mode and sets physical size and bus flags.

State and persistence: State stores detected panel type plus syscon regmaps. Hardware detection is performed at probe; no persistent storage is written beyond IB2 enable bits.

Dependencies and integration: Depends on OF platform device, MFD syscon/regmap, videomode helpers, and DRM panel. Integrates with ARM Versatile/RealView display controllers through a DPI panel abstraction.

Risks: Unknown IDs return `-ENODEV`, including the VGA/no-panel case. IB2 lookup failure is tolerated by treating it as absent. Register definitions are board-specific.

Test signals: Boot on Versatile AB/PB variants, syscon read failure paths, each supported ID mode, IB2 enable/disable bit updates, and connector mode dimensions/bus flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-arm-versatile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-asus-z00t-tm5p5-n35596.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-asus-z00t-tm5p5-n35596.c

Purpose: MIPI DSI DRM panel driver for the ASUS Z00T TM5P5 NT35596 1080x1920 video-mode panel.

Important APIs/types/functions: `struct tm5p5_nt35596`, reset/on/off helpers, prepare/unprepare, fixed mode, panel funcs, DCS backlight ops, DSI probe/remove, and OF match table.

Control flow: Probe gets `vdd`/`vddio` regulators, reset GPIO, configures four-lane RGB888 video burst DSI with low-power commands, creates a DCS backlight, registers the panel, and attaches to the DSI host. Prepare enables regulators, toggles reset, and sends a long vendor command sequence ending in sleep-out/display-on. Unprepare sends display-off/sleep-in commands, drops reset, and disables regulators. Backlight ops temporarily leave LPM to set/get DCS brightness.

State and persistence: Driver state holds panel, DSI device, two regulators, and reset GPIO. Brightness lives in panel DCS registers and backlight core state.

Dependencies and integration: Depends on DRM MIPI DSI, GPIO, regulators, backlight class, OF, and DRM panel mode helpers.

Risks: Command sequence failures accumulate through `mipi_dsi_multi_context`; prepare must clean up power on any error. Backlight get returns low 8 bits despite DCS 16-bit storage. DSI mode flag toggling around brightness is stateful.

Test signals: DSI attach/probe on matching DT, regulator/reset sequencing, prepare failure cleanup, display mode timing, DCS brightness set/get, and remove detach error logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-asus-z00t-tm5p5-n35596.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-auo-a030jtn01.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-auo-a030jtn01.c

Purpose: SPI/regmap DRM panel driver for AU Optronics A030JTN01 320x480 DPI LCD panels.

Important APIs/types/functions: Defines register masks for standby and blanking, `struct a030jtn01_info`, `struct a030jtn01`, prepare/unprepare/enable/disable/get_modes funcs, regmap readability helper, SPI probe/remove, and match tables.

Control flow: Probe sets SPI mode 3 and 3-wire, allocates a DPI panel, initializes regmap with readable/writeable register mask, obtains match data, regulator, reset GPIO, and optional backlight. Prepare enables power, toggles reset, performs a required dummy register read, programs vertical and horizontal blanking, and leaves the panel ready. Enable sets standby bit and waits for stability; disable clears it. `get_modes` exposes 60 Hz and 50 Hz modes plus RGB888 delta bus format.

State and persistence: Holds SPI, regmap, fixed panel info, regulator, reset GPIO, and optional backlight. Hardware registers are restored on each prepare.

Dependencies and integration: Depends on SPI, REGMAP_SPI, regulator/GPIO, DRM panel, media bus formats, and SPI/OF match data.

Risks: The unexplained dummy read is required for correct colors, so removing it can regress hardware. The register mask limits accessible registers. Two modes are exposed without a preferred bit because `num_modes != 1`.

Test signals: SPI 3-wire communication, dummy-read behavior on real hardware, blanking register writes, both mode timings, standby enable/disable, and power/reset failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-auo-a030jtn01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-bf060y8m-aj0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-bf060y8m-aj0.c

Purpose: MIPI DSI OLED panel driver for the BOE BF060Y8M-AJ0 5.99 inch 1080x2160 module using an SW43404-like controller.

Important APIs/types/functions: Defines supply enum, `struct boe_bf060y8m_aj0`, reset/on/off helpers, prepare/unprepare, fixed mode, DCS backlight ops, regulator initialization, DSI probe/remove, and OF match table.

Control flow: Probe validates and obtains five supplies, optional reset GPIO, configures four-lane RGB888 video sync-pulse DSI, marks `prepare_prev_first`, creates a DCS backlight, registers the panel, and attaches. Prepare enables ELVDD/ELVSS first, then VCC/VDDIO/VCI with delays, toggles reset, and sends DCS init/sleep-out/display-on. Unprepare sends display-off/sleep-in in high-speed mode, asserts reset, and bulk-disables supplies. Backlight writes DCS brightness.

State and persistence: State stores DSI, regulators, reset GPIO, and DRM panel/backlight. Supply voltage/current constraints are checked/set at probe but not persisted by this driver beyond regulator framework state.

Dependencies and integration: Depends on MIPI DSI, backlight class, regulator framework, GPIO, DRM panel, and video MIPI DCS definitions.

Risks: Power sequence is strict and uses negative ELVSS represented as positive regulator voltage magnitude. `regulator_is_supported_voltage` returning zero is treated as failure, which assumes unsupported ranges are fatal. Optional reset GPIO is still used unconditionally in reset/off paths if absent, relying on gpiod handling NULL safely.

Test signals: Regulator constraint handling, ordered power-up/down with delays, DSI command success, DCS brightness, fixed mode at 1080x2160, and failure cleanup after each supply or DSI step.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-bf060y8m-aj0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-himax8279d.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-himax8279d.c

Purpose: Descriptor-driven MIPI DSI panel driver for BOE Himax8279d 8-inch and 10-inch 1200x1920 TFT LCD modules.

Important APIs/types/functions: `struct panel_cmd`, `struct panel_desc`, `struct panel_info`, `send_mipi_cmds`, panel prepare/enable/disable/unprepare/get_modes functions, shared `default_display_mode`, two large on-command arrays, two panel descriptors, OF match data, and DSI probe/remove.

Control flow: Probe selects the descriptor by compatible string, copies DSI mode flags/format/lanes, gets `pp18`, `pp33`, and `enable` GPIOs, attaches OF backlight, registers the panel, and attaches to the DSI host. Prepare powers GPIO rails in sequence, toggles enable reset, sends every descriptor command as a two-byte DCS write buffer, exits sleep mode, waits, sets display on, and waits again. Enable redundantly waits and sends display on. Disable sends display off; unprepare sends display off, sleep in, waits, and drops GPIOs.

State and persistence: State holds panel, DSI link, descriptor, and three GPIOs. Command tables encode all panel tuning and are static.

Dependencies and integration: Depends on DRM MIPI DSI, GPIO, OF match data, DRM panel, and optional backlight binding.

Risks: `send_mipi_cmds` ignores its `cmds` length argument and uses `desc->on_cmds_num`; descriptor counts must match arrays exactly. GPIOs use non-cansleep setters, so backing controllers must be atomic-safe. Regulators are included but not used. `get_modes` does not mark the mode preferred.

Test signals: Both compatibles, command count audit against array size, GPIO sequencing on hardware, DSI attach/remove, display-on redundancy tolerance, and panel mode/bpc reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-himax8279d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-td4320.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-td4320.c

Purpose: MIPI DSI video-mode panel driver for BOE TD4320 1080x2340 panels, generated from vendor DSI data.

Important APIs/types/functions: `struct boe_td4320`, static supply table, reset/on/off helpers, prepare/unprepare, fixed display mode, panel funcs, probe/remove, and OF match.

Control flow: Probe obtains constant supplies `iovcc`, `vsn`, and `vsp`, reset GPIO, configures four-lane RGB888 video burst DSI with non-continuous clock, sets `prepare_prev_first`, attaches OF backlight, registers panel, and attaches DSI. Prepare enables supplies, resets, sends vendor generic/DCS command sequence including brightness/control-display/sleep-out/display-on, and cleans up on failure. Unprepare sends display-off/sleep-in and powers down.

State and persistence: State stores panel, DSI, supply array, and reset GPIO. Brightness is initialized by command sequence but external backlight is managed through OF panel backlight.

Dependencies and integration: Uses DRM MIPI DSI multi-context helpers, regulator bulk const API, GPIO, DRM fixed mode helper, panel backlight, and OF.

Risks: Generated command sequences are opaque and panel-specific. `boe_td4320_off` returns an error but unprepare only logs it and continues power-down. DSI LPM flag is toggled inside on/off and may interact with host state.

Test signals: Probe with `boe,td4320`, supply/reset sequencing, DSI command failure cleanup, fixed mode helper output, backlight phandle attachment, and remove detach handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-td4320.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-th101mb31ig002-28a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-th101mb31ig002-28a.c

Purpose: Descriptor-driven MIPI DSI panel driver for BOE TH101MB31IG002-28A and Starry ER88577 800x1280 LCD panels.

Important APIs/types/functions: `struct panel_desc` captures mode, DSI flags, init callback, lanes, LP11/reset delays, and power-off delays. `struct boe_th101mb31ig002` stores panel, DSI, descriptor, power regulator, enable/reset GPIOs, and orientation. Provides reset, two init-command functions, disable/unprepare/prepare, get_modes/get_orientation, descriptors, OF match, and DSI probe/remove.

Control flow: Probe selects descriptor, configures DSI, gets `power`, `enable`, optional `reset`, reads panel orientation from DT, attaches OF backlight, registers panel, and attaches to DSI. Prepare enables power, optionally enters LP11 before reset, waits descriptor-defined delays, enables panel, resets, and calls the descriptor init sequence. Disable waits optional backlight delay, sends display-off, sleep-in, and optional reset delay. Unprepare drives reset/enable low and disables power with optional off delay. Modes are reported through the fixed-mode helper and orientation is exposed through both connector and panel funcs.

State and persistence: State is per DSI device. Descriptor data is static and controls timing/power behavior for each compatible.

Dependencies and integration: Depends on DRM MIPI DSI, regulator, GPIO, OF device match data, OF panel orientation, DRM probe helper, and DRM panel backlight integration.

Risks: Optional reset GPIO is used by `boe_th101mb31ig002_reset`; platforms without reset must be verified against gpiod optional semantics. Prepare does not undo regulator/enable on init failure. Descriptor timing mistakes can break one compatible while the other works.

Test signals: Both compatibles, orientation property handling, LP11-before-reset sequence for Starry, power failure cleanup review, fixed-mode enumeration, backlight delay behavior, and DSI command error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-th101mb31ig002-28a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-tv101wum-ll2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-tv101wum-ll2.c

Purpose: MIPI DSI video-mode panel driver for BOE TV101WUM-LL2 1200x1920 panels, generated from vendor DSI data.

Important APIs/types/functions: `struct boe_tv101wum_ll2`, static `vsp`/`vsn` supply table, reset/on/off helpers, prepare/unprepare, fixed display mode, panel funcs, DSI probe/remove, and OF match.

Control flow: Probe gets constant supplies, reset GPIO, configures four-lane RGB888 video burst DSI with HSE, sets `prepare_prev_first`, attaches OF backlight, registers the panel, and attaches to DSI. Prepare enables supplies, toggles reset, exits sleep, sends vendor DCS/generic commands, sets display on, and cleans up on failure. Unprepare sends display-off/sleep-in plus vendor off commands, asserts reset, and disables regulators.

State and persistence: Per-device state stores DSI, reset GPIO, supply array, and DRM panel. The panel is reinitialized on each prepare.

Dependencies and integration: Depends on DRM MIPI DSI, regulator bulk const API, GPIO, DRM fixed mode helper, OF, and panel backlight.

Risks: Off sequence ignores accumulated DSI errors by design and powers down regardless. Display bpc is not explicitly set, relying on default 8 bpc. Generated vendor commands are opaque.

Test signals: Probe with `boe,tv101wum-ll2`, supply/reset timing, fixed mode at 1200x1920, backlight binding, command failure cleanup in prepare, and detach/remove path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-tv101wum-ll2.c -->
