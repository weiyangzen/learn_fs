# Research: sources/cloud-native/buildkit/executor/resources/monitor.go

## Purpose
Resource monitor for cgroup v2 execution samples.

## Important APIs, Types, and Functions
`Monitor`, `cgroupRecord`, `RecordOpt`, `NetworkSampler`, `nopRecord`; methods `RecordNamespace`, `Start`, `Close`, `CloseAsync`, `Wait`, `Samples`, `sample`, `NewMonitor`.

## Control Flow
Detects cgroup v2, optionally prepares controllers, records namespaces, samples CPU/memory/IO/PIDs/network every interval, captures final sample, computes host CPU delta, and removes records on close.

## State and Persistence
In-memory records/sample slices; reads cgroup/proc files but does not persist reports itself.

## Dependencies and Integration Points
Depends on procfs, cgroup v2 files, resource type definitions, and optional network samplers. Used by runc executor to return a resource `Recorder`.

## Risks and Edge Cases
No cgroup v2 or closed monitors degrade to no-op; permissions and sampling errors affect output.

## Test Signals
Parser tests cover components; full lifecycle needs cgroup integration.
