# sources/distributed-fs/ceph-client/arch/loongarch/lib/clear_user.S

Purpose: implements `__clear_user()` for zeroing user memory with fault recovery and optional fast unaligned 64-bit stores.

Important APIs, types, and functions: exported `__clear_user`, generic byte loop `__clear_user_generic`, and 64-bit `__clear_user_fast` selected through `ALTERNATIVE` when `CPU_FEATURE_UAL` is present.

Control flow: 32-bit or CPUs without unaligned support use byte stores with exception-table recovery. The fast path handles small sizes through a jump table and larger sizes by zeroing the first word, aligning upward, then storing 64/32/16/8-byte chunks plus tail. Exception table entries route faults to fixups that finish byte-wise where possible and return bytes not cleared.

State and persistence: no global state; returns remaining byte count in `a0`.

Dependencies and integration points: called by generic usercopy APIs; depends on alternative patching, exception tables, CPU feature `UAL`, and unwind hints for nonstandard assembly.

Risks: fixup return counts must be exact for usercopy semantics. Fast unaligned stores require CPU support. Jump-table offsets and exception labels are fragile.

Test signals: LKDTM/usercopy tests, fault injection with inaccessible user pages, KASAN/usercopy checks, and CPU feature alternative coverage.
