<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/string_64.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/string_64.S

## Purpose
This PPC64 assembly file implements the 64-bit `__arch_clear_user` primitive for zeroing user memory with optimized short, medium, and cache-line-sized paths.

## Important APIs, types, and functions
The exported `_GLOBAL_TOC(__arch_clear_user)` entry uses helper macros `err1`, `err2`, and `err3` to attach exception table entries to stores. It reads cache block size/log size from `ppc64_caches`.

## Control flow
The routine aligns the destination to 8 bytes, then chooses short clears, 32-byte medium clears, or a long path using `dcbz` after aligning to the data-cache block size. Fixup labels retry with byte stores or return the remaining byte count after a fault.

## State and persistence behavior
It writes zeros to user memory and returns zero on full success or the number of bytes not cleared. It uses register-only bookkeeping and has no durable state.

## Dependencies and integration points
This is used by PPC64 uaccess clear-user paths after access validation. It depends on valid cache metadata offsets, exception tables, and the architecture guarantee that `dcbz` can clear cacheable user memory.

## Risks and edge cases
Fault recovery must preserve correct residual counts across aligned stores, long `dcbz` loops, and fallback byte clearing. Wrong cache block metadata or non-cacheable destinations could make the optimized path unsafe.

## Test signals
Signals include kernel usercopy tests, copy/clear fault-injection, and architecture boot/runtime use of `clear_user`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/string_64.S -->
