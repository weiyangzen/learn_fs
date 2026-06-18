<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_ppc970.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_ppc970.S

## Purpose
`cpu_setup_ppc970.S` provides low-level PPC970/PPC970MP hypervisor-mode setup and restore routines used by the Book3S 64 CPU table. It programs HID registers before normal kernel execution, saves selected CPU state, and restores that state after low-level transitions where the MMU context may be unavailable.

## Important APIs, Types, And Functions
Exported assembly entry points are `__cpu_preinit_ppc970`, `__setup_cpu_ppc970`, `__setup_cpu_ppc970MP`, and `__restore_cpu_ppc970`. The file defines a small `cpu_state_storage` data area holding HID0, HID1, HID4, and HID5 snapshots. It relies on SPR constants including `SPRN_HID0`, `SPRN_HID1`, `SPRN_HID4`, `SPRN_HID5`, and `SPRN_HIOR`.

## Control Flow
All major routines first test MSR HV state and return or downgrade features when not running in hypervisor mode. Preinit clears HID4 real-mode cache-inhibited mode, large-page and DCBZ-related HID5 bits, enables HID1 fetch cacheability/prefetch, and clears HIOR. CPU setup selects PPC970 or PPC970MP idle/deep-nap HID0 behavior, writes HID0 with repeated reads/synchronization, attempts to set HID4 LPES1, saves HID state, and if the bit does not stick removes `CPU_FTR_HVMODE` from the active CPU spec. Restore clears unsafe HID4 state and HIOR, then writes the saved HID registers with the required sync/isync sequencing.

## State And Persistence
State is per-kernel in-memory assembly data, not persistent storage. The only durable side effect is hardware CPU SPR programming and mutation of the boot CPU's `cpu_spec` feature bits when HV mode is unavailable.

## Dependencies And Integration Points
The PPC970 entries in `cpu_specs_book3s_64.h` reference these routines through `cpu_setup` and `cpu_restore`. It depends on PowerPC assembly helpers, CPU feature structures, page/cache constants, and correct early boot relocation behavior.

## Risks
Incorrect SPR ordering can leave the CPU in an unsafe cache or interrupt-prefix state. The shared `cpu_state_storage` is minimal and assumes the saved boot setup is suitable for later restore. The `no_hv_mode` path mutates the active CPU spec through register `r4`, so calling convention changes would be dangerous.

## Test Signals
Signals are architecture boot tests on PPC970-class hardware or emulators, suspend/restore paths invoking `cpu_restore`, absence of early machine checks, and feature detection showing `CPU_FTR_HVMODE` only when HID4 LPES programming succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_ppc970.S -->
