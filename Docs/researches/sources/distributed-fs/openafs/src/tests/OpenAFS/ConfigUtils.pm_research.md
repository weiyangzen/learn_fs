# sources/distributed-fs/openafs/src/tests/OpenAFS/ConfigUtils.pm

## Purpose
`ConfigUtils.pm` provides small Perl utility functions for the OpenAFS test setup modules: command execution, debug printing, and an unwind stack.

## Important APIs, types, and functions
Package `OpenAFS::ConfigUtils` exports `@unwinds`, `run`, and `unwind`; it also has package global `$debug`.

## Control flow
`run` accepts either a code reference or shell command string. Code references are executed under `eval` and die on exceptions; shell strings optionally print when `$debug` is true, run with `system`, and die on nonzero return. `unwind` pushes a cleanup command or code reference onto `@unwinds`.

## State and persistence behavior
It stores cleanup entries in package global `@unwinds` and debug mode in `$debug`. Shell commands can have arbitrary external side effects.

## Dependencies and integration points
It depends on Perl `Exporter` and is used by authentication and OS setup modules to run OpenAFS/Kerberos/system commands.

## Risks
Shell string execution has quoting/injection risks and only reports raw `$?`. The unwind stack is only collected here; execution policy must be implemented by callers. Global debug state is shared across all users.

## Test signals
Unit tests should cover successful/failed shell commands, successful/failing code refs, debug output, and unwind stack ordering.
