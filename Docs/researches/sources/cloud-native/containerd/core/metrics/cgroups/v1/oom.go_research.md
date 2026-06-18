# sources/cloud-native/containerd/core/metrics/cgroups/v1/oom.go

Purpose: monitors cgroup v1 OOM eventfds with epoll, exposes OOM counts as Prometheus metrics, and triggers task OOM events.

Important APIs and types: `newOOMCollector`, `oomCollector`, `oom`, `Add`, `Describe`, `Collect`, `Close`, `start`, `process`, and `flushEventfd`.

Control flow: `newOOMCollector` creates an epoll fd, optionally creates a `memory_oom` descriptor and registers with the metrics namespace, then starts an epoll loop goroutine. `Add` obtains a cgroup OOM event fd, stores an `oom` record keyed by fd, and registers fd with epoll. `start` waits forever in `EpollWait`, retrying through EINTR, and calls `process` for ready fds. `process` flushes the eventfd, removes and closes deleted cgroups, otherwise increments an atomic count and invokes triggers. `Collect` emits current counts as counters.

State and persistence: runtime-only epoll fd, fd-to-oom map, and per-cgroup atomic counters. No persistent state.

Dependencies and integration: integrates cgroup1 `OOMEventFD`, cgroup state, task monitor trigger callbacks, unix epoll/eventfd reads, Docker metrics, Prometheus, and logging.

Risks: `Describe` emits `nil` descriptor if namespace was nil and the collector is still used directly. FDs stay registered until an event indicates deletion; idle stopped tasks may retain registrations. Event loop exits permanently on epoll wait errors.

Test signals: not directly tested in subset; cgroup v1 monitor wires it in `cgroups.go`.
