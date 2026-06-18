# sources/distributed-fs/ceph-client/arch/x86/mm/pkeys.c

## Purpose
`pkeys.c` manages x86 Intel Memory Protection Keys policy around execute-only mappings and initial PKRU defaults. It lets normal `mprotect(PROT_EXEC)` transparently use a pkey to deny data reads while allowing instruction fetches.

## Important APIs, Types, and Functions
Key functions are `__execute_only_pkey()`, `__arch_override_mprotect_pkey()`, debugfs handlers for `init_pkru`, and boot option parser `setup_init_pkru()`. Persistent `init_pkru_value` initializes pkey access-disallow bits for pkeys 1 through 15 while leaving pkey 0 usable.

## Control Flow and State
`__execute_only_pkey()` lazily allocates `mm->context.execute_only_pkey`, checks current PKRU to avoid redundant writes, then calls `arch_set_user_pkey_access()` with `PKEY_DISABLE_ACCESS`. If setup fails, it frees the key and disables execute-only pkey use for that attempt. `__arch_override_mprotect_pkey()` preserves explicit `mprotect_pkey()` values, assigns the execute-only pkey for plain `PROT_EXEC`, resets former execute-only VMAs to `ARCH_DEFAULT_PKEY` when protections broaden, or inherits the existing VMA pkey otherwise. Debugfs and `init_pkru=` allow controlled tuning of default PKRU.

## State and Persistence
State persists in each `mm_struct` execute-only pkey, per-thread PKRU hardware state, and global `init_pkru_value`. The debugfs write path rejects disabling access or writes on pkey 0 to avoid immediate system breakage.

## Dependencies and Integration Points
It depends on CPU `OSPKE`, Linux pkey allocation helpers, `vma_pkey()`, PKRU read/write helpers, debugfs, user-copy parsing, and generic mprotect paths.

## Risks and Test Signals
Risks include failing open to readable executable mappings if pkey allocation or PKRU writes fail, per-thread PKRU inheritance surprises, and unsafe `init_pkru=` values from boot or debugfs. Test signals are pkeys selftests, execute-only mmap/mprotect behavior, debugfs `init_pkru` read/write validation, and context-switch PKRU preservation.
