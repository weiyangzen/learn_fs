<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/signal.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/signal.h

**Purpose:** Defines kernel-side Alpha signal set sizing and OSF-compatible signal action structures while importing UAPI signal numbers.

**Important APIs/types/functions:** `_NSIG`, `_NSIG_BPW`, `_NSIG_WORDS`, `old_sigset_t`, kernel `sigset_t`, `struct osf_sigaction`, `__ARCH_HAS_KA_RESTORER`, and `asm/sigcontext.h` inclusion.

**Control flow:** Signal delivery and compat OSF syscall paths use these layouts to copy masks/actions and build restorer-aware frames.

**State and persistence behavior:** Per-task signal state is generic; this file defines the Alpha binary layout for masks and legacy OSF actions.

**Dependencies and integration points:** Depends on UAPI signal definitions, `sigcontext`, and generic signal core.

**Risks:** Kernel `_NSIG=64` differs from UAPI `NSIG=32`; libc and kernel must agree on exposed behavior. Layout changes break signal ABI.

**Test signals:** Signal mask/action tests, legacy OSF signal syscalls, restorer frame validation, and real-time signal boundary checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/signal.h -->
