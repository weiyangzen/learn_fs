# sources/distributed-fs/ceph-client/arch/arm64/net/Makefile

## Purpose
This Makefile selects ARM64 networking code for the kernel build. It conditionally builds the ARM64 BPF JIT compiler objects when `CONFIG_BPF_JIT` is enabled.

## Important APIs, Types, and Functions
The only build rule is `obj-$(CONFIG_BPF_JIT) += bpf_jit_comp.o bpf_timed_may_goto.o`.

## Control Flow
Kbuild expands `obj-y` or `obj-m` according to the value of `CONFIG_BPF_JIT`. When enabled, the two object files are compiled and linked into the architecture networking subtree; when disabled, they are omitted.

## State and Persistence
There is no runtime state. The persistent effect is build graph inclusion of BPF JIT support objects.

## Dependencies and Integration Points
This integrates with the kernel Kbuild system, ARM64 BPF JIT implementation files, and the global `CONFIG_BPF_JIT` option.

## Risks
The risk is build coverage: if a new ARM64 BPF JIT object is added but not listed, it will not link; if an object is listed without its config dependency, disabled builds can fail.

## Test Signals
Build ARM64 kernels with `CONFIG_BPF_JIT=y` and `CONFIG_BPF_JIT=n`. The enabled build should include `bpf_jit_comp.o` and `bpf_timed_may_goto.o`; the disabled build should not compile them.
