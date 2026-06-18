# sources/distributed-fs/beegfs/meta/source/net/message/mon/RequestMetaDataMsgEx.cpp

## Purpose
Implements monitoring metadata snapshot responses for the monitoring service.

## Important APIs And Types
processIncoming gathers local node alias/hostname/ID/NICs, root ownership flag, indirect/direct work queue sizes, normal plus mirrored session counts, and high-resolution stats since the request value, then sends RequestMetaDataRespMsg and updates MetaOpCounter_REQUESTMETADATA.

## Control Flow
The flow is read-only: collect App state, query StatsCollector history, build response, send response, update op stats.

## State And Persistence
No durable state is changed. It observes session stores, work queues, local node configuration, and stats history.

## Dependencies And Integration Points
Depends on NetMessage base classes, Program/App service registries, MessagingTk, node/session/target stores, generated common message classes, and operation statistics counters.

## Risks And Edge Cases
Large stats histories can grow response size depending on lastStatsMS. Session count merges regular and mirrored stores. Root ownership is a boolean comparison of meta root owner and local node ID.

## Test Signals
Test empty and populated stats history, root/non-root node, session counts including mirrored sessions, queue sizes, NIC serialization, and op-stat update.
