# sources/distributed-fs/ceph-client/net/vmw_vsock/Makefile

## Purpose
`Makefile` maps the vmw_vsock Kconfig symbols to kernel objects and defines which source files compose each loadable module. It is the build manifest for the AF_VSOCK core, diagnostics, VMCI, virtio, shared virtio code, Hyper-V, and loopback modules.

## Important APIs, Types, And Functions
The main build products are `vsock.o`, `vsock_diag.o`, `vmw_vsock_vmci_transport.o`, `vmw_vsock_virtio_transport.o`, `vmw_vsock_virtio_transport_common.o`, `hv_sock.o`, and `vsock_loopback.o`. The `vsock-y` composite includes `af_vsock.o`, `af_vsock_tap.o`, and `vsock_addr.o`, with `vsock_bpf.o` added when `CONFIG_BPF_SYSCALL` is set. VMCI includes `vmci_transport.o`, `vmci_transport_notify.o`, and `vmci_transport_notify_qstate.o`.

## Control Flow
Kbuild includes each object only when its `CONFIG_` symbol resolves to built-in or module. Composite targets gather several `.o` files into one module, so the AF_VSOCK core always carries address utilities and tap support, while optional BPF hooks are compiled into the core only on BPF-capable builds.

## State And Persistence
There is no runtime state here. The persistent effect is build composition: for example, virtio protocol state-machine code is separated into `vmw_vsock_virtio_transport_common.o`, allowing both real virtio and loopback/vhost-style users to share the same packet and credit logic.

## Dependencies And Integration Points
This file integrates directly with `Kconfig` symbols and with exported symbols in `af_vsock.c`, `af_vsock_tap.c`, and `virtio_transport_common.c`. It also defines module naming that userspace and modprobe configuration depend on.

## Risks And Edge Cases
The highest risk is silently omitting a companion object from a composite target. For VMCI, missing either notify implementation would break negotiated notification callbacks; for the core, missing `vsock_addr.o` or `af_vsock_tap.o` would create link failures or observability regressions.

## Test Signals
Build tests should cover built-in and modular variants for every symbol combination, especially `CONFIG_BPF_SYSCALL`, `VSOCKETS_LOOPBACK`, `VIRTIO_VSOCKETS_COMMON`, and VMCI. `modinfo` and module insertion can confirm the expected composite modules are emitted.
