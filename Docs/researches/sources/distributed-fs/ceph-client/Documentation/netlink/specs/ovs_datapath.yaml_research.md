# sources/distributed-fs/ceph-client/Documentation/netlink/specs/ovs_datapath.yaml

Purpose: describes the legacy Generic Netlink API for Open vSwitch datapath configuration and state.

Important APIs/types/functions: protocol is `genetlink-legacy`, UAPI header `linux/openvswitch.h`, operation prefix `ovs-dp-cmd-`, and fixed header `ovs-header`. Definitions include `ovs-header` with datapath ifindex, `user-features` flags, `ovs-dp-stats`, and `ovs-dp-megaflow-stats`. The `datapath` attribute set includes datapath `name`, upcall pid(s), stats, megaflow stats, user features, mask cache size, per-CPU pids, and ifindex.

Control flow: `get` value 3 performs targeted or dump retrieval by datapath name and replies with datapath status and statistics. `new` value 1 creates a datapath with name, upcall pid, and user features. `del` value 2 deletes an existing datapath by name.

State and persistence: operations mutate or read kernel OVS datapath instances, upcall delivery configuration, stats, and flow mask cache state. This state is live kernel state and normally managed by OVS userspace daemons rather than persisted by netlink itself.

Dependencies and integration points: integrates with the kernel OVS datapath module and userspace `ovs-vswitchd`/datapath tooling. The fixed OVS header is shared with OVS flow and other OVS netlink families.

Risks: datapath name and ifindex must stay synchronized with kernel state. Upcall pids and per-CPU pids affect packet miss delivery; misconfiguration can break control-plane flow installation. Binary struct stats require exact layout compatibility with `linux/openvswitch.h`.

Test signals: create/get/delete datapath round trips, dump multiple datapaths, validate stats struct decoding, upcall pid behavior, and generated command values against `openvswitch.h`.
