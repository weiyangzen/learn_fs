
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cpufeature.h

Purpose: runtime and static x86 CPU feature testing API.

Important APIs and control flow: `enum cpuid_leafs` maps CPUID words to `x86_capability` indexes. Macros test, set, clear, and force CPU feature bits. `cpu_feature_enabled()` uses disabled masks and `static_cpu_has()`. `_static_cpu_has()` uses `asm goto` and alternatives to patch feature tests after boot. Bug-feature wrappers alias to normal capability operations.

State, dependencies, and risks: state is `boot_cpu_data`, per-CPU `cpu_info`, capability arrays, set/clear masks, and alternative patching status. Dependencies include processor definitions, bitops, alternatives, and generated feature masks. Risks include testing raw CPU capability when kernel enablement is required, forcing features after alternatives are patched, and stale dependency clearing. Test signals are CPU feature enumeration, alternatives patch tests, mitigation feature toggles, and CPUID masking.
