# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/pusher_test.go

## Purpose
Tests Docker pusher upload paths, already-exists detection, reset behavior, and helper path generation.

## Important APIs, Types, And Functions
`TestGetManifestPath`, `TestPusherErrClosedRetry`, `TestPusherErrReset`, `Test_dockerPusher_push`, `samplePusher`, `tryUpload`, and `uploadableMockRegistry`.

## Control Flow
The mock registry handles minimal POST/PUT/HEAD registry APIs. Tests create a `dockerPusher`, toggle registry uploadability, write content through returned writers, and inspect commit errors or response channels. Reset testing forces the first PUT to return request timeout so `doWithRetries` replaces the pipe and the writer reports `content.ErrReset`.

## State And Persistence
Uses in-memory mock registry state (`availableContents`) and `NewInMemoryTracker`.

## Dependencies And Integration Points
Targets pusher behavior against actual `httptest.Server` HTTP paths and containerd content writer semantics.

## Risks And Edge Cases
The mock is intentionally small and does not exercise auth, upload redirects across hosts, mount-from success, or resumable/chunked uploads.

## Test Signals
Strong coverage for high-risk writer state transitions: incomplete close retry, reset and rewrite, remote already-exists, and digest-confirmed commit.
