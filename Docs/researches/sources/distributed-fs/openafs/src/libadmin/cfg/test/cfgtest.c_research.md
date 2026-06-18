# sources/distributed-fs/openafs/src/libadmin/cfg/test/cfgtest.c

## Purpose
This file is a command-line test driver for cfg admin operations. It initializes AFS client admin state, obtains tokens, opens a cell, registers libcmd commands, and dispatches individual manual/integration tests for CellServDB, server, host, and client configuration functions.

## Important APIs, Types, and Functions
- Global state: `myCellName`, `myTokenHandle`, and `myCellHandle` hold process-wide admin context.
- `GetErrorText` translates `afs_status_t` values with `util_AdminErrorCodeTranslate`.
- CellServDB commands: `DoCellServDbAddHost`, `DoCellServDbRemoveHost`, `DoCellServDbEnumerate`, plus `CellServDbCallBack` and pthread condition state for async completion.
- Server commands: `DoDbServersWaitForQuorum`, `DoFileServerStart`, and `DoFileServerStop`.
- Host/client commands: `DoHostPartitionTableEnumerate`, `DoClientCellServDbAdd`, `DoClientCellServDbRemove`, `DoClientStart`, `DoClientStop`, `DoClientSetCell`, `DoClientQueryStatus`, and `DoHostQueryStatus`.

## Control Flow and State
`main` calls `afsclient_Init`, discovers the local cell, tries to reuse existing tokens, falls back to unauthenticated tokens, opens a cell handle, registers all commands, dispatches the requested command, and closes handles. Command handlers generally open a cfg host handle, call one cfg API, print translated status, and close the handle. CellServDB add/remove handlers wait on a condition variable until the callback reports termination.

## Persistence and Side Effects
The test commands can mutate real cell/server/client configuration: adding/removing CellServDB hosts, starting/stopping fileservers and clients, setting default client cell, and changing client CellServDB entries. It also opens tokens and cell handles. Output is printed to stdout and errors are reported as translated text.

## Dependencies and Integration Points
The driver integrates `afs_clientAdmin`, `afs_cfgAdmin`, `afs_utilAdmin`, pthreads, OpenAFS command parsing, and cellconfig types. It is built by `cfg/test/Makefile.in` and serves as a manual integration harness for cfg APIs rather than a self-checking unit test suite.

## Risks
Because commands operate on live AFS configuration, accidental invocation against production hosts can be destructive. Several handlers overwrite `st` during cleanup, so a close failure may mask the operation result. `DoClientSetCell` builds a multistring in a fixed 1024-byte buffer without length checks. The callback wait assumes the terminal callback always fires after successful async start. Token fallback to unauthenticated mode can make tests pass into no-auth paths unintentionally.

## Test Signals
The command registrations document expected public cfg workflows. Useful signals include successful command parsing, callback completion for CellServDB updates, proper status translation, handle cleanup after each command, and realistic integration runs against a disposable cell or mocked admin APIs.
