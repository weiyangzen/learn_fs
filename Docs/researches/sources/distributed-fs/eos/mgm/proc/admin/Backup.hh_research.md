# Research: sources/distributed-fs/eos/mgm/proc/admin/Backup.hh

## Purpose

`Backup.hh` declares `TwindowFilter`, an `IFilter` implementation used by backup creation to exclude version files, files outside a time window, and directories that no retained files require.

## Important APIs, Types, and Functions

- `TwindowFilter(const std::string& twindow_type, const std::string& twindow_val)` stores the filter dimension and threshold.
- `FilterOutFile(const std::map<std::string,std::string>& entry_info)` decides whether a file archive-entry should be skipped.
- `FilterOutDir(const std::string& path)` decides whether a directory archive-entry should be skipped.
- Private state includes `mTwindowType`, `mTwindowVal`, and `mSetDirs`.

## Control Flow

The intended flow is two-pass backup creation. First, file entries are scanned through `FilterOutFile()`, and accepted files populate `mSetDirs` with their ancestor directories. Second, directory entries are scanned through `FilterOutDir()`, which keeps only paths found in `mSetDirs`. If no time-window fields are configured, both methods keep everything.

## State and Persistence Behavior

The filter is purely in-memory and per-backup. It does not persist state. `mSetDirs` is an execution cache built by file filtering and consumed by directory filtering.

## Dependencies and Integration Points

It includes `ProcCommand.hh` for `IFilter` and logging base definitions, plus `<set>`. It is constructed in `Backup.cc` and passed to `ProcCommand::ArchiveAddEntries()`.

## Risks and Edge Cases

- Directory filtering only works if the same filter object sees the file pass before the directory pass.
- The header does not constrain `mTwindowType`; validation is done by `Backup()`.
- `FilterOutFile()` implementation depends on expected archive-entry keys such as `file`, `ctime`, or `mtime`.

## Test Signals

Tests should instantiate the filter with empty and non-empty time-window settings, feed file entries with older/newer times, verify version-file exclusion, verify ancestor directory retention, and verify directory filtering after and before file-pass population.
