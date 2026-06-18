<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/IProcCommand.hh -->
# sources/distributed-fs/eos/mgm/proc/IProcCommand.hh

Source read size: 389 lines, 15417 bytes.

## Purpose

Declares `IProcCommand`, the abstract base class for protobuf-backed MGM proc commands.

## Important APIs, Types, and Functions

The class provides constructors, destructor, virtual `open/read/stat/close/GetCmd/ProcessRequest/GetResult/SetError`, final `LaunchJob` and `KillJob`, temporary-file helpers, path/id resolution helpers, JSON response helpers, operation-forbidden and routing helpers, slot accounting, `RoutingInfo`, and many stream/result fields.

## Control Flow

Subclasses implement `ProcessRequest`. The base `open` method handles launching and response conversion, while `read/stat/close` expose the result to XRootD. The destructor marks `mForceKill`, closes/unlinks temp files, and decrements command slot counters when held.

## State and Persistence Behavior

Per-object state includes request proto, future, async flags, force-kill flag, virtual identity, timestamp/comment, routing info, temp files, response buffers, and stream read-phase booleans. Static state tracks command concurrency.

## Dependencies and Integration Points

Depends on MGM namespace/logging/mapping, console protobufs, XRootD SFS interfaces, futures, streams, JSONCPP forward declarations, and proc command subclasses.

## Risks and Edge Cases

The default `GetResult` returns placeholder text, so callers must use concrete subclasses for real result access. `stat` computes sizes from current stream positions and assumes stream state is seekable. Subclasses must honor `mForceKill` for cancellation to be effective.

## Test Signals

Subclass-based tests for virtual dispatch, async cancellation, stat/read sequencing for file and memory results, destructor cleanup, slot accounting, and JSON formatting exposure through `CallJsonFormatter`-style wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/IProcCommand.hh -->
