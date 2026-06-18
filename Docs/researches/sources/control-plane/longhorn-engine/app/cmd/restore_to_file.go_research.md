# sources/control-plane/longhorn-engine/app/cmd/restore_to_file.go

## Purpose
Implements `backup restore-to-file`, restoring a Longhorn backup into a standalone raw or qcow2 image, optionally merging restored snapshot data with a qcow2 backing file.

## Important APIs, Types, and Functions
- Constants for default formats and temporary filenames.
- `RestoreToFileCmd()` defines CLI flags.
- `restore()` invokes backupstore delta restore into `backup.img` and displays progress.
- `restoreToFile()` orchestrates restore, backing-file handling, qemu conversion, rebase, commit, and cleanup.
- `outputFormatSupported()`, `CheckBackingFileFormat()`, `CopyFile()`, `CleanupTempFiles()`, `ConvertImage()`, `MergeSnapshotsToBackingFile()`, `rebaseSnapshot()`, `commitSnapshot()`.

## Control Flow
`restoreToFile` validates output format and backup URL, resolves output path, schedules temporary cleanup, restores the backup to `BackupFilePath`, then either converts the restored image directly to requested format or resolves/copies a backing file, converts backup to qcow2, rebases that qcow2 on the copied backing file, commits snapshot contents into the copied backing file, and converts the merged image to the requested output.

## State and Persistence Behavior
Creates local temporary files (`backup.img`, `backup.img.converted`, `backing.img.cp`) and the requested output image. Cleanup removes temps unless a temp path equals the output path. It does not mutate backupstore state, but reads backup contents and may copy/merge backing image data.

## Dependencies and Integration Points
Depends on backupstore delta restore APIs, `replica.NewRestore`, Longhorn exec wrapper, `qemu-img`, and `util.ResolveBackingFilepath`. It is called by `integration/common/cmd.py::restore_to_file` and likely exercised by backup data tests outside or around this subset.

## Risks and Edge Cases
`CleanupTempFiles` logs remove failures, which can happen when optional temp files were never created. External `qemu-img`, `cp`, and local working directory assumptions are critical. `CheckBackingFileFormat` uses textual `qemu-img info` output and only accepts qcow2. Progress loop relies on `RestoreDeltaBlockBackup` returning after kicking off restore object state; if progress never reaches terminal state it can wait indefinitely.

## Test Signals
Listed helpers expose `restore_to_file`; backup integration tests focus more on restore-to-volume, block integrity, backing image behavior, and backup metadata. There is no explicit unit test for qemu conversion helpers in this subset.
