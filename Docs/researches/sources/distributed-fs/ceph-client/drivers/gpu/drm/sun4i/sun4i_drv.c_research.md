# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_drv.c

## Purpose
`sun4i_drv.c` is the master DRM/platform driver for Allwinner display engines. It allocates the DRM device, binds component drivers discovered from OF graph pipelines, initializes mode config and clients, and coordinates shutdown/suspend/resume.

## Important APIs, Types, and Functions
- `sun4i_drv_driver`: DRM driver descriptor with GEM DMA, modeset, atomic, and fbdev helpers.
- `sun4i_drv_bind/unbind`: master component lifecycle for DRM allocation, reserved memory, component binding, vblank, aperture removal, framebuffer setup, polling, DRM registration, and client setup.
- Graph helpers: node-type predicates, `sun4i_drv_traverse_endpoints`, and `sun4i_drv_add_endpoints`.
- `sun4i_drv_probe/remove/shutdown`: platform driver lifecycle.
- `struct endpoint_list`: small KFIFO used for breadth-first graph traversal.

## Control Flow, State, and Persistence
Probe seeds the endpoint FIFO from `allwinner,pipelines`, walks graph endpoints breadth-first, adds component matches for supported non-connector nodes, and registers the component master when any components are found. Bind allocates DRM and `struct sun4i_drv`, initializes frontend/engine/TCON lists, claims reserved memory, initializes mode config, binds all components, initializes vblank for the created CRTCs, removes conflicting framebuffers, calls `sun4i_framebuffer_init`, initializes polling, registers DRM, and starts DRM clients. Unbind reverses registration, polling, atomic state, components, mode config, reserved memory, and DRM allocation.

## Dependencies and Integration Points
The file depends on component framework, OF graph, reserved memory, aperture removal, DRM atomic/GEM/client helpers, and display-engine subdrivers including frontend, framebuffer, TCON, and TCON TOP. It is the root that discovers and binds the display pipeline.

## Risks and Test Signals
Risks include graph traversal edge cases, disabled frontend pass-through, TCON TOP loop avoidance, 32-bit DMA masking despite newer hardware, component bind ordering, and cleanup after partial bind failures. Tests should cover representative device trees, dual pipelines, disabled frontends, TCON channel-0 panels, TCON TOP HDMI routing, reserved-memory success/failure, suspend/resume, and unbind/shutdown with active DRM clients.
