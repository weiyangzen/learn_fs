# sources/distributed-fs/ceph-client/include/uapi/asm-generic/Kbuild

Purpose: Lists mandatory generic UAPI asm headers that architectures should provide or inherit for user-space header installation.

Important APIs/types/functions: `mandatory-y` entries include `auxvec.h`, `bitsperlong.h`, `bpf_perf_event.h`, `errno.h`, `fcntl.h`, `ioctl.h`, `ioctls.h`, IPC/memory/resource/signal/socket/stat/term/types/unistd headers, and more.

Control flow: The headers-install Kbuild pass reads this file to decide which `usr/include/asm/` headers are required for non-UML architectures.

State/persistence: No runtime state; affects installed UAPI header completeness.

Dependencies/integration: Used by Kbuild UAPI export logic and architecture-specific asm-generic fallback mechanisms.

Risks: Missing mandatory headers break user-space builds; adding headers without compatible generic definitions can expose unstable ABI.

Test signals: Run `make headers_install` and compile representative userspace programs against the installed asm headers.
