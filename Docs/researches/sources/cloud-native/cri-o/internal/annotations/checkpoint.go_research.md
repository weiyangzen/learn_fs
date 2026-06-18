# sources/cloud-native/cri-o/internal/annotations/checkpoint.go

## Purpose
Constants for annotations embedded in container checkpoint images.

## Important APIs, Types, and Functions
Exports CheckpointAnnotationName, RawImageName, RootfsImageID, RootfsImageName, CRIOVersion, and CriuVersion.

## Control Flow
No control flow.

## State and Persistence
Values are persisted in checkpoint image metadata by checkpoint code.

## Dependencies
No external deps.

## Integration Points
Used by checkpoint/restore image creation and consumers.

## Risks and Edge Cases
Renaming breaks checkpoint compatibility.

## Test Signals
Indirect checkpoint/restore tests validate it.
