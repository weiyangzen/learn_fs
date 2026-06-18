# sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/SessionStoreResyncer.cpp

## Purpose
Implements mirrored session-store resync after metadata bulk and modification sync have drained and workers are quiesced.

## Important APIs And Types
The main API is doSync(). It reads mirrored SessionStore size, serializes the store to a buffer, sends ResyncSessionStoreMsg to the buddy node with streamout hook registration, waits for ResyncSessionStoreRespMsg, and updates counters/errors.

## Control Flow
doSync obtains App, mirrored sessions, and meta node store; records the number of sessions to sync; serializes the complete session store; fails if serialization returns zero bytes; sends a request/response to the buddyNodeID; treats communication or non-success response as errors; and on success records all sessions synced.

## State And Persistence
State is the buddy node ID plus atomic session counts and one error flag. The operation replaces/updates remote session persistence on the buddy; local session state is read-only during this step.

## Dependencies And Integration Points
Depends on Program/App singletons, InternodeSyncer, MetaStore paths under the buddy mirror subtree, EntryLockStore locking, SyncCandidateStore queues, MessagingTk request/response, ResyncRawInodes/ResyncSessionStore messages, target state stores, and worker barriers.

## Risks And Edge Cases
The caller must ensure client operations are stopped or session state can change while being serialized. A zero-length serialized buffer is interpreted as failure, so an actually empty valid serialization must not use size zero. Response casting assumes the expected type from requestResponseNode.

## Test Signals
Test empty and non-empty session stores, serialization failure, communication failure, non-success response, and stats before/after doSync.
