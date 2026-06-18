# sources/distributed-fs/beegfs/meta/source/net/message/control/AckMsgEx.h

## Purpose
Declares the metadata-side AckMsg handler.

## Important APIs And Types
Exports processIncoming(ResponseContext&) override on top of common AckMsg.

## Control Flow
Factory creates this handler for NETMSGTYPE_Ack.

## State And Persistence
No state beyond inherited AckMsg value.

## Dependencies And Integration Points
Depends on NetMessage base classes, Program/App service registries, MessagingTk, node/session/target stores, generated common message classes, and operation statistics counters.

## Risks And Edge Cases
Header depends on common AckMsg semantics used by AcknowledgeableMsg.

## Test Signals
Compile and factory mapping tests cover this file.
