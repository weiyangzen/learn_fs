<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/inet.h -->
# sources/distributed-fs/ceph-client/include/linux/inet.h

Purpose: Declares kernel IP text parsing and formatting helpers for IPv4/IPv6 addresses.

Important APIs/types/functions: Constants `INET_ADDRSTRLEN` and `INET6_ADDRSTRLEN`; `in_aton()`, `in4_pton()`, `in6_pton()`, `inet_pton_with_scope()`, and `inet_addr_is_any()`.

Control flow: Callers parse strings into binary addresses, optionally with scope and network namespace context, or test sockaddr storage for wildcard addresses.

State/persistence: Stateless parsing; scope parsing may consult namespace/device context externally.

Dependencies/integration: Depends on kernel types, socket definitions, and net namespaces; used by procfs/sysfs/config parsers and networking subsystems.

Risks: Delimiter/end pointer handling is subtle; scoped IPv6 parsing must validate interfaces correctly.

Test signals: IPv4/IPv6 parse vectors, invalid input, delimiter behavior, scoped link-local addresses, and wildcard sockaddr tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/inet.h -->
