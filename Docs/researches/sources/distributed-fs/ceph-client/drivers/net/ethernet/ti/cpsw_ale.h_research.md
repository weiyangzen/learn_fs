# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_ale.h

## Purpose
`cpsw_ale.h` defines the public CPSW ALE interface and state structures used by CPSW Ethernet and switchdev code.

## Important APIs, Types, And Functions
`struct cpsw_ale_params` passes MMIO base, device, ageout, table size, policer count, port count, SoC `dev_id`, reg fields, and bus frequency into `cpsw_ale_create()`. `struct cpsw_ale` stores the resolved parameters, timer, regmap fields, version/features, dynamic field widths, host untag bitmap, and VLAN field table. Enumerations define regmap fields (`enum ale_fields`), control selectors (`enum cpsw_ale_control`), and port states (`enum cpsw_ale_port_state`). Flags such as `ALE_SECURE`, `ALE_BLOCKED`, `ALE_SUPER`, and `ALE_VLAN` select entry semantics.

## Control Flow
The header declares ALE lifecycle, table manipulation, VLAN modification, multicast/allmulti, rate limiting, control get/set, dump/restore, table size query, host untag query, and classifier setup APIs. Callers create an ALE object once during CPSW common initialization, start/stop it during netdev open/close, and then mutate entries from netdev, VLAN, switchdev, and TC paths.

## State And Persistence
The declared `struct cpsw_ale` persists across the lifetime of `struct cpsw_common`; individual ALE entries persist in hardware until cleared, aged, or explicitly removed. `p0_untag_vid_mask` is software state tied to VLAN entry updates and used by RX VLAN restoration.

## Dependencies And Integration Points
The header forward-declares regmap and field metadata and exposes ALE to CPSW legacy, switchdev, ethtool, private helper, and K3-related drivers. It assumes Linux bit macros and VLAN constants from included kernel headers through users.

## Risks
Because the header exposes internals of `struct cpsw_ale`, external code can rely on fields that should remain implementation details. Callers must pass valid port masks matching `ale_ports`; stale masks can create unreachable VLAN or multicast entries. `cpsw_ale_get_vlan_p0_untag()` assumes `ale` and its bitmap are initialized.

## Test Signals
Build coverage should include all users of the declarations. Runtime signals include correct open/close ALE lifecycle, VLAN add/delete behavior, ethtool ALE dumps, bridge MDB/FDB offload, TC policer offload, and RX VLAN tag restoration for host-untagged versus tagged VLANs.
