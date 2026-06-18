<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_kvm_hook.c -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_kvm_hook.c

Purpose: This file defines and exports the zPCI KVM hook table used to connect the host zPCI layer with optional KVM/vfio passthrough support.

Important APIs/types/functions: It defines `struct zpci_kvm_hook zpci_kvm_hook` and exports it with `EXPORT_SYMBOL_GPL`.

Control flow: There is no local control flow. Other modules install or inspect callbacks through the exported hook object, and zPCI code can use those hooks when passthrough state is present.

State and persistence: The exported `zpci_kvm_hook` object is global kernel state. Its callback fields persist for the lifetime of the module/kernel and must be managed by users of the hook contract.

Dependencies and integration points: It depends on the zPCI KVM hook type from s390 PCI headers and integrates zPCI with KVM/vfio passthrough event/error paths.

Risks and test signals: Because the hook is a global mutable callback table, registration/unregistration ordering and NULL checks in consumers matter. Tests should cover builds with and without KVM/vfio support, passthrough device error events, and module unload paths that clear callbacks before code disappears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_kvm_hook.c -->
