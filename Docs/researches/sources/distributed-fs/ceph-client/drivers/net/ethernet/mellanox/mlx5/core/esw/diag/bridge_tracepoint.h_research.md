# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/diag/bridge_tracepoint.h

Purpose: Defines tracepoints for mlx5 bridge offload lifecycle and multicast membership changes.

Important APIs/types/functions: Trace event classes cover FDB entries, VLANs, bridge ports, and MDB port attach/detach. Events include FDB init/refresh/cleanup, VLAN create/cleanup, vport init/cleanup, and MDB attach/detach. Each event copies relevant fields into trace entries and prints compact identifiers such as netdev name, MAC, VID, flags, use age, port count, and offload state.

Control flow and integration: `bridge.c` defines `CREATE_TRACE_POINTS` before including this file, generating tracepoint definitions. `bridge_mcast.c` includes it for trace event calls. The include path/file macros at the end point ftrace to `esw/diag/bridge_tracepoint`.

State and persistence: Tracepoints store no persistent driver state, but snapshot fields from bridge private structs at call time. FDB `used` is derived from jiffies minus `lastuse`.

Dependencies and risks: Depends on `bridge_priv.h`, `netdev_name()`, tracepoint infrastructure, and stable private struct fields. Risks are trace format regressions, dereferencing invalid objects if tracepoints are called after cleanup ordering changes, and overhead on frequent FDB refresh paths. Test signals include successful trace event registration and correct fields when enabling mlx5 bridge tracepoints during bridge FDB/VLAN/MDB operations.
