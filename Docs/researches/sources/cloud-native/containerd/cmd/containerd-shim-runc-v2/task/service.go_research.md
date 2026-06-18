# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/task/service.go

## Purpose
Implements the shim's ttrpc task service for runc containers, bridging containerd task API calls to `runc.Container` and process state while publishing lifecycle/OOM events.

## Important APIs, Control Flow, And State
`NewTaskService` initializes OOM watchers, reaper subscription, process maps, platform, event forwarding, and shutdown socket cleanup. `service` stores containers, running PID mappings, exec counters, init exit stashes, exit subscribers, and event publisher. `Create`, `Start`, `Delete`, `Exec`, `State`, `Pause`, `Resume`, `Kill`, `Pids`, `CloseIO`, `Checkpoint`, `Update`, `Wait`, `Connect`, `Shutdown`, and `Stats` implement task API operations. `preStart` and `processExits` handle exit/start races by subscribing to early reaper events. `handleInitExit` kills remaining processes when needed and delays init exit publication until exec exits are published. Persistent/runtime state includes process maps, cgroup/OOM watchers, reaper events, task events, and shim shutdown callbacks.

## Dependencies And Integration
Uses task v3 API, event types, cgroups v1/v2, go-runc reaper, process/runc packages, OOM packages, namespace/event publishers, protobuf/typeurl, errgrpc, ttrpc, and shutdown service. It is the core runtime service used by containerd for runc v2 tasks.

## Risks And Test Signals
Risks include PID reuse races, missed early exits, event ordering regressions, exec counters not decremented on start failure, OOM watcher leaks, cgroup stat type mismatches, and shutdown before events flush. Tests should cover lifecycle API paths, early exit/start races, init-exit ordering with execs, OOM publishing, stats for cgroup modes, delete cleanup, and event forwarding during shutdown.
