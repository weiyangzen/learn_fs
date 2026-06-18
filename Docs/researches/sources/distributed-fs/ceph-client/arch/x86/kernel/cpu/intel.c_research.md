# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/intel.c

Purpose: implements Intel CPU vendor initialization, including early microcode-sensitive mitigations, feature quirks, cache/TLB detection, platform feature enablement, and CPU device registration.

Important APIs and flow: `intel_cpu_dev` registers callbacks for early init, BSP init, full init, and TLB detection. `early_init_intel()` reads microcode/platform ID, disables broken Spectre v2 microcode mitigation features, applies Atom PSE, PAT, PGE, fast-string, physical-address, TSC, CLFLUSH, and TME/MKTME adjustments. `intel_unlock_cpuid_leafs()` clears BIOS CPUID limiting. `init_intel()` layers 32-bit workarounds, cacheinfo, arch perfmon, LFENCE_RDTSC, DS/BTS/PEBS, CLFLUSH/MONITOR bugs, preferred YMM selection for downclock-sensitive ZMM CPUs, NUMA node setup, `init_ia32_feat_ctl()`, `init_intel_misc_features()`, split-lock init, and thermal init. `intel_detect_tlb()` parses CPUID leaf 2 descriptors into global TLB sizing state.

State and persistence: mutates `cpuinfo_x86` feature/bug fields, global ELF HWCAP2 for ring3 MWAIT, per-CPU MSR misc feature shadows, global TLB variables, and boot parameters such as `ring3mwait=disable` and `forcepae`.

Dependencies and integration: integrates with CPU feature flags, microcode, speculation mitigations, memory encryption, KVM/SGX feature control, thermal, resctrl, NUMA, split-lock, and cpuid descriptor helpers.

Risks and test signals: high compatibility risk because small model/stepping table mistakes can expose unsafe features or hide valid ones. Signals include model-specific boot tests, dmesg warnings, mitigation flags, MTRR/PAT behavior, TME physical-bit accounting, KVM/SGX availability, TLB/cache reports, and 32-bit legacy CPU coverage when enabled.
