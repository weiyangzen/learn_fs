<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/rss.c -->
# sources/distributed-fs/ceph-client/net/ethtool/rss.c

## Purpose
Implements the ethtool netlink RSS API: reading, dumping, modifying, creating, and deleting receive-side scaling contexts, indirection tables, hash keys, hash functions, input transforms, and per-flow hash-field selections.

## APIs, Types, and Functions
Defines `struct rss_req_info`, `struct rss_reply_data`, flow-type mapping table `ethtool_rxfh_ft_nl2ioctl`, GET/SET/CREATE/DELETE policies, and `ethnl_rss_request_ops`. Important helpers include `rss_parse_request()`, `rss_prepare_flow_hash()`, `rss_get_data_alloc()`, `rss_prepare_get()`, `rss_prepare_ctx()`, `rss_prepare()`, `rss_fill_reply()`, dump helpers `ethnl_rss_dump_start()` and `ethnl_rss_dumpit()`, mutation helpers `rss_set_prep_indir()`, `rss_set_prep_hkey()`, `ethnl_set_rss_fields()`, `rss_set_ctx_update()`, plus `ethnl_rss_create_doit()` and `ethnl_rss_delete_doit()`.

## Control Flow, State, and Persistence
GET parses an optional context ID, rejects `START_CONTEXT`, snapshots flow hash fields if supported, and either calls driver `get_rxfh()` for the default context or loads a saved `struct ethtool_rxfh_context` from `dev->ethtool->rss_ctx`. Dumps iterate devices and context IDs using callback cursor state. SET prepares current state, validates/rebuilds an indirection table, duplicates and updates the hash key, handles hash function and input transform changes, updates per-flow fields under `dev->ethtool->rss_lock`, then calls `set_rxfh()` or `modify_rxfh_context()` as needed and mirrors accepted values back into kernel context storage. CREATE allocates a context, assigns or inserts an XArray ID, calls the driver, builds a reply, and converts the same skb into a create notification. DELETE checks context busy state, calls driver removal, erases the XArray entry, frees the context, and emits delete notification. Persistent state is per-netdev RSS metadata: `rss_ctx`, `rss_indir_user_size`, and context fields.

## Dependencies and Integration
Depends on ethtool driver operations `get_rxfh`, `set_rxfh`, `create_rxfh_context`, `modify_rxfh_context`, `remove_rxfh_context`, `get_rxfh_fields`, and `set_rxfh_fields`; on `dev->ethtool->rss_lock`; on XArray context storage; and on RX ring count helpers. It integrates with ethtool notifications, rtnl and netdev ops locks, and generic-netlink dump cursors.

## Risks and Test Signals
Risks include races between driver callbacks and XArray state, validating user indirection tables against changing queue counts, partial flow-field updates before later driver RSS config failure, symmetric input-transform conflicts with non-symmetric flow fields, and notification build failures after context creation. Test signals should cover default and per-context GET, dump start context, indirection replication and reset, queue out-of-range errors, key length checks, unsupported per-context key/fields, symmetric transform conflicts, create with automatic and explicit IDs, busy delete, and create/delete notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/rss.c -->
