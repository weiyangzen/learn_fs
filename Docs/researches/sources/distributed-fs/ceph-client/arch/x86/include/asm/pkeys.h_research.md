# sources/distributed-fs/ceph-client/arch/x86/include/asm/pkeys.h

Purpose: implements x86 memory protection key allocation helpers and integration points for `mprotect_pkey()` and execute-only mappings.

Important APIs, types, and functions: defines `arch_max_pkey()`, `arch_set_user_pkey_access()`, `arch_pkeys_enabled()`, `__execute_only_pkey()`, `execute_only_pkey()`, `__arch_override_mprotect_pkey()`, `arch_override_mprotect_pkey()`, `ARCH_VM_PKEY_FLAGS`, `mm_pkey_allocation_map()`, `mm_set_pkey_allocated()`, `mm_set_pkey_free()`, `mm_pkey_is_allocated()`, `mm_pkey_alloc()`, `mm_pkey_free()`, and `vma_pkey()`.

Control flow: pkey support is available only when `X86_FEATURE_OSPKE` is enabled. Allocation checks whether all hardware-supported keys are in use, finds the first zero bit with `ffz()`, and marks it allocated. Freeing rejects unallocated keys and execute-only reserved keys. `execute_only_pkey()` and mprotect override wrappers fall back when OSPKE is absent.

State and persistence: per-mm pkey state lives in `mm->context.pkey_allocation_map` and `execute_only_pkey`. It is process address-space state, not external persistence.

Dependencies and integration points: depends on CPU feature detection, `mm_struct` context, VM flag pkey bits, PKRU setup, mprotect, exec-only mapping logic, and user pkey syscalls.

Risks: only 16 keys are assumed; expanding hardware support requires type/mask audits. The execute-only key is allocated internally but hidden from user allocation. Incorrect allocation can allow wrong PKRU permissions or expose reserved keys.

Test signals: pkey syscall selftests, OSPKE absent fallback, allocation exhaustion, freeing invalid/execute-only keys, mprotect_pkey override behavior, execute-only mappings, fork/exec pkey state, and PKRU access enforcement.
