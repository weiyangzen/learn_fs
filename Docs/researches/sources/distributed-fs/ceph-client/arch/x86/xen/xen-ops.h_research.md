<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/xen-ops.h -->
# sources/distributed-fs/ceph-client/arch/x86/xen/xen-ops.h

## Purpose
Central private header for x86 Xen implementation files. It declares PV/HVM setup, memory, time, vCPU, SMP, spinlock, VGA, EFI, suspend, multicall, PMU, hypercall, and low-level assembly interfaces, with stubs for disabled configuration blocks.

## Important APIs, Types, And Functions
Major declarations include Xen start/shared-info globals, memory/p2m helpers, `xen_arch_setup`, time hooks, vCPU placement/restoration, SMP hooks, spinlock setup, VGA setup, EFI setup, suspend hooks, `struct multicall_space` and batching helpers, PMU hooks, CPU bringup assembly, IPI functions, and hypercall stubs.

## Control Flow
This header does not execute control flow directly. Its inline helpers route multicall batching through `xen_mc_batch`, `xen_mc_entry`, and `xen_mc_issue`, and compile-time stubs collapse optional features such as SMP, spinlocks, VGA, EFI, PMU, and HVM/PV suspend when configuration symbols are absent.

## State And Persistence
It exposes shared globals and structs but owns no independent state. Its inline multicall helpers affect per-CPU multicall batching state maintained elsewhere.

## Dependencies And Integration Points
Integrates nearly all files in `arch/x86/xen`, x86 page/table types, Xen public interfaces, event/IPI constants, and paravirt/hypercall assembly.

## Risks And Edge Cases
Header drift causes link failures or, worse, mismatched assumptions across low-level C and assembly. Optional stub behavior must preserve valid builds for configurations without SMP, PMU, VGA, EFI, or suspend variants. Multicall issue modes must be used with the correct batching lifecycle.

## Test Signals
All Xen x86 defconfig combinations are relevant: PV, HVM/PVHVM, SMP/non-SMP, PMU enabled/disabled, EFI, VGA, suspend, and paravirt spinlock configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/xen-ops.h -->
