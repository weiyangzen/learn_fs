<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/ex.S -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/ex.S

Purpose: builds SH-2A 512-entry exception vector table.

Important APIs/types/functions: `exception_entry0`, `exception_entry1`, `exception_trampoline0/1`, `vbr_base`.

Control flow: emits two banks of 256 stubs, extends vector number to 0-511, and jumps to `exception_handler`.

State and persistence: state is CPU VBR table and temporary saved r0/r1.

Dependencies/integration: integrates with SH-2A entry code and trap initialization.

Risks: stub spacing and vector-bank math must match hardware exception numbering.

Test signals: trigger low and high vector exceptions and verify handler vector numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/ex.S -->
