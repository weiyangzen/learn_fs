# sources/distributed-fs/ceph-client/drivers/net/ovpn/netlink.h

Purpose: Declares the ovpn module's public netlink hooks used outside `netlink.c`.

Important APIs, types, and functions: The header exposes `ovpn_nl_register()` and `ovpn_nl_unregister()` for module initialization/cleanup, plus notification helpers `ovpn_nl_peer_del_notify()`, `ovpn_nl_peer_float_notify()`, and `ovpn_nl_key_swap_notify()`. It forward-relies on `struct ovpn_peer`, `struct sockaddr_storage`, and `u8` being visible through includers.

Control flow: Main module setup calls the register/unregister pair around generic-netlink family lifetime. Peer-management code calls delete and float notifications after state changes. Crypto/data-path code can call key-swap notification when a primary key becomes unusable.

State and persistence behavior: No state is defined here. The declarations are entry points into netlink multicast and registration code that acts on runtime peer/socket state.

Dependencies and integration points: This header ties peer lifetime and crypto state transitions to the generic-netlink userspace ABI in `linux/ovpn.h`. It is included by peer and module code that must report kernel-side events to OpenVPN userspace.

Risks and edge cases: Callers must hold or otherwise own a valid peer reference while notifying because the implementation reads peer fields and RCU-protected socket state. Notification failures are non-fatal but should be visible to tests because userspace may rely on them to clean up or rekey.

Test signals: Build tests should catch missing type includes in includers. Runtime signals are successful generic-netlink family registration, teardown without stale family objects, and multicast notifications for peer expiry, userspace deletion, transport disconnect, floating, and key renewal.
