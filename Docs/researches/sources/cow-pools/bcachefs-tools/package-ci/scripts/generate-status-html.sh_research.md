# File Research: sources/cow-pools/bcachefs-tools/package-ci/scripts/generate-status-html.sh

## Purpose
Generate a static CI status page at `$PUBLIC_HTML/ci.html`.

## Behavior
- Reads desired commit from `$STATE_DIR/desired`.
- Iterates build directories newest-first.
- For each commit, renders a table of job statuses except the source job.
- Links each job to `/ci-builds/$commit/$job/log`.
- Summarizes done/failed/building counts.
- Adds auto-refresh every 30 seconds and an updated UTC timestamp.
- Writes atomically through a temporary file then `mv`.

## Dependencies
Requires shell access to the CI state directory and public HTML directory.
