# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fw.c

## Purpose
`fw.c` implements firmware-facing mlx5 control-plane helpers: adapter identity queries, HCA capability discovery, HCA init/teardown variants, firmware flashing through the common `mlxfw` FSM, and running/pending firmware version queries.

## Important APIs, Types, And Functions
- `mlx5_query_board_id` and `mlx5_core_query_vendor_id` issue `QUERY_ADAPTER`.
- `mlx5_query_hca_caps` conditionally queries all supported capability blocks, including general, port selection, ethernet/IPoIB offloads, ODP, atomic, RoCE, flow tables, eswitch, QoS, debug, access-register capability maps, device memory, TLS, vDPA/TLP emulation, IPsec, crypto, MACsec, advanced virtualization/RDMA, SHAMPO, and PSP.
- `mlx5_cmd_init_hca`, `mlx5_cmd_teardown_hca`, `mlx5_cmd_force_teardown_hca`, and `mlx5_cmd_fast_teardown_hca` wrap HCA lifecycle commands.
- Firmware-flash register helpers access MCC, MCDA, MCQI, MCQS, and MIRC registers, and `mlx5_firmware_flash` wires mlx5 into `mlxfw_firmware_flash`.
- `mlx5_fw_version_query` locates the boot image component and reads running and pending versions.

## Control Flow And State
Capability discovery starts from general capabilities and only queries optional blocks when the relevant capability bit is present. HCA init can pass software owner ID and software VHCA ID. Fast teardown first asks firmware to prepare, disables the NIC interface, and polls until the NIC state is disabled or PCI access fails/times out.

Firmware flashing uses the `mlxfw_dev_ops` callback table: lock update handle, describe/update component, download blocks through MCDA, verify, activate/reactivate, query FSM state, cancel, and release. Version query scans MCQS component entries until it finds the boot image, reads the running version through MCQI, then checks whether a pending reset-active image exists before querying stored version.

## State And Persistence Behavior
The file mutates device capability caches, `dev->board_id`, HCA state in firmware, firmware update FSM state, pending stored firmware image state, and NIC interface state during fast teardown. It does not persist data in files; persistence is firmware/NVRAM-controlled through the firmware update mechanism.

## Dependencies And Integration Points
It depends on mlx5 command execution, access-register helpers, devlink via `priv_to_devlink`, the shared `mlxfw` library, eswitch manager checks, and timeout helpers. Reset and health code depend on HCA teardown and NIC state helpers.

## Risks And Edge Cases
Capability probing is long and conditional; a new feature bit may require querying a matching capability block before use. Flashing requires multiple register capabilities and returns `-EOPNOTSUPP` if any are absent. Fast teardown must handle PCI channel offline and stale NIC state. Version query uses `U32_MAX` as a failure sentinel for running/pending versions.

## Test Signals
Signals include successful probe capability population on multiple device generations, init/teardown/fast-teardown paths under normal and timeout conditions, firmware flashing rejected on unsupported firmware, flash progress through lock/update/verify/activate, and correct devlink-reported running/pending firmware versions.
