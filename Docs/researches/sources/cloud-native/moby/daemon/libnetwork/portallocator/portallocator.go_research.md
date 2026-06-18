<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator.go

Purpose: shared in-memory logical host-port allocator for TCP, UDP, and SCTP across IP addresses.

Important APIs/types/functions: `PortAllocator` contains a mutex, default IP, `ipMap`, default dynamic range, and reserved ports. Public methods are `Get`, `GetPortRange`, `RequestPort`, `RequestPortInRange`, `RequestPortsInRange`, `ReleasePort`, and `ReleaseAll`. Internal structures `portMap` and `portRange` track allocated ports and per-range cursors. Errors include `errAllPortsAllocated`, `errUnknownProtocol`, and `alreadyAllocatedErr`.

Control flow: `RequestPortsInRange` validates protocol/range/input, normalizes IPs with `netip`, creates missing maps, and builds a set of port maps that must be free. Unspecified addresses reserve against all addresses in their family; specific addresses also check the corresponding unspecified map. Exact requests check all required maps before marking allocating maps. Dynamic/range requests scan from the first address range cursor and skip system reserved ports only for default ephemeral allocation.

State and persistence: singleton process memory only. No datastore persistence; `ReleaseAll` resets maps using the current dynamic range.

Dependencies and integration points: platform-specific `getDynamicPortRange` and `getReservedPorts` supply defaults. OS allocators and NAT mappers layer real sockets on top.

Risks and test signals: address-family and unspecified-address semantics are subtle. Tests cover duplicates, reuse, ranges, multiple IPs, reserved ports, unknown protocols, and exhaustion.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator.go -->
