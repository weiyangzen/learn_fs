# Research: sources/cloud-native/buildkit/executor/resources/cpu.go

## Purpose
CPU cgroup v2 sampler for BuildKit resource monitoring.

## Important APIs, Types, and Functions
The key local helper returns `CPU` stats in `executor/resources/types` and parses `cpu.stat` and `cpu.pressure`, converts usec to ns, and records throttling/PSI.

## Control Flow
`Monitor.sample` calls it during periodic sampling; it reads cgroup files, parses key/value records, tolerates absent optional files where intended, and returns a typed stat object.

## State and Persistence
No persistence; samples kernel cgroup files at a point in time.

## Dependencies and Integration Points
Depends on Linux cgroup v2 file formats, PSI where applicable, and shared resource types. Integrated into executor resource recorders.

## Risks and Edge Cases
Kernel config/version affects file availability; malformed fields or missing required files can fail sampling.

## Test Signals
The paired test file covers parser output and optional/missing files.
