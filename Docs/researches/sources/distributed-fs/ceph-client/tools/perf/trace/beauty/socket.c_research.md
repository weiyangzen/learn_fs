# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/socket.c

Purpose: Formats socket protocol and socket option level arguments.

Important APIs/types/functions: `syscall_arg__scnprintf_socket_protocol` maps protocol numbers to `IPPROTO_*` only for AF_INET/AF_INET6 domains. `syscall_arg__scnprintf_socket_level` maps levels, with special handling for `SOL_SOCKET`.

Control flow: The protocol formatter reads argument 0 for domain and either uses `socket__scnprintf_ipproto` or falls back to integer output. The level formatter accounts for architectures where `SOL_SOCKET` is `0xffff`, otherwise checks `1`, then uses the generated socket-level table.

State and persistence: Stateless formatting.

Dependencies and integration points: Includes generated `socket.c` from `socket.sh`, sockets headers, and perf syscall argument helpers.

Risks: Non-IP socket domains intentionally leave protocol numeric. Architecture-specific `SOL_SOCKET` handling must stay aligned with kernel ABI.

Test signals: Trace `socket(AF_INET, ..., IPPROTO_TCP)`, non-IP socket creation, and `setsockopt`/`getsockopt` levels.
