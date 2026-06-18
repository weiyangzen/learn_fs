# sources/distributed-fs/beegfs/meta/source/net/message/NetMessageFactory.h

## Purpose
Declares the metadata NetMessageFactory subclass used by the app to instantiate message handlers from wire message type IDs.

## Important APIs And Types
Exports a default constructor and overrides createFromMsgType(unsigned short) from AbstractNetMessageFactory.

## Control Flow
The app-level networking layer owns or references this factory and delegates type-specific construction to the cpp switch.

## State And Persistence
The class holds no state.

## Dependencies And Integration Points
Depends on NetMessage base classes, Program/App service registries, MessagingTk, node/session/target stores, generated common message classes, and operation statistics counters.

## Risks And Edge Cases
Any signature drift from AbstractNetMessageFactory would break dispatch. Constructor currently does no initialization.

## Test Signals
Compile tests and a dispatch smoke test are sufficient for the header.
