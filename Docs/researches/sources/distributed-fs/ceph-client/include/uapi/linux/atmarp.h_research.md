<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmarp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atmarp.h

## Purpose
Defines ATMARP protocol constants and the kernel-to-daemon control message ABI for Classical IP over ATM address resolution.

## Important APIs, Types, And Functions
Exports retry/queue constants, ioctls `ATMARPD_CTRL`, `ATMARP_MKIP`, `ATMARP_SETENTRY`, and `ATMARP_ENCAP`, `enum atmarp_ctrl_type`, and `struct atmarp_ctrl`.

## Control Flow
An ATMARP daemon registers a control socket, receives need/up/down/change events, resolves IP-to-ATM mappings, attaches sockets to IP, sets ARP entries, and configures encapsulation.

## State And Persistence
State includes runtime ARP cache entries, unresolved packet queues, daemon control socket registration, and encapsulation settings. Persistence is external to the kernel ABI.

## Dependencies And Integration Points
Depends on Linux types, ATM API alignment, and ATM ioctl ranges. Integrates with Classical IP over ATM and ATMARP daemon tooling.

## Risks And Edge Cases
Unresolved queue limits, retry timing, daemon absence, network byte order IP fields, and stale hidden entries are operational risks.

## Test Signals
Daemon registration, need/up/down/change message delivery, ARP entry set/hide, encapsulation changes, retry timeout behavior, and queue overflow handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmarp.h -->
