# sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/getrandom.h

Purpose: Provides the x86 vDSO inline syscall fallback for `getrandom()`.

Important APIs/types/functions: `getrandom_syscall(void *buffer, size_t len, unsigned int flags)` issues `__NR_getrandom` with the x86-64 `syscall` instruction, passing args in `rdi`, `rsi`, and `rdx`, returning either bytes written or a negative error value.

Control flow: The vDSO getrandom implementation calls this helper when it cannot satisfy a request from vDSO-managed state. Inline assembly loads the syscall number in `rax`, executes `syscall`, and returns `rax`.

State and persistence: No local state. It writes random bytes to the caller-provided user buffer through the kernel syscall path.

Dependencies and integration points: Includes `asm/unistd.h` for `__NR_getrandom`. Integrates with the generic vDSO getrandom code and the kernel random subsystem.

Risks: Register constraints and clobbers are ABI-critical. The helper is x86-64 specific as written; incorrect use from non-64-bit vDSO code would be unsafe. The memory clobber is needed so buffer accesses are not reordered across the syscall.

Test signals: vDSO getrandom selftests, syscall fallback tests for flags and partial/error returns, and architecture build coverage.
