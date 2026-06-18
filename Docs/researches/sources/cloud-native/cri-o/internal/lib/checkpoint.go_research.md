# sources/cloud-native/cri-o/internal/lib/checkpoint.go

## Purpose
Implements container checkpointing and optional checkpoint archive export for CRI-O containers, including runtime pause/checkpoint coordination, rootfs diff capture, metadata/spec dumps, bind mount type metadata, log capture, archive generation, and cleanup.

## Important APIs, Types, And Functions
- `ContainerCheckpointOptions` exposes `Keep`, `KeepRunning`, and `TargetFile`.
- `(*ContainerServer).ContainerCheckpoint` is the main checkpoint API.
- Helpers/constants: `containerMounts`, `bindMount`, `skipBindMount`, `getDiff`, `ExternalBindMount`, `prepareCheckpointExport`, and `exportCheckpoint`.

## Control Flow
`ContainerCheckpoint` looks up the container, loads `config.json`, requires running state, pauses the container, and defers status update/unpause/state persistence. If exporting, it writes spec/config dumps and bind mount metadata before invoking runtime checkpoint. On checkpoint failure it removes the checkpoint directory. If exporting, it captures rootfs diff/logs and writes a tar to `TargetFile`, then removes checkpoint directory. If `KeepRunning` is false it unmounts/stops storage. If `Keep` is false it deletes selected dump/stat files from the container directory.

## State And Persistence
Writes checkpoint artifacts under `ctr.CheckpointPath()`/`ctr.Dir()`, optional metadata JSON files (`spec.dump`, `config.dump`, `bind.mounts`), optional copied log file, rootfs diff tar components, and the final export file with mode `0600`. It updates in-memory/runtime status through runtime calls and persists container state to disk in the deferred path.

## Dependencies And Integration Points
Integrates `checkpointctl` metadata, CRIU stats filenames, OCI runtime-tools generator, CRI-O runtime/storage servers, Podman/common CRIU utilities, containers/storage archive diff/tar APIs, CRI-O annotations, and OCI container state.

## Risks And Edge Cases
Checkpointing pauses the container to reduce rootfs/log race windows, but exported files can still represent a point-in-time approximation. Export failure after runtime checkpoint can leave partial export files. `TargetFile` is opened with `O_RDWR|O_CREATE` but not `O_TRUNC`, so overwriting a larger existing file can risk trailing bytes. Cleanup of files and checkpoint dirs is best-effort in places. Bind mount source stat failures abort export prep.

## Test Signals
`checkpoint_test.go` covers invalid container ID, invalid config, not-running containers, successful checkpoint, runtime pause failure, export with bind mount metadata and rootfs diff, and storage unmount failure.
