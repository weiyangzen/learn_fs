# sources/distributed-fs/beegfs/meta/source/net/message/mon/RequestMetaDataMsgEx.h

## Purpose
Declares the metadata monitoring request handler.

## Important APIs And Types
Exports processIncoming(ResponseContext&) override on common RequestMetaDataMsg and includes the matching response type.

## Control Flow
Factory creates this handler for NETMSGTYPE_RequestMetaData.

## State And Persistence
No additional state beyond inherited request value.

## Dependencies And Integration Points
Depends on NetMessage base classes, Program/App service registries, MessagingTk, node/session/target stores, generated common message classes, and operation statistics counters.

## Risks And Edge Cases
Header includes App and logging dependencies used by the implementation.

## Test Signals
Compile and factory mapping tests cover this file.
