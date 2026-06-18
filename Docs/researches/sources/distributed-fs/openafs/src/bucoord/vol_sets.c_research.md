# sources/distributed-fs/openafs/src/bucoord/vol_sets.c

## Purpose
Implements volume-set command handlers and BUDB text-block synchronization. It creates/deletes/lists volume sets, adds/deletes volume entries, parses the stored text format, saves persistent sets, and refreshes in-memory state on BUDB version changes.

## Important APIs, Types, And Functions
Command handlers are `bc_AddVolSetCmd`, `bc_DeleteVolSetCmd`, `bc_AddVolEntryCmd`, `bc_DeleteVolEntryCmd`, and `bc_ListVolSetCmd`. Persistence/support functions are `bc_ClearVolumeSets`, `bc_ParseVolumeSet`, `bc_SaveVolumeSet`, and `bc_UpdateVolumeSet`; `ListVolSet` formats one set.

## Control Flow
Command handlers refresh the current volume-set text, lock `TB_VOLUMESET` for persistent sets, perform model mutations through `dsvs.c`, save when needed, and unlock. Temporary volume sets skip locking and saving. Parsing reads a repeated text format of `volumeset <name>`, one or more `<server> <partition> <volume-regexp>` lines, and `end`, allocating linked `bc_volumeSet` and `bc_volumeEntry` records. Saving truncates the stream and writes all non-temporary sets in the same format before sending it to BUDB. Updating checks text version, locks if stale, clears only non-temporary existing sets, downloads text into a temp stream, fetches the server version, parses, and optionally unlocks.

## State And Persistence
State is `bc_globalConfig->vset` and text handle `configText[TB_VOLUMESET]`. Persistent volume sets are stored in BUDB text. Temporary sets live only in memory and are preserved across refreshes by `bc_ClearVolumeSets`.

## Dependencies And Integration Points
Depends on BUDB text helpers from `ubik_db_if.c`, model helpers from `dsvs.c`, command/com_err APIs, and `bc_globalConfig`. `commands.c` uses the resulting volume sets to evaluate dumps/restores.

## Risks And Test Signals
`bc_AddVolEntryCmd` reports an uninitialized/old `code` if a set is missing before `ERROR(code)`. Several refresh failure paths return without unlocking when they already hold the lock. Parser errors can leak partially allocated structures, and host-parse failures are logged but do not stop entry creation until partition parsing. Fixed-size `%255s` parsing disallows whitespace and truncates long fields. Test signals include persistent and temporary set lifecycle, entry add/delete by 1-based index, malformed text with missing `end`, stale version refresh preserving temporary sets, save failure session-only behavior, wildcard host/partition entries, invalid regex strings surfaced later by volume evaluation, and listing selected/all sets.
