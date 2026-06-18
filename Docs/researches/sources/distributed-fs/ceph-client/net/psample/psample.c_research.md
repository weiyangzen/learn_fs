# sources/distributed-fs/ceph-client/net/psample/psample.c

## Purpose
`psample.c` implements a generic netlink channel for packet samples and associated metadata. Kernel producers obtain a sample group, emit truncated packet bytes plus metadata to multicast listeners, and release the group when no longer used.

## Important APIs, types, and functions
Global group state is `psample_groups_list` guarded by `psample_groups_lock`. The generic netlink family is `psample_nl_family`, with config and sample multicast groups. Group APIs are `psample_group_get()`, `psample_group_take()`, and `psample_group_put()`, exported GPL. Dump support uses `psample_nl_cmd_get_group_dumpit()` and `psample_group_nl_fill()`. Notifications use `psample_group_notify()`, `psample_group_create()`, and `psample_group_destroy()`.

The sample emission API is `psample_sample_packet()`, exported GPL. Optional tunnel metadata support is under `CONFIG_INET` through `psample_tunnel_meta_len()`, `psample_ip_tun_to_nlattr()`, and `__psample_ip_tun_to_nlattr()`.

## Control flow and state
A producer calls `psample_group_get(net, group_num)`, which creates a group if needed, increments its refcount, links it globally, and multicasts a new-group notification. `psample_group_put()` decrements the refcount and destroys/notifies/frees via RCU at zero. Group dump iterates groups in the caller's net namespace.

Sampling first checks whether any listeners exist on the sample multicast group for the group namespace. It computes metadata size, includes tunnel metadata if present, clamps packet data length to `trunc_size` and the 64 KiB psample netlink size limit, allocates a generic netlink skb, writes ifindex/sample rate/original size/group/sequence/traffic class/latency/timestamp/protocol/tunnel/user-cookie/probability attributes, copies packet bytes into `PSAMPLE_ATTR_DATA`, and multicasts to listeners.

## State and persistence behavior
Groups are global in-memory objects keyed by `(net, group_num)`, with a simple integer refcount and per-group sequence counter. Sequence increments on each emitted sample. Objects are freed via `kfree_rcu()`. There is no persistent state.

## Dependencies and integration points
The file integrates with generic netlink, net namespaces, multicast listener checks, skb data copying, IP tunnel metadata (`dst_metadata`/`ip_tunnel_info`), and external packet sampling producers. The sample multicast group requires `CAP_NET_ADMIN` for listeners via `GENL_MCAST_CAP_NET_ADMIN`.

## Risks and edge cases
Risks include netlink size calculation underflow when metadata approaches `PSAMPLE_MAX_PACKET_SIZE`, group refcount misuse by producers, spinlock-held notification allocation constraints, tunnel metadata length mismatches, and sequence races if samples are emitted concurrently for the same group without locking around `group->seq++`. The code intentionally returns silently when no listeners exist to keep producers cheap.

## Test signals
Use generic netlink clients to dump groups, subscribe to config/sample multicast groups, validate group create/destroy notifications, emit samples with and without listeners, test truncation boundaries, user cookies, probability flag, tunnel metadata for IPv4/IPv6/Geneve/ERSPAN, namespace filtering, and concurrent producers hitting the same group.
