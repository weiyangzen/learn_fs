# sources/distributed-fs/ceph-client/arch/mips/boot/compressed/calc_vmlinuz_load_addr.c

Purpose: MIPS compressed-kernel boot support file `calc_vmlinuz_load_addr.c`. It provides either decompressor build rules, tiny C runtime helpers, UART debug output, or low-level entry code needed before the full kernel is decompressed.

Important APIs and functions: visible functions or entry points include main. The file is compiled into the self-extracting boot image with minimal library support.

Control flow: firmware jumps into the compressed image entry code, the decompressor runtime initializes enough state for debug I/O and memory operations, calls the selected decompression backend, then jumps to the decompressed kernel address.

State and persistence: uses only early boot memory, scratch buffers, UART registers, and linker-provided symbols. No persistent state.

Dependencies and integration points: depends on the compressed boot Makefile, linker script symbols, optional debug UART backends, architecture byte-order/libgcc replacement helpers, and kernel decompressor interfaces.

Risks and test signals: failures are usually pre-kernel and hard to diagnose. Test by building all compression modes, enabling early compressed boot debug where supported, checking image load addresses, and booting on boards that use each UART/debug path.
