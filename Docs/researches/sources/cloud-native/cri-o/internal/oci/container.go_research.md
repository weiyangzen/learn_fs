# sources/cloud-native/cri-o/internal/oci/container.go

## Purpose
Defines CRI-O's in-memory container model, persisted container state, CRI projection helpers, PID identity verification, stop coordination, exec PID tracking, runtime-user/resource snapshots, checkpoint metadata, and monitor-process recovery. It is the shared state object consumed by OCI, conmon-rs pod, and VM runtime implementations.

## Important APIs, Types, and Functions
`Container` stores CRI metadata, paths (`bundlePath`, `dir`, log path), runtime handler, OCI spec, volumes, Linux resources, PID namespace handle, checkpoint/restore fields, and locks. `ContainerState` embeds `specs.State` and adds created/started/finished timestamps, exit/OOM/seccomp status, immutable init PID/start-time identity, checkpoint time, and `ContainerMonitorProcess`. `NewContainer`, `NewSpoofedContainer`, `CRIContainer`, `CRIAttributes`, `SetSpec`, `Spec`, accessors, `FromDisk`, `ContainerState.SetInitPid`, `Living`, `Pid`, `ProcessState`, `verifyPid`, `SetAsStopping`, `WaitOnStopTimeout`, `SetAsDoneStopping`, `StartExecCmd`, `DeleteExecPID`, `KillExecPIDs`, and `SetMonitorProcess` are the key APIs.

## Control Flow and State
Creation seeds CRI protobuf metadata and an empty state. `SetSpec` stores the OCI spec and derives CRI resources and runtime user. `FromDisk` decodes `state.json`, upgrading old state that only had `Pid` by recording `InitPid` and `InitStartTime`. PID use flows through `pid()`: state must exist, `InitPid` and runtime `Pid` must be valid, `kill(pid, 0)` must succeed, process start time must match saved start time, and zombie/dead states are treated as not found. Stop flow is coordinated by `stopLock`, a timeout channel, watcher channels, and a `stopKillLoopBegun` barrier that prevents new exec processes once SIGKILL looping starts.

## Persistence and Dependencies
Persistent state is `dir/state.json`; exit state is `dir/exit`; checkpoints live under `dir/checkpoint`. PID identity depends on OS-specific `getPidStartTime`/`getPidStatData`. The file integrates Kubernetes CRI protobufs, OCI runtime-spec, CRI-O storage image IDs and image references, namespace manager cleanup, checkpointctl metadata, goccy JSON, Podman signal parsing, and cgroups/runtime helpers through platform files.

## Integration Points
All runtime implementations mutate `ContainerState` under `opLock`. Server/image layers read CRI projections and resources. Runtime code reads `RuntimePathForPlatform`, log/bundle paths, exec cgroup paths, monitor process fields, stop signal, checkpoint paths, volumes, and PID identity helpers.

## Risks and Test Signals
High-risk areas are lock ordering, stop timeout channel closure, PID reuse/wrap protection, PID 0 exec registration, stale conmon PID reuse, and returning internal maps/pointers without deep copies. `container_test.go` covers accessors, resource projection, state reload upgrade, PID liveness and start-time mismatch, stop watcher races, exec PID tracking, and spoofed container behavior.
