<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_test.go

Purpose: shared allocator unit tests for protocol validation, exact/dynamic/range allocation, release, exhaustion, multiple IPs, unspecified address interactions, and reserved-port semantics.

Important APIs/functions: tests instantiate `newInstance` to avoid singleton contamination and call `RequestPort`, `RequestPortInRange`, `RequestPortsInRange`, `ReleasePort`, and `ReleaseAll`. `BenchmarkAllocatePorts` measures full-range allocation/reset.

Control flow: tests allocate default dynamic ports, exact ports, all ports in the range, custom ranges, ports across multiple IP addresses, and combinations of specific and unspecified addresses. Reserved-port tests mutate `p.reserved` to prove default ephemeral allocation skips reserved values but explicit requests/ranges still honor caller intent.

State and persistence: all allocator state is in-memory maps and range cursors. Tests confirm release makes exact ports reusable and exhaustion returns `errAllPortsAllocated`.

Dependencies and integration points: uses Go `net` IPs and `gotest.tools`. It indirectly validates behavior consumed by OS allocators and port mappers.

Risks and test signals: strong signal for subtle collision rules between `0.0.0.0`/`::` and concrete addresses. Some spelling in test names is legacy, but behavior is precise.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_test.go -->
