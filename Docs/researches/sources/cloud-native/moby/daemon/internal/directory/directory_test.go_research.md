# sources/cloud-native/moby/daemon/internal/directory/directory_test.go

## Purpose
Tests exported directory size behavior.

## APIs, Control Flow, and Integration
The suite creates temp dirs/files and verifies empty dirs, empty files, 5-byte files, empty nested dirs, file plus empty nested dir, file plus nonempty nested file, and nonexistent root errors. It calls `Size(context.Background(), ...)` in all cases.

## State, Dependencies, and Risks
State is temporary filesystem content. Tests validate file byte summation and error propagation, but not context cancellation, hard-link de-duplication on Unix, disappearing child paths during walk, or Windows-specific hard-link double counting.
