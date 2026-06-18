# Research: subset-b-003573

Grouped source research for subset B work item `subset-b-003573`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_plane.c

## Purpose
This file implements the common Exynos DRM plane helper used by several Exynos display controllers. It owns per-plane atomic state allocation, clipping and source/destination coordinate translation, modifier and scaling validation, z-position/blending property registration, and dispatch from generic DRM plane callbacks into the display-controller-specific `exynos_drm_crtc_ops`.

## Important APIs, Types, and Functions
The public entry point is `exynos_plane_init()`, which wraps `drm_universal_plane_init()`, attaches `plane_helper_funcs`, stores the plane index and immutable configuration, and creates zpos, blend-mode, and alpha properties according to `struct exynos_drm_plane_config` capabilities.

Key internal functions are `exynos_plane_get_size()`, `exynos_plane_mode_set()`, `exynos_drm_plane_reset()`, `exynos_drm_plane_duplicate_state()`, `exynos_drm_plane_destroy_state()`, `exynos_drm_plane_check_format()`, `exynos_drm_plane_check_size()`, `exynos_plane_atomic_check()`, `exynos_plane_atomic_update()`, and `exynos_plane_atomic_disable()`. The file depends on Exynos-specific plane state fields such as `src`, `crtc`, `h_ratio`, and `v_ratio`, plus capabilities including `EXYNOS_DRM_PLANE_CAP_SCALE`, `EXYNOS_DRM_PLANE_CAP_DOUBLE`, `EXYNOS_DRM_PLANE_CAP_TILE`, `EXYNOS_DRM_PLANE_CAP_ZPOS`, `EXYNOS_DRM_PLANE_CAP_PIX_BLEND`, and `EXYNOS_DRM_PLANE_CAP_WIN_BLEND`.

## Control Flow
Plane creation starts in a display controller such as FIMD, DECON, mixer, or VIDI by calling `exynos_plane_init()`. DRM atomic helpers later call `exynos_plane_atomic_check()`, which ignores disabled planes, converts 16.16 DRM source coordinates to integer Exynos-private state, computes fixed-point scaling ratios, clips negative or off-screen CRTC rectangles against the adjusted display mode, and validates modifier and scaling constraints. Atomic update then obtains the owning `exynos_drm_crtc` and calls `ops->update_plane()`. Atomic disable uses the old CRTC and calls `ops->disable_plane()`.

## State and Persistence Behavior
The persistent object state is `struct exynos_drm_plane_state`, allocated on reset and duplicated for atomic commits. It mirrors user-visible DRM plane state but also stores clipped Exynos coordinates and ratios consumed by hardware drivers. No hardware registers are touched here; register persistence is delegated to the CRTC implementation after atomic update. Z-position is initialized from the static plane config, and can be mutable only when the plane advertises zpos capability.

## Dependencies and Integration Points
This file integrates with DRM atomic helpers, DRM framebuffer/modifier APIs, DRM blend properties, `exynos_drm_fb_dma_addr()` consumers, and Exynos controller implementations through `exynos_drm_crtc_ops`. Its output state is consumed directly by `exynos_mixer.c`, DECON/FIMD drivers, and VIDI. Modifier handling currently recognizes linear buffers and Samsung 64x32 tiled buffers. The possible CRTC mask is `1 << dev->mode_config.num_crtc`, so plane initialization order depends on Exynos mode config setup.

## Risks
The clipping path divides by `crtc_w` and `crtc_h`, so callers rely on DRM atomic validation to avoid zero-sized visible planes. Scaling validation is capability-driven; a wrong plane config can either reject legal hardware use or allow unsupported scaling into a controller path. `EXYNOS_DRM_PLANE_CAP_DOUBLE` treats exactly half-scale ratios as acceptable even without generic scaling support, matching mixer behavior but easy to misapply to other hardware. Modifier validation is narrow and rejects any unlisted modifier. The possible CRTC mask construction assumes a single current CRTC bit and could be wrong if used after multiple CRTCs already exist in a different topology.

## Test Signals
Useful tests include atomic modeset with primary, overlay, and cursor planes; negative CRTC x/y clipping; partially off-screen planes; exact 1:1, half-scale, and unsupported scaling requests; zpos ordering; pixel and window alpha blending; linear and Samsung tiled framebuffer modifiers; and smoke tests on FIMD/DECON/mixer/VIDI paths to confirm their `update_plane` and `disable_plane` callbacks receive clipped coordinates and ratios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_plane.h

## Purpose
This header exposes the common Exynos plane initialization API to Exynos display controller drivers. It is intentionally small: controller-specific files include it when they need to instantiate `struct exynos_drm_plane` objects with a static `struct exynos_drm_plane_config`.

## Important APIs, Types, and Functions
The only declaration is `int exynos_plane_init(struct drm_device *dev, struct exynos_drm_plane *exynos_plane, unsigned int index, const struct exynos_drm_plane_config *config);`. The referenced structures are defined in the Exynos DRM private headers, so this header acts as a cross-module contract rather than defining types itself.

## Control Flow
There is no executable control flow. At runtime, callers in mixer, VIDI, FIMD, DECON, and related Exynos display drivers call `exynos_plane_init()` during component bind or CRTC setup. The implementation then registers the DRM plane and attaches atomic helper callbacks.

## State and Persistence Behavior
The header stores no state. Its API transfers ownership expectations to the implementation: the caller must provide storage for `struct exynos_drm_plane`, a stable plane index, and a static or otherwise long-lived config describing supported formats, plane type, zpos, and capabilities.

## Dependencies and Integration Points
This header depends on prior declarations of `struct drm_device`, `struct exynos_drm_plane`, and `struct exynos_drm_plane_config` from the including source's header chain. It integrates the shared plane helper into all Exynos display blocks that expose DRM universal planes.

## Risks
Because the header has no include guard-local type declarations beyond the prototype, include order matters unless the including file already pulled in the Exynos DRM definitions. Passing a config with temporary lifetime is unsafe because `exynos_plane_init()` stores the pointer in the plane object. Incorrect indexes or capabilities propagate to hardware-specific update paths.

## Test Signals
Build coverage is the main signal for this header. Runtime signals come from every controller that calls `exynos_plane_init()`: successful plane enumeration, correct plane properties in modetest, and working atomic updates across all Exynos display backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_rotator.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_rotator.c

## Purpose
This file implements the Exynos rotator IPP backend. The hardware reads a source DMA buffer, applies crop, rotation, and reflection, writes a destination DMA buffer, and signals completion through an interrupt. The driver registers the hardware as a DRM Exynos IPP processor with crop and rotate capabilities.

## Important APIs, Types, and Functions
The key driver objects are `struct rot_context`, which stores the IPP object, DRM device, DMA registration cookie, MMIO base, clock, format table, and currently active IPP task, and `struct rot_variant`, which selects supported formats and limits by compatible string.

Important functions are `rotator_probe()`, `rotator_bind()`, `rotator_unbind()`, `rotator_commit()`, `rotator_irq_handler()`, `rotator_runtime_suspend()`, and `rotator_runtime_resume()`. Register helpers include `rotator_reg_set_irq()`, `rotator_reg_get_irq_status()`, `rotator_src_set_fmt()`, `rotator_src_set_buf()`, `rotator_dst_set_transf()`, `rotator_dst_set_buf()`, and `rotator_start()`. Format/limit tables describe XRGB8888 and NV12 limits for S5PV210, Exynos4210, Exynos4212/4412, and Exynos5250.

## Control Flow
Probe allocates context, selects variant data from device tree, maps registers, requests IRQ, gets the `rotator` clock, enables runtime PM autosuspend, and registers as a component. Bind attaches to the DRM device, registers the device for DMA mapping, and calls `exynos_drm_ipp_register()` with crop and rotate capabilities. An IPP task enters through `rotator_commit()`: runtime PM resumes the device, the current task pointer is stored, source format/crop/DMA registers are programmed, transform bits are written, destination registers are programmed, IRQ is enabled, and the start bit is set. The IRQ handler reads status, clears the pending bit, drops runtime PM with autosuspend, and calls `exynos_drm_ipp_task_done()` with success only for complete status.

## State and Persistence Behavior
The only live task state is `rot->task`, which is cleared in the interrupt handler. Runtime PM keeps the hardware clock on only while a task is running and for the autosuspend delay afterward. Register state is rewritten for every commit, so no per-job state persists in hardware beyond an active operation. Format limits are static data tied to the device compatible string.

## Dependencies and Integration Points
The driver depends on the Exynos DRM IPP framework, component framework, runtime PM, DMA registration helpers, MMIO register definitions in `regs-rotator.h`, and device-tree compatibles for the supported SoCs. It integrates with user-visible Exynos IPP operations through `DRM_EXYNOS_IPP_CAP_CROP` and `DRM_EXYNOS_IPP_CAP_ROTATE`.

## Risks
`rotator_commit()` assumes the IPP framework serializes tasks because there is only one `rot->task` pointer and no local queueing. If a reset or illegal-status interrupt is lost, runtime PM and task completion can hang. Only NV12 and XRGB8888 are mapped in `rotator_src_set_fmt()`, so adding formats requires both register mapping and limit updates. The file contains a duplicate unreachable `return 0;` in `rotator_bind()`, which is harmless but signals low cleanup coverage. DMA addresses are written as 32-bit register values, so platform DMA mask and buffer placement must match hardware addressing.

## Test Signals
Test with IPP crop-only, rotate 90/180/270, reflect X/Y, combined rotate plus reflect, XRGB8888 and NV12 formats, SoC-specific minimum/maximum/alignment limits, illegal parameter rejection, IRQ completion, autosuspend/resume cycles, component unbind, and fault injection for missing IRQ or clock acquisition errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_rotator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_scaler.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_scaler.c

## Purpose
This file implements the Exynos scaler IPP backend for crop, scale, rotate, reflect, and color conversion operations. It programs source and destination DMA planes, spans, luma/chroma positions, size, scaling ratios, rotation, CSC coefficients, timeout, interrupts, and starts the scaler hardware for each IPP task.

## Important APIs, Types, and Functions
The main state is `struct scaler_context`, containing the IPP object, DRM device, DMA cookie, MMIO base, up to four clocks, active task, and SoC data. `struct scaler_data` selects clock names and supported format tables. `struct scaler_format` maps DRM fourcc formats to hardware color-format values and chroma tile geometry.

Key functions include `scaler_probe()`, `scaler_bind()`, `scaler_unbind()`, `scaler_commit()`, `scaler_irq_handler()`, `scaler_runtime_suspend()`, and `scaler_runtime_resume()`. Register-programming helpers cover reset, interrupt masks/status, source/destination format/base/span/position/size, ratios, rotation, CSC matrix, timeout, and hardware start. Format tables expose many YUV and RGB formats plus Samsung 16x16 tiled input/output entries with Exynos5420/5433 limits.

## Control Flow
Probe allocates context, selects SoC data, maps MMIO, requests a threaded IRQ, gets clocks, enables runtime PM autosuspend, and registers as a component. Bind registers DMA and calls `exynos_drm_ipp_register()` with crop, rotate, scale, and convert capabilities. `scaler_commit()` resolves source and destination DRM formats, resumes runtime PM, resets the scaler, stores the task, programs all source registers, programs all destination registers, computes horizontal and vertical fixed-point ratios with rotation awareness, writes rotation/reflection bits, selects a CSC matrix based on source format class, enables timeout and interrupts, and starts hardware. The IRQ handler acknowledges all status bits, disables interrupts, releases runtime PM, and completes the task with success only when `SCALER_INT_STATUS_FRAME_END` is present.

## State and Persistence Behavior
The active task is a single pointer cleared on interrupt completion. Runtime PM controls all clocks based on job activity and autosuspend. Hardware register state is rewritten per task after a soft reset. Supported formats, limits, and clock names persist as static SoC data. There is no software persistence across driver removal or system suspend beyond the component and runtime PM frameworks.

## Dependencies and Integration Points
The driver depends on the Exynos IPP core, DRM fourcc/modifier data, runtime PM, component binding, clock framework, register definitions in `regs-scaler.h`, and Samsung tiled format modifiers. It integrates with Exynos DRM DMA mapping helpers and device-tree compatibles `samsung,exynos5420-scaler` and `samsung,exynos5433-scaler`.

## Risks
`scaler_commit()` returns `-EIO` on reset failure after runtime PM resume without dropping the runtime PM reference, which can leak an active PM usage count on that path. `scaler_clk_ctrl()` ignores individual clock enable failures and always returns 0, making partial clock-enable failures hard to diagnose. The file contains a duplicated local declaration in `scaler_clk_ctrl()`, which would be a compile-time issue in a strict current build unless already patched elsewhere. Tile support is represented by `modifier != 0`, so any future nonzero modifier would be treated as tiled unless format validation prevents it. Ratio and position fields are masked by register macros; out-of-range values must be caught by IPP limits before commit.

## Test Signals
Exercise RGB and YUV conversions, NV12/NV21/YUV420/YUV422/YUV444 paths, tiled and linear buffers, up/down scaling within 1/4x to 16x limits, rotate 90/180/270, reflect X/Y, CSC direction changes, illegal size/ratio IRQs, timeout IRQs, reset failure injection, runtime PM autosuspend, and multi-clock Exynos5433 suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_scaler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_vidi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_vidi.c

## Purpose
This file implements VIDI, a virtual Exynos display output used for testing and simulated hotplug. It creates a virtual CRTC, three virtual planes, a virtual connector with fake or user-supplied EDID, a simple encoder, and a timer-driven 50 Hz fake vblank source.

## Important APIs, Types, and Functions
The core type is `struct vidi_context`, holding the encoder, DRM device, CRTC, connector, three planes, optional raw EDID, connection state, suspend state, vblank timer, and mutex. The user-facing entry point is `vidi_connection_ioctl()`, also exposed through the sysfs `connection` attribute for the fake EDID path.

Important functions include `vidi_probe()`, `vidi_bind()`, `vidi_unbind()`, `vidi_remove()`, `vidi_enable_vblank()`, `vidi_fake_vblank_timer()`, `vidi_update_plane()`, `vidi_atomic_enable()`, `vidi_atomic_disable()`, `vidi_detect()`, `vidi_get_modes()`, and `vidi_create_connector()`.

## Control Flow
Probe allocates context, initializes the timer and mutex, stores driver data, and registers the component. Bind stores the DRM device, exposes the device through `priv->vidi_dev`, initializes three planes using the shared Exynos plane helper, creates an Exynos CRTC backed by the primary plane and `vidi_crtc_ops`, initializes a TMDS encoder, maps possible CRTCs, and creates a virtual connector. Connection can be changed either through sysfs using fake EDID or through `vidi_connection_ioctl()` with user-provided EDID. Both paths update `ctx->connected` and call `drm_helper_hpd_irq_event()`. Vblank is simulated by a periodic timer that calls `drm_crtc_handle_vblank()` and rearms itself while vblank remains enabled.

## State and Persistence Behavior
The driver persists connection state, optional EDID, suspend state, and plane/CRTC/connector objects for the lifetime of the component. `raw_edid` is dynamically replaced on connect IOCTL and freed on disconnect/remove. The vblank timer is active only when vblank is enabled and the CRTC is not suspended. Plane updates do not program hardware; they only log framebuffer DMA addresses.

## Dependencies and Integration Points
VIDI integrates with `EXYNOS_VIDI_CONNECTION` in `exynos_drm_drv.c`, `exynos_drm_private::vidi_dev`, the shared Exynos plane helper, Exynos CRTC creation, DRM EDID helpers, DRM hotplug helpers, DRM vblank core, and virtual connector mode probing. The header `exynos_drm_vidi.h` provides a NULL stub when the config option is disabled.

## Risks
`vidi_connection_ioctl()` trusts the EDID extension count enough to allocate `(extensions + 1) * EDID_LENGTH` after copying only the header, so malformed but accessible user memory can request a larger copy before `drm_edid_valid()` rejects it. The same-function duplicate unreachable `return -EINVAL;` is harmless but noisy. Connection and EDID state are mutex-protected, but `vidi_detect()` uses `READ_ONCE()` without locking and can observe connection changes independently of EDID replacement. The sysfs path refuses to operate when raw EDID is set, so tests must reset via IOCTL before using fake EDID again. Timer cleanup must occur before context removal to avoid use after free.

## Test Signals
Run modetest against the virtual connector, toggle sysfs `connection` with fake EDID, use the VIDI connection IOCTL with valid and invalid EDID blobs, verify hotplug events, confirm `get_modes()` returns fake/user modes, enable/disable vblank and observe 50 Hz events, perform atomic plane updates across all three formats, and test remove/unbind while vblank is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_vidi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_vidi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_vidi.h

## Purpose
This header exposes the optional VIDI connection IOCTL hook to the Exynos DRM core. It lets `exynos_drm_drv.c` wire the IOCTL when VIDI support is enabled while compiling to a NULL handler otherwise.

## Important APIs, Types, and Functions
When `CONFIG_DRM_EXYNOS_VIDI` is enabled, it declares `int vidi_connection_ioctl(struct drm_device *drm_dev, void *data, struct drm_file *file_priv);`. When disabled, it defines `vidi_connection_ioctl` as `NULL`, allowing the driver IOCTL table to compile without conditional call-site logic.

## Control Flow
There is no runtime flow in the header. At compile time, the preprocessor selects either the real function declaration or the NULL macro. At runtime, the DRM IOCTL dispatcher calls the function only when the driver table contains the real symbol.

## State and Persistence Behavior
The header stores no state. It controls availability of VIDI's connection state machine by build configuration only.

## Dependencies and Integration Points
The prototype depends on DRM core types `struct drm_device` and `struct drm_file`, usually provided through the including Exynos DRM driver headers. Its main integration point is the `DRM_IOCTL_DEF_DRV(EXYNOS_VIDI_CONNECTION, ...)` entry.

## Risks
The NULL macro form means consumers must only use the symbol in contexts where a NULL function pointer is valid. If a caller tried to invoke it directly while VIDI is disabled, it would become an invalid call through NULL. Build coverage should include both enabled and disabled configurations.

## Test Signals
Compile with `CONFIG_DRM_EXYNOS_VIDI=y/m` and confirm the IOCTL resolves to the real implementation. Compile with VIDI disabled and confirm the Exynos DRM driver still builds and the IOCTL table safely omits or rejects the VIDI operation according to core DRM behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_vidi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_hdmi.c

## Purpose
This file implements the Exynos HDMI encoder, connector, PHY programming, hotplug, EDID/DDC, CEC notifier, bridge attachment, runtime PM, and HDMI audio codec integration. It supports several Exynos HDMI IP variants with different register maps, PHY programming tables, clock gates/muxes, APB or I2C PHY access, PMU/sysreg controls, and timing programming paths.

## Important APIs, Types, and Functions
Key data structures are `struct hdmi_context`, `struct hdmi_driver_data`, `struct hdmiphy_config`, `struct hdmiphy_configs`, `struct string_array_spec`, and `struct hdmi_audio`. Variant tables include Exynos4210, Exynos4212, Exynos5420, and Exynos5433 driver data and PHY configuration arrays. The exported platform driver is `hdmi_driver`.

Important functions include `hdmi_probe()`, `hdmi_remove()`, `hdmi_bind()`, `hdmi_create_connector()`, `hdmi_get_modes()`, `hdmi_mode_valid()`, `hdmi_mode_fixup()`, `hdmi_enable()`, `hdmi_disable()`, `hdmiphy_enable()`, `hdmiphy_disable()`, `hdmiphy_conf_apply()`, `hdmi_conf_apply()`, `hdmi_v13_mode_apply()`, `hdmi_v14_mode_apply()`, `hdmi_irq_thread()`, `hdmi_register_audio_device()`, and HDMI codec callbacks for hw params, mute, shutdown, and ELD.

## Control Flow
Probe allocates context, loads variant data, initializes resources, maps HDMI registers, gets DDC and PHY access, requests GPIO HPD IRQ, obtains PMU/sysreg regmaps, enables an optional `hdmi-en` regulator, enables runtime PM, initializes default audio infoframe fields, registers the HDMI audio codec, and joins the component framework. Bind initializes a TMDS encoder, sets possible CRTCs, locates the HDMI Exynos CRTC, assigns a `pipe_clk` callback that controls the HDMI PHY, and creates the HDMI connector.

Connector probing reads EDID over DDC when available, updates connector display info and CEC physical address, detects DVI mode from EDID, or falls back to 640x480 no-EDID modes. Mode validation requires an exact pixel-clock match in the selected PHY table. Enabling the encoder powers and configures the PHY, initializes HDMI/DVI mode, audio, infoframes, and timing registers, then starts the timing generator. HPD GPIO interrupts schedule debounced hotplug work. Runtime suspend/resume gates HDMI clocks.

## State and Persistence Behavior
`hdmi_context` persists device resources, connector state, bridge, CEC notifier, clock/regulator handles, audio parameters, and a `powered` flag protected by `mutex`. PHY and HDMI core registers are reprogrammed on enable and mode set. Audio parameters and mute state persist in software and are applied when powered. The CEC physical address is updated from EDID and invalidated on disconnect/disable. Runtime PM controls clock gates, while `hdmiphy_enable()` controls regulators, PMU PHY enable, sysreg refclk, PHY power, and clock parent switching.

## Dependencies and Integration Points
The file depends on DRM connector/encoder/bridge/EDID helpers, Exynos CRTC pipe-clock hooks, GPIO descriptors, I2C DDC, optional I2C or APB HDMI PHY access, regmap syscon for PMU/sysreg, regulator bulk APIs, clock framework, runtime PM, CEC notifier, sound `hdmi-codec`, and register definitions in `regs-hdmi.h`. It is registered by the Exynos DRM driver when HDMI support is enabled and is paired with the mixer CRTC for TV output.

## Risks
Mode validation requires exact pixel clocks from static PHY tables, so otherwise valid EDID modes with close clocks are rejected. `hdmiphy_reg_write_buf()` returns raw short-write values from `i2c_master_send()`, which may be positive but still treated as an error by callers. `hdmiphy_enable()` logs but ignores regulator bulk enable failure, then continues to power/configure the PHY. `hdmi_disable()` cancels hotplug work and invalidates CEC but deliberately does not power down when `powered` is true, relying on the mixer/pipe clock sequencing; this coupling must be preserved. The file as present contains a duplicated function parameter line in `hdmi_audio_hw_params()` and a duplicated debug string in `hdmi_mode_valid()`, which are strong build-review signals. Resource cleanup must balance DDC adapter, I2C PHY client, APB PHY iounmap, bridge, audio platform device, regulators, and runtime PM.

## Test Signals
Build with all Exynos HDMI variants, boot with Exynos4210/4212/5420/5433 compatible data, test DDC EDID and no-EDID fallback, HPD debounce, DVI versus HDMI infoframe behavior, CEC physical address updates, bridge attachment, mode validation for all PHY-table clocks, interlaced and progressive modes, suspend/resume, regulator/clock failure paths, audio hw_params/mute/ELD, and combined mixer enable/disable sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_mixer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_mixer.c

## Purpose
This file implements the Exynos mixer CRTC for HDMI/TV output. It manages two RGB graphic planes and, on older variants, one video-processor NV12/NV21 plane. It programs mixer and VP registers for scan mode, color space conversion, layer priority, blending, framebuffer addresses, scaling, vblank, runtime PM, and synchronization with the HDMI timing generator.

## Important APIs, Types, and Functions
Key state is in `struct mixer_context`: platform device, DRM device, DMA cookie, Exynos CRTC, three planes, flags, IRQ, mixer/VP MMIO bases, spinlock, clocks, version, and scan value. `struct mixer_drv_data` selects hardware version, VP availability, and extra sclk needs. Static `plane_configs` define primary, cursor, and VP overlay formats/capabilities.

Important functions include `mixer_probe()`, `mixer_bind()`, `mixer_unbind()`, `mixer_initialize()`, `mixer_atomic_enable()`, `mixer_atomic_disable()`, `mixer_atomic_begin()`, `mixer_update_plane()`, `mixer_disable_plane()`, `mixer_atomic_flush()`, `mixer_mode_valid()`, `mixer_mode_fixup()`, `mixer_irq_handler()`, `mixer_graph_buffer()`, `vp_video_buffer()`, `mixer_win_reset()`, `vp_win_reset()`, `mixer_commit()`, and runtime PM suspend/resume.

## Control Flow
Probe allocates context, selects variant flags, enables runtime PM, and registers the component. Bind initializes hardware resources, registers DMA, creates supported planes with the common Exynos plane helper, and creates the HDMI-type Exynos CRTC. Atomic enable resumes runtime PM, enables the HDMI pipe clock callback, disables sync, resets the mixer, enables vsync IRQ if requested, resets windows and VP filters, commits scan/RGB format, enables sync, and marks the mixer powered. Atomic begin waits for prior shadow updates to synchronize, then disables sync before new register writes. Plane updates program either VP or graphic registers. Atomic flush re-enables sync and handles pending CRTC events. Atomic disable stops the mixer, disables all planes, disables the HDMI pipe clock, drops runtime PM, and clears powered state.

## State and Persistence Behavior
Software state lives in mixer flags, scan value, plane state, and the `MXR_BIT_POWERED`, `MXR_BIT_VSYNC`, `MXR_BIT_INTERLACE`, `MXR_BIT_VP_ENABLED`, and `MXR_BIT_HAS_SCLK` bits. Hardware state is mostly shadowed; synchronization is controlled through mixer/VP shadow update bits and `MXR_STATUS_SYNC_ENABLE`. Runtime PM controls mixer, HDMI, VP, and optional sclk clocks. DMA registration persists while bound. VP filter coefficients are reloaded during reset.

## Dependencies and Integration Points
The mixer depends on Exynos DRM CRTC/plane helpers, Exynos DMA registration, DRM vblank core, DRM framebuffer/fourcc/blend helpers, runtime PM, clock framework, device-tree compatibles, `regs-mixer.h`, and `regs-vp.h`. It is tightly integrated with `exynos_hdmi.c`: HDMI bind installs a pipe-clock callback on the HDMI CRTC, and mixer enable/disable calls `exynos_drm_pipe_clk_enable()` to power the HDMI PHY in the right order.

## Risks
Hardware sync is timing-sensitive; if `mixer_wait_for_sync()` times out, register updates continue after logging an error. The VP path depends on correct interlaced address offsets and tiled buffer offsets. The file contains a duplicated `priority` declaration in `vp_video_buffer()`, which is a compile-time issue unless corrected in the local tree. Runtime resume returns immediately on later clock failures without unwinding clocks already enabled, so partial-enable cleanup is a risk. Mode fixup silently expands some modes to fixed TV timings on older mixers; HDMI must be configured consistently with the adjusted timing.

## Test Signals
Test RGB plane formats and alpha modes, VP NV12/NV21 linear and Samsung tiled buffers, zpos/layer priority, half-scale graphics support, VP scaling, interlaced output, CEA modes and adjusted-mode fixups, vblank enable/disable, atomic update synchronization, HDMI pipe-clock sequencing, runtime PM suspend/resume, IRQ delivery, and all compatible variants with and without VP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_mixer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-decon5433.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-decon5433.h

## Purpose
This header defines register offsets and bitfield helpers for Exynos543x DECON display controller variants, including Exynos5430, Exynos5433, internal, and TV register differences. It is a hardware ABI map for DECON timing, windows, blending, interrupts, QoS, update/trigger, clock gating, and CRC control.

## Important APIs, Types, and Functions
The file exports macros for core register offsets such as `DECON_VIDCON0`, `DECON_VIDOUTCON0`, `DECON_WINCONx(n)`, `DECON_VIDOSDx*`, `DECON_SHADOWCON`, window buffer address registers, `DECON_VIDINTCON*`, `DECON_BLENDCON`, `DECON_UPDATE`, timing registers, trigger registers, CRC registers, and clock-gate registers. Bitfield macros cover `VIDCON0` enable/reset/status, output interface and interlace flags, window burst length, BPP modes, alpha/blending flags, shadow protection, interrupt status, update triggers, timing fields, CRC enable, and blending coefficients.

## Control Flow
The header has no executable flow. DECON driver code includes it to compose register values during mode set, atomic plane updates, shadow protection, vblank/framdone IRQ setup, trigger/update firing, and CRC reads.

## State and Persistence Behavior
The macros describe persistent MMIO state in DECON hardware. Window configuration, framebuffer addresses, alpha/blend settings, trigger mode, and timing registers remain programmed until changed or reset. Shadow-protection and update bits control when buffered register writes become active.

## Dependencies and Integration Points
Consumers are Exynos543x DECON drivers and related Exynos plane/CRTC code. The header depends on Linux bit helpers such as `GENMASK` from the including context. It integrates with display timing programming, framebuffer DMA address programming, blending, interrupt handling, QoS tuning, and optional TV/internal output paths.

## Risks
Register maps are SoC-specific; using Exynos5433 offsets on Exynos7 or FIMD hardware will program the wrong registers. Several macros take window numbers with implicit assumptions, including `n - 1` for key registers, so window 0 misuse can underflow offsets. BPP mode definitions include overlapping values for 25/32 bpp modes, so callers must pair them with format-specific semantics. Trigger and shadow bits are safety-critical for atomic updates because premature update can show partial framebuffer state.

## Test Signals
Build DECON543x users, verify mode set timing registers, window enable/disable, framebuffer base/end/size programming, alpha and pixel blending, shadow protection, vblank/framdone interrupts, trigger/update behavior, CRC enable/readback, and QoS/clock-gate settings on Exynos543x hardware or register-level tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-decon5433.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-decon7.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-decon7.h

## Purpose
This header defines register offsets and bitfield macros for the Exynos7 DECON display controller. It covers video control, output interface selection, clocking, shadow control, window configuration, framebuffer addresses and offsets, OSD geometry, color keying, blending equations, interrupts, timing, CRC, clock gating, and update control.

## Important APIs, Types, and Functions
Important offset macros include `VIDCON0`, `VIDOUTCON0`, `VCLKCON*`, `SHADOWCON`, `WINCON(_win)`, `VIDW_*`, `VIDOSD_*`, `WINxMAP`, `WKEYCON*`, `BLENDE(_win)`, `VIDINTCON*`, `VIDCON1(_x)`, `VIDTCON*`, `CRCCTRL`, `DECON_CMU`, and `DECON_UPDATE`. Bitfields encode enable/reset/stop status, RGB/I80 output, burst lengths, buffer selection, triple buffering, pixel formats, alpha selection, OSD coordinates, color map/key values, 8-bit alpha blend mode, interrupt frame/fifo selection, line count, RGB order, timing porch/sync/active sizes, CRC start, and standalone update.

## Control Flow
There is no code flow. Exynos7 DECON code uses these macros during atomic enable, mode programming, plane setup, shadow protect/unprotect, vblank IRQ handling, and update triggering.

## State and Persistence Behavior
The header maps DECON hardware state. Programmed windows, buffer addresses, timing, blend equations, and clock/update registers persist in MMIO until reset or overwritten. Shadow and update bits coordinate active versus pending state for atomic commits.

## Dependencies and Integration Points
The direct consumer is `exynos7_drm_decon.c`. It integrates with Exynos DRM plane state, DRM display modes, framebuffer DMA addresses, interrupt handling, CRC/debug paths, and display interface setup for RGB or I80 outputs.

## Risks
Several macros rely on caller-supplied window indexes and shift constants, so invalid window numbers can compute valid-looking but wrong offsets. `VIDW_BLKSIZE(win)` references `_win` in the macro body while the parameter is named `win`, which is a source-level defect if used. Some burst mask definitions mask only one bit while values encode more than one, so callers must verify the register layout before reusing. Shadow/update sequencing is critical to prevent tearing or partial plane state.

## Test Signals
Compile Exynos7 DECON paths, run atomic modesets across supported pixel formats, verify triple/double buffering, window OSD coordinates, color key and blending equations, RGB/I80 output selection, vblank and extra interrupt delivery, CRC operation, and standalone update behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-decon7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-fimc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-fimc.h

## Purpose
This header defines the Samsung FIMC register map used by the Exynos DRM FIMC IPP backend. It covers input source format, window offsets, global control, input/output DMA addresses, scaler ratios, target format, image capture, status, effects, line skips, original/real sizes, tiling parameters, MIPI/clock/sysreg controls, and writeback routing.

## Important APIs, Types, and Functions
Register offsets include `EXYNOS_CISRCFMT`, `EXYNOS_CIWDOFST`, `EXYNOS_CIGCTRL`, output DMA address banks `EXYNOS_CIOYSA*`, `EXYNOS_CIOCBSA*`, `EXYNOS_CIOCRSA*`, input DMA addresses `EXYNOS_CIIYSA*`, target/scaler/status registers, `EXYNOS_MSCTRL`, offset/original-size registers, `EXYNOS_CIDMAPARAM`, `EXYNOS_CIEXTEN`, and `SYSREG_CAMERA_BLK`. Helper macros select frame-address banks, encode sizes, offsets, pre/main scaler ratios, status fields, flip/rotation, input/output formats, planar ordering, tiling modes, interrupt controls, and clock/writeback routing.

## Control Flow
There is no executable flow. `exynos_drm_fimc.c` uses these macros when configuring an IPP task from memory or local writeback input to output DMA, including crop, scale, rotate/flip, color conversion, line stride/offset, buffer ping-pong addresses, and interrupt completion.

## State and Persistence Behavior
FIMC hardware state persists in the registers described here: input/output DMA base banks, scaler ratios, target sizes, capture enable, interrupt enable, and sysreg writeback routing. The IPP driver rewrites relevant registers per task and uses status bits to detect completion and overflows.

## Dependencies and Integration Points
The header integrates with the Exynos DRM FIMC backend, Exynos IPP framework, display writeback sysreg paths, MIPI/local camera selection logic, and Samsung tiled/linear DMA modes. It is hardware-specific and depends on callers using correct field masks for the FIMC revision.

## Risks
Many macros do not mask arguments, so out-of-range sizes, offsets, and ratios can spill into neighboring fields unless validated before use. Some duplicated definitions and comments exist, including repeated RGB666 and repeated CR8 comments, which increase maintenance risk. Address-bank helper macros assume fixed default ping-pong bank counts. Incorrect planar order, tile size, or field/weave bits can silently corrupt image output. Sysreg writeback routing constants affect other display/camera blocks.

## Test Signals
Exercise FIMC IPP tasks with memory input/output, writeback input, RGB/YUV formats, 1/2/3-plane buffers, linear and tiled modes, crop/scale/rotate/flip, scaler ratio boundaries, frame-end and overflow interrupts, multiple ping-pong buffer indexes, and sysreg writeback routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-fimc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-gsc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-gsc.h

## Purpose
This header defines the Samsung G-Scaler register map for the Exynos DRM GSC IPP backend. It supports enable/update control, reset, IRQs, input/output format and paths, crop/scaled/destination sizes, prescaler and main ratios, chroma stride, multi-bank base addresses, filter coefficients, bus controls, vertical position, clock gating counters, and sysreg writeback routing.

## Important APIs, Types, and Functions
Key macros include `GSC_ENABLE`, `GSC_SW_RESET`, `GSC_IRQ`, `GSC_IN_CON`, `GSC_SRCIMG_SIZE`, `GSC_SRCIMG_OFFSET`, `GSC_CROPPED_SIZE`, `GSC_OUT_CON`, `GSC_SCALED_SIZE`, `GSC_PRE_SCALE_RATIO`, `GSC_MAIN_H_RATIO`, `GSC_MAIN_V_RATIO`, input/output chroma stride registers, base-address mask and bank macros for Y/Cb/Cr, coefficient macros `GSC_HCOEF()` and `GSC_VCOEF()`, `GSC_BUSCON`, clock counters, and `SYSREG_GSCBLK_CFG*` writeback controls.

## Control Flow
The header has no code flow. `exynos_drm_gsc.c` uses it to program GSC tasks: select memory or local input/output paths, set format/order/tile/rotation bits, program source/cropped/scaled/destination rectangles, write DMA base banks, load scaling coefficients, fire updates, and process frame-done or overrun IRQs.

## State and Persistence Behavior
GSC register state persists until changed or reset. The enable and SFR update bits control when staged settings are applied. Address masks and ping-pong indexes represent hardware buffer state. Sysreg constants affect cross-block writeback routing outside the GSC local register space.

## Dependencies and Integration Points
This header integrates with the Exynos GSC IPP backend, Exynos IPP task validation, DRM format/modifier handling, local FIMD/camera writeback paths, and SoC sysreg blocks. It is tied to the G-Scaler hardware layout used by Exynos display/media pipelines.

## Risks
Several bitfield macros shift raw values without masking, so prior bounds checks are required. Some macro names contain typographical errors such as `OEDER`, which can propagate into callers. Tile type, chroma order, RGB range, and rotation fields share control registers, making partial updates risky. Address mask/bank macros assume expected bank counts and 32-bit DMA addressing. Sysreg writeback fields can disrupt display/camera routing if reused incorrectly.

## Test Signals
Test GSC IPP crop/scale/convert/rotate paths, RGB and YUV input/output, tiled and linear modes, local writeback and memory paths, frame-done IRQ and overrun IRQ handling, scaling coefficient programming, prescale/main ratio boundaries, chroma stride handling, ping-pong base selection, bus cache settings, and sysreg routing on supported SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-gsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-hdmi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-hdmi.h

## Purpose
This header defines the Samsung Exynos HDMI register map and bitfields used by `exynos_hdmi.c`. It covers HDMI 1.3 and 1.4 control/core/I2S/timing-generator regions, video timing, HPD/interrupts, PHY control/status, infoframe packets, ACR audio clock regeneration, HDCP register offsets, I2S audio routing/channel status, PHY mode-set values, PMU PHY control, and Exynos5433 sysreg refclk control.

## Important APIs, Types, and Functions
Address-space helpers `HDMI_CTRL_BASE()`, `HDMI_CORE_BASE()`, `HDMI_I2S_BASE()`, and `HDMI_TG_BASE()` compose offsets. Important groups include `HDMI_CON_*`, `HDMI_MODE_SEL`, `HDMI_*_BLANK`, `HDMI_*_SYNC*`, `HDMI_TG_*`, packet registers `HDMI_AVI_*`, `HDMI_AUI_*`, `HDMI_VSI_*`, ACR registers for v1.3/v1.4, I2S registers `HDMI_I2S_*`, HDCP offsets, `HDMIPHY*`, `PMU_HDMI_PHY_CONTROL`, and `EXYNOS5433_SYSREG_DISP_HDMI_PHY`.

## Control Flow
There is no executable flow. The HDMI driver uses these constants to disable IP HPD interrupts, choose HDMI or DVI mode, program infoframes, configure timing-generator registers for progressive/interlaced modes, set ACR N/CTS values, configure I2S audio, power/reset the PHY, and poll PHY-ready status.

## State and Persistence Behavior
The mapped registers persist hardware output state: mode selection, timing, infoframe transmit cadence, audio routing, PHY power, and HDCP-related blocks. The driver rewrites most of this state during encoder enable and mode application, and runtime PM may gate clocks around it.

## Dependencies and Integration Points
Direct consumer is `exynos_hdmi.c`. The macros tie together DRM display mode programming, HDMI infoframe helpers, sound HDMI codec callbacks, PMU/sysreg regmaps, APB/I2C PHY programming, and CEC/EDID hotplug behavior.

## Risks
The same semantic registers live at different offsets in HDMI 1.3 and 1.4, so `exynos_hdmi.c` maps selected registers through an indirection table; any missing mapped register can program the wrong generation. Several duplicate definitions exist, such as `HDMI_VACT_SPACE_6_0`, and unused HDCP offsets may be stale. I2S channel status values and word-length fields are easy to confuse because they mirror IEC status bytes. Timing-generator fields use low/high byte registers with 4-byte spacing, so write helper byte counts must match hardware expectations.

## Test Signals
Validate HDMI 1.3 and 1.4 modes, DVI/HDMI mode selection, infoframe transmission, ACR/I2S audio setup for 16/20/24-bit samples and common sample rates, PHY reset/ready polling, Exynos5433 refclk and mode-set behavior, interlaced timing, hotplug masking, and register dumps against hardware manuals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-hdmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-mixer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-mixer.h

## Purpose
This header defines the Samsung mixer register map and bitfields used by `exynos_mixer.c`. It covers mixer status, configuration, interrupts, layer priority, video configuration, two graphic layers, background colors, color-matrix coefficients, resolution, and shadow-register offsets.

## Important APIs, Types, and Functions
Important offsets are `MXR_STATUS`, `MXR_CFG`, `MXR_INT_EN`, `MXR_INT_STATUS`, `MXR_LAYER_CFG`, `MXR_VIDEO_CFG`, `MXR_GRAPHIC*_*`, `MXR_BG_*`, `MXR_CM_COEFF_*`, `MXR_RESOLUTION`, and shadow registers such as `MXR_CFG_S` and `MXR_GRAPHIC*_BASE_S`. Parametric macros like `MXR_GRAPHIC_CFG(i)`, `MXR_GRAPHIC_BASE(i)`, and `MXR_GRAPHIC_DXY(i)` address the two graphic layers. Field helpers `MXR_MASK()` and `MXR_MASK_VAL()` encode format, size, offsets, layer priority, RGB range, scan mode, destination, burst, sync, run, and vblank bits.

## Control Flow
There is no code flow. The mixer driver uses these macros to reset/run/stop the mixer, enable graphic and VP layers, program framebuffer addresses and spans, set output RGB/YUV/HDMI mode, configure scan mode and quantization, write CSC coefficients, handle vsync IRQs, and check shadow synchronization.

## State and Persistence Behavior
Mixer hardware state persists in these registers while clocks remain active. Shadow registers reflect committed state and are used to wait for synchronization. `MXR_STATUS_SYNC_ENABLE` and `MXR_CFG_LAYER_UPDATE` control when pending layer updates become visible.

## Dependencies and Integration Points
The direct consumer is `exynos_mixer.c`, in combination with `regs-vp.h` for the video processor plane. It integrates with Exynos CRTC atomic updates, HDMI timing output, DRM vblank, and framebuffer DMA programming.

## Risks
The mask helper assumes valid high/low bit ordering and can produce surprising values if reused incorrectly. Width/height and coordinate fields have fixed bit widths; callers must pre-validate dimensions. `MXR_GRP_CFG_MISC_MASK` combines blending and alpha bits, so careless masked writes can unintentionally change pixel/window blending. Shadow register offsets are version-sensitive and only meaningful on hardware that implements them.

## Test Signals
Verify mixer register programming for start/stop, RGB output, SD/HD scan modes, quantization range, graphic layer formats, graphic layer base/span/size/offsets, layer priority, alpha blending, vblank interrupt enable/clear, and shadow synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-mixer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-rotator.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-rotator.h

## Purpose
This header defines the Samsung rotator register offsets and bitfields used by `exynos_drm_rotator.c`. It maps configuration, image control, status, source/destination DMA addresses, buffer sizes, crop positions, crop size, and alignment helper macros.

## Important APIs, Types, and Functions
Important macros include `ROT_CONFIG`, `ROT_CONFIG_IRQ`, `ROT_CONTROL`, format bits for YCbCr420 2-plane and RGB888, flip and rotation masks/values, `ROT_CONTROL_START`, `ROT_STATUS`, IRQ status extraction and clear helpers, `ROT_SRC_BUF_ADDR(n)`, `ROT_DST_BUF_ADDR(n)`, `ROT_SRC_BUF_SIZE`, `ROT_DST_BUF_SIZE`, crop position/size helpers, and `ROT_ALIGN`, `ROT_MIN`, `ROT_MAX`.

## Control Flow
There is no executable flow. The rotator driver uses these macros to enable interrupts, set source format, program source/destination buffer geometry and DMA addresses, encode rotation/reflection transforms, start a job, read completion or illegal status, and clear pending IRQ bits.

## State and Persistence Behavior
Rotator register state is per-operation hardware state. The driver rewrites it for each IPP task and relies on the status register to report completion. Format, crop, DMA address, and transform bits persist until overwritten or reset.

## Dependencies and Integration Points
The direct consumer is the Exynos DRM rotator IPP backend. The macros are tied to DRM rotation/reflection mapping and Exynos IPP format/limit validation.

## Risks
Several field helpers shift raw values without masking, so invalid width, height, crop, or address values can corrupt neighboring fields. `ROT_CONFIG_IRQ` sets two bits, and status clear uses bit positions derived from status enum values, so any mismatch between `ROT_STATUS_IRQ_VAL_*` and clear bits breaks completion. Only the formats represented in the driver should be encoded with these constants.

## Test Signals
Validate register writes for RGB and NV12 jobs, all rotation angles, X/Y reflection, crop positions and sizes, IRQ enable/clear behavior, complete versus illegal status, and alignment/min/max values used by limit tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-rotator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-scaler.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-scaler.h

## Purpose
This header defines the Samsung scaler register map and bitfield helpers for `exynos_drm_scaler.c`. It covers global status/config, interrupts, source/destination format and DMA, spans, luma/chroma positions, sizes, ratios, rotation/reflection, filter coefficients, color-space conversion, dithering, version, cycle/timeout counters, blending, fill, address queues, CRC, and shadow register offset.

## Important APIs, Types, and Functions
Important groups include `SCALER_STATUS`, `SCALER_CFG`, `SCALER_INT_EN`, `SCALER_INT_STATUS`, `SCALER_SRC_*`, `SCALER_DST_*`, `SCALER_H_RATIO`, `SCALER_V_RATIO`, `SCALER_ROT_CFG`, coefficient macros `SCALER_YHCOEF()`, `SCALER_YVCOEF()`, `SCALER_CHCOEF()`, `SCALER_CVCOEF()`, `SCALER_CSC_COEF()`, timeout and blend/fill registers, queue status registers, and CRC registers. Generic helpers `SCALER_MASK`, `SCALER_GET`, and `SCALER_SET` encode most fields. Color constants map YUV/RGB DRM formats to hardware values.

## Control Flow
The header has no runtime flow. The scaler driver uses it to reset hardware, enable a broad set of error and frame-end interrupts, write source/destination format/addresses/spans/rectangles, set scaling ratios, encode rotation/reflection, configure CSC, set a timeout, start a command, and decode/ack interrupt status.

## State and Persistence Behavior
Scaler MMIO state persists for the active IPP command. Non-shadow status/interrupt/version/counter registers reflect live hardware state, while other registers may be shadowed depending on the block. The driver rewrites the state after every reset for each task.

## Dependencies and Integration Points
The direct consumer is `exynos_drm_scaler.c`. The macros are connected to Exynos IPP format tables, DRM rotation bits, Samsung tile modifiers, timeout handling, CSC conversion, and IRQ completion.

## Risks
`SCALER_MASK` uses `1 << width`, so fields with width equal to or exceeding the native int bit width would be unsafe; current fields stay below that but should be reviewed when adding fields. Many setters mask values to field width, which can silently truncate invalid input if validation is missing. Source and destination chroma position math depends on the format table's tile dimensions. Address queue and blending macros are defined even though the current driver does not fully exercise them, so unused definitions may drift from hardware documentation.

## Test Signals
Test scaler task programming for all supported formats, luma/chroma span fields, source/destination positions and sizes, scaling ratio encoding, rotation/reflection bits, CSC coefficients, timeout interrupt, illegal-parameter interrupts, frame-end interrupt, CRC/debug paths if enabled, and register readback on Exynos5420/5433.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-scaler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-vp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-vp.h

## Purpose
This header defines the Samsung video processor register offsets and bitfields used by the mixer VP overlay path. The VP handles NV12/NV21 video-plane input, tiled or linear memory, line-skip interlace behavior, source/destination rectangles, scaling ratios, filter coefficients, endian mode, and shadow updates.

## Important APIs, Types, and Functions
Important macros include `VP_ENABLE`, `VP_SRESET`, `VP_SHADOW_UPDATE`, `VP_FIELD_ID`, `VP_MODE`, luma/chroma image sizes, top/bottom Y/C pointers, endian mode, source/destination position and size registers, `VP_H_RATIO`, `VP_V_RATIO`, and filter coefficient base offsets `VP_POLY8_Y0_LL`, `VP_POLY4_Y0_LL`, and `VP_POLY4_C0_LL`. Helper macros `VP_MASK()` and `VP_MASK_VAL()` encode fields such as image size and source horizontal position.

## Control Flow
There is no executable flow. `exynos_mixer.c` uses these macros to reset VP hardware, load default filters, configure NV12/NV21 and tiled/linear mode, set interlace line skip, program source/destination dimensions and positions, set scaling ratios, write top/bottom field DMA pointers, enable VP, and request shadow update.

## State and Persistence Behavior
VP registers persist video plane state while the mixer is active. Shadow update controls when pending changes are committed. Top/bottom pointers preserve separate field addresses for interlaced output.

## Dependencies and Integration Points
The direct consumer is the VP branch in `exynos_mixer.c`, alongside `regs-mixer.h`. It integrates with DRM framebuffer modifiers, Exynos plane clipped source/CRTC state, HDMI interlace modes, and mixer layer priority/blending.

## Risks
`VP_MODE_FMT_MASK` combines memory mode and format bits in a compact mask; incorrect masked writes can change both tiling and NV12/NV21 order. Field macros rely on unmasked caller values. Filter table writes assume 4-byte alignment and fixed coefficient layout. Interlaced pointer offsets differ for tiled and linear memory, so wrong mode detection corrupts field output.

## Test Signals
Verify VP reset completion, filter coefficient loading, NV12 and NV21 display, tiled and linear modifiers, interlaced top/bottom pointer programming, scaling ratios, source/destination positioning, endian mode, shadow update behavior, and mixer integration for VP layer enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-vp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/Kconfig

## Purpose
This Kconfig entry defines the build option for the Freescale DCU DRM driver. It declares the hardware support as tristate and encodes the core subsystem dependencies and selected helper libraries needed by the driver.

## Important APIs, Types, and Functions
The config symbol is `DRM_FSL_DCU` with prompt `DRM Support for Freescale DCU`. It depends on `DRM`, `OF`, `ARM`, and `COMMON_CLK`. It selects `BACKLIGHT_CLASS_DEVICE`, `DRM_CLIENT_SELECTION`, `DRM_GEM_DMA_HELPER`, `DRM_KMS_HELPER`, `DRM_PANEL`, `REGMAP_MMIO`, `VIDEOMODE_HELPERS`, and conditionally `MFD_SYSCON` for `SOC_LS1021A`.

## Control Flow
There is no runtime control flow. At configuration time, this symbol controls whether the Makefile builds the `fsl-dcu-drm` module or built-in driver. The selected symbols ensure the source files have the helpers required for KMS, panels, DMA GEM buffers, regmap MMIO access, backlight, and videomode conversion.

## State and Persistence Behavior
Kconfig state persists in the kernel `.config`. If selected as `m`, the resulting module is named `fsl-dcu-drm`; if built in, the driver initializes with the kernel.

## Dependencies and Integration Points
The entry integrates with the DRM subsystem, ARM device-tree platforms, common clock framework, Freescale/NXP DCU device-tree nodes, panel/backlight infrastructure, and LS1021A syscon routing needs. The Makefile consumes `CONFIG_DRM_FSL_DCU`.

## Risks
The ARM dependency excludes non-ARM platforms even if similar DCU IP appeared elsewhere. Conditional `MFD_SYSCON` only for LS1021A means other SoCs needing syscon support would require Kconfig updates. Selected helper symbols increase build surface and must match actual driver use. The help text says "an Freescale" but that is cosmetic.

## Test Signals
Run Kconfig build coverage for disabled, module, and built-in configurations; verify dependency selection; build on LS1021A and non-LS1021A ARM configs; and confirm the module name and autoload behavior with matching device-tree compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/Makefile

## Purpose
This Makefile defines the object composition for the Freescale DCU DRM driver. It tells kbuild which source files make up the `fsl-dcu-drm` driver and ties the aggregate object to `CONFIG_DRM_FSL_DCU`.

## Important APIs, Types, and Functions
The object list `fsl-dcu-drm-y` includes `fsl_dcu_drm_drv.o`, `fsl_dcu_drm_kms.o`, `fsl_dcu_drm_rgb.o`, `fsl_dcu_drm_plane.o`, `fsl_dcu_drm_crtc.o`, and `fsl_tcon.o`. The line `obj-$(CONFIG_DRM_FSL_DCU) += fsl-dcu-drm.o` makes the aggregate object conditional on the Kconfig symbol.

## Control Flow
There is no runtime control flow. During the kernel build, kbuild compiles the listed objects, links them into `fsl-dcu-drm.o`, and either links it built-in or emits it as a module depending on `CONFIG_DRM_FSL_DCU`.

## State and Persistence Behavior
The Makefile has no runtime state. Build state is represented in generated object files and the final built-in or module artifact.

## Dependencies and Integration Points
It integrates with the Kconfig symbol in the same directory and with kbuild. The object list expresses source-level integration: driver core, KMS setup, RGB connector, plane support, CRTC support, and timing-controller support all form one driver.

## Risks
Adding a new source file without updating this list leaves code unbuilt. Removing or renaming one listed source breaks the build. All objects are unconditional once `DRM_FSL_DCU` is enabled, so optional feature splits would require additional Makefile conditionals.

## Test Signals
Build `CONFIG_DRM_FSL_DCU=y` and `=m`, confirm all listed objects compile and link, inspect module contents with `modinfo`/symbol checks, and run incremental builds after touching each listed source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_crtc.c

## Purpose
This file implements the CRTC object for the Freescale DCU DRM driver. It programs display timing, polarity, background, thresholds, update mode, pixel clock, DCU enable/disable, vblank interrupt masking, and page-flip event delivery for atomic KMS.

## Important APIs, Types, and Functions
The public entry point is `fsl_dcu_drm_crtc_create()`, which initializes planes, creates the primary plane, initializes the DRM CRTC with helper and CRTC funcs, and attaches helper callbacks. Important atomic callbacks are `fsl_dcu_drm_crtc_atomic_flush()`, `fsl_dcu_drm_crtc_atomic_disable()`, `fsl_dcu_drm_crtc_atomic_enable()`, and `fsl_dcu_drm_crtc_mode_set_nofb()`. Vblank functions are `fsl_dcu_drm_crtc_enable_vblank()` and `fsl_dcu_drm_crtc_disable_vblank()`.

## Control Flow
CRTC creation calls `fsl_dcu_drm_init_planes()`, creates the primary plane, registers a CRTC through `drm_crtc_init_with_planes()`, and adds helper funcs. During mode set, `mode_set_nofb` sets the pixel clock rate, converts the DRM mode to `struct videomode`, derives pixel/HSYNC/VSYNC polarity from connector bus flags and mode flags, writes horizontal and vertical porch/sync registers, active display size, sync polarity, black background, raster/blend mode, and FIFO thresholds. Atomic enable prepares the pixel clock, sets DCU normal mode, triggers a register update, and enables vblank. Atomic flush triggers a register update and arms or sends pending vblank events. Atomic disable disables planes, turns vblank off, sets DCU off mode, triggers update, and disables the pixel clock.

## State and Persistence Behavior
Runtime state lives in `struct fsl_dcu_drm_device`, especially `regmap`, `pix_clk`, connector, and CRTC. Hardware timing and mode registers persist until the next mode set or disable. Pending page-flip events are stored in `crtc->state->event` and consumed under the DRM event lock. Vblank state is maintained by DRM core and DCU interrupt mask bits.

## Dependencies and Integration Points
The file depends on regmap MMIO access, common clock APIs, videomode conversion, DRM atomic helpers, DRM vblank/event helpers, FSL DCU register macros from the driver headers, RGB connector display info, and plane creation helpers in `fsl_dcu_drm_plane.c`. It is called from KMS initialization in `fsl_dcu_drm_kms.c`.

## Risks
`clk_prepare_enable()` and `clk_set_rate()` return values are ignored in enable and mode-set paths, so pixel-clock failures may become display failures without clear propagation. Event handling sends the event immediately if `drm_crtc_vblank_get()` fails, which is standard but can mask vblank-disabled sequencing problems. Bus flag interpretation defaults to inverted pixel clock unless `DRM_BUS_FLAG_PIXDATA_DRIVE_POSEDGE` is present, so panel/display-info accuracy is important. Register writes are not rolled back if a later mode register programming step would fail, though regmap writes generally do not report here.

## Test Signals
Test CRTC creation, primary plane creation failure cleanup, multiple display modes, pixel clock rates, HSYNC/VSYNC polarity flags, bus pixel data edge flags, atomic enable/disable, page flips with vblank events, vblank interrupt mask/unmask, runtime suspend around the pixel clock, and visual validation of black background and FIFO threshold stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_crtc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_crtc.h

## Purpose
This header declares the Freescale DCU CRTC creation function and forward-declares the driver device structure. It is the interface used by the KMS setup code to instantiate the DCU CRTC.

## Important APIs, Types, and Functions
The header provides the include guard `__FSL_DCU_DRM_CRTC_H__`, forward declaration `struct fsl_dcu_drm_device;`, and prototype `int fsl_dcu_drm_crtc_create(struct fsl_dcu_drm_device *fsl_dev);`.

## Control Flow
There is no executable flow. During KMS initialization, caller code includes this header and invokes `fsl_dcu_drm_crtc_create()` to create planes and register the CRTC.

## State and Persistence Behavior
The header stores no state. The function contract expects the caller to pass an initialized `struct fsl_dcu_drm_device` with DRM device, regmap, connector, and clock resources ready for CRTC setup.

## Dependencies and Integration Points
The direct integration point is `fsl_dcu_drm_kms.c`. The implementation integrates with plane setup, CRTC helper funcs, regmap, and clock programming, but this header keeps those details private.

## Risks
The forward declaration hides required initialization details, so misuse is possible if a caller invokes creation before the DRM device, connector, pixel clock, or regmap are ready. Build coverage should catch signature drift between header and implementation.

## Test Signals
Compile all FSL DCU objects, verify KMS setup calls this function once, and test CRTC creation success and failure paths through driver probe on DCU device-tree platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_crtc.h -->
