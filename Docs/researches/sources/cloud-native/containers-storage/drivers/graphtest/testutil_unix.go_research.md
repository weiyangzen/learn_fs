# sources/cloud-native/containers-storage/drivers/graphtest/testutil_unix.go

## Purpose
`testutil_unix.go` provides Unix-specific metadata helpers for graphdriver tests.

## Important APIs, Types, And Functions
`verifyFile` checks file type, permissions, sticky/setuid/setgid bits, UID, and GID. `createBase` creates a base layer with a subdirectory and file using specific permissions and ownership. `verifyBase` validates that structure.

## Control Flow
`createBase` temporarily sets umask to zero, creates a writable layer, gets its root, creates test entries, applies chown, and puts the layer. `verifyBase` gets the layer and asserts root, subdir, file, and directory listing properties.

## State And Persistence
It writes deterministic base-layer content and metadata used by shared graphdriver tests.

## Dependencies And Integration Points
It depends on Unix stat data, `graphdriver`, `testify`, and `x/sys/unix`. `graphtest_unix.go` relies on these helpers for create/snapshot/template tests.

## Risks
Tests require permission to chown to UID/GID 1/2 or suitable test environment behavior. Umask restoration is important for process-wide test isolation.

## Test Signals
Strong signal for metadata preservation across driver create and snapshot operations.
