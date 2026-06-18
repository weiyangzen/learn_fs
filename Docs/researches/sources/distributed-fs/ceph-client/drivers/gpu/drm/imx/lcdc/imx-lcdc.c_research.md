# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/lcdc/imx-lcdc.c

## Purpose
Implements a simple DRM/KMS driver for older i.MX LCDC controllers. It uses a single simple display pipe, DMA-backed framebuffers, a downstream bridge connector, clock-gated register programming, EOF vblank interrupts, and strict mode limits.

## Important APIs, types, and functions
- `struct imx_lcdc` embeds `struct drm_device`, `struct drm_simple_display_pipe`, connector pointer, MMIO base, and IPG/AHB/PER clocks.
- Pipe callbacks are `imx_lcdc_pipe_enable()`, `imx_lcdc_pipe_disable()`, `imx_lcdc_pipe_check()`, and `imx_lcdc_pipe_update()`.
- Hardware programming is centralized in `imx_lcdc_update_hw_registers()` and `imx_lcdc_get_format()`.
- Lifecycle functions are `imx_lcdc_probe()`, `imx_lcdc_remove()`, and `imx_lcdc_shutdown()`.
- IRQ handling is in `imx_lcdc_irq_handler()`.

## Control flow
Probe allocates the DRM device, maps MMIO, finds the downstream bridge, obtains the three clocks, sets a 32-bit DMA mask, initializes managed mode config, creates a simple display pipe for RGB565/XRGB8888, initializes vblank, attaches the bridge and bridge connector, toggles all clocks once to reset a potentially bootloader-enabled LCDC, sets mode limits and helpers, requests the IRQ, registers the DRM device, and starts client setup.

Pipe enable programs LPCR polarity, TFT/color/bpp/clock divider fields, clears panning and hardware cursor bits, enables IPG and AHB clocks, calls the register update path with a full mode set, and enables EOF interrupts. Register update always writes the screen start address; for modesets it temporarily disables the PER clock if the old CRTC was enabled, programs frame size, horizontal/vertical porch/sync registers, format bpp, virtual page width, and re-enables PER if the new CRTC is enabled. Pipe update detects format or CRTC changes, updates registers, and arms or sends pending vblank events. Disable turns off clocks, completes any pending event, and disables EOF interrupts.

## State and persistence
DRM state persists in the embedded DRM device and simple pipe. Hardware state persists in LCDC registers such as LSSAR, LSR, LHCR, LVCR, LPCR, LVPWR, and LIER. Clock enable state is carefully managed because the controller starts directly when clocks are enabled and has no explicit enable bit.

## Dependencies and integration points
Depends on DRM simple display pipe, GEM DMA helpers with vmap/fbdev support, dirty framebuffer creation, bridge connector helpers, Linux clock framework, platform resources, and DRM vblank/event helpers. Device tree provides the MMIO region, IRQ, clocks, and downstream bridge.

## Risks
The controller has no enable bit, so incorrect clock ordering can start it with invalid register state. Mode checks enforce 64..1024 dimensions and hdisplay multiple of 16; unsupported panels fail atomic check. Frame size and porch fields have controller-specific encodings and offsets. `clk_div - 1` assumes a nonzero rounded divider. IRQ status is handled but not explicitly cleared in the handler, relying on controller semantics.

## Test signals
Validation should cover RGB565 and XRGB8888, mode size and hdisplay alignment rejection, bridge probe deferral, bootloader-left-on reset by clock toggling, page flips that only update LSSAR, format changes requiring full register update, vblank event delivery on EOF, and shutdown/remove with active output.
