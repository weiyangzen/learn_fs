## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/extable.h

Purpose: defines PowerPC relative exception table entries and helpers for fault fixups.

Important APIs/types/functions: `ARCH_HAS_RELATIVE_EXTABLE`, `struct exception_table_entry`, `extable_fixup()`, and `EX_TABLE(_fault, _target)`.

Control flow: faulting instruction addresses and fixup targets are stored as relative offsets in `__ex_table`. On fault, `extable_fixup()` reconstructs the continuation address from the entry-local offset.

State and persistence: exception table entries persist in the kernel image. The header owns no mutable state.

Dependencies and integration: used by inline assembly, uaccess, copy routines, and exception handling code that recovers from expected faults.

Risks and test signals: relative offset encoding must match linker/runtime lookup assumptions. Bad entries cause recoverable faults to oops or continue at the wrong address. Test signals include uaccess fault injection, copy_from_user tests, exception table sorting/lookup, and module exception table handling.
