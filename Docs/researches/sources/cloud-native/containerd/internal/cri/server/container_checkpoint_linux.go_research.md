# sources/cloud-native/containerd/internal/cri/server/container_checkpoint_linux.go

## Purpose

This Linux file implements CRI checkpoint export and checkpoint restore/import. It recognizes checkpoint OCI images or local checkpoint archives, reconstructs CRI/container metadata, reuses normal container creation with restore state, unpacks checkpoint payloads, and writes CRIU checkpoint archives.

## Important APIs, Types, and Functions

`checkIfCheckpointOCIImage` resolves an image and checks OCI index annotations for checkpoint metadata. `CRImportCheckpoint` imports a checkpoint archive/image into a CRI container. `CheckpointContainer` checkpoints a running container into an archive. `withCheckpointOpts` configures runtime checkpoint options. `writeCriuCheckpointData`, `writeRootFsDiffTar`, and `writeSpecDumpFile` extract blobs from containerd checkpoint content into checkpoint archive layout.

## Control Flow

Restore validates an image/archive input, detects OCI checkpoint image versus local file, mounts or partially unpacks checkpoint metadata into a temp directory, reads `spec.dump`, `config.dump`, and `status.dump`, fixes metadata/labels/annotations for the target sandbox, ensures the base image exists and is tagged, resolves the image, adjusts image config/env, annotates restore metadata, then calls `createContainer` with `restore=true`. After creation, it copies mounted checkpoint image content or fully unpacks the archive into the container root and restores `container.log` if present.

Checkpoint export verifies CRIU version, validates the container is running, records container config/status metadata, calls task checkpoint with runc options leaving the container running, reads the checkpoint image index, creates a temporary checkpoint directory, copies status/stats/log files, writes config/status dumps, extracts CRIU data/rootfs diff/spec blobs by media type, archives the directory to the requested location, deletes the temporary checkpoint image, and records metrics.

## State and Persistence Behavior

Restore creates temporary directories, snapshot views/mounts, CRI container root/volatile directories through `createContainer`, containerd containers/snapshots, CRI store entries, annotations, and restored log files. Checkpoint creates temporary checkpoint content under the container root, writes the requested archive, and deletes the internal checkpoint image. Both paths use defer cleanup for temp mounts/directories.

## Dependencies and Integration Points

It depends on checkpointctl metadata constants, CRIU utilities/stats, containerd client/content/images/mount/archive APIs, CRI stores/labels/annotations, image store resolution, snapshotter runtime config, OCI descriptors, and Linux runtime options. `CreateContainer` calls this path when the requested image is a checkpoint archive or checkpoint OCI image.

## Risks and Edge Cases

Restore has complex metadata rewriting for pod UID, container/pod labels, hash, and restart count. Base image tag conflicts are tolerated even if tag points to a different digest. Image-store resolve uses a bounded retry loop. Archive extraction defends against `..` only in CRIU checkpoint data extraction. Mount cleanup must run for OCI checkpoint images. Checkpoint requires a running container and sufficient CRIU support.

## Test Signals

Tests should cover checkpoint image detection, local archive metadata unpack filters, restore metadata fixups, base image pull/tag behavior, `createContainer` restore status, log restore, CRIU version failure, non-running checkpoint rejection, media-type extraction, path traversal rejection, and archive creation cleanup.
