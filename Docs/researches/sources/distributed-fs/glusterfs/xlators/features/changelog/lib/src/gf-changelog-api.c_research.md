# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-api.c

Purpose: this file implements the simple live changelog consumer API layered over the changelog journal state. It lets consumers scan available changelog files, iterate their paths from a tracker file, reset iteration, and mark files processed.

Important APIs: `gf_changelog_done` validates a processed file path and renames it into the processed directory. `gf_changelog_start_fresh` truncates the tracker so iteration restarts. `gf_changelog_next_change` reads the next tracker line and returns it without the trailing newline. `gf_changelog_scan` scans the processing directory, writes changelog paths to the tracker, and rewinds the tracker for iteration.

Control flow: every API fetches `THIS`, then obtains the journal pointer through `GF_CHANGELOG_GET_API_PTR`. `scan` refuses work if the journal is API-disconnected, truncates the tracker, rewinds `jnl_dir`, iterates entries excluding `.` and `..`, writes full processing paths plus newline into the tracker, and seeks back to the start. `next_change` reads one line using the helper buffered reader. `done` resolves the input path and ensures it is within `jnl_working_dir` before renaming to `jnl_processed_dir`.

State and persistence behavior: persistent state consists of the journal working, processing, and processed directories plus the tracker file descriptor. `gf_changelog_done` is the state transition from processing to processed. `gf_changelog_scan` refreshes the tracker but does not consume files.

Dependencies and integration points: depends on GlusterFS globals, syscall wrappers, changelog journal structures, helper I/O functions, and changelog library messages. Public examples in C and Python call these APIs directly.

Risks: `gf_changelog_done` constructs `to_path` by concatenating `jnl_processed_dir` and `basename(buffer)` and assumes directory strings already carry separators. The realpath containment check is prefix-based; it relies on canonical paths and could be sensitive to similarly prefixed directories if not normalized with separator boundaries. `scan` writes entries one by one and breaks on write failure, returning `-1` unless it cleanly reaches end.

Test signals: scan empty and populated processing directories, iterate until zero, call done on valid and invalid paths, verify path traversal is rejected, simulate disconnected journals, write failures, and tracker truncation/reseek behavior.
