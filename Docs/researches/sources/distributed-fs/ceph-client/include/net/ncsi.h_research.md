<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ncsi.h -->
# sources/distributed-fs/ceph-client/include/net/ncsi.h

## Purpose
`ncsi.h` exposes the public Network Controller Sideband Interface state and functions used by NIC drivers that delegate management traffic/control to NCSI.

## Important APIs, types, and functions
It defines external device states, `struct ncsi_dev`, and enabled or stubbed functions for VLAN VID add/kill, device registration, start, stop, and unregister.

## Control flow
A netdevice driver registers an NCSI device with a notifier, starts it to select/configure an active package/channel, reacts to state/link callbacks, and stops/unregisters on teardown. Without `CONFIG_NET_NCSI`, calls return errors or no-ops.

## State and persistence
Runtime state is the NCSI state integer, link-up flag, back pointer to netdevice, and notifier handler. More detailed package/channel state lives in internal NCSI headers and implementation.

## Dependencies and integration points
It depends on netdevice and CONFIG_NET_NCSI. It integrates BMC/NCSI management channels with Ethernet drivers.

## Risks and test signals
Risks include callers not handling disabled stubs, state-machine transitions during suspend/config/probe, VLAN synchronization failures, and callback lifetime. Tests should cover enabled and disabled builds, register/start/stop/unregister order, link-up notifications, VLAN events, and suspend/config state transitions.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/ncsi.h` completely for this pass (72 lines, 1990 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ncsi.h -->
