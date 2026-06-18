# sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/head.S

Purpose: provides the entry point for the PA-RISC compressed kernel loader. It initializes a minimal execution environment, clears the loader BSS, determines payload placement, and branches into C decompression.

Important APIs/types/functions: exports `ENTRY(startup)` and local `startup_continue`; includes `sizes.h`, `asm/psw.h`, `asm/pdc.h`, and assembly macros. It uses `BOOTADDR`, PA 2.0 wide-mode PSW handling, and linker symbols from the generated size header.

Control flow: firmware enters `startup`; the assembly selects the correct PSW width mode, prepares stack/global register state, zeros the loader BSS, passes firmware command-line and initrd arguments onward, and after decompression `startup_continue` transfers control to the uncompressed kernel entry.

State and persistence: mutates only early CPU registers and memory ranges owned by the compressed loader. Dependencies and integration: depends on exact linker-script layout, PA-RISC calling conventions, PDC-provided boot registers, and `misc.c`'s decompression entry.

Risks and test signals: register, PSW, or BSS mistakes are immediate boot failures and can differ between 32-bit and 64-bit kernels. Test with objdump entry inspection and boot smoke tests on narrow and wide PA-RISC targets.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
