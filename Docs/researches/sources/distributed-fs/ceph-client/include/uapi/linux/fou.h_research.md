# sources/distributed-fs/ceph-client/include/uapi/linux/fou.h

This generated UAPI header defines the generic-netlink ABI for Foo-over-UDP and related UDP tunnel port management. It is generated from `Documentation/netlink/specs/fou.yaml`.

Important exports include family metadata `FOU_GENL_NAME` and `FOU_GENL_VERSION`, encapsulation types for direct FOU and GUE, attribute IDs such as port, address family, IP protocol, local peer, peer port, interface index, encapsulation type, and UDP checksum controls, plus command IDs for add, delete, and get/dump operations.

Control flow is generic-netlink based: userspace sends add/delete/get commands with the required attributes; the kernel updates or reports UDP tunnel socket state for FOU/GUE encapsulation. State lives in network namespace tunnel-port tables and sockets. Persistence is runtime only and normally recreated by network configuration tools.

Dependencies are generic netlink, UDP tunnel infrastructure, IP protocol numbers, network namespaces, and the YNL generation pipeline. Integration points include `ip fou`, tunnel drivers, GUE/FOU encapsulation, and `tools/net/ynl`.

Risks include hand-editing generated constants, invalid attribute combinations, namespace leaks, tunnel port conflicts, checksum setting mismatches, and schema/header drift. Test signals include YNL regeneration diff checks, `ip fou` roundtrip tests, netlink policy tests, namespace isolation tests, and tunnel packet encapsulation/decapsulation tests.
