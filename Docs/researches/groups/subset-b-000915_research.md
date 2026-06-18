# subset-b-000915 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/tdx.c -->
# sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/tdx.c

Purpose: Implements x86 host-side Intel TDX bring-up and the KVM-facing TDH.* SEAMCALL wrapper layer. It detects BIOS KeyID partitioning, disables incompatible hibernation/S3 paths, initializes the TDX module, builds static TDX memory regions and TDMRs, allocates PAMTs, configures the global KeyID, blocks incompatible memory hotplug, and exports TD lifecycle helpers for KVM TDX guests.

Important APIs/types/functions: Early setup enters through `tdx_init()` and later `tdx_enable()` as a `subsys_initcall`. CPU lifecycle uses `tdx_cpu_enable()`, `tdx_online_cpu()`, `tdx_offline_cpu()`, and syscore suspend/resume/shutdown hooks. Module setup flows through `get_tdx_sys_info()`, `build_tdx_memlist()`, `alloc_tdmr_list()`, `construct_tdmrs()`, `config_tdx_module()`, `config_global_keyid()`, and `init_tdmrs()`. Exported KVM helpers include `tdx_get_sysinfo()`, KeyID allocation/free, `tdx_quirk_reset_page()`, `tdh_vp_enter()`, TD/VP creation and initialization calls, SEPT/memory add/remove/block/track calls, measurement calls, reclaim/cache-writeback calls, and kexec cache cleanup.

Control flow: TDX is prequalified by MSR KeyID partitioning in `tdx_init()`, then enabled only if host CPU features include TDX host platform, XSAVE, MOVDIR64B, and self-snoop. CPU hotplug setup obtains VMX refs and runs global/per-LP TDH.SYS initialization before the module is configured. Initialization snapshots memblock memory under `mem_hotplug_lock`, aligns it into 1GB TDMRs, allocates contiguous PAMT memory per TDMR, reserves memory holes and overlapping PAMTs inside TDMRs, sends physical TDMR addresses to TDH.SYS.CONFIG, programs the package global KeyID after WBINVD, and iterates TDH.SYS.TDMR.INIT until each region is complete.

State and persistence behavior: Persistent boot state is held in `tdx_global_keyid`, guest KeyID range fields, `tdx_guest_keyid_pool`, per-CPU `tdx_lp_initialized`, global `tdx_sysinfo`, `tdx_tdmr_list`, `tdx_memlist`, and `tdx_module_initialized`. `tdx_memlist` is immutable after module setup and used to reject later memory outside the configured TDX range. The TDMR/PAMT arrays remain read-mostly for page-private checks and KVM operation. Exported TDH wrappers are mostly stateless except for flushing pages before handing them to the module and returning extended error registers to callers.

Dependencies and integration points: The file depends on VMX reference accounting, CPU hotplug, syscore suspend, memblock/memory hotplug, contig page allocation, ACPI suspend hooks, MKTME MSRs, machine-check reporting, KVM-exported symbols, and low-level SEAMCALL functions from `tdxcall.S`. It integrates upward with KVM TDX through TDH wrappers and KeyID allocation, and downward with the TDX module ABI through `struct tdx_module_args`.

Risks: Initialization is security-critical: wrong TDMR alignment, reserved-area accounting, PAMT overlap handling, KeyID sequencing, or cache flushing can make the TDX module reject memory or expose stale encrypted/private state. CPU offlining is constrained while TD guest KeyIDs are allocated because package-wide WBINVD/PConfig work must remain possible. Memory hotplug after initialization is intentionally conservative. Error unwind must reset potentially private PAMT pages on affected CPUs to avoid later #MC. Test signals include TDX host boot with varied NUMA/memory holes, memory hotplug rejection, CPU hotplug package-last refusal, KVM TDX TD create/destroy, suspend/hibernation exclusion, kexec cache flush, and MCE messages for TDX-private memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/tdx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/tdx.h -->
# sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/tdx.h

Purpose: Defines the local TDX host architecture constants and private data structures used by `tdx.c`. It separates hardware-defined TDX ABI values from Linux-only helper state.

Important APIs/types/functions: The header enumerates TDH.* SEAMCALL leaf IDs, `TDX_VERSION_SHIFT`, TDX physical page types `PT_NDA` and `PT_RSVD`, TDMR alignment constants, `struct tdmr_reserved_area`, packed/aligned `struct tdmr_info`, `TDX_FEATURES0_NO_RBP_MOD`, `struct tdx_memblock`, `TDMR_NR_WARN`, and `struct tdmr_info_list`.

Control flow and state: This file has no executable control flow, but its layout definitions control how `tdx.c` builds the physical TDMR array passed to TDH.SYS.CONFIG. `tdmr_info` uses a flexible reserved-area tail whose size is calculated from TDX module metadata. `tdx_memblock` records source memory PFN ranges and NUMA node IDs, while `tdmr_info_list` records the contiguous TDMR allocation, element size, maximum count, and consumed count.

Dependencies and integration points: It includes `linux/bits.h` and is included by the TDX host implementation. Its constants must match the TDX module ABI and the generic `asm/tdx.h` structures used for SEAMCALL arguments.

Risks and test signals: Because these structures are consumed by firmware/module code, packing, alignment, leaf IDs, and page type values are ABI-sensitive. Regression signals are TDX module initialization failures, unexpected TDH.SYS.CONFIG errors, reserved-area exhaustion warnings, or KVM TDX wrapper calls targeting the wrong leaf.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/tdx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/tdx_global_metadata.c -->
# sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/tdx_global_metadata.c

Purpose: Provides generated helper functions for reading TDX module global metadata fields into `struct tdx_sys_info`. It is intentionally included into another C file because it relies on the including file's `read_sys_metadata_field()` SEAMCALL primitive.

Important APIs/types/functions: `get_tdx_sys_info_version()` reads module major/minor/update versions. `get_tdx_sys_info_features()` reads `tdx_features0`. `get_tdx_sys_info_tdmr()` reads TDMR limits and PAMT entry sizes. `get_tdx_sys_info_td_ctrl()` reads TDR/TDCS/TDVPS base sizes. `get_tdx_sys_info_td_conf()` reads fixed attribute/XFAM masks, CPUID config count, max vCPUs per TD, and CPUID leaf/value arrays. `get_tdx_sys_info()` sequences the full read and logs the module version.

Control flow and state: Each helper short-circuits on first read error. CPUID array reads validate `num_cpuid_config` against destination array sizes before filling leaves and value pairs. The only persisted state is the caller-provided `tdx_sys_info` structure.

Dependencies and integration points: Field IDs are TDX module ABI constants encoded directly in the generated code. The helpers depend on Linux `ARRAY_SIZE`, `pr_info`, and the including translation unit's SEAMCALL read wrapper. `tdx.c` uses the result to check features, size TDMR/PAMT allocations, and expose sysinfo to KVM.

Risks and test signals: Stale generated field IDs or missing bounds checks can corrupt host setup or KVM's advertised TD capabilities. Test signals include module version logging, failure on unsupported metadata, CPUID config count overflows returning `-EINVAL`, and successful KVM TD creation using the exported sysinfo.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/tdx_global_metadata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/tdxcall.S -->
# sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/tdxcall.S

Purpose: Implements the assembly glue for TDCALL and SEAMCALL through the shared `TDX_MODULE_CALL` macro, moving C `struct tdx_module_args` fields into ABI registers, invoking the instruction, optionally saving return registers, handling SEAMCALL faults, and preserving the x86-64 ABI.

Important APIs/types/functions: The file defines instruction bytes for `tdcall` and `seamcall` and a parameterized `TDX_MODULE_CALL host ret saved` macro. The macro supports normal calls, calls that return output registers, and calls requiring callee-saved registers for large ABIs such as VP.ENTER.

Control flow and state: Inputs arrive with leaf in `%rdi` and args pointer in `%rsi`. The macro loads RAX/RCX/RDX/R8-R11 and optionally RBX/RDI/RSI/R12-R15, saves callee-saved registers, executes SEAMCALL or TDCALL, copies outputs back to the args structure when requested, clears shared guest/VMM registers on saved-return paths to reduce speculative exposure, restores saved registers, and returns RAX status. SEAMCALL CF is normalized to `TDX_SEAMCALL_VMFAILINVALID`; #GP/#UD traps are converted to TDX software error codes through an exception table.

Dependencies and integration points: It uses asm offsets for `struct tdx_module_args`, frame macros, exception table annotations, and status constants from `asm/tdx.h`. It is the low-level backend for host TDX wrappers in `tdx.c` and guest TDX code elsewhere.

Risks and test signals: Register save/restore errors can corrupt callers or leak guest-controlled values. Fault mapping must distinguish absent/busy SEAM firmware from real module status. Objtool/noinstr constraints matter for VP.ENTER paths. Test signals include successful TDH.SYS.* calls, injected SEAMCALL #UD/#GP handling, VP.ENTER register round trips, kexec/noinstr validation, and absence of callee-saved register corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/tdxcall.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/Kconfig -->
# sources/distributed-fs/ceph-client/arch/x86/xen/Kconfig

Purpose: Defines x86 Xen guest configuration options and feature dependencies for PV, PVHVM, PVH, Dom0, debugfs, and PV MSR behavior.

Important entries: `XEN` enables base Xen guest support and selects paravirt clock, callback vector, and hibernate callbacks. `XEN_PV` adds 64-bit PV support with XXL paravirt ops, PV MMU, VPMU, and guest perf. `XEN_512GB` limits PV domain memory by default. `XEN_PVHVM`, `XEN_PVHVM_GUEST`, and `XEN_PVH` cover HVM/PVH modes. `XEN_DOM0` selects Dom0 support with ACPI/PCI/IOAPIC constraints. `XEN_DEBUG_FS` enables debug/tuning files. `XEN_PV_MSR_SAFE` defaults PV MSR access to safe variants.

Control flow and state: Kconfig choices determine which objects are built and which paravirt, MMU, interrupt, grant-table, and boot paths are available. There is no runtime state in this file, but options such as `XEN_PV_MSR_SAFE` and `XEN_512GB` feed boot-time defaults in the source files.

Dependencies and integration points: The file depends on x86 paravirt, APIC, TSC, ACPI, PCI, SWIOTLB_XEN, and architecture mode constraints. It directly drives `arch/x86/xen/Makefile` object inclusion.

Risks and test signals: Misstated dependencies can build unusable guest modes or omit required runtime pieces. Build matrix signals include PV-only, HVM/PVHVM, PVH Dom0, debugfs, SMP/non-SMP, and safe-MSR combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/xen/Makefile

Purpose: Selects x86 Xen object files and special compiler flags according to the Xen Kconfig feature set.

Important behavior: It disables function tracing for low-level debug/time/IRQ spinlock objects and disables stack protector for early `enlighten_pv.o` and `mmu_pv.o`, which run before normal stack-protector setup. Common objects include `enlighten.o`, `mmu.o`, `time.o`, `grant-table.o`, and `suspend.o`. HVM/PVHVM adds HVM enlightenment, MMU, suspend, and platform unplug support. PV adds setup/APIC/PMU/suspend/p2m/enlighten/MMU/IRQ/multicall/asm support. PVH, SMP, PV spinlock, debugfs, Dom0 VGA, and EFI objects are conditional.

Control flow and state: Build composition controls runtime initialization paths registered through `hypervisor_x86`, paravirt ops, initcalls, and exported Xen helpers. There is no persistent state in the Makefile itself.

Dependencies and integration points: It mirrors `Kconfig` symbols and ties C/assembly modules into the x86 Xen subsystem. The object split matters because PV early boot cannot tolerate instrumentation or stack protector before GDT/TLS are initialized.

Risks and test signals: Incorrect object selection can lead to missing symbols or subtle boot failures in one guest mode. Test signals are allmodconfig/allyesconfig builds, PV boot without stack protector faults, HVM/PVH boot with platform unplug, and debugfs/EFI/Dom0-specific link coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/apic.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/apic.c

Purpose: Provides Xen PV APIC and IO-APIC operation shims so the native x86 APIC framework can run in a PV guest where real APIC register access is replaced by Xen hypercalls or emulation.

Important APIs/types/functions: `xen_io_apic_read()` uses `PHYSDEVOP_apic_read` and falls back to emulated register values. `xen_apic_read()` synthesizes LVR/APIC ID and queries Dom0 CPU info when needed. `xen_apic_write()`, `xen_apic_eoi()`, and ICR helpers warn on unexpected native-style accesses, with LVTPC redirected to PMU support. `xen_pv_apic` is registered through `apic_driver()`, and `xen_init_apic()` installs Xen IO-APIC read ops.

Control flow and state: During PV boot, APIC probing succeeds only for Xen PV domains. Reads synthesize enough APIC identity/version state for x86 code and route Dom0 APIC IDs through platform ops. SMP IPI callbacks are wired to Xen send-IPI helpers. The file maintains no private mutable state.

Dependencies and integration points: It depends on APIC/IO-APIC core structures, Xen physdev/platform hypercalls, CPU topology, PMU APIC update hooks, and Xen domain predicates from `xen-ops.h`.

Risks and test signals: Unexpected native APIC writes indicate missing PV interception. Wrong APIC ID synthesis can break SMP topology, interrupt routing, or Dom0 CPU mapping. Signals include Xen PV SMP boot, IPI delivery, Dom0 platform CPU info, PMU LVTPC updates, and absence of WARNs for normal APIC paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/apic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/debugfs.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/debugfs.c

Purpose: Creates and caches the top-level Xen debugfs directory for Xen-specific diagnostics and tuning files.

Important APIs/types/functions: `xen_init_debugfs()` returns a `struct dentry *` for `/sys/kernel/debug/xen`, creating it on first use and reusing `d_xen_debug` afterward.

Control flow and state: The only persistent state is the static `d_xen_debug` dentry pointer. Callers can safely request the Xen debugfs root during init and attach their own subdirectories/files.

Dependencies and integration points: It depends on `CONFIG_XEN_DEBUG_FS`, Linux debugfs, and `xen-ops.h`. `p2m.c` uses this root for an MMU/p2m debug file.

Risks and test signals: The file is small, but null or duplicate dentry handling affects all Xen debugfs consumers. Signals include debugfs-mounted Xen guests showing a single `xen` root and p2m debug entries appearing under it when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/efi.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/efi.c

Purpose: Builds a paravirtual EFI system table for Xen initial domains and initializes Linux EFI flags/secure-boot state using Xen firmware-info hypercalls.

Important APIs/types/functions: `xen_efi_probe()` queries EFI config tables, vendor, firmware version, and runtime version through `XENPF_firmware_info`, then calls `xen_efi_runtime_setup()`. `xen_efi_get_secureboot()` uses EFI variables and shim MokSBState to classify secure boot. `xen_efi_init()` writes the Xen EFI signature and table address into `boot_params`, sets `boot_params->secure_boot`, and marks `EFI_BOOT`, `EFI_PARAVIRT`, and `EFI_64BIT`.

Control flow and state: EFI probing is limited to `xen_initial_domain()`. Static initdata holds the synthetic EFI table and vendor buffer. Runtime services pointers are intentionally invalid because runtime calls are handled through Xen-specific setup.

Dependencies and integration points: It integrates Xen platform firmware ops with generic Linux EFI boot parameter processing, secure boot policy, and PVH/PV early boot paths.

Risks and test signals: Incorrect table addresses or flags can break EFI config-table discovery in Dom0. Secure boot classification must respect shim insecure mode. Test signals include Xen Dom0 EFI boot, correct `efi=runtime` behavior through Xen hooks, secure boot reporting, and graceful no-op on non-initial domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/efi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/enlighten.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/enlighten.c

Purpose: Contains Xen guest state common to PV, HVM, and PVH modes: hypercall function selection, vCPU info placement, restore handling, panic/reboot handling, console preferences, vCPU pinning, extra-memory accounting, and shared exported globals.

Important APIs/types/functions: It defines the `xen_hypercall` static call, per-CPU `xen_vcpu`, `xen_vcpu_info`, and `xen_vcpu_id`, `machine_to_phys_mapping`, `xen_start_info`, `HYPERVISOR_shared_info`, `xen_domain_type`, and `xen_start_flags`. Key functions include `xen_hypercall_setfunc()`, `__xen_hypercall_setfunc()`, `xen_cpuhp_setup()`, `xen_vcpu_restore()`, `xen_vcpu_info_reset()`, `xen_vcpu_setup()`, `xen_banner()`, `xen_running_on_version_or_later()`, `xen_add_preferred_consoles()`, `xen_reboot()`, `xen_panic_handler_init()`, `xen_pin_vcpu()`, `xen_add_extra_mem()`, and `arch_xen_unpopulated_init()`.

Control flow and state: HVM/PVH guests start with a generic hypercall static call and switch to AMD/Hygon or Intel calling convention after vendor detection; PV replaces it earlier. vCPU setup maps per-CPU `vcpu_info` when supported, otherwise resets pointers into shared info. Restore temporarily downs other vCPUs, refreshes runstate/vCPU info, and brings them back up. Panic handling changes shutdown behavior when no crash kernel is loaded. Extra memory regions are reserved and later handed to unpopulated-page allocation or ballooning.

Dependencies and integration points: This file links Xen core interfaces with Linux CPU hotplug, static calls, panic notifiers, kexec, console selection, PMU shutdown, scheduler ops, memory resources, and balloon/unpopulated page handling.

Risks and test signals: vCPU info registration is one-shot per CPU, so restore/hotplug ordering is fragile. Hypercall function selection must be noinstr-safe. Panic policy changes visible shutdown behavior. Test signals include CPU hotplug and suspend/resume across Xen versions, HVM/PVH AMD/Intel hypercalls, panic with/without crash kernel, console ordering, vCPU pinning errors, and balloon target correctness from released pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/enlighten.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/enlighten_hvm.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/enlighten_hvm.c

Purpose: Initializes Xen HVM/PVHVM guest enlightenments: shared-info mapping, callback vector handling, vCPU setup, event/interrupt/time/MMU hooks, device unplug, nopv behavior, and hypervisor registration.

Important APIs/types/functions: `xen_hvm_init_shared_info()` maps Xen shared info into a reserved PFN. `reserve_shared_info()` and `xen_hvm_init_mem_mapping()` transition the mapping from early memremap to normal virtual addressing. `init_hvm_pv_info()` detects CPUID Xen data and vCPU id. `sysvec_xen_hvm_callback` handles event-channel upcalls. CPU hotplug uses `xen_cpu_up_prepare_hvm()` and `xen_cpu_dead_hvm()`. `xen_hvm_guest_init()`, `xen_hvm_guest_late_init()`, and `xen_platform_hvm()` implement the hypervisor init flow. `x86_hyper_xen_hvm` exports the registration.

Control flow and state: Detection checks Xen CPUID and respects `nopv`/`xen_nopv`, with special PVH handling. Initialization reserves a low RAM page for shared info, maps it via `XENMEM_add_to_physmap`, initializes vCPU pointers, installs panic and SMP hotplug hooks, unplugs emulated devices, and installs Xen IRQ/time/MMU ops. Late init upgrades ACPI-discovered PVH and sets restart behavior. `xen_percpu_upcall` controls per-CPU callback EOI behavior.

Dependencies and integration points: It depends on CPUID Xen leaves, memory ops, event channels, ACPI CPU UID, APIC/IO-APIC, kexec/crash hooks, virtio restricted-memory callbacks, platform unplug, SMP, timer, and HVM MMU support.

Risks and test signals: Incorrect shared-info reservation or remapping breaks event channels and pvclock. `nopv` exceptions for PVH are policy-sensitive. CPU hotplug must not double-register vCPU info. Test signals include HVM and PVH boot, per-CPU vector callbacks, no-vector fallback, CPU online/offline, kexec soft reset, crash shutdown, virtio grant restrictions, and emulated device unplug behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/enlighten_hvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/enlighten_pv.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/enlighten_pv.c

Purpose: Implements the core Xen PV paravirt backend and first C boot path. It replaces privileged CPU/MMU/interrupt operations with Xen hypercalls, sets PV CPU capabilities, rewrites IDT/GDT/TLS handling, manages PV event upcalls, and boots the kernel from Xen `start_info`.

Important APIs/types/functions: Major entry points include `xen_start_kernel()`, `xen_pv_init_platform()`, `xen_setup_vcpu_info_placement()`, `xen_init_capabilities()`, `xen_cpuid()`, descriptor operations (`xen_load_gdt()`, `xen_load_idt()`, `xen_write_*_entry()`), segment/MSR/control-register hooks, `xen_pv_evtchn_do_upcall()`, trap conversion helpers, PV machine ops, NMI reason handling, EDD boot-param import, and PV CPU hotplug callbacks.

Control flow: `xen_start_kernel()` clears BSS, records `start_info`, patches early iret, marks PV domain state, installs `pv_info` and `pv_ops`, initializes IRQ/APIC/MMU ops, builds p2m and page tables, sets GDT before stack-protected code, disables incompatible features, registers CPU hotplug, maps the kernel into physical memory, sets IOPL, fills boot params/initrd/cmdline, handles Dom0 vs DomU legacy/PCI/ACPI/VGA differences, initializes runstate/EFI, and jumps into normal x86 reservations. Runtime context switches enter lazy CPU mode and batch descriptor/TLS changes.

State and persistence behavior: Persistent PV state includes `xen_initial_gdt`, per-CPU lazy mode and shadow TLS descriptors, optional preemptible hypercall flags, cached CR0 values, boot CPUID MWAIT leaf overrides, `xen_msr_safe`, and per-CPU IDT descriptors. Trap tables and descriptor pages are mirrored to Xen, with guest page permissions changed to satisfy hypervisor validation.

Dependencies and integration points: It ties Linux paravirt ops to Xen hypercalls, event channels, PMU emulation, MTRR/ACPI firmware data, APIC/SMP/time/MMU setup, PCI, boot params, hvc consoles, virtio grant restrictions, and PV assembly stubs.

Risks and test signals: This is extremely boot-order-sensitive because stack protector, percpu base, interrupt flags, and vCPU info are not fully initialized early. Descriptor conversion must not expose unsupported IST paths. MSR safe/unsafe behavior changes fault handling. Test signals include PV Dom0/DomU boot, SMP hotplug, trap delivery for NMI/#DB/#DF/#MC, syscall/MSR setup, TLS/LDT changes, EDD/VGA import, ACPI Dom0 behavior, and absence of early stack or paravirt faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/enlighten_pv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/enlighten_pvh.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/enlighten_pvh.c

Purpose: Handles Xen PVH-specific boot setup, especially PVH Dom0 firmware/memory quirks, GSI setup, EFI probing, VGA console import, and e820 map acquisition.

Important APIs/types/functions: `xen_pvh` records PVH mode. Dom0 builds can export `xen_pvh_setup_gsi()`. `pvh_reserve_extra_memory()` turns selected UNUSABLE e820 ranges into reserved RAM for foreign mappings/ballooning. `pvh_arch_setup()` applies PVH arch policy. `xen_pvh_init()` marks PVH mode and installs arch setup/banner hooks. `mem_map_via_hcall()` gets the memory map from `XENMEM_memory_map`.

Control flow and state: PVH init sets `xen_domain_type` to HVM, records `pvh_start_info.flags`, installs PVH arch hooks, calls Xen EFI init, and for initial domains imports Xen's Dom0 console into `boot_params`. Arch setup reserves extra memory and, for Dom0, adds Xen consoles and disables native cpuidle/cpufreq because Xen owns those power states.

Dependencies and integration points: It uses Xen memory and platform hypercalls, ACPI GSI semantics, x86 boot params, hvc console, IO-APIC, EFI, cpuidle/cpufreq controls, and common Xen extra-memory handling.

Risks and test signals: PVH Dom0 maps host-like memory with unavailable holes; mishandling UNUSABLE conversion can collide with MMIO or foreign mappings. GSI setup errors affect device interrupts. Test signals include PVH Dom0 boot, ACPI interrupt setup, memory balloon headroom, disabled native power drivers, EFI table discovery, and correct e820 population from the hypervisor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/enlighten_pvh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/grant-table.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/grant-table.c

Purpose: Implements x86-specific grant table mapping support, allocating virtual areas for PV grant shared/status frames and setting/removing PTEs that map Xen-provided grant MFNs.

Important APIs/types/functions: `arch_gnttab_map_shared()` and `arch_gnttab_map_status()` map grant frame MFNs into preallocated vmalloc areas. `arch_gnttab_unmap()` clears those PTEs. `arch_gnttab_init()` allocates shared/status virtual areas for PV guests. `xen_pvh_gnttab_setup()` preallocates translated grant frames for PVH.

Control flow and state: Static `gnttab_shared_vm_area` and `gnttab_status_vm_area` hold vmalloc areas, captured PTE pointers, and an index filled by `apply_to_page_range()`. PV guests allocate both shared and status spaces; status is allocated even before V2 is active to survive migration to V2-capable hosts. PVH setup initializes auto-translated grant frame storage before generic grant-table init.

Dependencies and integration points: It depends on Xen grant-table core, vmalloc/page-table helpers, Xen page macros, PV/PVH predicates, ballooned page translation helpers, and event setup headers.

Risks and test signals: PTE arrays must match virtual area size and lifetime; status-frame preallocation affects migration compatibility. Test signals include grant table v1/v2 operation, migration between hosts, map/unmap leak checks, PVH grant mappings, and frontend/backend I/O through granted pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/grant-table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/irq.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/irq.c

Purpose: Provides Xen PV interrupt flag/halt operations and event-channel callback forcing for the x86 paravirt IRQ layer.

Important APIs/types/functions: `xen_force_evtchn_callback()` issues a cheap hypercall so Xen rechecks pending events after callback mask changes. `xen_safe_halt()` blocks via `SCHEDOP_block`, which implicitly enables interrupts. `xen_halt()` either downs the vCPU when interrupts are disabled or calls safe halt. `xen_init_irq_ops()` installs PV IRQ ops and Xen interrupt initialization.

Control flow and state: The installed PV ops make initial save-fl and irq-disable no-ops/zero-return while interrupts are known off, mark irq-enable as a bug during early setup, and install Xen halt hooks. No private persistent state is stored in this file.

Dependencies and integration points: It depends on Xen scheduler/vCPU hypercalls, event-channel core, paravirt IRQ ops, `x86_init.irqs`, and `xen_vcpu_nr()`.

Risks and test signals: Halt and callback behavior affects idle, interrupt reenable, and pending event delivery. Test signals include PV idle wakeups, event callback after mask clear, no unexpected `BUG_func` irq-enable during early boot, and correct vCPU down behavior when halting with IRQs disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/mmu.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/mmu.c

Purpose: Provides small x86 Xen MMU helpers shared by PV and HVM paths for arbitrary virtual-to-machine translation and domain GFN unmap routing.

Important APIs/types/functions: `arbitrary_virt_to_mfn()` wraps `arbitrary_virt_to_machine()`. `arbitrary_virt_to_machine()` uses fast `virt_to_machine()` for linear mappings or walks page tables and returns an `xmaddr_t` for vmalloc/ioremap addresses. `xen_unmap_domain_gfn_range()` dispatches to auto-translated unmap for non-PV guests and rejects page-backed PV unmap requests.

Control flow and state: No persistent state is held. Translation either uses the p2m fast path for valid linear addresses or resolves the PTE and combines MFN with page offset.

Dependencies and integration points: It depends on Xen page conversion helpers, `lookup_address()`, memory hypercall interfaces, and grant/foreign mapping users that need machine addresses for non-linear kernel addresses.

Risks and test signals: Incorrect page-table walking can pass wrong MFNs to Xen hypercalls. Test signals include grant table PTE updates from vmalloc areas, PV foreign mapping unmap errors, HVM translated GFN unmapping, and BUG coverage when non-present addresses are passed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/mmu_hvm.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/mmu_hvm.c

Purpose: Installs HVM-specific Xen MMU hooks for page-table lifetime notification and vmcore RAM classification.

Important APIs/types/functions: With vmcore support, `xen_vmcore_pfn_is_ram()` queries `HVMOP_get_mem_type` so kdump avoids ballooned/MMIO-DM pages. `xen_hvm_exit_mmap()` notifies Xen via `HVMOP_pagetable_dying` when an mm's page table is being destroyed. `is_pagetable_dying_supported()` probes the hypercall. `xen_hvm_init_mmu_ops()` installs `pv_ops.mmu.exit_mmap` and registers the vmcore callback.

Control flow and state: Initialization probes support once and conditionally changes the MMU op table. The vmcore callback is registered globally when configured. No separate private state is kept.

Dependencies and integration points: It depends on HVM hypercalls, generic `pv_ops.mmu`, crash dump vmcore callbacks, and Xen HVM memory-type semantics.

Risks and test signals: Missing pagetable-dying notifications can leave stale hypervisor shadow state; wrong vmcore classification can fault or corrupt crash dumps. Signals include HVM guest process churn, Xen logs for pagetable dying support, kdump vmcore reads with ballooned pages, and no warnings from `HVMOP_get_mem_type`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/mmu_hvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/mmu_pv.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/mmu_pv.c

Purpose: Implements Xen PV MMU paravirt operations, including PFN/MFN PTE conversion, hypercall-based page-table updates, page-table pin/unpin, CR3/TLB operations, early kernel page-table construction, p2m relocation, fixmap behavior, contiguous DMA memory exchange, and remapping foreign PFNs into VMAs.

Important APIs/types/functions: Exported or externally used helpers include `make_lowmem_page_readonly()`, `make_lowmem_page_readwrite()`, `set_pte_mfn()`, `xen_mm_pin_all()`, `xen_mm_unpin_all()`, `xen_setup_machphys_mapping()`, `xen_setup_kernel_pagetable()`, `xen_relocate_p2m()`, `xen_reserve_special_pages()`, `xen_pt_check_e820()`, `xen_init_mmu_ops()`, `xen_create_contiguous_region()`, `xen_destroy_contiguous_region()`, `xen_remap_pfn()`, and `paddr_vmcoreinfo_note()`. Core internal operations cover PTE/PMD/PUD/P4D setters and value constructors, lazy multicall extension, page-table walkers, pinning, CR3 switching, TLB flushes, allocator hooks, and fixmap replacement.

Control flow: `xen_init_mmu_ops()` installs early PV MMU hooks before normal paging init. `xen_pagetable_init()` switches to hypercall PTE writes, runs generic paging init, installs post-allocator hooks, rebuilds the p2m tree, frees old p2m mappings, rebuilds the MFN list list, remaps memory, and publishes p2m info to Xen. `xen_setup_kernel_pagetable()` grafts Xen-provided boot tables into Linux tables, converts PFN entries to MFNs, pins the new L4, unpins Xen's initial table, and loads CR3. Runtime mm entry pins page tables read-only, runtime mm exit forces CPUs off stale CR3s and unpins.

State and persistence behavior: Important state includes `xen_reservation_lock`, discontiguous frame scratch arrays, per-CPU logical/current CR3 values, `xen_pt_base/xen_pt_size`, `xen_struct_pages_ready`, vsyscall/identity page-table pages, and the dummy fixmap page. Page `PagePinned`/`PageSavePinned` flags persist page-table validation state across save/restore. PTE constructors store MFNs in hardware tables while exposing PFNs to generic code.

Dependencies and integration points: This file depends on `p2m.c`, Xen multicalls, mmuext/mmu_update hypercalls, page-table locks, `pv_ops.mmu`, x86 paging init, memblock/e820, kexec/vmcore, balloon/foreign mapping, SWIOTLB/DMA contiguous-region creation, and tracepoints.

Risks and test signals: The code is high risk because Linux modifies the CPU's actual page tables under Xen validation. Mistimed RO/pin transitions can fault or corrupt page tables; CR3 lazy updates and cross-CPU stale references must be flushed before unpin. PFN/MFN conversion errors affect all memory access. Test signals include PV boot, process creation/destruction, fork/exec stress, page-table debug warnings, suspend/resume pin/unpin, TLB shootdowns, fixmap/APIC/IOAPIC mappings, DMA contiguous region allocation, foreign VMA remap errors, kdump vmcore note address, and p2m relocation under e820 conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/mmu_pv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/multicalls.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/multicalls.c

Purpose: Implements per-CPU batching for Xen hypercalls through the multicall interface, amortizing trap overhead for MMU, descriptor, and CPU lazy-mode operations.

Important APIs/types/functions: `struct mc_buffer` stores pending multicall entries, argument bytes, and post-flush callbacks. Optional `struct mc_debug_data` records callers and arguments. Public helpers are `xen_mc_flush()`, `__xen_mc_entry()`, `xen_mc_extend_args()`, and `xen_mc_callback()`. Early params/init include `xen_mc_debug` and `mc_debug_enable()`.

Control flow and state: Callers allocate a slot and argument storage in the current CPU buffer. If the buffer or argument area is full, it flushes. Flush disables interrupts, directly invokes single calls or `HYPERVISOR_multicall()` for batches, reports failed entries, resets indices, and runs callbacks such as deferred lock release or CR3 state updates. Debug mode copies entries before executing so failures can print original arguments and callers.

Dependencies and integration points: It depends on Xen hypercall wrappers, per-CPU state, static keys, debugfs-related config, tracepoints, and all PV MMU/CPU code that enters lazy modes.

Risks and test signals: Multicall code assumes non-preemptible callers and per-CPU ordering. Failure reporting is diagnostic only; many failures still WARN/BUG higher up. Callback ordering is part of MMU correctness. Test signals include PV boot under `xen_mc_debug`, lazy MMU batching, descriptor/TLB update stress, no preemptible caller BUGs, and useful logs for injected multicall failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/multicalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/p2m.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/p2m.c

Purpose: Maintains Xen PV physical-to-machine mapping state. It builds the guest-visible linear p2m table, Xen toolstack MFN list tree, sparse missing/identity mappings, dynamic p2m allocation, foreign grant mappings, non-RAM remap support, and optional debugfs p2m dumps.

Important APIs/types/functions: Global exported state includes `xen_p2m_addr`, `xen_p2m_size`, and `xen_max_p2m_pfn`. Key functions include `xen_build_dynamic_phys_to_machine()`, `xen_vmalloc_p2m_tree()`, `xen_build_mfn_list_list()`, `xen_setup_mfn_list_list()`, `get_phys_to_machine()`, `xen_alloc_p2m_entry()`, `set_phys_range_identity()`, `set_phys_to_machine()`, `set_foreign_p2m_mapping()`, `clear_foreign_p2m_mapping()`, `xen_do_remap_nonram()`, `xen_add_remap_nonram()`, and debugfs `p2m_dump_show()`.

Control flow: Boot starts with the domain-builder MFN list in `start_info`, pads invalid entries, then vmallocs a larger sparse p2m area. `xen_rebuild_p2m_list()` maps full p2m pages, shared missing pages, shared identity pages, or shared PMD-level pages depending on contiguous element type. The parallel MFN tree is built for Xen/toolstack access unless `SIF_VIRT_P2M_4TOOLS` is set. Runtime updates allocate missing PMD/PTE/leaf levels under `p2m_update_lock`, bump shared-info `p2m_generation` around visible changes, and update max PFN hints.

State and persistence behavior: Persistent state is split between the linear p2m mapping, `p2m_top_mfn`, `p2m_top_mfn_p`, missing/identity leaf pages, `p2m_generation`, `xen_p2m_last_pfn`, and a small `xen_nonram_remap` table. Foreign grant mappings store `FOREIGN_FRAME` entries and must be cleared on unmap. Identity entries are marked with `IDENTITY_FRAME_BIT` to disambiguate true PFN==MFN mappings.

Dependencies and integration points: It integrates with Xen shared info, grant tables, balloon/unpopulated pages, ACPI ioremap overrides, memblock/vmalloc, page-table population helpers, debugfs root creation, and PV MMU PFN/MFN conversion.

Risks and test signals: Sparse p2m changes are visible to external tools, so generation barriers matter. Foreign mapping failure paths must unmap grants immediately. Non-RAM remap capacity is tiny and fatal on overflow. Test signals include PV boot with sparse/identity p2m, memory hotplug limit sizing, grant map/unmap stress, migration/suspend p2m rebuild, ACPI non-RAM ioremap remap boundaries, debugfs p2m ranges, and toolstack p2m scanning correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/p2m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/platform-pci-unplug.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/platform-pci-unplug.c

Purpose: Handles Xen HVM platform PCI unplug protocol and reports whether PV disk/NIC devices should be considered available alongside or instead of emulated devices.

Important APIs/types/functions: `check_platform_magic()` validates Xen platform I/O port magic/protocol and sends Linux product/version identifiers. Exported predicates include `xen_has_pv_devices()`, `xen_has_pv_nic_devices()`, `xen_has_pv_disk_devices()`, and `xen_has_pv_and_legacy_disk_devices()`. `xen_unplug_emulated_devices()` performs the actual unplug. `parse_xen_emul_unplug()` parses the early `xen_emul_unplug=` parameter.

Control flow and state: Static `xen_emul_unplug` accumulates user/default requested unplug bits; `xen_platform_pci_unplug` records the final post-unplug state. PV/PVH domains always report PV devices; HVM depends on platform PCI availability, user flags, and frontend/platform-driver build-time requirements. Defaults unplug NICs/disks only when matching PV frontends and platform PCI support are compiled. PVH skips unplug because it has no emulated devices.

Dependencies and integration points: It depends on Xen platform I/O ports, frontend availability helpers (`xen_must_unplug_*`), Xen domain predicates, early boot parameters, and HVM guest initialization.

Risks and test signals: Wrong unplug decisions can leave duplicate disk/NIC drivers or remove the boot disk before PV frontend is available. Test signals include HVM boot with blkfront/netfront built-in or modular, `xen_emul_unplug=never/unnecessary/all/...`, host blacklist behavior, unknown protocol warnings, PVH no-op, and correct `xen_has_pv_*` answers for driver probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/platform-pci-unplug.c -->
