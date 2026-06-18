# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sockaddr.sh

Purpose: Generates address-family string names for sockaddr formatting.

Important APIs/types/functions: It reads `AF_*` definitions from the beauty copy of `include/linux/socket.h` and emits `static const char *socket_families[]`.

Control flow: The script selects a header directory, parses `#define AF_NAME number` lines, formats indexed entries, and filters aliases/noisy entries `UNIX` and `MAX`.

State and persistence: stdout-only generator.

Dependencies and integration points: Output is included by `sockaddr.c` and wrapped as `DEFINE_STRARRAY(socket_families, "PF_")`.

Risks: It uses AF names but the formatter prefixes with `PF_`, relying on Linux AF/PF value equivalence. Non-decimal definitions are ignored.

Test signals: Regenerate and ensure families such as LOCAL, INET, INET6, NETLINK, and PACKET appear; compile `sockaddr.c`.
