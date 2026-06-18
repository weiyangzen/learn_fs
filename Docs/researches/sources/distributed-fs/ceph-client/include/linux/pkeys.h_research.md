# sources/distributed-fs/ceph-client/include/linux/pkeys.h

Purpose: provides the generic kernel wrapper for memory protection keys (pkeys), including fallback stubs for architectures without pkey support.

Important APIs and types: `ARCH_DEFAULT_PKEY` is the default key. With `CONFIG_ARCH_HAS_PKEYS`, architecture definitions come from `asm/pkeys.h`; without it, fallback macros define one available key, no execute-only dedicated key, no VM pkey flags, and neutral `arch_override_mprotect_pkey()`. Stub helpers include `vma_pkey()`, `mm_pkey_is_allocated()`, `mm_pkey_alloc()`, `mm_pkey_free()`, `arch_set_user_pkey_access()`, and `arch_pkeys_enabled()`.

Control flow: MM and syscall paths can call the generic helpers unconditionally. On pkey-capable architectures, arch code handles allocation, VMA key extraction, mprotect overrides, and user access register programming; on other architectures, only pkey 0 appears allocated and allocation/free requests fail or no-op.

State and persistence: this header owns no state. Supported architectures store pkey allocation state in `mm_struct` and access permissions in task/CPU-specific registers. Fallback builds have no persistent pkey state.

Dependencies and integration points: depends on `linux/mm.h` and optional `asm/pkeys.h`. It integrates `pkey_alloc`, `pkey_free`, `mprotect`, VMA flags, execute-only mappings, and per-task architecture access controls.

Risks and test signals: risks include fallback behavior masking feature assumptions, incorrect default key semantics, VMA flag drift, and architecture code failing to synchronize task access registers. Test pkey syscalls and mprotect on pkey-capable systems, compile fallback architectures, execute-only mapping behavior, fork/exec inheritance expectations, and invalid pkey error paths.
