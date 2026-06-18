<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psample.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/psample.h

Purpose: defines the generic netlink ABI for packet sampling events, sample groups, tunnel metadata, and sample-rate/probability reporting.

Important APIs and types: `PSAMPLE_ATTR_*` attributes describe ingress/egress ifindex, original size, sample group, group sequence, sample rate or probability, packet data, group refcount, tunnel metadata, output TC occupancy, latency, timestamp, protocol, and user cookie. `enum psample_command` includes sample and group operations. `enum psample_tunnel_key_attr` carries tunnel ID, IPv4/IPv6 endpoints, ToS/TTL, flags, Geneve/VXLAN/ERSPAN options, transport ports, and bridge mode. Family constants are `PSAMPLE_GENL_NAME`, version, and multicast group names.

Control flow: kernel sampling producers emit `PSAMPLE_CMD_SAMPLE` generic-netlink messages with attributes to the packets multicast group; userspace can query and receive group config messages via the config group.

State and persistence: sample groups, sequence counters, and refcounts are runtime network namespace state. Individual samples are transient netlink messages and are not persisted.

Dependencies and integration points: integrates with generic netlink, tc sample action, switchdev/offload sampling, tunnel metadata, monitoring collectors, and network telemetry systems.

Risks and test signals: risks include dropped multicast samples, inconsistent rate/probability semantics, oversized packet data, tunnel attribute mismatch, and group refcount leaks. Test tc sample action, hardware/offload sampled packets, netlink attribute validation, multicast listener loss behavior, and tunnel metadata decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psample.h -->
