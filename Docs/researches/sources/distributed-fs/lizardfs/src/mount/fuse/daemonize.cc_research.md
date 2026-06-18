# sources/distributed-fs/lizardfs/src/mount/fuse/daemonize.cc

## Purpose
`daemonize.cc` implements a small fork-and-wait helper for mount startup. The child runs a supplied function and reports its startup status to the parent through a pipe.

## Important APIs, Types, And Functions
- Static `gWaiter[2]` stores pipe fds.
- `daemonize_return_status(int status)` writes a status to the child pipe endpoint and closes it.
- `daemonize_and_wait(std::function<int()> run_function)` creates the pipe, forks, waits in the parent for an int status, and runs the function in the child.

## Control Flow
`daemonize_and_wait` initializes fds, creates a pipe, forks, and handles errors by printing to stderr and returning `1`. The parent closes the write end and reads an int; short read means failure status `1`. The child closes the read end, executes `run_function`, reports the returned status via `daemonize_return_status`, and returns it.

## State And Persistence
State is process-global pipe fd array. There is no persistence. After fork, parent and child have separate copies of the fds.

## Dependencies And Integration Points
It uses POSIX `pipe`, `fork`, `read`, `write`, and `close`; `daemonize.h` declares the functions. FUSE mount startup code can use it to report whether daemonized startup succeeded.

## Risks
- This helper forks but does not perform full daemonization steps such as `setsid`, cwd change, umask, or stdio redirection; those may happen elsewhere or not at all.
- On fork failure after pipe creation, fds are not closed.
- Parent does not close `gWaiter[0]` after read.
- Global `gWaiter` is not thread-safe or reentrant.

## Test Signals
Tests should cover run function success/failure, explicit early `daemonize_return_status`, short-read failure when child exits without writing, and pipe/fork error handling where injectable.
