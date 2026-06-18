# subset-b-000756 Research

Grouped research report for the PA-RISC compressed boot and architecture header subset. Each source section is delimited for deterministic reconciliation into the requested source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/Makefile -->
# sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/Makefile

Purpose: builds the PA-RISC self-extracting compressed kernel image from the already linked `vmlinux`. It assembles `head.o`/`real2.o`, compiles the decompressor support, embeds the compressed payload through `piggy.o`, and links the bootloader-format `arch/parisc/boot/compressed/vmlinux`.

Important APIs/types/functions: the public surface is Kbuild variables and rules: `OBJECTS`, `targets`, `KBUILD_CFLAGS`, `LDFLAGS_vmlinux`, `sed-sizes`, `sizes.h`, compression suffix selection from `CONFIG_KERNEL_*`, and binary-link flags for `piggy.o`. `sizes.h` exports linker-derived symbols such as `SZ__bss_start`, `SZ_end`, and `SZparisc_kernel_start`.

Control flow: Kbuild first derives `sizes.h` from the real kernel `vmlinux`, builds early boot objects with `BOOTLOADER`, links the compressed loader with `vmlinux.lds`, strips the real kernel to `vmlinux.bin`, compresses it with the configured algorithm, and relinks that binary blob into `piggy.o`.

State and persistence: no runtime state is stored here; the persistent output is the compressed boot image and generated `sizes.h`. Dependencies and integration: relies on PA-RISC compiler flags such as `-mno-space-regs`, `-mdisable-fpregs`, optional `-mfast-indirect-calls`, libgcc, `vmlinux.scr`, and generic kernel compression commands.

Risks and test signals: wrong symbol extraction or compression suffix selection can produce an image that links but cannot relocate or decompress. Build tests should cover every enabled `CONFIG_KERNEL_*` compressor and both 32-bit and 64-bit PA-RISC builds.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/firmware.c -->
# sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/firmware.c

Purpose: includes the architecture firmware implementation from `arch/parisc/kernel/firmware.c` into the compressed bootloader build so early decompressor code can call PDC/IODC services before the full kernel is available.

Important APIs/types/functions: this file declares no new API; it reuses the firmware call wrappers and console routines from the kernel source, especially the PDC IODC printing path consumed by `misc.c`.

Control flow: control is inherited completely from the included source. In this build context, calls are made by bootloader code while virtual memory, normal devices, and kernel services are not yet initialized.

State and persistence: any state is firmware-owned or static state from the included implementation. Dependencies and integration: tightly depends on relative source layout, `BOOTLOADER` preprocessor behavior, and PA-RISC firmware ABI headers.

Risks and test signals: the include wrapper can silently break if the kernel firmware source starts depending on full-kernel facilities unavailable to the decompressor. Boot tests should verify early console output and firmware calls from the compressed loader.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/head.S -->
# sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/head.S

Purpose: provides the entry point for the PA-RISC compressed kernel loader. It initializes a minimal execution environment, clears the loader BSS, determines payload placement, and branches into C decompression.

Important APIs/types/functions: exports `ENTRY(startup)` and local `startup_continue`; includes `sizes.h`, `asm/psw.h`, `asm/pdc.h`, and assembly macros. It uses `BOOTADDR`, PA 2.0 wide-mode PSW handling, and linker symbols from the generated size header.

Control flow: firmware enters `startup`; the assembly selects the correct PSW width mode, prepares stack/global register state, zeros the loader BSS, passes firmware command-line and initrd arguments onward, and after decompression `startup_continue` transfers control to the uncompressed kernel entry.

State and persistence: mutates only early CPU registers and memory ranges owned by the compressed loader. Dependencies and integration: depends on exact linker-script layout, PA-RISC calling conventions, PDC-provided boot registers, and `misc.c`'s decompression entry.

Risks and test signals: register, PSW, or BSS mistakes are immediate boot failures and can differ between 32-bit and 64-bit kernels. Test with objdump entry inspection and boot smoke tests on narrow and wide PA-RISC targets.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/misc.c -->
# sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/misc.c

Purpose: implements the C side of the PA-RISC compressed kernel loader: tiny libc helpers, firmware console output, decompressor integration, ELF program-header parsing, cache flushes, and final jump to the real kernel.

Important APIs/types/functions: defines `memmove`, `memset`, `memcpy`, `strlen`, `strchr`, `error`, minimal `printf`, allocator wrappers, `flush_data_cache`, `parse_elf`, and decompressor entry plumbing for gzip, bzip2, lz4, lzma, lzo, and xz. Externs include `input_data`, `input_len`, `output_len`, `_bss`, `_ebss`, `_startcode_end`, and `startup_continue`.

Control flow: the loader allocates a scratch area, decompresses `piggy.o` input, validates the ELF magic, copies loadable segments to their target addresses, clears segment BSS, flushes data/instruction caches, and calls `startup_continue(entry, cmdline, rd_start, rd_end)`.

State and persistence: `free_mem_ptr` and `free_mem_end_ptr` are the only heap state; loaded ELF segments persist as the kernel image. Dependencies and integration: uses included generic decompressor C files, PA-RISC cache instructions, `get_unaligned` for linker-provided `output_len`, and firmware printing.

Risks and test signals: malformed segment sizes, unaligned length reads, cache flushing, or scratch overlap can corrupt the boot image. Test each compressor, verify ELF segment placement with crafted images, and boot with/without initrd and command line.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/real2.S -->
# sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/real2.S

Purpose: reuses `arch/parisc/kernel/real2.S` inside the compressed bootloader. That source contains low-level real-mode/PDC transition support needed before the full kernel runtime exists.

Important APIs/types/functions: this wrapper adds no symbols of its own; the API is the assembly entry points from the included `real2.S`, compiled with `BOOTLOADER` and the compressed-loader assembler flags.

Control flow: calls from early boot or firmware helpers enter the included real-mode routines, switch to the required PA-RISC firmware calling context, perform the firmware operation, and return to loader code.

State and persistence: register and space-register state is transient but ABI-critical. Dependencies and integration: depends on relative source layout, `asm/assembly.h`, PDC ABI definitions, and bootloader-specific preprocessor paths.

Risks and test signals: changes to the shared real-mode source can break the decompressor even if the normal kernel still builds. Boot tests should cover firmware console output and any PDC calls made by the compressed loader.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/real2.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/vmlinux.lds.S

Purpose: linker script for the PA-RISC compressed loader image. It fixes the loader entry point, section layout, page alignment, embedded payload positions, BSS bounds, and discarded metadata for the self-extracting binary.

Important APIs/types/functions: exports the `startup` entry and layout symbols such as `_text`, `_startcode_end`, `input_data`, `input_len`, `output_len`, `__bss_start`, `_bss`, `_ebss`, and `_end`. It selects `elf32-hppa-linux` or `elf64-hppa-linux` output format according to `CONFIG_64BIT`.

Control flow: no runtime control flow is implemented, but the script dictates the memory order consumed by `head.S`, `misc.c`, and `sizes.h`: loader text/data first, compressed payload next, then BSS.

State and persistence: the script creates persistent load-image symbols and ranges. Dependencies and integration: includes generic linker helpers, `asm/page.h`, and generated `sizes.h`.

Risks and test signals: section reordering can make `misc.c` overwrite itself or misread the compressed payload. Verify with `readelf -S/-s`, `nm` symbol checks, and compressed-kernel boot tests.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/boot/compressed/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/defpalo.conf -->
# sources/distributed-fs/ceph-client/arch/parisc/defpalo.conf

Purpose: default PALO bootloader configuration for PA-RISC. It documents the expected kernel image path, partition selection, boot command line, and recovery comments used when preparing boot media.

Important APIs/types/functions: not executable code; key fields are the PALO directives and commented examples that set the boot partition, kernel image, optional initrd, root device, and console/kernel parameters.

Control flow: PALO consumes this declarative file at bootloader install or boot time to find and pass arguments to the kernel. Kernel control flow begins only after the bootloader loads the configured image.

State and persistence: values persist in the installed bootloader configuration or filesystem file. Dependencies and integration: integrates with PA-RISC PALO tooling, disk partition layout, and kernel command-line parsing.

Risks and test signals: stale device names or image paths can make a system unbootable even though the kernel builds. Test by running PALO config validation where available and checking that documented paths match packaged PA-RISC boot artifacts.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/defpalo.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/Kbuild

Purpose: declares PA-RISC architecture headers that should be generated or exported through Kbuild's UAPI/header-install machinery.

Important APIs/types/functions: the file contains Kbuild directives rather than C symbols. It names generic or generated header relationships for the `arch/parisc/include/asm` tree.

Control flow: during header generation and install, Kbuild reads these declarations to decide which asm headers are produced or forwarded to generic implementations.

State and persistence: no runtime state; persistent outputs are generated header files in build/install directories. Dependencies and integration: part of the kernel header build pipeline and consumed by userspace header installation.

Risks and test signals: missing or stale entries can break external builds or generated-offset inclusion. Test with `make headers_install`, allmodconfig compile coverage, and checks that `generated/asm-offsets.h` remains reachable.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/alternative.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/alternative.h

Purpose: defines PA-RISC runtime instruction alternative metadata and assembly macros. It lets boot code patch instructions based on CPU/platform conditions such as SMP, cache presence, split TLB availability, I/O cache behavior, or QEMU.

Important APIs/types/functions: `struct alt_instr`, `ALT_COND_*`, `INSN_PxTLB`, `INSN_NOP`, declarations for `set_kernel_text_rw()` and `apply_alternatives_all()`, and the `ALTERNATIVE`/`ALTERNATIVE_CODE` macros.

Control flow: assembly emits original instructions plus entries in `__alt_instructions`; early runtime code makes kernel text writable, evaluates conditions, patches replacement instructions, and restores protection.

State and persistence: patch decisions persist by modifying kernel text. Dependencies and integration: integrates with `sections.h`, cache/TLB setup, text patching, and architecture initialization.

Risks and test signals: wrong instruction counts or section metadata can patch adjacent code. Test with objdump section checks, boot logs for alternative application, and platform coverage for all condition bits.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/alternative.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/asm-offsets.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/asm-offsets.h

Purpose: forwards PA-RISC assembly sources to the generated offsets header produced from C structure layout.

Important APIs/types/functions: this file exposes no independent definitions; it includes `generated/asm-offsets.h`.

Control flow: assembly preprocessing resolves constants such as pt_regs offsets, thread fields, and task layout from the generated header before assembling low-level entry code.

State and persistence: generated offsets persist in the build tree and must match the compiled C layout. Dependencies and integration: depends on the architecture offsets generator and all assembly code using symbolic structure offsets.

Risks and test signals: missing generation or stale offsets causes build failures or much worse register-frame corruption. Test by clean-building after structure changes and disassembling entry paths that use generated offsets.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/asm-offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/asmregs.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/asmregs.h

Purpose: names PA-RISC general, space, floating-point, and control registers for assembly readability.

Important APIs/types/functions: defines assembler aliases for ABI registers such as `rp`, `arg0`-`arg7`, `dp/gp`, `ret0`, `sp`, raw `r0`-`r31`, `sr0`-`sr7`, `fr0`-`fr31`, and control registers.

Control flow: there is no executable flow; assembly files include this header so register use remains readable and consistent with PA-RISC ABI conventions.

State and persistence: no state is stored, but aliases affect every assembled instruction using them. Dependencies and integration: included by `assembly.h` and low-level boot, trap, syscall, and context-switch sources.

Risks and test signals: alias drift can make assembly silently use the wrong hardware register. Test through assembler preprocessing and objdump inspection of exception and boot paths.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/asmregs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/assembly.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/assembly.h

Purpose: central PA-RISC assembly helper contract. It defines frame sizes, ABI constants, instruction mnemonics, space-register roles, virtual/physical conversion macros, safe bitfield macros, register save/restore blocks, and exception-frame helpers.

Important APIs/types/functions: key macros include `FRAME_SIZE`, `CALLEE_SAVE_FRAME_SIZE`, `LDCW`, `BL`, `PA_ASM_LEVEL`, `PRIV_*`, `SR_*`, `LDREG/STREG`, `tophys/tovirt`, `load32`, `loadgp`, `save_general`, `rest_general`, `save_specials`, and related pt_regs helpers.

Control flow: low-level entry code expands these macros to save register state, translate addresses, handle PA1.x versus PA2.0 instruction differences, and restore execution context.

State and persistence: it does not store state itself, but it defines the saved register-frame layout used persistently on kernel stacks. Dependencies and integration: depends on generated offsets, `page.h`, `types.h`, `asmregs.h`, and `psw.h`.

Risks and test signals: any frame-size or register-save mismatch corrupts traps, syscalls, and context switches. Test with build coverage for 32/64-bit, stack unwinder tests, syscall/trap stress, and objdump review of macro expansion.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/assembly.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/atomic.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/atomic.h

Purpose: implements PA-RISC atomic integer operations. Because PA-RISC lacks broad in-memory atomic RMW primitives, operations are serialized through hashed spinlocks around aligned values.

Important APIs/types/functions: declares `__atomic_hash[ATOMIC_HASH_SIZE]`, lock/unlock helpers, `arch_atomic_read`, `arch_atomic_set`, add/sub/and/or/xor operations, return/fetch variants, and 64-bit `atomic64_t` equivalents.

Control flow: each modifying operation chooses a hash lock from the target address, disables/restores IRQ state, updates the underlying counter, and releases the lock. Reads and sets use barriers where required.

State and persistence: atomic values persist in caller-owned memory; the global hash-lock table is shared serialization state. Dependencies and integration: depends on `cmpxchg.h`, `barrier.h`, `spinlock.h`, and cache-line alignment.

Risks and test signals: incorrect locking or alignment can lose updates under IRQ/SMP concurrency. Test with atomic selftests, lockdep, SMP stress, and 32-bit/64-bit builds.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/barrier.h

Purpose: defines PA-RISC memory-ordering primitives for normal CPU, SMP, and DMA contexts.

Important APIs/types/functions: exports `synchronize_caches()`, `mb`, `rmb`, `wmb`, `dma_rmb`, `dma_wmb`, SMP acquire/release helpers, and then includes generic barrier fallbacks.

Control flow: on SMP-capable builds barriers issue PA-RISC `sync` sequences, with alternatives available for cache-related behavior; on simpler configurations they may collapse to compiler barriers.

State and persistence: no state is stored, but ordering affects visibility of shared memory, MMIO, and DMA descriptors. Dependencies and integration: integrates with `alternative.h`, atomics, spinlocks, device drivers, and page-table updates.

Risks and test signals: too-weak barriers cause rare data races or device coherency failures; too-strong barriers cost performance. Test with memory-model litmus tests, DMA stress, and SMP filesystem/network workloads.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/bitops.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/bitops.h

Purpose: implements PA-RISC bit operations, including atomic bit set/clear/change/test and optimized find-first/last helpers.

Important APIs/types/functions: defines `set_bit`, `clear_bit`, `change_bit`, `test_and_set_bit`, `test_and_clear_bit`, `test_and_change_bit`, `__ffs`, `ffs`, `fls`, and imports generic non-atomic, little-endian, lock, scheduler, ext2, and hweight helpers.

Control flow: atomic operations are built on Linux atomic operations against the containing word; find operations use PA-RISC-friendly bit scanning sequences.

State and persistence: modifies caller-owned bitmaps, flags, page state, and filesystem bitmaps. Dependencies and integration: depends on compiler annotations, byte order, barriers, and generic bitops.

Risks and test signals: bit numbering and endian assumptions are high risk for filesystem and scheduler state. Test with bitmap selftests, ext2 bitops tests, and big-endian PA-RISC boot coverage.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/bug.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/bug.h

Purpose: provides PA-RISC implementations of `BUG()` and `WARN_ON()` using architecture break instructions and optional bug-table metadata.

Important APIs/types/functions: defines `HAVE_ARCH_BUG`, `HAVE_ARCH_WARN_ON`, `PARISC_BUG_BREAK_ASM`, `PARISC_BUG_BREAK_INSN`, `BUG()`, `__WARN_FLAGS`, and `WARN_ON()`.

Control flow: failing conditions emit a break instruction; with generic bug table support, metadata records file, line, flags, and condition string for diagnostics.

State and persistence: bug table entries persist in special ELF sections; runtime state is the trap frame produced by the break. Dependencies and integration: integrates with generic bug handling, exception decoding, and PA-RISC trap code.

Risks and test signals: wrong break encoding or table layout makes diagnostics misleading or prevents controlled panic/warn handling. Test with intentional WARN/BUG injection and objdump of bug-table sections.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/cache.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/cache.h

Purpose: declares PA-RISC cache geometry, alignment rules, cache/TLB purge instructions, and cache-initialization globals.

Important APIs/types/functions: defines `L1_CACHE_BYTES`, `ARCH_DMA_MINALIGN`, `ARCH_KMALLOC_MINALIGN`, `arch_slab_minalign`, `cache_line_size`, `pdtlb`, `pitlb`, `asm_io_fdc`, `asm_io_sync`, `asm_syncdma`, and declarations for cache setup and SID management.

Control flow: runtime cache setup populates stride and PDC cache information; low-level code uses inline assembly macros to flush TLB/cache lines and synchronize I/O.

State and persistence: globals such as `split_tlb`, `dcache_stride`, `icache_stride`, `cache_info`, and `btlb_info` persist after boot probing. Dependencies and integration: consumed by DMA, cacheflush, page-table, and allocator code.

Risks and test signals: wrong alignment or stride corrupts DMA and aliasing-cache behavior. Test with cache-info proc output, DMA stress, page alias tests, and boot on split/non-split TLB systems.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/cacheflush.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/cacheflush.h

Purpose: defines PA-RISC cache-flush interfaces used by memory management, vmalloc, folio/page writeback, and executable mapping updates.

Important APIs/types/functions: declares static keys for cache presence, assembly flush routines, `flush_cache_all`, `flush_cache_mm`, `flush_kernel_dcache_range`, `flush_kernel_vmap_range`, `invalidate_kernel_vmap_range`, `flush_dcache_folio`, `flush_dcache_page`, `flush_icache_range`, `flush_anon_page`, and `kunmap_flush_on_unmap`.

Control flow: callers select full-cache, mm, vmap, folio, page, or icache range flushing; static keys skip work on cacheless configurations.

State and persistence: no ordinary state, but cache contents and instruction visibility are affected. Dependencies and integration: depends on `mm.h`, `uaccess.h`, TLB flushing, jump labels, and page cache mappings.

Risks and test signals: missed D/I cache synchronization breaks newly generated code, modules, and userspace mappings. Test with module loading, JIT-like mprotect tests, mmap write/exec tests, and aliasing-cache workloads.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/cacheflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/cachetype.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/cachetype.h

Purpose: exposes the PA-RISC cache aliasing property to generic memory-management code.

Important APIs/types/functions: defines `cpu_dcache_is_aliasing()` as `true`.

Control flow: generic mm/cache code queries this helper to decide whether extra alias management is required for mappings and page-cache transitions.

State and persistence: no state is stored. Dependencies and integration: consumed by generic cache-management paths and architecture-neutral memory code.

Risks and test signals: reporting non-aliasing on PA-RISC would permit stale or incoherent aliases. Test through mmap alias writeback, executable mapping transitions, and cacheflush selftests.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/cachetype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/checksum.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/checksum.h

Purpose: provides PA-RISC network checksum helpers for IPv4/IPv6 pseudo-header checksums while delegating the rest to generic checksum code.

Important APIs/types/functions: defines `csum_tcpudp_nofold`, `_HAVE_ARCH_IPV6_CSUM`, and `csum_ipv6_magic()`.

Control flow: networking code calls these inline helpers while constructing or validating TCP/UDP checksums; the helpers add source/destination addresses, length, protocol, and partial checksum without folding until the caller needs it.

State and persistence: stateless arithmetic over packet fields. Dependencies and integration: includes `linux/in6.h` and `asm-generic/checksum.h`, and integrates with the IP, TCP, UDP, and IPv6 stacks.

Risks and test signals: endian or carry-folding mistakes cause dropped packets. Test with IPv4/IPv6 TCP/UDP checksum validation, offload-disabled network tests, and packet captures on PA-RISC big-endian systems.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/cmpxchg.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/cmpxchg.h

Purpose: defines PA-RISC exchange and compare-exchange primitives for typed memory sizes and local fallbacks.

Important APIs/types/functions: declares `__xchg8`, `__xchg32`, optional `__xchg64`, `__cmpxchg_u8/u16/u32/u64`, `arch_xchg`, `arch_cmpxchg`, `arch_cmpxchg_local`, and `arch_cmpxchg64`.

Control flow: callers dispatch by operand size; unsupported sizes call bad-pointer sentinel functions so misuse fails at link or runtime. Local variants use generic helpers when full atomicity is not required.

State and persistence: mutates caller-owned shared memory; serialization details live in out-of-line assembly/C implementations. Dependencies and integration: fundamental to atomics, locking, refcounts, and lock-free kernel helpers.

Risks and test signals: size dispatch or sign extension mistakes break synchronization. Test with cmpxchg selftests, 64-bit-only coverage, and lock/refcount stress under SMP.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/cmpxchg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/compat.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/compat.h

Purpose: defines PA-RISC 32-bit compatibility ABI types and structures used when a 64-bit kernel runs 32-bit userspace.

Important APIs/types/functions: provides `compat_mode_t`, `compat_ipc_pid_t`, `compat_nlink_t`, `compat_stat`, `compat_sigcontext`, IPC64 structures, `COMPAT_ELF_NGREG`, `compat_elf_gregset_t`, `__is_compat_task()`, and `is_compat_task()`.

Control flow: syscall, signal, ptrace, and ELF code query task personality/flags and marshal data through these compat layouts.

State and persistence: structures define persistent user-visible ABI memory layouts; no private runtime state is stored. Dependencies and integration: includes generic compat support, scheduler/task headers, and thread-info flags.

Risks and test signals: layout drift breaks 32-bit userspace on 64-bit kernels. Test with compat syscall suites, 32-bit signal delivery, IPC stat calls, ptrace register dumps, and ELF core generation.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/compat_ucontext.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/compat_ucontext.h

Purpose: defines the PA-RISC 32-bit compatible `ucontext` layout for signal frames on 64-bit kernels.

Important APIs/types/functions: `struct compat_ucontext` contains compat flags, link pointer, stack, signal mask, and machine context fields used by signal delivery and return.

Control flow: compat signal setup writes this structure to userspace; signal return reads it back to restore register and mask state.

State and persistence: the structure persists on the user stack for the lifetime of a delivered signal frame. Dependencies and integration: depends on `linux/compat.h`, PA-RISC signal context, and syscall/signal return code.

Risks and test signals: wrong padding or field order breaks user signal handlers. Test with 32-bit signal stress, alternate signal stacks, nested signals, and `sigreturn` validation.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/compat_ucontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/current.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/current.h

Purpose: provides PA-RISC access to the current task pointer.

Important APIs/types/functions: defines `get_current()` and `current` plumbing around `current_thread_info()`/thread-info storage.

Control flow: kernel code expands `current` to find the running task from low-level per-thread state without a function call.

State and persistence: does not store state; it exposes the scheduler-maintained current task. Dependencies and integration: used nearly everywhere in kernel code, including syscall, scheduler, and fault paths.

Risks and test signals: an incorrect current-task derivation corrupts scheduler and security decisions globally. Test through context-switch stress, syscall tracing, and stack/thread-info layout checks.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/current.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/delay.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/delay.h

Purpose: declares PA-RISC busy-wait delay routines and maps generic delay interfaces to architecture implementations.

Important APIs/types/functions: declares `__delay`, `__udelay`, `__cr16_delay`, and delay calibration hooks used by `udelay`/`ndelay` style callers.

Control flow: callers request a short wait; architecture code loops against CPU counters or calibrated cycles until elapsed time has passed.

State and persistence: relies on boot-calibrated CPU timing state outside this header. Dependencies and integration: used by drivers, early boot, firmware wait loops, and generic delay APIs.

Risks and test signals: under-delays break device programming; over-delays slow boot and drivers. Test with timer calibration, driver probe timing, and CPU-frequency/CR16 behavior checks.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/delay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/dma-mapping.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/dma-mapping.h

Purpose: supplies PA-RISC DMA mapping hooks and cache-alignment policy to the generic DMA API.

Important APIs/types/functions: declares architecture DMA operations selection and includes generic noncoherent helpers as needed; it ties `arch_dma_alloc`, `dma_set_mask`, or cache synchronization behavior to PA-RISC IOMMU/direct-DMA capabilities.

Control flow: device drivers call the generic DMA API; generic code dispatches into PA-RISC direct or IOMMU mapping implementations based on device/bus state.

State and persistence: mapping state lives in IOMMU page directories or direct DMA masks outside this header. Dependencies and integration: integrates with SBA/LBA PCI, cache alignment, and generic DMA mapping code.

Risks and test signals: wrong ops selection can cause devices to DMA to invalid or stale memory. Test with PCI DMA stress, high-memory buffers, coherent allocations, and streaming map/unmap checks.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/dma-mapping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/dma.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/dma.h

Purpose: defines legacy PA-RISC DMA constants and helpers for ISA/EISA-style DMA and fallback device code.

Important APIs/types/functions: provides DMA channel limits, address constraints, request/free DMA declarations, `MAX_DMA_ADDRESS`, and compatibility helpers for drivers still using legacy DMA APIs.

Control flow: old drivers reserve a channel, program a transfer through architecture support, and release the channel. Modern PCI devices usually use the generic DMA mapping API instead.

State and persistence: channel ownership and controller programming persist in platform DMA hardware. Dependencies and integration: integrates with EISA/ISA compatibility, floppy support, and machine-specific DMA setup.

Risks and test signals: incorrect address limits or channel programming can corrupt low memory. Test with floppy/legacy-device builds, DMA API debug, and platform probes that still expose ISA-compatible DMA.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/dwarf.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/dwarf.h

Purpose: defines PA-RISC DWARF register numbering and unwind-related constants for debugging/unwinding integration.

Important APIs/types/functions: exports architecture register number mappings used by unwinders, debug info, and low-level assembly annotations.

Control flow: unwinder/debug tooling uses these constants to map saved machine registers to DWARF register slots.

State and persistence: no runtime state; the mappings become part of generated debug/unwind metadata. Dependencies and integration: used by stack unwinding, ftrace/debug code, and toolchain-facing assembly.

Risks and test signals: wrong register numbers produce misleading traces. Test with kernel stack unwinding, kgdb backtraces, and objdump/readelf inspection of CFI where present.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/dwarf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/eisa_bus.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/eisa_bus.h

Purpose: declares PA-RISC EISA bus discovery and device representation hooks.

Important APIs/types/functions: defines or declares EISA bus structures and initialization functions used by platform bus code.

Control flow: platform initialization probes firmware-described EISA hardware, creates bus/device records, and lets EISA drivers bind.

State and persistence: discovered bus/device data persists in kernel device structures. Dependencies and integration: integrates with firmware inventory, EISA EEPROM parsing, and legacy device drivers.

Risks and test signals: firmware parsing or resource mistakes break old expansion devices. Test with EISA-enabled build configs and boot on systems with/without EISA slots.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/eisa_bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/eisa_eeprom.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/eisa_eeprom.h

Purpose: describes PA-RISC EISA EEPROM record layouts and constants used to decode EISA slot configuration.

Important APIs/types/functions: defines packed resource structures for board IDs, functions, memory, IRQ, DMA, port, and initialization data plus constants for EISA configuration tags.

Control flow: EISA setup reads EEPROM bytes, interprets records through these layouts, and registers resources for legacy drivers.

State and persistence: EEPROM contents are platform firmware/hardware state; decoded resources persist in kernel device/resource structures. Dependencies and integration: used by EISA bus probing and resource assignment.

Risks and test signals: structure packing or endian mistakes misroute IRQ/DMA/IO ranges. Test by decoding known EEPROM dumps and comparing registered resources to firmware setup screens.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/eisa_eeprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/elf.h

Purpose: defines PA-RISC ELF ABI constants, relocation behavior, register sets, core-dump layout, auxiliary vector handling, and personality selection.

Important APIs/types/functions: exports `ELF_ARCH`, `ELF_CLASS`, `ELF_DATA`, `ELF_PLAT_INIT`, `ELF_HWCAP`, `elf_check_arch`, `elf_greg_t`, `elf_gregset_t`, `ELF_NGREG`, `ELF_CORE_COPY_REGS`, and compat-related definitions.

Control flow: binfmt_elf validates PA-RISC binaries, initializes registers and stack ABI state, emits core dumps, and selects 32-bit or 64-bit behavior from ELF class/personality.

State and persistence: defines user-visible process and core-file ABI state. Dependencies and integration: works with `processor.h`, `ptrace.h`, uapi ELF definitions, and signal/syscall paths.

Risks and test signals: ABI drift breaks program startup, dynamic linking, or core analysis. Test with native and compat ELF execution, core dumps, auxv inspection, and ptrace register validation.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/extable.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/extable.h

Purpose: defines PA-RISC exception-table entry layout and fixup sorting/search semantics.

Important APIs/types/functions: declares `struct exception_table_entry`, `ARCH_HAS_RELATIVE_EXTABLE`, fixup address accessors, and exception-table helper hooks.

Control flow: fault handlers search exception tables after recoverable faults, find the fixup target, and redirect instruction execution.

State and persistence: exception table entries persist in kernel ELF sections. Dependencies and integration: used by uaccess, copy routines, module loading, and generic extable code.

Risks and test signals: wrong relative offset handling causes recoverable user-copy faults to oops. Test with fault-injection in `copy_to_user`/`copy_from_user`, module extables, and sorted-section checks.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/extable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/fixmap.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/fixmap.h

Purpose: defines PA-RISC fixed virtual mapping slots used for early boot, I/O, and architecture-specific permanent mappings.

Important APIs/types/functions: declares fixed-address indices, `FIXADDR_TOP`, `FIXADDR_SIZE`, `__fix_to_virt`, `__virt_to_fix`, and `set_fixmap` integration.

Control flow: early or low-level code selects a fixed slot, installs a PTE, uses the stable virtual address, and later clears or reuses the slot when appropriate.

State and persistence: fixmap PTEs persist in kernel page tables while active. Dependencies and integration: included by `pgtable.h` and early ioremap/memory setup.

Risks and test signals: overlapping or out-of-range slots corrupt fixed mappings. Test with boot-time fixmap assertions, early ioremap users, and page-table dumps.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/fixmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/floppy.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/floppy.h

Purpose: supplies PA-RISC architecture glue for the legacy floppy driver, including DMA, virtual DMA, and platform I/O access assumptions.

Important APIs/types/functions: defines floppy DMA setup/teardown helpers, virtual DMA hooks, request/free DMA wrappers, and architecture-specific constants consumed by the generic floppy driver.

Control flow: the floppy driver requests DMA, programs controller transfers, handles virtual DMA fallbacks where required, and performs I/O through PA-RISC accessors.

State and persistence: DMA channel ownership and floppy controller state persist during transfers. Dependencies and integration: integrates with `dma.h`, `io.h`, SuperIO/legacy IRQ routing, and the generic floppy driver.

Risks and test signals: legacy DMA assumptions are fragile on non-PC PA-RISC hardware. Test with build coverage, floppy probe/no-probe boot paths, and real hardware transfer tests if available.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/floppy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/ftrace.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/ftrace.h

Purpose: defines PA-RISC ftrace integration points and call-site patching constraints.

Important APIs/types/functions: declares `MCOUNT_INSN_SIZE`, graph tracing support, `return_address`/ftrace frame details, and architecture hooks used by dynamic ftrace.

Control flow: ftrace records call sites, patches branch/call instructions through text-patching code, and optionally redirects returns for function graph tracing.

State and persistence: patched text and tracing metadata persist until tracing is disabled or repatched. Dependencies and integration: depends on text patching, unwinding, module loading, and compiler instrumentation.

Risks and test signals: bad instruction-size or return-address assumptions crash traced functions. Test with function and graph tracing, module tracepoints, and objdump validation of patched call sites.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/ftrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/futex.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/futex.h

Purpose: implements PA-RISC futex atomic operations used by the userspace locking ABI.

Important APIs/types/functions: defines architecture futex operations such as atomic op-in-user and compare-exchange-in-atomic helpers, wired into generic futex code.

Control flow: futex code performs user-memory atomic reads/modifies under fault handling, returns old values or comparison results, and falls back through exception tables on bad user addresses.

State and persistence: modifies userspace futex words and may observe task wait queues managed by generic futex code. Dependencies and integration: depends on uaccess, exception tables, cmpxchg/atomic primitives, and syscall ABI.

Risks and test signals: user-access fault recovery and endian/width handling are critical for pthreads. Test with futex selftests, robust futexes, PI futexes where supported, and fault-injection on invalid addresses.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/grfioctl.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/grfioctl.h

Purpose: defines PA-RISC graphics framebuffer/graphics device ioctl numbers and small ABI structures.

Important APIs/types/functions: exports graphics ioctl constants and data layouts used by legacy PA-RISC graphics drivers and userspace tools.

Control flow: userspace issues ioctl calls; drivers decode these command numbers and copy the associated structures to or from userspace.

State and persistence: ioctl data may expose or update device mode/state; this header only defines ABI layouts. Dependencies and integration: consumed by graphics drivers and user-facing uapi compatibility code.

Risks and test signals: ioctl number or structure layout changes break legacy userspace. Test with header install checks, graphics driver build coverage, and ioctl ABI comparison.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/grfioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/hardirq.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/hardirq.h

Purpose: defines PA-RISC hard IRQ accounting and per-CPU interrupt state integration.

Important APIs/types/functions: provides `ack_bad_irq`, IRQ stack/accounting definitions, and includes generic hardirq helpers.

Control flow: low-level interrupt handlers update per-CPU counts and call generic interrupt dispatch; bad IRQs are reported through the architecture hook.

State and persistence: per-CPU IRQ counters and nesting state persist across interrupt handling. Dependencies and integration: used by irq core, `/proc/interrupts`, and PA-RISC interrupt entry code.

Risks and test signals: accounting mistakes hide interrupt storms or break preemption state. Test with timer/IPI/device interrupts and procfs interrupt count inspection.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/hardirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/hardware.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/hardware.h

Purpose: defines PA-RISC hardware inventory abstractions and constants used to describe firmware-discovered devices.

Important APIs/types/functions: provides hardware type/version constants, `enum cpu_type`, device ID/class helpers, and declarations tying firmware inventory to Linux device structures.

Control flow: boot firmware probing records hardware identity; platform and bus drivers match these IDs to initialize CPUs, buses, I/O adapters, and legacy devices.

State and persistence: discovered hardware records persist in `struct parisc_device` and CPU information. Dependencies and integration: used by PDC probing, processor setup, parisc-device bus code, and platform drivers.

Risks and test signals: wrong ID classification causes driver binding failures or wrong CPU capability selection. Test by comparing boot inventory logs across PA-RISC models.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/hardware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/hash.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/hash.h

Purpose: implements PA-RISC hashing helpers used by memory-management and architecture code, including space-ID or address hash transformations.

Important APIs/types/functions: exports inline hash/mixing helpers and constants used to derive architecture-specific hash values.

Control flow: callers pass addresses or IDs through deterministic mixing functions to select buckets or hardware-friendly hash values.

State and persistence: stateless computation. Dependencies and integration: used by MM, cache/TLB, and possibly page-table or context allocation code.

Risks and test signals: poor or incompatible hashing can degrade lookup distribution or conflict with hardware assumptions. Test with compile coverage and targeted unit checks for known input/output values if modified.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/hugetlb.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/hugetlb.h

Purpose: supplies PA-RISC hugepage hooks to generic hugetlb code.

Important APIs/types/functions: defines architecture helpers for huge PTE access, hugepage flush/update behavior, and generic hugetlb integration points.

Control flow: hugetlb code allocates huge mappings, updates PTEs with PA-RISC flags, and flushes TLB/cache entries as required.

State and persistence: huge PTEs persist in process page tables and TLBs. Dependencies and integration: depends on `pgtable.h`, `page.h`, and generic hugetlb mm code.

Risks and test signals: flag conflicts with `_PAGE_HUGE` or special bits can corrupt mappings. Test with hugetlb selftests, mmap/munmap, fork, and page-fault handling on huge pages.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/hugetlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/io.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/io.h

Purpose: defines PA-RISC memory-mapped and port I/O accessors, address translation for I/O spaces, raw/relaxed read-write helpers, and string I/O operations.

Important APIs/types/functions: includes `ioremap` declarations, `readb/readw/readl/readq`, `writeb/writew/writel/writeq`, raw variants, `inb/outb` style port helpers, `virt_to_phys`-related I/O conversions, and memcpy-to/from-io helpers.

Control flow: drivers map device resources, then access registers through ordered PA-RISC I/O primitives that handle endian, barriers, and platform address spaces.

State and persistence: device registers and I/O mappings persist outside normal RAM. Dependencies and integration: integrates with PCI/LBA, SBA IOMMU, generic io APIs, and device drivers.

Risks and test signals: wrong endian/order semantics break device drivers. Test with PCI enumeration, UART/network/storage MMIO access, sparse `__iomem` checks, and DMA/MMIO ordering tests.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/irq.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/irq.h

Purpose: defines PA-RISC interrupt numbering limits and architecture IRQ initialization hooks.

Important APIs/types/functions: declares IRQ count constants, `irq_canonicalize`, and architecture IRQ initialization/dispatch functions used by generic irq core.

Control flow: platform setup initializes interrupt controllers and maps firmware/device IRQs into Linux IRQ numbers; runtime handlers dispatch through generic irq_descs.

State and persistence: IRQ mappings and controller state persist after boot. Dependencies and integration: used by IOSAPIC, SuperIO, SMP IPI, and generic interrupt code.

Risks and test signals: IRQ-number mismatches cause lost or misdelivered interrupts. Test with timer, IPI, PCI device, and legacy IRQ delivery.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/irqflags.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/irqflags.h

Purpose: implements PA-RISC local interrupt enable/disable/save/restore primitives.

Important APIs/types/functions: exports raw local IRQ helpers around control register or PSW interrupt bits, consumed by generic `local_irq_*` APIs.

Control flow: callers save current flags, disable interrupts for critical sections, and restore the prior state; low-level assembly manipulates PA-RISC interrupt mask state.

State and persistence: CPU-local interrupt-enable state persists until changed. Dependencies and integration: used by spinlocks, atomics, scheduler, interrupt entry/exit, and tracing.

Risks and test signals: incorrect flag restoration deadlocks or permits reentrancy. Test with lockdep, IRQ-off tracing, timer interrupt stress, and nested critical sections.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/irqflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/jump_label.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/jump_label.h

Purpose: provides PA-RISC static key/jump-label instruction encoding and patch hooks.

Important APIs/types/functions: defines jump-label NOP/branch encoding helpers and `arch_static_branch`/`arch_static_branch_jump` behavior for generic static keys.

Control flow: code initially executes a NOP or branch; when a static key changes, text-patching code rewrites the instruction to flip fast-path control flow.

State and persistence: patched instructions persist in kernel text. Dependencies and integration: depends on `text-patching.h`, alternatives, cache coherency, and generic jump-label code.

Risks and test signals: branch displacement or patching mistakes corrupt hot paths. Test with static key selftests, cacheflush/jump-label toggling, and objdump of generated sites.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/jump_label.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/kbdleds.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/kbdleds.h

Purpose: declares PA-RISC keyboard LED defaults or hooks for console keyboard support.

Important APIs/types/functions: exports keyboard LED constants/macros consumed by generic keyboard code.

Control flow: keyboard/VT code reads the architecture default when initializing LED state.

State and persistence: LED state is ultimately device state; the header stores no runtime state. Dependencies and integration: integrates with console keyboard and legacy input support.

Risks and test signals: low risk; wrong defaults only affect initial keyboard LED behavior. Test with keyboard/VT build coverage and boot on systems with legacy keyboard hardware.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/kbdleds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/kexec.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/kexec.h

Purpose: defines PA-RISC kexec limits and hooks for loading and entering a replacement kernel.

Important APIs/types/functions: declares architecture memory limits, page constraints, and machine_kexec-related structures or prototypes.

Control flow: kexec validates target segments, prepares control code, shuts down devices/interrupts, and transfers execution to the new kernel image.

State and persistence: loaded kexec segments persist in reserved memory until executed or replaced. Dependencies and integration: generic kexec, crash dump, firmware/boot ABI, and cache/TLB shutdown paths.

Risks and test signals: address or cache mistakes fail only during reboot/crash paths. Test with `kexec -l/-e`, crash kernel loading if supported, and segment-boundary validation.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/kexec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/kfence.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/kfence.h

Purpose: supplies PA-RISC KFENCE integration, especially page protection/cache behavior for guarded allocations.

Important APIs/types/functions: defines architecture hooks for KFENCE pool setup and PTE protection changes.

Control flow: KFENCE allocates guarded pages and uses PA-RISC page-table operations to protect/unprotect guard regions around sampled allocations.

State and persistence: guard-page PTE state persists while KFENCE objects are active. Dependencies and integration: uses pgtable/cacheflush behavior and generic KFENCE.

Risks and test signals: missing TLB/cache flushes can let invalid accesses pass or fault incorrectly. Test with KFENCE selftests, sampled allocation faults, and SMP TLB shootdown coverage.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/kfence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/kgdb.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/kgdb.h

Purpose: defines PA-RISC KGDB register layout and breakpoint integration.

Important APIs/types/functions: exports `BREAK_INSTR_SIZE`, breakpoint instruction encoding, `NUMREGBYTES`, register numbering/layout helpers, and kgdb trap declarations.

Control flow: KGDB inserts breakpoints, trap handling captures PA-RISC registers into the KGDB packet layout, and remote debugging commands restore or inspect state.

State and persistence: breakpoint-patched text and captured register packets persist during debugging sessions. Dependencies and integration: trap handling, ptrace register layout, text patching, and kgdb core.

Risks and test signals: wrong register packet layout makes remote debugging unsafe. Test with kgdb break/continue, register read/write, and single-step where supported.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/kgdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/kprobes.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/kprobes.h

Purpose: defines PA-RISC kprobes instruction slot, breakpoint, and per-probe architecture state.

Important APIs/types/functions: provides `struct arch_specific_insn`, `struct prev_kprobe`, breakpoint constants, `flush_insn_slot`, and architecture handlers for probe preparation and single stepping.

Control flow: kprobes copies an instruction to a slot, patches the original site with a break, handles the trap, executes or emulates the original instruction, then resumes.

State and persistence: probe metadata and patched instructions persist while probes are registered. Dependencies and integration: trap code, instruction decoder, cacheflush, and text patching.

Risks and test signals: branch delay/nullification and PA-RISC instruction semantics make probe emulation delicate. Test with kprobe selftests on branches, calls, and module text.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/kprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/ldcw.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/ldcw.h

Purpose: defines the PA-RISC `ldcw` lock primitive and alignment helpers used by spinlocks and low-level atomic serialization.

Important APIs/types/functions: exports `__ldcw`, `LDCW_ALIGN`, lock-value helpers, and architecture-specific inline assembly for load-and-clear-word.

Control flow: locking code repeatedly executes `ldcw` on an aligned word until it obtains the lock value, with barriers around acquisition and release.

State and persistence: lock words in memory persist as synchronization state. Dependencies and integration: used by `spinlock.h`, atomic hash locks, and any PA-RISC low-level lock users.

Risks and test signals: PA-RISC requires strict alignment for `ldcw`; misalignment can break all locking. Test with lock alignment assertions, SMP stress, and lockdep.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/ldcw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/led.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/led.h

Purpose: declares PA-RISC chassis/front-panel LED interfaces used for boot, panic, and diagnostic indicators.

Important APIs/types/functions: exports LED state constants and functions such as LED initialization and update hooks consumed by platform code.

Control flow: platform initialization registers LED support; status paths update display patterns for activity, panic, or heartbeat where hardware exists.

State and persistence: LED pattern state persists in device registers and possibly software shadow variables. Dependencies and integration: integrates with PDC/chassis code, procfs/status reporting, and platform drivers.

Risks and test signals: mostly diagnostic, but wrong register access can affect platform firmware interfaces. Test with LED-enabled hardware, boot/panic indication, and no-op behavior on systems without LEDs.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/led.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/linkage.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/linkage.h

Purpose: provides PA-RISC linkage and symbol annotation macros for assembly/C ABI boundaries.

Important APIs/types/functions: defines architecture-specific `ENTRY`, `END`, alignment, and calling-convention annotations layered on generic linkage.

Control flow: assembly files use these macros to expose functions with correct symbol type, alignment, and unwind/linker metadata.

State and persistence: no runtime state; affects ELF symbol table and code layout. Dependencies and integration: used by boot, syscall, trap, and library assembly routines.

Risks and test signals: bad linkage annotations break kallsyms, ftrace, unwinding, or module relocation. Test through objdump/readelf symbol inspection and all assembly builds.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/linkage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/mman.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/mman.h

Purpose: defines PA-RISC memory-management flags and maps generic mmap/mprotect constants to architecture ABI expectations.

Important APIs/types/functions: includes uapi mman definitions and architecture overrides such as executable/read implementation details.

Control flow: syscall code validates and applies mmap/mprotect flags using these constants.

State and persistence: mappings persist in process VMAs and page tables. Dependencies and integration: userspace ABI, mm subsystem, ELF loader, and signal stack setup.

Risks and test signals: ABI flag changes break userspace. Test mmap/mprotect syscall suites, executable mappings, and header ABI comparisons.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/mmu.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/mmu.h

Purpose: defines the PA-RISC MMU context type used by each process address space.

Important APIs/types/functions: provides `mm_context_t`, primarily carrying the PA-RISC space ID and related context data.

Control flow: context allocation assigns a space ID; context switch and TLB flush code loads that ID into space registers and TLB purge operations.

State and persistence: `mm_context_t` persists in `mm_struct` for the life of an address space. Dependencies and integration: used by `mmu_context.h`, `pgtable.h`, processor setup, and fault/TLB handlers.

Risks and test signals: incorrect context state causes cross-process address aliasing. Test with fork/exec stress, ASID/space-ID recycling, and TLB flush tests.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/mmu_context.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/mmu_context.h

Purpose: implements PA-RISC MMU context lifecycle and space-ID switching.

Important APIs/types/functions: defines `init_new_context`, `destroy_context`, `switch_mm`, `activate_mm`, `enter_lazy_tlb`, and related helpers around `alloc_sid`/`free_sid`.

Control flow: new address spaces receive a space ID; context switches update current CPU state and space registers; teardown returns IDs for reuse.

State and persistence: process `mm->context.space_id` and CPU active-mm state persist across scheduling decisions. Dependencies and integration: depends on cache/SID management, TLB flush routines, scheduler, and generic mm.

Risks and test signals: stale or reused space IDs without proper flushes can expose another process's memory. Test with context-switch stress, fork/exit loops, and TLB shootdown validation.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/mmzone.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/mmzone.h

Purpose: provides PA-RISC NUMA/mmzone integration stubs.

Important APIs/types/functions: includes or defines minimal zone/node helpers required by generic memory management for PA-RISC configurations.

Control flow: generic page allocator code includes this header while computing zones and nodes; PA-RISC mostly relies on generic behavior here.

State and persistence: no private state; memory zones live in generic mm structures. Dependencies and integration: page allocator, sparsemem, and NUMA configuration.

Risks and test signals: low risk unless PA-RISC memory topology changes. Test with memory hotplug/sparsemem build coverage and boot memory maps.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/mmzone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/module.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/module.h

Purpose: defines PA-RISC module architecture metadata and relocation requirements.

Important APIs/types/functions: provides `struct mod_arch_specific` fields and module PLT/stub limits or helpers used by module loader code.

Control flow: module loading validates PA-RISC relocations, prepares architecture-specific stubs/descriptors if required, and patches module text/data.

State and persistence: module arch metadata persists while a module is loaded. Dependencies and integration: integrates with ELF relocation code, ftrace/kprobes, alternatives, and module memory permissions.

Risks and test signals: relocation or descriptor mistakes break loadable modules. Test with module load/unload, far-call relocations, ftrace-enabled modules, and `modpost` checks.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/page.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/page.h

Purpose: defines PA-RISC page size, page alignment, physical/virtual conversion, page table entry base types, and memory layout constants.

Important APIs/types/functions: exports `PAGE_SHIFT`, `PAGE_SIZE`, `PAGE_MASK`, `__PAGE_OFFSET`, `PAGE_OFFSET`, `__pa`, `__va`, `virt_to_page`, `clear_page`, `copy_page`, and typedefs for PTE/PMD/PGD-related values.

Control flow: MM code uses these macros for address translation, page allocation, page-table construction, and low-level copying/clearing.

State and persistence: no private state, but constants define every process and kernel mapping. Dependencies and integration: used by boot, pgtable, cache, DMA, and virtually all mm code.

Risks and test signals: address conversion errors are catastrophic. Test with memory map validation, high-memory/64-bit builds, page allocator tests, and boot with varied RAM sizes.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/parisc-device.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/parisc-device.h

Purpose: defines the PA-RISC firmware-discovered device model used by architecture bus drivers.

Important APIs/types/functions: provides `struct parisc_device`, `struct parisc_driver`, `struct parisc_device_id`, matching helpers, and registration declarations.

Control flow: firmware inventory creates `parisc_device` objects; drivers register ID tables and probe matching devices.

State and persistence: device and driver records persist in the Linux device model. Dependencies and integration: used by native PA-RISC bus, PDC inventory, SBA/LBA/CPU/platform drivers.

Risks and test signals: ID matching or resource fields must remain ABI-stable for in-tree drivers. Test with boot inventory, driver binding logs, and module autoload/probe coverage.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/parisc-device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/parport.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/parport.h

Purpose: provides PA-RISC parallel-port discovery hooks for the generic parport subsystem.

Important APIs/types/functions: declares architecture parport initialization or maps to generic no-op behavior depending on platform support.

Control flow: parport core calls architecture probing to register available parallel ports, often through SuperIO/legacy resources.

State and persistence: registered parport devices persist in the device model. Dependencies and integration: integrates with SuperIO, PCI/legacy I/O, and printer/parallel drivers.

Risks and test signals: resource or IRQ mismatch breaks legacy parallel devices. Test with parport build/probe and SuperIO systems.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/parport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/pci.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/pci.h

Purpose: defines PA-RISC PCI host-bridge integration, DMA addressing policy, bus/resource helpers, and platform-specific PCI data.

Important APIs/types/functions: provides `struct pci_hba_data`, PCI DMA/resource constants, `pcibios_*` hooks, `PCI_DMA_BUS_IS_PHYS`, and helpers for bus-to-resource mapping.

Control flow: PCI initialization discovers LBA/SBA host bridges, assigns resources, configures IRQs, and supplies DMA/IOMMU behavior to devices.

State and persistence: PCI host bridge data, bus resources, and DMA masks persist after enumeration. Dependencies and integration: ties together `ropes.h`, `io.h`, DMA mapping, IOSAPIC, and generic PCI core.

Risks and test signals: wrong bus/resource translation breaks all PCI devices. Test with PCI enumeration, DMA-capable devices, MSI/IRQ routing where supported, and config-space access.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/pdc.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/pdc.h

Purpose: defines core PA-RISC Processor Dependent Code firmware interface constants, status codes, structures, and call declarations.

Important APIs/types/functions: exports PDC procedure numbers, return codes, model/cache/BTLB/IO descriptors, and firmware helper prototypes used for console, inventory, cache, and boot services.

Control flow: early boot and platform code issue PDC calls with function/subfunction selectors, parse returned structures, and use the data to initialize CPU, memory, console, and devices.

State and persistence: firmware data persists in boot-time kernel structures; firmware itself owns platform state. Dependencies and integration: used by boot/compressed firmware code, processor setup, cache probing, device inventory, and PALO boot interactions.

Risks and test signals: structure layout and calling ABI are firmware contracts. Test on multiple PA-RISC firmware revisions, validate boot logs, and compare PDC-reported model/cache/device data.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/pdc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/pdc_chassis.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/pdc_chassis.h

Purpose: defines PDC chassis status, warning, LED, and display interfaces for PA-RISC systems.

Important APIs/types/functions: includes chassis message constants, LCD/LED structures, status enums, and function declarations for warning, display, and chassis log interactions.

Control flow: platform or panic paths call PDC chassis services to report boot state, warnings, panic codes, or front-panel display text.

State and persistence: chassis logs and display/LED state may persist in firmware or front-panel hardware until overwritten. Dependencies and integration: used by LED support, platform diagnostics, PDC firmware calls, and proc/status reporting.

Risks and test signals: firmware calls may differ across models; bad lengths or encodings can fail silently. Test with model-specific chassis status output and graceful fallback on systems without chassis display support.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/pdc_chassis.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/pdcpat.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/pdcpat.h

Purpose: defines PA-RISC PAT firmware extensions for cell-based 64-bit systems, including interrupt routing, cell/module information, memory descriptors, nonvolatile memory, protection domains, and TOC registration.

Important APIs/types/functions: exports `PDC_PAT_*` procedure/subfunction constants, capability bits, memory descriptor values, `is_pdc_pat()`, `pdc_pat_get_irt_size()`, `pdc_pat_get_irt()`, and PAT return structures such as cell, CPU, and memory PDT info.

Control flow: 64-bit platform setup queries PAT capabilities, retrieves interrupt routing and memory tables, registers TOC vectors, and configures cell/module resources.

State and persistence: PAT-reported topology and memory state persist in kernel platform data; some calls mutate firmware TOC/NVRAM state. Dependencies and integration: depends on `pdc.h`, 64-bit configuration, IOSAPIC, memory discovery, and SMP/cell setup.

Risks and test signals: PAT is firmware ABI-heavy; wrong structure widths break large systems. Test on PAT and non-PAT machines, interrupt routing validation, memory table parsing, and 32-bit fallback behavior.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/pdcpat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/perf.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/perf.h

Purpose: defines PA-RISC CPU performance-monitoring register layout and event selectors for low-level perf support.

Important APIs/types/functions: exports performance counter control/status constants, CPU event encodings, and helper declarations used by perf and platform code.

Control flow: perf setup programs counter selectors, enables counting, handles overflow interrupts, and reads counter values.

State and persistence: hardware performance counters and control registers persist until reprogrammed. Dependencies and integration: integrates with `perf_event`, interrupt handling, processor identification, and control-register accessors.

Risks and test signals: wrong event encodings produce misleading metrics or interrupt storms. Test with `perf stat`, overflow sampling, CPU model gating, and counter reset/readback checks.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/perf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/perf_event.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/perf_event.h

Purpose: connects PA-RISC to the generic perf event framework.

Important APIs/types/functions: declares architecture perf initialization hooks or maps to generic defaults when hardware support is limited.

Control flow: perf core calls architecture hooks during event creation, scheduling, reading, and overflow handling.

State and persistence: active perf events and hardware counter assignments persist while events are scheduled. Dependencies and integration: depends on `perf.h`, IRQ handling, and generic perf_event code.

Risks and test signals: incomplete hooks should fail cleanly rather than expose bogus counters. Test with perf list/stat/record and unsupported-event error paths.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/pgalloc.h

Purpose: supplies PA-RISC page-table allocation and freeing helpers for generic memory management.

Important APIs/types/functions: defines `pgd_alloc/free`, `pmd_alloc_one/free`, `pte_alloc_one`, `pte_free`, and page-table constructor/destructor behavior based on configured page-table levels.

Control flow: mm creates page-table pages during process creation and faults, initializes them, and frees them during unmap/exit.

State and persistence: allocated page-table pages persist in process address spaces. Dependencies and integration: uses `pgtable.h`, generic page allocator, and TLB/cache flushing.

Risks and test signals: wrong allocation order or missing initialization corrupts page walks. Test with fork/exit stress, mmap/munmap, page-table debug, and 2-level/3-level builds.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/pgtable.h

Purpose: defines the PA-RISC page-table format, page protection bits, address-space geometry, TLB purge serialization, and PTE/PMD/PGD manipulation helpers.

Important APIs/types/functions: includes `purge_tlb_start/end`, `purge_tlb_entries`, `set_pte`, page-table level sizing macros, `_PAGE_*` bit definitions, `PTE_SHIFT`, `PFN_PTE_SHIFT`, protection presets, `pte_*` helpers, and swap/hugepage special-bit handling.

Control flow: fault handlers and mm code build PTEs, update entries with barriers, serialize TLB broadcasts when required, and use PA-RISC `pdtlb/pitlb` instructions to purge stale translations.

State and persistence: PTEs/PMDs/PGDs persist as the authoritative virtual-memory state; TLBs cache derived state. Dependencies and integration: depends on `page.h`, `fixmap.h`, cache/processor helpers, and generic pgtable layers.

Risks and test signals: comments warn TLB miss handlers assume specific bit ordering, so flag changes are high risk. Test with page-fault, COW, swap, hugepage, SMP TLB shootdown, and memory-protection selftests.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/prefetch.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/prefetch.h

Purpose: provides PA-RISC prefetch and prefetch-for-write hints.

Important APIs/types/functions: defines `ARCH_HAS_PREFETCH`, `prefetch()`, `ARCH_HAS_PREFETCHW`, and `prefetchw()` using PA-RISC load/prefetch-style instructions.

Control flow: generic and driver code emits hints before anticipated memory access; CPU may fetch cachelines earlier without changing program semantics.

State and persistence: no architectural state beyond cache effects. Dependencies and integration: included by processor and performance-sensitive kernel code.

Risks and test signals: hints must be safe for any valid kernel address and not fault unexpectedly. Test with build coverage and stress paths that use list/hash prefetching.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/prefetch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/processor.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/processor.h

Purpose: defines PA-RISC CPU and thread state, task address-space limits, mmap layout hooks, unaligned-access policy, and user-thread startup ABI.

Important APIs/types/functions: key definitions are `TASK_SIZE`, `DEFAULT_TASK_SIZE*`, `system_cpuinfo_parisc`, `cpuinfo_parisc`, `thread_struct`, `task_pt_regs`, unaligned-control flags, `INIT_THREAD`, `start_thread`, `release_thread`, and CPU identification globals.

Control flow: boot fills CPU info, scheduler stores task register state in `thread_struct`, exec uses `start_thread` to initialize PA-RISC user registers/space IDs/stack ABI, and prctl paths update unaligned-access behavior.

State and persistence: CPU info is global/per-CPU state; each task persists register and layout state in `thread_struct`. Dependencies and integration: ties together PDC, ptrace, ELF, MM, scheduler, and syscall return paths.

Risks and test signals: PA-RISC has unusual stack and argument ABI; errors break every exec. Test native/compat exec, mmap layout, unaligned access prctl, context switching, and ptrace register views.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/psw.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/psw.h

Purpose: defines PA-RISC Processor Status Word bits, kernel/user PSW masks, real-mode PSW setup, and C bitfield view of PSW state.

Important APIs/types/functions: exports `PSW_*`, `PSW_SM_*`, `KERNEL_PSW`, `REAL_MODE_PSW`, `USER_PSW_MASK`, `USER_PSW`, `struct pa_psw`, and `pa_psw(task)`.

Control flow: boot, trap return, signal, and exec code compose PSW values to enable/disable interrupts, data/address translation, wide mode, and user-visible condition bits.

State and persistence: PSW is live CPU state and saved in task/trap frames. Dependencies and integration: used by `head.S`, `assembly.h`, `processor.h`, `ptrace`, and trap return assembly.

Risks and test signals: wrong user/kernel masks expose privileged state or break wide/narrow execution. Test trap/syscall return, 32-bit/64-bit tasks, signal frames, and ptrace PSW reads/writes.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/psw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/ptrace.h

Purpose: defines PA-RISC ptrace/register inspection helpers used by tracing, profiling, and stack unwinding.

Important APIs/types/functions: provides `task_regs`, `user_mode`, `user_space`, `instruction_pointer`, `instruction_pointer_set`, `regs_return_value`, `regs_get_register`, `regs_query_register_offset/name`, `kernel_stack_pointer`, and stack helpers.

Control flow: ptrace, perf, kprobes, and exception code inspect or modify saved `pt_regs` fields through these helpers.

State and persistence: operates on saved task/trap register frames. Dependencies and integration: depends on `assembly.h`, uapi ptrace layout, and generic tracing/debug code.

Risks and test signals: IA queue low privilege bits make instruction-pointer masking important. Test ptrace, single-step/block-step, perf callchains, and kernel/user mode detection.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/ropes.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/ropes.h

Purpose: describes PA-RISC SBA/Ike/Astro/Pluto IOMMU and LBA PCI host bridge data structures and register offsets, historically named around chipset ropes.

Important APIs/types/functions: defines `struct ioc`, `struct sba_device`, `struct lba_device`, chipset ID helpers `IS_ASTRO/IS_IKE/IS_PLUTO/IS_ELROY/IS_MERCURY/IS_QUICKSILVER`, IOMMU page-directory constants, IOC/LMMIO/rope register offsets, and IOSAPIC registration declarations.

Control flow: PCI/IOMMU setup identifies chipset type, maps SBA/LBA registers, initializes IOC page directories/resource maps, routes PCI ropes, registers IOSAPICs, and serves DMA map/unmap requests.

State and persistence: `sba_list`, IOC resource maps, page directories, delayed unmap queues, and host-bridge data persist for the life of the system. Dependencies and integration: used by `drivers/parisc/sba_iommu.c`, LBA PCI, IOSAPIC, DMA mapping, and PCI resource code.

Risks and test signals: IOMMU page-size/resource-map mistakes cause device DMA memory corruption. Test PCI DMA, IOMMU unmap flushes, AGP/Pluto paths, and multi-IOC systems.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/ropes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/rt_sigframe.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/rt_sigframe.h

Purpose: defines the PA-RISC realtime signal-frame layout and sizing constants.

Important APIs/types/functions: provides `struct rt_sigframe`, `SIGFRAME`, `FUNCTIONCALLFRAME`, and `PARISC_RT_SIGFRAME_SIZE`.

Control flow: signal delivery builds this frame on the user stack; `rt_sigreturn` validates and consumes it to restore context.

State and persistence: signal frames persist on user stacks while handlers run. Dependencies and integration: used by signal setup/return, ucontext/sigcontext ABI, and compat signal code.

Risks and test signals: frame size/alignment mistakes break signal handlers and unwinding. Test realtime signals, alternate stacks, nested handlers, and sigreturn fault paths.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/rt_sigframe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/runway.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/runway.h

Purpose: defines small register offsets for PA-RISC Runway bus status/debug access.

Important APIs/types/functions: exports `RUNWAY_STATUS` and `RUNWAY_DEBUG`.

Control flow: platform diagnostic code reads or writes these offsets relative to Runway bus control blocks.

State and persistence: accessed registers are hardware state; this header stores none. Dependencies and integration: used by Runway chipset/platform support.

Risks and test signals: incorrect offsets affect low-level hardware diagnostics. Test with build coverage and hardware readback on Runway systems.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/runway.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/seccomp.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/seccomp.h

Purpose: connects PA-RISC to generic seccomp definitions.

Important APIs/types/functions: includes `asm-generic/seccomp.h` and exports the architecture audit/seccomp mode constants expected by generic code.

Control flow: syscall entry checks seccomp state through generic code after architecture syscall number/argument extraction.

State and persistence: seccomp filters persist in task state; this header adds no private state. Dependencies and integration: used by syscall tracing/audit and BPF seccomp.

Risks and test signals: generic mapping must agree with PA-RISC syscall ABI. Test seccomp selftests, audit arch values, and filtered syscall argument extraction.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/seccomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/sections.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/sections.h

Purpose: extends generic section declarations with PA-RISC function descriptor and alternatives-section symbols.

Important APIs/types/functions: typedefs `func_desc_t` as `Elf64_Fdesc` on 64-bit and declares `__alt_instructions`/`__alt_instructions_end`.

Control flow: alternatives code walks the alternative instruction section; module/core code may use function descriptor typing for PA-RISC ABI support.

State and persistence: linker-defined section ranges persist in the kernel image. Dependencies and integration: depends on `elf.h`, generic sections, and `alternative.h`.

Risks and test signals: wrong section symbols prevent runtime patching. Test alternatives application, linker map inspection, and 64-bit function descriptor users.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/sections.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/serial.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/serial.h

Purpose: defines PA-RISC default serial baud-base constant.

Important APIs/types/functions: exports `BASE_BAUD` as `1843200 / 16`.

Control flow: serial drivers use this constant when initializing UART port timing unless platform data overrides it.

State and persistence: no software state; UART divisor programming persists in device registers. Dependencies and integration: consumed by 8250/serial platform setup.

Risks and test signals: wrong baud base causes console garbling. Test early and runtime serial console at standard baud rates.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/serial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/shmparam.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/shmparam.h

Purpose: defines PA-RISC System V shared-memory alignment requirements for aliasing caches.

Important APIs/types/functions: exports `SHMLBA` and `SHM_COLOUR`.

Control flow: SysV shared-memory attach code aligns requested addresses according to these constants to avoid cache aliasing problems.

State and persistence: shared-memory mappings persist in process VMAs and page tables. Dependencies and integration: used by IPC shm code and mmap layout.

Risks and test signals: insufficient alignment causes incoherent shared mappings. Test SysV shm attach at varied addresses and aliasing-cache data consistency.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/shmparam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/signal.h

Purpose: exposes PA-RISC signal ABI definitions to kernel code.

Important APIs/types/functions: includes `uapi/asm/signal.h` and, for kernel builds, `asm/sigcontext.h`.

Control flow: signal delivery and return code use the included constants and context layouts to build user-visible frames.

State and persistence: signal masks and frames persist in task/user-stack state. Dependencies and integration: signal core, compat signal handling, ptrace, and uapi headers.

Risks and test signals: ABI mismatch breaks signal handlers. Test signal selftests, header install, and 32/64-bit signal frame compatibility.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/smp.h

Purpose: declares PA-RISC SMP CPU mapping, boot rendezvous, IPI, and CPU hotplug hooks.

Important APIs/types/functions: exports `init_per_cpu`, PDC rendezvous constants, `cpu_number_map`, `cpu_logical_map`, `raw_smp_processor_id`, IPI send functions, `NO_PROC_ID`, `ANY_PROC_ID`, `__cpu_disable`, and `__cpu_die`.

Control flow: boot code initializes per-CPU state, firmware rendezvous starts secondary CPUs, IPIs deliver function calls/NOPs, and hotplug paths disable or wait for CPUs.

State and persistence: CPU maps, per-CPU thread info, pending IPI state, and CPU lifecycle state persist in scheduler/platform data. Dependencies and integration: firmware PDC, scheduler, interrupt/IPI code, and CPU hotplug core.

Risks and test signals: bad CPU numbering or rendezvous handling breaks SMP boot. Test SMP boot, IPI selftests, CPU hotplug, and `raw_smp_processor_id` debug checks.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/socket.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/socket.h

Purpose: provides PA-RISC socket flag ABI definitions while including the uapi socket constants.

Important APIs/types/functions: includes `uapi/asm/socket.h` and defines PA-RISC `SOCK_NONBLOCK` as `0x40000000`.

Control flow: socket syscalls translate user flags through these constants when creating or accepting sockets.

State and persistence: socket flags persist in file/socket state. Dependencies and integration: networking syscall layer and userspace ABI headers.

Risks and test signals: flag mismatch breaks nonblocking socket creation for PA-RISC userspace. Test socket/accept4 flag selftests and header ABI comparison.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/sparsemem.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/sparsemem.h

Purpose: defines PA-RISC sparsemem geometry.

Important APIs/types/functions: exports `MAX_PHYSMEM_BITS` and `SECTION_SIZE_BITS`.

Control flow: memory initialization divides physical memory into sparse sections using these constants.

State and persistence: section metadata persists in the sparsemem memory model. Dependencies and integration: mm initialization, memory hotplug, and page-to-section translations.

Risks and test signals: too-small limits hide RAM; wrong section size wastes memory or breaks pfn translation. Test boot with large memory maps and sparsemem debug checks.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/sparsemem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/special_insns.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/special_insns.h

Purpose: wraps PA-RISC privileged and special instructions for address probing, physical address lookup, control registers, and space registers.

Important APIs/types/functions: defines `lpa`, `lpa_user`, `prober_user`, control-register IDs `CR_EIEM`, `CR_CR16`, `CR_EIRR`, plus `mfctl`, `mtctl`, `get_eiem`, `set_eiem`, `mfsp`, and `mtsp`.

Control flow: low-level code invokes these inline assembly helpers to read/write CPU control state, test user addresses, and translate virtual addresses to physical addresses.

State and persistence: control and space register writes persist in CPU state until changed. Dependencies and integration: used by IRQ flags, TLB/cache management, uaccess, timers, and MMU context switching.

Risks and test signals: operand constraints and privilege assumptions are critical. Test syscall/uaccess probing, timer reads, interrupt mask changes, and context-switch space-register state.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/special_insns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/spinlock.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/spinlock.h

Purpose: implements PA-RISC raw spinlock and rwlock operations on top of the `ldcw` primitive.

Important APIs/types/functions: defines `arch_spin_val_check`, `arch_spin_is_locked`, `arch_spin_lock`, `arch_spin_unlock`, `arch_spin_trylock`, `arch_read_trylock`, `arch_write_trylock`, `arch_read_lock`, `arch_write_lock`, and unlock helpers.

Control flow: lock acquisition spins on an aligned lock word with PA-RISC load-and-clear semantics; rwlocks encode reader counts and writer state in the lock word.

State and persistence: lock words persist in shared kernel structures. Dependencies and integration: depends on barriers, `ldcw.h`, processor relax behavior, and spinlock type definitions.

Risks and test signals: fairness, alignment, and barrier behavior are SMP-critical. Test locktorture, rwlock stress, IRQ-safe locking, and lockdep.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/spinlock_types.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/spinlock_types.h

Purpose: defines PA-RISC raw spinlock and rwlock storage layouts and unlocked values.

Important APIs/types/functions: provides `arch_spinlock_t`, `arch_rwlock_t`, `__ARCH_SPIN_LOCK_UNLOCKED_VAL`, `SPINLOCK_BREAK_INSN`, and rwlock initializer constants.

Control flow: `spinlock.h` operations interpret these fields during lock/unlock/trylock paths.

State and persistence: lock structures persist wherever embedded in kernel objects. Dependencies and integration: used by generic lock initializers, lockdep, and PA-RISC spinlock operations.

Risks and test signals: initializer mismatch makes static locks start locked or corrupt. Test compile-time initializers, locktorture, and objdump/assert checks for lock alignment.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/spinlock_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/string.h

Purpose: advertises PA-RISC optimized string/memory routines to generic code.

Important APIs/types/functions: defines `__HAVE_ARCH_MEMSET`, declares `memset`, defines `__HAVE_ARCH_MEMCPY`, and declares `memcpy`.

Control flow: generic code links to architecture implementations instead of generic C versions for these operations.

State and persistence: functions mutate caller-provided memory only. Dependencies and integration: used by lib/string, boot, mm, and drivers.

Risks and test signals: optimized routines must handle overlap rules where applicable and all alignments. Test string/memcpy selftests, KASAN/KMSAN builds where possible, and early boot memory clearing.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/superio.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/superio.h

Purpose: defines PA-RISC SuperIO legacy device registers, IRQ routing constants, device structure, and helper declarations.

Important APIs/types/functions: exports PIC/SuperIO config register offsets, trigger/routing registers, legacy IRQ constants for USB/serial/parallel/floppy/IDE, `SUPERIO_NIRQS`, `struct superio_device`, `is_superio_device`, and `superio_fixup_irq`.

Control flow: PCI/legacy setup identifies SuperIO functions, programs or reads IRQ routing, and fixes PCI device IRQ lines through IOSAPIC integration.

State and persistence: SuperIO config registers and IRQ routing persist in hardware. Dependencies and integration: used by serial, parport, floppy, IDE, USB legacy support, and PCI fixup code.

Risks and test signals: wrong routing can make legacy devices unusable or share IRQs incorrectly. Test SuperIO probe logs, serial/floppy/parallel IRQ delivery, and PCI fixup paths.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/superio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/switch_to.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/switch_to.h

Purpose: defines the PA-RISC scheduler context-switch wrapper.

Important APIs/types/functions: declares `_switch_to(prev, next)` and defines `switch_to(prev, next, last)` to call the low-level implementation and return the previous task.

Control flow: the scheduler invokes `switch_to`; assembly/C low-level code saves current callee-saved state, loads next task state, and returns with `last` set.

State and persistence: task register state persists in `thread_struct` and kernel stacks. Dependencies and integration: scheduler core, processor/thread layout, and low-level context-switch assembly.

Risks and test signals: register-save mismatches corrupt tasks. Test scheduler stress, fork/exit loops, preemption, and FP/register preservation tests.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/switch_to.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/syscall.h

Purpose: provides PA-RISC syscall inspection and mutation helpers for tracing, seccomp, audit, and ptrace.

Important APIs/types/functions: defines `NR_syscalls`, `syscall_get_nr`, `syscall_set_nr`, `syscall_get_arguments`, `syscall_set_arguments`, `syscall_get_error`, `syscall_get_return_value`, `syscall_set_return_value`, `syscall_rollback`, and `syscall_get_arch`.

Control flow: tracing/seccomp code reads syscall number and args from `pt_regs`, may rewrite them, and later reads or sets the return value/error according to PA-RISC ABI.

State and persistence: operates on saved syscall register frames. Dependencies and integration: depends on uapi audit constants, compat, errnos, and ptrace helpers.

Risks and test signals: PA-RISC argument registers differ from many architectures; mistakes break tracing and seccomp. Test strace, seccomp user notification/filtering, ptrace syscall emulation, and compat syscalls.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/text-patching.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/text-patching.h

Purpose: declares PA-RISC kernel text patching functions used by alternatives, jump labels, ftrace, kprobes, and live instruction updates.

Important APIs/types/functions: declares `patch_text`, `patch_text_multiple`, `__patch_text`, and `__patch_text_multiple`.

Control flow: callers request one or more instruction writes; implementation handles permissions, atomicity expectations, and cache synchronization so CPUs execute the new instructions.

State and persistence: modifies kernel text, which persists until repatched or module unload. Dependencies and integration: used by alternatives, static keys, tracing, and probe subsystems.

Risks and test signals: text patching must synchronize I/D caches and avoid partially visible instructions. Test alternatives, ftrace, jump-label toggling, kprobe registration, and SMP patch stress.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/text-patching.h -->
