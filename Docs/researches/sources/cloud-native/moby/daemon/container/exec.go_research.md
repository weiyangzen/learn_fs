<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/exec.go -->
# sources/cloud-native/moby/daemon/container/exec.go

## Purpose
Defines exec configuration and an in-memory concurrent store for exec sessions associated with containers.

## Important APIs, Types, And Functions
`ExecConfig`, `NewExecConfig`, `ExecConfig.InitializeStdio`, `CloseStreams`, `SetExitCode`, `ExecStore`, `NewExecStore`, `Commands`, `Add`, `Get`, `Delete`, and `List`.

## Control Flow
New exec configs get a random ID, stream config, and `Started` channel. Stdio copies containerd direct IO to stream pipes and closes Windows stdin when not needed. Store operations lock around the map; `Commands` returns a shallow copied map.

## State And Persistence Behavior
Exec configs and store are runtime-only and are not serialized with containers. ExitCode is a pointer to distinguish unset from zero.

## Dependencies And Integration Points
Integrates containerd CIO, daemon stream config, libcontainerd process handles, random string IDs, and container exec API paths.

## Risks And Test Signals
Risks include shallow copy exposing mutable exec config pointers, callers needing to close `Started`, and runtime-only state loss after daemon restart. Exec API tests are downstream signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/exec.go -->
