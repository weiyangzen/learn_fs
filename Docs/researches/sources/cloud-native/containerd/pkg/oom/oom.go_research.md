# sources/cloud-native/containerd/pkg/oom/oom.go

Purpose: Linux OOM watcher interface shared by cgroup v1 and v2 implementations.

Important APIs/types/functions: `Watcher` requires `Close() error`, `Run(ctx context.Context)`, and `Add(id string, cg any) error`.

Control flow: interface-only. Implementations add cgroups to be watched, run an event loop, publish task OOM events, and close resources.

State/persistence: no state directly. Implementations hold kernel event fds, channels, or cgroup references.

Dependencies/integration: build-tagged Linux. Used by runtime/task services that need a common abstraction over cgroup versions.

Risks: `Add` accepts `any`, so type errors are runtime errors in implementations. Consumers must run the watcher loop and close it on shutdown.

Test signals: implementation tests should assert type checking, event publication, cancellation, and cleanup for both cgroup versions. This file provides compile-time contract only.
