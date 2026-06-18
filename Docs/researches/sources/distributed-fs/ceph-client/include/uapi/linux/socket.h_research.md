<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/socket.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/socket.h

Purpose: defines generic socket UAPI pieces shared across protocol headers: sockaddr storage size/alignment, kernel socket family type, socket buffer lock flags, and transmit hash policy constants.

Important APIs, types, and functions: `_K_SS_MAXSIZE` fixes sockaddr storage at 128 bytes. `__kernel_sa_family_t` is the exported family type. `struct __kernel_sockaddr_storage` uses an anonymous union/struct and pointer member to enforce family placement and default alignment. `SOCK_SNDBUF_LOCK`, `SOCK_RCVBUF_LOCK`, and `SOCK_BUF_LOCK_MASK` describe locked buffer settings. `SOCK_TXREHASH_*` constants define transmit rehash policy values.

Control flow: protocol UAPI headers embed or alias sockaddr storage for address payloads. Socket option code uses buffer lock flags to report or enforce user-locked send/receive buffer sizes, and networking code can expose txrehash policy through sysctl/socket options.

State and persistence behavior: storage structs are transient ABI containers. Buffer lock and txrehash state live in kernel socket objects.

Dependencies and integration points: this header is included by many networking UAPI headers and libc-visible socket definitions. It integrates with protocol address structs, getsockopt/setsockopt buffer handling, and core socket code.

Risks and edge cases: storage size and alignment are ABI-critical and must satisfy RFC2553-style expectations. Anonymous unions/structs can interact with compiler modes. Protocols must not exceed `_K_SS_MAXSIZE` when using generic storage.

Test signals: compile/layout tests for sockaddr storage size/alignment, protocol structs embedding storage, buffer lock option behavior, txrehash policy values, and 32/64-bit ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/socket.h -->
