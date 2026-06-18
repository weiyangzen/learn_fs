# subset-b-000882 Research

Grouped research report for the requested x86 CPU and MCE source subset. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/feat_ctl.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/feat_ctl.c

Purpose: manages Intel `IA32_FEAT_CTL` policy during CPU initialization, deciding whether VMX and SGX remain exposed to the kernel after BIOS/TXT constraints are applied. With `CONFIG_X86_VMX_FEATURE_NAMES`, it also converts VMX capability MSRs into `cpuinfo_x86::vmx_capability` feature words and legacy `/proc/cpuinfo` synthetic feature bits.

Important APIs and flow: `nosgx` clears SGX early through the `nosgx` boot option. `init_ia32_feat_ctl()` reads `MSR_IA32_FEAT_CTL`, clears VMX/SGX if the MSR is unavailable, decides whether KVM and SGX support require enabling bits, locks the MSR if firmware left it unlocked, writes VMX outside/inside SMX and SGX/SGX_LC bits as appropriate, then updates CPU caps. `init_vmx_capabilities()` reads VMX control, EPT/VPID, VMFUNC, and tertiary control MSRs and derives aggregate APICV/flexpriority/EPT/VPID capability bits.

State and persistence: persistent state is the locked hardware MSR; once locked, later software cannot change feature enablement until reset. The code also mutates per-CPU capability state.

Dependencies and integration: called from Intel CPU initialization and depends on KVM, SGX, TXT/tboot, VMX MSR definitions, and CPU feature infrastructure.

Risks and test signals: ordering is critical because VMX/SGX users trust CPU caps. Regression signals include boot logs for BIOS-disabled VMX/SGX, `/proc/cpuinfo` VMX feature names, KVM load behavior, SGX driver/KVM availability, and boot tests with locked/unlocked firmware MSR values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/feat_ctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/hygon.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/hygon.c

Purpose: registers and initializes Hygon x86 CPUs, mostly following AMD-family behavior with Hygon-specific vendor identity, feature exposure, NUMA correction, cache/TLB detection, and virtualization/security quirks.

Important APIs and flow: `hygon_cpu_dev` supplies early, BSP, regular, and TLB callbacks to `cpu_dev_register()`. `early_init_hygon()` records microcode, maps power bits to constant/nonstop TSC, accumulated power and RAPL, enables syscall32 on x86-64, sets extended APIC ID and VMMCALL capability. `bsp_init_hygon()` checks TSC frequency behavior, enables MWAITX delay, configures LS_CFG-based SSBD if architectural bits are absent, and invokes resctrl detection. `init_hygon()` enables Zen-like features, cacheinfo, NUMA SRAT handling, SVM BIOS-disable detection, LFENCE serialization, ARAT, SYSRET bug marking, null-segment checks, and APIC MSR fence clearing. `cpu_detect_tlb_hygon()` fills global TLB sizing variables from extended CPUID leaves.

State and persistence: state is per-CPU capability/bug flags, global TLB descriptors, NUMA CPU-to-node mapping, and cached SSBD MSR base/mask data. No filesystem persistence.

Dependencies and integration: integrates with generic CPU identification, NUMA, cacheinfo, APIC/SMP, resctrl, speculation-control, SVM, and delay-loop code.

Risks and test signals: risks are misclassified capabilities or NUMA nodes on unusual firmware. Test signals include CPU bring-up logs, `/proc/cpuinfo` flags, SVM availability under BIOS disable, NUMA topology under broken SRAT, cache/TLB reporting, and suspend/idle timing on MWAITX systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/hygon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/hypervisor.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/hypervisor.c

Purpose: detects the active x86 hypervisor early and installs hypervisor-specific platform hooks.

Important APIs and flow: the static `hypervisors[]` table lists configured providers, including Xen, VMware, Hyper-V, KVM, Jailhouse, ACRN, and bhyve. The `nopv` early parameter suppresses paravirtual provider selection unless a provider declares `ignore_nopv`. `detect_hypervisor_vendor()` calls each provider's `detect()` method, keeps the highest priority match, and logs the provider name. `init_hypervisor_platform()` copies non-NULL init/runtime hook arrays from the selected provider into `x86_init.hyper` and `x86_platform.hyper`, sets exported `x86_hyper_type`, and calls the selected `init_platform()` hook.

State and persistence: global boot-time state consists of `nopv`, `x86_hyper_type`, and copied function pointers in x86 platform initialization structures. There is no persistence beyond the running kernel.

Dependencies and integration: depends on provider `struct hypervisor_x86` implementations and the x86 platform hook tables used by time, interrupt, memory, and paravirtual subsystems.

Risks and test signals: detection priority conflicts or `nopv` handling can change boot behavior under nested virtualization. Signals include early boot hypervisor logs, exported hypervisor type, paravirtual feature availability, and boot tests across supported guests with and without `nopv`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/hypervisor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/intel.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/intel.c

Purpose: implements Intel CPU vendor initialization, including early microcode-sensitive mitigations, feature quirks, cache/TLB detection, platform feature enablement, and CPU device registration.

Important APIs and flow: `intel_cpu_dev` registers callbacks for early init, BSP init, full init, and TLB detection. `early_init_intel()` reads microcode/platform ID, disables broken Spectre v2 microcode mitigation features, applies Atom PSE, PAT, PGE, fast-string, physical-address, TSC, CLFLUSH, and TME/MKTME adjustments. `intel_unlock_cpuid_leafs()` clears BIOS CPUID limiting. `init_intel()` layers 32-bit workarounds, cacheinfo, arch perfmon, LFENCE_RDTSC, DS/BTS/PEBS, CLFLUSH/MONITOR bugs, preferred YMM selection for downclock-sensitive ZMM CPUs, NUMA node setup, `init_ia32_feat_ctl()`, `init_intel_misc_features()`, split-lock init, and thermal init. `intel_detect_tlb()` parses CPUID leaf 2 descriptors into global TLB sizing state.

State and persistence: mutates `cpuinfo_x86` feature/bug fields, global ELF HWCAP2 for ring3 MWAIT, per-CPU MSR misc feature shadows, global TLB variables, and boot parameters such as `ring3mwait=disable` and `forcepae`.

Dependencies and integration: integrates with CPU feature flags, microcode, speculation mitigations, memory encryption, KVM/SGX feature control, thermal, resctrl, NUMA, split-lock, and cpuid descriptor helpers.

Risks and test signals: high compatibility risk because small model/stepping table mistakes can expose unsafe features or hide valid ones. Signals include model-specific boot tests, dmesg warnings, mitigation flags, MTRR/PAT behavior, TME physical-bit accounting, KVM/SGX availability, TLB/cache reports, and 32-bit legacy CPU coverage when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/intel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/intel_epb.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/intel_epb.c

Purpose: manages Intel Energy Performance Bias (EPB) across CPU hotplug and system sleep, and exposes a sysfs knob for user policy.

Important APIs and flow: per-CPU `saved_epb` stores the low EPB bits plus an internal saved marker. `intel_epb_save()` reads `MSR_IA32_ENERGY_PERF_BIAS`; `intel_epb_restore()` writes the saved value back or changes firmware-default `performance` to `normal` on first online. Syscore callbacks save/restore the boot CPU during suspend/resume. CPU hotplug callbacks restore EPB on online, save on offline, and merge/unmerge the `power/energy_perf_bias` sysfs group. The sysfs show/store path accepts raw 0-15 values or named strings such as `performance`, `normal`, and `power`. `intel_epb_init()` gates on `X86_FEATURE_EPB`, applies model-specific normal defaults, installs CPUHP state, and registers syscore ops.

State and persistence: EPB lives in per-CPU MSRs and is shadowed in per-CPU RAM across offline/suspend transitions. User writes persist until firmware resets MSRs or the CPU is removed without restore.

Dependencies and integration: depends on CPU hotplug, syscore PM, CPU device sysfs, x86 CPU matching, and MSR access helpers.

Risks and test signals: risks include losing user EPB policy across suspend/hotplug or writing unavailable CPUs. Signals include sysfs read/write behavior, suspend/resume retention, CPU offline/online retention, and boot warning when EPB is normalized from firmware `performance`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/intel_epb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/match.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/match.c

Purpose: provides reusable x86 CPU match-table helpers for code that needs model, feature, stepping, platform, or vendor CPU-type selection.

Important APIs and flow: `x86_match_cpu()` scans an `x86_cpu_id` table until the valid-entry flag ends, matching against `boot_cpu_data` vendor, family, model, stepping bitmask, Intel platform mask, feature bit, and vendor-specific CPU type. `x86_match_vendor_cpu_type()` treats `X86_CPU_TYPE_ANY` as wildcard, intentionally treats hybrid CPUs as matching all CPU types, and otherwise compares Intel or AMD topology-provided type fields. `x86_match_min_microcode_rev()` reuses `x86_match_cpu()` and compares `driver_data` with the boot CPU microcode revision.

State and persistence: read-only against `boot_cpu_data`; no persistence or allocation.

Dependencies and integration: exported to modules and GPL users, and used by Intel EPB, errata, driver matching, and CPU feature code. It depends on stable `asm/cpu_device_id.h` table macros.

Risks and test signals: boot-CPU-only matching assumes homogeneous relevant features. Hybrid CPU wildcard behavior is intentional but can surprise code trying to target only performance or efficiency cores. Signals include module auto-match behavior, microcode-gated feature tests, and table terminator validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/Makefile

Purpose: defines the build composition for x86 machine-check exception support.

Important APIs and flow: `core.o`, `severity.o`, and `genpool.o` are always built for this directory. Optional objects are selected by Kconfig: ancient P5/Winchip handlers, Intel MCE support, AMD MCE support, threshold interrupt support, the `mce-inject` module/object from `inject.o`, APEI bridge support, and legacy `/dev/mcelog`.

State and persistence: no runtime state; this file controls which machine-check code exists in the kernel image or module set.

Dependencies and integration: ties `CONFIG_X86_ANCIENT_MCE`, `CONFIG_X86_MCE_INTEL`, `CONFIG_X86_MCE_AMD`, `CONFIG_X86_MCE_THRESHOLD`, `CONFIG_X86_MCE_INJECT`, `CONFIG_ACPI_APEI`, and `CONFIG_X86_MCELOG_LEGACY` to the implementation files in this folder.

Risks and test signals: incorrect object selection can leave unresolved symbols or silently remove vendor handling. Signals are configuration matrix builds, module build for injection, and boot tests with optional legacy and ACPI APEI paths enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/amd.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/amd.c

Purpose: implements AMD/Hygon-style machine-check support: SMCA bank discovery, threshold and deferred-error interrupt setup, vendor errata filtering, memory-error classification, bank clearing, storm handling, and per-CPU threshold sysfs objects.

Important APIs and flow: `mce_amd_feature_init()` applies CPU quirks, enables AMD thresholding, sets SMCA interrupt vectors, configures each bank with `smca_configure()`, disables known-bad thresholding, walks threshold blocks, and initializes their limits/APIC routing. `smca_bsp_init()` installs AMD threshold and deferred interrupt vectors. `amd_filter_mce()`, `amd_mce_is_memory_error()`, and `amd_mce_usable_address()` feed the common MCE pipeline. `amd_clear_bank()` resets threshold limits and clears MCA_STATUS or SMCA DESTAT as appropriate. `sysvec_deferred_error` handles deferred-error APIC delivery by polling deferred banks. `mce_threshold_create_device()` and removal helpers create per-CPU machinecheck sysfs kobjects for bank/block threshold control.

State and persistence: maintains per-CPU AMD bank data, SMCA bank descriptors/counts, threshold-bank object pointers, bank maps, interrupt-bank bitmaps, threshold limit state in MCA_MISC/SMCA MSRs, and global vector function pointers. Sysfs changes immediately reprogram hardware threshold MSRs but are not persistent across reboot.

Dependencies and integration: depends on common MCE core, APIC extended LVT setup, CPU hotplug-created MCE devices, APEI threshold defaults, AMD NB/topology definitions, and SMCA MSR layouts.

Risks and test signals: risks include wrong SMCA bank naming, interrupt routing mistakes, stale sysfs objects during hotplug, and incorrect usable-address classification. Signals include AMD SMCA boot logs, threshold interrupt injection, deferred-error injection, sysfs threshold read/write tests, hotplug create/remove tests, and EDAC/RAS decoding of UMC memory errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/amd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/apei.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/apei.c

Purpose: bridges ACPI APEI/GHES/ERST hardware error reporting with the x86 MCE logging format.

Important APIs and flow: `apei_mce_report_mem_error()` converts CPER memory errors with physical addresses into synthetic `struct mce` records and queues them with severity-dependent UC/PCC bits. `apei_smca_report_x86_error()` imports SMCA register arrays from CPER processor context, maps the LAPIC ID to a CPU, decodes fixed SMCA register layout fields, and logs the record. `apei_write_mce()` serializes a fatal MCE into a CPER record and writes it to ERST. `apei_read_mce()`, `apei_check_mce()`, and `apei_clear_mce()` support legacy mcelog reads of persistent records after reboot.

State and persistence: normal GHES reports are queued in memory through MCE logging. Fatal records can persist across reboot in ERST until read and cleared.

Dependencies and integration: depends on ACPI APEI, GHES, CPER structures, ERST storage, common MCE prep/log helpers, and SMCA feature checks.

Risks and test signals: address-mask handling and SMCA register-count validation are key correctness points. Signals include GHES corrected-memory reports appearing as MCE records, ERST write/read/clear behavior after fatal MCE, and BERT/CPER SMCA import tests with valid and invalid register layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/apei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/core.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/core.c

Purpose: implements the generic x86 Machine Check Architecture runtime: record preparation, polling, #MC exception handling, severity-driven recovery/panic, notifier dispatch, timers, boot/hotplug setup, sysfs controls, suspend/shutdown behavior, and debugfs hooks.

Important APIs and flow: `mce_prep_record*()` fills common/per-CPU `struct mce` fields. `mce_log()` queues records into the genpool and schedules work. `machine_check_poll()` scans configured banks, reads status/auxiliary registers, tracks storms, logs eligible corrected/deferred events, and clears banks. `do_machine_check()` is the core #MC path: handles ancient CPU redirection, gathers MCG state, finds fatal banks with `mce_no_way_out()`, coordinates broadcast MCEs through monarch/subject state (`mce_start()`, `mce_end()`, `mce_reign()`), scans banks, logs records, clears state, and either panics or schedules task work for user/kernel-recoverable memory failures. `mcheck_cpu_init()` and `mca_bsp_init()` initialize bank counts, vendor features, MCG control, bootlog polling, timers, and CR4.MCE. Device init registers the machinecheck bus, per-CPU devices, bank sysfs attributes, CPU hotplug callbacks, and syscore PM callbacks.

State and persistence: central state includes `mca_cfg`, `mce_flags`, per-CPU bank arrays/counts/poll masks/timers/last errors, global CE-disabled banks, monarch synchronization atomics, queued genpool records, sysfs-configurable bank masks and policy flags, and debugfs fake-panic state. APEI may persist fatal records through ERST; core itself keeps runtime state only.

Dependencies and integration: integrates with vendor MCE files, severity grading, genpool/notifier dispatch, legacy mcelog, memory failure/hwpoison, APIC CMCI/threshold code, CPU hotplug, syscore PM, tracepoints, kexec crash handling, TDX auxiliary data, and debugfs/sysfs.

Risks and test signals: this code runs in #MC/NMI-like contexts, so locking, instrumentation, duplicate shared-bank reporting, and recovery decisions are high risk. Signals include MCE injection, CMCI/deferred threshold tests, memory_failure recovery tests, sysfs policy changes, suspend/resume, CPU hotplug, bootlog processing, fake panic debugfs coverage, and panic-path console output stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/dev-mcelog.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/dev-mcelog.c

Purpose: provides the legacy `/dev/mcelog` misc device and helper trigger interface for user-space MCE consumers.

Important APIs and flow: `dev_mce_log()` is a notifier that copies decoded MCEs into a fixed in-memory ring-like buffer, marks overflow, wakes pollers, and marks non-AMD records handled by mcelog. `mce_work_trigger()` schedules an optional usermode helper configured through the `trigger` sysfs attribute. Character device operations implement exclusive open, full-buffer reads that first drain APEI ERST records, poll readiness, privileged ioctls for record length/log length/flags, and privileged writes that call the injector notifier chain. `dev_mcelog_init_device()` allocates the buffer, registers the misc device, and registers the decode notifier.

State and persistence: state includes the allocated `mce_log_buffer`, open/exclusive counters, trigger helper path, waitqueue, APEI-read completion flag, and injector notifier chain. APEI records may originate from persistent ERST storage but are cleared after read.

Dependencies and integration: depends on common MCE notifier priorities, APEI helpers, miscdevice, usermodehelper, poll/ioctl APIs, and optional injection support.

Risks and test signals: legacy ABI expectations are strict; buffer full behavior discards new entries. Signals include `/dev/mcelog` read/ioctl/poll tests, helper trigger execution, exclusive-open behavior, ERST drain ordering, and injection writes with `CAP_SYS_ADMIN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/dev-mcelog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/genpool.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/genpool.c

Purpose: supplies a lockless, preallocated event pool for MCE records captured in machine-check context, where normal allocation and printk paths are unsafe.

Important APIs and flow: `mce_gen_pool_init()` lazily creates a `gen_pool` sized to at least 80 records or two records per possible CPU. `mce_gen_pool_add()` filters vendor-ignored records, allocates a node, copies the `mce_hw_err`, and pushes it onto a lockless list. `mce_gen_pool_process()` drains and reverses the list in workqueue context, calls the MCE decoder notifier chain for each record, and frees nodes back to the pool. `mce_gen_pool_prepare_records()` is panic-path support that drains records, reverses them into chronological order, and drops duplicates before console printing.

State and persistence: global state is the fixed gen_pool and lockless event list. Records persist only until processed, panic-dumped, or lost due to pool exhaustion.

Dependencies and integration: used by `mce_log()`, MCE workqueue processing, panic dumping, vendor filters, and decoder notifier consumers.

Risks and test signals: pool exhaustion can drop records, while duplicate suppression relies on bank/status/address/misc comparison. Signals include injection bursts, panic-path duplicate logs, notifier ordering, and pool-full ratelimited warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/genpool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/inject.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/inject.c

Purpose: implements the MCE injection test module, exposing debugfs controls for software decode-only records, hardware #MC injection, deferred-error interrupts, and threshold interrupts.

Important APIs and flow: debugfs files under `mce-inject` write fields in the global `i_mce` record (`status`, `misc`, `addr`, `synd`, `ipid`, `cpu`, `flags`, `bank`). Writing `bank` validates the target bank and triggers `do_inject()`. Software injection queues the record through `mce_log()`. Hardware and interrupt modes set MCA/SMCA MSRs on the target CPU with `prepare_msrs()`, temporarily enable HWCR injection, then trigger int18, deferred vector, or threshold vector. The module also registers a legacy mcelog injector notifier and an NMI handler for broadcast/random-context injection paths.

State and persistence: runtime state includes `i_mce`, injection type, hardware-injection availability, debugfs dentries, a cpumask for broadcast injection, and per-CPU `injectm` records used by MCE MSR wrappers. No persistence beyond module lifetime.

Dependencies and integration: depends on common MCE core, AMD SMCA/HWCR behavior, APIC/NMI/IPI delivery, debugfs, CPU hotplug read locks, legacy mcelog write notifier, and optional AMD northbridge PCI configuration.

Risks and test signals: hardware injection can panic the system by design, and platform firmware may block writes to status MSRs. Signals include debugfs mode parsing, software decode records, fake-panic-protected #MC injection, deferred/threshold vector delivery, invalid CPU/bank rejection, and cleanup on module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/intel.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/intel.c

Purpose: implements Intel/Zhaoxin MCE vendor features, especially CMCI ownership/discovery, local machine-check enablement, memory-controller logging, vendor quirks, filtering, and usable-address validation.

Important APIs and flow: `mce_intel_feature_init()` applies bank quirks, initializes CMCI, enables LMCE, and enables selected integrated memory controller logs. `cmci_supported()` validates configuration, APIC, vendor, and `MCG_CMCI_P`. `cmci_discover()` scans banks under a raw lock, skips firmware-owned or already-owned banks, chooses thresholds, claims banks by setting `MCI_CTL2_CMCI_EN`, clears polled banks, and handles inherited storm thresholds. `intel_threshold_interrupt()` polls owned banks. CPU hotplug paths call `cmci_clear()`, `cmci_rediscover()`, and `cmci_reenable()` through core callbacks. `intel_init_lmce()` gates LMCE on MCG_CAP and locked `IA32_FEAT_CTL`; `intel_filter_mce()` filters known erratum signatures; `intel_mce_usable_address()` accepts only page-granularity physical-address reports.

State and persistence: per-CPU owned-bank masks, global CMCI threshold defaults, storm state in common threshold code, and hardware MCi_CTL2/MCG_EXT_CTL MSRs. State is reestablished on CPU hotplug/resume.

Dependencies and integration: depends on common MCE polling, APIC CMCI vector, threshold storm handling, feature-control setup, CPU hotplug, and Intel model tables.

Risks and test signals: shared-bank ownership and storm thresholds are race-sensitive. Signals include CMCI interrupt delivery, shared-bank rediscovery after hotplug, `mce=no_cmci`/`ignore_ce`, LMCE enable bits, storm begin/end logs, and injection/filter tests for known errata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/intel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/internal.h -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/internal.h

Purpose: defines the private interface and shared data contracts for the x86 MCE implementation.

Important APIs and types: declares severity levels, event-list nodes, genpool functions, decoder chain, Intel/AMD/threshold/APEI/injection hooks with stubs for disabled configs, storm tracking structures, `mca_config`, `mce_vendor_flags`, per-bank `struct mce_bank`, vendor helpers, and MSR helpers. `mce_cmp()` defines duplicate equivalence by bank/status/address/misc. `smca_extract_err_addr()` normalizes SMCA error addresses based on bank configuration. `mca_msr_reg()` maps logical bank/register enums to SMCA or legacy MCA MSR addresses.

State and persistence: this header declares global and per-CPU state owned by implementation files: `mca_cfg`, `mce_flags`, bank arrays, bank counts, storm descriptors, CE-disabled banks, and poll hooks. It has no storage except inline behavior.

Dependencies and integration: included by all MCE implementation files and bridges optional Kconfig features while keeping core code buildable with stubs.

Risks and test signals: contract drift can break subtle build combinations or wrong MSR selection. Signals include all relevant Kconfig matrix builds, SMCA and legacy bank access tests, and duplicate/panic-path record behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/p5.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/p5.c

Purpose: supports old Intel Pentium-style machine-check reporting when ancient MCE support is enabled.

Important APIs and flow: global `mce_p5_enabled` defaults off. `pentium_machine_check()` reads `MSR_IA32_P5_MC_ADDR` and `MSR_IA32_P5_MC_TYPE`, prints emergency diagnostics including possible thermal failure, and taints the kernel. `intel_p5_mcheck_init()` only enables this path when requested, verifies `X86_FEATURE_MCE`, reads the old MSRs to clear/prime state, sets CR4.MCE, and logs enablement.

State and persistence: state is the global enable flag, CR4.MCE, and old machine-check MSRs. No persistent records or sysfs state.

Dependencies and integration: called from common ancient CPU detection in MCE core and used by `do_machine_check()` when `mce_flags.p5` is set.

Risks and test signals: hardware is rare and often miswired, explaining the default-off behavior. Signals are limited to legacy boot tests with `mce` enabling, int18 handling, and emergency log output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/p5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/severity.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/severity.c

Purpose: grades MCE records into recovery, keep, deferred, uncorrected, action-required, or panic severities.

Important APIs and flow: Intel-compatible grading is table-driven through `severities[]`; first matching rule wins using status masks, MCG status masks, software error recovery availability, exception context, CPU model/stepping, and bank ranges. `error_context()` classifies user, kernel, or recoverable-kernel context, using exception-table fixup types and instruction decoding to identify copy-from-user accesses. AMD/Hygon grading in `mce_severity_amd()` follows PPR-style logic: PCC panics, deferred errors are deferred, corrected errors are kept, overflow without recovery panics, lack of SUCCOR panics, and unrecoverable kernel context panics. `mce_severity()` dispatches by vendor. Debugfs `severities-coverage` reports and resets which Intel rules have been exercised.

State and persistence: mutates `m->kflags` for recoverable kernel/copyin paths and records debugfs coverage bits in the severity table. No persistence beyond runtime.

Dependencies and integration: central to `machine_check_poll()` and `do_machine_check()`, and depends on memory failure configuration, exception tables, instruction decoder, CPU model IDs, and common `mca_cfg`.

Risks and test signals: rule ordering is safety-critical; a too-low severity can allow corruption, while a too-high severity panics unnecessarily. Signals include injection coverage for table rules, copy-from-user recovery tests, memory_failure-enabled/disabled builds, AMD deferred/SUCCOR cases, and debugfs coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/severity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/threshold.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/threshold.c

Purpose: provides common threshold interrupt handling and CMCI/threshold storm tracking for corrected machine-check events.

Important APIs and flow: `mce_save_apei_thr_limit()` stores a firmware-provided corrected-error threshold limit for AMD threshold setup. `sysvec_threshold()` dispatches the threshold APIC vector through `mce_threshold_vector`, defaulting to a warning until a vendor installs a handler. Per-CPU `storm_desc` tracks bank histories, storm counts, and poll mode. `mce_track_storm()` shifts per-bank history by elapsed seconds, records corrected errors, starts storm mode when recent errors exceed `STORM_BEGIN_THRESHOLD`, and ends it after enough clean polls. `cmci_storm_begin()` enables polling and kicks the MCE timer; `cmci_storm_end()` restores normal polling ownership. `mce_handle_storm()` delegates threshold changes to Intel or AMD vendor code.

State and persistence: state is the APEI threshold limit, vector function pointer, and per-CPU storm descriptors. It is runtime-only and rebuilt after boot/hotplug.

Dependencies and integration: used by Intel CMCI, AMD thresholding, common polling timers, APIC vector entry code, and APEI HEST threshold reporting.

Risks and test signals: storm transitions can suppress or duplicate corrected error reporting if thresholds are wrong. Signals include corrected-error flood injection, storm begin/end logs, timer interval behavior, and vendor threshold restoration after storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/threshold.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/winchip.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/winchip.c

Purpose: supports IDT WinChip C6 machine-check reporting for ancient x86 configurations.

Important APIs and flow: `winchip_machine_check()` prints an emergency machine-check message and taints the kernel. `winchip_mcheck_init()` reads `MSR_IDT_FCR1`, enables EIERRINT and MCE reporting bits, writes the MSR back, sets CR4.MCE, and logs enablement for CPU0.

State and persistence: state is hardware MSR configuration, CR4.MCE, and `mce_flags.winchip` set by common core. No queued records or persistent storage.

Dependencies and integration: selected by ancient MCE support and invoked from common CPU init/exception redirection for Centaur family 5.

Risks and test signals: minimal modern coverage and hardware scarcity. Signals are build coverage with `CONFIG_X86_ANCIENT_MCE`, boot on supported WinChip hardware or emulator, and int18 emergency log behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/winchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/Makefile

Purpose: defines the build composition for x86 CPU microcode loading support.

Important APIs and flow: `microcode-y := core.o` builds the common loader core. `obj-$(CONFIG_MICROCODE) += microcode.o` includes the aggregate object when microcode support is enabled. Vendor-specific objects are included conditionally: `intel.o` for `CONFIG_CPU_SUP_INTEL` and `amd.o` for `CONFIG_CPU_SUP_AMD`.

State and persistence: no runtime state; it controls which microcode implementation objects are linked.

Dependencies and integration: ties CPU vendor support Kconfig to the microcode subsystem used by CPU bring-up and mitigation code, including Intel initialization that reads current microcode revisions.

Risks and test signals: wrong object selection can break vendor microcode loading or leave common code without a vendor backend. Signals are Kconfig build matrix coverage and boot-time microcode update logs on Intel-only, AMD-only, and mixed-capability configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/Makefile -->
