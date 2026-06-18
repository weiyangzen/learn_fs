## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/extable.h

Purpose: defines macros to emit vDSO exception-table entries from assembly or inline assembly.

Important APIs/macros: `_ASM_VDSO_EXTABLE_HANDLE(from, to)` for assembler and C-string contexts, and `ASM_VDSO_EXTABLE_HANDLE` assembler macro. Entries are two `.long` relative offsets to `__ex_table`.

Control flow: no runtime execution. At build time, protected instruction/fixup pairs are placed in the `__ex_table` section for later scanning by `extable.c`.

State/persistence: persists relative exception-table metadata inside vDSO images.

Integration points: `vdso64/vsgx.S`, common vDSO linker script retaining `__ex_table`, and kernel fixup handler `fixup_vdso_exception()`.

Risks: relative-offset encoding differs from normal kernel extables; using the wrong macro or section would make vDSO fixups invisible. Test signals include vDSO image section inspection, SGX exception tests, and assembly build coverage.
