# Research: sources/distributed-fs/ceph-client/arch/alpha/boot/head.S

`head.S` is the assembly entry and PAL helper layer for the Alpha bootloader objects. `__start` initializes GP relative to the current PC, calls C `start_kernel`, and halts through PAL if it returns.

Exported entry points include `wrent`, `wrkgp`, `switch_to_osf_pal`, `tbi`, `halt`, and `move_stack`. `switch_to_osf_pal` saves integer registers on the current stack, stores the current KSP into the PCB supplied by C, sets PAL arguments, calls `PAL_swppal`, restores registers on return, and returns the PAL status. `move_stack` copies the active 8 KiB stack page to a new page preserving the current offset, then switches `$30`.

The file has no persistent storage; it mutates PAL state, the PCB, and stack pointer. Integration is direct with `main.c`, `bootp.c`, and `bootpz.c`, which declare these helpers. Risks are ABI-level: register save layout, stack-page size, PAL calling convention, and GP setup must match the Alpha ABI and linker script. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
