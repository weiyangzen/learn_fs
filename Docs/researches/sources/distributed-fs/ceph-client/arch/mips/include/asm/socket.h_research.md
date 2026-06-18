<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/socket.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/socket.h

Purpose: Wraps MIPS UAPI socket definitions and provides kernel-visible socket type enumeration values when not building with strict ABI compatibility.

Important APIs/types/functions: Includes `<uapi/asm/socket.h>`, defines `enum sock_type` values such as `SOCK_STREAM`, `SOCK_DGRAM`, `SOCK_RAW`, `SOCK_RDM`, `SOCK_SEQPACKET`, `SOCK_DCCP`, and `SOCK_PACKET`, then sets `ARCH_HAS_SOCKET_TYPES`.

Control flow: Kernel networking code can use arch-provided socket type constants matching the MIPS ABI while generic code detects `ARCH_HAS_SOCKET_TYPES`.

State and persistence: No runtime state; this is ABI constant exposure.

Dependencies and integration points: Depends on UAPI socket definitions and generic socket users.

Risks: Socket type numeric values are user ABI. Any change breaks syscall compatibility.

Test signals: Networking syscall ABI tests, MIPS userspace socket smoke tests, and compile coverage are useful.

Source read size: 41 lines, 1108 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/socket.h -->
