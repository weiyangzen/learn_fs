# sources/control-plane/mayastor/test/python/common/command.py

## Purpose
Shared command execution helpers for Python tests. It wraps local synchronous commands, local async shell commands, and remote async SSH commands with consistent return objects and error messages.

## Important APIs, Types, And Functions
Exports `CommandReturn`, `run_cmd`, `run_cmd_async`, and `run_cmd_async_at`. Async helpers capture stdout/stderr and raise `ChildProcessError` with command context on nonzero exit.

## Control Flow
`run_cmd` delegates to `subprocess.run`. `run_cmd_async` creates an asyncio shell process and waits for completion. `run_cmd_async_at` opens an `asyncssh` connection, runs the command, and converts the result.

## State And Persistence
No persistent state is stored. Remote state changes are whatever the invoked commands perform.

## Dependencies And Integration Points
Used by fio/NVMe tests, Mayastor fixtures, and remote initiator utilities. Depends on `asyncio`, `subprocess`, and `asyncssh`.

## Risks
Commands are shell strings, so callers must handle quoting. Remote SSH identity/configuration is assumed. The helper raises generic `ChildProcessError`, so tests rely on message text for diagnosis rather than typed failures.

## Test Signals
Failures surface as rich command logs in pytest, while successful calls return decoded stdout/stderr for downstream assertions.
