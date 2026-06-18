# subset-b-003755 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_dispc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_dispc.c

## Purpose

`tidss_dispc.c` is the hardware abstraction for the TI DSS display controller used by the `tidss` DRM driver. It describes SoC-specific DISPC feature tables, maps named platform resources, programs video ports, overlays, planes, scaling filters, color conversion, gamma/CTM state, interrupt masks, OLDI control bits, and runtime power transitions.

## Important APIs, Types, and Functions

- SoC feature descriptors: `dispc_k2g_feats`, `dispc_am625_feats`, `dispc_am62a7_feats`, `dispc_am62l_feats`, `dispc_am65x_feats`, and `dispc_j721e_feats` define register maps, VP/OVR/resource names, bus types, plane order, scaling limits, gamma support, and hardware plane IDs.
- `struct dispc_device`: private runtime state for mapped common/VID/OVR/VP register bases, VP clocks, OLDI syscon, feature pointer, format list, bandwidth limit, and errata flags.
- IRQ API: `dispc_read_and_clear_irqstatus()` and `dispc_set_irqenable()` dispatch to K2G or K3 register layouts and translate raw VP/VID bits into the packed `dispc_irq_t` layout from `tidss_irq.h`.
- VP API: `dispc_vp_prepare()`, `dispc_vp_enable()`, `dispc_vp_disable()`, `dispc_vp_unprepare()`, `dispc_vp_go()`, `dispc_vp_mode_valid()`, and clock helpers program timing, polarity, bus width, clock rate, and GO/enable bits.
- Plane API: `dispc_plane_check()`, `dispc_plane_setup()`, `dispc_plane_enable()`, and `dispc_plane_formats()` validate scaling/CSC support and program DMA base addresses, increments, picture/output sizes, FIR coefficients, CSC, alpha, and premultiplied-alpha state.
- Color/scaler helpers: `dispc_vid_calc_scaling()`, `tidss_get_scale_coefs()` integration, `dispc_find_csc()`, gamma table writers, and CTM-to-CSC conversion routines implement the display processing math.
- Lifecycle API: `dispc_init()`, `dispc_remove()`, `dispc_runtime_suspend()`, and `dispc_runtime_resume()` allocate resources, initialize hardware, and restore register state after PM.

## Control Flow

Probe enters through `dispc_init()`. It selects the already matched feature table, configures DMA masks, allocates `struct dispc_device`, applies errata filtering to the FourCC list, installs the feature-specific common register map, ioremaps common/VID/OVR/VP resources by the names in the feature table, acquires VP and functional clocks, optionally finds AM65x OLDI syscon control, reads `max-memory-bandwidth`, soft-resets the controller, and finally stores `tidss->dispc`.

Atomic modeset code calls into the VP and plane APIs. A CRTC new modeset programs the VP with bus format, OLDI data width if needed, horizontal/vertical timing, polarity, screen size, default color, gamma table, and CTM. Plane update code calls `dispc_plane_setup()`, which recalculates scaling, maps DRM FourCCs to DISPC format codes, writes DMA addresses for one- or two-plane buffers, computes row/pixel increments with decimation, sets scaler registers and coefficients, configures YUV-to-RGB CSC where required, and updates alpha/blending fields.

Interrupt handling is split by hardware generation. K2G has per-VP/per-VID IRQ registers under VP/VID bases plus a top-level status; K3-style devices use common-space per-VP/per-VID status and enable registers. Both paths clear statuses around enable-mask transitions to avoid stale IRQ delivery.

## State and Persistence Behavior

The feature table is immutable per device and controls all register layout decisions. `struct dispc_device` persists for the platform device lifetime and owns devm-managed mappings, clocks, gamma tables, and the generated FourCC list. Hardware state is volatile across runtime suspend; `dispc_runtime_resume()` re-enables `fclk`, logs reset/idle status, calls `dispc_initial_config()`, marks `is_enabled`, and restores IRQ enables through `tidss_irq_resume()`. Gamma tables are kept in memory per VP and rewritten when color management changes or after resume setup paths.

## Dependencies and Integration Points

The file depends on Linux clock, DMA, regmap/syscon, runtime PM, OF, SoC matching, and MMIO helpers. It integrates upward with `tidss_crtc.c`, `tidss_plane.c`, `tidss_irq.c`, `tidss_oldi.c`, and `tidss_kms.c`; downward it consumes `tidss_dispc_regs.h`, `tidss_irq.h`, and scale coefficients. DRM integration uses format metadata, DMA framebuffer helpers, color encoding/range/CTM/gamma objects, and mode validation enums.

## Risks and Edge Cases

- `dispc_common_regmap` is file-global, so it assumes one active register map at a time. Multiple TIDSS devices with different subrevisions would share this pointer.
- Several hardware waits use tight count loops for OLDI reset without `cpu_relax()` or timeout based on time; behavior depends on CPU speed.
- `dispc_plane_setup()` calls `dispc_vid_calc_scaling()` but does not check its return, relying on atomic check to have rejected invalid states.
- CTM conversion clamps coefficient formats differently for K2G and K3; color changes need hardware comparison on each SoC family.
- The bandwidth check assumes 4 bytes per pixel and may be conservative or inaccurate for 16/24-bit and YUV formats.
- OLDI support is split between legacy AM65x handling in this file and the newer `tidss_oldi.c` bridge; bus-type and external-clock flags must remain consistent.
- Erratum i2000 disables all YUV formats for matched AM65x SR1.0 devices; tests need coverage that filtered formats reach plane creation.

## Test Signals

Useful signals include probe success on each compatible string, ioremap/clock/syscon failure handling, mode validation for porch/clock/bandwidth limits, plane validation for scaling and YUV CSC combinations, gamma/CTM programming with both 8-bit and 10-bit LUT hardware, IRQ enable/clear behavior under lock, runtime suspend/resume preserving display state, and real scanout tests for RGB, YUYV/UYVY/NV12, overlay z-order, alpha, and scaler ratios near hardware limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_dispc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_dispc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_dispc.h

## Purpose

`tidss_dispc.h` is the public contract between the TIDSS DRM/KMS code and the DISPC hardware layer. It defines feature-description types, SoC subrevision identifiers, VP bus types, errata/scaling capabilities, exported feature tables, and the DISPC operations used by CRTC, plane, IRQ, OLDI, and driver lifecycle code.

## Important APIs, Types, and Functions

- `enum tidss_gamma_type`, `struct tidss_vp_feat`, and `struct tidss_plane_feat` describe color-management and plane feature metadata.
- `struct dispc_features_scaling` captures scaling limits used by `dispc_vid_calc_scaling()`.
- `struct dispc_vid_info` maps logical TIDSS plane slots to hardware resource names, hardware IDs, and lite/non-lite capabilities.
- `enum dispc_vp_bus_type` distinguishes DPI, AM65x OLDI, internal, and tied-off VPs.
- `enum dispc_dss_subrevision` identifies supported DISPC generations.
- `struct dispc_features` aggregates resource names, register map pointer, VP/plane counts, bus types, plane order, and color/scaling features for a compatible device.
- Exported functions cover OLDI configuration, pixel-clock comparison, IRQ mask/status access, overlay programming, VP setup/clock/mode validation, runtime PM, plane check/setup/enable, format discovery, and DISPC init/remove.

## Control Flow

Platform matching in `tidss_drv.c` picks one of the exported `dispc_*_feats` objects and stores it in `tidss->feat`. `dispc_init()` then consumes that structure to map resources and initialize hardware. KMS setup asks `dispc_plane_formats()` for the filtered format list, `tidss_crtc` calls VP functions during modeset and flush, `tidss_plane` calls plane functions from atomic helpers, and `tidss_irq` calls the IRQ functions from its handler and vblank enable/disable paths.

## State and Persistence Behavior

The header keeps `struct dispc_device` opaque to most of the driver, so persistent state is owned by `tidss_dispc.c` while callers retain only a pointer in `struct tidss_device`. Feature-table objects are static constants and should not be mutated. The API assumes callers pass valid hardware VP and plane indices derived from the same feature table.

## Dependencies and Integration Points

The header includes DRM color-management definitions and `tidss_drv.h` for `struct tidss_device`, limits, and `dispc_irq_t`. It is included by nearly every TIDSS module and therefore acts as the cross-file ABI for DISPC programming.

## Risks and Edge Cases

- Feature arrays are fixed at `TIDSS_MAX_PORTS` and `TIDSS_MAX_PLANES`; adding hardware with more resources requires updating driver-wide limits.
- `struct tidss_plane_feat` is defined but not heavily consumed in the reviewed files, so feature declarations can drift from actual enforcement.
- Several APIs accept raw `u32` hardware indices with no type distinction between logical and hardware IDs.
- Opaque `struct dispc_device` prevents accidental mutation, but it also means callers depend on runtime checks and `WARN_ON()`s rather than compile-time shape validation.

## Test Signals

Build coverage should catch signature drift across all TIDSS modules. Runtime tests should ensure feature-table values match DT resource names, supported formats, VP clock names, bus types, and plane ordering for each compatible. API tests should exercise all public functions through atomic modesets, vblank toggles, suspend/resume, and OLDI setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_dispc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_dispc_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_dispc_regs.h

## Purpose

`tidss_dispc_regs.h` defines the DISPC register offset and bitfield vocabulary used by `tidss_dispc.c`. It supports per-SoC common-register relocation through an enum-indexed common register map, while VID, OVR, VP, OLDI, and AM65x IO-control offsets are encoded as fixed register-relative constants.

## Important APIs, Types, and Definitions

- `enum dispc_common_regs` enumerates common-block registers whose offsets vary across K2G, AM65x, J721E, and related SoCs.
- `REG(r)` maps common-register enum entries through the file-global `dispc_common_regmap` pointer defined in `tidss_dispc.c`.
- Common register macros cover revision, reset/status, top-level IRQ registers, per-VP/per-VID IRQ register bases, writeback IRQs, MFLAG, global output/buffer, CBA, secure/FBDC, and J721E connection routing.
- VID macros define attributes, DMA base/extension addresses, FIFO thresholds, CSC/FIR registers, picture/output sizes, increments, alpha, CLUT, safety, and J721E DMA buffer size.
- OVR macros define default/transparent colors and layer position/channel/enable fields, including the J721E alternate position register.
- VP macros define config/control/timing/polarity/size/gamma/CSC/safety/OLDI registers.
- OLDI bit definitions and `enum oldi_mode_reg_val` encode LVDS mapping, clone/dual-link, polarity, reset, enable, and AM65x IO-control power-down bits.

## Control Flow

Callers set `dispc_common_regmap` to the selected feature table's `common_regs` during `dispc_init()`. After that, macros such as `DSS_SYSSTATUS` or `DISPC_IRQENABLE_SET` expand to the correct common offset for the active hardware. VID/OVR/VP offsets are applied against already mapped per-block bases. Bitfield masks are used with `FIELD_PREP`, `FIELD_GET`, and local field-modify wrappers.

## State and Persistence Behavior

The header itself holds no state, but its `REG()` indirection depends on an external global pointer. Register writes persist in hardware until reset, runtime suspend loss, or later atomic updates. OLDI and safety macros represent hardware state that may be shared with bridge setup and system-control regmaps.

## Dependencies and Integration Points

It depends on kernel bitfield/bit macros through includers and is consumed primarily by `tidss_dispc.c`, with OLDI constants also used by `tidss_oldi.c`. It is tightly coupled to the feature-table common-register arrays in `tidss_dispc.c`.

## Risks and Edge Cases

- `REG()` has no bounds or NULL protection; using common macros before `dispc_common_regmap` is initialized would dereference invalid state.
- A missing entry in a feature common register array resolves to offset zero, which may alias a real register rather than failing obviously.
- Bitfield definitions encode hardware ABI; incorrect masks can silently corrupt adjacent fields.
- The AM65x and newer OLDI power/reset definitions live near VP register definitions, so maintainers must distinguish DISPC VP registers from external control-MMR registers.

## Test Signals

Hardware bring-up should verify register dumps for each supported compatible, especially common IRQ offsets and J721E connection routing. Static review should compare masks and offsets against TRMs. Runtime tests should validate reset/status, IRQ masking, timing fields, plane DMA extension registers, gamma table programming, and OLDI enable/disable bits on target hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_dispc_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_drv.c

## Purpose

`tidss_drv.c` is the platform DRM driver entry point for TI Keystone/TIDSS display controllers. It owns DRM device allocation, runtime/system PM plumbing, DISPC and OLDI initialization, modeset setup, IRQ installation, device registration, fbdev/client setup, and platform remove/shutdown ordering.

## Important APIs, Types, and Functions

- `tidss_runtime_get()` and `tidss_runtime_put()` wrap runtime PM resume/autosuspend for atomic commit paths.
- Runtime PM callbacks delegate to `dispc_runtime_suspend()` and `dispc_runtime_resume()`.
- System suspend/resume callbacks call `drm_mode_config_helper_suspend()` and `drm_mode_config_helper_resume()`.
- `tidss_driver` defines DRM features, DMA GEM/fbdev helper ops, file ops, release callback, and driver identity.
- `tidss_probe()` performs all platform initialization.
- `tidss_remove()` unregisters the DRM device, shuts down atomic state, removes IRQs, disables PM, deinitializes OLDI, and clears the DISPC pointer.
- `tidss_of_table` maps compatible strings to the `dispc_features` tables exported by `tidss_dispc.c`.

## Control Flow

Probe allocates `struct tidss_device` embedded around `struct drm_device`, stores the OF-matched feature table, sets platform drvdata, initializes the IRQ spinlock, initializes DISPC, initializes OLDI bridges, enables runtime PM with autosuspend, sets up modesetting, retrieves and installs the platform IRQ, initializes poll helpers, resets mode config, registers the DRM device, removes conflicting firmware/simple framebuffers, and starts DRM client setup. Error paths unwind IRQs, runtime PM, and OLDI state.

Remove unregisters first to prevent new users, then calls `drm_atomic_helper_shutdown()`, uninstalls IRQs, handles no-PM suspend fallback, disables autosuspend/runtime PM, deinitializes OLDI bridges, and marks the devm-managed DISPC pointer NULL. Shutdown only performs atomic shutdown.

## State and Persistence Behavior

`struct tidss_device` persists as the DRM private object. Runtime PM state is active during commits and autosuspended otherwise. `tidss_release()` finalizes polling, while most allocations are devm/drmm managed. `tidss->feat`, `tidss->dispc`, CRTC/plane arrays, OLDI array, IRQ number, IRQ mask, and external VP clock flags are shared across submodules.

## Dependencies and Integration Points

The file depends on DRM managed allocation, DMA GEM helpers, fbdev DMA helpers, DRM client setup, aperture conflict removal, platform OF matching, runtime PM, and module platform-driver helpers. It integrates directly with `tidss_dispc`, `tidss_oldi`, `tidss_kms`, and `tidss_irq`.

## Risks and Edge Cases

- `tidss_runtime_get()` warns on failure but still returns the PM error; callers must not ignore fatal PM failures in contexts where hardware access follows.
- `aperture_remove_all_conflicting_devices()` happens after `drm_dev_register()`, so a failure unregisters the DRM device but userspace may briefly observe it.
- Under `!CONFIG_PM`, manual DISPC resume/suspend paths must mirror runtime PM behavior.
- Probe error unwinding relies on devm/drmm for many resources; ordering mistakes can leave hardware enabled until device release.
- `tidss_shutdown()` passes platform drvdata to `drm_atomic_helper_shutdown()`, which is valid only because drvdata is a `struct tidss_device` embedding `struct drm_device` first? In this file `struct drm_device` is the first member, so the cast works through layout assumptions.

## Test Signals

Test probe and remove on every compatible, deferred panel/bridge probing, IRQ-not-found paths, runtime PM autosuspend while idle, suspend/resume with active scanout, fbdev takeover from firmware framebuffer, and no-PM kernel configurations. KASAN/lockdep should cover remove/shutdown ordering and PM usage during atomic commits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_drv.h

## Purpose

`tidss_drv.h` defines the shared TIDSS device state and driver-wide limits used by all TIDSS modules. It is the main internal header for cross-module access to the DRM device, platform device, DISPC pointer, feature table, KMS object arrays, OLDI bridges, and IRQ state.

## Important APIs, Types, and Definitions

- `TIDSS_MAX_PORTS`, `TIDSS_MAX_PLANES`, and `TIDSS_MAX_OLDI_TXES` bound array sizes across the driver.
- `typedef u32 dispc_irq_t` standardizes packed DISPC IRQ masks.
- `struct tidss_device` embeds `struct drm_device`, stores `struct device *dev`, selected `struct dispc_features *feat`, opaque `struct dispc_device *dispc`, external VP clock flags, CRTC/plane/OLDI arrays and counts, IRQ number, IRQ spinlock, and current IRQ mask.
- `to_tidss()` converts from `struct drm_device` to `struct tidss_device`.
- `tidss_runtime_get()` and `tidss_runtime_put()` are exported runtime PM helpers.

## Control Flow

`tidss_drv.c` allocates and populates `struct tidss_device`. `tidss_kms.c` appends CRTC and plane pointers during modeset initialization. `tidss_oldi.c` appends OLDI bridges and marks `is_ext_vp_clk[parent_vp]`. `tidss_irq.c` uses `irq_lock` and `irq_mask`; `tidss_dispc.c` reads features and external-clock flags; plane/CRTC helpers retrieve private state through `to_tidss()`.

## State and Persistence Behavior

This structure persists for the DRM device lifetime and is shared without deep encapsulation. KMS object counts only grow during initialization and are read afterward. IRQ state is protected by `irq_lock`. Runtime PM is not stored here directly but is controlled through `dev`.

## Dependencies and Integration Points

It includes Linux spinlocks and DRM device definitions, and forward declares `struct tidss_oldi`. It depends on `struct dispc_features` and `struct dispc_device` being visible or forward-declared by including order in users.

## Risks and Edge Cases

- Fixed-size arrays require feature-table counts to stay within limits.
- Public mutable fields increase risk of cross-module ordering bugs.
- `is_ext_vp_clk` changes DISPC pixel-clock validation semantics; OLDI init/deinit must keep it accurate.
- `dispc_irq_t` is 32-bit, so increasing packed IRQ layout beyond current VP/plane limits would require widening.

## Test Signals

Build tests should cover all TIDSS modules including this header. Runtime assertions should validate counts never exceed limits, IRQ mask updates happen under `irq_lock`, and OLDI deinit clears external clock flags. Suspend/resume and hot-unbind tests should watch for stale `dispc`, CRTC, plane, or OLDI pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_encoder.c

## Purpose

`tidss_encoder.c` creates the DRM encoder and bridge-connector chain for each TIDSS video port. It provides a small internal bridge that extracts display bus format/flags during atomic checks and forwards attach operations to the next bridge or panel bridge.

## Important APIs, Types, and Functions

- `struct tidss_encoder` embeds a DRM bridge, DRM encoder, connector pointer, next bridge pointer, and parent `struct tidss_device`.
- `tidss_bridge_attach()` attaches the next bridge after the TIDSS bridge.
- `tidss_bridge_atomic_check()` determines the input bus format and bus flags from the next bridge state or connector display info and stores them in `struct tidss_crtc_state`.
- `tidss_encoder_create()` allocates the bridge wrapper, initializes a simple encoder, attaches the bridge without creating a connector, creates a `drm_bridge_connector`, and attaches that connector to the encoder.

## Control Flow

`tidss_kms.c` discovers panel/bridge endpoints per VP, then calls `tidss_encoder_create()` after creating the corresponding CRTC. During atomic check, bridge state propagation runs before CRTC programming; this file writes `bus_format` and `bus_flags` into the TIDSS CRTC state so `dispc_vp_bus_check()` and `dispc_vp_prepare()` can program data width and polarities.

## State and Persistence Behavior

The encoder/bridge wrapper is devm/drmm managed and persists for the DRM device lifetime. The connector pointer is stored for ownership/reference only after `drm_bridge_connector_init()`. The bus format is not persistent in the encoder; it is copied into each atomic CRTC state.

## Dependencies and Integration Points

The file depends on DRM bridge, bridge connector, atomic helper bridge state, simple encoder helpers, connector display info, and `tidss_crtc_state`. It integrates with `tidss_kms.c` for creation and `tidss_dispc.c` for later VP bus programming.

## Risks and Edge Cases

- If neither the next bridge state nor connector display info provides bus formats, atomic check fails.
- Only the first connector bus format is used when there is no next bridge state.
- Bridge attach requires the caller to pass `DRM_BRIDGE_ATTACH_NO_CONNECTOR` semantics through the chain.
- Encoder type is supplied by KMS setup and must match bus type/panel connector type.

## Test Signals

Tests should cover panel bridge and external bridge chains, atomic bus-format negotiation, missing bus-format errors, connector attach failures, LVDS/DPI encoder type selection from KMS setup, and mode commits where bus flags affect VP polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_encoder.h

## Purpose

`tidss_encoder.h` exposes the TIDSS encoder creation API to KMS setup code. It is intentionally small: callers provide the parent device, downstream bridge, encoder type, and possible CRTC mask.

## Important APIs, Types, and Functions

- Includes DRM encoder definitions for encoder type and CRTC mask context.
- Forward declares `struct tidss_device`.
- Declares `tidss_encoder_create(struct tidss_device *tidss, struct drm_bridge *next_bridge, u32 encoder_type, u32 possible_crtcs)`.

## Control Flow

`tidss_kms.c` calls this function once for each discovered output pipe after creating the CRTC. The implementation allocates encoder/bridge/connector objects and hooks the output path into DRM bridge atomic checks.

## State and Persistence Behavior

The header holds no state. The created objects persist under DRM/devm management after a successful call.

## Dependencies and Integration Points

It links KMS pipe discovery with `tidss_encoder.c` and the DRM bridge ecosystem. The downstream bridge can represent a panel bridge, OLDI bridge, or other bridge obtained from DT graph discovery.

## Risks and Edge Cases

- The prototype uses raw `u32` for encoder type and mask, so invalid values are caught only by runtime paths.
- The header does not document whether `next_bridge` may be NULL; the implementation assumes a valid bridge for attach.

## Test Signals

Build coverage should catch signature changes. Runtime coverage should include successful encoder creation for DPI and LVDS paths and expected failures when the downstream bridge is absent or rejects attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_irq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_irq.c

## Purpose

`tidss_irq.c` manages the TIDSS interrupt mask and top-level IRQ handler. It enables/disables vblank IRQs, installs/uninstalls the platform IRQ, restores masks after resume, and dispatches packed DISPC status bits to CRTC and plane error handlers.

## Important APIs, Types, and Functions

- `tidss_irq_update()` writes `tidss->irq_mask` to DISPC and asserts that `irq_lock` is held.
- `tidss_irq_enable_vblank()` and `tidss_irq_disable_vblank()` update the even/odd VSYNC bits for a CRTC's hardware videoport.
- `tidss_irq_handler()` reads and clears DISPC status under `irq_lock`, then routes VP VSYNC, frame-done, sync-lost, and plane underflow statuses.
- `tidss_irq_resume()` rewrites the saved mask after DISPC runtime resume.
- `tidss_irq_install()` requests the IRQ, initializes `irq_mask` with always-on sync-lost, frame-done, and plane underflow bits, but leaves actual enable programming to later update/resume paths.
- `tidss_irq_uninstall()` frees the IRQ.

## Control Flow

After KMS objects are created, `tidss_probe()` calls `tidss_irq_install()`. During normal operation DRM vblank core calls enable/disable vblank callbacks in CRTC code, which delegate here. Hardware IRQs enter `tidss_irq_handler()`, which performs the MMIO read/clear atomically with respect to mask updates, then iterates currently registered CRTCs and planes to deliver events. Runtime resume calls `tidss_irq_resume()` after DISPC initial config.

## State and Persistence Behavior

The persistent state is `tidss->irq_mask`, protected by `tidss->irq_lock`. CRTC/plane arrays are read locklessly after initialization. DISPC IRQ enable registers are hardware state that is lost across runtime suspend and restored from `irq_mask`.

## Dependencies and Integration Points

The file depends on Linux request/free IRQ and DRM device/private conversion. It integrates with `tidss_dispc.c` for hardware status/mask access, `tidss_crtc.c` for vblank/framedone/sync-lost callbacks, and `tidss_plane.c` for FIFO underflow reporting.

## Risks and Edge Cases

- `tidss_irq_install()` computes the initial mask but does not call `tidss_irq_update()` immediately; initial enable depends on resume or later vblank operations.
- The handler always returns `IRQ_HANDLED` even if no known bits were set.
- CRTC and plane arrays must be fully initialized before installation; otherwise the initial mask and dispatch loops are wrong.
- Plane underflow errors are routed by hardware plane ID, so feature-table plane ordering must match IRQ packing.

## Test Signals

Signals include vblank enable/disable toggling only the target VP bits, IRQ dispatch producing page-flip/vblank completion, sync-lost and FIFO-underflow ratelimited logs, runtime resume restoring masks, and no lockdep warnings for concurrent vblank toggles and interrupt handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_irq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_irq.h

## Purpose

`tidss_irq.h` defines the packed software IRQ status layout used by TIDSS. It maps device, writeback, video-port, and plane interrupt bits into a single `dispc_irq_t` value and declares the IRQ-management functions implemented by `tidss_irq.c`.

## Important APIs, Types, and Definitions

- Device/writeback masks include `DSS_IRQ_DEVICE_FRAMEDONEWB`, `DSS_IRQ_DEVICE_WBBUFFEROVERFLOW`, `DSS_IRQ_DEVICE_WBUNCOMPLETEERROR`, and `DSS_IRQ_DEVICE_WB_MASK`.
- Bit-position helpers `DSS_IRQ_VP_BIT_N()` and `DSS_IRQ_PLANE_BIT_N()` allocate four bits per VP and one bit per plane.
- Mask helpers `DSS_IRQ_VP_MASK()` and `DSS_IRQ_PLANE_MASK()` select all bits for a VP or plane.
- VP event macros cover frame-done, even/odd VSYNC, and sync-lost.
- Plane event macro covers FIFO underflow.
- Public functions declare vblank enable/disable, IRQ install/uninstall, and resume-mask restore.

## Control Flow

`tidss_dispc.c` translates raw hardware bits to these packed macros. `tidss_irq.c` stores and updates masks in this representation and dispatches callbacks based on it. CRTC vblank code calls the enable/disable functions declared here.

## State and Persistence Behavior

The header has no state; the packed values are stored in `tidss->irq_mask` and transient handler status variables. The layout assumes the configured `TIDSS_MAX_PORTS` and `TIDSS_MAX_PLANES` fit inside `u32`.

## Dependencies and Integration Points

It includes Linux types and `tidss_drv.h` for `dispc_irq_t` and max resource counts. It is the common dependency between the DISPC hardware translator and high-level IRQ handler.

## Risks and Edge Cases

- The comment describes a fixed bit layout; increasing resource limits can overflow or collide bits.
- `DSS_IRQ_PLANE_MASK()` currently returns a single-bit `GENMASK` and is equivalent to the underflow bit; future multi-bit plane events would require adjustment.
- Device/writeback bits are defined but not handled in the reviewed TIDSS IRQ dispatcher.

## Test Signals

Unit-style checks can validate bit positions and masks for all max VPs/planes. Integration tests should confirm that DISPC K2G and K3 translations produce the same packed bits for equivalent events and that vblank toggles affect only VSYNC bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_kms.c

## Purpose

`tidss_kms.c` initializes DRM mode configuration and assembles TIDSS KMS objects from DT graph outputs. It also customizes atomic commit ordering so bridge pre-enable runs before CRTC enable, adds plane-position state propagation, and sets global DRM mode limits.

## Important APIs, Types, and Functions

- `tidss_atomic_commit_tail()` open-codes atomic helper sequencing around TIDSS/OLDI bridge requirements and wraps hardware access in runtime PM get/put.
- `tidss_atomic_check()` runs the generic atomic check, marks CRTC state when plane position changes, and adds affected planes when zpos or position changes.
- `tidss_dispc_modeset_init()` discovers panel/bridge endpoints, creates primary planes, CRTCs, encoders/connectors, and leftover overlay planes.
- `tidss_modeset_init()` initializes mode config, installs funcs/helper funcs, runs DISPC modeset setup, initializes vblank, and resets mode config.

## Control Flow

Driver probe calls `tidss_modeset_init()` after DISPC and OLDI setup. The function initializes mode config, then `tidss_dispc_modeset_init()` scans each VP port through `drm_of_find_panel_or_bridge()`. Direct panels are wrapped with panel bridges after connector-type compatibility checks. For each output pipe it creates one primary plane using the next hardware plane from `vid_order`, creates a CRTC for the VP, and creates an encoder bound to the downstream bridge. Remaining hardware planes become overlays available to all CRTCs.

Atomic commits use `tidss_atomic_commit_tail()` instead of the standard tail because the bridge chain must be prepared before the CRTC is enabled and disabled after the CRTC is disabled. Plane commits happen before bridge pre-enable/CRTC enable, then writebacks, hw_done, flip waits, cleanup, and runtime PM put.

## State and Persistence Behavior

KMS object arrays and counts in `struct tidss_device` are populated during initialization and remain stable. Plane-position changes are stored in TIDSS-specific CRTC state for a single atomic transaction. Runtime PM keeps DISPC active during commit and allows autosuspend afterward.

## Dependencies and Integration Points

This file depends on DRM atomic, bridge/panel discovery, GEM framebuffer creation, vblank initialization, and panel bridge helpers. It integrates with `tidss_plane_create()`, `tidss_crtc_create()`, `tidss_encoder_create()`, and `dispc_plane_formats()`.

## Risks and Edge Cases

- If no output pipes are discovered, `crtc_mask` becomes zero and overlay creation would create unusable planes; probe behavior depends on downstream discovery.
- `crtc_mask = (1 << num_pipes) - 1` assumes `num_pipes` fits the bit width and DRM CRTC indexing order matches creation order.
- Panel connector-type checks cover direct panel paths, but external bridges rely on bridge negotiation.
- Plane order and count depend on feature-table `vid_order`; mismatches can assign lite/non-lite planes unexpectedly.
- Custom commit sequencing must track DRM helper API changes over time.

## Test Signals

Tests should cover DT graphs with zero, one, and multiple outputs; direct DPI panels; OLDI bridges; deferred bridge probing; primary and overlay plane creation; zpos/position updates; atomic modeset sequencing around bridge pre/post hooks; and vblank initialization with the number of discovered CRTCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_kms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_kms.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_kms.h

## Purpose

`tidss_kms.h` exposes the single KMS initialization entry point used by the TIDSS platform driver.

## Important APIs, Types, and Functions

- Forward declares `struct tidss_device`.
- Declares `int tidss_modeset_init(struct tidss_device *tidss)`.

## Control Flow

`tidss_drv.c` calls `tidss_modeset_init()` after DISPC and OLDI initialization and before IRQ installation and DRM registration. The implementation creates mode config, CRTCs, planes, encoders, connectors, and vblank state.

## State and Persistence Behavior

The header has no state. A successful call populates persistent KMS arrays inside `struct tidss_device` and mode-config state inside the embedded DRM device.

## Dependencies and Integration Points

It is the boundary between platform-driver probe and TIDSS KMS object construction.

## Risks and Edge Cases

- The declaration hides that DISPC and OLDI must already be initialized.
- Callers must handle `-EPROBE_DEFER` without treating it as a hard device failure.

## Test Signals

Probe tests should verify successful and deferred `tidss_modeset_init()` behavior, and build tests should catch signature drift between the header and implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_kms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_oldi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_oldi.c

## Purpose

`tidss_oldi.c` implements a DRM bridge for TIDSS OLDI/LVDS transmitters described under the `oldi-transmitters` DT node. It configures OLDI link mode, serial clock, IO power, input bus-format negotiation, and bridge-chain attachment for single-link and dual-link LVDS paths.

## Important APIs, Types, and Functions

- `struct tidss_oldi` stores parent TIDSS device, bridge, downstream bridge, link type, selected bus format, OLDI instance IDs, parent VP, serial clock, and IO-control regmap.
- `oldi_bus_formats[]` maps LVDS media bus formats to data width, OLDI map field, and TIDSS input bus format.
- Bridge funcs: `tidss_oldi_bridge_attach()`, `tidss_oldi_atomic_pre_enable()`, `tidss_oldi_atomic_post_disable()`, `tidss_oldi_atomic_get_input_bus_fmts()`, and `tidss_oldi_mode_valid()`.
- Hardware helpers: `tidss_oldi_set_serial_clk()`, `tidss_oldi_tx_power()`, and `tidss_oldi_config()`.
- DT helpers: `get_oldi_mode()` resolves single, clone, dual, and secondary modes; `get_parent_dss_vp()` finds the connected DSS VP.
- Lifecycle: `tidss_oldi_init()` discovers/registers bridges; `tidss_oldi_deinit()` removes them and clears external-clock flags.

## Control Flow

Probe calls `tidss_oldi_init()` before modeset discovery. The function finds `oldi-transmitters`, iterates available child OLDI nodes, identifies their parent DSS VP through graph port 0, fetches downstream sink bridge from port 1, determines companion/link mode from `ti,companion-oldi`, `ti,secondary-oldi`, and LVDS dual-link pixel order, rejects unsupported and current clone configurations, allocates/registers a bridge for usable primary OLDI nodes, acquires IO-control regmap and serial clock, records the bridge in `tidss->oldis`, and marks the parent VP as externally clocked.

During atomic bus negotiation, the bridge maps output LVDS format to the DSS input RGB format and stores the selected OLDI bus format. Pre-enable configures the DISPC OLDI bits for single/dual link, sets the serial clock to seven times pixel clock, and powers IO. Post-disable powers IO down, sets serial clock to the idle frequency, and clears DISPC OLDI config.

## State and Persistence Behavior

Each registered OLDI bridge persists in `tidss->oldis[]`. `oldi->bus_format` is selected during atomic bus-format negotiation and later consumed by pre-enable, so a valid negotiation must precede enable. `tidss->is_ext_vp_clk[parent_vp]` persists while the OLDI bridge exists and tells DISPC to skip internal VP clock checks. Hardware OLDI config and IO power are enabled only during active bridge state.

## Dependencies and Integration Points

The file depends on OF graph helpers, DRM bridge APIs, LVDS dual-link parsing, clocks, syscon regmap, media bus formats, `tidss_dispc` OLDI configuration helpers, and OLDI bit definitions from `tidss_dispc_regs.h`. KMS discovery later sees these registered bridges as downstream endpoints.

## Risks and Edge Cases

- Clone mode code exists for hardware power/config but initialization rejects clone because DRM cannot represent the needed dual encoder pipelines here.
- `companion_instance` is initialized once before the loop; failed or skipped nodes must not leak stale values into later nodes.
- `of_clk_get_by_name()` obtains a clock reference but deinit does not explicitly `clk_put()`; managed lifetime depends on OF clock handling and device cleanup.
- Pre-enable ignores return values from `tidss_oldi_config()` and `tidss_oldi_set_serial_clk()`, so enable can continue after logged failures.
- `oldi->bus_format` can be NULL if the downstream bridge does not call `atomic_get_input_bus_fmts()` before pre-enable.

## Test Signals

Tests should cover single-link, primary/secondary dual-link, rejected clone, invalid companion reg, missing downstream bridge, missing IO syscon/serial clock, unsupported output bus formats, serial clock round-rate validation, pre-enable/post-disable register changes, and deinit clearing bridges and external VP clock flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_oldi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_oldi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_oldi.h

## Purpose

`tidss_oldi.h` defines the OLDI bridge public lifecycle API and DT/control-register constants used by `tidss_oldi.c`.

## Important APIs, Types, and Definitions

- `OLDI_INPUT_PORT` and `OLDI_OUTPUT_PORT` define graph port indices used to connect OLDI transmitters to DSS and downstream sinks.
- `OLDI_PD_CTRL` and `OLDI_LB_CTRL` are control-MMR register offsets.
- `OLDI_PWRDOWN_TX(n)` and `OLDI_PWRDN_BG` define IO power-down bits.
- `enum tidss_oldi_link_type` distinguishes unsupported, single-link, clone, secondary clone, dual-link, and secondary dual-link modes.
- Declares `tidss_oldi_init()` and `tidss_oldi_deinit()`.

## Control Flow

The platform driver calls `tidss_oldi_init()` before modeset setup and `tidss_oldi_deinit()` on error/remove. The implementation uses these constants while parsing DT and toggling IO power around bridge enable/disable.

## State and Persistence Behavior

The header has no state. Link-type values persist inside each `struct tidss_oldi` allocated by the implementation.

## Dependencies and Integration Points

It includes `tidss_drv.h` for `struct tidss_device` and driver limits. It is consumed by the platform driver and the OLDI implementation.

## Risks and Edge Cases

- Control-MMR offsets and power bits are SoC ABI; incorrect values can power the wrong OLDI transmitter or bandgap.
- Link-type enum values are used in switches; adding a mode requires updates in init, power, config, and bridge callbacks.

## Test Signals

Build tests should cover the lifecycle prototypes. Runtime tests should verify DT graph port numbers, power bit mapping for transmitter 0/1, and correct handling of each link-type switch case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_oldi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_plane.c

## Purpose

`tidss_plane.c` implements DRM plane objects for TIDSS. It validates atomic plane state against DRM helper constraints and DISPC hardware limits, programs visible planes through DISPC, disables invisible planes, reports FIFO underflows, and creates zpos/color/alpha/blend properties.

## Important APIs, Types, and Functions

- `tidss_plane_error_irq()` logs underflow errors for the hardware plane ID.
- `tidss_plane_atomic_check()` handles detached planes, invokes `drm_atomic_helper_check_plane_state()`, validates chroma subsampling alignment, and calls `dispc_plane_check()` for visible states.
- `tidss_plane_atomic_update()` calls `dispc_plane_setup()` for visible planes or disables invisible planes.
- `tidss_plane_atomic_enable()` and `_disable()` toggle DISPC plane enable bits.
- `tidss_plane_create()` allocates `struct tidss_plane`, initializes a universal plane, installs primary or overlay helper funcs, and creates zpos, color encoding/range, alpha, and blend-mode properties.

## Control Flow

KMS setup creates primary planes first and overlays later. During atomic check, the plane ensures source coordinates and width align to format subsampling, visible states satisfy generic scaling/position constraints, and DISPC accepts the requested scaling/CSC. During commit, update writes plane registers while enable/disable toggles the hardware layer state. Primary planes additionally expose `get_scanout_buffer` through DMA framebuffer helpers.

## State and Persistence Behavior

`struct tidss_plane` stores the persistent DRM plane and immutable hardware plane ID. Atomic state remains DRM-managed. Plane hardware state persists until the next atomic update, disable, or DISPC reset. Object destruction calls `drm_plane_cleanup()` and frees the allocation.

## Dependencies and Integration Points

The file depends on DRM atomic helpers, blend/color properties, DMA scanout helpers, FourCC format metadata, and `tidss_dispc` plane APIs. It integrates with `tidss_kms.c` for creation and `tidss_irq.c` for underflow reporting.

## Risks and Edge Cases

- `drm_atomic_helper_check_plane_state()` is called with `INT_MAX` scaling limits, so true scaler limits rely on the later DISPC check.
- The update path trusts that invalid scaling was rejected during check.
- The custom `drm_plane_destroy()` name shadows a common DRM concept; local static scope avoids symbol conflict but can confuse readers.
- Allocation uses plain `kzalloc_obj()` and manual free rather than drmm allocation, so error and cleanup paths must stay correct.
- Color properties are created for all planes regardless of hardware lite/non-lite differences; DISPC validation is the effective guard.

## Test Signals

Plane tests should cover detach visibility reset, subsampling-aligned and misaligned YUV source rectangles, lite-plane scaling rejection, scaler limit rejection, CSC property combinations, zpos ordering, alpha/blend modes, primary scanout buffer export, underflow IRQ logging, and cleanup on property creation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_plane.h

## Purpose

`tidss_plane.h` defines the TIDSS plane wrapper and plane creation/error APIs shared between KMS setup, DISPC programming, and IRQ handling.

## Important APIs, Types, and Functions

- `to_tidss_plane()` converts `struct drm_plane *` to `struct tidss_plane *`.
- `struct tidss_plane` embeds a DRM plane and stores the hardware plane ID.
- `tidss_plane_create()` creates a primary or overlay plane with the supplied CRTC mask and format list.
- `tidss_plane_error_irq()` reports hardware underflow for a plane.

## Control Flow

`tidss_kms.c` creates planes through this header. `tidss_irq.c` converts stored plane pointers through `to_tidss_plane()` to match IRQ bits and logs errors through `tidss_plane_error_irq()`. Plane helper callbacks use the hardware ID to call DISPC plane APIs.

## State and Persistence Behavior

The hardware plane ID is persistent and immutable after creation. DRM plane state is managed by the DRM core.

## Dependencies and Integration Points

It includes DRM plane definitions and forward declares `struct tidss_device`. It is consumed by KMS, IRQ, and plane implementation files.

## Risks and Edge Cases

- The hardware ID is a raw `u32`; caller-supplied feature-table ordering must be correct.
- `to_tidss_plane()` assumes the pointer really belongs to a TIDSS plane.

## Test Signals

Build coverage should catch API changes. Runtime coverage should verify plane IDs match DISPC registers and IRQ underflow bits for each feature-table `vid_order`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_scale_coefs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_scale_coefs.c

## Purpose

`tidss_scale_coefs.c` provides the FIR scaler coefficient tables used by TIDSS DISPC video plane scaling. It maps a computed FIR increment to one of several 3-tap or 5-tap coefficient sets.

## Important APIs, Types, and Functions

- Static `coef5_m*` tables define 5-tap coefficient arrays for scaling-factor buckets.
- Static `coef3_m*` tables define 3-tap coefficient arrays for wider-input or lower-resource paths.
- `tidss_get_scale_coefs(struct device *dev, u32 firinc, bool five_taps)` converts `firinc` into `inc = firinc / 0x40000`, selects the matching bucket, and returns either the 3-tap or 5-tap table.
- Upscaling more than 2x intentionally maps to M11/M16/M19 tables instead of the M8 table to reduce observed blockiness/outlines.

## Control Flow

`tidss_dispc.c` calculates FIR increments from input/output dimensions in `dispc_vid_calc_scaling()`. For horizontal, vertical, and UV scaling paths it calls `tidss_get_scale_coefs()`, then `dispc_vid_write_fir_coefs()` writes the returned coefficient arrays into hardware phase registers during plane setup.

## State and Persistence Behavior

All coefficient tables are static constant data. Returned pointers are stable for the kernel lifetime. Hardware persistence occurs only after DISPC writes the selected table into plane registers.

## Dependencies and Integration Points

The file depends on Linux device logging and fixed-width types from the header. It is tightly coupled to DISPC FIR register programming and the scaling-limit calculations in `tidss_dispc.c`.

## Risks and Edge Cases

- If `firinc` falls outside all buckets, the function logs an error and returns NULL; the DISPC writer logs another error and skips writing coefficients.
- Bucket boundaries encode empirical quality choices; changing them can affect visible scaler output.
- Tables come from an interpolation script noted in comments, but the script is not present here for regeneration or verification.
- 3-tap tables leave `c2` zero-initialized through struct initialization, which is intentional but easy to misread.

## Test Signals

Tests should cover bucket selection at every boundary, 3-tap versus 5-tap selection, upscaling special buckets, invalid `firinc` error logging, and visual/hardware validation for representative scaler ratios including NV12 chroma scaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_scale_coefs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_scale_coefs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_scale_coefs.h

## Purpose

`tidss_scale_coefs.h` declares the scaler coefficient data shape and lookup function used by the TIDSS DISPC scaler.

## Important APIs, Types, and Functions

- `struct tidss_scale_coefs` stores `c2[16]`, `c1[16]`, and `c0[9]` coefficient arrays matching the hardware phase layout.
- `tidss_get_scale_coefs()` returns a const table for a FIR increment and 3-tap/5-tap choice.

## Control Flow

`tidss_dispc.c` includes this header, obtains coefficient tables during scaling calculations, and writes the arrays into DISPC FIR coefficient registers.

## State and Persistence Behavior

The header has no state. Returned coefficient tables are immutable static data in the implementation.

## Dependencies and Integration Points

It includes Linux types and forward declares `struct device` for error logging in the lookup function. It is a narrow interface between scaler math and coefficient storage.

## Risks and Edge Cases

- Array sizes must stay synchronized with hardware writer loops: 16 phases for `c1/c2` and 9 entries for `c0`.
- No metadata identifies which ratio bucket was chosen; callers can only observe pointer identity or logs.

## Test Signals

Build tests should catch struct-size mismatches with writer code. Runtime tests should verify coefficient lookup never returns NULL for all ratios accepted by `dispc_plane_check()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_scale_coefs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/Kconfig

## Purpose

`tilcdc/Kconfig` exposes configuration options for the TI LCDC DRM driver and its legacy panel-binding compatibility layer.

## Important APIs, Types, and Functions

- `DRM_TILCDC` is a tristate option for TI LCDC display controllers. It depends on `DRM`, `OF`, and `ARM`, and selects DRM client, KMS, DMA GEM, bridge, display helper, bridge connector, panel bridge, videomode, and backlight support.
- `DRM_TILCDC_PANEL_LEGACY` is a bool compatibility option for legacy `ti,tilcdc,panel` DT blobs. It depends on `DRM_TILCDC`, OF, backlight, and PM, and selects OF overlay and `DRM_PANEL_SIMPLE`.

## Control Flow

Kernel configuration enables compilation of `tilcdc.o` through the Makefile. If the legacy option is enabled, an early initcall module applies a DT overlay and property migration before normal device probing.

## State and Persistence Behavior

Kconfig choices persist in the kernel build configuration. The legacy option defaults to enabled when dependencies are met, which affects boot-time DT mutation behavior.

## Dependencies and Integration Points

These options integrate with the DRM subsystem, OF graph/device-tree probing, panel/bridge helpers, DMA GEM memory management, and backlight/videomode helpers. `DRM_TILCDC_PANEL_LEGACY` also integrates with OF overlay infrastructure and the simple panel driver.

## Risks and Edge Cases

- `DRM_TILCDC` is restricted to ARM despite possible compile-test interest; portability requires config changes.
- The legacy option defaults on and mutates the live DT; systems with unexpected legacy-compatible nodes can be affected.
- Selecting helper subsystems pulls in broad DRM infrastructure, so dependency regressions surface at build time.

## Test Signals

Kconfig tests should cover built-in, module, and disabled combinations; legacy enabled/disabled builds; missing OF overlay dependencies; and boot tests with legacy and modern panel bindings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/Makefile

## Purpose

`tilcdc/Makefile` defines how the TI LCDC DRM driver and legacy panel overlay support are built.

## Important APIs, Types, and Functions

- Adds `-Werror` to `ccflags-y` unless `KCFLAGS` already contains `-W`.
- Builds the composite `tilcdc.o` from `tilcdc_plane.o`, `tilcdc_crtc.o`, `tilcdc_encoder.o`, and `tilcdc_drv.o`.
- Adds `tilcdc_panel_legacy.o` and the wrapped `tilcdc_panel_legacy.dtbo.o` when `CONFIG_DRM_TILCDC_PANEL_LEGACY` is enabled.

## Control Flow

Kbuild uses `obj-$(CONFIG_DRM_TILCDC)` to include the main driver object and `obj-$(CONFIG_DRM_TILCDC_PANEL_LEGACY)` for the legacy helper and embedded DT overlay.

## State and Persistence Behavior

The Makefile controls build artifacts only. The embedded DTBO symbols consumed by `tilcdc_panel_legacy.c` come from the `.dtbo.o` object listed here.

## Dependencies and Integration Points

It integrates with Kbuild composite-object rules, Kconfig symbols, and DT overlay wrapping via kernel build scripts.

## Risks and Edge Cases

- Enforced `-Werror` can break builds when compiler warnings change.
- The legacy C file depends on begin/end symbols generated only if the DTBO object is built; removing that object breaks linking.

## Test Signals

Build tests should cover different compilers and warning flags, main driver as built-in/module, and legacy overlay enabled to ensure DTBO symbol generation and linking succeed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_crtc.c

## Purpose

`tilcdc_crtc.c` implements the single CRTC for the TI LCDC DRM driver. It programs LCDC scanout DMA, timings, pixel clock, palette loading, raster enable/disable, page flips, vblank IRQs, sync-lost recovery, and mode validation for LCDC revision 1 and 2 hardware.

## Important APIs, Types, and Functions

- `struct tilcdc_crtc` embeds the DRM CRTC and stores primary plane pointer, pending event, enable/shutdown state, frame-done wait state, IRQ lock, last vblank timestamp, frame duration, deferred framebuffer, sync-lost recovery state, palette DMA memory, and recovery work.
- `set_scanout()` writes framebuffer base/ceiling DMA addresses, using a 64-bit write where available to avoid torn address updates.
- `tilcdc_crtc_load_palette()` loads the required 32-byte true-color palette and waits for palette-loaded IRQ.
- `tilcdc_crtc_set_clk()` sets functional clock/divider and rev2 clock enables.
- `tilcdc_crtc_set_mode()` programs DMA, timing, raster format, polarity, clock, palette, scanout, and cached hardware mode.
- Enable/disable paths: `tilcdc_crtc_enable()`, `tilcdc_crtc_off()`, atomic wrappers, and shutdown helper.
- Flip path: `tilcdc_crtc_update_fb()` either writes scanout immediately or defers to next vblank if too close to frame end.
- IRQ path: `tilcdc_crtc_irq()` handles EOF/vblank, palette load, FIFO underflow, sync lost, frame done, and rev2 end-of-interrupt indication.
- `tilcdc_crtc_create()` allocates the primary plane and CRTC, DMA palette, locks, waitqueue, and managed destroy action.

## Control Flow

Probe creates the CRTC before encoder setup. On atomic enable, the CRTC runtime-resumes hardware, resets rev2 if needed, programs mode registers, enables IRQs, starts raster DMA, and turns DRM vblank on. Plane updates call `tilcdc_crtc_update_fb()`; if the next vblank is near, the new framebuffer is stored in `next_fb` and swapped from the EOF IRQ. Disable clears raster enable, waits for frame-done, sends pending events, disables IRQs, turns vblank off, and drops runtime PM.

Mode validation rejects unsupported width, width not multiple of 16, height over 2048, porch/sync fields outside register ranges, pixel clocks above DT/default limits, and bandwidth above `max_bandwidth`. Mode fixup adjusts HSKEW and horizontal sync polarity for LCDC-specific sync alignment.

## State and Persistence Behavior

The CRTC object persists under DRM managed allocation. Hardware register state is set on enable and lost on reset/PM. Palette memory is coherent DMA memory and persists for device lifetime. `last_vblank`, `next_fb`, pending event, `frame_done`, and sync-lost counters are transient runtime state protected by locks or waitqueues.

## Dependencies and Integration Points

The file depends on DRM atomic/vblank helpers, DMA GEM framebuffer helpers, runtime PM, clocks through the driver private struct, OF graph node ownership, and register helpers from `tilcdc_regs.h`. It integrates with `tilcdc_plane.c` through `tilcdc_crtc_update_fb()` and with `tilcdc_drv.c` through IRQ forwarding, cpufreq clock update, shutdown, and create APIs.

## Risks and Edge Cases

- Several PM calls use `pm_runtime_get_sync()` without checking negative returns.
- `mode->flags == DRM_BUS_FLAG_*` comparisons look like bus-flag checks but `mode->flags` usually contains DRM mode flags; this can miss combined flags or represent a semantic mismatch.
- `tilcdc_crtc_disable_vblank()` clears `LCDC_INT_ENABLE_SET_REG` for rev2 rather than writing the clear register, which should be reviewed against hardware expectations.
- Page-flip event state is split between `tilcdc_crtc->event` and `crtc->state->event`; races are mitigated by locks but need testing.
- Sync-lost flood recovery queues work on `system_wq`, while the driver also owns `priv->wq`; teardown flushes `priv->wq` but not necessarily `system_wq`.
- Palette load timeout leaves the function continuing to raster setup after logging.

## Test Signals

Tests should cover rev1 and rev2 enable/disable, palette-loaded IRQ timeout/success, mode validation boundaries, pixel-clock fallback divider, page flips just before and far from vblank, frame-done wait timeout, FIFO underflow logs, sync-lost flood recovery, cpufreq-triggered clock updates, shutdown with active scanout, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_drv.c

## Purpose

`tilcdc_drv.c` is the platform DRM driver for TI LCDC controllers. It allocates the driver-private DRM device, discovers hardware revision and pixel formats, reads DT limits, initializes CRTC/encoder/vblank/IRQ/debugfs/client setup, and handles suspend/resume, remove, shutdown, and optional cpufreq notifications.

## Important APIs, Types, and Functions

- `enum tilcdc_variant` distinguishes AM33xx and DA850 for FIFO threshold defaults.
- Pixel-format arrays select rev1, straight wiring, crossed wiring, and legacy wiring formats.
- `tilcdc_atomic_check()` reruns modeset checks after plane checks because plane format changes can set `mode_changed`.
- `modeset_init()` configures mode limits and mode config funcs.
- `cpufreq_transition()` updates CRTC clock after CPU frequency changes when enabled.
- `tilcdc_irq_install()` and `_uninstall()` request/free the platform IRQ.
- Debugfs helpers expose register dumps and DRM MM state.
- `tilcdc_pdev_probe()` performs complete device initialization and registration.
- `tilcdc_pdev_remove()` and `_shutdown()` tear down or disable active scanout.

## Control Flow

Probe allocates `struct tilcdc_drm_private`, initializes DRM mode config, creates an ordered workqueue, maps MMIO, gets the functional clock, enables runtime PM, reads `LCDC_PID_REG` to determine rev1/rev2, chooses pixel formats based on revision and optional `blue-and-red-wiring`, reads `max-bandwidth`, `max-width`, and `max-pixelclock`, sets FIFO threshold by variant, creates the CRTC, initializes mode config, registers cpufreq notifier, creates the encoder/connector from DT bridge, initializes vblank and IRQ, resets mode config, initializes polling, registers the DRM device, and starts DRM client setup with a selected color depth.

Error paths unwind cpufreq, PM, clock, and workqueue state. Remove unregisters DRM, stops polling, uninstalls IRQ, unregisters cpufreq notifier, disables PM, puts the clock, and destroys the workqueue. System PM uses DRM mode-config helper suspend/resume plus pinctrl sleep/default state selection.

## State and Persistence Behavior

Driver-private state persists for the platform device lifetime and stores MMIO, clock, revision, IRQ, DRM device, format list, max mode limits, FIFO threshold, cpufreq notifier, workqueue, CRTC, encoder, connector, and IRQ-enabled flag. Runtime PM state is enabled after clock acquisition and disabled on teardown.

## Dependencies and Integration Points

The file depends on platform/OF matching, runtime PM, pinctrl PM states, DRM managed allocation, DMA GEM/fbdev helpers, bridge connector flow through `tilcdc_encoder.c`, CRTC creation through `tilcdc_crtc.c`, register helpers, debugfs, cpufreq when enabled, and DRM client setup.

## Risks and Edge Cases

- `clk_get()` is not devm-managed and must match all error/remove paths; the code handles this manually.
- If encoder creation finds no bridge, probe later returns `-EPROBE_DEFER` because `priv->connector` remains NULL.
- Unknown PID defaults to revision 1, reducing feature support and possibly misprogramming rev2-compatible hardware.
- `pm_runtime_get_sync()` result during PID read is ignored.
- Debugfs register reads perform runtime PM get/put without error handling.
- Workqueue ownership is mixed with recovery work in the CRTC file, which uses `system_wq`.

## Test Signals

Probe tests should cover AM33xx/DA850 matches, rev1/rev2 PIDs, unknown PID fallback, all wiring modes, DT max limits, missing clock/MMIO/IRQ, deferred bridge probing, cpufreq notifier registration, debugfs register access, suspend/resume pinctrl transitions, and remove/shutdown with active display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_drv.h

## Purpose

`tilcdc_drv.h` defines the TI LCDC driver's private state, default hardware limits, wrappers for plane/encoder objects, debug macro, and cross-file function prototypes.

## Important APIs, Types, and Definitions

- Default limits: `TILCDC_DEFAULT_MAX_PIXELCLOCK`, `TILCDC_DEFAULT_MAX_WIDTH_V1`, `TILCDC_DEFAULT_MAX_WIDTH_V2`, and `TILCDC_DEFAULT_MAX_BANDWIDTH`.
- `struct tilcdc_drm_private` embeds MMIO, clock, revision, IRQ, DRM device, mode limits, FIFO threshold, format list, cpufreq notifier, workqueue, CRTC, encoder, connector, and IRQ-enabled state.
- `ddev_to_tilcdc_priv()` converts embedded DRM device to private state.
- CRTC API declarations include create, IRQ, clock update, shutdown, and framebuffer update.
- `struct tilcdc_plane` and `struct tilcdc_encoder` wrap DRM objects.
- `tilcdc_plane_init()` creates the primary plane.

## Control Flow

`tilcdc_drv.c` fills the private struct during probe. `tilcdc_regs.h` uses it for MMIO access. `tilcdc_crtc.c`, `tilcdc_plane.c`, and `tilcdc_encoder.c` retrieve state through `ddev_to_tilcdc_priv()` and update shared CRTC/encoder/connector pointers.

## State and Persistence Behavior

`struct tilcdc_drm_private` persists for the DRM device lifetime. Some fields are immutable after probe, while `irq_enabled`, connector pointers, and CRTC runtime fields change during operation.

## Dependencies and Integration Points

The header depends on cpufreq and DRM print declarations plus forward-declared DRM types. It is the central internal ABI for all tilcdc source files.

## Risks and Edge Cases

- The embedded `struct drm_device ddev` means conversion macros depend on layout.
- Public mutable fields can be modified by any tilcdc module.
- Defaults are fallback policy; DT values must be validated in runtime mode checks.
- Conditional cpufreq field requires all users to guard access under `CONFIG_CPU_FREQ`.

## Test Signals

Build tests should cover cpufreq enabled/disabled and all tilcdc modules. Runtime tests should validate private-field initialization, connector presence, IRQ flag transitions, and limit enforcement from defaults and DT overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_encoder.c

## Purpose

`tilcdc_encoder.c` creates the tilcdc encoder and attaches the downstream DT bridge/panel chain through a DRM bridge connector.

## Important APIs, Types, and Functions

- `tilcdc_attach_bridge()` sets the encoder CRTC mask, attaches the downstream bridge with `DRM_BRIDGE_ATTACH_NO_CONNECTOR`, creates a bridge connector, attaches it to the encoder, and stores `priv->connector`.
- `tilcdc_encoder_create()` retrieves the downstream bridge from OF graph port 0, allocates a simple encoder, stores it in private state, and attaches the bridge.

## Control Flow

Probe calls `tilcdc_encoder_create()` after CRTC creation. If no bridge exists (`-ENODEV`), the function returns success without setting `priv->connector`; probe later treats this as no output and defers. Successful creation completes the single display pipeline.

## State and Persistence Behavior

The encoder is DRM-managed. `priv->encoder` and `priv->connector` persist until device removal. The downstream bridge chain owns mode discovery and bus properties.

## Dependencies and Integration Points

The file depends on DRM bridge, bridge connector, OF bridge lookup, simple encoder allocation, and the tilcdc private struct. It integrates with DT graph endpoints and the CRTC created in `tilcdc_crtc.c`.

## Risks and Edge Cases

- Returning success on no bridge shifts the actual error decision to probe; future callers must know to check `priv->connector`.
- The possible CRTC mask is hardcoded to `BIT(0)`, matching the single-CRTC design.
- Encoder type is `DRM_MODE_ENCODER_NONE`; downstream bridge/panel must provide meaningful connector behavior.

## Test Signals

Tests should cover absent bridge, deferred bridge, successful bridge connector creation, connector attach failure, and mode probing through panel/bridge chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_encoder.h

## Purpose

`tilcdc_encoder.h` declares the tilcdc encoder creation entry point for the platform probe path.

## Important APIs, Types, and Functions

- Declares `int tilcdc_encoder_create(struct drm_device *ddev);`.

## Control Flow

`tilcdc_drv.c` calls this function after CRTC/mode-limit setup and before vblank/IRQ registration.

## State and Persistence Behavior

The header has no state. The implementation populates `priv->encoder` and potentially `priv->connector`.

## Dependencies and Integration Points

It relies on `struct drm_device` being visible to the includer and connects the driver core to `tilcdc_encoder.c`.

## Risks and Edge Cases

- The include guard name still references `EXTERNAL` and the trailing comment references `SLAVE`, suggesting historical naming drift.
- No forward declaration of `struct drm_device` appears in this header; includers must include a DRM header or `tilcdc_drv.h` first.

## Test Signals

Build tests should include this header from current and potential new users to catch missing type declarations. Probe tests should validate the success/no-connector behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_panel_legacy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_panel_legacy.c

## Purpose

`tilcdc_panel_legacy.c` provides boot-time compatibility for deprecated `ti,tilcdc,panel` device-tree bindings. It applies an embedded overlay that creates a modern panel-dpi node, copies panel and timing properties from the legacy node, translates selected panel-info flags, and disables matching on the legacy node.

## Important APIs, Types, and Functions

- Embedded symbols `__dtbo_tilcdc_panel_legacy_begin/end` identify the built-in DT overlay blob.
- `tilcdc_panel_update_prop()` allocates and queues a property update in an OF changeset.
- `tilcdc_panel_copy_props()` selects native timing, copies panel properties except `compatible`, creates `panel-timing`, copies timing properties, translates `invert-pxl-clk` and `sync-edge` to `pixelclk-active` and `syncclk-active`, removes the old compatible property, and applies the changeset.
- `tilcdc_panel_legacy_init()` finds tilcdc and legacy panel nodes, applies the overlay, finds the new panel node, copies properties, and removes the overlay on failure.
- `subsys_initcall()` runs the conversion early in boot.

## Control Flow

If both tilcdc and legacy panel nodes exist and are available, the initcall applies the embedded overlay, locates `tilcdc-panel-dpi`, migrates properties, and leaves the live DT in a state consumable by standard `panel-dpi`/bridge code. If migration fails after overlay apply, the overlay is removed.

## State and Persistence Behavior

The live device tree is mutated for the remainder of boot. Allocated properties are owned by OF changeset/DT infrastructure after apply. The legacy node's `compatible` is removed to prevent old driver matching.

## Dependencies and Integration Points

The file depends on OF core, OF overlay, wrapped DTBO symbols from the Makefile, and simple-panel expectations for `panel-dpi`. It is enabled by `DRM_TILCDC_PANEL_LEGACY`.

## Risks and Edge Cases

- `of_changeset_apply()` return is ignored in `tilcdc_panel_copy_props()`.
- If `of_find_property(old_panel, "compatible", NULL)` returns NULL, removal behavior depends on OF changeset validation.
- Property copy is broad and may migrate legacy-only properties that modern panel-dpi ignores or misinterprets.
- The code assumes one matching LCDC and one matching legacy panel.
- Endianness conversion is handled for generated boolean-like timing values, but copied properties retain original representation.

## Test Signals

Boot tests should cover legacy DT with native-mode phandle, legacy DT without native-mode, missing `display-timings`, missing `panel-info`, unavailable LCDC/panel nodes, overlay apply failure, property-copy allocation failures, and successful creation of a usable panel-dpi bridge for tilcdc probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_panel_legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_plane.c

## Purpose

`tilcdc_plane.c` implements the single primary plane for the tilcdc driver. It enforces full-screen, unscaled scanout matching the CRTC mode and forwards framebuffer changes to the CRTC scanout/page-flip path.

## Important APIs, Types, and Functions

- `tilcdc_plane_funcs` wires universal plane operations to DRM atomic helper reset/update/disable/state helpers.
- `tilcdc_plane_atomic_check()` validates CRTC attachment, framebuffer presence, zero CRTC x/y, plane size equal to mode size, pitch equal to mode width times bytes per pixel, and marks the CRTC mode changed if the framebuffer pixel format changes.
- `tilcdc_plane_atomic_update()` calls `tilcdc_crtc_update_fb()` and clears the CRTC event on success.
- `tilcdc_plane_init()` allocates the primary plane with the pixel formats selected by probe and installs helper funcs.

## Control Flow

Probe creates this plane from `tilcdc_crtc_create()`. During atomic check the plane rejects overlays, scaling, panning, and mismatched pitch. During atomic update the framebuffer is passed to the CRTC, which either updates scanout immediately or defers to vblank. The driver has no overlay planes.

## State and Persistence Behavior

The plane is DRM-managed and stores no state beyond the embedded DRM plane. Framebuffer changes are reflected through CRTC state and hardware DMA address registers.

## Dependencies and Integration Points

The file depends on DRM atomic helpers, framebuffer format metadata, selected format arrays in `tilcdc_drv.c`, and `tilcdc_crtc_update_fb()`.

## Risks and Edge Cases

- Strict pitch equality rejects framebuffers with padding, which is intentional for simple LCDC scanout but can surprise generic userspace.
- Pixel format changes force a modeset because raster format bits live in CRTC mode programming.
- `WARN_ON(!crtc_state)` returns success rather than a hard error, but such a missing state should not occur for an attached plane.

## Test Signals

Tests should cover full-screen valid scanout, nonzero position rejection, scaled-size rejection, padded pitch rejection, pixel-format change forcing modeset, page flip event delivery through CRTC update, and initialization with each selected format list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_regs.h

## Purpose

`tilcdc_regs.h` defines TI LCDC register offsets, status/control bit masks, DMA/timing/raster field helpers, and inline MMIO access helpers for the tilcdc driver.

## Important APIs, Types, and Definitions

- Status bits include EOF0/EOF1, palette load done, FIFO underflow, sync lost, and frame done.
- DMA control macros encode burst size, FIFO threshold, EOF interrupts, and dual-framebuffer enable.
- Control/raster/timing macros encode clock divisor, raster mode, palette load mode, TFT/monochrome flags, rev1/rev2 interrupt enables, rev2 clock enables, 24bpp unpack/mode, AC bias, sync edge, pixel clock inversion, HSYNC/VSYNC inversion, and LPP high bit.
- Register offsets cover PID, CTRL, STAT, RASTER timing/control, DMA framebuffer base/ceiling, rev2 IRQ status/enable/end-of-int, and clock reset/enable.
- Inline helpers `tilcdc_write()`, `tilcdc_write64()`, `tilcdc_read()`, `tilcdc_write_mask()`, `tilcdc_set()`, `tilcdc_clear()`, `tilcdc_irqstatus_reg()`, `tilcdc_read_irqstatus()`, and `tilcdc_clear_irqstatus()` centralize MMIO access.

## Control Flow

All tilcdc modules use these helpers to access registers through `struct tilcdc_drm_private::mmio`. Revision-dependent IRQ status selection is handled by `tilcdc_irqstatus_reg()`: rev2 uses `LCDC_MASKED_STAT_REG`, rev1 uses `LCDC_STAT_REG`.

## State and Persistence Behavior

The header has no state; it reads private MMIO state from the DRM device. Hardware register state persists until overwritten, reset, or PM loss. The 64-bit write helper attempts atomic base/ceiling programming where supported and falls back to an architecture-specific volatile 64-bit store.

## Dependencies and Integration Points

It includes Linux bitops and `tilcdc_drv.h`, and is consumed by CRTC, driver, and IRQ paths. It is tightly coupled to LCDC rev1/rev2 hardware behavior.

## Risks and Edge Cases

- `tilcdc_write64()` fallback uses a forced volatile 64-bit write and comments that it compiles to `strd` on ARM7; portability to other architectures requires care.
- Register masks use open-coded shifts in several callers; helper macros do not cover all fields.
- Rev2 interrupt disable must be done by writing clear registers in callers; the helpers only select status registers.
- Clearing IRQ status writes the supplied mask to the active status register, so callers must avoid clearing unobserved bits when that matters.

## Test Signals

Hardware tests should validate rev1/rev2 register dumps, 64-bit scanout address update behavior, IRQ status read/clear semantics, raster timing field programming, clock reset/enable bits, and endian correctness of DMA address writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/Kconfig

## Purpose

`tiny/Kconfig` lists configuration entries for small DRM drivers, including the Apple Touch Bar DRM driver in this work item. It controls build-time availability and helper dependencies for USB, PCI, SPI, and simple panel/display devices.

## Important APIs, Types, and Functions

- `DRM_APPLETBDRM` is a tristate option for Apple Touch Bar display support. It depends on `DRM`, `USB`, `MMU`, and `X86 || COMPILE_TEST`, and selects SHMEM GEM and KMS helpers.
- The file also defines options for ARC PGU, Bochs, Cirrus QEMU, GM12U320, MIPI DBI panels, Pixpaper, HX8357D, ILI9163, ILI9225, ILI9341, ILI9486, MI0283QT, RePaper, and Sharp Memory LCD drivers.

## Control Flow

Kconfig selections drive the tiny DRM Makefile. Enabling `DRM_APPLETBDRM` compiles `appletbdrm.o` and provides a USB DRM driver module named `appletbdrm`.

## State and Persistence Behavior

Configuration choices persist in the kernel build. Selected helper dependencies determine which DRM memory-management and KMS APIs are available to the compiled driver.

## Dependencies and Integration Points

`DRM_APPLETBDRM` integrates with USB and DRM SHMEM/KMS helper infrastructure and is limited to x86 runtime platforms unless compile-testing. Other entries select helpers appropriate to their buses and memory models.

## Risks and Edge Cases

- `DRM_APPLETBDRM` does not select `DRM_CLIENT_SELECTION`, so automatic fbdev/client behavior depends on generic DRM behavior and explicit setup in the driver, which this file does not provide.
- Tiny drivers share one Kconfig file; dependency edits can unintentionally affect unrelated drivers.
- Mixed indentation appears in the Pixpaper entry, which is cosmetic but can distract from Kconfig style consistency.

## Test Signals

Build tests should cover `DRM_APPLETBDRM=y/m/n`, x86 and `COMPILE_TEST` builds, USB disabled builds, and allmodconfig interactions with other tiny DRM entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/Makefile

## Purpose

`tiny/Makefile` maps tiny DRM Kconfig symbols to their object files.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_DRM_APPLETBDRM) += appletbdrm.o` builds the Apple Touch Bar DRM driver.
- Other entries build arcpgu, bochs, cirrus-qemu, gm12u320, panel-mipi-dbi, pixpaper, hx8357d, ili9163, ili9225, ili9341, ili9486, mi0283qt, repaper, and sharp-memory drivers.

## Control Flow

Kbuild includes each object when the corresponding Kconfig symbol is enabled as built-in or module. The object name determines the module name for module builds.

## State and Persistence Behavior

The Makefile has no runtime state; it controls compile/link outputs.

## Dependencies and Integration Points

It integrates the tiny DRM directory with top-level Kbuild and the options declared in `tiny/Kconfig`.

## Risks and Edge Cases

- Missing or mismatched object entries cause enabled drivers not to build.
- Formatting inconsistencies, such as spacing around `pixpaper.o`, are harmless but can hide accidental changes in reviews.

## Test Signals

Build all tiny DRM entries as modules and built-ins, and verify `appletbdrm.ko` is produced when `CONFIG_DRM_APPLETBDRM=m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/appletbdrm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/appletbdrm.c

## Purpose

`appletbdrm.c` is a USB DRM/KMS driver for Apple Touch Bar displays. It discovers bulk endpoints, speaks the Touch Bar request/response protocol, exposes a fixed non-desktop DRM connector, converts/flushes framebuffer damage to device-oriented frame messages, and clears the display on disable/shutdown.

## Important APIs, Types, and Functions

- Protocol structures: request/response headers, simple request, information response, frame payload, framebuffer request footer, framebuffer request, and update-complete response.
- `struct appletbdrm_device` embeds USB endpoint IDs, display dimensions, DRM device, fixed mode, connector, primary plane, CRTC, and encoder.
- `struct appletbdrm_plane_state` extends DRM shadow plane state with allocated USB request/response buffers and damage frame sizes.
- USB protocol helpers: `appletbdrm_send_request()`, `appletbdrm_read_response()`, `appletbdrm_send_msg()`, `appletbdrm_clear_display()`, `appletbdrm_signal_readiness()`, and `appletbdrm_get_information()`.
- Plane helpers: `appletbdrm_primary_plane_helper_atomic_check()` allocates a request sized for current damage clips; `appletbdrm_flush_damage()` fills frame records, converts XRGB8888 to BGR888 if needed, sends the USB bulk request, reads update completion, and checks the timestamp; reset/duplicate/destroy manage shadow state.
- `appletbdrm_setup_mode_config()` initializes one primary plane, one CRTC, one encoder, one USB connector, fixed mode, orientation, non-desktop property, and mode config funcs.
- USB lifecycle: `appletbdrm_probe()`, `appletbdrm_disconnect()`, and `appletbdrm_shutdown()`.

## Control Flow

USB probe finds bulk endpoints, allocates the DRM device, stores endpoint addresses, sets interface data, optionally sets the DMA device for buffer sharing, requests display information, sends readiness, sets up DRM mode config, registers the DRM device, and clears the display. Userspace commits damage to the primary plane; atomic check sizes and allocates protocol buffers based on damage clips, and atomic update flushes those damaged rectangles via USB bulk messages. Disable and shutdown clear or shut down display state so persistent Touch Bar contents are removed.

The device coordinate system swaps axes and inverts one axis. `appletbdrm_setup_mode_config()` creates the fixed DRM mode with width/height swapped, and `appletbdrm_flush_damage()` translates damage rectangles into device `begin_x`, `begin_y`, `width`, and `height`.

## State and Persistence Behavior

Device width/height and fixed mode persist after probe. Per-atomic plane state owns request/response allocations and frees them in `atomic_destroy_state()`. Display contents persist on the physical device across boots, so disable/shutdown paths explicitly clear or shut down scanout. USB device unplug is handled through `drm_dev_unplug()` and `drm_dev_enter()/exit()` guards around update/disable.

## Dependencies and Integration Points

The file depends on USB bulk APIs, DRM atomic/connector/CRTC/encoder helpers, damage helpers, SHMEM GEM, shadow-plane helpers, framebuffer format conversion helpers, fixed-mode helpers, and DRM device unplug protection. It matches USB vendor/product `05ac:8302` with audio-video interface class.

## Risks and Edge Cases

- In `appletbdrm_get_information()`, an early send failure returns without freeing `info`, leaking the allocation on that path.
- In atomic check, if response allocation fails after request allocation succeeds, the request is not freed until state destroy; this is acceptable if the failed state is destroyed but should be verified by DRM atomic cleanup paths.
- `appletbdrm_flush_damage()` calls `drm_gem_fb_end_cpu_access()` even when `begin_cpu_access` failed, due to the shared exit label.
- Timestamp comparison logs a mismatch but does not set `ret`, so the update can report success after a mismatch.
- Damage buffer sizing uses damage rectangles before intersection with `state->dst`; skipped rectangles can leave unused allocated frame space, which is safe but worth understanding.
- USB protocol fields are partly unknown constants; firmware changes can break assumptions about headers, footer, readiness, or expected pixel format.
- Probe registers the DRM device before `appletbdrm_clear_display()`; if clear fails, probe returns error after registration.

## Test Signals

Tests should cover endpoint discovery failure, information response validation for dimensions/bpp/pixel format, readiness-signal retry handling, fixed mode dimensions/orientation/non-desktop property, BGR888 and XRGB8888 damage flushes, multiple damage clips, zero-damage commits, timestamp mismatch handling, unplug during update, disable clear display, shutdown clearing persistent content, and error-path leak detection with KASAN/KMEMLEAK.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/appletbdrm.c -->
