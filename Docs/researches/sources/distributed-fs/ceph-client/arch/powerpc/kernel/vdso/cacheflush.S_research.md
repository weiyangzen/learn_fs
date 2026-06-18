# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/cacheflush.S

## Purpose
Provides the userspace vDSO routine `__kernel_sync_dicache`, which flushes data cache and invalidates instruction cache for a supplied address range.

## Important APIs, Types, And Functions
Exports vDSO function `__kernel_sync_dicache(start, end)`. It uses `get_datapage`, cache block-size fields from `vdso_u_arch_data` on 64-bit, and the `CPU_FTR_COHERENT_ICACHE` feature section.

## Control Flow
If the CPU has coherent I-cache, the function takes a short path with `sync`, one `icbi`, `isync`, and returns zero. Otherwise it rounds the start address down to a D-cache line boundary, computes line count, emits `dcbst` over the range, synchronizes, then invalidates I-cache lines with `icbi`, finishes with `isync`, clears SO, and returns zero.

## State And Persistence
It changes hardware cache state for the caller-provided range and has no persistent software state.

## Dependencies And Integration Points
Depends on cache metadata populated by `vdso_init`, PowerPC cache instructions, vDSO feature fixups, and user JIT/self-modifying-code callers that need instruction visibility without a syscall.

## Risks And Edge Cases
Range calculation must handle empty ranges, unaligned addresses, and dynamic 64-bit cache block sizes. Incorrect feature fixups or cache metadata can leave stale instructions visible. Users must provide a valid range; the code does not fault-probe addresses.

## Test Signals
JIT/self-modifying-code tests should write instructions, call `__kernel_sync_dicache`, and execute them. Build/runtime coverage should include coherent and noncoherent I-cache CPUs, 32-bit and 64-bit vDSOs, and unusual cache block sizes.
