# sources/cloud-native/cri-o/internal/lib/checkpoint_test.go

## Purpose
Tests `ContainerServer.ContainerCheckpoint` behavior for invalid input, container state validation, runtime failures, successful checkpointing, export paths, and storage unmount errors.

## Important APIs, Types, And Functions
- Exercises `sut.ContainerCheckpoint` with `metadata.ContainerConfig` and `lib.ContainerCheckpointOptions`.
- Uses mock storage store expectations, mock runtime configuration helpers, and CRIU availability checks.

## Control Flow
The main checkpoint tests set up dummy config/runtime state, skip when CRIU is unavailable, add a container/sandbox, configure container state/spec, and call checkpoint. Export test writes a custom OCI config with file and directory bind mounts, expects storage `Changes`, `Mount`, `Container`, and `Unmount` calls, and verifies success. Separate tests without full CRIU setup cover invalid ID and invalid `config.json` handling.

## State And Persistence
Creates temporary files/directories, writes test `config.json`, may create `cp.tar`, and removes test dump/export files. Mutates mocked container state to running where needed.

## Dependencies And Integration Points
Integrates CRIU utility version checking, checkpointctl metadata, runtime-spec state, containers/storage mocks, archive change fixtures, and CRI-O test setup helpers.

## Risks And Edge Cases
Tests are environment-sensitive because CRIU availability gates the main block. Some assertions depend on exact error strings. Export test uses `/tmp/` as a mocked mountpoint and verifies success rather than deeply inspecting tar contents.

## Test Signals
Good coverage for major checkpoint control-flow branches and error wrapping. It does not fully validate archive contents or cleanup on every failure path.
