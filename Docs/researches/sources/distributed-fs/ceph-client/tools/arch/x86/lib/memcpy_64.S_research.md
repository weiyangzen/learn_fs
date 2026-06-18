# sources/distributed-fs/ceph-client/tools/arch/x86/lib/memcpy_64.S

## Purpose
Provides the x86-64 assembly implementation of `__memcpy`/`memcpy` for kernel/tool code, with an FSRM fast-string alternative and a manual fallback.

## APIs, Types, and Functions
Exports `__memcpy` and aliases `memcpy` through `SYM_FUNC_ALIAS_MEMFUNC()` and `SYM_PIC_ALIAS()`. Local fallback label is `memcpy_orig`.

## Control Flow, State, and Persistence
The entry path can be patched by `ALTERNATIVE` to jump to the original implementation unless `X86_FEATURE_FSRM` permits `rep movsb`. The fallback returns the original destination in `rax`, chooses forward or backward 32-byte block copy based on low address-byte comparison to reduce false dependencies, then handles tails in 16-, 8-, 4-, and 1-3-byte cases.

## Dependencies and Integration
Includes kernel-style linkage/export/alternative headers, `asm/errno.h`, and `cpufeatures.h`. Integrated with low-level x86 runtime code and alternative patching infrastructure.

## Risks and Test Signals
Risks include overlap assumptions differing from `memmove`, false-dependency heuristic edge cases, tail-copy off-by-one bugs, and alternative patching mismatches. Test signals are exhaustive small-size copies, alignment matrices, overlapping-source/destination behavior expectations, large-copy performance tests, and boot/runtime tests with and without FSRM.
