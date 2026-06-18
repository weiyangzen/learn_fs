# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_rdma.c

Purpose: Provides a small Register DMA helper for Meson VPU register writes. It builds a coherent descriptor buffer of register/value pairs and configures RDMA channel 1 to replay them on VSYNC, used primarily by G12A AFBCD updates.

Important APIs, types, and functions: Public functions are `meson_rdma_init()`, `meson_rdma_free()`, `meson_rdma_setup()`, `meson_rdma_stop()`, `meson_rdma_reset()`, `meson_rdma_writel_sync()`, and `meson_rdma_flush()`. Internal `meson_rdma_writel()` appends register/value pairs. Descriptors are two `u32`s, with a single 4 KiB buffer.

Control flow: init allocates a coherent page if absent, resets offset, resets/configures RDMA control. setup marks channel 1 as write, no address increment. `writel_sync()` appends the pair and writes immediately to hardware, so current state changes now and is also replayable later. flush stops channel 1, writes DMA start/end addresses for the filled buffer, sets channel 1 trigger to VSYNC, and clears the offset for the next batch. free stops and releases coherent memory.

State and persistence: State is `priv->rdma.addr`, DMA address, and offset. Hardware state includes RDMA control, access-auto trigger mode, IRQ clear bits, and channel start/end addresses. After flush, the hardware can replay the just-built sequence on every VSYNC until stopped or reconfigured.

Dependencies and integration points: Uses Linux DMA coherent allocation, `meson_registers.h` RDMA constants, and `priv->io_base`. G12A AFBCD calls init/setup/writel_sync/flush/reset/free.

Risks: Buffer overflow is handled by a `dev_warn_once()` and dropped writes, which can leave an incomplete replay sequence. No locking is present; callers must serialize access. `meson_rdma_flush()` assumes offset is non-zero when computing end address. The implementation uses only channel 1 and does not service RDMA IRQs.

Test signals: G12A AFBCD setup should allocate one page, write immediate MAFBC registers, and replay them on VSYNC. Stress tests should verify no overflow for the current register sequence and that reset/free stop channel 1 cleanly.
