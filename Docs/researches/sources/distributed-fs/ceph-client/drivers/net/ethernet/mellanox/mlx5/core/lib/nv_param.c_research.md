# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/nv_param.c

## Purpose
`nv_param.c` exposes selected mlx5 nonvolatile firmware configuration items as devlink permanent parameters. It reads and writes the MNVDA register for global PCI, per-host-PF PCI, software offload, software offload capability, and software accelerate configuration classes, then maps them to devlink SR-IOV, VF count, CQE compression, and SW parser checksum mode settings.

## Important APIs, types, and functions
Public functions are `mlx5_nv_param_register_dl_params()` and `mlx5_nv_param_unregister_dl_params()`. Low-level helpers are `mlx5_nv_param_read()`, `mlx5_nv_param_write()`, and class-specific read wrappers for SW offload, SW accelerate, global PCI config/capability, and per-host-PF PCI config. Devlink callbacks include get/set/validate for `ENABLE_SRIOV`, `TOTAL_VFS`, driver parameter `cqe_compress_type`, and driver parameter `swp_l4_csum_mode`. Local bitfield structs describe MNVDA configuration item headers and payloads.

## Control flow
Registration is PF-only and registers a static array of devlink parameters. Each get callback prepares an MNVDA header with type class, parameter index, header length, and sometimes access mode, reads the register, decodes fields, and fills `ctx->val`. Set callbacks usually read the existing NV item first, update a specific field, and write the whole item back. Validation callbacks reject unsupported strings and, for `l4_only`, read capability bits before allowing the value. SR-IOV setters first force global configuration into per-PF VF-count mode, then update per-PF enable or VF total fields.

## State and persistence behavior
Writes through `mlx5_nv_param_write()` mutate nonvolatile device configuration via the MNVDA register using write access mode. Values are devlink `CMODE_PERMANENT`, so effects may require reload or reset depending on firmware. The file itself keeps no dynamic state.

## Dependencies and integration points
The file depends on mlx5 register access, generated IFC field macros, devlink parameter APIs, extack reporting, and PF detection. It integrates with mlx5 devlink setup/teardown and with firmware configuration storage for SR-IOV and offload defaults.

## Risks and edge cases
The SR-IOV enable setter appears to compute `data` before clearing/re-reading `mnvda`, then sets `pf_total_vf_en` after the per-PF read without refreshing `data`; that is a fragile pointer-to-stack-buffer pattern and should be reviewed. Similar care is needed wherever `mnvda` is memset after `data` is assigned. Invalid firmware values are surfaced as `-EOPNOTSUPP` or `-EINVAL`. Permanent NV writes can change device behavior after reboot, so validation and extack messages are important. Global versus per-PF SR-IOV support is intentionally restricted to per-PF-capable devices.

## Test signals
Test devlink param registration on PF and non-PF devices, get/set/validate for all four parameters, unsupported capability handling, invalid strings, max VF validation, MNVDA read/write failure injection, persistence across reload or reboot where available, and SR-IOV per-PF behavior on devices with and without `per_pf_total_vf_supported`.
