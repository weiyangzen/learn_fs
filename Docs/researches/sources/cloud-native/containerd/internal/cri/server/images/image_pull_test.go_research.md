
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_pull_test.go -->
# sources/cloud-native/containerd/internal/cri/server/images/image_pull_test.go

## Purpose

This test file covers image pull support logic: registry auth parsing, registry mirror endpoint construction, default scheme choice, encrypted pull options, snapshotter selection from runtime handler or annotation, pinned-image labels, and progress reporter behavior.

## Important APIs, Types, and Functions

Tests include `TestParseAuth`, `TestRegistryEndpoints`, `TestDefaultScheme`, `TestEncryptedImagePullOpts`, `TestSnapshotterFromPodSandboxConfig`, `TestImageGetLabels`, `TestTransferProgressReporter`, and `TestPullProgressReporter`.

## Control Flow

Auth tests exercise nil, empty, identity token, username/password, base64 auth, invalid auth, and server-address matching. Endpoint tests configure mirror maps and assert default endpoint addition, wildcard behavior, host-specific precedence, missing scheme handling, localhost HTTP defaults, and paths. Snapshotter tests configure runtime-specific snapshotter mappings and validate precedence of the explicit runtime handler over the deprecated annotation.

Progress reporter tests feed synthetic transfer progress events and assert active request and byte counts, ignored malformed progress nodes, completion without explicit complete events, timeout cancellation, and multiple concurrent nodes. Local pull progress tests manually increment request and bytes counters to prove stuck requests are canceled and progressing requests are not.

## State and Persistence Behavior

All tests use in-memory service config, maps, fake contexts, and reporter counters. They do not contact registries, write image metadata, or unpack snapshots.

## Dependencies and Integration Points

Dependencies include CRI runtime API, CRI config, CRI labels/annotations, containerd transfer progress types, image-spec descriptors, platform defaults, base64 encoding, time, and assertion libraries.

## Risks and Edge Cases

The tests validate support functions but not full `PullImage` success or failure with containerd. Progress timeout tests use real timers and short sleeps, which can be sensitive under high load. Encrypted pull option test currently only checks option count, not functional decryption.

## Test Signals

Passing tests provide strong regression signals for auth precedence, mirror endpoint compatibility, snapshotter-selection compatibility with older clients, pinned image labeling, and the no-progress cancellation bug class called out in the comments.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_pull_test.go -->
