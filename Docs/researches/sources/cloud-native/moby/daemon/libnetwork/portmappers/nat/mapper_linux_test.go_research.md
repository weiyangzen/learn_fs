<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmappers/nat/mapper_linux_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/portmappers/nat/mapper_linux_test.go

Purpose: focused unit test for NAT mapper grouped-request validation.

Important APIs/functions: `TestBindHostPortsError` constructs two `PortBindingReq` values with same protocol/container port but different host port ranges, then calls `MapPorts`.

Control flow: the mapper should reject the mismatched group before allocating sockets. The test asserts the exact internal error text and nil bindings.

State and persistence: no persistent state; no sockets should be allocated because validation fails early.

Dependencies and integration points: uses `portmapperapi`, libnetwork `types`, and `gotest.tools`.

Risks and test signals: verifies a critical caller contract: grouped requests must only differ by host IP. It does not cover happy-path allocation or rootless port-driver behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmappers/nat/mapper_linux_test.go -->
