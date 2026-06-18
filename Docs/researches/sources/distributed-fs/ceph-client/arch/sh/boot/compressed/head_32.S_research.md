# sources/distributed-fs/ceph-client/arch/sh/boot/compressed/head_32.S



Source read size: 126 lines, 2430 bytes.



Purpose: 32-bit SH compressed-kernel entry code. It establishes the initial status register, relocates the loader if needed, clears BSS, calls the C decompressor, and jumps to the decompressed kernel.

Important APIs/types/functions: global `startup`, labels `clear_bss`, `stack_start`, `decompress_kernel`, `___pa(_text + PAGE_SIZE)`, cache writeback via `ocbwb`, and the fake bzImage header block.

Control flow: set privileged SR, compare current and linked addresses, copy the loader backward in cache-line chunks when relocated, clear BSS, load the bootstrap stack, call `decompress_kernel()`, then jump to the physical or linked kernel start depending on 32-bit mode.

State and persistence: mutates CPU SR, stack pointer, BSS, and instruction/data cache state; no persistent data beyond boot memory layout.

Dependencies and integration points: coupled to `vmlinux.lds`, `misc.c`, SH cache instructions, kexec zImage parsing magic, page constants, and the compressed payload object.

Risks and test signals: relocation overlap, cache writeback, SR masking, and kernel-start physical translation are fragile. Test with relocated and non-relocated zImage loads, kexec parsing, SH4 cache-enabled systems, and all compression formats.
