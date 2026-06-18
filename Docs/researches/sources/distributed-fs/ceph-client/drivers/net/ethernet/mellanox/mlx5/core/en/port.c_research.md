# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/port.c

Purpose: wraps mlx5 Ethernet port firmware registers for autoneg/link modes, port buffers, priority-to-buffer mapping, shared-buffer controls, and FEC configuration.

Important APIs/functions: `mlx5_port_query_eth_autoneg`, `mlx5_port_set_eth_ptys`, `mlx5e_port_linkspeed`, PBMC/SBPR/SBCM/PPTB query/set wrappers, `mlx5e_fec_in_caps`, `mlx5e_get_fec_mode`, and `mlx5e_set_fec_mode`.

Control flow: register wrappers allocate or stack-build input/output buffers, set `local_port`/selectors, and call `mlx5_core_access_reg`. Link speed queries extended PTYS first and falls back to legacy PTYS when needed. FEC logic queries PPLM, walks supported link-mode fields gated by PCAM feature bits, maps ethtool FEC policy to lane-speed-specific firmware policies, clears unsupported speeds to auto, and writes the updated PPLM.

State and persistence: no driver-local long-lived state. Successful register writes persist in firmware/admin port configuration.

Dependencies and integration: depends on mlx5 register layouts (`PTYS`, `PBMC`, `SBPR`, `SBCM`, `PPTB`, `PPLM`), port capability helpers, and ethtool-facing FEC constants from `port.h`.

Risks: FEC field coverage must track new link modes and capability bits. `mlx5_port_set_eth_ptys` denies autoneg disable when unsupported. Priority-to-buffer packing uses four bits per priority and depends on valid buffer indices from callers.

Test signals: extended vs legacy PTYS devices, missing PCAM/PPLM support, every FEC policy and lane-speed class, register access failures, and priority-buffer round trips.
