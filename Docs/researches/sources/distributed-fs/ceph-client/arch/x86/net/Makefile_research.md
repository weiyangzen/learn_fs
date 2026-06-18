# sources/distributed-fs/ceph-client/arch/x86/net/Makefile

## Purpose
`arch/x86/net/Makefile` selects the architecture-specific eBPF JIT objects built for x86 networking.

## Important APIs, Types, and Functions
There are no C APIs. The build variables add `bpf_jit_comp32.o` for `CONFIG_X86_32=y`, or `bpf_jit_comp.o` plus `bpf_timed_may_goto.o` for non-32-bit x86, all gated by `CONFIG_BPF_JIT`.

## Control Flow and State
Kbuild evaluates the `ifeq ($(CONFIG_X86_32),y)` branch at build time. Runtime behavior is entirely in the selected object files.

## State and Persistence
The file owns no runtime state. Its persistent effect is the object list recorded in the kernel build graph for the selected configuration.

## Dependencies and Integration Points
It integrates with Kbuild, x86 config symbols, and the BPF JIT implementation under `arch/x86/net`. The 64-bit path includes timed `may_goto` support in addition to the main JIT compiler.

## Risks and Test Signals
Risks include building the wrong JIT object for 32-bit versus 64-bit kernels or omitting auxiliary 64-bit BPF support. Test signals are `CONFIG_BPF_JIT` x86_32 and x86_64 builds, BPF selftests, and module/object presence in build logs.
