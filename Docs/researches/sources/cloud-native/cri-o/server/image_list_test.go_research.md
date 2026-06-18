<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_list_test.go -->
# sources/cloud-native/cri-o/server/image_list_test.go

## Purpose

This suite tests image listing and image conversion behavior.

## Important APIs, Types, and Functions

It calls `sut.ListImages` and `server.ConvertImage`, using mocked image server calls and parsed storage image references/IDs.

## Control Flow

List tests cover unfiltered success, filtered success through short-name resolution and image status, image list failure, and filtered status failure. Conversion tests cover empty tags/digests, tags and digests with size and numeric user, previous name plus digest fallback, and nil input.

## State and Persistence Behavior

No real image storage is mutated. Mock image server responses drive the results.

## Dependencies and Integration Points

The suite depends on gomock, OpenContainers digest, internal storage reference parsing, and CRI image types.

## Risks and Edge Cases

Artifact listing/status paths are not explicitly tested. Streaming list chunking is also not covered.

## Test Signals

The tests lock down the CRI conversion shape, especially user-to-UID handling and previous-name digest fallback.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/image_list_test.go -->
