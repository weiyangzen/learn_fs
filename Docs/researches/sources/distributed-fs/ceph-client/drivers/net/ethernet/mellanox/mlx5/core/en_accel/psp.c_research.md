# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/psp.c

Purpose: implements mlx5e PSP offload control plane, flow steering, counters, key/SPI operations, and registration with the kernel PSP device API.

Important APIs, types, and functions: public functions initialize/cleanup RX and TX PSP tables, register/unregister the PSP device, and initialize/cleanup `priv->psp`. `struct mlx5e_psp_fs` holds TX and RX flow-steering state. TX state is `struct mlx5e_psp_tx`; RX protocol state is `mlx5e_accel_fs_psp_prot` for IPv4 and IPv6 UDP PSP. PSP dev ops include config, RX SPI allocation, TX key add/delete, key rotation, and stats. `mlx5e_accel_psp_fs_get_stats_fill()` queries mlx5 flow counters.

Control flow: init first checks PSP, SWP, checksum, partial L4 checksum, and LSO capabilities. It allocates PSP state, initializes TX egress namespace state and RX counters/protocol mutexes, then stores `priv->psp`. RX table activation creates an error table that copies PSP syndrome into metadata for OK packets and drops/counts auth fail, bad trailer, and other errors. The main RX table matches UDP PSP default port, marks metadata reg B with PSP marker bits, performs crypto decrypt, and forwards to the error table. TX table activation creates an egress IPsec namespace rule matching UDP PSP default port, performing crypto encrypt and counting. Registration creates a `psp_dev` with supported AES-GCM versions based on firmware caps.

State and persistence: PSP state persists in `priv->psp`; flow tables are refcounted under mutexes. Flow counters persist until PSP FS cleanup. TX key count and TX drops are atomic. Per-association driver data stores the mlx5 encryption-key id. Hardware key rotation resets PSP generation to zero and sends `MLX5_CMD_OP_PSP_ROTATE_KEY`.

Dependencies and integration points: depends on kernel PSP APIs, mlx5 flow steering, TTC redirection, egress IPsec namespace, crypto key APIs, flow counters, and firmware PSP commands. Datapath files consume key ids in association driver data and CQE metadata created by these flow tables.

Risks: RX error table `max_fte` appears smaller than the number of rules installed, so table sizing should be checked against firmware behavior. Refcounted table get/put must be balanced by netdev open/close paths. Capability checks silently disable PSP, so tests must distinguish unsupported from failed initialization. Association driver storage is sized as `sizeof(u32)` but cast to a local `struct psp_key`.

Test signals: capability-gated init, register/unregister, RX/TX table get/put balance, IPv4 and IPv6 PSP traffic, auth-fail/bad-trailer drops, SPI generation for 128/256-bit keys, association add/delete key count, key rotation, stats query, and teardown with nonzero key count warnings.
