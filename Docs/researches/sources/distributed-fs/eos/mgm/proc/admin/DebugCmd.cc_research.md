# Research: sources/distributed-fs/eos/mgm/proc/admin/DebugCmd.cc

## Purpose

`DebugCmd.cc` implements the protobuf admin command for reading and setting MGM/FST debug log levels and filters.

## Important APIs, Types, and Functions

- `DebugCmd::ProcessRequest()` dispatches `get` and `set`.
- `GetSubcmd()` reports local MGM log priority and node debug states from `FsView`.
- `PrepareMsg()` builds the legacy `mgm.cmd=debug` message body string.
- `PrepareQuery()` builds FST query parameters for debug level/filter.
- `SetSubcmd()` validates root privilege, log level, wildcard use, updates local logging, and broadcasts to selected endpoints.

## Control Flow

`get` takes a read lock on `FsView::gFsView.ViewMutex`, reads the global logging priority, lowercases it, prints the local MGM endpoint, then iterates node view entries and prints each node's `debug.state`.

`set` requires `mVid.uid == 0`. It validates the requested debug level through `Logging::GetPriorityByString()`, rejects node patterns with more than one wildcard, prepares legacy body/query strings, and updates local MGM logging when the target is `*`, empty, the MGM queue, or `/eos/*/mgm`. For an all-MGM target or empty target it returns after local update. Otherwise it resolves endpoints through `FsView::gFsView.CollectEndpoints()` and sends `gOFS->BroadcastQuery()` to FSTs/nodes.

## State and Persistence Behavior

The command mutates runtime logging priority and optional log-id filter in `eos::common::Logging`. It can also mutate remote FST/node debug state via broadcast query. These are runtime operational settings, not persisted config in this file.

## Dependencies and Integration Points

Dependencies include `DebugCmd.hh`, `ProcInterface`, `XrdMgmOfs`, `FsView`, `MessagingRealm`, and common logging. It integrates with node endpoint discovery and `BroadcastQuery()`.

## Risks and Edge Cases

- Only uid 0 can set debug, stricter than central admin gating.
- For local-only `/eos/*/mgm` or empty node target, `SetSubcmd()` sets `retc` and returns without setting stdout, even though it built a success message.
- `PrepareMsg()` builds a body string that is not used by the current broadcast path; it may be leftover compatibility code.
- Wildcard validation only counts `*`; it does not validate other pattern forms before endpoint collection.
- `GetSubcmd()` copies `mNodeView` then indexes back into the global map, so concurrent changes are protected by the read lock but the pattern is slightly redundant.

## Test Signals

Tests should cover get output with local priority and node states, non-root set refusal, invalid log levels, multiple wildcard rejection, local MGM-only update, filter update, endpoint-not-found failure, broadcast success/failure, and expected stdout behavior for local-only targets.
