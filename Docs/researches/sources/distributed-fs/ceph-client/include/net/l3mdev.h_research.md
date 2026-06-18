# sources/distributed-fs/ceph-client/include/net/l3mdev.h

Purpose: Provides the L3 master device API used by VRF-like devices to steer FIB rules, route table lookup, link-scope IPv6 lookup, and L3 receive/output hooks.

Important APIs/types/functions: `l3mdev_type` currently defines VRF. `l3mdev_ops` supplies per-device callbacks for FIB table id, L3 receive, L3 output, and IPv6 link-scope lookup. APIs include table lookup registration, ifindex lookup by table id, FIB rule match, flow update, master ifindex/device lookup, table lookup by device/index, link-scope lookup, and IP/IP6 receive/output inline wrappers. Disabled builds return no-op or negative stubs.

Control flow: FIB rule matching compares `flowi_l3mdev` with input or output ifindex based on `FLOWI_FLAG_L3MDEV_OIF`. Flow update populates L3 master context. Receive wrappers select the master for L3 slaves or L3 rx-handler devices and invoke `l3mdev_l3_rcv`; output wrappers inspect dst device under RCU and invoke master output op for slaves.

State and persistence: The header does not own state; L3 master membership is in netdevice upper/lower relationships and per-device `l3mdev_ops`. Table lookup callbacks are registered per L3 type.

Dependencies/integration: Depends on `dst`, fib rules, netdevice L3 master/slave flags, RCU device lookup, IPv6 `flowi6`, and VRF implementation.

Risks: RCU device lookup must wrap master access; const removal in `l3mdev_master_dev_rcu` is intentional but must remain read-only; disabled stubs must not accidentally make rules match incorrectly. Test signals include VRF table lookup, input/output FIB rules, link-local IPv6 route lookup, L3 receive/output hooks, netdevice enslave/unenslave, and no-op behavior without `CONFIG_NET_L3_MASTER_DEV`.
