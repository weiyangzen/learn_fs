# File Research: sources/cow-pools/bcachefs-tools/package-ci/scripts/status.sh

## Purpose
Command-line status reporter for package CI builds.

## Behavior
- Uses explicit commit argument or reads `$STATE_DIR/desired`.
- Validates that the commit build directory exists.
- Iterates job directories and prints status rows.
- Counts done, failed, building, and pending jobs.

## Notes
The script emits human-readable status symbols for done/failed/building/pending.
