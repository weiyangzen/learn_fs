# sources/distributed-fs/openafs/src/butc/error_macros.h

## Purpose
`error_macros.h` centralizes the `butc` cleanup convention and declares cross-file helpers used by dump, restore, label, scan, and RPC code.

## Important APIs, Types, and Functions
- `ERROR_EXIT(evalue)` assigns `code = evalue` and jumps to `error_exit`.
- `ERROR_EXIT2(evalue)` jumps to `error_exit2`.
- `ABORT_EXIT(evalue)` jumps to `abort_exit`, letting callers mark abort-specific state before normal cleanup.
- Declares logging (`ErrorLog`, `TapeLog`, `TLog`), task node (`CreateNode`, `FreeNode`, `InitNodeList`), device latch (`EnterDeviceQueue`, `LeaveDeviceQueue`), expiration (`ExpirationDate`), and status mutation (`setStatus`, `clearStatus`) functions.

## Control Flow
The header has no runtime control flow by itself. It imposes a local function shape: a `code` variable plus labels named `error_exit`, `error_exit2`, or `abort_exit`. Most `butc` functions use it to converge cleanup for allocated buffers, mounted tapes, Rx calls, volserver transactions, XBSA transactions, and status nodes.

## State and Persistence Behavior
The macros mutate only local state. Declared functions affect logs, task/status queues, device locks, and BUDB-derived expiration state in their implementation files.

## Dependencies and Integration Points
Included widely by `butc` sources and depends on AFS types plus visible `struct dumpNode` and `struct deviceSyncNode` declarations. Logging is implemented in `lwps.c`; node management in `list.c`; status functions in shared `bucoord/status.c`.

## Risks and Test Signals
Misuse can skip cleanup or compile only after label/local-variable mistakes are fixed. Static analysis should verify every macro call has an initialized `code` and appropriate cleanup label. Behavior tests should cover abort paths distinct from ordinary errors, especially in `dump.c`.
