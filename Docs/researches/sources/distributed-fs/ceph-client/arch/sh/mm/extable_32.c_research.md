# sources/distributed-fs/ceph-client/arch/sh/mm/extable_32.c

Purpose: resolves SH exception-table fixups for recoverable kernel faults.

Important API: `fixup_exception`.

Control flow: searches the exception table for the faulting `regs->pc`; if found, rewrites the PC to the fixup address and returns success.

State and persistence: mutates `pt_regs->pc` during fault recovery; no persistent state.

Dependencies and integration: used by page fault and trap paths, depends on generic `search_exception_tables` and uaccess/checksum/copy assembly fixup entries.

Risks: wrong fixup addresses lead to loops or skipped cleanup. Assembly exception-table entries must match faulting instruction locations exactly.

Test signals: uaccess fault injection and checksum/copy-user recovery tests.
