<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/generic/Makefile

**Purpose:** Selects objects for the generic MIPS machine support directory.

**Important APIs/types/functions:** Core objects `init.o`, `irq.o`, and `proc.o` depend on `CONFIG_MACH_GENERIC_CORE`; board/shim objects depend on their Kconfig symbols.

**Control flow:** Kbuild links the correct machine support files for selected boards.

**State, dependencies, integration:** Integrates generic FDT boot, IRQ helpers, proc system type, YAMON fixups, and board-specific machine descriptors into the kernel image.

**Risks and test signals:** Missing object selection prevents `MIPS_MACHINE` descriptors or platform hooks from linking. Test representative configs for generic core, each legacy board, Ingenic, Ranchu, and Realtek.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/Makefile -->
