<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/vdso/getrandom.c -->
# sources/distributed-fs/ceph-client/lib/vdso/getrandom.c

## Purpose
Generic userspace vDSO implementation of `getrandom()`, using per-thread opaque state, ChaCha20 fast key erasure, kernel RNG generation tracking, and syscall fallback for unsupported or unsafe cases.

## APIs, Types, and Functions
Core implementation is `__cvdso_getrandom_data()`, wrapped by `__cvdso_getrandom()`. It uses `struct vdso_rng_data`, `struct vgetrandom_state`, `struct vgetrandom_opaque_params`, `getrandom_syscall()`, `__arch_get_vdso_u_rng_data()`, and `__arch_chacha20_blocks_nostack()`. Helper `memcpy_and_zero_src()` copies batch bytes while zeroing the source using unaligned access helpers.

## Control Flow, State, and Persistence
A special parameter query call (`buffer == NULL`, `len == 0`, `flags == 0`, `opaque_len == ~0UL`) fills mmap parameters and state size. Normal calls validate that the opaque state does not straddle a page, flags are known, opaque length matches, and the kernel RNG is ready. If validation fails, or the state is already `in_use`, it calls the syscall. On generation mismatch, it writes the current generation before reseeding to detect forks correctly, pairs with kernel release ordering via `smp_rmb()`, fetches a fresh key from the syscall, and invalidates state on failure. It serves bytes from a cached batch, zeroing consumed bytes, generates full ChaCha blocks directly into the buffer, then refills a combined batch/key region to preserve forward secrecy. Before returning, it rereads state and kernel generations to detect fork/reseed/zeroed droppable memory; it retries once then falls back.

## Dependencies and Integration
Depends on vDSO datapage definitions, random uapi flags, memory mapping flags including `MAP_DROPPABLE`, architecture ChaCha and syscall hooks, barriers, page size config, and unaligned access helpers. It integrates into architecture vDSO symbol wrappers.

## Risks and Test Signals
Risks include per-state concurrency misuse across threads, signal reentrancy limitations, page-straddling state faults, generation ordering bugs, low-memory zeroing of droppable state, unsupported flags, and exact syscall fallback compatibility before RNG readiness. Test signals include parameter query ABI, flag matrix, zero-length behavior before and after readiness, fork detection, signal handler reentrancy, state page-boundary rejection, generation reseed races, and byte-for-byte length returns capped by `MAX_RW_COUNT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/vdso/getrandom.c -->
