# sources/distributed-fs/ceph-client/drivers/net/vsockmon.c

## Purpose
`vsockmon.c` implements a lightweight rtnetlink-created monitoring netdevice for AF_VSOCK traffic, modeled after `nlmon`. It registers a `vsockmon` link kind whose open path attaches a `vsock_tap` to the VSOCK core so packets can be observed through normal network-device capture paths.

## Important APIs, Types, And Functions
`struct vsockmon` wraps `struct vsock_tap`. `vsockmon_open()` registers the tap; `vsockmon_close()` removes it; `vsockmon_xmit()` accounts and frees SKBs; `vsockmon_get_stats64()` reads lightweight stats; `vsockmon_change_mtu()` validates MTU against `struct af_vsockmon_hdr`; `vsockmon_setup()` initializes the netdev; and `vsockmon_link_ops` registers rtnl kind `vsockmon`.

## Control Flow
Module init registers rtnetlink link ops. Creating a device calls setup. Bringing it up registers a VSOCK tap; bringing it down unregisters the tap. Transmit counts bytes/packets and drops the SKB. Ettool link status is always reported as up.

## State And Persistence
Per-device state is the embedded `vsock_tap`, populated while open. The netdevice is freed by core due to `needs_free_netdev`. Stats are per-CPU lightweight stats. Default MTU is `VIRTIO_VSOCK_MAX_PKT_BUF_SIZE + sizeof(struct af_vsockmon_hdr)`.

## Dependencies And Integration Points
Depends on rtnetlink, netdevice, ethtool, AF_VSOCK monitor UAPI, VSOCK tap APIs, and virtio-vsock packet sizing. Userspace creates a `vsockmon` link and captures packets from it.

## Risks
MTU validation must track monitor header size. Open/close must balance tap registration. Transmit always frees packets, so accidental data-device use silently drops traffic by design.

## Test Signals
Create/delete links, up/down cycles, tap registration balance, capture VSOCK traffic, ethtool link reporting, MTU edge cases, and stats increments.
