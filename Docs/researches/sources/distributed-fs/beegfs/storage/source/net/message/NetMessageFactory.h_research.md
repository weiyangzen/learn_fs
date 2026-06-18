## sources/distributed-fs/beegfs/storage/source/net/message/NetMessageFactory.h

### Purpose
`NetMessageFactory.h` declares the storage daemon implementation of `AbstractNetMessageFactory`. It provides the type-erased entry point used by the network layer to build message objects.

### Important APIs, Types, And Functions
The class has a trivial constructor and overrides `createFromMsgType(unsigned short) const`, returning `std::unique_ptr<NetMessage>`.

### Control Flow, State, And Persistence
The header has no persistent state. The protected override enforces that all creation flows go through the common factory interface.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `common/Common.h` and `AbstractNetMessageFactory`. Integration is with `App::getNetMessageFactory()` and `MessagingTk` deserialization. Risks are minimal but include ABI/interface drift if the abstract factory signature changes. Tests should compile and instantiate the factory through the base interface.
