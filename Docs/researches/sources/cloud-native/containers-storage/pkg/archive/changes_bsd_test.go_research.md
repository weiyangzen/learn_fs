# sources/cloud-native/containers-storage/pkg/archive/changes_bsd_test.go

## Purpose
This BSD-only test file validates that file flags are included in change detection on platforms where `chflags`/file flags matter.

## Important Test
`TestChangesWithFileFlags` creates two directories with a file of the same contents, applies a flag such as `UF_NODUMP` to the new file, runs `ChangesDirs`, and expects a single `ChangeModify` entry for `/file`.

## Control Flow and State
The test creates old and new temp directories, writes matching files, changes flags on the new file through `unix.Chflags`, runs the directory comparison, and asserts the exact change list. The persistent state under test is filesystem file flags.

## Dependencies and Integration Points
The file depends on `golang.org/x/sys/unix`, `testify/require`, `idtools`, and `changes.go` plus BSD file-flag helpers. It complements `fflags_bsd.go` and platform-specific stat comparison behavior.

## Risks and Edge Cases
It tests one flag and one file. It does not validate tar header preservation of flags directly; archive round-trip behavior is covered through other platform-specific file flag code.

## Test Signals
The test confirms that metadata-only file flag differences are not ignored by `ChangesDirs`, which is important for faithful layer diffing on BSD-like systems.
