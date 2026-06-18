# sources/distributed-fs/ceph-client/include/uapi/asm-generic/auxvec.h

Purpose: Provides an empty generic architecture auxiliary-vector header for architectures that need no extra auxvec constants beyond `linux/auxvec.h`.

Important APIs/types/functions: Only defines the include guard `__ASM_GENERIC_AUXVEC_H`; no constants or types are exported.

Control flow: Included by exported asm header sets as a placeholder/fallback.

State/persistence: No state.

Dependencies/integration: Complements `linux/auxvec.h` and architecture-specific overrides.

Risks: Adding generic constants here would affect all inheriting architectures and user-space ABI.

Test signals: Headers-install and userspace compile checks that include `<asm/auxvec.h>`.
