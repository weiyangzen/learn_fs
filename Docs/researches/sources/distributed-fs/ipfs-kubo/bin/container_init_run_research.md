# sources/distributed-fs/ipfs-kubo/bin/container_init_run

## Purpose
This helper runs one container initialization script from `/container-init.d`.

## Important APIs, Types, And Functions
It accepts one script path. Executable scripts are run as child processes; non-executable scripts are sourced into the current shell.

## Control Flow
The script prints whether it is executing or sourcing, then runs the script under `set -e`.

## State And Persistence Behavior
Executable scripts mutate only their child process environment and external state; sourced scripts can mutate the current shell environment before the daemon exec.

## Dependencies And Integration Points
It is invoked by `container_daemon` via sorted `find`/`xargs`.

## Risks And Test Signals
Risks include arbitrary hook behavior, sourced script side effects, and startup aborts on failures. Signal is each hook's printed execution line and container startup continuing.
