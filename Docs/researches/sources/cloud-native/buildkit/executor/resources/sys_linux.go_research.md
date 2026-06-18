# Research: sources/cloud-native/buildkit/executor/resources/sys_linux.go

## Purpose
Linux system-wide resource sampler.

## Important APIs, Types, and Functions
`newSysSampler` and `sampleSys` use procfs to sample host CPU and memory.

## Control Flow
Creates a generic sampler whose callback reads `/proc/stat` and memory info into `SysSample`.

## State and Persistence
In-memory samples; read-only procfs access.

## Dependencies and Integration Points
Depends on prometheus procfs and Linux `/proc`. Adds host context to resource reports.

## Risks and Edge Cases
Procfs availability/field variation can affect output.

## Test Signals
No direct tests in this subset.
