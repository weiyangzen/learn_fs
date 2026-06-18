# sources/distributed-fs/ceph-client/drivers/dma-buf/Kconfig

Purpose: defines the dma-buf subsystem feature switches for explicit sync files, software sync validation, userspace dma-buf creation, debug checks, selftests, and userland memory heaps.

Important APIs/types/functions: Kconfig symbols include `SYNC_FILE`, `SW_SYNC`, `UDMABUF`, `DMABUF_DEBUG`, `DMABUF_SELFTESTS`, and menuconfig `DMABUF_HEAPS`. `SYNC_FILE` and `DMABUF_HEAPS` select `DMA_SHARED_BUFFER`; heap configuration is delegated to `drivers/dma-buf/heaps/Kconfig`.

Control flow: no runtime control flow. The symbols determine which objects in `drivers/dma-buf/Makefile` are compiled and which code paths are enabled, including sync-file ioctls, sw_sync debugfs test driver, dma-buf importer debug wrapping, and heap char devices.

State and persistence behavior: build-time configuration only. `DMABUF_DEBUG` defaults to y for debug kernels and changes runtime validation behavior in `dma-buf.c`.

Dependencies and integration points: integrates with the Linux dma-buf core, sync_file framework, debugfs, memfd creation, MMU support, and heap drivers.

Risks and test signals: enabling `SW_SYNC` is explicitly test/debug oriented and can deadlock kernel drivers if misused from userspace. Test signals are correct object inclusion under each symbol combination, `/dev/dma_heap/*` nodes when heaps are enabled, sync-file ioctls only when `SYNC_FILE` is enabled, and selftest module availability under `DMABUF_SELFTESTS`.
