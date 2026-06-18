<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/xen/privcmd.h -->
# sources/distributed-fs/ceph-client/include/uapi/xen/privcmd.h

Purpose: defines the privileged Xen control ABI exposed through `/proc/xen/privcmd` or equivalent device nodes for hypercalls, foreign memory mapping, device-model ops, restrictions, resource mapping, irqfd/ioeventfd, and PCI GSI lookup.

Important APIs and types: structs include `privcmd_hypercall`, `privcmd_mmap_entry`, `privcmd_mmap`, `privcmd_mmapbatch`, `privcmd_mmapbatch_v2`, `privcmd_dm_op_buf`, `privcmd_dm_op`, `privcmd_mmap_resource`, `privcmd_irqfd`, `privcmd_ioeventfd`, and `privcmd_pcidev_get_gsi`. Ioctls cover hypercall, mmap, mmapbatch/v2, device-model ops, restriction, resource mapping, irqfd/ioeventfd assignment/deassignment, and PCI GSI lookup.

Control flow: privileged userspace issues hypercalls with up to five args, maps foreign GFNs or resources into its address space, performs batched remaps with per-frame errors, submits device-model buffers, restricts the fd to a domid, and wires eventfds for IRQ or I/O event injection.

State and persistence: state includes per-fd restrictions, mapped VMAs, device-model/eventfd registrations, and resource mappings. Effects are runtime hypervisor/domain state and can affect guest memory/device emulation.

Dependencies and integration points: depends on Linux types/compiler annotations and Xen public `xen.h`. It integrates with Xen toolstacks, QEMU device models, dom0 control flows, foreign memory mapping, and eventfd-based emulation.

Risks and test signals: risks are high because this is a privileged hypervisor control surface: pointer validation, domid restriction enforcement, GFN/MFN naming legacy, batched error reporting, and eventfd deassignment races. Test hypercall argument copying, restricted fd behavior, mmapbatch partial failures, resource unmap, irqfd/ioeventfd assign/deassign, and compat ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/xen/privcmd.h -->
