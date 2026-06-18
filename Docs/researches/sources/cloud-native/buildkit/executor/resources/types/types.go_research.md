# Research: sources/cloud-native/buildkit/executor/resources/types/types.go

## Purpose
Shared resource sample data model and recorder interface.

## Important APIs, Types, and Functions
`Recorder`, `Samples`, `Sample`, `NetworkSample`, `CPUStat`, `MemoryStat`, `IOStat`, `PIDsStat`, `Pressure`, `PressureValues`.

## Control Flow
Executors return recorders; callers start/close/wait and retrieve nested stat samples.

## State and Persistence
In-memory data contract, serialized by higher layers as needed.

## Dependencies and Integration Points
Depends on context/time. Boundary between runtime collection and BuildKit reporting/API layers.

## Risks and Edge Cases
Pointer fields encode absent vs zero and must be preserved.

## Test Signals
Parser tests indirectly assert schema use.
