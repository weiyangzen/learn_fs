<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/loop_watchdog.cc -->
# sources/distributed-fs/lizardfs/src/common/loop_watchdog.cc

## Purpose
Provides static storage and SIGALRM handler wiring for `SignalLoopWatchdog`. The source was read completely for this report.

## Important APIs, Types, And Functions
Defines `SignalLoopWatchdog::exit_loop_`, `alarmHandler`, `kHandlerInitialized`, and debug `refcount_`.

## Control Flow
At static initialization, the SIGALRM handler is registered. The handler sets a volatile flag consumed by active watchdog instances.

## State And Persistence Behavior
Global process signal handler state is modified; no file persistence.

## Dependencies And Integration Points
Depends on `loop_watchdog.h` and platform signal APIs.

## Risks And Edge Cases
Installing a process-wide SIGALRM handler can conflict with other components. Volatile bool is minimal signal communication, and debug refcount asserts only one watchdog.

## Test Signals
Needs runtime tests carefully isolating SIGALRM interactions; unit coverage is not present in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/loop_watchdog.cc -->
