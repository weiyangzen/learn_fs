# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/scripts/process_with_sigterm_trap.sh

## Purpose
This Bash script is a test process that records its PID and remains alive while trapping termination signals. It supports tests of process management and signal handling.

## Important Behavior
It installs traps that print messages for `SIGTERM` and `SIGINT`, writes its PID to the first positional argument, then loops forever sleeping 1.3 seconds at a time.

## Control Flow
Startup registers traps, emits `$$` to the supplied file path, and enters an infinite loop. Signals do not terminate the process by default because the trap handlers only echo messages; external tests must use stronger termination or cleanup logic if they need it to exit.

## State And Persistence
The script writes a PID file at `$1`. It otherwise maintains only process state and stdout output from traps.

## Dependencies And Integration Points
It integrates with Hadoop shell/process tests that need a long-lived child process and deterministic signal observability.

## Risks
If called without an argument, PID-file writing fails. Because trapped `SIGTERM` does not exit, tests must avoid leaving the process running. The infinite loop can leak processes if cleanup fails.

## Test Signals
Expected signals are the PID file content and observable `SIGTERM trapped!` or `SIGINT  trapped!` output when tests send signals.
