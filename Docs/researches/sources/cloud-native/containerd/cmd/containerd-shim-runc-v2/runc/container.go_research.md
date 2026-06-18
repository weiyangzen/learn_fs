# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/runc/container.go

## Purpose
Wraps a runc container and its init/exec processes for the shim task service, handling create-time options, rootfs mounts, cgroups, process maps, and operation delegation.

## Important APIs, Control Flow, And State
`NewContainer` decodes runc options, converts rootfs mounts, creates `rootfs`, writes `options.json` and `runtime`, mounts rootfs components, constructs `process.Init`, calls `Create`, stores cgroup info, and returns a `Container`. Helpers read/write `options.json` and `runtime`. `Container` uses a mutex to manage init process, exec process map, and reserved exec IDs. Methods delegate start/delete/exec/pause/resume/resize/kill/closeIO/checkpoint/update to the process layer and remove execs on delete. `loadProcessCgroup` loads cgroup v1 or v2 by PID. Persistent state includes bundle option/runtime files, rootfs mounts, runc state, cgroup references, and process maps in memory.

## Dependencies And Integration
Uses task v3 API, runc options, cgroups v1/v2, mounts, namespaces, stdio platform, process package, errdefs/errgrpc, and typeurl. It is the object stored in `task.service.containers`.

## Risks And Test Signals
Risks include partial create cleanup, rootfs mount leaks, option file compatibility, concurrent exec ID races, cgroup load failures, and type assertions to `*process.Init`. Tests should cover create failure cleanup, rootfs mount/unmount, exec reservation, process lookup, cgroup modes, and checkpoint/update delegation.
