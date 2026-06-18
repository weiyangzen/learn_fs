# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/int_port.c

Purpose: Manages OVS internal-port offload objects, metadata mappings, RX restore rules, and skb forwarding for internal ingress/egress ports.

Important APIs: `mlx5e_tc_int_port_supported()`, init/cleanup, rep RX init/cleanup, get/put, metadata getters, flow source getter, and `mlx5e_tc_int_port_dev_fwd()`.

Control flow: Init creates a metadata mapping context keyed by SW image GUID. `get()` locks, checks uplink RX readiness, looks up an existing `(ifindex,type)` object or allocates one. Allocation reserves metadata, maps it into reg_c0 object pool for miss handling, creates an RX rule matching metadata and forwarding to uplink root FT, adds the object to an RCU list, and sets refcount. Put removes and frees on last reference. Rep RX cleanup marks RX not ready and deletes RX rules in-place while preserving objects.

State and persistence: `mlx5e_tc_int_port_priv` owns device, mutex, RCU list, port count, readiness flag, and metadata mapping. Each internal port stores type, ifindex, match metadata, reg_c0 mapping id, RX rule, refcount, and RCU head.

Dependencies and integration: Requires eswitch vport metadata and `reg_c_preserve`, mapping API, reg_c0 object pool, uplink representor root table, flow rules, and skb forwarding helpers. Action parsers call into this code to program internal-port actions.

Risks and tests: Cleanup currently destroys the mutex and mapping without explicitly draining the int-port list; expected callers must release refs first. RX teardown leaves objects with `rx_rule = NULL`, so add/remove paths must tolerate it. `mlx5e_tc_int_port_dev_fwd()` uses `init_net` and does not `dev_put()` after `dev_get_by_index()`, which should be reviewed for reference handling in the broader code. Tests should cover max port count, duplicate get refcounting, metadata allocation/free, rep RX teardown/reinit, ingress/egress skb rewrite, unsupported caps, and concurrent get/put.
