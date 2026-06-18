# sources/distributed-fs/ceph-client/arch/s390/kvm/pci.c

## Purpose
Implements s390 KVM zPCI passthrough support for VFIO zdev devices, including adapter event notification interpretation, adapter interruption forwarding, and registration of a zPCI device with a specific KVM VM for load/store interpretation.

## Important APIs, Types, And Functions
The exported/externally referenced functions are `kvm_s390_pci_aen_init()`, `kvm_s390_pci_aen_exit()`, `kvm_s390_pci_init_list()`, `kvm_s390_pci_clear_list()`, `kvm_s390_pci_zpci_op()`, `kvm_s390_pci_init()`, and `kvm_s390_pci_exit()`. Static helpers set/reset the global AIPB (`zpci_setup_aipb()`, `zpci_reset_aipb()`), register/deregister floating adapter IRQ forwarding (`kvm_zpci_set_airq()`, `kvm_zpci_clear_airq()`), account pinned guest pages against `RLIMIT_MEMLOCK`, enable/disable AIF, and attach/detach `struct kvm_zdev` to `struct zpci_dev`.

## Control Flow And State
`kvm_s390_pci_init()` installs `zpci_kvm_hook` callbacks and allocates the global `aift` if interpretation is allowed. `kvm_s390_pci_register_kvm()` is called by zPCI/VFIO registration, opens a `kvm_zdev`, enables VM-wide PCI interpretation on first use, programs `zdev->gisa`, re-enables the device, and links it into `kvm->arch.kzdev_list`. `kvm_s390_pci_zpci_op()` dispatches userspace zPCI operations by function handle, currently register/deregister AEN. AIF enable pins guest AIBV/AISB pages, allocates an AIFT summary bit, fills a GAITE, rewrites the FIB for host forwarding, then issues the zPCI modify function. Disable reverses firmware registration, frees the summary bit/vector, unpins pages, unregisters GISC, and clears saved FIB state.

## Dependencies And Integration
Integrates Linux KVM, VFIO zPCI hooks, s390 zPCI CLP/mod-fc firmware calls, GISA/GISC interrupt routing, adapter interruption vectors, SCLP capability detection, and KVM VM locking/list state.

## Risks And Test Signals
Risks center on pinned-page accounting leaks, lock ordering across `kvm->lock`, `zdev->kzdev_lock`, and `aift` locks, stale global AIPB state across module unload/reload, failure rollback, and forced cleanup when devices disappear. Signals include VFIO zPCI passthrough tests, module load/unload with AEN, guest MSI delivery, memlock accounting, lockdep, and KVM zPCI ioctl error paths.
