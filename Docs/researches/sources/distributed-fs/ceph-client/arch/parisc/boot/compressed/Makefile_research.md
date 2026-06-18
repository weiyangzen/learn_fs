# sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/Makefile

Purpose: builds the PA-RISC self-extracting compressed kernel image from the already linked `vmlinux`. It assembles `head.o`/`real2.o`, compiles the decompressor support, embeds the compressed payload through `piggy.o`, and links the bootloader-format `arch/parisc/boot/compressed/vmlinux`.

Important APIs/types/functions: the public surface is Kbuild variables and rules: `OBJECTS`, `targets`, `KBUILD_CFLAGS`, `LDFLAGS_vmlinux`, `sed-sizes`, `sizes.h`, compression suffix selection from `CONFIG_KERNEL_*`, and binary-link flags for `piggy.o`. `sizes.h` exports linker-derived symbols such as `SZ__bss_start`, `SZ_end`, and `SZparisc_kernel_start`.

Control flow: Kbuild first derives `sizes.h` from the real kernel `vmlinux`, builds early boot objects with `BOOTLOADER`, links the compressed loader with `vmlinux.lds`, strips the real kernel to `vmlinux.bin`, compresses it with the configured algorithm, and relinks that binary blob into `piggy.o`.

State and persistence: no runtime state is stored here; the persistent output is the compressed boot image and generated `sizes.h`. Dependencies and integration: relies on PA-RISC compiler flags such as `-mno-space-regs`, `-mdisable-fpregs`, optional `-mfast-indirect-calls`, libgcc, `vmlinux.scr`, and generic kernel compression commands.

Risks and test signals: wrong symbol extraction or compression suffix selection can produce an image that links but cannot relocate or decompress. Build tests should cover every enabled `CONFIG_KERNEL_*` compressor and both 32-bit and 64-bit PA-RISC builds.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
