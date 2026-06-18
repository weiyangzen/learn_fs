# sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/vmlinux.lds.S

Purpose: linker script for the PA-RISC compressed loader image. It fixes the loader entry point, section layout, page alignment, embedded payload positions, BSS bounds, and discarded metadata for the self-extracting binary.

Important APIs/types/functions: exports the `startup` entry and layout symbols such as `_text`, `_startcode_end`, `input_data`, `input_len`, `output_len`, `__bss_start`, `_bss`, `_ebss`, and `_end`. It selects `elf32-hppa-linux` or `elf64-hppa-linux` output format according to `CONFIG_64BIT`.

Control flow: no runtime control flow is implemented, but the script dictates the memory order consumed by `head.S`, `misc.c`, and `sizes.h`: loader text/data first, compressed payload next, then BSS.

State and persistence: the script creates persistent load-image symbols and ranges. Dependencies and integration: includes generic linker helpers, `asm/page.h`, and generated `sizes.h`.

Risks and test signals: section reordering can make `misc.c` overwrite itself or misread the compressed payload. Verify with `readelf -S/-s`, `nm` symbol checks, and compressed-kernel boot tests.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
