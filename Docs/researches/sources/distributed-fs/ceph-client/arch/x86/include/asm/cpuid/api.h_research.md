
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cpuid/api.h

Purpose: raw and structured CPUID access helpers plus hypervisor-base and descriptor parsing utilities.

Important APIs and control flow: `native_cpuid()` issues CPUID with EAX/ECX inputs and four outputs. `cpuid()`, `cpuid_count()`, single-register helpers, `cpuid_leaf()`, `cpuid_subleaf()`, and register-specific macros enforce output object sizes. `cpuid_function_is_indexed()` lists leaves with subleaf semantics. `cpuid_base_hypervisor()` scans hypervisor CPUID ranges for a 12-byte signature and required leaf count. `cpuid_leaf_0x2()` sanitizes descriptor output, and `for_each_cpuid_0x2_desc()` iterates descriptor table entries.

State, dependencies, and risks: state is CPU/hypervisor CPUID output; no persistent storage here. Dependencies include paravirt `__cpuid`, cpuid types, build bugs, and early-boot-safe `__builtin_memcmp`. Risks include using indexed leaves as flat leaves, stale ECX input, early instrumentation constraints, and malformed descriptor hardware output. Test signals are CPU discovery, hypervisor detection, cache/TLB enumeration, and CPUID emulation tests.
