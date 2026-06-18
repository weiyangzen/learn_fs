# sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/firmware.c

Purpose: includes the architecture firmware implementation from `arch/parisc/kernel/firmware.c` into the compressed bootloader build so early decompressor code can call PDC/IODC services before the full kernel is available.

Important APIs/types/functions: this file declares no new API; it reuses the firmware call wrappers and console routines from the kernel source, especially the PDC IODC printing path consumed by `misc.c`.

Control flow: control is inherited completely from the included source. In this build context, calls are made by bootloader code while virtual memory, normal devices, and kernel services are not yet initialized.

State and persistence: any state is firmware-owned or static state from the included implementation. Dependencies and integration: tightly depends on relative source layout, `BOOTLOADER` preprocessor behavior, and PA-RISC firmware ABI headers.

Risks and test signals: the include wrapper can silently break if the kernel firmware source starts depending on full-kernel facilities unavailable to the decompressor. Boot tests should verify early console output and firmware calls from the compressed loader.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
