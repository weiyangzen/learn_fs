# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-mmio.c

## Purpose
`vgic-mmio.c` is the shared MMIO engine for VGIC register emulation. It implements generic per-interrupt state accessors, region lookup and validation, endian conversion, guest MMIO dispatch, userspace migration access, VMCR model dispatch, and distributor iodev registration.

## Important APIs, Types, And Functions
Common register callbacks include `vgic_mmio_read_group()`, `vgic_mmio_write_group()`, `vgic_mmio_read_enable()`, `vgic_mmio_write_senable()`, `vgic_mmio_write_cenable()`, pending and active read/write pairs, priority/config handlers, line-level info helpers, and RAZ/RAO/WI helpers. Infrastructure functions include `vgic_find_mmio_region()`, `vgic_get_mmio_region()`, `vgic_uaccess()`, `vgic_data_mmio_bus_to_host()`, `vgic_data_host_to_mmio_bus()`, `vgic_set_vmcr()`, `vgic_get_vmcr()`, `kvm_io_gic_ops`, and `vgic_register_dist_iodev()`.

## Control Flow
Guest MMIO accesses enter `dispatch_mmio_read()` or `dispatch_mmio_write()`. The code converts little-endian MMIO bytes to host values, finds a descriptor with `vgic_get_mmio_region()`, validates access size/alignment and IRQ range, then calls the descriptor callback for distributor, CPU interface, redistributor, or ITS iodev type. Userspace migration access goes through `vgic_uaccess()`, forces 32-bit access, chooses redist VCPU if needed, and prefers uaccess-specific callbacks when present.

Per-IRQ operations compute the first INTID from the register offset and bits-per-IRQ, iterate over affected IRQs, take `irq_lock` when mutating state, and queue or unqueue interrupts through VGIC core helpers. Active-state guest MMIO may halt/resume the guest around shared or cross-VCPU active changes to avoid racing list-register state.

## State And Persistence
This file mutates persistent `struct vgic_irq` fields: `group`, `enabled`, `pending_latch`, `line_level`, `active`, `active_source`, `priority`, and `config`. It also touches physical IRQ state for mapped interrupts and hardware SGIs, including pending/active bits and host IRQ enable state. Migration paths intentionally differ from guest MMIO in places, for example v3 userspace pending reads use `pending_latch` while guest reads may sample physical line level.

## Dependencies And Integration Points
It depends on descriptor tables from v2/v3/ITS files, VGIC core IRQ lookup/reference helpers, KVM IO bus APIs, KVM guest halt/resume, arch timer assumptions for PPI configuration, physical IRQ helpers, GICv4 SGI property update, and model-specific VMCR implementations in v2/v3/v5 runtime files.

## Risks
The most important risks are lost pending/active transitions when interacting with hardware-backed IRQs, failure to halt running VCPUs before active-state migration changes, mismatches between guest MMIO and userspace ABI semantics, and region descriptor mistakes that allow unsupported widths or out-of-range INTIDs. Priority writes explicitly do not reschedule already queued interrupts, which is an intentional behavioral limitation.

## Test Signals
Run per-register MMIO width/alignment tests, migration uaccess tests for pending/active/line-level differences, mapped level IRQ resampling tests, hardware SGI enable/disable/group/priority updates, active-state writes while VCPUs are running, endian conversion tests on non-8-byte widths, and descriptor table ordering tests through `has_attr`.
