<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/socket.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/socket.h

Purpose: Defines PowerPC-specific socket option numbers that differ before importing generic socket options.

Important APIs/types/functions: `SO_RCVLOWAT`, `SO_SNDLOWAT`, old timeout options, `SO_PASSCRED`, and `SO_PEERCRED`.

Control flow: Socket syscalls decode these option numbers for getsockopt/setsockopt, then generic options fill the rest.

State and persistence: Options correspond to per-socket state in networking core.

Dependencies and integration points: Depends on `asm-generic/socket.h` and socket syscall implementation.

Risks: Option numbers are ABI; mismatches break libc/network applications.

Test signals: Socket option regression tests and cross-checks with PowerPC libc headers.

Source read size: 21 lines, 600 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/socket.h -->
