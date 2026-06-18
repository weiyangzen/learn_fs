# File Research: sources/cow-pools/openzfs/cmd/zfs/zfs_util.h

Shared utility header for the `zfs` command.

Defines:
- Includes `<libzfs.h>` for the userland ZFS handle API.
- C++ linkage guards for mixed C/C++ consumers.
- `safe_malloc(size_t size)`: allocation wrapper expected to terminate or report consistently on failure.
- `nomem(void)`: out-of-memory reporting helper.
- `extern libzfs_handle_t *g_zfs`: process-global libzfs handle used by `zfs` command modules.

Role:
- Centralizes common allocation/error helpers and the global libzfs command handle.
- Contains declarations only; command behavior lives in corresponding `.c` files.
