# sources/distributed-fs/ceph-client/tools/perf/util/include/asm/cpufeature.h

Purpose: a perf tools compatibility header for kernel assembly that expects `asm/cpufeature.h`. It provides just enough symbol surface to include `arch/x86/lib/memcpy_64.S` in the userspace tools build.

Important APIs and types: defines include guard `PERF_CPUFEATURE_H` and `X86_FEATURE_REP_GOOD` as `0`. No functions or types are exported.

Control flow: compile-time only. Assembly or C preprocessor users can test or reference `X86_FEATURE_REP_GOOD`, but this tools stub does not implement runtime CPU feature probing.

State and persistence: none.

Dependencies and integration: part of perf's local kernel-header shim layer. It integrates with x86 assembly imports by satisfying a narrow macro dependency without carrying the kernel's full cpufeature system.

Risks: the dummy value is intentionally not a real feature bit. Any new users that treat it as real feature state would be wrong. The header should stay minimal and scoped to imported assembly compatibility.

Test signals: successful perf tools builds on x86 with imported memcpy assembly. A regression would usually surface as missing macro build failures or incorrect accidental use in non-stub code.
