# sources/cloud-native/moby/daemon/internal/containerfs/rm_nodarwin_test.go

## Purpose
Tests platform-independent non-Darwin removal behavior.

## APIs, Control Flow, and Integration
Tests assert `EnsureRemoveAll` does not error for a nonexistent path, a temporary directory, or a temporary file. The file is excluded on Darwin by build tag and covers both Unix and Windows implementations where applicable.

## State, Dependencies, and Risks
Tests operate on temp files/directories plus one fixed nonexistent path. They confirm the helper's contract not to return `os.ErrNotExist` for missing targets. They do not cover race retries, busy mount unmounting, or permission failures.
