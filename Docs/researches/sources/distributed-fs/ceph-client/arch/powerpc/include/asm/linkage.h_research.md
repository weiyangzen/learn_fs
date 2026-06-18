# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/linkage.h

Purpose: provides PowerPC linkage overrides for conditional syscalls and syscall aliases on 64-bit ELF ABI v1.

Important APIs/types/functions: under `CONFIG_PPC64_ELF_ABI_V1`, `cond_syscall(x)` emits weak aliases for both descriptor and dot-symbol forms to `sys_ni_syscall`; `SYSCALL_ALIAS(alias, name)` emits global aliases for both forms.

Control flow: no runtime flow; inline assembly affects symbol resolution at link time.

State and persistence: no state, but generated weak/global symbols persist in the kernel image.

Dependencies and integration points: includes `asm/types.h` and integrates with syscall tables, PPC64 ELFv1 function descriptor ABI, and generic linkage macros.

Risks: ELFv1 requires both `name` and `.name`; missing one breaks syscall dispatch or module symbol resolution. These macros must not be generalized to ABI v2 without revisiting symbol semantics.

Test signals: build PPC64 ELFv1 kernels, inspect syscall symbols, verify unimplemented syscalls resolve to `sys_ni_syscall`, and run syscall smoke tests.
