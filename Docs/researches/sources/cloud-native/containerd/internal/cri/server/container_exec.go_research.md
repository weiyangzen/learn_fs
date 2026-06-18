# sources/cloud-native/containerd/internal/cri/server/container_exec.go

## Purpose
This file implements the streaming CRI `Exec` request setup. It validates container existence and running state, then asks the stream server to allocate an exec endpoint.

## Important APIs, Types, and Functions
`(*criService).Exec` reads `runtime.ExecRequest`, looks up the container in `containerStore`, records tracing attributes, checks `cntr.Status.Get().State()`, and returns `c.streamServer.GetExec(r)`.

## Control Flow, State, and Persistence
No task is created here; this only prepares a streaming endpoint. Runtime execution happens later through the streaming server and shared exec internals. State checks prevent exec against created/exited/unknown containers.

## Dependencies and Integration Points
It integrates CRI streaming, tracing, container store lookup, and status state conversion. `container_execsync.go` contains the lower-level exec process implementation used by synchronous and streaming paths.

## Risks and Test Signals
Risks include allowing exec into non-running containers or leaking ambiguous container lookup errors. This subset lacks a direct `Exec` test, so behavior is mainly protected through shared store/status conventions.
