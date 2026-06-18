# sources/cloud-native/moby/daemon/internal/containerfs/rm_test.go

## Purpose
Tests Linux/non-Windows/non-Darwin mount cleanup behavior for `EnsureRemoveAll`.

## APIs, Control Flow, and Integration
`TestEnsureRemoveAllWithMount` requires root, creates two temp dirs, bind-mounts one inside the other, calls `EnsureRemoveAll` asynchronously, fails on a 5-second timeout, and verifies the outer directory is gone.

## State, Dependencies, and Risks
The test mutates real mounts and skips when not root. It directly validates recursive unmount/busy-path handling, but depends on host mount permissions and can be skipped in most CI environments. It does not assert the secondary source directory remains intact beyond deferred cleanup.
