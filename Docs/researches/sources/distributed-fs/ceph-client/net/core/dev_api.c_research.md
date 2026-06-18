# sources/distributed-fs/ceph-client/net/core/dev_api.c

Purpose: Provides exported netdevice management APIs that wrap lower-level `netif_*` helpers with the correct netdev lock or ops lock. These functions are common entry points for in-kernel callers and uAPI adapters that need to change names, flags, aliases, MAC addresses, MTU, carrier, promiscuity, allmulti state, XDP state, threaded NAPI mode, and device state notifications.

Important APIs, types, and functions: Key exports include `dev_set_alias()`, `dev_change_flags()`, `dev_set_mac_address_user()`, `dev_change_net_namespace()`, `dev_open()`, `dev_close()`, `dev_eth_ioctl()`, `dev_set_mtu()`, `dev_disable_lro()`, `dev_set_promiscuity()`, `dev_set_allmulti()`, `dev_set_mac_address()`, `dev_xdp_propagate()`, `netdev_state_change()`, and `dev_set_threaded()`. Internal wrappers also cover `dev_change_name()`, `dev_set_group()`, `dev_change_carrier()`, `dev_change_tx_queue_len()`, and `dev_change_proto_down()`.

Control flow and state: The file is deliberately thin. Each function acquires `netdev_lock_ops()` or `netdev_lock()` as appropriate, calls the corresponding `netif_*` operation, and releases the lock. Calls that alter RX filtering visibility, such as flags, promiscuity, and allmulti changes, call `netif_rx_mode_sync()` before unlocking so deferred async RX-mode work is completed before returning to userspace. `dev_set_mac_address_user()` additionally serializes through `dev_addr_sem` around MAC address changes.

Dependencies and integration points: It depends on `linux/netdevice.h`, `net/netdev_lock.h`, and declarations in `dev.h`. It is used by ioctl, rtnetlink, drivers, and other kernel subsystems that need a stable lock boundary without directly calling lower-level `netif_*` functions.

Risks: Because most logic lives below this layer, the main risks are missing lock coverage, using `netdev_lock()` where ops locking is required or vice versa, and forgetting RX-mode synchronization for APIs whose users expect filtering changes to be visible on return. `dev_eth_ioctl()` must guard driver callbacks with both ops presence and `netif_device_present()` to avoid invoking removed hardware.

Test signals: Functional signals include successful `ip link` flag, MTU, name, alias, MAC, carrier, proto-down, promisc/allmulti, XDP, and threaded-NAPI operations under lockdep. Async RX-mode drivers should observe that userspace-facing setters return only after `netif_rx_mode_sync()` has run.
