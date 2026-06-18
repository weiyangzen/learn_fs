<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/helpers_unix.go -->
# sources/cloud-native/containerd/integration/client/helpers_unix.go

## Purpose
Provides Unix implementations for platform-dependent integration helpers.

## APIs, Types, And Functions
The file defines `forceRemoveAll` and `SkipTestOnHost` behind the `!windows` build tag.

## Control Flow And State
`forceRemoveAll` delegates directly to `os.RemoveAll`, reflecting that Unix test cleanup does not need Windows container layer unprepare/deactivate semantics. `SkipTestOnHost` always returns false because there is no Unix host-version skip encoded here.

## Persistence And Integration Points
The helper is used by daemon and fuzz cleanup paths that remove containerd roots, state directories, and temp workspaces. It integrates only with the standard library on Unix builds.

## Risks And Test Signals
The risk is broad recursive deletion if callers pass an unsafe path; this file does no guard enforcement. Test signal is indirect through all integration cleanup that expects Unix roots to be removable after daemon/task teardown.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/helpers_unix.go -->
