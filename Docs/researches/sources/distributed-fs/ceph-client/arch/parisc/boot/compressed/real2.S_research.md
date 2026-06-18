# sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/real2.S

Purpose: reuses `arch/parisc/kernel/real2.S` inside the compressed bootloader. That source contains low-level real-mode/PDC transition support needed before the full kernel runtime exists.

Important APIs/types/functions: this wrapper adds no symbols of its own; the API is the assembly entry points from the included `real2.S`, compiled with `BOOTLOADER` and the compressed-loader assembler flags.

Control flow: calls from early boot or firmware helpers enter the included real-mode routines, switch to the required PA-RISC firmware calling context, perform the firmware operation, and return to loader code.

State and persistence: register and space-register state is transient but ABI-critical. Dependencies and integration: depends on relative source layout, `asm/assembly.h`, PDC ABI definitions, and bootloader-specific preprocessor paths.

Risks and test signals: changes to the shared real-mode source can break the decompressor even if the normal kernel still builds. Boot tests should cover firmware console output and any PDC calls made by the compressed loader.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
