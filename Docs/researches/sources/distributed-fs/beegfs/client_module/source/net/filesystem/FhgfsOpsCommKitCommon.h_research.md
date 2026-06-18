# sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsCommKitCommon.h

## Purpose
Provides shared types, constants, callback contracts, and inline poll/error handling for BeeGFS communication-kit implementations.

## Important APIs and Types
Defines `BEEGFS_COMMKIT_MSGBUF_SIZE`, debug flags, retry flags, `CKTargetBadAction`, `CommKitContextOps`, and `CommKitContext`. Inline helpers `__FhgfsOpsCommKitCommon_pollStateSocks()` and `__FhgfsOpsCommKitCommon_handlePollError()` centralize socket polling behavior.

## Control Flow
Operation implementations fill a `CommKitContextOps` table with target-state handling, header preparation, send/receive callbacks, logging hooks, retry flags, and a log context. The poll helper computes timeout based on how many states are waiting/done/unconnectable/bufferless; if any state can still progress, it uses nonblocking poll, otherwise `connMsgLongTimeout`. Poll errors mark `pollTimedOut` so individual states invalidate sockets.

## State and Persistence
`CommKitContext` is per communication run and tracks app/logger/private data/io info, target list, retry/done/acquired connection counts, poll state, logged flags, retry limits, and optional NVFS result. No durable state.

## Dependencies and Integration Points
Depends on logging, write response messages, messaging/socket toolkits, `RemotingIOInfo`, node stores, `Config`, and poll abstractions. Included by both generic and vector comm-kit headers.

## Risks
The invariant comment requires counters never exceed state count; bugs in state transitions can create busy loops or invalid timeouts. Poll timeout logging is rate-limited per context, so repeated failures may only show the first log. `CommKitErrorInjectRate` exists only under debug configuration.

## Test Signals
Unit or integration tests for polling timeout selection, poll timeout/error propagation, signal interruption logging, counter invariants under mixed state sets, and operation callback tables with/without send/receive phases.
