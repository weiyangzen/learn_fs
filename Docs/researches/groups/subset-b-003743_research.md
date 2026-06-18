# subset-b-003743 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_drv.h

## Purpose

`rockchip_drm_drv.h` is the shared Rockchip DRM driver contract used by the VOP, VOP2, GEM, framebuffer, RGB, LVDS, HDMI, MIPI, DP, and component binding code. It defines display output mode constants, common Rockchip CRTC and encoder state, DMA/IOMMU helper prototypes, platform-driver declarations, and container helpers used across the Rockchip DRM subsystem.

## Important APIs, Types, and Functions

- `ROCKCHIP_MAX_FB_BUFFER`, `ROCKCHIP_MAX_CONNECTOR`, and `ROCKCHIP_MAX_CRTC` bound local arrays and CRTC assumptions.
- `ROCKCHIP_OUT_MODE_*` encodes hardware output bus packing such as P888, P666, P565, BT.656/1120, serial RGB, YUV420, and 10-bit `AAAA`.
- `ROCKCHIP_OUTPUT_DSI_DUAL` marks dual-channel DSI routing.
- `struct rockchip_crtc_state` extends `drm_crtc_state` with output connector type, output mode, bpc, output flags, AFBC enablement, YUV overlay flag, bus format, bus flags, and color space. Encoder atomic checks populate these fields and VOP/VOP2 atomic enable consumes them.
- `struct rockchip_drm_private` stores the shared IOMMU domain, IOMMU device, `drm_mm` allocator, and `mm_lock` used by GEM IOVA mapping.
- `struct rockchip_encoder` wraps `drm_encoder` with `crtc_endpoint_id`, allowing VOP2 to select an output interface from device-tree endpoint IDs.
- `rockchip_drm_dma_attach_device`, `rockchip_drm_dma_detach_device`, and `rockchip_drm_dma_init_device` are the cross-file DMA mapping hooks called by VOP/VOP2 and GEM paths.
- `rockchip_drm_wait_vact_end` exposes the VOP line-flag wait service to display bridge drivers.
- `to_rockchip_crtc_state` and `to_rockchip_encoder` are container conversion helpers.

## Control Flow

This header has no executable control flow beyond `to_rockchip_encoder`. Its main flow is contractual: encoders set `rockchip_crtc_state` fields during atomic checks, display controllers read those fields during atomic enable, and GEM/VOP code coordinate through the private DMA/IOMMU structures and helper prototypes.

## State and Persistence Behavior

The persistent state declared here lives inside `drm_device->dev_private`, `drm_crtc->state`, and Rockchip encoder instances. `rockchip_crtc_state` is duplicated and reset by VOP/VOP2 CRTC state hooks, so its fields persist across atomic state transitions rather than global driver state. `rockchip_drm_private` persists for the DRM device lifetime and protects shared `drm_mm` state with `mm_lock`.

## Dependencies and Integration Points

The header depends on DRM atomic/GEM types, Linux component binding, I2C, modules, bits, and platform-driver declarations. It is included by framebuffer, GEM, VOP, VOP2, LVDS, RGB, and other Rockchip encoder drivers. Device-tree endpoint integration flows through `rockchip_drm_encoder_set_crtc_endpoint_id` and `rockchip_drm_endpoint_is_subdriver`.

## Risks and Edge Cases

The output-mode constants are ABI-like hardware contracts; accidental renumbering would break register programming. `ROCKCHIP_OUT_MODE_P888` and `ROCKCHIP_OUT_MODE_BT1120` intentionally share value 0, which can be confusing when reviewing output paths. `rockchip_crtc_state` fields are not self-validating, so bridge atomic checks must populate consistent `output_type`, `output_mode`, `bus_format`, and `output_bpc` combinations. Shared IOMMU state relies on correct `dev_private` initialization before GEM allocation.

## Test Signals

Build tests should cover all Rockchip DRM configurations because this header gates many optional subdrivers. Atomic modeset tests should confirm encoder atomic checks populate `rockchip_crtc_state` and VOP/VOP2 consumes it correctly for RGB, LVDS, HDMI, DSI, eDP, DP, and YUV bus formats. GEM stress should exercise concurrent IOMMU allocations under `mm_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_fb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_fb.c

## Purpose

`rockchip_drm_fb.c` installs Rockchip-specific DRM mode configuration and framebuffer creation. Its main addition over generic GEM framebuffer helpers is allocation of `struct drm_afbc_framebuffer` and initialization of AFBC metadata when the framebuffer modifier is AFBC.

## Important APIs, Types, and Functions

- `rockchip_drm_fb_funcs` uses generic GEM framebuffer destruction, GEM handle creation, and atomic dirtyfb handling.
- `rockchip_mode_config_helpers` selects `drm_atomic_helper_commit_tail_rpm`, integrating atomic commits with runtime PM.
- `rockchip_fb_create()` allocates a `drm_afbc_framebuffer`, initializes the base GEM framebuffer with `drm_gem_fb_init_with_funcs`, then calls `drm_gem_fb_afbc_init` for AFBC modifiers.
- `rockchip_drm_mode_config_funcs` wires framebuffer create, atomic check, and atomic commit callbacks into `drm_device->mode_config`.
- `rockchip_drm_mode_config_init()` sets min/max mode-config dimensions, installs funcs/helpers, and enables normalized z-position.

## Control Flow

Driver setup calls `rockchip_drm_mode_config_init`. Later, userspace `ADDFB2` requests enter `rockchip_fb_create`. The helper allocates the AFBC-capable framebuffer wrapper, initializes GEM planes and format metadata, validates AFBC layout only when `drm_is_afbc(mode_cmd->modifier[0])`, and returns the base framebuffer. Error paths free the wrapper directly before framebuffer registration or drop the framebuffer reference after AFBC initialization failure.

## State and Persistence Behavior

The mode-config callbacks persist for the DRM device lifetime. Each framebuffer owns GEM object references through `drm_gem_fb_init_with_funcs`; AFBC metadata persists in the `drm_afbc_framebuffer` wrapper until `drm_gem_fb_destroy`. `normalize_zpos = true` makes atomic state carry normalized plane ordering for VOP/VOP2 composition.

## Dependencies and Integration Points

The file depends on DRM framebuffer, GEM framebuffer, AFBC, damage, probe, and atomic helpers. It integrates with Rockchip GEM objects through included declarations and with VOP/VOP2 through framebuffer modifiers and z-position normalization. Runtime-PM-aware atomic commit tail is important because display controllers enable clocks and attach DMA mappings during atomic enable.

## Risks and Edge Cases

`rockchip_fb_create` assumes AFBC state is represented by modifier plane 0. Any multi-plane modifier convention change would need review. `max_width` and `max_height` default to 4096, but VOP2 bind later tightens mode-config bounds to SoC-specific input limits; ordering matters. AFBC framebuffer allocation uses `kzalloc_obj(*afbc_fb)`, so error handling must keep direct `kfree` and `drm_framebuffer_put` paths distinct.

## Test Signals

Useful tests include linear and AFBC `ADDFB2` creation, malformed AFBC metadata rejection, GEM handle creation through framebuffer handles, dirtyfb dispatch, zpos normalization with multiple planes, and atomic commits under runtime PM suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_fb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_fb.h

## Purpose

`rockchip_drm_fb.h` is the minimal public header for Rockchip framebuffer mode configuration. It exposes only `rockchip_drm_mode_config_init`.

## Important APIs, Types, and Functions

- `rockchip_drm_mode_config_init(struct drm_device *dev)` initializes `drm_device->mode_config` with Rockchip framebuffer creation, atomic helpers, dimension limits, runtime-PM-aware commit tail, and normalized zpos.

## Control Flow

The header provides no control flow. The Rockchip DRM driver includes it during device setup and calls the exported initializer before registering or using mode objects.

## State and Persistence Behavior

State initialized by the declared function persists in `dev->mode_config`. The header itself owns no data.

## Dependencies and Integration Points

The header relies on consumers already having a visible `struct drm_device` declaration. It is consumed by Rockchip DRM setup code and by VOP code that includes the framebuffer interface.

## Risks and Edge Cases

Because this header does not include DRM type declarations itself, include ordering must provide `struct drm_device`. That works in current users but can surprise new consumers. Any signature change must be synchronized with `rockchip_drm_fb.c`.

## Test Signals

Build coverage with all Rockchip DRM objects enabled is the main signal. Runtime validation is covered by framebuffer creation and atomic commit tests that prove `rockchip_drm_mode_config_init` was called before use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_gem.c

## Purpose

`rockchip_drm_gem.c` implements Rockchip GEM buffer allocation, mmap, dumb-buffer creation, and PRIME import/export. It supports two backing modes: page-backed buffers mapped through the Rockchip shared IOMMU domain, and contiguous DMA allocations when no IOMMU domain is available.

## Important APIs, Types, and Functions

- `rockchip_gem_alloc_object()` creates a rounded-up `rockchip_gem_object`, initializes the embedded DRM GEM object, and installs `rockchip_gem_object_funcs`.
- `rockchip_gem_create_object()` allocates object metadata and backing storage, optionally with a kernel mapping for fbdev buffers.
- `rockchip_gem_dumb_create()` sizes dumb buffers with 64-byte pitch alignment required by Mali and creates a GEM handle.
- IOMMU path: `rockchip_gem_get_pages`, `rockchip_gem_iommu_map`, `rockchip_gem_alloc_iommu`, `rockchip_gem_iommu_unmap`, and `rockchip_gem_free_iommu`.
- DMA path: `rockchip_gem_alloc_dma`, `rockchip_gem_free_dma`, and `rockchip_gem_dma_map_sg`.
- mmap path: `rockchip_drm_gem_object_mmap` normalizes `vm_pgoff`, sets write-combine/decrypted page protection, and delegates to page or DMA mmap.
- PRIME path: `rockchip_gem_prime_get_sg_table`, `rockchip_gem_prime_import_sg_table`, `rockchip_gem_prime_vmap`, and `rockchip_gem_prime_vunmap`.

## Control Flow

New local buffers are created through `rockchip_gem_create_object`. Allocation first initializes the GEM object, then chooses IOMMU or DMA backing from `drm->dev_private->domain`. The IOMMU path gets pages, converts them to an sg table, fakes DMA addresses to support cache syncing, syncs to device, reserves IOVA space in `drm_mm` under `mm_lock`, and maps the sg table into the IOMMU domain. The DMA path uses `dma_alloc_attrs`, adding `DMA_ATTR_NO_KERNEL_MAPPING` when a kernel vmap is not requested.

Freeing is inverse. Imported buffers unmap the imported sg table from IOMMU or DMA and call `drm_prime_gem_destroy`; native buffers free their selected backing. PRIME import creates only GEM metadata, then maps the provided sg table into IOMMU space or requires a contiguous DMA span. PRIME vmap reuses existing `kvaddr` when possible or temporarily vmaps page-backed buffers.

## State and Persistence Behavior

Each `rockchip_gem_object` persists DMA address, optional kernel virtual address, DMA attrs, page array, sg table, page count, IOMMU `drm_mm_node`, and mapped size. The shared `drm_mm` allocator persists in `rockchip_drm_private` and serializes allocation/removal with `mm_lock`. Imported objects keep `obj->import_attach` and `rk_obj->sgt` until GEM release. Page-backed buffers may have persistent `kvaddr` only when `alloc_kmap` was requested.

## Dependencies and Integration Points

This file depends on DRM GEM, GEM DMA VM ops, PRIME helpers, dumb-buffer helpers, Linux IOMMU, DMA-buf, scatter-gather, vmalloc, and Rockchip private DMA helpers. VOP and VOP2 plane updates consume `to_rockchip_obj(fb->obj[n])->dma_addr` as scanout addresses. fbdev uses `alloc_kmap` via the file/client check in `rockchip_gem_create_with_handle`.

## Risks and Edge Cases

The IOMMU path treats `iommu_map_sgtable` returning less than requested size as failure, but stores the returned mapped byte count as `rk_obj->size` on success; unmap correctness depends on the IOMMU API return semantics. The DMA PRIME path rejects non-contiguous sg tables without IOMMU, which is necessary for linear scanout but can surprise importers. `rockchip_drm_gem_object_mmap_iommu` only rejects zero user pages and maps `obj->size >> PAGE_SHIFT` pages, relying on DRM mmap setup to bound VMA size. `rockchip_gem_free_iommu` calls `vunmap(rk_obj->kvaddr)` even when `kvaddr` may be NULL, which is tolerated but should remain intentional. Cache coherency for page-backed allocations relies on `dma_sync_sgtable_for_device` and write-combine mappings.

## Test Signals

Exercise dumb allocation with and without IOMMU, mmap read/write, fbdev creation requiring kernel mapping, PRIME export/import of contiguous and non-contiguous buffers, vmap/vunmap of native and imported objects, concurrent GEM allocation/free under stress, and VOP/VOP2 scanout from both linear and imported buffers. IOMMU fault logs and bus-error IRQs are important hardware signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_gem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_gem.h

## Purpose

`rockchip_drm_gem.h` defines the Rockchip GEM object layout and exports the allocation, free, dumb-buffer, PRIME, and vmap interfaces implemented by `rockchip_drm_gem.c`.

## Important APIs, Types, and Functions

- `to_rockchip_obj()` converts a `drm_gem_object` to `struct rockchip_gem_object`.
- `struct rockchip_gem_object` embeds the DRM GEM base and stores `kvaddr`, `dma_addr`, DMA attributes, IOMMU `drm_mm_node`, pages, sg table, page count, and mapped size.
- `rockchip_gem_create_object()` allocates a GEM object and backing store.
- `rockchip_gem_free_object()` is installed as `drm_gem_object_funcs.free`.
- `rockchip_gem_dumb_create()` is the dumb-buffer driver callback.
- PRIME helpers expose sg table export/import and vmap/vunmap.

## Control Flow

The header is consumed by framebuffer and display-controller paths. Plane update code uses `to_rockchip_obj` on framebuffer GEM objects and reads `dma_addr` directly to program scanout registers. DRM driver setup wires the declared functions into driver callbacks and GEM object funcs.

## State and Persistence Behavior

The object fields persist for the GEM object's lifetime. In IOMMU mode, `pages`, `sgt`, `num_pages`, `mm`, `size`, and `dma_addr` describe the IOVA mapping. In DMA mode, `kvaddr`, `dma_addr`, and `dma_attrs` describe the coherent/write-combine allocation. Imported objects use `sgt` and `dma_addr` without owning native pages.

## Dependencies and Integration Points

The type relies on DRM GEM and Linux DMA/scatterlist types from including contexts. It is tightly integrated with VOP/VOP2 plane programming, PRIME dma-buf import/export, dumb-buffer creation, and the Rockchip shared IOMMU domain.

## Risks and Edge Cases

Direct field access by scanout code makes `dma_addr` a cross-file invariant: allocation, import, and free paths must set and clear it consistently. `flags` is present but unused in this snapshot. Include ordering must provide several type declarations; the header does not include all dependencies itself.

## Test Signals

Build all users of `to_rockchip_obj`, then run allocation, mmap, PRIME, and scanout tests that confirm the fields are valid in both IOMMU and DMA configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_gem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_vop.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_vop.c

## Purpose

`rockchip_drm_vop.c` implements the legacy Rockchip VOP display controller as a DRM CRTC with primary, cursor, and overlay planes. It programs register-described windows, scaling, AFBC, RGB/YUV conversion, gamma LUTs, output timings, vblank/event delivery, runtime PM, clocks, resets, and component bind/unbind.

## Important APIs, Types, and Functions

- `struct vop` is the persistent controller state: DRM CRTC, clock/reset handles, register base, LUT base, register shadow (`regsbak`), locks, IRQ, completions, pending vblank event, flip-work, feature data, optional RGB encoder, and flexible window array.
- `struct vop_win` binds a DRM plane to `vop_win_data` register metadata and optional YUV2YUV registers.
- `vop_reg_set()` centralizes masked register writes and maintains `regsbak` for read-modify-write registers.
- Format helpers map DRM formats to VOP encodings and swap flags; scaler helpers compute scale factors, line-buffer mode, and vertical skip.
- Plane callbacks validate scaling/AFBC/YUV constraints, program framebuffer addresses, format, mirrors, scaling, YUV coefficients, alpha blending, and AFBC state.
- CRTC callbacks validate mode width, round dclk, enable/disable hardware, program timings/output interface/dither/gamma, flush cfg-done, and handle atomic events.
- `rockchip_drm_wait_vact_end()` exports a line-flag wait helper.
- `vop_bind`/`vop_unbind` implement component lifecycle.

## Control Flow

Component bind allocates `struct vop`, maps MMIO and optional LUT memory, initializes windows, creates planes/CRTC, enables runtime PM, resets hardware, snapshots registers into `regsbak`, disables windows, requests the shared IRQ, optionally creates an internal RGB encoder, and initializes DMA mapping.

On atomic enable, `vop_enable` resumes PM, enables clocks, attaches the DMA mapping, restores register backup, disables stale windows unless exiting self-refresh, clears AFBC, and enables vblank. `vop_crtc_atomic_enable` then programs connector-specific output enables from `rockchip_crtc_state`, sets output mode, dither, timings, line flag, dclk rate, standby clear, and gamma. Plane atomic update programs the selected window from `rockchip_gem_object` DMA addresses, including UV plane addresses and AFBC header pointer. Atomic flush enables global AFBC if needed, writes cfg-done, waits out a possibly racing vblank IRQ, captures page-flip events, and queues old framebuffer unrefs for after vblank. Disable waits for DSP hold before detaching IOMMU and turning off clocks.

## State and Persistence Behavior

`regsbak` mirrors non-write-mask registers across suspend/runtime power loss and is replayed on enable. `win_enabled` tracks which windows should be restored after self-refresh. `is_enabled` guards register access and IRQ enablement. `event` and `pending` coordinate vblank completion and deferred framebuffer release. Completion objects synchronize DSP hold and line-flag interrupts. CRTC state is extended with Rockchip output fields and duplicated/reset by local CRTC funcs.

## Dependencies and Integration Points

The driver depends on DRM atomic helpers, GEM framebuffer helpers, vblank, flip work, self-refresh, runtime PM, clocks, resets, IOMMU attach/detach, and SoC register data from `rockchip_vop_reg.c`. It consumes `rockchip_gem_object->dma_addr`, `rockchip_crtc_state`, and optional `rockchip_rgb`. Analogix DP CRC hooks are compiled when enabled.

## Risks and Edge Cases

Register shadowing requires every non-write-mask update to go through `vop_reg_set`; direct writes can desynchronize resume state. AFBC is limited to one plane and rejects offsets/rotation in check paths; unsupported combinations must stay aligned with Mesa/modifier expectations. Async cursor updates can accumulate many old framebuffer references before vblank, as noted by the FIXME. Disable relies on a DSP hold interrupt with a 200 ms timeout to avoid memory-bus hangs. Shared IRQ handling must distinguish VOP from IOMMU interrupts under runtime PM. Output mode fallback mutates `rockchip_crtc_state` when RGB10 is unavailable.

## Test Signals

Test linear RGB/YUV scanout, AFBC acceptance/rejection, one-AFBC-plane enforcement, scaling limits, YUV odd-source rejection, reflection properties, alpha blending on nonzero windows, async cursor updates, gamma LUT enable/update/disable, self-refresh entry/exit, suspend/resume register restoration, vblank event delivery, line-flag waits, shared IRQ behavior, and IOMMU fault handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_vop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_vop.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_vop.h

## Purpose

`rockchip_drm_vop.h` is the register-description and helper contract for legacy Rockchip VOP hardware. It defines VOP version macros, AFBC modifier support, register-field descriptors, SoC data tables, interrupt bits, alpha/scaler/dither enums, scaler math helpers, and the exported component ops.

## Important APIs, Types, and Functions

- `VOP_VERSION`, `VOP_MAJOR`, and `VOP_MINOR` encode hardware IP versions.
- `ROCKCHIP_AFBC_MOD` defines the supported AFBC modifier: 16x16 sparse blocks with YTR transform.
- `struct vop_reg` describes offset, mask, shift, write-mask behavior, and relaxed-write behavior for one hardware field.
- `struct vop_common`, `vop_output`, `vop_modeset`, `vop_intr`, `vop_afbc`, `vop_win_phy`, `vop_win_data`, and related structs describe SoC register layout.
- `struct vop_data` aggregates the complete SoC descriptor, including version, windows, LUT size, max output, and feature flags.
- Interrupt and alpha macros encode the packed register fields used by `rockchip_drm_vop.c`.
- Scaler helpers compute fixed-point coefficients, vertical skip, scaling mode, and line-buffer mode.
- `extern const struct component_ops vop_component_ops` is consumed by platform registration code.

## Control Flow

The header contributes inline scaler decision flow. `scl_get_scl_mode` picks none/up/down, `scl_get_vskiplines` chooses vertical skip for large downscale ratios, and `scl_vop_cal_lb_mode` selects line-buffer mode based on width and YUV/RGB. The executable VOP driver uses these helpers during plane atomic update.

## State and Persistence Behavior

The structures defined here are mostly static SoC descriptions referenced by the live `struct vop`. They do not own runtime state themselves. The `write_mask` and `relaxed` fields affect persistent register-shadow behavior in `vop_reg_set`.

## Dependencies and Integration Points

The header depends on DRM format modifier definitions, Linux bits, and the component framework through includers. It is paired with SoC register tables in `rockchip_vop_reg.c` and implementation in `rockchip_drm_vop.c`.

## Risks and Edge Cases

Register descriptors are highly sensitive: wrong masks, shifts, or write-mask flags cause silent hardware misprogramming. `enum sacle_up_mode` contains a spelling error that is stable API within the driver. `scl_cal_scale` assumes destination greater than one; call sites must validate sizes. AFBC modifier comments document a strict producer/consumer contract, so changing modifier bits can break userspace buffers.

## Test Signals

Compile coverage against all VOP SoC tables is essential. Runtime signals include correct scaling across up/down ratios, AFBC modifier negotiation with userspace, interrupt mask/clear behavior, dither modes, alpha blending, and line-buffer mode validation for wide outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_vop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_vop2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_vop2.c

## Purpose

`rockchip_drm_vop2.c` implements the newer Rockchip VOP2 display controller. VOP2 has multiple video ports, shared overlay/layer routing, cluster and smart windows, regmap-backed register fields, SoC-specific interface mux operations, gamma/debugfs support, runtime PM, clocks, IRQs, and component lifecycle.

## Important APIs, Types, and Functions

- `vop2_bind`/`vop2_unbind` create and destroy the component, map MMIO, initialize regmap, clocks, syscon GRFs, windows, CRTCs, IRQs, optional RGB output, DMA mapping, and runtime PM.
- `vop2_win_init` creates per-window regmap fields from cluster or smart register descriptors.
- Plane helpers validate min/max sizes, scaling, AFBC, YUV alignment, rotation, background-color alpha constraints, and modifier compatibility.
- `vop2_plane_atomic_update` programs linear or AFBC scanout addresses, stride, format, swaps, mirroring/rotation, scale, CSC, color key, dither-up, VP selection, and cluster enablement.
- `vop2_crtc_atomic_enable`, `vop2_crtc_atomic_disable`, `vop2_crtc_atomic_begin`, and `vop2_crtc_atomic_flush` manage video-port timings, interface muxing, dither, post-scaler/background, gamma, cfg-done, vblank events, and standby.
- `vop2_enable`/`vop2_disable` manage global clocks, PM, DMA attach/detach, hardware-version checks, bus-error IRQs, and regcache invalidation.
- `vop2_isr` and `rk3576_vp_isr` handle shared/global and per-VP interrupts.
- Debugfs helpers expose summary, active register dump, and full register dump.

## Control Flow

During bind, the driver reads SoC match data, initializes regmap and mode-config bounds, allocates regmap fields for every hardware window, maps optional gamma LUT memory, obtains GRF/PMU syscons based on feature bits, gets core clocks and optional HDMI PHY PLLs, requests IRQs, creates DRM planes and CRTCs for connected graph ports, registers per-VP IRQs for RK3576-class hardware, creates an internal RGB encoder when an RGB endpoint exists, initializes DMA mapping, and enables runtime PM.

Atomic enable prepares the VP dclk, globally enables VOP2 on the first active port, computes polarity flags, asks SoC ops to program the output interface mux and return the effective clock, chooses output mode and swaps from `rockchip_crtc_state`, writes timings including interlace handling, optionally switches the VP clock parent to an HDMI PHY PLL, sets post-scaler/background registers, writes cfg-done, writes VP DSP control, updates gamma, and enables vblank. Plane updates are per-window but feed shared overlay selection prepared in `setup_overlay` during atomic begin. Flush handles gamma-only updates, post config, cfg-done, and page-flip event arming. Disable turns off planes, waits for DSP hold, restores dclk parent, decrements global enable count, and disables shared hardware when the last VP stops.

## State and Persistence Behavior

`struct vop2` persists global resources: regmap, syscons, clocks, IRQ, enable count, old shared layer/port selection values, overlay lock, optional RGB encoder, and flexible window array. Each `vop2_video_port` persists CRTC state, dclk source, win mask, primary plane, event pointer, layer count, and DSP hold completion. Regmap uses `REGCACHE_MAPLE`; selected VP/window ranges are marked non-volatile in the cache because config-done-delayed registers read back old values until committed. `enable_count` gates global hardware enable/disable across multiple CRTCs.

## Dependencies and Integration Points

The driver integrates with Rockchip GEM DMA addresses, `rockchip_crtc_state`, `rockchip_encoder->crtc_endpoint_id`, optional `rockchip_rgb`, SoC data from `rockchip_vop2_reg.c`, syscon GRFs, DRM atomic helpers, vblank, debugfs, media bus formats, V4L2 color spaces, runtime PM, clk framework, and IOMMU attach/detach.

## Risks and Edge Cases

`vop2_enable` has early returns after clock/DMA attach/version failures that do not visibly unwind every resource in the same function, so error-path review is important. Shared overlay registers require `ovl_lock` and SoC ops to avoid cross-VP races. RK3568 cluster windows are AFBC-only, RK3588 10bpc linear restrictions are encoded in modifier checks, and AFBC rotation/mirroring requires strict alignment. Gamma LUT on RK356x is limited to one CRTC at a time. Event delivery waits for cfg-done to clear in IRQ context; incorrect cfg-done handling can delay page-flip completion. VOP2 assumes at least one primary-capable non-mirror window per active VP.

## Test Signals

Test multi-CRTC modesets, shared overlay routing, zpos/layer limits, AFBC and linear modifiers across cluster/smart windows, 10bpc restrictions, YUV/RGB CSC, interlaced modes, HDMI PHY PLL clock parent switching, gamma on RK356x and newer SoCs, debugfs register reads, bus-error IRQs, per-VP IRQs on RK3576, suspend/resume with regcache, and hotplug graph configurations with missing ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_vop2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_vop2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_vop2.h

## Purpose

`rockchip_drm_vop2.h` defines the public and internal data model for VOP2 hardware. It contains version constants, feature flags, output-interface helpers, window register indices, SoC data structures, runtime structs, interrupt bits, register offsets/fields, layer IDs, regmap accessors, and cfg-done helper used by VOP2 implementation and register tables.

## Important APIs, Types, and Functions

- `VOP2_VERSION` and `VOP_VERSION_RK*` identify supported VOP2 IP revisions.
- Feature flags describe VP 10-bit output, required GRF/PMU syscons, AFBDC support, cluster windows, and internal power domains.
- `enum vop2_win_regs` names every per-window regmap field consumed by `vop2_plane_atomic_update`.
- `struct vop2_win_data`, `vop2_video_port_data`, and `vop2_data` are the SoC descriptor contracts.
- `struct vop2_win`, `vop2_video_port`, and `vop2` are the runtime window, CRTC/video-port, and global controller objects.
- `struct vop2_ops` provides SoC-specific hooks for interface muxing, background delay, and overlay setup.
- Register macros cover system, video-port, overlay, cluster, smart, HDR, interrupt, and output-interface fields.
- Inline helpers wrap regmap reads/writes, window regmap-field writes, container conversions, cluster-window detection, and `vop2_cfg_done`.

## Control Flow

The inline flow is simple but central. VOP2 code writes window fields through `vop2_win_write`, writes VP-relative registers through `vop2_vp_write`, and commits delayed state with `vop2_cfg_done`, which sets global cfg-done enable plus the VP-specific cfg-done bit and write mask.

## State and Persistence Behavior

The descriptor structs are static per SoC, while runtime structs persist for the component lifetime. `vop2` owns shared clocks, syscon maps, regmap, enable count, old overlay selections, and flexible windows. `vop2_video_port` owns per-CRTC clock/event/layer state. `vop2_win` owns regmap fields and plane identity. The header's register constants define persistent hardware layout and cached regmap behavior in the C file.

## Dependencies and Integration Points

The header depends on Linux regmap, DRM modes, VOP helper definitions, Rockchip DRM state, and device-tree endpoint IDs from `dt-bindings/soc/rockchip,vop2.h`. It is consumed by VOP2 implementation and SoC register data tables.

## Risks and Edge Cases

Register offsets and bitfields are SoC-critical and easy to misapply across RK3568, RK3588, RK3528, RK3562, and RK3576 revisions. The cfg-done helper notes write-mask behavior differences; using it incorrectly can leave registers uncommitted. `ROCKCHIP_VOP2_PHY_ID_INVALID = -1` in an enum should be treated carefully when stored in unsigned fields. Output interface helper predicates assume endpoint IDs stay synchronized with device-tree bindings.

## Test Signals

Build with every VOP2 SoC table, then validate register programming on RK356x/RK3588/RK3576-class hardware. Focus on cfg-done commits, interface mux selection, per-window regmap fields, power-domain bits, interrupts, and debugfs register dumps matching expected offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_vop2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_lvds.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_lvds.c

## Purpose

`rockchip_lvds.c` implements the Rockchip LVDS component driver for RK3288 and PX30 style LVDS blocks. It binds a DRM encoder to a panel or downstream bridge, parses output/data-mapping properties, programs LVDS/RGB/dual-LVDS hardware and GRF muxes, manages panel prepare/enable sequencing, runtime PM, clocks, PHY setup, and component lifecycle.

## Important APIs, Types, and Functions

- `struct rockchip_lvds_soc_data` selects SoC-specific probe and encoder helper functions.
- `struct rockchip_lvds` stores MMIO, GRF regmap, pclk, optional PHY, output/format selections, DRM panel/bridge, Rockchip encoder, and optional pinctrl info.
- `rockchip_lvds_encoder_atomic_check` writes `ROCKCHIP_OUT_MODE_P888` and LVDS connector type into `rockchip_crtc_state`.
- RK3288 helpers power on/off LVDS or TTL lanes, program PLL/lane registers, configure GRF format/dual-channel/source selection, and handle panel enable/disable.
- PX30 helpers enable LVDS mode/P2S in GRF, configure format/source, and handle PHY initialization/power.
- `rockchip_lvds_bind` resolves panel/bridge graph endpoints, parses `rockchip,output` and remote `data-mapping`, creates the encoder and bridge connector, and enables runtime PM.
- `rockchip_lvds_probe` chooses match data, obtains GRF, runs SoC probe, and registers component ops.

## Control Flow

Platform probe allocates state, reads match data, obtains `rockchip,grf`, performs RK3288 or PX30-specific initialization, stores drvdata, and adds the component. Bind then locates port 1 endpoints, finds a panel or bridge, derives output type and LVDS mapping, initializes a DRM LVDS encoder, attaches helper funcs, wraps panels in a bridge when needed, attaches a bridge connector, and enables runtime PM. Encoder enable prepares the panel, powers/configures LVDS hardware and VOP source mux, then enables the panel. Disable reverses panel enable, hardware power, and panel prepare.

## State and Persistence Behavior

`rockchip_lvds` persists for the platform device lifetime. Parsed `output` and `format` control later enable-time register programming. RK3288 pclk is prepared during probe and enabled around poweron; PX30 keeps a PHY initialized and powered on after probe, while runtime PM gates register access. The encoder stores Rockchip endpoint information through the embedded `rockchip_encoder`.

## Dependencies and Integration Points

The driver depends on DRM bridge/panel/connector helpers, OF graph, syscon regmap, pinctrl, PHY, clocks, runtime PM, and Rockchip CRTC state. It integrates with VOP/VOP2 through encoder atomic state and GRF source selection. Header constants in `rockchip_lvds.h` define RK3288/PX30 bitfields.

## Risks and Edge Cases

`rockchip_lvds_unbind` unconditionally calls the SoC encoder disable helper, which assumes a valid panel/hardware state. Several enable error paths unprepare the panel but do not call poweroff after partial RK3288/PX30 poweron failures past hardware enable. PX30 rejects RGB and dual-LVDS output, while RK3288 supports RGB/LVDS/dual-LVDS; device-tree property validation must match hardware. `brige_to_lvds` is misspelled but local. Panel bridge removal happens only on some error/unbind paths and should be reviewed for externally supplied bridges.

## Test Signals

Test RK3288 RGB, single LVDS, and dual LVDS outputs; PX30 LVDS-only output; VESA/JEIDA 18/24-bit mappings; VOP source selection from graph endpoint IDs; panel prepare/enable/disable sequencing; runtime suspend/resume; missing panel/bridge endpoints; invalid properties; and GRF register writes via regmap tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_lvds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_lvds.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_lvds.h

## Purpose

`rockchip_lvds.h` defines register offsets, bit masks, write-mask field helpers, and LVDS format constants for RK3288 and PX30 LVDS hardware.

## Important APIs, Types, and Functions

- RK3288 channel register offsets and lane enable/bias/mode/data bits describe LVDS/TTL lane programming.
- PLL helper macros split feedback and predivider values across RK3288 registers.
- GRF offsets and bits define VOP source selection, LVDS dual-channel, TTL enable, format, start phase, clock inversion, channel enable, and powerdown controls.
- Format constants map VESA/JEIDA 18/24-bit data mappings to driver values.
- PX30 GRF helpers use `FIELD_PREP_WM16` for write-mask encoded mode, P2S, MSB select, VOP select, clock tie/invert, and format fields.

## Control Flow

The header contains only macros. The C file combines them into poweron, poweroff, and GRF configuration sequences for RK3288 and PX30.

## State and Persistence Behavior

The constants define hardware state programmed by `rockchip_lvds.c`. They do not allocate runtime state. Write-mask macros persist only through GRF register writes.

## Dependencies and Integration Points

The header depends on Linux bit and hardware bitfield helpers. It is private to the Rockchip LVDS driver and tightly tied to the SoC register manuals.

## Risks and Edge Cases

Incorrect write-mask field values can overwrite unrelated GRF bits. RK3288 register values such as `RK3288_LVDS_CFG_REG21_TX_ENABLE` are literal magic values, so changes require hardware validation. The guard name `_ROCKCHIP_LVDS_` is nonstandard but functional.

## Test Signals

Register-level tests should compare GRF/MMIO writes for each mapping and output mode. Hardware validation should check lane activity, bit ordering, clock polarity, dual-channel behavior, and PX30 PHY/P2S enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_lvds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_rgb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_rgb.c

## Purpose

`rockchip_rgb.c` implements an optional internal RGB output helper used by VOP/VOP2 when the display controller directly exposes an RGB/DPI-style panel or bridge instead of a separate subdriver. It creates a simple DRM encoder, attaches a panel/bridge connector, and fills Rockchip CRTC output mode during atomic checks.

## Important APIs, Types, and Functions

- `struct rockchip_rgb` stores device/DRM pointers, bridge, embedded `rockchip_encoder`, connector storage, and output mode.
- `rockchip_rgb_encoder_atomic_check` reads connector bus formats and sets `rockchip_crtc_state.output_mode` to P666, P565, or P888. It sets output type to LVDS connector type for this internal RGB path.
- `rockchip_rgb_init()` scans an OF graph port, ignores endpoints owned by subdrivers, resolves a panel or bridge, creates a simple encoder, attaches helper funcs, wraps panels with `drm_panel_bridge_add_typed`, attaches a bridge connector, records `crtc_endpoint_id`, and returns the helper object.
- `rockchip_rgb_fini()` removes the panel bridge and cleans connector/encoder state.

## Control Flow

VOP or VOP2 calls `rockchip_rgb_init` when SoC data or graph endpoints indicate internal RGB output. The helper scans the selected video port endpoints; if no non-subdriver child exists, it returns NULL to indicate no RGB output. If a panel/bridge is found, it builds encoder and connector objects attached to the supplied CRTC. During atomic check, the encoder maps display bus format to Rockchip output mode; VOP/VOP2 later consumes that state while programming output registers.

## State and Persistence Behavior

The allocated `rockchip_rgb` object is devm-managed by the display controller device and persists until controller unbind. The bridge pointer may be a panel bridge created by this file or an existing bridge. `crtc_endpoint_id` persists in the embedded Rockchip encoder for VOP2 output mux selection.

## Dependencies and Integration Points

The file depends on DRM bridge, panel, bridge connector, simple encoder, OF graph, media bus formats, DP helper includes, and Rockchip endpoint helper APIs. It integrates with VOP through `VOP_FEATURE_INTERNAL_RGB` and with VOP2 through `vop2_find_rgb_encoder`.

## Risks and Edge Cases

The atomic check sets `output_type` to `DRM_MODE_CONNECTOR_LVDS` even for RGB/DPI-style output, matching existing Rockchip handling but potentially confusing. `rgb->connector` is embedded, but `drm_bridge_connector_init` returns an allocated connector and the local pointer is reassigned; `rockchip_rgb_fini` cleans `&rgb->connector`, which may not be the connector actually returned. That lifecycle should be reviewed. If `drm_panel_bridge_add_typed` succeeds and later attach fails, cleanup relies on `err_free_encoder` and may not remove the panel bridge.

## Test Signals

Test no-endpoint, deferred-probe, panel, and bridge cases; endpoint filtering through `rockchip_drm_endpoint_is_subdriver`; bus format mapping for RGB565/RGB666/RGB888; VOP2 endpoint ID muxing; connector cleanup under unbind; and probe/remove leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_rgb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_rgb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_rgb.h

## Purpose

`rockchip_rgb.h` exposes the optional internal RGB encoder helper. It provides real declarations when `CONFIG_ROCKCHIP_RGB` is enabled and NULL/no-op stubs otherwise.

## Important APIs, Types, and Functions

- `rockchip_rgb_init(struct device *dev, struct drm_crtc *crtc, struct drm_device *drm_dev, int video_port)` creates or discovers an internal RGB panel/bridge path for the given video port.
- `rockchip_rgb_fini(struct rockchip_rgb *rgb)` tears down the helper.
- Stub versions return NULL and do nothing when the feature is disabled.

## Control Flow

The header controls compile-time feature flow. VOP/VOP2 can call `rockchip_rgb_init` unconditionally from their perspective; disabled builds compile to no RGB output instead of requiring `#ifdef` blocks in display-controller code.

## State and Persistence Behavior

The header owns no state. Real runtime state is private to `rockchip_rgb.c`; disabled builds persist no object because init returns NULL.

## Dependencies and Integration Points

The function signatures depend on `struct device`, `struct drm_crtc`, and `struct drm_device` declarations from includers. It is consumed by both legacy VOP and VOP2 drivers.

## Risks and Edge Cases

The disabled stub returning NULL is treated as "no RGB output"; callers must distinguish NULL from `ERR_PTR` in enabled builds. Include ordering must provide type declarations.

## Test Signals

Build with `CONFIG_ROCKCHIP_RGB=y` and disabled. Runtime tests should confirm VOP/VOP2 tolerate NULL stubs and properly bind/fini real RGB helpers when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_rgb.h -->
