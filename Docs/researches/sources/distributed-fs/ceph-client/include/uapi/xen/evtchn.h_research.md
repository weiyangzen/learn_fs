<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/xen/evtchn.h -->
# sources/distributed-fs/ceph-client/include/uapi/xen/evtchn.h

Purpose: defines the `/dev/xen/evtchn` userspace ABI for binding, notifying, unbinding, resetting, restricting, and statically binding Xen event channels.

Important APIs and types: ioctl structs include `ioctl_evtchn_bind_virq`, `bind_interdomain`, `bind_unbound_port`, `unbind`, `notify`, `restrict_domid`, and `bind`. Ioctl numbers use `_IOC()` with type `'E'` and operation IDs `0..7`.

Control flow: userspace opens the event channel device, binds a VIRQ/interdomain/unbound/static port, waits for events via the file descriptor, notifies ports, unbinds ports, resets event buffers, or restricts future interdomain binds to one domid.

State and persistence: state is per file descriptor: bound ports, buffered pending events, error/reset condition, and an optional irreversible domid restriction. Event channels are runtime hypervisor/kernel resources, not persistent data.

Dependencies and integration points: depends on Xen public types such as `domid_t` from the include environment. It integrates with Xen control stacks, backend/frontend drivers in userspace, and event-channel hypercalls.

Risks and test signals: risks include stale bindings after restriction, domid validation, event buffer reset semantics, port lifetime on fd close, and ioctl compatibility. Test bind/notify/read/unbind, restriction behavior, static port errors, reset after overflow, and multi-domain access control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/xen/evtchn.h -->
