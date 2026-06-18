<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/images_fuzz_test.go -->
# sources/cloud-native/containerd/contrib/fuzz/images_fuzz_test.go

## Purpose
Fuzzes image validation/check logic.

## Important APIs, Types, And Functions
Defines `FuzzImagesCheck`.

## Control Flow
Generates image/descriptor-like structures and calls image check routines.

## State And Persistence
No persistent state beyond test-scoped objects.

## Dependencies And Integration Points
containerd image package and fuzz headers.

## Risks And Test Signals
Crash-resistance focus; does not prove images are runnable. Source size reviewed: 45 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/images_fuzz_test.go -->
