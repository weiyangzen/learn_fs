# sources/cloud-native/moby/daemon/debugtrap_windows.go

## Purpose
Installs a Windows global named event listener that writes goroutine stack dumps when signaled.

## Important APIs, Types, And Functions
- `setupDumpStackTrap` builds the `Global\docker-daemon-<pid>` event name, creates the event, sets a finalizer to close the handle, and starts a wait goroutine.
- The goroutine calls `windows.WaitForSingleObject` and `stackdump.DumpToFile(root)`.

## Control Flow
On startup, the daemon creates a global event and waits forever. Each successful wait triggers a stack dump and then continues waiting. Errors creating the event or dumping stacks are logged.

## State And Persistence
Creates a Windows kernel event handle and writes dump files under the provided root when the event is set. The handle is closed by finalizer when the wrapper is collected.

## Dependencies And Integration Points
Uses Windows syscall APIs, process ID naming conventions, containerd logging, and Moby stackdump. The event is meant for external Windows diagnostic tooling to trigger.

## Risks And Edge Cases
Global event creation can fail due to permissions or namespace restrictions. The finalizer-based close is best-effort; the listener goroutine is process-lifetime.

## Test Signals
No direct unit tests; manual/integration validation is creating/signaling the named event and observing a dump file.
