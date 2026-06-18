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
