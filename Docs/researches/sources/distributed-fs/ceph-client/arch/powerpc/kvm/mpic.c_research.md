
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/mpic.c

## Purpose
Implements an in-kernel Freescale/OpenPIC MPIC device model for PowerPC KVM. It provides MMIO register emulation, interrupt source/destination state, IPI/timer/MSI support, KVM device attributes, vCPU connection, and IRQ routing callbacks.

## Important APIs, Types, And Functions
Main exported/integrated functions are `kvm_mpic_ops`, `kvmppc_mpic_connect_vcpu()`, `kvmppc_mpic_disconnect_vcpu()`, `kvmppc_mpic_set_epr()`, `kvm_set_msi()`, and `kvm_set_routing_entry()`. Important types are `struct openpic`, `struct irq_source`, `struct irq_dest`, `struct irq_queue`, `struct mem_reg`, and `struct fsl_mpic_info`. Core internals include `openpic_set_irq()`, `openpic_update_irq()`, `IRQ_local_pipe()`, `openpic_iack()`, `openpic_cpu_write_internal()`, and the MMIO bank read/write handlers.

## Control Flow
Device creation initializes register banks, model-specific flags for FSL MPIC 2.0 or 4.2, default routing, and reset state, then publishes `kvm->arch.mpic`. Userspace sets the MMIO base via device attributes, causing `map_mmio()`/`unmap_mmio()` under `slots_lock`. Guest MMIO accesses are routed through `kvm_mpic_read()`/`kvm_mpic_write()` to bank handlers. IRQ assertion updates source pending/activity, masks, priority, destination mode, and either raises/lower KVM external interrupts or tracks non-INT output counters. IACK moves raised interrupts to servicing; EOI clears servicing and notifies acked IRQ listeners.

## State And Persistence
All MPIC state lives in one spinlock-protected `struct openpic`: global registers, source IVPR/IDR/ILR-derived output/destination state, per-CPU CTPR/raised/servicing queues, timer registers, MSI registers, routing base, model flags, and connected vCPU pointers. Destruction disconnects from the VM and frees the device model.

## Dependencies And Integration Points
Depends on KVM device API, MMIO bus, irqfd routing, `kvm_vcpu_ioctl_interrupt()`, `kvm_notify_acked_irq()`, PowerPC EPR helpers, and userspace device attributes (`KVM_DEV_MPIC_*`). It integrates with common `powerpc.c` capability and vCPU enable-cap handling.

## Risks
The model supports only one MPIC per VM and uses a single spinlock for all state. Non-INT outputs are mostly TODO and only INT output is actively queued/dequeued. Some register behavior is simplified, summary registers are placeholders, and return values from routing callbacks are intentionally not meaningful. Lock dropping around EOI notification requires care because state can change before the lock is reacquired.

## Test Signals
Useful tests include KVM device creation for both MPIC models, base-address alignment, register get/set attributes, IRQ active attributes, MMIO IACK/EOI ordering, IPI delivery to multiple vCPUs, MSI bank clear-on-read, irqfd routing, and EPR proxy mode behavior.
