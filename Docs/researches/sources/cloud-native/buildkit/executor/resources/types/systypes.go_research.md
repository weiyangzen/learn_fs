# Research: sources/cloud-native/buildkit/executor/resources/types/systypes.go

## Purpose
System-wide resource sample types.

## Important APIs, Types, and Functions
`SysCPUStat`, custom `MarshalJSON`, `ProcStat`, `SysMemoryStat`, `SysSample`, `Timestamp`.

## Control Flow
Samplers populate structs; JSON marshaling makes API/report output valid.

## State and Persistence
Data-only types.

## Dependencies and Integration Points
Depends on encoding/json, math, time. Used by system sampler and resource report consumers.

## Risks and Edge Cases
NaN/Inf CPU JSON handling is a serialization risk addressed by custom marshaling.

## Test Signals
Consumer serialization tests are expected.
