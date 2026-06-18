# sources/distributed-fs/ceph-client/arch/mips/include/asm/uaccess.h

## Purpose

`uaccess.h` implements MIPS user-memory access primitives and raw copy/string helpers.

## Important APIs, Types, And Functions

Important APIs are `put_user()`, `get_user()`, `__put_user()`, `__get_user()`, `raw_copy_from_user()`, `raw_copy_to_user()`, `clear_user()`, `strncpy_from_user()`, `strnlen_user()`, kernel nofault helpers, and exception-table-backed load/store assembly macros. Includes: `linux/kernel.h`, `linux/string.h`, `asm/asm-eva.h`, `asm/extable.h`, `asm-generic/access_ok.h`. Macros/constants: `_ASM_UACCESS_H`, `__UA_LIMIT`, `TASK_SIZE_MAX`, `__UA_ADDR`, `__UA_LA`, `__UA_ADDU`, `__UA_t0`, `__UA_t1`, `put_user`, `get_user`, `__put_user`, `__get_user`, `__m`, `__GET_DW`, `__get_data_asm`, `__get_data_asm_ll32`, `__get_kernel_nofault`, `__PUT_DW`, `__put_data_asm`, `__put_data_asm_ll32`, `__put_kernel_nofault`, `__MODULE_JAL`, `DADDI_SCRATCH`, `INLINE_COPY_FROM_USER`, `INLINE_COPY_TO_USER`, `bzero_clobbers`, `clear_user`. Types/enums/unions: `__large_struct`. Functions/prototypes/helpers: `__raw_copy_from_user`, `__raw_copy_to_user`, `raw_copy_from_user`, `raw_copy_to_user`, `__bzero`, `__clear_user`, `__strncpy_from_user_asm`, `strncpy_from_user`, `__strnlen_user_asm`, `strnlen_user`, `might_fault`, `__chk_user_ptr`, `__put_data_asm`, `__PUT_DW`, `BUILD_BUG`, `__asm__`.

## Control Flow

The macros check `access_ok()` for public helpers, execute EVA or normal user load/store instructions, and install `__ex_table` fixups that set `-EFAULT`, zero destinations where required, or return uncopied byte counts. Bulk copy jumps into assembly routines with ABI-fixed argument registers.

## State And Persistence

State is caller buffers, user memory, exception-table metadata, and residual counts/errors; no long-lived state is stored.

## Dependencies And Integration Points

It depends on `asm-eva.h`, `extable.h`, generic `access_ok`, module long-call handling, DADDI/EVA prefetch workarounds, and copy-user assembly implementations.

## Risks

Risks are security-critical: missing bounds checks, bad exception fixups, wrong register clobbers, data leaks on fault, residual-count errors, and module call range issues.

## Test Signals

Test signals are LTP uaccess/syscall tests, fault-injection into user copies, hardened usercopy, KASAN where available, 32/64-bit and EVA builds, and copy/string boundary tests.
Static review signal: this source currently has 565 lines and 15028 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
