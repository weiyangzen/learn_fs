# subset-b-000906 Research

Grouped research report for the requested x86 KVM/Xen and x86 library files. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/x86.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/x86.h

Purpose: this is the central private header for x86 KVM core helpers. It aggregates common KVM x86 capabilities, host CPU state, nested virtualization helpers, guest mode predicates, MMIO exit preparation, MSR return conventions, CR4 feature validation, hypercall glue, and small policy helpers consumed by VMX, SVM, TDX, emulator, MMU, interrupt, timing, and MSR paths.

Important APIs/types/functions: `struct kvm_caps` records host-supported TSC scaling, bus-lock/notify VM exits, VM types, MCE/XCR0/XSS/perf/quirk masks. `struct kvm_host_values` snapshots host max physical address and architectural MSRs. Inline helpers include PLE growth/shrink, `kvm_leave_nested`, `kvm_nested_vmexit_handle_ibrs`, `kvm_can_set_cpuid_and_feature_msrs`, event queue helpers, mode predicates (`is_protmode`, `is_long_mode`, `is_64_bit_mode`, `is_pae_paging`), canonical-address checks, MMIO cache helpers, register read/write width handling, disabled-exit predicates, PAT/DR validation, and CET validation. It also declares major cross-file APIs such as guest time update, virtual guest access, emulation, MTRR MSRs, INVPCID, memory-failure handling, and hypercall handling.

Control flow: most functions are low-level guards used by hot paths. Guest mode helpers inspect cached vCPU state. MMIO caching stores a generation-tagged GVA/GFN/access tuple unless memslots are being updated, and later match helpers compare against the current memslot generation. Hypercall macros call `____kvm_emulate_hypercall()` and then complete positive returns. `kvm_nested_vmexit_handle_ibrs()` conditionally issues an indirect branch prediction barrier when nested exits could expose L1 to L2 predictor state.

State and persistence behavior: this header mutates in-memory KVM/vCPU state only: exception/interrupt queues, `arch.disabled_exits`, MMIO cache fields, run exit structures, and per-CPU L1TF flush flags. There is no persistent storage. Many helpers depend on stable vCPU state and memslot generation counters.

Dependencies/integration points: depends on KVM host structs, x86 FPU/xstate, MCE, pvclock, KVM register cache, emulator, CPUID, x86 feature bits, and `kvm_x86_ops`. It is included broadly by KVM x86 implementation files and forms a shared contract between common KVM code and vendor backends.

Risks: mistakes in static inline helpers have wide blast radius. Canonical-address rules differ for MSR/descriptor/invlpg operands versus normal operands and must track hardware behavior. `kvm_can_set_cpuid_and_feature_msrs()` prevents unsupported model rewrites after vCPU execution; bypassing it risks stale virtualization state. MMIO caching depends on generation invalidation. Security-sensitive helpers cover IBRS, L1TF flushes, CET validity, and guest/host interrupt accounting.

Test signals: KVM selftests around CPUID/MSR setting, nested VMX/SVM exits, MMIO emulation, hypercalls, CET, PAT/DR MSR validation, and migration-sensitive timing exercise this header indirectly. Compile-time `BUILD_BUG_ON` and `static_assert` checks are important structural tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/x86.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/xen.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/xen.c

Purpose: implements KVM's in-kernel Xen HVM emulation. It provides shared-info and vcpu-info page management, Xen runstate accounting, Xen timers, event-channel injection/routing, hypercall acceleration, eventfd-backed outbound event channels, userspace attribute handling, and VM/vCPU Xen lifecycle setup.

Important APIs/types/functions: externally visible functions include `kvm_xen_hvm_set_attr`, `kvm_xen_hvm_get_attr`, `kvm_xen_vcpu_set_attr`, `kvm_xen_vcpu_get_attr`, `kvm_xen_write_hypercall_page`, `kvm_xen_hvm_config`, `kvm_xen_hypercall`, `kvm_xen_set_evtchn_fast`, `kvm_xen_setup_evtchn`, `kvm_xen_hvm_evtchn_send`, init/destroy hooks, runstate update hooks, and interrupt injection helpers. Internal helpers include `kvm_xen_shared_info_init`, `xen_get_guest_pvclock`, `kvm_xen_start_timer`, `kvm_xen_update_runstate_guest`, `kvm_xen_schedop_poll`, `kvm_xen_hcall_*`, and eventfd assign/update/deassign/reset routines. `DEFINE_STATIC_KEY_DEFERRED_FALSE(kvm_xen_enabled, HZ)` gates fast checks.

Control flow: userspace configures VM-wide and vCPU-wide Xen attributes under `xen_lock` and SRCU, activating `gfn_to_pfn_cache` mappings for shared info, vcpu info, vcpu time, and runstate areas. Shared-info initialization writes Xen wallclock data using versioned pvclock updates. Xen timers translate guest absolute kvmclock deadlines to host hrtimers, prefer guest pvclock math when possible, and fall back to `get_kvmclock_ns()` during early or migration states. Hypercalls dispatch CPL0 calls for Xen version, event channel send, sched op, vcpu op, and set_timer_op; unsupported or userspace-permitted calls exit via `KVM_EXIT_XEN`. Event-channel delivery sets shared-info pending bits, vcpu-info pending selectors/upcall flags, kicks blocked vCPUs, or emits LAPIC upcall vectors.

State and persistence behavior: persistent state is per-VM/per-vCPU in memory: Xen long mode, shared-info cache, upcall vector, version, runstate update flag, IDR of event-channel send ports, hvm config blobs/MSR, vCPU Xen IDs, runstate times, timer expiry/pending flags, polling state, and GPC mappings. Guest-visible pages are marked dirty when updated so migration can preserve state. No disk persistence occurs.

Dependencies/integration points: integrates with KVM memory cache APIs, SRCU, hrtimers, eventfd, IDR, irq routing, LAPIC delivery, KVM hypercall/emulation paths, Hyper-V hypercall fallback, pvclock, scheduler run-delay accounting, Xen ABI structures, and KVM userspace ioctls. IRQ routing uses `.set = evtchn_set_fn`; userspace sends events via `KVM_XEN_HVM_EVTCHN_SEND`.

Risks: this file is concurrency-heavy. GPC mappings can fault or invalidate while event delivery runs, requiring SRCU, lock ordering, retry, and `-EWOULDBLOCK` fallback. Runstate writes may cross pages and must handle atomic scheduler-out contexts without sleeping. Timer migration snapshots can race with pending delivery but are intentionally idempotent. Eventfd IDR objects require SRCU grace periods before freeing. ABI layout `BUILD_BUG_ON`s are critical for 32/64-bit Xen compatibility.

Test signals: KVM Xen selftests should cover attribute set/get, shared-info wallclock placement, hypercall exits and completions, event-channel delivery/masking/polling, timer migration, vcpu runstate data/adjustments, 32-bit versus 64-bit layout, eventfd assign/update/deassign/reset, and irq routing. Runtime tracepoints `trace_kvm_xen_hypercall` and dirty-page observation are useful integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/xen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/xen.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/xen.h

Purpose: declares the KVM Xen emulation interface and provides fast inline predicates/stubs used by the wider x86 KVM core. It hides `CONFIG_KVM_XEN` differences while exposing event injection, attribute handling, hypercall-page configuration, VM/vCPU lifecycle, event-channel routing, and runstate helpers.

Important APIs/types/functions: under `CONFIG_KVM_XEN`, the header declares `kvm_xen_enabled`, `__kvm_xen_has_interrupt`, `kvm_xen_inject_pending_events`, `kvm_xen_inject_vcpu_vector`, VM/vCPU attr get/set functions, HVM attr get/set functions, event-channel send/setup functions, hypercall-page write/config functions, and lifecycle hooks. Inline helpers include `kvm_xen_sw_enable_lapic`, `kvm_xen_is_tsc_leaf`, `kvm_xen_msr_enabled`, `kvm_xen_is_hypercall_page_msr`, `kvm_xen_hypercall_enabled`, `kvm_xen_has_interrupt`, `kvm_xen_has_pending_events`, `kvm_xen_timer_enabled`, and `kvm_xen_has_pending_timer`. Stubs for disabled builds return false, zero, or success-compatible defaults. It also defines compatibility Xen vCPU info structures and runstate state-transition wrappers.

Control flow: most inline predicates first check the deferred static key to avoid overhead when no Xen VM is active. Interrupt detection requires active `vcpu_info_cache` and a configured upcall vector before calling the slow helper. LAPIC software-enable paths inject a pending Xen upcall if the vCPU becomes able to receive it. Runstate helpers call `kvm_xen_update_runstate()` with Xen `RUNSTATE_running` or `RUNSTATE_runnable`, with a warning if preemption state is inconsistent.

State and persistence behavior: the header itself persists nothing, but reads and mutates `vcpu->arch.xen` and `kvm->arch.xen` fields via inline helpers. When Xen is compiled out, callers get no-op behavior without changing state.

Dependencies/integration points: includes Xen CPUID/hypervisor ABI, pvclock ABI, Xen interface structures, jump-label ratelimit support, and KVM host structures. It is used by x86 KVM interrupt, MSR, CPUID, run loop, LAPIC, and hypercall code.

Risks: static-key gating must remain consistent with VM config refcounting in `xen.c`; otherwise Xen paths can be skipped or enabled unnecessarily. Stub return values are ABI-visible through KVM behavior, so disabled-config semantics must remain conservative. `kvm_xen_is_tsc_leaf()` must match Xen CPUID base/limit logic exactly.

Test signals: compile both `CONFIG_KVM_XEN=y` and `n`. Exercise CPUID Xen TSC leaf detection, hypercall-page MSR checks, LAPIC enable delivery, pending timer checks, and non-Xen VM fast paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/xen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/lib/Makefile

Purpose: controls which x86 architecture library objects are built into the kernel or lib archive and how generated instruction attribute tables are produced. It is the integration map for low-level delay, memory, checksum, instruction decoding, user access, MSR, cache, KASLR, error injection, retpoline, and atomic helper files.

Important build rules: disables KCOV and KCSAN sanitization for `delay.o`, and removes ftrace from `delay.o` under KCSAN to avoid lockdep/ftrace/KCSAN/udelay recursion. Defines the `inat-tables.c` generation rule using `arch/x86/tools/gen-insn-attr-x86.awk` over `x86-opcode-map.txt`; `inat.o` depends on the generated table and `clean-files` removes it. Common `lib-y` includes delay, misc, cmdline, cpu, usercopy, getuser, putuser, memcpy, and pc-conf-reg. Conditional entries add copy-machine-check, instruction decoder, KASLR, error injection, retpoline, SMP MSR/cache helpers, and always-built MSR/IOMEM/hweight objects.

Control flow: Kbuild selects 32-bit versus 64-bit variants based on `CONFIG_X86_32` and `BITS`. On 32-bit it includes `atomic64_32.o`, CX8 or 386 atomic64 assembly, checksum/string/memmove/cmpxchg8b helpers. On 64-bit it conditionally includes non-generic checksum helpers and always includes clear/copy page, memmove/memset, user copy, cmpxchg16b emulation, and BHI code.

State and persistence behavior: build-time only. It generates `inat-tables.c` in the object tree and influences final kernel symbol availability; it does not create runtime state.

Dependencies/integration points: integrates Kbuild config symbols, awk tool generation, architecture opcode maps, and low-level library sources used by the rest of the kernel. Exported symbols from built objects are consumed by core kernel, modules, KVM, networking, and memory subsystems.

Risks: wrong conditional selection can create duplicate symbols, missing architecture helpers, instrumentation recursion, or broken instruction decoding. The generated `inat-tables.c` must stay in sync with opcode maps. Sanitizer/ftrace flags are safety-critical for delay code.

Test signals: allnoconfig/defconfig and 32/64-bit build coverage, `make clean` for generated files, instruction decoder builds with `CONFIG_INSTRUCTION_DECODER`, and configs with KCSAN/KCOV/ftrace enabled are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/atomic64_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/atomic64_32.c

Purpose: provides the export policy macro for 32-bit x86 `atomic64_t` helper symbols and includes the generic Linux atomic64 implementation.

Important APIs/types/functions: defines `ATOMIC64_EXPORT` as `EXPORT_SYMBOL`, then includes `<linux/export.h>` and `<linux/atomic.h>`. The included atomic code uses the macro to export the architecture-backed 64-bit atomic operations implemented by the selected x86 assembly helpers.

Control flow: there is no local runtime control flow. The file acts as a compile-time wrapper that causes generated/included atomic64 operations to be exported from this translation unit.

State and persistence behavior: no state is stored locally. Runtime state is the caller-provided `atomic64_t` memory manipulated by the included implementations and assembly backends.

Dependencies/integration points: built only on 32-bit x86 via the Makefile. It links generic atomic definitions with x86-specific `atomic64_386_32.S` or `atomic64_cx8_32.S` depending on CPU config. Exported symbols are used by kernel code and modules needing 64-bit atomics on 32-bit kernels.

Risks: the file is tiny but symbol visibility matters. If `ATOMIC64_EXPORT` changes or this wrapper is not built, modules may fail to link against atomic64 helpers. Correctness depends on the assembly implementation matching the generic atomic operation ABI.

Test signals: 32-bit build/link tests with modular users of atomic64, plus atomic API selftests or stress tests on CX8 and non-CX8 configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/atomic64_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/atomic64_386_32.S -->
# sources/distributed-fs/ceph-client/arch/x86/lib/atomic64_386_32.S

Purpose: implements 64-bit atomic operations for 386/486-class 32-bit x86 systems without `cmpxchg8b`. Because real SMP-safe 64-bit atomics are unavailable, operations protect critical sections by disabling local interrupts and are intended for non-SMP or otherwise constrained builds.

Important APIs/functions: defines `atomic64_*_386` entry points for read, set, exchange, add/sub, add/sub return, inc/dec, inc/dec return, `atomic64_add_unless_386`, `atomic64_inc_not_zero_386`, and `atomic64_dec_if_positive_386`. Macros `IRQ_SAVE`, `IRQ_RESTORE`, `BEGIN_IRQ_SAVE`, and `RET_IRQ_RESTORE` wrap each function with `pushfl; cli` and `popfl`.

Control flow: each function enters with local interrupts disabled, performs paired 32-bit low/high operations with carry/borrow as needed, and restores flags before returning. Return-value functions load or compute `%edx:%eax`. Conditional helpers compare the computed or current 64-bit value before deciding whether to store and return success/failure.

State and persistence behavior: modifies only caller-provided atomic memory and CPU flags/interrupt state transiently. No persistent global state exists.

Dependencies/integration points: selected by the Makefile for 32-bit x86 when `CONFIG_X86_CX8` is not enabled. It must match the atomic64 generic ABI included through `atomic64_32.c`. It uses Linux linkage macros and x86 alternative headers.

Risks: comments explicitly say SMP support would require real spinlocks; local IRQ masking is not enough against other CPUs. NMI contexts can still observe partial state. Register conventions are non-obvious and must match callers. Carry/borrow mistakes corrupt signed semantics for decrement and conditional operations.

Test signals: non-CX8 32-bit boot/build coverage, atomic64 API tests, lockdep or concurrency stress on UP-compatible configs, and disassembly checks for interrupt-save/restore balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/atomic64_386_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/atomic64_cx8_32.S -->
# sources/distributed-fs/ceph-client/arch/x86/lib/atomic64_cx8_32.S

Purpose: implements 64-bit atomic operations for 586+ 32-bit x86 systems using `cmpxchg8b`, with lock-prefixed compare/exchange loops for SMP-safe updates.

Important APIs/functions: exports assembly entry points named `atomic64_read_cx8`, `atomic64_set_cx8`, `atomic64_xchg_cx8`, generated `atomic64_add_return_cx8`, `atomic64_sub_return_cx8`, `atomic64_inc_return_cx8`, `atomic64_dec_return_cx8`, plus `atomic64_dec_if_positive_cx8`, `atomic64_add_unless_cx8`, and `atomic64_inc_not_zero_cx8`. Helper macros `read64`, `read64_nonatomic`, `addsub_return`, and `incdec_return` encapsulate repeated patterns.

Control flow: operations read the current 64-bit value into `%edx:%eax`, compute a proposed new value in `%ecx:%ebx`, and use locked `cmpxchg8b` retry loops until the write succeeds or a conditional operation decides not to store. `atomic64_set_cx8` relies on aligned 64-bit writes being atomic on 586+ but still uses `cmpxchg8b` looping without lock. Conditional helpers return success in `%eax` or the decremented value as required by the atomic ABI.

State and persistence behavior: mutates only caller-provided atomic memory. No globals. Stack saves preserve callee-sensitive registers where loops need `%ebx`, `%esi`, `%edi`, and `%ebp`.

Dependencies/integration points: selected for 32-bit x86 with `CONFIG_X86_CX8` support. Coupled to the generic atomic64 wrapper and Linux x86 calling conventions.

Risks: correctness depends on alignment, exact register ABI, and proper lock prefix use. `read64` notes that `cmpxchg8b` writes even for read-like use, hence locked operation is required. Conditional comparisons in `add_unless` and zero checks are race-sensitive and must be looped.

Test signals: 32-bit SMP atomic stress tests, refcount-style `inc_not_zero` tests, signed `dec_if_positive` boundary tests, and build coverage for CX8-enabled CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/atomic64_cx8_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/bhi.S -->
# sources/distributed-fs/ceph-client/arch/x86/lib/bhi.S

Purpose: provides the `__bhi_args` code array used by FineIBT Branch History Injection mitigation paths. It supplies carefully aligned return stubs that conditionally sanitize argument registers before returning, with intentional `ud2` sites placed for short conditional branches.

Important APIs/functions: defines `__bhi_args` in `.noinstr.text`, local labels `__bhi_args_0` through `__bhi_args_7`, global `__bhi_args_end`, and conditional code under `CONFIG_FINEIBT_BHI`. The stubs use `ANNOTATE_NOENDBR`, `UNWIND_HINT_FUNC`, `ANNOTATE_UNRET_SAFE`, and `ANNOTATE_REACHABLE`.

Control flow: when FineIBT BHI is enabled, each 32-byte-aligned element checks `jne` to an intentional `ud2` trap and otherwise uses `cmovne %rax, <arg register>` for an increasing number of argument registers before returning. The preamble is expected to enter with ZF set and `%eax` zero. Elements 1 and 5 include alignment holes so two nearby `ud2` sites can be reached by short conditional jumps.

State and persistence behavior: no persistent state. It transiently modifies argument registers on paths where condition flags select the `cmovne` operations and returns through annotated mitigation-safe paths.

Dependencies/integration points: included only in the 64-bit library build. Integrated with x86 speculation mitigation infrastructure, objtool/unwind annotations, FineIBT, and noinstr constraints.

Risks: alignment and label layout are part of the contract; small edits can break branch reachability, objtool validation, or mitigation properties. Because it is in `.noinstr.text`, instrumentation must not be introduced. Flag assumptions from callers are critical.

Test signals: objtool noinstr/unwind validation, builds with and without `CONFIG_FINEIBT_BHI`, disassembly/layout inspection for 32-byte element spacing and `ud2` placement, and mitigation selftests where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/bhi.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/cache-smp.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/cache-smp.c

Purpose: provides SMP helpers to execute cache writeback/invalidate operations on one CPU, all CPUs, or a CPU mask.

Important APIs/functions: exports `wbinvd_on_cpu`, `wbinvd_on_all_cpus`, `wbinvd_on_cpus_mask`, `wbnoinvd_on_all_cpus`, and `wbnoinvd_on_cpus_mask`. Internal callbacks `__wbinvd` and `__wbnoinvd` invoke the CPU instructions.

Control flow: wrappers call `smp_call_function_single`, `on_each_cpu`, or `on_each_cpu_mask` with wait enabled. The callback runs synchronously on target CPUs and executes the selected instruction.

State and persistence behavior: no C-level state. Hardware cache state is written back and optionally invalidated globally or on targeted CPUs, which affects memory visibility and device/virtualization correctness.

Dependencies/integration points: built under `CONFIG_SMP`. Includes Linux SMP/export infrastructure and KVM export typing. KVM and memory-management code use these helpers for cache coherency operations that must happen on specific CPUs.

Risks: these operations are expensive and globally disruptive. Incorrect CPU masks or missing synchronization can leave stale cache state. `wbinvd` has stronger side effects than `wbnoinvd`, so call sites must select carefully.

Test signals: SMP build tests, KVM module link tests for exported symbols, CPU hotplug stress around target masks, and platform tests involving cache-flush-sensitive device assignment or memory type changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/cache-smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/checksum_32.S -->
# sources/distributed-fs/ceph-client/arch/x86/lib/checksum_32.S

Purpose: implements 32-bit x86 Internet checksum routines optimized for IP/TCP/UDP and checksum-with-copy operations.

Important APIs/functions: defines and exports `csum_partial` and `csum_partial_copy_generic`. Two implementation families are compiled depending on `CONFIG_X86_USE_PPRO_CHECKSUM`: a 486/Pentium-oriented loop and a Pentium Pro/II unrolled/nospec dispatch version. Exception macro `EXC` annotates faulting copy instructions for uaccess recovery and clearing `%eax`.

Control flow: `csum_partial` handles odd, 2-byte, and 4-byte alignment first, then accumulates 32-byte or 128-byte chunks with carry using `adcl`, then handles trailing words/bytes and rotates the result if the original buffer was odd-aligned. `csum_partial_copy_generic` copies from source to destination while accumulating checksum, with exception table fixups so faults return a safe value and stop copying. The PPro path uses computed jumps guarded by `JMP_NOSPEC` for unrolled chunk entry.

State and persistence behavior: no global state. It reads packet buffers, writes destination buffers in copy variants, and returns an unfolded checksum. Faults may leave partial destination contents depending on exception point, with wrappers responsible for higher-level handling.

Dependencies/integration points: used by the networking stack on 32-bit x86 when generic checksum is not selected. Depends on Linux exception table formats, uaccess exception typing, export symbols, and nospec branch helpers.

Risks: checksum correctness is sensitive to byte order, odd alignment, carry folding, and tail handling. Exception table labels must match faulting loads/stores. Computed jump tables must be speculation-safe. Any ABI/register-save mistake can corrupt networking data paths.

Test signals: network checksum selftests, packet send/receive with odd and unaligned buffers, fault-injection tests for checksum-copy from/to user memory, and 32-bit builds with both PPro checksum configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/checksum_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/clear_page_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/lib/clear_page_64.S

Purpose: implements 64-bit page clearing and clear-user alternatives with exception handling.

Important APIs/functions: exports GPL symbol `__clear_pages_unrolled` and exported `rep_stos_alternative`. `__clear_pages_unrolled` zeros page-aligned memory in 64-byte chunks. `rep_stos_alternative` is a user-access clearing routine with the same calling convention as `rep stos`, returning remaining byte count in `%rcx`.

Control flow: `__clear_pages_unrolled` divides length by 64 and stores eight zeroed 64-bit words per loop iteration using `%rax` as zero. `rep_stos_alternative` handles small byte tails, 8-byte word stores, and 64-byte unrolled stores. Exception table entries redirect failed user stores to a tail loop or exit so `%rcx` reflects uncleared bytes as closely as practical.

State and persistence behavior: writes zeroes to kernel or user memory supplied by callers. No persistent global state. Faults can leave partially cleared memory and return remaining count.

Dependencies/integration points: 64-bit library build, usercopy/clear_user alternatives, Linux exception tables, objtool annotations, and CFI type annotations.

Risks: exception fixups must preserve the clear-user ABI. Unrolled stores can clear some bytes twice after a fault, which is accepted, but must not report success incorrectly. The page-clearing entry assumes correct alignment/length from callers.

Test signals: `clear_user` fault tests, page allocator zero-page tests, KASAN/KMSAN builds, objtool validation, and usercopy tests with faults at byte, word, and unrolled store sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/clear_page_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/cmdline.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/cmdline.c

Purpose: supplies small x86 command-line parsing helpers for early and normal boot code.

Important APIs/functions: exports `cmdline_find_option_bool` and `cmdline_find_option`. Internal state-machine helpers `__cmdline_find_option_bool` and `__cmdline_find_option` parse bounded command-line buffers. `myisspace()` treats any byte `<= ' '` as whitespace.

Control flow: boolean lookup scans words up to `COMMAND_LINE_SIZE`, matching an entire option word and returning its 1-based position or zero; null `cmdline` returns `-1`. Value lookup scans for `option=argument`, returns the full argument length, copies a truncated NUL-terminated value into the supplied buffer if present, and intentionally returns the last occurrence. Public wrappers first search the supplied command line and, if enabled and not already added, fall back to `builtin_cmdline`.

State and persistence behavior: no local mutable state. Reads `builtin_cmdline` and `builtin_cmdline_added` from setup code. Writes only the caller-provided output buffer.

Dependencies/integration points: used by x86 setup and early option consumers. Depends on `CONFIG_CMDLINE_BOOL`, `COMMAND_LINE_SIZE`, and builtin command-line setup state.

Risks: callers must interpret zero, positive positions, positive lengths, and `-1` correctly. `cmdline_find_option` returns only if `ret > 0`, so empty arguments do not suppress fallback. The parser is whitespace-only and does not handle quoting.

Test signals: unit-style parser tests for whole-word matching, repeated options, truncation, null command lines, empty values, builtin fallback, and maximum-size non-NUL-terminated buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/cmdline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/cmpxchg16b_emu.S -->
# sources/distributed-fs/ceph-client/arch/x86/lib/cmpxchg16b_emu.S

Purpose: emulates a per-CPU `cmpxchg16b %gs:(%rsi)` operation for contexts that need 128-bit compare/exchange semantics on per-CPU data without using the hardware instruction directly.

Important APIs/functions: defines `this_cpu_cmpxchg16b_emu`. Inputs are `%rsi` per-CPU memory location, `%rax:%rdx` old low/high 64-bit value, and `%rbx:%rcx` new low/high 64-bit value. It reports success/failure through the ZF bit in saved EFLAGS, matching compare/exchange conventions.

Control flow: saves flags, disables interrupts, compares both 64-bit halves at the per-CPU address, writes the new halves if both match, and sets ZF in the saved flags. On mismatch it reloads actual memory into `%rax:%rdx` and clears ZF. Finally it restores flags and returns.

State and persistence behavior: modifies only the target per-CPU 16-byte object and transient interrupt state. It has no globals.

Dependencies/integration points: x86-64 per-CPU addressing, processor flags, Linux linkage. Used by per-CPU atomic code paths where local IRQ exclusion is the intended serialization mechanism.

Risks: comment states it is not lock-prefixed and not safe against NMIs. It only serializes local interrupt handlers, not arbitrary concurrent observers. Register ABI and ZF reporting must remain exact because callers inspect flags.

Test signals: per-CPU cmpxchg tests for success/failure values, interrupt-preemption stress, disassembly validation for `%gs` per-CPU addressing, and NMI-safety review for call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/cmpxchg16b_emu.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/cmpxchg8b_emu.S -->
# sources/distributed-fs/ceph-client/arch/x86/lib/cmpxchg8b_emu.S

Purpose: emulates 64-bit `cmpxchg8b` operations on 32-bit x86 for CPUs or contexts without direct support, including normal memory and per-CPU memory variants.

Important APIs/functions: conditionally defines and exports `cmpxchg8b_emu` when `CONFIG_X86_CX8` is disabled. Also defines `this_cpu_cmpxchg8b_emu` except under UML. Inputs are `%esi` pointer, `%edx:%eax` old value, `%ecx:%ebx` new value. Success/failure is returned via ZF in flags and actual memory is returned in `%edx:%eax` on failure.

Control flow: both variants push flags, disable interrupts, compare low and high 32-bit halves, write new halves on exact match, set ZF in saved flags, restore flags, and return. Failure paths reload current memory and clear ZF.

State and persistence behavior: modifies target 8-byte memory and transient interrupt state. No persistent globals.

Dependencies/integration points: used by 32-bit atomic/per-CPU code and exported for non-CX8 builds. Relies on x86 per-CPU addressing macros, processor flags, exception-free memory accesses, and Linux symbol exports.

Risks: not lock-prefixed, so safety is limited to UP/local-interrupt serialization for the non-CX8 emulation and per-CPU contexts. NMI races can observe or interleave partial operations. Callers must not use it as a general SMP atomic primitive unless configuration guarantees make that safe.

Test signals: non-CX8 32-bit build/link coverage, atomic cmpxchg success/failure tests, per-CPU cmpxchg tests, and interrupt/NMI call-site audits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/cmpxchg8b_emu.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/copy_mc.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/copy_mc.c

Purpose: implements C dispatch for machine-check-tolerant memory copy operations, choosing fragile byte/word-safe copying, enhanced fast-string copying, or ordinary copy depending on platform capability and MCE quirks.

Important APIs/functions: `enable_copy_mc_fragile()` enables a static key under `CONFIG_X86_MCE`. `copy_mc_fragile_handle_tail()` probes byte-by-byte after write faults. `copy_mc_to_kernel()` and `copy_mc_to_user()` are the main exported/called APIs. Assembly backends `copy_mc_fragile` and `copy_mc_enhanced_fast_string` are declared here.

Control flow: if fragile mode is enabled, copies are instrumented and routed through `copy_mc_fragile`. Otherwise ERMS-capable CPUs use `copy_mc_enhanced_fast_string`. Kernel destination fallback is plain `memcpy`; user destination fallback is `copy_user_generic`. User copies bracket machine-check copy with `__uaccess_begin/end`.

State and persistence behavior: only static key state persists after `enable_copy_mc_fragile`. Copies modify destination memory and return remaining byte count on exception. Instrumentation hooks notify sanitizers/tracing about copy ranges.

Dependencies/integration points: depends on MCE support, x86 feature detection, uaccess, instrumentation hooks, and assembly routines in `copy_mc_64.S`. Used by memory error recovery, persistent memory, and usercopy paths that may encounter poisoned memory.

Risks: choosing fast-string on CPUs that cannot recover from machine checks could be fatal; platform quirks must call `enable_copy_mc_fragile()`. User access windows must be balanced. Return values must be honored by callers to avoid treating partial copies as complete.

Test signals: MCE/poison injection tests, ERMS and non-ERMS CPU coverage, fragile static-key path tests, usercopy fault injection, and sanitizer instrumentation checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/copy_mc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/copy_mc_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/lib/copy_mc_64.S

Purpose: provides 64-bit assembly backends for machine-check-safe copying: a fragile conservative copy loop and an enhanced fast-string copy with exception recovery.

Important APIs/functions: defines `copy_mc_fragile` under `CONFIG_X86_MCE` and `copy_mc_enhanced_fast_string` outside UML. `copy_mc_fragile` returns zero on success or remaining bytes on read/write exception. `copy_mc_enhanced_fast_string` performs `rep movsb` and returns `%rcx` bytes remaining on exception.

Control flow: fragile copy aligns the source to 8 bytes with byte copies, copies aligned 8-byte words, then trailing bytes. Read exceptions on leading/word/trailing loads compute remaining byte count. Write exceptions on word stores call `copy_mc_fragile_handle_tail()` to probe the exact destination fault point. Enhanced fast-string sets `%rcx` from length, performs `rep movsb`, and exception-table fixup returns the remaining count.

State and persistence behavior: modifies destination memory partially or fully. No global state. Exception table metadata controls recovery behavior.

Dependencies/integration points: called by `copy_mc.c`, depends on Linux exception tables with `EX_TYPE_DEFAULT_MCE_SAFE`, x86 assembly/linkage, MCE recovery capability, and uaccess wrappers where destination is user memory.

Risks: exception fixup labels and remaining-byte calculations are correctness-critical. Fragile copy intentionally avoids dangerous fast-string cases but still assumes poison alignment properties. Enhanced fast-string should only be used on CPUs whose MCE recovery supports it.

Test signals: poison-copy fault injection across byte, word, and cacheline boundaries; write-fault tests; ERMS fast-string fault tests; and build coverage with `CONFIG_X86_MCE` and UML exclusions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/copy_mc_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/copy_page_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/lib/copy_page_64.S

Purpose: implements the 64-bit `copy_page` primitive for copying one 4 KiB page.

Important APIs/functions: exports `copy_page`. Internal `copy_page_regs` is an unrolled register-copy fallback. `ALTERNATIVE` selects the fast `rep movsq` implementation when `X86_FEATURE_REP_GOOD` is available.

Control flow: on CPUs with good REP behavior, the function copies `4096/8` quadwords with `rep movsq`. Otherwise it saves `%rbx` and `%r12`, copies 64-byte chunks with eight general-purpose registers and prefetching, then copies a final fixed five chunks, restores registers, and returns.

State and persistence behavior: writes exactly one page at the destination from the source page. No global state.

Dependencies/integration points: used by memory-management page copy paths. Depends on x86 alternatives, CPU feature detection, Linux export/linkage, and the calling convention where `%rdi` and `%rsi` are destination/source.

Risks: assumes caller provides valid page-sized source/destination. Register save/restore correctness matters because fallback clobbers callee-saved registers. Alternative patching must match CPU feature semantics.

Test signals: boot-time page allocator and fork/COW behavior, memory copy stress, alternative instruction patching tests, and objtool/build validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/copy_page_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/copy_user_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/lib/copy_user_64.S

Purpose: implements `rep_movs_alternative`, the 64-bit exception-aware user memory copy fallback for CPUs without FSRM.

Important APIs/functions: exports `rep_movs_alternative`. The calling convention matches `rep movs`: `%rdi` destination, `%rsi` source, `%rcx` count, returning remaining bytes in `%rcx`.

Control flow: small copies use byte and qword loops with exception table entries that fall back to byte-tail copying. Large copies use an alternative: ERMS CPUs can do `rep movsb`, otherwise the code aligns destination, copies qwords with `rep movsq`, and handles tails. Exception fixups return or recompute remaining bytes then retry the tail.

State and persistence behavior: partially or fully copies memory from source to destination. No global state. Faults leave `%rcx` as remaining byte count and may leave partial destination writes.

Dependencies/integration points: used by generic x86 usercopy code and alternative patching. Depends on exception-table uaccess annotations, ERMS feature detection, objtool annotations, and user access enabling by higher-level wrappers.

Risks: the ABI is intentionally tied to raw `rep movs`, so register changes can break alternative call-site rewriting. Exception fixup precision affects usercopy return values. Large-copy alignment math must not underflow counts.

Test signals: usercopy tests with page faults at source/destination, ERMS and non-ERMS CPU paths, small/large/unaligned copy cases, and copy return-count validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/copy_user_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/copy_user_uncached_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/lib/copy_user_uncached_64.S

Purpose: implements `copy_to_nontemporal`, an exception-aware uncached/non-temporal copy routine used when copying user data into destinations where kernel writes may machine-check or should bypass cache.

Important APIs/functions: exports `copy_to_nontemporal`. Inputs are `%rdi` destination, `%rsi` source, `%edx` byte count; return `%rax` is uncopied bytes. It uses aligned `movnti` stores for 32/64-bit chunks and normal stores for small unaligned pieces.

Control flow: the function first aligns the destination to 8 bytes, then performs 64-byte unrolled loops of eight loads and eight non-temporal stores. It falls back to qword, dword, word, and byte tails and issues `sfence` before cached tail stores. Exception table fixups distinguish first-half load faults, second-half load faults after 32 bytes have been stored, write faults at each store offset, alignment faults, and a final 4-byte retry path.

State and persistence behavior: writes destination memory partially or fully and returns the remaining count. Non-temporal writes affect cache persistence/order and require `sfence` before completion.

Dependencies/integration points: used by uncached usercopy/nocache paths and machine-check-sensitive copy code. Depends on uaccess exception tables, x86 non-temporal store semantics, and caller-managed user access state.

Risks: exception recovery is intricate; incorrect offset fixups over- or under-report copied bytes. Missing `sfence` can leave non-temporal stores unordered. The code intentionally avoids byte probing after some fatal-looking faults, so callers must handle nonzero returns.

Test signals: usercopy fault injection at every extable site, unaligned destination tests, non-temporal ordering tests where practical, and machine-check/poison copy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/copy_user_uncached_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/cpu.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/cpu.c

Purpose: provides small CPUID signature decoding helpers for x86 family, model, and stepping fields.

Important APIs/functions: exports GPL symbols `x86_family`, `x86_model`, and `x86_stepping`.

Control flow: `x86_family()` extracts base family bits `[11:8]` and adds extended family bits `[27:20]` for family `0xf`. `x86_model()` calls `x86_family()`, extracts base model bits `[7:4]`, and adds extended model bits `[19:16] << 4` for family `>= 0x6`. `x86_stepping()` returns signature bits `[3:0]`.

State and persistence behavior: pure functions; no state, no side effects.

Dependencies/integration points: uses Linux export infrastructure and `<asm/cpu.h>`. Consumed by CPU feature, quirk, driver, and module code that needs consistent CPUID signature decoding.

Risks: simple but architecture-defined bit positions must stay exact. Family/model handling differs before family 6/15; helpers encode those rules.

Test signals: unit checks with known Intel/AMD signatures, module link tests, and CPU identification paths during boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/csum-copy_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/lib/csum-copy_64.S

Purpose: implements 64-bit checksum-copy core used by x86 networking wrappers, copying memory while computing an unfolded Internet checksum with exception recovery.

Important APIs/functions: defines `csum_partial_copy_generic`. It uses local `source` and `dest` macros to annotate faulting loads/stores with uaccess exception table entries that branch to `.Lfault`.

Control flow: saves callee registers, initializes sum to `-1`, handles destination alignment including odd-byte rotation bookkeeping, processes 64-byte chunks with eight qword loads, checksum accumulation using carry, and eight qword stores. It then handles 8-byte, 2-byte, and 1-byte tails, folds the 64-bit accumulator to 32 bits, rotates if the original alignment was odd, and restores registers. Any source or destination fault returns zero via `.Lfault`; wrappers handle higher-level validity.

State and persistence behavior: writes destination memory while reading source memory. No global state. On exceptions destination can be partially written and checksum return is zero.

Dependencies/integration points: called by `csum-wrappers_64.c` for user and kernel copy/checksum APIs. Depends on x86 exception tables, uaccess annotations, and networking checksum conventions.

Risks: checksum correctness depends on carry propagation, fold order, and odd alignment rotation. The function does not distinguish source versus destination faults to callers; wrapper contracts must tolerate zero checksum on fault. Prefetch exceptions are deliberately non-uaccess and ignored.

Test signals: checksum-copy tests for aligned/unaligned and odd source/destination cases, fault injection during source/destination access, comparison with generic checksum implementation, and network stack checksum validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/csum-copy_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/csum-partial_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/csum-partial_64.c

Purpose: provides optimized 64-bit x86 Internet checksum routines for arbitrary memory and IP-style checksums.

Important APIs/functions: exports `csum_partial` and `ip_compute_csum`. Internal helpers `csum_finalize_sum()` and `update_csum_40b()` fold 64-bit accumulators and add five qwords using inline assembly carry chains.

Control flow: `csum_partial()` accumulates two parallel 40-byte lanes for lengths >=80 to improve instruction-level parallelism, handles a hot exact 40-byte path, then processes 32-, 16-, and 8-byte tails with inline assembly. Remaining 1-7 bytes are loaded with `load_unaligned_zeropad()` and masked by shift before final carry addition. `ip_compute_csum()` folds the partial checksum to a 16-bit checksum.

State and persistence behavior: pure read-only over the supplied buffer; no global state.

Dependencies/integration points: used by the networking stack when `CONFIG_GENERIC_CSUM` is not selected. Depends on checksum types, word-at-a-time helpers, exports, and x86 carry arithmetic.

Risks: unaligned tail loading must not fault beyond valid memory due to `load_unaligned_zeropad` expectations. Carry folding and endian behavior must match Internet checksum semantics. Optimized 40-byte path targets IPv6 headers and needs exact length handling.

Test signals: networking checksum selftests, comparisons against generic checksum for random buffers and all alignments/lengths, IPv6 header checksum cases, and KASAN validation for tail loads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/csum-partial_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/csum-wrappers_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/csum-wrappers_64.c

Purpose: provides C wrappers around the 64-bit assembly checksum-copy routine for user and kernel copy/checksum APIs.

Important APIs/functions: defines `csum_and_copy_from_user`, `csum_and_copy_to_user`, and exported `csum_partial_copy_nocheck`.

Control flow: user wrappers call `might_sleep()`, attempt `user_access_begin()` over the source or destination range, call `csum_partial_copy_generic()` with forced kernel pointers while the uaccess window is open, and then call `user_access_end()`. If access cannot begin, they return zero. The nocheck wrapper directly calls the assembly routine.

State and persistence behavior: no persistent state. Copies to destination buffers and returns an unfolded checksum, with zero indicating failed access or assembly fault.

Dependencies/integration points: depends on asm checksum declarations, Linux uaccess, SMAP helpers, and the assembly symbol in `csum-copy_64.S`. Used by socket and networking code that combines copy and checksum.

Risks: zero is both a valid checksum value and an error fallback at this layer, so higher-level code must use existing API semantics. User access windows must be correctly balanced. The wrappers do not zero destination on failure; assembly behavior is partial-copy oriented.

Test signals: usercopy fault injection, SMAP-enabled builds, checksum-copy comparisons, `might_sleep` context checks, and network receive/send tests involving user buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/csum-wrappers_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/delay.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/delay.c

Purpose: implements x86 busy-wait and halt-assisted delay primitives used by `__delay`, `udelay`, and `ndelay`.

Important APIs/functions: exports `__delay`, `__const_udelay`, `__udelay`, and `__ndelay`; provides `use_tsc_delay`, `use_tpause_delay`, `use_mwaitx_delay`, and `read_current_timer`. Internal delay engines are `delay_loop`, `delay_tsc`, `delay_halt_tpause`, `delay_halt_mwaitx`, and `delay_halt`. Function pointers `delay_fn` and `delay_halt_fn` are `__ro_after_init`.

Control flow: boot starts with loop-based delay. Calibration may switch to TSC delay, TPAUSE, or MWAITX. `delay_tsc()` disables preemption while sampling ordered TSC, periodically enables preemption/native_pause to let RT tasks run, and adjusts if migrated to another CPU. Halt-assisted delay repeatedly invokes vendor-specific halt wait until the requested TSC cycles elapsed. `__const_udelay()` scales requested loops by per-CPU `loops_per_jiffy` or global fallback, then calls `__delay`.

State and persistence behavior: delay engine function pointers persist after boot initialization. No other persistent state. Reads per-CPU CPU info and global `loops_per_jiffy`.

Dependencies/integration points: used throughout the kernel and by KCSAN itself, hence Makefile disables instrumentation. Depends on TSC, timer, mwait/tpause, SMP/preemption, CPU info, and scheduler behavior.

Risks: instrumentation recursion is a known risk. TSC migration handling must ensure delays are at least as long as requested. Halt instructions can return early, so elapsed time must be checked. Scaling constants for micro/nanoseconds must remain accurate enough for busy waits.

Test signals: boot calibration, delay accuracy tests, RT scheduling latency checks, KCSAN/ftrace/lockdep configs, CPU migration stress during delays, and platform coverage for TSC/TPAUSE/MWAITX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/delay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/error-inject.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/error-inject.c

Purpose: supplies a tiny architecture hook for function error injection by redirecting execution to an immediate-return stub.

Important APIs/functions: defines assembly symbol `just_return_func` and C function `override_function_with_return(struct pt_regs *regs)`. Marks the override helper with `NOKPROBE_SYMBOL`.

Control flow: `just_return_func` contains an annotated no-ENDBR function entry and `ASM_RET`. `override_function_with_return()` sets `regs->ip` to the stub address, causing the probed/injected function to return immediately when execution resumes.

State and persistence behavior: no persistent state. Mutates the instruction pointer in the supplied register frame.

Dependencies/integration points: built with `CONFIG_FUNCTION_ERROR_INJECTION`; integrates with kprobes, Linux error-injection infrastructure, objtool annotations, and x86 return/IBT annotations.

Risks: redirecting IP must preserve calling-convention assumptions for injected sites. The helper must not itself be probed. IBT/ENDBR annotations must match kernel control-flow enforcement expectations.

Test signals: function error-injection selftests, kprobe exclusion validation, objtool/IBT builds, and tests that injected functions return without executing body side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/error-inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/getuser.S -->
# sources/distributed-fs/ceph-client/arch/x86/lib/getuser.S

Purpose: implements low-level `__get_user_*` helpers that load 1, 2, 4, or 8 bytes from user memory and return both an error code and loaded value using a non-standard register ABI.

Important APIs/functions: exports `__get_user_1`, `__get_user_2`, `__get_user_4`, `__get_user_8`, and nocheck variants for each size. Local `__get_user_handle_exception` returns `-EFAULT` and zero value. Macros `check_range` and `UACCESS` implement address limiting and exception-table annotations.

Control flow: checked variants clamp/check the user pointer against `USER_PTR_MAX` on 64-bit or `TASK_SIZE_MAX` on 32-bit with nospec masking. They enable user access with `ASM_STAC`, perform the load under `_ASM_EXTABLE_UA`, clear access with `ASM_CLAC`, zero `%eax` for success, and return loaded data in `%edx` plus `%ecx` high half for 32-bit 8-byte loads. Nocheck variants omit range checks but include a speculation barrier alternative before load.

State and persistence behavior: no persistent state. Reads user memory and transiently toggles SMAP access state. Faults return zeroed value and `-EFAULT`.

Dependencies/integration points: core uaccess implementation, SMAP, runtime constants, nospec alternatives, exception tables, and exported helper ABI used by inline uaccess code.

Risks: ABI is unusual and register clobbers are constrained. Missing `CLAC` on fault would be a security bug; exception handler performs it. Range/nospec logic protects against out-of-range and speculative user pointer misuse. 32-bit 8-byte loads must zero high registers before faults.

Test signals: uaccess selftests for each size, fault injection, SMAP enabled tests, speculation mitigation configs, 32-bit and 64-bit builds, and objtool validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/getuser.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/hweight.S -->
# sources/distributed-fs/ceph-client/arch/x86/lib/hweight.S

Purpose: provides software Hamming-weight/popcount helpers for x86 when hardware popcount or inline implementations are not used.

Important APIs/functions: exports `__sw_hweight32` on all x86 and `__sw_hweight64` on x86-64.

Control flow: both functions implement classic parallel bit-count algorithms: subtract shifted pairs masked with `0x55...`, combine two-bit groups with `0x33...`, combine nibbles with `0x0f...`, multiply by `0x0101...`, and shift out the total count. Register saves protect temporary registers.

State and persistence behavior: pure register computation; no memory state except stack saves.

Dependencies/integration points: used by generic bit operations as fallback popcount helpers and exported for modules. Depends on Linux linkage/export macros and x86 register-size abstractions.

Risks: constants and shift widths must match operand size. Calling convention differences between 32-bit and 64-bit are handled explicitly; changing register use can break callers.

Test signals: bitops selftests comparing every small value and random 32/64-bit values, module link tests, and builds with hardware POPCNT disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/hweight.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/inat.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/inat.c

Purpose: provides lookup APIs over generated x86 instruction attribute tables used by the instruction decoder.

Important APIs/functions: includes generated `inat-tables.c` and defines `inat_get_opcode_attribute`, `inat_get_last_prefix_id`, `inat_get_escape_attribute`, `inat_get_group_attribute`, `inat_get_avx_attribute`, and `inat_get_xop_attribute`.

Control flow: primary opcodes index `inat_primary_table`. Escape and group lookups derive table IDs from attributes, select default or prefix-variant tables, and return zero/common attributes when a table is absent. AVX lookup validates VEX map and prefix selectors, handles group tables specially, and returns attribute entries. XOP lookup validates map range and indexes XOP tables.

State and persistence behavior: read-only generated table access; no mutable state.

Dependencies/integration points: `inat-tables.c` is generated by the Makefile from `x86-opcode-map.txt`. The decoder in `insn.c` and evaluator in `insn-eval.c` depend on these attributes for prefix/opcode/ModRM/immediate parsing.

Risks: generated tables must match Intel/AMD opcode semantics. Returning zero for missing tables causes decode failure paths; incorrect variant selection can misdecode instructions. AVX/VEX/XOP prefix handling is especially sensitive to map/prefix bits.

Test signals: instruction decoder selftests, generated table regeneration diffs, opcode-map validation, AVX/XOP decode coverage, and builds ensuring `inat-tables.c` is generated before `inat.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/inat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/insn-eval.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/insn-eval.c

Purpose: evaluates decoded x86 instructions against a `pt_regs` frame to resolve registers, segment bases/limits, effective addresses, instruction fetch addresses, MMIO access types, and recognized NOPs.

Important APIs/functions: exports/defines `insn_has_rep_prefix`, `pt_regs_offset`, `insn_get_seg_base`, `insn_get_code_seg_params`, `insn_get_modrm_rm_off`, `insn_get_modrm_reg_off`, `insn_get_modrm_reg_ptr`, `insn_get_addr_ref`, `insn_get_effective_ip`, `insn_fetch_from_user`, `insn_fetch_from_user_inatomic`, `insn_decode_from_regs`, `insn_decode_mmio`, and `insn_is_nop`. Internal helpers resolve segment overrides, selectors, descriptor tables, ModRM/SIB register offsets, 16/32/64-bit effective addresses, and segment limits.

Control flow: segment resolution first considers long mode, string-instruction constraints, override prefixes, and default segment rules. Descriptor lookup reads LDT or GDT where valid. Address resolution decodes ModRM/SIB/displacements, gets register values from `pt_regs`, applies segment base and limit checks for 16/32-bit modes, and returns a user linear address or `-1L`. Fetch helpers compute effective IP and copy instruction bytes from user memory. MMIO decode maps MOV/MOVS/MOVSX/MOVZX opcodes to read/write types and byte widths. NOP recognition checks opcode/prefix/ModRM/SIB patterns without allowing false positives like PAUSE.

State and persistence behavior: mostly read-only over instruction buffers, descriptors, MSRs, current mm LDT, and user memory. It writes output buffers and may take `current->mm->context.lock` for LDT lookup. No persistent state.

Dependencies/integration points: uses the instruction decoder (`insn.c`/inat), x86 descriptor/LDT/MSR/vm86 helpers, uaccess, pt_regs accessors, and MMIO/emulation consumers. Fault handlers, uprobes, alternatives, and emulators rely on these utilities.

Risks: x86 addressing rules are complex across real/v8086/protected/long modes, 16-bit address encodings, FS/GS bases, REX/REX2 extensions, and segment limits. Misresolving addresses can produce wrong fault emulation or security bugs. LDT access requires valid context and locking. NOP detection must avoid false positives because callers may skip or compress instructions.

Test signals: instruction/address decoder tests across 16/32/64-bit modes, LDT/vm86 cases, FS/GS base tests, MMIO decode tests for supported MOV forms, user fetch fault tests, and NOP recognition tests including PAUSE and VEX exclusions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/insn-eval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/insn.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/insn.c

Purpose: implements the generic x86 instruction decoder that parses prefixes, opcodes, ModRM, SIB, displacement, immediates, and total instruction length into `struct insn`.

Important APIs/functions: defines `insn_init`, `insn_get_prefixes`, `insn_get_opcode`, `insn_get_modrm`, `insn_rip_relative`, `insn_get_sib`, `insn_get_displacement`, `insn_get_immediate`, `insn_get_length`, and `insn_decode`. Internal helpers parse Xen/KVM emulate prefixes and immediate variants.

Control flow: initialization caps buffers at `MAX_INSN_SIZE` and sets default operand/address sizes. Prefix parsing consumes optional Xen/KVM emulate prefixes, legacy prefixes, REX/REX2, VEX/XOP/EVEX prefixes, and updates address/operand sizes. Opcode parsing consults inat tables, handles VEX/XOP/REX2 maps, escapes, invalid64, groups, and must-VEX/EVEX constraints. Later stages lazily parse ModRM, SIB, displacement, and immediates according to attributes. `insn_decode()` runs the full length decode for a selected mode and rejects incomplete decodes.

State and persistence behavior: all state is in the caller-provided `struct insn`; no globals except read-only emulate-prefix arrays. It reads only the provided instruction buffer.

Dependencies/integration points: depends on generated inat attribute APIs, `asm/insn.h`, unaligned little-endian loads, emulate-prefix definitions, and Kconfig mode. Consumers include KVM, uprobes, alternatives, fault decoding, and MMIO emulation.

Risks: decoder must never read past the bounded buffer; `validate_next` guards all byte fetches. Prefix interactions are subtle, especially duplicate legacy prefixes, REX2 map bits, XOP ambiguity in 32-bit mode, EVEX scalable operands, and invalid instructions. Incorrect length decoding can corrupt patching/emulation.

Test signals: x86 instruction decoder test suites, fuzzing random byte streams under bounded buffers, AVX/EVEX/XOP/REX2 coverage, emulate-prefix tests, and KASAN checks for no over-read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/insn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/iomem.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/iomem.c

Purpose: implements x86 I/O memory copy and set helpers with string-instruction or unrolled byte operations depending on confidential-computing platform constraints.

Important APIs/functions: exports `memcpy_fromio`, `memcpy_toio`, and `memset_io`. Internal helpers include `string_memcpy_fromio`, `string_memcpy_toio`, `unrolled_memcpy_fromio`, `unrolled_memcpy_toio`, `unrolled_memset_io`, and `rep_movs`.

Control flow: normal paths align odd/word portions then use `rep movsl` plus word/byte tails for IO copy. Confidential guest platforms with `CC_ATTR_GUEST_UNROLL_STRING_IO` use byte-by-byte `readb`/`writeb` loops instead of string IO. `memset_io` uses unrolled `writeb` under that attribute, otherwise plain `memset` to the IO address.

State and persistence behavior: reads or writes MMIO/device memory and normal memory buffers. `memcpy_fromio` unpoisons destination for KMSAN because device-provided data is initialized; `memcpy_toio` checks source initialization before writing to devices.

Dependencies/integration points: Linux IO API, confidential-computing platform attributes, KMSAN, string assembly, and exported architecture IO memory APIs used by drivers.

Risks: string IO can be unsafe or semantically wrong for some confidential guest environments, hence the unrolled path. MMIO ordering and access width patterns can matter for devices. KMSAN annotations prevent false positives and real uninitialized writes to devices.

Test signals: driver IO copy tests, confidential guest boot tests, KMSAN runs, device emulation tests comparing string versus unrolled behavior, and zero-length/unaligned IO copy cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/iomem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/kaslr.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/kaslr.c

Purpose: provides early x86 entropy mixing for KASLR base and memory randomization, usable both in the compressed boot environment and regular kernel.

Important APIs/functions: defines `kaslr_get_random_long(const char *purpose)`. Internal `i8254()` reads the PIT counter as fallback entropy. Non-compressed builds map debug and feature helpers to regular kernel equivalents and use `kaslr_offset()` as boot seed.

Control flow: starts with a boot seed, optionally prints the purpose and entropy sources, mixes in RDRAND if available and successful, mixes in RDTSC if available, otherwise falls back to i8254 PIT reads. It then multiplies by an architecture-width diffusion constant, adds the high product half, prints completion if requested, and returns the mixed value.

State and persistence behavior: no persistent local state. Reads CPU random/TSC/PIT sources and boot seed. Writes debug output through early printing when requested.

Dependencies/integration points: used by compressed kernel and early normal kernel KASLR code. Depends on archrandom, TSC, E820/setup, shared IO port access, CPU feature checks, and early debug output.

Risks: early boot environment restricts available APIs. Entropy quality can be weak without RDRAND/TSC; PIT fallback is last resort. IO port reads must wait until status is ready. The function is not a cryptographic RNG; it is entropy mixing for address randomization.

Test signals: compressed and regular kernel builds, boot logs showing selected sources, CPU-feature matrix tests, i8254 fallback on minimal emulation, and KASLR offset variability checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/kaslr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/memcpy_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/memcpy_32.c

Purpose: provides exported 32-bit C wrappers for `memcpy` and `memset` when compiler builtins call out-of-line functions.

Important APIs/functions: defines `memcpy()` and `memset()` as visible functions, exporting both. They delegate to `__memcpy` and `__memset`.

Control flow: direct wrapper calls only: `memcpy(to, from, n)` returns `__memcpy(to, from, n)`, and `memset(s, c, count)` returns `__memset(s, c, count)`.

State and persistence behavior: state effects are entirely those of the underlying memory functions. No local globals.

Dependencies/integration points: 32-bit x86 library build, generic string/memory implementations providing `__memcpy` and `__memset`, compiler out-of-line builtin calls, and module symbol exports.

Risks: wrapper symbols must avoid macro/builtin substitution, hence `#undef`. Missing exports can break modules or compiler-emitted calls. Correctness depends on underlying implementations.

Test signals: 32-bit build/link tests, module use of `memcpy`/`memset`, compiler configurations that emit out-of-line calls, and basic memory operation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/memcpy_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/memcpy_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/lib/memcpy_64.S

Purpose: implements 64-bit `memcpy`/`__memcpy` in noinstr text with alternatives for fast short `rep movsb` and an optimized manual fallback.

Important APIs/functions: exports `__memcpy` and aliases/exports `memcpy`. Local `memcpy_orig` handles the fallback path.

Control flow: if `X86_FEATURE_FSRM` is available, `__memcpy` copies with `rep movsb` after moving destination to `%rax` for return. Otherwise it jumps to `memcpy_orig`, which copies 32-byte chunks forward or backward depending on low-byte ordering to reduce false dependencies, then handles 16-, 8-, 4-, and 1-3-byte tails using overlapping loads/stores.

State and persistence behavior: copies bytes from source to destination and returns original destination. No global state. Although `memcpy` has no overlap guarantee, the fallback contains backward-copy handling for dependency/performance considerations.

Dependencies/integration points: core kernel memory operations, x86 alternative patching, CFI type annotations, noinstr constraints, and exported module symbols.

Risks: being in `.noinstr.text` forbids instrumentation. Tail copy patterns use overlapping loads/stores and require valid ranges. Alternative patching and return-value preservation are ABI-critical.

Test signals: memcopy correctness tests for all small sizes/alignment combinations, large-copy performance/correctness tests, FSRM and non-FSRM CPU coverage, objtool noinstr validation, and KASAN/KMSAN builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/memcpy_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/memmove_32.S -->
# sources/distributed-fs/ceph-client/arch/x86/lib/memmove_32.S

Purpose: implements 32-bit `memmove`, including overlap-safe forward and backward copies optimized for small and large ranges.

Important APIs/functions: defines and exports `memmove`. It uses the 32-bit `-mregparm=3` convention: destination in `%eax`, source in `%edx`, count in `%ecx`, returning original destination in `%eax`.

Control flow: saves callee-saved registers and destination return value, selects forward copy when source is at or above destination, otherwise backward copy. Large aligned ranges may use `rep movsl`; smaller or unaligned ranges use 16-byte unrolled loops. Tail handlers cover 8-15, 4-7, 2-3, and 1 byte with overlapping loads/stores. Backward `rep movsl` sets DF and clears it before return.

State and persistence behavior: copies memory in place safely for overlapping regions. No globals. Temporarily changes direction flag in backward `rep movsl` path and restores it.

Dependencies/integration points: 32-bit x86 string library, compiler/runtime out-of-line `memmove`, and exported symbol consumers.

Risks: direction flag must always be cleared. Stack/register save/restore is essential because the implementation clobbers callee-saved registers. Overlap direction tests and tail addressing must be exact to avoid corruption.

Test signals: exhaustive memmove overlap tests around small sizes, large aligned/unaligned ranges, forward/backward paths, DF state validation after calls, and 32-bit build/link tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/memmove_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/memmove_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/lib/memmove_64.S

Purpose: implements 64-bit overlap-safe `memmove`/`__memmove` in noinstr text, with ERMS/FSRM alternatives and manual fallback loops.

Important APIs/functions: exports `__memmove` and aliases/exports `memmove`.

Control flow: saves original destination in `%rax`, detects overlap by comparing destination with source and source+count, and selects forward or backward copy. Forward path may use `rep movsb` for ERMS/FSRM or `rep movsq` for large aligned ranges; otherwise it uses 32-byte unrolled loops. Backward path similarly uses `std; rep movsq; cld` for aligned large copies or manual backward loops. Tail handlers cover 16-31, 8-15, 4-7, 2-3, and 1 byte.

State and persistence behavior: modifies destination memory safely for overlap and returns original destination. Temporarily sets direction flag only in backward `rep movsq` path and clears it before continuing.

Dependencies/integration points: core kernel memory API, x86 alternatives for ERMS/FSRM, noinstr validation, CFI annotations, and exported symbols.

Risks: overlap detection must be exact; otherwise memmove degenerates into corrupting memcpy behavior. Direction flag leakage would break later code. Alternative paths must preserve the same ABI and return value.

Test signals: memmove overlap tests with every relative offset and size boundary, ERMS/FSRM/non-ERMS CPU paths, DF-after-call tests, objtool noinstr checks, and sanitizer builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/memmove_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/memset_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/lib/memset_64.S

Purpose: implements 64-bit `memset`/`__memset` in noinstr text with fast-string alternatives and manual fallback.

Important APIs/functions: exports `__memset`, aliases/exports `memset`, and defines local `memset_orig`.

Control flow: if `X86_FEATURE_FSRS` is available, `__memset` saves destination in `%r9`, expands byte into `%al`, runs `rep stosb`, returns original destination in `%rax`. Fallback expands the byte across a qword, handles initial unaligned destination by one unaligned qword store when length permits, writes 64-byte chunks with eight qword stores, then 8-byte and byte tails.

State and persistence behavior: fills destination memory with a byte pattern and returns original destination. No globals.

Dependencies/integration points: core kernel memory API, x86 alternatives, CFI annotations, noinstr constraints, and exported module symbols.

Risks: fallback unaligned qword store intentionally writes within the requested range only when enough bytes exist; alignment math must remain correct. Fast-string alternative must preserve return value. No instrumentation is allowed in noinstr text.

Test signals: memset correctness across lengths 0-128 and alignments, large fills, FSRS and fallback CPU paths, objtool noinstr validation, and KASAN/KMSAN tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/memset_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/misc.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/misc.c

Purpose: provides a small numeric formatting helper for counting decimal digits.

Important APIs/functions: defines `num_digits(int val)`.

Control flow: initializes digit count to one, adds one for a negative sign and negates the value, then multiplies a decimal threshold by 10 until the value is below the threshold. The result includes the sign when present.

State and persistence behavior: pure computation; no global state.

Dependencies/integration points: declared via `<asm/misc.h>` and used by x86 code needing decimal width estimates.

Risks: negating `INT_MIN` overflows in C, which is a latent edge-case risk unless callers avoid it or compiler behavior is tolerated. Uses `long long` threshold to avoid threshold overflow for normal int ranges.

Test signals: unit tests for 0, one-digit values, powers of ten, negative values, and `INT_MIN` behavior review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/msr-reg-export.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/msr-reg-export.c

Purpose: exports safe MSR register-array access helpers implemented in assembly.

Important APIs/functions: exports `rdmsr_safe_regs` and `wrmsr_safe_regs`.

Control flow: none locally; this file only emits export records for the assembly symbols.

State and persistence behavior: no state. Runtime behavior is in `msr-reg.S`.

Dependencies/integration points: depends on `<asm/msr.h>` declarations and the linked `msr-reg.o` symbols. Modules or subsystems needing safe MSR operations with full register arrays rely on these exports.

Risks: if exports are missing or mismatched, modular MSR users fail to link. Symbol names must match assembly exactly.

Test signals: module link tests for MSR helpers and build coverage across 32-bit/64-bit configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/msr-reg-export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/msr-reg.S -->
# sources/distributed-fs/ceph-client/arch/x86/lib/msr-reg.S

Purpose: implements safe MSR read/write helpers that take and update an eight-element general-purpose register array, returning `0` or `-EIO` instead of faulting on MSR exceptions.

Important APIs/functions: macro `op_safe_regs` generates `rdmsr_safe_regs` and `wrmsr_safe_regs`. The register array layout is `u32 gprs[eax, ecx, edx, ebx, esp, ebp, esi, edi]`. 64-bit and 32-bit implementations differ in stack/register handling but share the same logical ABI.

Control flow: each generated function saves callee registers, loads MSR input registers from the array, executes `rdmsr` or `wrmsr` at label `1`, then stores resulting register values back to the array and returns the saved return code. An exception table entry catches faults at the MSR instruction, sets return code to `-EIO`, and jumps to the common store/return path.

State and persistence behavior: reads or writes CPU MSR state and updates the caller-provided register array with post-instruction register values. No global memory state.

Dependencies/integration points: used by low-level MSR access code and exported via `msr-reg-export.c`. Depends on Linux exception tables, x86 MSR instructions, calling conventions, and CFI/linkage annotations on 64-bit.

Risks: MSR faults must be contained reliably; otherwise invalid MSR access can oops the kernel. Stack layout is subtle, especially on 32-bit where the return code and original pointer are staged on the stack. The array layout is ABI-like and must match declarations/users.

Test signals: MSR safe-access tests on valid and invalid MSRs, 32-bit and 64-bit build coverage, module link tests, and exception table validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/msr-reg.S -->
