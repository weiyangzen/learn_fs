# sources/distributed-fs/lizardfs/src/uraft/uraftcontroller.cc

## Purpose
`uraftcontroller.cc` connects uRaft leadership decisions to real LizardFS metadata-server process management. It runs helper commands to promote, demote, detect local metadata-server liveness, fetch metadata version, and handle dead-server recovery while keeping leader promotion blocked during unsafe local states.

## Important APIs, Types, and Functions
The file implements `uRaftController`: `init()`, `set_options()`, callback overrides `nodePromote()`, `nodeDemote()`, `nodeGetVersion()`, and `nodeLeader()`, periodic checks `checkCommandStatus()` and `checkNodeStatus()`, command helpers `runSlowCommand()`, `checkSlowCommand()`, `stopSlowCommand()`, `setSlowCommandTimeout()`, `runCommand()`, and `readString()`. It uses `CommandType` states `kCmdNone`, `kCmdPromote`, `kCmdDemote`, and `kCmdStatusDead`.

## Control Flow
Construction initializes timers, command pid/type, forced demote state, local liveness, and command timeouts. `init()` starts the status/uRaft base, blocks promotion, and, unless in elector-only mode, schedules periodic command-status and node-status checks. `nodePromote()` starts `lizardfs-uraft-helper promote` unless another incompatible command is running; conflicts demote the Raft leader and block promotion. `nodeDemote()` similarly starts helper demotion and blocks promotion until it completes. `checkCommandStatus()` reaps slow commands, cancels command timeout, unblocks promotion after demotion, marks node alive after promotion, and runs delayed forced demotion if needed. `checkNodeStatus()` polls `lizardfs-uraft-helper isalive`; a transition to alive unblocks promotion, while a transition to dead demotes Raft state, blocks promotion, and starts `lizardfs-uraft-helper dead`.

## State and Persistence Behavior
Runtime state tracks one child process pid, command type, timeout timer, forced-demote flag, and last liveness. Persistent effects are delegated to `lizardfs-uraft-helper`, which restarts LizardFS master/shadow services, assigns or drops floating IPs, and reads metadata version. `nodeGetVersion()` preserves the last known `state_.data_version` when helper output times out or is invalid, avoiding a downgrade from transient command failure.

## Dependencies and Integration Points
The controller depends on Boost.Asio timers, Boost lexical cast/version fork notifications, POSIX `fork`, `exec`, `pipe`, `poll`, `waitpid`, `kill`, syslog, and `common/time_utils::Timeout`. It integrates with `uRaftStatus` and `uRaft`, and with the installed `lizardfs-uraft-helper` command.

## Risks and Edge Cases
Slow helper commands are shell-executed strings, while fast commands use `execvp` argument vectors. Timeout killing only kills the direct child, so helper scripts that spawn descendants need their own cleanup. Command completion status is not inspected beyond process exit; any exit is treated as completion. Promotion is blocked during demotion/dead handling, making missed unblock paths dangerous. Poll-based `readString()` treats EOF after data as success but kills the child on timeout or read error.

## Test Signals
Mock helper commands should cover promote/demote conflicts, timeout killing, invalid metadata-version output, isalive alive/dead transitions, dead handler invocation, elector mode, forced demote after a running promote, and promotion blocking/unblocking. HA integration tests should verify service personality and floating IP transitions.
