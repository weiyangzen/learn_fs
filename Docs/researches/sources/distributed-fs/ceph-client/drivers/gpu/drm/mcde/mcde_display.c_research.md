## sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_display.c

### Purpose

`mcde_display.c` implements the MCDE simple display pipe. It programs one framebuffer pipeline from external source 0 through overlay 0, channel 0, FIFO A, and either DSI formatter 0 or DPI formatter 0; it handles IRQ/vblank reporting, FIFO flow control, format setup, timing setup, and framebuffer base updates.

### Important APIs, types, and functions

The file exposes `mcde_display_irq()`, `mcde_display_disable_irqs()`, and `mcde_display_init()`. Important helpers configure external sources, overlays, channels, FIFOs, DSI formatters, DPI timing, DSI packet sizing, FIFO enable/disable/drain, flow start, and framebuffer addresses. `mcde_display_funcs` supplies DRM simple-pipe `.check`, `.enable`, `.disable`, `.update`, and vblank hooks.

### Control flow

Atomic check validates 32-bit framebuffer address alignment, requires pitch to equal `hdisplay * cpp`, and forces a mode change if the framebuffer format changes. Enable powers EPOD, clears IRQs, computes DPI or DSI timing, drains FIFO A/channel 0, configures EXTSRC/overlay/channel/FIFO, enables either the FIFO DPI clock or the DSI bridge plus formatter, enables TE capture if the flow mode uses TE, starts vblank, starts FIFO flow unless in one-shot mode, and sets MCDE enable/autoclock bits. Update arms or fakes vblank events, writes EXTSRC base addresses, and starts flow when needed. Disable stops vblank, drains FIFO flow, disables DPI clock or DSI bridge, sends pending events, disables EPOD, and waits for power-down.

### State and persistence behavior

Runtime state is in `struct mcde`: `flow_mode`, `flow_active`, `stride`, bridge/DSI pointers, FIFO clocks, and locks. Hardware state persists in MCDE external source, overlay, channel, FIFO, formatter, timing, IRQ, and global control registers until power is cut through EPOD. `flow_lock` protects software accounting and FIFO flow toggles.

### Dependencies

It depends on DRM simple KMS helpers, DRM GEM DMA framebuffer helpers, MIPI DSI format helpers, bridge/panel connector metadata, regulators, clocks, and MCDE register definitions.

### Integration points

`mcde_drv.c` calls `mcde_display_init()` during modeset setup. `mcde_display_irq()` is invoked by the top-level MCDE IRQ handler and delegates DSI IRQ status to `mcde_dsi_irq()`. DSI enable/disable calls are intentionally made from this display path because MCDE formatter and DSI link sequencing are tightly coupled.

### Risks

The implementation supports only one pipeline and makes many hardcoded routing choices. Pitch changes other than tight scanout are rejected. TE/one-shot flow control is sequence-sensitive, and comments mark uncertainty around BTA TE, DSI command-mode triggering, bus format mapping, and several packet timing values. DPI muxing is hardcoded to a known board setup. Power-domain register access must stay inside EPOD-enabled windows.

### Test signals

Useful validation includes MCDE boot on DSI video panels, DSI command/TE panels, DPI panels with RGB888 bus format, page flips with real and fake vblank events, framebuffer format changes, FIFO drain timeout absence, TE IRQ handling, suspend/resume power cycling, and mode timings around porch/sync polarity.
