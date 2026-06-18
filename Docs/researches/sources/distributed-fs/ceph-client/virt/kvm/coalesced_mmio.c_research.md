<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/coalesced_mmio.c -->
# sources/distributed-fs/ceph-client/virt/kvm/coalesced_mmio.c

## Purpose

Implements KVM coalesced MMIO/PIO zones, letting repeated guest writes be queued into a shared ring for userspace to drain instead of exiting on every write.

## Important APIs, Types, and Functions

Source size: 190 lines, 4708 bytes. Functions/classes: Copyright, coalesced_mmio_in_range, coalesced_mmio_write, coalesced_mmio_destructor, kvm_coalesced_mmio_init, kvm_coalesced_mmio_free, kvm_vm_ioctl_register_coalesced_mmio, kvm_vm_ioctl_unregister_coalesced_mmio, list_for_each_entry_safe. Includes: kvm/iodev.h, linux/kvm_host.h, linux/slab.h, linux/kvm.h, coalesced_mmio.h.

## Control Flow and Data Flow

Registration creates an IO device for a zone and adds it to the MMIO or PIO bus under `slots_lock`. Writes validate range, lock the shared ring, check userspace-controlled indices and capacity, copy address/data/pio fields, publish with `smp_wmb()`, and advance `last`. Unregistration removes matching zones.

## State and Persistence Behavior

VM state includes a zeroed page-backed coalesced ring, `ring_lock`, and `coalesced_zones` list. Devices persist until unregistered or destroyed by the IO bus.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/virt/kvm`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Userspace controls `first` and can make the ring appear full or corrupt indices; kernel defends by checking bounds. Range overflow, pio flag validation, and destructor/list lifetime are important.

## Test Signals

Register/unregister MMIO and PIO zones, write in/out of range, fill ring to full, mutate first/last from userspace, and verify ordering of data before index publication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/coalesced_mmio.c -->
