# sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic-v3.h

## Purpose
`arm-gic-v3.h` is the architectural register and data-structure contract for ARM GICv3/GICv4 interrupt controllers, redistributors, ITS/LPI support, virtual LPIs, and CPU interface system registers.

## Important APIs, types, and functions
It defines distributor, redistributor, VLPI, ITS, command, error, and CPU-interface register offsets and bitfields; cacheability/shareability encoders; `GIC_IRQ_TYPE_LPI`; `struct rdists`; and declarations for ITS/LPI/MBI initialization. `gic_enable_sre` enables the system-register interface using arch `gic_read_sre`/`gic_write_sre`.

## Control flow
GIC drivers program distributor/redistributor control, route SPIs/PPIs/LPIs, allocate and configure LPI property/pending tables, issue ITS commands, and enable CPU interface system-register access. Virtualization paths use VPROPBASER/VPENDBASER/VSGI fields for vLPI/vSGI state.

## State and persistence
State is hardware register and table state plus runtime `rdists` tracking: per-CPU redistributor base, pending page, physical base, property table, GIC typer fields, VLPI capability flags, and memory reservation hotplug state.

## Dependencies and integration points
It depends on bitfield macros, arch GICv3 system-register access, irqdomains, fwnodes, page allocation, KVM VGIC, MSI/ITS code, and CPU hotplug.

## Risks and test signals
Risks include wrong bitfield encoding, cacheability/shareability mismatches, ITS command-table sizing, redistributor affinity discovery, SRE enable failure, and virtual LPI residency bugs. Tests should cover GICv3/v4 hardware, ITS MSI allocation, LPI table invalidation, CPU hotplug, pseudo-NMI priority, KVM vLPI/vSGI paths, and emulated GIC register behavior.
