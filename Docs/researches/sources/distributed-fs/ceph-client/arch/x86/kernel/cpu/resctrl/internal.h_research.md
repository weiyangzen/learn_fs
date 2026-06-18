# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/internal.h

## Purpose

This header defines x86-private resctrl data structures, constants, CPUID layouts, ABMC encodings, and cross-file prototypes. It is the contract between `core.c`, control update code, monitoring code, pseudo-locking, and optional Intel AET support.

## Important APIs, Types, And Functions

Important types include `struct arch_mbm_state`, `struct rdt_hw_ctrl_domain`, `struct rdt_hw_l3_mon_domain`, `struct rdt_perf_pkg_mon_domain`, `struct msr_param`, `struct rdt_hw_resource`, CPUID unions for RDT allocation leaves, and `union l3_qos_abmc_cfg`. Inline conversion helpers map generic `struct rdt_resource`, `struct rdt_ctrl_domain`, and `struct rdt_l3_mon_domain` to architecture-private containers. Constants describe CDP MSR bits, MBM counter widths, RMID error bits, ABMC/SDCIAE bits, and event identifiers.

## Control Flow

The header itself has no runtime flow, but it enables common call paths: `rdt_ctrl_update()` receives `msr_param`, monitor reads use `arch_mbm_state`, ABMC configuration packs fields into `l3_qos_abmc_cfg`, and Intel AET functions compile either as real hooks or stubs depending on Kconfig.

## State, Dependencies, And Integration

The header exposes `rdt_resources_all[]` and architecture-private fields that persist for boot lifetime. It depends on generic `linux/resctrl.h` and is included by all x86 resctrl implementation files. It also shields non-AET builds with inline stubs.

## Risks And Test Signals

Layout changes can break container conversions or generic/architecture assumptions. Bitfield definitions must match hardware MSR encodings. Test signals are compile coverage across Intel, AMD, AET disabled/enabled, ABMC/SDCIAE paths, and runtime monitor reads that validate MBM overflow and ABMC counter behavior.
