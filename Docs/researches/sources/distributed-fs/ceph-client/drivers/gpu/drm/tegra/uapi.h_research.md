# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/uapi.h

## Purpose

`uapi.h` declares the Tegra DRM private per-file state, BO mapping state, new channel/syncpoint ioctl entry points, and mapping close helpers shared by `drm.c`, `uapi.c`, and `submit.c`.

## Important APIs, Types, and Functions

- `struct tegra_drm_file` stores legacy context IDR state plus new UAPI xarrays for channel contexts and syncpoints, protected by `lock` for many operations.
- `struct tegra_drm_mapping` owns a kref, host1x BO mapping, host1x BO ref, and IOVA start/end.
- Ioctl declarations cover channel open/close/map/unmap/submit and syncpoint allocate/free/wait.
- `tegra_drm_uapi_close_file()` tears down per-file UAPI resources.
- `tegra_drm_mapping_put()` drops a mapping reference.

## Control Flow

The header has no runtime control flow. It defines the contracts used by the DRM file open/close and ioctl dispatch paths.

## State and Persistence Behavior

The declared structures are long-lived per DRM file or per mapped BO. Context and syncpoint xarrays persist until explicit close/free or file teardown. Mapping krefs allow submitted jobs to outlive userspace unmap calls safely.

## Dependencies and Integration Points

It includes DMA mapping, IDR, kref, xarray, and DRM declarations. It depends on host1x BO types defined through surrounding Tegra DRM includes. `submit.c` uses mapping refs and ioctl declaration; `uapi.c` owns implementation.

## Risks and Edge Cases

The locking contract is implicit. Callers must know which xarray operations require `tegra_drm_file.lock` and which are safe through xarray locking or teardown context. Exposed `iova_end` suggests range validation, but correctness depends on submit/firewall users checking it.

## Test Signals

Build coverage verifies ioctl declarations match dispatch tables. Runtime tests should assert file close destroys every context/syncpoint and that mapping refs are balanced with job submission.
