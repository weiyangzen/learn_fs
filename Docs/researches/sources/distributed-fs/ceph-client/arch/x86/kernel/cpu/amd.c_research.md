# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/amd.c

## Purpose
This file implements AMD CPU identification, early feature setup, family/model-specific errata workarounds, topology/NUMA fixups, security mitigation feature adjustments, cache/TLB reporting, debug register address mask support, and late platform diagnostics.

## Important APIs, Types, and Functions
The CPU vendor descriptor `amd_cpu_dev` registers `early_init_amd()`, `cpu_detect_tlb_amd()`, `bsp_init_amd()`, and `init_amd()`. Family-specific helpers cover K5/K6/K7/K8/F10h/F12h/F15h/F16h and Zen generations. Security and correctness helpers include `early_detect_mem_encrypt()`, `bsp_determine_snp()`, `tsa_init()`, `fix_erratum_1386()`, `init_spectral_chicken()`, `zen2_zenbleed_check()`, `clear_rdrand_cpuid_bit()`, and Zen RDSEED handling. Exported/debugger-facing functions include `amd_set_dr_addr_mask()`, `amd_get_dr_addr_mask()`, and `amd_check_microcode()`.

## Control Flow
Early init sets K8/common capability bits, records microcode, derives constant/nonstop TSC, RAPL/accumulated power, extended APIC IDs, VMMCALL, memory encryption exposure, and branch prediction capabilities. BSP init checks TSC semantics, Fam15h VA alignment randomization, MWAITX delay, SSBD fallback, resctrl, Zen generation classification, SNP host support, TSA mitigation, and CPUID faulting. Full init applies family errata, Zen common setup, Zen-generation-specific mitigations, cache/TLB detection, NUMA node repair, SVM disabling detection, LFENCE serialization, ARAT, PREFETCHW, SYSRET bug, IRPERF, AUTOIBRS, APIC MSR fence clearing, and TCE enabling.

## State and Persistence
Persistent state includes CPU capability and bug bits, global `invlpgb_count_max`, `x86_amd_ls_cfg_*` mitigation state, randomized `va_align` bits, per-CPU debug register address masks, and cache/TLB global descriptors. Late init reads and clears FCH S5 reset status and logs AGESA strings from DMI additional info.

## Dependencies and Integration Points
The file integrates with x86 CPU vendor registration, CPUID/MSR helpers, NUMA/APIC topology, PCI config access, SME/SEV/SNP confidential-computing platform state, scheduler clock/delay, randomization, resctrl, cacheinfo, KVM exported symbols, microcode update paths, DMI, MMIO, and speculation mitigation infrastructure.

## Risks and Test Signals
Risks include over- or under-exposing CPU capabilities, unsafe MSR writes on guests, stale microcode tables, incorrect Zen family classification, NUMA node misassignment, breaking SVM or SME/SEV detection, and mitigation regressions. Test signals include boot CPU feature flags, dmesg errata notices, microcode update rechecks, kvm/debug register tests, NUMA topology validation, suspend/resume RDRAND behavior, SME/SEV/SNP boot tests, and late reset/AGESA logs.
