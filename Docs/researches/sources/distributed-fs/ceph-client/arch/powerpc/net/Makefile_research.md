# sources/distributed-fs/ceph-client/arch/powerpc/net/Makefile

## Purpose
This Makefile builds the PowerPC architecture-specific networking code for BPF JIT support.

## Important APIs, Types, And Functions
There are no source APIs. When `CONFIG_BPF_JIT` is enabled, it builds the common `bpf_jit_comp.o` plus a word-size-specific backend selected by `$(BITS)`, such as `bpf_jit_comp32.o` on 32-bit PowerPC.

## Control Flow
The single object rule is conditional on `CONFIG_BPF_JIT`. Build-time expansion of `$(BITS)` selects the backend matching the target ABI.

## State And Persistence
The file affects the linked kernel image by including or excluding JIT objects. It has no runtime state.

## Dependencies And Integration Points
It connects Kconfig `CONFIG_BPF_JIT` with architecture backend source files and must stay aligned with available `bpf_jit_comp$(BITS).c` implementations.

## Risks And Test Signals
Risks include missing backend objects for a new bitness, compiling BPF JIT code when unsupported, or omitting the common compiler. Test signals include 32-bit and 64-bit PowerPC builds with `CONFIG_BPF_JIT=y` and disabled JIT builds that omit these objects cleanly.
