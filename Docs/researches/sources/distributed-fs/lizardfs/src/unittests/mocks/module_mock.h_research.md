# sources/distributed-fs/lizardfs/src/unittests/mocks/module_mock.h

Purpose: Declares `ModuleMock`, a reusable threaded network module mock for unit tests.

Important APIs/types/functions: Virtual hooks `onNewConnection`, `onIncomingMessage`, `onConnectionEnd`; waits `waitForPacketReceived`, `waitForPacketsReceived`, `waitForSignal`; `init`; `port`; `address`; protected `respondToCurrentClient`, `disconnectCurrentClient`, `signal`; nested `ClientRecord`.

Control flow: Templated wait helpers use a `Timeout`, mutex, and condition variable to consume packet/signal counters with timeout. The event loop and socket serving are defined in the implementation file.

State and persistence: Declares all runtime server/client state, receive buffers, write queues, and synchronization counters. No persistent state.

Dependencies and integration: Used by tests that need realistic packet framing over TCP without launching full modules.

Risks and test signals: Wait helpers consume counters, so repeated waits require care. The mock is single-current-client oriented for response helpers. Header design encourages subclass hooks for assertions and scripted responses.
