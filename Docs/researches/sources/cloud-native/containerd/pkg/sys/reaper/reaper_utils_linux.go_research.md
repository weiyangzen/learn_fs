<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/reaper/reaper_utils_linux.go -->
# sources/cloud-native/containerd/pkg/sys/reaper/reaper_utils_linux.go

## Purpose
Linux prctl helpers for child subreaper state.

## Important APIs, Types, And Functions
SetSubreaper sets PR_SET_CHILD_SUBREAPER; GetSubreaper reads PR_GET_CHILD_SUBREAPER.

## Control Flow
Thin wrappers around unix.Prctl.

## State And Persistence
Mutates/reads process kernel subreaper flag.

## Dependencies And Integration Points
Used by shim_linux.go.

## Risks And Edge Cases
Requires Linux prctl support; unsafe pointer is used for GetSubreaper output.

## Test Signals
No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/reaper/reaper_utils_linux.go -->
