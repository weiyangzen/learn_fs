# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_trim.rs

Command wrapper for issuing offline discard requests for free thin-pool data space.

CLI:
- Required `--metadata-dev`.
- Required `--data-dev`.
- `--quiet`.
- Adds verbose, version, and engine args.

Runtime behavior:
- Validates metadata device exists and is not tiny, and data device exists.
- Parses thin engine options.
- Runs full `thin_check` before trimming; if metadata check fails, reports to run `thin_check`/possibly `thin_repair` and returns `DATAERR`.
- Builds `ThinTrimOptions` and calls `thin::trim::trim`.
