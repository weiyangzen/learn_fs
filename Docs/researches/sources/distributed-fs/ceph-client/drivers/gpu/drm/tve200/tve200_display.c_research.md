<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/tve200_display.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/tve200_display.c

Purpose: Implements TVE200's simple display pipe, vblank interrupt handler, mode validation, framebuffer address update, and register programming for supported RGB/YUV formats and fixed TV-class resolutions.

Important APIs/types/functions: `tve200_irq()` handles TVE200 interrupts and toggles vblank trigger position to work around level-like interrupt behavior. `tve200_display_check()` validates supported modes, dword-aligned base addresses, exact pitch, and format-change constraints. `tve200_display_enable()` resets hardware, enables clocks, programs `TVE200_CTRL` format/resolution/bus flags, and starts vblank. `tve200_display_update()` writes Y/U/V frame base registers and handles vblank events. `tve200_display_init()` creates the `drm_simple_display_pipe` with supported formats.

Control flow: Atomic check rejects unsupported modes or framebuffer layouts. Enable prepares the TVE clock, resets the block with retry sleeps, builds control bits from mode/connector bus flags/DRM fourcc, writes the control register, and enables vblank. Plane updates write framebuffer DMA addresses and arm/send events under `event_lock`. Disable turns off vblank, clears control, asserts reset, and disables the clock.

State and persistence: State is in hardware registers, `priv->pipe`, connector display info, and DRM CRTC event/vblank state. No durable persistence exists.

Dependencies and integration points: Integrates DRM simple KMS pipe, GEM DMA framebuffer helpers, panel bridge connector data, Linux clocks, MMIO accessors, and DRM vblank core. It relies on register constants and private device state from `tve200_drm.h`.

Risks and test signals: Risks include hard-coded NTSC/noninterlace choices, reset timeout leaving the clock enabled, pitch limitations, YUV plane address programming, and vblank IRQ toggling correctness. Test signals include atomic mode validation for all supported resolutions/formats, vblank event delivery, IRQ storm resistance, framebuffer alignment rejection, and suspend/remove shutdown paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/tve200_display.c -->
