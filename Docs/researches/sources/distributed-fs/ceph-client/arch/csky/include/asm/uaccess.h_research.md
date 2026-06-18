# sources/distributed-fs/ceph-client/arch/csky/include/asm/uaccess.h

## Purpose

implements user memory access, copying, and exception-table helpers

## Important APIs, Types, and Functions

Source read size: 203 lines, 4980 bytes. Includes: `asm-generic/uaccess.h`. Functions:
`__put_user_fn`, `__get_user_fn`. Key macros/defines: `__ASM_CSKY_UACCESS_H`, `__put_user_asm_b(x,
ptr, err)`, `__put_user_asm_h(x, ptr, err)`, `__put_user_asm_w(x, ptr, err)`, `__put_user_asm_64(x,
ptr, err)`, `__put_user_fn`, `__get_user_asm_common(x, ptr, ins, err)`, `__get_user_asm_64(x, ptr,
err)`, `__get_user_fn`, `__clear_user`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
