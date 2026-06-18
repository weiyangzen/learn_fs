# File Research: sources/block-storage/lvm2/lib/format_text/archive.c

This file implements low-level text metadata archive listing, creation, expiration, and display. Archive files are expected to live in a directory and use a VG-derived name with a numeric index and `.vg` suffix.

Archive discovery:
- `_split_vg` parses filenames of the form `<vg>_<number...>.vg` and extracts the VG name and index.
- `_scan_archive` uses `scandir` with `versionsort` when available, filters entries for the requested VG, copies file names into a memory pool, and inserts them into a list sorted newest-first by index.
- `_insert_archive_file` maintains that sorted list.

Expiration and creation:
- `_remove_expired` walks old archives from the back of the list, removes files older than the configured retention days while preserving the minimum archive count, and warns if archive storage grows beyond broad size/count thresholds.
- `archive_vg` writes metadata to a temporary file, closes it safely, scans existing archive names to choose the next index, tries up to ten rename names using a random suffix, and then prunes expired archives.

Display:
- `_display_archive` creates a private text format instance for the archive file, reads metadata with timestamp and description, and prints file, VG name, description, and backup time.
- `archive_list` lists all archives for a VG from oldest display order by iterating the sorted list backward.
- `archive_list_file` displays one explicit archive path.
- `backup_list` displays the current backup file if present, using the same display path.

The file depends on text import/export, config parsing, LVM file helpers, and command context backup format support. It treats archive files as text metadata files and validates them by reading the VG before display.
