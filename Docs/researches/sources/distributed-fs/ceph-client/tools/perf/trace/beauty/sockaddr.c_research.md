# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sockaddr.c

Purpose: Beautifies socket address pointer arguments when perf trace has captured augmented user memory.

Important APIs/types/functions: `syscall_arg__scnprintf_sockaddr` chooses augmented formatting or pointer fallback. `af_inet__scnprintf`, `af_inet6__scnprintf`, and `af_local__scnprintf` render protocol-specific fields. The generated `socket_families` array maps address families.

Control flow: If `arg->augmented.args` is absent, the pointer is printed as hex. Otherwise, the captured bytes are treated as `struct sockaddr`, the family name is printed, and a family-specific callback adds path, port/address, IPv6 flowinfo, or scope id when supported.

State and persistence: Reads captured syscall argument bytes only; no persistent state.

Dependencies and integration points: Depends on syscall augmentation, generated `sockaddr.c`, sockets headers, UNIX sockets, and `inet_ntop`.

Risks: Captured buffer size is not checked in this local code before casting to larger sockaddr variants. UNIX paths may not be NUL-terminated in malformed input.

Test signals: Trace bind/connect/sendto with AF_UNIX, AF_INET, AF_INET6, unsupported families, and augmentation disabled.
