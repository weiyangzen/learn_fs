# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_rdma.h

Purpose: Declares the Meson VPU Register DMA helper API.

Important APIs, types, and functions: Exports lifecycle functions `meson_rdma_init()`, `meson_rdma_free()`, setup/control functions `meson_rdma_setup()`, `meson_rdma_reset()`, `meson_rdma_stop()`, and write/commit functions `meson_rdma_writel_sync()` and `meson_rdma_flush()`.

Control flow: Callers initialize, set up access mode, queue synchronous register writes, flush to start VSYNC replay, and stop/reset/free during teardown or disable.

State and persistence: No state is declared in the header; all state lives in `priv->rdma` and RDMA hardware registers.

Dependencies and integration points: Includes `meson_drv.h` for `struct meson_drm`. Used by G12A AFBCD and can be reused by other Meson display blocks that need synchronized register programming.

Risks: The API does not expose locking or capacity, so callers must know that the implementation has one small channel-1 buffer. Misuse from multiple subsystems would interleave descriptors.

Test signals: Compile coverage plus runtime G12A AFBCD operation are the main signals.
