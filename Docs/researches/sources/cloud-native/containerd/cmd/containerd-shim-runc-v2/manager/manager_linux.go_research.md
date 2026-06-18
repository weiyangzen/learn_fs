# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/manager/manager_linux.go

## Purpose
Implements the Linux runc v2 shim manager used by containerd to bootstrap shim processes, report runtime info, and force-stop orphaned containers.

## Important APIs, Control Flow, And State
`NewShimManager` returns a `shim.Shim`. `Start` builds an exec command for the current binary with namespace/id/address flags, reads bundle `config.json` annotations to choose a grouping socket, creates one or two inherited Unix sockets, locks the OS thread for optional sched-core setup, starts the shim, optionally joins a configured shim cgroup, adjusts OOM score, and returns bootstrap protocol/address. `Stop` reconstructs bundle path and runc options, force-deletes the runc container, unmounts rootfs, and returns synthetic SIGKILL status. `Info` reads runtime options, resolves runtime binary, reports containerd version, options, and optional `runc features` output. Persistent state includes sockets, bundle files (`config.json`, `options.json`, `runtime`), cgroup membership, and rootfs mounts.

## Dependencies And Integration
Uses bootstrap APIs, shim helpers, runc wrapper files, cgroups v1/v2, OCI runtime features, namespaces, defaults, schedcore, mounts, and typeurl. It is called by containerd runtime v2 infrastructure.

## Risks And Test Signals
Risks include stale socket cleanup, grouping collisions, leaked sockets on partial start, cgroup join failures, thread lock/unlock around sched-core, and runtime feature command incompatibility. Tests should cover socket reuse, debug sockets, group labels, stop cleanup, options parsing, runtime lookup, and cgroup modes.
