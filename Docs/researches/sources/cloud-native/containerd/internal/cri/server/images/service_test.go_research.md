
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/service_test.go -->
# sources/cloud-native/containerd/internal/cri/server/images/service_test.go

## Purpose

This test file provides the image service test harness and validates local image resolution and runtime-specific snapshotter selection.

## Important APIs, Types, and Functions

It defines constants `testImageFSPath` and `testSandboxImage`, helper `newTestCRIService`, `testImageConfig`, `TestLocalResolve`, and `TestRuntimeSnapshotter`.

## Control Flow

`newTestCRIService` builds a `CRIImageService` with fake image and snapshot stores, an empty runtime platform map, and test config, returning both core and gRPC wrapper objects. `TestLocalResolve` installs one fake busybox image with Docker-qualified references and asserts that digest ID, short names, tagged names, digest references, library-prefixed names, and Docker-qualified forms all resolve to the same image. A random ID is expected to return `NotFound`. `TestRuntimeSnapshotter` checks default and runtime override cases.

## State and Persistence Behavior

All state is in-memory fake stores and config structs. No snapshot syncer, content store, registry, or containerd client is used by these tests.

## Dependencies and Integration Points

Dependencies include CRI config, image and snapshot stores, errdefs, platform defaults, and assertion libraries. The helper is reused by other image package tests.

## Risks and Edge Cases

The test harness omits several real service dependencies, so methods that require client, images store, content store, or transfer service need additional setup. Local resolve tests do not cover invalid Docker reference parse diagnostics or multiple images sharing references.

## Test Signals

Passing tests prove Docker reference normalization behavior and default-versus-runtime snapshotter selection for the image service.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/service_test.go -->
