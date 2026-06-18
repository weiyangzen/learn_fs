# sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/misc.c

Purpose: implements the C side of the PA-RISC compressed kernel loader: tiny libc helpers, firmware console output, decompressor integration, ELF program-header parsing, cache flushes, and final jump to the real kernel.

Important APIs/types/functions: defines `memmove`, `memset`, `memcpy`, `strlen`, `strchr`, `error`, minimal `printf`, allocator wrappers, `flush_data_cache`, `parse_elf`, and decompressor entry plumbing for gzip, bzip2, lz4, lzma, lzo, and xz. Externs include `input_data`, `input_len`, `output_len`, `_bss`, `_ebss`, `_startcode_end`, and `startup_continue`.

Control flow: the loader allocates a scratch area, decompresses `piggy.o` input, validates the ELF magic, copies loadable segments to their target addresses, clears segment BSS, flushes data/instruction caches, and calls `startup_continue(entry, cmdline, rd_start, rd_end)`.

State and persistence: `free_mem_ptr` and `free_mem_end_ptr` are the only heap state; loaded ELF segments persist as the kernel image. Dependencies and integration: uses included generic decompressor C files, PA-RISC cache instructions, `get_unaligned` for linker-provided `output_len`, and firmware printing.

Risks and test signals: malformed segment sizes, unaligned length reads, cache flushing, or scratch overlap can corrupt the boot image. Test each compressor, verify ELF segment placement with crafted images, and boot with/without initrd and command line.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
