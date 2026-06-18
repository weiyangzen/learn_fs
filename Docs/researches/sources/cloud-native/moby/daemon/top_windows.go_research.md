# sources/cloud-native/moby/daemon/top_windows.go

## Purpose
`top_windows.go` implements `docker top` for Windows containers using containerd/HCS task summaries.

## Important APIs, Types, And Functions
`ContainerTop` rejects ps arguments, obtains a running task, calls `task.Summary`, and returns titles `Name`, `PID`, `CPU`, and `Private Working Set`.

## Control Flow
After container lookup and restart/running validation, the function reads process summaries, formats combined kernel+user 100ns CPU time as `HH:MM:SS.mmm`, formats private working set with `units.HumanSize`, and appends rows to `TopResponse`.

## State And Persistence
No persistent state is changed.

## Dependencies And Integration Points
Integrates Windows task summaries from libcontainerd, API top response types, and Docker units formatting.

## Risks
Windows does not support Linux `psArgs`; clients passing args receive an error. CPU is cumulative time, not percentage.

## Test Signals
Windows top integration tests validate task summary mapping.
