# sources/distributed-fs/beegfs/meta/source/net/message/fsck/FsckSetEventLoggingMsgEx.cpp

## Purpose
Enables or disables fsck modification event logging.

## Important APIs And Types
processIncoming gets ModificationEventFlusher, enables logging with UDP port/NIC list/forceRestart or disables logging, reports result/loggingEnabled/missedEvents, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Mutates event flusher runtime state and exposes whether fsck missed events while disabled.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Enable path always returns result=true and missedEvents ignored, so callers must interpret fields by loggingEnabled. Force restart can reset existing logging.

## Test Signals
Test enable, disable, force restart, missed-events reporting, and response fields.
