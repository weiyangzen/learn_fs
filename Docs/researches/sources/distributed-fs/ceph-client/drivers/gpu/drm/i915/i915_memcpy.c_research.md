# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_memcpy.c

## Purpose
Implements accelerated reads from write-combining memory using SSE4.1 `movntdqa`, with aligned and mostly-unaligned variants for i915 buffer readback paths.

## Important APIs, types, and functions
Public functions are `i915_memcpy_init_early()`, `i915_memcpy_from_wc()`, and `i915_unaligned_memcpy_from_wc()`. Private helpers `__memcpy_ntdqa()` and `__memcpy_ntdqu()` perform inline assembly copies inside `kernel_fpu_begin()/end()`. `has_movntdqa` is a static key.

## Control flow
Early init enables the static key only when the CPU supports SSE4.1 and is not running under a hypervisor. The aligned copy rejects any source, destination, or length not 16-byte aligned and returns whether acceleration was possible. The unaligned copy first copies bytes until the source is 16-byte aligned, then uses unaligned stores and rounded-up 16-byte reads for the remainder.

## State and persistence
The only persistent state is the `has_movntdqa` static branch. Copy operations do not store driver state.

## Dependencies and integration points
Depends on x86 FPU APIs, cpufeature checks, static branches, and callers that map WC memory and can satisfy alignment/read-past-end guarantees.

## Risks
FPU usage in kernel context must be bracketed correctly. `i915_unaligned_memcpy_from_wc()` assumes callers provide valid memory for a possible 16-byte read past the requested end. Hypervisor emulation gaps intentionally disable the fast path. Non-x86 builds would need equivalent support elsewhere.

## Test signals
Call `i915_has_memcpy_from_wc()`, aligned and misaligned copies, readback correctness from WC mappings, KVM guest behavior, and debug builds where `CI_BUG_ON()` catches invalid unaligned use.
