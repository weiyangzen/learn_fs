# sources/distributed-fs/ceph-client/arch/riscv/kernel/pi/pi.h

Purpose: Declares interfaces shared by RISC-V position-independent early boot helpers.

Important APIs/types/functions: Declares early FDT, command-line, SATP mode, KASLR seed, and architectural random helper functions.

Control flow: Header-only; no runtime logic.

State and persistence: No direct state, but the declared helpers influence persistent boot choices such as KASLR and page-table mode.

Dependencies and integration points: Used by `archrandom_early.c`, `cmdline_early.c`, `fdt_early.c`, and early boot/MM setup.

Risks and test signals: Prototype drift can break early boot or link. Test all PI helper build configs and early boot with and without KASLR.
