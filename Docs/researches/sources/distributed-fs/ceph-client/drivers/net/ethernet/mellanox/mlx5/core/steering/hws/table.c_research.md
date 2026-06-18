# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/table.c

Purpose: manages HWS flow-table objects, default FDB miss behavior, table creation/destruction, and chaining one table's miss path to another table or matcher RTC.

Important APIs/functions: `mlx5hws_table_create`, `mlx5hws_table_destroy`, `mlx5hws_table_get_id`, `mlx5hws_table_create_default_ft`, `mlx5hws_table_destroy_default_ft`, `mlx5hws_table_connect_to_miss_table`, `mlx5hws_table_update_connected_miss_tables`, `mlx5hws_table_ft_set_default_next_ft`, `mlx5hws_table_ft_set_next_rtc`, and `mlx5hws_table_ft_set_next_ft`.

Control flow: create validates HWS support and table type, creates a firmware flow table under `ctx->ctrl_lock`, obtains default STCs, initializes matcher/default-miss lists, and links into the context table list. FDB tables create/reference a shared default miss table that forwards to the eswitch-manager vport. Miss-table connection chooses the source table's last FT, then either sets a GOTO table miss action or connects the last FT directly to the first matcher RTCs in the destination table.

State/persistence: `mlx5hws_table` stores firmware table IDs, type, UID, level, matcher list, context list node, and default-miss relationship. The shared `ctx->common_res.default_miss` is refcounted. State is in-memory plus firmware flow table objects; no persistent storage.

Dependencies/integration: relies on HWS command wrappers, action default STC management, context capabilities (`ignore_flow_level_rtc_valid`, FDB levels), matcher RTC IDs, and Linux lists/mutexes.

Risks: miss-chain correctness depends on list ordering and lock discipline. Destroy refuses tables with matchers or incoming default-miss users, but misuse can leave firmware miss actions pointing at destroyed tables. FDB default miss refcounting assumes create/destroy paths remain paired.

Test signals: table create/destroy under empty and busy conditions, FDB default miss refcount reuse, connect/disconnect to empty and populated destination tables, matcher insertion order changes, and capability-disabled default miss support.
