## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vgetrandom.c

Purpose: 64-bit vDSO wrapper for `getrandom`.

Important APIs/functions: `__vdso_getrandom(void *buffer, size_t len, unsigned int flags, void *opaque_state, size_t opaque_len)` and weak alias `getrandom`. It includes `lib/vdso/getrandom.c`.

Control flow: wrapper delegates to `__cvdso_getrandom()`, passing caller buffer, length, flags, and opaque userspace state used by the generic vDSO random implementation.

State/persistence: no local state; state is managed by generic vDSO getrandom code and caller-provided opaque state.

Integration points: ChaCha block assembly, random subsystem vDSO data contract, 64-bit linker script, libc getrandom lookup, and fallback syscall behavior.

Risks: ABI signature and opaque-state size handling are security-sensitive. Test signals include getrandom vDSO selftests, fallback behavior for unsupported flags/state, entropy reseed tests, and symbol version checks.
