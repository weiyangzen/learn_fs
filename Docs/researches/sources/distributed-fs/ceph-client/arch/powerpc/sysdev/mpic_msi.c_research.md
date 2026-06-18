<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_msi.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_msi.c

Purpose: Initializes and maintains the MPIC MSI hardware interrupt bitmap allocator.

Important APIs/types/functions: Provides `mpic_msi_reserve_hwirq()` and `mpic_msi_init_allocator()`, plus U3-specific reserve helper `mpic_msi_reserve_u3_hwirqs()` when HT IRQ support is enabled.

Control flow: Allocator init creates an MSI bitmap sized to MPIC sources, reserves device-tree-specified unavailable ranges, and if no DT ranges exist on U3/U4 hardware, reserves known non-MSI source ranges and every hwirq already referenced by OF interrupts. Runtime reservation marks MPIC hwirqs unavailable when normal IRQs are mapped.

State and persistence: Operates on `mpic->msi_bitmap`, which persists reserved/free hardware source state for MSI allocation.

Dependencies and integration points: Depends on `msi_bitmap.c`, MPIC irqdomain xlate ops, OF IRQ scanning, PCI MSI config, and U3/U4 MPIC setup.

Risks: U3 fallback reservation is heuristic and scans all OF nodes; incorrect reservation can allocate an MSI source already used by a wired interrupt. If DT `msi-available-ranges` is malformed, MSI allocator setup fails.

Test signals: MSI allocation with valid DT ranges, missing-range U3 fallback, reservation of wired interrupts, normal IRQ mapping reserving hwirqs, and failure cleanup.

Source read size: 99 lines, 2352 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_msi.c -->
