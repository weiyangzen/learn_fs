# File Research: sources/block-storage/lvm2/lib/format_text/archiver.c

This file provides command-context lifecycle and high-level workflows for metadata archives and backups. Archives are pre-change historical copies; backups are the current post-change VG metadata copy.

Initialization and control:
- `archive_init`, `archive_exit`, and `archive_enable` manage `cmd->archive_params`, including directory, retention days, minimum archive count, and enabled state.
- `backup_init`, `backup_exit`, and `backup_enable` manage `cmd->backup_params`, including directory, enabled state, and warning suppression count.
- `_build_desc` creates descriptions recording whether metadata was created before or after executing the command line.

Archive/backup creation:
- `_archive` skips orphan VGs, disabled archive configs, test mode, and already-archived VGs. When enabled it creates the archive directory, handles read-only filesystems differently for compulsory vs best-effort calls, and calls `archive_vg`.
- `archive` wraps `_archive` with signal-interrupt handling.
- `backup_locally` creates the backup directory and writes the current backup with `_backup`, while warning if backups are disabled. `backup` unlocks memory first and skips orphan VGs.
- `backup_to_file` creates a private text-format instance and writes/commits VG metadata through its metadata area operations.

Read and restore:
- `backup_read_vg` reads a VG from a backup file through the backup text format instance and attaches PV devices with `set_pv_devices`.
- `_restore_vg_should_write_pv` decides whether a PV label/metadata must be written during restore, considering `do_pvcreate`, format feature support, and cached PV extension flags.
- `backup_restore_vg` optionally recreates PV structures, removes existing metadata areas, builds a new format instance, schedules PV writes, runs format-specific PV setup, optionally wipes labels/initial sectors, then performs `vg_write` and `vg_commit`.
- `backup_restore_from_file` reads a VG, rejects missing PV restores, requires `--force` for thin volumes, validates LV segment completeness, and restores the VG.
- `backup_restore` resolves the standard backup path and delegates.

Maintenance:
- `backup_remove` silently unlinks a current backup.
- `archive_display` and `archive_display_file` list archive/backup metadata.
- `check_current_backup` verifies the current backup matches VG seqno and ID; when stale, it archives the old backup, archives the current VG, and writes a fresh backup. It suppresses noisy read errors while checking.

The code is careful around test mode, read-only filesystems, signal handling, and orphan VGs. It uses both command memory pools and ordinary `strdup/free` for long-lived context settings.
