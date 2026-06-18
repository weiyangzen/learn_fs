# sources/distributed-fs/lizardfs/src/uraft/uraftstatus.h

## Purpose
`uraftstatus.h` declares the TCP status wrapper around the uRaft election engine.

## Important APIs, Types, and Functions
`uRaftStatusConnection` exposes `socket()` and `init()` and stores a response byte vector. `uRaftStatus::Options` extends `uRaft::Options` with `status_port`. `uRaftStatus` exposes constructor/destructor, `init()`, `set_options()`, and protected `acceptConnection()`/`storeData()`.

## Control Flow
After options are set, `init()` starts the base election machinery and then the status accept loop. Each accepted connection gets a freshly generated snapshot and an async write.

## State and Persistence Behavior
Only TCP acceptor/socket state and options are stored in this layer. It reads but does not persist inherited Raft state.

## Dependencies and Integration Points
It includes `<list>` but primarily depends on `uraft.h` and Boost.Asio types through the base class. `uRaftController` subclasses this to combine status reporting with service control.

## Risks and Edge Cases
`uRaftStatusConnection::data_` is public so the server fills it directly before `init()`. The class is tightly coupled to Asio lifetime rules; forgetting `shared_from_this()` would risk use-after-free during async writes.

## Test Signals
Compile and integration tests should confirm accepted connections remain alive through write completion and that configured `status_port` is honored.
