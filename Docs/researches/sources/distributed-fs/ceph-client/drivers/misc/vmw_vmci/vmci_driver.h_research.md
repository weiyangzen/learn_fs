# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_driver.h

Purpose: internal driver-wide interface for personality state, current context IDs, guest datagram send, host/guest init and exit, VSOCK callback dispatch, and shared file-private object typing.

Important types/APIs: `enum vmci_obj_type` distinguishes file-private VMCI objects such as VMX VM contexts and sockets. `struct vmci_obj` is a generic file-handle payload. It declares global `vmci_pdev`, context ID helpers, datagram send, host and guest lifecycle/activity functions, host-user count, VM context ID, and PPN width selection.

Control flow/integration: included by most submodules to determine whether to route as host or guest and to call the guest hypercall transport.

State/persistence: exposes `vmci_pdev` singleton because the virtual hardware allows only one VMCI device.

Risks: global singleton assumptions must match hardware and PCI probe behavior. `vmci_obj` typing is only as safe as file-operation code maintaining `ct_type` correctly.

Test signals: compile coverage across host-disabled and guest-disabled configurations, singleton device setup/teardown, and file-private object lifecycle in `/dev/vmci`.
