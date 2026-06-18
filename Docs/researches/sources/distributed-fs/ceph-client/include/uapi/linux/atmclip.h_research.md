<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmclip.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atmclip.h

## Purpose
Defines Classical IP over ATM constants and ioctl to create CLIP network interfaces.

## Important APIs, Types, And Functions
Exports RFC1483 LLC header length, RFC1626 default MTU, CLIP idle/check timers, and `SIOCMKCLIP` for creating an IP-over-ATM interface.

## Control Flow
Userspace creates a CLIP interface with `SIOCMKCLIP`, then ATMARP and CLIP code resolve addresses and attach VCs for IP traffic.

## State And Persistence
State includes created CLIP netdevices, idle timers, and ATMARP-managed VC mappings. It is runtime network configuration.

## Dependencies And Integration Points
Depends on socket ioctl and ATM ioctl ranges. Integrates with ATMARP, ATM PVC/SVC sockets, and IP networking over ATM.

## Risks And Edge Cases
Idle timer defaults, daemon availability, MTU expectations, and ioctl collisions in the CLIP range are compatibility concerns.

## Test Signals
CLIP interface creation, MTU defaults, idle expiry, ATMARP resolution integration, and invalid ioctl context rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmclip.h -->
