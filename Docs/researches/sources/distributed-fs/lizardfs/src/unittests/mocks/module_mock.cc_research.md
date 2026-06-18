# sources/distributed-fs/lizardfs/src/unittests/mocks/module_mock.cc

Purpose: Implements `ModuleMock`, a nonblocking TCP server test double that accepts clients, receives framed packets, and can queue responses.

Important APIs/types/functions: Constructor/destructor; `init`; `port`; `address`; `operator()` event loop; `serveFd`; `respondToCurrentClient`; `disconnectCurrentClient`; `signal`.

Control flow: `init` creates a nonblocking localhost listening socket and starts a thread. The event loop polls the listener and client sockets, accepts clients, feeds incoming bytes into `MessageReceiveBuffer`, calls virtual hooks for new connections/messages/end, counts received packets, and drains queued response buffers via `MultiBufferWriter`.

State and persistence: Maintains socket fd, background thread, termination flag, connected client records, current client fd, packet counters, signal counters, mutex and condition variable. No persistent storage.

Dependencies and integration: Uses common socket wrappers, `MessageReceiveBuffer`, `MultiBufferWriter`, `NetworkAddress`, and packet headers. Tests subclass it to simulate modules in integration-style unit tests.

Risks and test signals: Destructor assumes `init` started a joinable thread. Callbacks can disconnect current clients while message processing is active, so the implementation checks map membership. Poll timeout controls responsiveness. `module_mock_unittest.cc` exercises basic connection/message/response behaviors.
