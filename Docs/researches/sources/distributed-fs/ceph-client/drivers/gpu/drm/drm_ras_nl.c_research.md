# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ras_nl.c

Purpose: generated YNL Generic Netlink specification binding for DRM RAS commands, policies, operations, and family metadata.

Important APIs/types/functions: `drm_ras_get_error_counter_do_nl_policy` requires node ID and error ID as `NLA_U32` for do requests. `drm_ras_get_error_counter_dump_nl_policy` accepts node ID for dump requests. `drm_ras_nl_ops` binds `DRM_RAS_CMD_LIST_NODES` and `DRM_RAS_CMD_GET_ERROR_COUNTER` to dumpit/doit handlers. `drm_ras_nl_family` defines family name, version, netns support, parallel ops, module owner, split ops, and op count.

Control flow: Generic Netlink dispatch validates attributes with the policy associated with each split op, enforces admin permission flags, and calls handlers implemented in `drm_ras.c`.

State and persistence behavior: family and ops tables are static; `drm_ras_nl_family` is marked `__ro_after_init`.

Dependencies and integration points: generated from `Documentation/netlink/specs/drm_ras.yaml`; depends on UAPI `drm_ras.h`, netlink/genetlink headers, and handler prototypes from `drm_ras_nl.h`.

Risks: generated files should not be hand-edited; mismatch with YAML or UAPI breaks userspace tooling. `parallel_ops = true` means handlers must be concurrency safe. Admin permission flags restrict access and need to match intended observability.

Test signals: YNL regeneration diff, family registration, policy rejection for missing/wrong attrs, admin permission behavior, list and get command dispatch, and build checks after UAPI changes.
