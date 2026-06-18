# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-history-changelog.c

## Purpose
Implements historical changelog consumption APIs for libgfchangelog. It locates HTIME metadata files for a requested timestamp range, decodes historical `CHANGELOG.*` files into the history scratch area, and exposes an iterator over processed history entries.

## APIs, Types, and Functions
Public APIs include `gf_history_changelog()`, `gf_history_changelog_scan()`, `gf_history_changelog_next_change()`, `gf_history_changelog_done()`, and `gf_history_changelog_start_fresh()`. Search and consume helpers include `gf_changelog_extract_min_max()`, `gf_history_b_search()`, `gf_history_check()`, `gf_history_get_timestamp()`, `gf_history_consume()`, `gf_changelog_consume_wrap()`, and `gf_is_changelog_usable()`.

## Control Flow, State, and Persistence
`gf_history_changelog()` opens `<changelog_dir>/htime`, scans HTIME files, extracts min/max timestamp and total count from filename plus `trusted.glusterfs.htime`, binary-searches fixed-length NUL-terminated path records for start/end indexes, and spawns detached `gf_history_consume()`. The consume thread reads records in bounded parallel batches, ignores lower-case `changelog.*` placeholders for empty files, decodes usable changelogs with `gf_changelog_consume(..., no_publish=true)`, then publishes decoded files after joins succeed. `hist_done` moves from 1 while parsing, to 0 when done, or -1 on parse/publish failure. `gf_history_changelog_scan()` rewrites the history tracker file from `.processing`, and `next_change()` reads one tracker line for consumers; `done()` validates the path with `realpath()` and moves it to `.processed`.

## Dependencies and Integration
Depends on `gf_changelog_journal_t` from the journal handler, HTIME constants and xattrs from `changelog-misc.h`, Gluster syscall wrappers, pthreads, and decode/publish routines from `gf-changelog-journal-handler.c`. It is used by legacy consumers that need historical replay before or alongside live journal callbacks.

## Risks and Test Signals
Risks include fixed-length record assumptions, directory scan ordering, static `is_last_scan`, detached background parsing with shared `hist_done`, partial-history heuristics using a 20-second window, path-name based empty-changelog detection, and possible resource handling issues on mid-loop failures. Test signals include timestamp range boundary searches, missing/invalid HTIME xattrs, partial history return code 1, no-history return -2, parallel consume errors, scan/next/done iterator behavior, and protection against marking files outside the history scratch tree done.
