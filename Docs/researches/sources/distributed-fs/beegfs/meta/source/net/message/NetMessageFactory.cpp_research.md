# sources/distributed-fs/beegfs/meta/source/net/message/NetMessageFactory.cpp

## Purpose
Implements the metadata server message factory that maps NETMSGTYPE_* IDs to concrete common response messages or meta-side *MsgEx request handlers.

## Important APIs And Types
The key API is createFromMsgType(unsigned short). It covers control, node, storage, session, monitoring, fsck, and chunk-balancing message groups and returns std::unique_ptr<NetMessage>. Unknown types become SimpleMsg(NETMSGTYPE_Invalid).

## Control Flow
Incoming serialized messages are parsed by AbstractNetMessageFactory, which calls this factory by type. Response-only types instantiate common response classes; request types instantiate server-side Ex handlers with processIncoming implementations.

## State And Persistence
The factory is stateless. Its mappings define the runtime dispatch table for all metadata network message processing.

## Dependencies And Integration Points
Depends on NetMessage base classes, Program/App service registries, MessagingTk, node/session/target stores, generated common message classes, and operation statistics counters.

## Risks And Edge Cases
A missing mapping makes valid wire messages invalid on this service. Mapping a request to a response class or vice versa can silently break processing. The long switch must stay synchronized with message type definitions and included headers.

## Test Signals
Test createFromMsgType for every listed NETMSGTYPE, invalid type fallback, compile coverage for all includes, and smoke tests that representative request handlers process through the listener path.
