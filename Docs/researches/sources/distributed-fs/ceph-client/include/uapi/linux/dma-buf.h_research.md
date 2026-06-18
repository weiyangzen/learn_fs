## sources/distributed-fs/ceph-client/include/uapi/linux/dma-buf.h

Purpose: This UAPI header defines ioctl structures for dma-buf file descriptors shared across devices and subsystems. It covers CPU cache synchronization, naming, and explicit/implicit synchronization interop through `sync_file` export and import.

Important APIs and types: `struct dma_buf_sync` contains `flags` combining `DMA_BUF_SYNC_START` or `DMA_BUF_SYNC_END` with read/write intent. `struct dma_buf_export_sync_file` returns a sync-file fd for current dma-buf fences. `struct dma_buf_import_sync_file` imports a sync-file fd as a read or write fence on a dma-buf. Ioctls are `DMA_BUF_IOCTL_SYNC`, `DMA_BUF_SET_NAME` plus Android-compatible `_A` and `_B` encodings, `DMA_BUF_IOCTL_EXPORT_SYNC_FILE`, and `DMA_BUF_IOCTL_IMPORT_SYNC_FILE`.

Control flow and state: For CPU mmap access, userspace brackets access with START and END using matching read/write flags so the kernel can maintain cache coherency. For explicit synchronization interop, userspace snapshots current implicit fences with EXPORT, schedules device work that waits on the returned sync file, then IMPORTs completion fences back into the dma-buf so implicit consumers see ordering. This is not atomic across export, work submission, and import; userspace must serialize against other contexts if strict ordering is required.

Persistence and dependencies: The persistent object is the dma-buf file and its attached reservation/fence state. The header depends on `<linux/ioctl.h>` and `<linux/types.h>`. Consumers include DRM, V4L2, media, GPU, display, Android graphics, and any dma-buf heap allocator user.

Integration points: Polling on dma-buf fds provides implicit sync waits. Export/import sync-file bridges explicit APIs such as Vulkan with implicit dma-buf users such as many media and OpenGL paths.

Risks and test signals: Risks include forgetting CPU sync brackets, assuming cache sync also prevents concurrent device access, using invalid flag combinations, fd leaks from sync-file export, Android ioctl number compatibility, and races between export and import. Tests should validate accepted flag masks, CPU mmap coherency on noncoherent platforms, poll equivalence for read/write fences, import visibility to later implicit consumers, rejected invalid flags/fds, and behavior across 32-bit and 64-bit userspace.
