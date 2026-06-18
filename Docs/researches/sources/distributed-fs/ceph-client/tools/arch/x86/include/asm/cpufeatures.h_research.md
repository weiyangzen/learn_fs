# sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/cpufeatures.h

## Purpose
Defines the numeric x86 CPU feature and CPU bug bit namespace copied into `tools/`. It gives user-space tools and generated helper tables a kernel-compatible map from CPUID-derived capability names to bit positions.

## APIs, Types, and Functions
There are no functions. The public contract is macro-only: `NCAPINTS`, `NBUGINTS`, hundreds of `X86_FEATURE_*` macros grouped by CPUID word, and `X86_BUG(x)` plus `X86_BUG_*` vulnerability/erratum bits. Comments with quoted strings encode the `/proc/cpuinfo` flag spelling used by generators.

## Control Flow, State, and Persistence
The header has no runtime state. Its control behavior is compile-time indexing: every feature is `word * 32 + bit`, and bug bits start after `NCAPINTS * 32`. Consumers must preserve these stable positions because bitsets, generated name arrays, and mitigation logic depend on them.

## Dependencies and Integration
Integrated by tool-side x86 code and by `gen-cpu-feature-names-x86.awk`, which scans the `X86_FEATURE_` and `X86_BUG_` defines. It mirrors the kernel x86 feature taxonomy, including Intel, AMD, VIA/Centaur, Transmeta, virtualization, security mitigation, memory encryption, and synthetic Linux words.

## Risks and Test Signals
Risks are index drift from the kernel copy, stale `NCAPINTS`, duplicate bit allocation in a word, and comments not matching desired exported names. Test signals include successful generation of feature-name arrays, build coverage for all users including assembly, and comparisons with upstream kernel `cpufeatures.h` when refreshing this tools snapshot.
