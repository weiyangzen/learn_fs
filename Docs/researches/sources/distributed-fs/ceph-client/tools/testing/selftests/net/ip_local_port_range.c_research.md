# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip_local_port_range.c

Purpose: kselftest coverage for the per-socket `IP_LOCAL_PORT_RANGE` option across IPv4, IPv6, TCP, UDP, SCTP, and MPTCP variants.

Important APIs and types: Uses `kselftest_harness`, `setsockopt`/`getsockopt` with `SOL_IP` and `IP_LOCAL_PORT_RANGE`, `IP_BIND_ADDRESS_NO_PORT`, `SO_DOMAIN`, loopback binds, `getsockname`, packed 32-bit low/high port format, and fixture variants for protocol families.

Control flow: Helpers pack/unpack ranges, discover socket domain, bind to loopback port zero, and read assigned port. Variant tests validate invalid option sizes and low greater than high, ranges outside the namespace ephemeral range, clamped single-port ranges, exhaustion of an eight-port range, late bind behavior with `IP_BIND_ADDRESS_NO_PORT`, and `getsockopt` before/after set/unset. SCTP late-bind variants are marked expected failure.

State and persistence: Per-test sockets hold the configured socket option. The test assumes namespace ephemeral port sysctl is `[40000, 49999]`, set by the shell wrapper. No persistent state.

Dependencies and integration: Requires kernel support for the socket option, optional SCTP/MPTCP protocol availability, and isolated netns sysctl state.

Risks: Protocol availability can affect socket creation. Tests assume the ephemeral range is exactly configured by the wrapper and that no unrelated sockets occupy tested ports.

Test signals: Harness pass means invalid values are rejected, bind allocation respects intersection/clamping/exhaustion semantics, late bind chooses from the socket range, and getsockopt round-trips correctly.
