# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_lag.c

Purpose: implements LAN966x hardware offload support for Linux bonding/LAG membership, hash configuration, active link state, bridge offload integration, and MAC entry migration as the representative first LAG port changes.

Important APIs and functions: exported entry points are `lan966x_lag_port_join`, `lan966x_lag_port_leave`, `lan966x_lag_port_prechangeupper`, `lan966x_lag_port_changelowerstate`, `lan966x_lag_netdev_prechangeupper`, `lan966x_lag_netdev_changeupper`, `lan966x_lag_first_port`, and `lan966x_lag_get_mask`. Internal helpers program port IDs and aggregation PGIDs via `lan966x_lag_update_ids`, `lan966x_lag_set_port_ids`, and `lan966x_lag_set_aggr_pgids`.

Control flow: pre-change validates that LAG TX type is hash-based, all LAN966x LAGs use the same hash type, and the hash type is one of L2, L23, or L34; it then programs `ANA_AGGR_CFG`. Join records `port->bond`, recalculates port IDs/forward masks/aggregation PGIDs, registers switchdev bridge-port offload for the lower port, sets STP state from the bridge port, and migrates stored MAC entries when this port becomes the first LAG representative. Leave migrates or removes LAG MAC entries if the first port leaves, clears bond state, recalculates IDs, and restores forwarding STP state. Lower-state changes update `lag_tx_active` and rebuild aggregation PGIDs.

State and persistence: per-port LAG state is `bond`, `lag_tx_active`, and `hash_type`. Hardware state persists in source/destination PGIDs, aggregation PGIDs, `ANA_PORT_CFG_PORTID_VAL`, and `ANA_AGGR_CFG`. Software MAC entries track whether they were learned for a LAG and may be reprogrammed to a new representative port.

Dependencies and integration points: depends on Linux netdev LAG notifier data, bridge STP helpers, switchdev bridge port offload, LAN966x switchdev notifier blocks, forwarding-mask update code, and MAC table LAG migration helpers.

Risks: only one hash type is allowed across all LAN966x LAGs because the hardware aggregation config is global. First-port selection changes can race logically with FDB/MAC notifier updates if ordering is wrong. Aggregation PGID programming must handle zero active members without division by zero. Bridge offload failure must roll back `port->bond` and hardware IDs.

Test signals: create/delete bonds with LAN966x ports; unsupported TX/hash type extack; L2/L23/L34 hash traffic distribution; link up/down active member changes; adding/removing the lowest-numbered LAG member; bridge+bond FDB offload; STP state transitions; multiple bonds with matching and mismatched hash types.
