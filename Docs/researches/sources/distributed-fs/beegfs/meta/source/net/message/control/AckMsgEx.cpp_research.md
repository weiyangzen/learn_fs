# sources/distributed-fs/beegfs/meta/source/net/message/control/AckMsgEx.cpp

## Purpose
Processes incoming acknowledgement messages for async waiters such as lock-grant notification work.

## Important APIs And Types
processIncoming logs the ack value in debug builds, calls AcknowledgmentStore::receivedAck(getValue()), updates node operation stats with MetaOpCounter_ACK, and returns true without sending a response.

## Control Flow
The control flow is single-step: consume ack, update stats, no response.

## State And Persistence
Mutates the in-memory AcknowledgmentStore and operation counters. No durable state is written.

## Dependencies And Integration Points
Depends on NetMessage base classes, Program/App service registries, MessagingTk, node/session/target stores, generated common message classes, and operation statistics counters.

## Risks And Edge Cases
Malformed or unexpected ack values are delegated to AcknowledgmentStore behavior. The message is intentionally one-way, so clients must not wait for a response.

## Test Signals
Test ack delivery to registered waiters, unknown ack IDs, op-stat update, and no-response listener behavior.
