# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-tx49xx/spaces.h

Purpose: TX49xx virtual address layout override.

Important APIs/types/functions: Defines `FIXADDR_TOP` as `((unsigned long)(long)(int)0xfefe0000)` before including generic MIPS spaces. The cast preserves a sign-extended 32-bit fixed-address top on relevant builds.

Control flow, state, and persistence: No runtime behavior. This header changes address constants used to lay out fixmap and kernel virtual regions.

Dependencies and integration: Includes `asm/mach-generic/spaces.h` after defining the platform override. It integrates with fixmap, ioremap, highmem, and early boot virtual memory setup.

Risks and test signals: Address-layout mistakes can overlap fixed mappings with other kernel regions or break early I/O mappings. Test by building TX49xx, validating boot-time memory layout messages, and exercising fixmap users such as early console or PCI setup.
