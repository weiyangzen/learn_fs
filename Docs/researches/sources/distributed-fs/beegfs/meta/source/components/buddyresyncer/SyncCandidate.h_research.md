# sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/SyncCandidate.h

## Purpose
Defines metadata resync candidate value types for directory bulk sync and file-level modification sync.

## Important APIs And Types
Important types are MetaSyncDirType, MetaSyncCandidateDir, MetaSyncFileType, SerializeAs<MetaSyncFileType>, MetaSyncCandidateFile::Element, and MetaSyncCandidateStore typedef. MetaSyncCandidateFile supports move semantics, addModification(), addDeletion(), releaseElements(), prepareSignal(), and signal().

## Control Flow
Gather slaves enqueue MetaSyncCandidateDir. Mirrored operations collect MetaSyncCandidateFile elements in TLS, prepare a barrier signal, enqueue to the job, and wait until the mod-sync slave signals completion.

## State And Persistence
Candidates are in-memory queue records. The Barrier pointer is non-owning and exists only to synchronize a worker with modification resync completion.

## Dependencies And Integration Points
Depends on Program/App singletons, InternodeSyncer, MetaStore paths under the buddy mirror subtree, EntryLockStore locking, SyncCandidateStore queues, MessagingTk request/response, ResyncRawInodes/ResyncSessionStore messages, target state stores, and worker barriers.

## Risks And Edge Cases
signal() assumes prepareSignal() has been called and barrier is non-null. releaseElements() moves the vector, making the candidate empty. Element path/type/isDeletion order semantics are enforced by the mod-sync slave, not by this data class.

## Test Signals
Test move construction/assignment, vector release, addModification/addDeletion values, enum serialization as uint8_t, and barrier signaling behavior.
