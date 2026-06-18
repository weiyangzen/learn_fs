<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_fs_info_test.go -->
# sources/cloud-native/cri-o/server/image_fs_info_test.go

## Purpose

This suite tests image filesystem usage reporting.

## Important APIs, Types, and Functions

It calls `sut.ImageFsInfo`, mocks storage store methods, creates a test directory, and checks returned filesystem entry counts.

## Control Flow

The success case sets graph root and image store to empty, graph driver to `test`, creates `test-images`, and expects one image and one container filesystem entry. The failure case leaves the driver name empty and expects an error.

## State and Persistence Behavior

The test creates and removes a local directory. Store behavior is mocked.

## Dependencies and Integration Points

It depends on gomock store expectations, the server harness, and filesystem access.

## Risks and Edge Cases

It does not test separate image store paths, inodes values, or permission errors.

## Test Signals

The tests confirm path construction for the shared storage-root case and that invalid storage paths surface errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_fs_info_test.go -->
