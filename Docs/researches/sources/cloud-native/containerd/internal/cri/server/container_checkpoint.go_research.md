# sources/cloud-native/containerd/internal/cri/server/container_checkpoint.go

## Purpose

This non-Linux file stubs checkpoint/restore support for platforms where CRIU checkpointing is unavailable.

## Important APIs, Types, and Functions

`checkIfCheckpointOCIImage` returns empty result. `CRImportCheckpoint` returns `errdefs.ErrNotImplemented`. `CheckpointContainer` updates the checkpoint timer with a dummy runtime label for lint/metric consistency and returns an unimplemented gRPC status error.

## Control Flow

All functions immediately return. Checkpoint requests fail explicitly with `codes.Unimplemented`, and direct checkpoint import attempts fail with `errdefs.ErrNotImplemented`.

## State and Persistence Behavior

No state is read or written.

## Dependencies and Integration Points

It is selected by `//go:build !linux` and allows shared create-container code to compile while checkpoint images are ignored outside Linux.

## Risks and Edge Cases

Direct checkpoint requests and direct checkpoint imports are rejected. `checkIfCheckpointOCIImage` returning no image means normal `CreateContainer` image references do not enter checkpoint restore on non-Linux. Platform behavior differs from Linux restore support.

## Test Signals

Non-Linux tests should assert `CheckpointContainer` returns unimplemented and normal image create paths do not enter checkpoint restore.
