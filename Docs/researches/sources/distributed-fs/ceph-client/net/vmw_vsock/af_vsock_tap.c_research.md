# sources/distributed-fs/ceph-client/net/vmw_vsock/af_vsock_tap.c

## Purpose
`af_vsock_tap.c` implements packet tap support for AF_VSOCK monitoring devices. It lets vsock monitor drivers register `ARPHRD_VSOCKMON` net devices and receive cloned skbuffs for observed vsock traffic.

## Important APIs, Types, And Functions
The exported APIs are `vsock_add_tap()`, `vsock_remove_tap()`, and `vsock_deliver_tap()`. Registered taps are `struct vsock_tap` entries in the RCU-protected `vsock_tap_all` list, protected for mutation by `vsock_tap_lock`.

## Control Flow
A monitor calls `vsock_add_tap()` with a tap whose device type must be `ARPHRD_VSOCKMON`; the module reference is incremented and the tap is inserted with `list_add_rcu()`. Removal searches the list, deletes the entry with `list_del_rcu()`, waits for `synchronize_net()`, and drops the module reference. Transports call `vsock_deliver_tap()` with a callback that builds a monitor-format skb only when at least one tap exists, then each tap receives a cloned skb via `dev_queue_xmit()`.

## State And Persistence
Runtime state is the global tap list and module references held while a tap is registered. The delivered monitor packet is transient; the original transport packet remains owned by the caller.

## Dependencies And Integration Points
This file depends on net devices, RCU, skbuff cloning, and module reference counting. It integrates with `virtio_transport_common.c` through `virtio_transport_deliver_tap_pkt()`, which builds `vsockmon` headers before calling into the generic tap fanout.

## Risks And Edge Cases
Tap delivery runs under RCU and may be in atomic contexts, so allocation uses `GFP_ATOMIC` and failures silently skip clones. Incorrect device type registration is rejected. A delivery error breaks fanout early, so one failing tap can prevent later taps from observing a packet.

## Test Signals
Test signals include loading a vsockmon device, registering and unregistering taps under traffic, verifying cloned packets with tcpdump-like tooling, module unload after tap removal, and stress testing allocation failure and concurrent tap removal with KASAN/RCU diagnostics.
