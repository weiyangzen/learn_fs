# sources/distributed-fs/ceph-client/fs/dlm/lockspace.h

## Purpose
`lockspace.h` declares the lockspace lifecycle and lookup API used outside `lockspace.c`. It is the narrow contract for creating, finding, releasing references to, and stopping DLM lockspaces.

## Important APIs
- `DLM_LSFL_FS` marks a kernel/filesystem lockspace and enables direct BAST/CAST callbacks through `LSFL_FS`.
- `dlm_lockspace_init()` and `dlm_lockspace_exit()` manage global lockspace subsystem setup.
- `dlm_find_lockspace_global()`, `dlm_find_lockspace_local()`, and `dlm_find_lockspace_device()` acquire active references by global id, opaque local pointer, or miscdevice minor.
- `dlm_put_lockspace()` releases a reference acquired by the find helpers.
- `dlm_stop_lockspaces()` stops running lockspaces when userland control is unavailable.
- `dlm_new_user_lockspace()` creates a userspace-facing lockspace. Kernel callers use the corresponding public API implemented in `lockspace.c`/DLM core, while this header exposes the user variant to internal user-device code.

## Control Flow and State
The header has no state. Its functions operate on `struct dlm_ls` and the global lockspace list maintained by `lockspace.c`. The `DLM_LSFL_FS` comment documents that the flag is internal and expected to be removed later, so consumers should avoid expanding its use.

## Dependencies and Integration Points
Consumers must have DLM types and `struct dlm_lockspace_ops` available from public/private DLM headers. The declarations are used by lock, user, recovery, and module lifecycle code to coordinate lockspace references and creation.

## Risks
- `dlm_find_lockspace_local()` treats an opaque `dlm_lockspace_t *` as `struct dlm_ls *`; callers must only pass valid live lockspace handles.
- The reference discipline is manual: every successful find must be matched by `dlm_put_lockspace()`.
- `DLM_LSFL_FS` is internal but still defined in a shared header, which can encourage coupling to a flag planned for removal.

## Test Signals
- Build tests should catch signature drift between `lockspace.h` and `lockspace.c`.
- Refcount tests should pair find/put calls under create/release concurrency.
- User lockspace creation tests should confirm `DLM_LSFL_SOFTIRQ` is rejected for user lockspaces while filesystem lockspaces can set FS behavior through the kernel creation path.
