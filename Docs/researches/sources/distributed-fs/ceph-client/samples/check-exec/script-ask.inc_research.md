<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/script-ask.inc -->
# sources/distributed-fs/ceph-client/samples/check-exec/script-ask.inc

## Purpose
`script-ask.inc` is an executable sample script for the `inc` interpreter that reads a number interactively and increments it.

## Important APIs, Types, And Functions
The shebang is `#!/usr/bin/env inc`. Interpreter commands are `?` to read a number from stdin and `+` to increment and print it.

## Control Flow
When executed, the kernel invokes `env inc`, and `inc` reads the script. The `?` command prompts for a new counter value, then `+` increments and prints it.

## State And Persistence
The only state is the interpreter's in-memory counter during script execution.

## Dependencies And Integration Points
It depends on `inc` being in `PATH` and integrates with check-exec policy around executable scripts and interactive input.

## Risks And Edge Cases
Under `SECBIT_EXEC_DENY_INTERACTIVE`, the prompt/read behavior may be denied depending on how the script is invoked. If stdin is not numeric, the interpreter warns and keeps the existing counter value.

## Test Signals
Supplying `41` should result in output `42` after the prompt when policy permits interactive reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/script-ask.inc -->
