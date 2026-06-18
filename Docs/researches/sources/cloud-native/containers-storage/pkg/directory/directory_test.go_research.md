## sources/cloud-native/containers-storage/pkg/directory/directory_test.go

Purpose: validates directory usage accounting and `MoveToSubdir`.

Important APIs/types/functions: tests for empty/nonempty files and directories, nested directory accounting, migration into subdir, non-existing directory errors, and `expectSizeAndInodeCount`.

Control flow: creates temporary directory trees, writes small files, calls `Usage`, compares expected size and inode count, and verifies renamed entries after `MoveToSubdir`.

State and persistence: uses real temporary files and directories.

Dependencies and integration points: covers Unix and Windows `Usage` contracts at a behavioral level, although expected inode counts depend on the active OS implementation.

Risks: no hard-link test despite Unix implementation deduping by inode. `MoveToSubdir` test does not cover destination collision or partial rename failure.

Test signals: basic filesystem behavior coverage; local execution blocked by absent `go`.
