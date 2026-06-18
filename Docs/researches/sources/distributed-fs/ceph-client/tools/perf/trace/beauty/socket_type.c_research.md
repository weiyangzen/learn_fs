# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/socket_type.c

Purpose: Formats the combined socket type and type flags argument to `socket(2)`.

Important APIs/types/functions: `syscall_arg__scnprintf_socket_type` recognizes base `SOCK_*` types and flags `SOCK_CLOEXEC` and `SOCK_NONBLOCK`.

Control flow: The function splits the low type nibble using `SOCK_TYPE_MASK`, switch-formats the base type, then appends recognized high flags and unknown leftovers.

State and persistence: Stateless formatting.

Dependencies and integration points: Depends on `<sys/socket.h>` and local fallback definitions. Bound via `SCA_SK_TYPE`.

Risks: The flag-printing macro omits the optional `SOCK_` prefix for flags even when `show_string_prefix` is true, which may be intentional but is inconsistent with the base type behavior. ABI-specific type values are handled manually because MIPS may override values.

Test signals: Trace sockets with stream/dgram/raw and CLOEXEC/NONBLOCK combinations on multiple architectures when possible.
