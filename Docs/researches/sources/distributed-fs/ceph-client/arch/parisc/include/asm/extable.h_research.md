# sources/distributed-fs/ceph-client/arch/parisc/include/asm/extable.h

Purpose: defines PA-RISC exception-table entry layout and fixup sorting/search semantics.

Important APIs/types/functions: declares `struct exception_table_entry`, `ARCH_HAS_RELATIVE_EXTABLE`, fixup address accessors, and exception-table helper hooks.

Control flow: fault handlers search exception tables after recoverable faults, find the fixup target, and redirect instruction execution.

State and persistence: exception table entries persist in kernel ELF sections. Dependencies and integration: used by uaccess, copy routines, module loading, and generic extable code.

Risks and test signals: wrong relative offset handling causes recoverable user-copy faults to oops. Test with fault-injection in `copy_to_user`/`copy_from_user`, module extables, and sorted-section checks.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
