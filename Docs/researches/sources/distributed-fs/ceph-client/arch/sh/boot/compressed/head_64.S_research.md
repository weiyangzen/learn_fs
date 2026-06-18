# sources/distributed-fs/ceph-client/arch/sh/boot/compressed/head_64.S



Source read size: 159 lines, 4021 bytes.



Purpose: SHmedia/SH-5 compressed-kernel startup code that installs fixed TLB mappings, enables caches and MMU, runs decompression, disables MMU, and branches to the decompressed image.

Important APIs/types/functions: global `startup`, fixed ITLB/DTLB constants, ICCR/OCCR cache register setup, `decompress_kernel`, `stack_start`, and target branch to `CONFIG_MEMORY_START + 0x2000`.

Control flow: clears branch target registers to avoid speculative device fetches, invalidates ITLB/DTLB entries, creates 512 MiB cached mappings, enables instruction and operand caches, enters MMU mode through SSR/SPC/RTE, clears BSS, calls decompression, disables MMU, then jumps to the kernel.

State and persistence: initializes TLB, cache controller registers, SR/MMU state, stack, and BSS. These are transient boot states before the main kernel takes over.

Dependencies and integration points: depends on SHmedia cache/TLB/register definitions, memory-start config, linker labels, and the C decompressor.

Risks and test signals: early TLB/cache register errors can hang before console output; the final entry address is hard-coded relative to memory start. Test on SHmedia configurations with cache/TLB tracing or emulator support.
