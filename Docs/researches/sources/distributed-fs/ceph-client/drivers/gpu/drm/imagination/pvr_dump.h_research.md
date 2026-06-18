# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_dump.h

Purpose: declares the firmware context-reset dump helper.

Important API: `pvr_dump_context_reset_notification(struct pvr_device *pvr_dev, struct rogue_fwif_fwccb_cmd_context_reset_data *data)`.

Control flow and state: no state in the header; FWCCB processing passes reset data to the implementation for diagnostic logging.

Dependencies and integration: forward declares `pvr_device` and the firmware context reset data struct, keeping callers decoupled from full dump implementation details.

Risks: purely diagnostic API; callers must not expect it to reset or mark contexts faulty.

Test signals: compile coverage from CCB processing and runtime reset-notification logs.
