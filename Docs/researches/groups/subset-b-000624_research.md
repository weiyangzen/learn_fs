# Research Group: subset-b-000624

Grouped research for Alpha architecture boot, low-level synchronization, I/O, platform core, interrupt, DMA, ELF, and firmware interface files under the Ceph client Linux source tree. Each section preserves the original source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/Makefile -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/Makefile

This architecture Makefile defines the top-level Alpha kernel build contract. It forces static non-relaxed vmlinux linking, adds Alpha-specific check flags, disables floating-point register use with `-mno-fp-regs`, reserves register 8, optionally disables jump tables, and selects CPU tuning flags for EV56, PCA56/Polaris/SX164, EV6, EV67, or generic EV56/EV6 tuning. It also forces the assembler into EV6 mode so instructions such as BWX are not silently emulated for chipsets that require exact instruction support.

Important integration points are `libs-y += arch/alpha/lib/`, exported `LIBS_Y` for the boot Makefile, `boot := arch/alpha/boot`, and targets `boot`, `bootimage`, `bootpfile`, and `bootpzfile`. `archheaders` delegates syscall table generation to `arch/alpha/kernel/syscalls`.

The control flow is pure kbuild routing: the default target builds `arch/alpha/boot/vmlinux.gz` from `vmlinux`; image-specific targets recurse into `arch/alpha/boot`. No runtime state is persisted, but the selected `CONFIG_ALPHA_*` values persist into every object through compiler/assembler flags. Risks are mostly build regressions: incorrect CPU flags can emit instructions unsupported by older Alpha cores, while boot target dependencies must stay aligned with `arch/alpha/boot/Makefile`. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/boot/Makefile -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/boot/Makefile

This boot Makefile builds Alpha SRM and BOOTP boot artifacts from the linked kernel. It defines host tools `tools/mkbb` and `tools/objstrip`, raw/stripped kernel targets, compressed payloads, boot headers, and final images: `bootimage`, `bootpfile`, `bootpzfile`, and `vmlinux.gz`.

The key build APIs are kbuild `if_changed` commands for `gzip`, `strip`, `objstrip`, and `ld`; generated size headers `ksize.h` and `kzsize.h`; and object sets `OBJ_bootlx`, `OBJ_bootph`, and `OBJ_bootpzh`. `INITRD` is optional and, when set, its size is added to generated headers and its bytes are appended to BOOTP images.

Control flow strips `vmlinux` to `vmlinux.nh`, compresses where needed, creates raw bootloader/header binaries with `objstrip`, concatenates header plus payload, and for SRM `bootimage` calls `mkbb` to install boot block metadata. State exists only as generated artifacts under the object tree. Risks include stale size headers, missing initrd files, linker-script mismatch, and `objstrip` assumptions about one program segment/OMAGIC layout. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/boot/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/boot/bootp.c -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/boot/bootp.c

`bootp.c` is the uncompressed BOOTP loader for Linux/Alpha. It runs from the SRM-loaded BOOTP image, switches PALcode to OSF/1 mode, copies the kernel payload from the image to `START_ADDR`, optionally moves an initrd, prepares the zero page with boot arguments/initrd metadata, and jumps into the kernel.

Important routines are `find_pa`, `pal_init`, `load`, `runkernel`, and `start_kernel`. `pal_init` constructs a temporary `pcb_struct`, locates its physical address via the virtual page table at `VPTB`, invokes `switch_to_osf_pal`, records the PAL revision in the HWRPB per-CPU area, and invalidates the TB. `start_kernel` validates 8 KiB pages and the expected VPTB address, computes page-aligned `initrd_start`, moves the stack via assembly `move_stack`, reads `ENV_BOOTED_OSFLAGS`, then performs a two-step copy through `START_ADDR + 4*KERNEL_SIZE` to avoid SRM virtual/physical overlap.

State is firmware-facing: `hwrpb`, the dummy PCB, `ZERO_PGE`, and optional initrd slots at `ZERO_PGE+256`. After the copy starts, the code intentionally avoids callbacks/prints because stack/image overlap can corrupt the payload. Risks are fixed placement arithmetic, stack relocation, exact `KERNEL_SIZE`, and assumptions about SRM loading at `BOOT_ADDR`. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/boot/bootp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/boot/bootpz.c -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/boot/bootpz.c

`bootpz.c` is the compressed BOOTP loader. It combines PAL initialization with overlap-aware decompression so the gzip payload can be inflated without overwriting the loader, SRM-loaded data, stack, final kernel image, or optional initrd.

Important APIs are `find_pa`, `check_range`, `pal_init`, `decompress_kernel`, `move_stack`, `memcpy`, and `runkernel`. The file defines virtual BOOTP image ranges, final kernel ranges, copy/decompression ranges, and initrd placement macros derived from `KERNEL_SIZE`, `KERNEL_Z_SIZE`, `REAL_INITRD_SIZE`, and `MALLOC_AREA_SIZE`.

Control flow records SP on entry, validates HWRPB page size and VPTB, switches PALcode, captures boot flags, checks whether bootstrapper pages overlap the final kernel range, decides whether decompression must happen in a copy area, slides that copy area page by page until it no longer overlaps the SRM data range, inflates the kernel, moves initrd and possibly the kernel, writes the zero page, then jumps to `START_ADDR`. Persistent state is limited to firmware/HWRPB fields and zero-page handoff data. Risks are high: the overlap logic relies on Alpha page-table interpretation, the stack address is virtual, debug printing can corrupt the image, and `__kmalloc` is a dummy that should never be used. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/boot/bootpz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/boot/head.S -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/boot/head.S

`head.S` is the assembly entry and PAL helper layer for the Alpha bootloader objects. `__start` initializes GP relative to the current PC, calls C `start_kernel`, and halts through PAL if it returns.

Exported entry points include `wrent`, `wrkgp`, `switch_to_osf_pal`, `tbi`, `halt`, and `move_stack`. `switch_to_osf_pal` saves integer registers on the current stack, stores the current KSP into the PCB supplied by C, sets PAL arguments, calls `PAL_swppal`, restores registers on return, and returns the PAL status. `move_stack` copies the active 8 KiB stack page to a new page preserving the current offset, then switches `$30`.

The file has no persistent storage; it mutates PAL state, the PCB, and stack pointer. Integration is direct with `main.c`, `bootp.c`, and `bootpz.c`, which declare these helpers. Risks are ABI-level: register save layout, stack-page size, PAL calling convention, and GP setup must match the Alpha ABI and linker script. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/boot/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/boot/main.c -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/boot/main.c

`main.c` is the classic SRM disk bootloader for Linux/AXP. It opens the SRM boot device, reads the uncompressed kernel from the boot medium, places boot flags in the zero page, and transfers control to the kernel entry.

Important functions are `find_pa`, `pal_init`, `openboot`, `close`, `load`, `runkernel`, and `start_kernel`. `load` reads the kernel using SRM `callback_read`, with LBN offset based on the bootloader size rounded to 512-byte sectors. `runkernel` sets `$30` to `PAGE_SIZE + INIT_STACK`, places `START_ADDR` in the return register, and returns into the kernel.

State and handoff are firmware-oriented: global `hwrpb`, static dummy PCB, PAL revision update, SRM environment strings, and command line copied to `ZERO_PGE`. Risks include exact sector offset calculation using `_end - BOOT_ADDR`, assuming 8 KiB pages, partial SRM reads, and unimplemented `ENV_BOOTED_FILE` handling. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/boot/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/boot/misc.c -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/boot/misc.c

`misc.c` adapts old gzip inflate support for the Alpha compressed bootloader. Its only exported runtime service is `decompress_kernel`, used by `bootpz.c` to inflate the compressed kernel into a selected destination.

Important state includes `inbuf`, `window`, `insize`, `inptr`, `outcnt`, `input_data`, `input_data_size`, `output_data`, `output_ptr`, `bytes_out`, and the minimal heap bounds `free_mem_ptr/free_mem_end_ptr`. It includes `../../../lib/inflate.c` directly, providing `gunzip`, CRC support, and decompressor allocation expectations. `fill_inbuf` provides the compressed buffer once and errors on exhaustion; `flush_window` copies the sliding window to output while updating CRC; `error` prints through SRM and loops forever.

There is no filesystem persistence. The decompressor mutates global bootloader BSS and writes the final kernel image. Risks are fixed heap sizing, lack of recovery on bad gzip streams, output overflow if `KERNEL_SIZE` is wrong, and reliance on `malloc` behavior supplied by included inflate support. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/boot/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/boot/stdio.c -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/boot/stdio.c

`stdio.c` supplies a tiny formatting library for bootloader code that cannot rely on the full kernel printf implementation. It implements `strnlen`, `vsprintf`, `sprintf`, numeric formatting, field width, precision, flags, and common integer/string/pointer conversions.

Important helpers are `skip_atoi`, the `do_div` macro, `number`, `vsprintf`, and `sprintf`. Control flow follows classic Linux early-boot formatting: parse flags, width, precision, qualifier, switch on conversion, and write into a caller-supplied buffer without bounds checking.

State is purely stack/local except the caller-provided output buffer. Integration is with `srm_printk` and boot code that needs formatted firmware output. Risks are expected for this era of code: no `snprintf` bounds, limited qualifier support, no modern format extensions, and dependence on boot code not formatting untrusted or oversized strings. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/boot/stdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/boot/tools/mkbb.c -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/boot/tools/mkbb.c

`mkbb.c` is a host utility that installs an SRM-compatible boot block while preserving the existing Alpha disklabel. It is used by the boot Makefile after concatenating `lxboot`, `bootlx`, and `vmlinux.nh`.

The key type is the local `bootblock` union, which overlays a 512-byte block as bytes, quadwords, a disklabel at offset 64, and a checksum at the last quadword. `main` opens the target device read/write, reads the 512-byte bootloader block, reads the current disk boot block, copies the disklabel from disk into the bootloader image, recomputes the first-63-quadword checksum, seeks to the start, and writes the full block.

Persistent state is the target block device/file. Risks are significant because this tool writes sector zero: argument reversal, short reads/writes, endian/word-size assumptions for `unsigned long`, and weak error exits can damage a target image. Test signals are host-tool compilation plus running against temporary files with known disklabel/checksum bytes rather than a real device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/boot/tools/mkbb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/boot/tools/objstrip.c -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/boot/tools/objstrip.c

`objstrip.c` is a host utility that converts ELF or ECOFF Alpha executables into raw bootable binary payloads and can also generate an SRM primary boot block. It is the bridge between linked bootloader/header objects and the byte streams concatenated into boot images.

Important options are `-v` for diagnostics, `-b` for 512-byte padding/zero-filled BSS, and `-p` for primary bootblock generation. In primary mode it writes a 64-quadword block with the string `Linux SRM bootblock`, sector count, starting sector, flags, and checksum. In extraction mode it validates ELF `ET_EXEC`/`EM_ALPHA` or ECOFF executable/OMAGIC headers, computes file and memory sizes, handles an ELF entry-point/p_vaddr workaround, copies the loadable bytes, and zero-fills to BSS/padding length.

Persistent outputs are raw binary files or stdout. Risks include assuming one ELF program header, relying on Linux kernel header structs, host endianness/word-size expectations, and allowing extraction to continue after warning about multiple program headers. Tests should cover ELF and ECOFF fixtures, `-p` checksum generation, BSS zero-fill size, and failure paths for wrong architecture or malformed headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/boot/tools/objstrip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/Kbuild -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/Kbuild

This Kbuild fragment declares generated and generic asm header wiring for Alpha. It asks kbuild to generate `syscall_table.h` and to use generic versions of `agp.h`, `asm-offsets.h`, `kvm_para.h`, `mcs_spinlock.h`, and `text-patching.h`.

There is no runtime control flow or persistence; the file affects generated header availability and include resolution during builds. Dependencies are kbuild's `generated-y` and `generic-y` mechanisms. Risks are missing generated syscall tables or accidentally shadowing a generic header with an incomplete arch-local version. Test signals are clean Alpha header generation and compile coverage for includes that expect these generic fallbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/agp_backend.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/agp_backend.h

This header defines Alpha-specific AGP backend data structures. `alpha_agp_mode` overlays AGP capability/mode bits over a 32-bit longword, including rate, fast-write, 4GB, enable, sideband addressing, and request queue depth. `alpha_agp_info` binds a PCI hose, aperture bus base/size/sysdata, capability and active mode, private state, and operation table.

`struct alpha_agp_ops` is the main API: chipset backends provide `setup`, `cleanup`, `configure`, `bind`, `unbind`, and DMA-address `translate` callbacks. Integration is through `alpha_machine_vector.agp_info`, PCI controller code, and generic AGP memory management. State is held in the info object and backend private data, with hardware aperture programming performed by implementations elsewhere.

Risks are ABI drift between generic AGP and Alpha hose/aperture assumptions, incorrect bitfield layout assumptions, and stale chipset operations. Tests are build coverage plus AGP backend initialization/bind/unbind paths on supported chipsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/agp_backend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/asm-prototypes.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/asm-prototypes.h

This header exposes C prototypes for assembly helpers that need modversion or C-visible declarations. It includes spinlock, checksum, console, page, string, uaccess, and generic asm prototypes, then declares Alpha division/remainder helpers and `__udiv_qrnnd`.

The important APIs are `__divl`, `__reml`, `__divq`, `__remq`, unsigned variants, and `__udiv_qrnnd`. There is no runtime control flow in the header; it coordinates symbol typing between assembly implementations and C/generated metadata.

Risks are missing prototypes causing modversion mismatches or incorrect calling conventions for compiler-emitted division calls. Test signals are successful Alpha allmodconfig/module builds and no unresolved arithmetic helper symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/asm-prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/atomic.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/atomic.h

This header implements Alpha `atomic_t` and `atomic64_t` operations using load-locked/store-conditional loops. It supplies read/set, add/sub, bitwise and/andnot/or/xor, fetch and return variants, add-unless, and `atomic64_dec_if_positive`.

The central macros are `ATOMIC_OP`, `ATOMIC_OP_RETURN`, `ATOMIC_FETCH_OP`, and 64-bit equivalents. They emit `ldl_l/stl_c` or `ldq_l/stq_c`, branch to a cold subsection on store-conditional failure, and retry. Because Alpha has very weak ordering, the relaxed fetch/return primitives end with `smp_mb()`, and acquire/post fences are intentionally empty to avoid redundant back-to-back fences in generic wrappers. `arch_atomic_fetch_add_unless` and 64-bit versions add explicit full barriers before and after the LL/SC loop.

State is the atomic counter field itself. Dependencies include `READ_ONCE`, `WRITE_ONCE`, `asm/barrier.h`, and `asm/cmpxchg.h`. Risks are memory-ordering regressions, incorrect inline-asm constraints, and changing generic atomic expectations without preserving Alpha dependency ordering. Tests should include atomic API build tests, LKMM-style litmus assumptions, SMP stress, and refcount/add-unless users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/barrier.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/barrier.h

This header defines Alpha memory barrier primitives. `mb()` and `rmb()` emit `mb`; `wmb()` emits `wmb`. `__smp_load_acquire` performs a compile-time atomic-type assertion and a single `__READ_ONCE`, relying on Alpha-specific atomic rules and generic barrier composition. `__ASM_SMP_MB` expands to an assembly `mb` only under SMP.

It integrates with `asm-generic/barrier.h`, atomics, futexes, bitops, and I/O wrappers. There is no persistence; the state effect is CPU memory-order visibility. The key risk is Alpha's weak memory model: replacing these with weaker operations can break lockless code even when it works on stronger architectures. Tests are SMP boot/stress, atomic/futex paths, and memory-model litmus coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/bitops.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/bitops.h

This header provides Alpha atomic and non-atomic bit operations plus bit-scan and hweight helpers. Atomic setters/clearers/changers use 32-bit `ldl_l/stl_c` loops over the addressed word; test-and operations return whether the bit was previously set and insert SMP barriers around lock-like operations.

Important APIs include `set_bit`, `clear_bit`, `clear_bit_unlock`, `change_bit`, `test_and_set_bit`, `test_and_set_bit_lock`, `test_and_clear_bit`, `test_and_change_bit`, non-atomic `arch___*` variants, `xor_unlock_is_negative_byte`, `ffz`, `__ffs`, `ffs`, `fls64`, `__fls`, `fls`, hweight hooks, and `sched_find_first_bit`. EV67-capable builds use CIX helpers such as `__kernel_cttz`, `__kernel_ctlz`, and `__kernel_ctpop`; older CPUs use byte-compare/extract sequences and `__flsm1_tab`.

State is the target bitmap word. Dependencies are `asm/compiler.h`, barriers, and generic bitops includes for little-endian/ext2/non-instrumented helpers. Risks include 32-bit word addressing of bitmaps on a 64-bit architecture, missing barriers for lock/unlock semantics, and CPU feature ifdefs that must match compiler flags. Tests should exercise lock bitops, bitmap scans, scheduler bitmap selection, and EV6/EV67 versus generic builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/bug.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/bug.h

This header defines Alpha's architecture `BUG()` implementation when `CONFIG_BUG` is enabled. The macro emits `call_pal PAL_bugchk`, followed by the source line and file pointer, then marks the path unreachable.

It integrates with PALcode and `asm-generic/bug.h`, providing `HAVE_ARCH_BUG`. The comment notes why `.gprel32` is avoided: modules might not have GP loaded for the file reference. Persistent state is crash/debug metadata embedded in the instruction stream.

Risks are module relocation/GP assumptions and tooling expectations around the inline `.long`/`.8byte` data after the PAL call. Test signals are build coverage and decoding of BUG reports on Alpha.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/cache.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/cache.h

This header defines L1 cacheline sizing for Alpha. Generic and EV6 builds use 64-byte lines; older EV4/EV5 style systems use 32-byte lines. `SMP_CACHE_BYTES` is set equal to `L1_CACHE_BYTES`.

There is no control flow or persistence. The values affect structure alignment, per-CPU layout, DMA/cache assumptions, and generic kernel cacheline padding. Risks are false sharing or ABI/layout changes if CPU selection and actual hardware diverge. Test signals are compile-time layout checks and runtime stability on both EV5-like and EV6-like systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/cacheflush.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/cacheflush.h

This header defines Alpha instruction-cache flush behavior. Kernel/module `flush_icache_range` maps to `imb()` on UP or `smp_imb()` on SMP. User-page flushing uses a cheaper ASN-context strategy: for executable VMAs, reload the active mm context or clear the per-CPU mm context so the next use gets a new address-space number.

Important APIs are `flush_icache_range`, `flush_icache_user_page`, and `flush_icache_pages`. The implementation relies on Alpha icache entries being ASN-tagged; it avoids indiscriminate user `imb` where changing ASN suffices. Dependencies include `linux/mm.h`, `current`, `smp_processor_id`, and `__load_new_mm_context`.

State effects are mm context updates and global instruction-stream barriers. Risks are stale instructions after ptrace/breakpoint/module writes, especially on SMP where the function is external. Test signals include module loading, ptrace breakpoints, executable page writes, and SMP icache shootdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/cacheflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/checksum.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/checksum.h

This header declares Alpha-optimized network checksum routines. It exports IP header checksums, TCP/UDP pseudo-header checksum helpers, partial checksums, copy-and-checksum helpers, and IPv6 pseudo-header checksums.

Important APIs are `ip_fast_csum`, `csum_tcpudp_magic`, `csum_tcpudp_nofold`, `csum_partial`, `csum_and_copy_from_user`, `csum_partial_copy_nocheck`, `ip_compute_csum`, `csum_fold`, and `csum_ipv6_magic`. It advertises `_HAVE_ARCH_COPY_AND_CSUM_FROM_USER`, `_HAVE_ARCH_CSUM_AND_COPY`, and `_HAVE_ARCH_IPV6_CSUM`.

There is no local state. Integration is with the networking stack and Alpha assembly/C implementations under `arch/alpha/lib`. Risks include odd-length fragment handling, alignment assumptions, user-copy faults, and endian/fold correctness. Tests are packet checksum selftests, IPv4/IPv6 TCP/UDP traffic, and fault-injection for user-copy checksum paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/cmpxchg.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/cmpxchg.h

This header implements Alpha exchange and compare-exchange primitives. It supports 1, 2, 4, and 8 byte objects using LL/SC loops; byte and halfword operations operate inside an aligned quadword with insert/mask/extract instructions.

Important helpers are `____xchg_u8/u16/u32/u64`, `____cmpxchg_u8/u16/u32/u64`, dispatcher functions `____xchg` and `____cmpxchg`, local macros `xchg_local`, `arch_cmpxchg_local`, `arch_cmpxchg64_local`, and fully ordered `arch_xchg`, `arch_cmpxchg`, and `arch_cmpxchg64`. Invalid sizes deliberately reference undefined bad-pointer functions to cause link errors.

State is the target memory word. Full arch operations wrap local LL/SC with `smp_mb()` before and after, because they may implement critical sections. Risks are memory ordering, unaligned or unexpected object sizes, inline assembly constraints, and 8/16-bit updates contending on the same aligned quadword. Tests should cover cmpxchg loops, try-cmpxchg users, byte/word atomicity, and lock/refcount code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/cmpxchg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/compiler.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/compiler.h

This small header includes `uapi/asm/compiler.h`, exposing Alpha compiler/instruction helper definitions to kernel code. It has no local APIs beyond the include guard.

Integration is broad: headers such as bitops and core I/O depend on compiler helper intrinsics/macros supplied by the UAPI compiler header. Risks are mostly include-order and UAPI drift; missing helpers would break inline assembly wrappers and CPU instruction abstractions. Test signal is full Alpha header and kernel compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/compiler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/console.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/console.h

This header declares SRM console callback interfaces and console initialization helpers. It includes UAPI console constants and exposes callback functions for puts/getc/open/close/read/getenv/setenv/save-env, plus `srm_fixup`, `srm_puts`, `srm_printk`, `callback_init_done`, and `callback_init`.

The APIs are firmware integration points used by boot code and early kernel console paths. They operate on SRM units, channels, environment ids, and HWRPB/CRB callback data. State is external firmware callback state plus `callback_init_done`.

Risks include callback calling conventions, buffer lengths, HWRPB callback relocation through `srm_fixup`, and using console callbacks after boot code has started moving or overwriting its image. Test signals are SRM boot logs, environment variable reads, and early printk behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/console.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_cia.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_cia.h

This chipset header describes the CIA/21171, CIA-2/21172, and PYXIS/21174 core logic used by EV5-class Alpha systems. It defines CSR addresses for CIA control, memory, PCI windows, HAE registers, diagnostics, performance counters, error registers, ALCOR GRU interrupt registers, PYXIS interrupt registers, sparse/dense memory spaces, and a CIA machine-check system-data frame.

The important runtime APIs are `cia_ioread8/16/32/64`, `cia_iowrite8/16/32/64`, `cia_ioportmap`, `cia_ioremap`, `cia_is_ioaddr`, `cia_is_mmio`, plus BWX variants `cia_bwx_*`. Non-BWX accesses use sparse memory encodings with byte-enable/transfer-length bits and HAE state; BWX-capable paths can use more linear byte/word I/O. The header chooses `__IO_PREFIX` as `cia` or `cia_bwx` based on `__WANT_IO_DEF`.

State includes chipset CSRs, HAE cache/register state mediated by `io.h`, PCI window registers, and machine-check logout data. Integration is via `asm/io.h`, `alpha_machine_vector`, PCI hose setup, interrupt code, and error handling. Risks are address-mask/HAE mistakes, sparse memory byte-lane encoding, PYXIS/CIA revision quirks, and generic-kernel dispatch selecting the wrong prefix. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_cia.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_irongate.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_irongate.h

This header models the AMD-751 Irongate chipset used on Nautilus EV6 systems. It defines PCI configuration register structures `Irongate0` and `Irongate1`, CSR/config address macros, memory/I/O/config/IACK spaces, the `IronECC` CSR pointer, and an Irongate machine-check frame.

Runtime APIs are simple linear mapping helpers: `irongate_ioportmap`, external `irongate_ioremap`/`irongate_iounmap`, `irongate_is_ioaddr`, and `irongate_is_mmio`. It then sets `__IO_PREFIX=irongate` and marks byte/word and long/quad I/O and MMIO operations as trivial so `io_trivial.h` supplies direct loads/stores.

State is chipset PCI/AGP/GART/ECC CSRs and mapped I/O addresses. Integration is with `asm/io.h`, PCI/AGP setup, DMA/IOMMU paths, and machine-check reporting. Risks include the 44-bit physical address split, GART/AGP register layout drift, and distinguishing MMIO from port space using address bits. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_irongate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_marvel.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_marvel.h

This header defines EV7 Marvel/IO7 platform addressing and register structures. It covers EV7 CSR address construction, IO7 port/hose physical and kernel addresses, IRQ vector sizing for up to 32 PIDs, IO7 window/control unions, `io7_port` and `io7` topology structures, and IACK/DAC constants.

Important APIs include external `marvel_ioread8`, `marvel_iowrite8`, `marvel_ioremap`, `marvel_iounmap`, `marvel_ioportmap`, `marvel_is_mmio`, inline 16-bit helpers using `__kernel_ldwu/stw`, and `marvel_is_ioaddr`. It sets `__IO_PREFIX=marvel`, with direct MMIO read/write operations but non-trivial byte/word port I/O.

State is IO7 topology, per-port CSR pointers, PCI window registers, and Marvel interrupt routing. Integration is through generic Alpha I/O dispatch, PCI hose discovery, AGP port handling, and EV7 error/interrupt code. Risks include large multi-processor/hose address encodings, 49-bit DAC offset assumptions, port 7 CSR handling, and mixing direct kernel addresses with remapped resources. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_marvel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_mcpcia.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_mcpcia.h

This header describes MCPCIA/Turbolaser multi-hose core logic. It defines per-MID sparse/dense/I/O/config/CSR address spaces, interrupt registers, HAE registers, error and scatter-gather window CSRs, default hose bias values, DAC offset, and an uncorrected machine-check frame.

Important APIs are `mcpcia_ioread8/16/32/64`, `mcpcia_iowrite8/16/32/64`, `mcpcia_ioportmap`, `mcpcia_ioremap`, `mcpcia_is_ioaddr`, and `mcpcia_is_mmio`. Like CIA, byte/word accesses use sparse encodings and HAE-like state, while long/quad dense accesses are simpler. The `MCPCIA_FROB_MMIO` macro adjusts MMIO addresses depending on dense/sparse treatment.

State includes MCPCIA CSRs, interrupt masks, PCI windows, HAE registers, and machine-check data. Integration is with `asm/io.h`, PCI controller setup, DMA TBI/window code, and platform interrupt handlers. Risks are hose/MID mapping errors, sparse memory masks, one-window HAE assumptions, and multi-hose I/O address canonicalization. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_mcpcia.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_polaris.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_polaris.h

This header provides the Polaris platform's core memory and I/O map. It defines sparse/dense memory, sparse/dense I/O, config, and IACK base addresses, a few dense config vendor/device/status register aliases, and a minimal Polaris machine-check system-data structure.

Runtime APIs are `polaris_ioportmap`, `polaris_ioremap`, `polaris_is_ioaddr`, and `polaris_is_mmio`. The header declares all read/write and I/O operations trivial through `io_trivial.h`, with `__IO_PREFIX=polaris`.

State is the mapped chipset address space and any external machine-check data. Integration is the compile-time chipset branch in `asm/io.h`. Risks are low compared with sparse-chipset headers, but base-address constants and MMIO-vs-port classification must match hardware. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_polaris.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_t2.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_t2.h

This header models the T2/Gamma core logic used by Sable-style systems. It defines Gamma bias, config/I/O/sparse/dense memory spaces, T2 IOCSR/error/HAE/window/TLB registers, CPU and memory CSR bases, and detailed T2 machine-check/corrected-error frame structures.

Important APIs include low-level `t2_inb/outb/inw/outw/inl/outl/inq/outq`, `t2_readb/readw/readl/readq`, `t2_writeb/writew/writel/writeq`, `t2_ioportmap`, `t2_ioremap`, `t2_is_ioaddr`, `t2_is_mmio`, and macro-generated `t2_ioread*`/`t2_iowrite*`. The code has explicit HAE update logic (`t2_set_hae`) around sparse accesses and uses non-trivial I/O flags so `asm/io.h` does not replace it with simple loads/stores.

State includes T2 HAE registers, Gamma bias via `alpha_mv.sys.t2.gamma_bias` for generic cases, PCI windows, and machine-check logout frames. Integration is with Alpha I/O dispatch, platform error handling, and DMA/PCI setup. Risks are HAE synchronization, sparse address encoding, CPU/memory bank register interpretation, and machine-check frame layout. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_t2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_titan.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_titan.h

This header describes Titan/Privateer EV6-family core logic. It defines CChip/DChip/PAChip/GPChip structures, AGP and boot CPU globals, PAChip window/control/error unions, hose address macros, IACK/IO/MEM bias values, IO space size, TIG space, DAC offset, and Titan/Privateer machine-check/environmental frames.

Runtime APIs are external `titan_ioportmap`, `titan_ioremap`, `titan_iounmap`, external `titan_is_mmio`, and inline `titan_is_ioaddr`. It selects `__IO_PREFIX=titan` and marks I/O/MMIO operations as trivial, letting `io_trivial.h` provide direct load/store access.

State lives in Titan chipset CSRs, AGP flags, PCI windows, interrupt/environmental error frames, and mapped I/O pointers. Integration is with PCI/AGP setup, interrupt routing, machine checks, and generic `asm/io.h`. Risks include PAChip bitfield layout, AGP presence/control handling, DAC offset being documented as a guess, and multi-hose address calculations. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_titan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_tsunami.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_tsunami.h

This header defines Tsunami/Typhoon EV6 core logic. It models CChip, DChip, and PChip CSRs; PChip error, window base, control, and error-mask unions; hose address spaces; I/O and memory bias; DAC offset; and an empty Tsunami machine-check system-data structure placeholder.

Important APIs are external `tsunami_ioportmap` and `tsunami_ioremap`, inline `tsunami_is_ioaddr` and `tsunami_is_mmio`, and `io_trivial.h`-supplied direct I/O/MMIO access under `__IO_PREFIX=tsunami`. `TSUNAMI_bootcpu` tracks platform boot CPU identity externally.

State includes CChip/PChip registers, PCI windows/TLB invalidation registers, and mapped I/O. Integration is through Alpha I/O, PCI hose setup, DMA/IOMMU windows, and error handlers. Risks include hose address shifts, 40-bit DAC offset, PChip bitfield correctness, and assuming iounmap is trivial. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_tsunami.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_wildfire.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_wildfire.h

This header describes Wildfire's QBB/PCA/PCI fabric. It defines maximum QBB/PCA/IRQ counts, hard/soft QBB maps and masks, existence macros, aligned CSR wrapper types, structures for QSD/QSA/IOP/GP/PCA/PCI entities, entity/address construction macros, PCI hose mapping, and I/O/MEM bias constants.

Runtime APIs are inline `wildfire_ioportmap`, `wildfire_ioremap`, `wildfire_is_ioaddr`, and `wildfire_is_mmio`, with trivial direct access generated by `io_trivial.h` under `__IO_PREFIX=wildfire`. The mapping combines QBB, hose, PCA entity, and local offsets to form kernel-visible addresses.

State is platform topology masks, CSR structures, interrupt routing state, PCI windows, and mapped addresses. Integration is Alpha generic I/O, IRQ sizing (`NR_IRQS` for Wildfire), PCI discovery, and platform init. Risks include topology mask interpretation, hard/soft QBB translation, large address construction, and fixed maximum QBB assumptions. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_wildfire.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/delay.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/delay.h

This header declares Alpha delay primitives: `__delay`, `udelay`, and `ndelay`, and marks `ndelay` as arch-provided. There is no local implementation or state.

Integration is with generic timing/delay users and Alpha library implementations calibrated from CPU timing data. Risks are calibration accuracy and overflow/rounding for very small or large delays. Test signals are boot calibration, device driver timing stability, and compile coverage for generic delay APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/delay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/device.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/device.h

This header delegates architecture-specific `struct device` extensions to `asm-generic/device.h`. It defines no Alpha-only fields or control flow.

The integration point is the driver core's `struct device` layout. Risks are minimal; adding Alpha-specific device state would require replacing or extending this generic include. Test signal is driver-core build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/dma-mapping.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/dma-mapping.h

This header connects the generic DMA mapping API to Alpha's PCI DMA operations. It declares `alpha_pci_ops` and returns it from `get_arch_dma_ops`.

There is no internal state; DMA mapping state is managed by the implementation behind `alpha_pci_ops` and platform PCI/IOMMU code. Integration is broad across all DMA-capable drivers. Risks include selecting the wrong ops for systems with or without an IOMMU and stale assumptions in legacy ISA DMA paths. Tests include DMA API debug, PCI device I/O, and platforms with direct and translated DMA windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/dma-mapping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/dma.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/dma.h

This header implements legacy ISA 8237 DMA controller definitions and helpers for Alpha PCs. It documents channel layout, byte/word transfer differences, boundary limits, count semantics, page-register mapping, and Alpha-specific high-page registers for 32-bit DMA addresses.

Important APIs and macros include `MAX_DMA_CHANNELS`, platform-specific `MAX_ISA_DMA_ADDRESS`, `MAX_DMA_ADDRESS`, controller register constants, `claim_dma_lock`, `release_dma_lock`, `enable_dma`, `disable_dma`, `clear_dma_ff`, `set_dma_mode`, `set_dma_ext_mode`, `set_dma_page`, `set_dma_addr`, `set_dma_count`, `get_dma_residue`, `request_dma`, `free_dma`, and `check_dma`. Helpers write port registers through `outb/inb` from `asm/io.h` and require interrupt-disabled serialized access around flip-flop-sensitive sequences.

State includes the external `dma_spin_lock`, DMA controller registers, page/high-page registers, and active channel reservations. Risks are old hardware constraints: 64K/128K boundary crossing, channel 5-7 word alignment, page register ordering, platform-specific address ceilings, and direct-map assumptions. Tests are floppy/ISA DMA users, DMA residue checks, and build coverage for platforms with and without PCI IOMMU support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/elf.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/elf.h

This header defines Alpha ELF ABI constants for the kernel. It lists Alpha relocation types, symbol `st_other` values, section flags, e_flags, register set sizes/types, executable page size, ET_DYN base, architecture checks, platform initialization, core-dump register copy hooks, hardware capability reporting, platform string selection, and auxiliary vector cache-shape entries.

Important APIs/macros are `elf_check_arch`, `ELF_CLASS/DATA/ARCH`, `ELF_EXEC_PAGESIZE`, `ELF_ET_DYN_BASE`, `ELF_PLAT_INIT`, `ELF_CORE_COPY_REGS`, `ELF_CORE_COPY_TASK_REGS`, `ELF_HWCAP`, `ELF_PLATFORM`, and `ARCH_DLINFO`. It depends on Alpha special instructions `amask` and `implver`, current thread info, and external cache-shape variables.

State is process exec/core-dump metadata and auxv entries. Risks are ABI-visible: relocation constants, rejecting `EF_ALPHA_32BIT`, register ordering for core files, and platform string/hwcap values consumed by dynamic loaders. Test signals are ELF exec, core dumps, dynamic loader behavior, auxv inspection, and binfmt_elf build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/emergency-restart.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/emergency-restart.h

This header delegates emergency restart support to `asm-generic/emergency-restart.h`. It has no Alpha-specific implementation.

Integration is with panic/reboot paths. Risks are only that generic restart may not capture platform-specific PAL/SRM restart needs; platform-specific shutdown hooks live elsewhere. Test signal is build coverage and reboot/panic behavior on supported Alpha systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/emergency-restart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/err_common.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/err_common.h

This header defines common Alpha error-log and machine-check packet constants. It provides SCB vector ids, machine-check disposition codes, error-log class/type ids, an `el_timestamp` union, and `struct el_subpacket` for system error, system event, halt, logout, Regatta, and raw packet headers.

There is no control flow. State is the layout of firmware/PAL error records parsed by machine-check handlers. Integration is with EV6/EV7/platform-specific error headers and machine-check code that walks logout frames. Risks are binary layout and bit-width drift; changing these structs can break decoding of firmware-provided records. Tests are machine-check parser builds, synthetic logout-frame decoding, and hardware/firmware error logs where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/err_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/err_ev6.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/err_ev6.h

This header is currently a guarded placeholder for EV6-specific error handling declarations. It contains no types, functions, or macros beyond the include guard comment.

Its purpose is dependency stability: code can include `asm/err_ev6.h` even though EV6-specific packet declarations are not needed here. There is no state or control flow. Risks are minimal, but adding declarations later must stay compatible with common machine-check parsing. Test signal is include/build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/err_ev6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/err_ev7.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/err_ev7.h

This header defines EV7 PAL logout-frame subpacket layouts. It includes structures for logout, processor, ZBOX, RBOX, IO, IO port, environmental subpackets, a union `ev7_pal_subpacket`, and `ev7_lf_subpackets` for collected pointers.

The only inline control-flow helper is `ev7_lf_env_index`, which validates environmental packet type with `BUG_ON` and converts PAL environmental type ids into a zero-based array index. Dependencies include common error-log type constants and `BUG_ON`.

State is decoded firmware/PAL logout data, including CPU, memory, routing, IO ASIC, environmental, and hot-plug condition fields. Integration is EV7/Marvel machine-check handling. Risks are binary layout fidelity, validating environmental type ranges before indexing, and interpreting multiple subpacket revisions. Tests are synthetic EV7 logout parsing and build coverage for machine-check handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/err_ev7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/extable.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/extable.h

This header defines Alpha exception table entries and fixup behavior. `struct exception_table_entry` stores a PC-relative faulting instruction offset and a packed fixup word containing next-instruction offset, error register, and value register.

The key API is `fixup_exception(map_reg, _fixup, pc)`: it zeros `valreg` unless it is register 31, writes `-EFAULT` to `errreg` unless it is register 31, and returns `pc + nextinsn`. `ARCH_HAS_RELATIVE_EXTABLE` declares relative table entries. `swap_ex_entry_fixup` swaps fixup units during sorting.

State is exception-table metadata consumed by fault handlers and uaccess fixups. Risks are packed bitfield layout, Alpha register numbering, and the assembler emission format described by the comments. Tests include user access fault fixups, exception-table sorting, and sparse/compile checks for `EXC()` users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/extable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/floppy.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/floppy.h

This header provides Alpha-specific glue for the legacy floppy driver. It maps floppy I/O to ISA port access, wires floppy DMA and IRQ operations to Alpha DMA/IRQ helpers, and supplies a PCI DMA setup helper when `CONFIG_PCI` is enabled.

Important macros include `fd_inb/outb`, DMA request/free/enable/disable/mode/address/count helpers, IRQ request/free/enable/disable helpers, `fd_dma_setup`, `virtual_dma_init`, controller base constants `FDC1/FDC2`, and fixed floppy type constants. `alpha_fd_dma_setup` caches the last DMA mapping, unmaps it if address/size/direction changes, maps the new buffer through `isa_bridge->dev`, programs the 8237 DMA controller, sets `virtual_dma_port`, and enables DMA.

State includes static cached `bus_addr`, previous buffer metadata, controller globals, DMA controller registers, and `virtual_dma_port`. Risks include cached DMA mapping lifetime, direction mapping, ISA bridge availability, fixed CMOS-less drive type assumptions, and legacy DMA boundary rules inherited from `dma.h`. Tests are floppy build coverage and real/virtual floppy read/write where hardware exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/floppy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/fpu.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/fpu.h

This header defines Alpha floating-point control register access and declares FP register helpers. `rdfpcr` reads the FPCR either from saved thread state or from hardware using EV6 `ftoit/itoft` sequences or older store/load floating instructions. `wrfpcr` writes saved thread state when FP is saved or writes hardware FPCR directly, preserving `$f0`.

`swcr_update_status` merges accrued exception status from hardware FPCR into software control word on EV6. External helpers read/write FP registers in full and single precision. The functions disable preemption while inspecting or changing current thread FP state.

State includes `current_thread_info()->status`, saved FP array slot 31, hardware FPCR, and TS_RESTORE_FP status. Risks are preemption safety, preserving `$f0`, EV6 versus older instruction sequences, and lazy FP restore semantics. Tests include FP signal/context switching, ptrace FP register access, and math exception status behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/ftrace.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/ftrace.h

This file is intentionally empty. It satisfies generic include expectations for `asm/ftrace.h` on Alpha without declaring architecture-specific ftrace hooks.

There is no state, control flow, or API surface. Risks are feature-expectation drift if generic ftrace starts requiring arch definitions for Alpha. Test signal is ftrace-related build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/ftrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/futex.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/futex.h

This header implements futex atomic operations in user memory for Alpha. The central `__futex_atomic_op` macro emits optional SMP `mb`, a 32-bit `ldl_l/stl_c` loop, operation-specific arithmetic/logic, retry on failed store-conditional, and exception-table fixups for user faults.

`arch_futex_atomic_op_inuser` validates `access_ok`, supports `FUTEX_OP_SET`, `ADD`, `OR`, `ANDN`, and `XOR`, writes the old value to `oval` on success, and returns `-ENOSYS` for unknown operations. `futex_atomic_cmpxchg_inatomic` performs an in-user compare-exchange with exception fixups and returns the observed value through `uval`.

State is user memory, output old-value storage, and exception fixup registers. Dependencies include futex constants, uaccess, Alpha errno, barriers, and `EXC` exception-table machinery. Risks include weak memory ordering, user fault recovery, access_ok coverage, signed/unsigned operation arguments, and live-lock under contention. Tests are futex selftests, robust mutexes, and fault-injection around invalid user addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/gct.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/gct.h

This header defines Galaxy Configuration Tree v6 node structures and search plumbing. `gct6_node` captures firmware tree node metadata including type/subtype, ownership, IDs, links, flags, FRU id, checksum, and magic. `gct6_search_struct` pairs a type/subtype with a callback.

Important macros are `GCT_NODE_MAGIC`, `GCT_TYPE_HOSE`, `GCT_SUBTYPE_IO_PORT_MODULE`, and `GCT_NODE_PTR`, which resolves a firmware tree offset relative to `hwrpb->frut_offset`. `gct6_find_nodes` is declared for walking/searching nodes.

State is firmware FRU/configuration tree data reachable from HWRPB. Integration is platform discovery, especially hose/I/O module enumeration. Risks are trusting firmware offsets, checksum/magic validation, and pointer arithmetic against HWRPB. Tests are build coverage and platform discovery on systems exposing GCT/FRU data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/gct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/hardirq.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/hardirq.h

This header declares Alpha's `ack_bad_irq` hook and then includes generic hardirq definitions. It defines `ack_bad_irq` so generic code uses the arch-provided implementation for unexpected interrupts.

State is generic hardirq per-CPU accounting plus any logging/counting in the implementation elsewhere. Risks are minimal; the key integration point is ensuring bad IRQs are acknowledged in a platform-appropriate way. Test signals are interrupt-controller build coverage and spurious IRQ handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/hardirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/hw_irq.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/hw_irq.h

This header declares low-level Alpha interrupt counters and actual IRQ count selection. It exposes `irq_err_count`, per-CPU `irq_pmi_count`, and `ACTUAL_NR_IRQS`, which resolves to `alpha_mv.nr_irqs` for generic kernels or `NR_IRQS` for fixed-platform builds.

State is interrupt error/performance-monitor counters and platform vector configuration. Integration is with `machvec.h`, `irq.h`, and interrupt handling code. Risks include static array sizing versus actual platform IRQ count and generic-kernel machine-vector initialization. Tests are interrupt init, `/proc/interrupts` style accounting, and platform-specific IRQ routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/hw_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/hwrpb.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/hwrpb.h

This header defines the Alpha Hardware Restart Parameter Block contract. It declares the initial HWRPB address, architected CPU and system type constants, and structures for PCB, per-CPU data, procedure descriptors, console callback routine block mappings, memory descriptors/clusters, dynamic system recognition data, and the top-level `hwrpb_struct`.

The important API is global `hwrpb` plus `hwrpb_update_checksum`, which sums all quadwords before `chksum` and writes the checksum. HWRPB fields provide page size, physical address bits, max ASN, system identity, clock frequencies, VPTB, processor tables, console terminal/callback offsets, memory descriptor offsets, restart callbacks, and FRU/DSR pointers.

State is firmware-owned boot/runtime configuration shared with the kernel and bootloaders. Integration is everywhere in Alpha early boot, PAL setup, console callbacks, memory discovery, CPU discovery, and platform selection. Risks are binary layout fidelity, flexible-array offset arithmetic, checksum correctness, and assuming `INIT_HWRPB` contents before validation. Tests are boot on SRM/QEMU, HWRPB parsing, checksum update coverage, and platform detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/hwrpb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/io.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/io.h

This is Alpha's central I/O abstraction. It defines the kernel identity mapping base `IDENT_ADDR`, HAE update helpers, `virt_to_phys`/`phys_to_virt`, deprecated ISA bus mapping helpers, compile-time or generic machine-vector dispatch for chipset I/O, external I/O function declarations, inline `ioport_map`, `ioremap`, `iounmap`, `__is_ioaddr`, `__is_mmio`, barrier-wrapped read/write and ioread/iowrite wrappers, relaxed accessors, string I/O operations, RTC port defaults, and generic I/O inclusion.

Control flow depends on `CONFIG_ALPHA_GENERIC`: generic kernels route through `alpha_mv.mv_*`; fixed-platform kernels include one `core_*.h` header and set `__IO_PREFIX`. If the selected backend marks operations trivial, this header emits inline wrappers around backend loads/stores with `mb()` before/after. `__set_hae` raises IPL to `IPL_MAX`, updates the machine-vector HAE cache/register, issues barriers and a readback, then restores IPL.

State includes HAE register/cache, HWRPB physical address width, direct-map base/size, machine-vector function pointers, and memory-mapped device state. Risks are broad: Alpha memory ordering, HAE atomicity against interrupts, generic versus fixed backend selection, deprecated ISA mappings returning 0/NULL, and classifying MMIO versus port space. Test signals include all driver I/O paths, PCI resource mapping, DMA users, and multi-chipset builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/io_trivial.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/io_trivial.h

This header is a reusable template for chipset backends whose I/O mapping is already linear. It may be included multiple times with different `__IO_PREFIX` and `*_trivial_*` feature macros.

When enabled, it emits prefixed `ioread8/16`, `iowrite8/16`, `ioread32/64`, `iowrite32/64`, raw `readb/readw/readl/readq`, `writeb/writew/writel/writeq`, and a no-op `iounmap`. Byte and word operations use Alpha byte/word helper instructions (`__kernel_ldbu`, `__kernel_ldwu`, `__kernel_stb`, `__kernel_stw`); long and quad operations use volatile direct loads/stores. `trivial_rw_bw == 2` routes read/write through ioread/iowrite instead of direct load/store.

State is only the addressed device memory. Integration is with every linear `core_*.h` backend and `asm/io.h` barrier wrappers. Risks are macro hygiene from multiple inclusion, using direct operations for non-linear spaces, and missing force/volatile semantics. Tests are compile coverage for each backend prefix and runtime I/O on linear chipsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/io_trivial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/irq.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/irq.h

This header defines Alpha IRQ count limits and IRQ canonicalization. `NR_IRQS` is selected by platform config, ranging from 16 on small systems to `32768 + 16` for Marvel, with generic kernels using an upper bound unless legacy start address excludes large platforms.

`irq_canonicalize` maps IRQ 2 to IRQ 9 for old PC-compatible serial/ISA behavior. The header also declares `perf_irq`, a performance interrupt hook taking a vector and pt_regs.

State is compile-time IRQ table sizing and an external performance IRQ callback. Integration is with `hw_irq.h`, machine-vector actual IRQ counts, platform interrupt controllers, and legacy drivers. Risks are static array over/under-sizing, generic upper-bound memory cost, and old ISA IRQ alias assumptions. Test signals are interrupt controller init, device IRQ mapping, and perf interrupt delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/irqflags.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/irqflags.h

This header implements Alpha local interrupt flag operations using PAL processor status/IPL helpers. It defines IPL levels from minimum through machine check, optionally replaces `IPL_MIN` for broken IRQ masks, and wraps `rdps`, `swpipl`, and `setipl`.

Important APIs are `arch_local_save_flags`, `arch_local_irq_disable`, `arch_local_irq_save`, `arch_local_irq_enable`, `arch_local_irq_restore`, `arch_irqs_disabled_flags`, and `arch_irqs_disabled`. Disable/save raise IPL to `IPL_MAX`; enable restores `IPL_MIN`; restore sets the saved IPL.

State is processor IPL. Integration is spinlocks, interrupt entry/exit, DMA locking, and HAE updates. Risks include treating saved flags as raw IPL, broken-mask platform minimums, and missing compiler barriers around PAL operations. Tests are interrupt nesting, spinlock IRQ save/restore, and platform IRQ enable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/irqflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/linkage.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/linkage.h

This header defines Alpha linkage helpers. `cond_syscall(x)` emits a weak symbol alias to `sys_ni_syscall`; `SYSCALL_ALIAS(alias, name)` emits an assembler alias and global symbol.

There is no runtime state in the header, but it directly affects syscall symbol resolution and assembly linkage. Integration is syscall table generation and weak optional syscalls. Risks are assembler syntax drift and aliases not matching generated syscall names. Test signals are syscall table/header generation and no unresolved syscall symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/linkage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/local.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/local.h

This header defines `local_t` counters backed by `atomic_long_t` and optimized local operations. Simple read/set/inc/dec/add/sub delegate to atomic_long operations; `local_add_return` and `local_sub_return` use `ldq_l/stq_c` loops without full SMP barriers; cmpxchg/xchg use local cmpxchg primitives.

Important APIs include `LOCAL_INIT`, `local_read`, `local_set`, arithmetic helpers, `local_cmpxchg`, `local_try_cmpxchg`, `local_xchg`, `local_add_unless`, `local_inc_not_zero`, and test/return variants. It also defines non-atomic `__local_*` helpers, though `__local_dec` appears to increment in this source, a notable risk signal if used.

State is the local counter. Integration is per-CPU counters and generic local API users. Risks include memory-order differences from full atomics, the suspicious `__local_dec` macro, and casting in `local_try_cmpxchg`. Tests are local_t API compile/runtime tests and any users of `__local_dec`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/machvec.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/machvec.h

This header defines `struct alpha_machine_vector`, the generic-kernel dispatch table for platform-specific I/O, IRQ, PCI, AGP, machine-check, SMP, RTC, and shutdown behavior. The first fields are HAE cache/register for assembly convenience, followed by platform limits and many function pointers.

Important vector fields include IRQ counts, RTC settings, max ASN, ISA DMA limit, IACK address, minimum I/O/MEM addresses, PCI DAC offset, PCI TBI, ioread/iowrite/read/write families, map/unmap/classification hooks, interrupt update/ack/device handlers, machine check handler, init hooks, PCI swizzle/map_irq/ops, AGP info, vector name, and small platform-specific parameter union.

State is the global `alpha_mv`, plus generic flags `alpha_using_srm` and `alpha_using_qemu`. Integration is central for `CONFIG_ALPHA_GENERIC`; `asm/io.h`, DMA, IRQ, PCI, cache/TB, and platform init all depend on it. Risks are uninitialized function pointers, vector mismatch with detected hardware, and keeping the first two fields stable for assembly. Tests are generic Alpha boot on multiple platforms and QEMU/SRM detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/machvec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/mc146818rtc.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/mc146818rtc.h

This header defines Alpha accessors for MC146818-compatible RTC registers. Unless a platform overrides `RTC_PORT`, it uses ISA ports `0x70+x` and sets `RTC_ALWAYS_BCD` to 1 in this header. `CMOS_READ` writes the index port then reads data; `CMOS_WRITE` writes the index then data.

State is CMOS/RTC hardware registers. Integration is generic RTC/CMOS code and Alpha ISA port I/O. Risks are platform differences in RTC access and the conflicting broader `asm/io.h` default of `RTC_ALWAYS_BCD 0`, making include context important. Tests are RTC read/write on supported systems and build coverage for RTC drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/mc146818rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/mce.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/mce.h

This header defines common Alpha machine-check logout structures. `struct el_common` is the shared logout header with size, retry/second-error flags, processor/system offsets, code, and revision. EV5 and EV6 structures then describe processor-specific uncorrectable machine-check frames with PAL temps, exception state, cache/ECC/interface status, addresses, syndromes, and control registers.

There is no control flow. State is binary machine-check data supplied by PAL/firmware and consumed by error handlers. Integration is with platform-specific error headers and machine-check decoding/reporting. Risks are structure packing/layout fidelity, differing PAL revisions, and correct interpretation of retry/second-error bits. Tests are compile coverage, synthetic frame decode tests, and hardware error logs where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/mce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/mmu.h -->
# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/mmu.h

This header defines Alpha's MMU context type as `unsigned long mm_context_t[NR_CPUS]`: one ASN/context bitmap or value per CPU.

There is no control flow. State lives in each mm's per-CPU context array and is used by context switch, TLB, and icache-ASN flushing code. Dependencies include `NR_CPUS` availability from kernel configuration. Risks are array sizing for large CPU counts and assumptions in cacheflush/mmu_context code about per-CPU context invalidation. Tests are process context switching, TLB flushes, and SMP builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/mmu.h -->
