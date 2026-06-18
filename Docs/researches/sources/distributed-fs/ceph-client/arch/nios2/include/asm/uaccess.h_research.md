# sources/distributed-fs/ceph-client/arch/nios2/include/asm/uaccess.h

Purpose: implements Nios II get_user, put_user, raw user-copy declarations, and exception-table annotated
inline user access sequences.

Important APIs/types/functions: functions: `Copyright`, `clear_user`; prototypes: `__volatile__`, `__clear_user`,
`raw_copy_from_user`, `__get_user_unknown`, `__get_user_asm`, `__typeof__`, `__put_user_asm`;
macros: `_ASM_NIOS2_UACCESS_H`, `__EX_TABLE_SECTION`, `INLINE_COPY_FROM_USER`,
`INLINE_COPY_TO_USER`, `__get_user_asm(val, insn, addr, err)`, `__get_user_8(val, ptr, err)`,
`__get_user_common(val, size, ptr, err)`, `__get_user(x, ptr)`, `get_user(x, ptr)`,
`__put_user_asm(val, insn, ptr, err)`, `__put_user_common(__pu_val, __pu_ptr)`, `__put_user(x,
ptr)`, and 1 more.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/string.h`, `asm/page.h`, `asm/extable.h`, `asm-generic/access_ok.h`.
Integration points include generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree,
syscall, and cache/TLB subsystems plus Nios II control-register assembly. This source is part of the
Nios II architecture port under the vendored ceph-client kernel tree.

Risks: Risks include stale TLB/cache state, wrong access permissions, corrupted page tables, bad ASID
reuse, kernel faults without fixups, DMA coherency loss, or ABI-visible memory corruption.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
