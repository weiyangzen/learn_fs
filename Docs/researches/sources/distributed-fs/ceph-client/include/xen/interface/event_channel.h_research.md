<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/event_channel.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/event_channel.h

## Purpose
This Xen public header defines the event-channel hypercall ABI: port type, operation numbers, argument structures, status values, 2-level channel capacity, and FIFO event-channel layout.

## Important APIs, Types, And Functions
- `evtchn_port_t` is a 32-bit port identifier and has a guest-handle type.
- Operation structures cover allocate unbound, bind interdomain, bind VIRQ, bind PIRQ, bind IPI, close, send, status, bind VCPU, unmask, reset, FIFO control initialization, FIFO array expansion, and priority setting.
- `struct evtchn_status` reports channel state and associated remote domain/port, PIRQ, or VIRQ.
- `struct evtchn_op` is the legacy union wrapper for selected operations.
- `EVTCHN_2L_NR_CHANNELS` derives two-level ABI capacity from `xen_ulong_t`.
- FIFO constants define priorities, event-word bits (`PENDING`, `MASKED`, `LINKED`, `BUSY`), link width/mask, maximum channels, and `struct evtchn_fifo_control_block`.

## Control Flow
Guests allocate or bind ports, optionally bind them to VCPUs, unmask them, send notifications, query status, close/reset them, or initialize FIFO control pages. The Linux `xen/events.h` layer wraps these ABI structures in IRQ APIs.

## State And Persistence
Event-channel state persists in Xen: port allocation, channel type/status, remote endpoint, VCPU binding, mask/pending bits, FIFO queues, priorities, and control/array pages.

## Dependencies And Integration Points
It depends on Xen base types and guest handles. It is the shared ABI for Linux event handling, Xenbus, console, block/net front/back drivers, userspace event-channel devices, and hypervisor tooling.

## Risks And Edge Cases
Privilege restrictions apply to binding physical IRQs or querying other domains. VIRQ/IPI bindings are tied to VCPUs and cannot be moved like normal channels. FIFO setup requires correct page GFNs/offsets and link-bit handling. Closing interdomain channels changes the remote endpoint to unbound, which peers must handle.

## Test Signals
Signals include successful alloc/bind/send/close/status operations, VCPU binding behavior, reset closing channels, FIFO control initialization and priority delivery, correct status transitions, and permission failures for unprivileged cross-domain/PIRQ operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/event_channel.h -->
