# sources/distributed-fs/ceph-client/net/core/netdev-genl-gen.c

## Purpose

`netdev-genl-gen.c` is generated YNL kernel code for the generic netlink `netdev` family described by `Documentation/netlink/specs/netdev.yaml`. It defines attribute validation policies, split operation dispatch, multicast groups, per-socket private-data hooks, and the `genl_family` object.

## Important APIs, Types, And Functions

The file exports policy arrays for common nested types: `netdev_lease_nl_policy`, `netdev_page_pool_info_nl_policy`, and `netdev_queue_id_nl_policy`. It defines command-specific policies for device get, page-pool get/stats, queue get/create, NAPI get/set, qstats get, dmabuf bind RX/TX, and queue creation. The `netdev_nl_ops` array maps commands to implementation callbacks declared in the generated header but implemented elsewhere. `netdev_nl_mcgrps` declares `mgmt` and `page-pool` multicast groups. `netdev_nl_family` is the exported family object.

## Control Flow

Generic netlink registration code consumes `netdev_nl_family`. Incoming requests are validated using the policy associated with the matching `genl_split_ops` entry, then dispatched to callbacks such as `netdev_nl_dev_get_doit()`, `netdev_nl_queue_get_dumpit()`, `netdev_nl_napi_set_doit()`, or `netdev_nl_queue_create_doit()`. Dump and do operations are split when both forms exist. Per-netlink-socket private data is initialized and destroyed through wrappers around `netdev_nl_sock_priv_init()` and `netdev_nl_sock_priv_destroy()`.

## State And Persistence Behavior

The generated file stores static validation metadata and the global `genl_family` descriptor. Runtime request state belongs to generic netlink and the implementation callbacks. Family socket private state has size `sizeof(struct netdev_nl_sock)` and is managed by the callback hooks.

## Dependencies And Integration Points

It depends on generic netlink, netlink policy helpers, UAPI `linux/netdev.h`, and implementation functions from `net/netdev_netlink.h`. Conditional operations depend on `CONFIG_PAGE_POOL` and `CONFIG_PAGE_POOL_STATS`. Administrative commands are marked with `GENL_ADMIN_PERM`; the family is namespace-aware with `netnsok = true` and permits `parallel_ops`.

## Risks

Because this file is generated, manual edits would be overwritten and may desynchronize from the YAML spec. Policy mistakes can reject valid user requests or accept invalid attributes. Range checks are security-relevant for IDs, ifindexes, queue types, NAPI settings, and dmabuf binding. `parallel_ops = true` means callbacks must provide their own synchronization.

## Test Signals

Signals include YNL selftests generated from the spec, generic netlink family introspection, command validation tests for accepted/rejected attributes, namespace tests, page-pool config matrix builds, and admin-permission checks for privileged operations.
