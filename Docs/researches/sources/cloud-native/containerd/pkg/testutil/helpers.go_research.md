<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/testutil/helpers.go -->
# sources/cloud-native/containerd/pkg/testutil/helpers.go

## Purpose
Shared test helpers for root-gated tests, directory dumping, and unmount cleanup.

## Important APIs, Types, And Functions
rootEnabled flag registration, DumpDir, DumpDirOnFailure, and Unmount.

## Control Flow
init registers or observes -test.root. DumpDir walks paths and logs symlink targets, small regular-file content, and metadata. Unmount calls mount.UnmountAll and asserts no error.

## State And Persistence
Reads filesystem and unmounts mount points during tests; no persistent state beyond registered flag.

## Dependencies And Integration Points
Depends on core/mount and testify/assert. Used across containerd tests.

## Risks And Edge Cases
DumpDir fatals on walk errors, so it is diagnostic but intrusive. Root flag interop handles continuity/testutil duplicate registration.

## Test Signals
Helpers are exercised by many tests, including namespace tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/testutil/helpers.go -->
