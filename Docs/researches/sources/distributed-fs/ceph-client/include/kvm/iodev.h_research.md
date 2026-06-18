<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/iodev.h -->
# sources/distributed-fs/ceph-client/include/kvm/iodev.h

## Purpose
`iodev.h` defines KVM's small polymorphic interface for memory-mapped or port I/O devices attached to a VM address space.

## Important APIs, types, and functions
`struct kvm_io_device_ops` contains optional `read`, `write`, and `destructor` callbacks. `struct kvm_io_device` stores the ops table. `kvm_iodevice_init()` assigns operations. `kvm_iodevice_read()` and `kvm_iodevice_write()` dispatch to callbacks or return `-EOPNOTSUPP`.

## Control flow
KVM bus code locates a registered iodev under `slots_lock`, then invokes read/write. A callback returning zero means the transaction was handled; nonzero lets the bus continue to another device. The inline wrappers only handle callback presence and dispatch.

## State and persistence behavior
The only state in the base object is the ops pointer. Device-specific state is carried by embedding `struct kvm_io_device` in a larger structure, such as VGIC MMIO device objects.

## Dependencies and integration points
The header depends on KVM types, `gpa_t`, errno values, and `struct kvm_vcpu`. It integrates with VM bus registration, VGIC/IOAPIC/PIT-style in-kernel devices, and MMIO emulation.

## Risks and test signals
Risks include registering partially initialized ops, callbacks that mishandle length/endian behavior, destructor lifetime bugs, and relying on `-EOPNOTSUPP` semantics incorrectly. Test signals include MMIO read/write routing tests, fallback-to-next-device behavior, and device unregister/destructor tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/iodev.h -->
