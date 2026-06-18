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
