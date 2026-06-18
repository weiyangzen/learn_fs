# sources/distributed-fs/ceph-client/arch/arc/mm/extable.c

Purpose: implements ARC exception-table fixup lookup.

Important APIs/functions: `fixup_exception(struct pt_regs *regs)` searches exception tables for the current instruction pointer and, if found, rewrites `regs->ret` to the fixup address.

Control flow: called from fault/trap paths before declaring kernel faults fatal. A found entry returns `1`; no entry returns `0`.

State and persistence: no owned state; mutates `pt_regs` to redirect execution to fixup code.

Dependencies and integration: depends on generic exception-table search, ARC `instruction_pointer()` semantics, and `.fixup`/`__ex_table` placement from linker and inline assembly.

Risks: incorrect instruction pointer or fixup address causes bad recovery from uaccess faults. Missing exception table entries turn recoverable user-copy faults into oopses.

Test signals: `copy_to_user()`/`copy_from_user()` fault injection, unaligned emulation guarded byte accesses, and kernel fault tests that should recover via exception tables.
