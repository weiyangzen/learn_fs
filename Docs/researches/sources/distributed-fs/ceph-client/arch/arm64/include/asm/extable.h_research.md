## sources/distributed-fs/ceph-client/arch/arm64/include/asm/extable.h

Purpose: defines arm64 exception-table entry layout and fixup helpers.

Important APIs/types/functions: includes generic extable support, defines architecture exception table structures/macros, and declares fixup handlers used by uaccess and fault recovery paths.

Control flow: when a fault occurs at a protected instruction, exception handling searches extables and redirects execution to a fixup target or specialized handler.

State and persistence: exception table entries are persistent kernel image metadata; runtime state is the adjusted pt_regs.

Dependencies and integration: used by uaccess, futex, copy routines, alternatives, module loading, and fault handling.

Risks: bad relative offsets or handler IDs can turn recoverable user faults into kernel oopses. Test signals are usercopy fault tests, futex fault tests, module extable validation, and objtool/build checks.
