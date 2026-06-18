# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/fw.h

## Purpose
`fw.h` declares the firmware-facing data structures and command helper prototypes implemented mainly by `fw.c` and partly by `icm.c`. It is the local contract for mlx4 firmware discovery, HCA setup, port capabilities, function capabilities, adapter identity, ICM mapping, basic firmware lifecycle commands, and operation-required handling.

## Important APIs, Types, and Functions
Important data structures are `struct mlx4_mod_stat_cfg`, `struct mlx4_port_cap`, `struct mlx4_dev_cap`, `struct mlx4_func_cap`, `struct mlx4_func`, `struct mlx4_adapter`, `struct mlx4_init_hca_param`, `struct mlx4_init_ib_param`, and `struct mlx4_set_ib_param`. These structures aggregate parsed firmware capability fields for resources, ports, BlueFlame, UARs, ICM, RSS, steering, WOL, rate limiting, health buffers, special QPs, reserved lkeys, HCA context bases, CQE/EQE sizing, and IB port setup.

The header declares firmware query and lifecycle functions such as `mlx4_QUERY_DEV_CAP()`, `mlx4_QUERY_PORT()`, `mlx4_QUERY_FUNC_CAP()`, `mlx4_QUERY_FUNC_CAP_wrapper()`, `mlx4_QUERY_FUNC()`, `mlx4_QUERY_FW()`, `mlx4_QUERY_ADAPTER()`, `mlx4_INIT_HCA()`, `mlx4_QUERY_HCA()`, `mlx4_CLOSE_HCA()`, `mlx4_RUN_FW()`, `mlx4_NOP()`, and `mlx4_MOD_STAT_CFG()`. It also declares ICM mapping helpers `mlx4_MAP_FA()`, `mlx4_UNMAP_FA()`, `mlx4_map_cmd()`, `mlx4_SET_ICM_SIZE()`, `mlx4_MAP_ICM_AUX()`, `mlx4_UNMAP_ICM_AUX()`, plus `mlx4_opreq_action()`.

## Control Flow
The header itself has no executable control flow. Its structure reflects initialization order: query firmware and device capabilities, allocate/map firmware and ICM memory, initialize the HCA with `mlx4_init_hca_param`, query or initialize ports, then use capability structures to enable higher-level Ethernet, IB, steering, QoS, and virtualization features.

## State and Persistence
There is no direct state mutation in the header. State is represented by structs populated by firmware commands and then copied into `struct mlx4_dev` capability fields or private firmware state. The declarations define which capability fields are durable driver runtime state and which command parameters must remain aligned with firmware mailbox layouts.

## Dependencies and Integration Points
The header includes `mlx4.h` and `icm.h`, so it sits between core device state and ICM management. It is consumed by core initialization, EQ setup, port management, Ethernet and IB subdrivers, SR-IOV command wrappers, and firmware memory setup. Any structure change must remain consistent with parsing in `fw.c` and with consumers in `main.c`, `eq.c`, and related mlx4 modules.

## Risks
The main risks are ABI drift between declared structures and firmware parser expectations, missing prototypes for exported helpers, and ambiguous ownership of capability fields. Because many values are sizes, resource counts, or bitfields decoded from firmware, incorrect type widths can truncate hardware limits or flags. The header also exposes wrapper prototypes, so misuse by non-wrapper paths could bypass expected validation.

## Test Signals
Compile coverage is the primary signal: all consumers should build with no prototype or type mismatches. Runtime signals come from successful firmware query/init flows, correct capability propagation into `dev->caps`, correct ICM mapping, correct port capability consumers, and SR-IOV wrapper calls matching the declared signatures.
