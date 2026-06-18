# sources/cloud-native/moby/daemon/server/router/image/image_list_response_test.go

## Purpose
This test verifies legacy image-list JSON compatibility for the `VirtualSize` field.

## Important APIs, Types, And Functions
`TestImageListVirtualSize` builds `image.Summary` values, wraps them with `compat.Wrap` and `compat.WithExtraFields`, marshals to JSON, and asserts `VirtualSize == Size` for old API behavior.

## Control Flow
The test has two subtests: one validates the wrapped pre-1.44 response includes `VirtualSize`; the other validates direct marshaling for newer APIs omits it.

## State And Persistence
No state is persisted. The test validates response serialization only.

## Dependencies And Integration Points
It protects the wrapping path in `getImagesJSON` and depends on API image types plus daemon `compat`.

## Risks
Removing or renaming legacy fields can break old clients that still expect `VirtualSize`.

## Test Signals
The test directly asserts the JSON-level wire contract rather than only Go struct fields.
