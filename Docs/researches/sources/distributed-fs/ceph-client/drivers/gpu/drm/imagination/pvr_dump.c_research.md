# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_dump.c

Purpose: decodes firmware context reset notifications into readable DRM log messages.

Important APIs/functions: `pvr_dump_context_reset_notification()` prints whether all contexts or a specific context reset, reset reason, data master, job reference, and page-fault address when present. Internal `get_reset_reason_desc()` maps Rogue reset reason enums to strings; `get_dm_name()` maps firmware data-master IDs to names.

Control flow and state: stateless. It receives FWCCB context-reset data and logs through `drm_info()` using the owning `pvr_device`.

Dependencies and integration: called from `pvr_ccb.c` when processing `ROGUE_FWIF_FWCCB_CMD_CONTEXT_RESET_NOTIFICATION`. Depends on firmware ABI enums and PowerVR device conversion.

Risks: unknown reset reasons/data masters are logged as `Unknown`; future firmware enum additions should update the mapping tables. This file logs diagnostics only and does not modify context state.

Test signals: firmware reset notification injection or hardware reset events should produce clear reset reason/data-master/job/page-fault logs.
