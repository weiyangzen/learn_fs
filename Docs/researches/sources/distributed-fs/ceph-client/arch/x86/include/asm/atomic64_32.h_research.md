
# sources/distributed-fs/ceph-client/arch/x86/include/asm/atomic64_32.h

Purpose: 64-bit atomic operations for 32-bit x86, including fallback paths for CPUs without native `cmpxchg8b`.

Important APIs and control flow: `atomic64_t` is an 8-byte-aligned signed 64-bit counter. `arch_atomic64_read_nonatomic()` is explicitly only for priming unconditional cmpxchg loops. Operation declarations point to `atomic64_*_cx8` helpers or 386 emulation helpers selected by alternatives. Core operations wrap `arch_cmpxchg64`, `arch_try_cmpxchg64`, alternative call stubs for xchg/read/set/add/sub/inc/dec, and cmpxchg loops for bitwise/fetch operations.

State, dependencies, and risks: state is shared aligned counter storage plus CPU feature/alternative patching. Dependencies include out-of-line atomic64 assembly, CX8 feature detection, cmpxchg8b emulation, and strict inline-asm constraints. Risks include torn nonatomic reads if misused, missing 8-byte alignment, and behavior differences between CX8 and 386 fallback paths. Test signals are 32-bit SMP atomic tests, non-CX8 build coverage, and stress on refcounts and lockless counters.
