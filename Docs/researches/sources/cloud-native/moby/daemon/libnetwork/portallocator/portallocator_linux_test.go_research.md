<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_linux_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_linux_test.go

Purpose: unit tests for Linux reserved-port parsing.

Important APIs/functions: `TestParseReservedPorts` directly exercises `parseReservedPorts`.

Control flow: table-driven cases pass kernel-style strings such as empty input, single ports, multiple ports, port ranges, and malformed entries. Expected maps verify that only ports in the requested allocator bounds survive.

State and persistence: no persistent state; tests operate entirely on strings and returned maps.

Dependencies and integration points: uses `gotest.tools` assertions and the Linux-only parser in `portallocator_linux.go`.

Risks and test signals: validates the parser layer that prevents default auto-allocation from selecting `/proc/sys/net/ipv4/ip_local_reserved_ports`. It does not read real procfs, so environmental reserved-port settings are not required.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_linux_test.go -->
