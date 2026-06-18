# sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-drm-drv.c

## Purpose
Implements the main DRM/KMS driver for Ingenic JZ47xx LCD controllers. It supports SoC-specific format/plane capabilities, descriptor-driven DMA scanout, optional OSD overlay and IPU plane integration, palette/gamma handling for C8, bridge/panel output discovery, vblank interrupts, non-coherent framebuffer syncing, and pixel-clock coordination.

## Important APIs, types, and functions
- Hardware descriptors are `struct ingenic_dma_hwdesc` and `struct ingenic_dma_hwdescs`, including an optional palette descriptor and extended JZ4780 descriptor fields.
- `struct jz_soc_info` describes per-SoC capabilities: device clock need, OSD/alpha support, non-coherent mapping, extended descriptors, broken F0 plane, max burst, max dimensions, and format lists.
- `struct ingenic_drm` is the private device object embedding DRM device, planes, CRTC, clocks, regmap, DMA descriptors, clock notifier state, and private atomic object.
- Atomic paths include `ingenic_drm_crtc_atomic_check()`, `ingenic_drm_crtc_atomic_begin()`, `ingenic_drm_crtc_atomic_flush()`, `ingenic_drm_crtc_atomic_enable()`, `ingenic_drm_crtc_atomic_disable()`, `ingenic_drm_plane_atomic_check()`, `ingenic_drm_plane_atomic_update()`, and `ingenic_drm_plane_atomic_disable()`.
- Bridge/encoder paths include `ingenic_drm_bridge_atomic_check()`, `ingenic_drm_bridge_atomic_enable()`, `ingenic_drm_bridge_atomic_disable()`, `ingenic_drm_bridge_atomic_get_input_bus_fmts()`, and `ingenic_drm_encoder_atomic_mode_set()`.
- Lifecycle functions include `ingenic_drm_bind()`, `ingenic_drm_probe()`, `ingenic_drm_unbind()`, suspend/resume, shutdown, module init, and module exit.

## Control flow
Probe either binds directly or creates a component master when IPU support is enabled and an IPU graph endpoint exists at port 8. Bind resolves SoC data, optionally attaches reserved memory, allocates the DRM device, initializes mode config, maps MMIO through regmap, obtains IRQ and clocks, allocates coherent DMA descriptor memory, initializes descriptor rings for F0/F1/palette, creates the primary plane on F1 when OSD exists or F0 otherwise, creates the CRTC, enables palette color management, optionally creates the OSD overlay and binds the IPU component, discovers all downstream panels/bridges from output port entries, creates one encoder/local bridge/connector per output, sets possible clone masks, requests IRQ, initializes vblank, enables clocks, configures OSD/alpha, registers a pixel-clock parent notifier, initializes the private atomic object, registers DRM, and starts client setup.

Atomic CRTC check validates gamma LUT size, ensures the private state is present, pulls F1/F0/IPU plane states on modesets, rejects simultaneous F1 and IPU use, and records `no_vblank` when all scanout planes are disabled. Plane check rejects broken F0 on affected SoCs, runs no-scaling DRM checks, enforces no positioning when OSD is absent, records whether the palette descriptor is needed for C8, forces modesets for OSD enable/disable/position/size/depth changes, and requests damage tracking for non-coherent systems. Plane update syncs non-coherent damage, writes descriptor address/command/next fields, fills extended descriptor fields when required, reprograms plane format/position on modesets, and updates palette data when color management changed.

Bridge atomic check stores the negotiated output bus config, adjusts 3x8-bit serial modes by tripling dot-clock timing fields while preserving display area, and validates supported bus formats. Encoder mode set programs LCD CFG/RGBC fields from connector type, bus format, bus flags, Sharp panel flag, descriptor mode, and sync polarity. CRTC flush updates timings and pixel clock, coordinating with the clock notifier mutex, and arms or sends vblank events. Bridge enable clears state and sets LCD enable; bridge disable requests LCD disable and polls the disabled bit.

## State and persistence
Persistent runtime state includes `struct ingenic_drm`, SoC capability table pointer, DMA descriptor memory, palette table, clock notifier flags, private atomic `use_palette`, plane enable bits, and `no_vblank`. Hardware state persists in LCD timing/config/OSD registers, DMA descriptor base registers, descriptor memory read by the LCD controller, OSD plane registers, pixel/lcd clocks, and optional reserved-memory mappings.

## Dependencies and integration points
Depends on DRM atomic, bridge, connector, color-management, GEM DMA, fbdev, and vblank helpers; regmap MMIO; common clocks and clock notifiers; OF graph panel/bridge lookup; reserved memory; optional component framework for IPU; and functions exported in `ingenic-drm.h` for IPU support. It integrates with `ingenic-dw-hdmi.c` through OF graph as a downstream bridge/connector path.

## Risks
Descriptor rings are hardware-facing and must remain coherent and correctly chained, especially when palette mode switches `DA0` to descriptor 2. `no_vblank` disables vblank when no planes are active, so event paths must handle that case. Pixel-clock parent changes wait for one vblank while holding a mutex; missing vblank or disabled CRTC scenarios can cause latency or deadlock risks. 3x8 serial timing rewriting is unusual and can regress modes if fields are not kept consistent. Non-coherent framebuffer sync relies on damage clips. Simultaneous IPU/F1 use is rejected only when IPU support is compiled and bound. The JZ4780 F0 plane is explicitly disabled as not working.

## Test signals
Validation should cover each compatible SoC table, OSD and non-OSD modes, F0/F1 format lists, C8 palette/gamma LUT size and palette descriptor chaining, page flips, OSD position/size modesets, bridge bus formats including 3x8 serial, TV connector mode selection, vblank IRQ enable/disable with no planes, clock-rate changes, suspend/resume, non-coherent damage flushing on JZ4770, IPU component binding and F1/IPU mutual exclusion, and clean module unload.
