# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_txp.c

Purpose: Implements the VC4 TXP/MOP writeback pipeline as a DRM CRTC, encoder, and writeback connector. It configures TXP destination registers so HVS output can be written into a framebuffer instead of a physical display.

Important APIs/types/functions: `struct vc4_txp` wraps `vc4_crtc`, `vc4_encoder`, writeback connector, platform device, data, and MMIO base. Register definitions cover `TXP_DST_PTR`, `TXP_DST_PITCH`, `TXP_DIM`, `TXP_DST_CTRL`, progress, and 40-bit high-address registers. Atomic writeback hooks are `vc4_txp_connector_atomic_check()` and `_commit()`. CRTC hooks use `vc4_hvs_atomic_*`. IRQ handling is in `vc4_txp_interrupt()`. Platform/component binding is `vc4_txp_bind()`/`unbind()` with data for bcm2835 TXP and bcm2712 MOP/MOPLET.

Control flow: Bind maps registers, initializes a CRTC, virtual encoder, writeback connector with supported formats, and IRQ. Atomic check validates writeback job size, format, and 16-byte pitch alignment, then marks the CRTC state armed. Commit computes TXP control bits from format/alpha/platform flags, writes destination address/pitch/dim/control, queues the writeback job, and relies on IRQ completion. Disable aborts busy hardware and powers down pre-gen6 TXP.

State and persistence: Runtime state is MMIO register programming and the writeback job queued on the connector. `txp_armed` is stored in `vc4_crtc_state`. Platform data persists per device and records HVS output/channel, encoder type, 40-bit support, byte-enable support, and dimension convention.

Dependencies and integration points: Uses DRM writeback, atomic helpers, framebuffer DMA helpers, vblank, component framework, platform OF matches, HVS CRTC helpers, and `vc4_regs.h` field helpers. It is an HVS output endpoint, not a render engine path.

Risks: Format arrays `drm_fmts[]` and `txp_fmts[]` must stay index-aligned. Incorrect address high register handling breaks >32-bit DMA. Interrupt completion must disable `TXP_EI` and signal writeback exactly once. Busy abort loop is polling with a timeout. KUnit guard macros intentionally fail tests on real MMIO access.

Test signals: DRM writeback tests should cover all advertised formats, alpha/no-alpha output, pitch alignment rejection, framebuffer/mode size mismatch, irq completion, disable during busy TXP, 40-bit addresses on bcm2712 data, and connector always-connected behavior.
