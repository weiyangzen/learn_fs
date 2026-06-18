
# sources/distributed-fs/ceph-client/net/devlink/rate.c

## Purpose
This file implements devlink rate objects. Rate leaves are attached to devlink ports, while rate nodes are named hierarchy objects. The API exposes transmit share/max limits, priority, weight, parent-node assignment, and per-traffic-class bandwidth arrays through devlink netlink commands and driver callbacks.

## Important APIs, Types, And Functions
Object classification uses `devlink_rate_is_leaf()` and exported `devlink_rate_is_node()`. Lookup helpers resolve leaves from `DEVLINK_ATTR_PORT_INDEX` and nodes from `DEVLINK_ATTR_RATE_NODE_NAME`, rejecting empty or all-decimal node names.

Netlink output is built by `devlink_nl_rate_fill()`, which emits device handle, rate type, leaf port index or node name, tx share/max, priority, weight, optional parent name, and all `DEVLINK_RATE_TCS_MAX` traffic-class bandwidth values via `devlink_rate_put_tc_bws()`.

Command handlers are `devlink_nl_rate_get_doit()`, `devlink_nl_rate_get_dumpit()`, `devlink_nl_rate_set_doit()`, `devlink_nl_rate_new_doit()`, and `devlink_nl_rate_del_doit()`. Driver-facing creation/destruction APIs are `devl_rate_node_create()`, `devl_rate_leaf_create()`, `devl_rate_leaf_destroy()`, and `devl_rate_nodes_destroy()`. `devlink_rates_check()` lets other code reject teardown while rate nodes exist.

## Control Flow
Set operations first resolve the target object, check that every requested attribute has the corresponding leaf or node operation in `struct devlink_ops`, then apply fields one by one in `devlink_nl_rate_set()`. Each successful callback updates the cached devlink value. Parent changes call the relevant parent-set callback, prevent self-parenting and cycles, and maintain parent refcounts.

Creating a node requires driver support for both `rate_node_new` and `rate_node_del`. The code rejects duplicate valid names, allocates a node, calls the driver's create callback, applies any requested initial rate attributes, initializes the refcount, links the node into `devlink->rate_list`, and notifies userspace. Deleting a node requires `refcnt == 1`, which means no children currently reference it.

Traffic-class bandwidth updates parse every repeated `DEVLINK_ATTR_RATE_TC_BWS` nest, reject duplicate TC indexes, require all traffic classes to be specified, call the driver TC bandwidth setter, and then copy the full array into cached state.

## State And Persistence
Rate state is in memory on `devlink->rate_list` and on `devlink_port->devlink_rate`. Each object caches type, parent pointer, refcount, driver private pointer, name for nodes, and configured bandwidth/rate/priority/weight values. The file does not persist settings itself; driver callbacks may program hardware or persistent firmware policies.

## Dependencies And Integration Points
The file depends on `devl_internal.h`, `struct devlink_ops` rate callbacks, generated nested TC bandwidth policy from `netlink_gen.c`, and the port lookup helpers from `port.c`. Drivers create leaves during port setup and may create nodes themselves or allow userspace-created nodes through `DEVLINK_CMD_RATE_NEW`.

## Risks And Edge Cases
Set operations are not transactional. If `tx_share` succeeds and `tx_max` fails, cached and hardware state retain the first change. Parent reassignment updates refcounts only after driver callbacks succeed, but failures inside driver callbacks must leave hardware topology unchanged.

`devl_rate_node_create()` increments the parent refcount before duplicating the node name; if name allocation fails, the parent refcount is not decremented in this implementation. That is a leak risk on the driver-created node path. The netlink-created path does not have that exact ordering.

`devl_rate_nodes_destroy()` assumes parent-set and delete callbacks are available and ignores callback errors during cleanup, which is common for teardown but means hardware cleanup failures are not reported to userspace.

## Test Signals
The local tree references `tools/testing/selftests/drivers/net/hw/devlink_rate_tc_bw.py`, which is directly relevant to the all-TC bandwidth parsing and validation path. Additional useful tests cover hierarchy cycle rejection, deleting a node with children, parent clear/reassign, leaf create/destroy under port lifecycle, and partial failure behavior of multi-attribute sets.
