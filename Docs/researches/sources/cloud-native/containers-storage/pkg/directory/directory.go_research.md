## sources/cloud-native/containers-storage/pkg/directory/directory.go

Purpose: platform-neutral directory utilities shared by OS-specific usage implementations.

Important APIs/types/functions: `DiskUsage` and `MoveToSubdir`.

Control flow: `MoveToSubdir` lists entries in `oldpath` and renames every entry except the target subdirectory into `oldpath/subdir/<name>`.

State and persistence: mutates directory layout via `os.Rename`. Does not create the subdir itself; caller must ensure it exists.

Dependencies and integration points: paired with `Usage`/`Size` implementations in OS-specific files. Used for store layout migrations.

Risks: rename can fail across filesystems or if destination entries exist. There is no rollback, so partial migrations can occur.

Test signals: `directory_test.go` covers moving four files into an existing subdirectory and usage accounting. Local execution unavailable due to missing `go`.
