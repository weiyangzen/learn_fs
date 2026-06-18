# subset-b-000679 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/cpufeature.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/cpufeature.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/cpufeature.c` is the ARM64 CPU feature
sanitization and capability engine. It records boot and secondary CPU ID register values, derives
system-wide safe feature values, advertises ELF HWCAPs to user space, enables internal CPU
capabilities, applies alternative patching, and rejects or taints CPUs whose feature set conflicts
with the finalized system view. In this imported Ceph client kernel tree it is not Ceph protocol
logic, but it is a platform contract for every filesystem, networking, page-cache, crypto, and MM
path that depends on ARM64 instruction, cache, memory-tagging, virtualization, tracing, and security
features.

### Important APIs, Types, And Functions
Key global state includes `system_cpucaps`, `boot_cpucaps`, `elf_hwcap`, `cpucap_ptrs`,
`arm64_ftr_reg_ctrel0`, the `arm64_ftr_override` instances for boot-time ID overrides, per-CPU
`this_cpu_vector`, and the optional `cpu_32bit_el0_mask`. The main table types are
`struct arm64_ftr_bits`, `struct arm64_ftr_reg`, and `struct arm64_cpu_capabilities`.

The feature-register path is built from the `ftr_*` arrays, `arm64_ftr_regs`,
`sort_ftr_regs()`, `get_arm64_ftr_reg()`, `arm64_ftr_safe_value()`, `init_cpu_ftr_reg()`,
`update_cpu_ftr_reg()`, `check_update_ftr_reg()`, `read_sanitised_ftr_reg()`, and
`__read_sysreg_by_encoding()`. The capability path centers on `arm64_features`,
`arm64_elf_hwcaps`, `compat_elf_hwcaps`, `init_cpucap_indirect_list()`,
`update_cpu_capabilities()`, `enable_cpu_capabilities()`, `verify_local_cpu_caps()`,
`check_local_cpu_capabilities()`, `setup_boot_cpu_features()`, `setup_system_features()`, and
`setup_user_features()`. User-visible emulation and reporting are handled by `do_emulate_mrs()`,
`try_emulate_mrs()`, `cpu_get_elf_hwcap*()`, `cpu_show_meltdown()`, and 32-bit EL0 sysfs support.

### Control Flow
Boot starts with CPU register snapshots from `cpuinfo.c`. `init_cpu_features()` sorts and validates
the feature-register table, initializes sanitized values from the boot CPU, applies valid override
masks, initializes SVE/SME vector length maps when available, and records optional MPAM/MTE metadata.
`setup_boot_cpu_features()` builds the indirect cpucap lookup array, checks pseudo-NMI firmware
constraints, detects boot and local capabilities, enables boot-scope CPU controls, and applies boot
alternatives.

As secondary CPUs start, `update_cpu_features()` compares their raw ID registers against the boot
CPU and folds mismatches into the safe system value according to each field's policy
(`FTR_EXACT`, `FTR_LOWER_SAFE`, `FTR_HIGHER_SAFE`, or `FTR_HIGHER_OR_ZERO_SAFE`). Strict mismatches
warn and taint the kernel with `TAINT_CPU_OUT_OF_SPEC`. Before system finalization,
`check_local_cpu_capabilities()` updates local feature/erratum capabilities; after finalization it
verifies that new CPUs match all advertised capabilities and parks or panics CPUs on conflicts.

System finalization calls `setup_system_features()`: it detects system-scope capabilities from the
sanitized ID registers, uses `stop_machine()` for non-boot CPU enable callbacks that may need real
PSTATE changes, applies alternatives globally, installs KPTI/non-global mapping effects, and runs
SVE/SME setup. `setup_user_features()` masks user-visible ID fields for errata, constructs HWCAP
bitmaps, fixes compat HWCAPs, and updates minimum signal stack sizing.

### State, Persistence, And Dependencies
All persistent state is in kernel memory: bitmap capabilities, per-CPU vectors, per-CPU or global
cpumasks for weak local features, sanitized feature-register values, static branches, sysfs
attributes, and exported HWCAP values. There is no filesystem persistence beyond sysfs/procfs
presentation. Boot parameters such as `kpti=`, `allow_mismatched_32bit_el0`, and
`irqchip.gicv3_pseudo_nmi=` mutate early policy state.

Dependencies are broad: CPU ID accessors and sysreg encodings, `asm/cpufeature.h`,
`asm/hwcap.h`, `asm/fpsimd.h`, `asm/mte.h`, KVM/hypervisor hooks, MPAM state, GICv3/GICv5
register access, Spectre/KPTI mitigation code, alternative patching, CPU hotplug, sysfs, percpu,
stop-machine, KASLR and mitigation policy, and compat AArch32 support.

### Integration Points
This file feeds `cpuinfo.c`, exception entry vectors, KVM, ptrace/sysreg emulation, ELF auxv,
`/proc/cpuinfo`, CPU hotplug, alternatives, Spectre/Meltdown reporting, SVE/SME/FPSIMD setup, MTE,
MPAM, GIC priority masking, and KPTI vector selection. Ceph client code depends on these decisions
indirectly through atomics, crypto HWCAP dispatch, page-cache coherency, networking, DMA/cache
maintenance, memory tagging, and scheduler/hotplug stability.

### Risks
Feature table mistakes are high impact: a wrong safe value can expose unsupported instructions to
user space, hide available CPU features, or permit unsafe heterogeneous CPU combinations. Missing
strictness can allow late CPU corruption; excessive strictness can prevent hotplug on valid systems.
Capability ordering matters because some entries depend on earlier caps. Override handling can
force unsafe values only if validation is wrong. KPTI, PAN, BTI, MTE, pointer authentication, GIC
priority masking, and KVM feature decisions all have security consequences. Several paths are
configuration-specific and hardware-specific, making coverage gaps likely.

### Test Signals
Useful signals are ARM64 defconfig and randconfig builds, boot on heterogeneous big.LITTLE systems,
CPU hotplug stress, KVM selftests, SVE/SME vector-length tests, MTE tests, ptrace/MRS emulation
tests, `/proc/cpuinfo` and auxv HWCAP checks, sysfs CPU register reads, Spectre/Meltdown mitigation
reporting, kdump boots, pseudo-NMI configurations, and targeted boot-parameter tests for KPTI,
feature overrides, and mismatched 32-bit EL0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/cpufeature.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/cpuinfo.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/cpuinfo.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/cpuinfo.c` captures ARM64 CPU identity and
feature-register snapshots, exposes `/proc/cpuinfo`, and publishes selected per-CPU ID registers
through sysfs. It provides the raw CPU data consumed by `cpufeature.c` to build sanitized system
feature state.

### Important APIs, Types, And Functions
The core storage is `DEFINE_PER_CPU(struct cpuinfo_arm64, cpu_data)`, plus `boot_cpu_data` and
`__icache_flags`. User-visible feature names live in `hwcap_str[]` and, under `CONFIG_COMPAT`,
`compat_hwcap_str[]` and `compat_hwcap2_str[]`. `/proc/cpuinfo` is served by `cpuinfo_op` using
`c_start()`, `c_next()`, `c_stop()`, and `c_show()`. Sysfs register exposure uses
`CPUREGS_ATTR_RO()`, `cpuid_cpu_online()`, `cpuid_cpu_offline()`, and `cpuinfo_regs_init()`.
Hardware capture is performed by `__cpuinfo_store_cpu()`, `__cpuinfo_store_cpu_32bit()`,
`cpuinfo_store_cpu()`, and `cpuinfo_store_boot_cpu()`.

### Control Flow
On the boot CPU, `cpuinfo_store_boot_cpu()` reads architectural registers into per-CPU CPU0 data,
copies them to `boot_cpu_data`, and calls `init_cpu_features()`. On secondary CPU startup,
`cpuinfo_store_cpu()` refreshes this CPU's snapshot and calls `update_cpu_features()` to fold the
CPU into the sanitized system state or verify it after finalization. `__cpuinfo_store_cpu()` reads
the effective cache type, DC ZVA size, MIDR/REVIDR/AIDR, AArch64 ID registers, optional GMID, SMIDR,
and AArch32 registers only if 32-bit EL0 is supported. MPAMIDR is deliberately deferred to
`cpufeature.c` so overrides can prevent unsafe firmware traps.

For reporting, `/proc/cpuinfo` iterates online CPUs and prints processor number, BogoMIPS, HWCAP
feature strings, implementer, architecture, variant, part, and revision. Sysfs hotplug callbacks add
a `regs/identification` group under each CPU device containing MIDR, REVIDR, AIDR, and optionally
SMIDR when SME is supported.

### State, Persistence, And Dependencies
The file persists data only in kernel memory and sysfs/procfs views. `__icache_flags` records
whether any CPU has an aliasing I-cache. Dependencies include CPU ID/system-register accessors,
`arch_timer_get_cntfrq()`, cpumasks, CPU hotplug, kobjects/sysfs, `loops_per_jiffy`, personality
handling for compat `/proc/cpuinfo`, `cpufeature.c` exports, and SME/MTE/MPAM feature helpers.

### Integration Points
`cpufeature.c` consumes these snapshots for all feature sanitization and CPU capability decisions.
`/proc/cpuinfo` is consumed by legacy userspace and libc CPU enumeration behavior, while sysfs
register files are consumed by diagnostic tools. Cache policy detection feeds global I-cache
maintenance decisions that affect executable mappings and JIT coherency.

### Risks
Reading unavailable or firmware-trapped registers too early can crash or hang boot, which is why
some optional registers are gated. Misreporting HWCAP names can break user-space feature dispatch.
Incorrect cache-type interpretation can produce stale instruction execution or excessive cache
maintenance. Hotplug sysfs lifetime errors can leak or double-remove kobjects. Compat reporting is
ABI-sensitive because older software parses strings rather than auxv.

### Test Signals
Boot and hotplug on varied ARM64 CPUs, `/proc/cpuinfo` comparison against auxv, sysfs
`/sys/devices/system/cpu/cpu*/regs/identification/*` reads across online/offline transitions,
compat process checks, SME-enabled builds, and cache aliasing/JIT tests are the main validation
signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/cpuinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/crash_dump.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/crash_dump.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/crash_dump.c` supplies the ARM64 kdump hooks
for reading memory from a crashed kernel and reading the crash ELF core header. It supports
kexec-based crash dump collection.

### Important APIs, Types, And Functions
`copy_oldmem_page()` maps one old-memory PFN with `memremap(..., MEMREMAP_WB)`, copies a requested
range into an `iov_iter`, and unmaps it. `elfcorehdr_read()` copies bytes from the crash kernel's
mapped ELF core header using `phys_to_virt()` and advances the caller's physical position pointer.

### Control Flow
`copy_oldmem_page()` exits immediately for zero-length reads, maps the requested PFN for one page,
copies `csize` bytes from `offset` into the iterator, then unmaps before returning the copied byte
count. `elfcorehdr_read()` is a straight physical-to-virtual memcpy from the crash header address.

### State, Persistence, And Dependencies
The file keeps no long-lived state. It depends on crash dump core code, `iov_iter`, memremap,
physical-to-virtual address translation, and ARM64 page sizing. Persistence is the crashed kernel's
RAM image and ELF core metadata, not local filesystem state.

### Integration Points
Generic kdump and `/proc/vmcore` paths call these architecture hooks to extract pages and the ELF
header. The output is eventually consumed by crash analysis tools. For Ceph deployments this matters
operationally because kernel panics in filesystem, networking, or block paths must leave usable
vmcore data.

### Risks
Bad PFNs or mapping failures return short/error results. Incorrect cache attributes could read stale
or corrupted old memory. Offset/size validation is delegated to callers, so callers must not request
cross-page ranges through the one-page mapping. `elfcorehdr_read()` assumes the header is directly
mapped and valid.

### Test Signals
Boot a crash kernel, collect `/proc/vmcore`, validate ELF headers with crash tools, test sparse and
high-memory PFNs, inject mapping failures, and compare copied ranges against known memory patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/crash_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/debug-monitors.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/debug-monitors.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/debug-monitors.c` implements ARM64 self-hosted
debug monitor control, single-step state management, and breakpoint exception dispatch. It bridges
architectural debug exceptions to ptrace, uprobes, kprobes, kgdb, BUG/KASAN/UBSAN/CFI handlers, and
user SIGTRAP delivery.

### Important APIs, Types, And Functions
`debug_monitors_arch()` reports the sanitized debug architecture level. `enable_debug_monitors()` and
`disable_debug_monitors()` maintain per-CPU `mde_ref_count` and `kde_ref_count` and update
`MDSCR_EL1`. `debug_enabled` can be disabled by the `nodebugmon` early parameter or debugfs
`debug_enabled`. CPU hotplug clears OS lock via `clear_os_lock()` and `debug_monitors_init()`.
Exception handlers include `do_el0_softstep()`, `do_el1_softstep()`, `do_el0_brk64()`,
`do_el1_brk64()`, `do_bkpt32()`, and `try_handle_aarch32_break()`. Single-step APIs include
`user_enable_single_step()`, `user_disable_single_step()`, `user_rewind_single_step()`,
`user_fastforward_single_step()`, `kernel_enable_single_step()`, `kernel_disable_single_step()`, and
`kernel_active_single_step()`.

### Control Flow
Debug monitor users enable MDE and optionally KDE through refcounted per-CPU calls, with preemption
expected disabled. MDSCR writes mask DAIF locally to avoid exception races. On boot/hotplug,
`clear_os_lock()` unlocks debug registers. EL0 single-step first offers the event to uprobes, then
sends `SIGTRAP/TRAP_TRACE` and rewinds state if the client wants continued stepping. EL1 single-step
offers the event to kgdb and otherwise warns and re-enables stepping in the saved SPSR.

EL1 BRK dispatch inspects the BRK immediate and routes to BUG, CFI, reserved-fault, KASAN software
tag, UBSAN trap, KGDB, kprobes, or kretprobes handlers. Unhandled EL1 BRK calls `die()`. EL0 BRK
routes uprobes BRK immediates to uprobes and sends `SIGTRAP/TRAP_BRKPT` otherwise. AArch32 break
handling fetches ARM or Thumb instructions from user memory and recognizes ARM, Thumb, or Thumb-2
break encodings.

### State, Persistence, And Dependencies
Persistent state is per-CPU MDSCR enable refcounts, the debugfs `debug_enabled` boolean, task
`TIF_SINGLESTEP`, and saved SPSR.SS bits in `pt_regs`. Dependencies include sysreg access, ptrace,
uprobes, kprobes, kgdb, KASAN, UBSAN, CFI, exception entry, user accessors, CPU hotplug, debugfs, and
signal delivery.

### Integration Points
`entry-common.c` calls these handlers for debug exception classes. Ptrace and syscall restart paths
use the user stepping APIs; kprobes/kgdb rely on kernel stepping and BRK dispatch. The file is also
part of external-debugger coexistence because debugfs and `nodebugmon` can suppress self-hosted
debug monitor enablement.

### Risks
Incorrect MDSCR refcounting can leave debug exceptions disabled or unexpectedly enabled. Calling
enable/disable paths while preemptible can update the wrong CPU's state. Bad BRK immediate routing
can turn diagnostics into fatal oopses or hide real traps. User instruction fetches for AArch32
break detection must tolerate faults. These paths are marked `NOKPROBE` where recursion would be
dangerous.

### Test Signals
Ptrace single-step tests, uprobes/kprobes tests, kgdb break/step tests, KASAN/UBSAN/BUG trap tests,
AArch32 compat breakpoint tests, CPU hotplug with debug register access, `nodebugmon`, debugfs
toggling, and lockdep/preemption warnings around MDSCR users are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/debug-monitors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/efi-header.S -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/efi-header.S

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/efi-header.S` emits the ARM64 kernel's UEFI
PE/COFF header data. It lets firmware recognize the kernel image as an EFI application while still
keeping a valid non-EFI entry opcode when EFI support is disabled.

### Important APIs, Types, And Functions
The file defines two assembler macros: `efi_signature_nop` and `__EFI_PE_HEADER`. With
`CONFIG_EFI`, `efi_signature_nop` emits an instruction whose opcode encodes the UEFI `MZ` DOS
signature. Without EFI it emits a normal `nop`. `__EFI_PE_HEADER` writes the PE signature, COFF file
header, PE32+ optional header, section table, optional debug directory entries, CodeView path data,
BTI forward-CFI DLL characteristics, and alignment padding.

### Control Flow
There is no runtime control flow beyond the first header instruction. The assembler emits a static
binary layout controlled by `CONFIG_EFI`, `CONFIG_DEBUG_EFI`, `CONFIG_ARM64_BTI_KERNEL`,
`CONFIG_RELOCATABLE`, linker symbols such as `_end`, `__initdata_begin`, and EFI constants from
`linux/pe.h`.

### State, Persistence, And Dependencies
The persistent artifact is the kernel image header on disk/in memory. Dependencies include PE/COFF
constants, segment and file alignment definitions, EFI stub entry symbol
`__efistub_efi_pe_entry`, linker-provided size symbols, `VMLINUX_PATH` for debug builds, and BTI
kernel configuration.

### Integration Points
Firmware and bootloaders consume this header before Linux runs. EFI stub code uses the declared
entry point and section metadata. Debug EFI and BTI metadata allow firmware/tooling to understand
debug path and branch protection properties.

### Risks
Any offset, size, alignment, section count, or signature error can make the kernel unbootable via
UEFI. Debug-table RVAs are subtle because the header itself is not covered by a section, so payload
placement must remain synchronized with the comments. BTI metadata must agree with actual kernel BTI
support.

### Test Signals
Build with and without `CONFIG_EFI`, inspect the image with PE/COFF tools, boot via UEFI firmware and
common bootloaders, verify debug EFI builds expose the expected path data, and test BTI-kernel images
on firmware that interprets DLL characteristics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/efi-header.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/efi-rt-wrapper.S -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/efi-rt-wrapper.S

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/efi-rt-wrapper.S` provides the assembly wrapper
used to call EFI runtime services on ARM64. It preserves kernel callee-saved state, switches to a
dedicated EFI runtime stack, protects the platform/shadow-call-stack register `x18`, and provides a
recovery landing path for synchronous exceptions inside firmware.

### Important APIs, Types, And Functions
`__efi_rt_asm_wrapper` takes an EFI function pointer and up to five register arguments, preserves
frame, LR, `x18`, and callee-saved registers, records the interrupted task SP at the top of the EFI
stack, calls firmware, checks whether firmware corrupted `x18`, and tail-calls
`efi_handle_corrupted_x18()` if needed. `__efi_rt_asm_recover` restores state after
`efi_runtime_fixup_exception()` redirects control out of a faulting firmware call.

### Control Flow
The wrapper saves kernel state on the current stack, loads `efi_rt_stack_top`, switches SP to the EFI
stack, records `x18` and the old frame pointer, moves arguments into EFI ABI positions, and branches
to the firmware function. On normal return it restores the old SP, clears the saved task SP slot,
restores registers, and returns if `x18` survived. If `x18` changed, shadow-call-stack builds reload
`x18` from the EFI stack record before reporting corruption. The recovery path uses `x30` as the
saved kernel stack pointer supplied by the C exception fixup and restores callee-saved state without
returning through firmware.

### State, Persistence, And Dependencies
State is transient register and stack state plus the global `efi_rt_stack_top` allocated by
`efi.c`. Dependencies include ARM64 AAPCS, EFI runtime calling conventions, shadow call stack use of
`x18`, C handlers `efi_handle_corrupted_x18()` and `efi_runtime_fixup_exception()`, and stack layout
agreement with `efi.c`.

### Integration Points
`arch_efi_call_virt_setup()`/`teardown()` prepare address-space and FPSIMD state around calls that
enter this wrapper. Synchronous exception handling consults the EFI stack records and redirects to
`__efi_rt_asm_recover` when firmware faults.

### Risks
Register-save ordering and stack offsets are ABI-critical. Failing to restore `x18` corrupts shadow
call stack or platform state. Clearing the recorded SP too early or too late can break firmware
exception recovery. EFI calls that unexpectedly use stack arguments would violate the wrapper's
assumption that ARM64 runtime services use at most five arguments.

### Test Signals
EFI runtime service tests (`GetTime`, variables, `ResetSystem` paths), fault injection inside EFI
runtime calls, shadow-call-stack builds, preemptible kthread EFI calls, and register-corruption
instrumentation around `x18` validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/efi-rt-wrapper.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/efi.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/efi.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/efi.c` implements ARM64-specific EFI runtime
mapping, permission, call setup, call teardown, runtime stack allocation, and firmware-fault
recovery. It adapts generic EFI runtime support to ARM64 page permissions, BTI, TTBR0 PAN handling,
FPSIMD state, and shadow-call-stack concerns.

### Important APIs, Types, And Functions
Mapping helpers are `region_is_misaligned()`, `create_mapping_protection()`,
`efi_create_mapping()`, `set_permissions()`, and `efi_set_mapping_permissions()`. Runtime-call
helpers are `efi_poweroff_required()`, `efi_handle_corrupted_x18()`, `arch_efi_call_virt_setup()`,
`arch_efi_call_virt_teardown()`, and `efi_runtime_fixup_exception()`. Initialization is handled by
`arm64_efi_rt_init()`, which allocates the dedicated EFI runtime stack and initializes
`efi_rt_stack_top`.

### Control Flow
During EFI memory-map setup, `efi_create_mapping()` chooses device, read-only, executable, or
non-executable kernel page protections from EFI memory descriptor type and attributes. Misaligned
runtime regions are forced to page mappings and weaker permissions because OS pages can overlap
adjacent EFI regions. Later `efi_set_mapping_permissions()` tightens page-level RO/XN/BTI guarded
page bits for runtime code/data regions when the descriptors and mapping granularity allow it.

Before each runtime call, `arch_efi_call_virt_setup()` asserts the EFI runtime lock, either borrows
`efi_mm` in a preemptible kthread with migration disabled or loads the EFI virtual map directly,
enables TTBR0 access and erratum workaround state, and begins EFI FPSIMD handling. Teardown ends
FPSIMD handling, disables TTBR0 access before unloading the EFI map, and releases borrowed mm or
migration state. If a synchronous exception occurs while executing firmware,
`efi_runtime_fixup_exception()` disables runtime services, taints the kernel for firmware workaround,
sets the return value to `EFI_ABORTED`, restores LR and optionally `x18` from the EFI stack record,
and redirects PC to `__efi_rt_asm_recover`.

### State, Persistence, And Dependencies
Persistent state includes `efi_rt_stack_top`, EFI runtime service enable bits in `efi.flags`, EFI
runtime mappings in `efi_mm`, and the allocated vmap stack. Dependencies include generic EFI memory
attribute parsing, page table creation, `apply_to_page_range()`, protected MMIO helpers, BTI feature
detection, kthread borrowed-mm support, migration control, TTBR0/PAN helpers, `post_ttbr_update_workaround()`,
EFI FPSIMD wrappers, stacktrace/current-in-EFI state, kmemleak, and vmap stack allocation.

### Integration Points
Generic EFI runtime code calls the mapping and setup/teardown hooks. The assembly wrapper in
`efi-rt-wrapper.S` uses `efi_rt_stack_top` and recovery semantics. Exception handling calls
`efi_runtime_fixup_exception()` when faults may have occurred in firmware. Poweroff and capsule
update behavior depends on `efi_poweroff_required()`.

### Risks
Miscomputed permissions can leave firmware code writable/executable or make valid runtime code
unexecutable. Misaligned regions force weaker protection and can conflict with adjacent descriptors.
Incorrect TTBR0 or EFI virtual map sequencing can expose user page tables or fault in runtime calls.
Failure to disable migration for preemptible kthread calls can resume firmware-polling flows on the
wrong CPU. Firmware faults disable all runtime services, so false positives are disruptive.

### Test Signals
EFI variable reads/writes, time service calls, capsule update/poweroff flows, memory-attribute-table
permission checks, BTI EFI runtime mappings, fault injection in firmware calls, lockdep around the
EFI runtime lock, shadow-call-stack builds, and kthread/preemptible runtime callers are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/efi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/elfcore.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/elfcore.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/elfcore.c` adds ARM64 Memory Tagging Extension
metadata to ELF core dumps. When MTE is supported, it emits extra program headers and tag storage
for VMAs marked `VM_MTE`.

### Important APIs, Types, And Functions
`for_each_mte_vma` iterates coredump VMA metadata only when `system_supports_mte()` is true and the
VMA has `VM_MTE`. `mte_vma_tag_dump_size()` calculates compact tag storage size. `mte_dump_tag_range()`
saves tags page by page. Generic ELF hooks are `elf_core_extra_phdrs()`,
`elf_core_write_extra_phdrs()`, `elf_core_extra_data_size()`, and `elf_core_write_extra_data()`.

### Control Flow
The core dump code first asks for the number and size of extra headers/data. For each MTE VMA,
`elf_core_write_extra_phdrs()` emits a `PT_AARCH64_MEMTAG_MTE` program header whose file size is
the compact tag dump and whose memory size is the VMA range. Data emission then walks pages in
`mte_dump_tag_range()`: missing zero pages and untagged pages are represented by skipped zero tag
storage, tagged pages allocate temporary storage, save page tags, and emit them to the dump.

### State, Persistence, And Dependencies
The file has no long-lived state. It reads core VMA metadata, page table dump pages, page MTE tag
state, and MTE tag storage. Its persistence is the generated core file contents. Dependencies are
generic coredump/ELF helpers, `get_dump_page()`, `dump_emit()`, `dump_skip()`, page reference
management, and ARM64 MTE helpers.

### Integration Points
ELF core dump generation calls these architecture hooks. Debuggers and postmortem tools consume the
`PT_AARCH64_MEMTAG_MTE` segments to reconstruct allocation tags. This is relevant to diagnosing
memory corruption in kernel-provided user processes and filesystem clients running on MTE-enabled
systems.

### Risks
Tag data must stay aligned with dumped pages; skipping zero or untagged pages must produce exactly
the expected zero-length representation. Allocation failure aborts extra data emission. Incorrect
page reference handling can leak pages. The code assumes start/end/dump sizes are page-aligned by
the core dump layer.

### Test Signals
User MTE coredump tests, comparison of tag segments with live process tags, sparse mapping core
dumps, PROT_EXEC-only mappings, untagged pages in MTE VMAs, allocation failure injection, and
debugger parsing of `PT_AARCH64_MEMTAG_MTE` segments validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/elfcore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/entry-common.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/entry-common.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/entry-common.c` is the C half of ARM64
exception entry. It receives saved `pt_regs` from `entry.S`, transitions RCU/lockdep/irq/context
tracking state, classifies ESR exception classes, invokes the appropriate subsystem handler, and
returns through user or kernel exit preparation.

### Important APIs, Types, And Functions
Entry/exit helpers include `arm64_enter_from_kernel_mode()`, `arm64_exit_to_kernel_mode()`,
`arm64_enter_from_user_mode()`, `arm64_exit_to_user_mode()`, syscall-specific entry/exit helpers,
`asm_exit_to_user_mode()`, `arm64_enter_el1_dbg()`, and `arm64_exit_el1_dbg()`. Interrupt helpers are
`do_interrupt_handler()`, `el1_interrupt()`, `el0_interrupt()`, and wrappers around `handle_arch_irq`
and `handle_arch_fiq`. Main handlers include `el1h_64_sync_handler()`, EL1 IRQ/FIQ/error handlers,
`el0t_64_sync_handler()`, EL0 IRQ/FIQ/error handlers, compat 32-bit handlers, `handle_bad_stack()`,
and `__sdei_handler()`.

### Control Flow
For EL1 synchronous exceptions, the handler reads `ESR_EL1`, switches on ESR class, and dispatches
aborts, PC alignment, undefined/sysreg traps, BTI, GCS, MOPS, breakpoints, single-step, watchpoints,
BRK64, FPAC, or panic for unhandled classes. EL1 interrupts are treated as normal IRQ/FIQ or
pseudo-NMI depending on PSTATE/PMR state. EL1 SError enters NMI-style accounting and calls
`do_serror()`.

For EL0, every handler first enters from user mode, applies branch-prediction hardening for
potential kernel addresses, restores DAIF to process context where appropriate, calls the specific
fault/syscall/debug/FPSIMD/SVE/SME/GCS/MOPS handler, and exits to user mode. Syscall entry also
handles the Cortex-A76 single-step erratum workaround and FPSIMD/SVE syscall ABI cleanup. Compat
32-bit handling adds CP15 and BKPT dispatch. SDEI handling is NMI-like and fixes PAN state before
calling the generic SDEI layer.

### State, Persistence, And Dependencies
State is mostly transient exception context: `pt_regs`, ESR/FAR values, DAIF state, irqentry state,
RCU/context tracking, current task flags, FPSIMD last-state markers, and optional per-CPU erratum
state. Dependencies include generic irq-entry code, context tracking, lockdep, RCU, MTE, SME/SVE,
FPSIMD, debug monitors, traps, memory abort code, system call handlers, branch predictor hardening,
SDEI, and stack overflow handling.

### Integration Points
`entry.S` branches to these C handlers. Subsystems reached from here include MM fault handling,
signals, ptrace/debug, kprobes/uprobe, syscalls, IRQ chips, SError/RAS, FPSIMD/SVE/SME lazy state,
MTE tag-fault checks, livepatch/resume-user-mode logic through generic exit code, and SDEI firmware
events.

### Risks
Ordering is critical: many functions are `noinstr` because tracing, KASAN, lockdep, or faults are
unsafe until entry state is established. Enabling interrupts too early or leaving DAIF in the wrong
state can recurse or lose accounting. Missing MTE/SME/FPSIMD entry/exit hooks breaks user ABI.
Incorrect ESR classification can turn recoverable faults into panics or vice versa. Debug exception
paths must avoid scheduling and instrumentation recursion.

### Test Signals
Exception selftests, syscall ABI tests, user and kernel fault injection, ptrace/kprobes/uprobes,
MTE async fault tests, SVE/SME syscall tests, pseudo-NMI IRQ tests, SError/RAS injection, stack
overflow tests, compat 32-bit syscall/fault tests, and objtool/noinstr validation are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/entry-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/entry-fpsimd.S -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/entry-fpsimd.S

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/entry-fpsimd.S` provides low-level ARM64
assembly routines for saving, loading, sizing, and flushing FPSIMD, SVE, and SME architectural
state. It is the register-movement backend for the higher-level FPSIMD/SVE/SME context-management
code.

### Important APIs, Types, And Functions
Always-present functions are `fpsimd_save_state()` and `fpsimd_load_state()`. Under
`CONFIG_ARM64_SVE`, the file exports `sve_save_state()`, `sve_load_state()`, `sve_get_vl()`,
`sve_set_vq()`, and `sve_flush_live()`. Under `CONFIG_ARM64_SME`, it exports `sme_get_vl()`,
`sme_set_vq()`, `sme_save_state()`, and `sme_load_state()`. Implementation uses macros from
`asm/fpsimdmacros.h` such as `fpsimd_save`, `sve_save`, `sve_load`, `sve_flush_z`,
`sve_flush_p`, `sve_flush_ffr`, `sme_save_za`, and `sme_load_za`.

### Control Flow
The FPSIMD routines simply save or restore the fixed FP/SIMD register file to the supplied
`struct fpsimd_state`. SVE routines save/load vector and predicate state, read or configure vector
length, and flush non-FPSIMD portions of live SVE state during syscall ABI cleanup. SME routines read
or configure streaming vector length and save/load ZA plus optional ZT state.

### State, Persistence, And Dependencies
State is CPU register state and caller-provided memory buffers; no file-local storage exists.
Dependencies include the ARM64 vector architecture, compile-time SVE/SME configuration, CPACR access
having been enabled by C callers, and exact buffer layouts shared with `fpsimd.c`, signal handling,
ptrace, and task context switching.

### Integration Points
`entry-common.c` calls `sve_flush_live()` on syscall entry. FPSIMD/SVE/SME management code uses the
save/load helpers for context switch, signal frame, ptrace, exec, and lazy state management. These
helpers are enabled only after `cpufeature.c` has detected and enabled the corresponding CPU caps.

### Risks
Any mismatch between macro layout and C structure layout corrupts task vector state. Calling SVE/SME
helpers without enabling access traps. Incorrect vector-length setup can overrun buffers or preserve
invalid state. Syscall flushing must clear the right architectural state to maintain the user ABI
while preserving shared FPSIMD lanes.

### Test Signals
FPSIMD context-switch tests, signal-frame save/restore tests, ptrace register tests, SVE vector
length switching, SME ZA/ZT save/load tests, syscall ABI tests that verify SVE state discard, and
preemption stress with vector workloads are useful validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/entry-fpsimd.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/entry-ftrace.S -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/entry-ftrace.S

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/entry-ftrace.S` implements ARM64 ftrace entry
and function-graph tracing trampolines. It adapts compiler instrumentation call sites to generic
ftrace callbacks while preserving live AAPCS registers and constructing usable frame records for
stack unwinding.

### Important APIs, Types, And Functions
With `CONFIG_DYNAMIC_FTRACE_WITH_ARGS`, the central symbol is `ftrace_caller`, with optional direct
call paths `ftrace_caller_direct`, `ftrace_caller_direct_late`, and `ftrace_stub_direct_tramp`.
Without that mode, `_mcount`, `ftrace_caller`, and optional `ftrace_graph_caller` implement the
classic `-pg` path. Common stubs are `ftrace_stub`, `ftrace_stub_graph`, and
`return_to_handler()` for function graph returns. The code uses `struct ftrace_regs` offsets from
`asm-offsets.h`.

### Control Flow
In patchable-function-entry mode, enabled call sites branch to `ftrace_caller` after moving LR to
`x9`. The trampoline optionally loads per-callsite `ftrace_ops`, handles direct-call trampolines
without full register save when possible, saves argument registers and callsite metadata into
`ftrace_regs`, creates frame records, calls the selected tracer function, restores live registers,
and returns to the post-callsite PC or branches to a direct trampoline. In legacy mcount mode,
`_mcount` starts as a return-only stub, and patched call sites route through `ftrace_caller`, which
derives function PC/LR from frame records and invokes patched tracer or graph-tracer call sites.
`return_to_handler()` preserves return-value registers while asking generic graph tracing for the
original return address.

### State, Persistence, And Dependencies
The file stores no persistent state itself; ftrace core patches callsites and global labels such as
`ftrace_call` or `ftrace_graph_call`. Dependencies include dynamic ftrace, direct calls, function
graph tracer, compiler instrumentation mode, frame-pointer ABI, BTI landing pads, `ftrace_regs`
layout, and generic ftrace functions such as `prepare_ftrace_return()` and
`ftrace_return_to_handler()`.

### Integration Points
Generic ftrace patching code rewrites NOPs/branches that target these symbols. Kernel tracers,
function graph tracing, BPF/direct-call users, livepatch diagnostics, and perf-style function
tracing depend on this trampoline preserving the interrupted function ABI.

### Risks
Register preservation is subtle: x0-x8, FP, LR, PC, SP, and shadow call stack assumptions must match
the compiler and tracing ABI. Bad frame records break stack traces and graph tracing. Direct-call
paths must branch to valid BTI/PAC landing sites without unbalancing return prediction. Offset drift
between assembly and `struct ftrace_regs` silently corrupts tracing state.

### Test Signals
Dynamic ftrace enable/disable tests, function graph tracer tests, direct-call/BPF fentry tests,
stacktrace validation through traced functions, BTI/PAC builds, shadow-call-stack builds, legacy
`-pg` builds, and ftrace selftests under preemption/interrupt stress are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/entry-ftrace.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/entry.S -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/entry.S

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/entry.S` is the low-level ARM64 exception,
return, context-switch, IRQ-stack, KPTI trampoline, branch-history-mitigation, and SDEI assembly
entry code. It saves architectural state into `pt_regs`, switches between user/kernel execution
contexts, installs mitigation state, and dispatches into `entry-common.c`.

### Important APIs, Types, And Functions
Core macros include `kernel_ventry`, `kernel_entry`, `kernel_exit`, `entry_handler`,
`apply_ssbd`, MTE tag-fault/GCR helpers, `tramp_map_kernel`, `tramp_unmap_kernel`, `tramp_ventry`,
and vector-generation macros. Major symbols are `vectors`, `__bad_stack`, generated
`el*_*_*` entry stubs, `ret_to_kernel`, `ret_to_user`, `tramp_vectors`, `tramp_exit`,
`__bp_harden_el1_vectors`, `cpu_switch_to`, `ret_from_fork`, `call_on_irq_stack`, and SDEI symbols
`__sdei_asm_entry_trampoline`, `__sdei_asm_exit_trampoline`, `__sdei_asm_handler`, and
`__sdei_handler_abort`.

### Control Flow
Each vector slot runs `kernel_ventry`, allocates `pt_regs`, checks for stack overflow without
clobbering GPRs, and branches to an EL/handler-specific stub. `kernel_entry` saves GPRs, clears user
GPRs on EL0 entry, swaps `sp_el0` to the current task, disables pending single-step state, checks
MTE async tag faults, installs kernel pointer-auth keys, applies SSBD mitigation, sets kernel MTE
GCR, loads shadow call stack state, records ELR/SPSR/LR/SP metadata, handles software PAN, and saves
PMR for pseudo-NMI. Generated entry handlers call the matching C handler and branch to kernel or user
return.

`kernel_exit` restores PMR, ELR/SPSR, software PAN/TTBR0 state, user SP, pointer-auth keys, MTE user
GCR, SSBD state, all registers, KPTI trampoline exit if needed, speculative-load/TLBI workarounds,
and finally `eret`. KPTI trampoline vectors map the kernel, apply optional BHB mitigations, install
real vectors, and jump into the full vector table. `cpu_switch_to` saves/restores callee-saved task
context, updates `sp_el0`, pointer-auth keys, and shadow call stack. `ret_from_fork` finishes new
tasks and returns through user exit. `call_on_irq_stack` switches to per-CPU IRQ and shadow IRQ
stacks before invoking a C IRQ handler. SDEI assembly saves firmware-preserved register state,
switches to SDEI stacks, calls C SDEI handling, and completes/resumes through SMC/HVC.

### State, Persistence, And Dependencies
State is architectural: GPRs, ELR/SPSR, SPs, VBAR, TTBR1, PMR, MDSCR step state, MTE TFSR/GCR,
pointer-auth keys, shadow call stack pointers, task `thread_info`, per-CPU entry task/vector/IRQ/SDEI
stacks, and saved `pt_regs`. Dependencies include generated asm offsets, ARM64 alternatives,
exception C handlers, MMU/KPTI layout, Spectre SSBD/BHB mitigation callbacks, MTE, pointer
authentication, software PAN, pseudo-NMI/GIC priority masking, shadow call stack, stackleak,
scheduler context switch layout, and SDEI firmware ABI.

### Integration Points
This is the hardware-facing entrance to `entry-common.c`, scheduler context switching, IRQ handling,
fork return, KPTI vector selection from `cpufeature.c`, Spectre mitigation code, SDEI firmware
events, stack overflow panic handling, and per-task security state. All kernel subsystems,
including Ceph client code, depend on these paths for correct syscall, interrupt, fault, and
preemption behavior.

### Risks
The vector slot size, stack overflow arithmetic, `pt_regs` offsets, and register restore ordering
are ABI- and hardware-critical. Any instruction after user register restore can leak or clobber user
state. Mitigation ordering affects Spectre/KPTI/PAN/MTE/PAuth security. Incorrect PMR or DAIF
handling can lose interrupts or break pseudo-NMI semantics. SDEI and IRQ-stack switching must
preserve shadow call stack state. Assembly and C structure layout drift is especially dangerous.

### Test Signals
Boot tests with KPTI on/off, Spectre BHB/SSBD mitigation variants, pseudo-NMI, MTE, pointer auth,
shadow call stack, stackleak, software PAN, SDEI, IRQ flood tests, syscall/fault stress,
context-switch stress, fork/exec tests, stack-overflow tests, CPU hotplug, and objdump validation of
vector slot size and alternative patch sites are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/entry.S -->
