# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_devlink.c

## Purpose
Implements devlink operations for NFP PFs: physical port split/unsplit, shared buffer pool operations, eswitch mode delegation, firmware/board info reporting, flash update, and devlink port registration.

## Important APIs, Types, and Functions
- `nfp_devlink_port_split()` and `nfp_devlink_port_unsplit()` validate ETH port lane topology and call `nfp_devlink_set_lanes()` through NSP config transactions.
- Shared buffer callbacks call `nfp_shared_buf_pool_get()` and `nfp_shared_buf_pool_set()`.
- `nfp_devlink_eswitch_mode_get/set()` delegate to app callbacks.
- `nfp_devlink_info_get()` publishes serial number, running/stored NSP versions, and fixed HWInfo versions.
- `nfp_devlink_flash_update()` calls `nfp_flash_update_common()`.
- `nfp_devlink_port_register()` populates physical devlink port attributes, switch ID from CPP serial, lane/split info, and registers port ops.

## Control Flow
Devlink core invokes `nfp_devlink_ops`. Port split/unsplit takes RTNL to copy a stable `nfp_eth_table_port`, starts NSP ETH config, applies split lane count, commits, and refreshes the port table if changed. Info get opens NSP, optionally reads version buffer, publishes version keys, closes NSP, then adds HWInfo-derived fixed versions.

## State and Persistence Behavior
Port split/unsplit modifies firmware/NSP-managed hardware port configuration. Flash update writes persistent firmware image through NSP. Devlink port registration creates runtime devlink objects tied to `struct nfp_port`.

## Dependencies and Integration Points
Depends on devlink, RTNL, NSP ETH/versions/flash APIs, HWInfo, app eswitch callbacks, shared-buffer code, and port structures. It is registered by PF devlink allocation in `nfp_main.c`.

## Risks
Lane special cases for 100G CXP to 2x40G are topology-specific. NSP access failures must report extack accurately. Serial number construction concatenates vendor/part/serial into a temporary buffer and depends on all three HWInfo fields. Port registration assumes a valid physical `nfp_port` and ETH table copy.

## Test Signals
`devlink dev info`, flash update failure/success paths, split/unsplit invalid counts, already-unsplit errors, shared-buffer get/set, eswitch mode get/set for apps that support it, and devlink port attributes/switch ID validation.
