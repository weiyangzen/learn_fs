# sources/distributed-fs/ceph-client/drivers/net/ovpn/main.h

Purpose: declares the minimal public device-identification helper for the ovpn module.

Important APIs/types/functions: `ovpn_dev_is_valid()` returns whether a net_device is backed by ovpn netdev ops.

Control flow: header only; implementation lives in `main.c`.

State and persistence: no state.

Dependencies and integration: used by netlink or peer-management code that receives an ifindex/netdev and must reject non-ovpn devices before accessing `struct ovpn_priv`.

Risks: correctness depends on comparing the expected `netdev_ops`; any future alternate ovpn ops table would need this helper updated.

Test signals: call through netlink pre-doit on ovpn and non-ovpn devices, and compile all users against the declaration.
