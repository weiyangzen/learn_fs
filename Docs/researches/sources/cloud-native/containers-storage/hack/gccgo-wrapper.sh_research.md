<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/gccgo-wrapper.sh -->
# sources/cloud-native/containers-storage/hack/gccgo-wrapper.sh

## Purpose
This wrapper works around gccgo include path behavior for vendored dependencies.

## Important APIs, Types, And Functions
It scans command arguments for directories containing `github.com/containers/storage/vendor` and appends `-I <vendor>` flags before execing `gccgo`.

## Control Flow
For each argument that is a directory with the vendor path, it accumulates include flags, then replaces the shell with `gccgo $addflags "$@"`.

## State And Persistence
No persistent state is written.

## Dependencies And Integration Points
The script integrates with gccgo build flows and references a Go issue in comments.

## Risks And Test Signals
Arguments with spaces are handled for original arguments but `addflags` is expanded as a string, so unusual paths could be fragile. It assumes gccgo is on `PATH`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/gccgo-wrapper.sh -->
