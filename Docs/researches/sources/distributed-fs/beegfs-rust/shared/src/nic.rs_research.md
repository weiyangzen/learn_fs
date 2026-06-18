## sources/distributed-fs/beegfs-rust/shared/src/nic.rs

### Purpose
Parses NIC filters, discovers local network interfaces, prioritizes matching addresses, and checks whether IPv6 dual-stack sockets are usable on the host.

### Important APIs, Types, and Functions
- `Protocol` parses `"4"` and `"6"` into IPv4/IPv6 selectors.
- `NicFilter` contains optional name, address, protocol, NIC type, and invert flag.
- `NicFilter::parse_optional` and `parse` parse filters in the form `[!] [name|*] [addr|*] [4|6|*] [tcp|rdma|*]`.
- `serde::Deserialize for NicFilter` parses string config entries through `NicFilterVisitor`.
- `nic_priority` matches a discovered `(name, ip)` against filters, rejects link-local addresses, and handles inverted entries.
- `Nic` stores address, `NicType`, interface name, priority, interface index, and address index; `Ord` sorts by filter priority, non-loopback, IPv4 preference, RDMA, interface index, and address index.
- `query_nics(filter, use_ipv6)` uses `pnet_datalink::interfaces()` and returns sorted matching TCP NICs.
- `check_ipv6(port, use_ipv6)` uses libc socket/connect/getsockopt to require IPv6 availability and dual-stack behavior.

### Control Flow and State
Filter parsing is stateless. NIC discovery walks OS interfaces, filters each address, and sorts the result. IPv6 checking creates a temporary nonblocking AF_INET6 socket, probes localhost connect behavior for `EADDRNOTAVAIL`, and checks `IPV6_V6ONLY`.

### Dependencies and Integration Points
Depends on shared `NicType`, `serde`, `regex`, `pnet_datalink`, `libc`, and standard networking/FD APIs. Integrates with node registration and connection address selection by producing local NIC lists and deciding IPv4/IPv6 mode.

### Risks and Edge Cases
RDMA detection is not implemented; RDMA filter entries currently do not match discovered interfaces in `nic_priority`. `check_ipv6` ignores errors from `fcntl` and treats many connect failures as acceptable unless specifically `EADDRNOTAVAIL`. `NicFilter::parse_optional` accepts extra fields after the expected five because it does not reject leftovers. Sorting currently puts RDMA before TCP based on `NicType` ordering, but discovered NICs are always TCP.

### Test Signals
Includes tests for filter parsing, matching/inversion behavior, and NIC sorting. Host-dependent `query_nics` and `check_ipv6` are not covered by deterministic tests.
