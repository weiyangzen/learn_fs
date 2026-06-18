<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/images_test.go -->
# sources/cloud-native/containers-storage/images_test.go

## Purpose
This test file validates image name history behavior and name ownership transfer between images.

## Important APIs, Types, And Functions
`newTestImageStore` creates a temporary read-write image store. `addTestImage` creates an image and assigns names. `TestAddNameToHistorySuccess` checks de-duplication of history entries. `TestHistoryNames` checks set/add/remove name operations and conflict handling.

## Control Flow
The main test creates two images with overlapping requested names, verifies the later image takes conflicting names, then reassigns many names to the first image and verifies the second loses them. It also tests add and remove operations preserving history.

## State And Persistence
Tests use a temporary store directory, writing real `images.json`, lockfiles, and image metadata through store APIs.

## Dependencies And Integration Points
The file depends on digest defaults, testify require, and image store internal methods.

## Risks And Test Signals
Coverage is focused on name history only. It is a useful regression signal for `updateNames` conflict transfer, but does not cover big data, reload, garbage collection, or read-only store behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/images_test.go -->
