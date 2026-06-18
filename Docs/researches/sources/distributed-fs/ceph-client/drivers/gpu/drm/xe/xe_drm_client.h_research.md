<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_client.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_client.h

## Purpose
`xe_drm_client.h` defines the lightweight client accounting object and inline refcount helpers used by BO tracking and fdinfo reporting.

## Important APIs, types, and functions
`struct xe_drm_client` contains a kref, numeric id, and, under `CONFIG_PROC_FS`, a spinlock-protected `bos_list`. Inline `xe_drm_client_get()` and `xe_drm_client_put()` manage references through `__xe_drm_client_free()`. Public declarations cover allocation, fdinfo output, and BO add/remove hooks, with no-op BO hooks when procfs is disabled.

## Control flow and integration points
The header has only inline refcount control. BO creation paths call add/remove when internal objects need client accounting. DRM driver fdinfo callbacks call `xe_drm_client_fdinfo()` under procfs.

## State and persistence behavior
The client object persists while held by an open `xe_file` and by any internal BOs linked for accounting. The list is protected by `bos_lock`; when procfs is disabled no list state exists.

## Dependencies, risks, and test signals
Dependencies include Linux kref/list/spinlock and DRM file/printer declarations. Risks include double add/remove of BO client links, refcount imbalance, and conditional-build drift between procfs and non-procfs configurations. Test signals are open/close refcount stress, internal BO lifetime tests, procfs fdinfo reads, and allmodconfig/no-procfs builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_client.h -->
