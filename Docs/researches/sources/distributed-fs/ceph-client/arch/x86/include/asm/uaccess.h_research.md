# sources/distributed-fs/ceph-client/arch/x86/include/asm/uaccess.h

Purpose: central x86 user-memory access interface for scalar `get_user`/`put_user`, unsafe access regions, kernel nofault access, user cmpxchg, NMI copy, string helpers, machine-check copy, and nontemporal copy support.

Important APIs/types/functions: `get_user()`, `__get_user()`, `put_user()`, `__put_user()`, `user_access_begin()`, `user_access_end()`, `arch_unsafe_get_user()`, `arch_unsafe_put_user()`, `unsafe_try_cmpxchg_user()`, `__try_cmpxchg_user()`, `unsafe_copy_to_user()`, `arch_get_kernel_nofault()`, `arch_put_kernel_nofault()`, `copy_from_user_nmi()`, `strncpy_from_user()`, `strnlen_user()`, and optional `copy_mc_to_kernel()/copy_mc_to_user()`.

Control flow: public scalar accessors run `might_fault()` and call size-specialized assembly thunks or inline asm. Access windows use `stac()`/`clac()` with `barrier_nospec()` after `access_ok()`. Faulting load/store/cmpxchg instructions are paired with exception-table fixups to branch to error labels or produce `-EFAULT`. Compile-time branches handle asm-goto output capabilities and 32-bit/64-bit 8-byte operations.

State/persistence: no persistent state is owned. It temporarily changes SMAP AC state, records instrumentation hooks, updates caller-provided output variables, and may update old-value pointers for failed cmpxchg.

Dependencies/integration: depends on compiler instrumentation, KASAN, MM types, SMAP, exception tables, TLB/user address helpers, `uaccess_32.h` or `uaccess_64.h`, and generic `access_ok`. It is used by syscalls, ptrace, signal handling, procfs, filesystems, BPF, and most kernel/user copy boundaries.

Risks/test signals: this is security-critical. Risks include missing `access_ok()`, unbalanced `stac/clac`, wrong exception-table type, speculative bypass, bad register constraints, missing instrumentation, and width/sign-extension bugs. Test with LKDTM/usercopy, fault-injection, KASAN/KMSAN, hardened usercopy, 32-bit compat, pagefault-disabled paths, `copy_from_user_nmi`, cmpxchg futex-style paths, and compiler matrix with/without asm-goto output support.
