# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/uapi.c

## Purpose

`uapi.c` implements Tegra DRM per-file UAPI resource management for the newer channel API: opening/closing engine channels, mapping/unmapping GEM BOs into engine or memory-context address spaces, allocating/freeing/waiting on host1x syncpoints, and closing all resources on file teardown.

## Important APIs, Types, and Functions

- `tegra_drm_mapping_release()` and `tegra_drm_mapping_put()` release pinned host1x BO mappings and GEM BO references through krefs.
- `tegra_drm_channel_context_close()` drops a context's memory context, all mappings, xarray storage, host1x channel, and the context allocation.
- `tegra_drm_uapi_close_file()` closes every context and syncpoint in `struct tegra_drm_file`.
- `tegra_drm_find_client()` searches registered Tegra DRM clients by host1x class.
- `tegra_drm_ioctl_channel_open()` allocates a context, finds an engine client, requests or references a host1x channel, optionally allocates a host1x memory context, inserts the context into `fpriv->contexts`, and returns version/capability data.
- `tegra_drm_ioctl_channel_map()` looks up a context and GEM handle, pins the BO for read/write direction, records IOVA range, and inserts a mapping ID.
- `tegra_drm_ioctl_channel_unmap()` erases a mapping and drops its ref.
- `tegra_drm_ioctl_syncpoint_allocate/free/wait()` expose client-managed host1x syncpoint allocation and waiting.

## Control Flow

Channel open validates flags, allocates context state, finds a client matching `host1x_class`, obtains a shared or new channel, optionally allocates an isolated memory context when the engine and IOMMU support it, inserts the context into the file xarray with IDs starting at 1, initializes the mapping xarray, and returns client version and cache-coherency capability. Close erases the context under the file lock, then performs potentially blocking teardown outside the lock.

Mapping validates flags, locks file state, loads the context, allocates mapping state, chooses the mapping device as either the memory-context device or engine device, looks up the GEM BO, converts requested READ/WRITE flags into DMA direction, pins via `host1x_bo_pin()`, stores IOVA and IOVA end, allocates an ID in the context mapping xarray, and returns it. Unmap erases the mapping under the lock and then releases it.

Syncpoint allocate requests a host1x client-managed syncpoint, uses its host1x ID as the userspace handle, and inserts it into the per-file xarray. Free erases and puts it. Wait validates padding, resolves a syncpoint by global host1x ID without taking a ref, converts absolute timeout to jiffies, and waits until threshold or timeout.

## State and Persistence Behavior

`struct tegra_drm_file` persists for a DRM file and contains an IDR for legacy contexts, a mutex, and xarrays for new channel contexts and syncpoints. Each `tegra_drm_context` owns a host1x channel, optional memory context, client pointer, and mapping xarray. Each mapping owns a kref, host1x BO ref, host1x pin mapping, and IOVA range. File close tears down contexts before syncpoints; job submission can hold mapping refs after userspace unmaps them.

Memory contexts are tied to the current TGID at channel open. Syncpoint IDs are host1x-global IDs but lifetime is tracked per file through `fpriv->syncpoints`.

## Dependencies and Integration Points

The file depends on DRM file/ioctl plumbing, Tegra DRM client registration, host1x channels/syncpoints/memory contexts, Tegra GEM lookup, dma/IOMMU state, xarray, kref, and `drm_timeout_abs_to_jiffies()`. It provides state consumed by `submit.c`.

## Risks and Edge Cases

- `tegra_drm_uapi_close_file()` iterates xarrays and releases entries but does not erase before `xa_destroy()`; this is acceptable only if no concurrent lookup can occur during file teardown.
- Syncpoint wait uses `host1x_syncpt_get_by_id_noref()` by global ID rather than checking `fpriv->syncpoints`, so a file may wait on a syncpoint it did not allocate if it knows the ID.
- Mapping `iova_end` is computed but not used by `submit.c` relocation bounds, leaving range checking incomplete.
- Channel open does not call an engine `open_channel` callback visible in some clients; it directly uses `shared_channel` or `host1x_channel_request()`, so client-specific open hooks must be wired elsewhere or are bypassed for this UAPI version.
- File mutex is not used consistently around syncpoint allocate insertion, while free takes it; xarray concurrency expectations should be verified.
- DMA direction mapping is easy to misread: userspace READ maps to `DMA_TO_DEVICE`, WRITE maps to `DMA_FROM_DEVICE`, and READ_WRITE maps bidirectional.

## Test Signals

Tests should cover invalid flags, unknown host1x class, channel exhaustion, memory-context allocation errors and `-EOPNOTSUPP` fallback, cache-coherent capability reporting, map/unmap invalid context/handle/flags, DMA direction selection, mapping ID uniqueness, close-file cleanup with live mappings, syncpoint allocation with nonzero ID rejected, duplicate syncpoint insertion, free invalid ID, wait invalid padding/ID/timeouts, and interaction with live submitted jobs holding mapping refs.
