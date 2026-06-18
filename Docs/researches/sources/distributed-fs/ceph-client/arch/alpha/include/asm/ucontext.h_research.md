<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/ucontext.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/ucontext.h

**Purpose:** Defines Alpha kernel `struct ucontext` used for signal frames and user context save/restore.

**Important APIs/types/functions:** `struct ucontext` with flags, link, OSF signal mask, stack, machine context, and extensible signal mask tail.

**Control flow:** Signal delivery builds this structure; signal return restores machine context and masks from it.

**State and persistence behavior:** The structure is userspace-visible signal-frame state, not kernel-persistent.

**Dependencies and integration points:** Depends on `old_sigset_t`, `stack_t`, `struct sigcontext`, and kernel `sigset_t` from signal headers.

**Risks:** Layout changes break signal ABI and `sigreturn`. The final `uc_sigmask` placement is intentionally extensible.

**Test signals:** Signal handler context tests, alternate stack tests, `getcontext`/libc compatibility where applicable, and sigreturn validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/ucontext.h -->
