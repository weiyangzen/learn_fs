# sources/distributed-fs/ceph-client/arch/s390/kvm/pci.h

## Purpose
Private header for s390 KVM zPCI passthrough. It defines the KVM-side zPCI tracking objects, the global adapter interruption forwarding table shape, and declarations consumed by KVM core and PCI implementation code.

## Important APIs, Types, And Functions
`struct kvm_zdev` binds a `struct zpci_dev` to a `struct kvm`, stores the guest/host FIB used for adapter interruption forwarding, and links into `kvm->arch.kzdev_list`. `struct zpci_gaite` models a guest adapter interrupt table entry containing GISA, GISC, reference count, AISB offset, and AISB address. `struct zpci_aift` holds the global GAIT, summary-bit vector, per-summary-index `kvm_zdev` map, and two locks: `gait_lock` for interrupt-side GAIT access and `aift_lock` for broader table lifecycle. `kvm_s390_pci_si_to_kvm()` maps an adapter summary index to the associated VM if CONFIG support and table state exist. `kvm_s390_pci_interp_allowed()` gates support on config, SCLP facilities, and known machine IDs without SHM.

## Control Flow And State
The header is declarative but encodes the persistent state model: one global `aift`, per-VM zdev lists, per-device saved FIB state, and feature gating before interpretation setup. The machine-ID denylist short-circuits even if general zPCI facilities are present.

## Dependencies And Integration
Depends on Linux KVM host structures, PCI/zPCI definitions, s390 AIRQ vectors, CPU ID, and SCLP feature flags. Consumers include `pci.c`, KVM VM init/teardown, and interrupt delivery paths that need to recover a KVM from a zPCI summary bit.

## Risks And Test Signals
Risks include stale `aift->kzdev` lookups, summary-index bounds assumptions, mismatched feature gating between header and implementation, and use after free during module exit or interrupt delivery. Test signals are zPCI passthrough initialization on supported/unsupported machine models, AEN forwarding, lockdep, and compile coverage for CONFIG_VFIO_PCI_ZDEV_KVM on/off.
