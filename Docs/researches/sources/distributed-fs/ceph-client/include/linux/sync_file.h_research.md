<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sync_file.h -->
# sources/distributed-fs/ceph-client/include/linux/sync_file.h

## Purpose

`sync_file.h` defines the userspace file descriptor wrapper for DMA fences. It lets drivers export one or merged fences as pollable files and lets userspace import a fence from an fd.

## Important APIs, types, and functions

`struct sync_file` contains the backing `struct file`, optional debugfs list node, waitqueue, flags, a `struct dma_fence *`, callback storage, and a user-provided merged-fence name buffer. `POLL_ENABLED` marks active polling. APIs are `sync_file_create()`, `sync_file_get_fence()`, and `sync_file_get_name()`.

## Control flow

A driver creates a sync file from a DMA fence, returns its fd to userspace, and userspace polls or passes it elsewhere. Poll setup attaches a fence callback that wakes the waitqueue when signaled. Importers call `sync_file_get_fence()` to resolve an fd back to a referenced fence.

## State and persistence behavior

The sync file persists as long as the file descriptor/reference exists. The fence reference tracks asynchronous GPU/display/DMA completion. Debug builds can list active sync files. Poll state is stored in `flags` and callback fields.

## Dependencies and integration points

It depends on file descriptors, waitqueues, debugfs optionally, and `dma_fence`. It integrates with DRM, DMA-BUF, display, GPU, camera, and media synchronization APIs.

## Risks and test signals

Risks include fence reference leaks, use-after-free around callbacks, polling after fence signal, incorrect merged names, and accepting unrelated fds. Tests should create/signaled/unsignaled fences, poll and wake behavior, fd import/export, release races, debugfs listing, and invalid fd handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sync_file.h -->
