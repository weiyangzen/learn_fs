# Research: subset-b-000765

Grouped research for PowerPC crypto helpers, low-level architecture headers, and Book3S 32/64 MMU support in the Ceph client source tree.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/ppc-xlate.pl -->
# sources/distributed-fs/ceph-client/arch/powerpc/crypto/ppc-xlate.pl

Purpose: translates portable PowerPC assembly input into assembler syntax accepted by Linux, AIX, and macOS assemblers. It is used by the PowerPC crypto assembly generation path to normalize symbol naming, directives, local labels, register syntax, and newer instruction encodings.

Important APIs/types/functions: command-line inputs are `flavour` and output path. Directive handlers include `$globl`, `$text`, `$machine`, `$size`, `$asciz`, and `$quad`. Mnemonic shims include `cmplw`, `bdnz`, `bltlr`, `bnelr`, `beqlr`, `extrdi`, `vmr`, `mtspr`, `mfspr`, VSX unaligned memory helpers, and PowerISA 2.07 crypto helpers such as `vcipher`, `vshasigmaw`, and `vpmsumd`.

Control flow: the script opens the output as stdout, emits `<asm/ppc_asm.h>` for Linux, then reads stdin line by line. It strips comments and whitespace, canonicalizes local labels, parses an optional directive/instruction prefix and suffix, optionally removes register class prefixes, dispatches to a Perl code reference when a mnemonic needs translation, and prints either the rewritten line or the default instruction/directive.

State and persistence: persistent output is the generated assembly file only. In-memory state is limited to `%GLOBALS`, the target flavour, and local-label policy. No runtime kernel state is modified.

Dependencies and integration points: depends on Perl and assembler conventions for OpenSSL-derived PowerPC crypto sources. Linux integration relies on `_GLOBAL()` and PowerPC assembler headers; Power8 crypto assembly depends on the emitted `.long` encodings when the assembler does not know newer mnemonics.

Risks: flavour matching is regex-based, so new ABI strings can silently choose the wrong directive path. The `.quad` fallback notes 32-bit Perl arithmetic risk. Register and comment stripping are intentionally simple and can break unusual assembly syntax. The Linux ppc64le vrsave special case substitutes no-op/read-all behavior and must stay ABI-aware.

Test signals: regenerate all PowerPC crypto assembly flavours and build with both old and new binutils. Inspect emitted Linux ppc64le output for `_GLOBAL`, `.abiversion 2`, local labels, and raw instruction encodings for VMX/VSX crypto operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/ppc-xlate.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/vmx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/crypto/vmx.c

Purpose: registers the Power8 VMX/Vector Crypto AES skcipher implementations with the Linux crypto API when the CPU advertises vector crypto support.

Important APIs/types/functions: `p8_init()` registers `p8_aes_cbc_alg`, `p8_aes_ctr_alg`, and `p8_aes_xts_alg`; `p8_exit()` unregisters them in reverse order. `module_cpu_feature_match(PPC_MODULE_FEATURE_VEC_CRYPTO, p8_init)` gates module initialization on the CPU feature.

Control flow: initialization attempts CBC registration first, then CTR, then XTS. Each failure jumps to a rollback label that unregisters previously registered algorithms before returning the error. Exit unconditionally unregisters XTS, CTR, and CBC.

State and persistence: state lives in the crypto algorithm registry for the module lifetime. This file owns no private persistent data and relies on algorithm objects declared in `aesp8-ppc.h`.

Dependencies and integration points: includes module, CPU feature, and crypto skcipher headers, plus `<asm/cputable.h>`. It integrates with the kernel crypto manager, module loader, and Power8 AES assembly/C glue.

Risks: registration order must match rollback and exit order to avoid leaked or double-unregistered algorithms. The module is useful only when `PPC_MODULE_FEATURE_VEC_CRYPTO` matches actual hardware and kernel vector state handling is correct.

Test signals: build the module, load it on Power8 or later hardware with vector crypto, and verify `cbc(aes)`, `ctr(aes)`, and `xts(aes)` self-tests and crypto API listings. Negative tests should force registration failure and confirm rollback leaves no partial algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/vmx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/8xx_immap.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/8xx_immap.h

Purpose: defines the memory-mapped internal register layout for MPC8xx processors, including SIU, PCMCIA, memory controller, timers, clock/reset, video/LCD, I2C, SDMA, CPM interrupt controller, I/O ports, CPM timers, SCC/SMC/SPI/parallel interfaces, FEC, dual-port RAM, and parameter RAM.

Important APIs/types/functions: major types are `sysconf8xx_t`, `pcmconf8xx_t`, `memctl8xx_t`, `sit8xx_t`, `car8xx_t`, `sitk8xx_t`, `cark8xx_t`, `vid823_t`, `lcd823_t`, `i2c8xx_t`, `sdma8xx_t`, `cpic8xx_t`, `iop8xx_t`, `cpmtimer8xx_t`, `scc_t`, `smc_t`, `fec_t`, `cpm8xx_t`, and top-level `immap_t`. Register bit macros cover memory-controller BR/OR fields, timer status/control bits, keep-alive power keying, and FEC/LCD aliases. `mpc8xx_immr` is the exported mapped base pointer.

Control flow: this header is declarative. Board and driver code map the IMMR area, cast it to `immap_t`, then access the nested register blocks directly or through the `cp_fec`, `cp_fec1`, `cp_fec2`, and `lcd_cmap` aliases.

State and persistence: all state is live MPC8xx hardware state. Register writes configure chip selects, wait states, timers, resets, interrupt masks, serial channels, Ethernet descriptors, DMA, and dual-port RAM; values persist until reset or reprogramming.

Dependencies and integration points: available only for `__KERNEL__`. It depends on kernel integer typedefs and `__iomem`. It integrates with old 8xx board support, CPM serial/Ethernet/I2C code, early platform setup, and low-level memory-controller initialization.

Risks: structure padding and reserved byte counts must exactly match the processor manual; casual refactors can shift every hardware register. Some blocks are model-specific, and the FEC/LCD address union means simultaneous assumptions are unsafe. Direct volatile MMIO users must handle endian, ordering, and posted writes externally.

Test signals: validate with `BUILD_BUG_ON` offsets where available, boot MPC8xx targets, exercise timer, FEC, CPM serial, I2C, and PCMCIA paths, and compare register dumps against the hardware manual after board initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/8xx_immap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/Kbuild

Purpose: declares generated and generic PowerPC UAPI/asm header exports for Kbuild.

Important APIs/types/functions: `generated-y += syscall_table_32.h` and `generated-y += syscall_table_64.h` mark generated syscall tables. `generic-y += kvm_para.h`, `mcs_spinlock.h`, `early_ioremap.h`, `irq_regs.h`, and `export.h` select generic headers.

Control flow: Kbuild consumes this metadata during header generation and installation. The file has no C control flow.

State and persistence: it affects generated build artifacts and exported include trees, not runtime state.

Dependencies and integration points: depends on Linux Kbuild's `generated-y` and `generic-y` conventions. It integrates architecture-specific syscall table generation with generic asm header fallbacks.

Risks: removing an entry can break userspace header export or kernel compilation for includes that expect generic fallbacks. Adding architecture-specific headers with the same names requires adjusting this file to avoid conflicts.

Test signals: run PowerPC `headers_install`, allmodconfig/defconfig builds, and include smoke tests for the generic headers named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/accounting.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/accounting.h

Purpose: defines the per-CPU accounting data layout used by PowerPC time accounting code.

Important APIs/types/functions: `struct cpu_accounting_data` contains accumulated user, system, guest, hardirq, softirq, stolen, and idle cputime values plus internal timebase snapshots. With `CONFIG_ARCH_HAS_SCALED_CPUTIME`, it also carries scaled user/system fields and SPURR-based snapshots.

Control flow: this header is declarative. Accounting code elsewhere updates the fields on ticks, context transitions, IRQ entry/exit, and virtualization accounting events.

State and persistence: instances of `cpu_accounting_data` persist as CPU-local runtime accounting state. The structure records accumulated time plus start snapshots such as `starttime`, `starttime_user`, and optional `startspurr`.

Dependencies and integration points: integrates with PowerPC scheduler cputime accounting, timebase/SPURR accounting, guest time, stolen time, and IRQ time accounting implementations.

Risks: field order and config-gated fields must match all users. Incorrect snapshot maintenance in implementation code would skew user/system/steal/IRQ time, especially on virtualized systems.

Test signals: build with and without `CONFIG_ARCH_HAS_SCALED_CPUTIME`; validate `/proc/stat`, task cputime, guest/steal accounting, and IRQ time under CPU-bound and interrupt-heavy workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/accounting.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/archrandom.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/archrandom.h

Purpose: exposes PowerPC architecture random-number hooks to the generic kernel random subsystem.

Important APIs/types/functions: when `CONFIG_ARCH_RANDOM` is enabled it declares `powernv_get_random_long(unsigned long *v)`, `pseries_get_random_long(unsigned long *v)`, and `powerpc_arch_randomize_init(void)`.

Control flow: this header has no inline logic. Platform code implements the backend random retrieval functions, and random initialization code calls `powerpc_arch_randomize_init()` to wire the platform backend.

State and persistence: no state is stored here. Entropy state is owned by platform firmware/hardware and the generic random subsystem.

Dependencies and integration points: integrates PowerNV and pSeries firmware/hardware RNG providers with the generic `arch_get_random*` path under `CONFIG_ARCH_RANDOM`.

Risks: declarations are gated by config, so call sites must also be config-gated. Hardware or firmware RNG failures must be handled in implementation code by returning false rather than supplying weak values.

Test signals: build with `CONFIG_ARCH_RANDOM`, boot PowerNV and pSeries targets, verify random subsystem credits/uses arch randomness only on successful backend calls, and test failure paths on systems without RNG support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/archrandom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/asm-compat.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/asm-compat.h

Purpose: provides assembly mnemonic and register-size compatibility macros shared by C inline assembly and assembly files across 32-bit and 64-bit PowerPC.

Important APIs/types/functions: selects `PPC_LL`, `PPC_STL`, `PPC_LCMPI`, `PPC_LONG`, `PPC_LONG_ALIGN`, `PPC_LONG_SHIFT`, `PPC_LONG_SIZE`, `PPC_LONG_ALIGN_BYTES`, and load-reserve/store-conditional forms such as `PPC_LLARX`, `PPC_STLCX`, `PPC_LDARX`, and `PPC_STDCX`. It also defines `stringify_in_c()` for embedding macro-expanded opcodes in C asm strings.

Control flow: compile-time `#ifdef CONFIG_PPC64` or `__powerpc64__` selects 64-bit mnemonics and sizes; otherwise 32-bit forms are used. No runtime control flow exists.

State and persistence: no state is stored. The macros affect generated code and ABI layout assumptions.

Dependencies and integration points: included by atomic, bitops, bug, barriers, and assembly code that needs one source to build for ppc32 and ppc64.

Risks: an incorrect macro here can corrupt atomics, exception code, or data layout across the architecture. The file is sensitive to assembler syntax and the distinction between kernel config and compiler predefined architecture macros.

Test signals: build 32-bit and 64-bit PowerPC configurations, inspect inline assembly for expected `lwz/stw/lwarx/stwcx.` or `ld/std/ldarx/stdcx.` forms, and run atomic/locking stress tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/asm-compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/asm-const.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/asm-const.h

Purpose: provides constants that can be shared between assembler and C contexts without type suffix problems.

Important APIs/types/functions: includes `<vdso/const.h>` and depends on the VDSO `ASM_CONST`/constant helpers for architecture headers that need constants in both C and assembly.

Control flow: declarative include wrapper only.

State and persistence: no runtime state.

Dependencies and integration points: many PowerPC MMU, barrier, bit, and instruction headers include this before defining large constants used in assembly or inline asm.

Risks: if the included VDSO constant interface changes, architecture headers using `ASM_CONST` can break in assembly-only builds. Because this file is tiny, accidental removal can produce widespread compile errors.

Test signals: compile C and assembler translation units that include Book3S MMU headers, especially constants above 32 bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/asm-const.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/asm-offsets.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/asm-offsets.h

Purpose: redirects architecture assembly code to the generated offset definitions used by the Linux build.

Important APIs/types/functions: includes `<generated/asm-offsets.h>`, which contains structure offsets and constants generated from C.

Control flow: no control flow; this is a generated-header bridge.

State and persistence: no state here. Build output persists in the generated include directory.

Dependencies and integration points: used by assembly macros and exception/MMU code needing offsets into `thread_struct`, `pt_regs`, stack frames, and other C structures.

Risks: stale or missing generated offsets can produce assembly that saves/restores the wrong fields. Include ordering matters for assembly files that expect this path.

Test signals: clean PowerPC build from scratch, verify generated offsets are rebuilt when relevant C structures change, and boot-test exception paths that consume stack/register offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/asm-offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/asm-prototypes.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/asm-prototypes.h

Purpose: declares C-visible prototypes for symbols implemented in PowerPC assembly so modversions and C callers see consistent signatures.

Important APIs/types/functions: includes checksum, uaccess, string, and asm headers; declares low-level helpers such as `flush_icache_range`, `__flush_icache_range`, `_mcount`, ftrace and kprobes trampoline symbols, compare/copy/checksum helpers, and interrupt/exception entry helpers depending on configuration.

Control flow: no runtime logic. Preprocessor config gates declarations for ftrace, kprobes, KASAN, PPC32/PPC64, and exception models.

State and persistence: no state is stored. It constrains ABI contracts between assembly and C.

Dependencies and integration points: consumed by assembly build infrastructure and C modules that need symbol CRCs. It integrates exception entry, ftrace, kprobes, checksum/string routines, and user access assembly.

Risks: signature mismatch between declarations and assembly implementations can break module versioning or calling conventions. Config guards must track where the symbols are actually built.

Test signals: allmodconfig builds with `CONFIG_MODVERSIONS`, ftrace, kprobes, KASAN, PPC32, and PPC64 combinations; runtime smoke tests for tracing and checksum/string routines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/asm-prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/asm.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/asm.h

Purpose: compatibility include for generic architecture assembly helpers.

Important APIs/types/functions: includes `<asm/asm-compat.h>` and `<asm/extable.h>`, making register-size macros and exception-table helpers available through the traditional `asm.h` include path.

Control flow: no runtime logic.

State and persistence: no state.

Dependencies and integration points: included by low-level PowerPC assembly and C inline assembly sources that expect a central architecture asm header.

Risks: because it is a broad include shim, changing it can affect many assembly files indirectly. Missing `extable` inclusion would break exception fixup annotations.

Test signals: architecture build coverage for assembly files and inline exception-table users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/async_tx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/async_tx.h

Purpose: selects PowerPC DMA offload capability flags for the async_tx subsystem.

Important APIs/types/functions: defines `async_tx_issue_pending_all()` as an empty inline hook and `async_tx_find_channel(dep, type)` as a macro passing `async_tx_cap_mask_all` to `__async_tx_find_channel()`.

Control flow: callers use the generic async_tx channel lookup path. This header does not perform runtime work beyond the macro call.

State and persistence: no state is stored. DMA channel ownership and descriptors are managed by async_tx and DMA engine code.

Dependencies and integration points: includes `<linux/async_tx.h>`. It integrates architecture policy with async XOR/memcpy/PQ users.

Risks: the empty issue-pending hook means PowerPC relies on lower layers to submit work; if an architecture-specific pending flush were needed it would be absent. The all-capability mask assumes generic filtering is sufficient.

Test signals: build async_tx users, run DMA engine self-tests or RAID acceleration paths, and verify channel selection/fallback works when no DMA engine is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/async_tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/atomic.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/atomic.h

Purpose: implements PowerPC atomic integer operations using load-reserve/store-conditional loops and architecture-specific acquire/release barriers.

Important APIs/types/functions: provides `arch_atomic_read`, `arch_atomic_set`, generated add/sub/and/or/xor operations, relaxed return and fetch variants, `arch_atomic_fetch_add_unless`, `arch_atomic_dec_if_positive`, and 64-bit variants such as `arch_atomic64_read`, `arch_atomic64_set`, `arch_atomic64_inc_not_zero`, and `arch_atomic64_fetch_add_unless` under `__powerpc64__`.

Control flow: each modifying operation loops on `lwarx/stwcx.` or `ldarx/stdcx.` until the conditional store succeeds. Return/fetch variants preserve either new or old values. Specialized functions branch out when comparison predicates fail.

State and persistence: state is the caller-provided `atomic_t` or `atomic64_t` counter. The header itself stores nothing.

Dependencies and integration points: depends on `<asm/cmpxchg.h>`, barriers, asm constants, and asm compatibility macros. It is foundational for kernel refcounts, locks, scheduler state, memory management, and driver synchronization.

Risks: barrier placement is subtle and tied to `PPC_ATOMIC_ENTRY_BARRIER`, `PPC_ATOMIC_EXIT_BARRIER`, acquire, and release definitions. Prefixed instruction handling uses base-register fallbacks to avoid out-of-range generated offsets. Inline asm clobbers such as `xer` must stay correct for add/sub carry forms.

Test signals: build 32/64-bit configs, run LKDTM/refcount/atomic tests, lock and refcount stress workloads, KCSAN-oriented concurrency tests, and inspect generated code for prefixed-kernel configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/backlight.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/backlight.h

Purpose: declares the PowerMac/PowerBook backlight control interface shared with platform implementation code.

Important APIs/types/functions: exports `pmac_backlight`, `pmac_backlight_mutex`, `pmac_has_backlight_type()`, `pmac_backlight_key()`, `pmac_backlight_key_up()`, `pmac_backlight_key_down()`, legacy PMU brightness setters/getter, and enable/disable helpers.

Control flow: inline key helpers call `pmac_backlight_key(0)` for up and `pmac_backlight_key(1)` for down. Other operations are implemented in platform code.

State and persistence: global backlight state is represented by the external `backlight_device` pointer and mutex. Hardware brightness persists according to the device/PMU state, not this header.

Dependencies and integration points: depends on the Linux backlight class and PowerMac platform backlight implementation. It integrates keyboard brightness events, legacy PMU control, and display power management.

Risks: callers must observe the locking rules from the implementation file. Legacy PMU brightness APIs may not map to all backlight hardware types.

Test signals: PowerBook/PowerMac boot tests with keyboard brightness keys, suspend/resume display tests, and lockdep checks around `pmac_backlight_mutex`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/backlight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/barrier.h

Purpose: defines PowerPC memory-ordering primitives for full barriers, SMP barriers, DMA barriers, acquire/release operations, speculation barriers, and persistent-memory write ordering.

Important APIs/types/functions: defines `__mb`, `__rmb`, `__wmb`, `__lwsync`, `__dma_rmb`, `__dma_wmb`, `__smp_mb`, `__smp_rmb`, `__smp_wmb`, `data_barrier(x)`, `__smp_store_release`, `__smp_load_acquire`, `barrier_nospec_asm`, `barrier_nospec()`, and `pmem_wmb()`.

Control flow: compile-time CPU family/config selects `SMPWMB` as `lwsync`, `mbar`, or `eieio`. Runtime control is limited to inline assembly barriers emitted at call sites.

State and persistence: no state is stored. Barriers constrain memory visibility, speculation, and persistent-store ordering.

Dependencies and integration points: depends on `<asm/ppc-opcode.h>` for patchable opcodes and `<asm-generic/barrier.h>` for generic wrappers. Used throughout locking, atomics, DMA, MMIO, PMEM, and side-channel mitigation paths.

Risks: using `lwsync` where `sync` is required can violate ordering, while excessive `sync` hurts performance. `barrier_nospec` relies on correct fixup slot sizing per CPU family. Persistent memory ordering assumes the preceding cache-block flush/persist instructions are used correctly.

Test signals: litmus/concurrency tests, DMA coherency tests, PMEM persistence tests, speculation-mitigation build/runtime checks, and inspection of generated opcodes for Book3S64/e500/BookE configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/bitops.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/bitops.h

Purpose: implements PowerPC atomic bit operations and bit-number conversion helpers while importing generic non-atomic, little-endian, hweight, and filesystem bitmap helpers.

Important APIs/types/functions: defines `PPC_BIT*` masks, `set_bits`, `clear_bits`, `change_bits`, `arch_set_bit`, `arch_clear_bit`, `arch_clear_bit_unlock`, `arch_change_bit`, `arch_test_and_set_bit`, lock and clear/change variants, `arch_xor_unlock_is_negative_byte`, `arch___clear_bit_unlock`, `fls`, `fls64`, and hweight declarations for PPC64.

Control flow: modifying operations use `PPC_LLARX/PPC_STLCX` retry loops. Clear paths optimize constant masks on PPC32 with `rlwinm` when possible. Test-and-set/clear/change return the old masked bit state.

State and persistence: state is caller-provided bitmaps or words. The header stores nothing.

Dependencies and integration points: requires inclusion through `<linux/bitops.h>`, plus asm compatibility, sync, barrier, and generic bitops headers. Used by scheduler, filesystems, locks, memory management, and drivers.

Risks: PowerPC big-endian word bit numbering differs from byte-oriented little-endian bitmap expectations. Barrier variants must match lock/unlock semantics. Constant-mask optimization must preserve semantics for wrapping masks and PPC32 instruction constraints.

Test signals: generic bitops self-tests, ext2/ext4 bitmap tests on big-endian PowerPC, lock bit stress, KCSAN concurrency tests, and compile checks for PPC32 and PPC64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/32/kup.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/32/kup.h

Purpose: implements 32-bit Book3S Kernel User Access Protection (KUAP) using segment register supervisor-key bits.

Important APIs/types/functions: defines `KUAP_NONE`, `kuap_lock_one()`, `kuap_unlock_one()`, `uaccess_begin_32s()`, `uaccess_end_32s()`, `__kuap_save_and_lock()`, `kuap_user_restore()`, `__kuap_kernel_restore()`, `__kuap_get_and_assert_locked()`, `allow_user_access()`, `prevent_user_access()`, `prevent_user_access_return()`, `restore_user_access()`, and `__bad_kuap_fault()`.

Control flow: access enable/disable paths are compile-time gated on `CONFIG_PPC_KUAP` and runtime-patched by `MMU_FTR_KUAP`. Write access records one unlocked user segment in `current->thread.kuap`, clears or sets `SR_KS` through `mtsr/mtsrin`, and uses `isync` after segment updates.

State and persistence: per-thread KUAP state is in `current->thread.kuap` and saved/restored through `pt_regs->kuap` on exceptions. Hardware state is in segment registers.

Dependencies and integration points: depends on Book3S 32 hash segment definitions, `current`, `pt_regs`, `fix_alignment()`, `regs_add_return_ip()`, and single-step emulation. It integrates with uaccess, exceptions, and page-fault diagnostics.

Risks: only write access is controlled here. Unaligned writes crossing segments require special fault handling; incorrect restore can leave user memory writable from kernel. Debug assertions are config-dependent.

Test signals: KUAP debug builds, uaccess copy tests, exception-entry/return tests, unaligned store fault tests crossing segment boundaries, and fault injection for missing `allow_user_access()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/32/kup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/32/mmu-hash.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/32/mmu-hash.h

Purpose: defines 32-bit Book3S hash MMU constants, BAT encoding helpers, segment register fields, hash PTE layout, context representation, and user segment update helpers.

Important APIs/types/functions: macros include BAT block sizes, `BPP_*`, `BAT_PHYS_ADDR`, `PHYS_BAT_ADDR`, `PP_*`, `SR_NX`, `SR_KP`, `SR_KS`, `CTX_TO_VSID`, `mmu_virtual_psize`, and `mmu_linear_psize`. Types include `struct ppc_bat`, `struct hash_pte`, and `mm_context_t`. Functions/macros include assembly `update_user_segments_by_4`, C `update_user_segment()`, `update_user_segments()`, `find_free_bat()`, `bat_block_size()`, and `update_bats()`.

Control flow: assembler macros conditionally program segment registers for configured user segments and optionally issue `isync` on hash-table cores. C helpers update each segment register up to `TASK_SIZE`, masking and skewing the VSID value.

State and persistence: state is hardware BATs, segment registers, hash table entries, and `mm_context_t` context IDs. Updates persist until context switch, MMU reprogramming, or reset.

Dependencies and integration points: depends on asm offsets, `reg.h`, task size definitions, MMU feature patching, and low-level hash fault/flush assembly.

Risks: `CTX_TO_VSID` must remain synchronized with hash functions. Segment-update ordering and `isync` are CPU-sensitive. BAT physical address bit packing differs for 64-bit physical address support.

Test signals: boot 6xx/7xx/604/603-style targets, switch processes over varied `TASK_SIZE`, exercise BAT mappings, and run TLB/hash fault tests with and without extended physical addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/32/mmu-hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/32/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/32/pgalloc.h

Purpose: provides 32-bit Book3S page-table allocation and free helpers for the two-level Linux page table layout used over the hash MMU.

Important APIs/types/functions: implements `pgd_alloc()`, `pgd_free()`, `pmd_populate_kernel()`, `pmd_populate()`, `pgtable_free()`, `pgtable_free_tlb()`, `__tlb_remove_table()`, and `__pte_free_tlb()`. PMD freeing is a no-op because this configuration has no real PMD level.

Control flow: `pgd_alloc()` allocates from `PGT_CACHE(PGD_INDEX_SIZE)` and copies kernel mappings from `swapper_pg_dir` on 603. Free paths either free PTE fragments or cache-backed tables, with TLB-delayed removal encoding the table shift in low bits.

State and persistence: allocated page-table pages/fragments are owned by an `mm_struct` until freed through direct or TLB-deferred paths.

Dependencies and integration points: depends on slab, thread counts, `PGT_CACHE`, `pgtable_gfp_flags`, fragment allocators, and mmu_gather table removal.

Risks: low-bit shift encoding in `pgtable_free_tlb()` depends on alignment. Incorrect 603 kernel mapping copy would corrupt kernel/user split. No-op PMD frees rely on the folded PMD model remaining true.

Test signals: process creation/exit stress, fork/exec under 603 configs, memory reclaim with page-table freeing, and debug builds checking `BUG_ON(index_size > MAX_PGTABLE_INDEX_SIZE)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/32/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/32/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/32/pgtable.h

Purpose: defines the 32-bit Book3S Linux page-table format, permission/cache bits, virtual layout, PTE update primitives, swap encoding, and pgprot helpers for classic hash MMU processors.

Important APIs/types/functions: key macros are `_PAGE_PRESENT`, `_PAGE_HASHPTE`, `_PAGE_READ`, `_PAGE_WRITE`, `_PAGE_EXEC`, `_PAGE_*CACHE*`, `PTE_RPN_MASK`, `_PAGE_CHG_MASK`, `PAGE_KERNEL*`, index sizes, `VMALLOC_START/END`, and swap encoders. Functions include `map_kernel_page()`, `unmap_kernel_page()`, `flush_hash_entry()`, `pte_update()`, `ptep_get_and_clear()`, `ptep_set_wrprotect()`, `__ptep_set_access_flags()`, PTE accessors/modifiers, `pfn_pte()`, `__set_pte_at()`, and pgprot cache transformations.

Control flow: PTE changes call `pte_update()` for atomic hash-safe updates when needed, flush hash entries when clearing accessed or replacing hashed 64-bit PTEs, and select simple stores for UP/per-CPU cases. Access-flag updates set dirty/accessed/RW/exec bits and flush the TLB page.

State and persistence: state is Linux page-table memory plus cached HPTE state signaled by `_PAGE_HASHPTE`. Virtual layout constants define vmalloc/ioremap/fixmap relationships for the boot lifetime.

Dependencies and integration points: depends on generic folded PMD headers, page table checks, scheduler/thread definitions, KASAN, highmem, hash TLB flushing, and MMU feature detection.

Risks: `_PAGE_HASHPTE` preservation is central to avoiding stale hash entries. 64-bit PTE store ordering uses `eieio` between halves. Swap encoding borrows bits and must not collide with present/hash markers. Vmalloc/ioremap layout can clash with early mappings on large RAM systems.

Test signals: hash page fault tests, `mprotect`, fork, swap, THP-disabled page-table walks, KASAN vmalloc configs, highmem configs, and stress that clears accessed/dirty bits while faults occur.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/32/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/32/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/32/tlbflush.h

Purpose: provides TLB and hash-table flush wrappers for 32-bit Book3S CPUs, selecting hash-specific flushes or direct TLB invalidation depending on MMU features.

Important APIs/types/functions: declares `hash__flush_tlb_mm()`, `hash__flush_tlb_page()`, `hash__flush_range()`, `hash__flush_gather()`, `_tlbie()`, and `_tlbia()`. Defines `tlb_flush()`, `flush_range()`, `flush_tlb_mm()`, `flush_tlb_page()`, `flush_tlb_range()`, `flush_tlb_kernel_range()`, and local flush aliases.

Control flow: each wrapper tests `MMU_FTR_HPTE_TABLE`. Hash-capable CPUs delegate to hash flush functions; 603/non-hash paths use `_tlbie()` for single pages or `_tlbia()` for broad invalidation.

State and persistence: affects processor TLBs and hash page-table entries. No software state is stored in the header.

Dependencies and integration points: integrates with `mmu_gather`, `vm_area_struct`, `init_mm`, page-table update paths, and assembler implementations of hash flushing.

Risks: range sizing chooses `_tlbie` only for one page on non-hash CPUs; wrong boundaries can leave stale translations. SMP `_tlbie` is extern, while UP inline emits `tlbie; sync`.

Test signals: page-table unmap/remap tests, process teardown with `mmu_gather`, SMP TLB shootdown tests, and non-hash 603 boot coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/32/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/hash-4k.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/hash-4k.h

Purpose: defines 64-bit Book3S hash MMU geometry and PTE/HPTE metadata for 4 KiB base-page kernels.

Important APIs/types/functions: defines hash index sizes, kernel virtual range constants, `H_MAX_PHYSMEM_BITS`, HPTE flag bits (`H_PAGE_F_SECOND`, `H_PAGE_F_GIX`, `H_PAGE_BUSY`, `H_PAGE_HASHPTE`), fragment sizes, pkey bit mappings, `remap_4k_pfn`, real-PTE helpers, `pte_iterate_hashed_subpages`, `pte_pagesize_index`, and THP stubs/externs.

Control flow: 4K real-PTE handling is mostly pass-through: one PTE maps one hashed subpage, iteration emits a single body, and `pte_set_hidx()` computes the hash slot bits to store. THP hash helpers mostly BUG or return unsupported for 4K hash.

State and persistence: state is encoded in PTE bits that remember HPTE slot/index metadata. No standalone state exists here.

Dependencies and integration points: included through 64-bit hash/radix page-table headers. It integrates hash fault insertion/removal with Linux PTE storage for 4K pages.

Risks: 4K hash lacks THP and combo-page support, so callers must not assume 64K behavior. HPTE slot bits are overloaded into pkey/RPN-reserved fields and must not collide with generic PTE bits.

Test signals: boot 4K-page hash kernels, run page fault/unmap/mprotect tests, verify no THP exposure in hash-4K mode, and inspect HPTE insertion/removal paths for correct slot tracking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/hash-4k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/hash-64k.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/hash-64k.h

Purpose: defines 64-bit Book3S hash MMU page-table geometry and subpage/HPTE metadata for 64 KiB base-page kernels.

Important APIs/types/functions: defines 64K hash index sizes, physical/EA limits, kernel map ranges, combo and 4K-PFN flags, HPTE slot encodings, fragment sizes, pkey bit mapping, real-PTE composition, hashed-subpage iteration, `pte_pagesize_index()`, `pte_set_hidx()`, and hash THP helper declarations.

Control flow: helpers track multiple 4K hardware subpages inside a 64K Linux PTE when needed, including combo-page and hash-slot metadata. Iteration walks valid hashed subpages and passes index/shift to hash code.

State and persistence: PTE bits and companion slot arrays store subpage HPTE placement. Kernel virtual layout constants persist for the boot configuration.

Dependencies and integration points: used by hash fault, hugepage, and page-table code under `CONFIG_PPC_64K_PAGES`. It integrates with protection keys and subpage hash handling.

Risks: bit overloading is dense; RPN, pkey, combo, and HPTE metadata must not conflict. Cache-inhibited mapping restrictions can demote processes to 4K subpages. THP hash slot arrays must be kept in sync with HPTE invalidation.

Test signals: 64K hash boot, subpage protection tests, cache-inhibited user mappings, THP hash tests if enabled, hugepage mapping/unmapping, and pkey tests on hash MMU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/hash-64k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/hash-pkey.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/hash-pkey.h

Purpose: maps PowerPC memory protection key state into hash-MMU PTE bits.

Important APIs/types/functions: provides hash-specific helpers for translating VMA flags to PTE pkey bits and extracting pkey fields from PTE flags, using the `H_PTE_PKEY_BIT*` definitions supplied by the active hash page-size header.

Control flow: inline helpers are conditional on memory-key/MMU support and operate by masking and shifting PTE flag bits. There is no runtime state machine here.

State and persistence: pkey state is persisted in PTE flag bits and per-mm key allocation data defined elsewhere.

Dependencies and integration points: included by `book3s/64/pkeys.h`; depends on hash page-size headers and `mmu_has_feature(MMU_FTR_PKEY)`. It integrates with mprotect/pkey syscalls and access-permission checks.

Risks: hash pkey bit placement differs between 4K and 64K modes. Incorrect mapping can grant or deny memory access unexpectedly. Radix support is intentionally not implemented through this hash helper.

Test signals: pkey allocation and mprotect tests on hash MMU, read/write/execute denial checks, and builds for both 4K and 64K page sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/hash-pkey.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/hash.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/hash.h

Purpose: supplies common 64-bit Book3S hash-MMU page-table operations used by the top-level page-table dispatcher.

Important APIs/types/functions: provides hash versions of PTE update, set, same/none checks, PMD/PUD bad/same checks, hugepage update and deposit/withdraw interfaces, hash vmemmap/kernel mapping functions, and transparent hugepage support hooks. It also supplies constants derived from hash 4K or 64K headers.

Control flow: inline operations generally preserve hash-specific HPTE flags while updating software PTE bits. Some paths delegate to extern implementations for hugepage, vmemmap, and kernel mapping operations. Compile-time page-size selection chooses 4K or 64K hash behavior.

State and persistence: state is encoded in Linux PTE/PMD/PUD values and HPTE tracking bits. External hash page-table state is managed by hash fault and flush implementations.

Dependencies and integration points: included by `book3s/64/pgtable.h` alongside radix support. It integrates with page faults, TLB/hash flushes, hugepage handling, vmemmap population, and kernel mapping setup.

Risks: hash PTE updates must coordinate with concurrent HPTE invalidation. Mistakes can leak stale hash translations. Hugepage behavior diverges sharply between 4K and 64K hash modes.

Test signals: hash MMU boot, page fault stress, `mprotect`, THP/hugetlb where supported, vmemmap population, kernel ioremap tests, and concurrent unmap/fault stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/hugetlb.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/hugetlb.h

Purpose: provides Book3S64 hugetlb helpers for translating Linux hugepage sizes to MMU page-size indexes and dispatching radix-specific hugepage TLB/protection operations.

Important APIs/types/functions: declares `radix__flush_hugetlb_page()`, `radix__local_flush_hugetlb_page()`, `radix__huge_ptep_modify_prot_commit()`, `huge_ptep_modify_prot_start()`, and `huge_ptep_modify_prot_commit()`. Inline helpers include `hstate_get_psize()`, `gigantic_page_runtime_supported()`, `flush_hugetlb_page()`, `check_and_get_huge_psize()`, and `arch_has_huge_bootmem_alloc()`.

Control flow: `hstate_get_psize()` maps a hugepage shift to `MMU_PAGE_2M`, `1G`, `16M`, or `16G`, warning and falling back to `mmu_virtual_psize` on mismatch. `check_and_get_huge_psize()` rejects firmware page sizes unsupported by the active MMU: radix allows 2M/1G, hash allows 16M/16G. Runtime gigantic allocation is disabled for hash LPARs.

State and persistence: no private state is stored. The helpers act on hugetlb VMA/PTE state and firmware/MMU page-size definitions.

Dependencies and integration points: depends on firmware feature checks, `radix_enabled()`, `mmu_psize_defs`, hugetlb hstate data, and Book3S64 page-table code. It integrates hugetlbfs, boot-time hugepage reservation, and radix TLB flush/protection paths.

Risks: accepting an unsupported hugepage shift would create page-table entries the active MMU cannot represent. Hash LPAR gigantic pages require hypervisor-assisted reservation and are not safe for runtime allocation.

Test signals: hugetlbfs tests for radix 2M/1G and hash 16M/16G, boot-time hugepage reservation on LPAR hash systems, runtime allocation rejection tests, and hugepage permission-change flush tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/hugetlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/kexec.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/kexec.h

Purpose: resets Book3S64 security and breakpoint-related SPR state before a kexec transition.

Important APIs/types/functions: defines `reset_sprs()` as the architecture hook. It clears `SPRN_AMR` and `SPRN_UAMOR` on ISA 2.06 CPUs, `SPRN_IAMR` and CIABR on ISA 2.07S CPUs, and `SPRN_DEXCR` plus `SPRN_HASHKEYR` on ISA 3.1 CPUs. CIABR is cleared either directly in HV mode or through `plpar_set_ciabr(0)`.

Control flow: `reset_sprs()` tests CPU feature bits in increasing ISA order, writes the relevant SPRs to zero, then issues `isync()` before the kexec reset path continues.

State and persistence: the function clears live per-CPU SPR state so AMR/IAMR, CIABR, DEXCR, and HASHKEYR settings do not leak into the next kernel.

Dependencies and integration points: includes `plpar_wrappers.h` and uses `cpu_has_feature()`, `mtspr()`, SPR constants, and PAPR CIABR hypervisor calls. It integrates with the generic kexec architecture reset hook.

Risks: missing a security-sensitive SPR could leave stale access-control, breakpoint, or execution-control state after kexec. CIABR clearing must use the hypervisor call when not in HV mode.

Test signals: kexec and kdump tests across ISA 2.06, 2.07S, and 3.1 systems; verify AMR/IAMR/CIABR/DEXCR/HASHKEYR are reset before entering the new kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/kexec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/kup.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/kup.h

Purpose: implements 64-bit Book3S Kernel User Access/Execute Protection using AMR/IAMR registers and PowerPC protection-key features.

Important APIs/types/functions: defines `AMR_KUAP_BLOCK_READ`, `AMR_KUAP_BLOCK_WRITE`, `AMR_KUEP_BLOCKED`, `AMR_KUAP_BLOCKED`, assembly macros `kuap_user_restore`, `kuap_kernel_restore`, `kuap_check_amr`, `kuap_save_amr_and_lock`, static key `uaccess_flush_key`, defaults `default_uamor/default_amr/default_iamr`, and C helpers for AMR/IAMR restore, `get_kuap()`, `set_kuap()`, `allow_user_access()`, `prevent_user_access()`, `prevent_user_access_return()`, and `restore_user_access()`.

Control flow: exception entry assembly saves AMR/IAMR and blocks user access depending on pkey/KUAP/KUEP features and whether the exception came from user or kernel. C uaccess helpers build an AMR value for read, write, or read/write access and use `isync; mtspr; isync` around AMR writes.

State and persistence: state is in AMR/IAMR SPRs, saved `pt_regs` fields, per-thread user AMR/IAMR, and read-only default register values. Optional flushing is controlled by `uaccess_flush_key`.

Dependencies and integration points: depends on SPR definitions, MMU feature tests, pkeys, ptrace registers, exception entry stack offsets, and uaccess flushing. It integrates with all kernel user-memory access on Book3S64.

Risks: missing context synchronization around AMR writes can expose user memory or create spurious faults. Non-nesting design means callers must pair allow/prevent carefully. Debug checks depend on `CONFIG_PPC_KUAP_DEBUG`.

Test signals: KUAP/KUEP debug builds, uaccess copy tests, pkey tests, interrupt entry/return tests from user and kernel, fault injection for blocked access, and static-key flush path tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/kup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/mmu-hash.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/mmu-hash.h

Purpose: defines 64-bit Book3S hash MMU structures, HPTE/SLB encodings, VSID allocation, hash calculations, segment handling, and hash-specific `mm_context` data.

Important APIs/types/functions: core types are `struct mmu_hash_ops`, `struct hash_pte`, `struct slb_entry`, `struct slice_mask`, `struct hash_mm_context`, and optional `struct subpage_prot_table`. Helpers include page-size conversions, `hpte_encode_avpn()`, old/new HPTE conversion, `hpte_encode_v/r()`, `hpt_vpn()`, `hpt_hash()`, `vsid_scramble()`, `user_segment_size()`, `get_vsid()`, `get_kernel_context()`, `get_kernel_vsid()`, `mk_esid_data()`, and `mk_vsid_data()`. Numerous externs cover hash faulting, HPTE insertion/removal, SLB management, and setup.

Control flow: hash faults compute VSIDs from context and EA, encode HPTE V/R words, hash VPNs into HPTE groups, then call `mmu_hash_ops` to insert/update/remove entries. SLB helpers encode ESID/VSID data for bolted and dynamic segment entries. Context helpers assign different kernel contexts to linear, vmalloc, IO, and vmemmap regions.

State and persistence: persistent boot state includes `mmu_hash_ops`, `htab_address`, `htab_size_bytes`, `htab_hash_mask`, page-size definitions, segment sizes, SLB size, and per-mm `hash_mm_context` slice masks. Hardware state includes SLB and HPTE entries.

Dependencies and integration points: included by `book3s/64/mmu.h` and pgtable code; integrates with pSeries/native HPTE backends, SLB miss handlers, subpage protection, slices, hugepages, KVM/firmware page-size capabilities, and kexec cleanup.

Risks: VSID math must avoid zero/reserved VSIDs and stay bijective. ISA 3.0 HPTE format conversion must match CPU features. Kernel context counts depend on physical memory bits. Any mismatch between page-size encodings and HPTE insertion can cause hard-to-debug translation faults.

Test signals: hash MMU boot on pre- and post-POWER9 systems, SLB miss stress, hugepage and subpage protection tests, pSeries/native HPTE backend tests, kexec, and memory configurations above 512TB where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/mmu-hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/mmu.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/mmu.h

Purpose: defines the Book3S64 MMU abstraction shared by hash and radix modes, including page-size definitions, process/partition table formats, per-mm context state, and early MMU dispatch.

Important APIs/types/functions: `struct mmu_psize_def`, `struct prtb_entry`, `struct patb_entry`, `mm_context_t`, context helpers for hash slices, globals for PID/LPID bits and page sizes, `mmu_early_init_devtree()`, `hash__early_init_mmu()`, `radix__early_init_mmu()`, `early_init_mmu()`, `early_init_mmu_secondary()`, `setup_initial_memory_limit()`, `radix_init_pseries()`, and hash `get_user_context()`/`get_user_vsid()`.

Control flow: early init dispatches to radix or hash based on `radix_enabled()`/`early_radix_enabled()`. Initial memory limits use hash restrictions unless early radix is selected. Hotplug cleanup and context helpers are config-gated.

State and persistence: `mm_context_t` persists per process and tracks PID/context IDs, active CPUs, coprocessor and VAS window users, hash slice state, VDSO pointer, page-table fragments, IOMMU memory lists, and memory protection keys. Global MMU sizing state persists after early boot.

Dependencies and integration points: integrates with hash MMU definitions, radix process/partition tables, pkeys, pSeries, CPU hotplug, IOMMU, VAS, scheduler mm cpumasks, and memory hotplug.

Risks: hash and radix share fields with different meanings, especially `id` versus extended hash context IDs. Early dispatch must match firmware/CPU capabilities. PID/LPID sizing controls table allocation and hardware limits.

Test signals: hash and radix boots, CPU hotplug, pSeries radix init, memory hotplug, process creation with high address ranges, pkey tests, and IOMMU/VAS users of `mm_context_t`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/pgalloc.h

Purpose: implements Book3S64 page-table allocation/free helpers, including different PGD allocation sizes for radix and hash, page-table fragments, and vmemmap backing tracking.

Important APIs/types/functions: defines `struct vmemmap_backing`, `vmemmap_list`, `pmd_fragment_alloc/free`, `pgtable_free_tlb()`, `__tlb_remove_table()`, `pte_frag_destroy()`, `radix__pgd_alloc/free()`, `pgd_alloc()`, `pgd_free()`, PUD/PMD/PTE allocation and populate helpers, and fragment-aware free paths.

Control flow: allocation chooses radix or hash sizing and may use pages, page fragments, or slab caches depending on table level and page size. Free paths encode table index/shift for TLB-deferred release and use fragment destructors where applicable.

State and persistence: allocated tables are tied to an `mm_struct`; per-mm `pte_frag` and `pmd_frag` cache fragments. `vmemmap_list` tracks physical backing for vmemmap mappings.

Dependencies and integration points: depends on slab, cpumask, kmemleak, percpu, mmu_gather, and Book3S64 page-table geometry. It integrates with process lifecycle, memory hotplug, vmemmap, and RCU/TLB table freeing.

Risks: radix 4K PGDs allocate higher-order pages, so allocation failure handling matters. Fragment accounting must be exact to avoid leaks or double frees. TLB-deferred low-bit encoding depends on table alignment and index-size bounds.

Test signals: fork/exit stress, page-table allocation fault injection, memory hotplug, kmemleak scans, THP split/collapse, and both 4K/64K page-size builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/pgtable-64k.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/pgtable-64k.h

Purpose: provides 64 KiB page-size-specific Book3S64 page-table definitions included by the common pgtable header.

Important APIs/types/functions: bridges the common Book3S64 PTE layout with 64K-specific hash/radix fragment and index definitions selected in lower headers.

Control flow: declarative include-time configuration only.

State and persistence: no private state. It affects compile-time page-table layout and runtime table sizes through macros/globals initialized elsewhere.

Dependencies and integration points: only used under `CONFIG_PPC_64K_PAGES`; integrates with hash-64K, radix-64K, pgalloc, hugetlb, and vmemmap layout.

Risks: 64K page configurations have different PTE fragment sizes and subpage hash behavior. A mismatch with hash/radix geometry would corrupt page-table walks.

Test signals: 64K hash and radix boots, page fault/mprotect tests, hugepage tests, and page-table allocation/free stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/pgtable-64k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/pgtable.h

Purpose: defines the common Book3S64 Linux page-table format and dispatch layer for hash and radix MMUs, including PTE/PMD/PUD/P4D accessors, permission bits, virtual layout, swap encoding, cache attributes, hugepage helpers, and kernel mapping wrappers.

Important APIs/types/functions: key macros include `_PAGE_EXEC/WRITE/READ/PRIVILEGED`, `_PAGE_PRESENT`, `_PAGE_PTE`, `_PAGE_INVALID`, pkey/software bits, `PTE_RPN_MASK`, `PAGE_KERNEL*`, dynamic index/table-size globals, `VMALLOC_*`, IO layout, and swap encoders. Functions include `pte_update()`, `ptep_test_and_clear_young()`, `ptep_get_and_clear()`, `pte_clear()`, PTE accessors/modifiers, `pfn_pte()`, `check_pte_access()`, `__ptep_set_access_flags()`, `pte_same()`, `pte_none()`, `__set_pte_at()`, pgprot helpers, PMD/PUD/P4D accessors, `map_kernel_page()`, vmemmap mapping wrappers, hugepage update/get/clear/deposit/withdraw functions, and protection modification transactions.

Control flow: many helpers branch on `radix_enabled()` to call radix or hash implementations. PTE updates preserve hash HPTE flags where needed, radix can optimize full clears, and hugepage helpers route PMD/PUD operations to the active MMU. Access checks require present, user, read, optional write, and optional pkey permission.

State and persistence: page-table entries persist per mapping and encode hardware and Linux software state. Dynamic globals define table geometry and virtual regions for the boot mode. Hash mode also stores HPTE tracking bits in PTE fields.

Dependencies and integration points: includes generic folded P4D support, page-table checks, barrier, hash/radix headers, pkeys, THP, hugetlb, KASAN/fixmap/io mapping, vmemmap, and memory hotplug.

Risks: this is a high-blast-radius header. Hash/radix bit sharing must remain compatible; `_PAGE_PTE` distinguishes leafs from pointers; `_PAGE_INVALID` serializes THP splits. Soft-dirty and swap bits must not collide with HPTE flags. Missing TLB/HPTE flushes can leave stale translations.

Test signals: full mm selftests, `mprotect`, swap, soft-dirty, pkeys, THP split/collapse/migration, hugetlb, memory hotplug, vmemmap, ioremap, and both hash/radix 4K/64K build-and-boot matrices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/pkeys.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/pkeys.h

Purpose: exposes Book3S64 memory protection key conversion helpers for page-table code.

Important APIs/types/functions: includes hash pkey support and defines `vmflag_to_pte_pkey_bits()` plus `pte_to_pkey_bits()` style helpers that return no pkey bits when `MMU_FTR_PKEY` is absent and currently BUG for radix pkey conversion in the visible path.

Control flow: inline helpers first test `mmu_has_feature(MMU_FTR_PKEY)`, then route to hash helpers when hash mode is active.

State and persistence: pkey allocation state lives in `mm_context_t`; this header only maps it to/from PTE bits.

Dependencies and integration points: depends on `hash-pkey.h`, MMU feature detection, radix/hash mode checks, and VM flags. It integrates with `mprotect`, `pkey_mprotect`, PTE construction, and access checks.

Risks: radix pkey behavior must not accidentally enter hash-only helpers. Incorrect bit extraction can break isolation by granting or denying access.

Test signals: pkey selftests on hash systems, build checks with and without `CONFIG_PPC_MEM_KEYS`, and negative coverage for unsupported radix pkey paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/pkeys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/radix-4k.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/radix-4k.h

Purpose: defines radix page-table index and fragment geometry for Book3S64 kernels using 4 KiB base pages.

Important APIs/types/functions: sets `RADIX_PTE_INDEX_SIZE`, `RADIX_PMD_INDEX_SIZE`, `RADIX_PUD_INDEX_SIZE`, `RADIX_PGD_INDEX_SIZE`, `RADIX_PTE_FRAG_SIZE_SHIFT`, `RADIX_PTE_FRAG_NR`, `RADIX_PMD_FRAG_SIZE_SHIFT`, and `RADIX_PMD_FRAG_NR`.

Control flow: declarative compile-time configuration only.

State and persistence: no private state. These constants determine runtime page-table sizes and address coverage.

Dependencies and integration points: included by `radix.h` when `CONFIG_PPC_64K_PAGES` is not set. It feeds pgtable geometry, pgalloc, and radix walk setup.

Risks: index sizes define a 4PB range with 64KB PGD pages; wrong values break hardware radix walks and allocation sizes.

Test signals: 4K radix boot, page-table allocation/free tests, mmap/fault coverage across high addresses, and process table root-size validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/radix-4k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/radix-64k.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/radix-64k.h

Purpose: defines radix page-table index and fragment geometry for Book3S64 kernels using 64 KiB base pages.

Important APIs/types/functions: sets 64K-specific `RADIX_PTE_INDEX_SIZE`, `RADIX_PMD_INDEX_SIZE`, `RADIX_PUD_INDEX_SIZE`, `RADIX_PGD_INDEX_SIZE`, `RADIX_PTE_FRAG_SIZE_SHIFT/NR`, and `RADIX_PMD_FRAG_SIZE_SHIFT/NR`.

Control flow: compile-time constants only.

State and persistence: no state beyond generated table geometry.

Dependencies and integration points: selected by `radix.h` under `CONFIG_PPC_64K_PAGES`; used by pgtable, pgalloc, process table setup, and vmemmap sizing.

Risks: 64K radix uses 256-byte PTE fragments. Fragment accounting and hardware walk geometry must match these constants exactly.

Test signals: 64K radix boot, page-table fragment stress, THP/hugetlb coverage, and memory hotplug/vmemmap tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/radix-64k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/radix.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/radix.h

Purpose: defines Book3S64 radix MMU geometry, virtual layout, PTE update primitives, THP support hooks, vmemmap mapping interfaces, kernel mapping, and process-table tree sizing.

Important APIs/types/functions: defines radix bad-bit masks, shift/range constants, kernel/vmalloc/IO/vmemmap ranges, table-size macros, strict RWX hooks, `__radix_pte_update()`, `radix__pte_update()`, `radix__ptep_get_and_clear_full()`, `radix__pte_same()`, `radix__pte_none()`, `radix__set_pte_at()`, PMD/PUD/P4D bad/same helpers, THP helpers, vmemmap functions, `radix__map_kernel_page()`, `radix__get_tree_size()`, and memory-hotplug section mapping functions.

Control flow: PTE updates use an `ldarx/stdcx.` loop on big-endian PTE storage. Set-PTE deliberately avoids `ptesync` for normal PTE stores, relying on tolerated spurious faults except for kernel mappings handled elsewhere. THP availability checks compare hardware page-size shifts to PMD/PUD shifts.

State and persistence: radix page tables, process/partition tables, and vmemmap mappings persist for the boot lifetime. This header stores no private state.

Dependencies and integration points: depends on page-size-specific radix headers, cmpxchg, TLB flush radix helpers, CPU feature checks, memory hotplug, dev_pagemap/DAX vmemmap optimization, and strict kernel RWX.

Risks: radix table geometry must match hardware process table RTS encoding. Missing synchronization in kernel mapping paths can cause unrecoverable kernel faults. Bad-bit masks must catch malformed table pointers without rejecting valid leafs.

Test signals: radix boot on POWER9+, page fault/mprotect stress, kernel ioremap, THP PMD/PUD tests, memory hotplug, DAX vmemmap optimization tests, strict RWX tests, and process table sizing validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/radix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/slice.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/slice.h

Purpose: defines hash-MMU slice sizing and public helpers for selecting unmapped areas and page sizes across a Book3S64 process address space.

Important APIs/types/functions: defines `HAVE_ARCH_HUGETLB_UNMAPPED_AREA`, `HAVE_ARCH_UNMAPPED_AREA`, and `HAVE_ARCH_UNMAPPED_AREA_TOPDOWN` for hash MMU configs. Slice constants include `SLICE_LOW_SHIFT`, `SLICE_LOW_TOP`, `SLICE_NUM_LOW`, `GET_LOW_SLICE_INDEX`, `SLICE_HIGH_SHIFT`, `SLICE_NUM_HIGH`, `GET_HIGH_SLICE_INDEX`, and `SLB_ADDR_LIMIT_DEFAULT`. Declares `slice_get_unmapped_area()`, `get_slice_psize()`, `slice_set_range_psize()`, `slice_init_new_context_exec()`, and `slice_setup_new_exec()`.

Control flow: implementation code uses these declarations to choose bottom-up or top-down unmapped areas and to set page-size classes over address ranges. Low slices cover 256MB chunks below 4GB; high slices cover 1TB chunks.

State and persistence: slice page-size masks persist in each hash `mm_context_t`, while `SLB_ADDR_LIMIT_DEFAULT` seeds address limits for new contexts.

Dependencies and integration points: included by `mmu-hash.h`; integrates with mmap layout, hugetlb unmapped-area selection, process exec setup, and SLB segment/page-size programming.

Risks: slice indexes must match the hash MMU segment scheme. Incorrect page-size range updates can create SLB entries incompatible with PTE/HPTE size expectations.

Test signals: mmap and top-down allocation tests, hugetlb unmapped-area tests, exec context reset tests, high-address mappings above 1TB, and SLB miss coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/slice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/tlbflush-hash.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/tlbflush-hash.h

Purpose: declares hash-MMU TLB and HPTE flush operations for Book3S64.

Important APIs/types/functions: provides hash flush declarations for TLB ranges, pages, mm contexts, hugepage invalidation, and low-level HPTE/hash range flushing used by page-table updates.

Control flow: implementation code performs HPTE invalidation and local/global flush decisions; this header exposes the interfaces to common pgtable and mm code.

State and persistence: affects hardware TLBs and hash page-table entries. No state is stored here.

Dependencies and integration points: depends on hash MMU structures, `mmu_gather`, VMA/MM types, and platform HPTE operations. It integrates with unmap, mprotect, page aging, and hugepage invalidation.

Risks: hash mode requires flushing both Linux-visible TLB effects and HPTE entries. Local/global flags must match CPU and hypervisor expectations to avoid stale translations on other CPUs.

Test signals: hash unmap/remap stress, SMP shootdown tests, THP/hugetlb invalidation, page aging tests, and pSeries/native HPTE backend validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/tlbflush-hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/tlbflush-radix.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/tlbflush-radix.h

Purpose: declares radix-MMU TLB invalidation interfaces for Book3S64.

Important APIs/types/functions: exposes radix flush functions for TLB mm, page, range, kernel range, PID/LPID contexts, and page-size-aware invalidations used by radix page-table and memory hotplug paths.

Control flow: callers route radix flush requests here; implementation code chooses local versus global invalidation and appropriate `tlbie/tlbiel` or hypervisor sequences.

State and persistence: modifies processor/hypervisor translation caches. No header-owned state.

Dependencies and integration points: integrates with radix page-table updates, process/partition table management, KVM/LPID handling, memory hotplug, and kernel mapping changes.

Risks: radix invalidation must use correct PID/LPID and page-size encodings. Under-flushing can leave stale translations; over-flushing hurts performance.

Test signals: radix SMP TLB shootdown tests, KVM/LPID invalidation tests, memory hotplug, kernel ioremap changes, and page-size matrix testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/tlbflush-radix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/tlbflush.h

Purpose: provides common Book3S64 TLB flush wrappers that dispatch to hash or radix implementations.

Important APIs/types/functions: includes hash/radix flush headers and defines common `flush_tlb_mm`, `flush_tlb_page`, `flush_tlb_range`, `flush_tlb_kernel_range`, `local_flush_tlb_*`, `tlb_flush`, and page-size-aware helpers.

Control flow: wrappers branch on `radix_enabled()` to select radix invalidation; otherwise they call hash flush routines. Some helpers are no-ops or aliases when the active MMU does not need separate local handling.

State and persistence: affects hardware translation caches and, in hash mode, HPTE state. No private state is stored.

Dependencies and integration points: used by common mmu_gather, page-table update, mprotect, unmap, and kernel mapping code.

Risks: dispatch must match the active MMU mode. Mixing hash and radix flush semantics would leave stale translations or call unsupported operations.

Test signals: hash/radix boot matrices, mmu_gather teardown tests, SMP shootdown, mprotect/unmap stress, and kernel-range flush tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/pgalloc.h

Purpose: selects the correct Book3S page-table allocation header for 32-bit or 64-bit builds.

Important APIs/types/functions: includes either `asm/book3s/64/pgalloc.h` or `asm/book3s/32/pgalloc.h` based on architecture configuration.

Control flow: compile-time include dispatch only.

State and persistence: no state. It determines which allocation helpers are compiled into callers.

Dependencies and integration points: included by generic PowerPC pgalloc users that do not want to know the Book3S word size.

Risks: wrong config guards would include incompatible page-table allocation APIs. This wrapper must track directory layout and architecture symbols.

Test signals: build Book3S 32-bit and 64-bit configs and verify page-table allocation symbols resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/pgtable.h

Purpose: selects the correct Book3S page-table definition header for 32-bit or 64-bit PowerPC builds.

Important APIs/types/functions: includes `asm/book3s/64/pgtable.h` for 64-bit and `asm/book3s/32/pgtable.h` for 32-bit.

Control flow: compile-time include dispatch only.

State and persistence: no state; it exposes the appropriate page-table ABI to common code.

Dependencies and integration points: used by common PowerPC MM code and architecture-independent mm includes.

Risks: a bad include selection would mix incompatible PTE formats and table geometry. Header ordering must avoid recursive include issues.

Test signals: 32-bit and 64-bit Book3S builds, plus compile coverage for common MM users including swap, mprotect, and page-table allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/tlbflush.h

Purpose: selects the correct Book3S TLB flush header for 32-bit or 64-bit builds.

Important APIs/types/functions: includes the 64-bit or 32-bit `tlbflush.h` implementation based on architecture configuration.

Control flow: compile-time include dispatch only.

State and persistence: no state; it exposes the active TLB flush API to common code.

Dependencies and integration points: used by page-table and mmu_gather code across Book3S variants.

Risks: selecting the wrong header would dispatch to unavailable or semantically wrong hash/radix flush functions.

Test signals: 32-bit and 64-bit build coverage and runtime unmap/mprotect tests on both modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/bootx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/bootx.h

Purpose: describes the legacy BootX bootloader interface used by MacOS-era PowerPC systems to pass display and device-tree information to Linux.

Important APIs/types/functions: defines `BOOTX_COLORTABLE_SIZE`, `struct bootx_dt_prop`, `struct bootx_dt_node`, and `bootx_init(unsigned long r4, unsigned long phys)`. It includes UAPI BootX definitions.

Control flow: early boot code calls `bootx_init()` with BootX register/physical address inputs; this header only provides the data layout.

State and persistence: BootX-provided device tree and framebuffer metadata are boot-time state consumed during early initialization.

Dependencies and integration points: integrates with old PowerMac boot paths, early device-tree parsing, and boot text/framebuffer setup.

Risks: structures use 32-bit offsets from an old flattened format, not modern OF/FDT layout. Incorrect interpretation can lose device tree properties or display setup.

Test signals: boot legacy BootX-supported PowerMac systems or emulation, validate parsed device tree nodes/properties, and confirm early framebuffer colormap/display setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/bootx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/bpf_perf_event.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/bpf_perf_event.h

Purpose: defines the PowerPC register type used by BPF programs attached to perf events.

Important APIs/types/functions: includes `<asm/ptrace.h>` and typedefs `struct user_pt_regs` to `bpf_user_pt_regs_t`.

Control flow: no runtime logic.

State and persistence: no state. It defines a type contract between BPF helpers and PowerPC pt_regs layout.

Dependencies and integration points: integrates BPF perf event programs with PowerPC user register views.

Risks: if `user_pt_regs` layout changes, BPF program expectations and verifier/context access must remain consistent.

Test signals: BPF perf-event selftests on PowerPC, compile checks for BPF programs referencing `bpf_user_pt_regs_t`, and pt_regs field access validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/bpf_perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/btext.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/btext.h

Purpose: declares early boot text console helpers used to draw diagnostics on PowerPC framebuffers before normal console drivers are available.

Important APIs/types/functions: declares display discovery/setup/update functions, `btext_prepare_BAT()` on PPC32, `btext_map()`, `btext_unmap()`, character/string/hex/text drawing functions, and screen/line flush/clear helpers.

Control flow: early boot code finds or sets up a framebuffer, maps it, draws text/hex diagnostics, flushes lines or screen, and later unmaps it.

State and persistence: display state is maintained in the implementation file. Framebuffer contents persist on screen until overwritten or the display mode changes.

Dependencies and integration points: integrates BootX/Open Firmware display discovery, early panic/debug output, and PPC32 BAT mapping setup.

Risks: early mapping runs before normal MM is ready; invalid physical framebuffer parameters can crash or corrupt memory. PPC64 has no BAT preparation path.

Test signals: early boot with `btext` enabled, panic-before-console scenarios, framebuffer mode changes, and PPC32 BAT mapping checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/btext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/bug.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/bug.h

Purpose: implements PowerPC architecture-specific BUG/WARN emission and declares exception/fault handling helpers.

Important APIs/types/functions: assembly macro `EMIT_BUG_ENTRY`, C `_EMIT_BUG_ENTRY`, `BUG_ENTRY`, `BUG()`, `BUG_ON()`, `WARN_ON()`, `EMIT_WARN_ENTRY`, and declarations for `hash__do_page_fault()`, `bad_page_fault()`, `emulate_single_step()`, `_exception()`, `_exception_pkey()`, `die()`, `die_mce()`, `die_will_crash()`, and panic kmsg flush hooks.

Control flow: BUG/WARN macros emit a trap instruction (`twi`/`tdnei` style) followed by an entry in `__bug_table`. Constant conditions are optimized at compile time where possible; nonconstant PPC64 `BUG_ON`/`WARN_ON` emit conditional trap instructions.

State and persistence: bug metadata persists in the built kernel's `__bug_table` and optional `.rodata` file strings. Runtime state is exception handling and warning tainting managed elsewhere.

Dependencies and integration points: depends on asm offsets for assembler mode, asm compatibility, generic bug handling, exception tables, fault handlers, and panic infrastructure.

Risks: bug table entry layout must match generated offsets and generic bug parser expectations. Trap instruction selection must be valid for 32/64-bit builds. Incorrect WARN flags can misreport taints.

Test signals: `CONFIG_BUG` and `CONFIG_DEBUG_BUGVERBOSE` builds, LKDTM BUG/WARN tests, module bug table decoding, and exception path tests for conditional traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cache.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cache.h

Purpose: defines PowerPC cache-line geometry, instruction-fetch alignment, DMA alignment, and PPC64 cache information structures.

Important APIs/types/functions: macros include `L1_CACHE_SHIFT`, `L1_CACHE_BYTES`, `SMP_CACHE_BYTES`, `IFETCH_ALIGN_SHIFT`, `IFETCH_ALIGN_BYTES`, `MAX_COPY_PREFETCH`, and `ARCH_DMA_MINALIGN` for noncoherent caches. PPC64 types include `struct ppc_cache_info`, `struct ppc64_caches`, global `ppc64_caches`, and accessors such as `l1_dcache_shift()`, `l1_dcache_bytes()`, and `l1_icache_shift()`.

Control flow: compile-time CPU/config selection chooses cache-line sizes for 8xx, e500mc, PPC32, 47x, and PPC64. PPC64 runtime accessors read populated cache-info globals.

State and persistence: PPC64 cache descriptors persist in `ppc64_caches` after boot discovery. Other values are compile-time constants.

Dependencies and integration points: used by slab alignment, DMA mapping, copy routines, cache flush code, instruction patching, and performance-sensitive memory operations.

Risks: wrong cache-line size can cause false sharing, broken DMA alignment, or incomplete cache flushes. Runtime cache info must be initialized before accessors are used.

Test signals: boot CPU families covered by each branch, DMA tests on noncoherent systems, cache flush/instruction patching tests, and sanity checks against device-tree cache properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cacheflush.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cacheflush.h

Purpose: defines PowerPC cache-maintenance interfaces for page dirty-to-icache tracking, vmalloc synchronization, dcache range clean/flush/invalidate, and instruction-cache flushing.

Important APIs/types/functions: defines `PG_dcache_clean`, `flush_cache_vmap()` for Book3S64 `ptesync`, `flush_dcache_folio()`, `flush_dcache_page()`, `flush_icache_range()`, `flush_icache_user_page()`, `flush_dcache_icache_folio()`, `flush_dcache_range()`, `clean_dcache_range()`, `invalidate_dcache_range()`, and `flush_instruction_cache()` with a 44x inline `iccci` implementation.

Control flow: `flush_dcache_folio()` skips work on coherent-icache CPUs and otherwise clears the per-folio clean bit. Range helpers align the start address down to the L1 dcache block size, iterate cache blocks with `dcbf`, `dcbst`, or `dcbi`, and issue `mb()` synchronization. Book3S64 vmalloc flush emits `ptesync` to avoid spurious kernel faults after PTE installation.

State and persistence: the `PG_dcache_clean` folio flag records whether a page needs icache cleaning before user execution. Cache operations affect CPU cache state, not durable memory state.

Dependencies and integration points: depends on cache geometry accessors, CPU feature checks, generic cacheflush, folio/page flags, vmalloc, JIT/text patching, and noncoherent DMA paths.

Risks: incorrect range alignment or missing barriers can leave stale dcache data. Failing to clear `PG_dcache_clean` after kernel writes can let user mappings execute stale instructions. `flush_cache_vmap()` placement is subtle but required for Book3S64 kernel mappings.

Test signals: module load/ftrace/BPF JIT text execution, dcache/icache coherency selftests, noncoherent DMA tests, vmalloc mapping access immediately after install, and 44x instruction-cache flush coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cacheflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cell-pmu.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cell-pmu.h

Purpose: defines Cell Broadband Engine PMU counter counts, selected control/status bits, and PMU register names.

Important APIs/types/functions: `NR_PHYS_CTRS` is 4, `NR_CTRS` is 8 logical 16-bit counters, `CBE_PM_16BIT_CTR(ctr)` selects 16-bit counter mode bits in `pm_control`, `CBE_PM_TRACE_BUF_EMPTY` marks trace-buffer empty status, and `enum pm_reg_name` names `group_control`, `debug_bus_control`, `trace_address`, `ext_tr_timer`, `pm_status`, `pm_control`, `pm_interval`, and `pm_start_stop`.

Control flow: declarative only. Cell PMU implementation code uses the enum and macros when reading or programming PMU registers.

State and persistence: PMU state lives in Cell hardware registers and perf event state, not in this header.

Dependencies and integration points: integrates Cell platform PMU code with the PowerPC perf subsystem and Cell register definitions.

Risks: counter-count assumptions are Cell-specific. Incorrect `CBE_PM_16BIT_CTR()` use can configure the wrong physical counter half.

Test signals: build Cell perf configs, run `perf stat`/`perf record` on Cell hardware or simulator, and verify 32-bit versus 16-bit counter mode behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cell-pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cell-regs.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cell-regs.h

Purpose: defines Cell Broadband Engine I/O page-table entry bit masks shared by on-chip system device code.

Important APIs/types/functions: includes `cell-pmu.h` and defines `CBE_IOPTE_PP_W`, `CBE_IOPTE_PP_R`, `CBE_IOPTE_M`, `CBE_IOPTE_SO_R`, `CBE_IOPTE_SO_RW`, `CBE_IOPTE_RPN_Mask`, `CBE_IOPTE_H`, and `CBE_IOPTE_IOID_Mask`.

Control flow: declarative only. Cell IOMMU/platform code composes and decodes IOPTE values using these masks.

State and persistence: state is stored in Cell I/O page-table entries maintained by platform/IOMMU code. The header itself owns no state.

Dependencies and integration points: integrates Cell on-chip system devices, IOMMU/page-table setup, and PMU-related Cell headers.

Risks: IOPTE bit masks control read/write permission, coherency, ordering, real page number, cache hint, and IOID fields; incorrect masks can expose device memory or break DMA translation.

Test signals: Cell platform boot, DMA/IOMMU mapping tests, device access with read/write permission changes, and IOPTE dumps compared with hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cell-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/checksum.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/checksum.h

Purpose: implements PowerPC optimized Internet checksum helpers for IP, TCP/UDP pseudoheaders, copy-and-checksum, and checksum arithmetic.

Important APIs/types/functions: declares `csum_partial_copy_generic()`. Provides `csum_and_copy_from_user()`, `csum_and_copy_to_user()`, `csum_partial_copy_nocheck`, `csum_fold()`, `from64to32()`, `csum_tcpudp_nofold()`, `csum_tcpudp_magic()`, `csum_add()`, `csum_shift()`, `ip_fast_csum_nofold()`, `ip_fast_csum()`, `csum_partial()`, and `ip_compute_csum()`.

Control flow: copy helpers validate user access before using generic copy/checksum. Folding and add helpers use PowerPC carry behavior in inline asm. `ip_fast_csum_nofold()` sums IPv4 header words with carry propagation; `csum_partial()` processes buffers with optimized loops and folds final carries.

State and persistence: no state is stored. Functions operate on packet buffers and return checksum accumulators or folded checksums.

Dependencies and integration points: depends on bitops, IPv6 types, uaccess, networking checksum types, and assembly conventions. It is used by IP, TCP, UDP, and driver/network stack fast paths.

Risks: carry handling and endian assumptions are subtle. User copy helpers must not access invalid user memory. Offsets in `csum_shift()` must handle odd-byte alignment correctly.

Test signals: networking checksum selftests, IPv4/IPv6 TCP/UDP traffic, packet corruption detection, unaligned buffer tests, user-copy fault injection, and comparison with generic checksum implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/clocksource.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/clocksource.h

Purpose: routes the architecture clocksource include path to the PowerPC VDSO clocksource definitions.

Important APIs/types/functions: includes `<asm/vdso/clocksource.h>` under the PowerPC clocksource include guard.

Control flow: no runtime logic in this wrapper. Timekeeping and VDSO code consume the included definitions.

State and persistence: no state is stored here. Clocksource state lives in the timekeeping core and PowerPC VDSO data.

Dependencies and integration points: integrates generic clocksource include users with PowerPC VDSO clocksource support.

Risks: if the VDSO clocksource header changes path or API, this wrapper must stay aligned or architecture timekeeping builds will fail.

Test signals: PowerPC timekeeping builds, VDSO clock_gettime tests, and boot-time clocksource registration checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/clocksource.h -->
