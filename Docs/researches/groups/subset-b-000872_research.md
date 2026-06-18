# subset-b-000872 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm_host.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm_host.h

## Purpose
Defines the x86 KVM host architecture contract: vCPU and VM architectural state, MMU roles, paravirtual clock state, APIC and interrupt acceleration state, Hyper-V/Xen emulation state, PMU/MTRR/MCE state, request bits, statistics, and the static-call operation table implemented by VMX and SVM. It is the central include consumed by x86 KVM core code and vendor backends.

## Important APIs, Types, And Functions
Major exported types include `struct kvm_vcpu_arch`, `struct kvm_arch`, `struct kvm_mmu`, `union kvm_mmu_page_role`, `union kvm_cpu_role`, `struct kvm_pmu`, `struct kvm_pmc`, `struct kvm_x86_ops`, `struct kvm_x86_nested_ops`, `struct kvm_lapic_irq`, and Hyper-V/Xen substructures. Important request and policy macros include `KVM_REQ_*`, `CR0_RESERVED_BITS`, `CR4_RESERVED_BITS`, `PFERR_*`, `KVM_X86_VALID_QUIRKS`, and APICv inhibit reasons. Function declarations cover MMU creation, root freeing, page faults, CR/MSR/register access, exception/NMI injection, emulation, APICv updates, async page fault delivery, TSC scaling, user-return MSRs, and KVM vendor init/exit. `kvm_x86_call()` and `kvm_pmu_call()` route common code through static calls declared via `asm/kvm-x86-ops.h`.

## Control Flow
The header itself is declarative, but it shapes runtime flow. KVM common x86 code queues `KVM_REQ_*` bits, caches dirty registers in `regs_dirty`, dispatches hardware-specific operations through `kvm_x86_ops`, and routes nested virtualization through `nested_ops`. MMU fault handling uses `struct kvm_mmu` callbacks, role unions, root caches, and memory caches. Entry/exit paths use vCPU arch state for interrupt/NMI/SMI injection, emulation completion, MSR interception, TSC offsets, APICv state, and protected guest hooks. VM-scope paths use `struct kvm_arch` locks, memslot metadata, TDP/MMU root lists, clock state, and filters.

## State And Persistence
State is in-memory and scoped to KVM VMs and vCPUs. Persistent-in-runtime fields include guest registers, control registers, FPU state, CPUID capabilities, MSR values, PMU counters and perf events, APIC maps, MTRRs, machine-check banks, async page fault queues, paravirtual time caches, Hyper-V SynIC timers and TLB flush FIFOs, Xen runstate/evtchn caches, MMU roots, rmap/lpage/write-track metadata, and dirty-log CPU state. No filesystem persistence is defined; userspace migration depends on matching this state through KVM ioctls and nested state APIs.

## Dependencies And Integration Points
Depends on Linux KVM core types, mmu notifiers, perf, pvclock, irqbypass, vhost tasks, x86 APIC/debug/MSR/MTRR/descriptor headers, Hyper-V HVDK, page tracking, and vendor implementation files. Integration points include QEMU/KVM ABI structs, VMX/SVM backends, x86 emulator, LAPIC/IOAPIC/PIT, gmem/private memory, TDX/SEV hooks, Hyper-V and Xen emulation, host perf events, user-return MSRs, and trace/error paths.

## Risks And Edge Cases
Risk concentrates in ABI-sensitive struct fields, request bit numbering, role bit packing, APIC ID/vCPU ID sizing, SMM address spaces, private-memory restrictions, TDP MMU root lifetime, APICv inhibit synchronization, nested run pending state, MSR filters, PMU event filtering, Hyper-V TSC page status, and emulation failure behavior. Changing masks such as `PFERR_SYNTHETIC_MASK`, `KVM_CLOCK_VALID_FLAGS`, or reserved CR bits can alter guest-visible behavior. Static-call table changes must remain synchronized with `kvm-x86-ops.h` and vendor implementations.

## Test Signals
Signals include x86 KVM selftests for CPUID/MSR state, nested VMX/SVM, MMU roles, dirty logging, private memory, APICv/AVIC, Hyper-V and Xen features, SMM, TSC scaling, and emulation failures. Build coverage must include VMX, SVM, 32-bit conditionals, KVM disabled, Hyper-V, Xen, SMM, IOAPIC, external write tracking, and protected guest configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm_host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm_page_track.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm_page_track.h

## Purpose
Defines the optional external write-tracking notifier interface for x86 KVM memory pages. It lets external KVM subsystems observe guest writes to tracked GFNs and be notified when tracked regions disappear.

## Important APIs, Types, And Functions
When `CONFIG_KVM_EXTERNAL_WRITE_TRACKING` is enabled, `struct kvm_page_track_notifier_head` owns an SRCU domain and notifier hlist, while `struct kvm_page_track_notifier_node` provides `track_write()` and `track_remove_region()` callbacks. Public helpers are `kvm_page_track_register_notifier()`, `kvm_page_track_unregister_notifier()`, `kvm_write_track_add_gfn()`, and `kvm_write_track_remove_gfn()`. With the config disabled, an empty notifier node preserves embeddability.

## Control Flow
Registration links a notifier into the VM head under KVM MMU protection. When a guest write to a write-protected tracked page is emulated, KVM invokes `track_write()` after the write completes. When a memslot is deleted, `track_remove_region()` reports the removed GFN range. Add/remove helpers adjust write tracking reference counts for individual GFNs.

## State And Persistence
State is transient VM metadata: the notifier list, SRCU tracking domain, and per-memslot write-track counters referenced through KVM architecture memory-slot state. There is no durable storage.

## Dependencies And Integration Points
Depends on `linux/kvm_types.h`, `struct kvm`, `gpa_t`, and `gfn_t`. It integrates with x86 KVM MMU write protection, memslot lifecycle, and optional consumers such as external shadow paging or accelerator modules.

## Risks And Edge Cases
Callbacks run in sensitive MMU/write-emulation paths and must respect SRCU and KVM lock ordering. Counter imbalance can leave pages over-protected or untracked. Region removal callbacks must tolerate large ranges and memslot teardown. The disabled-config empty struct must remain valid for direct header inclusion tests.

## Test Signals
Useful coverage includes KVM selftests or module tests that register a notifier, add and remove tracked GFNs, verify callback order after emulated writes, delete memslots, and build with `CONFIG_KVM_EXTERNAL_WRITE_TRACKING` both enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm_page_track.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm_para.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm_para.h

## Purpose
Provides x86 guest-side KVM paravirtualization helpers, hypercall wrappers, KVM clock hooks, async page fault handling, and optional paravirtual spinlock initialization.

## Important APIs, Types, And Functions
Defines `KVM_HYPERCALL` using `ALTERNATIVE("vmcall", "vmmcall", X86_FEATURE_VMMCALL)`, wrappers `kvm_hypercall0()` through `kvm_hypercall4()`, and `kvm_sev_hypercall3()`. Guest hooks include `kvmclock_init()`, `kvmclock_disable()`, `kvm_para_available()`, `kvm_arch_para_features()`, `kvm_arch_para_hints()`, `kvm_async_pf_task_wait_schedule()`, `kvm_read_and_reset_apf_flags()`, `kvm_handle_async_pf()`, and `kvm_spinlock_init()`. TDX guests route hypercalls through `tdx_kvm_hypercall()`.

## Control Flow
Guests place the hypercall number in RAX and up to four arguments in RBX, RCX, RDX, and RSI. If the CPU advertises TDX guest mode, wrappers call the TDX-specific hypercall ABI; otherwise inline assembly emits the patched `vmcall`/`vmmcall` instruction. Async page fault handling is gated by the `kvm_async_pf_enabled` static key so the common path returns false when disabled.

## State And Persistence
The header owns no durable state. It exposes static-key-gated APF state and guest clock initialization hooks implemented elsewhere. Hypercall effects depend on host KVM and guest per-CPU state.

## Dependencies And Integration Points
Depends on x86 processor features, alternatives, interrupt regs, UAPI KVM paravirt definitions, and TDX support. It integrates with KVM guest clocksource code, async page fault exception handling, paravirt spinlocks, SEV/TDX confidential guest paths, and host KVM hypercall emulation.

## Risks And Edge Cases
Register constraints are ABI-critical. TDX and SEV paths must not issue unsupported raw hypercall instructions. Disabled `CONFIG_KVM_GUEST` stubs must be side-effect-free. Async page fault handling must remain cheap when the static key is false.

## Test Signals
Boot KVM guests with KVM clock, async page faults, PV spinlocks, SEV, and TDX. Selftests should verify hypercall argument passing and fallback stubs under non-KVM builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm_para.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm_types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm_types.h

## Purpose
Defines small x86-specific KVM type and symbol-export policy constants shared by common KVM code and x86 vendor modules.

## Important APIs, Types, And Functions
`KVM_SUB_MODULES` expands to `kvm-amd`, `kvm-intel`, or both when the respective vendor backends are modules. If neither vendor backend is modular, `EXPORT_SYMBOL_FOR_KVM(symbol)` is suppressed because `kvm.ko` only exists when at least one vendor module is enabled. `KVM_ARCH_NR_OBJS_PER_MEMORY_CACHE` sets the x86 per-cache object target to 40.

## Control Flow
Kbuild and export macro expansion are the only flow. The preprocessor selects module names from `CONFIG_KVM_AMD` and `CONFIG_KVM_INTEL` module states.

## State And Persistence
No runtime state. The constants affect build output and memory-cache sizing in KVM runtime allocations.

## Dependencies And Integration Points
Integrates with Linux KVM symbol exporting, vendor module packaging, and architecture memory-cache helpers included through generic KVM types.

## Risks And Edge Cases
Incorrect module detection can hide symbols required by modular backends or export symbols unnecessarily. Cache sizing changes can affect allocation pressure and latency in MMU hot paths.

## Test Signals
Build matrix coverage for builtin-only, AMD-module-only, Intel-module-only, and both-module KVM configurations is the main signal. Link failures in vendor modules expose export mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm_vcpu_regs.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm_vcpu_regs.h

## Purpose
Provides canonical numeric indexes for x86 KVM vCPU general-purpose registers, used by `kvm_host.h` and register cache bitmaps.

## Important APIs, Types, And Functions
Defines `__VCPU_REGS_RAX` through `__VCPU_REGS_RDI` for all x86 builds and `__VCPU_REGS_R8` through `__VCPU_REGS_R15` when `CONFIG_X86_64` is enabled. There are no functions.

## Control Flow
The header participates in compile-time layout only. `enum kvm_reg` in `kvm_host.h` aliases these values and appends RIP plus extra register slots.

## State And Persistence
No standalone state. The indexes address `struct kvm_vcpu_arch.regs[]`, `regs_avail`, and `regs_dirty`.

## Dependencies And Integration Points
Integrated with KVM register caching, emulator register access, VMX/SVM save/restore code, and userspace register APIs that depend on stable x86 register ordering.

## Risks And Edge Cases
Renumbering entries would corrupt register-cache interpretation. The 64-bit-only registers must remain conditional or 32-bit builds will allocate and reference invalid slots.

## Test Signals
Compile both 32-bit and 64-bit x86 KVM. Register get/set selftests and emulator tests detect ordering mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm_vcpu_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kvmclock.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kvmclock.h

## Purpose
Declares per-CPU KVM pvclock storage accessors for x86 guests using the KVM clocksource.

## Important APIs, Types, And Functions
Exports `DECLARE_PER_CPU(struct pvclock_vsyscall_time_info *, hv_clock_per_cpu)`, `this_cpu_pvti()`, and `this_cpu_hvclock()`. `this_cpu_pvti()` returns the embedded `pvclock_vcpu_time_info`, while `this_cpu_hvclock()` returns the full per-CPU vsyscall time-info object.

## Control Flow
Callers read the current CPU's `hv_clock_per_cpu` pointer and dereference it for time calculations. The helper assumes per-CPU clock storage has been initialized before use.

## State And Persistence
State is per-CPU memory containing pvclock time data shared with the KVM clock implementation. It persists only while the guest kernel runs.

## Dependencies And Integration Points
Depends on Linux per-CPU APIs and pvclock ABI types. It integrates with KVM guest clocksource initialization, vDSO/vsyscall time paths, and paravirtual time updates from the host.

## Risks And Edge Cases
Uninitialized per-CPU pointers or CPU-hotplug mistakes can crash time reads. Time correctness depends on pvclock sequence handling in implementation files outside this header.

## Test Signals
KVM guest boot, CPU hotplug, timekeeping selftests, vDSO clock tests, and suspend/resume under KVM clock exercise these helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kvmclock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/linkage.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/linkage.h

## Purpose
Defines x86 assembly linkage, alignment, return, CFI, and symbol-start macros used by assembly and low-level C code.

## Important APIs, Types, And Functions
Key macros include `notrace`, `_THIS_IP_`, x86-32 `asmlinkage`, `__ALIGN`, `FUNCTION_PADDING`, `ASM_FUNC_ALIGN`, `SYM_F_ALIGN`, assembler/C `RET` and `ASM_RET`, `__CFI_TYPE()`, `SYM_TYPED_FUNC_START()`, `SYM_FUNC_START*()`, `SYM_FUNC_ALIAS_MEMFUNC`, and `SYM_PIC_ALIAS()`. Return macros route through `__x86_return_thunk` under rethunk mitigation or append `int3` under SLS mitigation.

## Control Flow
The preprocessor selects alignment and padding based on `CONFIG_FUNCTION_ALIGNMENT`, `CONFIG_CALL_PADDING`, export/VDSO contexts, and mitigation options. Assembly entry macros then emit aligned symbols, ENDBR where needed, CFI type stubs, and safe return sequences.

## State And Persistence
No runtime state. It affects generated text layout, symbol tables, CFI metadata, and patchable padding.

## Dependencies And Integration Points
Depends on `linux/stringify.h` and `asm/ibt.h`. It integrates with objtool, kCFI, retbleed/SLS mitigations, alternative patching, exportable assembly routines, VDSO builds, and position-independent startup aliases.

## Risks And Edge Cases
Alignment or padding mistakes break alternatives, ftrace/livepatch expectations, kCFI symbol layout, or mitigation validation. The RET macro must stay consistent with `nospec-branch.h` thunks and build contexts that intentionally disable exports.

## Test Signals
Builds with kCFI, IBT, call padding, SLS, rethunk, VDSO, UML, and x86-32 should pass objtool validation and boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/linkage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/local.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/local.h

## Purpose
Implements x86 `local_t`, a per-CPU/local counter API backed by `atomic_long_t` but using non-lock-prefixed instructions where safe.

## Important APIs, Types, And Functions
Defines `local_t`, `LOCAL_INIT()`, `local_read()`, `local_set()`, `local_inc()`, `local_dec()`, `local_add()`, `local_sub()`, condition helpers such as `local_sub_and_test()`, `local_add_negative()`, return-value helpers, `local_cmpxchg()`, `local_try_cmpxchg()`, `local_xchg()`, `local_add_unless()`, and `local_inc_not_zero()`. The `__local_*` macros alias the same operations.

## Control Flow
Simple add/sub/inc/dec emit inline x86 arithmetic on memory. Tests use `GEN_*_RMWcc` helpers to derive flags. Return-value add uses `xadd`, while exchange and add-unless loop with local compare-exchange until successful or blocked by the sentinel value.

## State And Persistence
State is the counter value in memory, generally used for CPU-local data. It is not globally synchronized unless callers enforce locality or locking.

## Dependencies And Integration Points
Depends on Linux per-CPU and atomic APIs plus x86 asm helper macros. It integrates with generic local counter users and x86 optimized atomic primitives.

## Risks And Edge Cases
These are not a replacement for inter-CPU atomic operations. Misusing them on shared data can race. `local_xchg()` intentionally avoids locked `xchg` for performance, so correctness relies on locality.

## Test Signals
Atomic/local API compile tests, lockless counter stress tests under preemption-disabled use, and x86-32/x86-64 build coverage provide signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mach_timer.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/mach_timer.h

## Purpose
Provides legacy machine-specific TSC calibration helpers using the PIT channel 2 gate and counter.

## Important APIs, Types, And Functions
Defines `CALIBRATE_TIME_MSEC`, `CALIBRATE_LATCH`, `mach_prepare_counter()`, and `mach_countup()`. The helpers program PIT channel 2 through ports `0x43`, `0x42`, and gate/speaker port `0x61`.

## Control Flow
`mach_prepare_counter()` raises the gate, disables the speaker, programs PIT channel 2 for mode 0, and loads the calibration latch. `mach_countup()` busy-loops until port `0x61` indicates terminal count, returning the loop count through an output pointer.

## State And Persistence
State is transient hardware timer programming and port state during calibration. It does not persist beyond boot-time calibration except for the resulting TSC calibration computed elsewhere.

## Dependencies And Integration Points
Depends on PIT constants and port I/O helpers. It integrates with legacy x86 TSC calibration paths and early timer setup.

## Risks And Edge Cases
Port I/O timing is hardware-sensitive. Virtualized or unusual systems may emulate the PIT poorly. Busy-loop count depends on compiler and CPU behavior, so calibration users must bound error.

## Test Signals
Boot logs reporting sane TSC frequency on 32-bit/legacy paths, PIT-emulated virtual machines, and old hardware are the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mach_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mach_traps.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/mach_traps.h

## Purpose
Defines default x86 machine-specific NMI reason handling and NMI reassertion support.

## Important APIs, Types, And Functions
Defines NMI reason port `0x61`, SERR/IOCHK reason and clear masks, `default_get_nmi_reason()`, and `reassert_nmi()`. It uses CMOS lock helpers from `mc146818rtc.h`.

## Control Flow
`default_get_nmi_reason()` reads port `0x61`. `reassert_nmi()` preserves or acquires the CMOS index lock, toggles RTC index registers `0x8f` and `0x0f` with dummy reads to reassert an NMI, then restores the previous CMOS index or unlocks.

## State And Persistence
Only transient port and CMOS index state is touched. The CMOS lock tracks ownership on 32-bit builds.

## Dependencies And Integration Points
Depends on RTC/CMOS accessors and x86 port I/O. It integrates with trap/NMI handling code that diagnoses system error and I/O check NMIs.

## Risks And Edge Cases
NMI context is fragile: CMOS lock ownership must be restored exactly. Port `0x70/0x71` access can race with RTC users if locking rules are broken. Hardware behavior is legacy-platform-specific.

## Test Signals
Build coverage plus NMI injection or hardware error tests that exercise unknown, SERR, and IOCHK NMI paths. Regression signals include lost CMOS index state or stuck NMI sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mach_traps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/math_emu.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/math_emu.h

## Purpose
Declares the minimal stack-context structure used by old x86 floating-point math emulation paths.

## Important APIs, Types, And Functions
Defines `struct math_emu_info` with `___orig_eip` and `struct pt_regs *regs`. There are no helpers.

## Control Flow
The structure models data saved around a device-not-present exception so emulation code can recover the faulting instruction pointer and register state.

## State And Persistence
State is exception-frame-local. It is not persisted beyond the emulation event.

## Dependencies And Integration Points
Depends on `asm/ptrace.h` for `pt_regs`. It integrates with legacy FPU emulation and trap handling on configurations that still build those paths.

## Risks And Edge Cases
The field layout must match stack expectations from 80386/80486-era exception handling. Any mismatch breaks instruction restart or register access.

## Test Signals
Compile coverage for math emulation configs and any legacy FPU-emulation boot or trap tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/math_emu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mc146818rtc.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/mc146818rtc.h

## Purpose
Defines machine-dependent CMOS/MC146818 RTC register access helpers and locking rules for x86.

## Important APIs, Types, And Functions
Defines `RTC_PORT()`, `RTC_ALWAYS_BCD`, `CMOS_READ()`, `CMOS_WRITE()`, `RTC_IRQ`, `rtc_cmos_read()`, `rtc_cmos_write()`, `mach_set_cmos_time()`, and `mach_get_cmos_time()`. On x86-32 it declares `cmos_lock` and inline helpers `lock_cmos()`, `unlock_cmos()`, `do_i_have_lock_cmos()`, `current_lock_cmos_reg()`, `lock_cmos_prefix()`, and `lock_cmos_suffix()`.

## Control Flow
32-bit locking stores owner CPU plus current CMOS register in a single word using compare-and-swap. NMI code can detect if it interrupted the current owner and temporarily access CMOS while preserving the index register. Non-32-bit builds stub the lock helpers.

## State And Persistence
CMOS hardware persists RTC/date settings. Kernel state is the transient `cmos_lock` owner/register marker. `mach_set_cmos_time()` writes durable RTC time; `mach_get_cmos_time()` reads it.

## Dependencies And Integration Points
Depends on x86 port I/O, processor helpers, SMP CPU IDs, and the generic RTC core. It is used by timekeeping, NMI reassertion, and legacy platform code.

## Risks And Edge Cases
CMOS index/data port access is globally serialized and NMI-sensitive. Incorrect lock restoration can corrupt unrelated RTC accesses. BCD/binary mode assumptions and century handling are implementation-side risks.

## Test Signals
RTC read/write tests, suspend/resume time validation, 32-bit NMI stress, and boot-time CMOS access on legacy hardware or emulators are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mc146818rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mce.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/mce.h

## Purpose
Defines x86 machine-check architecture constants, error record structures, notifier APIs, polling flags, vendor-specific Scalable MCA IDs, and initialization hooks.

## Important APIs, Types, And Functions
Important macros cover `MCG_CAP`, `MCG_STATUS`, `MCi_STATUS`, AMD SMCA MSR address calculation, MCACOD masks, MCE handling flags, and `MAX_NR_BANKS`. Types include `struct mce_log_buffer`, `enum mce_notifier_prios`, `struct mce_hw_err`, `mce_banks_t`, `enum mcp_flags`, and AMD `enum smca_bank_types`. Functions include `mcheck_init()`, `mca_bsp_init()`, `mcheck_cpu_init()`, `mce_prep_record()`, `mce_log()`, `machine_check_poll()`, `do_machine_check()`, `mce_register_decode_chain()`, Intel/AMD feature init hooks, APEI reporting helpers, and copy-machine-check helpers.

## Control Flow
CPU init discovers MCA banks and vendor features, machine-check exceptions populate `struct mce_hw_err`, records are decoded through notifier chains, and polling checks selected banks with flags controlling timestamps and uncorrected-error logging. Intel CMCI and AMD deferred error paths use vector hooks declared here.

## State And Persistence
State includes per-CPU MCE devices, exception/poll counters, poll bank bitmaps, injection records, MCE log buffers, bank state, and hardware MSRs. Logs persist only in kernel memory or downstream reporting facilities.

## Dependencies And Integration Points
Depends on UAPI MCE records, CPU feature data, percpu/atomic APIs, APEI/CPER, EDAC, NFIT, mcelog consumers, and vendor-specific MCA decoders.

## Risks And Edge Cases
Bit definitions are hardware ABI. Recovery decisions depend on `PCC`, `AR`, `S`, address validity, and kernel-copy flags. Vendor structure offsets are externally parsed and must remain stable. Polling, CMCI, deferred interrupts, and firmware-claimed banks must not double-report or clear errors incorrectly.

## Test Signals
RAS/MCE injection tests, APEI error injection, EDAC/mcelog decode paths, copy_mc fault tests, Intel CMCI rediscovery, AMD SMCA bank typing, and build coverage with MCE disabled are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mem_encrypt.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/mem_encrypt.h

## Purpose
Declares AMD SME/SEV memory encryption setup interfaces, early encrypt/decrypt helpers, decrypted BSS section annotations, and physical-address masking helpers.

## Important APIs, Types, And Functions
Exports `mem_encrypt_init()`, `mem_encrypt_setup_arch()`, `sme_encrypt_execute()`, `sme_early_encrypt()`, `sme_early_decrypt()`, `sme_map_bootdata()`, `sme_unmap_bootdata()`, `sme_early_init()`, `sme_encrypt_kernel()`, `sme_enable()`, `early_set_memory_decrypted()`, `early_set_memory_encrypted()`, `early_set_mem_enc_dec_hypercall()`, `mem_encrypt_free_decrypted_mem()`, `sev_es_init_vc_handling()`, `sme_get_me_mask()`, `add_encrypt_protection_map()`, `__sme_pa()`, and `__sme_pa_nodebug()`. State symbols are `sme_me_mask` and `sev_status`.

## Control Flow
Early boot discovers encryption support, sets the SME mask, encrypts or decrypts kernel regions, maps boot data with correct attributes, and initializes SEV-ES VC handling. Non-enabled configs compile to stubs and zero masks.

## State And Persistence
State is boot-time and global: encryption mask, SEV status, decrypted BSS ranges, and page attribute changes. It persists for the lifetime of the booted kernel but not across reboot.

## Dependencies And Integration Points
Depends on confidential-computing platform helpers, boot parameters, page-table physical address conversion, and AMD memory-encryption code. It integrates with early boot, kernel relocation/encryption, SEV-ES exception handling, and hypercall-assisted attribute changes.

## Risks And Edge Cases
Incorrect mask use in CR3 or page-table addresses can corrupt address translation. Early decrypted/encrypted transitions run before normal allocators and are hard to recover from. Stubs must preserve callers across non-AMD or disabled builds.

## Test Signals
Boot tests on SME, SEV, SEV-ES, and non-encrypted systems; kexec/suspend smoke tests; and early page attribute validation are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mem_encrypt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/memtype.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/memtype.h

## Purpose
Declares x86 PAT and memory-type reservation APIs used to coordinate cacheability attributes for RAM, IO mappings, and kernel mappings.

## Important APIs, Types, And Functions
Functions include `pat_enabled()`, `pat_bp_init()`, `pat_cpu_init()`, `memtype_reserve()`, `memtype_free()`, `memtype_kernel_map_sync()`, `memtype_reserve_io()`, `memtype_free_io()`, `pat_pfn_immune_to_uc_mtrr()`, `x86_has_pat_wp()`, and `pgprot2cachemode()`.

## Control Flow
Callers reserve a physical range with a requested page cache mode and receive the effective mode. Kernel and IO mapping paths synchronize attributes with PAT/MTRR state. Free calls release reservations.

## State And Persistence
The header declares access to global PAT/memtype reservation state maintained elsewhere. Reservations persist while mappings or drivers hold them.

## Dependencies And Integration Points
Depends on Linux types, resources, and x86 page table cache-mode definitions. It integrates with ioremap, DRM/framebuffer WC mappings, MTRR interaction, kernel text/data mappings, and PAT CPU initialization.

## Risks And Edge Cases
Conflicting cacheability aliases can cause data corruption or machine checks. Range end semantics must be consistent. PAT write-protect support is CPU-dependent, and UC MTRR immunity must be honored.

## Test Signals
PAT selftests, ioremap/memremap cache-mode tests, driver WC mapping tests, and boot logs for PAT/MTRR setup provide signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/memtype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/microcode.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/microcode.h

## Purpose
Defines x86 microcode loader interfaces, CPU signature structures, Intel microcode blob layout, revision helpers, and late-loading NMI hooks.

## Important APIs, Types, And Functions
Types include `struct cpu_signature`, `struct ucode_cpu_info`, `struct microcode_header_intel`, and `struct microcode_intel`. Functions include `load_ucode_bsp()`, `load_ucode_ap()`, `microcode_bsp_resume()`, `microcode_loader_disabled()`, `intel_microcode_get_datasize()`, `intel_get_platform_id()`, `intel_get_microcode_revision()`, `microcode_nmi_handler()`, `microcode_offline_nmi_handler()`, and `microcode_nmi_handler_enabled()`. `initrd_start_early` exposes early initrd location.

## Control Flow
Early BSP/AP loaders apply microcode during boot or resume. Intel revision reads write zero to `MSR_IA32_UCODE_REV`, executes CPUID leaf 1, then reads the revision MSR. Late loading can enable an NMI handler through a static key.

## State And Persistence
State includes per-CPU signature/revision data, loaded microcode payload pointers, and CPU microcode hardware state. Updates persist until reset and are not filesystem-persistent through this header.

## Dependencies And Integration Points
Depends on MSR helpers and Intel CPU support. It integrates with early initrd scanning, CPU hotplug, suspend/resume, Intel IFS public header needs, and late microcode synchronization.

## Risks And Edge Cases
Microcode updates are CPU- and platform-sensitive. Header struct layout must match Intel blob format. Late loading needs NMI coordination and can interact with mitigations and errata state.

## Test Signals
Boot-time microcode revision logs, CPU hotplug after update, resume tests, late-loading tests, Intel and non-Intel build coverage, and disabled-loader command-line coverage are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/microcode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/misc.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/misc.h

## Purpose
Declares miscellaneous x86 helper `num_digits()`.

## Important APIs, Types, And Functions
The sole API is `int num_digits(int val)`, expected to return the decimal digit count for an integer value.

## Control Flow
No inline flow is present; callers link to the implementation elsewhere.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Used by x86 code needing compact numeric formatting without pulling in larger helpers.

## Risks And Edge Cases
Implementation behavior for zero and negative values must match callers' expectations. The header is intentionally minimal.

## Test Signals
Compile/link coverage and any formatting tests around integer digit counts are sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mman.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/mman.h

## Purpose
Adds x86 memory-management protection-key VM flag translation before including the UAPI mmap definitions.

## Important APIs, Types, And Functions
When `CONFIG_X86_INTEL_MEMORY_PROTECTION_KEYS` is enabled, `arch_calc_vm_prot_bits(prot, key)` maps low four bits of a protection key to `VM_PKEY_BIT0` through `VM_PKEY_BIT3`. It then includes `uapi/asm/mman.h`.

## Control Flow
Compile-time macro expansion attaches pkey bits to VMA protection flags during mmap/mprotect handling.

## State And Persistence
No state in this header. Pkey state lives in mm context and VMA flags.

## Dependencies And Integration Points
Integrates with generic mm pkey handling, x86 PKU support, and user-visible mmap/mprotect constants.

## Risks And Edge Cases
Incorrect bit mapping would assign the wrong protection key to VMAs. Disabled configs must leave generic behavior unchanged.

## Test Signals
Protection key selftests, mmap/mprotect tests, and builds with PKU enabled and disabled are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mmconfig.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/mmconfig.h

## Purpose
Declares x86 PCI MMCONFIG enablement quirks for AMD systems.

## Important APIs, Types, And Functions
When `CONFIG_PCI_MMCONFIG` is enabled, exports `fam10h_check_enable_mmcfg()` and `check_enable_amd_mmconf_dmi()`. Otherwise both compile to empty stubs.

## Control Flow
Boot-time PCI setup can call these helpers to detect and enable memory-mapped PCI config space on systems that need family 10h or DMI-based quirks.

## State And Persistence
No header-owned state. Implementations may update PCI MMCONFIG availability for the booted kernel.

## Dependencies And Integration Points
Integrates with x86 PCI initialization, ACPI/firmware MMCONFIG discovery, and AMD platform quirks.

## Risks And Edge Cases
Enabling incorrect MMCONFIG ranges can break PCI config access. Stubs must allow non-MMCONFIG builds to compile without conditional callers.

## Test Signals
Boot PCI enumeration on AMD family 10h and affected DMI systems, plus builds with `CONFIG_PCI_MMCONFIG` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mmconfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mmu.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/mmu.h

## Purpose
Defines x86 `mm_context_t`, the architecture-specific per-mm state used for TLB generation, LDT, LAM, VDSO, protection keys, RDPMC permission, and optional global ASID tracking.

## Important APIs, Types, And Functions
Key flags are `MM_CONTEXT_UPROBE_IA32`, `MM_CONTEXT_HAS_VSYSCALL`, `MM_CONTEXT_LOCK_LAM`, `MM_CONTEXT_FORCE_TAGGED_SVA`, and `MM_CONTEXT_NOTRACK`. `mm_context_t` contains `ctx_id`, `tlb_gen`, `next_trim_cpumask`, optional `ldt_usr_sem`/`ldt`, LAM masks, `lock`, `vdso`, `vdso_image`, `perf_rdpmc_allowed`, pkey allocation fields, and broadcast TLB global ASID fields. `INIT_MM_CONTEXT()` initializes `init_mm` context.

## Control Flow
The fields are manipulated by context creation, duplication, exit, and `switch_mm` paths. TLB update paths increment `tlb_gen` after page-table modifications before flushing.

## State And Persistence
State is per-process address-space state. It persists for the lifetime of an `mm_struct` and is inherited or reset during fork/exec according to `mmu_context.h`.

## Dependencies And Integration Points
Depends on locks, atomics, LAM, pkeys, VDSO, uprobe IA32 mode, broadcast TLB flush, and paravirt/Xen behavior. It integrates with the scheduler, TLB flushing, mm teardown, perf RDPMC, and userspace address tagging.

## Risks And Edge Cases
`ctx_id` must not be reused. `tlb_gen` ordering is central to avoiding stale translations. LAM and DMA/SVA compatibility flags must be synchronized. LDT lifetime is security-sensitive.

## Test Signals
TLB shootdown tests, LAM tests, pkey tests, modify_ldt tests, VDSO mapping tests, perf RDPMC policy tests, and fork/exec stress are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mmu_context.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/mmu_context.h

## Purpose
Implements x86 address-space context lifecycle helpers: LDT management, LAM duplication, pkey duplication, context ID allocation, `switch_mm` declarations, and temporary-mm APIs.

## Important APIs, Types, And Functions
Defines optional `struct ldt_struct`, `init_new_context_ldt()`, `ldt_dup_context()`, `destroy_context_ldt()`, `load_mm_ldt()`, `switch_ldt()`, `mm_lam_cr3_mask()`, `dup_lam()`, `mm_untag_mask()`, `mm_reset_untag_mask()`, `arch_pgtable_dma_compat()`, `init_new_context()`, `destroy_context()`, `switch_mm()`, `switch_mm_irqs_off()`, `activate_mm`, `deactivate_mm`, `arch_dup_pkeys()`, `arch_dup_mmap()`, `arch_exit_mmap()`, `is_64bit_mm()`, `is_notrack_mm()`, `set_notrack_mm()`, `arch_vma_access_permitted()`, `__get_current_cr3_fast()`, `use_temporary_mm()`, and `unuse_temporary_mm()`.

## Control Flow
`init_new_context()` initializes the context lock, allocates a monotonic `ctx_id`, clears `tlb_gen`, initializes pkey defaults, global ASID, LAM untag mask, and LDT state. Fork duplication copies pkeys and LAM state then duplicates LDT. Exit tears down paravirt and LDT state. Context switch callers use `switch_mm_irqs_off()` and architecture-specific deactivate cleanup for GS/FS and shadow stacks.

## State And Persistence
State persists per `mm_struct`: context ID, TLB generation, LDT, LAM, pkeys, global ASID, and VDSO metadata. Temporary mm switching changes CPU CR3 state temporarily, not durable storage.

## Dependencies And Integration Points
Depends on pkeys, TLB flush tracing, paravirt, debug registers, GS segment, descriptors, LAM, shadow stacks, and generic mmu context. It integrates with scheduler context switching, fork/exec, `modify_ldt`, PKRU enforcement, DMA/SVA compatibility, and kernel temporary mapping code.

## Risks And Edge Cases
LAM masks are read locklessly during switch, so `READ_ONCE` semantics matter. LDT alias mappings are PTI-sensitive. Pkey enforcement only applies to current non-foreign VMAs. Context IDs must be monotonic and global ASID lifetime must match mm lifetime.

## Test Signals
Fork/exec stress, modify_ldt tests, LAM and pkey selftests, context-switch TLB tests, temporary-mm users, shadow-stack builds, and paravirt/Xen builds provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/module.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/module.h

## Purpose
Defines x86 module architecture-specific metadata for ORC unwinding and indirect-target selection mitigation pages.

## Important APIs, Types, And Functions
Types include `struct its_array` with optional `pages` and `num`, and `struct mod_arch_specific` with ORC unwind table fields `num_orcs`, `orc_unwind_ip`, `orc_unwind`, plus `its_pages`.

## Control Flow
Module loader code fills this metadata when loading modules with ORC unwind data or ITS mitigation support. The header itself is structural.

## State And Persistence
State is per-loaded-module kernel memory. It persists until module unload.

## Dependencies And Integration Points
Depends on generic module metadata and `asm/orc_types.h`. It integrates with the ORC unwinder, module loader relocation, and mitigation code that allocates ITS thunk pages.

## Risks And Edge Cases
Incorrect ORC counts or pointers break stack unwinding through modules. ITS page lifetime must match module lifetime. Disabled config fields must not be referenced.

## Test Signals
Module load/unload tests, ORC unwinder stack traces through modules, livepatch/ftrace module coverage, and ITS mitigation build coverage are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mpspec.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/mpspec.h

## Purpose
Declares x86 Intel MultiProcessor Specification parser state, bus/IRQ capacity constants, APIC identity globals, and helper accessors.

## Important APIs, Types, And Functions
Defines `MAX_MP_BUSSES` and `MAX_IRQ_SOURCES` by architecture/config, declares `pic_mode`, optional `mp_bus_id_to_type`, `mp_bus_not_pci`, `boot_cpu_physical_apicid`, `boot_cpu_apic_version`, `smp_found_config`, MP parser functions, `phys_cpu_present_map`, `reset_phys_cpu_present_map()`, and `copy_phys_cpu_present_map()`.

## Control Flow
Early boot parser functions locate and parse MP tables when `CONFIG_X86_MPPARSE` is enabled; otherwise they become no-ops. Helper functions reset or copy the physical APIC present bitmap.

## State And Persistence
State is boot-time topology and interrupt-routing metadata retained in globals after parsing. It is not durable beyond boot.

## Dependencies And Integration Points
Depends on MP table structures, x86 init hooks, APIC definitions, EISA support, and local APIC config. It integrates with SMP bring-up, IOAPIC routing, and legacy firmware table parsing.

## Risks And Edge Cases
Capacity constants must cover old large 32-bit Summit/generic systems and 64-bit PCI IRQ source counts. Incorrect APIC present maps affect CPU discovery. Disabled parser stubs must keep call sites simple.

## Test Signals
Boot on MP-table-only systems, ACPI-disabled configurations, 32-bit large bus configs, SMP CPU discovery logs, and IOAPIC IRQ routing tests provide signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mpspec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mpspec_def.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/mpspec_def.h

## Purpose
Defines the packed Intel MP Specification 1.1/1.4 table structures and constants used by x86 MP table parsers.

## Important APIs, Types, And Functions
Defines `SMP_MAGIC_IDENT`, `MPC_SIGNATURE`, entry type constants `MP_PROCESSOR`, `MP_BUS`, `MP_IOAPIC`, `MP_INTSRC`, `MP_LINTSRC`, and `MP_TRANSLATION`, CPU flags, bus type strings, APIC flags, IRQ polarity/trigger masks, `MP_APIC_ALL`, `MPC_OEM_SIGNATURE`, `enum mp_irq_source_types`, `enum mp_bustype`, and structures `mpf_intel`, `mpc_table`, `mpc_cpu`, `mpc_bus`, `mpc_ioapic`, `mpc_intsrc`, `mpc_lintsrc`, and `mpc_oemtable`.

## Control Flow
The parser reads the floating pointer structure, validates signatures/checksums, then walks entries by type using these layouts to build CPU, bus, IOAPIC, and interrupt-source state.

## State And Persistence
No runtime state is owned here. The structs describe firmware memory that is consumed at boot.

## Dependencies And Integration Points
Integrated with `mpspec.h`, early SMP parsing, IOAPIC setup, and legacy firmware compatibility.

## Risks And Edge Cases
Field sizes and order are firmware ABI and cannot drift. Checksum/signature constants must match the spec. Unexpected OEM or translation entries require parser-side bounds handling.

## Test Signals
MP table parser tests, booting ACPI-disabled legacy SMP guests, fuzzed MP table parsing, and 32-bit `MAX_MPC_ENTRY` build coverage are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mpspec_def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mshyperv.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/mshyperv.h

## Purpose
Declares x86 Microsoft Hyper-V integration: hypercall ABI helpers, isolation-type detection, VP assist pages, TLB flush hypercalls, APIC/MSI mapping, confidential VM hooks, VTL mode support, and synthetic MSR helpers.

## Important APIs, Types, And Functions
Important definitions include `HV_IOAPIC_BASE_ADDRESS`, VTL constants, `hyperv_fill_flush_list_func`, `hv_do_hypercall()`, `hv_do_fast_hypercall8()`, `hv_do_fast_hypercall16()`, `hv_get_vp_assist_page()`, `hyperv_init()`, `hyperv_setup_mmu_ops()`, TSC change callbacks, `hyperv_flush_guest_mapping*()`, `hv_create_pci_msi_domain()`, `hv_map_msi_interrupt()`, `hv_map_ioapic_interrupt()`, `hv_ghcb_*()`, `hv_vtom_init()`, `hv_ivm_msr_read/write()`, `hv_is_synic_msr()`, `hv_is_sint_msr()`, `hv_get_msr()`, `hv_set_msr()`, `hv_apicid_to_vp_index()`, `struct mshv_vtl_cpu_context`, and VTL return-call hooks.

## Control Flow
On 64-bit Hyper-V builds, hypercalls dispatch through a static call that selects standard, SNP, or TDX hypercall implementations. On 32-bit, inline assembly calls the hypercall page through `CALL_NOSPEC`. Fast hypercalls pass register operands without parameter pages. Disabled configs compile most operations to stubs returning failure or zero.

## State And Persistence
State includes hypercall page pointers, per-CPU GHCB pages, VP assist pages, isolation static keys, TSC callbacks, and VTL CPU context saved across secure returns. It persists for the running guest or root partition session only.

## Dependencies And Integration Points
Depends on Hyper-V HVDK ABI, x86 MSR and nospec helpers, MSI/IRQ domains, io access, FPU state, SEV-SNP, TDX, and generic Hyper-V code. It integrates with clock/TLB management, APIC, PCI MSI, crash dump, confidential VM boot, and VTL mode transitions.

## Risks And Edge Cases
Hypercall register ABI and physical address translation are critical. Isolation type must select the correct hypercall path. Disabled stubs must match callers' error expectations. VTL context layout must match assembly save/restore.

## Test Signals
Hyper-V guest boot, enlightened TLB flush tests, synthetic interrupt/MSI tests, SNP/TDX confidential guest boot, VTL mode tests, crash dump coverage, and non-Hyper-V build coverage are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mshyperv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/msi.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/msi.h

## Purpose
Defines x86-specific MSI message bit layouts, allocation info aliasing, and PCI MSI preparation hooks.

## Important APIs, Types, And Functions
Defines `msi_alloc_info_t`, `pci_msi_prepare()`, packed `arch_msi_msg_data_t`, `arch_msi_msg_addr_lo_t`, `arch_msi_msg_addr_hi_t`, `X86_MSI_BASE_ADDRESS_LOW`, `X86_MSI_BASE_ADDRESS_HIGH`, `x86_msi_msg_get_destid()`, `X86_VECTOR_MSI_FLAGS_SUPPORTED`, and `X86_VECTOR_MSI_FLAGS_REQUIRED`.

## Control Flow
IRQ domain allocation uses `pci_msi_prepare()` to fill architecture allocation data. MSI composition code packs vector, delivery mode, destination mode, trigger/level, redirect hint, and destination ID bits into message address/data fields, with alternate DMAR subhandle layout.

## State And Persistence
No persistent state. MSI messages are programmed into devices and interrupt-remapping tables by callers.

## Dependencies And Integration Points
Depends on x86 hardware IRQ and IRQ domain types plus generic MSI definitions. It integrates with PCI MSI/MSI-X, interrupt remapping, xAPIC/x2APIC destination encoding, and vector domains.

## Risks And Edge Cases
Packed bitfields must match APIC/MSI hardware format and endianness expectations. Extended destination IDs and DMAR formats are easy to encode incorrectly. Required flags must remain aligned with generic MSI core behavior.

## Test Signals
PCI MSI/MSI-X device tests, interrupt remapping tests, high APIC ID systems, dynamic MSI-X allocation, and IRQ affinity tests provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/msi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/msr-index.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/msr-index.h

## Purpose
Provides the central x86 model-specific register number and bit-definition catalog used across CPU feature, mitigation, PMU, power, MTRR, machine-check, virtualization, and vendor-specific code.

## Important APIs, Types, And Functions
The file defines MSR numbers such as `MSR_EFER`, syscall MSRs, FS/GS base MSRs, FRED MSRs, `MSR_IA32_SPEC_CTRL`, `MSR_IA32_PRED_CMD`, MTRR/PAT MSRs, debug/branch tracing MSRs, PASID/CET MSRs, machine-check MSRs, RAPL/HWP/power MSRs, Intel PT/LBR/PEBS MSRs, AMD/Hygon/VIA/Centaur ranges, VMX/SVM feature MSRs, and many feature bit masks including `EFER_*`, `SPEC_CTRL_*`, `PRED_CMD_*`, `ARCH_CAP_*`, and memory type constants `X86_MEMTYPE_*`.

## Control Flow
There is no runtime flow; preprocessor constants are consumed by MSR read/write paths, CPU init, mitigation setup, perf, KVM, MCE, power drivers, and virtualization code.

## State And Persistence
No state is owned here. The constants address hardware MSR state, much of which persists until CPU reset or microcode-managed changes.

## Dependencies And Integration Points
Depends on `linux/bits.h`. It is integrated nearly everywhere x86 low-level code touches MSRs: `msr.h`, KVM, perf, speculation mitigations, microcode, RAPL, MTRR/PAT, MCE, CET, FRED, Intel PT, and vendor initialization.

## Risks And Edge Cases
Wrong numbers or masks can write the wrong CPU register, causing crashes, security exposure, or silent misconfiguration. Vendor-specific overlap and reserved bits require careful naming. Newly added bits must match SDM/PPR documentation and users must mask reserved fields.

## Test Signals
Broad x86 boot coverage, MSR selftests, KVM CPUID/MSR tests, perf tests, mitigation sysfs validation, powercap/RAPL tests, MCE injection, and vendor build coverage are required signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/msr-index.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/msr-trace.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/msr-trace.h

## Purpose
Defines tracepoints for x86 MSR and PMC access instrumentation.

## Important APIs, Types, And Functions
Declares `TRACE_SYSTEM msr`, trace include path/file, event class `msr_trace_class`, and concrete events `read_msr`, `write_msr`, and `rdpmc`. Each event records MSR/counter number, 64-bit value, and failure status.

## Control Flow
`msr.h` calls trace helpers after MSR/PMC accesses when tracepoints are enabled. The trace event prints the register number, value, and `#GP` marker on failure.

## State And Persistence
Tracepoint state is managed by ftrace/perf infrastructure. Event records persist only in trace buffers.

## Dependencies And Integration Points
Depends on Linux tracepoint APIs and is included by `msr.h`/trace generation. It integrates with kernel tracing, perf, and debugging of MSR failures.

## Risks And Edge Cases
Tracepoint format is user-visible to tracing tools. Excessive tracing of hot MSR paths can perturb timing. Failed accesses must be reported without causing recursive faults.

## Test Signals
Trace event enable/disable tests, `trace-cmd` or ftrace reads of MSR events, and build coverage with tracepoints disabled are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/msr-trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/msr.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/msr.h

## Purpose
Implements x86 MSR and PMC access primitives, safe exception-handled variants, trace integration, per-CPU MSR helpers, SMP remote access declarations, and WRMSRNS support.

## Important APIs, Types, And Functions
Types include `struct msr_info`, `struct msr_regs_info`, `struct saved_msr`, and `struct saved_msrs`. Core helpers include `__rdmsr()`, `__wrmsrq()`, `native_rdmsr()`, `native_rdmsrq()`, `native_wrmsr()`, `native_wrmsrq()`, `native_read_msr()`, `native_read_msr_safe()`, `native_write_msr()`, `native_write_msr_safe()`, `native_read_pmc()`, `rdmsr()`, `wrmsr()`, `rdmsrq()`, `wrmsrq()`, `rdmsr_safe()`, `wrmsrq_safe()`, `rdpmc()`, `wrmsrns()`, `msrs_alloc()`, `msrs_free()`, bit set/clear helpers, and `*_on_cpu()` variants.

## Control Flow
Bare primitives emit `rdmsr` or `wrmsr` with exception table fixups. Safe variants return an error instead of faulting. Traced wrappers call trace hooks when enabled. Paravirt builds can override generic wrappers; non-paravirt builds call native helpers. SMP helpers execute MSR operations on target CPUs or fall back to CPU 0 in UP builds.

## State And Persistence
The header manipulates CPU MSR hardware state. Per-CPU `struct msr` allocations store temporary snapshots. Hardware changes persist until overwritten or reset.

## Dependencies And Integration Points
Depends on `msr-index.h`, x86 asm constraints, exception tables, cpumasks, UAPI MSR structs, tracepoints, atomics, and paravirt. It integrates with CPU init, KVM, perf, mitigations, power management, MCE, and debug code.

## Risks And Edge Cases
Invalid MSRs can #GP, so safe variants and exception types must be correct. Register constraints must preserve low/high halves. `wrmsrns()` is feature-gated through alternatives. Tracing must not alter bare primitive semantics.

## Test Signals
MSR selftests, safe invalid-MSR probes, remote CPU MSR tests, tracepoint tests, paravirt builds, and WRMSRNS-capable CPU boot coverage are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/msr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mtrr.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/mtrr.h

## Purpose
Defines x86 Memory Type Range Register hardware masks, saved-state structure, runtime APIs, fallback stubs, and 32-bit compat ioctl layouts.

## Important APIs, Types, And Functions
Defines masks for `MTRR_CAP`, default type, `PHYSBASE`, and `PHYSMASK`, plus `struct mtrr_state_type`. Runtime APIs under `CONFIG_MTRR` include `mtrr_bp_init()`, `guest_force_mtrr_state()`, `mtrr_type_lookup()`, `mtrr_save_fixed_ranges()`, `mtrr_save_state()`, `mtrr_add()`, `mtrr_add_page()`, `mtrr_del()`, `mtrr_del_page()`, `mtrr_trim_uncached_memory()`, `amd_special_default_mtrr()`, `mtrr_disable()`, `mtrr_enable()`, and `mtrr_generic_set_state()`. Compat structs and `MTRRIOC32_*` ioctl numbers support 32-bit userspace.

## Control Flow
Callers add/delete MTRR ranges, save/restore fixed ranges, look up effective type over an address range, and temporarily disable/enable MTRRs during updates. Disabled configs return uncachable defaults or `-ENODEV`.

## State And Persistence
State includes hardware MTRR MSRs and saved kernel copies in `mtrr_state_type`. Hardware state persists until changed or reset.

## Dependencies And Integration Points
Depends on UAPI MTRR types and Linux bits. It integrates with PAT, cacheability selection, KVM guest MTRR emulation, `/proc/mtrr` ioctls, and early memory trimming.

## Risks And Edge Cases
MTRR changes affect cache coherency globally. Range alignment, fixed vs variable ranges, and default types are hardware-sensitive. Compat ioctl layouts must stay ABI-stable.

## Test Signals
MTRR ioctl tests, PAT/MTRR cache-type tests, KVM guest MTRR tests, AMD default MTRR quirks, and disabled-config builds are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mtrr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mwait.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/mwait.h

## Purpose
Provides inline wrappers and constants for MONITOR/MWAIT, AMD MONITORX/MWAITX, Intel TPAUSE, and idle-loop MWAIT usage.

## Important APIs, Types, And Functions
Defines hint masks, CPUID leaf 5 flags, `MWAIT_ECX_INTERRUPT_BREAK`, `MWAITX_ECX_TIMER_ENABLE`, `MWAITX_MAX_WAIT_CYCLES`, TPAUSE state constants, `__monitor()`, `__monitorx()`, `__mwait()`, `__mwaitx()`, `__sti_mwait()`, `mwait_idle_with_hints()`, and `__tpause()`.

## Control Flow
Idle code checks `need_resched()`, clears CPU buffers if required, sets polling, optionally flushes the monitored address for CPU errata, executes MONITOR on `thread_info.flags`, then either uses interrupt-breaking MWAIT or `sti; mwait` followed by IRQ disable. MWAITX adds a timer in EBX/ECX. TPAUSE encodes the instruction manually.

## State And Persistence
State is CPU-local wait state, polling flags, monitored address state, and optional idle buffer-clearing side effects. No durable persistence.

## Dependencies And Integration Points
Depends on scheduler idle APIs, CPU features, and nospec buffer clearing. It integrates with x86 idle drivers, scheduler reschedule signaling, and CPU errata workarounds.

## Risks And Edge Cases
The `sti; mwait` sequence must be adjacent to avoid missing interrupts. Errata `X86_BUG_MONITOR` and `X86_BUG_CLFLUSH_MONITOR` must be honored. MWAIT hints and timer fields are vendor-specific.

## Test Signals
Idle residency tests, scheduler wakeup latency tests, CPU hotplug, suspend/resume, AMD MWAITX-capable systems, Intel UMWAIT/TPAUSE tests, and errata build coverage are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/mwait.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/nmi.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/nmi.h

## Purpose
Declares x86 NMI handler registration, NMI source types, panic policy globals, perf counter reservation hooks, and NMI stop/restart helpers.

## Important APIs, Types, And Functions
Defines NMI types `NMI_LOCAL`, `NMI_UNKNOWN`, `NMI_SERR`, `NMI_IO_CHECK`, `NMI_MAX`, return values `NMI_DONE` and `NMI_HANDLED`, `NMI_FLAG_FIRST`, `nmi_handler_t`, `struct nmiaction`, `register_nmi_handler()`, `__register_nmi_handler()`, `unregister_nmi_handler()`, `set_emergency_nmi_handler()`, `stop_nmi()`, `restart_nmi()`, `local_touch_nmi()`, panic policy globals, and local-APIC perf counter reservation helpers.

## Control Flow
Handlers are registered as static `struct nmiaction` objects and linked into per-type lists. The NMI dispatcher invokes handlers by type, with first handlers prioritized. Unknown NMIs can be offered to fallback handlers.

## State And Persistence
State is in-memory handler lists, panic policy globals, perf NMI reservations, and emergency handler pointers. It persists while the kernel runs.

## Dependencies And Integration Points
Depends on irq work, PM, IRQ definitions, I/O, local APIC, perf, watchdog, and machine-check/trap code.

## Risks And Edge Cases
NMI handlers run in non-maskable context and must be minimal. Registration names are used for removal. Panic policy changes can make hardware noise fatal. Perf reservations must avoid counter conflicts.

## Test Signals
NMI watchdog tests, perf NMI reservation tests, unknown NMI injection, SERR/IOCHK paths, panic policy sysctl tests, and stop/restart NMI coverage are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/nmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/nops.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/nops.h

## Purpose
Defines canonical x86 multi-byte NOP byte sequences and assembler string macros for alternatives, tracing, and code padding.

## Important APIs, Types, And Functions
Defines `BYTES_NOP1` through `BYTES_NOP8` for 32-bit, `BYTES_NOP1` through `BYTES_NOP11` for 64-bit, `ASM_NOP1` through `ASM_NOP11` where available, `ASM_NOP_MAX`, and external `x86_nops[]`.

## Control Flow
Compile-time selection chooses 32-bit or 64-bit NOP encodings. Alternative patching and alignment code consume the byte macros or runtime `x86_nops` table.

## State And Persistence
No runtime state except the external NOP table. Generated instruction bytes persist in kernel text.

## Dependencies And Integration Points
Depends on x86 asm byte helpers. It integrates with alternatives, ftrace, static calls, jump labels, and padding/alignment machinery.

## Risks And Edge Cases
Wrong-length NOPs corrupt instruction patching. 32-bit and 64-bit encodings differ and must remain compatible with supported assemblers and CPUs. Prefix-heavy long NOPs must not create unintended instructions.

## Test Signals
Alternative patching tests, ftrace/static-call/jump-label boot coverage, objdump validation of NOP lengths, and 32-bit/64-bit builds are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/nops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/nospec-branch.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/nospec-branch.h

## Purpose
Defines x86 speculative-execution mitigation macros and helpers for retpolines, RSB stuffing, return thunks, IBPB/IBRS control, call-depth tracking, branch-history clearing, and CPU buffer clearing.

## Important APIs, Types, And Functions
Important macros include `RET_DEPTH_*`, `RSB_RET_STUFF_LOOPS`, `__FILL_RETURN_BUFFER`, `__FILL_ONE_RETURN`, assembler `JMP_NOSPEC`, `CALL_NOSPEC`, `FILL_RETURN_BUFFER`, `UNTRAIN_RET*`, `CLEAR_CPU_BUFFERS`, `CLEAR_BRANCH_HISTORY*`, and C `CALL_NOSPEC`/`THUNK_TARGET`. Types include `retpoline_thunk_t`, `its_thunk_t`, `enum spectre_v2_mitigation`, `enum spectre_v2_user_mitigation`, and `enum ssb_mitigation`. Helpers include `alternative_msr_write()`, `indirect_branch_prediction_barrier()`, `firmware_restrict_branch_speculation_start/end()`, `spec_ctrl_current()`, `update_spec_ctrl_cond()`, `x86_clear_cpu_buffers()`, and `x86_idle_clear_cpu_buffers()`.

## Control Flow
Assembler paths use alternatives to patch mitigation sequences depending on CPU features. Indirect branches route through thunks under retpoline. Return paths can stuff RSB entries, untrain predictors, issue IBPB, or account call depth. Firmware calls temporarily enable IBRS/IBPB. VERW clears CPU buffers when the static key or feature requires it.

## State And Persistence
State includes per-CPU call-depth counters, debug counters, `x86_spec_ctrl_base`, per-CPU current SPEC_CTRL, static keys for mitigation policy, and thunk function pointers. Hardware predictor and buffer state is transient.

## Dependencies And Integration Points
Depends on alternatives, cpufeatures, MSR definitions, objtool annotations, unwind hints, percpu data, and segment selectors. It integrates with entry code, context switch, VM exit, firmware calls, idle, KVM, and compiler-generated retpoline expectations.

## Risks And Edge Cases
Mitigation code is security-critical and instruction-layout-sensitive. Missing annotations can fail objtool validation. Wrong feature gating can leave speculation windows or impose unnecessary overhead. Register clobbers and stack adjustments in RSB stuffing must be exact.

## Test Signals
Objtool noinstr validation, mitigation sysfs tests, Spectre/MDS/TSA mitigation boot logs, KVM VM-exit tests, firmware-call paths, retpoline builds, call-depth debug counters, and CPU-vendor matrix coverage are essential.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/nospec-branch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/numa.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/numa.h

## Purpose
Declares x86 NUMA CPU/node mapping state and lifecycle helpers.

## Important APIs, Types, And Functions
With `CONFIG_NUMA`, declares `numa_off`, `__apicid_to_node[]`, `numa_nodes_parsed`, `numa_phys_nodes_parsed`, `set_apicid_to_node()`, `numa_cpu_node()`, `numa_set_node()`, `numa_clear_node()`, `init_cpu_to_node()`, `numa_add_cpu()`, `numa_remove_cpu()`, `init_gi_nodes()`, and `num_phys_nodes()`. Non-NUMA builds provide stubs and return `NUMA_NO_NODE` or 1 physical node. Debug builds can call `debug_cpumask_set_cpu()`.

## Control Flow
Early topology code maps APIC IDs to nodes, initializes CPU-to-node maps, and updates mappings during CPU hotplug. Non-NUMA configs compile calls away.

## State And Persistence
State is boot-time and hotplug-updated NUMA topology in node masks and APIC-to-node arrays. It persists for the running kernel.

## Dependencies And Integration Points
Depends on node masks, topology, APIC definitions, and debug per-CPU maps. It integrates with memory policy, scheduler topology, CPU hotplug, ACPI/SRAT parsing, and platform-specific NUMA code.

## Risks And Edge Cases
APIC ID bounds and overrides are important, especially on 32-bit with APIC-specific `numa_cpu_node()` behavior. Wrong mappings hurt locality or break memory allocation assumptions.

## Test Signals
NUMA boot on multi-node systems, CPU hotplug, SRAT parsing tests, scheduler topology checks, and non-NUMA build coverage are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/numa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/numachip/numachip.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/numachip/numachip.h

## Purpose
Declares minimal Numascale NumaConnect platform detection and PCI initialization hooks.

## Important APIs, Types, And Functions
Exports global `u8 numachip_system` and `int __init pci_numachip_init(void)`.

## Control Flow
Platform detection code sets `numachip_system`, and PCI initialization calls `pci_numachip_init()` during boot on matching systems.

## State And Persistence
`numachip_system` is boot-time platform state that persists for the running kernel. No filesystem persistence.

## Dependencies And Integration Points
Integrates with x86 platform setup, Numachip APIC/CSR code, and PCI initialization.

## Risks And Edge Cases
False platform detection can route PCI or APIC setup through Numachip-specific paths on non-Numachip hardware. Missing init on real hardware can break PCI topology.

## Test Signals
Boot coverage on Numascale systems or emulation, PCI enumeration logs, and non-Numachip boot regression checks are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/numachip/numachip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/numachip/numachip_csr.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/numachip/numachip_csr.h

## Purpose
Defines Numascale NumaConnect CSR address constants and inline read/write helpers for local CSR spaces on first- and second-generation Numachip systems.

## Important APIs, Types, And Functions
Defines `CSR_NODE_SHIFT`, `CSR_NODE_BITS()`, `CSR_NODE_MASK`, `CSR_OFFSET_MASK`, CSR offsets such as `CSR_G0_NODE_IDS` and `CSR_G3_EXT_IRQ_GEN`, first-generation `NUMACHIP_LCSR_*` constants, `lcsr_address()`, `read_lcsr()`, `write_lcsr()`, second-generation `NUMACHIP2_LCSR_*`, timer/APIC offsets, `numachip2_lcsr_address()`, `numachip2_read32_lcsr()`, `numachip2_read64_lcsr()`, `numachip2_write32_lcsr()`, `numachip2_write64_lcsr()`, and `numachip2_timer()`.

## Control Flow
Callers compute local CSR virtual addresses by ORing fixed physical windows with offset masks, then perform endian-swapped 32-bit accesses for original Numachip or native 32/64-bit MMIO accesses for Numachip2. `numachip2_timer()` selects per-CPU timer offset using CPU ID modulo 48.

## State And Persistence
State is hardware CSR/MMIO state. Writes persist in platform registers until changed or reset.

## Dependencies And Integration Points
Depends on SMP CPU IDs, I/O accessors, byte swapping, `__va()`, and platform mapping assumptions. It integrates with Numachip interrupt, timer, APIC, and node discovery code.

## Risks And Edge Cases
Physical windows and PMD alignment assumptions are platform-specific. Endianness swapping must match hardware. The CPU modulo timer calculation assumes fixed per-node timer layout.

## Test Signals
Boot on Numachip/Numachip2 hardware, CSR read sanity, timer interrupt delivery, external IRQ generation, and CPU hotplug on high-node systems are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/numachip/numachip_csr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/olpc.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/olpc.h

## Purpose
Declares OLPC XO platform identification, board revision helpers, DCON presence checks, power-management hooks, PCI init, and GPIO assignments.

## Important APIs, Types, And Functions
Defines `struct olpc_platform_t`, flags `OLPC_F_PRESENT` and `OLPC_F_DCON`, `olpc_board()`, `olpc_board_pre()`, `machine_is_olpc()`, `olpc_has_dcon()`, `olpc_board_at_least()`, optional `do_olpc_suspend_lowlevel()`, `olpc_xo1_pm_wakeup_set()`, `olpc_xo1_pm_wakeup_clear()`, `pci_olpc_init()`, and GPIO constants for DCON, SMBus, lid, EC SCI, thermal alarm, and workaux lines.

## Control Flow
Platform detection fills `olpc_platform_info`; inline helpers query flags and board revision. Power-management and PCI setup code calls the declared platform hooks only when configured.

## State And Persistence
State is `olpc_platform_info` and hardware GPIO/PM state. It persists for the running kernel and through suspend as managed by platform code.

## Dependencies And Integration Points
Depends on Geode GPIO helpers. Integrates with OLPC platform setup, DCON display controller driver, GPIO users, PCI quirks, and XO-1 power management.

## Risks And Edge Cases
Board revision comparisons encode OLPC prototype numbering. Incorrect GPIO constants break platform devices. Stubs for non-OLPC builds must keep generic x86 code harmless.

## Test Signals
Boot on XO-1/XO variants, DCON driver probe, lid/EC SCI GPIO interrupts, suspend/resume wakeup, PCI init, and non-OLPC build coverage are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/olpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/olpc_ofw.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/olpc_ofw.h

## Purpose
Declares OLPC Open Firmware detection, call, page-table setup, and device-tree construction interfaces.

## Important APIs, Types, And Functions
Defines `OLPC_OFW_PDE_NR`, `OLPC_OFW_SIG`, `olpc_ofw(name, args, res)` wrapper, `__olpc_ofw()`, `olpc_ofw_detect()`, `setup_olpc_ofw_pgd()`, `olpc_ofw_present()`, `olpc_ofw_is_installed()`, and `olpc_dt_build_devicetree()`. Disabled configs provide no-op stubs for setup/detection.

## Control Flow
Boot code detects whether OFW is installed and mapped at the expected location, installs its PDE into kernel page tables, then later callers can invoke firmware commands through `__olpc_ofw()` with argument/result arrays. Device-tree construction can query OFW.

## State And Persistence
State is detected firmware presence and page-table mapping. It persists for the booted kernel.

## Dependencies And Integration Points
Integrates with OLPC platform boot, early page-table setup, firmware calls, and device-tree population.

## Risks And Edge Cases
Calling firmware requires exact argument counts and stable mapping. Wrong PDE index or signature handling can corrupt page tables or call absent firmware. Disabled stubs omit `olpc_ofw_present()`, so callers must be config-aware.

## Test Signals
OLPC boot with OFW present, device-tree creation, firmware command smoke tests, and non-OLPC build coverage are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/olpc_ofw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/orc_header.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/orc_header.h

## Purpose
Emits an ORC metadata header containing the generated hash of the ORC entry definition.

## Important APIs, Types, And Functions
Defines `ORC_HEADER`, which places a static used 4-byte-aligned `orc_header[]` into the `.orc_header` section with bytes from `ORC_HASH`.

## Control Flow
Compilation of files that use `ORC_HEADER` emits the section. Tooling compares the embedded hash against expected ORC entry layout generated by `scripts/orc_hash.sh`.

## State And Persistence
No runtime mutable state. The section persists in the kernel image or object file.

## Dependencies And Integration Points
Depends on Linux compiler attributes, types, and `asm/orc_hash.h`. It integrates with objtool, ORC unwind metadata generation, and module/kernel image validation.

## Risks And Edge Cases
If `ORC_HASH` does not reflect `struct orc_entry`, unwinder metadata can be misinterpreted. Section alignment and retention are important during link and LTO-like transformations.

## Test Signals
Objtool ORC validation, kernel/module link checks for `.orc_header`, and unwinder smoke tests provide signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/orc_header.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/orc_lookup.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/orc_lookup.h

## Purpose
Defines ORC unwinder lookup-table block sizing and symbols used to accelerate searches through `.orc_unwind`.

## Important APIs, Types, And Functions
Defines `LOOKUP_BLOCK_ORDER` as 8, `LOOKUP_BLOCK_SIZE` as 256, external symbols `orc_lookup[]` and `orc_lookup_end[]`, and lookup address bounds `LOOKUP_START_IP` and `LOOKUP_STOP_IP` when not in linker-script context.

## Control Flow
The ORC unwinder maps an instruction pointer range to a subset of the ORC table through lookup blocks, reducing search cost. The linker script consumes the same constants without C symbols.

## State And Persistence
The lookup table is generated into kernel image data and is immutable at runtime.

## Dependencies And Integration Points
Integrates with ORC table generation, linker scripts, unwinder runtime, and `_stext`/`_etext` kernel text bounds.

## Risks And Edge Cases
Block size must be a power of two and match generator/runtime expectations. Wrong text bounds or table endpoints can make unwinding fail or search out of range.

## Test Signals
ORC unwinder tests, stack traces under interrupts/exceptions, objtool validation, and linker-script builds are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/orc_lookup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/orc_types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/orc_types.h

## Purpose
Defines the compact ORC unwind entry format and register/type constants used by objtool and the in-kernel ORC unwinder.

## Important APIs, Types, And Functions
Defines ORC register constants `ORC_REG_UNDEFINED`, `ORC_REG_AX`, `ORC_REG_DX`, `ORC_REG_SP`, `ORC_REG_BP`, `ORC_REG_DI`, `ORC_REG_R10`, `ORC_REG_R13`, `ORC_REG_PREV_SP`, indirect variants, and `ORC_REG_MAX`; type constants `ORC_TYPE_UNDEFINED`, `END_OF_STACK`, `CALL`, `REGS`, and `REGS_PARTIAL`; and packed `struct orc_entry` with SP/BP offsets, base registers, type, and signal flag.

## Control Flow
Objtool emits one ORC entry for one or more code locations. At runtime the unwinder reads the entry for an IP and computes previous SP/BP or register frames according to these fields.

## State And Persistence
ORC entries are immutable metadata in kernel/module images. No mutable state is declared here.

## Dependencies And Integration Points
Depends on Linux types/compiler attributes and x86 bitfield byte order. It integrates with objtool, `orc_header.h`, module metadata, and the ORC unwinder.

## Risks And Edge Cases
The packed bitfield layout is ABI between objtool and the kernel; endian handling must stay correct. Offset ranges are 16-bit signed, so unusual stacks need correct representation.

## Test Signals
Objtool validation, live stack traces through entry code, interrupts, modules, and signal-like frames, plus ORC hash checks are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/orc_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/page.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/page.h

## Purpose
Provides the main x86 kernel page header wrapper: architecture page includes, physical/virtual address conversion macros, page copy helpers, PFN mapping declarations, and canonical-address helpers.

## Important APIs, Types, And Functions
Includes `page_types.h` and either `page_64.h` or `page_32.h`. Declares `pfn_mapped[]`, `nr_pfn_mapped`, `copy_user_page()`, `vma_alloc_zeroed_movable_folio()`, `__pa()`, `__pa_nodebug()`, `__pa_symbol()`, `__va()`, `__boot_va()`, `__boot_pa()`, `virt_to_page()`, `virt_addr_valid()`, `pfn_to_kaddr()`, `__canonical_address()`, `__is_canonical_address()`, and `HAVE_ARCH_HUGETLB_UNMAPPED_AREA`.

## Control Flow
Callers convert between kernel virtual and physical addresses, validate direct-map addresses, copy pages, and canonicalize virtual addresses using sign extension based on address width. The selected 32-bit or 64-bit page header supplies low-level implementations.

## State And Persistence
State is global PFN mapping ranges and memory model data declared elsewhere. Address conversions are pure calculations.

## Dependencies And Integration Points
Depends on page type definitions, generic memory model, getorder helpers, folio allocation, and architecture page headers. It integrates with memory management, boot mappings, hugetlb, direct map, and low-level address validation.

## Risks And Edge Cases
`__pa_symbol()` hides relocation arithmetic from compiler overflow assumptions. `virt_to_page()` is valid only if `virt_addr_valid()` is true. Canonical-address helpers must match LA48/LA57 rules.

## Test Signals
Memory hotplug, debug-virtual checks, hugetlb tests, canonical address tests, direct-map validation, and 32-bit/64-bit builds are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/page_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/page_32.h

## Purpose
Defines x86-32 physical address conversion and basic page clear/copy helpers.

## Important APIs, Types, And Functions
Includes `page_32_types.h`, defines `__phys_addr_nodebug(x)` as `x - PAGE_OFFSET`, optional debug `__phys_addr()`, `__phys_addr_symbol()`, `__phys_reloc_hide()`, and inline `clear_page()` and `copy_page()` using `memset()` and `memcpy()`.

## Control Flow
Address conversion subtracts the 32-bit kernel `PAGE_OFFSET`. Page clear/copy helpers operate directly on kernel virtual addresses without exception handling.

## State And Persistence
No state is declared. The helpers mutate page memory supplied by callers.

## Dependencies And Integration Points
Depends on 32-bit page type constants and Linux string routines. It is included by `page.h` for non-64-bit x86 builds and used throughout mm initialization and page management.

## Risks And Edge Cases
No exception handling means callers must pass valid mapped kernel addresses. Debug virtual builds replace `__phys_addr()` with a checked function. The direct subtraction model assumes classic 32-bit kernel mapping.

## Test Signals
x86-32 build and boot coverage, debug-virtual tests, page allocator tests, and memory copy/clear stress provide signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/page_32.h -->
