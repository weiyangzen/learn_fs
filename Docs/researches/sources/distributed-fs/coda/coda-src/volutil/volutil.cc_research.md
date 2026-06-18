# sources/distributed-fs/coda/coda-src/volutil/volutil.cc

## Purpose

`volutil.cc` is the fileserver-side RPC service harness for volume utility requests. The complete 357-line file was read. It exports the utility subsystem, starts worker LWPs, authenticates admin callers, dispatches generated volutil RPC requests, and provides several simple administrative service handlers.

## Important APIs, Types, and Functions

Key functions are `InitVolUtil()`, `VolUtilLWP()`, `InitServer()`, `IsAdminUser()`, `VolGetKey()`, `GetVolId()`, `S_VolUpdateDB()`, `S_VolShutdown()`, `S_VolSwaplog()`, `S_VolSwapmalloc()`, `S_VolSetDebug()`, `S_VolMerge()`, and stubbed debug-memory handlers `S_VolDumpMem()`, `S_VolPeekInt()`, `S_VolPokeInt()`, `S_VolPeekMem()`, and `S_VolPokeMem()`.

## Control Flow

`InitVolUtil()` exports `UTIL_SUBSYSID` and starts two `VolUtilLWP` workers. Each worker initializes per-thread RVM state when needed, tags itself with `FSTAG=volumeUtility`, blocks in `RPC2_GetRequest()` with `VolGetKey()` authentication, dispatches through `volUtil_ExecuteRequest()`, logs errors, and unbinds failed connections. `VolGetKey()` authenticates Coda tokens and checks `System:Administrators`, or falls back to the volutil shared key for legacy clients.

## State and Persistence Behavior

The harness mutates process state: exported RPC subsystem, worker LWPs, per-thread RVM structures, logging/debug levels, malloc tracing, shutdown flag via `ViceTerminate()`, and database reload via `ViceUpdateDB()`. Memory peek/poke RPCs are intentionally disabled and return "use gdb" behavior.

## Dependencies and Integration Points

Dependencies include RPC2, RVM, auth2, getsecret, access-list group checks, `srv.h`, `vldb.h`, and generated `volUtil_ExecuteRequest()`. It is the server counterpart to `volclient.cc`.

## Risks and Test Signals

Risks include only two utility workers, backward-compatible shared-key auth, process-wide debug changes, reliance on LWP rocks for program type, and broad administrative authority once authenticated. Tests should cover token admin acceptance/rejection, shared-key auth, worker dispatch, unbind-on-error behavior, `GetVolId()` numeric/name lookup, debug level propagation, shutdown/update requests, and disabled memory-debug RPCs.
