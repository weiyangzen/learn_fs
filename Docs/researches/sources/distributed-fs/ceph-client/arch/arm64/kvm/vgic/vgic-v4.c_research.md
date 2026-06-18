# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-v4.c

## Purpose
`vgic-v4.c` bridges KVM's virtual ITS/VGIC state with GICv4/GICv4.1 hardware direct injection. It manages vPE allocation and residency, doorbell IRQs, direct virtual SGI configuration, VLPI forwarding from VFIO/MSI routing, and cleanup of hardware-backed LPIs.

## Important APIs, Types, And Functions
Entry points include `vgic_v4_configure_vsgis()`, `vgic_v4_get_vlpi_state()`, `vgic_v4_request_vpe_irq()`, `vgic_v4_init()`, `vgic_v4_teardown()`, `vgic_v4_put()`, `vgic_v4_load()`, `vgic_v4_commit()`, `kvm_vgic_v4_set_forwarding()`, and `kvm_vgic_v4_unset_forwarding()`. Internal helpers manage doorbells (`vgic_v4_doorbell_handler()`), vSGI enable/disable, vPE doorbell policy, and lookup of an LPI by host IRQ.

## Control Flow
Initialization allocates VM vPE pointers, asks the ITS driver for vCPU IRQs, configures doorbell IRQ flags, and requests per-VCPU doorbell interrupts. On VCPU load, direct-IRQ support makes the vPE resident after setting doorbell IRQ affinity to the current CPU. On put, the vPE is made non-resident and a doorbell is requested if the VCPU is in WFI or nested execution needs to be interrupted.

When userspace/VFIO configures MSI forwarding, `kvm_vgic_v4_set_forwarding()` resolves the routing entry to a vITS, translates DEVID/EVENTID to a `vgic_irq`, builds an `its_vlpi_map`, and calls `its_map_vlpi()`. If successful, the LPI becomes hardware-backed (`irq->hw`, `host_irq`) and pending software state is transferred to the host irqchip. Unset reverses this by finding the LPI by host IRQ, decrementing the target vPE VLPI count, clearing `hw`, and unmapping the VLPI.

## State And Persistence
The file mutates `dist->its_vm.vpes`, per-VCPU `its_vpe` residency/ready/pending/vlpi_count state, SGI config in the vPE, `vgic_irq->hw`, `host_irq`, and pending latch transfer between software and hardware. It does not own migration table format, but it affects whether ITS save can observe pending state; pre-v4.1 hardware-backed LPIs can cause save to fail elsewhere.

## Dependencies And Integration Points
It depends on the irqchip ITS GICv4 API (`its_alloc_vcpu_irqs`, `its_make_vpe_resident`, `its_map_vlpi`, `its_unmap_vlpi`, etc.), VFIO/KVM MSI routing callbacks, virtual ITS resolution from `vgic-its.c`, common VGIC IRQ state, GICv3 vPE storage, and KVM VCPU wakeup/request mechanisms.

## Risks
Direct injection state spans KVM and the host irqchip, so refcount and lock mistakes can leak or misroute host IRQs. Doorbell races are explicitly handled with `vpe_lock` on v4.1. Forwarding silently falls back to software injection for many invalid states, which is correct but can hide performance regressions. vSGI conversion must transfer pending, priority, group, and enable state without losing software pending bits.

## Test Signals
Use hardware-enabled tests for VLPI forwarding/unforwarding, pending transfer on mapping, doorbell wake from WFI, vPE migration between physical CPUs, GICv4.1 vSGI enable/disable through GICD_CTLR nASSGIreq, teardown after partial init failure, and migration/save behavior with hardware-backed LPIs.
