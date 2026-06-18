# sources/distributed-fs/ceph-client/include/linux/irqchip/arm-vgic-info.h

## Purpose
`arm-vgic-info.h` carries interrupt-controller metadata from physical GIC drivers to KVM VGIC initialization code.

## Important APIs, types, and functions
It defines `enum gic_type`, `struct gic_kvm_info`, and `vgic_set_kvm_info` with a no-op stub when KVM is disabled.

## Control flow
GIC drivers populate virtual CPU/control interface resources, maintenance IRQ, hardware deactivation quirks, and v4/v4.1 capability flags, then pass them to KVM through `vgic_set_kvm_info`.

## State and persistence
The header declares only transfer metadata; KVM stores any accepted copy at runtime.

## Dependencies and integration points
It depends on resource and I/O types and integrates GICv2/v3/v5 drivers with KVM ARM VGIC.

## Risks and test signals
Risks include incorrect maintenance IRQ masking, wrong resource ranges, misreported vLPI/RVPEID capability, and KVM disabled stubs hiding unused data. Tests should cover KVM boot on GICv2/v3/v5, v4/v4.1 capability exposure, and platforms with no maintenance IRQ mask.
