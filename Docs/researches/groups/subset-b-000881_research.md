# subset-b-000881 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/bugs.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/bugs.c

## Purpose
`bugs.c` is the x86 speculative-execution and CPU-vulnerability mitigation coordinator. It selects, updates, applies, and reports mitigations for Spectre v1/v2, Spectre BHI, Retbleed, SRSO, ITS, TSA, VMSCAPE, SSB, L1TF, MDS, TAA, MMIO stale data, RFDS, SRBDS, GDS, iTLB multihit, old microcode, and related SMT-sensitive cases. It is intentionally centralized because many mitigations share MSRs, static keys, return thunks, VERW clearing, IBPB/STIBP policy, SMT policy, KVM exposure, and `/sys/devices/system/cpu/vulnerabilities/*` output.

## Important APIs, Types, and Functions
Key exported/shared state includes `x86_spec_ctrl_base`, per-CPU `x86_spec_ctrl_current`, per-CPU `x86_ibpb_exit_to_user`, `x86_pred_cmd`, `x86_return_thunk`, `switch_to_cond_stibp`, `switch_mm_cond_ibpb`, `switch_mm_always_ibpb`, `switch_vcpu_ibpb`, `cpu_buf_idle_clear`, and `switch_mm_cond_l1d_flush`. KVM-visible exports include `x86_virt_spec_ctrl()`, `switch_vcpu_ibpb`, `itlb_multihit_kvm_mitigation`, `l1tf_mitigation`, `l1tf_vmx_mitigation`, and `gds_ucode_mitigated()`.

The file follows a common pattern for each vulnerability: `<vuln>_select_mitigation()` chooses a mode from CPU bug flags, boot parameters, compile-time config, attack-vector controls, and hardware support; optional `<vuln>_update_mitigation()` resolves cross-mitigation dependencies; `<vuln>_apply_mitigation()` mutates CPU caps, MSRs, static keys, SMT state, or thunks. `cpu_select_mitigations()` is the top-level boot orchestrator. `cpu_bugs_smt_update()` reacts to SMT state changes after boot.

Important runtime APIs are `update_spec_ctrl_cond()`, `spec_ctrl_current()`, `x86_spec_ctrl_setup_ap()`, `arch_prctl_spec_ctrl_set()`, `arch_prctl_spec_ctrl_get()`, and `arch_seccomp_spec_mitigate()`. These connect the boot-selected policy to context switch, seccomp, prctl, vCPU load, AP startup, and return-to-user paths.

## Control Flow
Early boot parameter handlers such as `mds=`, `tsx_async_abort=`, `mmio_stale_data=`, `reg_file_data_sampling=`, `srbds=`, `l1d_flush=`, `gather_data_sampling=`, `nospectre_v1`, `retbleed=`, `indirect_target_selection=`, `tsa=`, `spectre_v2_user=`, `nospectre_v2`, `spectre_v2=`, `spectre_bhi=`, `nospec_store_bypass_disable`, `spec_store_bypass_disable=`, `l1tf=`, `spec_rstack_overflow=`, and `vmscape=` seed mode globals before mitigation selection.

`cpu_select_mitigations()` first reads `MSR_IA32_SPEC_CTRL` into `x86_spec_ctrl_base`, clears inherited mitigation bits from kexec, reads `MSR_IA32_ARCH_CAPABILITIES`, and prints active attack-vector policy. It then runs all selection functions before alternatives are patched, runs update functions in dependency order, then applies each mitigation. Ordering matters: Spectre v2 selection feeds Retbleed, ITS, BHI, and Spectre v2 user handling; Retbleed can force Spectre v2 user STIBP behavior and can satisfy SRSO/VMSCAPE IBPB needs; MDS/TAA/MMIO/RFDS share `verw_clear_cpu_buf_mitigation_selected`.

`cpu_bugs_smt_update()` is invoked when SMT state changes. It updates STIBP static keys or `SPEC_CTRL_STIBP`, toggles buffer clearing for MDS/TSA cases, and emits one-time warnings when SMT leaves a selected mitigation incomplete.

`arch_prctl_spec_ctrl_set()` and `arch_prctl_spec_ctrl_get()` route `PR_SPEC_STORE_BYPASS`, `PR_SPEC_INDIRECT_BRANCH`, and `PR_SPEC_L1D_FLUSH` to per-task flag handlers. Current-task updates immediately call speculation-control update paths; non-current task changes are delayed until scheduling.

## State and Persistence
Most mitigation decisions are `__ro_after_init` globals. Runtime mutable state is deliberately narrow: per-CPU cached SPEC_CTRL values, per-task speculation flags, static keys for context-switch and idle paths, KVM-visible globals, and SMT-dependent STIBP/buffer-clear adjustments. MSR state persists per CPU until changed, so AP startup calls `x86_spec_ctrl_setup_ap()`, `update_srbds_msr()`, and `update_gds_msr()` from the CPU bring-up path in `common.c`.

Sysfs vulnerability output is generated from the selected globals and current SMT/static-key state. These files are observations of kernel state, not stored configuration.

## Dependencies and Integration Points
This file depends on CPU bug bits from `common.c`, capability clearing/forcing from `cpuid-deps.c`, CPU attack-vector controls, SMT scheduling state, BPF unprivileged state, KVM headers, x86 MSR helpers, return thunk symbols, alternatives/static keys, x86 FPU/entry flags, E820 memory ranges for L1TF, and hypervisor detection. It integrates with process APIs through `prctl` and seccomp, with KVM through exported mitigation variables/functions, with CPU hotplug through AP setup and SMT update callbacks, and with sysfs through `cpu_show_*()` vulnerability attributes.

## Risks
The main risk is ordering: moving select/update/apply calls can leave related mitigations inconsistent, for example STIBP mode before Retbleed resolution, ITS before Spectre v2 retpoline mode, or VERW state before MDS/TAA/MMIO/RFDS updates. MSR writes must preserve reserved bits via `x86_spec_ctrl_base`. Static keys must only be enabled when the entry/context-switch code has matching alternatives. SMT warnings and disablement must not over-disable systems unless a selected mode explicitly asks for `nosmt` or global SMT mitigation policy requires it. Sysfs strings are ABI-like and are used by tests and admin tooling.

## Test Signals
Useful validation signals are boot logs with `mitigations:` and per-vulnerability prefixes, `/sys/devices/system/cpu/vulnerabilities/*` contents, `prctl(PR_SET_SPECULATION_CTRL/PR_GET_SPECULATION_CTRL)` behavior for SSB, indirect branch, and L1D flush, CPU hotplug/AP bring-up on affected hardware, KVM module behavior for exported mitigation state, unprivileged eBPF warnings, SMT on/off transitions, and command-line matrix tests for each early parameter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/bugs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/bus_lock.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/bus_lock.c

## Purpose
`bus_lock.c` implements x86 split-lock and bus-lock detection policy. It discovers whether the processor safely supports split-lock detection, parses `split_lock_detect=`, configures `MSR_TEST_CTRL` and `MSR_IA32_DEBUGCTLMSR`, handles user and guest split-lock traps, rate-limits bus-lock traps, and exposes `/proc/sys/kernel/split_lock_mitigate` when sysctl is enabled.

## Important APIs, Types, and Functions
`enum split_lock_detect_state` defines `off`, `warn`, `fatal`, and `ratelimit`. Global state includes `sld_state`, cached `msr_test_ctrl_cache`, `cpu_model_supports_sld`, `bld_ratelimit`, `sysctl_sld_mitigate`, and `buslock_sem`. Public integration points are `sld_setup()`, `split_lock_init()`, `bus_lock_init()`, `handle_guest_split_lock()`, `handle_user_split_lock()`, and `handle_bus_lock()`.

`split_lock_setup()` validates model/MSR support and enables `X86_FEATURE_SPLIT_LOCK_DETECT`. `sld_state_setup()` parses the boot parameter. `sld_update_msr()` toggles split-lock detection from the cached MSR value. `split_lock_warn()` provides the "misery" mitigation by delaying, serializing progress through `buslock_sem`, scheduling delayed re-enable work, and temporarily disabling split-lock detection on the current CPU.

## Control Flow
Early CPU identification calls `sld_setup(c)` from `common.c`. That probes known CPU models or `MSR_IA32_CORE_CAPS`, verifies `MSR_TEST_CTRL` writes, parses the command line, and prints selected behavior. Per-CPU initialization calls `split_lock_init()`: in rate-limit mode it disables split-lock #AC detection so bus locks are handled by #DB; otherwise it enables or disables split-lock detection according to `sld_state`.

Normal operation splits by trap type. `handle_user_split_lock()` handles #AC for user split locks and either returns false for fatal/alignment-check cases or warns and resumes. `handle_guest_split_lock()` lets KVM convert guest split locks into warn or SIGBUS behavior. `handle_bus_lock()` handles #DB bus-lock traps and applies warn, fatal, or rate-limit policy. `bus_lock_init()` programs `DEBUGCTLMSR_BUS_LOCK_DETECT` when bus-lock detection should be used.

## State and Persistence
The selected mode and cached MSR value are `__ro_after_init`; runtime state is the sysctl mitigation switch, per-task `reported_split_lock`, delayed works, ratelimit bucket, and semaphore. Split-lock MSR state is per core but treated per CPU; offline callback `splitlock_cpu_offline()` unconditionally re-enables detection to avoid sibling CPUs being left with detection disabled.

## Dependencies and Integration Points
The file depends on CPUID/CPU model matching, command-line parsing, MSR helpers, trap handling, workqueues, CPU hotplug, sysctl, ratelimit, and KVM exports. It is called by `common.c` during CPU identification and by trap/KVM paths when #AC or #DB events occur.

## Risks
`MSR_TEST_CTRL` must only be touched on known-safe CPUs; the file explicitly warns that unsupported writes can be unsafe. The temporary disable/re-enable path is sensitive to CPU hotplug and HT sibling behavior. Rate-limit parsing allows `ratelimit:N` only in 1..1000, so invalid input silently falls back to default. `sysctl_sld_mitigate=0` removes the semaphore/sleep mitigation and allows more concurrent bus-locked progress.

## Test Signals
Boot with `split_lock_detect=off|warn|fatal|ratelimit:N` and inspect dmesg for #AC/#DB policy. Trigger user split locks to verify warning, SIGBUS, or rate limiting. Exercise KVM guest split-lock handling via `handle_guest_split_lock()`. Toggle `/proc/sys/kernel/split_lock_mitigate` and hotplug CPUs while delayed re-enable work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/bus_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/cacheinfo.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/cacheinfo.c

## Purpose
`cacheinfo.c` detects x86 cache topology, populates Linux cacheinfo leaves, maintains shared L2/LLC CPU masks, and coordinates cache-disable/cache-enable sequences used by MTRR and PAT programming. It supports Intel deterministic CPUID leaf 4, legacy Intel descriptor leaf 2, AMD/Hygon deterministic leaf `0x8000001d`, and legacy AMD cache leaves.

## Important APIs, Types, and Functions
Per-CPU state includes `cpu_llc_shared_map` and `cpu_l2c_shared_map`; global cache-control state includes `memory_caching_control`, `cpu_cacheinfo_mask`, `cache_aps_delayed_init`, `saved_cr4`, and `cache_disable_lock`.

Detection helpers include `_cpuid4_*` unions, `_cpuid4_info`, `legacy_amd_cpuid4()`, `amd_fill_cpuid4_info()`, `intel_fill_cpuid4_info()`, `fill_cpuid4_info()`, `find_num_cache_leaves()`, `get_cache_id()`, `calc_cache_topo_id()`, `intel_cacheinfo_0x2()`, and `intel_cacheinfo_0x4()`. Public/vendor APIs include `cacheinfo_amd_init_llc_id()`, `cacheinfo_hygon_init_llc_id()`, `init_amd_cacheinfo()`, `init_hygon_cacheinfo()`, `init_intel_cacheinfo()`, `init_cache_level()`, and `populate_cache_leaves()`.

Cache-control APIs are `cache_disable()`, `cache_enable()`, `cache_bp_init()`, `cache_bp_restore()`, `cache_aps_init()`, `set_cache_aps_delayed_init()`, and `get_cache_aps_delayed_init()`.

## Control Flow
Vendor CPU initialization calls `init_*_cacheinfo()` to set cache sizes, LLC IDs, L2 IDs, and cache leaf counts. Intel first tries CPUID leaf 4, accumulating L1/L2/L3 sizes and topology IDs, and falls back to CPUID leaf 2 descriptor parsing through `cpuid_0x2_table`. AMD/Hygon use deterministic leaf `0x8000001d` when topology extensions are available, otherwise `legacy_amd_cpuid4()` synthesizes leaf-4-like data from leaves `0x80000005` and `0x80000006`.

The generic cacheinfo framework calls `init_cache_level()` and `populate_cache_leaves()`. `populate_cache_leaves()` fills each `struct cacheinfo`, computes cache IDs, attaches AMD northbridge private data for L3 when available, and populates shared CPU maps using AMD/Hygon special cases or APIC-ID-derived sharing.

Boot cache-control starts with `cache_bp_init()`, which initializes MTRR/PAT state and programs the boot CPU when `memory_caching_control` requests it. AP handling is registered by `cache_ap_register()`. AP cache programming is either delayed until `cache_aps_init()` or run on online hotplug via `stop_machine_from_inactive_cpu()`.

## State and Persistence
Detected cache topology is stored in `cpuinfo_x86` topology fields and per-CPU `struct cpu_cacheinfo` lists. Shared CPU maps evolve with CPU online/offline state. MTRR/PAT programming persists in CPU MSRs and must be replayed on boot CPU restore, AP startup, resume, and hotplug. `cache_disable()` temporarily changes CR0.CD and CR4.PGE, disables MTRRs, flushes caches/TLBs, and serializes the sequence with a raw spinlock; `cache_enable()` reverses it.

## Dependencies and Integration Points
The file depends on `linux/cacheinfo`, CPU hotplug, stop_machine, CPUID helpers, AMD northbridge L3 support, MTRR, PAT, TLB flush accounting, APIC topology from `cpu_data`, and the Intel leaf-2 descriptor table. It feeds sysfs cacheinfo, scheduler/topology assumptions about LLC sharing, and memory type initialization.

## Risks
Cache size/topology detection is vendor-specific and CPUID-dependent; wrong sharing IDs can mislead scheduler/cacheinfo consumers. Legacy AMD fallback must handle invalid associativity encodings. Cache-disable sequences are high-risk because interrupts must already be disabled by the caller and because only the local CPU is cache-disabled while MTRRs are changed. Hotplug ordering is delicate: MTRR mutex cannot be held in early AP startup, so the code relies on stop_machine and cpuhotplug locking assumptions.

## Test Signals
Validate `/sys/devices/system/cpu/cpu*/cache/index*` size, type, ID, and shared CPU maps on Intel, AMD, Hygon, SMT, multi-die, and no-L3 systems. Exercise CPU hotplug and resume paths with MTRR/PAT enabled. Compare dmesg cache/TLB output and `lscpu -C` against expected CPUID. Run with delayed AP cache initialization both true and false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/cacheinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/centaur.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/centaur.c

## Purpose
`centaur.c` provides the x86 vendor driver for Centaur/VIA/Zhaoxin-style CPUs identified by `CentaurHauls`. It performs early feature normalization, enables legacy VIA/Centaur crypto and RNG units, handles old 32-bit WinChip/C3 quirks, fixes cache reporting, and registers the vendor with the generic CPU identification framework.

## Important APIs, Types, and Functions
The central registered object is `centaur_cpu_dev`, with `c_early_init = early_init_centaur`, `c_init = init_centaur`, optional 32-bit `legacy_cache_size = centaur_size_cache`, and `c_x86_vendor = X86_VENDOR_CENTAUR`.

`early_init_centaur()` sets `X86_FEATURE_CENTAUR_MCR` on family 5 32-bit systems, marks constant/nonstop TSC based on family/model and `x86_power`, and runs before full vendor init. `init_centaur()` calls `init_intel_cacheinfo()`, detects architectural perfmon, handles family 5 FCR/model-name setup on 32-bit, calls `init_c3()` for family 6+ units, forces `LFENCE_RDTSC` on 64-bit, and finishes with `init_ia32_feat_ctl()`. `init_c3()` enables ACE crypto and RNG via VIA MSRs and sets feature bits.

## Control Flow
`cpu_dev_register(centaur_cpu_dev)` places the descriptor in the `.x86_cpu_dev.init` section. `common.c` discovers it in `init_cpu_devs()`, matches `CentaurHauls`, runs early init during early boot, and later runs full init from `identify_cpu()`. Cache reporting uses Intel paths because these CPUs expose compatible cache leaves/descriptors.

On 32-bit family 5, `init_centaur()` rewrites FCR bits for specific WinChip models, may clear broken TSC, sets Centaur MCR/CX8/3DNow capabilities, reads extended cache leaves when present, and builds a model string. On C3-family systems it enables ACE/RNG if the extended Centaur CPUID leaf reports units present but disabled.

## State and Persistence
State is mainly in `struct cpuinfo_x86` feature, cache, and model fields. MSR writes to VIA FCR/RNG registers persist for the running CPU. Feature corrections are not stored outside CPU caps but become part of the boot CPU common capability set and per-CPU state.

## Dependencies and Integration Points
The file depends on x86 CPUID helpers, MSR helpers, MTRR, E820, scheduler clock headers, and generic `cpu.h` vendor registration. It integrates with `common.c` CPU identification and with `cacheinfo.c` through `init_intel_cacheinfo()`.

## Risks
Much of the 32-bit logic touches old model-specific FCR bits; incorrect model matching could expose broken TSC or wrong cache sizes. ACE/RNG enablement assumes VIA extended CPUID/MSRs behave as expected. The code is low churn but covers rare hardware, so regressions are likely to be found only by boot testing on affected systems or emulation.

## Test Signals
Boot on Centaur/VIA/Zhaoxin hardware or targeted emulation and check CPU vendor/model, feature flags for ACE/RNG/CX8/3DNow/REP_GOOD/constant TSC, cacheinfo output, and dmesg lines for ACE/RNG enablement or FCR changes. On old 32-bit models, verify TSC stability decisions and `centaur_size_cache()` corrections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/centaur.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/common.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/common.c

## Purpose
`common.c` is the main x86 CPU bring-up and feature-normalization pipeline. It owns early and full CPU identification, vendor driver dispatch, CPUID feature collection, bug-bit enumeration, command-line feature overrides, control-register setup/pinning, per-CPU GDT/TSS/syscall/debug state, boot and secondary CPU finalization, late microcode feature checks, SMT update hooks, and the final handoff to mitigation and alternatives setup.

## Important APIs, Types, and Functions
Global/per-CPU state includes `cpu_info`, `USER_PTR_MAX`, `elf_hwcap2`, topology count exports (`__max_threads_per_core`, `__max_dies_per_package`, `__max_logical_packages`, `__num_nodes_per_package`, `__num_cores_per_package`, `__num_threads_per_package`), `gdt_page`, forced capability bitmaps `cpu_caps_cleared` and `cpu_caps_set`, `current_task`, `__preempt_count`, `cpu_current_top_of_stack`, `__x86_call_depth`, and `__stack_chk_guard`.

CPU detection APIs include `init_cpu_devs()`, `early_cpu_init()`, `cpu_detect()`, `get_cpu_vendor()`, `get_cpu_cap()`, `get_cpu_address_sizes()`, `identify_boot_cpu()`, `identify_secondary_cpu()`, and `arch_cpu_finalize_init()`. Feature/bug logic includes `filter_cpuid_features()`, `init_speculation_control()`, `cpu_set_bug_bits()`, `parse_set_clear_cpuid()`, `cpu_parse_early_param()`, `check_null_seg_clears_base()`, and `detect_nopl()`.

Low-level setup APIs include `native_write_cr0()`, `native_write_cr4()`, `cr4_update_irqsoff()`, `cr4_read_shadow()`, `cr4_init()`, `load_direct_gdt()`, `load_fixmap_gdt()`, `switch_gdt_and_percpu_base()`, `setup_pku()`, `setup_cet()`, `cet_disable()`, `syscall_init()`, `cpu_init_exception_handling()`, `cpu_init_replace_early_idt()`, and `cpu_init()`.

## Control Flow
`early_cpu_init()` registers vendor descriptors from the linker section and runs `early_identify_cpu(&boot_cpu_data)`. Early identification does minimum CPUID/vendor/capability discovery, parses early feature-suppression options (`noxsave`, `clearcpuid`, `setcpuid`, `fred=off`, etc.), initializes topology, runs vendor early/BSP hooks, checks feature dependencies, sets bug bits, runs split-lock setup, clears impossible 32-bit capabilities, handles 5-level paging visibility, detects NOPL, and initializes MCE BSP state.

`arch_cpu_finalize_init()` later calls `identify_boot_cpu()`, sets SMT thread counts, selects the idle routine, runs `cpu_select_mitigations()` from `bugs.c`, updates SMT-sensitive subsystems, initializes FPU/EFI, copies final boot CPU data into the per-CPU slot, marks it initialized, and patches alternatives.

`identify_cpu()` is the full identification path used for boot and secondary CPUs. It resets fields, runs generic CPUID identification, parses topology, calls vendor identify/init hooks, runs bus-lock setup, configures SMEP/SMAP/UMIP, filters CPUID-level-dependent features, checks dependency consistency, chooses/fills model name, initializes random/PKEY/CET support, reapplies forced caps, intersects AP features into boot common caps, mirrors bug bits to APs, initializes PPIN/MCE/NUMA, and leaves a normalized `cpuinfo_x86`.

Secondary CPU bring-up uses `identify_secondary_cpu()`, then replays SEP where needed, SPEC_CTRL/AP mitigation MSRs, SRBDS/GDS MSRs, TSX AP setup, and marks the CPU initialized. Per-CPU runtime state is finalized through `cpu_init_exception_handling()` and `cpu_init()`.

## State and Persistence
Capability state is accumulated in `struct cpuinfo_x86` and global forced-cap bitmaps. Bug bits are synthesized from whitelist/blacklist tables, architectural capability MSR bits, hypervisor state, microcode revision, and vendor features. CR4 pinning records sensitive CR4 bits after CPU init and uses static-key guarded write wrappers to restore missing bits if later writes try to clear them. GDT/TSS/syscall/debug-register setup is per CPU and must be reloaded on CPU init, resume, and hotplug. Late microcode checks snapshot capabilities and warn if features change after loading.

## Dependencies and Integration Points
This file is the integration center for vendor files (`centaur.c`, `cyrix.c`, Intel/AMD/Hygon/etc. files), cache detection, topology, split/bus lock handling, vulnerability mitigation (`bugs.c`), CPUID dependency clearing (`cpuid-deps.c`), microcode, MCE, NUMA, APIC, FPU, EFI, FRED, TDX, SEV, PKU, CET/IBT, syscall/entry code, KVM exports for CR4/GDT, and CPU hotplug/SMT callbacks.

## Risks
Ordering is critical. Feature bits must be stable before alternatives and FPU/EFI choices; bug bits must exist before mitigation selection; forced `clearcpuid`/`setcpuid` changes must be applied after each CPUID probe; CR pinning must not start until the intended CR4 bits are known. Vendor hooks can mutate capabilities, so generic filters and dependency checks must run after them. Whitelist/blacklist bug tables are security-sensitive and require accurate CPU model/microcode data. Late microcode changes cannot fully re-patch all static alternatives, so the file warns instead of silently assuming changes take effect.

## Test Signals
Boot smoke tests should check dmesg CPU identification, model strings, feature flags in `/proc/cpuinfo`, topology debugfs, vulnerability sysfs, CR4 pinning warnings under LKDTM-style tests, `clearcpuid=`/`setcpuid=` taint and feature effects, AP hotplug, suspend/resume, late microcode warning paths, 32-bit SEP/syscall behavior where applicable, and virtualization paths for TDX/SEV/Xen/KVM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/cpu.h -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/cpu.h

## Purpose
`cpu.h` is the private header for `arch/x86/kernel/cpu`. It defines the vendor-driver registration contract, declares cross-file CPU detection/cache/mitigation helpers, provides config-dependent stubs, and exposes a small inline helper for Spectre v2 eIBRS mode tests.

## Important APIs, Types, and Functions
`struct cpu_dev` is the key type. It contains vendor display/CPUID identity strings, hooks for early init, BSP init, full init, pre-CPUID identification, TLB detection, vendor enum, and 32-bit legacy cache/model metadata. `cpu_dev_register()` places a `struct cpu_dev` pointer in the `.x86_cpu_dev.init` section consumed by `common.c`.

Declarations cover TSX/Intel helpers, spectral chicken setup, CPU capability/address/cache discovery, scattered CPUID features, Intel/AMD/Hygon cacheinfo init, null segment behavior checks, AMD/Hygon LLC ID helpers, AMD northbridge L3 cache private data, aperf/mperf frequency, mitigation selection, AP mitigation MSR setup, SRBDS/GDS MSR updates, and `spectre_v2_enabled`.

`spectre_v2_in_eibrs_mode()` returns true for `SPECTRE_V2_EIBRS`, `SPECTRE_V2_EIBRS_RETPOLINE`, and `SPECTRE_V2_EIBRS_LFENCE`.

## Control Flow
Vendor implementation files define static `struct cpu_dev` objects and invoke `cpu_dev_register()`. During early boot, `common.c:init_cpu_devs()` scans `__x86_cpu_dev_start..__x86_cpu_dev_end` and stores descriptors for matching in `get_cpu_vendor()` and vendor hook calls. The declared helpers form the private call graph between CPU identification, cacheinfo, and mitigation files.

## State and Persistence
The header itself has no mutable state. It declares external state such as `spectre_v2_enabled` and uses linker-section placement for persistent init-time vendor descriptors.

## Dependencies and Integration Points
It includes `asm/cpu.h`, `asm/topology.h`, and local `topology.h`. It is included by core CPU files and vendor files. Config stubs allow code to call Intel TSX/CPUID leaf unlock helpers even when Intel CPU support is not built.

## Risks
Changing `struct cpu_dev` affects every vendor file and the linker-section registration contract. Adding hooks or declarations requires careful init-section annotations because many descriptors live in init memory. Misusing `spectre_v2_in_eibrs_mode()` outside its intended enum can hide Spectre v2 user/BHI policy bugs.

## Test Signals
Build coverage across `CONFIG_CPU_SUP_INTEL`, 32-bit, 64-bit, `CONFIG_AMD_NB`, and `CONFIG_SYSFS` is the main signal. Runtime signals are successful vendor matching and absence of unresolved symbols or init-section mismatch warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/cpuid-deps.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/cpuid-deps.c

## Purpose
`cpuid-deps.c` enforces dependency relationships between x86 CPU feature bits. When a feature is cleared by command line, config, erratum handling, microcode state, or generic filtering, dependent features are recursively cleared so the final capability set does not advertise impossible or unsafe combinations.

## Important APIs, Types, and Functions
`struct cpuid_dep` maps a feature to the feature it depends on. `cpuid_deps[]` covers FPU/FXSR, XSAVE families, vector extensions, AVX512 subfeatures, resource-control subfeatures, SGX subfeatures, AMX/XFD, shadow stack, FRED/LKGS, SSBD/SPEC_CTRL, and LASS/SMAP.

Public APIs are `clear_cpu_cap(struct cpuinfo_x86 *c, unsigned int feature)`, `setup_clear_cpu_cap(unsigned int feature)`, and `check_cpufeature_deps(struct cpuinfo_x86 *c)`. Internals include `clear_feature()`, `do_clear_cpu_cap()`, and `x86_feature_name()`.

## Control Flow
`do_clear_cpu_cap()` first clears the requested feature on either a specific CPU or the boot CPU/global cleared bitmap, warns if clearing an already-boot-visible feature after alternatives were patched, then builds a bitmap of disabled features. It repeatedly scans `cpuid_deps[]` until no newly dependent features are added, clearing each dependent capability as it goes.

`check_cpufeature_deps()` is a diagnostic pass used after feature discovery/filtering. It warns once if a CPU still has a feature set while its dependency is absent.

## State and Persistence
For boot-global clearing, `clear_feature(NULL, feature)` mutates `boot_cpu_data` and records the bit in `cpu_caps_cleared` so later CPUID probes and APs inherit the forced clear. Per-CPU clearing mutates only that CPU's `x86_capability`. There is no persistent storage beyond the capability bitmaps.

## Dependencies and Integration Points
The file depends on `asm/cpufeature.h`, `boot_cpu_data`, `alternatives_patched`, feature-name arrays, and the global forced-cap bitmaps declared in `common.c`. `common.c` calls dependency checks during early and full identification, and feature clearing is used throughout CPU/vendor/mitigation code.

## Risks
The dependency table is policy-sensitive: missing entries can leave impossible CPUID combinations, while overly broad dependencies can hide usable features. Clearing after alternatives are patched may not update patched code paths, hence the warning. The recursive algorithm assumes dependency count is small and acyclic enough to converge quickly.

## Test Signals
Boot with `clearcpuid=` for base features such as `xsave`, `avx`, `avx512f`, `sgx`, `xfd`, or `smap` and verify dependent flags disappear from `/proc/cpuinfo`. Check dmesg for dependency warnings on deliberately inconsistent virtual CPUID. Build/run CPU hotplug because the table is not `__init`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/cpuid-deps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/cpuid_0x2_table.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/cpuid_0x2_table.c

## Purpose
`cpuid_0x2_table.c` is the static descriptor table for legacy Intel CPUID leaf `0x2` cache and TLB descriptors. It lets older CPUs without deterministic cache leaf `0x4` translate one-byte descriptor values into cache sizes, cache levels, TLB types, and TLB entry counts.

## Important APIs, Types, and Functions
The only exported object is `const struct leaf_0x2_table cpuid_0x2_table[256]`. `CACHE_ENTRY()` initializes cache descriptor entries with `c_type` and KiB size. `TLB_ENTRY()` initializes TLB descriptor entries with `t_type` and entry count.

Entries include L1 instruction/data cache descriptors, L2 and L3 descriptors, instruction/data/STLB descriptors for 4K, 2M, 4M, and 1G page sizes, and descriptors used by the parser macros in the CPUID types header.

## Control Flow
There is no runtime logic in this file. `cacheinfo.c:intel_cacheinfo_0x2()` calls `cpuid_leaf_0x2()` and iterates descriptors with `for_each_cpuid_0x2_desc()`, which indexes this table and accumulates cache sizes by `CACHE_L1_INST`, `CACHE_L1_DATA`, `CACHE_L2`, and `CACHE_L3`. TLB detection code elsewhere uses the TLB entries for last-level TLB counts.

## State and Persistence
The table is immutable static data. It has no runtime state, side effects, or persistence beyond being compiled into the kernel image.

## Dependencies and Integration Points
It depends on `linux/sizes.h`, `asm/cpuid/types.h`, and local `cpu.h`. Its main integration point is Intel legacy cache/TLB discovery, especially `cacheinfo.c` and any CPUID descriptor iterator using `cpuid_0x2_table`.

## Risks
Incorrect descriptor mappings directly produce wrong cache or TLB reporting on legacy CPUs. Missing descriptors are treated as empty/default entries, so silent under-reporting is possible. Because this is legacy hardware data, broad test coverage is difficult.

## Test Signals
On CPUs or emulators exposing CPUID leaf `0x2` without leaf `0x4`, compare `/proc/cpuinfo`, cacheinfo sysfs, and TLB dmesg lines against vendor documentation. Unit-like validation can iterate known descriptors and verify table type/size/entry values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/cpuid_0x2_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/cyrix.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/cyrix.c

## Purpose
`cyrix.c` implements vendor identification and initialization for Cyrix and National Semiconductor Geode-era x86 CPUs. It handles CPUs with disabled or absent CPUID, reads Cyrix DIR/CCR registers, builds model strings, enables Cyrix/NSC memory/cache modes, applies old errata workarounds, marks Cyrix-specific MTRR emulation features, and registers Cyrix and NSC vendor descriptors.

## Important APIs, Types, and Functions
Low-level register helpers are `__do_cyrix_devid()` and `do_cyrix_devid()`, which probe CCR/DIR registers under IRQ protection. Main hooks are `early_init_cyrix()`, `init_cyrix()`, `init_nsc()`, and `cyrix_identify()`. Supporting routines include `check_cx686_slop()`, `set_cx86_reorder()`, `set_cx86_memwb()`, `geode_configure()`, and `test_cyrix_52div()`.

Registered descriptors are `cyrix_cpu_dev` (`CyrixInstead`, early init, full init, pre-CPUID identify) and `nsc_cpu_dev` (`Geode by NSC`, NSC init).

## Control Flow
On CPUs without CPUID, `common.c` can call vendor `c_identify()`. `cyrix_identify()` uses the 5/2 division flags test to detect Cyrix 486-class CPUs, sets the vendor string, and enables CPUID on affected 6x86/6x86MX models by writing CCR registers.

Early init reads DIR0/DIR1 and marks `X86_FEATURE_CYRIX_ARR` for 6x86 and 6x86MX/M II families. Full init converts Cyrix's extended MMX bit into `X86_FEATURE_CXMMX`, clears the original generic bit, recalibrates delay if the SLOP bit was set, derives family/model/stepping and printable model name from DIR values, applies MediaGX/Geode PCI/DMA/TSC workarounds, enables MMX extensions and memory write-back/reorder modes where needed, and marks `X86_BUG_COMA` on affected cores.

`init_nsc()` handles NSC-branded GX processors directly or delegates back to Cyrix initialization for other rebranded parts.

## State and Persistence
State is mostly in `struct cpuinfo_x86`: vendor, model ID, feature flags, bug flags, stepping, cache size, and loops-per-jiffy. The global `Cx86_dir0_msb` records the Cyrix family nibble for older bug logic. CCR/CR0 changes in memory write-back/reorder/power setup persist for the running CPU. `isa_dma_bridge_buggy` and TSC stability state are global platform effects for MediaGX systems.

## Dependencies and Integration Points
The file depends on Cyrix processor register helpers, PCI direct config access, ISA DMA, TSC stability, scheduler delay calibration, CR0 flags, and generic vendor registration in `cpu.h`. It integrates with `common.c` identification and with legacy MTRR emulation through `X86_FEATURE_CYRIX_ARR`.

## Risks
This file manipulates undocumented or lightly documented legacy CPU registers and chipset behavior. IRQ protection around CCR/DIR access is important. Incorrect model decoding can enable wrong memory modes, mark the wrong bug flags, or produce bad model strings. MediaGX workarounds affect ISA DMA and TSC stability globally. Hardware availability for regression tests is limited.

## Test Signals
Boot on Cyrix/NSC/Geode hardware or emulators with CPUID disabled/enabled and verify vendor detection, model string, `CXMMX`, `CYRIX_ARR`, `COMA`, cache size, delay-loop calibration, TSC stability messages, and MediaGX DMA workaround. Exercise 32-bit builds where most of this code is relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/cyrix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/debugfs.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/debugfs.c

## Purpose
`debugfs.c` exposes x86 CPU topology internals through debugfs. It creates `arch_debugfs_dir/topo/domains` for system topology domain sizes/shifts and `arch_debugfs_dir/topo/cpus/<cpu>` for per-CPU topology and cache IDs.

## Important APIs, Types, and Functions
`cpu_debug_show()` prints online state and, if initialized, APIC IDs, package/die/core/module-like topology fields, CPU type, logical topology IDs, LLC/L2 cache IDs, AMD node data, and package/core/thread count globals. `dom_debug_show()` prints domain names, shifts, domain sizes, and cumulative max thread counts from `x86_topo_system`.

`cpu_debug_open()` and `dom_debug_open()` wrap the show functions with `single_open()`. `dfs_cpu_ops` and `dfs_dom_ops` provide read-only seq_file operations. `cpu_init_debugfs()` creates the directory tree at `late_initcall`.

## Control Flow
At late init, `cpu_init_debugfs()` creates `topo`, then `domains`, then a `cpus` directory with one file per possible CPU. Reading a CPU file uses the CPU number stored in `inode->i_private`, gets `per_cpu(cpu_info, cpu)`, and prints nothing beyond online state if that CPU has not completed initialization. Reading `domains` iterates `TOPO_MAX_DOMAIN`.

## State and Persistence
The file has no independent persistent state. Debugfs dentries persist while mounted and reflect live kernel state from `cpu_info`, topology globals, and CPU online state at read time.

## Dependencies and Integration Points
It depends on debugfs, seq_file, `arch_debugfs_dir`, APIC/topology structures, `cpu_info` from `common.c`, and topology helpers such as `get_topology_cpu_type_name()` and `topology_amd_nodes_per_pkg()`.

## Risks
Debugfs is diagnostic and optional, but formatting changes can affect scripts used by developers. The per-CPU files are created for possible CPUs, so reads must tolerate offline or not-yet-initialized CPUs. There is no explicit error handling for debugfs creation failures, matching common debugfs practice.

## Test Signals
With debugfs mounted, inspect `/sys/kernel/debug/x86/topo/domains` and `/sys/kernel/debug/x86/topo/cpus/*` on SMT, multi-core, multi-die, AMD-node, and hybrid CPU systems. Hotplug CPUs and confirm online/initialized behavior remains coherent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/debugfs.c -->
