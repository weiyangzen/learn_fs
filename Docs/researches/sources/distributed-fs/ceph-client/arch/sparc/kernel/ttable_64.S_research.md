<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ttable_64.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/ttable_64.S

## Purpose
Defines SPARC V9 trap tables for TL0 and TL1, including boot, faults, interrupts, TLB misses, register-window spill/fill vectors, syscall traps, kprobes, kgdb, uprobes, Sun4v mondos, and patchable Cheetah/Sun4v error vectors.

## Important APIs, Types, And Functions
Exported labels include `sparc64_ttable_tl0`, `sparc64_ttable_tl1`, `tl0_icpe`, `tl1_icpe`, `tl0_dcpe`, `tl1_dcpe`, `tl0_fecc`, `tl1_fecc`, `tl0_cee`, `tl1_cee`, `tl0_iae`, `tl1_iae`, `tl0_dae`, and `tl1_dae`. It uses macros such as `TRAP`, `TRAP_NOSAVE`, `TRAP_7INSNS`, `TRAP_SAVEFPU`, `TRAP_IRQ`, `TRAP_NMI_IRQ`, `SUN4V_ITSB_MISS`, `SUN4V_DTSB_MISS`, `TRAP_UTRAP`, `UPROBES_TRAP`, and the spill/fill macros.

## Control Flow
TL0 handles ordinary exceptions and includes fast TLB miss handlers from `itlb_miss.S`, `dtlb_miss.S`, and `dtlb_prot.S`. TL1 handles nested traps and generally routes unexpected conditions to fatal TL1 C handlers. Trap vectors for cache/ECC/parity start as bad traps and are patched by `cheetah_ecache_flush_init`. Syscall, kprobe, kgdb, uprobe, get/set context, and user-trap vectors dispatch to their specialized entry paths.

## State And Persistence
The table is static executable state, but selected vector slots are intentionally mutable during CPU-family initialization. Its labels are also persistent anchors for patching and diagnostics.

## Dependencies And Integration Points
It is the direct caller of many handlers in `traps_64.c`, entry assembly, TSB miss code, interrupt handling, syscall paths, uprobe/kprobe code, and register-window macros. It also depends on linker placement and patch sections collected by `vmlinux.lds.S`.

## Risks And Edge Cases
Vector width and instruction layout are hardware contracts. TL1 paths cannot rely on normal trap-entry state. Patching cache-error vectors must occur after CPU type detection and before such traps are enabled. Uprobe/kprobe trap numbers must match userspace/kernel breakpoint encodings.

## Test Signals
Signals include SPARC64 boot, user and kernel traps, all syscall ABIs, TLB miss/fault behavior, interrupt delivery, nested TL1 trap diagnostics, Cheetah error-vector patching, user-trap delivery, and uprobe traps at `0x173`/`0x174`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ttable_64.S -->
