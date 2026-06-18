# File Research: sources/cow-pools/bcachefs-tools/src/commands/reconcile.rs

## Purpose
Implements `bcachefs reconcile` command group for viewing and waiting on background reconcile accounting work.

## Main Interfaces
- Command group export: `CMD`
- Subcommands:
  - `CMD_STATUS`
  - `CMD_WAIT`
- CLI structs:
  - `StatusCli`
  - `WaitCli`
- Main helpers:
  - `reconcile_status_to_text`
  - `reconcile_wait_tui`
  - `reconcile_wait_headless`

## Behavior
- `status` opens a mounted filesystem, queries reconcile accounting, prints scan-pending state, per-type data/metadata work, and appends kernel `reconcile_status` sysfs text when available.
- `wait` triggers `internal/trigger_reconcile_wakeup`, then polls until selected reconcile work types are complete.
- In interactive terminals, wait mode uses an alternate-screen TUI with live updates and exits on `q`, Esc, or Ctrl-C.
- In non-interactive mode, wait mode sleeps one second between polls and produces no progress output.
- Default status types include all reconcile types; default wait types exclude `Pending`.

## Dependencies and Coupling
- Uses `BcachefsHandle` for mounted filesystem access.
- Uses sysfs files:
  - `reconcile_scan_pending`
  - `reconcile_status`
  - `internal/trigger_reconcile_wakeup`
- Uses accounting query mask `BCH_DISK_ACCOUNTING_reconcile_work`.
- Uses `DiskAccountingKind::ReconcileWork` decoding and `prt_reconcile_type`.

## Important Implementation Notes
- Per-type counters are stored as `[data_sectors, metadata_sectors]`.
- Output uses `Printbuf` tab-stop alignment and human-readable sector units.
- TUI uses crossterm and `run_tui` wrapper.

## Risks and Edge Cases
- Missing sysfs files are treated as zero or skipped depending on file.
- Headless wait has no timeout or status output.
- `event::poll(Duration::ZERO)` drains extra terminal input after a key event.
