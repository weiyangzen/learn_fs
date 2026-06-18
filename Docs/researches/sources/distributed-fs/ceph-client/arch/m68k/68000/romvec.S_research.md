# sources/distributed-fs/ceph-client/arch/m68k/68000/romvec.S

Purpose: ROM vector table for 68000 CPU startup. It supplies the initial stack pointer, reset PC, default exception handlers, and syscall trap vector in a dedicated `.romvec` section.

The table `e_vectors` begins with `CONFIG_RAMBASE + CONFIG_RAMSIZE - 4` as the initial SP and `_start` as the reset vector. Bus errors go to `buserr`, most processor exceptions and traps go to `trap`, and TRAP #0 is wired to `system_call`. Later entries are zero-filled placeholders.

State/persistence: this is static ROM image content used before C initialization and before the RAM vector table is fully initialized. It does not execute by itself but controls first CPU dispatch after reset.

Dependencies include `_start` from `head.S`, `buserr`/`trap`/`system_call` trap handlers, linker placement for `.romvec`, and Kconfig RAM sizing. Integration is with ROM/XIP boot images and CPU reset expectations.

Risks and test signals: a wrong initial SP or reset vector prevents boot; an incorrect syscall trap vector breaks the user ABI. Validate linker map placement, objdump of `.romvec`, and a boot smoke test that reaches `_start` and later accepts system calls.
