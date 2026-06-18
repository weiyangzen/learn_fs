<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/getrandom.h -->
# sources/distributed-fs/ceph-client/include/vdso/getrandom.h

Purpose: declares the vDSO getrandom state layout and architecture hooks for stack-safe ChaCha20 generation and the exported `__vdso_getrandom` entry point.

Important APIs and types: `vgetrandom_state` holds a union of buffered random bytes plus the next ChaCha key, a generation snapshot, current batch position, and reentrancy guard. `__arch_chacha20_blocks_nostack()` generates ChaCha20 output without stack writes, and `__vdso_getrandom()` is the arch-specific vDSO symbol delegating to common code.

Control flow: userspace passes an opaque per-thread state to `__vdso_getrandom`; the vDSO checks RNG generation/readiness, consumes buffered bytes, derives a new key/batch through the arch ChaCha routine, and falls back to syscall behavior when needed.

State and persistence: the opaque state is userspace-owned transient per-thread state. Its generation ties it to `vdso_rng_data`; it must be refreshed after kernel reseed. `in_use` prevents same-thread signal-handler reentrancy from reusing mutable state.

Dependencies and integration points: depends on Linux types and integrates with `vdso/datapage.h` RNG data, common vDSO getrandom implementation, arch ChaCha assembly/C code, and the getrandom syscall ABI.

Risks and test signals: risks include leaking stack data across fork, reentrancy races, stale generation handling, incorrect opaque state length, and flags behavior mismatch with syscall. Test fork/signal stress, reseed generation changes, small/large reads, invalid flags, fallback paths, and architecture ChaCha known-answer outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/getrandom.h -->
