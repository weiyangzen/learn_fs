# sources/cloud-native/cri-o/server/listen_unix_test.go

Purpose: Ginkgo tests for the non-Windows `Listen` wrapper.

Important APIs and functions: calls `server.Listen("unix", "address")` and asserts listener presence or bind error.

Control flow: first test creates a Unix socket and removes the path after the test. Second test binds once, then attempts a second bind to the same path.

State and persistence: creates a local Unix socket file named `address` in the test working directory and removes it with `defer os.Remove`.

Dependencies and integration: uses Ginkgo/Gomega and the public `server.Listen` wrapper.

Risks: the hard-coded relative socket path can collide with leftover files if cleanup fails, but the test deliberately exercises that behavior.

Test signals: validates successful bind and duplicate-bind error behavior.
