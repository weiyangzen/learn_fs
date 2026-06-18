# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/dnotify_test.c

## Purpose
Manual/extended dnotify sample that prints events for modifications or file creation in the current directory.

## Important APIs, Types, And Functions
Uses `sigaction` with `SA_SIGINFO`, `F_SETSIG`, `F_NOTIFY`, `DN_MODIFY`, `DN_CREATE`, `DN_MULTISHOT`, and signal handler storing `si_fd` in `event_fd`.

## Control Flow
It installs a realtime signal handler, opens `.`, configures dnotify to send `SIGRTMIN+1`, and loops forever pausing and printing the fd that generated an event.

## State And Persistence
Holds one directory fd and installs process signal state. No file writes.

## Dependencies And Integration Points
Built as `TEST_GEN_PROGS_EXTENDED`, useful as a manual test rather than finite automated kselftest.

## Risks
The infinite loop means it is unsuitable for default automated runs. It does not check return values for `sigaction`, `open`, or `fcntl`.

## Test Signals
Console output `Got event on fd=...` after creating/modifying files in the directory confirms dnotify delivery.
