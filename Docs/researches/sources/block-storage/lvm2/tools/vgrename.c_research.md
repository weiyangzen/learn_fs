# File Research: sources/block-storage/lvm2/tools/vgrename.c

Purpose: implements `vgrename`, renaming a VG by name or UUID while coordinating lock ordering, metadata updates, activation paths, backups, lockd, and persistent reservation key file names.

Read coverage: complete file read, 250 lines.

Key responsibilities:
- Validates exactly old and new VG identifiers and rename parameters.
- Handles old identifier as UUID, where the real old VG name is known only after `process_each_vg()`.
- Takes global lock, clears hints, and pre-locks the new VG name when lock ordering requires it.
- Rejects new names already found as VG names or matching an existing VG UUID string.
- Calls lockd pre-rename hook, renames PR key file if needed, updates VG metadata name, writes and commits.
- If activated device paths exist, refreshes visible LVs so `/dev/<old>` paths become `/dev/<new>`.
- Calls lockd final hook, removes old backups, unlocks the new VG name, and reports success.

Dependencies:
- Uses VG rename validation, lvmcache VG name/UUID lookup, lockd rename hooks, persistent key-file rename, activation path refresh, backup removal, and process-each-VG.

Risks and edge cases:
- UUID old-name mode suppresses normal pre-lock ordering because the real VG name is unknown beforehand.
- Error paths unlock the new name and notify lockd of failed rename.
- Path construction can fail if device directory plus VG name exceeds `PATH_MAX`.
