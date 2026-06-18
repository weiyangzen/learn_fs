# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/uaccess.h

## Purpose

implements user memory access validation, copy, clear, get_user, put_user, and exception-table
wrappers

## Important APIs, Types, and Functions

Source read size: 269 lines, 7126 bytes. Includes: `linux/kernel.h`, `asm/mmu.h`, `asm/page.h`,
`linux/pgtable.h`, `asm/extable.h`, `linux/string.h`, `asm-generic/access_ok.h`. Defined functions:
`__clear_user`, `clear_user`, `raw_copy_from_user`, `raw_copy_to_user`. Declared functions:
`Copyright`, `__volatile__`, `__clear_user`, `__user_bad`, `typeof`, `__get_user_asm`,
`__put_user_asm`, `__copy_tofrom_user`, `strncpy_from_user`. Key macros/defines:
`_ASM_MICROBLAZE_UACCESS_H`, `__FIXUP_SECTION`, `__EX_TABLE_SECTION`, `__get_user_asm(insn,
__gu_ptr, __gu_val, __gu_err)`, `get_user(x, ptr)`, `__get_user(x, ptr)`, `__put_user_asm(insn,
__gu_ptr, __gu_val, __gu_err)`, `__put_user_asm_8(__gu_ptr, __gu_val, __gu_err)`, `put_user(x,
ptr)`, `__put_user_check(x, ptr, size)`, `__put_user(x, ptr)`, `INLINE_COPY_FROM_USER`,
`INLINE_COPY_TO_USER`. External symbols referenced/declared: `__copy_tofrom_user`, `__user_bad`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
