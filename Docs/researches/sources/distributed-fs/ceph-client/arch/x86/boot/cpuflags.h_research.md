# sources/distributed-fs/ceph-client/arch/x86/boot/cpuflags.h

Purpose: declares the minimal CPU feature structure and CPUID helpers used by setup and compressed boot code.

Important APIs and state: `struct cpu_features` stores level, family, model, and `flags[NCAPINTS]`. Externs expose `cpu` and `cpu_vendor`. Declares `has_eflag()`, `get_cpuflags()`, `cpuid_count()`, and `has_cpuflag()`. On non-32-bit builds, `has_eflag()` is stubbed true.

Control flow: none; it is a contract header.

Dependencies and integration: included by CPU validation and TDX detection. It bridges setup code with asm cpufeature definitions without pulling in full kernel CPU infrastructure.

Risks and test signals: declaration mismatch with implementations or NCAPINTS changes can break early CPU validation. Compile-test with 32-bit and 64-bit configurations and required feature masks.
