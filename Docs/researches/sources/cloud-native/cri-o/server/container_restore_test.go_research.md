<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_restore_test.go -->
# sources/cloud-native/cri-o/server/container_restore_test.go

## Purpose

This Ginkgo suite exercises checkpoint restore import behavior from archives and OCI checkpoint images.

## Important APIs, Types, and Functions

It calls `sut.CRImportCheckpoint`, sets checkpoint restore configuration, uses CRIU availability checks, creates temporary tar archives with checkpoint metadata files, and sets gomock expectations on image/storage/runtime servers.

## Control Flow

Failure cases cover nonexistent archives, empty archives, invalid tar data, malformed `spec.dump`, missing or malformed annotations, broken `config.dump`, and OCI checkpoint image mount paths missing metadata. Success cases build archives containing spec annotations, mounts, masked/readonly paths, and config with either `rootfsImageName` or `rootfsImageRef`, then expect storage container creation/start and graph root access.

## State and Persistence Behavior

The tests write and remove local files such as `archive.tar`, `spec.dump`, and `config.dump`, and use temporary graph roots. Mock expectations stand in for persistent storage/runtime mutations.

## Dependencies and Integration Points

The suite depends on checkpoint-restore/go-criu, containers/storage archive utilities, runtime-spec and image-spec types, internal storage reference parsers, kubelet labels, and gomock.

## Risks and Edge Cases

Some tests skip without CRIU or when rootless. They validate many parse and validation branches but do not perform a real runtime restore; `StartContainer` restore behavior is covered separately only at a high level.

## Test Signals

The suite is a strong signal that restore import rejects malformed checkpoint inputs and enforces bind mount declaration instead of blindly trusting checkpoint metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_restore_test.go -->
