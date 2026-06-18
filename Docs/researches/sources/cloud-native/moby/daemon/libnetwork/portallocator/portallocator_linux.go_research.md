<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_linux.go

Purpose: Linux platform implementation for dynamic port range and reserved port discovery.

Important APIs/functions: `getDynamicPortRange` reads `/proc/sys/net/ipv4/ip_local_port_range` and scans start/end. `getReservedPorts` reads `/proc/sys/net/ipv4/ip_local_reserved_ports`. `parseReservedPorts` parses comma-separated single ports and ranges, filters to the allocator range, and returns a `map[uint16]struct{}`.

Control flow: dynamic range parsing expects two numbers. Reserved-port parsing trims whitespace, handles empty files as nil, splits entries on commas and optional hyphens, validates uint16 values and range ordering, then inserts only ports between `begin` and `end`.

State and persistence: reads kernel procfs configuration at allocator initialization/reset. The resulting reserved map affects only default ephemeral allocation, not explicit port or explicit range requests.

Dependencies and integration points: used by `newInstance`, `dynamicPortRange`, and `reservedPorts` in the shared allocator.

Risks and test signals: malformed kernel reserved-port contents are logged and ignored by the caller, which may allow Docker to auto-pick administratively reserved ports. Tests in `portallocator_linux_test.go` cover empty input, single/multiple ports, ranges, filtering, and parse errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_linux.go -->
