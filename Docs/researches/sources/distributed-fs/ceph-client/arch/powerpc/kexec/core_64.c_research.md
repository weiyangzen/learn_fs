# sources/distributed-fs/ceph-client/arch/powerpc/kexec/core_64.c

## Purpose
Implements 64-bit PowerPC kexec preparation, CPU shutdown coordination, MMU-sensitive image copying, static stack/PACA handoff, hash table export, and CPU-node FDT updates.

## Important APIs, Types, And Functions
Defines `machine_kexec_prepare`, `kexec_copy_flush`, `default_machine_kexec`, and `update_cpus_node`. Internal pieces include `copy_segments`, SMP helpers `kexec_smp_down`, `kexec_prepare_cpus_wait`, `wake_offline_cpus`, `kexec_prepare_cpus`, static `kexec_stack`, static `kexec_paca`, `export_htab_values`, and `add_node_props`.

## Control Flow
Preparation rejects segments that overwrite static kernel memory or TCE tables. The transition path stops or wakes CPUs as needed, disables IRQs, waits for all CPUs to enter real mode, optionally disables pseries relocation-on-exception, switches to a static stack and copied PACA, unshares secure guest pages for normal kexec, chooses whether to copy with MMU off, and enters assembly `kexec_sequence`. `kexec_copy_flush` copies indirection-listed pages with MMU off and flushes I-cache for destination ranges.

## State And Persistence
Mutates PACA kexec states, CPU online state, interrupt state, static kexec stack/PACA, Open Firmware `/chosen` htab properties, and FDT CPU nodes. No filesystem persistence occurs.

## Dependencies And Integration Points
Integrates with generic kexec, SMP/hotplug, pseries/powernv firmware hooks, hash/radix MMU state, secure VM ultravisor sharing, hardware breakpoints, libfdt, and the assembly `kexec_sequence` in `misc_64.S`.

## Risks And Edge Cases
CPU rendezvous and real-mode entry are fragile, especially with offline CPUs, SMT state, and crash versus normal kexec. Copying with MMU off is necessary on radix/non-LPAR to avoid overwriting page tables. Switching PACA and stack invalidates many normal kernel assumptions. Segment overlap checks must catch TCE/static memory collisions.

## Test Signals
Normal kexec on radix and hash MMU, LPAR and bare metal, secure guest kexec, CPU hotplug/offline CPU cases, SMT-disabled systems, TCE table overlap rejection, and FDT CPU-node validation are key tests.
