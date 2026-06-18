# sources/distributed-fs/lizardfs/src/mount/fuse/daemonize.h

## Purpose
`daemonize.h` declares the mount daemon startup status helper functions.

## Important APIs, Types, And Functions
- `void daemonize_return_status(int status)` lets the child report startup result to the waiting parent.
- `int daemonize_and_wait(std::function<int()> run_function)` forks, runs the callback in the child, and returns the reported status in the parent.

## Control Flow
Callers pass the main mount startup function to `daemonize_and_wait`; child code may call `daemonize_return_status` earlier if it wants to unblock the parent before returning.

## State And Persistence
No header state. Implementation uses a process-global pipe.

## Dependencies And Integration Points
It includes `<functional>` and `common/platform.h`, and is used by FUSE mount startup code.

## Risks
- The callback executes after `fork`; it must be safe in the child process context.
- No API surface exposes fd cleanup or cancellation.

## Test Signals
Compile and behavior tests should include a simple callback returning a known status and a callback that reports before returning.
