# sources/distributed-fs/beegfs/meta/source/net/message/control/SetChannelDirectMsgEx.cpp

## Purpose
Processes requests that toggle direct-channel mode on the current socket.

## Important APIs And Types
processIncoming logs the value in debug builds, calls ctx.getSocket()->setIsDirect(getValue()), updates node operation stats with MetaOpCounter_SETCHANNELDIRECT, and returns true.

## Control Flow
The handler mutates socket state immediately and sends no explicit response in this implementation.

## State And Persistence
State is per-socket directness plus operation counters.

## Dependencies And Integration Points
Depends on NetMessage base classes, Program/App service registries, MessagingTk, node/session/target stores, generated common message classes, and operation statistics counters.

## Risks And Edge Cases
A peer can change how the socket is classified; authentication and caller restrictions must be enforced elsewhere if required. No response means caller protocol must know this is fire-and-forget.

## Test Signals
Test direct flag true/false, op-stat update, and connection behavior after toggling.
