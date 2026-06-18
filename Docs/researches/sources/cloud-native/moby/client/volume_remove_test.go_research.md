# sources/cloud-native/moby/client/volume_remove_test.go

## Purpose
Tests volume removal server errors, connection errors, method/path correctness, and force query encoding.

## APIs, Types, And Functions
The tests are `TestVolumeRemoveError`, `TestVolumeRemoveConnectionError`, and `TestVolumeRemove`. They use `Client.VolumeRemove`, `VolumeRemoveOptions`, mock `DELETE /volumes/volume_id`, and errdefs assertions.

## Control Flow, State, And Integration
Mock handlers assert method, path, and query values, then return status codes. The connection test uses a client pointing to an unreachable server to verify transport error behavior.

## Risks And Test Signals
Signals protect a destructive endpoint from method/path/query regressions. The tests do not cover driver-specific daemon side effects.
