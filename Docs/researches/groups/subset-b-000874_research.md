# Research: subset-b-000874

Grouped research for x86 architecture processor, register, boot, virtualization, memory-protection, syscall, locking, stack, string, time, and TLB headers. Each section is keyed by exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/processor.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/processor.h

Purpose: defines central x86 CPU and task-processor state used across boot, scheduling, entry code, CPU feature detection, idle, mitigations, and low-level helpers. Important APIs/types include `cpuinfo_topology`, `cpuinfo_x86`, x86 vendor IDs, `x86_hw_tss`, `x86_io_bitmap`, `tss_struct`, entry/IRQ stack objects, `thread_struct`, `task_pt_regs()`, CR3 helpers, prefetch helpers, `start_thread()`, TSC control macros, LLC/L2 helpers, AMD divider clearing, L1TF/MDS mitigation enums, and `weak_wrmsr_fence()`.

Control flow: most logic is inline glue that callers use during CPU bring-up, context switching, entry handling, and mitigation paths. Boot and CPU hotplug populate `boot_cpu_data`, `new_cpu_data`, and per-CPU `cpu_info`; scheduler and entry code consume `thread_struct`, top-of-stack, TSS, and I/O bitmap fields; CR3 and CR4-related users rely on the helper wrappers to preserve encryption and serialization constraints.

State and persistence: owns declarations for per-CPU CPU descriptors, TSS pages, IRQ stack pointers, top-of-stack values, task thread state, CPU capability masks, bootloader identity, mitigation settings, and cache-coherency indicators. All state is runtime kernel state, with some fields visible through `/proc/cpuinfo`, ELF aux vectors, ptrace/debug paths, and task context switches.

Dependencies and integration points: includes FPU, segments, page tables, CPUID, special instructions, percpu, memory encryption, shadow stack, and paravirt hooks. It integrates with scheduler switch code, entry assembly, SMP bring-up, CPU detection, microcode, idle selection, x86 mitigations, FPU state placement, and TSS/I/O permission management.

Risks: layout changes in `thread_struct`, `pt_regs` placement helpers, TSS, or I/O bitmap offsets can break entry assembly and hardware ABI expectations. Capability and topology fields feed userspace ABI and mitigation decisions. CR3 and WRMSR helpers must preserve SME encryption bits and ordering for weakly ordered MSR uses. Test signals include boot on 32/64-bit, SMP CPU hotplug, ptrace/FPU/debug register tests, I/O permission tests, idle selection, `/proc/cpuinfo`, and mitigation selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/prom.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/prom.h

Purpose: provides x86 OpenFirmware/device-tree declarations. Important APIs are `of_ioapic`, `initial_dtb`, `add_dtb()`, `x86_of_pci_init()`, `x86_flattree_get_config()`, and the exported boot `cmd_line`.

Control flow: when `CONFIG_OF` is enabled, early boot and PCI initialization can record a DTB address, parse the flattened tree, and initialize PCI/device-tree resources. Without OF support, the header supplies no-op stubs and `of_ioapic` as zero so call sites compile away.

State and persistence: stores only boot-time DTB and command-line state; nothing persists beyond kernel runtime. Dependencies include Linux OF, PCI, IRQ, and x86 setup definitions. Risks are wrong conditional stubs masking missing OF initialization or breaking early boot command-line/DTB parsing. Test signals include OF-enabled x86 boot with IOAPIC and PCI nodes, no-OF builds, and DTB command-line propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/prom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/proto.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/proto.h

Purpose: centralizes miscellaneous x86 architecture prototypes used by entry, syscall, NX setup, reboot, and 64-bit arch-prctl code. Important APIs include `syscall_init()`, entry symbols for native and compat syscall/sysenter/sysret paths, `x86_configure_nx()`, `reboot_force`, and `do_arch_prctl_64()`.

Control flow: initialization code calls `syscall_init()` and NX setup; ptrace and arch-prctl code call `do_arch_prctl_64()` for FS/GS and related 64-bit controls; entry code and helpers use the declared symbol boundaries for syscall-gap detection and single-step regions. Compat symbols are replaced with NULL when IA32 emulation is absent.

State and persistence: only declares runtime entry symbols and reboot flag state. Dependencies are LDT/task structures and architecture entry assembly. Risks are prototype mismatches with assembly, incorrect compat NULL assumptions, and syscall-gap boundary drift. Test signals include syscall/sysenter/sysret on native and compat tasks, NX boot configuration, and arch-prctl FS/GS tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pti.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pti.h

Purpose: exposes Page Table Isolation lifecycle hooks for x86. Important APIs are `pti_init()`, `pti_check_boottime_disable()`, and `pti_finalize()` when `CONFIG_MITIGATION_PAGE_TABLE_ISOLATION` is enabled, with a no-op disable-check stub otherwise.

Control flow: early boot checks command-line/CPU state to disable PTI if appropriate, initializes PTI mappings, then finalizes them after paging setup. State is owned by the implementation rather than this header. Dependencies include mitigation config and entry/page-table code.

Risks: PTI is a security boundary for kernel/user page-table separation; calling order and config stubs must match boot paging state. Test signals include PTI-enabled and disabled boots, KPTI command-line switches, Meltdown-vulnerable CPU coverage, and syscall/interrupt entry tests under PTI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pti.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/ptrace.h

Purpose: defines the kernel-visible x86 `pt_regs` layouts and register access helpers used by entry code, ptrace, kprobes, ftrace, syscall handling, signal delivery, and stack unwinding. It also models FRED CS/SS extension fields on 64-bit builds.

Important APIs/types/functions: 32-bit and 64-bit `struct pt_regs`, `fred_cs`, `fred_ss`, `regs_return_value()`, `regs_set_return_value()`, `user_mode()`, `v8086_mode()`, `user_64bit_mode()`, `any_64bit_mode()`, `ip_within_syscall_gap()`, register pointer accessors, `regs_get_register()`, stack-range helpers, `regs_get_kernel_stack_nth()`, `regs_get_kernel_argument()`, single/block-step capability macros, and thread-area prototypes.

Control flow: entry assembly populates `pt_regs`; generic kernel code uses the helpers to classify user/kernel origin, retrieve return values, recover function arguments, and walk saved kernel stack slots. FRED-enabled 64-bit systems extend the saved CS/SS slots with event metadata; compat and 32-bit code handle vm86 and 16-bit selector fields specially.

State and persistence: `pt_regs` instances live on kernel stacks or exception frames and are transient, but their layout is ABI-sensitive through ptrace, signal frames, perf, kprobes, and core dumps. Dependencies include segment constants, page/thread sizes, paravirt extra user CS, entry symbols from `proto.h`, and nofault copying.

Risks: any layout or offset drift breaks assembly, debugger ABI, syscall tracing, and signal return. Stack argument recovery is heuristic and must avoid unsafe kernel memory reads. FRED metadata must remain synchronized with hardware event-frame format. Test signals include ptrace register read/write, signal delivery/return, syscall tracing, kprobe/ftrace argument fetches, FRED and non-FRED entry tests, vm86 on 32-bit, and compat syscall paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/purgatory.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/purgatory.h

Purpose: declares the x86 kexec purgatory entry point. Important API is `purgatory()` plus the generic purgatory include.

Control flow: kexec/crash-kexec code transfers through purgatory to verify and prepare the next kernel before final jump. This header has no executable logic; it only gives C users the assembly symbol. State is maintained by generic kexec/purgatory code. Risks are symbol/prototype mismatches or assembly-only include misuse. Test signals include normal `kexec -e`, crash kernel boot, and purgatory checksum validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/purgatory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pvclock-abi.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pvclock-abi.h

Purpose: defines the KVM/Xen paravirtual clock ABI shared between hypervisor and guest. Important types are packed `pvclock_vcpu_time_info` and `pvclock_wall_clock`; important flags are `PVCLOCK_TSC_STABLE_BIT`, `PVCLOCK_GUEST_STOPPED`, and the deprecated `PVCLOCK_COUNTS_FROM_ZERO`.

Control flow: guests read a versioned time structure using an odd/even update protocol to avoid torn hypervisor updates, then scale TSC deltas against `system_time`. State is hypervisor-shared memory, not kernel-owned persistence. Dependencies include exact packing and shared ABI knowledge from Xen/KVM.

Risks: these structures must not change because layout is a hypervisor ABI. Version handling, flag interpretation, and field widths affect guest time monotonicity. Test signals include KVM/Xen boot, pvclock wallclock reads, live migration/resume, guest-stop flag handling, and timekeeping stability tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pvclock-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pvclock.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pvclock.h

Purpose: supplies x86 pvclock helper declarations and inline read/scale primitives used by KVM and Xen clock sources. Important APIs include `pvclock_clocksource_read()`, `pvclock_read_flags()`, `pvclock_tsc_khz()`, `pvclock_read_wallclock()`, `pvclock_resume()`, `pvclock_touch_watchdogs()`, `pvclock_read_begin()`, `pvclock_read_retry()`, `pvclock_scale_delta()`, `__pvclock_read_cycles()`, and pvti CPU0 accessors.

Control flow: callers read a stable version, copy time fields, compute scaled TSC deltas with architecture-specific multiply code, then retry if the hypervisor version changed. Clocksource and wallclock paths use the same ABI structures to produce nanoseconds or wall time.

State and persistence: uses hypervisor-updated pvclock pages and optional per-CPU vsyscall time info; no disk persistence. Dependencies include pvclock ABI, virtual memory barriers, clocksource, paravirt clock config, and x86 asm multiply semantics. Risks include torn reads, scaling overflow/shift bugs, unstable TSC flags, and incorrect 32-bit multiply constraints. Test signals include pvclock monotonicity, 32/64-bit builds, migration/resume, watchdog touch behavior, and vDSO/paravirt clock access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pvclock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/qrwlock.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/qrwlock.h

Purpose: wires x86 queued read/write locks to the generic qrwlock implementation and type definitions. There are no x86-specific functions in this header.

Control flow and state: all behavior is inherited from `asm-generic/qrwlock.h` and `qrwlock_types.h`; lock state lives in generic qrwlock structures. Dependencies are generic queued rwlock primitives. Risks are limited to include ordering and architecture feature expectations. Test signals are generic locking, lockdep, rwsem/rwlock stress, and SMP contention tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/qrwlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/qspinlock.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/qspinlock.h

Purpose: provides x86 queued spinlock customization, especially the pending-bit fast path and paravirtual lock integration. Important APIs/macros are `_Q_PENDING_LOOPS`, `queued_fetch_set_pending_acquire()`, `native_pv_lock_init()`, and inclusion of generic qspinlock logic.

Control flow: lock acquisition uses `GEN_BINARY_RMWcc()` with a locked `btsl` to atomically set the pending bit and reconstruct the observed lock word, then falls through to generic queued spinlock paths. Paravirt builds route through paravirt spinlock hooks.

State and persistence: lock state resides in `struct qspinlock`; this header owns no global state. Dependencies include jump labels, CPU features, paravirt, `rmwcc`, and generic qspinlock types. Risks include incorrect condition-code read-modify-write semantics, pending-bit races, and paravirt/native divergence. Test signals include SMP spinlock stress, locktorture, paravirt guests, and queued lock fairness under contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/qspinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/qspinlock_paravirt.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/qspinlock_paravirt.h

Purpose: defines optimized paravirtual queued spinlock unlock glue for x86. Important APIs are `__pv_queued_spin_unlock_slowpath()`, callee-save thunks, `__pv_queued_spin_unlock`, and the 64-bit `PV_UNLOCK_ASM` implementation.

Control flow: the fast path attempts a locked byte `cmpxchg` from locked to zero; if it fails, it preserves required registers and calls the slowpath with the observed lock byte. On 32-bit, the implementation is an external callee-save function instead of inline hand-coded assembly.

State and persistence: operates only on `struct qspinlock` lock bytes. Dependencies include IBT/ENDBR-compatible thunk machinery, qspinlock constants, and paravirt slowpath code. Risks include calling convention drift, register save/restore errors, section placement, and IBT annotation issues. Test signals include paravirt guest locktorture, unlock fast/slow path tracing, objtool validation, and 32/64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/qspinlock_paravirt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/realmode.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/realmode.h

Purpose: describes the x86 real-mode blob headers and trampoline entry data used for SMP startup, ACPI resume, BIOS/APM reboot, and encrypted-memory AP startup. Important types are `real_mode_header` and `trampoline_header`; APIs include `real_mode_size_needed()`, `set_real_mode_mem()`, `reserve_real_mode()`, `load_trampoline_pgtable()`, and `init_real_mode()`.

Control flow: boot reserves low memory for the real-mode blob, copies/relocates the blob, initializes trampoline fields such as start address, EFER/CR4, SME flags, and lock word, then AP startup/reboot/resume paths jump through those real-mode entry points.

State and persistence: global pointers and symbols reference the allocated blob, relocation table, trampoline lock, initial code/stack, optional VC handler, and architecture-specific startup symbols. State is boot/runtime low-memory state. Dependencies include realmode assembly layouts, ACPI sleep, AMD memory encryption, paging, and SMP startup. Risks are strict layout coupling with assembly, low-memory allocation mistakes, SME/SEV flag handling, and wrong trampoline page table setup. Test signals include SMP bring-up, CPU hotplug, ACPI S3 resume, reboot modes, SEV-ES AP startup, and relocation-size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/realmode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/reboot.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/reboot.h

Purpose: declares x86 machine reboot, halt, poweroff, shutdown, and crash shutdown operations. Important type is `struct machine_ops`; important APIs include `machine_ops`, `crashing_cpu`, `native_machine_crash_shutdown()`, `native_machine_shutdown()`, `machine_real_restart()`, `nmi_shootdown_cpus()`, and `run_crash_ipi_callback()`.

Control flow: generic reboot/poweroff paths dispatch through `machine_ops`; crash paths mark `crashing_cpu`, shoot down other CPUs via NMI callbacks, and may enter real-mode restart. State is runtime machine operation pointers and crash CPU identity.

Dependencies include kdebug, `pt_regs`, realmode reboot assembly dispatch values `MRR_BIOS`/`MRR_APM`, SMP/NMI infrastructure, and crash-kexec. Risks include failed CPU shootdown, unsafe callback execution in NMI/crash context, and mismatched realmode dispatch constants. Test signals include reboot, halt, poweroff, emergency restart, crash dump, NMI shootdown, and BIOS/APM restart modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/reboot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/reboot_fixups.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/reboot_fixups.h

Purpose: declares `mach_reboot_fixups()`, the x86 hook for platform-specific reboot quirks.

Control flow and state: reboot code can invoke the function before reset to apply chipset or machine-specific workarounds; state is owned by implementation-specific fixups. Dependencies are reboot flow and platform quirk tables. Risks are regressions on old machines that require special reset sequencing. Test signals include reboot testing on affected systems and compile/link coverage when fixup support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/reboot_fixups.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/resctrl.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/resctrl.h

Purpose: supplies x86 resource-control integration for Intel/AMD cache allocation and monitoring. Important APIs/types are `resctrl_pqr_state`, per-CPU `pqr_state`, capability booleans, static keys, `resctrl_arch_enable_alloc/mon()`, `resctrl_arch_disable_alloc/mon()`, `resctrl_arch_sched_in()`, CLOSID/RMID setters/matchers, RMID index encoding, monitor context stubs, and `resctrl_cpu_detect()`.

Control flow: mount/configuration paths enable static keys; scheduler context switch calls `resctrl_arch_sched_in()`, which chooses task-specific or per-CPU default CLOSID/RMID, compares against cached MSR state, and writes `MSR_IA32_PQR_ASSOC` only when values change. Monitoring values are rounded to hardware scale.

State and persistence: per-CPU PQR state caches current/default CLOSID and RMID; task fields store assigned IDs. Resource assignments are runtime kernel state, usually managed through resctrl filesystem policy. Dependencies include MSR writes, static branches, scheduler, `task_struct` CLOSID/RMID fields, and CPU detection fields in `boot_cpu_data`.

Risks: scheduler hot-path overhead, stale cached PQR values, incorrect ID fallback, and wrong scaling for occupancy. Test signals include resctrl mount/unmount, task and CPU group assignment, context-switch MSR tracing, monitoring values, CLOSID/RMID matching, and no-op builds without `CONFIG_X86_CPU_RESCTRL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/resctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/rmwcc.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/rmwcc.h

Purpose: defines macros that perform x86 read-modify-write instructions and return a condition-code result, supporting lock-free and lock fast paths. Important macros include `GEN_UNARY_RMWcc()`, `GEN_BINARY_RMWcc()`, and lower-level `__GEN_RMWcc` forms built around `asm goto`.

Control flow: callers supply an instruction template, memory operand, condition code, and operands; the macro emits inline assembly that branches to labels based on the CPU flags and returns a boolean-like value. State is the target memory operand only.

Dependencies include compiler support for asm goto, x86 condition-code constraints, and users such as qspinlock pending-bit logic. Risks include compiler instrumentation interactions, label use inside statement expressions, operand constraint mistakes, and memory-order assumptions. Test signals include qspinlock builds, objtool/compiler matrix coverage, and lock stress on GCC/Clang variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/rmwcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/rqspinlock.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/rqspinlock.h

Purpose: adapts queued spinlocks for real-time or raw queued spinlock configurations on x86. Important APIs are the architecture include glue and paravirt lock initialization/unlock hooks selected by config.

Control flow: compilation routes lock users to either generic queued spinlock behavior or architecture/paravirt variants. State is the underlying qspinlock word. Dependencies include qspinlock, paravirt spinlocks, and real-time locking configuration. Risks are configuration-specific include mismatches and divergence between raw and paravirt lock semantics. Test signals include RT kernel builds, locktorture, lockdep, and paravirt guest contention tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/rqspinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/runtime-const.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/runtime-const.h

Purpose: provides x86 runtime-constant patching helpers that let selected immediate constants be fixed up after boot while compiling as fast constant loads. Important macros/functions include runtime-constant pointer/shift helpers, symbol declarations, and asm sections that record patch sites.

Control flow: code emits references tagged into special sections; boot/runtime patching later rewrites instruction immediates or displacement fields once the chosen runtime value is known. State is encoded in patch-site metadata and patched text. Dependencies include text patching, linker sections, compiler inline asm formats, and configured runtime-constant users.

Risks: patch-site encoding must match instruction bytes and relocation constraints; wrong runtime constants affect all call sites using the optimized path. Test signals include objdump validation of patch sites, boot-time patch application, KASLR/relocation builds, and functional tests for subsystems using runtime constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/runtime-const.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/seccomp.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/seccomp.h

Purpose: defines x86 seccomp audit architecture constants and syscall argument mappings for native and compat ABIs. Important macros include `SECCOMP_ARCH_NATIVE`, `SECCOMP_ARCH_NATIVE_NR`, `SECCOMP_ARCH_COMPAT`, `SECCOMP_ARCH_COMPAT_NR`, and register-index mappings for syscall arguments.

Control flow: seccomp and BPF syscall filters use these constants to expose syscall numbers and arguments consistently across x86-64, i386, and x32/compat modes. State is per-task seccomp state owned by generic code.

Dependencies include syscall ABI, audit arch values, ptrace register layout, and compat configuration. Risks include wrong argument register mapping causing filters to allow or deny the wrong syscalls, especially in compat/x32 modes. Test signals include seccomp-bpf selftests on native and compat binaries, audit arch checks, and syscall argument filter tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/seccomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sections.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/sections.h

Purpose: extends generic section declarations with x86-specific symbols. Important exports include exception table/special section boundaries and architecture text/data markers used by alternatives, entry code, and memory permissions.

Control flow: boot and patching code use section symbols to locate ranges for initialization, alternatives, exception handling, and permission changes. State is linker-defined address ranges, not mutable runtime data except where sections are freed or permission-adjusted.

Dependencies include `asm-generic/sections.h`, linker scripts, alternatives, text patching, and module/core layout. Risks are symbol mismatches with the linker script and incorrect range checks for executable or freed memory. Test signals include link-time symbol resolution, boot memory freeing, exception table lookup, alternatives patching, and strict kernel text permission checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sections.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/segment.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/segment.h

Purpose: defines x86 segment selector constants, GDT/LDT entry numbers, descriptor privilege levels, user/kernel code/data selectors, TLS slots, per-CPU segment behavior, and helpers for segment arithmetic. It is a fundamental ABI header for entry, ptrace, TLS, compat, and boot code.

Important APIs/macros: GDT entry identifiers, `__KERNEL_CS`, `__KERNEL_DS`, `__USER_CS`, `__USER_DS`, compat selectors, TLS selector helpers, `SEGMENT_RPL_MASK`, `USER_RPL`, and configuration-specific selectors for 32-bit, 64-bit, SYSENTER/SYSCALL, percpu, and FRED-sensitive paths.

Control flow: entry code, task setup, ptrace, TLS setup, and syscall paths load or compare selectors using these constants. Compat and paravirt paths can use alternate user 64-bit selectors. State is primarily CPU descriptor tables and task TLS descriptors declared elsewhere.

Dependencies include UAPI segment definitions, descriptor tables, LDT/TLS code, entry assembly, and syscall ABI. Risks are extremely high because selector values are hard ABI with assembly, userspace signal/ptrace expectations, and CPU privilege checks. Test signals include native and compat syscall entry/exit, TLS set/get, signal return, ptrace segment access, FRED/non-FRED builds, and boot descriptor-table validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/segment.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/serial.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/serial.h

Purpose: declares x86 legacy serial-port defaults and early serial support constants. Important content includes UART base/IRQ defaults and `BASE_BAUD` configuration used by 8250/legacy serial setup.

Control flow: serial core and early console setup consume these constants when probing standard PC COM ports. State is owned by serial drivers and platform resources. Dependencies include legacy ISA I/O port layout and serial driver configuration.

Risks: wrong defaults break early console or legacy serial devices; modern platforms often use firmware-described ports, so this file must remain conservative. Test signals include earlyprintk/earlycon on COM ports, 8250 probe, ISA serial devices, and builds with/without serial support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/serial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/set_memory.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/set_memory.h

Purpose: declares x86 page attribute and memory encryption transition APIs. Important APIs include `set_memory_uc/wc/wb/wp/ro/rw/x/nx()`, array variants, encrypted/decrypted/private/shared transitions, direct-map invalidation/restoration, cache flushing helpers, and CPA initialization functions.

Control flow: callers request attribute changes over page ranges; implementation updates page tables, flushes caches/TLBs as needed, and may alter direct-map aliases. Confidential computing paths call private/shared helpers for SEV-SNP or TDX state transitions.

State and persistence: mutates kernel page tables, direct-map aliases, and encryption/share state; changes persist until reversed or memory is freed. Dependencies include page tables, cache/TLB flushing, CPA code, AMD/Intel confidential-computing backends, and module/text permission management.

Risks: attribute aliasing, missing TLB/cache flushes, W+X exposure, incorrect shared/private conversion, and direct-map inconsistencies. Test signals include rodata/text permission tests, module load/unload, ioremap/cache attribute tests, SEV/TDX shared memory transitions, and debug page-table checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/set_memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/setup.h

Purpose: defines x86 boot/setup constants, memory reservation hooks, architecture setup declarations, and boot parameter plumbing. Important APIs include command-line size constants, `setup_arch()`-adjacent declarations, E820/initrd/ramdisk helpers, `reserve_standard_io_resources()`, early CPU/IO/APIC setup hooks, and architecture-specific resource reservation symbols.

Control flow: early boot parses setup data and boot parameters, reserves low memory and firmware resources, initializes APIC/IO resources, handles initrd placement, and exposes architecture data to later init. State is boot-only command-line/setup data plus runtime resource reservations.

Dependencies include UAPI boot params, E820, firmware setup data, initrd, resource management, and architecture boot code. Risks include command-line truncation, bad memory reservations, initrd overlap, and stale declarations for early boot phases. Test signals include BIOS/EFI boot, initrd loading, `mem=`/setup data options, resource tree checks, and early platform device initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/setup_arch.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/setup_arch.h

Purpose: tiny setup header for architecture setup code inclusion. It acts as a narrow include boundary for setup implementation files.

Control flow, state, and dependencies are minimal; any behavior is in the corresponding setup implementation. Risks are limited to include guard or declaration drift. Test signals are compile coverage of x86 setup code and successful early boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/setup_arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/setup_data.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/setup_data.h

Purpose: extends UAPI setup-data records with kernel-only x86 boot payload structures. Important types are `pci_setup_rom` for PCI option ROM handoff and `efi_setup_data` for EFI setup information.

Control flow: early boot walks the setup_data linked list from boot params and interprets records by type, including PCI ROM and EFI data. State is bootloader-provided memory consumed during boot and not persistent after initialization.

Dependencies include UAPI setup_data layout, PCI, EFI, and bootloader contracts. Risks are packed layout/width mismatches with bootloaders and wrong physical-address handling. Test signals include EFI boots, kexec with setup_data, PCI ROM handoff tests, and boot parameter parser coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/setup_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sev-common.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/sev-common.h

Purpose: defines shared AMD SEV/SEV-ES/SNP constants, GHCB MSR protocol values, VMGEXIT exit codes, SNP page-state-change operations, termination reasons, and hypervisor feature bits used by both guest and host code.

Important APIs/macros: GHCB MSR info/error encodings, `GHCB_MSR_*` requests/responses, `SVM_VMGEXIT_*` exit codes, page state change op values, SNP feature and termination constants, and helper masks/shifts for protocol fields.

Control flow: SEV-ES/SNP guest code encodes requests into GHCB MSR or GHCB shared pages, issues VMGEXIT, and decodes hypervisor responses with these constants. Host/KVM paths validate and synthesize matching values. State lives in GHCB pages/MSRs and SNP firmware-managed metadata.

Dependencies include AMD GHCB/SNP firmware ABI, SVM definitions, confidential computing core, and KVM/guest exception handling. Risks are ABI mismatches with firmware/hypervisor, wrong bit shifts, and ambiguous error handling during early boot. Test signals include SEV-ES boot, SNP guest requests, GHCB MSR fallback, page-state changes, KVM SEV tests, and termination/error-path validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sev-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sev.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/sev.h

Purpose: declares AMD SEV-ES/SNP guest and host support interfaces, firmware message formats, secrets-page structures, SVSM protocol structures, RMP/PVALIDATE helpers, GHCB operations, memory private/shared transitions, secure TSC support, and KVM RMP-management hooks.

Important APIs/types/functions: `es_result`, `es_fault_info`, `es_em_ctxt`, `cc_blob_sev_info`, SNP CPUID table structures, `rmp_state`, SNP guest message/header/request/response structures, `snp_secrets_page`, `snp_msg_desc`, SVSM call/attestation/PVALIDATE structures, `pte_enc_desc`, `rmpadjust()`, `pvalidate()`, `setup_ghcb()`, SNP memory state APIs, `snp_send_guest_request()`, secure TSC init, `sev_es_ghcb_hv_call()`, `snp_cpuid()`, `sev_es_terminate()`, and KVM RMP helpers such as `rmp_make_private()` and `rmp_make_shared()`.

Control flow: early boot discovers SEV/SNP state, maps secrets/CPUID/GHCB resources, negotiates GHCB protocol, handles #VC exceptions by emulating or forwarding operations through GHCB/VMGEXIT, validates/accepts memory, and later services guest firmware requests using encrypted private buffers and shared GHCB/message pages. KVM host code uses RMP helpers to assign or release pages for SNP guests.

State and persistence: runtime state includes GHCB pages, boot GHCB pointer, negotiated GHCB version, SNP VMPL, secrets-page keys and message sequence numbers, secure TSC data, RMP entries, private/shared page-table encryption state, and SVSM calling areas. The data is memory-resident but security-sensitive and tied to firmware/hypervisor state.

Dependencies and integration points: depends on `sev-common.h`, SVM/GHCB layouts, confidential-computing detection, set-memory APIs, page tables, EFI/boot params, AES-GCM, KVM AMD SEV, exception entry, kexec, and firmware ABI. Risks are high: sequence-number/key misuse can break SNP request security; private/shared transitions can corrupt memory; `pvalidate`/`rmpadjust` failure handling affects page ownership; GHCB protocol errors can terminate guests. Test signals include SEV, SEV-ES, and SNP guest boot, #VC emulation, SNP guest requests/attestation, secure TSC, SVSM calls, kexec, KVM SNP page assignment, and non-AMD_MEM_ENCRYPT stub builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sgx.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/sgx.h

Purpose: defines Intel SGX architectural structures and Linux SGX helper declarations. Important definitions include SGX CPUID leaves, ENCLS function numbers, ENCLS fault flag, return codes, `sgx_miscselect`, SGX attributes and masks, `sgx_secs`, `sgx_tcs`, `sgx_pageinfo`, page/secinfo types, `sgx_secinfo`, `sgx_pcmd`, `sgx_sigstruct`, KVM virtualization hooks, and `sgx_set_attribute()`.

Control flow: SGX driver and KVM code use these layouts to create enclaves, add/extend pages, initialize signatures, swap EPC pages, virtualize ECREATE/EINIT, and enforce allowed attributes. ENCLS return/fault encoding is normalized with `SGX_ENCLS_FAULT_FLAG` so callers can distinguish SGX positive status, CPU faults, and Linux errors.

State and persistence: SGX enclave state resides in EPC pages and metadata described by SECS/TCS/SECINFO/PCMD; swapped pages carry PCMD integrity data in regular memory. The header itself declares ABI layouts rather than owning state.

Dependencies include SGX CPU architecture, KVM SGX virtualization, user ioctl structures, EPC management, RSA/signature validation, and xsave attribute masks. Risks include packed layout drift, reserved-bit validation errors, wrong fault-code mapping, and privilege mistakes around provisioning/token keys. Test signals include SGX selftests, enclave create/init/run, EPC reclaim/load, KVM SGX ECREATE/EINIT, invalid attribute masks, and ENCLS fault-path coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sgx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/shared/io.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/shared/io.h

Purpose: provides shared x86 boot/compressed/kernel I/O primitives for port I/O and memory-mapped reads/writes. Important APIs are small inline `inb/outb` and `readb/readw/readl/readq`/`write*` style helpers depending on build context.

Control flow: early boot and decompressor code use direct inline assembly or volatile memory accesses before the full kernel I/O abstraction is available. State is the addressed device or MMIO register. Dependencies include x86 I/O port instructions and shared include use from boot code.

Risks: these helpers can run before normal fault handling or mapping infrastructure, so addresses and ordering must be correct. Test signals include compressed kernel boot, early console/I/O use, and builds for 32/64-bit boot environments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/shared/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/shared/msr.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/shared/msr.h

Purpose: supplies shared MSR read/write helpers usable by early boot/compressed code. Important APIs include low-level `rdmsr`/`wrmsr`-style inline helpers with split 32-bit halves or 64-bit values.

Control flow: early architecture code reads or writes model-specific registers before full kernel helpers are available. State is CPU MSR state. Dependencies include x86 `rdmsr`/`wrmsr` instruction semantics and caller-provided MSR numbers.

Risks: invalid MSR accesses can fault in fragile early contexts; write ordering and feature checks must be handled by callers. Test signals include early CPU feature setup, compressed boot, SEV/TDX early paths using MSRs, and fault-free boot on CPUs lacking optional MSRs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/shared/msr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/shared/tdx.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/shared/tdx.h

Purpose: defines Intel TDX guest-module and hypercall constants shared by the kernel, decompressor, and early boot paths. Important definitions include TDX CPUID identity, TDG leaf numbers, TD attributes, shared bit handling, TDVMCALL register masks, hypercall status codes, MMIO/port I/O hypercall subfunctions, and `tdx_module_args`.

Control flow: TDX guests use these constants to issue `TDCALL`/`TDVMCALL` operations for CPUID, VE info, memory acceptance, reports, MMIO, port I/O, and hypervisor services. State is carried in register arguments and TDX module metadata, not owned by this header.

Dependencies include TDX module ABI, confidential-computing detection, #VE handling, boot decompressor code, and shared register calling conventions. Risks include wrong register masks, hypercall leaf values, or shared-bit calculations causing boot failure or data exposure. Test signals include TDX guest boot, #VE MMIO/PIO handling, memory acceptance, TDREPORT, CPUID identity detection, and compressed-kernel TDX paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/shared/tdx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/shmparam.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/shmparam.h

Purpose: defines x86 System V shared-memory alignment. Important macro is `SHMLBA`, typically tied to page size.

Control flow and state: generic SysV SHM code uses the alignment when attaching shared memory; the header has no runtime state. Dependencies are page size and generic IPC memory management. Risks are ABI-visible alignment changes affecting old applications. Test signals include SysV SHM attach/detach tests and compat ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/shmparam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/shstk.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/shstk.h

Purpose: declares x86 user shadow stack state and control hooks for Intel CET. Important type is `thread_shstk`; important APIs include `shstk_setup()`, `shstk_alloc_thread_stack()`, `shstk_free()`, `shstk_disable()`, `reset_thread_features()`, and arch-prctl feature locking helpers, with stubs when shadow stacks are disabled.

Control flow: exec/thread creation allocates and initializes user shadow stacks; arch-prctl and signal paths enable, disable, or lock features; exit/exec frees state. State is per-thread shadow-stack address/size and feature masks in `thread_struct`.

Dependencies include CET CPU features, memory management, arch-prctl, signal delivery, and `thread_struct` feature fields. Risks include leaking shadow-stack mappings, wrong feature-lock semantics, signal restore mismatches, and ABI regressions. Test signals include CET/shstk selftests, clone/exec/exit, arch_prctl enable/disable/lock, signal delivery, and non-CET stub builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/shstk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/sigcontext.h

Purpose: exposes x86 signal-context UAPI definitions to kernel users. It primarily includes `uapi/asm/sigcontext.h`.

Control flow and state: signal delivery and return code use the UAPI structures to save/restore user-visible register and xstate context; this wrapper owns no state. Dependencies include the stable UAPI signal ABI and FPU/xstate layout. Risks are ABI breakage if the included definitions are changed incompatibly. Test signals include signal frame selftests, rt_sigreturn, FPU/xstate signal preservation, and compat signal handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sigframe.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/sigframe.h

Purpose: declares internal x86 signal-frame layouts and helpers for native and compat signal delivery. Important types include signal frame structures for rt and legacy frames, embedded `ucontext`, siginfo, FPU frame placement, and optional compat variants.

Control flow: signal setup code builds these frames on the user stack, stores saved `pt_regs`, signal mask, siginfo/ucontext, and FPU/xstate frame, then arranges user return through sigreturn trampolines. Sigreturn reads the same layout to restore state.

State and persistence: frames are transient user-stack ABI data but persist until user signal handlers return. Dependencies include UAPI signal context, FPU/xstate, compat ABI, ptrace-visible regs, and altstack handling. Risks include stack alignment, frame-size miscalculation, user memory faults, and ABI drift. Test signals include signal delivery/return, altstack, SA_SIGINFO, 32-bit compat signals, xstate preservation, and malformed sigreturn tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sigframe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sighandling.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/sighandling.h

Purpose: declares x86 signal handling entry points and helpers. Important APIs include `do_signal()`, `do_notify_resume()`, signal setup/restore helpers, and architecture-specific fault-to-signal glue declarations.

Control flow: return-to-user paths call notification/signal handling when thread flags request work; signal setup builds frames and modifies `pt_regs`, while sigreturn validates and restores user state. State is task signal state plus transient user frames.

Dependencies include `pt_regs`, generic signal code, thread flags, FPU restore, and syscall restart machinery. Risks include incorrect restart state, missed user-return work, or unsafe register restoration. Test signals include signal stress, syscall restart, ptrace-signal interactions, compat signals, and return-to-user work flag tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sighandling.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/signal.h

Purpose: provides x86 signal ABI glue, signal stack definitions, and architecture overrides layered on top of UAPI/generic signal headers. Important content includes signal type aliases, `__ARCH_HAS_SA_RESTORER`, and inclusion boundaries for kernel versus userspace.

Control flow: generic signal code uses these definitions to interpret user sigaction structures and restorer behavior on x86. State lives in task signal handlers and user signal frames. Dependencies include UAPI signal numbers, generic signal implementation, and x86 restorer ABI.

Risks: signal ABI is stable userspace contract; changing restorer or stack definitions can break libc and old binaries. Test signals include POSIX signal tests, sigaction restorer behavior, compat signal ABI, and libc signal trampoline compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/simd.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/simd.h

Purpose: declares x86 SIMD/FPU-in-kernel availability helpers. Important APIs are `may_use_simd()` and related include glue for code deciding whether vector instructions are safe in kernel context.

Control flow: crypto and optimized routines call these helpers before using SIMD registers; implementation considers preemption, interrupt context, and FPU ownership. State is current CPU/task FPU state managed elsewhere. Dependencies include FPU state management and preemption/context rules.

Risks: using SIMD when not allowed corrupts user FPU state or violates interrupt constraints; being too conservative hurts performance. Test signals include crypto SIMD selftests, preempt/IRQ context checks, KVM/FPU interactions, and kernel_fpu_begin/end validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/simd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/smap.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/smap.h

Purpose: defines Supervisor Mode Access Prevention helpers for toggling user-memory access from kernel mode. Important macros/functions include `ASM_STAC`, `ASM_CLAC`, `stac()`, `clac()`, `__uaccess_begin()`, `__uaccess_end()`, and masked user-access helpers depending on config and CPU feature.

Control flow: uaccess code opens a small window with STAC before touching user memory and closes it with CLAC afterward. Alternative patching removes or changes instructions when SMAP is absent. State is the AC flag in RFLAGS and CPU feature alternatives.

Dependencies include CPU feature detection, alternatives, uaccess routines, exception entry, and objtool/asm annotations. Risks include leaving AC set, missing STAC before user access, using helpers in NMI/entry contexts incorrectly, and mismatched alternatives. Test signals include hardened usercopy, SMAP fault tests, uaccess selftests, fault injection, and objtool validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/smap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/smp.h

Purpose: declares x86 SMP topology maps, CPU startup/shutdown operations, IPI helpers, cache writeback helpers, and boot-control flags. Important APIs/types include per-CPU sibling/core/die/cache masks, early APIC/ACPI IDs, `struct smp_ops`, native SMP callbacks, stop/reschedule/call-function IPI wrappers, CPU hotplug functions, `raw_smp_processor_id()`, shared-cache mask helpers, `smpboot_control`, and startup flags.

Control flow: generic SMP and hotplug code dispatch through `smp_ops` to prepare CPUs, kick APs, send IPIs, disable/die CPUs, and enter dead states. Cache writeback helpers run WBINVD/WBNOINVD locally or on masks. !SMP builds collapse many helpers to local operations.

State and persistence: per-CPU topology masks and APIC/ACPI IDs describe runtime CPU layout; boot-control flags coordinate AP startup. Dependencies include cpumasks, APIC, CPU hotplug, scheduler IPIs, topology discovery, and cache flush instructions.

Risks: wrong topology masks affect scheduler/cache locality; IPI failures break rescheduling and TLB shootdowns; CPU hotplug races are severe. Test signals include SMP boot, parallel AP startup, CPU online/offline, scheduler IPI tests, cache flush operations, topology sysfs, and UP build stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/softirq_stack.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/softirq_stack.h

Purpose: declares x86 softirq stack handling. Important API is the architecture hook for running softirq work on an alternate stack when configured.

Control flow: interrupt/softirq code switches to a per-CPU softirq stack before executing softirq handlers to avoid exhausting task stacks. State is per-CPU softirq stack pointers declared elsewhere. Dependencies include interrupt entry, per-CPU stacks, and generic softirq code.

Risks: stack switching bugs corrupt task or IRQ stacks; nested softirq/interrupt handling must be controlled. Test signals include network/block softirq stress, IRQ stack overflow checks, lockdep/stack traces, and 32-bit stack configuration builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/softirq_stack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sparsemem.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/sparsemem.h

Purpose: defines x86 sparsemem section sizing, physical address limits, and memory-model constants. Important macros include section size bits and maximum physical memory bits for 32/64-bit and configuration-specific variants.

Control flow: memory initialization uses these constants to size sparsemem sections and validate PFN ranges. State is memory model metadata owned by generic mm. Dependencies include page size, physical address width, NUMA, memory hotplug, and Kconfig memory model.

Risks: wrong limits can hide RAM, overrun mem_section arrays, or break hotplug. Test signals include large-memory boot, NUMA, memory hotplug, sparsemem/vmemmap initialization, and 32-bit PAE/non-PAE builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sparsemem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/spec-ctrl.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/spec-ctrl.h

Purpose: declares x86 speculative-execution control helpers and state used for Spectre/MDS/SSB/IBRS-style mitigations. Important APIs include speculation MSR update helpers, `x86_spec_ctrl_*` state declarations, and entry/exit or context-switch mitigation hooks.

Control flow: CPU feature setup initializes mitigation MSR defaults; context-switch and entry paths update SPEC_CTRL or related MSRs based on task flags and CPU vulnerability state. State includes per-CPU/global shadow values for speculation-control MSRs and task thread flags.

Dependencies include MSR access, CPU bug flags, static keys, thread_info flags, entry code, KVM, and mitigation command-line handling. Risks include missing barriers, stale MSR shadow state, high context-switch overhead, and security regressions. Test signals include Spectre/MDS mitigation selftests, sysfs vulnerability output, context-switch tracing, KVM guest/host tests, and CPU vendor matrix coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/spec-ctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/special_insns.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/special_insns.h

Purpose: provides inline wrappers for privileged and special x86 instructions. Important APIs include CR0/CR2/CR3/CR4 read/write helpers, native CR variants, `wbinvd()`, `clflush*`, `stts()/clts()`, `native_halt()`, `safe_halt()`, `rdpkru()/wrpkru()`, `serialize()`, `mwait/monitor`, `tile_release()`, and related feature-conditional helpers.

Control flow: low-level kernel code uses wrappers to manipulate control registers, cache state, protection keys, halt/mwait idle, and serialization. Alternative patching or paravirt can replace some operations; callers handle feature checks.

State and persistence: mutates CPU control registers, TLB/cache state, PKRU, TS bit, and idle state. Dependencies include processor flags, barriers, paravirt, CPU features, and asm constraints. Risks are severe: wrong control-register writes can crash the CPU; missing memory clobbers or ordering can corrupt page-table/security state. Test signals include boot, CPU hotplug, idle, cache flush, PKU selftests, CR4 shadow tests, and objtool/compiler validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/special_insns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/spinlock.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/spinlock.h

Purpose: selects x86 spinlock implementations and architecture hooks. It pulls in queued spinlocks, queued rwlocks, and paravirt variants as configured.

Control flow: generic locking users compile through this header into qspinlock/qrwlock primitives. State is lock object memory. Dependencies include qspinlock, qrwlock, paravirt, and architecture atomic operations.

Risks include config-specific include ordering, lock primitive ABI mismatch, and paravirt locking regressions. Test signals include locktorture, lockdep, SMP stress, RT builds where applicable, and paravirt guest locking tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/spinlock_types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/spinlock_types.h

Purpose: exposes x86 spinlock type definitions by including queued spinlock and queued rwlock type headers. No executable logic lives here.

State is embedded in lock objects declared by kernel users. Dependencies are generic qspinlock/qrwlock type layouts. Risks are type-layout changes affecting static initializers or lockdep. Test signals include compile coverage, static lock initializers, lockdep, and SMP locking tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/spinlock_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/stackprotector.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/stackprotector.h

Purpose: defines x86 stack-canary setup for stack protector support. Important APIs include canary initialization helpers that seed per-task/per-CPU canary storage and write the value into the architecture location used by compiler-generated checks.

Control flow: boot and fork paths initialize canary values before protected C code depends on them; 64-bit typically stores canaries in per-CPU/GS-accessible areas, while 32-bit has segment-specific handling. State is the stack canary for current CPU/task.

Dependencies include random canary generation, per-CPU areas, task/thread setup, compiler stack protector ABI, and segment base layout. Risks include predictable canaries, writing the wrong per-CPU slot, or missing initialization on secondary CPUs/tasks. Test signals include stack protector boot tests, forced stack-smash detection, SMP bring-up, fork/exec, and compiler configuration matrix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/stackprotector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/stacktrace.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/stacktrace.h

Purpose: declares x86 stacktrace, unwind, and stack-type helpers. Important APIs/types include stack type enums, stack metadata, `get_stack_info()`, `unwind_start()`, `unwind_next_frame()`-adjacent declarations, reliable stacktrace helpers, and checks for entry/exception/IRQ stacks.

Control flow: oops, perf, ftrace, livepatch, lockdep, and proc stack readers classify an address into task, IRQ, exception, entry, or unknown stacks, then unwind frames using ORC/frame-pointer/guess unwinders. State is stack memory and unwinder cursor state.

Dependencies include thread/IRQ stack layout, ORC unwinder, frame pointers, entry stacks, per-CPU stacks, and KASAN/KMSAN constraints. Risks include unreliable unwinds, stack-boundary misclassification, false livepatch safety, and unsafe reads from corrupted stacks. Test signals include oops backtraces, perf callchains, livepatch reliable stacktrace tests, NMI/IRQ stack unwinds, and frame-pointer/ORC build variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/stacktrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/static_call.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/static_call.h

Purpose: implements x86 architecture support for static calls, which patch direct call/jump sites for low-overhead indirect-call replacement. Important macros/functions include static-call trampoline/site declarations, architecture patch constants, inline/static call transformations, and text patching integration.

Control flow: static call users compile call sites and trampolines; registration/update paths patch instruction bytes to point at the selected target or return path. State is text patch-site metadata and patched kernel code.

Dependencies include jump labels, objtool, text patching, alternatives, module loading, and instruction encoding for CALL/JMP/RET. Risks include patching wrong instruction lengths, module unload races, CFI/IBT interaction, and stale target pointers. Test signals include static_call selftests, tracepoint/perf users, module load/unload with static calls, objtool validation, and IBT/CFI builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/static_call.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/string.h

Purpose: selects x86 optimized string/memory operation declarations for 32-bit or 64-bit builds. It includes `string_32.h` or `string_64.h` and supplies architecture `memcpy/memset/memmove` feature markers.

Control flow: generic libc-like kernel callers resolve to x86 optimized routines or sanitizer-safe fallbacks depending on config. State is only caller-provided memory. Dependencies include architecture string assembly, KMSAN/KASAN/fortify constraints, and compiler builtins.

Risks include sanitizer bypass, overlap semantics for memmove, and ABI conflicts with compiler intrinsics. Test signals include lib/string tests, KASAN/KMSAN builds, fortify tests, boot-time memory operations, and 32/64-bit build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/string_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/string_32.h

Purpose: declares and implements 32-bit x86 optimized string/memory helpers. Important APIs include `memcpy`, `memmove`, `memset`, `strncpy`, `strnlen`, `memcmp`, and inline/extern variants selected by compiler and config.

Control flow: callers use architecture routines with inline assembly or external optimized implementations for byte/word movement and comparison. State is caller memory. Dependencies include i386 calling conventions, compiler constraints, sanitizer/fortify config, and generic string fallback behavior.

Risks: incorrect constraints or overlap behavior can corrupt memory; inline asm must preserve registers and flags as expected. Test signals include 32-bit kernel boot, lib/string tests, KASAN/KMSAN/fortify, overlapping memmove cases, and early boot memory initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/string_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/string_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/string_64.h

Purpose: declares x86-64 optimized memory/string functions and inline memset-size helpers. Important APIs include `memcpy`, `__memcpy`, `memset`, `__memset`, `memset16/32/64`, `memmove`, `memcmp`, `strcmp`, and `memcpy_flushcache()` for persistent-memory/cache-flush users.

Control flow: generic callers use optimized external assembly/C routines; inline `memset16/32/64` use `rep stos*`; flushcache copies call cache-flushing implementations when `CONFIG_ARCH_HAS_UACCESS_FLUSHCACHE` is enabled. KMSAN can redirect to sanitizer-specific string helpers.

State and persistence: mutates caller buffers and may flush destination cachelines for persistence-domain users. Dependencies include jump labels, sanitizer config, fortify, persistent-memory copy support, and x86-64 string instruction semantics. Risks include sanitizer visibility, non-temporal/persistent copy ordering, and overlap handling. Test signals include lib/string, pmem/DAX copy tests, KMSAN/KASAN, fortify, and memset width-specific tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/string_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/suspend.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/suspend.h

Purpose: selects x86 suspend state definitions for 32-bit or 64-bit builds. It includes `suspend_32.h` or `suspend_64.h` and exposes common suspend/resume interfaces.

Control flow: hibernation and ACPI suspend save CPU state using architecture-specific structures, then restore it on resume. State is saved processor/register context. Dependencies include ACPI sleep, hibernation, CPU state save/restore assembly, and page-table state.

Risks include incomplete register restoration, wrong CR/segment state, and resume failures after CPU feature changes. Test signals include suspend-to-RAM, hibernation, CPU hotplug plus suspend, and 32/64-bit resume paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/suspend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/suspend_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/suspend_32.h

Purpose: defines 32-bit x86 saved CPU context for suspend/hibernate. Important type is the architecture saved-context structure containing control registers, segment descriptors/selectors, GDT/IDT, LDT/TR, and general resume state.

Control flow: suspend code saves processor state before low-power transition or image creation and restores it during resume. State is memory-resident saved CPU context. Dependencies include 32-bit descriptor tables, paging, ACPI/hibernate assembly, and CPU feature restoration.

Risks include stale descriptor pointers, CR3/CR4 mismatches, and resume crashes on CPUs with changed state. Test signals include i386 suspend-to-RAM/hibernate, resume after CPU hotplug, and descriptor-table validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/suspend_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/suspend_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/suspend_64.h

Purpose: defines 64-bit x86 saved CPU context for suspend and hibernation. Important fields include saved CR registers, MSRs such as EFER/FS/GS/KERNEL_GS, descriptor table pointers, segment selectors, and restore entry data.

Control flow: suspend saves long-mode CPU state, switches through low-level resume code, restores control registers/MSRs/descriptors, and resumes normal kernel execution. State is saved per-CPU processor context in memory.

Dependencies include long-mode paging, MSR helpers, percpu GS base, ACPI sleep, hibernate image restore, and CPU feature reinitialization. Risks include GS/FS base corruption, EFER/CR4 mismatch, broken KASLR/percpu assumptions, and resume failure under virtualization. Test signals include x86-64 S3, hibernation, FSGSBASE/CET/PCID configurations, and resume on multiple CPU vendors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/suspend_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/svm.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/svm.h

Purpose: defines AMD SVM virtualization hardware structures, intercept constants, VMCB/GHCB layouts, AVIC fields, SEV feature bits, event injection encodings, and GHCB accessors used primarily by KVM and SEV guest code.

Important APIs/types: intercept enumerations, `vmcb_control_area`, TLB-control and interrupt-control bits, AVIC logical/physical table masks, SEV feature bits, `vmcb_seg`, `vmcb_save_area`, `sev_es_save_area`, `ghcb_save_area`, `ghcb`, `vmcb`, size/offset build checks, selector/event injection masks, and generated `ghcb_*` valid/get/set accessors.

Control flow: KVM programs VMCB control/save areas before VMRUN, handles exits by reading `exit_code/info`, injects events with encoded fields, manages AVIC acceleration, and uses GHCB pages for SEV-ES/SNP guest-host communication. Guest #VC paths use accessors to mark GHCB fields valid before VMGEXIT.

State and persistence: VMCB/GHCB pages are live virtualization state shared with CPU hardware or hypervisor; AVIC tables and SEV VMSA pages persist for the lifetime of vCPUs. Dependencies include AMD APM layout, KVM uapi, Hyper-V enlightenments, SEV/SNP ABI, and bitops.

Risks: packed layout and offsets are hardware ABI; any drift breaks virtualization. Event injection and intercept bits are security-critical. GHCB valid bitmap misuse can leak or ignore state. Test signals include KVM SVM unit tests, nested virtualization, AVIC/x2AVIC, SEV-ES/SNP guests, VMCB size build checks, and VM exit/injection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/svm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/switch_to.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/switch_to.h

Purpose: declares x86 context-switch structures and helpers. Important APIs include inactive task frame layout, `switch_to()` macro/glue, `__switch_to_asm`, `__switch_to()`, `update_task_stack()`, and fork/thread stack setup helpers.

Control flow: scheduler saves callee-preserved registers in an inactive frame, switches stacks in assembly, then runs C-level `__switch_to()` to update FPU, segment, debug, speculation, TSS, and per-task state. Fork setup creates an initial inactive frame for new tasks.

State and persistence: per-task kernel stack frame and `thread_struct` fields persist across scheduling. Dependencies include processor/thread state, entry stack layout, FPU, TLS, paravirt, speculation controls, and objtool unwind hints. Risks include stack-frame layout mismatch with assembly, lost callee-saved registers, and missed per-task hardware updates. Test signals include context-switch stress, fork/clone, ptrace debug registers, TLS/FSGS tests, and objtool unwind validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/switch_to.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sync_bitops.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/sync_bitops.h

Purpose: provides fully synchronized x86 bit operations for users that require locked atomic bit manipulation. Important APIs include `sync_set_bit()`, `sync_clear_bit()`, `sync_change_bit()`, `sync_test_and_set_bit()`, `sync_test_and_clear_bit()`, `sync_test_and_change_bit()`, and `sync_test_bit()`.

Control flow: wrappers emit locked `bts/btr/btc` operations or equivalent atomic bitops, returning previous bit values where needed. State is the target bitmap word. Dependencies include x86 atomic instruction semantics and generic bitops expectations.

Risks include overusing heavier synchronized operations in hot paths, wrong memory-order assumptions, and bit-number/address constraints. Test signals include atomic bitop selftests, SMP races, lock bitmap users, and compiler constraint builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sync_bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sync_core.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/sync_core.h

Purpose: defines x86 instruction stream/core synchronization helpers used after text patching, memory permission changes, and control-flow-sensitive updates. Important APIs include `sync_core()`, `iret_to_self()`, `sync_core_before_usermode()`, and flags controlling return-to-user synchronization.

Control flow: callers force a serializing event, often via CPUID or IRET-to-self, so later instruction fetch observes patched code or updated permissions. Return-to-user paths can defer synchronization until safe. State includes CPU pipeline/front-end state and per-thread sync flags.

Dependencies include special instructions, entry/IRET mechanics, thread flags, alternatives/text patching, and speculation/IBT-sensitive code. Risks include executing stale patched instructions, excessive serialization overhead, and unsafe use in noinstr/entry contexts. Test signals include live text patching, ftrace/kprobes/static calls, module alternatives, and SMP patch synchronization tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sync_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/syscall.h

Purpose: supplies x86 syscall inspection and mutation helpers for generic syscall tracing, seccomp, audit, ptrace, and restart logic. Important APIs include `syscall_get_nr()`, `syscall_rollback()`, `syscall_get_error()`, `syscall_get_return_value()`, `syscall_set_return_value()`, `syscall_get_arguments()`, `syscall_get_arch()`, and syscall-user-dispatch hooks.

Control flow: tracing/seccomp/audit code reads syscall number and argument registers from `pt_regs`; ptrace and restart paths can roll back or replace return values; ABI detection distinguishes x86-64, i386 compat, and x32-style syscall state.

State and persistence: operates on transient syscall `pt_regs` and thread status flags. Dependencies include register ABI, `thread_info` compat status, audit arch constants, seccomp, ptrace, and syscall table conventions. Risks include wrong register mapping, compat ABI confusion, and bad rollback corrupting restarted syscalls. Test signals include strace/ptrace, seccomp, audit, syscall restart, x32/ia32 emulation, and syscall user dispatch tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/syscall_wrapper.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/syscall_wrapper.h

Purpose: generates x86 syscall wrapper functions that decode `pt_regs`, invoke typed syscall implementations, and support native and compat syscall tables. Important macros include `__SYSCALL_DEFINEx`, `COMPAT_SYSCALL_DEFINEx`, register argument extraction macros, aliasing helpers, and conditional wrappers for `CONFIG_ARCH_HAS_SYSCALL_WRAPPER`.

Control flow: entry code dispatches to generated wrapper symbols; wrappers pull arguments from ABI-specific registers, call `__do_sys_*` functions, then return long results. Compat wrappers convert 32-bit argument types as required.

State and persistence: no persistent state; wrappers operate on syscall regs and user arguments. Dependencies include syscall metadata generation, ptrace register layout, compat types, asmlinkage conventions, and tracing/syscall table build logic. Risks include wrong argument order/sign-extension, symbol alias mismatches, and tracing metadata drift. Test signals include syscall ABI selftests, compat syscalls, strace argument decoding, generated table builds, and allnoconfig/compat configuration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/syscall_wrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/syscalls.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/syscalls.h

Purpose: declares x86-specific syscall entry points not covered solely by generic syscall declarations. Important declarations include architecture syscalls such as `sys_ioperm`, `sys_iopl`, and related compat/native variants depending on config.

Control flow: syscall tables reference these symbols; wrappers or entry dispatch call them with decoded arguments. State changes are syscall-specific, commonly task I/O permission bitmap or IOPL emulation state. Dependencies include syscall table generation, processor I/O permission support, and compat ABI.

Risks include missing declarations causing table/build failures and ABI mismatch for x86-specific syscalls. Test signals include ioperm/iopl tests, syscall table link checks, compat syscall invocation, and seccomp/audit naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/syscalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/tdx.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/tdx.h

Purpose: declares Intel TDX guest and host kernel interfaces beyond the shared ABI constants. Important APIs include TDX detection/init helpers, #VE handling, TDCALL/TDVMCALL wrappers, memory accept/private/shared helpers, KVM/host TDX module calls, and stubs for non-TDX builds.

Control flow: early boot detects TDX, accepts memory, configures #VE handling, and routes MMIO/PIO or hypervisor services through TDVMCALL. Host/KVM code initializes and invokes the TDX module for TD lifecycle operations when configured.

State and persistence: TDX guest state lives in TDX module/SEAM state, accepted-memory bitmap/state, and per-CPU exception handling context; host state includes module metadata and TD resources. Dependencies include `shared/tdx.h`, confidential-computing framework, set-memory, exception entry, KVM TDX code, and firmware/module ABI.

Risks: unaccepted memory use, wrong shared/private transitions, #VE recursion, hypercall ABI mismatch, and host module call failure handling. Test signals include TDX guest boot, memory acceptance, MMIO #VE tests, TDREPORT/hypercalls, KVM TDX initialization, and non-TDX stub builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/tdx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/tdx_global_metadata.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/tdx_global_metadata.h

Purpose: auto-generated header describing TDX global system-info metadata returned by the TDX module. Important types include `tdx_sys_info_version`, `tdx_sys_info_features`, `tdx_sys_info_tdmr`, `tdx_sys_info_td_ctrl`, `tdx_sys_info_td_conf`, and aggregate `tdx_sys_info`.

Control flow: TDX host initialization reads module metadata into these structures to size TDMRs, validate supported features, and configure TD controls. State is module-provided capability data cached by host code.

Dependencies include TDX module ABI and host KVM TDX setup. Risks include generated layout drift versus module metadata fields, causing invalid TD configuration. Test signals include TDX module initialization, metadata parsing tests, feature gating, and build checks when regenerating the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/tdx_global_metadata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/text-patching.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/text-patching.h

Purpose: declares and implements x86 runtime text patching primitives and instruction emulation helpers. Important APIs include `text_poke()`, `text_poke_copy()`, `text_poke_kgdb()`, `text_poke_bp()`, `smp_text_poke_*()`, opcode size constants, `text_opcode_size()`, `text_gen_insn()`, `__text_gen_insn()`, and INT3 emulation helpers for jmp/call/ret/jcc.

Control flow: patching code writes new instruction bytes using safe text mappings or breakpoint-assisted patching, synchronizes CPUs, and uses INT3 handlers to emulate instructions while patching is in progress. Instruction generators compute relative displacements for CALL/JMP/JMP8 and verify range constraints.

State and persistence: mutates kernel text and uses `text_poke_mm`/temporary mapping addresses after boot. Dependencies include alternatives, static calls, ftrace/kprobes, KGDB, SMP synchronization, `pt_regs`, instruction encoding, and memory permissions.

Risks: patching live text is high risk: wrong displacement, instruction length, CPU synchronization, or INT3 emulation corrupts control flow. Test signals include alternatives, ftrace, kprobes, static calls, jump labels, livepatch-style stress, SMP patch batching, KGDB breakpoints, and objtool validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/text-patching.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/thermal.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/thermal.h

Purpose: declares x86 thermal interrupt/vector initialization hooks. Important APIs are `therm_lvt_init()`, `intel_init_thermal()`, `x86_thermal_enabled()`, and `intel_thermal_interrupt()` when `CONFIG_X86_THERMAL_VECTOR` is enabled, with stubs otherwise.

Control flow: CPU initialization sets up local APIC thermal vector handling and Intel CPU thermal support; interrupts dispatch to the thermal handler. State is CPU thermal/APIC configuration owned by implementation. Dependencies include CPU detection, APIC LVT thermal vector, and thermal/interrupt subsystems.

Risks include missing thermal interrupts, false enablement on unsupported CPUs, and build issues for stubbed `x86_thermal_enabled()` users. Test signals include thermal vector initialization, simulated thermal interrupts, CPU hotplug, and no-thermal-vector builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/thermal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/thread_info.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/thread_info.h

Purpose: defines low-level x86 per-thread flags/status and kernel stack padding used by entry, scheduler, syscall, and context-switch code. Important content includes `TOP_OF_KERNEL_STACK_PADDING`, `struct thread_info`, `INIT_THREAD_INFO`, supported TIF declarations, x86-specific TIF bits, `_TIF_WORK_CTXSW*` masks, `STACK_WARN`, `arch_within_stack_frames()`, `TS_COMPAT`, `TS_I386_REGS_POKED`, and `in_ia32_syscall()`.

Control flow: entry and scheduler code inspect TIF masks to decide return-to-user work, speculation updates, FPU loading, I/O bitmap switching, CPUID/TSC restrictions, and single/block stepping. Stack validation uses frame pointers to check whether copies stay within one stack frame. Compat syscall code marks 32-bit syscall state in `status`.

State and persistence: `thread_info` lives with each task and stores flags, syscall work flags, synchronous status, and current CPU on SMP. Dependencies include generic TIF infrastructure, page/thread size, entry assembly offsets, frame pointers, compat syscall code, and stackleak/usercopy validation.

Risks: bit assignments and masks are entry ABI; wrong padding breaks `pt_regs` placement on 32-bit/FRED; stack-frame checks can produce false positives/negatives. Test signals include syscall return work, context-switch mitigation flags, compat syscall status, hardened usercopy stack checks, FRED builds, and 32-bit vm86/SYSENTER corner cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/time.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/time.h

Purpose: declares x86 timer initialization interfaces. Important APIs are `hpet_time_init()`, `pit_timer_init()`, and `global_clock_event`.

Control flow: boot timekeeping selects and initializes HPET/PIT clock event sources; generic clockevent code uses `global_clock_event`. State is clockevent device state and hardware timer configuration. Dependencies include HPET, PIT/RTC, and generic clocksource/clockevent subsystems.

Risks include boot hangs from missing timer interrupts, wrong fallback from HPET to PIT, and clockevent misregistration. Test signals include boot timer initialization, no-HPET systems, PIT fallback, suspend/resume timekeeping, and clocksource watchdog output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/timer.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/timer.h

Purpose: declares x86 scheduler-clock and CPU-frequency time conversion helpers. Important APIs/types include `native_sched_clock()`, `recalibrate_cpu_khz()`, `no_timer_check`, `using_native_sched_clock()`, `paravirt_set_sched_clock()`, `cyc2ns_data`, `cyc2ns_read_begin()`, and `cyc2ns_read_end()`.

Control flow: sched_clock converts TSC cycles to nanoseconds using a linear equation that preserves continuity across frequency changes; paravirt can replace the sched_clock provider. State includes cycle-to-ns multiplier, shift, and offset data managed elsewhere.

Dependencies include TSC calibration, paravirt clock hooks, interrupt/timer code, and CPU frequency recalibration. Risks include non-monotonic sched_clock, bad frequency recalibration, and paravirt/native provider mismatch. Test signals include sched_clock monotonicity, CPU frequency changes, paravirt clocksource guests, timer watchdogs, and `no_timer_check` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/timex.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/timex.h

Purpose: defines x86 timekeeping constants and entropy read helper. Important APIs/macros are `random_get_entropy()`, `CLOCK_TICK_RATE`, and `ARCH_HAS_READ_CURRENT_TIMER`.

Control flow: entropy and timing code call `random_get_entropy()`, which uses `rdtsc()` when TSC is enabled/available or falls back otherwise. State is CPU TSC hardware state. Dependencies include processor features, TSC helpers, and PIT tick rate.

Risks include using TSC when unavailable or unstable for intended entropy/timing semantics. Test signals include TSC and non-TSC boot paths, random entropy source tests, PIT tick-rate users, and clocksource validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/tlb.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/tlb.h

Purpose: provides x86 MMU gather flush glue and INVLPG/INVLPGB helpers. Important APIs include `tlb_flush()`, `invlpg()`, `__invlpgb()`, `__tlbsync()`, `invlpgb_flush_user_nr_nosync()`, `invlpgb_flush_single_pcid_nosync()`, `invlpgb_flush_all()`, `invlpgb_flush_addr_nosync()`, and `invlpgb_flush_all_nonglobals()`.

Control flow: generic unmap batching calls `tlb_flush()` to choose full-mm or range flushing through `flush_tlb_mm_range()`. Broadcast TLB flush configurations use INVLPGB to invalidate by VA/PCID/ASID and TLBSYNC to wait for completion, with preemption guarded where required.

State and persistence: mutates CPU/system TLB state only. Dependencies include generic `mmu_gather`, page/vDSO bits, broadcast TLB flush feature, x86 INVLPGB/TLBSYNC instruction encoding, and migration/preemption constraints.

Risks: missing synchronization leaves stale translations; incorrect ASID/PCID/VA flags invalidate too much or too little; migration during TLBSYNC can miss pending invalidations. Test signals include mmap/munmap stress, broadcast TLB flush capable CPUs, PCID tests, hugepage unmap, memory hotplug, and TLB shootdown selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/tlbbatch.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/tlbbatch.h

Purpose: defines x86 architecture state for deferred TLB unmap batching. Important type is `arch_tlbflush_unmap_batch`, containing a CPU mask and `unmapped_pages` flag.

Control flow: unmap paths accumulate CPUs that may hold stale translations and later flush them as a batch. State is temporary batch metadata. Dependencies include cpumasks, generic MMU gather, and x86 TLB flush code.

Risks include losing CPUs from the mask, failing to flush unmapped pages, or over-flushing under heavy munmap. Test signals include TLB gather stress, remote CPU unmap batching, mmu_gather tests, and memory reclaim under SMP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/tlbbatch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/tlbflush.h

Purpose: defines x86 TLB flush state, CR4 shadow management, dynamic PCID/ASID context tracking, lazy TLB handling, range flush APIs, broadcast ASID helpers, and PTE/PMD flush-decision helpers.

Important APIs/types: `tlb_context`, `tlb_state`, `tlb_state_shared`, per-CPU `cpu_tlbstate`, `enter_lazy_tlb()`, `nmi_uaccess_okay()`, CR4 set/clear helpers, `initialize_tlbstate_and_flush()`, `flush_tlb_info`, `flush_tlb_local()`, `flush_tlb_multi()`, `flush_tlb_mm_range()`, `flush_tlb_kernel_range()`, `arch_tlbbatch_*()`, `pte_flags_need_flush()`, `pte_needs_flush()`, `huge_pmd_needs_flush()`, and LAM state helpers.

Control flow: context switch updates loaded mm/ASID/PCID state and decides whether stale contexts require flush. Page-table changes increment mm TLB generations, collect affected CPUs, and issue local or remote flushes. Lazy TLB mode avoids unnecessary CR3 loads for kernel threads. CR4 helpers update shadow and hardware with interrupts disabled.

State and persistence: per-CPU TLB state tracks loaded mm, ASIDs, generation numbers, CR4 shadow, LAM mode, user PCID flush mask, lazy state, and invalidation flags. MM context stores TLB generation and optional global ASID transition state. Dependencies include mm, scheduler, SMP IPIs, PTI, PCID, INVPCID/INVLPGB, mmu notifiers, page-table flags, and address masking.

Risks: stale TLB entries can cause memory corruption or security bugs; loaded_mm inconsistency affects NMI uaccess; CR4 shadow races can corrupt CPU feature state; incorrect PTE flush decisions can miss permission demotions. Test signals include context-switch stress, fork/exec/mmap/munmap, PCID/PTI/LAM combinations, mmu notifier users, hugepage permission changes, NMI uaccess tests, and broadcast TLB flush capable hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/tlbflush.h -->
