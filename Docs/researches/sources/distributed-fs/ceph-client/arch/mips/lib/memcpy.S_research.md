# sources/distributed-fs/ceph-client/arch/mips/lib/memcpy.S

Purpose: implements optimized MIPS `memcpy`, `memmove`, reverse copy, and raw user-copy routines with exception-table handling.

Important APIs/functions: exports `memmove`, `memcpy`, `__raw_copy_from_user`, and `__raw_copy_to_user`; internal `__rmemcpy` handles backward overlap. The `__BUILD_COPY_USER` macro generates legacy and EVA copy bodies with load/store fixups.

Control flow: forward copy aligns destination/source, uses prefetch and unrolled word/dword loops for aligned and unaligned cases, then handles tail bytes. `memmove` selects forward or reverse copy based on overlap. User-copy variants return remaining bytes after faults using exception handlers and task bad-address state.

State and persistence: mutates destination memory; no global state. Fault fixups report incomplete byte counts.

Dependencies and integration: fundamental kernel memory and usercopy ABI; depends on MIPS 32/64-bit mode, endian-specific unaligned load/store pairs, EVA instructions, exception tables, and CPU errata workarounds.

Risks: extremely sensitive to overlap direction, fault accounting, alignment, prefetch safety, and endian-specific first/rest load-store ordering. A bug can corrupt arbitrary kernel/user memory.

Test signals: lib/string tests, usercopy fault injection, overlap memmove tests, EVA builds, 32/64-bit and endian matrix builds, and boot stability.
