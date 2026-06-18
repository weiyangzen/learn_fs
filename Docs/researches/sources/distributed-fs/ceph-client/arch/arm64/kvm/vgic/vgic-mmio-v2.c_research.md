# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-mmio-v2.c

## Purpose
`vgic-mmio-v2.c` defines the memory-mapped GICv2 distributor and virtual CPU interface register model. It connects GICv2 architectural offsets to common VGIC state handlers, implements v2-only SGI and target-register behavior, and provides userspace migration access for v2 distributor/CPU registers.

## Important APIs, Types, And Functions
The descriptor tables `vgic_v2_dist_registers` and `vgic_v2_cpu_registers` are the central data structures. They map offsets such as `GIC_DIST_CTRL`, `GIC_DIST_IGROUP`, `GIC_DIST_ENABLE_SET`, `GIC_DIST_PENDING_SET`, `GIC_DIST_SOFTINT`, `GIC_CPU_CTRL`, `GIC_CPU_ACTIVEPRIO`, and `GIC_CPU_DEACTIVATE` to read/write callbacks. Exported entry points are `vgic_v2_init_dist_iodev()`, `vgic_v2_init_cpuif_iodev()`, `vgic_v2_has_attr_regs()`, `vgic_v2_cpuif_uaccess()`, and `vgic_v2_dist_uaccess()`.

## Control Flow
Guest MMIO is dispatched by the common `kvm_io_gic_ops` to descriptors initialized here. Distributor misc reads expose enable state, interrupt count, CPU count, and IIDR revision. Writes to `GIC_DIST_CTRL` toggle `dist->enabled` and kick VCPUs when enabling. SGI writes to `GIC_DIST_SOFTINT` decode target list/filter mode, mark target SGIs pending, set source bits, and queue the IRQ. Target-register writes update SPI `targets` and `target_vcpu`; private targets are read-only. SGI pending set/clear registers manipulate the per-source bitmap used by GICv2 SGI migration semantics.

CPU interface uaccess registers expose VMCR fields in the legacy v2 ABI shape. `GIC_CPU_DEACTIVATE` forwards to either `vgic_v2_deactivate()` or `vgic_v3_deactivate()` depending on host VGIC type, allowing GICv2 guests on GICv3 hardware.

## State And Persistence
This file persists distributor enable state, implementation revision, v2 group-writable compatibility, SGI source bitmaps, SPI target masks and target VCPUs, active priority registers, and VMCR fields. Userspace writes to `GIC_DIST_IIDR` validate the non-revision fields and use revision 2 or 3 as the compatibility opt-in that makes v2 interrupt groups writable by userspace.

## Dependencies And Integration Points
It relies heavily on common handlers in `vgic-mmio.c` for enable, pending, active, priority, group, and config state. Runtime deactivation integrates with `vgic-v2.c` and `vgic-v3.c`. MMIO registration is performed by `vgic-register_dist_iodev()` and v2 resource mapping code, while migration access is called from `vgic-kvm-device.c`.

## Risks
GICv2 SGI source state is architecturally awkward and lossy, especially across migration and active-state restore. IIDR revision compatibility must remain stable to avoid breaking migration from older kernels/userspace. Target register writes use online VCPU count masks, so tests must cover sparse VCPU IDs and late VCPU creation assumptions. CPU interface register semantics differ between real GICv2 hosts and GICv3 hosts emulating v2.

## Test Signals
Run v2 distributor and CPU interface KVM device register round trips, SGI injection tests for all target filter modes, IIDR revision migration tests, group writability compatibility tests, target register routing tests, `GIC_CPU_DEACTIVATE` behavior under EOImode, and invalid/unaligned `has_attr` queries.
