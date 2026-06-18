# sources/distributed-fs/lizardfs/src/uraft/uraftcontroller.h

## Purpose
`uraftcontroller.h` declares the controller layer that turns uRaft status changes into LizardFS metadata-server management actions.

## Important APIs, Types, and Functions
`uRaftController` extends `uRaftStatus`. Its `Options` adds local master host/port, elector mode, status polling periods, get-version timeout, promote/demote timeouts, and dead-handler timeout. Public methods are constructor/destructor, `init()`, `set_options()`, and overrides for `nodePromote()`, `nodeDemote()`, `nodeGetVersion()`, and `nodeLeader(int)`. Protected helpers manage periodic checks and child process execution.

## Control Flow
The header's API establishes the lifecycle: configure options, call `init()`, let inherited uRaft elect a leader, and have controller callbacks run helper commands. Periodic status timers keep local process liveness synchronized with promotion eligibility.

## State and Persistence Behavior
The class stores Asio timers, a child pid, command type, elapsed command timer, forced-demote flag, last node liveness, and options. Persistent behavior is indirect through helper commands that mutate local service state and network addresses.

## Dependencies and Integration Points
It includes `common/time_utils.h`, POSIX `unistd.h`, and `uraftstatus.h`. It is the main class used by the `lizardfs-uraft` executable and must stay compatible with the helper script interface.

## Risks and Edge Cases
The controller assumes only one slow helper command is active. Any new callback path must preserve that invariant and avoid blocking the Asio loop. Option defaults live in the `.cc`, so callers must set complete options or rely on constructor defaults.

## Test Signals
Tests should instantiate with a fake helper path or controlled environment and verify timer scheduling, command-state transitions, and inherited status output after callback activity.
