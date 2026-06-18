# sources/distributed-fs/beegfs/meta/source/net/message/control/SetChannelDirectMsgEx.h

## Purpose
Declares the metadata-side SetChannelDirectMsg handler.

## Important APIs And Types
Exports processIncoming(ResponseContext&) override on common SetChannelDirectMsg.

## Control Flow
Factory creates this handler for NETMSGTYPE_SetChannelDirect.

## State And Persistence
No additional state beyond inherited message value.

## Dependencies And Integration Points
Depends on NetMessage base classes, Program/App service registries, MessagingTk, node/session/target stores, generated common message classes, and operation statistics counters.

## Risks And Edge Cases
Protocol behavior depends on the common message value representation.

## Test Signals
Compile and factory mapping tests cover this file.
