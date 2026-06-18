<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/sriov.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/sriov.h

## Purpose
Declares generic SFC SR-IOV netdevice operation wrappers for builds with `CONFIG_SFC_SRIOV`.

## Important APIs, Types, And Functions
- Prototypes for `efx_sriov_set_vf_mac()`, `efx_sriov_set_vf_vlan()`, `efx_sriov_set_vf_spoofchk()`, `efx_sriov_get_vf_config()`, and `efx_sriov_set_vf_link_state()`.

## Control Flow
The header contributes no runtime logic; compiled users include it to wire netdev operations to `sriov.c` wrappers when SR-IOV support is enabled.

## State And Persistence Behavior
No state is owned here. It exposes operations that modify NIC-specific VF runtime configuration elsewhere.

## Dependencies And Integration Points
Includes `net_driver.h` for `struct net_device`, `struct ifla_vf_info`, integer types, and network constants. It integrates with generic SFC netdev operation tables.

## Risks And Test Signals
Disabled `CONFIG_SFC_SRIOV` builds intentionally omit prototypes, so call sites must be conditionally compiled. Build matrix coverage with SR-IOV enabled/disabled is the main test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/sriov.h -->
