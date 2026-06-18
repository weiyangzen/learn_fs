# sources/distributed-fs/ceph-client/net/vmw_vsock/Kconfig

## Purpose
`Kconfig` defines the build-time feature switches for Linux virtual sockets in this source tree. It exposes the common `VSOCKETS` address-family core, optional sock_diag monitoring, loopback transport, VMware VMCI transport, virtio transport and its shared implementation, and Hyper-V transport.

## Important APIs, Types, And Functions
This file contributes Kconfig symbols rather than C APIs. `VSOCKETS` builds the `vsock` core module. `VSOCKETS_DIAG` enables the PF_VSOCK monitoring interface used by `ss`. `VSOCKETS_LOOPBACK` and `VIRTIO_VSOCKETS` both select `VIRTIO_VSOCKETS_COMMON`, causing the shared virtio protocol implementation to be built. `VMWARE_VMCI_VSOCKETS` depends on `VMWARE_VMCI`, and `HYPERV_VSOCKETS` depends on `HYPERV_VMBUS`.

## Control Flow
Selection starts with `VSOCKETS`; transport entries are only meaningful when the core address family is enabled. Transport-specific symbols compile independent provider modules that later call `vsock_core_register()` from their module init paths. The common virtio option is hidden and selected by concrete users so shared helpers are not exposed as a manual user-facing transport.

## State And Persistence
The persistent state is kernel configuration state. Built-in versus module choices determine whether transports are always present or dynamically loadable. The default-enabled diagnostic and loopback choices affect what userspace observability and local communication features are present by default when VSOCKETS is selected.

## Dependencies And Integration Points
The symbols integrate with `Makefile` object selection in the same directory and with external subsystems: VMware VMCI, virtio, and Hyper-V VMBus. The module names in help text correspond to the objects built by `Makefile`.

## Risks And Edge Cases
Misconfigured dependencies can build a transport without its bus or hypervisor substrate, or build the core without any usable transport. Since only one transport can occupy each core feature slot at runtime, enabling multiple host/guest transports is safe at build time but may produce `-EBUSY` registration failures depending on runtime platform.

## Test Signals
Useful signals include allmodconfig/allnoconfig builds, module load tests for `vsock`, `vsock_diag`, `vmw_vsock_virtio_transport`, `vmw_vsock_vmci_transport`, `hv_sock`, and `vsock_loopback`, plus `ss -A vsock` behavior when `VSOCKETS_DIAG` is enabled.
