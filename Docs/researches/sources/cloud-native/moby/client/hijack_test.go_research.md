<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/hijack_test.go -->
# sources/cloud-native/moby/client/hijack_test.go

Purpose: validates close-writer behavior for hijacked TLS connections.

Important coverage: ensures `HijackedResponse.CloseWrite` behaves correctly when the underlying connection does or does not expose a write-half close operation.

Control flow and dependencies: uses in-memory or TLS-like connection test doubles and package hijack types.

State and risks: no persistence. The test protects stream shutdown semantics that affect attach/exec interactive sessions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/hijack_test.go -->
