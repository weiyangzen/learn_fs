# sources/distributed-fs/ceph-client/arch/loongarch/lib/Makefile

Purpose: selects LoongArch architecture library objects for low-level delay, user access, TLB dump, unaligned helpers, memory/string routines, checksum, int128 shifts, and error injection.

Important APIs, types, and functions: `lib-y` includes `delay.o`, `clear_user.o`, `copy_user.o`, `dump_tlb.o`, and `unaligned.o`; 32-bit builds add byte-swap helpers; 64-bit builds add `memset.o`, `memcpy.o`, `memmove.o`, and `csum.o`; optional objects are `tishift.o` and `error-inject.o`.

Control flow: Kbuild includes objects based on architecture width and config symbols.

State and persistence: build metadata only; it determines which low-level symbols are linked/exported.

Dependencies and integration points: used by generic kernel code, compiler runtime helper references, networking checksum paths, usercopy, and fault/debug infrastructure.

Risks: missing architecture helpers cause link failures or fallback to unsuitable generic routines. Width-specific object selection must match ABI.

Test signals: allnoconfig/defconfig/allmodconfig builds, usercopy tests, networking checksum tests, and compiler-generated int128/bswap references.
