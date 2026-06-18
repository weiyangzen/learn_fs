# Research: sources/distributed-fs/eos/mgm/proc/admin/Backup.cc

## Purpose

`Backup.cc` implements legacy backup command support and the `TwindowFilter` used to restrict backup contents by `ctime` or `mtime`. The command builds a backup metadata file from namespace archive-entry scans, copies it into the source EOS tree under the backup file prefix, then asks the archive subsystem to copy that backup file to the destination.

## Important APIs, Types, and Functions

- `TwindowFilter::FilterOutFile()` filters version files and files older than the configured time window, while recording directories that must be retained.
- `TwindowFilter::FilterOutDir()` filters directories not needed by retained files.
- `ProcCommand::Backup()` parses `mgm.backup.*` CGI keys, validates URLs/time-window config, queues a backup job or performs creation, and triggers archive execution.
- `ProcCommand::BackupCreate()` creates temporary files, uses `ArchiveAddEntries()` for files and directories, writes the final backup header plus entries, copies it to EOS, and cleans temporary files.

## Control Flow

`Backup()` reads source and destination SURLs, ensures trailing slash, validates `XrdCl::URL`s, translates `file:` URLs to local MGM `root://<ManagerId>/...` URLs, validates the time-window type, parses comma-separated excluded xattrs, and either submits a queued backup job or performs immediate creation if `mgm.backup.create` is present.

`BackupCreate()` creates `/tmp/eos.mgm/backup.<threadid>` files, owns the temp directory as daemon uid/gid, scans file entries first with `ArchiveAddEntries(..., true, filter)`, then directory entries with the same filter, writes a JSON header that swaps src/dst because backups are treated as archive get operations from tape to disk, appends directory and file entries, and copies the local file to `<src>/EOS_COMMON_PATH_BACKUP_FILE_PREFIX/backup.file` as root. On success, `Backup()` builds an archive JSON command for that backup file and calls `ArchiveExecuteCmd()`.

## State and Persistence Behavior

The backup command itself persists no MGM config. It creates transient local temp files and a backup metadata file in EOS. Queued jobs are stored through `gOFS->SubmitBackupJob(job_spec)`. The final backup metadata includes source/destination URLs, metadata field lists, excluded xattrs, uid/gid, time-window values, timestamp, and entry counts.

The filter keeps `mSetDirs` in memory while scanning, so file scanning must happen before directory scanning; otherwise directory filtering would not know which ancestor directories to keep.

## Dependencies and Integration Points

This file depends on `common/Path`, `Backup.hh`, `XrdMgmOfs`, `XrdCl::CopyProcess`, `XrdCl::URL`, `ArchiveAddEntries()`, `ArchiveExecuteCmd()`, EOS backup path constants, and XRootD CGI parsing. It integrates with the legacy proc command path and the archive daemon protocol.

## Risks and Edge Cases

- `Backup()` dereferences `src_surl.rbegin()` and `dst_surl.rbegin()` before checking empty strings; empty inputs can be undefined behavior.
- `TwindowFilter::FilterOutFile()` assumes `entry_info["file"]` exists and uses `strtof()` without validating conversion errors.
- Temporary files under `/tmp/eos.mgm` are named only by thread id; concurrent reuse or stale files should be considered.
- Some error paths rely on cleanup of only files created so far; coverage should verify no leaked temp files.
- Copying as root with `eos.ruid=0&eos.rgid=0` is powerful and must stay constrained to generated backup-file paths.

## Test Signals

Tests should cover URL validation, `file:` URL conversion, empty URL handling, invalid time-window type, excluded xattr serialization, queued duplicate backup jobs, immediate backup creation, no-file backup behavior, temp-file creation/open failures, copy prepare/run failures, archive command construction, time-window filtering for files/directories, and filtering of `.sys.v#.` version files.
