# sources/distributed-fs/ceph-client/net/core/netdev-genl-gen.h

## Purpose

`netdev-genl-gen.h` is the generated header for the generic netlink `netdev` family. It declares the generated policy arrays, operation callbacks to be provided by implementation code, multicast group IDs, the family object, and per-socket private hooks.

## Important APIs, Types, And Functions

The header declares `netdev_lease_nl_policy`, `netdev_page_pool_info_nl_policy`, and `netdev_queue_id_nl_policy`; doit/dump callbacks for device, page-pool, queue, NAPI, qstats, dmabuf bind, NAPI set, and queue create commands; multicast group enum values `NETDEV_NLGRP_MGMT` and `NETDEV_NLGRP_PAGE_POOL`; `extern struct genl_family netdev_nl_family`; and `netdev_nl_sock_priv_init()`/`netdev_nl_sock_priv_destroy()`.

## Control Flow

Implementation files include this header to provide the declared callbacks and register or reference `netdev_nl_family`. The generated C file includes this header to build the split operation table and family descriptor.

## State And Persistence Behavior

The header owns no runtime state. It defines link-time contracts for static policy arrays and the family descriptor.

## Dependencies And Integration Points

It depends on generic netlink headers, UAPI `linux/netdev.h`, and `net/netdev_netlink.h` for callback/private state types. It is tied to `Documentation/netlink/specs/netdev.yaml` and `tools/net/ynl/ynl-regen.sh`.

## Risks

Regenerating the YAML output can change callback declarations, group IDs, policy array names, or family wiring. Consumers must stay in sync with this generated contract. Missing callbacks or signature drift will fail builds; semantic drift can break user-space netdev netlink clients.

## Test Signals

Build coverage is the direct signal. Runtime signals come from generic netlink registration and YNL command tests that exercise every declared callback path.
