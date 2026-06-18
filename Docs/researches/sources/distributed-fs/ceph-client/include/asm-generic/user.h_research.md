# sources/distributed-fs/ceph-client/include/asm-generic/user.h

Purpose: generic placeholder for the obsolete `struct user` interface historically used by a.out/core-file code.

Important APIs/types/functions: none; the comment explicitly notes new architectures do not support a.out and need not define `struct user`.

Control flow: none.

State and persistence: none.

Dependencies and integration points: provides `<asm/user.h>` compatibility for code that includes it conditionally.

Risks: code expecting a concrete `struct user` cannot rely on this header. Architecture-specific ports must provide their own definition if legacy ABI support is required.

Test signals: build coverage for tools or kernel code that include `<asm/user.h>` on generic architectures.
