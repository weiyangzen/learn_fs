<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/ex.S -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/ex.S

Purpose: builds the SH-2 exception vector trampoline table.

Important APIs/types/functions: `vbr_base`, `exception_entry`, `exception_trampoline`.

Control flow: generates 256 vector stubs that save r0/r1, encode the vector number, and jump to `exception_handler`.

State and persistence: state is CPU VBR pointing at this table and the temporary exception stack frame.

Dependencies/integration: integrates with `per_cpu_trap_init()` and SH-2 entry.S.

Risks: stub size and vector arithmetic must match VBR table assumptions.

Test signals: trigger representative exceptions/IRQs and verify vector numbers reach handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/ex.S -->
