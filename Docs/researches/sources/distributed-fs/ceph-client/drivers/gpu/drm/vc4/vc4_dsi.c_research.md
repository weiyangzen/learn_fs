# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_dsi.c

## Purpose
`vc4_dsi.c` implements the VC4 DSI0/DSI1 encoder, DRM bridge, and MIPI DSI host. It supports DSI video-mode panel/bridge output, MIPI DSI command transfers, D-PHY timing/ULPS management, clock exposure for PHY-derived clocks, a DMA register-write workaround for broken BCM2835 DSI1 AXI writes, interrupt-driven transfer completion, and debugfs register dumps.

## Important APIs, Types, And Functions
- `struct vc4_dsi_variant` describes port number, broken AXI workaround requirement, debugfs name, and register table.
- `struct vc4_dsi` embeds `vc4_encoder`, `mipi_dsi_host`, and `drm_bridge`, and stores mapped registers, downstream bridge, DMA workaround resources, variant, MIPI lane/channel/format/divider/mode flags, escape/PHY/pixel clocks, PHY fixed-factor clocks, transfer completion state, and debugfs regset.
- `dsi_dma_workaround_write()` writes registers normally or via DMA memcpy when `reg_dma_chan` is present, because BCM2835 DSI1 cannot accept ARM AXI writes.
- `DSI_PORT_READ/WRITE/BIT` abstract DSI0/DSI1 register and bit differences.
- `vc4_dsi_ulps()` and `vc4_dsi_latch_ulps()` enter/exit Ultra Low Power State and wait for ULPS/STOP status.
- `dsi_hs_timing()` and `dsi_esc_timing()` convert D-PHY timing requirements to hardware register units.
- Bridge callbacks `vc4_dsi_bridge_mode_fixup()`, `pre_enable()`, `enable()`, `disable()`, `post_disable()`, and `attach()` configure adjusted mode timing, clocks, PHY registers, DISP0/DISP1, and downstream bridge chaining.
- `vc4_dsi_host_transfer()` builds MIPI DSI packets, splits long payloads across command and pixel FIFOs, enables completion/error interrupts, waits up to one second, handles RX packets, and resets FIFOs on failure.
- Host callbacks `vc4_dsi_host_attach()` and `detach()` record panel parameters, enforce video mode, add/remove the bridge, and add/remove the component.
- IRQ handlers `vc4_dsi_irq_defer_to_thread_handler()` and `vc4_dsi_irq_handler()` handle error bits and transfer completion, with a threaded path for DMA-write variants.
- `vc4_dsi_init_phy_clocks()` registers fixed-factor byte/ddr2/ddr clocks derived from the DSI PHY clock for CPRMAN consumers.
- `vc4_dsi_bind()` performs full DRM component bind for a host-attached DSI device.

## Control Flow
Platform probe allocates the bridge/host object with `devm_drm_bridge_alloc()`, initializes bridge metadata and host ops, stores driver data, and registers the MIPI DSI host. When a panel/bridge attaches, `vc4_dsi_host_attach()` copies lane/channel/format/mode settings, computes the PixelValve divider, rejects non-video mode, adds the DRM bridge, and adds this platform device as a VC4 component. The component master later calls `vc4_dsi_bind()`, which gets the variant, maps registers, validates the DSI ID, sets up DMA-write resources for broken DSI1 if needed, initializes transfer completion, requests IRQ, acquires clocks, finds the downstream bridge, sets the escape clock to 100 MHz, exposes PHY clocks, initializes the DRM encoder, enables runtime PM, and attaches the internal DSI bridge to the encoder.

During atomic enable, bridge `pre_enable()` resumes runtime PM, reads the adjusted CRTC mode, sets PHY PLL rate, resets DSI and FIFOs, configures analog PHY power/reset/current settings, enables escape/PHY/pixel clocks, calculates HS and escape timing registers, enables lanes and clock lane, configures timeouts and display FIFOs, ungates the block, releases AFE reset, exits ULPS, and sets DISP0 for video or command mode. `enable()` then sets `DSI_DISP0_ENABLE`. Disable clears that bit, while post-disable turns off clocks and drops runtime PM.

MIPI command transfer is asynchronous at the hardware level but synchronous to the caller: `vc4_dsi_host_transfer()` prepares packet registers/FIFOs, enables completion interrupts, writes the packet header/control to launch, waits for `xfer_completion`, restores always-enabled error interrupts, optionally reads response data, and resets command state/FIFOs on error.

## State And Persistence Behavior
Persistent object state includes variant, lane count, channel, format, divider, mode flags, clocks, DMA resources, downstream bridge pointer, and transfer completion fields. Runtime PM controls module power during bridge enable. Hardware state persists in DSI control, PHY, timing, timeout, interrupt, DISP0/DISP1, and FIFO registers. `xfer_result` and `xfer_completion` are per-transfer synchronization state updated by IRQ context.

The host is registered at platform probe and unregistered at remove. The component is only added after a MIPI device attaches, which means DSI without an attached panel/bridge does not participate in VC4 master binding.

## Dependencies And Integration Points
This file depends on Linux component, DMA engine/mapping, completion, clock, OF address, platform, runtime PM, and DRM bridge/panel/MIPI DSI/OF helpers. It integrates with the VC4 CRTC through `VC4_ENCODER_TYPE_DSI0/DSI1` and PixelValve clock select, with downstream panels/bridges through DRM bridge chaining and MIPI host ops, with CPRMAN through exposed PHY fixed-factor clocks, and with debugfs through shared regset helpers.

## Risks And Edge Cases
- The code comments state DSI1 video mode is the tested path; DSI0 and non-video command-mode panel operation are either limited or rejected.
- `vc4_dsi_host_attach()` returns `0` for unknown format and non-video mode after logging errors, which may leave attach semantics surprising even though it avoids adding the component in the non-video case.
- Long packet handling assumes pixel FIFO capacity; it warns if `pix_fifo_len >= DSI_PIX_FIFO_DEPTH` but does not otherwise reject before writing.
- RX long packet reads use `DSI1_RXPKT_FIFO`, which is relevant to port differences and should be scrutinized for DSI0 behavior.
- DMA register writes can sleep; DSI1 uses `IRQF_ONESHOT` and a threaded handler so writes to clear interrupts are not done in hard IRQ context.
- Clock enable error paths in `pre_enable()` return early after some resources may already be enabled; bridge/core teardown behavior must be validated.
- ULPS entry/exit relies on status bits and timeouts; failures log warnings and attempt partial recovery.

## Test Signals
- Hardware tests should cover DSI1 video-mode panel boot, mode changes, suspend/resume, runtime PM enable/disable, ULPS transitions, and MIPI command transfers with and without RX.
- BCM2835 DSI1 needs explicit testing of DMA register-write setup, IRQ thread clearing, and transfer completion.
- DSI0 tests should focus on ID validation, register offset abstraction, lane limits, and RX behavior.
- Clock tests should verify escape clock rate, PHY PLL rate, derived byte/ddr clocks, and PixelValve divider-adjusted mode timing.
- Debugfs `dsi*_regs`, interrupt error logs, and transfer timeout/reset messages are key observability signals.
