## sources/distributed-fs/ceph-client/arch/s390/kvm/Makefile

Purpose: Builds the s390 KVM module/object composition.

Important variables: Includes `virt/kvm/Makefile.kvm`, sets include flags for common and s390 KVM headers, builds `kvm-y` from `kvm-s390.o`, intercept/interrupt/priv/sigp, diag/gaccess/guestdbg/vsie/pv, `dat.o`, `gmap.o`, `faultin.o`, optional PCI zdev support, and links `kvm.o` under `CONFIG_KVM`.

Control flow: Kbuild aggregates architecture-specific objects into the KVM composite object and adds optional `pci.o` when VFIO PCI zdev KVM support is enabled.

State and persistence: Build output is `kvm.o` or module `kvm`. No runtime state is owned by the Makefile.

Dependencies and integration: Connects common KVM build logic with s390 implementation files including `dat.c`, gmap, SIE intercepts, protected virtualization, and VFIO PCI device support.

Risks and test signals: Risks are object ordering/dependency omissions and missing include paths. Test signals are built-in/module KVM builds, optional PCI config builds, and link resolution for s390 KVM symbols.
