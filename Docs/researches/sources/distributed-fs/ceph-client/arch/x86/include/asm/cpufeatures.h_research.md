
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cpufeatures.h

Purpose: canonical numeric definitions for x86 CPU feature and bug bits.

Important APIs and control flow: defines `NCAPINTS`, `NBUGINTS`, hundreds of `X86_FEATURE_*` values by CPUID word and bit, Linux-synthesized/scattered feature words, and `X86_BUG()` encodings for vulnerability/erratum bits. Comments with quoted strings drive `/proc/cpuinfo` display names; comments also require cpuid dependency table updates when feature dependencies are added.

State, dependencies, and risks: no direct runtime state, but every constant indexes capability arrays and user-visible feature reporting. Dependencies include CPUID discovery, `/proc/cpuinfo` flag tables, alternatives, mitigations, and KVM exposure. Risks include reusing non-free bits, wrong word assignments, missing dependency-table updates, and ABI-visible flag name changes. Test signals are CPU feature table builds, `/proc/cpuinfo`, KVM CPUID tests, and mitigation status coverage.
