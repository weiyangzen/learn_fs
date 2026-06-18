# Research: sources/distributed-fs/ceph-client/arch/alpha/boot/main.c

`main.c` is the classic SRM disk bootloader for Linux/AXP. It opens the SRM boot device, reads the uncompressed kernel from the boot medium, places boot flags in the zero page, and transfers control to the kernel entry.

Important functions are `find_pa`, `pal_init`, `openboot`, `close`, `load`, `runkernel`, and `start_kernel`. `load` reads the kernel using SRM `callback_read`, with LBN offset based on the bootloader size rounded to 512-byte sectors. `runkernel` sets `$30` to `PAGE_SIZE + INIT_STACK`, places `START_ADDR` in the return register, and returns into the kernel.

State and handoff are firmware-oriented: global `hwrpb`, static dummy PCB, PAL revision update, SRM environment strings, and command line copied to `ZERO_PGE`. Risks include exact sector offset calculation using `_end - BOOT_ADDR`, assuming 8 KiB pages, partial SRM reads, and unimplemented `ENV_BOOTED_FILE` handling. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
