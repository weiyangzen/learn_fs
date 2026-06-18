# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ras.c

Purpose: implements DRM RAS node registration and Generic Netlink handlers for listing RAS nodes and reading error counters from registered DRM driver components.

Important APIs/types/functions: global `drm_ras_xa` stores `struct drm_ras_node` by allocated ID. `struct drm_ras_ctx` carries dump restart state. Netlink handlers are `drm_ras_nl_list_nodes_dumpit()`, `drm_ras_nl_get_error_counter_dumpit()`, and `drm_ras_nl_get_error_counter_doit()`. Helpers include `get_node_error_counter()`, `msg_reply_value()`, and `doit_reply_value()`. Driver-facing registration APIs are `drm_ras_node_register()` and `drm_ras_node_unregister()`.

Control flow: register validates node names, supported type, error-counter range, and callback, then allocates an xarray ID. List-nodes dump iterates from the saved restart ID and emits one generic-netlink reply per node. Error-counter dump validates node ID, walks the node's configured error ID range from restart, skips driver-returned `-ENOENT` holes, and emits ID/name/value attributes. Single-counter doit validates node and error ID attributes, allocates a reply skb, queries the counter, appends attributes, and replies.

State and persistence behavior: RAS nodes remain in the global xarray until driver unregister. Dump restart offset is stored in netlink callback context. Error counter values are live data returned by driver callbacks, not persisted by the core.

Dependencies and integration points: depends on `drm_ras.h` driver contracts, generated `drm_ras_nl.h` command declarations, xarray allocation, and Generic Netlink message construction. Drivers integrate by filling `drm_ras_node` and callback fields.

Risks: xarray access does not add per-node refcounts, so unregister must not race active netlink dumps unless higher-level lifetime rules cover nodes. `doit_reply_value()` allocates and starts a message before querying the counter; on query failure it returns without freeing/canceling the skb, which is a leak risk. Dump handlers must update restart carefully on `-EMSGSIZE` to avoid repeating or skipping entries.

Test signals: register validation failures, list dump with multiple nodes and small skb continuation, sparse error ID ranges using `-ENOENT`, single-counter query errors and success replies, unregister during/after queries under KASAN/KCSAN, and YNL userspace coverage for the drm_ras family.
