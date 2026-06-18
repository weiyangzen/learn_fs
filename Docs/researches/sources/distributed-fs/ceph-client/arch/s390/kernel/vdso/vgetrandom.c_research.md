## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vgetrandom.c

Purpose: Implements the s390 vDSO-visible `__kernel_getrandom` wrapper.

Important API: `__kernel_getrandom(void *buffer, size_t len, unsigned int flags, void *opaque_state, size_t opaque_len)`.

Control flow: If facility 129 is available, forwards to generic `__cvdso_getrandom()`. If called with the special probe signature of all-zero arguments except `opaque_len == ~0UL`, returns `-ENOSYS`. Otherwise falls back to the `getrandom` syscall wrapper.

State and persistence: No owned state; uses generic vDSO getrandom opaque state when supported.

Dependencies and integration: Depends on facility probing, generic vDSO getrandom include selected by the Makefile, and syscall fallback helper.

Risks and test signals: Risks include incorrect support probing and probe-call semantics. Test signals are vDSO getrandom on machines with and without facility 129, fallback syscall behavior, special probe return, and flag/length edge cases.
