# sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_versatile.h

Purpose: This header declares the Versatile-family initialization hook used by the PL111 core.

Important APIs, types, and functions: `pl111_versatile_init(struct drm_device *dev, struct pl111_drm_dev_private *priv)` is the only exported API. The header includes `pl111_drm.h` and forward-declares `struct device` and `struct pl111_drm_dev_private`.

Control flow: No runtime control flow exists here. The declaration lets `pl111_drv.c` invoke the platform override before IRQ and modeset setup.

State and persistence: No state is owned by the header. It defines the dependency contract between core probe and platform variant setup.

Dependencies and integration points: Integrated with `pl111_versatile.c` and `pl111_drv.c`. It depends on DRM and PL111 private type definitions being available during compilation.

Risks: Any signature drift between this declaration and the implementation breaks the PL111 core build. Because the header includes the private PL111 header, it may propagate more internal definitions than strictly needed.

Test signals: Compile PL111 with this header included from the core driver and validate that `pl111_versatile_init()` links and is called during probe.
