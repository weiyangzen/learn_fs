# sources/distributed-fs/ceph-client/Documentation/netlink/specs/ovs_vport.yaml

Purpose: this YAML describes the Open vSwitch vport generic-netlink legacy family, binding the userspace ABI in `linux/openvswitch.h` to generated netlink documentation and schema data. It models datapath vports, their tunnel options, upcall delivery, statistics, and notifications.

Important APIs, types, and functions: the top-level family is `ovs_vport` version 2 with fixed `ovs-header` containing `dp-ifindex`. The main enum is `vport-type` (`unspec`, `netdev`, `internal`, `gre`, `vxlan`, `geneve`). Attribute sets include `vport-options` (`dst-port`, `extension`), `upcall-stats` (`success`, `fail`), and `vport` attributes such as `port-no`, `type`, `name`, `options`, `upcall-pid`, `stats`, `ifindex`, `netnsid`, and nested `upcall-stats`. `ovs-vport-stats` carries packet, byte, error, and drop counters as 64-bit fields.

Control flow: generated consumers use `ovs-vport-cmd-new` to create vports with `name`, `type`, optional `upcall-pid`, `ifindex`, and tunnel `options`; `del` removes by `port-no`, `type`, or `name`; `get` supports both single lookup by name and dump. Replies return port identity, upcall state, interface indices, and counters. Multicast group `ovs_vport` is the integration point for asynchronous vport updates.

State and persistence: this file itself is declarative. Runtime state is owned by the OVS datapath in the kernel: vport membership, names, tunnel port options, upcall pids, namespace ids, and monotonically changing stats.

Dependencies and integration: depends on the generic netlink legacy generator, `linux/openvswitch.h`, and OVS datapath semantics. The schema is consumed by documentation/generation tooling and by userspace ABI readers such as OVS control utilities.

Risks: binary fields (`upcall-pid`, `stats`) rely on exact struct layout and endian expectations. The `dst-port` tunnel option is typed as `u32`, so callers must track kernel interpretation. Dumps must handle concurrent datapath mutation. Tests should validate generated enum values against `openvswitch.h`, create/get/delete vport round trips, nested tunnel option encoding, and stats/upcall-stats presence in dumps.
