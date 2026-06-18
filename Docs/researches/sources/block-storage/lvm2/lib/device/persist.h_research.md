# File Research: sources/block-storage/lvm2/lib/device/persist.h

This header declares the persistent reservation API used by LVM command and metadata code. It defines string and numeric constants for supported reservation types: write exclusive, exclusive access, registrants-only variants, and all-registrants variants.

It also defines `SETPR_*` bit flags for user-facing persistent reservation options: enable/disable, require/norequire, autostart/noautostart, and PTPL/no-PTPL. `MAX_SETPR_ARGS` bounds comma-separated option parsing in `persist.c`.

The public API covers:
- PR state operations: `persist_check`, `persist_read`, `persist_start`, `persist_stop`, `persist_remove`, and `persist_clear`.
- VG lifecycle hooks: `persist_start_extend`, `persist_vgcreate_begin`, `persist_vgcreate_update`, `persist_finish_before`, `persist_finish_after`, and upgrade helpers for exclusive access.
- Query helpers for started/registered state and other-host detection.
- Key-file lifecycle helpers used by VG rename/remove paths.
- Device-level key/reservation functions for SCSI/NVMe dispatch and generic callers.

The header intentionally exposes NVMe-specific entry points while `persist.c` selects SCSI vs NVMe at runtime. Callers must provide full LVM context objects (`cmd_context`, `volume_group`, `device`, `dm_list`) and should treat integer return values as LVM-style success/failure booleans.
