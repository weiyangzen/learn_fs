# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_route.c

Purpose: central routing decision logic for VMCI datagrams and queue-pair route selection. It determines whether an operation should be handled locally as host, sent through the guest device to the hypervisor/host, or rejected.

Important API: `vmci_route(struct vmci_handle *src, const struct vmci_handle *dst, bool from_guest, enum vmci_route *route)` validates destination, samples host/guest activity, may fill an invalid source context with current context ID, and returns a route enum plus VMCI status.

Control flow: hypervisor destinations require active guest device and cannot be forwarded from guest-origin ioctls. Host destinations may route as guest when a local client in a guest must send down to the host, or as host for local host/hypervisor delivery. Non-host destinations first try active host contexts; VM-to-VM via host is rejected. If no host context path applies, active guest device routes down to the host for older VM-to-VM-capable environments.

State/persistence: no owned state; decisions are based on current host/guest personality activity and context existence.

Dependencies/integration: used by datagram dispatch and qpair allocation to select host versus guest implementation. Relies on `vmci_host_code_active()`, `vmci_guest_code_active()`, `vmci_get_context_id()`, and `vmci_ctx_exists()`.

Risks: host/guest active state can change after routing, so send paths must revalidate device availability. The function mutates `src->context`, which callers must expect. Unified host+guest mode intentionally removes ambiguous local host-to-host routing in some cases by preferring guest route for local clients.

Test signals: invalid destination, hypervisor route from guest rejection, no-device errors, host local delivery, guest-to-host route, host-to-guest context delivery, VM-to-VM rejection, and invalid source context fill-in.
