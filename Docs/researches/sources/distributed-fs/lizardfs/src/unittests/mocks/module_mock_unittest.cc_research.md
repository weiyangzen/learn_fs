# sources/distributed-fs/lizardfs/src/unittests/mocks/module_mock_unittest.cc

Purpose: Tests the `ModuleMock` TCP mock behavior.

Important APIs/types/functions: Test subclasses overriding hooks; tests for connection, packet receipt, queued responses, disconnection, and signal/wait helpers; socket helpers and packet builders.

Control flow: Test cases initialize a mock, connect a client socket, send LizardFS-framed packets, wait for packet counters or signals, and verify responses or connection events as appropriate.

State and persistence: Test-only sockets and mock counters. No persistent filesystem state.

Dependencies and integration: Depends on GTest, common socket helpers, packet serialization, and `ModuleMock`.

Risks and test signals: Provides practical coverage for the threaded mock, which many higher-level tests may rely on. It is still timing-sensitive because waits use real timeouts and background polling.
