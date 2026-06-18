# Research: subset-b-000788

Source group: `sources/distributed-fs/ceph-client/arch/powerpc/lib/*` selected PowerPC library files.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/Makefile

This Makefile controls which PowerPC architecture library objects enter the kernel or module build. It deliberately disables stack protector, ftrace instrumentation, KASAN/KCSAN, and latent entropy for `code-patching.o` and `feature-fixups.o` because those objects patch executable text and run in early or fragile contexts where tracing and sanitizers can recurse or fault. It also disables KASAN for `restart_table.o` because NMI/real-mode restart lookups must not touch instrumented memory.

Important build APIs are the object lists: unconditional `code-patching.o`, `feature-fixups.o`, and `pmem.o`; 32-bit `div64.o`, `copy_32.o`, `crtsavres.o`; 64-bit copy, page, memory, hweight, machine-check copy, and quad helpers through `obj64-y`; plus conditional qspinlocks, SPLPAR locks, Altivec helpers, selftests, error injection, and remote heap. Control flow is pure Kbuild selection, driven by `CONFIG_PPC32`, `CONFIG_PPC64`, `CONFIG_PPC_BOOK3S_64`, `CONFIG_PPC_QUEUED_SPINLOCKS`, and feature-test configs.

Dependencies and integration points are broad: architecture headers expect symbols from these objects for uaccess, text patching, feature fixups, persistent memory, and lock slow paths. Risks are mis-gating an object for the wrong bitness, allowing sanitizer/tracer instrumentation into patching paths, or omitting module `crtsavres.o` for older linkers. Test signals include successful PowerPC allmodconfig builds, `CONFIG_CODE_PATCHING_SELFTEST`, `CONFIG_FTR_FIXUP_SELFTEST`, KASAN/non-KASAN builds, and 32/64-bit link coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/checksum_32.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/checksum_32.S

This 32-bit assembly file implements IP-style one's-complement checksums. It exports `__csum_partial`, `csum_partial_copy_generic`, and `csum_ipv6_magic`. `__csum_partial(buff, len, sum)` aligns to halfword/word boundaries, accumulates 32-bit words with carry through `adde`, handles trailing halfword and byte pieces, then folds the final carry with `addze`.

`csum_partial_copy_generic(src, dst, len)` combines copy and checksum. Its control flow starts with destination cacheline alignment, optional byte/word prologue, a cacheline loop using `dcbt` prefetch and `dcbz` destination zeroing, then word/halfword/byte tails. The `CSUM_COPY_16_BYTES_WITHEX` macro performs unrolled 16-byte load/store/checksum steps, and `EX_TABLE` entries route any source or destination fault to a common `fault` return of zero. `csum_ipv6_magic` sums IPv6 source/destination addresses, length, protocol, and input sum, folds to 16 bits, complements, and exports the result.

State is only register state and exception-table metadata; there is no persistence. Dependencies include cache geometry macros, PowerPC exception tables, and Linux checksum ABI expectations. Risks are endian byte placement, carry-chain correctness, cacheline assumptions around `dcbz`, and preserving the exact fault ABI. Test signals include networking checksum tests, packet RX/TX validation, fault-injected copy paths, and comparison against generic C checksum implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/checksum_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/checksum_64.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/checksum_64.S

This 64-bit checksum implementation exports the same checksum ABI as the 32-bit file: `__csum_partial`, `csum_partial_copy_generic`, and `csum_ipv6_magic`. The main checksum path handles halfword alignment, then uses an aggressively scheduled 64-byte unrolled loop to avoid POWER6/POWER7 XER carry-chain stalls from back-to-back `adde`. It saves `r14-r16` only for the large loop and folds the 64-bit accumulator into a 32-bit checksum at the end.

The copy/checksum variant uses macros that stamp `EX_TABLE` entries for source and destination operations. It aligns source to doubleword where possible, copies 64-byte chunks with paired loads/stores and checksum accumulation, then handles doubleword, word, halfword, and byte tails. Faults restore any nonvolatile registers used by the large loop and return zero, matching the generic checksum-copy contract. `csum_ipv6_magic` uses 64-bit loads for the two IPv6 addresses, adjusts length/protocol byte order under little endian, folds twice, complements, and returns a `__sum16`.

Dependencies include the PowerPC ABI, `ppc_asm.h`, exception tables, and endian configuration. Risks include misfolding carry from 64-bit accumulation, byte-order mismatches in IPv6 pseudo-header handling, and exception recovery after the stack frame is active. Test signals are IPv4/IPv6 checksum selftests, network traffic under BE/LE kernels, and deliberate uaccess faults through checksum-copy callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/checksum_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/code-patching.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/code-patching.c

This file is the central PowerPC runtime text patching engine. It exports low-level and safe patch APIs including `raw_patch_instruction`, `patch_instruction`, `patch_uint`, `patch_ulong`, `patch_instructions`, `patch_branch`, `create_cond_branch`, `branch_target`, and `translate_branch`. It supports ordinary and prefixed PowerPC instructions, so patch writes may be 32 or 64 bits.

Control flow splits into early/relaxed patching and strict RWX patching. `poking_init()` installs CPU hotplug setup for per-CPU patching contexts. Hash or non-mm patching maps the target PFN into a per-CPU vmalloc text-poke area; SMP radix patching allocates a per-CPU temporary `mm_struct`, maps one randomized page, switches to it with IRQs disabled, suspends breakpoints, patches through the alias, flushes data/instruction caches, clears the PTE, and flushes the TLB. Multi-instruction patching walks page-sized pieces and can either copy a code buffer or repeat a single instruction.

State persists in per-CPU `patch_context` and the static key `poking_init_done`. Dependencies include MMU helpers, CPU hotplug, jump labels, nofault stores, `ppc_inst_t`, cache/TLB flush APIs, and branch encoding helpers. Integration points include ftrace, kprobes, modules, BPF JIT, security mitigations, and feature fixups. Risks are high: wrong cache synchronization, stale TLB aliases, patching across pages, mis-encoding relative branches, or instrumenting this code. Tests are `CONFIG_CODE_PATCHING_SELFTEST`, module/ftrace/kprobe exercise, radix/hash boot coverage, and prefixed-instruction patch tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/code-patching.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/copy_32.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/copy_32.S

This 32-bit assembly file provides core memory and user-copy primitives: `memset16`, `memset`, `memmove`, `memcpy`, `backwards_memcpy`, and `__copy_tofrom_user`, with KASAN-export aliases where configured. The memory routines optimize alignment, cacheline operations, and overlap handling. Early boot patch sites can disable the `dcbz` optimized paths until caches are active, then machine setup patches branches into normal fast paths.

`memset` expands byte values to words, aligns stores, optionally zeroes full cachelines with `dcbz`, then writes word and byte tails. `memcpy`/`memmove` choose forward or backward copy based on overlap, use a cacheline loop for non-overlapping cacheable copies, and fall back to `generic_memcpy` for overlap or early no-cache state. `__copy_tofrom_user` mirrors the copy loop but marks every load/store/dcbz region with exception table entries. Fault handlers compute bytes not copied, distinguish read and write faults, and on read faults attempt byte-by-byte progress before returning the remaining length.

State is register-only, with patch-site metadata and exception-table metadata. Dependencies include cache constants, `patch_site`, KASAN wrappers, and uaccess ABI. Risks include incorrect remaining-byte accounting, unsafe `dcbz` before cache enablement, overlap bugs, and fault recovery that clears or advances the wrong destination range. Test signals include uaccess fault tests, copy_{to,from}_user stress, KASAN/non-KASAN 32-bit builds, and early boot on cache-sensitive platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/copy_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/copy_mc_64.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/copy_mc_64.S

`copy_mc_64.S` exports `copy_mc_generic`, a 64-bit copy routine intended for machine-check tolerant memory copy paths. It copies from `from` to `to`, returns zero on success, and returns the number of bytes left when an exception occurs. This is integrated through `asm/uaccess.h` for copy-machine-check helpers.

Control flow keeps the original size in `r7`, aligns the source to 8 bytes with byte/halfword/word copies, then for large regions creates a stack frame and saves `r14-r22`. The main loop copies 128-byte cacheline-sized blocks with unrolled 16 doubleword loads and stores, followed by 64-, 32-, 16-, 8-, 4-, 2-, and 1-byte tails. `err1`, `err2`, and `err3` macros attach exception table entries. Large-loop faults restore nonvolatile registers and fall into a byte-by-byte retry path to find the precise remaining count; final faults return the current CTR count.

State is limited to registers and exception tables; no persistent data is modified beyond the destination bytes already copied. Dependencies are the PPC64 ABI, `EX_TABLE`, and uaccess machine-check wrappers. Risks include returning an imprecise residual count, failing to restore callee-saved registers on an exception, and treating write faults and source machine checks identically. Test signals include NVDIMM or machine-check injection tests, copy_mc uaccess fallbacks, and exception-table validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/copy_mc_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/copypage_64.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/copypage_64.S

This file exports the generic 64-bit `copy_page` routine. It copies exactly `PAGE_SIZE` bytes from source in `r4` to destination in `r3`. At entry it uses CPU feature fixup sections: if `CPU_FTR_VMX_COPY` is absent on Book3S 64, the patched code can branch to `copypage_power7`; if cache-block zeroing is available, it prefetches source and zeroes destination cachelines using cache parameters from `ppc64_caches`.

The main copy loop is scalar and copies the page in 128-byte strides. It adjusts the destination pointer, preloads the first chunk, then performs an unrolled sequence of doubleword loads and stores, using `ldu`/`stdu` to advance pointers. A final unrolled block finishes the last stride and returns. There is no exception-table recovery because page copy operates on kernel-mapped pages and is expected not to fault.

State is transient register state only. Dependencies include `asm/page.h`, `ppc64_caches`, feature-fixup macros, and the external Power7 optimized routine. Integration points are core MM page copy operations and kernel page migration/fault handling. Risks are incorrect feature patching, cache-block size assumptions, and page-size assumptions if configuration changes. Test signals include boot-time page allocator activity, MM selftests, page migration, transparent hugepage interactions that call page copy, and running with/without `CPU_FTR_CP_USE_DCBTZ` and `CPU_FTR_VMX_COPY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/copypage_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/copypage_power7.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/copypage_power7.S

`copypage_power7.S` implements a POWER7-oriented page copy routine, `copypage_power7`, used as an optimized target from `copy_page` feature fixups. It sets up enhanced data-cache touch streams for source and destination, with parameters adjusted for 64 KiB versus smaller page configurations, then copies in 128-byte units.

When Altivec is configured, the routine calls `enter_vmx_ops`. If VMX access is granted, it loops over the page using eight vector loads and stores per 128-byte chunk and tail-calls `exit_vmx_ops`. If VMX is not available or Altivec is not configured, it uses a scalar loop that saves `r14-r20`, loads sixteen doublewords, stores sixteen doublewords, advances by 128 bytes, and restores registers at the end. The control flow is all deterministic for `PAGE_SIZE / 128` iterations and has no exception recovery.

State consists of the temporary VMX enable/disable state managed by `enter_vmx_ops`/`exit_vmx_ops` and the saved nonvolatile GPRs in the scalar path. Dependencies include Altivec availability, cache-stream macros, page size, and ABI save/restore rules. Risks include using VMX in an unsafe context, mismatched stack unwind when VMX entry fails, and poor behavior on CPUs where stream setup is not suitable. Test signals are Book3S 64 page-copy benchmarks, VMX enabled/disabled kernels, 4 KiB and 64 KiB page builds, and MM stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/copypage_power7.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/copyuser_64.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/copyuser_64.S

This file exports the default 64-bit user/kernel copy engine: `__copy_tofrom_user` and `__copy_tofrom_user_base`. It copies `n` bytes between two addresses and returns the number of bytes not copied. The top-level entry uses feature fixups to branch to the POWER7 implementation when `CPU_FTR_VMX_COPY` is available.

The base control flow saves original destination, source, and length in the red-zone area, checks for a special 4 KiB aligned page copy, aligns the destination, handles unaligned source with endian-aware shift/or assembly, then uses unrolled doubleword copies and compact tails. Load and store exception macros encode handlers as offsets from the current destination position. Load faults recompute source/destination progress from the saved originals, retry byte-by-byte to copy as much as possible, and return the remaining count. Store faults may also try to advance over destination page-boundary overlap before returning residual bytes. A POWER4-style 4 KiB page copy path has its own abort handler that restores registers and falls back to the normal aligned path.

State is saved arguments and nonvolatile registers; persistence is only destination bytes successfully copied. Dependencies include exception tables, feature-fixup macros, endian helpers, and `asm/uaccess.h`. Risks are exact exception handler offset layout, residual count correctness, unaligned endian shifts, and page-copy fallback. Test signals include uaccess fault injection, copy_to/from_user tests, BE/LE kernels, and POWER feature-fixup selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/copyuser_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/copyuser_power7.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/copyuser_power7.S

This file provides POWER7-tuned user copy routines: `__copy_tofrom_user_power7` and, under Altivec, `__copy_tofrom_user_power7_vmx`. They share the same ABI as the base copy routine, returning zero on full success or remaining bytes on fault. The non-VMX path aligns source, copies large 128-byte blocks with unrolled doubleword loads/stores, then copies 64/32/16/8/4/2/1-byte tails.

Fault handling is intentionally conservative. Early or tail faults route through `err1` and fall back to `__copy_tofrom_user_base` using saved original arguments. Large-loop faults restore saved nonvolatile registers before falling back. The VMX path enters VMX state, sets source/destination cache touch streams, handles relatively aligned and unaligned vector copies separately, and uses `vperm` with `lvsl`/`lvsr` to assemble unaligned vectors. VMX exception handlers compute remaining length from original destination and length, restore LR and stack, and return without falling back.

State includes saved original arguments, optional VMX enable state, and callee-saved GPR/VR handling. Dependencies include Altivec, `enter_vmx_ops`, cache-stream macros, exception tables, endian vector permute definitions, and the base user-copy routine. Risks are VMX use in contexts where it cannot be enabled, residual count accuracy after vector stores, and fallback recursion assumptions. Test signals include large user-copy benchmarks, VMX/no-VMX builds, fault injection across vector and scalar ranges, and 4 KiB+ copy workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/copyuser_power7.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/crtsavres.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/crtsavres.S

`crtsavres.S` supplies compiler helper routines for saving and restoring nonvolatile registers when `CONFIG_CC_OPTIMIZE_FOR_SIZE` makes GCC emit calls to shared save/restore thunks. It covers 32-bit and 64-bit PowerPC ABIs, plus optional Altivec vector register save/restore helpers. The Makefile also builds it for modules on newer non-BFD linker combinations where final vmlinux may synthesize save/restore sections but modules still need the object.

The file is a table of fall-through labels. On 32-bit, `_savegpr_14` through `_savegpr_31` and aliases `_save32gpr_*` store GPRs relative to `r11`; `_restgpr_*` reload them; `_restgpr_*_x` also restores LR and stack pointer for epilogue helpers. On 64-bit, `_savegpr0_14` through `_savegpr0_31` store GPRs relative to `r1` and save LR in the ABI slot; restore helpers reload LR where needed. Altivec helpers save/restore `v20-v31` relative to `r0`.

There is no persistent state; correctness is ABI layout. Dependencies are compiler code generation conventions, stack frame layout, and optional Altivec. Risks include wrong offsets for an ABI variant, missing symbol aliases expected by GCC, and building the file when linker-provided alternatives conflict. Test signals are successful optimized-for-size kernel/module links, module load tests, and objdump checks for helper references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/crtsavres.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/div64.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/div64.S

This 32-bit PowerPC helper implements `__div64_32`, dividing an unsigned 64-bit dividend by a 32-bit divisor. The caller passes a pointer to the 64-bit dividend in `r3` and the divisor in `r4`; the routine overwrites the pointed dividend with the 64-bit quotient and returns the 32-bit remainder in `r3`. It assumes the high 32 bits of the dividend are initially nonzero.

Control flow first handles the case where the high word can produce a high quotient word directly. It then loops while the high word remains nonzero, estimating a quotient component by normalizing the dividend/divisor when the high bits permit, multiplying the estimate by the divisor, subtracting the product from the 64-bit working dividend with carry/borrow, and accumulating the low quotient word. When the high word is zero, it performs a final 32-bit `divwu` for the low word and stores both quotient words.

State is only the in-place dividend/quotient memory and registers. Dependencies include the 32-bit PowerPC integer instruction set and the kernel's generic div64 helper ABI. Risks are divide-by-zero being the caller's responsibility, quotient estimate edge cases, and carry/borrow correctness. Test signals include generic `do_div` users, arithmetic selftests on 32-bit PowerPC, and boundary values where high dividend is near or above divisor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/div64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/error-inject.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/error-inject.c

This small file implements the PowerPC hook for function error injection. It exports `override_function_with_return(struct pt_regs *regs)` for the generic error-injection/kprobe machinery. The function emulates a `blr` at the probed function entry by setting the return instruction pointer from the link register saved in `regs`.

Control flow is intentionally single-step: a kprobe captures registers at entry of an allowlisted function, error-injection core arranges the desired return value elsewhere, then this helper redirects execution to the caller by calling `regs_set_return_ip(regs, regs->link)`. The comment notes that 32-bit userspace on a 64-bit kernel is not relevant for this kernel/module function-entry context. The symbol is marked `NOKPROBE_SYMBOL` to avoid probing the override hook itself.

There is no persistent state. Dependencies include kprobes, `pt_regs`, and the PowerPC calling convention where LR is the return address. Integration points are `CONFIG_FUNCTION_ERROR_INJECTION`, kernel fault-injection tests, and kprobe-based override paths. Risks are corrupting control flow if used for functions whose entry state or ABI is not compatible, or if LR is not the intended return target. Test signals include function error-injection selftests and kprobe blacklist validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/error-inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/feature-fixups-test.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/feature-fixups-test.S

This assembly file supplies the code/data fixtures consumed by `feature-fixups.c` selftests under `CONFIG_FTR_FIXUP_SELFTEST`. It defines original, alternative, and expected instruction sequences for CPU feature, firmware feature, lwsync, branch translation, nested macro, and prefixed-instruction fixup cases.

The early sections define `ftr_fixup_test1` through `ftr_fixup_test7` to test nop-out behavior, replacement with shorter/longer alternative sections, branches internal to an alternative, external branch translation, and branch-to-end cases. The `MAKE_MACRO_TEST` and `MAKE_MACRO_TEST_EXPECTED` macros generate large matrices for `FTR` and, on 64-bit, `FW_FTR` macros: simple feature sections, nested sections, alt sections, nested alt sections, padded alternatives, and larger else cases. Later labels define `lwsync_fixup_test` expected either as `lwsync` or `sync`, plus prefixed instruction tests where a prefixed instruction occupies two words and must be nop-filled or replaced atomically as a logical instruction.

State is only static text fixtures linked into the kernel test image. Dependencies include `asm/feature-fixups.h`, PPC opcode macros, and the C selftest's external symbol references. Risks are fixture drift from macro semantics, assembler layout changes that hide branch translation bugs, and prefixed-instruction expectations on 32-bit builds. Test signal is the late-init "feature fixup self-tests" run and absence of printed failure lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/feature-fixups-test.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/feature-fixups.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/feature-fixups.c

This file applies runtime code fixups based on CPU, MMU, firmware, and security-mitigation features. Core APIs include `do_feature_fixups`, `apply_feature_fixups`, `update_mmu_feature_fixups`, `setup_feature_keys`, and mitigation-specific patchers for STF barriers, L1D flushes, RFI flushes, uaccess flushes, barrier-nospec, BTB flushes, and lwsync replacement.

Control flow starts with `fixup_entry` tables emitted by assembly macros. `patch_feature_section_mask()` computes original and alternative addresses, checks that alternatives fit, copies alternative instructions when the current feature value does not match, translates relative branches that leave the alt section, and nop-fills remaining original slots. Boot `apply_feature_fixups()` saves observed feature values, patches CPU/MMU/lwsync/firmware sections, and handles relocatable final interrupt copying. Security fixups patch instruction arrays at linker-provided fixup sections, often under `stop_machine()` and `exit_flush_lock` when interrupt exit code could be executing concurrently. `setup_feature_keys()` initializes jump labels for feature predicates and marks static-key checks initialized.

State persists in saved feature snapshots, reentrancy booleans for interrupt exits, `exit_flush_lock`, and exported `static_key_feature_checks_initialized`. Dependencies include text patching, linker sections, `cur_cpu_spec`, firmware feature globals, stop_machine, static keys, and security feature enums. Risks are severe: half-patched interrupt exits, invalid post-init addresses, branch translation mistakes, or changed feature bits after patching. Test signals include `CONFIG_FTR_FIXUP_SELFTEST`, mitigation boot logs, `late_initcall(check_features)`, and cross-CPU stop-machine stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/feature-fixups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/hweight_64.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/hweight_64.S

This file exports optimized 64-bit PowerPC population-count helpers: `__arch_hweight8`, `__arch_hweight16`, `__arch_hweight32`, and `__arch_hweight64`. Each returns the number of set bits in the low 8, 16, 32, or 64 bits of `r3`.

Each function is wrapped in feature-fixup sections. If `CPU_FTR_POPCNTB` is missing, the code branches to generic software helpers such as `__sw_hweight32`. If byte popcount exists but doubleword popcount does not, wider functions use `PPC_POPCNTB` plus shifts and adds to aggregate byte counts. If `CPU_FTR_POPCNTD` exists, 16/32/64-bit paths use word or doubleword popcount directly and mask down to the final byte result. Nested feature sections select the best available instruction while keeping a valid fallback layout.

There is no persistent state. Dependencies include `asm/feature-fixups.h`, `PPC_POPCNT*` opcode macros, software hweight helpers, and the kernel bitops API. Risks are wrong feature selection, accidentally counting high unused bits for narrower helpers, and macro layout breakage under `-mminimal-toc`. Test signals include lib/bitmap and hweight tests, boot on CPUs with/without popcount instructions, and comparing arch helpers to software helpers for randomized values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/hweight_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/ldstfp.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/ldstfp.S

`ldstfp.S` provides floating-point, Altivec/VMX, and VSX register access helpers for instruction emulation. It exports `get_fpr`, `put_fpr`, optional `get_vr`/`put_vr`, optional `get_vsr`/`put_vsr`, `load_vsrn`, `store_vsrn`, and conversion helpers `conv_sp_to_dp` and `conv_dp_to_sp`.

The FPR and VR helpers temporarily enable the relevant MSR bit (`MSR_FP` or `MSR_VEC`), use computed branch tables of 32 store/load instructions selected by register number, then restore the original MSR and synchronize with `isync`. VSX register move helpers use 64-entry branch tables around `XXLOR`. `load_vsrn` and `store_vsrn` build a small stack frame, save LR and `vs0` when needed, enable `MSR_VSX`, load or store a vector doubleword, handle little-endian doubleword swapping with `XXSWAPD`, then restore MSR and stack. Conversion helpers preserve `fr0` while doing scalar FP load/store conversion.

State changes are temporary MSR enablement and stack-saved registers. Dependencies include instruction emulation callers, MSR manipulation macros, VSX opcodes, endian configuration, and FPU/Altivec/VSX config gates. Risks are leaving FP/vector state enabled incorrectly, clobbering `vs0`/`fr0`, and missing endian swaps. Test signals include emulate-step tests, FP/VSX instruction emulation, KVM or signal-context scenarios that trigger emulated loads/stores, and endian coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/ldstfp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/locks.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/locks.c

This file implements SPLPAR-aware yielding helpers for classic PowerPC spinlocks and rwlocks when queued spinlocks are not selected. Under `CONFIG_PPC_SPLPAR`, it exports `splpar_spin_yield(arch_spinlock_t *lock)` and defines `splpar_rw_yield(arch_rwlock_t *rw)`.

The spinlock path reads `lock->slock`, returns if unlocked, extracts the holder CPU from low bits, validates it, samples the holder's hypervisor yield count, and returns if the vCPU is currently running. After a read memory barrier, it verifies the lock word is unchanged and calls `yield_to_preempted(holder_cpu, yield_count)`. The rwlock path is similar but only yields when the rwlock value is negative, indicating a writer is present and the holder CPU can be decoded.

State is read-only lock state plus hypervisor dispatch/yield counters; no persistent kernel state is updated here. Dependencies include SPLPAR hypervisor calls, `yield_count_of`, `yield_to_preempted`, CPU numbering, and lock word encoding. Integration is the lock slow path on shared-processor PowerPC systems without `CONFIG_PPC_QUEUED_SPINLOCKS`. Risks include stale holder CPU fields, yielding when the lock changed, and lock encoding changes. Test signals are shared-LPAR contention benchmarks, lockdep/smp stress, and builds with SPLPAR enabled and queued spinlocks disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/locks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/mem_64.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/mem_64.S

This 64-bit memory helper file exports `memset`, `memmove`, `backwards_memcpy`, and non-KASAN internal helpers `__memset16`, `__memset32`, and `__memset64`. The actual forward `memcpy` symbol lives in `memcpy_64.S` or a feature-routed Power7 variant; `memmove` branches to `memcpy` when the destination is not above the source.

`memset` expands the byte/halfword/word pattern to a 64-bit value, aligns the destination to eight bytes using byte/halfword/word stores, writes 64-byte unrolled blocks, then handles 32/16/8-byte chunks and 4/2/1-byte tails. KASAN wrappers export instrumented aliases. `backwards_memcpy` supports overlapping move when destination is above source: it starts at the end, uses pairs of word loads/stores where possible, aligns backward, and finishes with word/byte tails.

State is only destination memory and registers. Dependencies include PPC64 ABI, KASAN symbol wrappers, and the external forward `memcpy`. Risks are overlap direction mistakes, pattern expansion bugs for `__memset16/32/64`, and alignment assumptions in backwards copy. Test signals include generic string/memory tests, KASAN and non-KASAN builds, `memmove` overlap fuzzing, and boot-time memset-heavy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/mem_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/memcmp_32.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/memcmp_32.S

This file exports the 32-bit PowerPC `memcmp` implementation. It compares two buffers in `r3` and `r4` for `r5` bytes and returns zero, positive, or negative according to the first differing byte/word ordering expected by the C library-style kernel ABI.

Control flow divides the length by four and performs a word loop with indexed `lwzx` loads. If a word differs, it returns `1` or `-1` based on unsigned word comparison rather than subtracting the whole word. If all full words match, it checks remaining two-byte and one-byte tails. The halfword and byte tails subtract the second value from the first to produce an exact signed difference for small tails.

State is register-only. Dependencies are the PowerPC 32-bit calling convention and `EXPORT_SYMBOL(memcmp)` for kernel users. The implementation assumes regular kernel addresses and has no exception table because `memcmp` is not a uaccess primitive. Risks include endian-sensitive semantics for word-level early differences: returning only sign is acceptable for `memcmp`, but the sign must match the first byte difference under the architecture's load ordering. Test signals include lib/string tests, crypto and filesystem comparison workloads, and randomized comparison against generic C `memcmp`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/memcmp_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/memcmp_64.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/memcmp_64.S

This file exports an optimized 64-bit `memcmp`. It supports big and little endian by defining byte-reversing load macros for little endian (`lhbrx`, `lwbrx`, `ldbrx`) so unsigned doubleword comparisons preserve byte-order semantics. It has scalar short, aligned, different-offset, long, and optional VMX paths.

Control flow first handles zero and short lengths with byte comparisons. For longer ranges it checks whether the two addresses share the same 8-byte alignment. Same-offset paths align by masking and shifting an initial doubleword, then compare 32-byte scalar groups with four doubleword comparisons. Different-offset paths align only the first source and use unaligned/reordered loads for the second. For lengths at least 4 KiB on CPUs with `CPU_FTR_ARCH_207S`, Altivec paths enter VMX state, precheck the first 32 bytes to avoid expensive VMX setup for common early mismatches, then compare 16/32-byte vector chunks, using `vperm` for different 16-byte offsets. On mismatch, it falls back to scalar comparison of the relevant 16 bytes to return the correct sign.

State includes temporary VMX enablement and saved nonvolatile GPRs in scalar long paths. Dependencies include `enter_vmx_ops`, feature fixups, endian macros, and string ABI. Risks are page-crossing overreads for tails, endian sign correctness, VMX state management, and fallback after vector mismatch. Test signals include string selftests, BE/LE randomized fuzzing, large-buffer benchmarks, and VMX/no-VMX boots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/memcmp_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/memcpy_64.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/memcpy_64.S

This file exports the generic 64-bit `memcpy` implementation with KASAN aliases. It is feature-routed: when `CPU_FTR_VMX_COPY` is absent on Book3S 64, the patched entry can branch to `memcpy_power7`; on little endian there is a simple byte-copy placeholder expected to be replaced at runtime.

The big-endian scalar path saves the original destination for return, handles short copies, aligns the destination to eight bytes, optionally bypasses the unaligned-destination branch on CPUs with unaligned load/store support and without cache-block zero use, then runs aligned or source-unaligned doubleword copy loops. Source-unaligned copies combine adjacent loads with shifts to form destination doublewords. Tails handle word, halfword, and byte pieces, and every path restores the original destination pointer in `r3`.

State is only destination memory and stack-saved return pointer. Dependencies include feature-fixup macros, `memcpy_power7`, KASAN wrappers, endian configuration, and CPU feature bits. There are no exception handlers because kernel `memcpy` is not a fault-tolerant uaccess primitive. Risks include runtime feature patching on little endian, unaligned shift/or correctness, overlap misuse by callers that should use `memmove`, and return pointer preservation. Test signals include lib/string tests, BE/LE boot, KASAN builds, and comparison against generic `memcpy` under randomized alignment/length inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/memcpy_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/memcpy_power7.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/memcpy_power7.S

`memcpy_power7.S` implements a POWER7-optimized `memcpy_power7` target. It returns the original destination pointer and supports scalar and optional Altivec/VMX copies. The entry chooses VMX only for copies larger than 4096 bytes when `CPU_FTR_ALTIVEC` is available through feature-fixup logic; otherwise it uses the scalar 128-byte loop.

The scalar path aligns the source to 8 bytes with byte/halfword/word prologue copies, saves `r14-r22` for large loops, copies 128-byte chunks using sixteen doubleword loads/stores, then handles 64/32/16/8/4/2/1-byte tails. The VMX path enters VMX state, configures source and destination touch streams, checks relative 16-byte alignment, aligns destination, and copies 128-byte vector chunks. If source and destination are not relatively aligned, it uses `lvsl`/`lvsr` and `vperm` to assemble aligned destination vectors from adjacent source vectors. It tail-calls `exit_vmx_ops` after restoring stack state.

State is destination memory, saved original destination, optional VMX enablement, and saved nonvolatile registers. Dependencies include Altivec, feature fixups, cache-stream macros, and endian-specific vector permutes. Risks include VMX state leaks, unaligned vector assembly bugs, threshold regressions, and overlap misuse by callers. Test signals include large memcpy benchmarks, VMX enabled/disabled configs, randomized alignment tests, and fallback comparison with generic `memcpy_64.S`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/memcpy_power7.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/pmem.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/pmem.c

This file implements PowerPC persistent-memory cache maintenance hooks. It exports `arch_wb_cache_pmem`, `arch_invalidate_pmem`, and `memcpy_flushcache`, and defines `copy_from_user_flushcache` for `CONFIG_ARCH_HAS_UACCESS_FLUSHCACHE` style users.

The internal helpers compute L1 cacheline size and alignment, then loop over every cacheline intersecting `[start, stop)`. `__clean_pmem_range()` uses `PPC_DCBSTPS` to push dirty data toward persistence; `__flush_pmem_range()` uses `PPC_DCBFPS` to flush/invalidate persistent-storage cache state. Public `clean_pmem_range()` and `flush_pmem_range()` only execute those instructions when `CPU_FTR_ARCH_207S` is present. `copy_from_user_flushcache()` masks the user pointer, copies with `__copy_from_user`, then cleans the entire destination range; `memcpy_flushcache()` does a normal `memcpy` and cleans the destination.

State persistence is literal persistent-memory durability: the goal is flushing cachelines for pmem writes. Dependencies include libnvdimm, uaccess, cacheflush definitions, CPU feature detection, and low-level dcbf/dcbst persistent-storage opcodes. Risks are cleaning bytes that were not copied when `__copy_from_user` faults, missing required ordering barriers outside this helper, and no-op behavior on CPUs without ARCH_207S. Test signals include pmem/DAX tests, libnvdimm flush validation, faulted user-copy cases, and CPU feature coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/pmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/qspinlock.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/qspinlock.c

This is the PowerPC queued spinlock slow path. It exports `queued_spin_lock_slowpath` and, under paravirtual spinlocks, `pv_spinlocks_init`, while exposing many debugfs tunables for stealing and paravirtual yielding. It uses a compact lock word with locked, must-queue, sleepy, owner CPU, and tail CPU fields plus per-CPU MCS-like `qnode` arrays.

Control flow first tries bounded lock stealing in `try_to_steal_lock()`, with speculation barriers and optional yielding to a preempted owner. If stealing fails, `queued_spin_lock_mcs_queue()` allocates a per-CPU node, publishes its tail with release ordering, links behind the previous tail, waits for its node to be unlocked, then as queue head spins on the lock word. It may set `_Q_MUST_Q_VAL` to stop stealers after head spin limits, propagates "sleepy" state when preempted owners or waiters are observed, and can yield or prod vCPUs through paravirt hooks. Acquiring uses `trylock_clean_tail()` to set locked state and clear the tail if this CPU is last, then wakes the next MCS node.

Persistent state includes per-CPU `qnodes`, sleepy timestamps, tunable globals, and debugfs files under `arch_debugfs_dir`. Dependencies include atomic `lwarx/stwcx.`, PPC memory barriers, topology, paravirt yield/prod hooks, trace lock events, RCU synchronization for steal toggles, and `asm/qspinlock.h` encoding. Risks are memory-order bugs, queue corruption under nested locks beyond `MAX_NODES`, unfair stealing, and paravirt heuristics causing latency. Test signals include locktorture, shared-processor LPAR stress, debugfs tuning, KCSAN/lockdep, and NUMA contention benchmarks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/qspinlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/quad.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/quad.S

`quad.S` provides quadword load/store helpers for instruction emulation. It exports `do_lq`, `do_stq`, `do_lqarx`, and `do_stqcx`. These wrap PowerPC quadword and atomic quadword instructions and convert memory faults into `-EFAULT`.

`do_lq(ea, regs)` executes `lq` from effective address `ea`, stores the two result GPR values into `regs[0]` and `regs[1]`, and returns zero. `do_stq(ea, val0, val1)` stores the register pair with `stq`. `do_lqarx(ea, regs)` performs a reservation-form quadword load using `PPC_LQARX`, and `do_stqcx(ea, val0, val1, crp)` performs conditional quadword store, writes the resulting condition register to `*crp`, and returns zero. Each instruction has an `EX_TABLE` entry that branches to a `-EFAULT` return path.

State includes reservation state for lqarx/stqcx and the caller-provided output buffers. Dependencies include PPC opcode macros, exception tables, instruction emulation, and ABI pairing of registers. Risks are clobbering the wrong CR value, reservation semantics differing from emulated instruction expectations, and fault recovery after partial state changes. Test signals include emulate-step tests for lq/stq/lqarx/stqcx, alignment/fault injection, and transactional/atomic instruction emulation coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/quad.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/restart_table.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/restart_table.c

This file implements linear searches over linker-defined PowerPC interrupt restart metadata. It provides `search_kernel_soft_mask_table(unsigned long addr)` and `search_kernel_restart_table(unsigned long addr)`, both marked `NOKPROBE_SYMBOL` because they can run in fragile interrupt/NMI paths.

`search_kernel_soft_mask_table()` walks `__start___soft_mask_table` to `__stop___soft_mask_table`, comparing the supplied address against each `[start, end)` range and returning true when the address lies in soft-masked interrupt code. `search_kernel_restart_table()` similarly walks `__start___restart_table` to `__stop___restart_table` and returns the `fixup` address for the matching range, or zero if there is no restart entry. The Makefile disables KASAN for this object because these functions may be called in real mode or NMI interrupt paths.

State is read-only linker table contents; there is no mutation or persistence. Dependencies include `asm/interrupt.h`, linker section symbols, and low-level interrupt code that emits table entries. Integration appears in interrupt handling code that decides whether an interrupted instruction can restart at a fixup. Risks are table ordering/coverage mistakes, linear search cost in interrupt context, sanitizer/probe recursion, and invalid virtual accesses in real mode. Test signals include interrupt/NMI stress, soft-mask/restart exception tests, and objdump/linker validation of table ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/restart_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/rheap.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/rheap.c

`rheap.c` implements a "remote heap" allocator for managing address ranges without storing allocator metadata inside the managed memory. It exports creation, initialization, region attach/detach, aligned/fixed allocation, free, stats, owner update, and dump APIs around `rh_info_t` and `rh_block_t`.

The allocator keeps three lists in `rh_info_t`: empty metadata slots, free ranges, and taken ranges. `grow()` reallocates the metadata array with `GFP_ATOMIC`, copies old blocks, and fixes embedded list pointers by applying the allocation delta. `rh_attach_region()` aligns and coalesces a new free range. `rh_detach_region()` removes an aligned range from one free block, splitting if needed. `rh_alloc_align()` finds a free block that can satisfy size and requested alignment, splits front/back fragments, marks owner, and inserts into the sorted taken list. `rh_alloc_fixed()` allocates a caller-specified aligned range from a free block. `rh_free()` moves a taken block back to free and coalesces adjacent free blocks.

State persists in caller-owned `rh_info_t`, dynamic/static block arrays, and owner string pointers. Dependencies include `asm/rheap.h`, kernel lists, slab allocation, and exported GPL users. There is no internal locking, so callers must serialize. Risks include integer overflow in `start + size`, returning unsigned long-encoded negative errors, pointer fixup bugs after grow, off-by-one checks in `rh_free`/`rh_set_owner`, and fragmentation if metadata slots run out. Test signals include allocator unit tests, attach/detach split/coalesce cases, fixed allocation overlap tests, and early static initialization users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/rheap.c -->
