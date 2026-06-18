# subset-b-000870 research

This grouped report covers x86 architecture headers from the Ceph client Linux source tree. Each source file is documented in manifest order and delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/apic.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/apic.h

Purpose: public x86 local APIC control surface. It defines APIC verbosity, interrupt-mode identifiers, xAPIC/x2APIC register access helpers, APIC driver dispatch, vector bitmap helpers, topology registration prototypes, and SMP wakeup/IPI hooks.

Important APIs and control flow: `native_apic_mem_{read,write,eoi}` access the MMIO LAPIC window, with an `X86_BUG_11AP` alternative for writes. x2APIC helpers access APIC MSRs and gate behavior on `CONFIG_X86_X2APIC`. `struct apic` is the selected APIC driver vtable; `apic_driver()` places candidates in `.apicdrivers`; `apic_setup_apic_calls()` installs static-call wrappers such as `apic_read()`, `apic_write()`, `apic_eoi()`, and IPI send functions. Vector helpers query/set APIC IRR-style bitmaps.

State, dependencies, and risks: state is mostly global APIC mode, driver pointer, APIC ID topology, static calls, and hardware registers. Dependencies include fixmap APIC mapping, MSRs, SMP topology, posted interrupts, alternatives, and cpufeatures. Risks include early-boot ordering, APIC mode mismatch, x2APIC register exclusions, offline CPU/NMI behavior, and static-call replacement correctness. Test signals are indirect through SMP boot, interrupt delivery, x2APIC, CPU hotplug, and APIC selftests/boot logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/apic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/apicdef.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/apicdef.h

Purpose: symbolic register map and bit definitions for local APIC, IO-APIC base addresses, delivery modes, xAPIC/x2APIC enable bits, and APIC ID layout.

Important APIs and control flow: this file exports register offsets such as `APIC_ID`, `APIC_EOI`, `APIC_ICR`, LVT registers, timer divisor fields, ESR bits, interrupt command bits, and helper macros like `GET_APIC_VERSION()`, `GET_APIC_MAXLVT()`, `GET_XAPIC_DEST_FIELD()`, and `SET_APIC_DELIVERY_MODE()`. It also fixes `MAX_IO_APICS`, `MAX_LOCAL_APIC`, `BAD_APICID`, and cluster/CPU extraction macros by word size.

State, dependencies, and risks: it has no runtime state, but its constants bind APIC register programming throughout interrupt, SMP, and timer code. Dependencies are `linux/bits.h`, fixmap `APIC_BASE`, and configuration width. Risks are off-by-bit errors, using xAPIC-only encodings in x2APIC paths, and assuming APIC ID limits that differ between 32-bit and 64-bit builds. Test signals are APIC bringup, interrupt routing, timer calibration, and KVM/APIC emulation compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/apicdef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/apm.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/apm.h

Purpose: 32-bit APM BIOS call glue for legacy power-management paths. It wraps far calls through `apm_bios_entry` while preserving registers expected by BIOS interfaces.

Important APIs and control flow: `apm_bios_call_asm()` takes function and input registers, optionally zeros data segments under `APM_ZERO_SEGS`, pushes `edi`/`ebp`, performs `lcall *%cs:apm_bios_entry`, captures carry in `%al`, restores saved registers/segments, and returns EAX/EBX/ECX/EDX/ESI. `apm_bios_call_simple_asm()` is the reduced form that returns only EAX and a carry-derived error flag.

State, dependencies, and risks: state lives outside the header in the APM BIOS descriptor/entry point and CPU segment registers. Dependencies include 32-bit protected-mode BIOS calling convention and caller-side synchronization. Risks include segment-state corruption, BIOS clobbers, fragile inline-assembly constraints, and legacy-only behavior that is hard to exercise on modern machines. Test signal is mostly boot or suspend/resume on APM-era hardware or emulator coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/apm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/arch_hweight.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/arch_hweight.h

Purpose: architecture-optimized Hamming weight helpers for x86 bit counting.

Important APIs and control flow: `__arch_hweight32()` and 64-bit `__arch_hweight64()` use the alternatives framework to patch from software helpers (`__sw_hweight32`/`__sw_hweight64`) to `popcntl`/`popcntq` when `X86_FEATURE_POPCNT` is present. 16-bit and 8-bit helpers mask and reuse the 32-bit implementation. On 32-bit, 64-bit weight is computed as two 32-bit weights.

State, dependencies, and risks: there is no persistent state; behavior depends on alternative patching and cpufeature detection. Dependencies include `asm/cpufeatures.h`, call constraints, and software fallback symbols. Risks are wrong register constraints across 32/64-bit builds and using POPCNT before alternatives or feature bits are valid. Test signals are bitops/lib tests, compiler build coverage, and runtime CPU feature variation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/arch_hweight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/archrandom.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/archrandom.h

Purpose: x86 hardware random-number interface for the generic random subsystem.

Important APIs and control flow: `rdrand_long()` retries `rdrand` up to `RDRAND_RETRY_LOOPS` and returns success via carry flag. `rdseed_long()` issues one `rdseed`. `arch_get_random_longs()` and `arch_get_random_seed_longs()` first require a nonzero requested count, then use `static_cpu_has(X86_FEATURE_RDRAND/RDSEED)`, and return one filled `unsigned long` or zero. `x86_init_rdrand()` is declared for CPU initialization outside UML.

State, dependencies, and risks: state is CPU feature state plus hardware RNG behavior. Dependencies include `processor.h`, cpufeatures, and the random core. Risks include trusting firmware/CPU-reported features, RDRAND retry exhaustion, early-boot feature availability, and virtualization quirks. Test signals include random subsystem boot messages, CPU feature masking, and tests that force unavailable hardware random paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/archrandom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/asm-offsets.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/asm-offsets.h

Purpose: architecture include shim that exposes generated C-structure offsets to assembly.

Important APIs and control flow: the file directly includes `<generated/asm-offsets.h>`. There are no local declarations or branches; build tooling generates the target header from offset extraction code before assembly files consume it.

State, dependencies, and risks: state is build-generated, not runtime. Dependencies are the kernel build order and generated header path. Risks are stale or missing generated offsets causing assembly/C ABI mismatches, especially for entry code and low-level context structures. Test signals are compile failures, objtool validation, and boot-time failures in code using generated offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/asm-offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/asm-prototypes.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/asm-prototypes.h

Purpose: collects C prototypes and includes needed by assembly-exported x86 symbols and modversion generation.

Important APIs and control flow: it includes ftrace, uaccess, pgtable, string, page, checksum, MCE, generic asm prototypes, special instructions, preempt, FRED, GS segment, and nospec branch headers. It declares `cmpxchg8b_emu()` when CX8 is not guaranteed and exposes `__ref_stack_chk_guard` for stack protector builds.

State, dependencies, and risks: no direct runtime state, but it is a build ABI surface between assembly and C. Dependencies span low-level x86 subsystems. Risks are missing prototypes causing modversion or linkage drift, especially for assembly routines with C callers. Test signals are allmodconfig/modversion builds, non-CX8 32-bit builds, and stack-protector link coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/asm-prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/asm.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/asm.h

Purpose: common x86 assembly formatting, register-name, pointer-size, exception-table, and inline-assembly helper macros for both C inline asm and `.S` files.

Important APIs and control flow: `__ASM_FORM*`, `__ASM_SEL*`, `__ASM_SIZE`, `_ASM_REG`, `_ASM_PTR`, `_ASM_ALIGN`, and `_ASM_ARG*` abstract 32/64-bit syntax. `rip_rel_ptr()` materializes RIP-relative pointers. `_ASM_EXTABLE*` emits relative exception-table entries with fixup types, and `_ASM_EXTABLE_TYPE_REG` validates register operands through generated assembler macros. `ASM_OUTPUT`, `ASM_INPUT`, `COMMA`, `ASM_CALL_CONSTRAINT`, and `EAX_EDX_*` hide compiler constraint differences.

State, dependencies, and risks: there is no runtime state, but generated sections such as `__ex_table` and `_kprobe_blacklist` are persistent binary metadata. Dependencies include generated offsets, extable types, annotate/stringify helpers, and architecture register conventions. Risks include malformed inline asm strings, wrong register width under mixed 32/64-bit code, and exception table entries pointing to invalid fixups. Test signals are build coverage, objtool, exception-fixup paths, and fault-injection for uaccess/MSR operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/atomic.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/atomic.h

Purpose: x86 `atomic_t` implementation and dispatcher to 32-bit or 64-bit `atomic64_t` implementations.

Important APIs and control flow: `arch_atomic_read()`/`set()` use one-copy read/write primitives. Arithmetic operations emit locked `addl`, `subl`, `incl`, `decl`, or use `GEN_*_RMWcc` for flag-returning variants. Return/fetch operations use `xadd`; compare/exchange uses `arch_cmpxchg` and `arch_try_cmpxchg`; bitwise fetch operations loop on try-cmpxchg. The file then includes `atomic64_32.h` or `atomic64_64.h`.

State, dependencies, and risks: state is caller-owned atomic storage. Dependencies include x86 lock prefix handling, cmpxchg, rmwcc, and barrier semantics. Risks are memory-ordering expectations, integer overflow semantics, and livelock under high contention for cmpxchg loops. Test signals include LKDTM/atomic litmus tests, refcount users, lockless data-structure tests, and architecture build matrices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/atomic64_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/atomic64_32.h

Purpose: 64-bit atomic operations for 32-bit x86, including fallback paths for CPUs without native `cmpxchg8b`.

Important APIs and control flow: `atomic64_t` is an 8-byte-aligned signed 64-bit counter. `arch_atomic64_read_nonatomic()` is explicitly only for priming unconditional cmpxchg loops. Operation declarations point to `atomic64_*_cx8` helpers or 386 emulation helpers selected by alternatives. Core operations wrap `arch_cmpxchg64`, `arch_try_cmpxchg64`, alternative call stubs for xchg/read/set/add/sub/inc/dec, and cmpxchg loops for bitwise/fetch operations.

State, dependencies, and risks: state is shared aligned counter storage plus CPU feature/alternative patching. Dependencies include out-of-line atomic64 assembly, CX8 feature detection, cmpxchg8b emulation, and strict inline-asm constraints. Risks include torn nonatomic reads if misused, missing 8-byte alignment, and behavior differences between CX8 and 386 fallback paths. Test signals are 32-bit SMP atomic tests, non-CX8 build coverage, and stress on refcounts and lockless counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/atomic64_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/atomic64_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/atomic64_64.h

Purpose: native 64-bit x86 implementation of `atomic64_t` operations.

Important APIs and control flow: read/write use one-copy access; add/sub/inc/dec and bitwise updates use locked qword instructions. Conditional-return helpers use `GEN_*_RMWcc`; fetch and return helpers use `xadd`; cmpxchg, try-cmpxchg, and xchg delegate to generic x86 exchange primitives. Fetch-and/or/xor loop with `arch_atomic64_try_cmpxchg()`.

State, dependencies, and risks: state is caller-provided atomic64 storage. Dependencies include x86 lock semantics, cmpxchg, alternatives, and rmwcc. Risks include relying on implicit x86 ordering for generic atomic contracts, contention in cmpxchg bitwise loops, and misuse for non-atomic composite state. Test signals come from generic atomic tests, lockless data-structure stress, and sanitizer/litmus validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/atomic64_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/audit.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/audit.h

Purpose: x86 audit syscall classification declarations, focused on IA32 compatibility syscall classes.

Important APIs and control flow: declares `ia32_classify_syscall()` and class arrays for directory, write, read, chattr, and signal audit categories. Runtime control flow lives in audit/syscall code that indexes these arrays to map syscall numbers to audit classes.

State, dependencies, and risks: state is the external classification arrays. Dependencies include audit core and IA32 syscall numbering. Risks include syscall table drift, class-array size mismatches, and missing x32/compat distinctions. Test signals are audit rule tests under IA32 emulation and syscall-class regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/audit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/barrier.h

Purpose: x86 memory, speculation, DMA, SMP, acquire/release, and atomic-barrier definitions.

Important APIs and control flow: 32-bit `mb/rmb/wmb` use alternatives from locked stack add to SSE fences; 64-bit defines raw `mfence/lfence/sfence` helpers. `array_index_mask_nospec()` emits compare/sbb to build an all-ones or zero mask. `barrier_nospec()` patches to `lfence` when required. SMP barriers exploit x86 ordering, locked add, compiler barriers, and `xchg` for store-mb.

State, dependencies, and risks: no direct state; effects are ordering constraints visible to all lockless code and device interactions. Dependencies include alternatives, cpufeatures, generic barrier fallbacks, and x86 TSO assumptions. Risks include weakening required speculation barriers, using DMA barriers where real device ordering is needed, and compiler reordering around acquire/release primitives. Test signals are memory-model litmus tests, nospec tests, KCSAN, and driver DMA stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/bios_ebda.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/bios_ebda.h

Purpose: access and reservation hooks for BIOS Extended BIOS Data Area and legacy BIOS memory corruption checks.

Important APIs and control flow: `get_bios_ebda()` reads the real-mode segmented EBDA pointer at physical `0x40e`, shifts it by four to compute a physical address, and returns zero when absent. `reserve_bios_regions()` is declared for boot reservation. Optional corruption-check functions are real declarations under `CONFIG_X86_CHECK_BIOS_CORRUPTION` and no-op stubs otherwise.

State, dependencies, and risks: state is firmware-provided low-memory data and kernel reservations. Dependencies include early physical mapping through `phys_to_virt`. Risks include bogus BIOS pointers, early-memory access before mappings are stable, and false confidence from optional corruption checks. Test signals are boot on legacy BIOS systems, memory reservation logs, and corruption-check configuration builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/bios_ebda.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/bitops.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/bitops.h

Purpose: x86 atomic and non-atomic bit operations, bit scanning, and hweight integration for generic bitops users.

Important APIs and control flow: set/clear/change operations choose constant byte masks or variable `bts/btr/btc` forms, locked when atomic. Test-and-* variants return carry via `GEN_BINARY_RMWcc`. `arch_test_bit()` uses compile-time constant tests or `bt`; acquire version uses a memory-clobbered byte test for constants. `__ffs`, `ffz`, `__fls`, `ffs`, `fls`, and `fls64` use compiler builtins for constants and x86 scan/tzcnt/bsr instructions for variables.

State, dependencies, and risks: state is caller-owned bitmaps, often shared with locks or atomics. Dependencies include lock prefix alternatives, barriers, rmwcc, generic instrumented bitops, endian helpers, and hweight. Risks include confusing atomic and non-atomic variants, relying on undefined zero-input scan behavior, and byte-mask assumptions for constant bit numbers. Test signals are generic bitops tests, filesystem bitmap operations, scheduler masks, KVM comments around local atomic behavior, and KCSAN reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/boot.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/boot.h

Purpose: x86 boot/decompressor constants and prototypes shared by compressed boot code and early kernel setup.

Important APIs and control flow: defines `MIN_KERNEL_ALIGN`, validates `CONFIG_PHYSICAL_ALIGN`, selects `BOOT_HEAP_SIZE` by compressor, fixes stack and page-table allocation sizes, and defines trampoline layout constants. Declarations expose decompressor sizing symbols, `decompress_kernel()`, boot params pointer, trampoline buffer, and `trampoline_32bit_src()`.

State, dependencies, and risks: state is early boot memory, decompressor heap, boot params, and trampoline code. Dependencies include page-table types and UAPI boot definitions. Risks include too-small boot heap/page table allocations, physical alignment errors, and 5-level paging or KASLR mapping underestimation. Test signals are booting compressed kernels across compressors, KASLR, 5-level paging, and verbose boot configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/boot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/bootparam_utils.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/bootparam_utils.h

Purpose: boot parameter sanitizer for bootloaders that fail to zero unknown fields.

Important APIs and control flow: `sanitize_boot_params()` checks `boot_params->sentinel`; when set, it creates a zeroed static scratch object, copies only known-safe fields listed through `BOOT_PARAM_PRESERVE()`, then overwrites the original structure. The preserve list includes screen/APM/tboot/IST/disk/system/EFI/e820/EDD/secure boot/header and confidential-computing blob fields.

State, dependencies, and risks: state is the incoming `struct boot_params`. Dependencies are boot parameter layout and `offsetof`/field sizes. Risks include missing a field that a broken bootloader validly initialized, preserving a field that should be cleared, and static scratch lifetime in unusual reentry contexts. Test signals include kexec/bootloader compatibility tests and boot logs with sentinel-triggered sanitization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/bootparam_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/bug.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/bug.h

Purpose: x86 implementation of BUG/WARN trap instructions and `__bug_table` metadata.

Important APIs and control flow: defines UD2/UDB/UD1 instruction encodings, bug flags, and `BUG()` using `_BUG_FLAGS()` plus `__builtin_unreachable()`. Under `CONFIG_GENERIC_BUG`, `_BUG_FLAGS_ASM()` emits entries into `__bug_table` with relative address, optional format/file/line, and flags. With x86-64 format arguments, `__WARN_print_arg()` routes through a static call to `__WARN_trap()`.

State, dependencies, and risks: persistent state is binary bug-table metadata; runtime state includes warning taint/once behavior in generic code. Dependencies include instrumentation boundaries, objtool annotations, static calls, and architecture trap decoding. Risks include malformed table layouts, WARN in noinstr contexts, emulator behavior on UD2, and argument capture ABI fragility. Test signals are WARN/BUG tests, objtool validation, UBSAN trap handling, and panic-on-warn paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/bugs.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/bugs.h

Purpose: x86 CPU bug handling declarations that need to be visible outside CPU initialization.

Important APIs and control flow: declares `ppro_with_ram_bug()` for 32-bit Intel builds and returns zero otherwise. Declares `cpu_bugs_smt_update()` for updating bug/mitigation state when SMT topology changes.

State, dependencies, and risks: state is CPU bug flags and mitigation state in CPU core code. Dependencies include processor structures and config-gated CPU vendors. Risks are stale bug state after SMT hotplug and build-specific behavior for old Pentium Pro errata. Test signals are CPU mitigation sysfs/status tests, SMT toggle tests, and 32-bit Intel build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/bugs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cache.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cache.h

Purpose: cache-line size and cache-alignment declarations for x86.

Important APIs and control flow: defines `L1_CACHE_SHIFT`, `L1_CACHE_BYTES`, `__read_mostly`, internode cache sizing, and a VSMP-specific `__cacheline_aligned_in_smp` override that aligns to internode cache bytes and page-aligned data.

State, dependencies, and risks: no runtime state, but layout attributes affect persistent kernel data placement. Dependencies include Kconfig cache line sizes and linker sections. Risks include false sharing if sizing is wrong, ABI/layout changes for aligned structures, and VSMP-specific alignment surprises. Test signals are build coverage, performance regressions, and cacheline alignment checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cacheflush.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cacheflush.h

Purpose: x86 cache flush interface wrapper.

Important APIs and control flow: includes generic cacheflush behavior and x86 special instructions, then declares `clflush_cache_range(void *addr, unsigned int size)` for explicit cache-line flushing over a range.

State, dependencies, and risks: state is CPU cache contents and memory attributes, not software storage. Dependencies include generic mm cacheflush APIs and x86 `clflush` support paths. Risks include flushing wrong ranges, assuming coherency effects for DMA or persistent memory beyond what the primitive guarantees, and CPU feature variation. Test signals are persistence/pmem flush tests, driver cache-maintenance users, and build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cacheflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cacheinfo.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cacheinfo.h

Purpose: cache-control and cache-init declarations for MTRR/PAT management.

Important APIs and control flow: exports `memory_caching_control` flag bits `CACHE_MTRR` and `CACHE_PAT`, plus functions to disable/enable caches, delay AP cache initialization, initialize/restore boot CPU cache state, and initialize AP cache state.

State, dependencies, and risks: state is global cache-control mode plus per-CPU MTRR/PAT hardware state. Dependencies include early CPU init and memory-type setup. Risks include disabling caches at unsafe times, AP/BP ordering bugs, and inconsistent MTRR/PAT state across CPUs. Test signals are boot on PAT/MTRR systems, CPU hotplug, memory-type selftests, and cache attribute warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cacheinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/ce4100.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/ce4100.h

Purpose: Intel CE4100 platform hooks.

Important APIs and control flow: declares `ce4100_pci_init()` and conditionally declares `sdv_serial_fixup()` when 8250 serial support is enabled, otherwise provides a no-op inline stub.

State, dependencies, and risks: state lives in PCI and serial platform setup outside this header. Dependencies include platform detection and serial configuration. Risks are build-time omission of platform fixups and stale support for a narrow embedded x86 target. Test signals are platform boot tests and config builds with/without `CONFIG_SERIAL_8250`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/ce4100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cfi.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cfi.h

Purpose: x86 kernel Control Flow Integrity and FineIBT support declarations.

Important APIs and control flow: documents traditional, IBT, kCFI, and FineIBT call layouts. Defines `enum cfi_mode`, `cfi_mode`, optional BHI thunk state, `CFI_OFFSET`, and CFI helpers. With `CONFIG_CFI`, `handle_cfi_failure()`, `cfi_get_offset()`, `cfi_get_func_hash()`, `cfi_get_func_arity()`, and optional `decode_fineibt_insn()` are available; without it, failure handling is a no-op and arity returns zero. `CFI_NOSEAL()` emits IBT no-seal annotations where applicable.

State, dependencies, and risks: state includes selected CFI mode, BHI toggle, generated function hashes, and patched call prefixes. Dependencies include Clang CFI, IBT, retpoline/call padding, alternatives, and bug trap handling. Risks include wrong offset calculations, trap decoding mismatches, and hard-to-debug failures in indirect calls. Test signals are CFI fault tests, objtool, IBT boot, BHI mitigation coverage, and module indirect-call tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cfi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/checksum.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/checksum.h

Purpose: architecture checksum dispatcher.

Important APIs and control flow: when `CONFIG_GENERIC_CSUM` is enabled, includes the generic checksum implementation. Otherwise it advertises arch copy/checksum capabilities and includes `checksum_32.h` or `checksum_64.h` according to the x86 word size.

State, dependencies, and risks: no runtime state in this wrapper. Dependencies are network checksum users, generic checksum fallbacks, and arch-specific implementations. Risks are configuration mismatches that expose wrong helper prototypes or copy/checksum feature macros. Test signals are networking checksum selftests, build matrices, and packet transmit/receive checksum validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/checksum_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/checksum_32.h

Purpose: 32-bit x86 internet checksum and copy/checksum helpers.

Important APIs and control flow: declares `csum_partial()` and `csum_partial_copy_generic()`. Kernel-to-kernel copy wrapper is unchecked; user copy wrappers call `might_sleep()`, begin user access, run the generic copy/checksum routine, and end access. `ip_fast_csum()`, `csum_fold()`, `csum_tcpudp_nofold()`, `csum_tcpudp_magic()`, `ip_compute_csum()`, and `csum_ipv6_magic()` use inline add-with-carry assembly for folded checksums.

State, dependencies, and risks: state is transient checksum accumulation and user access state. Dependencies include uaccess, IPv6 types, assembly helpers, and caller alignment/length assumptions. Risks include missing `access_ok()` style validation when direct helpers are used, odd-length handling only on final fragments, and fragile register clobbers. Test signals are networking checksum tests, fault-injection on user copies, and packet checksum offload comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/checksum_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/checksum_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/checksum_64.h

Purpose: x86-64 internet checksum primitives and declarations.

Important APIs and control flow: inline helpers fold 32-bit sums, compute fast IPv4 header checksums, build TCP/UDP pseudo-header sums, add checksums with carry, and compute IPv6 pseudo-header checksums using 64-bit add/adc. Bulk checksum/copy routines are external assembly/C functions: `csum_partial`, `csum_partial_copy_generic`, user copy wrappers, unchecked copy, and `ip_compute_csum`.

State, dependencies, and risks: state is transient sum/carry handling and user access in external routines. Dependencies include byteorder, IPv6 types, and low-level checksum implementations. Risks include mixing folded/unfolded sums, assuming 64-bit alignment, and user-copy exception paths. Test signals are network stack checksum tests, IPv4/IPv6 packet validation, and uaccess fault tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/checksum_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/clock_inlined.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/clock_inlined.h

Purpose: tiny inlined clocksource and clockevent hooks for x86 TSC paths.

Important APIs and control flow: `arch_inlined_clocksource_read()` returns `rdtsc_ordered()`. `arch_inlined_clockevent_set_next_coupled()` writes the next deadline cycle to `MSR_IA32_TSC_DEADLINE`.

State, dependencies, and risks: state is hardware TSC and TSC-deadline MSR state. Dependencies include `asm/tsc.h`, MSR accessors, and clocksource/clockevent core expectations. Risks include using TSC before it is reliable, MSR writes on unsupported CPUs, and ordering assumptions around time reads. Test signals are timekeeping tests, clockevent programming, TSC deadline timer boot, and suspend/resume timing validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/clock_inlined.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/clocksource.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/clocksource.h

Purpose: x86 vDSO clocksource usage tracking.

Important APIs and control flow: declares `vclocks_used`. `vclock_was_used()` reads the bitmask with `READ_ONCE()` and tests a vclock bit. `vclocks_set_used()` ORs in a bit and writes it back with `WRITE_ONCE()`.

State, dependencies, and risks: state is a global bitmask describing which vDSO clock modes have been used. Dependencies include vDSO clocksource identifiers and one-copy access primitives. Risks include non-atomic read-modify-write lost updates if called concurrently in unexpected contexts, and stale vclock accounting. Test signals include vDSO time tests and clocksource switching tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/clocksource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cmdline.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cmdline.h

Purpose: early x86 command-line parsing declarations.

Important APIs and control flow: exposes `builtin_cmdline` and declares `cmdline_find_option_bool()` plus `cmdline_find_option()` for scanning boot command line strings with a fixed output buffer.

State, dependencies, and risks: state is static or bootloader-provided command-line storage. Dependencies include `COMMAND_LINE_SIZE` from setup definitions. Risks include buffer sizing, duplicate options, early parsing before full string helpers are available, and differences between built-in and bootloader command lines. Test signals are boot parameter tests and early option parsing coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cmdline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cmpxchg.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cmpxchg.h

Purpose: generic x86 exchange, compare-exchange, try-compare-exchange, and xadd primitives for 1/2/4/8-byte operands.

Important APIs and control flow: size selector macros map qword support out on 32-bit. `__xchg_op()` emits `xchg` or `xadd` per operand size and reports wrong sizes through compile-time/link errors. `__raw_cmpxchg()` and `__raw_try_cmpxchg()` emit lockable cmpxchg variants and update the expected-value pointer on failure. Public macros include `arch_xchg`, `arch_cmpxchg`, sync/local variants, `arch_try_cmpxchg`, and `xadd`.

State, dependencies, and risks: state is caller-owned memory and expected-value variables. Dependencies include lock-prefix alternatives, cpufeatures, and 32/64-bit cmpxchg extension headers. Risks include unsupported operand sizes, accidental local variants in SMP-shared state, qword use on 32-bit without the right helper, and inline-asm constraint bugs. Test signals include atomic tests, cmpxchg64/128 build coverage, and lockless algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cmpxchg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cmpxchg_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cmpxchg_32.h

Purpose: 32-bit x86 64-bit compare-exchange support.

Important APIs and control flow: `union __u64_halves` splits 64-bit values into low/high words for `cmpxchg8b`. Native `__cmpxchg64` and `__try_cmpxchg64` use locked or local `cmpxchg8b`. With `CONFIG_X86_CX8`, public macros alias directly. Without it, `arch_cmpxchg64*` and `arch_try_cmpxchg64*` use alternatives to call `cmpxchg8b_emu` on old CPUs or use real `cmpxchg8b` when available.

State, dependencies, and risks: state is 64-bit memory accessed from 32-bit code. Dependencies include CX8 detection, `cmpxchg8b_emu`, and correct register splitting. Risks include using qword atomics before feature alternatives are usable, emulation correctness on 386/486, and alignment requirements. Test signals are 32-bit atomic64 tests and non-CX8 build/runtime coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cmpxchg_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cmpxchg_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cmpxchg_64.h

Purpose: x86-64 64-bit and 128-bit compare-exchange support.

Important APIs and control flow: qword macros validate `sizeof(*ptr) == 8` and delegate to generic cmpxchg/try-cmpxchg. `union __u128_halves` splits 128-bit values for `cmpxchg16b`; `arch_cmpxchg128`, local variants, and try variants emit locked or local `cmpxchg16b` and return old values or success flags. `system_has_cmpxchg128()` checks `X86_FEATURE_CX16`.

State, dependencies, and risks: state is qword or 16-byte memory, usually lockless shared objects. Dependencies include CX16 support, alignment expectations, and compiler support for `u128`. Risks include using cmpxchg128 on unsupported hardware, insufficient alignment, and local variants on shared data. Test signals are 128-bit cmpxchg build tests, lockless algorithms using double-word CAS, and CPU feature fallback tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cmpxchg_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/coco.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/coco.h

Purpose: x86 confidential-computing vendor and encryption-mask interface.

Important APIs and control flow: `enum cc_vendor` identifies none, AMD, or Intel. With `CONFIG_ARCH_HAS_CC_PLATFORM`, global `cc_vendor` and `cc_mask` are exported; `cc_get_mask()`, `cc_set_mask()`, `cc_mkenc()`, `cc_mkdec()`, and `cc_random_init()` support address encryption-bit conversion and random initialization. Without support, vendor is none, mask is zero, conversions are identity, and random init is a no-op.

State, dependencies, and risks: state is global confidential-computing vendor/mask configuration. Dependencies include platform detection, memory encryption code, and random initialization. Risks include applying the wrong C-bit mask to physical addresses, changing mask too late, and identity stubs hiding missing platform support. Test signals are SEV/TDX boot, encrypted/decrypted mapping tests, and guest memory acceptance paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/coco.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/compat.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/compat.h

Purpose: x86 32-bit and x32 compatibility ABI types and syscall-mode helpers.

Important APIs and control flow: defines compat uid/gid/mode/dev/ipc types, `compat_stat`, packed flock64 need, `compat_statfs`, and `COMPAT_UTS_MACHINE`. `in_x32_syscall()` checks the x32 syscall bit when enabled; `in_32bit_syscall()` combines IA32 and x32; `in_compat_syscall()` overrides the generic implementation under `CONFIG_COMPAT`. x32 may override siginfo copying.

State, dependencies, and risks: state comes from current task registers and syscall number bits. Dependencies include generic compat ABI, processor/user32 definitions, and syscall numbering. Risks include struct layout drift from userspace ABI, incorrect x32/IA32 classification, and time/alignment differences. Test signals are compat syscall tests, x32 ABI tests, stat/statfs layout checks, and ptrace/signal compat tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cpu.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cpu.h

Purpose: shared x86 CPU initialization, hotplug, split-lock, microcode, and architecture capability declarations.

Important APIs and control flow: declares CPU restart/hotplug hooks, APERF/MPERF init, `mwait_usable()`, signature extraction helpers, optional split-lock/bus-lock handling, IA32 feature-control init, CET disable, Intel microcode helpers, architecture capability MSR reader, and `cpus_stop_mask`. Unsupported feature blocks provide no-op or false-returning stubs.

State, dependencies, and risks: state includes CPU feature state, microcode metadata, split-lock policy, and stop masks. Dependencies include topology, cpumasks, IBT/CET, and vendor-specific code. Risks include config-gated stubs masking missing behavior, split-lock exception handling in user/guest paths, and microcode signature mismatches. Test signals are CPU hotplug, microcode loading, split-lock selftests, and capability MSR tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cpu_device_id.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cpu_device_id.h

Purpose: helper macros for declaring x86 CPU match tables used by drivers and CPU-specific quirks.

Important APIs and control flow: `VFM_*` macros encode/decode vendor/family/model into the `x86_vfm` initializer-compatible layout. `X86_MATCH_CPU()` fills `struct x86_cpu_id` with vendor, family, model, stepping, feature, type, valid flag, and driver data. Shorthand macros match vendor/family/feature/model, VFM encodings, stepping ranges, and CPU type. `x86_match_cpu()` and `x86_match_min_microcode_rev()` perform runtime table matching.

State, dependencies, and risks: state is static match tables and runtime CPU info. Dependencies include mod device table ABI, Intel family constants, and processor vendor IDs. Risks include bad initializer casts, stepping masks outside legal ranges, stale family/model IDs, and file2alias expectations. Test signals are module alias generation, CPU quirk tests, and vendor/model match coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cpu_device_id.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cpu_entry_area.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cpu_entry_area.h

Purpose: defines the per-CPU entry-area virtual layout used by x86 entry, exception, GDT/TSS, and debug-store code.

Important APIs and control flow: 64-bit exception stack macros build guarded IST stack layout, including optional VC stacks for AMD memory encryption. `struct cpu_entry_area` maps GDT, entry stack, optional 32-bit doublefault stack, TSS, 64-bit exception stacks, debug store, and debug buffers. APIs declare setup and PTE mapping functions, `get_cpu_entry_area()`, `cpu_entry_stack()`, and helpers to find current IST top/bottom addresses.

State, dependencies, and risks: persistent state is per-CPU virtual aliases to backing storage; the struct itself is layout contract, not directly allocated. Dependencies include processor/TSS types, pgtable areas, Intel DS, percpu, and entry assembly offsets. Risks include layout changes breaking assembly, guard-page mistakes, RO/RW mapping mismatch, and confidential-computing VC stack sizing. Test signals are boot entry paths, NMI/DF/MCE/#VC handling, debug-store use, and objtool/offset checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cpu_entry_area.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cpufeature.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cpufeature.h

Purpose: runtime and static x86 CPU feature testing API.

Important APIs and control flow: `enum cpuid_leafs` maps CPUID words to `x86_capability` indexes. Macros test, set, clear, and force CPU feature bits. `cpu_feature_enabled()` uses disabled masks and `static_cpu_has()`. `_static_cpu_has()` uses `asm goto` and alternatives to patch feature tests after boot. Bug-feature wrappers alias to normal capability operations.

State, dependencies, and risks: state is `boot_cpu_data`, per-CPU `cpu_info`, capability arrays, set/clear masks, and alternative patching status. Dependencies include processor definitions, bitops, alternatives, and generated feature masks. Risks include testing raw CPU capability when kernel enablement is required, forcing features after alternatives are patched, and stale dependency clearing. Test signals are CPU feature enumeration, alternatives patch tests, mitigation feature toggles, and CPUID masking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cpufeature.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cpufeatures.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cpufeatures.h

Purpose: canonical numeric definitions for x86 CPU feature and bug bits.

Important APIs and control flow: defines `NCAPINTS`, `NBUGINTS`, hundreds of `X86_FEATURE_*` values by CPUID word and bit, Linux-synthesized/scattered feature words, and `X86_BUG()` encodings for vulnerability/erratum bits. Comments with quoted strings drive `/proc/cpuinfo` display names; comments also require cpuid dependency table updates when feature dependencies are added.

State, dependencies, and risks: no direct runtime state, but every constant indexes capability arrays and user-visible feature reporting. Dependencies include CPUID discovery, `/proc/cpuinfo` flag tables, alternatives, mitigations, and KVM exposure. Risks include reusing non-free bits, wrong word assignments, missing dependency-table updates, and ABI-visible flag name changes. Test signals are CPU feature table builds, `/proc/cpuinfo`, KVM CPUID tests, and mitigation status coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cpufeatures.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cpuid/api.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cpuid/api.h

Purpose: raw and structured CPUID access helpers plus hypervisor-base and descriptor parsing utilities.

Important APIs and control flow: `native_cpuid()` issues CPUID with EAX/ECX inputs and four outputs. `cpuid()`, `cpuid_count()`, single-register helpers, `cpuid_leaf()`, `cpuid_subleaf()`, and register-specific macros enforce output object sizes. `cpuid_function_is_indexed()` lists leaves with subleaf semantics. `cpuid_base_hypervisor()` scans hypervisor CPUID ranges for a 12-byte signature and required leaf count. `cpuid_leaf_0x2()` sanitizes descriptor output, and `for_each_cpuid_0x2_desc()` iterates descriptor table entries.

State, dependencies, and risks: state is CPU/hypervisor CPUID output; no persistent storage here. Dependencies include paravirt `__cpuid`, cpuid types, build bugs, and early-boot-safe `__builtin_memcmp`. Risks include using indexed leaves as flat leaves, stale ECX input, early instrumentation constraints, and malformed descriptor hardware output. Test signals are CPU discovery, hypervisor detection, cache/TLB enumeration, and CPUID emulation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cpuid/api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cpuid/types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cpuid/types.h

Purpose: CPUID register containers and parsed leaf 0x2 descriptor type definitions.

Important APIs and control flow: defines `struct cpuid_regs`, `enum cpuid_regs_idx`, selected leaf constants, `union leaf_0x2_regs`, packed cache/TLB descriptor type enums, `struct leaf_0x2_table`, the external `cpuid_0x2_table[256]`, and `TLB_0x63_2M_4M_ENTRIES`. Static assertions keep packed enum widths at one byte.

State, dependencies, and risks: state is external descriptor table data and caller-filled CPUID register unions. Dependencies include Linux integer types and build assertions. Risks include descriptor type overlap, enum packing differences under sparse/checker, and table entries drifting from Intel descriptor meanings. Test signals are CPUID descriptor parser tests, cache/TLB info output, and compile-time assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cpuid/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cpuidle_haltpoll.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cpuidle_haltpoll.h

Purpose: arch hooks for haltpoll cpuidle enable/disable on x86.

Important APIs and control flow: declares `arch_haltpoll_enable(unsigned int cpu)` and `arch_haltpoll_disable(unsigned int cpu)`. Actual policy and state transitions live in the haltpoll/cpuidle implementation.

State, dependencies, and risks: state is per-CPU haltpoll behavior outside the header. Dependencies include cpuidle/haltpoll drivers and CPU hotplug paths. Risks include enabling haltpoll on unsuitable CPUs or missing disable during hotplug. Test signals are haltpoll driver tests, virtualization latency measurements, and CPU online/offline coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cpuidle_haltpoll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cpumask.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cpumask.h

Purpose: x86-special cpumask helpers for early/instrumentation-sensitive online CPU checks.

Important APIs and control flow: declares `setup_cpu_local_masks()`. For SMP builds, `arch_cpu_online()` tests `cpu_online_mask` with `arch_test_bit()` and `arch_cpumask_clear_cpu()` clears with `arch_clear_bit()` after `cpumask_check()`. UP builds return CPU 0 online and no-op clear. `arch_cpu_is_offline()` wraps the negated online check.

State, dependencies, and risks: state is global and per-CPU cpumasks. Dependencies include generic cpumask and x86 bitops. Risks include using instrumented generic checks in NMI/MCE paths, stale online masks during hotplug, and invalid CPU indexes. Test signals are CPU hotplug, NMI/MCE paths on offlined CPUs, and cpumask selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/cpumask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/crash.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/crash.h

Purpose: x86 crash-kernel and kexec crash support declarations.

Important APIs and control flow: declares `crash_load_segments()`, `crash_setup_memmap_entries()`, and `crash_smp_send_stop()`. Implementations prepare crash image segments, populate boot-parameter memory maps, and stop secondary CPUs during crash transitions.

State, dependencies, and risks: state includes `struct kimage`, boot params, memory maps, and CPU stop state. Dependencies include kexec, e820/bootparam code, and SMP IPI/stop machinery. Risks include bad crash memory maps, failure to quiesce CPUs, and differences between normal and panic contexts. Test signals are kdump boot tests, crashkernel reservation tests, and panic/kexec integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/crash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/crash_reserve.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/crash_reserve.h

Purpose: x86 crashkernel reservation limits and default low-memory sizing.

Important APIs and control flow: defines 16 MiB `CRASH_ALIGN`, low/high reservation maxima by 32/64-bit mode, `DEFAULT_CRASH_KERNEL_LOW_SIZE`, and `HAVE_ARCH_ADD_CRASH_RES_TO_IOMEM_EARLY`. `crash_low_size_default()` returns zero on 32-bit and on 64-bit returns the maximum of SWIOTLB default plus 8 MiB and 256 MiB.

State, dependencies, and risks: state is crashkernel reservation sizing. Dependencies include SWIOTLB sizing and physical address limits for paging mode transitions. Risks include reserving memory above the kdump kernel's addressing mode, underallocating low memory for DMA/SWIOTLB, and architecture-specific alignment waste. Test signals are crashkernel command-line parsing, kdump boot, and 5-level-to-4-level paging jump scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/crash_reserve.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/current.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/current.h

Purpose: x86 implementation of the `current` task accessor.

Important APIs and control flow: declares cache-hot per-CPU `current_task` and a const per-CPU segment override alias `const_current_task`. `get_current()` reads `const_current_task` through segment support when enabled, otherwise uses stable per-CPU read of `current_task`. The macro `current` maps to `get_current()`.

State, dependencies, and risks: state is per-CPU current task pointer. Dependencies include x86 percpu access mode, linker-provided alias, and scheduler context switching. Risks include wrong per-CPU segment setup, stale current pointer during entry/exit transitions, and assumptions about const alias availability. Test signals are scheduler/context switch tests, entry code, and percpu access build variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/current.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/debugreg.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/debugreg.h

Purpose: x86 debug-register access, breakpoint save/restore, AMD address-mask hooks, and debug-control MSR helpers.

Important APIs and control flow: `native_get_debugreg()` and `native_set_debugreg()` switch on DR0-DR3, DR6, and DR7; DR7 access is volatile to avoid unsafe reordering under SEV-ES #VC handling. `hw_breakpoint_disable()` resets DR7 and address registers. `local_db_save()` skips hypervisor cases without active breakpoints, disables DR7 when nonzero, and returns the old value; `local_db_restore()` restores after a compiler barrier. Optional AMD mask hooks and `get/update_debugctlmsr()` wrap debug-control MSR access.

State, dependencies, and risks: state includes hardware debug registers, per-CPU `cpu_dr7`, AMD debug masks, and DEBUGCTL MSR. Dependencies include uapi debugreg bits, cpufeatures, MSRs, paravirt overrides, and breakpoint core. Risks include unsafe DR7 access in entry/NMI contexts, losing breakpoints around critical sections, and SEV-ES reordering. Test signals are hw_breakpoint selftests, perf debug events, SEV-ES boot, and ptrace debug register tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/debugreg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/delay.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/delay.h

Purpose: x86 delay-loop selection declarations.

Important APIs and control flow: includes generic delay APIs and declares `use_tsc_delay()`, `use_tpause_delay()`, and `use_mwaitx_delay()` for selecting TSC, TPAUSE, or MWAITX-backed delay implementations during CPU init.

State, dependencies, and risks: state is global/per-CPU delay backend selection in implementation files. Dependencies include TSC reliability, waitpkg/mwaitx features, and early init ordering. Risks include selecting a delay source before feature calibration or using unavailable low-power instructions. Test signals are boot calibration logs, delay accuracy tests, and CPU feature combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/delay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/desc.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/desc.h

Purpose: x86 descriptor-table manipulation helpers for GDT, IDT, LDT, TSS, TLS, and entry stack mappings.

Important APIs and control flow: `fill_ldt()` converts `user_desc` to an LDT descriptor. GDT helpers return writable per-CPU GDT, read-only CPU entry-area GDT, or physical addresses. `pack_gate()`/`idt_init_desc()` build IDT gates. Native load/store functions issue `lgdt`, `lidt`, `ltr`, `lldt`, `sgdt`, `sidt`, and `str`. TSS/LDT descriptor setup writes GDT entries; `native_load_tr_desc()` temporarily swaps from RO fixmap GDT to writable GDT on 64-bit. TSS limit helpers reload or invalidate TR around IO bitmap behavior.

State, dependencies, and risks: state is per-CPU GDT/TSS/TLS/IDT and cached TSS limit flags. Dependencies include descriptor definitions, CPU entry area, paravirt, thread flags, and entry setup. Risks include descriptor layout corruption, preemption-sensitive TSS limit updates, RO/RW GDT mismatch, and user LDT corner cases. Test signals include boot/entry tests, modify_ldt tests, IO bitmap tests, CPU hotplug, and virtualization exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/desc_defs.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/desc_defs.h

Purpose: x86 segment, system, and interrupt descriptor bit layouts shared by C and assembly.

Important APIs and control flow: defines low-level descriptor flags, high-level data/code/TSS constants, `struct desc_struct`, `GDT_ENTRY_INIT`, gate type enums, `struct ldttss_desc`, `struct idt_bits`, `struct idt_data`, `struct gate_struct`, `struct desc_ptr`, and access-right bit masks. `gate_offset()` and `gate_segment()` decode gate fields outside setup builds.

State, dependencies, and risks: no runtime state; structures are ABI contracts for CPU descriptor tables and assembly offsets. Dependencies include x86 hardware descriptor formats and `CONFIG_X86_64`. Risks include packed bitfield layout assumptions, incorrect high/low offset handling, and changing values consumed by assembly or hardware. Test signals are boot descriptor setup, IDT/GDT inspection, modify_ldt, and compile-time layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/desc_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/device.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/device.h

Purpose: x86 device architecture-data placeholders.

Important APIs and control flow: defines empty `struct dev_archdata` and `struct pdev_archdata`, satisfying generic driver-core and platform-device expectations without adding x86-specific fields.

State, dependencies, and risks: no state. Dependencies are generic device model structure embedding. Risks are future extensions changing struct size/layout in generic objects and drivers assuming archdata contains fields. Test signals are broad driver-core build and device registration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/div64.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/div64.h

Purpose: optimized 64-bit division and multiply/divide helpers for x86.

Important APIs and control flow: on 32-bit, `do_div()` modifies the dividend in place and returns the remainder, using power-of-two shifts or `divl` with high-word reduction. `div_u64_rem()`, `mul_u32_u32()`, and `add_u64_u32()` provide efficient 32-bit assembly paths. On 64-bit, generic `div64` is used plus `mul_u64_add_u64_div_u64()` and `mul_u64_u32_div()` using `mulq`, optional add/adc, then `divq`.

State, dependencies, and risks: state is caller variables modified by macros. Dependencies include compiler constraints, `ilog2`, and generic div64. Risks include divide overflow causing #DE on 64-bit helper, macro side effects, zero divisors, and clang/gcc codegen differences. Test signals are arithmetic unit tests, timekeeping frequency calculations, and 32-bit build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/div64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/dma-mapping.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/dma-mapping.h

Purpose: x86 hook for generic DMA mapping operations.

Important APIs and control flow: declares global `dma_ops` and returns it from `get_arch_dma_ops()`. Generic DMA code uses this to dispatch map/unmap/sync behavior.

State, dependencies, and risks: state is the selected DMA operations table, commonly influenced by IOMMU, SWIOTLB, or direct DMA setup. Dependencies include DMA-mapping core. Risks include `dma_ops` not initialized before use or being inconsistent with device/IOMMU state. Test signals are DMA API debug, IOMMU/SWIOTLB boot tests, and driver DMA mapping coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/dma-mapping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/dma.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/dma.h

Purpose: legacy ISA 8237 DMA controller constants and inline programming helpers.

Important APIs and control flow: defines DMA zones, controller I/O ports, page/address/count registers, and mode bits. Optional `claim_dma_lock()`/`release_dma_lock()` guard programming. Helpers enable/disable channels, clear the flip-flop, set mode/page/address/count, and read residue. Channel 0-3 byte mode and 5-7 word mode differ in address/count shifting and page-register masking.

State, dependencies, and risks: state is hardware DMA controller registers, page registers, flip-flop position, and optional `dma_spin_lock`. Dependencies include port I/O, ISA DMA API, and physical address constraints below 16 MiB. Risks include crossing 64K/128K boundaries, programming without the DMA lock, odd byte counts on 16-bit channels, and legacy hardware assumptions. Test signals are ISA DMA users, floppy/sound legacy drivers, DMA API debug, and emulator hardware tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/dmi.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/dmi.h

Purpose: x86 DMI allocation and mapping helpers for early firmware table scanning.

Important APIs and control flow: `dmi_alloc()` allocates from early `extend_brk()` with integer alignment. Remap macros map early DMI through `early_memremap`/`early_memunmap` and later DMI through `memremap(..., MEMREMAP_WB)`/`memunmap`.

State, dependencies, and risks: state is early boot brk allocation and DMI mapped memory. Dependencies include setup/early memory mapping APIs. Risks include allocating before memory management is ready, mapping firmware tables with wrong attributes, and lifetime mismatch between early and late mappings. Test signals are DMI scan boot logs, DMI-based quirk activation, and early boot memory tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/dmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/doublefault.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/doublefault.h

Purpose: double-fault initialization and shim declarations.

Important APIs and control flow: `doublefault_init_cpu_tss()` is declared on 32-bit and is a no-op inline on other builds. `doublefault_shim()` is declared `asmlinkage` and `__noreturn` for the low-level double-fault path.

State, dependencies, and risks: state includes the 32-bit double-fault TSS/stack setup and fatal exception path. Dependencies include entry assembly and descriptor setup. Risks include bad TSS setup causing triple faults, stack exhaustion, and no-return control flow assumptions. Test signals are fault-injection/entry tests and 32-bit boot coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/doublefault.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/dwarf2.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/dwarf2.h

Purpose: assembly-only aliases for DWARF CFI directives and section selection.

Important APIs and control flow: maps `CFI_*` macros to `.cfi_*` assembler directives and warns if included from C. Non-vDSO builds emit CFI into `.debug_frame`; vDSO builds emit both `.eh_frame` and `.debug_frame` so runtime and debug unwind data are available.

State, dependencies, and risks: state is emitted unwind/debug metadata in object files. Dependencies include assembler CFI support and vDSO build mode. Risks include including from C, missing unwind data for offline debugging, and unwanted runtime `.eh_frame` in kernel objects. Test signals are assembly builds, unwind/debug validation, and vDSO unwind tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/dwarf2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/e820/api.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/e820/api.h

Purpose: public API for x86 E820 firmware memory map processing and reservation.

Important APIs and control flow: declares the active, kexec, and firmware E820 tables plus `pci_mem_start`. Query helpers test whether ranges are mapped by type. Range add/update/remove helpers mutate tables; update helpers sanitize/sort/merge. Additional APIs compute RAM PFN limits, allocate/reserve through memblock, finish early parameters, reserve resources, set up memory and PCI gaps, reallocate tables, register nosave regions, and query entry type. `is_ISA_range()` checks full containment in the legacy ISA window.

State, dependencies, and risks: state is global E820 table variants and memblock/resource reservations. Dependencies include boot params, EFI/firmware memory maps, kexec, and resource tree setup. Risks include overlapping ranges, wrong type conversion, losing firmware map fidelity, and ISA/PCI gap mistakes. Test signals are boot memory maps, kexec/kdump, memblock debug, hibernation nosave regions, and E820 parser tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/e820/api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/e820/types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/e820/types.h

Purpose: E820 memory type values, entry/table structures, and legacy physical memory range constants.

Important APIs and control flow: defines standard and Linux-specific `enum e820_type` values for RAM, reserved, ACPI, NVS, unusable, PMEM, legacy PRAM, and soft-reserved memory. `struct e820_entry` is packed and describes `[addr, addr+size-1]` ranges. `E820_MAX_ENTRIES` extends zeropage capacity by a NUMA heuristic. `struct e820_table` stores entry count and fixed array. Constants identify ISA, BIOS, high-memory, and BIOS ROM ranges.

State, dependencies, and risks: state is memory-map arrays passed through boot and setup. Dependencies include UAPI bootparam E820 limits and NUMA sizing. Risks include table overflow on large systems, packed enum layout assumptions, and nonstandard PRAM type handling. Test signals are firmware memory map parsing, NUMA-heavy boots, EFI-to-E820 conversion, and `/proc/iomem` validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/e820/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/edac.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/edac.h

Purpose: x86 EDAC atomic scrub helper.

Important APIs and control flow: `edac_atomic_scrub()` walks a memory range as 32-bit words and issues `lock addl $0` to each word, carefully forcing an atomic read-modify-write without changing the value.

State, dependencies, and risks: state is target memory and cache coherency observed by ECC hardware. Dependencies include callers passing valid, 4-byte-addressable memory. Risks include size truncation for non-multiple-of-four lengths, using on MMIO or invalid memory, and performance impact from locked operations. Test signals are EDAC scrub paths, ECC error-injection tests, and build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/edac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/efi.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/efi.h

Purpose: x86 EFI runtime, stub, mixed-mode, memory-map, and boot-mode interface.

Important APIs and control flow: declares EFI firmware/config addresses, mixed-mode stack, runtime mapping constants, argument-count checking for assembler thunks, FPU begin/end wrappers, and 64-bit `efi_call()`/`arch_efi_call_virt()` with optional IBT disable/restore. EFI setup functions reserve ranges, allocate/setup page tables, map runtime regions, apply quirks, sync mappings, and unmap boot services. Mixed-mode support maps native arguments to 32-bit EFI thunk calls, zeroes upper halves of output pointers, splits 64-bit arguments, widens status values, and dispatches through `efi_fn_call()`.

State, dependencies, and risks: state includes EFI memory maps, runtime mappings, firmware tables, mixed-mode stack, boot mode, and runtime-map exports. Dependencies include FPU API, page tables, TLB/MMU context, IBT, EFI core, KASAN stub constraints, and boot compressed code. Risks include thunk argument count/width mistakes, runtime mapping instability across kexec, calling firmware with wrong FPU/IBT state, and mixed 32/64-bit pointer truncation. Test signals are EFI boot/runtime service tests, mixed-mode boot, kexec, secure boot mode checks, and runtime map sysfs coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/efi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/elf.h

Purpose: x86 ELF ABI constants, register dump layout, process personality setup, vDSO aux vector setup, and mmap layout hooks.

Important APIs and control flow: defines ELF register sets, relocation constants for i386/x86-64, ELF class/data/arch, architecture checks, platform init macros, and core-register copy macros for 32-bit and 64-bit. Compat paths validate IA32/x32 binaries, start compat threads, and set IA32 personality. `ELF_ET_DYN_BASE`, `ELF_HWCAP`, `ELF_HWCAP2`, `elf_read_implies_exec()`, `ARCH_DLINFO*`, `mmap_is_ia32()`, stack randomization masks, and vDSO setup declarations integrate exec with mm and auxv.

State, dependencies, and risks: state is current thread registers, fs/gs bases, personality flags, mm vDSO context, CPU capabilities, and VA alignment settings. Dependencies include ptrace/user ABI, vdso, fsgsbase, ia32/x32 support, and binfmt_elf. Risks include ABI-incompatible register ordering, wrong exec-stack policy for compat processes, vDSO auxv errors, and mmap base regressions. Test signals are ELF exec tests, core dump validation, compat/x32 tests, ASLR tests, and vDSO signal-return checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/elfcore-compat.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/elfcore-compat.h

Purpose: compat ELF core dump layout helpers for x86-64 supporting both i386 and x32 ABIs.

Important APIs and control flow: aliases `compat_elf_gregset_t` to 64-bit user regs for x32-sized compat regsets. Defines `struct i386_elf_prstatus` for the smaller i386 layout. `PRSTATUS_SIZE` and `SET_PR_FPVALID()` choose the correct layout based on `user_64bit_mode(task_pt_regs(current))`.

State, dependencies, and risks: state is current task mode and core-dump status buffers. Dependencies include `asm/user32.h`, ptrace registers, and compat ELF core code. Risks include writing `pr_fpvalid` at the wrong offset, misclassifying x32 versus i386 mode, and ABI-visible core dump layout regressions. Test signals are core dumps from 32-bit and x32 tasks on x86-64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/elfcore-compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/emergency-restart.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/emergency-restart.h

Purpose: declaration for immediate machine restart on x86.

Important APIs and control flow: declares `machine_emergency_restart()`, used by panic/reboot code when normal shutdown paths are unavailable or unsafe.

State, dependencies, and risks: state is hardware reset pathway outside this header. Dependencies include reboot implementation and platform reset mechanisms. Risks include failing to reset on some firmware/platforms or bypassing device quiesce intentionally. Test signals are reboot/panic tests and platform watchdog/reset coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/emergency-restart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/emulate_prefix.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/emulate_prefix.h

Purpose: byte prefixes that mark hypervisor instruction-emulation escape sequences.

Important APIs and control flow: defines `__XEN_EMULATE_PREFIX` and `__KVM_EMULATE_PREFIX` as `ud2` followed by ASCII tags. Callers embed these bytes before code sequences that a hypervisor recognizes and emulates.

State, dependencies, and risks: no software state, but emitted bytes become executable instruction stream metadata. Dependencies are Xen/KVM emulation decoders. Risks include corrupting instruction streams, hypervisor mismatch, and intentional UD2 trapping on native execution. Test signals are paravirtualization boot tests and KVM/Xen emulation path tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/emulate_prefix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/enclu.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/enclu.h

Purpose: SGX ENCLU leaf constants for enclave entry/exit/resume operations.

Important APIs and control flow: defines `EENTER`, `ERESUME`, and `EEXIT` leaf numbers. Actual instruction issuing and state transitions occur in SGX assembly/C code.

State, dependencies, and risks: state is SGX enclave CPU state outside this header. Dependencies include SGX feature support and ENCLU call sites. Risks include using wrong leaf numbers or exposing SGX paths on unsupported hardware. Test signals are SGX selftests and enclave transition tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/enclu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/entry-common.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/entry-common.h

Purpose: x86 hooks for generic syscall/interrupt entry and exit handling.

Important APIs and control flow: `arch_enter_from_user_mode()` performs `CONFIG_DEBUG_ENTRY` checks on EFLAGS, SMAP/XenPV AC state, user mode, thread stack, and regs location. `arch_exit_work()` fires user-return notifiers, updates the IO bitmap, and loads FPU state when needed. `arch_exit_to_user_mode_prepare()` asserts FPU consistency, handles pending work, updates FRED RSP0, clears compat status bits, and optionally issues IBPB before user return. `arch_exit_to_user_mode()` clears AMD divider state.

State, dependencies, and risks: state includes task thread flags/status, TSS IO bitmap, FPU registers, FRED state, and per-CPU branch prediction barrier flag. Dependencies include nospec branch mitigation, IO bitmap, FPU API, user-return notifier, and debug entry code. Risks include returning to user mode with stale compat flags, FPU state inconsistency, missing IBPB, or incorrect stack/regs assumptions. Test signals are syscall selftests, ptrace compat restart tests, FPU lazy-load tests, and entry debug assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/entry-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/espfix.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/espfix.h

Purpose: ESPFIX64 per-CPU stack declarations and initialization hooks.

Important APIs and control flow: under `CONFIG_X86_ESPFIX64`, declares read-mostly per-CPU `espfix_stack` and `espfix_waddr`, plus `init_espfix_bsp()` and `init_espfix_ap()`. Without ESPFIX64, AP init is a no-op stub.

State, dependencies, and risks: state is per-CPU ESPFIX mapping/stack addresses used to handle 16-bit stack segment return quirks. Dependencies include per-CPU setup, CPU bringup, and entry/IRET paths. Risks include missing AP initialization and regressions in legacy 16-bit compat returns. Test signals are espfix-specific tests, 16-bit return/IRET coverage, and CPU hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/espfix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/exec.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/exec.h

Purpose: placeholder header for x86 `arch_align_stack()` integration.

Important APIs and control flow: the file only contains a comment saying `arch_align_stack()` is defined here. There are no declarations or inline definitions in this source snapshot, so generic exec behavior relies on other headers or default definitions.

State, dependencies, and risks: no state. Dependencies are implicit exec/stack-alignment integration points. Risk is that consumers expecting an x86-specific declaration in this header may silently use defaults or fail if include expectations change. Test signals are exec/ASLR stack alignment tests and build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/exec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/extable.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/extable.h

Purpose: x86 exception table entry format and fixup handler declarations.

Important APIs and control flow: `struct exception_table_entry` stores relative instruction, fixup, and data/type fields. `ARCH_HAS_RELATIVE_EXTABLE` declares relative-entry semantics. `swap_ex_entry_fixup()` swaps sort entries while adjusting relative offsets. Declarations expose `fixup_exception()`, `ex_get_fixup_type()`, `early_fixup_exception()`, optional MCE MSR handler, and optional BPF JIT exception handler.

State, dependencies, and risks: persistent state is the sorted exception table emitted by assembly/inline asm. Runtime state is fault context in `pt_regs`. Dependencies include extable fixup types, fault handling, MCE, and BPF JIT. Risks include relative offset miscalculation during sorting, wrong fixup type data, and early exception handling before full infrastructure is ready. Test signals are uaccess/MSR fault injection, BPF JIT fault tests, machine-check paths, and extable sort validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/extable.h -->
