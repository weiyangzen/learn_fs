# sources/distributed-fs/ceph-client/arch/mips/boot/tools/relocs_main.c

Purpose: host-side MIPS boot relocation tool component `relocs_main.c`.

Important APIs and functions: visible functions or definitions include die, usage, main. The file helps build the `relocs` host program.

Control flow: Kbuild compiles the host tool, wrapper files select 32-bit or 64-bit ELF behavior, and `relocs_main.c` drives option parsing and relocation scanning/emission.

State and persistence: host process state only, except for generated relocation output or modified image files requested by the tool.

Dependencies and integration points: depends on host libc, `<elf.h>`, endian helpers, regex support, and the MIPS boot build pipeline.

Risks and test signals: broken host-tool parsing causes bad relocation tables and unbootable relocatable kernels. Test with 32/64-bit MIPS kernel images and compare emitted relocation lists.
