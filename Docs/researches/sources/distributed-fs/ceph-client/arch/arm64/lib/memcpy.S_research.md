# sources/distributed-fs/ceph-client/arch/arm64/lib/memcpy.S

Purpose: optimized ARM64 implementation of `memcpy` and `memmove`, including overlap-safe large copies and optional FEAT_MOPS acceleration.

Important APIs/types/functions: `__pi_memcpy_generic`, `__pi_memcpy`, aliases `__memcpy`, `memcpy`, `__pi_memmove`, `__memmove`, `memmove`, small/medium/large copy paths, backward overlap path, MOPS `cpyp/cpym/cpye`, and exports.

Control flow: for <=32 bytes it uses branch-light byte/word/end loads; for 33..128 bytes it copies fixed leading/trailing blocks; for >128 bytes it checks destination-source overlap. Non-overlap large copies align destination and pipeline 64-byte forward loops with an end copy. Overlap uses a symmetric backward loop. If MOPS is supported, `__pi_memcpy` dispatches to copy instructions; otherwise it aliases the generic implementation.

State and persistence: writes destination memory and reads source memory. No persistent state.

Dependencies/integration: core kernel memory API, alternative patching, ARMv8 unaligned accesses, FEAT_MOPS, and exported symbols expected by generic code.

Risks: despite `memcpy` semantics, the shared implementation also handles memmove overlap; any overlap decision bug corrupts data. Tail and end-copy overlap loads/stores are delicate. MOPS behavior must match generic memmove semantics.

Test signals: libc-style memcpy/memmove torture tests, overlap forward/backward cases, all small sizes, 33..128 boundaries, large unaligned buffers, MOPS and non-MOPS CPUs, and KASAN bounds tests.
