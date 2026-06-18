# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/amd_fam14h_idle.c

## Purpose
Implements a cpupower monitor plugin for AMD family 12h/14h package C-state counters and North Bridge P1 indication using PCI configuration registers.

## Important APIs, Types, and Functions
Important functions are `amd_fam14h_get_pci_info`, `amd_fam14h_init`, `amd_fam14h_disable`, `fam14h_nbp1_count`, `fam14h_get_count_percent`, `amd_fam14h_start`, `amd_fam14h_stop`, `is_nbp1_capable`, `amd_fam14h_register`, and `amd_fam14h_unregister`. The monitor exposes `!PC0`, `PC1`, `PC6`, and optional `NBP1` states.

## Control Flow, State, and Persistence
Registration requires AMD vendor and family 0x12 or 0x14, allocates per-CPU counter arrays, opens PCI slot 0x18 function 6, and reduces state count if NBP1 is unsupported. Start enables/zeros counters; stop reads counters, disables monitor bits, computes elapsed time, and warns on overflow. State is global static monitor storage plus live PCI counter state.

## Dependencies and Integration Points
Depends on libpci, cpupower CPU info, monitor framework callbacks, and root access. Results are printed by `cpupower-monitor.c` through `cstate_t` callbacks.

## Risks and Test Signals
PCI layout is family-specific and assumes one device. Registration leaks allocated arrays if PCI initialization later fails. Percentage math depends on 80 ns ticks and 32-bit overflow window. Test on matching AMD hardware, nonmatching CPUs, no PCI access, NBP1 capable/incapable systems, and long measurement overflow warning.
