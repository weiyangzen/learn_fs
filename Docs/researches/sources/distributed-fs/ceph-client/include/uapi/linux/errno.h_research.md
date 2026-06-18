## sources/distributed-fs/ceph-client/include/uapi/linux/errno.h

Purpose: This header forwards Linux UAPI errno definitions to the architecture-specific `<asm/errno.h>`.

Important APIs and types: It has a single include and defines no local constants, structs, or functions. The effective API is the errno namespace supplied by the target architecture.

Control flow and state: There is no control flow or state. Build preprocessing resolves errno values through the asm include path.

Persistence and dependencies: It depends entirely on architecture UAPI errno headers. Errno values are part of syscall ABI and userspace error handling conventions.

Integration points: Any UAPI header or userspace program including `<linux/errno.h>` receives the architecture errno constants used by syscall return translation, libc, and kernel/userspace interfaces.

Risks and test signals: Risks include include-path misconfiguration, architecture errno differences, and code assuming this file itself enumerates values. Tests should preprocess the header for each target architecture, verify common errno constants are visible, and ensure generated UAPI include sets resolve `<asm/errno.h>` correctly.
