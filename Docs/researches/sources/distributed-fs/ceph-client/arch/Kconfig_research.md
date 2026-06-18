<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/Kconfig -->
# sources/distributed-fs/ceph-client/arch/Kconfig

## Purpose
Generic architecture-dependent Kconfig library. It sources the selected architecture's Kconfig first, then defines common architecture capability symbols, scheduler topology controls, tracing/probing support, memory-management features, hardening options, ABI quirks, page-size selection, toolchain optimization features, and shared architecture gates.

## Important APIs, Types, And Functions
- Begins with `source "arch/$(SRCARCH)/Kconfig"` so each architecture can override defaults.
- Defines capability symbols such as `ARCH_HAS_DMA_OPS`, `HAVE_KPROBES`, `HAVE_RUST`, `HAVE_PERF_EVENTS_NMI`, `HAVE_ARCH_SECCOMP_FILTER`, `HAVE_OBJTOOL`, and many `ARCH_SUPPORTS_*` gates.
- User-visible choices include scheduler SMT/cluster/MC support, stack protector levels, shadow call stack, LTO mode, CFI, page size, VMAP stack, randomized kernel stack offset, strict kernel/module RWX, RELR, and lock event counts.
- Sources follow-on config files for GCOV and GCC plugins.

## Control Flow
Kconfig evaluates the active architecture first, then enters "General architecture-dependent options". Most entries are boolean feature gates selected by architecture Kconfig files and consumed by generic subsystems. User-visible options are guarded by those gates and by toolchain tests such as `$(cc-option,...)`, linker support, Clang/Rust versions, MMU presence, and subsystem dependencies.

## State And Persistence
This file defines `CONFIG_*` symbols that persist in `.config` and generated configuration headers. It does not write files directly, but its symbols drive compiler flags, linker flags, runtime hardening, memory layout, syscall ABI support, tracing behavior, and module formats.

## Dependencies And Integration Points
Integrated with every architecture Kconfig, generic scheduler, tracing, kprobes/uprobes, seccomp, stack protector, SCS, LTO, CFI, memory management, module loader, ASLR, objtool, Rust, GCOV, GCC plugins, and build-system compiler feature tests.

## Risks And Edge Cases
Incorrectly selecting a capability can compile generic code that requires missing arch hooks. Defaults and dependencies encode ABI and security assumptions, so changes can alter user ABI, page size, module relocation formats, or hardening behavior. Toolchain predicates must stay synchronized with Makefile feature usage.

## Test Signals
Run `olddefconfig` and build-test multiple architectures, especially those selecting new capability symbols. Kconfig warning-free evaluation, successful `allyesconfig`/`allmodconfig` subsets, seccomp/probing/hardening selftests, and compiler-flag validation are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/Kconfig -->
