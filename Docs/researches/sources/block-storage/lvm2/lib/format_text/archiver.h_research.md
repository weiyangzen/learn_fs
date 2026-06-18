# File Research: sources/block-storage/lvm2/lib/format_text/archiver.h

This header declares the public archive and backup APIs. Its comment defines the key distinction: archives are pre-change historical VG configurations, usually kept under `/etc/lvm/archive`; backups are the current VG configuration, usually kept under `/etc/lvm/backup`.

The API includes initialization/exit/enable functions for archive and backup settings, archive display helpers, backup creation/removal, backup VG reading, restore-from-VG and restore-from-file paths, raw backup-to-file output, and `check_current_backup`.

Callers are expected to pass initialized `cmd_context` and `volume_group` objects, and restore callers must already hold appropriate ORPHAN and VG locks as documented in `archiver.c`.
