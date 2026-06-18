# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_sriov.c

## Purpose

`nfp_net_sriov.c` implements PF-side netdev operations for configuring NFP SR-IOV VFs. It writes per-VF settings into the firmware VF config table, signals firmware through a mailbox/update path, and returns VF configuration to Linux.

## Important APIs, Types, and Functions

Public functions are `nfp_app_set_vf_mac()`, `nfp_app_set_vf_vlan()`, `nfp_app_set_vf_rate()`, `nfp_app_set_vf_spoofchk()`, `nfp_app_set_vf_trust()`, `nfp_app_set_vf_link_state()`, and `nfp_app_get_vf_config()`. Local helpers are `nfp_net_sriov_check()` for capability/table/VF validation and `nfp_net_sriov_update()` for mailbox update signaling.

## Control Flow

Each setter obtains the app from the netdev, validates that `vfcfg_tbl2` exists, checks the relevant firmware capability bit, validates VF index and user input, writes the appropriate fields in the VF's fixed-size config entry, writes mailbox VF number and update bits, then signals firmware with `nfp_net_reconfig(nn, NFP_NET_CFG_UPDATE_VF)` using the first PF vNIC. Firmware's return word is read and converted to a negative errno. Getter reads MAC, control flags, VLAN, optional VLAN protocol, and optional rates back into `struct ifla_vf_info`.

## State and Persistence Behavior

The file mutates the firmware-mapped `vfcfg_tbl2` area: mailbox capability/return/update/VF selector fields and per-VF MAC, control, VLAN, and rate entries. Changes are persistent from the PF driver's perspective but some, such as MAC changes, may require VF driver reload as noted by the log message.

## Dependencies and Integration Points

It depends on NFP app/PF state, VF config layout macros from `nfp_net_sriov.h`, CFG update bits from `nfp_net_ctrl.h`, Linux `ifla_vf_info`, VLAN protocol helpers, `FIELD_PREP/FIELD_GET`, and `nfp_net_reconfig()` firmware synchronization.

## Risks and Edge Cases

Capability checks must precede table writes for unsupported firmware. The VLAN path tolerates firmware without VLAN protocol support only for default 802.1Q; non-default TPIDs require the extra capability. Rate values are limited below `NFP_NET_VF_RATE_MAX`, and zero max maps to the firmware maximum sentinel. The update path assumes at least one vNIC exists on `pf->vnics`. Firmware return codes are positive errno values and are negated.

## Test Signals

Validate all VF ndo operations with supported and unsupported capabilities, invalid VF indexes, multicast MAC rejection, VLAN/QoS bounds, non-802.1Q VLAN protocol support, rate sentinel behavior, firmware refusal return codes, and `ip link show` VF config round trips.
