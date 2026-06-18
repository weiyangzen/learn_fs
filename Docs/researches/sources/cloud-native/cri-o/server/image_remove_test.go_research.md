<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_remove_test.go -->
# sources/cloud-native/cri-o/server/image_remove_test.go

## Purpose

This suite tests image removal behavior for storage images.

## Important APIs, Types, and Functions

It calls `sut.RemoveImage` and mocks image server methods for ID prefix resolution, candidate resolution, status, delete, and untag.

## Control Flow

Tests verify name-based untag success, full image ID deletion success, untag failure, candidate resolution failure, validation failure for empty image, idempotent success when full-ID delete reports unknown image, idempotent success when delete reports not-an-image, and idempotent success when untag reports not-an-image after concurrent deletion.

## State and Persistence Behavior

No real image storage is mutated. Mock expectations model storage behavior.

## Dependencies and Integration Points

The suite depends on containers/storage error types, gomock, CRI image request types, and internal storage reference/ID parsing.

## Risks and Edge Cases

It does not test artifact removal or image-volume in-use checks. It also does not assert container rootfs in-use behavior because storage owns that check.

## Test Signals

The suite strongly confirms CRI idempotency around image removal races and already-deleted images.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_remove_test.go -->
